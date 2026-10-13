## ADDED Requirements

### Requirement: One harness-suite run finishes in under three minutes
One run of the harness suite, as `.venv/bin/python -m pytest -q -p no:cacheprovider tests/factory` runs it after `uv sync --frozen`, SHALL pass every test and finish in under 180 seconds on the operator's machine.

#### Scenario: One suite run passes in under three minutes
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the script written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0051-time.py <<'EOF'
# .venv/bin/python t0051-time.py N LIMIT CMD...: from the checkout under test, starts N copies of the shell
# command CMD at once, each with its own fresh TMPDIR under /tmp, and stops any copy still running
# LIMIT seconds after the start. Prints one line per copy, in order: its output's last line, or
# `stopped`, then ` | under LIMIT s` or ` | over LIMIT s` by its own wall time.
import os, shutil, subprocess, sys, tempfile, time
n, limit, cmd = int(sys.argv[1]), float(sys.argv[2]), " ".join(sys.argv[3:])
t0, runs = time.monotonic(), []
for _ in range(n):
    d = tempfile.mkdtemp(prefix="t0051-time.", dir="/tmp")
    runs.append((d, subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                     env={**os.environ, "TMPDIR": d}, start_new_session=True)))
for d, p in runs:
    try:
        out, _ = p.communicate(timeout=max(0.1, limit - (time.monotonic() - t0)))
        last, took = (out.strip().splitlines() or [""])[-1], time.monotonic() - t0
    except subprocess.TimeoutExpired:
        os.killpg(p.pid, 9); p.communicate(); last, took = "stopped", limit + 1
    shutil.rmtree(d, ignore_errors=True)
    print(f"{last} | {'under' if took < limit else 'over'} {limit:g} s")
EOF
```

- WHEN `.venv/bin/python ${TMPDIR:-/tmp}/t0051-time.py 1 180 .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory`
- THEN it prints one line that reports a number of passed tests, contains no `failed` or `error`, and ends with `| under 180 s`

### Requirement: Two harness-suite runs at once each finish in under five minutes
Two runs of the harness suite started at the same moment SHALL each pass every test and finish in under 300 seconds on the operator's machine.

#### Scenario: Two suite runs at once each pass in under five minutes
Needs the GIVEN block of "One suite run passes in under three minutes" run once.
- WHEN `.venv/bin/python ${TMPDIR:-/tmp}/t0051-time.py 2 300 .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory`
- THEN it prints two lines, each of which reports a number of passed tests, contains no `failed` or `error`, and ends with `| under 300 s`

### Requirement: The suite's stand-in agent replies when several copies of one role start at once
Each stand-in for the `claude` program that the harness suite's driver tests use MUST reply with its JSON object and exit 0 when several copies of the same role start at the same moment and share one log.

#### Scenario: Four stand-ins of one role started together all reply, 200 times over
The script names the suite's helper module and its two stand-in programs, because this ticket's subject is the suite's own reliability (as the standing 2026-10-12 T-0045 decision allows for the suite's structure).
- GIVEN the script written by the block below, run once at column 0 as shown

```sh
cat > ${TMPDIR:-/tmp}/t0051-standin.py <<'EOF'
# .venv/bin/python t0051-standin.py, from the checkout under test: for each stand-in `claude` of the
# harness suite (the intake one and the build one), 200 times, starts four copies of the same role
# at once from four run directories that share one log, as the driver does for the checkers of four
# sub-tickets. Prints `<stand-in>: 200 rounds, <n> with a copy that did not reply, counter <c>`, where
# a copy that did not reply exited non-zero or printed no JSON object, and <c> is the stand-in's own
# count of verifier calls at the end (800 when no call was lost).
import json, os, subprocess, sys, tempfile, pathlib
sys.path.insert(0, "tests")
from factory import _fixtures as F  # the suite's helper module (tests/factory/_fixtures.py)
for name in ("STANDIN", "BUILD_STANDIN"):
    t = pathlib.Path(tempfile.mkdtemp()); exe = t / "claude"
    exe.write_text(getattr(F, name).format(python=sys.executable)); exe.chmod(0o755)
    env = {**os.environ, "STANDIN_LOG": str(t / "claude.log"), "STANDIN_PLAYS": json.dumps({"verifier": [{"say": "x"}]})}
    bad = 0
    for i in range(200):
        dirs = [t / f"r{i}" / f"run-000{k}-verifier" for k in (1, 2, 3, 4)]
        for d in dirs:
            d.mkdir(parents=True)
        ps = [subprocess.Popen([str(exe)], cwd=d, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for d in dirs]
        res = [(p.wait(), p.stdout.read()) for p in ps]
        def replied(rc, out):
            try:
                return rc == 0 and isinstance(json.loads(out), dict)
            except ValueError:
                return False
        bad += not all(replied(rc, out) for rc, out in res)
    nf = t / "claude.log.n-verifier"
    print(f"{name}: 200 rounds, {bad} with a copy that did not reply, counter {nf.read_text().strip() if nf.exists() else 'none'}")
EOF
```

- WHEN `.venv/bin/python -B ${TMPDIR:-/tmp}/t0051-standin.py`
- THEN it prints exactly `STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800`, then `BUILD_STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800`

### Requirement: This change keeps every test and assertion but the two the waiting park reason changes
Across this change's own merges and unmerged commits, the harness suite SHALL lose no test, and every assert statement in every existing test function MUST still be present in that function, except the two assertions listed under Tests to change.

#### Scenario: No test is removed and only the two listed assertions change
The command compares each `Merge factory/T-0051.<n>` commit reachable from HEAD with its first parent, and `git merge-base HEAD main` with HEAD, and adds up the results, so changes other tickets make to the same files are never counted. A collection failure shows as removed tests. tar may print a locale warning on stderr; it is not part of the result.
- WHEN `T=$(mktemp -d); { for m in $(git log --format=%H --grep='^Merge factory/T-0051[.]' HEAD); do echo "$(git rev-parse "$m^1") $m"; done; echo "$(git merge-base HEAD main) $(git rev-parse HEAD)"; } | while read b h; do [ "$b" = "$h" ] && continue; for s in $b $h; do [ -d "$T/$s" ] || { mkdir "$T/$s" && git archive "$s" | tar -x -C "$T/$s" && ln -s "$PWD/.venv" "$T/$s/.venv" && (cd "$T/$s" && PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest --collect-only -q -p no:cacheprovider tests/factory 2>&1 | grep '::' | sort > ids); }; done; echo "pair $b $h"; comm -23 "$T/$b/ids" "$T/$h/ids" | sed 's/^/removed /'; comm -13 "$T/$b/ids" "$T/$h/ids" | sed 's/^/added /'; .venv/bin/python -c 'import ast,pathlib,sys; A=lambda r: {f"{p.name}::{n.name}": {ast.unparse(a) for a in ast.walk(n) if isinstance(a,ast.Assert)} for p in sorted(pathlib.Path(r,"tests/factory").glob("test_*.py")) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name.startswith("test_")}; b,h=A(sys.argv[1]),A(sys.argv[2]); [print(f"missing {k}: {a[:80]}") for k in sorted(b) for a in sorted(b[k]-h.get(k,set()))]' "$T/$b" "$T/$h"; done > "$T/out"; for k in pair removed added missing; do echo "$k: $(grep -c "^$k " "$T/out")"; grep "^$k " "$T/out" | grep -v '^pair '; done; rm -rf "$T"`
- THEN `pair:` is at least 1; it prints `removed: 0`; every `added` line names a test in `tests/factory/test_empty_output.py`; and it prints `missing: 2`, followed by exactly one line that starts `missing test_drive.py::test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message: assert parked['reason'] == 'EMPTY-OUTPUT from triage'` and one that starts `missing test_empty_output.py::test_last_message_is_kept_for_an_empty_output_run: assert res == {'ok': True, 'run_id': s.rid, 'last_message':`

