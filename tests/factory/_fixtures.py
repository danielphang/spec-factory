"""Scenario fixtures that more than one file of the harness suite uses: stores, targets and
shepherds in a known state, with the constants and stand-ins they are built from. A test file
imports them from here, never from another test file; the generic helpers are in `_cli.py`. Not
named `test_*`, so pytest does not collect it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from ._cli import BIN, REPO, CliStore, approved_parent, cli, git_repo, js, tree

# ----- a plan with lettered sub-tickets (test_subtickets.py) --------------------------------------

PLAN_LETTERS = """# Plan — T-0001: alert the operator

## Grounding for this plan
Checked on this base.

## Fixture (prelude for every sub-ticket)
```
cat > /tmp/fx.py <<'PY'
## not a heading
PY
```

## T-0001-A / Emit the truncation event
**Depends on:** none. Lands first.

**Parallel-safe:** yes, alongside T-0001-C. The two edit disjoint files.

Scope: A

## T-0001-C / Retire the margin signal
**Depends on:** none. Lands second, before T-0001-B.

**Parallel-safe:** yes, alongside T-0001-A (disjoint files).

## T-0001-B / Re-anchor the check
**Depends on:** T-0001-C.

**Parallel-safe:** no. Same file as T-0001-C.

## Coverage map
- criterion 1 → T-0001-A

## Out-of-scope observations
none
STATUS: PLANNED
CONFIDENCE: high, fixture
ESCALATIONS: none
"""


# ----- the store's ticket files (test_build_startup.py) -------------------------------------------

def ticket_files(store: Path) -> list[str]:
    return sorted(p.name for p in (store / "tickets").iterdir())


# ----- a driver for build.js (test_sibling_tests.py) ----------------------------------------------

# Drives factory/workflows/build.js on parent T-0001: each clerk command runs for real, each role run
# returns an empty output (a killed run). Prints each park as `park <id>: <reason>`.
BUILD_DRIVER = r"""
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
"""


# ----- the t0027-amend.sh store fixture (test_spec_amend.py) --------------------------------------

SPEC = """=== proposal.md
## Problem
{problem}
## Decisions
- {decision}
=== design.md
## Proposed change
Edit `src/greet.py`.
## Tests to change
none
=== specs/demo/spec.md
## ADDED Requirements
### Requirement: Greets
{statement}

#### Scenario: Greeting is printed
- WHEN `{cmd}`
- THEN it prints `{out}`
{extra}=== verification.md
## Acceptance
- Greeting is printed → NEW
{labels}"""

TWO = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n"


def spec(decision="Greet by default.", cmd="echo hi", out="hi", problem="x", statement="The tool SHALL greet.",
         extra="", labels="") -> str:
    return SPEC.format(decision=decision, cmd=cmd, out=out, problem=problem, statement=statement, extra=extra,
                       labels=labels)


V1, V2 = spec(), spec(cmd="echo hello", out="hello")


class Fixture(CliStore):
    def __init__(self, tmp_path: Path):
        self.tmp = tmp_path
        self.store = tmp_path / "store"
        self.target = tmp_path / "t"
        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}

    def file(self, name: str, text: str) -> str:
        p = self.tmp / name
        p.write_text(text)
        return str(p)

    def ticket(self, tid: str) -> dict:
        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())

    def plan(self, text: str = TWO) -> None:
        self.ok("subticket", "add", "T-0001", "--file", self.file("plan.md", text))
        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")

    def amend(self, text: str, reason: str = "Seed the greeting.", intent: str = "unchanged",
              tid: str = "T-0001") -> subprocess.CompletedProcess:
        return self.cli("spec", "amend", tid, "--file", self.file("amend.md", text), "--reason", reason,
                        "--intent", intent)

    def snapshot(self) -> dict[str, bytes]:
        return {str(p.relative_to(self.store)): p.read_bytes() for p in sorted(self.store.rglob("*")) if p.is_file()}

    def change(self, rel: str) -> Path:
        return self.store / "openspec" / "changes" / "T-0001" / rel


@pytest.fixture
def f(tmp_path: Path) -> Fixture:
    f = Fixture(tmp_path)
    subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
    for rel in ("src/greet.py", "src/other.py"):
        (f.target / rel).parent.mkdir(parents=True, exist_ok=True)
        (f.target / rel).write_text(f"# {rel}\n")
    subprocess.run(["git", "-C", str(f.target), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f", "commit", "-qm", "land"],
                   check=True)
    f.ok("init")
    f.ok("ticket", "new", "--file", f.file("req.md", "# Fixture\n\nGreet.\n"))
    approved_parent(f.ok, "T-0001", f.file("v1.md", V1))
    return f


# ----- the spec drift checks (test_spec_drift.py) -------------------------------------------------

def land(f: Fixture, *files: str) -> str:
    """One commit on the target's main that appends a line to each file; returns its sha."""
    for rel in files:
        p = f.target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a") as fh:
            fh.write(f"# {rel}\n")
    git = ["git", "-C", str(f.target), "-c", "user.email=f@x", "-c", "user.name=f"]
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-qm", f"land {' '.join(files)}"], check=True)
    return head(f)


def head(f: Fixture) -> str:
    return subprocess.run(["git", "-C", str(f.target), "rev-parse", "main"], capture_output=True, text=True,
                          check=True).stdout.strip()


def start(f: Fixture, tid: str = "T-0001.1") -> subprocess.CompletedProcess:
    return f.cli("run", "start", "--role", "implementer", "--ticket", tid)


def implementer_runs(f: Fixture) -> list[str]:
    d = f.store / "runs"
    return sorted(p.name for p in d.iterdir() if p.name.endswith("-implementer")) if d.exists() else []


def drifted(f: Fixture, cp: subprocess.CompletedProcess, tid: str = "T-0001.1") -> str:
    """Assert a drift refusal that reserved no run and wrote nothing to the sub-ticket; return its error."""
    assert cp.returncode == 2, cp.stdout + cp.stderr
    error = json.loads(cp.stdout.strip().splitlines()[-1])["error"]
    assert error.startswith("BLOCKED from harness: spec drift: ")
    assert error.endswith(f"Amend the spec (`spec amend T-0001`) or rule (`resolve {tid} --ruling F`)")
    assert implementer_runs(f) == []
    sub = f.ticket(tid)
    assert sub["status"] == "ready-for-implementer" and sub["in_flight"] == [] and not sub.get("branch")
    return error


def started(cp: subprocess.CompletedProcess) -> None:
    assert cp.returncode == 0, cp.stdout + cp.stderr


# ----- the stand-in `claude` and the intake store of `factory drive` (test_drive.py) --------------

FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"

STANDIN = '''#!{python}
import fcntl, json, os, pathlib, sys, time
cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
with log.open("a") as f:
    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
role = cwd.name.split("-", 2)[2]
plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
nf = log.with_name(log.name + ".n-" + role)
with open(log.with_name(log.name + ".lock"), "w") as lk:  # copies of one role may start at once
    fcntl.flock(lk, fcntl.LOCK_EX)
    n = int(nf.read_text()) + 1 if nf.exists() else 1
    nf.write_text(str(n))
p = plays[min(n, len(plays)) - 1]
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


class Store(CliStore):
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


# ----- the build store of `factory drive` (test_drive_build.py) -----------------------------------

BUILD_STANDIN = '''#!{python}
import fcntl, json, os, pathlib, re, sys, time
t0 = time.time()
cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
with log.open("a") as f:
    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
role = cwd.name.split("-", 2)[2]
plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
nf = log.with_name(log.name + ".n-" + role)
with open(log.with_name(log.name + ".lock"), "w") as lk:  # copies of one role may start at once
    fcntl.flock(lk, fcntl.LOCK_EX)
    n = int(nf.read_text()) + 1 if nf.exists() else 1
    nf.write_text(str(n))
p = plays[min(n, len(plays)) - 1]
time.sleep(p.get("sleep", 0))
text, err = p.get("say", ""), "fail" in p
if "write" in p:
    head = re.search(r"^head: '?([0-9a-f]{{40}})", (cwd / "meta.yaml").read_text(), re.M)
    text = (("Commit: %s\\n" % head[1]) if head else "") + ("Gate suite: PASS\\n" if role == "verifier" else "")
    text += "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
    (cwd / "output.md").write_text(text)
elif err:
    text = p["fail"]
with log.with_name(log.name + ".times").open("a") as f:
    f.write("%f %f\\n" % (t0, time.time()))
print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
sys.exit(1 if err else 0)
'''


class BuildStore(Store):
    """Part A's store, with T-0001 approved at the spec gate (ready for its planner; a one-section
    spec, so the planner is skipped), a scratch git repository as the target, and this file's
    stand-in `claude`."""

    def __init__(self, tmp_path):
        super().__init__(tmp_path)
        (tmp_path / "bin" / "claude").write_text(BUILD_STANDIN.format(python=sys.executable))
        spec = tmp_path / "spec.md"
        spec.write_text("## Problem\nx\n")
        approved_parent(self.ok, "T-0001", spec)
        self.target = git_repo(tmp_path / "target")
        self.env.update(FACTORY_REPO=str(self.target), FACTORY_INTEGRATION_BRANCH="main")

    def git(self, *argv: str, cwd=None) -> str:
        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=cwd or self.target,
                            capture_output=True, text=True, check=True)
        return cp.stdout.strip()

    def two_subtickets_at_checks(self) -> None:
        """T-0001 planned into T-0001.1 and T-0001.2, independent, each at checks-in-flight on its own commit."""
        plan = self.tmp / "plan.md"
        plan.write_text("ST-1 / One\nDepends on: none\nParallel-safe: yes\n\n"
                        "ST-2 / Two\nDepends on: none\nParallel-safe: yes\n")
        self.ok("subticket", "add", "T-0001", "--file", str(plan))
        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
        for i in (1, 2):
            self.git("checkout", "-qb", f"factory/T-0001.{i}", "main")
            (self.target / f"f{i}.txt").write_text(f"{i}\n")
            self.git("add", f"f{i}.txt")
            self.git("commit", "-qm", f"w{i}")
            self.git("checkout", "-q", "main")
            head = self.git("rev-parse", f"factory/T-0001.{i}")
            self.ok("ticket", "set", f"T-0001.{i}", "status=checks-in-flight", f"branch=factory/T-0001.{i}",
                    f"head={head}")

    def most_at_once(self) -> int:
        spans = [tuple(map(float, ln.split())) for ln in (self.log.parent / (self.log.name + ".times"))
                 .read_text().splitlines()]
        return max([sum(a <= s < b for a, b in spans) for s, _ in spans] or [0])


# ----- a scratch target with its own store (test_live_store_guard.py) -----------------------------

RULE = "role runs may not write the live store"


@pytest.fixture
def target(tmp_path: Path) -> Path:
    t = git_repo(tmp_path / "target")
    cp = cli(t, "init", "--repo-name", "demo")
    assert cp.returncode == 0, cp.stderr
    req = tmp_path / "r.md"
    req.write_text("# demo\n\nDo the thing.\n")
    assert cli(t, "ticket", "new", "--file", str(req)).returncode == 0
    return t


def state(target: Path) -> Path:
    return target / ".factory" / "state"


def start_triage(target: Path) -> str:
    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 0, cp.stderr
    return js(cp)["run_id"]


def snapshot(target: Path) -> dict[str, bytes]:
    return {**tree(target / ".factory"), **tree(target / ".claude")}


def other_request(tmp_path: Path) -> str:
    p = tmp_path / "r2.md"
    p.write_text("# other\n\nDo another thing.\n")
    return str(p)


def assert_refused(cp, *details: str) -> None:
    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
    assert RULE in cp.stderr and "use a throwaway FACTORY_STATE" in cp.stderr
    assert "FACTORY_DISPATCH" not in cp.stderr + cp.stdout
    assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
    for d in details:
        assert d in cp.stderr


# ----- the store branch (test_store_branch.py) ----------------------------------------------------

BRANCH = "factory-store"
IDENT = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd: Path, *argv: str, check: bool = True) -> str:
    env = {**os.environ, **IDENT}
    cp = subprocess.run(["git", *argv], cwd=cwd, capture_output=True, text=True, env=env)
    if check:
        assert cp.returncode == 0, (argv, cp.stderr)
    return cp.stdout.strip()


def exclude(t: Path) -> Path:
    p = Path(git(t, "rev-parse", "--git-path", "info/exclude"))
    return p if p.is_absolute() else t / p


def request(tmp_path: Path) -> str:
    p = tmp_path / "r.md"
    p.write_text("# demo\n\nDo the thing.\n")
    return str(p)


# ----- the shepherd: the routing table applied to the store CLI (test_shepherd.py) ----------------

STUBS = Path(__file__).resolve().parent / "fixtures" / "stubs"
MAX_SPEC_ROUNDS = 2  # factory/config.yaml max_rounds.spec


def built_to_implementer(tmp_path, plan: str | None = None):
    """A ticket approved, planned and split; returns the shepherd, the parent id and its sub-ticket ids."""
    f = Shepherd(tmp_path, case="accept-approve", with_repo=True)
    f.human_runs("init")
    tid = f.request("# SPEC-99: Fixture\n\nThe bot should do the thing.\n")
    for role in ("triage", "spec_writer", "critic"):
        f.dispatch(role, tid)
    f.human_approves(tid)
    if plan:
        p = f.tmp / "plan.md"
        p.write_text(plan + "STATUS: PLANNED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
        f.dispatch("planner", tid, stub_path=p)
    else:
        f.dispatch("planner", tid)
    return f, tid, list(f.ok("ticket", "parent-check", tid)["subtickets"])


class Run:
    def __init__(self, run_id: str, input_text: str, sources: list[str], status: str | None):
        self.run_id, self.input, self.sources, self.status = run_id, input_text, sources, status


class Shepherd(CliStore):
    def __init__(self, tmp_path: Path, case: str, with_repo: bool = False):
        self.store = tmp_path / "state"
        self.case = case
        self.tmp = tmp_path
        self.count: dict[str, int] = {}
        self.last_join: dict = {}
        self.repo: Path | None = None
        if with_repo:  # a scratch target repo: one commit on `main`, the integration branch
            self.repo = tmp_path / "target"
            self.repo.mkdir()
            self.git("init", "-q", "-b", "main")
            self.git("config", "user.email", "fixture@example.com")
            self.git("config", "user.name", "fixture")
            (self.repo / "README.md").write_text("target repo\n")
            self.git("add", "README.md")
            self.git("commit", "-q", "-m", "initial")

    def git(self, *argv: str, cwd: Path | None = None) -> str:
        cp = subprocess.run(["git", *argv], cwd=cwd or self.repo, capture_output=True, text=True)
        assert cp.returncode == 0, f"git {' '.join(argv)}: {cp.stderr}"
        return cp.stdout

    def repo_rev(self, ref: str) -> str:
        return self.git("rev-parse", ref).strip()

    # --- the store CLI, as the clerk runs it
    def cli(self, *argv: str) -> subprocess.CompletedProcess:
        env = {**os.environ, "FACTORY_STATE": str(self.store), "PYTHONDONTWRITEBYTECODE": "1"}
        if self.repo:
            env["FACTORY_REPO"] = str(self.repo)
            env["FACTORY_INTEGRATION_BRANCH"] = "main"
        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)

    def ticket(self, tid: str) -> dict:
        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())

    def state(self, tid: str) -> str:
        return self.ticket(tid)["status"]

    def results(self, tid: str) -> dict:
        return self.ok("results", "show", tid)["rows"]

    def ready_implementers(self, parent: str) -> list[str]:
        return self.ok("ticket", "ready-implementers", parent)["ready"]

    def parent_check(self, parent: str) -> str:
        return self.ok("ticket", "parent-check", parent)["state"]

    def log(self) -> list[dict]:
        return [json.loads(ln) for p in sorted((self.store / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]

    # --- the humans
    def request(self, text: str) -> str:
        p = self.tmp / f"request-{len(list(self.tmp.glob('request-*.md'))) + 1}.md"
        p.write_text(text)
        return self.ok("ticket", "new", "--file", str(p))["id"]

    def human_runs(self, *argv: str) -> dict:
        return self.ok(*argv)

    def human_approves(self, tid: str) -> None:
        self.ok("approve-spec", tid)

    def human_answers(self, tid: str, text: str) -> None:
        p = self.tmp / f"answer-{tid}-{self.ticket(tid)['history'].__len__()}.md"
        p.write_text(text)
        self.ok("resolve", tid, "--answer", str(p))

    # --- one role run, then the routing table's row for its STATUS (as intake.js does)
    def dispatch(self, role: str, tid: str, stub: str | None = None, finish: bool = True, stub_path: Path | None = None, route: bool = True,
                 file: str = "thing.txt", merge_main: bool = False, no_change: bool = False, killed: bool = False) -> Run:
        self.count[role] = self.count.get(role, 0) + 1
        stub_path = stub_path or STUBS / (stub or f"{self.case}/{role}-{self.count[role]}.md")
        rid = self.ok("run", "start", "--role", role, "--ticket", tid)["run_id"]
        composed = self.ok("run", "compose", rid)
        input_text = (self.store / "runs" / rid / "input.md").read_text()
        if not finish:
            return Run(rid, input_text, composed["sources"], None)
        meta = yaml.safe_load((self.store / "runs" / rid / "meta.yaml").read_text())
        if role == "implementer":  # the stub implementer's one code change, committed on its branch
            wt = Path(meta["worktree"])
            if merge_main:  # a conflict run: merge the integration branch into the branch, nothing else
                self.git("merge", "-q", "--no-edit", "main", cwd=wt)
            elif no_change:
                pass  # an implementer that returns without touching its branch
            else:
                (wt / file).write_text("the thing\n")
                self.git("add", file, cwd=wt)
                self.git("commit", "-q", "-m", f"{tid}: the thing", cwd=wt)
        if killed:  # the run returned nothing (budget kill): no output, a KILLED row
            status = self.ok("run", "finish", rid, "--status-override", "KILLED")["status"]
            self.ok("run", "cleanup", rid)
            self.ok("results", "record", tid, "--head", self.ok("ticket", "head", tid)["head"], "--role", role, "--run", rid, "--killed")
            self.act_on_join(tid, rid)
            return Run(rid, input_text, composed["sources"], status)
        text = stub_path.read_text().replace("Commit: HEAD", f"Commit: {meta.get('head')}")
        (self.store / "runs" / rid / "output.md").write_text(text)
        status = self.ok("run", "finish", rid)["status"]
        if role in ("reviewer", "verifier"):
            self.ok("run", "cleanup", rid)
        if route:
            self.route(role, tid, rid, status, meta)
        return Run(rid, input_text, composed["sources"], status)

    def route(self, role: str, tid: str, rid: str, status: str, meta: dict | None = None) -> None:
        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
        park = lambda reason: self.ok("ticket", "park", tid, "--reason", reason, "--outputs", rid)  # noqa: E731
        if role == "triage":
            {"ACCEPT": lambda: go("ready-for-spec-writer"), "REJECT": lambda: go("closed"),
             "CLARIFY": lambda: go("waiting-requester"), "NEEDS-HUMAN": lambda: park("NEEDS-HUMAN from triage")}[status]()
        elif role == "spec_writer":
            self.ok("spec", "add", tid, "--from-run", rid)  # every version the writer returns is kept
            if status == "NEEDS-HUMAN":
                park("NEEDS-HUMAN from spec writer")
            else:
                assert status in ("READY-FOR-CRITIC", "NEEDS-SPLIT"), status
                go("ready-for-critic", "spec:init")
        elif role == "critic":
            if status == "APPROVE":
                go("awaiting-spec-gate")
            elif status == "ESCALATE":
                park("ESCALATE from critic")
            else:
                assert status == "REVISE", status
                if self.ticket(tid)["round"]["spec"] < MAX_SPEC_ROUNDS:
                    go("ready-for-spec-writer", "spec:+1")
                else:
                    park("max rounds")
        elif role == "planner":
            if status == "PLANNED":
                self.ok("spec", "tasks", tid, "--run", rid)
                self.ok("plan", "add", tid, "--from-run", rid)
                self.ok("subticket", "add", tid, "--run", rid)
                go("planned")
            else:
                park(f"{status} from planner")
        elif role == "implementer":
            if status == "BLOCKED":
                park("BLOCKED from implementer")
            else:
                assert status == "READY-FOR-REVIEW", status
                moved = self.ok("ticket", "head", tid)
                if moved["merge_refused"]:  # a conflict run that did not merge main in: ask the join, skip the checkers
                    self.act_on_join(tid, rid)
                else:
                    go("checks-in-flight", "pr:init")
        elif role in ("reviewer", "verifier"):
            if self.ticket(tid)["status"] == "ready-for-parent-verify":
                # | parent-close | VERIFIED archives the change, then closes; anything else parks the parent |
                if status == "VERIFIED":
                    self.ok("archive", tid)
                    go("closed")
                else:
                    park(f"{status} from parent-close verifier")
                return
            head = self.ok("ticket", "head", tid)["head"]  # as build.js does: the CLI names the head, never the store file
            assert self.ok("ticket", "show", tid, "--json")["head"] == head
            self.ok("results", "record", tid, "--head", head, "--role", role, "--output", str(self.store / "runs" / rid / "output.md"), "--run", rid)
            self.act_on_join(tid, rid)

    def act_on_join(self, tid: str, rid: str | None = None) -> dict:
        """`factory ticket join` decides; the dispatcher (build.js, and this shepherd) only carries it out."""
        go = lambda to, rnd=None: self.ok("ticket", "transition", tid, "--to", to, "--by", "workflow", *(["--round", rnd] if rnd else []))  # noqa: E731
        join = self.ok("ticket", "join", tid)
        self.last_join = join
        if join["decision"] == "merge":
            go("ready-for-merge")
            cp = self.cli("merge", tid)
            if cp.returncode != 0:
                again = self.ok("ticket", "join", tid)
                self.last_join = again
                if again["decision"] == "conflict":
                    go("ready-for-implementer")
                else:
                    self.ok("ticket", "park", tid, "--reason", again["reason"])
        elif join["decision"] == "revise":
            go("ready-for-implementer", join["round_op"])
        elif join["decision"] == "conflict":
            if self.state(tid) != "ready-for-implementer":
                go("ready-for-implementer")
        elif join["decision"] == "park":
            self.ok("ticket", "park", tid, "--reason", join["reason"], *(["--outputs", rid] if rid else []))
        return join  # "wait": the other checker has not reported on this head yet


# ----- a sub-ticket built to merged (test_parent_close_reuse.py) ----------------------------------

def _parent_verifier_runs(f, tid: str) -> list[str]:
    return [p.parent.name for p in (f.store / "runs").glob("*-verifier/meta.yaml")
            if yaml.safe_load(p.read_text())["ticket"] == tid]


def _build(f, st: str, file: str = "thing.txt"):
    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md", file=file)
    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
    assert f.state(st) == "merged"
    return ver
