"""`factory drive`, part A (T-0040): the intake phase run as `claude -p` processes, with no clerk.

Black-box through `bin/factory` on a throwaway store (FACTORY_STATE) with the suite's fixture
instance. A Python stand-in `claude`, written into tmp_path and put first on PATH, plays each role:
it logs its argv, working directory and FACTORY_DISPATCH, then plays the next entry of its role's
list in $STANDIN_PLAYS (the last one repeats): {"write": STATUS} writes output.md, {"say": text}
writes nothing, {"fail": text} replies with is_error and exits 1; any entry may first "sleep".
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BIN = REPO / "bin" / "factory"
FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"

STANDIN = '''#!{python}
import json, os, pathlib, sys, time
cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
with log.open("a") as f:
    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
role = cwd.name.split("-", 2)[2]
plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
time.sleep(p.get("sleep", 0))
text, err = p.get("say", ""), "fail" in p
if "write" in p:
    text = "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
    (cwd / "output.md").write_text(text)
elif err:
    text = p["fail"]
print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
sys.exit(1 if err else 0)
'''

TRIAGE_OK = {"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}]}


class Store:
    """A throwaway store with T-0001 ready for triage, and the stand-in `claude` first on PATH."""

    def __init__(self, tmp_path: Path, instance: Path = FIXTURE_INSTANCE):
        self.tmp = tmp_path
        self.root = tmp_path / "state"
        self.log = tmp_path / "claude.log"
        bindir = tmp_path / "bin"
        bindir.mkdir()
        (bindir / "claude").write_text(STANDIN.format(python=sys.executable))
        (bindir / "claude").chmod(0o755)
        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(instance),
                    "PYTHONDONTWRITEBYTECODE": "1", "STANDIN_LOG": str(self.log),
                    "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}"}
        self.env.pop("FACTORY_DISPATCH", None)
        req = tmp_path / "req.md"
        req.write_text("# Fixture\n\nThe bot should do the thing.\n")
        self.ok("ticket", "new", "--file", str(req))

    def cli(self, *argv: str, plays: dict | None = None) -> subprocess.CompletedProcess:
        env = {**self.env, "STANDIN_PLAYS": json.dumps(plays or {})}
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)

    def ok(self, *argv: str) -> dict:
        cp = self.cli(*argv)
        assert cp.returncode == 0, cp.stderr
        return json.loads(cp.stdout.strip().splitlines()[-1])

    def drive(self, plays: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict]:
        cp = self.cli("drive", "T-0001", *extra, plays=plays)
        return cp, json.loads(cp.stdout.strip().splitlines()[-1])

    def ticket(self, tid: str = "T-0001") -> dict:
        return yaml.safe_load((self.root / "tickets" / f"{tid}.yaml").read_text())

    def runs(self) -> list[dict]:
        return [yaml.safe_load(p.read_text()) for p in sorted(self.root.glob("runs/*/meta.yaml"))]

    def calls(self) -> list[dict]:
        return [json.loads(ln) for ln in self.log.read_text().splitlines()] if self.log.exists() else []

    def events(self) -> list[str]:
        return [json.loads(ln)["event"] for p in sorted((self.root / "log").glob("*.jsonl"))
                for ln in p.read_text().splitlines() if ln.strip()]


def test_an_approved_spec_stops_at_the_spec_gate_after_one_revision(tmp_path):
    s = Store(tmp_path)
    cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}, "--phase", "intake")
    assert cp.returncode == 0, cp.stderr
    assert res == {"ticket": "T-0001", "state": "awaiting-spec-gate", "rounds": 2, "ok": True}
    t = s.ticket()
    assert t["status"] == "awaiting-spec-gate" and t["round"]["spec"] == 2 and t["in_flight"] == []
    assert [(m["role"], m["status"]) for m in s.runs()] == [
        ("triage", "ACCEPT"), ("spec_writer", "READY-FOR-CRITIC"), ("critic", "REVISE"),
        ("spec_writer", "READY-FOR-CRITIC"), ("critic", "APPROVE")]
    assert len(s.calls()) == 5


def test_a_critic_still_revising_at_the_round_limit_parks_with_max_rounds(tmp_path):
    s = Store(tmp_path)
    cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "REVISE"}]}, "--phase", "intake")
    assert cp.returncode == 0, cp.stderr
    assert res["state"] == "parked" and res["reason"] == "max rounds"
    assert s.ticket()["status"] == "parked" and s.ticket()["parked"]["reason"] == "max rounds"


def test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message(tmp_path):
    s = Store(tmp_path)
    cp, res = s.drive({"triage": [{"say": "still waiting on my commands"}]})
    assert cp.returncode == 0, cp.stderr
    assert res["state"] == "parked"
    parked = s.ticket()["parked"]
    assert parked["reason"] == "EMPTY-OUTPUT from triage"
    assert [m["status"] for m in s.runs()] == ["EMPTY-OUTPUT", "EMPTY-OUTPUT"]
    for m in s.runs():
        kept = (s.root / "runs" / m["run_id"] / "last-message.md").read_text()
        assert kept == "still waiting on my commands\n"


def test_a_failed_role_process_is_recorded_killed_and_parks_once(tmp_path):
    s = Store(tmp_path)
    cp, res = s.drive({"triage": [{"fail": "usage limit reached"}]})
    assert cp.returncode == 0, cp.stderr
    assert res["state"] == "parked"
    assert s.ticket()["parked"]["reason"] == "agent call failed: triage: usage limit reached"
    assert [m["status"] for m in s.runs()] == ["KILLED"] and s.ticket()["in_flight"] == []
    assert len(s.calls()) == 1  # no retry
    assert "run.killed" in s.events()


def test_a_role_that_prints_no_json_is_a_failed_call_named_by_its_stderr(tmp_path):
    s = Store(tmp_path)
    (tmp_path / "bin" / "claude").write_text("#!/bin/sh\necho 'not json'\necho 'bad flag --x' >&2\necho >&2\n")
    cp, res = s.drive({})
    assert cp.returncode == 0, cp.stderr
    assert s.ticket()["parked"]["reason"] == "agent call failed: triage: bad flag --x"
    meta = s.runs()[0]
    assert meta["status"] == "KILLED" and meta["claude"] is None
    assert (s.root / "runs" / meta["run_id"] / "reply.json").read_text() == "not json\n"


def test_triage_reject_clarify_and_needs_human_route_as_the_script_does(tmp_path):
    for n, (status, state, reason) in enumerate([("REJECT", "closed", None),
                                                  ("CLARIFY", "waiting-requester", None),
                                                  ("NEEDS-HUMAN", "parked", "NEEDS-HUMAN from triage"),
                                                  ("MAYBE", "parked", "harness-bug: unknown STATUS MAYBE from triage")]):
        (tmp_path / str(n)).mkdir()
        s = Store(tmp_path / str(n))
        cp, res = s.drive({"triage": [{"write": status}]})
        assert cp.returncode == 0, cp.stderr
        assert (res["state"], s.ticket()["status"]) == (state, state)
        assert ((s.ticket()["parked"] or {}).get("reason")) == reason


def test_each_role_process_gets_its_prompt_model_and_tool_limits_and_no_marker(tmp_path):
    s = Store(tmp_path)
    s.env["FACTORY_DISPATCH"] = "1"  # started marked: the role processes still never see it
    cp, _ = s.drive({**TRIAGE_OK, "critic": [{"write": "APPROVE"}]}, "--phase", "intake")
    assert cp.returncode == 0, cp.stderr
    tmp = os.path.realpath(tempfile.gettempdir())
    models = {m["run_id"]: m["model"] for m in s.runs()}
    assert len(s.calls()) == 3
    for c in s.calls():
        run = os.path.realpath(c["cwd"])
        assert c["dispatch"] is None
        assert c["argv"] == [
            "-p", f"Your entire input is the file {run}/input.md; read it first and follow it. "
                  f"Write your complete output to {run}/output.md and return the same text.",
            "--model", models[Path(run).name], "--output-format", "json", "--permission-mode", "auto",
            "--append-system-prompt-file", f"{run}/system-prompt.txt",
            "--tools", "Read,Grep,Glob,Bash,Write,WebFetch,WebSearch",
            "--allowedTools", f"Read,Grep,Glob,Bash,WebFetch,WebSearch,Edit(/{run}/output.md),"
                              f"Edit(/{run}/scratch/**),Edit(/{tmp}/**)"]


def test_prompt_mode_replace_passes_the_role_prompt_as_the_whole_system_prompt(tmp_path):
    s = Store(tmp_path)
    cp, _ = s.drive({"triage": [{"write": "REJECT"}]}, "--prompt-mode", "replace")
    assert cp.returncode == 0, cp.stderr
    argv = s.calls()[0]["argv"]
    run = os.path.realpath(s.calls()[0]["cwd"])
    assert argv[argv.index("--system-prompt-file") + 1] == f"{run}/system-prompt.txt"
    assert "--append-system-prompt-file" not in argv


def role_argv(*args) -> list[str]:
    """factory.drive.role_argv, run in the harness checkout (the suite's `factory` is tests/factory)."""
    code = "import json, sys; from factory import drive; print(json.dumps(drive.role_argv(*json.loads(sys.argv[1]))))"
    cp = subprocess.run([sys.executable, "-c", code, json.dumps(args)], capture_output=True, text=True, cwd=REPO,
                        check=True)
    return json.loads(cp.stdout)


def test_the_implementer_alone_gets_edit_and_its_worktree():
    argv = role_argv("implementer", "/s/runs/run-0001-implementer", "opus", "append", "/s/worktrees/T-1.1", None)
    opts = dict(zip(argv[2::2], argv[3::2]))
    assert opts["--tools"].split(",")[-1] == "Edit"
    assert opts["--allowedTools"].endswith(",Edit(//s/worktrees/T-1.1/**)")
    assert opts["--add-dir"] == "/s/worktrees/T-1.1"
    checker = role_argv("reviewer", "/s/runs/run-0002-reviewer", "fable", "append", "/s/runs/x/wt", None)
    assert "Edit" not in checker[checker.index("--tools") + 1].split(",") and "--add-dir" not in checker


def test_a_configured_effort_is_passed_to_its_role_only(tmp_path):
    inst = tmp_path / "instance"
    shutil.copytree(FIXTURE_INSTANCE, inst)
    with (inst / "instance.yaml").open("a") as f:
        f.write("effort: {triage: low}\n")
    (tmp_path / "s").mkdir()
    s = Store(tmp_path / "s", instance=inst)
    cp, _ = s.drive({**TRIAGE_OK, "critic": [{"write": "APPROVE"}]})
    assert cp.returncode == 0, cp.stderr
    effort = [c["argv"][c["argv"].index("--effort") + 1] if "--effort" in c["argv"] else None for c in s.calls()]
    assert effort == ["low", None, None]


def test_each_run_keeps_its_reply_and_records_its_cost(tmp_path):
    s = Store(tmp_path)
    cp, _ = s.drive({"triage": [{"write": "REJECT"}]})
    assert cp.returncode == 0, cp.stderr
    meta = s.runs()[0]
    reply = json.loads((s.root / "runs" / meta["run_id"] / "reply.json").read_text())
    assert meta["claude"] == {"session_id": "s-" + meta["run_id"], "total_cost_usd": 0.5, "num_turns": 3,
                              "usage": {"output_tokens": 7}}
    assert reply["session_id"] == meta["claude"]["session_id"]


def test_run_finish_with_a_reply_that_is_not_a_json_object_records_claude_null(tmp_path):
    s = Store(tmp_path)
    rid = s.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]
    (tmp_path / "reply.json").write_text("[1, 2]\n")
    s.ok("run", "finish", rid, "--reply", str(tmp_path / "reply.json"))
    assert "claude" in s.runs()[0] and s.runs()[0]["claude"] is None


def test_every_step_line_names_the_ticket_and_the_status_file_shows_the_end(tmp_path):
    s = Store(tmp_path)
    cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "APPROVE"}]})
    assert cp.returncode == 0, cp.stderr
    lines = cp.stdout.strip().splitlines()
    assert len(lines) > 9 and all(ln.startswith('T-0001 "Fixture": ') for ln in lines[:-1])
    assert 'T-0001 "Fixture": -> awaiting-spec-gate' in lines
    st = yaml.safe_load((s.root / "drive" / "T-0001.yaml").read_text())
    assert (st["ticket"], st["title"], st["phase"], st["running"]) == ("T-0001", "Fixture", "intake", [])
    assert st["ended"] == res and st["last"] == lines[-2]
    assert "drive/" in (s.root / ".gitignore").read_text().splitlines()


def test_a_ticket_in_no_dispatch_state_ends_at_once(tmp_path):
    s = Store(tmp_path)
    s.ok("ticket", "transition", "T-0001", "--to", "waiting-requester", "--by", "t")
    cp, res = s.drive({})
    assert cp.returncode == 0, cp.stderr
    assert res == {"ticket": "T-0001", "state": "waiting-requester", "note": "nothing to dispatch from this state",
                   "ok": True}
    assert s.calls() == []


def test_a_stopped_driver_kills_its_role_records_the_run_and_resumes(tmp_path):
    s = Store(tmp_path)
    env = {**s.env, "STANDIN_PLAYS": json.dumps({"triage": [{"sleep": 60, "write": "ACCEPT"}]})}
    p = subprocess.Popen([str(BIN), "drive", "T-0001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True, env=env, cwd=REPO)
    status = s.root / "drive" / "T-0001.yaml"
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and not (status.exists() and (yaml.safe_load(status.read_text()) or {}).get("running")
                                               and s.calls()):
        time.sleep(0.1)
    running = yaml.safe_load(status.read_text())["running"]
    assert [(r["run"], r["role"]) for r in running] == [("run-0001-triage", "triage")]
    child = s.calls()[0]["pid"]
    p.send_signal(signal.SIGTERM)
    out, _ = p.communicate(timeout=30)
    assert p.returncode == 128 + signal.SIGTERM
    assert json.loads(out.strip().splitlines()[-1]) == {"ok": False, "ticket": "T-0001", "stopped": "SIGTERM"}
    assert s.runs()[0]["status"] == "KILLED"
    t = s.ticket()
    assert (t["status"], t["in_flight"], t["parked"]) == ("ready-for-triage", [], None)
    try:
        os.kill(child, 0)
        alive = True
    except ProcessLookupError:
        alive = False
    assert not alive
    st = yaml.safe_load(status.read_text())
    assert st["running"] == [] and st["ended"]["stopped"] == "SIGTERM"
    cp, res = s.drive({"triage": [{"write": "REJECT"}]})  # no --phase: ready-for-triage selects intake
    assert cp.returncode == 0, cp.stderr
    assert res["state"] == "closed" and len(s.calls()) == 2
    assert re.search(r"^T-0001 \"Fixture\": start triage run-0002-triage$", cp.stdout, re.M)
