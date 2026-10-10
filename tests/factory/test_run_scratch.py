"""A scratch directory per run (issue #35): `run start` creates `runs/<run id>/scratch/` for every
role, the composed input names it, every role's preamble directs temporary files there, the store's
`.gitignore` excludes it, and the harness clears a finished run's scratch when its ticket changes
to any state but `parked`.

Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE) with the suite's
fixture instance, like test_run_isolation.py.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
PRECEDENCE = "takes precedence over any other instruction to use a session scratchpad"
ACCEPT = "Type: bug\nTitle: A\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"


class Store:
    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.root = tmp_path / "state"
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(FIXTURE_INSTANCE),
                    "PYTHONDONTWRITEBYTECODE": "1"}
        self.n = 0

    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def request(self) -> str:
        self.n += 1
        p = self.tmp / f"req{self.n}.md"
        p.write_text(f"# Request {self.n}\n\nbody {self.n}\n")
        return self.ok("ticket", "new", "--file", str(p))["id"]

    def start(self, tid: str) -> str:
        return self.ok("run", "start", "--role", "triage", "--ticket", tid)["run_id"]

    def finish(self, rid: str, text: str = ACCEPT) -> None:
        p = self.tmp / f"{rid}.out"
        p.write_text(text)
        self.ok("run", "finish", rid, "--output-file", str(p))

    def scratch(self, rid: str) -> Path:
        return self.root / "runs" / rid / "scratch"

    def fill(self, rid: str) -> None:
        (self.scratch(rid) / "deep").mkdir(parents=True, exist_ok=True)
        (self.scratch(rid) / "deep" / "f").write_text("x")

    def gitignore(self) -> list[str]:
        return (self.root / ".gitignore").read_text().splitlines()


def test_each_run_gets_its_own_scratch_named_only_in_its_own_input(tmp_path):
    s = Store(tmp_path)
    a, b = s.start(s.request()), s.start(s.request())
    for rid, other in ((a, b), (b, a)):
        assert s.scratch(rid).is_dir() and not any(s.scratch(rid).iterdir())
        s.ok("run", "compose", rid)
        text = (s.root / "runs" / rid / "input.md").read_text()
        own = s.scratch(rid).resolve()
        assert text.count("\n## Scratch directory\n") == 1
        assert f"## Scratch directory\nPut every file you make for your own use in this run under `{own}`: " \
               "no other run uses it. The harness clears it when the ticket moves on, and keeps it while the " \
               "ticket is parked.\n" in text
        assert str(s.scratch(other).resolve()) not in text
        # directly after the Running code section, before any declared source
        assert re.search(r"\n## Running code\n[^\n]*\n\n## Scratch directory\n", text)
        meta = s.ok("run", "compose", rid)
        assert not any("scratch" in src for src in meta["sources"])


def test_every_system_prompt_carries_the_scratch_rule_once(tmp_path):
    s = Store(tmp_path)
    rid = s.start(s.request())
    sysp = (s.root / "runs" / rid / "system-prompt.txt").read_text()
    assert sysp.count(PRECEDENCE) == 1
    assert sysp.index("RUNNING CODE") < sysp.index("SCRATCH FILES") < sysp.index("GUARDRAIL PATHS")


def test_the_scratch_rule_is_in_all_three_preamble_copies():
    copies = [REPO / "docs" / "prompts" / "00-preamble.md", REPO / "factory" / "prompts" / "preamble.md"]
    texts = [p.read_text() for p in copies] + [(REPO / "docs" / "design.md").read_text()]
    for text in texts:
        assert text.count("\nSCRATCH FILES\n") == 1 and text.count(PRECEDENCE) == 1


def test_a_refused_run_start_writes_no_run_and_no_scratch(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    s.ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
    cp = s.cli("run", "start", "--role", "triage", "--ticket", tid)
    assert cp.returncode == 2 and "not ready-for-triage" in cp.stderr, cp.stderr
    runs = s.root / "runs"
    assert not runs.exists() or not any(runs.iterdir())
    assert not list(s.root.rglob("scratch"))


def test_a_file_in_scratch_is_ignored_by_the_store_git(tmp_path):
    s = Store(tmp_path)
    rid = s.start(s.request())
    s.fill(rid)
    assert "runs/*/scratch/" in s.gitignore()
    subprocess.run(["git", "-C", str(s.root), "init", "-q"], check=True)
    st = subprocess.run(["git", "-C", str(s.root), "status", "--porcelain", "--untracked-files=all"],
                        capture_output=True, text=True, check=True).stdout
    assert "/scratch/" not in st and f"runs/{rid}/meta.yaml" in st


def test_a_new_store_gitignore_is_the_full_commented_block_once(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    s.finish(s.start(tid))
    s.start(tid)
    lines = s.gitignore()
    for ln in ("worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml", "runs/*/scratch/", "drive/"):
        assert lines.count(ln) == 1, (ln, lines)
    assert sum(ln.startswith("#") for ln in lines) == 4


def test_an_existing_store_gitignore_gains_only_the_missing_lines(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    (s.root / ".gitignore").write_text("# kept\nworktrees/\nmine/\nruns/*/wt/\n")
    s.finish(s.start(tid))
    s.start(tid)
    assert s.gitignore() == ["# kept", "worktrees/", "mine/", "runs/*/wt/", "runs/*/tripwire.yaml",
                             "runs/*/scratch/", "drive/"]


def test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    (s.root / ".gitignore").write_text("worktrees/\nruns/*/wt/\nruns/*/tripwire.yaml")
    s.start(tid)
    assert s.gitignore() == ["worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml", "runs/*/scratch/", "drive/"]


def test_moving_a_ticket_on_clears_its_finished_runs_scratch_only(tmp_path):
    s = Store(tmp_path)
    t1, t2 = s.request(), s.request()
    done, other = s.start(t1), s.start(t2)
    s.fill(done)
    s.fill(other)
    s.finish(done)
    s.finish(other)
    live = s.start(t1)  # a second triage run on T-0001, still in flight
    s.fill(live)
    assert s.scratch(done).exists()  # run finish and run start change no status: nothing cleared
    s.ok("ticket", "transition", t1, "--to", "ready-for-spec-writer", "--by", "t")
    assert not s.scratch(done).exists()
    assert sorted(p.name for p in (s.root / "runs" / done).iterdir()) == ["meta.yaml", "output.md",
                                                                          "system-prompt.txt"]
    assert (s.scratch(live) / "deep" / "f").exists()  # in flight
    assert (s.scratch(other) / "deep" / "f").exists()  # another ticket's run


def test_a_parked_ticket_keeps_scratch_until_a_human_sends_it_on(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    rid = s.start(tid)
    s.fill(rid)
    s.finish(rid, "STATUS: NEEDS-HUMAN\nCONFIDENCE: low\nESCALATIONS: none\n")
    s.ok("ticket", "park", tid, "--reason", "q", "--outputs", rid)
    assert (s.scratch(rid) / "deep" / "f").exists()
    s.ok("ticket", "transition", tid, "--to", "ready-for-triage", "--by", "t")
    assert not s.scratch(rid).exists()


def test_ticket_set_status_clears_and_a_same_status_set_does_not(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    rid = s.start(tid)
    s.fill(rid)
    s.finish(rid)
    s.ok("ticket", "set", tid, "status=ready-for-triage")
    assert s.scratch(rid).exists()
    s.ok("ticket", "set", tid, "status=ready-for-spec-writer")
    assert not s.scratch(rid).exists()


def test_a_scratch_symlink_is_removed_without_touching_its_target(tmp_path):
    s = Store(tmp_path)
    tid = s.request()
    rid = s.start(tid)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "keep").write_text("x")
    s.scratch(rid).rmdir()
    s.scratch(rid).symlink_to(outside)
    s.finish(rid)
    s.ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
    assert not s.scratch(rid).is_symlink() and not s.scratch(rid).exists()
    assert (outside / "keep").read_text() == "x"
