## MODIFIED Requirements

### Requirement: Sharing an operation changes no refusal, park reason, event or parse result
After the operations above are shared, every command MUST print the same refusals, write the same events, history entries and park reasons, and parse every spec the same way as before, and the existing harness tests SHALL pass with no existing test file changed.

#### Scenario: Status transitions write the same events and history entries
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0046-store.sh <<'EOF'
# Sourced from the repo root: a throwaway store (the suite's fixture instance) whose T-0001 is
# awaiting the spec gate with a one-line spec, and a stand-in `claude` that fails if ever called.
# Leaves T set. Every command's output is discarded.
T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance
export FACTORY_REPO=$T/none FACTORY_INTEGRATION_BRANCH=main PYTHONDONTWRITEBYTECODE=1 LOGNAME=op; unset FACTORY_DISPATCH
mkdir $T/bin && printf '#!/bin/sh\necho "{}"; exit 1\n' > $T/bin/claude && chmod +x $T/bin/claude && export PATH=$T/bin:$PATH
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && printf '## Problem\nx\n' > $T/spec.md
bin/factory ticket new --file $T/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0046-reason.py <<'EOF'
# uv run --frozen python t0046-reason.py <store> <ticket>: the ticket's park reason, as a Python
# literal, with the store's scratch directory written as <T>.
import os, sys, yaml
t = yaml.safe_load(open(os.path.join(sys.argv[1], "tickets", sys.argv[2] + ".yaml")))
print(sys.argv[2], repr((t.get("parked") or {}).get("reason")).replace(os.path.dirname(sys.argv[1]), "<T>"))
EOF
cat > ${TMPDIR:-/tmp}/t0046-specstore.py <<'EOF'
# uv run --frozen python t0046-specstore.py, from the repo root: runs the spec parser of the merge
# base of HEAD and main and the checkout's own over every spec version, change part and
# current-truth file in this repo's store, and counts the calls whose result (or raised exception
# type) differs. Prints `files=<n> checks=<m> differ=<k>`, then up to five differing calls.
import glob, importlib.util, os, subprocess, sys, tempfile
sys.path.insert(0, os.getcwd())
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
def load(name, src):
    p = os.path.join(tempfile.mkdtemp(), name + ".py"); open(p, "w").write(src)
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old = load("t0046_old", git("show", git("merge-base", "HEAD", "main").strip() + ":factory/specstore.py"))
new = load("t0046_new", open("factory/specstore.py", encoding="utf-8").read())
S = os.path.join(os.path.dirname(git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()), ".factory", "store")
files = sorted(glob.glob(S + "/specs/*/v*.md") + glob.glob(S + "/openspec/**/*.md", recursive=True))
truths = sorted(glob.glob(S + "/openspec/specs/*/spec.md"))
def res(m, fn, a):
    try: return repr(getattr(m, fn)(*a))
    except Exception as e: return "raised " + type(e).__name__
checks, differ = 0, []
for path in files:
    t = open(path, encoding="utf-8").read(); parts = dict(old.split_parts(t)); ops = old.parse_delta(t)[0]
    calls = [("validate", (t,)), ("intent_of", (t,)), ("scenario_blocks", (t,)), ("requirement_blocks", (t,)),
             ("parse_delta", (t,)), ("decisions_of", (parts.get("proposal.md", t),)),
             ("acceptance_labels", (parts.get("verification.md", t),))]
    if any(ops.values()):
        calls += [("apply_delta", (open(c, encoding="utf-8").read(), os.path.basename(os.path.dirname(c)), ops)) for c in truths]
    for fn, a in calls:
        checks += 1
        if res(old, fn, a) != res(new, fn, a):
            differ.append(f"{fn} {os.path.relpath(path, S)}")
print(f"files={len(files)} checks={checks} differ={len(differ)}")
for d in differ[:5]: print(d)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: ST-1\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket ready-implementers T-0001 >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null && bin/factory ticket parent-check T-0001 >/dev/null && bin/factory log tail --event ticket.transition -n 50 | sed 's/^{"ts": "[^"]*", /{/' && uv run --frozen python -c "import glob, sys, yaml; [print(p.rsplit('/', 1)[1][:-5], {k: v for k, v in h.items() if k != 'ts'}) for p in sorted(glob.glob(sys.argv[1] + '/tickets/*.yaml')) for h in yaml.safe_load(open(p))['history']]" $FACTORY_STATE)`
- THEN it prints exactly these 14 lines:

```
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-triage", "to": "ready-for-spec-writer", "by": "t", "round": {"spec": 0, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-spec-writer", "to": "ready-for-critic", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-critic", "to": "awaiting-spec-gate", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-planner", "to": "planned", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001.2", "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "planned", "to": "ready-for-parent-verify", "by": "parent-check"}
T-0001.2 {'from': 'waiting-dependencies', 'to': 'ready-for-implementer', 'by': 'ready-implementers'}
T-0001 {'from': 'ready-for-triage', 'to': 'ready-for-spec-writer', 'by': 't', 'round': {'spec': 0, 'pr': 0}}
T-0001 {'from': 'ready-for-spec-writer', 'to': 'ready-for-critic', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'ready-for-critic', 'to': 'awaiting-spec-gate', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'awaiting-spec-gate', 'to': 'ready-for-planner', 'by': 'op', 'approved_version': 1}
T-0001 {'from': 'ready-for-planner', 'to': 'planned', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'planned', 'to': 'ready-for-parent-verify', 'by': 'parent-check'}
```

#### Scenario: Spec pinning and planner-run refusals keep their text
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && mkdir $T/s/openspec && bin/factory approve-spec T-0001 2>/dev/null | tail -1; rmdir $T/s/openspec && bin/factory approve-spec T-0001 >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0002 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p') && bin/factory subticket add T-0001 2>/dev/null | tail -1; bin/factory subticket add T-0001 --run $R 2>/dev/null | tail -1; bin/factory spec tasks T-0001 --run $R 2>/dev/null | tail -1)`
- THEN it prints exactly these 4 lines:

```
{"ok": false, "error": "spec not pinned: no `=== <path>` part lines"}
{"ok": false, "error": "no recorded planner run found for T-0001 (latest plan.added source: none); pass --run RUN or --file F"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
```

#### Scenario: The dispatcher parks a refused store command with the same reason
Needs the GIVEN block of "Status transitions write the same events and history entries" run once. `factory drive` runs for real on the throwaway store. T-0001.1's implementer run start is refused because the target repository does not exist. T-0001.2 sits at its checks with no branch. T-0002 is at its planner with no approved spec.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.2 status=checks-in-flight >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && bin/factory ticket set T-0002 status=ready-for-planner >/dev/null && bin/factory drive T-0001 --phase build >/dev/null 2>&1; bin/factory drive T-0002 --phase build >/dev/null 2>&1; for x in T-0001.1 T-0001.2 T-0002; do uv run --frozen python ${TMPDIR:-/tmp}/t0046-reason.py $FACTORY_STATE $x; done)`
- THEN it prints exactly these 3 lines:

```
T-0001.1 "harness-bug: run start implementer: factory: FileNotFoundError: [Errno 2] No such file or directory: PosixPath('<T>/none')\n"
T-0001.2 'harness-bug: no head for the checkers: T-0001.2 has no branch yet\n'
T-0002 'harness-bug: plan whole-spec: T-0002 has no approved spec\n'
```

#### Scenario: The spec parser gives the same result as the base on every spec in the store
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(uv run --frozen python ${TMPDIR:-/tmp}/t0046-specstore.py)`
- THEN it prints one line, `files=<n> checks=<m> differ=0`, with n and m above 0, and nothing after it

#### Scenario: The refactored harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes and no existing test file changes
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0046-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it

### Requirement: The command-line code has one module per job
The harness's command-line code SHALL be split by job: the spec-drift checks in
`factory/drift.py`, setup in `factory/setup.py`, the gates in `factory/gates.py`, the human
decisions in `factory/human.py`, the current-truth replay in `factory/truth.py`, and the helpers more than one of them uses, with the live-store
fence, in `factory/common.py`. `factory/cli.py` MUST keep the parser, the entry point and the role
list, and be under 910 lines.

Run every command of this change from the repository root of the checkout under test, after
`uv sync --frozen`, with `git` on `PATH`.

#### Scenario: The drift checks live in factory/drift.py
- WHEN `uv run --frozen python -B -c 'import factory.drift' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/drift.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`

#### Scenario: The shared helpers and the live-store fence live in factory/common.py
- WHEN `uv run --frozen python -B -c 'import factory.common' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/common.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `_add_spec_version _in_flight _integration_head _rel fence out`

#### Scenario: Instance and store setup live in factory/setup.py
- WHEN `uv run --frozen python -B -c 'import factory.setup' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/setup.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`

#### Scenario: The gates live in factory/gates.py
- WHEN `uv run --frozen python -B -c 'import factory.gates' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/gates.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`

#### Scenario: The human decisions live in factory/human.py
- WHEN `uv run --frozen python -B -c 'import factory.human' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/human.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add escape_add intervention_add request_changes resolve spec_amend`

#### Scenario: factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines
- WHEN `echo "$(wc -l < factory/cli.py | tr -d ' ') $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"`
- THEN it prints two numbers: the first below 910, the second `3`

