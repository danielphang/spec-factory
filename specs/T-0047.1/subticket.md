## T-0047.1 / Move the spec-drift checks to factory/drift.py and the shared helpers and live-store fence to factory/common.py
Depends on: none
Parallel-safe: no (it edits `factory/cli.py`, as every sibling does)

Parent: T-0047 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts A and B of the parent's design, under the rules at the top of its Proposed change
(byte-for-byte moves in their original order, a one-line docstring, then
`from __future__ import annotations`, then imports by name, no import of `factory.cli` from a new
module, drop the imports `factory/cli.py` no longer uses, move or drop `# -----` section comments,
no run of three blank lines).
- A: new `factory/drift.py` gets `_check_sibling_tests`, `TEST_FILE_RE`, `TICK_RE`,
  `_check_drift`, `_sibling_drift`, `_test_drift`, `_tests_to_change_section`. `factory/cli.py`
  imports `_check_drift` and `_check_sibling_tests` for `run_start`.
- B: new `factory/common.py` gets `out`, `_rel`, `_integration_head`, `_add_spec_version`,
  `_in_flight`, `fence`. `READ_ONLY` and its comment stay in `factory/cli.py` beside `main`.
  `factory/cli.py` imports `out`, `_rel`, `_add_spec_version` and `fence`, plus anything else of
  these it still calls.

Acceptance:
- NEW: The drift checks live in factory/drift.py.
  WHEN `uv run --frozen python -B -c 'import factory.drift' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/drift.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  THEN it prints exactly `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`
- NEW: The shared helpers and the live-store fence live in factory/common.py.
  WHEN `uv run --frozen python -B -c 'import factory.common' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/common.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  THEN it prints exactly `_add_spec_version _in_flight _integration_head _rel fence out`
- NEW: M (on this sub-ticket's base it prints `pairs=0 added=0 removed=0 lines=0`, which fails "n at least 1").
- REGRESSION: R1 to R19.
- Intermediate check (NEW): each new module loads first in a fresh interpreter, which catches an
  import cycle. WHEN `uv run --frozen python -B -c 'import factory.drift' && uv run --frozen python -B -c 'import factory.common'` THEN it exits 0 and prints nothing.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/common.py`, `factory/drift.py`
Out of scope: parts C, D and E; any rename, including making an underscored name public; any
change to a moved body; any change under `tests/`; any doc change.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: T-0047, approved spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`).

## How the parts were grouped, and why

The spec has five lettered parts, A to E. This plan makes four sub-tickets: A and B (the two
smallest moves, about 120 and 60 lines, and the only two that need nothing) go together in one,
and C, D and E get one each. Merging A with B saves one serial implementer, reviewer and verifier
cycle. It does not make review harder, because whether code was moved without being rewritten is
checked by a script, not by a reader. Keeping C, D and E separate means each pull request moves one
job's code (about 330, 250 and 300 lines), and each can be rolled back on its own.

Every part edits `factory/cli.py`, so no two sub-tickets can run at the same time. The plan
is therefore one chain: .1, then .2, then .3, then .4. Two of the links are only about order: the
spec says C needs only B, and D needs only B. The chain also has a real dependency at the end:
.4's check that `factory/cli.py` is under 900 lines can only pass once C, D and E have all merged.

Checked on `main` at `6203096` (the base the spec's line numbers are on, and still `main`'s tip):
- `factory/cli.py` is 2,020 lines. Spot checks of the cited anchors (`out` 30, `_rel` 34,
  `_check_sibling_tests` 249, `TEST_FILE_RE` 276, `_integration_head` 548, `ticket_head` 830,
  `MAX_CONFLICT_RUNS` 1005, `_git_toplevel` 1294, `STATE_DIR_LINE` 1482, `paths_cmd` 1613,
  `stats_cmd` 1627, `_verifier_rows` 1666, `archive_cmd` 1728, `READ_ONLY` 1960, `_in_flight` 1964,
  `fence` 1970) all match the spec.
- The drift code (lines 249-370) calls none of the helpers that move to `factory/common.py`, so
  part A does not depend on part B. The setup code (1294-1624) calls `fence`, `_in_flight` and
  `out`, so part C does depend on part B, as the spec says.
- Every scenario labelled REGRESSION below was run on `main` and passes there:
  `uvx ruff check --select F factory` and `uvx ruff check --select F401,F841 factory tests` both
  print `All checks passed!` (run with a throwaway HOME). The grep-based checks print `0 2 2`
  (run start), `1 1` (status transition), `0 1 1 1` (record copies), `0` (runs listing),
  `0 1` (event log), `0` (in-flight list), and the CLI importers are exactly
  `factory/__main__.py factory/drive.py factory/stats.py`. The docs check prints `0 1 0 1 `.
  I did not run the harness suite on `main`.

Line numbers shift after each merge. Every sub-ticket after .1 should find each definition by its
name, not by the line number the spec gives.

The shared regression set (`R`) below is the list of scenarios that every sub-ticket must keep
passing. Each sub-ticket's Acceptance names `R` and lists only what it adds to it.

### Shared regression set R (every sub-ticket; all REGRESSION against every sub-ticket's base)

Run from the checkout's repository root after `uv sync --frozen`, with `git` on `PATH`, each
through the "Running code" wrapper.

- R1. Only the entry point, the driver and the stats report import the CLI module.
  WHEN `grep -lE '^\s*(from factory\.cli import|import factory\.cli|from factory import ([^#]*, )?cli\b)' factory/*.py | paste -sd' ' -`
  THEN it prints exactly `factory/__main__.py factory/drive.py factory/stats.py`
- R2. The CLI's entry points stay importable.
  WHEN `uv run --frozen python -B -c 'import factory.cli, factory.drive, factory.stats; from factory.cli import main, build_parser, ROLES; print(len(ROLES), callable(main), callable(build_parser))'`
  THEN it prints exactly `7 True True`
- R3. The split harness has no undefined, unused or redefined names.
  WHEN `uvx ruff check --select F factory`
  THEN it prints `All checks passed!` and exits 0
- R4. After the split the harness suite passes with no test file changed.
  WHEN `(P=$(mktemp -d /tmp/t0047-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only main...HEAD -- tests)`
  THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it.
  (The spec notes one test of two concurrent checker runs failed once under load on the
  prototype and passed on rerun; a rerun is not a weakening, a repeat failure is a failure.)
- R5. The four dead definitions are gone and nothing names them.
  WHEN `echo "$(grep -nE '^(def run_gates\(|STATES = |OPS = |def load_config\()' factory/gitops.py factory/store.py factory/specstore.py | wc -l | tr -d ' ') $(grep -rnF --include='*.py' -e 'gitops.run_gates' -e 'store.STATES' -e 'specstore.OPS' -e 'store.load_config' factory tests | wc -l | tr -d ' ')"`
  THEN it prints `0 0`
- R6. No harness or test file names the force-push setting.
  WHEN `grep -rn --exclude-dir=__pycache__ force_push_allowed factory tests | wc -l | tr -d ' '`
  THEN it prints `0`
- R7. Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write.
  WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c prompt_name) $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c "already has run {t\[.in_flight.\]\[0\]} in flight") $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'store.ensure_gitignore(root)')"`
  THEN it prints `0 2 2`
- R8. No harness module has three blank lines in a row.
  WHEN `awk 'FNR==1{n=0} /^$/{n++; if(n==3) print FILENAME":"FNR; next} {n=0}' factory/*.py | wc -l | tr -d ' '`
  THEN it prints `0`
- R9. The three stale texts are gone.
  WHEN `grep -nF -e 'commit-and-push' -e 'live pilot store is unaffected' -e 'not supported yet' factory/*.py | wc -l | tr -d ' '`
  THEN it prints `0`
- R10. The repo-root helper takes no argument and every caller passes none.
  WHEN `echo "$(grep -n 'repo_root(cfg' factory/*.py | wc -l | tr -d ' ') $(grep -o 'gitops.repo_root()' factory/*.py | wc -l | tr -d ' ') $(grep -c '^def repo_root() -> Path:$' factory/gitops.py)"`
  THEN it prints `0 12 1`
- R11. The harness has no unused imports or variables.
  WHEN `uvx ruff check --select F401,F841 factory tests`
  THEN it prints `All checks passed!` and exits 0
- R12. The harness suite passes, and only the force-push test lines change under tests.
  WHEN `(P=$(mktemp -d /tmp/t0044-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only main...HEAD -- tests)`
  THEN the first line reports a number of passed tests and no `failed` or `error`, and every later line, if any, is `tests/factory/fixtures/instance/instance.yaml` or `tests/factory/test_instance.py`
- R13. Only the store module lists a ticket's runs.
  WHEN `cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py factory/compose.py factory/specstore.py 2>/dev/null | grep -cE 'runs\.(iterdir|glob)\(|"runs"\)\.(iterdir|glob)\('`
  THEN it prints `0`
- R14. The CLI and the stats report read the event log through a shared reader.
  WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py factory/stats.py 2>/dev/null | grep -c '"\*\.jsonl"') $(grep -c '"\*\.jsonl"' factory/store.py)"`
  THEN it prints `0 1`
- R15. One function records a status transition outside spec approval.
  WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c '"ticket\.transition"') $(grep -c '"ticket\.transition"' factory/store.py)"`
  THEN it prints `1 1`
- R16. Neither spec amend nor the dispatcher builds the in-flight list itself.
  WHEN `cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py factory/drive.py 2>/dev/null | grep -cE 'for \w+ in \(t, \*'`
  THEN it prints `0`
- R17. One function reads the integration-branch tip.
  WHEN `echo "$(cat factory/*.py | grep -cE 'rev\(repo, (gitops\.)?integration_branch\(') $(grep -c '^def integration_tip(' factory/gitops.py)"`
  THEN it prints `1 1`
- R18. Record copies, row set-asides, planner-run checks and spec apply checks each have one definition.
  WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'shutil\.copyfile(a\.') $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c '"results\.superseded"') $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'is not a PLANNED planner run') $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'specstore\.applies(root, deltas)')"`
  THEN it prints `0 1 1 1`
- R19. One line formats a failed-command park and one call cleans up a checker.
  WHEN `echo "$(grep -cE "harness-bug: .*stderr" factory/drive.py) $(grep -c 'call("run", "cleanup"' factory/drive.py) $(grep -cE '^def _(harness_bug|cleanup_checker)\(' factory/drive.py)"`
  THEN it prints `1 1 2`

The "moved, not rewritten" check (`M` below) is the parent's scenario "Every definition keeps its
exact text, and the split adds at most 100 lines". Its GIVEN step writes
`${TMPDIR:-/tmp}/t0047-moved.py` from the script block in that scenario of the parent spec
(`specs/harness-code/spec.md`), copied verbatim and run once at column 0.
- M. WHEN `(uv run --frozen python -B ${TMPDIR:-/tmp}/t0047-moved.py)`
  THEN it prints one line, `pairs=<n> added=0 removed=0 lines=<l>`, with n at least 1 and l at most 100, and nothing after it.
  The 100-line limit covers all four sub-tickets together, because the script adds up every
  earlier `Merge factory/T-0047.<n>` commit. The spec's prototype used 60 lines. As a guide, each
  sub-ticket should add no more than its module's docstring, `from __future__ import annotations`
  and its import lines, less the imports `factory/cli.py` no longer needs.

---
