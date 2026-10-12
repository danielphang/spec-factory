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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0488-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0488-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0488-verifier/wt` (branch `factory/T-0047.2`, base `700ce73e216d1fe5d218a9fe9b46e53545cf6674`, head `634117766e31f55980921ec1f9250d3d40e07c04`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0047.2

## T-0047.2 / Move instance and store setup to factory/setup.py
Depends on: T-0047.1
Parallel-safe: no (it edits `factory/cli.py`; it needs `factory/common.py` from T-0047.1)

Parent: T-0047 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part C of the parent's design, under the same move rules. New `factory/setup.py` gets
`_git_toplevel` through `paths_cmd` (`_git_toplevel`, `_new_instance_yaml`, `_revision`,
`_refuse_inside_store`, `_head_branch`, `_add_store_checkout`, `_exclude_store`, `_store_hint`,
`init_cmd`, `STATE_DIR_LINE`, `_ignored_files`, `_copy_mismatch`, `store_migrate`, `paths_cmd`).
It uses `import shutil` and keeps calling `shutil.copy2` through the module (Decision 6), so the
test in `tests/factory/test_store_migrate.py` that replaces `shutil.copy2` still reaches the moved
code. It imports what it needs from `factory.common` (it calls `fence`, `_in_flight` and `out`).
`stats_cmd` stays in `factory/cli.py` (Decision 4). `factory/cli.py` imports the moved commands
for `build_parser` and `main`.

Acceptance:
- NEW: Instance and store setup live in factory/setup.py.
  WHEN `uv run --frozen python -B -c 'import factory.setup' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/setup.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  THEN it prints exactly `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`
- REGRESSION: the parent's "drift checks live in factory/drift.py" and "shared helpers and the
  live-store fence live in factory/common.py" scenarios, with the commands and results given
  under T-0047.1.
- REGRESSION: M (its total `lines` across both sub-tickets stays at most 100).
- REGRESSION: R1 to R19. R7 counts `store.ensure_gitignore(root)` across all six modules, so the
  call that moves with `init_cmd` still counts.
- Intermediate check (NEW): WHEN `uv run --frozen python -B -c 'import factory.setup'` THEN it
  exits 0 and prints nothing.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/setup.py`
Out of scope: parts A, B, D and E; moving `stats_cmd`; any rename; any change to a moved body;
any change under `tests/`; any doc change.

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

Sub-ticket: T-0047.2, Move instance and store setup to factory/setup.py (parent T-0047, spec `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`)
Branch: `factory/T-0047.2` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0047.2`, base `700ce73e216d1fe5d218a9fe9b46e53545cf6674`, head `634117766e31f55980921ec1f9250d3d40e07c04` (one commit).

## What changed

This PR moves the harness's setup commands out of `factory/cli.py` into a new module, `factory/setup.py`. The setup commands are `factory init` (prepare a repository for the factory), `factory store migrate` (move the store, the factory's on-disk record of tickets and runs) and `factory paths` (print the paths a dispatcher needs). No command's behaviour changes. This is part C of the T-0047 split of `factory/cli.py`.

**C. `factory/setup.py`.**
- New module. It has a one-line docstring, `from __future__ import annotations`, and the imports its definitions use: `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `Path`, `yaml`, `factory.{gitops, instance, specstore, store}`, `_in_flight`, `fence` and `out` from `factory.common`, and `Refused`.
- The body is the block from `def _git_toplevel(` up to the blank lines before `def stats_cmd(`. That is 331 lines, copied byte for byte by a script that slices the file, in their original order: `_git_toplevel`, `_new_instance_yaml`, `_revision`, `_refuse_inside_store`, `_head_branch`, `_add_store_checkout`, `_exclude_store`, `_store_hint`, `init_cmd`, `STATE_DIR_LINE`, `_ignored_files`, `_copy_mismatch`, `store_migrate`, `paths_cmd`.
- It uses `import shutil` and still calls `shutil.copy2` through the module (Decision 6). The test in `tests/factory/test_store_migrate.py` that replaces `shutil.copy2` therefore still reaches the moved code. That test passed in every suite run below.
- `factory/cli.py` drops those 333 lines, which are the 331 moved lines and the two blank lines after them. It adds `from factory.setup import init_cmd, paths_cmd, store_migrate` for `build_parser`, and drops two imports it no longer uses: `import os` and `_in_flight`. The other imports it shared with the moved code (`json`, `shutil`, `subprocess`, `sys`, `yaml`, `specstore`) are still used in `factory/cli.py`, and ruff F401 confirms it.
- `stats_cmd` stays in `factory/cli.py` (Decision 4).
- `factory/cli.py` goes from 1,841 to 1,508 lines.

## Acceptance results

Each command ran through the fresh-HOME wrapper from the worktree root. Results are the actual output.

- NEW, Instance and store setup live in factory/setup.py.
  - Before: `ModuleNotFoundError: No module named 'factory.setup'`, nothing printed, exit 1.
  - After: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`, which matches exactly.
- Intermediate (NEW), `uv run --frozen python -B -c 'import factory.setup'`. Before: the same ModuleNotFoundError. After: exit 0, nothing printed.
- REGRESSION, drift scenario (T-0047.1): `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`.
- REGRESSION, common scenario (T-0047.1): `_add_spec_version _in_flight _integration_head _rel fence out`.
- REGRESSION, M, the check that the split moves code without rewriting it. Its GIVEN block was extracted verbatim from v2.md into the scratch directory and run with `TMPDIR` set to that directory. Output: `pairs=2 added=0 removed=0 lines=35`, and nothing after it. The 35 lines are 19 from T-0047.1 and 16 from this sub-ticket, so the total is within the 100-line limit.
- R1: `factory/__main__.py factory/drive.py factory/stats.py`
- R2: `7 True True`
- R3: `All checks passed!`, exit 0
- R4:
  - First run on HEAD: `1 failed, 575 passed in 549.04s`. Gloss: R4 is the full harness suite run under its own `/tmp` directory, plus a check that no test file changed.
  - The same command on base `700ce73` (a temporary checkout in scratch, since removed): `576 passed in 591.45s`, with nothing after it.
  - Rerun on HEAD: `576 passed in 552.33s (0:09:12)`, with nothing after it. See Known gaps.
- R5: `0 0`
- R6: `0`
- R7: `0 2 2`. The `store.ensure_gitignore(root)` call that moved with `init_cmd` is still counted, because R7 reads `factory/setup.py`.
- R8: `0`
- R9: `0`
- R10: `0 12 1`
- R11: `All checks passed!`, exit 0
- R12: `576 passed in 572.85s (0:09:32)`, with no later lines (no file under `tests/` changed).
- R13: `0`
- R14: `0 1`
- R15: `1 1`
- R16: `0`
- R17: `1 1`
- R18: `0 1 1 1`
- R19: `1 1 2`

Gates, each run exactly as written:
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`:
  - First run: `1 failed, 575 passed in 555.53s`, with the failure `tests/factory/test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`.
  - Rerun: `576 passed in 550.28s (0:09:10)`, exit 0.

## Tests added/changed

None. The sub-ticket says "Interim tests: none" and "Tests to change: none". The behaviour under test is where code lives, which the acceptance commands check directly. `git diff --name-only main...HEAD -- tests` prints nothing.

## Known gaps and uncertainties

- **One timing test failed in two of four full-suite runs on HEAD.** The test is `test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`.
  - Both failures had the same cause. The test's two checker runs (reviewer and verifier) each sleep 2 seconds. In both failures, T-0001.2's reviewer ended `KILLED` before the expected line `T-0001.2 "Two": parked: SPEC-DEFECT from verifier` was printed. The earlier assertion on the order the runs were seen passed.
  - Run on its own on HEAD, the test passed 3 times out of 3, in about 6 seconds each.
  - The full suite passed on base once (576 passed). On HEAD, the next two full runs passed: R12 and the R4 rerun. The gate rerun passed too.
  - The machine's load average was about 3 on 10 cores throughout.
  - The parent spec reports the same test failing once under load on the prototype (v2.md, around line 98). T-0047.1's implementer reported it failing once as well (run-0474).
  - This change only moves definitions between modules, and M shows that no definition's text changed. So I read the failures as the known timing flake, not a regression. I did not prove that: a failure 2 times in 4 on HEAD against 0 in 1 on base is weak evidence either way.
- **The `# -----` section comment stays in `factory/cli.py`.** The comment is `# ----- spec store (doc §Harness, Spec store; part K) ---...`. The design says to move a section comment with its code, or drop it where its section is now empty. Here that section is not empty in `factory/cli.py`: `stats_cmd`, `spec_tasks` and the gate helpers still follow it. So I left the comment there, and `factory/setup.py` relies on its module docstring instead. Moving the comment would leave `stats_cmd` under the "human surface" header.
- **One script ran without the wrapper.** My one-off move script (`scratch/move.py`) ran through plain `uv run`, without the fresh-HOME wrapper. It only reads and writes `factory/cli.py` and `factory/setup.py` in the worktree. Every test and check above did run through the wrapper.
- **A temporary base checkout was added and removed.** To run R4 on base, I added a detached git worktree at `scratch/base`, then removed and pruned it. `git worktree list` no longer shows it.

## Out-of-scope observations

- One full suite run takes about 9 to 10 minutes on this machine, close to the 10-minute limit a single tool call allows. I had to run it in the background and wait for it.
- The timing test above is fragile under CPU load. It may deserve its own issue: its 2-second sleeps decide whether a checker is killed. I did not change it.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The move is checked by machine (M: added=0 removed=0), all acceptance commands and both gates passed on HEAD, and the one failing test is a timing test known to be unreliable under load that passed on rerun.
ESCALATIONS: none

## Diff `700ce73e216d1fe5d218a9fe9b46e53545cf6674...634117766e31f55980921ec1f9250d3d40e07c04`

diff --git a/factory/cli.py b/factory/cli.py
index f8e5a71..280ca03 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -10,7 +10,6 @@ import datetime as dt
 import difflib
 import getpass
 import json
-import os
 import re
 import shutil
 import subprocess
@@ -20,8 +19,9 @@ from pathlib import Path
 import yaml
 
 from factory import compose, gitops, instance, specstore, status, store, subtickets, tripwire
-from factory.common import _add_spec_version, _in_flight, _rel, fence, out
+from factory.common import _add_spec_version, _rel, fence, out
 from factory.drift import _check_drift, _check_sibling_tests
+from factory.setup import init_cmd, paths_cmd, store_migrate
 from factory.store import Refused
 
 ROLES = ("triage", "spec_writer", "critic", "planner", "implementer", "reviewer", "verifier")
@@ -1139,339 +1139,6 @@ def decision_add(a, root, cfg):
 
 # ----- spec store (doc §Harness, Spec store; part K) ----------------------------------
 
-def _git_toplevel(cwd: Path) -> Path:
-    cp = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
-    if cp.returncode != 0 or not cp.stdout.strip():
-        raise Refused(f"factory init: {cwd} is not inside a git work tree")
-    return Path(cp.stdout.strip()).resolve()
-
-
-def _new_instance_yaml(repo_name: str) -> str:
-    """factory/instance.template.yaml with the per-instance values filled (design B.5)."""
-    text = instance.INSTANCE_TEMPLATE.read_text(encoding="utf-8")
-    for key, val in (("__REPO_NAME__", repo_name), ("__HARNESS__", str(instance.HARNESS))):
-        if key not in text:
-            raise Refused(f"{instance.INSTANCE_TEMPLATE} has no {key}")
-        text = text.replace(key, json.dumps(val, ensure_ascii=False))
-    return text
-
-
-def _revision() -> str:
-    rev = instance.harness_revision()
-    if rev is None:
-        raise Refused(f"factory init: cannot read the harness revision of {instance.HARNESS} (not a git checkout?)")
-    return rev
-
-
-def _refuse_inside_store(cwd: Path, top: Path) -> None:
-    """Refuse `init` from inside the store checkout, where it would build a second instance inside
-    the live store (design A.1). Called only with FACTORY_INSTANCE unset."""
-    if gitops.git(top, "symbolic-ref", "-q", "HEAD", check=False) == f"refs/heads/{gitops.STORE_BRANCH}":  # unborn too
-        raise Refused(f"factory init: {cwd} is inside the store checkout {top} (branch {gitops.STORE_BRANCH}); "
-                      "run init from the repository root")
-    # Whatever the store has checked out (a detached HEAD, another branch): the instance found by
-    # walking up names its store, and a checkout of the same repository at or under it is that store.
-    found = instance.find()
-    if found is None:
-        return
-    try:
-        cfg = instance.load_config(found)
-    except (OSError, yaml.YAMLError):  # an unreadable config names no store: nothing to compare
-        return
-    if not isinstance(cfg, dict) or not isinstance(cfg.get("state_dir"), str):
-        return
-    own = instance.own_state_root(found, cfg)
-    if top == own or (top.is_relative_to(own)
-                      and gitops.common_dir(top) == gitops.common_dir(instance.repo_root(found))):
-        raise Refused(f"factory init: {cwd} is inside the store {own} of the instance {found}; "
-                      "run init from the repository root")
-
-
-def _head_branch(repo: Path) -> str:
-    """The branch checked out at `repo`, or HEAD when it is detached."""
-    return gitops.git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False) or "HEAD"
-
-
-def _add_store_checkout(repo: Path, root: Path, branch: str, cfg_path: Path) -> None:
-    """Make the missing own store `root` a checkout of the store branch (design A.3): refused at a
-    path `branch` has ever tracked; the branch comes from a local branch, else the one remote that
-    carries it, else a new orphan, which needs no commit and so no git identity."""
-    store_branch = gitops.STORE_BRANCH
-    rel = root.relative_to(repo).as_posix() if root.is_relative_to(repo) else None
-    if rel is not None:
-        sha = gitops.last_tracked(repo, branch, rel)
-        if sha:
-            raise Refused(f"factory init: {branch} has tracked files under {rel} (last in commit {sha}); a checkout "
-                          f"of any older commit would overwrite a store kept there; set another state_dir in {cfg_path}")
-    local = bool(gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{store_branch}", check=False))
-    remotes = [] if local else gitops.remote_branches(repo, store_branch)
-    if len(remotes) > 1:
-        raise Refused(f"factory init: no local branch {store_branch}, and more than one remote carries it "
-                      f"({', '.join(remotes)}); run git branch {store_branch} <remote>/{store_branch} for the one "
-                      "to use, then init again")
-    if local:
-        args = ["worktree", "add", "-q", str(root), store_branch]
-    elif remotes:
-        args = ["worktree", "add", "-q", "--track", "-b", store_branch, str(root), remotes[0]]
-    else:
-        args = ["worktree", "add", "-q", "--orphan", "-b", store_branch, str(root)]
-    try:
-        gitops.git(repo, *args)
-    except Refused as e:
-        raise Refused(f"factory init: cannot check out the store at {root}: {e}") from None
-    if rel is not None:
-        _exclude_store(repo, rel)
-
-
-def _exclude_store(repo: Path, rel: str) -> None:
-    """The integration checkout ignores the store at `rel` through the repo's exclude file."""
-    exclude = Path(gitops.git(repo, "rev-parse", "--git-path", "info/exclude"))
-    exclude = exclude if exclude.is_absolute() else repo / exclude
-    have = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
-    line = f"/{rel}/"
-    if line not in have.splitlines():
-        store.write_text(exclude, have + ("" if not have or have.endswith("\n") else "\n") + line + "\n")
-
-
-def _store_hint(repo: Path, root: Path) -> None:
-    """An existing own store that is not the store branch's checkout is left alone (design A.5)."""
-    top = gitops.git(root, "rev-parse", "--show-toplevel", check=False)
-    if top and Path(top).resolve() == root.resolve() and gitops.common_dir(root) == gitops.common_dir(repo):
-        if _head_branch(root) == "HEAD":
-            print(f"the store worktree {root} is on a detached HEAD; check out {gitops.STORE_BRANCH} there",
-                  file=sys.stderr)
-        return
-    print(f"the store {root} is not on its branch {gitops.STORE_BRANCH}; factory store migrate --to PATH moves it",
-          file=sys.stderr)
-
-
-def init_cmd(a):
-    """Create whatever of the instance is missing (design B.5); idempotent. The instance is
-    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory, which may not
-    be inside the store checkout (A.1). Its pieces (instance.yaml, context.md, harness.lock, agent
-    files) are written only when the store in use is the instance's own: a run on a throwaway store
-    (FACTORY_STATE elsewhere, as every test does) initialises that store and nothing else. So
-    creating an instance while FACTORY_STATE names another store is refused before anything is
-    written: it would leave an instance.yaml with no context.md. A missing own store becomes a git
-    worktree of the store branch (A.3) before any instance file is written, so a refusal or a
-    failed git step leaves nothing behind."""
-    cwd = instance.caller_cwd()
-    top = _git_toplevel(cwd)
-    if instance.env_path("FACTORY_INSTANCE") is None:
-        _refuse_inside_store(cwd, top)
-    inst = instance.env_path("FACTORY_INSTANCE") or top / instance.DIRNAME
-    created: list[str] = []
-    cfg_path = inst / instance.CONFIG_NAME
-    new_text = None
-    if cfg_path.exists():
-        cfg = instance.load_config(inst)
-    else:
-        if not a.repo_name:
-            raise Refused(f"factory init: {cfg_path} does not exist; pass --repo-name NAME to create it")
-        new_text = _new_instance_yaml(a.repo_name)
-        cfg = yaml.safe_load(new_text)
-    root = instance.state_root(inst, cfg)
-    fence(inst, cfg, root)
-    own = instance.is_own_store(inst, cfg, root)
-    if new_text is not None:
-        if not own:
-            raise Refused(f"factory init: {inst} has no {instance.CONFIG_NAME}, and FACTORY_STATE names another "
-                          f"store ({root}); create the instance with FACTORY_STATE unset, then init that store")
-        _revision()  # refuse before writing anything if the lock cannot be written
-    repo = instance.repo_root(inst)
-    existed = root.exists()
-    if own and not existed:
-        if new_text is None and (os.environ.get("FACTORY_INTEGRATION_BRANCH") or cfg.get("integration_branch")):
-            branch = gitops.integration_branch(cfg, repo)
-        else:  # its own fallback, rev-parse --abbrev-ref HEAD, fails on an unborn branch, never tracked (A.3.1)
-            branch = _head_branch(repo)
-        _add_store_checkout(repo, root, branch, cfg_path)
-    if new_text is not None:
-        store.write_text(cfg_path, new_text)
-        created.append(str(cfg_path))
-    agents: list[str] = []
-    store_branch = None
-    if own:
-        ctx = inst / "context.md"
-        if not ctx.exists():
-            store.write_text(ctx, instance.CONTEXT_TEMPLATE.read_text(encoding="utf-8"))
-            created.append(str(ctx))
-        lock = inst / "harness.lock"
-        if not lock.exists():
-            store.write_text(lock, _revision() + "\n")
-            created.append(str(lock))
-        dest = repo / ".claude" / "agents"
-        for src in sorted(instance.AGENTS.glob("factory-*.md")):
-            if not (dest / src.name).exists():
-                (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
-                shutil.copyfile(src, dest / src.name)
-                agents.append(str(dest / src.name))
-        checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
-        if checkout is not None and checkout.resolve() == root:
-            store_branch = gitops.STORE_BRANCH
-        elif existed:
-            _store_hint(repo, root)
-    had_gitignore, had_gitattributes = (root / ".gitignore").exists(), (root / ".gitattributes").exists()
-    store.ensure_gitignore(root)
-    store.ensure_gitattributes(root)
-    written = specstore.init(root)
-    if not had_gitignore:
-        written.insert(0, ".gitignore")
-    if not had_gitattributes:
-        written.insert(0, ".gitattributes")
-    if written or created or agents:
-        store.log_event(root, "store.initialised", files=written, instance=created, agents=agents)
-    if agents:
-        print("restart the session so the agents register", file=sys.stderr)
-    out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
-         "created": created, "agents": agents, "store_branch": store_branch})
-
-
-STATE_DIR_LINE = re.compile(r"^(state_dir:[ \t]*)([^#\n]*?)([ \t]*(?:#.*)?)$", re.M)
-
-
-def _ignored_files(where: Path) -> list[str]:
-    """Every file git ignores under the directory `where`, relative to it. Git lists a nested
-    repository (a role's clone in its scratch directory) as its directory: its files are listed
-    here one by one. Empty directories are not files and are not listed."""
-    # factory: empty directories are not carried (git lists no such entry); copy whole trees if a
-    # role's scratch ever needs one
-    files = []
-    listed = gitops.git(where, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", ".")
-    for entry in filter(None, listed.split("\0")):
-        if entry.endswith("/"):
-            files += sorted(p.relative_to(where).as_posix() for p in (where / entry).rglob("*")
-                            if p.is_symlink() or p.is_file())
-        else:
-            files.append(entry)
-    return files
-
-
-def _copy_mismatch(old: Path, new: Path, listed: list[str]) -> str | None:
-    """The first way the copy at `new` differs from `old` (design B step 4), or None."""
-    for f in listed:
-        src, dst = old / f, new / f
-        if src.is_symlink():
-            same = dst.is_symlink() and os.readlink(dst) == os.readlink(src)
-        else:
-            same = dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes()
-        if not same:
-            return f"{f} differs"
-    copied = _ignored_files(new)
-    if len(copied) != len(listed):
-        return f"{len(copied)} ignored files at the new path, {len(listed)} listed"
-    status = gitops.git(new, "status", "--porcelain")
-    return f"git status there is not clean ({status.splitlines()[0].strip()})" if status else None
-
-
-def store_migrate(a, root, cfg):
-    """Move the instance's own store, a plain directory tracked on the integration branch, onto the
-    store branch checked out at --to PATH (design B). Every refusal comes before the first write. A
-    copy that does not match is undone and exits 1, before anything is deleted. Makes no commit on
-    the integration branch and pushes nothing: the operator reviews and commits both sides."""
-    def refuse(msg: str):
-        raise Refused(f"factory store migrate: {msg}")
-
-    inst = instance.require()
-    repo = instance.repo_root(inst)
-    sb = gitops.STORE_BRANCH
-    if not instance.is_own_store(inst, cfg, root):
-        refuse(f"the store in use, {root}, is not the instance's own (FACTORY_STATE names another); unset FACTORY_STATE")
-    old, rel_old = root.resolve(), cfg["state_dir"]
-    checkout = gitops.checkout_of(repo, sb)
-    if checkout is not None and checkout.resolve() == old:
-        refuse(f"the store {old} is already the checkout of {sb}")
-    if checkout is not None or gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{sb}", check=False):
-        refuse(f"a local branch {sb} already exists; this command starts it from the store")
-    branch, head = gitops.integration_branch(cfg, repo), _head_branch(repo)
-    if head == "HEAD" or head != branch:
-        refuse(f"the integration branch {'' if head == 'HEAD' else branch + ' '}is not checked out at {repo} "
-               f"({'its HEAD is detached' if head == 'HEAD' else head + ' is'}); check it out first")
-    runs = _in_flight(root)
-    if runs:
-        refuse(f"runs in flight on the store: {', '.join(runs)}; wait until they finish")
-    under = [ln.split(" ", 1)[1] for ln in gitops.git(repo, "worktree", "list", "--porcelain").splitlines()
-             if ln.startswith("worktree ") and Path(ln.split(" ", 1)[1]).resolve().is_relative_to(old)]
-    if under:
-        refuse(f"git worktrees under the store: {', '.join(under)}; remove them first")
-    status = gitops.git(repo, "status", "--porcelain", "--untracked-files=all", "--", rel_old)
-    if status:
-        names = [ln.strip().split(None, 1)[1] for ln in status.splitlines()]
-        refuse(f"uncommitted store files: {', '.join(names)}; commit them on {branch} first")
-    new = (repo / a.to).resolve()
-    if new.exists():
-        refuse(f"{a.to} exists; choose a path that does not")
-    if new.is_relative_to(old):
-        refuse(f"{a.to} is inside the store {old}, which this command deletes once it has moved")
-    rel_new = new.relative_to(repo).as_posix() if new.is_relative_to(repo) else None
-    if rel_new is not None:
-        sha = gitops.last_tracked(repo, branch, rel_new)  # init's never-tracked test (design A.3.1)
-        if sha:
-            refuse(f"{branch} has tracked files under {rel_new} (last in commit {sha}); a checkout of any older "
-                   "commit would overwrite a store kept there; choose another path")
-    cfg_path = inst / instance.CONFIG_NAME
-    text = cfg_path.read_text(encoding="utf-8")
-    m = STATE_DIR_LINE.search(text)
-    if m is None:
-        refuse(f"{cfg_path} has no state_dir: line to rewrite")
-    tree = gitops.git(repo, "rev-parse", "-q", "--verify", f"{branch}:{rel_old}", check=False)
-    if not tree or gitops.git(repo, "cat-file", "-t", tree) != "tree":
-        refuse(f"the store {rel_old} is not tracked on {branch}")
-    carried = gitops.rev(repo, branch)
-
-    # 1-2. The branch, one root commit of the store as last committed, checked out at PATH.
-    created = new  # the outermost directory this command creates, removed on undo
-    while not created.parent.exists():
-        created = created.parent
-    msg = f"store: carried over from {branch} at {carried}; earlier history: git log {carried} -- {rel_old}"
-    gitops.git(repo, "branch", sb, gitops.git(repo, "commit-tree", tree, "-m", msg))
-    try:
-        gitops.git(repo, "worktree", "add", "-q", str(new), sb)
-        # 3. The files git ignores, which the branch does not carry: run scratch directories, tripwire baselines.
-        listed = _ignored_files(old)
-        for f in listed:
-            (new / f).parent.mkdir(parents=True, exist_ok=True)
-            shutil.copy2(old / f, new / f, follow_symlinks=False)
-        # 4. Verify before deleting anything.
-        bad = _copy_mismatch(old, new, listed)
-        if bad:
-            raise RuntimeError(f"factory store migrate: the copy at {a.to} does not match: {bad}; "
-                               f"removed the new worktree and branch {sb}, the store at {rel_old} is unchanged")
-    except BaseException:
-        gitops.git(repo, "worktree", "remove", "--force", str(new), check=False)
-        gitops.git(repo, "worktree", "prune", check=False)
-        gitops.git(repo, "branch", "-D", sb, check=False)
-        shutil.rmtree(created, ignore_errors=True)
-        raise
-    # 5. The integration checkout: untrack the old path, ignore the new one, point state_dir at it.
-    gitops.git(repo, "rm", "-r", "-q", "--cached", rel_old)
-    if rel_new is not None:
-        _exclude_store(repo, rel_new)
-    store.write_text(cfg_path, text[:m.start(2)] + a.to + text[m.end(2):])
-    shutil.rmtree(old)
-    # 6.
-    fields = {"from": rel_old, "to": a.to, "branch": sb, "carried_from": carried, "copied": len(listed)}
-    store.log_event(new, "store.migrated", **fields)
-    out({"ok": True, **fields})
-    print(f"next: review git status and commit on {branch} (the old store untracked, state_dir now {a.to}); "
-          f"then commit the store (git -C {a.to} add -A && git -C {a.to} commit) and push it "
-          f"(git push origin {sb})", file=sys.stderr)
-
-
-def paths_cmd(a):
-    """Absolute paths a dispatcher needs (design B.6). Runs no lock check and writes nothing."""
-    inst = instance.find()
-    state = None
-    if inst is not None:
-        state = str(instance.state_root(inst, instance.load_config(inst)))
-    h = instance.HARNESS
-    out({"ok": True, "harness": str(h), "bin": str(h / "bin" / "factory"),
-         "intake_workflow": str(h / "factory" / "workflows" / "intake.js"),
-         "build_workflow": str(h / "factory" / "workflows" / "build.js"),
-         "harness_revision": instance.harness_revision(),
-         "instance": str(inst) if inst is not None else None, "state": state})
-
-
 def stats_cmd(a):
     """What each role catches and costs, counted from one or more stores (factory/stats.py). Like
     `paths`, it needs no instance, runs no fence or lock check and writes nothing. With no --store it
diff --git a/factory/setup.py b/factory/setup.py
new file mode 100644
index 0000000..2f8474f
--- /dev/null
+++ b/factory/setup.py
@@ -0,0 +1,349 @@
+"""Instance and store setup: `factory init`, `factory store migrate` and `factory paths`."""
+from __future__ import annotations
+
+import json
+import os
+import re
+import shutil
+import subprocess
+import sys
+from pathlib import Path
+
+import yaml
+
+from factory import gitops, instance, specstore, store
+from factory.common import _in_flight, fence, out
+from factory.store import Refused
+
+
+def _git_toplevel(cwd: Path) -> Path:
+    cp = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
+    if cp.returncode != 0 or not cp.stdout.strip():
+        raise Refused(f"factory init: {cwd} is not inside a git work tree")
+    return Path(cp.stdout.strip()).resolve()
+
+
+def _new_instance_yaml(repo_name: str) -> str:
+    """factory/instance.template.yaml with the per-instance values filled (design B.5)."""
+    text = instance.INSTANCE_TEMPLATE.read_text(encoding="utf-8")
+    for key, val in (("__REPO_NAME__", repo_name), ("__HARNESS__", str(instance.HARNESS))):
+        if key not in text:
+            raise Refused(f"{instance.INSTANCE_TEMPLATE} has no {key}")
+        text = text.replace(key, json.dumps(val, ensure_ascii=False))
+    return text
+
+
+def _revision() -> str:
+    rev = instance.harness_revision()
+    if rev is None:
+        raise Refused(f"factory init: cannot read the harness revision of {instance.HARNESS} (not a git checkout?)")
+    return rev
+
+
+def _refuse_inside_store(cwd: Path, top: Path) -> None:
+    """Refuse `init` from inside the store checkout, where it would build a second instance inside
+    the live store (design A.1). Called only with FACTORY_INSTANCE unset."""
+    if gitops.git(top, "symbolic-ref", "-q", "HEAD", check=False) == f"refs/heads/{gitops.STORE_BRANCH}":  # unborn too
+        raise Refused(f"factory init: {cwd} is inside the store checkout {top} (branch {gitops.STORE_BRANCH}); "
+                      "run init from the repository root")
+    # Whatever the store has checked out (a detached HEAD, another branch): the instance found by
+    # walking up names its store, and a checkout of the same repository at or under it is that store.
+    found = instance.find()
+    if found is None:
+        return
+    try:
+        cfg = instance.load_config(found)
+    except (OSError, yaml.YAMLError):  # an unreadable config names no store: nothing to compare
+        return
+    if not isinstance(cfg, dict) or not isinstance(cfg.get("state_dir"), str):
+        return
+    own = instance.own_state_root(found, cfg)
+    if top == own or (top.is_relative_to(own)
+                      and gitops.common_dir(top) == gitops.common_dir(instance.repo_root(found))):
+        raise Refused(f"factory init: {cwd} is inside the store {own} of the instance {found}; "
+                      "run init from the repository root")
+
+
+def _head_branch(repo: Path) -> str:
+    """The branch checked out at `repo`, or HEAD when it is detached."""
+    return gitops.git(repo, "symbolic-ref", "-q", "--short", "HEAD", check=False) or "HEAD"
+
+
+def _add_store_checkout(repo: Path, root: Path, branch: str, cfg_path: Path) -> None:
+    """Make the missing own store `root` a checkout of the store branch (design A.3): refused at a
+    path `branch` has ever tracked; the branch comes from a local branch, else the one remote that
+    carries it, else a new orphan, which needs no commit and so no git identity."""
+    store_branch = gitops.STORE_BRANCH
+    rel = root.relative_to(repo).as_posix() if root.is_relative_to(repo) else None
+    if rel is not None:
+        sha = gitops.last_tracked(repo, branch, rel)
+        if sha:
+            raise Refused(f"factory init: {branch} has tracked files under {rel} (last in commit {sha}); a checkout "
+                          f"of any older commit would overwrite a store kept there; set another state_dir in {cfg_path}")
+    local = bool(gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{store_branch}", check=False))
+    remotes = [] if local else gitops.remote_branches(repo, store_branch)
+    if len(remotes) > 1:
+        raise Refused(f"factory init: no local branch {store_branch}, and more than one remote carries it "
+                      f"({', '.join(remotes)}); run git branch {store_branch} <remote>/{store_branch} for the one "
+                      "to use, then init again")
+    if local:
+        args = ["worktree", "add", "-q", str(root), store_branch]
+    elif remotes:
+        args = ["worktree", "add", "-q", "--track", "-b", store_branch, str(root), remotes[0]]
+    else:
+        args = ["worktree", "add", "-q", "--orphan", "-b", store_branch, str(root)]
+    try:
+        gitops.git(repo, *args)
+    except Refused as e:
+        raise Refused(f"factory init: cannot check out the store at {root}: {e}") from None
+    if rel is not None:
+        _exclude_store(repo, rel)
+
+
+def _exclude_store(repo: Path, rel: str) -> None:
+    """The integration checkout ignores the store at `rel` through the repo's exclude file."""
+    exclude = Path(gitops.git(repo, "rev-parse", "--git-path", "info/exclude"))
+    exclude = exclude if exclude.is_absolute() else repo / exclude
+    have = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
+    line = f"/{rel}/"
+    if line not in have.splitlines():
+        store.write_text(exclude, have + ("" if not have or have.endswith("\n") else "\n") + line + "\n")
+
+
+def _store_hint(repo: Path, root: Path) -> None:
+    """An existing own store that is not the store branch's checkout is left alone (design A.5)."""
+    top = gitops.git(root, "rev-parse", "--show-toplevel", check=False)
+    if top and Path(top).resolve() == root.resolve() and gitops.common_dir(root) == gitops.common_dir(repo):
+        if _head_branch(root) == "HEAD":
+            print(f"the store worktree {root} is on a detached HEAD; check out {gitops.STORE_BRANCH} there",
+                  file=sys.stderr)
+        return
+    print(f"the store {root} is not on its branch {gitops.STORE_BRANCH}; factory store migrate --to PATH moves it",
+          file=sys.stderr)
+
+
+def init_cmd(a):
+    """Create whatever of the instance is missing (design B.5); idempotent. The instance is
+    FACTORY_INSTANCE, else `.factory/` at the git top level of the working directory, which may not
+    be inside the store checkout (A.1). Its pieces (instance.yaml, context.md, harness.lock, agent
+    files) are written only when the store in use is the instance's own: a run on a throwaway store
+    (FACTORY_STATE elsewhere, as every test does) initialises that store and nothing else. So
+    creating an instance while FACTORY_STATE names another store is refused before anything is
+    written: it would leave an instance.yaml with no context.md. A missing own store becomes a git
+    worktree of the store branch (A.3) before any instance file is written, so a refusal or a
+    failed git step leaves nothing behind."""
+    cwd = instance.caller_cwd()
+    top = _git_toplevel(cwd)
+    if instance.env_path("FACTORY_INSTANCE") is None:
+        _refuse_inside_store(cwd, top)
+    inst = instance.env_path("FACTORY_INSTANCE") or top / instance.DIRNAME
+    created: list[str] = []
+    cfg_path = inst / instance.CONFIG_NAME
+    new_text = None
+    if cfg_path.exists():
+        cfg = instance.load_config(inst)
+    else:
+        if not a.repo_name:
+            raise Refused(f"factory init: {cfg_path} does not exist; pass --repo-name NAME to create it")
+        new_text = _new_instance_yaml(a.repo_name)
+        cfg = yaml.safe_load(new_text)
+    root = instance.state_root(inst, cfg)
+    fence(inst, cfg, root)
+    own = instance.is_own_store(inst, cfg, root)
+    if new_text is not None:
+        if not own:
+            raise Refused(f"factory init: {inst} has no {instance.CONFIG_NAME}, and FACTORY_STATE names another "
+                          f"store ({root}); create the instance with FACTORY_STATE unset, then init that store")
+        _revision()  # refuse before writing anything if the lock cannot be written
+    repo = instance.repo_root(inst)
+    existed = root.exists()
+    if own and not existed:
+        if new_text is None and (os.environ.get("FACTORY_INTEGRATION_BRANCH") or cfg.get("integration_branch")):
+            branch = gitops.integration_branch(cfg, repo)
+        else:  # its own fallback, rev-parse --abbrev-ref HEAD, fails on an unborn branch, never tracked (A.3.1)
+            branch = _head_branch(repo)
+        _add_store_checkout(repo, root, branch, cfg_path)
+    if new_text is not None:
+        store.write_text(cfg_path, new_text)
+        created.append(str(cfg_path))
+    agents: list[str] = []
+    store_branch = None
+    if own:
+        ctx = inst / "context.md"
+        if not ctx.exists():
+            store.write_text(ctx, instance.CONTEXT_TEMPLATE.read_text(encoding="utf-8"))
+            created.append(str(ctx))
+        lock = inst / "harness.lock"
+        if not lock.exists():
+            store.write_text(lock, _revision() + "\n")
+            created.append(str(lock))
+        dest = repo / ".claude" / "agents"
+        for src in sorted(instance.AGENTS.glob("factory-*.md")):
+            if not (dest / src.name).exists():
+                (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
+                shutil.copyfile(src, dest / src.name)
+                agents.append(str(dest / src.name))
+        checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
+        if checkout is not None and checkout.resolve() == root:
+            store_branch = gitops.STORE_BRANCH
+        elif existed:
+            _store_hint(repo, root)
+    had_gitignore, had_gitattributes = (root / ".gitignore").exists(), (root / ".gitattributes").exists()
+    store.ensure_gitignore(root)
+    store.ensure_gitattributes(root)
+    written = specstore.init(root)
+    if not had_gitignore:
+        written.insert(0, ".gitignore")
+    if not had_gitattributes:
+        written.insert(0, ".gitattributes")
+    if written or created or agents:
+        store.log_event(root, "store.initialised", files=written, instance=created, agents=agents)
+    if agents:
+        print("restart the session so the agents register", file=sys.stderr)
+    out({"ok": True, "written": written, "active": True, "instance": str(inst), "state": str(root),
+         "created": created, "agents": agents, "store_branch": store_branch})
+
+
+STATE_DIR_LINE = re.compile(r"^(state_dir:[ \t]*)([^#\n]*?)([ \t]*(?:#.*)?)$", re.M)
+
+
+def _ignored_files(where: Path) -> list[str]:
+    """Every file git ignores under the directory `where`, relative to it. Git lists a nested
+    repository (a role's clone in its scratch directory) as its directory: its files are listed
+    here one by one. Empty directories are not files and are not listed."""
+    # factory: empty directories are not carried (git lists no such entry); copy whole trees if a
+    # role's scratch ever needs one
+    files = []
+    listed = gitops.git(where, "ls-files", "--others", "--ignored", "--exclude-standard", "-z", "--", ".")
+    for entry in filter(None, listed.split("\0")):
+        if entry.endswith("/"):
+            files += sorted(p.relative_to(where).as_posix() for p in (where / entry).rglob("*")
+                            if p.is_symlink() or p.is_file())
+        else:
+            files.append(entry)
+    return files
+
+
+def _copy_mismatch(old: Path, new: Path, listed: list[str]) -> str | None:
+    """The first way the copy at `new` differs from `old` (design B step 4), or None."""
+    for f in listed:
+        src, dst = old / f, new / f
+        if src.is_symlink():
+            same = dst.is_symlink() and os.readlink(dst) == os.readlink(src)
+        else:
+            same = dst.is_file() and not dst.is_symlink() and dst.read_bytes() == src.read_bytes()
+        if not same:
+            return f"{f} differs"
+    copied = _ignored_files(new)
+    if len(copied) != len(listed):
+        return f"{len(copied)} ignored files at the new path, {len(listed)} listed"
+    status = gitops.git(new, "status", "--porcelain")
+    return f"git status there is not clean ({status.splitlines()[0].strip()})" if status else None
+
+
+def store_migrate(a, root, cfg):
+    """Move the instance's own store, a plain directory tracked on the integration branch, onto the
+    store branch checked out at --to PATH (design B). Every refusal comes before the first write. A
+    copy that does not match is undone and exits 1, before anything is deleted. Makes no commit on
+    the integration branch and pushes nothing: the operator reviews and commits both sides."""
+    def refuse(msg: str):
+        raise Refused(f"factory store migrate: {msg}")
+
+    inst = instance.require()
+    repo = instance.repo_root(inst)
+    sb = gitops.STORE_BRANCH
+    if not instance.is_own_store(inst, cfg, root):
+        refuse(f"the store in use, {root}, is not the instance's own (FACTORY_STATE names another); unset FACTORY_STATE")
+    old, rel_old = root.resolve(), cfg["state_dir"]
+    checkout = gitops.checkout_of(repo, sb)
+    if checkout is not None and checkout.resolve() == old:
+        refuse(f"the store {old} is already the checkout of {sb}")
+    if checkout is not None or gitops.git(repo, "rev-parse", "-q", "--verify", f"refs/heads/{sb}", check=False):
+        refuse(f"a local branch {sb} already exists; this command starts it from the store")
+    branch, head = gitops.integration_branch(cfg, repo), _head_branch(repo)
+    if head == "HEAD" or head != branch:
+        refuse(f"the integration branch {'' if head == 'HEAD' else branch + ' '}is not checked out at {repo} "
+               f"({'its HEAD is detached' if head == 'HEAD' else head + ' is'}); check it out first")
+    runs = _in_flight(root)
+    if runs:
+        refuse(f"runs in flight on the store: {', '.join(runs)}; wait until they finish")
+    under = [ln.split(" ", 1)[1] for ln in gitops.git(repo, "worktree", "list", "--porcelain").splitlines()
+             if ln.startswith("worktree ") and Path(ln.split(" ", 1)[1]).resolve().is_relative_to(old)]
+    if under:
+        refuse(f"git worktrees under the store: {', '.join(under)}; remove them first")
+    status = gitops.git(repo, "status", "--porcelain", "--untracked-files=all", "--", rel_old)
+    if status:
+        names = [ln.strip().split(None, 1)[1] for ln in status.splitlines()]
+        refuse(f"uncommitted store files: {', '.join(names)}; commit them on {branch} first")
+    new = (repo / a.to).resolve()
+    if new.exists():
+        refuse(f"{a.to} exists; choose a path that does not")
+    if new.is_relative_to(old):
+        refuse(f"{a.to} is inside the store {old}, which this command deletes once it has moved")
+    rel_new = new.relative_to(repo).as_posix() if new.is_relative_to(repo) else None
+    if rel_new is not None:
+        sha = gitops.last_tracked(repo, branch, rel_new)  # init's never-tracked test (design A.3.1)
+        if sha:
+            refuse(f"{branch} has tracked files under {rel_new} (last in commit {sha}); a checkout of any older "
+                   "commit would overwrite a store kept there; choose another path")
+    cfg_path = inst / instance.CONFIG_NAME
+    text = cfg_path.read_text(encoding="utf-8")
+    m = STATE_DIR_LINE.search(text)
+    if m is None:
+        refuse(f"{cfg_path} has no state_dir: line to rewrite")
+    tree = gitops.git(repo, "rev-parse", "-q", "--verify", f"{branch}:{rel_old}", check=False)
+    if not tree or gitops.git(repo, "cat-file", "-t", tree) != "tree":
+        refuse(f"the store {rel_old} is not tracked on {branch}")
+    carried = gitops.rev(repo, branch)
+
+    # 1-2. The branch, one root commit of the store as last committed, checked out at PATH.
+    created = new  # the outermost directory this command creates, removed on undo
+    while not created.parent.exists():
+        created = created.parent
+    msg = f"store: carried over from {branch} at {carried}; earlier history: git log {carried} -- {rel_old}"
+    gitops.git(repo, "branch", sb, gitops.git(repo, "commit-tree", tree, "-m", msg))
+    try:
+        gitops.git(repo, "worktree", "add", "-q", str(new), sb)
+        # 3. The files git ignores, which the branch does not carry: run scratch directories, tripwire baselines.
+        listed = _ignored_files(old)
+        for f in listed:
+            (new / f).parent.mkdir(parents=True, exist_ok=True)
+            shutil.copy2(old / f, new / f, follow_symlinks=False)
+        # 4. Verify before deleting anything.
+        bad = _copy_mismatch(old, new, listed)
+        if bad:
+            raise RuntimeError(f"factory store migrate: the copy at {a.to} does not match: {bad}; "
+                               f"removed the new worktree and branch {sb}, the store at {rel_old} is unchanged")
+    except BaseException:
+        gitops.git(repo, "worktree", "remove", "--force", str(new), check=False)
+        gitops.git(repo, "worktree", "prune", check=False)
+        gitops.git(repo, "branch", "-D", sb, check=False)
+        shutil.rmtree(created, ignore_errors=True)
+        raise
+    # 5. The integration checkout: untrack the old path, ignore the new one, point state_dir at it.
+    gitops.git(repo, "rm", "-r", "-q", "--cached", rel_old)
+    if rel_new is not None:
+        _exclude_store(repo, rel_new)
+    store.write_text(cfg_path, text[:m.start(2)] + a.to + text[m.end(2):])
+    shutil.rmtree(old)
+    # 6.
+    fields = {"from": rel_old, "to": a.to, "branch": sb, "carried_from": carried, "copied": len(listed)}
+    store.log_event(new, "store.migrated", **fields)
+    out({"ok": True, **fields})
+    print(f"next: review git status and commit on {branch} (the old store untracked, state_dir now {a.to}); "
+          f"then commit the store (git -C {a.to} add -A && git -C {a.to} commit) and push it "
+          f"(git push origin {sb})", file=sys.stderr)
+
+
+def paths_cmd(a):
+    """Absolute paths a dispatcher needs (design B.6). Runs no lock check and writes nothing."""
+    inst = instance.find()
+    state = None
+    if inst is not None:
+        state = str(instance.state_root(inst, instance.load_config(inst)))
+    h = instance.HARNESS
+    out({"ok": True, "harness": str(h), "bin": str(h / "bin" / "factory"),
+         "intake_workflow": str(h / "factory" / "workflows" / "intake.js"),
+         "build_workflow": str(h / "factory" / "workflows" / "build.js"),
+         "harness_revision": instance.harness_revision(),
+         "instance": str(inst) if inst is not None else None, "state": state})
