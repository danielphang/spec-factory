## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0494-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0494-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0494-reviewer/wt` (branch `factory/T-0047.4`, base `43265a02f3ad943ebed963d7246495418c3d2ee8`, head `9349e5762e727e570bf0bd0e7ceb90c865387a71`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0047.4

## T-0047.4 / Move the human decisions to factory/human.py, leaving factory/cli.py under 900 lines
Depends on: T-0047.3
Parallel-safe: no (it edits `factory/cli.py`, and imports from `factory.gates` (T-0047.3) and `factory.common` (T-0047.1); its line-count check needs every earlier part merged)

Parent: T-0047 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part E of the parent's design, under the same move rules. New `factory/human.py` gets
`_restart_note`, `spec_amend`, `_by`, `_approval_dir`, `_next_n`, `_refuse_unless_applies`,
`_copy_record`, `approve_spec`, `request_changes`, `resolve`, `_supersede`,
`_set_aside_failed_rows`, `decision_add`. It imports `_branch_tip` and `undeclared_protected` from
`factory.gates`, and `out`, `_rel`, `_add_spec_version` and `fence` from `factory.common`.
`factory/cli.py` imports the moved commands for `build_parser`.

Acceptance:
- NEW: The human decisions live in factory/human.py.
  WHEN `uv run --frozen python -B -c 'import factory.human' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/human.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  THEN it prints exactly `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend`
- NEW: factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines.
  WHEN `echo "$(wc -l < factory/cli.py | tr -d ' ') $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"`
  THEN it prints two numbers: the first below 900, the second `3`
- REGRESSION: the parent's drift, common, setup and gates module scenarios and the README and
  principles scenario, with the commands and results given under T-0047.1, T-0047.2 and T-0047.3.
- REGRESSION: M (its total `lines` across all four sub-tickets stays at most 100).
- REGRESSION: R1 to R19. R15, R16 and R18 count across all six modules, so `approve_spec`,
  `spec_amend` and the record-copy, set-aside, planner-run and apply checks still count once
  they sit in `factory/human.py`.
- Intermediate check (NEW): WHEN `uv run --frozen python -B -c 'import factory.human'` THEN it
  exits 0 and prints nothing.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/human.py`
Out of scope: parts A to D; moving the ticket, run, spec or plan commands; any rename; any
change to a moved body; any change under `tests/`; any doc change.

---

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

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`

=== proposal.md
## Problem

The harness is the program that enforces the factory's rules: which state a ticket may move to,
when a merge is allowed, and who may write the store, the factory's on-disk record of tickets and
runs. Almost all of its commands live in one file, `factory/cli.py`. That file is 2,020 of the
harness's 5,073 lines of Python.

The file mixes five jobs that have little to do with each other:

| Job | What it does |
|---|---|
| Ticket and run bookkeeping | creates tickets, moves them between states, starts and finishes role runs (one agent working one step of a ticket) |
| Spec-drift checks | before a build agent starts, refuse when the code has moved away from what the approved spec assumed |
| Setup | prepare a repository for the factory and create or move its store |
| Gates | record review and verification results, and refuse a merge or a ticket close that they do not support |
| Human decisions | the commands a person uses to approve a spec, send it back, or rule on a stopped ticket |

This costs the agents that build harness changes, and the people who review those changes. An
agent asked to change one gate reads the whole 2,020-line file into its context. A reviewer of a
merge-gate change has to find it among setup and bookkeeping code. Every harness ticket that
touches a refusal, a gate or a human command edits this one file.

This change moves the code into one module per job and leaves `factory/cli.py` with the command
parser, the entry point and the bookkeeping commands. Nothing a command does changes: every
refusal message, exit code, logged event and printed result stays the same. The change saves no
lines. Its gain is that each job can be found, read and changed on its own.

## Root cause

`factory/cli.py` was the first module of the harness, and each build part added its commands to
it. Its docstring still reads "P0 subset of the build-harness spec, part B/K".
`dev/build-harness.plan.md` records that every sub-ticket of that build edited it. Nothing has
moved commands out since. The file is organised only by `# -----` section comments.

## Out of scope

- Any change to what a command does: its refusals, exit codes, events, records and printed JSON.
- The difference between `merge_cmd`, under which a closed sibling releases its dependants, and
  `ready_implementers`, under which a sibling must be merged. This is filed separately as a
  question.
- Retiring the no-spec-store (P0) mode, and deleting `store migrate` (#83 part D).
- Renaming any definition, including making an underscored helper public.
- Moving the ticket, run, spec and plan commands, which stay in `factory/cli.py`.
- Any change under `tests/`.
- `dev/build-harness.spec.md` and `dev/build-harness.plan.md`, which are build history.

## Open questions

none

## Decisions

1. The command-line code becomes six modules. `factory/cli.py` keeps the parser, the entry point,
   the role lists and the ticket, run, spec and plan commands. The five new modules are:
   - `factory/drift.py` for the spec-drift checks;
   - `factory/setup.py` for `init`, `store migrate` and `paths`;
   - `factory/gates.py` for results, the merge gate, join, the parent check and archive;
   - `factory/human.py` for `approve-spec`, `request-changes`, `resolve`, `decision add` and
     `spec amend`;
   - `factory/common.py` for the helpers more than one module calls, and the live-store fence.
     The fence refuses a write to the live store from inside a role run.

   The names follow the request. `setup.py` is kept because no build tool reads it (Evidence).
2. `fence` and `_in_flight` go to `factory/common.py`. Rejected: `factory/instance.py`, where the
   body of `fence` would change (Evidence). Also rejected: a sixth module, which would add a
   header for two functions.
3. `ticket_head` goes to `factory/gates.py`. It reports the commit that the checkers review and
   verify, and the gates record their results against that commit. Without it, `factory/cli.py`
   ends at about 906 lines (Evidence).
4. `stats_cmd` stays in `factory/cli.py`, where its comment about `ROLES` is true. `paths_cmd`
   moves to `setup.py`, as the request asks.
5. Each module imports what it uses by name, for example `from factory.common import _rel, out`.
   No function body changes, so a moved function reads exactly as it did. Rejected: importing the
   module and qualifying each call, such as `common.out(...)`, which edits nearly every body.
   Underscored names keep their underscore when another module imports them.
6. `factory/setup.py` uses `import shutil` and keeps calling `shutil.copy2` through the module.
   The test that replaces `shutil.copy2` therefore still reaches the moved code.
7. The rule that a move is not a rewrite is checked by machine. Across this change, every
   top-level function, class and assignment of `factory/*.py` must keep its exact source text.
   The comparison covers each of this ticket's merges and the checked-out branch, as T-0045's
   suite checks do. Other tickets' changes are therefore never counted.
8. The request's "within ±50 total Python lines" becomes "at most 100 lines added". The
   prototype, with one-line docstrings, added 60 lines: five module headers of imports, less the
   imports `factory/cli.py` no longer needs. With rule 7 in place, the line bound only limits
   header growth. Rejected: ±50, which would push the implementer to cut docstrings.
9. Acceptance names modules, functions and constants. The subject of this ticket is where code
   lives, so those names are the behaviour checked. T-0045 decided the same for the test suite's
   helpers.
10. The six harness-code checks that count text in `factory/cli.py` now count it across
    `factory/cli.py` and the five new modules (Evidence). The expected numbers do not change.
    Rejected: leaving them, which fails three and empties three.
11. Docs: `README.md:1171` and `docs/principles.md:106-107` name `factory/gates.py` for the moved
    gate commands. The README status date moves to the day of the change, as "Maintaining this
    page" asks. Every other doc line that names `factory/cli.py` stays true and is left alone.
12. Standing: no harness module imports `factory.cli` except the entry point (`__main__.py`), the
    driver (`drive.py`) and the stats report (`stats.py`). A command that a new module needs comes
    from that module's own imports. This states the request's rule with the third importer, which
    the request left out.

## Risk

Blast radius: every command of the harness.

- A moved function whose module lacks an import fails only when the function runs. `ruff`'s
  undefined-name check (F821) and the suite catch this.
- An import cycle fails as soon as a module loads. Each new module is imported first in a fresh
  interpreter, and none imports `factory.cli`.
- The suite replaces two functions while it runs (Evidence). Neither patch point moves out of
  reach.
- Every part edits `factory/cli.py`, so the parts cannot be built in parallel.
- Any other ticket that edits `factory/cli.py` while this one is in flight will conflict with it.
- The running factory is unaffected until the operator upgrades the runtime.

Protected paths: `factory/cli.py`, `factory/common.py`, `factory/drift.py`, `factory/gates.py`, `factory/human.py`, `factory/setup.py`

## Operator steps

After the last part merges, the running factory picks up the split at the next runtime upgrade,
accepted with `--accept-harness` as usual. No other step is needed.

=== design.md
## Proposed change

Every part follows the same rules:

- Move each definition named below from `factory/cli.py` to its module, byte for byte. Keep the
  definitions in the order they had in `factory/cli.py`.
- Give each new module a one-line docstring that says its job, then
  `from __future__ import annotations`, then the imports its definitions use. Import other moved
  definitions by name from their new module, as in `from factory.common import _rel, out`.
- Never import `factory.cli` from a new module.
- In `factory/cli.py`, import by name what it still calls, and drop each import nothing uses any
  more.
- Move a `# -----` section comment with its code, or drop it where its section is now empty.
- Leave no run of three blank lines.

Line numbers are on `main` at `6203096`. Each part must leave the suite passing. The parts are in
build order, and each needs the ones before it as noted.

**A. `factory/drift.py`, the spec-drift checks.** Needs nothing. Moves `_check_sibling_tests`
(249-273), `TEST_FILE_RE` and `TICK_RE` (276-277), `_check_drift` (280-296), `_sibling_drift`
(299-318), `_test_drift` (321-358) and `_tests_to_change_section` (361-370). `factory/cli.py`
imports `_check_drift` and `_check_sibling_tests` for `run_start`.

**B. `factory/common.py`, shared helpers and the live-store fence.** Moves `out` (30-31), `_rel`
(34-35), `_integration_head` (548-554), `_add_spec_version` (557-567), `_in_flight` (1964-1967) and
`fence` (1970-1988). `READ_ONLY` and its comment stay in `factory/cli.py` beside `main`, which
reads it. `factory/cli.py` imports `out`, `_rel`, `_add_spec_version` and `fence`.

**C. `factory/setup.py`, setup.** Needs B. Moves `_git_toplevel` through `paths_cmd` (1294-1624):
`_git_toplevel`, `_new_instance_yaml`, `_revision`, `_refuse_inside_store`, `_head_branch`,
`_add_store_checkout`, `_exclude_store`, `_store_hint`, `init_cmd`, `STATE_DIR_LINE`,
`_ignored_files`, `_copy_mismatch`, `store_migrate` and `paths_cmd`. It uses `import shutil` for
`shutil.copy2` (Decision 6). `stats_cmd` stays (Decision 4).

**D. `factory/gates.py`, the gates, and the two doc lines.** Needs B. Moves `ticket_head`
(830-851), `results_record` (854-891), `results_show` (894-899), `DECLARED_RE` (902), `_in_repo`
(905-907), `declared_paths` (910-922), `undeclared_protected` (925-943), `_branch_tip` (946-951),
`merge_cmd` (954-1000), `REVIEWER_STATUSES`, `VERIFIER_STATUSES` and `MAX_CONFLICT_RUNS`
(1003-1005), `ticket_join` (1008-1045), `ticket_parent_check` (1048-1061), `_verifier_rows`
(1666-1676), `_reused_subticket_run` (1679-1708), `_parent_close_verified` (1711-1725) and
`archive_cmd` (1728-1741). `factory/cli.py` imports `_parent_close_verified` for
`ticket_transition`, and the commands for `build_parser`. Docs, in the same part:
- `README.md:1171`: replace "`factory/cli.py` `ticket_join`, `merge_cmd`, `archive_cmd`" with
  "`factory/gates.py` `ticket_join`, `merge_cmd`, `archive_cmd`".
- `README.md:9`: set the status date to the day of the change.
- `docs/principles.md:106-107`: replace "the guards in `factory/cli.py`:" and the next line's
  "`ticket transition`, `run start`, `merge`;" with "the guards in `factory/cli.py`
  (`ticket transition`, `run start`) and `factory/gates.py` (`merge`);". Re-wrap the paragraph
  at 100 columns, keeping "`factory/gates.py` (`merge`)" on one line.

**E. `factory/human.py`, human decisions.** Needs B and D. Moves `_restart_note` (576-589),
`spec_amend` (592-659), `_by` (1066-1067), `_approval_dir` (1070-1073), `_next_n` (1076-1077),
`_refuse_unless_applies` (1080-1085), `_copy_record` (1088-1092), `approve_spec` (1095-1126),
`request_changes` (1129-1141), `resolve` (1144-1252), `_supersede` (1255-1259),
`_set_aside_failed_rows` (1262-1282) and `decision_add` (1285-1289). It imports `_branch_tip` and
`undeclared_protected` from `factory.gates`, and `out`, `_rel`, `_add_spec_version` and `fence`
from `factory.common`. After this part, `factory/cli.py` is under 900 lines.

Which scenarios each part can pass:

| Part | Scenarios |
|---|---|
| A | "The drift checks live in factory/drift.py" |
| B | "The shared helpers and the live-store fence live in factory/common.py" |
| C | "Instance and store setup live in factory/setup.py" |
| D | "The gates live in factory/gates.py"; "The README and the principles name gates.py for the moved gate commands" |
| E | "The human decisions live in factory/human.py"; "factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines" |
| every part | every other scenario of this change |

## Tests to change

none. No test reads `factory/cli.py` as a file or calls any `factory.cli` name but `main`
(Evidence). The two patched functions stay reachable as before.

=== specs/harness-code/spec.md
## ADDED Requirements

### Requirement: The command-line code has one module per job
The harness's command-line code SHALL be split by job: the spec-drift checks in
`factory/drift.py`, setup in `factory/setup.py`, the gates in `factory/gates.py`, the human
decisions in `factory/human.py`, and the helpers more than one of them uses, with the live-store
fence, in `factory/common.py`. `factory/cli.py` MUST keep the parser, the entry point and the role
list, and be under 900 lines.

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
- THEN it prints exactly `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend`

#### Scenario: factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines
- WHEN `echo "$(wc -l < factory/cli.py | tr -d ' ') $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"`
- THEN it prints two numbers: the first below 900, the second `3`

### Requirement: Splitting the command-line code changes no definition
Across this change, every top-level function, class and assignment in `factory/*.py` SHALL keep
its exact source text, wherever it ends up, and the change MUST add at most 100 lines to
`factory/*.py` in total.

#### Scenario: Every definition keeps its exact text, and the split adds at most 100 lines
The command compares each `Merge factory/T-0047.<n>` commit reachable from HEAD with its first
parent, and `git merge-base HEAD main` with HEAD, and adds up the results. Changes other tickets
make to the same files are therefore never counted.
- GIVEN the script written by the block below, run once at column 0 as shown

```sh
cat > ${TMPDIR:-/tmp}/t0047-moved.py <<'EOF'
# uv run --frozen python -B t0047-moved.py, from the repo root. Compares factory/*.py across each
# `Merge factory/T-0047.<n>` commit reachable from HEAD against its first parent, and across
# `git merge-base HEAD main` against HEAD, so other tickets' changes are never counted. Per pair it
# takes every top-level function, class and assignment by its exact source text, in whichever
# factory/*.py file holds it. Prints `pairs=<n> added=<a> removed=<r> lines=<l>`: a definition whose
# text changed counts once in each of added and removed; lines is the change in the files' total
# line count, summed over the pairs. Then the first line of up to ten definitions that differ.
import ast, collections, subprocess
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
def scan(rev):
    c, lines = collections.Counter(), 0
    for path in git("ls-tree", "--name-only", rev, "factory/").split():
        if path.endswith(".py"):
            src = git("show", f"{rev}:{path}"); lines += src.count("\n")
            for n in ast.parse(src).body:
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Assign, ast.AnnAssign)):
                    c[ast.get_source_segment(src, n)] += 1
    return c, lines
pairs = [(m + "^1", m) for m in git("log", "--format=%H", "--grep=^Merge factory/T-0047[.]", "HEAD").split()]
base, head = git("merge-base", "HEAD", "main").strip(), git("rev-parse", "HEAD").strip()
if base != head:
    pairs.append((base, head))
added, removed, lines = [], [], 0
for old, new in pairs:
    (o, lo), (n, ln) = scan(old), scan(new)
    added += list((n - o).elements()); removed += list((o - n).elements()); lines += ln - lo
print(f"pairs={len(pairs)} added={len(added)} removed={len(removed)} lines={lines}")
for d in (added + removed)[:10]: print(d.splitlines()[0])
EOF
```

- WHEN `(uv run --frozen python -B ${TMPDIR:-/tmp}/t0047-moved.py)`
- THEN it prints one line, `pairs=<n> added=0 removed=0 lines=<l>`, with n at least 1 and l at most 100, and nothing after it

### Requirement: Only the entry point, the driver and the stats report import the CLI module
No harness module SHALL import `factory.cli` except `factory/__main__.py`, `factory/drive.py` and
`factory/stats.py`. `main`, `build_parser` and `ROLES` MUST stay importable from `factory.cli`.

#### Scenario: Only the entry point, the driver and the stats report import the CLI module
- WHEN `grep -lE '^\s*(from factory\.cli import|import factory\.cli|from factory import ([^#]*, )?cli\b)' factory/*.py | paste -sd' ' -`
- THEN it prints exactly `factory/__main__.py factory/drive.py factory/stats.py`

#### Scenario: The CLI's entry points stay importable
- WHEN `uv run --frozen python -B -c 'import factory.cli, factory.drive, factory.stats; from factory.cli import main, build_parser, ROLES; print(len(ROLES), callable(main), callable(build_parser))'`
- THEN it prints exactly `7 True True`

### Requirement: The split harness passes its suite and its name checks
After the split, the harness suite SHALL pass with no test file changed, and the harness source
MUST have no undefined, unused or redefined name.

#### Scenario: The split harness has no undefined, unused or redefined names
- WHEN `uvx ruff check --select F factory`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: After the split the harness suite passes with no test file changed
Per the standing T-0023 decision, the command gives pytest its own temporary directory under
`/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0047-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it

## MODIFIED Requirements

### Requirement: The harness keeps no definition, setting or comment that nothing uses or that is no longer true
The harness source under `factory/` SHALL carry no definition that nothing calls or reads, no instance setting that no code reads, and no comment or message that describes behaviour the harness no longer has. It MUST keep every behaviour that a command can reach. Its checks on the command-line code read `factory/cli.py` and the five modules split from it: `common.py`, `drift.py`, `gates.py`, `human.py` and `setup.py`.

#### Scenario: The four dead definitions are gone and nothing names them
- WHEN `echo "$(grep -nE '^(def run_gates\(|STATES = |OPS = |def load_config\()' factory/gitops.py factory/store.py factory/specstore.py | wc -l | tr -d ' ') $(grep -rnF --include='*.py' -e 'gitops.run_gates' -e 'store.STATES' -e 'specstore.OPS' -e 'store.load_config' factory tests | wc -l | tr -d ' ')"`
- THEN it prints `0 0`

#### Scenario: No harness or test file names the force-push setting
- WHEN `grep -rn --exclude-dir=__pycache__ force_push_allowed factory tests | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write
- WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c prompt_name) $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c "already has run {t\[.in_flight.\]\[0\]} in flight") $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'store.ensure_gitignore(root)')"`
- THEN it prints `0 2 2`

#### Scenario: No harness module has three blank lines in a row
- WHEN `awk 'FNR==1{n=0} /^$/{n++; if(n==3) print FILENAME":"FNR; next} {n=0}' factory/*.py | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: The three stale texts are gone
- WHEN `grep -nF -e 'commit-and-push' -e 'live pilot store is unaffected' -e 'not supported yet' factory/*.py | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: The repo-root helper takes no argument and every caller passes none
- WHEN `echo "$(grep -n 'repo_root(cfg' factory/*.py | wc -l | tr -d ' ') $(grep -o 'gitops.repo_root()' factory/*.py | wc -l | tr -d ' ') $(grep -c '^def repo_root() -> Path:$' factory/gitops.py)"`
- THEN it prints `0 12 1`

#### Scenario: The harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes, and only the force-push test lines change under tests
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0044-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only main...HEAD -- tests)`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and every later line, if any, is `tests/factory/fixtures/instance/instance.yaml` or `tests/factory/test_instance.py`

### Requirement: Each operation the harness repeated has one definition
The harness SHALL define once each of the following: listing a ticket's runs, reading the event log (one reader for the CLI, one inside the standalone cost script), recording a status transition outside spec approval, listing the runs in flight on a ticket and its sub-tickets, reading the integration-branch tip, copying a resolution record, setting aside failed result rows, checking for a PLANNED planner run, refusing a spec that does not validate and apply, formatting a dispatcher park for a failed store command, and cleaning up a checker run. Every caller MUST use that definition. Its checks on the command-line code read `factory/cli.py` and the five modules split from it: `common.py`, `drift.py`, `gates.py`, `human.py` and `setup.py`.

#### Scenario: Only the store module lists a ticket's runs
- WHEN `cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py factory/compose.py factory/specstore.py 2>/dev/null | grep -cE 'runs\.(iterdir|glob)\(|"runs"\)\.(iterdir|glob)\('`
- THEN it prints `0`

#### Scenario: The CLI and the stats report read the event log through a shared reader
- WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py factory/stats.py 2>/dev/null | grep -c '"\*\.jsonl"') $(grep -c '"\*\.jsonl"' factory/store.py)"`
- THEN it prints `0 1`

#### Scenario: One function records a status transition outside spec approval
- WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c '"ticket\.transition"') $(grep -c '"ticket\.transition"' factory/store.py)"`
- THEN it prints `1 1`

#### Scenario: Neither spec amend nor the dispatcher builds the in-flight list itself
- WHEN `cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py factory/drive.py 2>/dev/null | grep -cE 'for \w+ in \(t, \*'`
- THEN it prints `0`

#### Scenario: One function reads the integration-branch tip
- WHEN `echo "$(cat factory/*.py | grep -cE 'rev\(repo, (gitops\.)?integration_branch\(') $(grep -c '^def integration_tip(' factory/gitops.py)"`
- THEN it prints `1 1`

#### Scenario: Record copies, row set-asides, planner-run checks and spec apply checks each have one definition
- WHEN `echo "$(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'shutil\.copyfile(a\.') $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c '"results\.superseded"') $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'is not a PLANNED planner run') $(cat factory/cli.py factory/common.py factory/drift.py factory/gates.py factory/human.py factory/setup.py 2>/dev/null | grep -c 'specstore\.applies(root, deltas)')"`
- THEN it prints `0 1 1 1`

#### Scenario: One line formats a failed-command park and one call cleans up a checker
- WHEN `echo "$(grep -cE "harness-bug: .*stderr" factory/drive.py) $(grep -c 'call("run", "cleanup"' factory/drive.py) $(grep -cE '^def _(harness_bug|cleanup_checker)\(' factory/drive.py)"`
- THEN it prints `1 1 2`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents name the module that holds each moved gate command
`README.md` and `docs/principles.md` SHALL name `factory/gates.py`, not `factory/cli.py`, for
`ticket_join`, `merge_cmd`, `archive_cmd` and the `merge` guard, and those three functions MUST be
defined in `factory/gates.py`.

#### Scenario: The README and the principles name gates.py for the moved gate commands
- WHEN `echo "$(grep -c 'factory/gates.py. .ticket_join., .merge_cmd., .archive_cmd.' README.md) $(grep -c 'factory/cli.py. .ticket_join.' README.md) $(grep -c 'factory/gates.py. (.merge.)' docs/principles.md) $(grep -c 'guards in .factory/cli.py.:' docs/principles.md) $(grep -cE '^def (ticket_join|merge_cmd|archive_cmd)\(' factory/gates.py 2>/dev/null)"`
- THEN it prints exactly `1 0 1 0 3`

=== verification.md
## Acceptance

- The drift checks live in factory/drift.py → NEW. Today the import fails with
  `ModuleNotFoundError: No module named 'factory.drift'` and nothing is printed.
- The shared helpers and the live-store fence live in factory/common.py → NEW. Today
  `ModuleNotFoundError: No module named 'factory.common'`, and nothing is printed.
- Instance and store setup live in factory/setup.py → NEW. Today
  `ModuleNotFoundError: No module named 'factory.setup'`, and nothing is printed.
- The gates live in factory/gates.py → NEW. Today
  `ModuleNotFoundError: No module named 'factory.gates'`, and nothing is printed.
- The human decisions live in factory/human.py → NEW. Today
  `ModuleNotFoundError: No module named 'factory.human'`, and nothing is printed.
- factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines → NEW.
  Today it prints `2020 3`.
- Every definition keeps its exact text, and the split adds at most 100 lines → NEW. Today it
  prints `pairs=0 added=0 removed=0 lines=0`, because there is no change to compare. On a change
  it discriminates: the prototype with one refusal text edited printed
  `pairs=2 added=1 removed=1 lines=60` and the edited function (Evidence).
- Only the entry point, the driver and the stats report import the CLI module → REGRESSION.
- The CLI's entry points stay importable → REGRESSION.
- The split harness has no undefined, unused or redefined names → REGRESSION.
- After the split the harness suite passes with no test file changed → REGRESSION. One test that
  asserts the order of two concurrent checker runs failed once under load on the prototype, and
  passed on rerun there and on base (Evidence).
- The README and the principles name gates.py for the moved gate commands → NEW. Today it prints
  `0 1 0 1 `, with nothing for the last count because `factory/gates.py` does not exist.
- The four dead definitions are gone and nothing names them → REGRESSION.
- No harness or test file names the force-push setting → REGRESSION.
- Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write → REGRESSION, in its new form. The old form prints `0 2 1` once `init_cmd` moves.
- No harness module has three blank lines in a row → REGRESSION.
- The three stale texts are gone → REGRESSION.
- The repo-root helper takes no argument and every caller passes none → REGRESSION.
- The harness has no unused imports or variables → REGRESSION.
- The harness suite passes, and only the force-push test lines change under tests → REGRESSION.
- Only the store module lists a ticket's runs → REGRESSION. It now also reads the five new modules.
- The CLI and the stats report read the event log through a shared reader → REGRESSION. It now
  also reads the five new modules.
- One function records a status transition outside spec approval → REGRESSION, in its new form.
  The old form prints `0 1` once `approve_spec` moves.
- Neither spec amend nor the dispatcher builds the in-flight list itself → REGRESSION. It now
  reads `factory/human.py`, where `spec_amend` goes.
- One function reads the integration-branch tip → REGRESSION, unchanged.
- Record copies, row set-asides, planner-run checks and spec apply checks each have one definition → REGRESSION, in its new form. The old form prints `0 0 1 0` once `human.py` holds the moved code.
- One line formats a failed-command park and one call cleans up a checker → REGRESSION, unchanged.

## PR description (the implementer's output)

Sub-ticket: T-0047.4 (Move the human decisions to factory/human.py, leaving factory/cli.py under 900 lines). Parent T-0047, spec v2 at `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`. Branch `factory/T-0047.4`, head `9349e5762e727e570bf0bd0e7ceb90c865387a71`, one commit on base `43265a02f3ad`.

## What changed

**Part E, `factory/human.py`, the human decisions.** "Human decisions" are the commands a person uses to approve a spec, send it back, or rule on a stopped ticket.
- New `factory/human.py` (324 lines). It holds the 13 definitions in the order they had in `factory/cli.py`: `_restart_note` and `spec_amend` first, then `_by` through `decision_add`.
- The definitions were moved by a script that cuts exact line ranges, so no body was edited. Check M confirms this with `added=0 removed=0`.
- The module header is a one-line docstring, then `from __future__ import annotations`, then the imports its code uses:
  - `difflib`, `getpass`, `shutil` and `Path`;
  - `gitops`, `specstore`, `store` and `subtickets`;
  - `_add_spec_version`, `_rel` and `out` from `factory.common`;
  - `_branch_tip` and `undeclared_protected` from `factory.gates`;
  - `Refused` from `factory.store`.
- The `# ----- human surface (K-lite)` section comment was dropped. The design allows dropping a section comment when its section in `factory/cli.py` is empty, and the module docstring now says what the code is for.
- `factory/cli.py` drops 316 lines. It goes from 1,198 to 882 lines.
  - It imports `approve_spec`, `decision_add`, `request_changes`, `resolve` and `spec_amend` from `factory.human`, for `build_parser`.
  - It drops the imports that nothing in it uses any more: `difflib`, `getpass`, `shutil`, and `_branch_tip` and `undeclared_protected` from `factory.gates`.
  - The `factory.gates` import was re-wrapped onto two lines after those two names were removed.
- Nothing under `tests/` changed, and no doc changed.

## Acceptance results

All commands were run from the worktree through the "Running code" wrapper. `TMPDIR` was set to the run's scratch directory for check M's script. The full log is `scratch/checks.out`.

NEW: The human decisions live in factory/human.py
- Before: `ModuleNotFoundError: No module named 'factory.human'`, nothing printed, exit 1.
- After: `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend`

NEW: factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines
- Before: `1198 3`
- After: `882 3`

Intermediate check (NEW): `uv run --frozen python -B -c 'import factory.human'`
- Before: `ModuleNotFoundError`, exit 1.
- After: prints nothing, exit 0.

REGRESSION, the module scenarios from T-0047.1 to T-0047.3. All match their expected text exactly:
- drift: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`
- common: `_add_spec_version _in_flight _integration_head _rel fence out`
- setup: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`
- gates: `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`
- README and principles: `1 0 1 0 3`

REGRESSION, check M (every moved definition keeps its exact text). The script was copied verbatim from the parent spec.
- Output: `pairs=4 added=0 removed=0 lines=54`, and nothing after it.
- The four pairs are the merges of T-0047.1, .2 and .3, plus this branch against `main`.
- This sub-ticket adds 8 of the 54 lines.

REGRESSION, the shared set R1 to R19 (R1 to R3, R5 to R11 and R13 to R19 are in `scratch/checks.out`; R4 and R12 are in `scratch/suites.out`):

| Check | Output |
|---|---|
| R1 | `factory/__main__.py factory/drive.py factory/stats.py` |
| R2 | `7 True True` |
| R3 | `All checks passed!`, exit 0 |
| R4 | `576 passed in 583.66s (0:09:43)`, and nothing after it (no test file changed) |
| R5 | `0 0` |
| R6 | `0` |
| R7 | `0 2 2` |
| R8 | `0` |
| R9 | `0` |
| R10 | `0 12 1` |
| R11 | `All checks passed!`, exit 0 |
| R12 | `576 passed in 564.04s (0:09:24)`, and nothing after it |
| R13 | `0` |
| R14 | `0 1` |
| R15 | `1 1` |
| R16 | `0` |
| R17 | `1 1` |
| R18 | `0 1 1 1` |
| R19 | `1 1 2` |

R15, R16 and R18 now find `approve_spec`, `spec_amend` and the record-copy, set-aside, planner-run and apply checks in `factory/human.py`. Their counts are the same as before the move.

Gates. Each was run exactly as written in the input:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 563.81s (0:09:23)`, exit 0.

## Tests added/changed

None. The sub-ticket lists no interim tests and no tests to change, and this is a move with no new behaviour. The existing suite covers the moved commands (576 passed).

## Known gaps and uncertainties

- **`fence` is not imported into `factory/human.py`, although the scope line names it.** The sub-ticket and design part E say human.py imports `fence` from `factory.common`. No moved definition uses that function. `spec_amend` assigns a local variable also named `fence` (a run of backticks for the diff record), and that local hides the imported name. Importing it would leave an unused import, which fails R3 and R11. I checked this by adding the import to a scratch copy: `ruff check --select F` reported `F401 factory.common.fence imported but unused`. I followed the design's general rule, "the imports its definitions use". `factory/cli.py` still imports `fence`, because `main` uses it.
- **One step ran without the wrapper.** The move script `scratch/move.py` was run once with `uv run --frozen python -B` outside the "Running code" wrapper. It only reads and writes `factory/cli.py` and `factory/human.py` by relative path inside the worktree. Every check and test above ran through the wrapper.
- **The suite is slow.** Each suite run took about 9.5 minutes. The flaky concurrent-checker test that the spec mentions did not fail in any of the three runs.

## Out-of-scope observations

- `stats_cmd` sits under the `# ----- spec store (doc §Harness, Spec store; part K)` section comment in `factory/cli.py`, which no longer describes it. This was true before this change, and the design keeps `stats_cmd` where it is (Decision 4). I left it alone.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance, regression and gate command was run on head `9349e57` and printed the expected result, and check M shows no definition text changed.
ESCALATIONS: none

## Diff `43265a02f3ad943ebed963d7246495418c3d2ee8...9349e5762e727e570bf0bd0e7ceb90c865387a71`

diff --git a/factory/cli.py b/factory/cli.py
index 9eca48c..728bfb4 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -7,11 +7,8 @@ from __future__ import annotations
 
 import argparse
 import datetime as dt
-import difflib
-import getpass
 import json
 import re
-import shutil
 import subprocess
 import sys
 from pathlib import Path
@@ -21,8 +18,9 @@ import yaml
 from factory import compose, gitops, instance, specstore, status, store, subtickets, tripwire
 from factory.common import _add_spec_version, _rel, fence, out
 from factory.drift import _check_drift, _check_sibling_tests
-from factory.gates import (_branch_tip, _parent_close_verified, archive_cmd, merge_cmd, results_record,
-                           results_show, ticket_head, ticket_join, ticket_parent_check, undeclared_protected)
+from factory.gates import (_parent_close_verified, archive_cmd, merge_cmd, results_record, results_show,
+                           ticket_head, ticket_join, ticket_parent_check)
+from factory.human import approve_spec, decision_add, request_changes, resolve, spec_amend
 from factory.setup import init_cmd, paths_cmd, store_migrate
 from factory.store import Refused
 
@@ -423,92 +421,6 @@ def spec_add(a, root, cfg):
     out({"ok": True, "id": t["id"], "version": n, "path": f"specs/{t['id']}/v{n}.md"})
 
 
-def _restart_note(root: Path, t: dict) -> str:
-    """What a restart keeps (merged sub-tickets) and discards (the rest not closed), and its two routes."""
-    subs = store.subtickets_of(root, t["id"])
-    kept = [f"{s['id']} / {s['title']} (merge {((s.get('merge') or {}).get('main_after') or '')[:9] or 'not recorded'})"
-            for s in subs if s["status"] == "merged"]
-    lost = [f"{s['id']} / {s['title']}: {s['status']}" + (f", branch {s['branch']}" if s.get("branch") else "")
-            for s in subs if s["status"] not in ("merged", "closed")]
-    tid = t["id"]
-    return (f"Restart instead of amending. Merged, and their merge commits stay on the integration branch: "
-            f"{'; '.join(kept) or 'none'}. Not merged, which a restart discards: {'; '.join(lost) or 'none'}. "
-            f"To re-spec and re-plan: `factory ticket park {tid} --reason \"<why>\"`, `factory resolve {tid} "
-            f"--to spec-gate`, then `factory approve-spec {tid} --edit F`; the new plan supersedes the unmerged "
-            f"sub-tickets. To close and re-file: `factory resolve {tid} --close`, then `factory ticket new --file F`. "
-            "The factory never restarts by itself.")
-
-
-def spec_amend(a, root, cfg):
-    """`spec amend PARENT --file F --reason LINE --intent unchanged`: a human writes F as the next spec
-    version and makes it the approved one, re-pinning the change folder and keeping its tasks.md.
-    Doc §Harness, Spec store. Every refusal comes before the first write."""
-    t = store.load_ticket(root, a.id)
-    tid, av = t["id"], t["spec"]["approved_version"]
-    if t.get("parent"):
-        raise Refused(f"{tid} is a sub-ticket; amend its parent's spec: spec amend {t['parent']}")
-    if t["status"] == "awaiting-spec-gate":
-        raise Refused(f"{tid} is awaiting-spec-gate; amend it at the gate with approve-spec {tid} --edit F")
-    if av is None:
-        raise Refused(f"{tid} has no approved spec to amend")
-    if t["status"] == "closed":
-        raise Refused(f"{tid} is closed")
-    reason = (a.reason or "").strip()
-    if not reason or len(reason.splitlines()) > 1:
-        raise Refused("--reason is one non-blank line of text")
-    subs = store.subtickets_of(root, tid)
-    runs = store.in_flight_runs(root, t)
-    if runs:
-        raise Refused(f"{tid} has runs in flight on it or its sub-tickets: {', '.join(runs)}; amend once they finish")
-    if a.intent == "changed":
-        raise Refused(f"intent changed: an amendment keeps the spec's intent, so --intent changed is never "
-                      f"applied. {_restart_note(root, t)}")
-    old = (root / "specs" / tid / f"v{av}.md").read_text(encoding="utf-8")
-    text = Path(a.file).read_text(encoding="utf-8")
-    changes = specstore.intent_changes(old, text)
-    if changes:
-        raise Refused(f"intent changed ({'; '.join(changes)}). --intent unchanged keeps the Problem section, "
-                      "every Decisions line, and each requirement's name, operation and statement; scenarios, "
-                      f"their setup, Evidence, design text and Tests to change may change. {_restart_note(root, t)}")
-    if specstore.is_active(root):
-        if not specstore.change_dir(root, tid).exists():
-            raise Refused(f"{tid} has no change folder ({_rel(root, specstore.change_dir(root, tid))}): "
-                          "it was archived, so its spec can no longer be amended")
-        _refuse_unless_applies(root, text, "spec not amended")
-    n = _add_spec_version(root, t, text, f"amend {a.file}", cfg)
-    if specstore.is_active(root):
-        tasks = specstore.change_dir(root, tid) / "tasks.md"
-        kept = tasks.read_text(encoding="utf-8") if tasks.exists() else None
-        specstore.pin(root, tid, text)
-        if kept is not None:
-            store.write_text(tasks, kept)
-    t["spec"]["approved_version"] = n
-    store.save_ticket(root, t)
-    for s in subs:
-        if s["status"] not in ("merged", "closed"):
-            s["spec"] = {"version": n, "approved_version": n}  # planned_from stays: no plan is superseded
-            store.save_ticket(root, s)
-    ob, nb = specstore.scenario_blocks(old), specstore.scenario_blocks(text)
-    scen = ([f"- changed: {k}" for k in nb if k in ob and ob[k] != nb[k]] + [f"- added: {k}" for k in nb if k not in ob]
-            + [f"- removed: {k}" for k in ob if k not in nb])
-    merged = [f"- {s['id']} / {s['title']}: merged" for s in subs if s["status"] == "merged"]
-    diff = "".join(difflib.unified_diff(old.splitlines(keepends=True), text.splitlines(keepends=True),
-                                        f"specs/{tid}/v{av}.md", f"specs/{tid}/v{n}.md")).rstrip("\n")
-    fence = "```"
-    while fence in diff:  # the spec's own fences must not close the record's
-        fence += "`"
-    d = _approval_dir(root, tid)
-    rec = d / f"amendment-{_next_n(d, 'amendment')}.md"
-    store.write_text(rec, "\n\n".join([
-        f"# {tid}: spec amended, v{av} to v{n}", f"By {_by()} at {store.now()}.", f"Reason: {reason}",
-        "Intent: unchanged", "## Scenarios changed", "\n".join(scen) or "none",
-        "## Sub-tickets merged before this amendment", "\n".join(merged) or "none",
-        "## Diff", f"{fence}diff\n{diff}\n{fence}"]) + "\n")
-    store.log_event(root, "spec.amended", ticket=tid, by=_by(), previous=av, version=n, reason=reason,
-                    record=_rel(root, rec))
-    out({"ok": True, "id": tid, "version": n, "record": _rel(root, rec)})
-
-
 def plan_add(a, root, cfg):
     t = store.load_ticket(root, a.id)
     text = _text_from(a, root)
@@ -677,234 +589,6 @@ def ticket_ready_implementers(a, root, cfg):
          "superseded": [s["id"] for s in superseded]})
 
 
-# ----- human surface (K-lite) -----------------------------------------------------
-
-def _by() -> str:
-    return getpass.getuser()
-
-
-def _approval_dir(root: Path, tid: str) -> Path:
-    d = root / "approvals" / tid
-    d.mkdir(parents=True, exist_ok=True)
-    return d
-
-
-def _next_n(d: Path, kind: str) -> int:
-    return len(list(d.glob(f"{kind}-*"))) + 1
-
-
-def _refuse_unless_applies(root: Path, text: str, refusal: str) -> None:
-    """Refuse spec `text` when it does not validate or its deltas do not apply to current truth."""
-    _, deltas, errors = specstore.validate(text)
-    errors += specstore.applies(root, deltas) if not errors else []
-    if errors:
-        raise Refused(f"{refusal}: " + "; ".join(errors))
-
-
-def _copy_record(d: Path, kind: str, src) -> Path:
-    """Copy `src` into approvals directory `d` as the next `<kind>-<n>.md`."""
-    dest = d / f"{kind}-{_next_n(d, kind)}.md"
-    shutil.copyfile(src, dest)
-    return dest
-
-
-def approve_spec(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    if a.edit:
-        text = Path(a.edit).read_text(encoding="utf-8")
-    else:
-        n = a.version or t["spec"]["version"]
-        if not (root / "specs" / t["id"] / f"v{n}.md").exists():
-            raise Refused(f"{t['id']} has no spec v{n}")
-        text = (root / "specs" / t["id"] / f"v{n}.md").read_text(encoding="utf-8")
-    pinned: list[str] = []
-    if specstore.is_active(root):
-        # Part K: refuse a malformed version or a delta that does not apply; nothing is written.
-        _refuse_unless_applies(root, text, "spec not pinned")
-    if t["status"] != "awaiting-spec-gate":
-        raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
-    if a.edit:
-        n = _add_spec_version(root, t, text, f"gate edit {a.edit}", cfg)
-    if specstore.is_active(root):
-        pinned = specstore.pin(root, t["id"], text)
-    t["spec"]["approved_version"] = n
-    store.write_text(root / "specs" / f"{t['id']}.md", text)
-    store.write_yaml(_approval_dir(root, t["id"]) / f"spec-v{n}.yaml", {"by": _by(), "at": store.now(), "version": n})
-    frm = t["status"]
-    t["status"] = "ready-for-planner"
-    t["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-planner", "by": _by(), "approved_version": n})
-    store.save_ticket(root, t)
-    store.log_event(root, "approval.recorded", ticket=t["id"], kind="spec", version=n, by=_by())
-    if pinned:
-        store.log_event(root, "change.pinned", ticket=t["id"], version=n, files=pinned)
-    store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": "ready-for-planner", "by": _by()})
-    out({"ok": True, "id": t["id"], "approved_version": n, "state": "ready-for-planner", "spec": f"specs/{t['id']}.md",
-         "change": pinned})
-
-
-def request_changes(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    if t["status"] != "awaiting-spec-gate":
-        raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
-    d = _approval_dir(root, t["id"])
-    dest = _copy_record(d, "changes", a.notes)
-    frm = t["status"]
-    t["status"] = "ready-for-spec-writer"
-    t["round"]["spec"] = 0
-    t["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-spec-writer", "by": _by(), "notes": _rel(root, dest)})
-    store.save_ticket(root, t)
-    store.log_event(root, "human.resolved", ticket=t["id"], kind="request-changes", by=_by(), notes=_rel(root, dest))
-    out({"ok": True, "id": t["id"], "state": "ready-for-spec-writer", "notes": _rel(root, dest)})
-
-
-def resolve(a, root, cfg):
-    if a.decision is not None:  # refuse before anything is written, so a decision is never dropped
-        # the branch below that will run: --answer wins, and --close runs only with no other mode
-        if not (a.answer or (a.close and not (a.ruling or a.accept_paths or a.to or a.redispatch or a.replan))):
-            raise Refused("--decision applies only with --answer or --close")
-        specstore.decision_text(a.decision)
-    t = store.load_ticket(root, a.id)
-    st, parked = t["status"], t["parked"] or {}
-    reason = parked.get("reason", "")
-    d = _approval_dir(root, t["id"])
-
-    def decided(via: str) -> dict:
-        """Log `--decision`, once this mode's own refusals have passed; the `extra` for move()."""
-        if a.decision is None:
-            return {}
-        line = specstore.record_decision(root, t["id"], a.decision)
-        store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via=via)
-        return {"decision": line}
-
-    def move(to: str, kind: str, extra: dict) -> None:
-        t["status"] = to
-        if to != "parked":
-            t["parked"] = None
-        t["history"].append({"ts": store.now(), "from": st, "to": to, "by": _by(), "resolve": kind, **extra})
-        store.save_ticket(root, t)
-        store.write_yaml(d / f"resolve-{_next_n(d, 'resolve')}.yaml", {"by": _by(), "at": store.now(), "kind": kind, "from": st, "to": to, **extra})
-        store.log_event(root, "human.resolved", ticket=t["id"], kind=kind, by=_by(), **{"from": st, "to": to})
-        out({"ok": True, "id": t["id"], "state": to, "kind": kind, **extra})
-
-    if a.answer:
-        if st == "waiting-requester":
-            to = "ready-for-triage"
-        elif st == "parked" and reason.startswith("NEEDS-HUMAN"):
-            to = "ready-for-spec-writer" if "spec writer" in reason else "ready-for-triage"
-        else:
-            raise Refused(f"--answer applies to waiting-requester or a NEEDS-HUMAN park; {t['id']} is {st} ({reason or 'no park'})")
-        req = root / t["request"]
-        n = req.read_text(encoding="utf-8").count("\n## Answer ") + 1
-        with req.open("a", encoding="utf-8") as fh:
-            fh.write(f"\n\n## Answer {n}\n\n{Path(a.answer).read_text(encoding='utf-8').rstrip()}\n")
-        move(to, "answer", {"answer": n, **decided("resolve --answer")})
-    elif a.ruling:
-        # the harness failed to start an implementer run (e.g. a drift refusal the Workflow clerk
-        # wrapped): routed as BLOCKED. Not a failed compose, which leaves its run in flight.
-        start_bug = (reason.startswith("harness-bug: run start implementer:")
-                     and parked.get("from") == "ready-for-implementer")
-        if st != "parked" or not (reason.startswith(("ESCALATE", "BLOCKED")) or start_bug):
-            if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
-                raise Refused("use --answer")
-            raise Refused("--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an "
-                          f"implementer's run start; {t['id']} is {st} ({reason or 'no park'})")
-        if reason.startswith("ESCALATE from reviewer"):
-            # Back to its checks, same round: the reviewer runs again with the ruling in its input.
-            head, moved = _supersede(root, t)
-            dest = _copy_record(d, "ruling", a.ruling)
-            move("checks-in-flight", "ruling", {"ruling": _rel(root, dest), "head": head, "superseded": moved})
-            return
-        if reason.startswith("BLOCKED") or start_bug:  # an implementer's or the gate's BLOCKED: back to the implementer, same round
-            to = "ready-for-implementer"
-        else:
-            to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
-        dest = _copy_record(d, "ruling", a.ruling)
-        move(to, "ruling", {"ruling": _rel(root, dest)})
-    elif a.accept_paths:
-        # The merge gate refused a protected path the pinned spec does not declare; the human accepts
-        # it under the approved design for this sub-ticket. Its results stand, so the build merges it.
-        if st != "parked" or not reason.startswith("BLOCKED from merge gate:"):
-            raise Refused("--accept-paths applies to a merge gate park (BLOCKED from merge gate); "
-                          f"{t['id']} is {st} ({reason or 'no park'})")
-        head = _branch_tip(gitops.repo_root(), t)
-        paths, _ = undeclared_protected(root, cfg, t, head)
-        if not paths:
-            raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
-        dest = _copy_record(d, "ruling", a.accept_paths)
-        t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
-        move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
-    elif a.to:
-        if a.to != "spec-gate":
-            raise Refused("--to accepts only spec-gate")
-        if st != "parked" or t["spec"]["version"] < 1:
-            raise Refused(f"--to spec-gate needs a parked ticket with a spec version; {t['id']} is {st}")
-        move("awaiting-spec-gate", "to-spec-gate", {})
-    elif a.redispatch:
-        # Re-run the checkers on the same head after the cause of the park is fixed outside the ticket
-        # (a harness or gate defect, a killed checker). Round unchanged.
-        if st != "parked" or parked.get("from") not in ("checks-in-flight", "ready-for-merge"):
-            raise Refused(f"--redispatch applies to a sub-ticket parked from its checks; {t['id']} is {st} (from {parked.get('from')})")
-        head, moved = _supersede(root, t)
-        move("checks-in-flight", "redispatch", {"head": head, "superseded": moved})
-    elif a.replan:
-        # After a failed parent-close check: back to the planner with F as a ruling. Its new
-        # sub-tickets take the next free ids under this parent; the merged ones stay merged.
-        if st != "parked":
-            raise Refused(f"--replan applies to a parked parent; {t['id']} is {st}")
-        subs = store.subtickets_of(root, t["id"])
-        if not subs:
-            raise Refused(f"--replan applies to a parent with sub-tickets; {t['id']} has none")
-        unmerged = [f"{s['id']} is {s['status']}" for s in subtickets.split_plan(subs)[0] if s["status"] != "merged"]
-        if unmerged:
-            raise Refused(f"--replan needs every sub-ticket merged: {', '.join(unmerged)}")
-        dest = _copy_record(d, "ruling", a.replan)
-        move("ready-for-planner", "replan", {"ruling": _rel(root, dest)})
-    elif a.close:
-        if st == "closed":
-            raise Refused(f"{t['id']} is already closed")
-        move("closed", "close", decided("resolve --close"))
-    else:
-        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate | --redispatch | "
-                      "--replan F | --close")
-
-
-def _supersede(root: Path, t: dict) -> tuple:
-    """Set aside the head's failed result rows and log it; returns (head, roles moved)."""
-    head, moved = t.get("head"), _set_aside_failed_rows(root, t)
-    store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
-    return head, moved
-
-
-def _set_aside_failed_rows(root: Path, t: dict) -> list[str]:
-    """Move the head's rows that did not pass under results/<head>/superseded-<n>/, so the join cannot
-    read them as current and the build runs only the checkers with no row. The reviewer row stays
-    when it is APPROVE; the verifier and ci rows, written by one verifier run, stay together when
-    they are VERIFIED and PASS. Returns the roles moved."""
-    head = t.get("head")
-    moved: list[str] = []
-    if head:
-        rows = {k: v.get("status") for k, v in store.results_for(root, head).items()}
-        stale = [] if rows.get("reviewer") == "APPROVE" else ["reviewer"]
-        if not (rows.get("verifier") == "VERIFIED" and rows.get("ci") == "PASS"):
-            stale += ["verifier", "ci"]
-        rd = root / "results" / head
-        todo = [store.result_path(root, head, r) for r in stale if r in rows]
-        if todo:
-            dest = rd / f"superseded-{len(list(rd.glob('superseded-*'))) + 1}"
-            dest.mkdir(parents=True, exist_ok=True)
-            for f in todo:
-                f.rename(dest / f.name)
-                moved.append(f.stem)
-    return moved
-
-
-def decision_add(a, root, cfg):
-    t = store.load_ticket(root, a.id)  # any state, closed included
-    line = specstore.record_decision(root, t["id"], a.text)
-    store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via="decision add")
-    out({"ok": True, "id": t["id"], "decision": line})
-
-
 # ----- spec store (doc §Harness, Spec store; part K) ----------------------------------
 
 def stats_cmd(a):
diff --git a/factory/human.py b/factory/human.py
new file mode 100644
index 0000000..f282e5b
--- /dev/null
+++ b/factory/human.py
@@ -0,0 +1,324 @@
+"""Human decisions: approve-spec, request-changes, resolve, decision add and spec amend."""
+from __future__ import annotations
+
+import difflib
+import getpass
+import shutil
+from pathlib import Path
+
+from factory import gitops, specstore, store, subtickets
+from factory.common import _add_spec_version, _rel, out
+from factory.gates import _branch_tip, undeclared_protected
+from factory.store import Refused
+
+
+def _restart_note(root: Path, t: dict) -> str:
+    """What a restart keeps (merged sub-tickets) and discards (the rest not closed), and its two routes."""
+    subs = store.subtickets_of(root, t["id"])
+    kept = [f"{s['id']} / {s['title']} (merge {((s.get('merge') or {}).get('main_after') or '')[:9] or 'not recorded'})"
+            for s in subs if s["status"] == "merged"]
+    lost = [f"{s['id']} / {s['title']}: {s['status']}" + (f", branch {s['branch']}" if s.get("branch") else "")
+            for s in subs if s["status"] not in ("merged", "closed")]
+    tid = t["id"]
+    return (f"Restart instead of amending. Merged, and their merge commits stay on the integration branch: "
+            f"{'; '.join(kept) or 'none'}. Not merged, which a restart discards: {'; '.join(lost) or 'none'}. "
+            f"To re-spec and re-plan: `factory ticket park {tid} --reason \"<why>\"`, `factory resolve {tid} "
+            f"--to spec-gate`, then `factory approve-spec {tid} --edit F`; the new plan supersedes the unmerged "
+            f"sub-tickets. To close and re-file: `factory resolve {tid} --close`, then `factory ticket new --file F`. "
+            "The factory never restarts by itself.")
+
+
+def spec_amend(a, root, cfg):
+    """`spec amend PARENT --file F --reason LINE --intent unchanged`: a human writes F as the next spec
+    version and makes it the approved one, re-pinning the change folder and keeping its tasks.md.
+    Doc §Harness, Spec store. Every refusal comes before the first write."""
+    t = store.load_ticket(root, a.id)
+    tid, av = t["id"], t["spec"]["approved_version"]
+    if t.get("parent"):
+        raise Refused(f"{tid} is a sub-ticket; amend its parent's spec: spec amend {t['parent']}")
+    if t["status"] == "awaiting-spec-gate":
+        raise Refused(f"{tid} is awaiting-spec-gate; amend it at the gate with approve-spec {tid} --edit F")
+    if av is None:
+        raise Refused(f"{tid} has no approved spec to amend")
+    if t["status"] == "closed":
+        raise Refused(f"{tid} is closed")
+    reason = (a.reason or "").strip()
+    if not reason or len(reason.splitlines()) > 1:
+        raise Refused("--reason is one non-blank line of text")
+    subs = store.subtickets_of(root, tid)
+    runs = store.in_flight_runs(root, t)
+    if runs:
+        raise Refused(f"{tid} has runs in flight on it or its sub-tickets: {', '.join(runs)}; amend once they finish")
+    if a.intent == "changed":
+        raise Refused(f"intent changed: an amendment keeps the spec's intent, so --intent changed is never "
+                      f"applied. {_restart_note(root, t)}")
+    old = (root / "specs" / tid / f"v{av}.md").read_text(encoding="utf-8")
+    text = Path(a.file).read_text(encoding="utf-8")
+    changes = specstore.intent_changes(old, text)
+    if changes:
+        raise Refused(f"intent changed ({'; '.join(changes)}). --intent unchanged keeps the Problem section, "
+                      "every Decisions line, and each requirement's name, operation and statement; scenarios, "
+                      f"their setup, Evidence, design text and Tests to change may change. {_restart_note(root, t)}")
+    if specstore.is_active(root):
+        if not specstore.change_dir(root, tid).exists():
+            raise Refused(f"{tid} has no change folder ({_rel(root, specstore.change_dir(root, tid))}): "
+                          "it was archived, so its spec can no longer be amended")
+        _refuse_unless_applies(root, text, "spec not amended")
+    n = _add_spec_version(root, t, text, f"amend {a.file}", cfg)
+    if specstore.is_active(root):
+        tasks = specstore.change_dir(root, tid) / "tasks.md"
+        kept = tasks.read_text(encoding="utf-8") if tasks.exists() else None
+        specstore.pin(root, tid, text)
+        if kept is not None:
+            store.write_text(tasks, kept)
+    t["spec"]["approved_version"] = n
+    store.save_ticket(root, t)
+    for s in subs:
+        if s["status"] not in ("merged", "closed"):
+            s["spec"] = {"version": n, "approved_version": n}  # planned_from stays: no plan is superseded
+            store.save_ticket(root, s)
+    ob, nb = specstore.scenario_blocks(old), specstore.scenario_blocks(text)
+    scen = ([f"- changed: {k}" for k in nb if k in ob and ob[k] != nb[k]] + [f"- added: {k}" for k in nb if k not in ob]
+            + [f"- removed: {k}" for k in ob if k not in nb])
+    merged = [f"- {s['id']} / {s['title']}: merged" for s in subs if s["status"] == "merged"]
+    diff = "".join(difflib.unified_diff(old.splitlines(keepends=True), text.splitlines(keepends=True),
+                                        f"specs/{tid}/v{av}.md", f"specs/{tid}/v{n}.md")).rstrip("\n")
+    fence = "```"
+    while fence in diff:  # the spec's own fences must not close the record's
+        fence += "`"
+    d = _approval_dir(root, tid)
+    rec = d / f"amendment-{_next_n(d, 'amendment')}.md"
+    store.write_text(rec, "\n\n".join([
+        f"# {tid}: spec amended, v{av} to v{n}", f"By {_by()} at {store.now()}.", f"Reason: {reason}",
+        "Intent: unchanged", "## Scenarios changed", "\n".join(scen) or "none",
+        "## Sub-tickets merged before this amendment", "\n".join(merged) or "none",
+        "## Diff", f"{fence}diff\n{diff}\n{fence}"]) + "\n")
+    store.log_event(root, "spec.amended", ticket=tid, by=_by(), previous=av, version=n, reason=reason,
+                    record=_rel(root, rec))
+    out({"ok": True, "id": tid, "version": n, "record": _rel(root, rec)})
+
+
+def _by() -> str:
+    return getpass.getuser()
+
+
+def _approval_dir(root: Path, tid: str) -> Path:
+    d = root / "approvals" / tid
+    d.mkdir(parents=True, exist_ok=True)
+    return d
+
+
+def _next_n(d: Path, kind: str) -> int:
+    return len(list(d.glob(f"{kind}-*"))) + 1
+
+
+def _refuse_unless_applies(root: Path, text: str, refusal: str) -> None:
+    """Refuse spec `text` when it does not validate or its deltas do not apply to current truth."""
+    _, deltas, errors = specstore.validate(text)
+    errors += specstore.applies(root, deltas) if not errors else []
+    if errors:
+        raise Refused(f"{refusal}: " + "; ".join(errors))
+
+
+def _copy_record(d: Path, kind: str, src) -> Path:
+    """Copy `src` into approvals directory `d` as the next `<kind>-<n>.md`."""
+    dest = d / f"{kind}-{_next_n(d, kind)}.md"
+    shutil.copyfile(src, dest)
+    return dest
+
+
+def approve_spec(a, root, cfg):
+    t = store.load_ticket(root, a.id)
+    if a.edit:
+        text = Path(a.edit).read_text(encoding="utf-8")
+    else:
+        n = a.version or t["spec"]["version"]
+        if not (root / "specs" / t["id"] / f"v{n}.md").exists():
+            raise Refused(f"{t['id']} has no spec v{n}")
+        text = (root / "specs" / t["id"] / f"v{n}.md").read_text(encoding="utf-8")
+    pinned: list[str] = []
+    if specstore.is_active(root):
+        # Part K: refuse a malformed version or a delta that does not apply; nothing is written.
+        _refuse_unless_applies(root, text, "spec not pinned")
+    if t["status"] != "awaiting-spec-gate":
+        raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
+    if a.edit:
+        n = _add_spec_version(root, t, text, f"gate edit {a.edit}", cfg)
+    if specstore.is_active(root):
+        pinned = specstore.pin(root, t["id"], text)
+    t["spec"]["approved_version"] = n
+    store.write_text(root / "specs" / f"{t['id']}.md", text)
+    store.write_yaml(_approval_dir(root, t["id"]) / f"spec-v{n}.yaml", {"by": _by(), "at": store.now(), "version": n})
+    frm = t["status"]
+    t["status"] = "ready-for-planner"
+    t["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-planner", "by": _by(), "approved_version": n})
+    store.save_ticket(root, t)
+    store.log_event(root, "approval.recorded", ticket=t["id"], kind="spec", version=n, by=_by())
+    if pinned:
+        store.log_event(root, "change.pinned", ticket=t["id"], version=n, files=pinned)
+    store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": "ready-for-planner", "by": _by()})
+    out({"ok": True, "id": t["id"], "approved_version": n, "state": "ready-for-planner", "spec": f"specs/{t['id']}.md",
+         "change": pinned})
+
+
+def request_changes(a, root, cfg):
+    t = store.load_ticket(root, a.id)
+    if t["status"] != "awaiting-spec-gate":
+        raise Refused(f"{t['id']} is {t['status']}, not awaiting-spec-gate")
+    d = _approval_dir(root, t["id"])
+    dest = _copy_record(d, "changes", a.notes)
+    frm = t["status"]
+    t["status"] = "ready-for-spec-writer"
+    t["round"]["spec"] = 0
+    t["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-spec-writer", "by": _by(), "notes": _rel(root, dest)})
+    store.save_ticket(root, t)
+    store.log_event(root, "human.resolved", ticket=t["id"], kind="request-changes", by=_by(), notes=_rel(root, dest))
+    out({"ok": True, "id": t["id"], "state": "ready-for-spec-writer", "notes": _rel(root, dest)})
+
+
+def resolve(a, root, cfg):
+    if a.decision is not None:  # refuse before anything is written, so a decision is never dropped
+        # the branch below that will run: --answer wins, and --close runs only with no other mode
+        if not (a.answer or (a.close and not (a.ruling or a.accept_paths or a.to or a.redispatch or a.replan))):
+            raise Refused("--decision applies only with --answer or --close")
+        specstore.decision_text(a.decision)
+    t = store.load_ticket(root, a.id)
+    st, parked = t["status"], t["parked"] or {}
+    reason = parked.get("reason", "")
+    d = _approval_dir(root, t["id"])
+
+    def decided(via: str) -> dict:
+        """Log `--decision`, once this mode's own refusals have passed; the `extra` for move()."""
+        if a.decision is None:
+            return {}
+        line = specstore.record_decision(root, t["id"], a.decision)
+        store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via=via)
+        return {"decision": line}
+
+    def move(to: str, kind: str, extra: dict) -> None:
+        t["status"] = to
+        if to != "parked":
+            t["parked"] = None
+        t["history"].append({"ts": store.now(), "from": st, "to": to, "by": _by(), "resolve": kind, **extra})
+        store.save_ticket(root, t)
+        store.write_yaml(d / f"resolve-{_next_n(d, 'resolve')}.yaml", {"by": _by(), "at": store.now(), "kind": kind, "from": st, "to": to, **extra})
+        store.log_event(root, "human.resolved", ticket=t["id"], kind=kind, by=_by(), **{"from": st, "to": to})
+        out({"ok": True, "id": t["id"], "state": to, "kind": kind, **extra})
+
+    if a.answer:
+        if st == "waiting-requester":
+            to = "ready-for-triage"
+        elif st == "parked" and reason.startswith("NEEDS-HUMAN"):
+            to = "ready-for-spec-writer" if "spec writer" in reason else "ready-for-triage"
+        else:
+            raise Refused(f"--answer applies to waiting-requester or a NEEDS-HUMAN park; {t['id']} is {st} ({reason or 'no park'})")
+        req = root / t["request"]
+        n = req.read_text(encoding="utf-8").count("\n## Answer ") + 1
+        with req.open("a", encoding="utf-8") as fh:
+            fh.write(f"\n\n## Answer {n}\n\n{Path(a.answer).read_text(encoding='utf-8').rstrip()}\n")
+        move(to, "answer", {"answer": n, **decided("resolve --answer")})
+    elif a.ruling:
+        # the harness failed to start an implementer run (e.g. a drift refusal the Workflow clerk
+        # wrapped): routed as BLOCKED. Not a failed compose, which leaves its run in flight.
+        start_bug = (reason.startswith("harness-bug: run start implementer:")
+                     and parked.get("from") == "ready-for-implementer")
+        if st != "parked" or not (reason.startswith(("ESCALATE", "BLOCKED")) or start_bug):
+            if st == "parked" and (reason.startswith("NEEDS-HUMAN") or "CLARIFY" in reason):
+                raise Refused("use --answer")
+            raise Refused("--ruling applies to an ESCALATE or BLOCKED park, or a harness-bug park from an "
+                          f"implementer's run start; {t['id']} is {st} ({reason or 'no park'})")
+        if reason.startswith("ESCALATE from reviewer"):
+            # Back to its checks, same round: the reviewer runs again with the ruling in its input.
+            head, moved = _supersede(root, t)
+            dest = _copy_record(d, "ruling", a.ruling)
+            move("checks-in-flight", "ruling", {"ruling": _rel(root, dest), "head": head, "superseded": moved})
+            return
+        if reason.startswith("BLOCKED") or start_bug:  # an implementer's or the gate's BLOCKED: back to the implementer, same round
+            to = "ready-for-implementer"
+        else:
+            to = "ready-for-planner" if "planner" in reason else "ready-for-critic"
+        dest = _copy_record(d, "ruling", a.ruling)
+        move(to, "ruling", {"ruling": _rel(root, dest)})
+    elif a.accept_paths:
+        # The merge gate refused a protected path the pinned spec does not declare; the human accepts
+        # it under the approved design for this sub-ticket. Its results stand, so the build merges it.
+        if st != "parked" or not reason.startswith("BLOCKED from merge gate:"):
+            raise Refused("--accept-paths applies to a merge gate park (BLOCKED from merge gate); "
+                          f"{t['id']} is {st} ({reason or 'no park'})")
+        head = _branch_tip(gitops.repo_root(), t)
+        paths, _ = undeclared_protected(root, cfg, t, head)
+        if not paths:
+            raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
+        dest = _copy_record(d, "ruling", a.accept_paths)
+        t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
+        move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
+    elif a.to:
+        if a.to != "spec-gate":
+            raise Refused("--to accepts only spec-gate")
+        if st != "parked" or t["spec"]["version"] < 1:
+            raise Refused(f"--to spec-gate needs a parked ticket with a spec version; {t['id']} is {st}")
+        move("awaiting-spec-gate", "to-spec-gate", {})
+    elif a.redispatch:
+        # Re-run the checkers on the same head after the cause of the park is fixed outside the ticket
+        # (a harness or gate defect, a killed checker). Round unchanged.
+        if st != "parked" or parked.get("from") not in ("checks-in-flight", "ready-for-merge"):
+            raise Refused(f"--redispatch applies to a sub-ticket parked from its checks; {t['id']} is {st} (from {parked.get('from')})")
+        head, moved = _supersede(root, t)
+        move("checks-in-flight", "redispatch", {"head": head, "superseded": moved})
+    elif a.replan:
+        # After a failed parent-close check: back to the planner with F as a ruling. Its new
+        # sub-tickets take the next free ids under this parent; the merged ones stay merged.
+        if st != "parked":
+            raise Refused(f"--replan applies to a parked parent; {t['id']} is {st}")
+        subs = store.subtickets_of(root, t["id"])
+        if not subs:
+            raise Refused(f"--replan applies to a parent with sub-tickets; {t['id']} has none")
+        unmerged = [f"{s['id']} is {s['status']}" for s in subtickets.split_plan(subs)[0] if s["status"] != "merged"]
+        if unmerged:
+            raise Refused(f"--replan needs every sub-ticket merged: {', '.join(unmerged)}")
+        dest = _copy_record(d, "ruling", a.replan)
+        move("ready-for-planner", "replan", {"ruling": _rel(root, dest)})
+    elif a.close:
+        if st == "closed":
+            raise Refused(f"{t['id']} is already closed")
+        move("closed", "close", decided("resolve --close"))
+    else:
+        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate | --redispatch | "
+                      "--replan F | --close")
+
+
+def _supersede(root: Path, t: dict) -> tuple:
+    """Set aside the head's failed result rows and log it; returns (head, roles moved)."""
+    head, moved = t.get("head"), _set_aside_failed_rows(root, t)
+    store.log_event(root, "results.superseded", ticket=t["id"], head=head, roles=moved)
+    return head, moved
+
+
+def _set_aside_failed_rows(root: Path, t: dict) -> list[str]:
+    """Move the head's rows that did not pass under results/<head>/superseded-<n>/, so the join cannot
+    read them as current and the build runs only the checkers with no row. The reviewer row stays
+    when it is APPROVE; the verifier and ci rows, written by one verifier run, stay together when
+    they are VERIFIED and PASS. Returns the roles moved."""
+    head = t.get("head")
+    moved: list[str] = []
+    if head:
+        rows = {k: v.get("status") for k, v in store.results_for(root, head).items()}
+        stale = [] if rows.get("reviewer") == "APPROVE" else ["reviewer"]
+        if not (rows.get("verifier") == "VERIFIED" and rows.get("ci") == "PASS"):
+            stale += ["verifier", "ci"]
+        rd = root / "results" / head
+        todo = [store.result_path(root, head, r) for r in stale if r in rows]
+        if todo:
+            dest = rd / f"superseded-{len(list(rd.glob('superseded-*'))) + 1}"
+            dest.mkdir(parents=True, exist_ok=True)
+            for f in todo:
+                f.rename(dest / f.name)
+                moved.append(f.stem)
+    return moved
+
+
+def decision_add(a, root, cfg):
+    t = store.load_ticket(root, a.id)  # any state, closed included
+    line = specstore.record_decision(root, t["id"], a.text)
+    store.log_event(root, "decision.recorded", ticket=t["id"], by=_by(), line=line, via="decision add")
+    out({"ok": True, "id": t["id"], "decision": line})
