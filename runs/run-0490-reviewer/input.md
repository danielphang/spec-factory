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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0490-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0490-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0490-reviewer/wt` (branch `factory/T-0047.3`, base `57b46e18ca48c71254487dec086b27c3d34ec79c`, head `c30b80f45a39824b71c7064cc22e2563a53f9438`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0047.3

## T-0047.3 / Move the gates to factory/gates.py, and name gates.py in the README and the principles
Depends on: T-0047.2
Parallel-safe: no (it edits `factory/cli.py`; it depends on T-0047.2 only so that the two do not edit `factory/cli.py` at once)

Parent: T-0047 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part D of the parent's design, under the same move rules.
- New `factory/gates.py` gets `ticket_head`, `results_record`, `results_show`, `DECLARED_RE`,
  `_in_repo`, `declared_paths`, `undeclared_protected`, `_branch_tip`, `merge_cmd`,
  `REVIEWER_STATUSES`, `VERIFIER_STATUSES`, `MAX_CONFLICT_RUNS`, `ticket_join`,
  `ticket_parent_check`, `_verifier_rows`, `_reused_subticket_run`, `_parent_close_verified`,
  `archive_cmd`. `factory/cli.py` imports `_parent_close_verified` for `ticket_transition`, and
  the commands for `build_parser`.
- Docs, in this sub-ticket: `README.md:1171`, replace "`factory/cli.py` `ticket_join`,
  `merge_cmd`, `archive_cmd`" with "`factory/gates.py` `ticket_join`, `merge_cmd`, `archive_cmd`";
  `README.md:9`, set the status date to the day of the change; `docs/principles.md:106-107`,
  replace "the guards in `factory/cli.py`:" and the next line's "`ticket transition`, `run start`,
  `merge`;" with "the guards in `factory/cli.py` (`ticket transition`, `run start`) and
  `factory/gates.py` (`merge`);", re-wrapped at 100 columns with "`factory/gates.py` (`merge`)" on
  one line. Read README's "Maintaining this page" section before editing it.

Acceptance:
- NEW: The gates live in factory/gates.py.
  WHEN `uv run --frozen python -B -c 'import factory.gates' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/gates.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  THEN it prints exactly `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`
- NEW: The README and the principles name gates.py for the moved gate commands.
  WHEN `echo "$(grep -c 'factory/gates.py. .ticket_join., .merge_cmd., .archive_cmd.' README.md) $(grep -c 'factory/cli.py. .ticket_join.' README.md) $(grep -c 'factory/gates.py. (.merge.)' docs/principles.md) $(grep -c 'guards in .factory/cli.py.:' docs/principles.md) $(grep -cE '^def (ticket_join|merge_cmd|archive_cmd)\(' factory/gates.py 2>/dev/null)"`
  THEN it prints exactly `1 0 1 0 3`
- REGRESSION: the parent's drift, common and setup module scenarios, with the commands and
  results given under T-0047.1 and T-0047.2.
- REGRESSION: M (its total `lines` across the three sub-tickets stays at most 100).
- REGRESSION: R1 to R19.
- Intermediate checks (NEW): WHEN `uv run --frozen python -B -c 'import factory.gates'` THEN it
  exits 0 and prints nothing. WHEN `git diff --check main...HEAD -- README.md docs/principles.md`
  THEN it prints nothing.

Interim tests: none
Tests to change: none
Protected paths: `factory/cli.py`, `factory/gates.py`
Out of scope: parts A, B, C and E; any other README or principles line that names
`factory/cli.py` (Decision 11: they stay true); the `merge_cmd` and `ready_implementers`
difference over closed siblings (filed separately); any rename; any change to a moved body; any
change under `tests/`.

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

Sub-ticket: T-0047.3 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`, part D). Branch `factory/T-0047.3`, head `c30b80f45a39824b71c7064cc22e2563a53f9438`, base `57b46e18ca48c71254487dec086b27c3d34ec79c`. Worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0047.3`.

## What changed

The gates are the harness commands that record review and verification results and refuse a merge or a ticket close that those results do not support. This change moves them out of `factory/cli.py` into a new module, `factory/gates.py`. No gate's behaviour changes. The README and the principles page now name the new module.

**Part D, the code.** These 18 definitions moved byte for byte, in the order they had in `factory/cli.py`:
- the first block, `ticket_head` through `ticket_parent_check`: `ticket_head`, `results_record`, `results_show`, `DECLARED_RE`, `_in_repo`, `declared_paths`, `undeclared_protected`, `_branch_tip`, `merge_cmd`, `REVIEWER_STATUSES`, `VERIFIER_STATUSES`, `MAX_CONFLICT_RUNS`, `ticket_join` and `ticket_parent_check`;
- the second block, `_verifier_rows` through `archive_cmd`: `_verifier_rows`, `_reused_subticket_run`, `_parent_close_verified` and `archive_cmd`.

The move was made by a script that cut both blocks between fixed anchors. It did not retype them.
- `factory/gates.py` starts with a one-line docstring and `from __future__ import annotations`. Its only imports are `re`, `Path`, `gitops`, `specstore`, `status`, `store`, `subtickets`, `out` from `factory.common` and `Refused`. It does not import `factory.cli`.
- `factory/cli.py` imports these names from `factory.gates`:
  - `_parent_close_verified`, for `ticket_transition`;
  - the seven commands, for `build_parser`;
  - `_branch_tip` and `undeclared_protected`, for `resolve`. The sub-ticket does not list these two. See Known gaps.
- No other import in `factory/cli.py` became unused. `ruff --select F` passes.
- No `# -----` section comment moved or was dropped, because each section still holds code in `factory/cli.py`.
- `factory/cli.py` went from 1,508 to 1,198 lines, and `factory/gates.py` has 321.

**Part D, the docs.**
- `README.md:9`: the status date is now 2026-10-12, the day of this change.
- `README.md:1171`: "`factory/cli.py` `ticket_join`, `merge_cmd`, `archive_cmd`" now reads "`factory/gates.py` `ticket_join`, `merge_cmd`, `archive_cmd`".
- `docs/principles.md:106-109`: the sentence now reads "…the guards in `factory/cli.py` (`ticket transition`, `run start`) and `factory/gates.py` (`merge`); …".
  - I re-wrapped only that sentence's lines, at 100 columns, so the paragraph went from 3 lines to 4. The longest line is 99 columns. "`factory/gates.py` (`merge`)" stays on one line.
  - The lines above it in the same block each begin their own sentence, so I left them as they were.

## Acceptance results

All commands ran from the worktree through the "Running code" wrapper with a fresh HOME, on head `c30b80f`. The full log is `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0489-implementer/scratch/checks.log`.

**NEW: The gates live in factory/gates.py.**
- Before: `ModuleNotFoundError: No module named 'factory.gates'`, exit 1, nothing printed.
- After: `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`. This is exactly the expected list.

**NEW: The README and the principles name gates.py for the moved gate commands.**
- Before: `0 1 0 1 ` (the last field is empty because `factory/gates.py` did not exist).
- After: `1 0 1 0 3`, as expected.

**Intermediate checks (NEW).**
- `uv run --frozen python -B -c 'import factory.gates'` exits 0 and prints nothing.
- `git diff --check main...HEAD -- README.md docs/principles.md` exits 0 and prints nothing.

**REGRESSION: the parent's module scenarios for drift, common and setup.**
- drift: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`
- common: `_add_spec_version _in_flight _integration_head _rel fence out`
- setup: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`

All three match the expected lists.

**REGRESSION M: every moved definition keeps its exact text, and the split adds at most 100 lines.** I copied the script verbatim from the parent spec's scenario block into the scratch directory rather than `/tmp`, because of the scratch-file rule.
- Before (on base): `pairs=2 added=0 removed=0 lines=35`.
- After: `pairs=3 added=0 removed=0 lines=46`, and nothing after it.
- What it shows: no definition's text changed. This sub-ticket adds 11 lines. The split has now used 46 of its 100 lines, which leaves 54 for T-0047.4.

**REGRESSION R1 to R19.** Each printed the expected value.

| Check | Output |
|---|---|
| R1 | `factory/__main__.py factory/drive.py factory/stats.py` |
| R2 | `7 True True` |
| R3 | `All checks passed!`, exit 0 |
| R4 | `576 passed in 571.88s (0:09:31)`, and no line after it |
| R5 | `0 0` |
| R6 | `0` |
| R7 | `0 2 2` |
| R8 | `0` |
| R9 | `0` |
| R10 | `0 12 1` |
| R11 | `All checks passed!`, exit 0 |
| R12 | `576 passed in 582.65s (0:09:42)`, and no line after it |
| R13 | `0` |
| R14 | `0 1` |
| R15 | `1 1` |
| R16 | `0` |
| R17 | `1 1` |
| R18 | `0 1 1 1` |
| R19 | `1 1 2` |

In R4 and R12, nothing after the pytest line means no file under `tests/` changed.

**Gate commands, exactly as written** (log: `scratch/gates.log`):
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `576 passed in 572.55s (0:09:32)`.

## Tests added/changed

None. The sub-ticket says "Interim tests: none" and "Tests to change: none".
- The behaviour this sub-ticket must keep is covered by the existing suite: 576 passed, three times.
- The acceptance commands check where the code now lives.
- No test patches a name that moved. A grep of `tests/factory` for `monkeypatch`, `mock.patch` and `setattr` found none aimed at the CLI module, and no test imports a moved name from `factory.cli`.

## Known gaps and uncertainties

- `factory/cli.py` also imports `_branch_tip` and `undeclared_protected` from `factory.gates`. The sub-ticket lists only `_parent_close_verified` and the commands.
  - These two are needed because `resolve` calls both of them. `resolve` stays in `factory/cli.py` until part E (T-0047.4) moves it to `factory/human.py`.
  - Without the two imports, `ruff` flags both names as undefined (F821), and `factory resolve --accept-paths` fails when it runs.
  - Part E's text already says `human.py` will import these same two names from `factory.gates`. After that move, T-0047.4 should drop them from `factory/cli.py`, and R11 (unused imports) will catch it if it does not.
  - I read this as the only way the sub-ticket can work, not as a change of design.
- In `factory/cli.py`, the new `from factory.gates import (...)` line is wrapped over two lines with a hanging indent. Its first line is 107 columns.
  - The other import lines in the file are single lines.
  - `ruff` here checks only F rules, so line length is not enforced.
  - Putting it on one line would save one line of the 100-line budget, but that line would be about 200 columns.

## Out-of-scope observations

- `factory/cli.py` still has the section comment `# ----- build half: sub-tickets, results, merge (parts B, D, G; local stand-in)`. After this move, that section holds only the sub-ticket and planning commands, so the words "results, merge" no longer describe it.
  - The design's rule is to move a section comment with its code, or drop it when its section is empty. This section is not empty.
  - Rewording the comment is outside this sub-ticket, so I left it.
- `docs/principles.md:106` still names `factory/cli.py` for the `ticket transition` and `run start` guards. That is still true, so Decision 11 leaves it alone.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW, REGRESSION and gate command passed on `c30b80f`, and M shows no moved definition changed its text.
ESCALATIONS: none

## Diff `57b46e18ca48c71254487dec086b27c3d34ec79c...c30b80f45a39824b71c7064cc22e2563a53f9438`

diff --git a/README.md b/README.md
index 0bf5aa0..42f3f0c 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-11. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-12. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -1168,7 +1168,7 @@ each section comes from:
 |---|---|---|
 | Roles, models | `.factory/instance.yaml` (`models`), `docs/prompts/` | read the files |
 | Terms, routing, states | `instance.yaml` (`routing`, `ready_state`); `factory/cli.py` (`ticket transition` guards) | read the files |
-| How a ticket moves | `factory/workflows/intake.js`, `build.js` (the `phase(...)` blocks and the `STATUS` routes); `factory/cli.py` `ticket_join`, `merge_cmd`, `archive_cmd` | read the code; confirm against the last closed ticket's run log in `.factory/store/log/` |
+| How a ticket moves | `factory/workflows/intake.js`, `build.js` (the `phase(...)` blocks and the `STATUS` routes); `factory/gates.py` `ticket_join`, `merge_cmd`, `archive_cmd` | read the code; confirm against the last closed ticket's run log in `.factory/store/log/` |
 | Where it runs, lock | `factory/instance.py` (`find`, `guard`), `instance.yaml` (`harness`, `state_dir`) | `~/dev/spec-factory-harness/bin/factory paths` (its `harness_revision` is the last commit touching harness code, not the runtime's HEAD); `cat .factory/harness.lock`, which must equal it |
 | Where a human decides | `factory/cli.py` `build_parser()`: the `approve-spec`, `request-changes`, `resolve`, `--accept-harness` arguments and the `decision` subparser | `~/dev/spec-factory-harness/bin/factory --help`; `… resolve --help`; `… decision add --help` (the runtime, not the dev checkout) |
 | Built / not built | `tests/factory/` (what has a test is built); `dev/issues.md` (what is named and open) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory`; `gh issue list --state open` |
diff --git a/docs/principles.md b/docs/principles.md
index 1ed1bcb..4473e7c 100644
--- a/docs/principles.md
+++ b/docs/principles.md
@@ -103,9 +103,10 @@ prompt or by the clerk.
 External test: reasoning-based guardrails fall to simple attacks (https://arxiv.org/pdf/2510.11570).
 Enforcement belongs between the decision to call a tool and the call
 (https://arxiv.org/pdf/2607.08028).
-Implemented by: the routing table (`routing` in `instance.yaml`) and the guards in `factory/cli.py`:
-`ticket transition`, `run start`, `merge`; the merge gate refuses a changed protected path the approved
-spec does not declare (#57, merged, live at the next runtime move).
+Implemented by: the routing table (`routing` in `instance.yaml`) and the guards in `factory/cli.py`
+(`ticket transition`, `run start`) and `factory/gates.py` (`merge`); the merge gate refuses a
+changed protected path the approved spec does not declare (#57, merged, live at the next runtime
+move).
 
 ### 8. Every stop is a logged state with a reason.
 
diff --git a/factory/cli.py b/factory/cli.py
index 280ca03..9eca48c 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -21,6 +21,8 @@ import yaml
 from factory import compose, gitops, instance, specstore, status, store, subtickets, tripwire
 from factory.common import _add_spec_version, _rel, fence, out
 from factory.drift import _check_drift, _check_sibling_tests
+from factory.gates import (_branch_tip, _parent_close_verified, archive_cmd, merge_cmd, results_record,
+                           results_show, ticket_head, ticket_join, ticket_parent_check, undeclared_protected)
 from factory.setup import init_cmd, paths_cmd, store_migrate
 from factory.store import Refused
 
@@ -675,240 +677,6 @@ def ticket_ready_implementers(a, root, cfg):
          "superseded": [s["id"] for s in superseded]})
 
 
-def ticket_head(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    if not t.get("branch"):
-        raise Refused(f"{t['id']} has no branch yet")
-    repo = gitops.repo_root()
-    head = gitops.rev(repo, t["branch"])
-    changed = head != t.get("head")
-    t["head"] = head
-    if t.get("merge_refused"):
-        if gitops.head_contains(repo, head, gitops.integration_branch(cfg, repo)):
-            t["merge_refused"] = None
-            t["conflict_runs"] = 0
-        else:
-            # A conflict run that did not merge the integration branch in. Counted once per
-            # implementer run (this command may be called more than once), so the loop is bounded.
-            last = [r for r, _ in store.ticket_runs(root, t["id"], "implementer", finished=True)]
-            if last and last[-1] != t.get("conflict_counted_run"):
-                t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
-                t["conflict_counted_run"] = last[-1]
-    store.save_ticket(root, t)
-    out({"ok": True, "id": t["id"], "head": head, "branch": t["branch"], "changed": changed,
-         "merge_refused": t.get("merge_refused"), "conflict_runs": int(t.get("conflict_runs") or 0)})
-
-
-def results_record(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    if a.role not in ("reviewer", "verifier"):
-        raise Refused("results record: --role reviewer|verifier")
-    if not re.fullmatch(r"[0-9a-f]{40}", a.head or ""):
-        raise Refused(f"results record: --head must be a full commit SHA, got {a.head!r}")
-    # A killed run's output is never read: the build loop passes --output even when the run wrote none.
-    text = Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""
-    if a.killed:
-        st = "KILLED"
-    else:
-        parsed = status.parse(text)
-        st = parsed["status"] or "UNKNOWN"
-    if not a.killed:  # every Commit: line must name the head; with none, the verdict is for no known commit
-        lines = re.findall(r"^Commit:.*$", text, re.M)
-        if not lines:
-            raise Refused("results record: the output has no Commit: line")
-        for line in lines:
-            cm = re.match(r"Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", line)
-            if not cm:
-                raise Refused(f"results record: Commit: {line[len('Commit:'):].strip()} is not a commit id")
-            if not a.head.startswith(cm.group(1).lower()):
-                raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
-    stale = t.get("head") is not None and a.head != t.get("head")
-    rows = [store.record_result(root, t["id"], a.head, a.role, st, a.run)]
-    if a.role == "verifier" and not a.killed:
-        # Heading and emphasis marks may wrap the line (`## Gate suite: PASS`, `**Gate suite:** PASS`);
-        # other text before `Gate suite:` is prose, not a verdict.
-        m = re.search(r"^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$", text, re.M)
-        ci = (m.group(1), m.group(2).strip(" \t\r*") or None) if m else ("FAIL", "missing Gate suite line")
-        mp = root / "runs" / str(a.run) / "meta.yaml"
-        skipped = (store.read_yaml(mp) or {}).get("gate_skipped") if a.run and mp.exists() else None
-        rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1],
-                                        {"skipped": skipped} if skipped else None))
-    ev = "result.stale-discarded" if stale else "result.recorded"
-    for r in rows:
-        store.log_event(root, ev, ticket=t["id"], head=a.head, role=r["role"], status=r["status"], run=a.run)
-    out({"ok": True, "id": t["id"], "head": a.head, "stale": stale, "rows": [{k: r[k] for k in ("role", "status")} for r in rows]})
-
-
-def results_show(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    head = t.get("head")
-    rows = store.results_for(root, head) if head else {}
-    missing = [r for r in store.RESULT_ROLES if r not in rows]
-    out({"ok": True, "id": t["id"], "head": head, "rows": {k: v["status"] for k, v in rows.items()}, "missing": missing})
-
-
-DECLARED_RE = re.compile(r"^\s*(?:[-*]\s+)?Protected paths:\s*(none|`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\.?\s*$")
-
-
-def _in_repo(globs: list[str]) -> list[str]:
-    """The patterns a repository diff can match: one starting `~` or `/` names a path outside it."""
-    return [g for g in globs if not g.startswith(("~", "/"))]
-
-
-def declared_paths(spec_text: str) -> list[str]:
-    """The entries of each `Protected paths:` line (DECLARED_RE) in the spec's `## Risk` section, in
-    order. The section runs from a line that is exactly `## Risk` to the next line starting `## ` or
-    `=== `; a line inside a fenced code block neither starts nor ends it and declares nothing."""
-    entries, in_risk = [], False
-    for line, in_fence in specstore.lines_outside_fences(spec_text):
-        if in_fence:
-            continue
-        if line.startswith(("## ", "=== ")):
-            in_risk = line.rstrip() == "## Risk"
-        elif in_risk and (m := DECLARED_RE.match(line)) and m.group(1) != "none":
-            entries += re.findall(r"`([^`]+)`", m.group(1))
-    return _in_repo(entries)
-
-
-def undeclared_protected(root: Path, cfg: dict, t: dict, head: str) -> tuple[list[str], str]:
-    """(the changed protected paths of `t` at `head` that the pinned spec does not declare, sorted;
-    where the declarations were read, for the refusal). Changed is `integration...head`. The pinned
-    spec is the parent's approved version, or the ticket's own when it has no parent; a path in the
-    ticket's `accepted_paths` counts as declared (`resolve --accept-paths`)."""
-    sid = t.get("parent") or t["id"]
-    av = (store.load_ticket(root, sid) if sid != t["id"] else t)["spec"]["approved_version"]
-    where = f"in {sid} spec v{av}" if av is not None else f"({sid} has no approved spec)"
-    patterns = [g for globs in (cfg.get("protected_paths") or {}).values()
-                for g in ([globs] if isinstance(globs, str) else list(globs or []))]
-    repo = gitops.repo_root()
-    integ = gitops.integration_branch(cfg, repo)
-    changed = gitops.changed_files(repo, integ, head, _in_repo(patterns))
-    if not changed:
-        return [], where
-    spec = root / "specs" / sid / f"v{av}.md"
-    declared = declared_paths(spec.read_text(encoding="utf-8")) if av is not None and spec.exists() else []
-    ok = set(gitops.changed_files(repo, integ, head, declared)) | set(t.get("accepted_paths") or [])
-    return sorted(p for p in changed if p not in ok), where
-
-
-def _branch_tip(repo: Path, t: dict) -> str:
-    """The ticket's head, refused unless it is the tip of its branch."""
-    head = t.get("head")
-    if not head or gitops.rev(repo, t["branch"]) != head:
-        raise Refused(f"{t['id']} head {head} is not the branch tip; run ticket head")
-    return head
-
-
-def merge_cmd(a, root, cfg):
-    """Rule-4 checks (part G) in the local stand-in: ci PASS + APPROVE + VERIFIED on the current
-    head, every changed protected path declared by the pinned spec (piece 8), head contains the
-    integration branch; then a local --no-ff merge. Exit 2 names the first failing condition;
-    'BLOCKED from merge gate' parks for a human; 'head does not contain main' is the conflict-run
-    signal."""
-    t = store.load_ticket(root, a.id)
-    if t["status"] not in ("ready-for-merge", "checks-in-flight"):
-        raise Refused(f"{t['id']} is {t['status']}, not ready-for-merge")
-    repo = gitops.repo_root()
-    integ = gitops.integration_branch(cfg, repo)
-    head = _branch_tip(repo, t)
-    rows = store.results_for(root, head)
-    for role, want in (("ci", "PASS"), ("reviewer", "APPROVE"), ("verifier", "VERIFIED")):
-        got = (rows.get(role) or {}).get("status")
-        if got != want:
-            raise Refused(f"{role} is {got or 'missing'} for {head[:9]}, need {want}")
-    undeclared, where = undeclared_protected(root, cfg, t, head)
-    if undeclared:
-        store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="protected paths not declared",
-                        paths=undeclared)
-        raise Refused(f"BLOCKED from merge gate: protected paths not declared {where}: {', '.join(undeclared)}")
-    with gitops.MergeLock(repo):
-        if not gitops.head_contains(repo, head, integ):
-            t["merge_refused"] = "head does not contain main"
-            t["conflict_runs"] = 0  # unfixed conflict runs since this refusal
-            store.save_ticket(root, t)
-            store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="head does not contain main")
-            raise Refused(f"head does not contain main ({integ} moved; merge it into {t['branch']} and re-check)")
-        before, after = gitops.merge_no_ff(repo, head, integ, f"Merge {t['branch']}: {t['title']} ({t['id']})")
-    t.update({"status": "merged", "merge": {"base_before": before, "main_after": after}, "merge_refused": None})
-    t["history"].append({"ts": store.now(), "from": "ready-for-merge", "to": "merged", "by": "merge", "head": head})
-    store.save_ticket(root, t)
-    store.log_event(root, "merge.done", ticket=t["id"], head=head, base_before=before, main_after=after)
-    released = []
-    if t.get("parent"):
-        parent = store.load_ticket(root, t["parent"])
-        if parent.get("parent_base") is None:
-            parent["parent_base"] = before
-            store.save_ticket(root, parent)
-        for s in store.subtickets_of(root, t["parent"]):
-            if s["status"] == "waiting-dependencies" and all(
-                    store.load_ticket(root, dep)["status"] in subtickets.SATISFIED for dep in s["depends_on"]):
-                store.record_transition(root, s, "ready-for-implementer", "merge")
-                released.append(s["id"])
-    gitops.remove_worktree(repo, root / "worktrees" / t["id"])
-    out({"ok": True, "id": t["id"], "state": "merged", "base_before": before, "main_after": after, "released": released})
-
-
-REVIEWER_STATUSES = ("APPROVE", "REQUEST-CHANGES", "ESCALATE", "KILLED")
-VERIFIER_STATUSES = ("VERIFIED", "FAILED", "SPEC-DEFECT", "KILLED")
-MAX_CONFLICT_RUNS = 2
-
-
-def ticket_join(a, root, cfg):
-    """The PR-loop join as a decision, read from the results table for the current head. The
-    dispatcher and the tests both ask here, so the routing lives in one place:
-    merge | revise (round +1) | conflict (same round) | wait | park, each with its reason."""
-    t = store.load_ticket(root, a.id)
-    head = t.get("head")
-    rows = store.results_for(root, head) if head else {}
-    st = {r: (rows.get(r) or {}).get("status") for r in store.RESULT_ROLES}
-    rnd, mx = t["round"]["pr"], cfg["max_rounds"]["pr"]
-
-    def decide(decision: str, reason: str, **extra):
-        out({"ok": True, "id": t["id"], "head": head, "rows": st, "round": rnd, "decision": decision, "reason": reason, **extra})
-
-    if t.get("merge_refused"):
-        if int(t.get("conflict_runs") or 0) >= MAX_CONFLICT_RUNS:
-            return decide("park", f"conflict: head still does not contain main after {MAX_CONFLICT_RUNS} conflict runs")
-        return decide("conflict", "head does not contain main: the implementer merges the integration branch into its branch, same round")
-    missing = [r for r in ("reviewer", "verifier", "ci") if st[r] is None]
-    if st["verifier"] == "KILLED" and st["ci"] is None:
-        missing.remove("ci")  # a killed verifier writes no ci row
-    if missing:
-        return decide("wait", f"results missing for the current head: {', '.join(missing)}", missing=missing)
-    for role, known in (("reviewer", REVIEWER_STATUSES), ("verifier", VERIFIER_STATUSES)):
-        if st[role] not in known:
-            return decide("park", f"harness-bug: unknown STATUS {st[role]} from {role}")
-    killed = [r for r in ("reviewer", "verifier") if st[r] == "KILLED"]
-    if killed:
-        return decide("park", f"budget kill: {', '.join(killed)}")
-    if st["reviewer"] == "ESCALATE":
-        return decide("park", "ESCALATE from reviewer")
-    if st["verifier"] == "SPEC-DEFECT":
-        return decide("park", "SPEC-DEFECT from verifier")
-    if st == {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}:
-        return decide("merge", "ci PASS + APPROVE + VERIFIED on the current head")
-    red = ", ".join(f"{r} {v}" for r, v in st.items() if v not in ("APPROVE", "VERIFIED", "PASS"))
-    if rnd < mx:
-        return decide("revise", f"{red}; implementer round {rnd + 1}", round_op="pr:+1")
-    return decide("park", f"max-round cutoff ({red} at round {rnd})")
-
-
-def ticket_parent_check(a, root, cfg):
-    """When every sub-ticket of the current plan is merged, the parent moves to ready-for-parent-verify
-    (part G); sub-tickets a later plan superseded do not count."""
-    parent = store.load_ticket(root, a.id)
-    every = store.subtickets_of(root, parent["id"])
-    if not every:
-        raise Refused(f"{parent['id']} has no sub-tickets")
-    subs, superseded = subtickets.split_plan(every)
-    if all(s["status"] == "merged" for s in subs) and parent["status"] == "planned":
-        store.record_transition(root, parent, "ready-for-parent-verify", "parent-check")
-    reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
-    out({"ok": True, "id": parent["id"], "state": parent["status"],
-         "subtickets": {s["id"]: s["status"] for s in subs}, "superseded": [s["id"] for s in superseded],
-         "reuse": reuse})
-
-
 # ----- human surface (K-lite) -----------------------------------------------------
 
 def _by() -> str:
@@ -1178,84 +946,6 @@ def spec_tasks(a, root, cfg):
     out({"ok": True, "id": t["id"], "path": _rel(root, dest)})
 
 
-def _verifier_rows(root: Path, tid: str) -> list[str]:
-    """`<head> · <ticket> · <STATUS> · <run_id>` per verifier row in results/ for the parent and
-    its sub-tickets, oldest first. results/ is a later build item; absent → no rows."""
-    res = root / "results"
-    rows = []
-    if res.exists():
-        for p in sorted(res.rglob("*.yaml")):
-            r = store.read_yaml(p) or {}
-            if str(r.get("ticket", "")).split(".")[0] == tid and r.get("role") == "verifier":
-                rows.append(f"{r.get('head')} · {r.get('ticket')} · {r.get('status')} · {r.get('run_id')}")
-    return rows
-
-
-def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
-    """The run id of a sub-ticket's VERIFIED verifier run that stands for the parent-close run
-    (design doc routing table, Merge gate row), or None when the parent needs its own run."""
-    # factory: one sub-ticket only, and scenario coverage is read from scenario names occurring in
-    # the sub-ticket's text; widen only when the store can check a coverage map per sub-ticket.
-    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
-    if len(subs) != 1 or not t.get("parent_base"):
-        return None
-    s = subs[0]
-    after = (s.get("merge") or {}).get("main_after")
-    if s["status"] != "merged" or not after or not s.get("head"):
-        return None
-    repo = gitops.repo_root()
-    if gitops.integration_tip(cfg, repo) != after:
-        return None
-    row = store.results_for(root, s["head"]).get("verifier") or {}
-    rid = row.get("run_id")
-    mp = root / "runs" / str(rid) / "meta.yaml"
-    if row.get("status") != "VERIFIED" or not rid or not mp.exists():
-        return None
-    m = store.read_yaml(mp) or {}
-    if m.get("status") != "VERIFIED" or m.get("head") != s["head"] or m.get("base") != t["parent_base"]:
-        return None
-    spec = root / "specs" / t["id"] / f"v{t['spec'].get('approved_version')}.md"
-    sub = root / "specs" / s["id"] / "subticket.md"
-    if not spec.exists() or not sub.exists():
-        return None
-    names = specstore.scenario_names(spec.read_text(encoding="utf-8"))
-    text = sub.read_text(encoding="utf-8")
-    return rid if names and all(n in text for n in names) else None
-
-
-def _parent_close_verified(root: Path, cfg: dict, t: dict) -> str | None:
-    """The run that verifies the parent: every current sub-ticket merged (a superseded one does not
-    count), and a finished verifier run on the parent itself said VERIFIED on a head that contains
-    every one of those merges (a run from before the last merge does not count); else a
-    sub-ticket's run that stands for it; else None."""
-    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
-    if any(s["status"] != "merged" for s in subs):
-        return None
-    repo = gitops.repo_root()
-    for rid, m in store.ticket_runs(root, t["id"], "verifier"):
-        if m.get("status") != "VERIFIED" or not m.get("head"):
-            continue
-        if all(gitops.head_contains(repo, m["head"], s["merge"]["main_after"]) for s in subs if s["merge"].get("main_after")):
-            return rid
-    return _reused_subticket_run(root, cfg, t)
-
-
-def archive_cmd(a, root, cfg):
-    t = store.load_ticket(root, a.id)
-    if not specstore.is_active(root):
-        raise Refused("no spec store (factory init not run)")
-    if not specstore.change_dir(root, t["id"]).exists():
-        raise Refused(f"{t['id']} has no change folder to archive")
-    errors = specstore.applies(root, specstore.delta_ops_of_change(root, t["id"]))
-    if errors:
-        raise Refused("archive does not apply: " + "; ".join(errors))
-    if store.subtickets_of(root, t["id"]) and not _parent_close_verified(root, cfg, t):
-        raise Refused(f"{t['id']} has sub-tickets but no VERIFIED parent-close verifier run on the integration branch")
-    res = specstore.archive(root, t["id"], _verifier_rows(root, t["id"]))
-    store.log_event(root, "change.archived", ticket=t["id"], **res)
-    out({"ok": True, "id": t["id"], **res})
-
-
 # ----- misc ---------------------------------------------------------------------
 
 def config_cmd(a, root, cfg):
diff --git a/factory/gates.py b/factory/gates.py
new file mode 100644
index 0000000..ab9fd3a
--- /dev/null
+++ b/factory/gates.py
@@ -0,0 +1,321 @@
+"""Gates: review and verification results, the merge gate, join, the parent check and archive."""
+from __future__ import annotations
+
+import re
+from pathlib import Path
+
+from factory import gitops, specstore, status, store, subtickets
+from factory.common import out
+from factory.store import Refused
+
+
+def ticket_head(a, root, cfg):
+    t = store.load_ticket(root, a.id)
+    if not t.get("branch"):
+        raise Refused(f"{t['id']} has no branch yet")
+    repo = gitops.repo_root()
+    head = gitops.rev(repo, t["branch"])
+    changed = head != t.get("head")
+    t["head"] = head
+    if t.get("merge_refused"):
+        if gitops.head_contains(repo, head, gitops.integration_branch(cfg, repo)):
+            t["merge_refused"] = None
+            t["conflict_runs"] = 0
+        else:
+            # A conflict run that did not merge the integration branch in. Counted once per
+            # implementer run (this command may be called more than once), so the loop is bounded.
+            last = [r for r, _ in store.ticket_runs(root, t["id"], "implementer", finished=True)]
+            if last and last[-1] != t.get("conflict_counted_run"):
+                t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
+                t["conflict_counted_run"] = last[-1]
+    store.save_ticket(root, t)
+    out({"ok": True, "id": t["id"], "head": head, "branch": t["branch"], "changed": changed,
+         "merge_refused": t.get("merge_refused"), "conflict_runs": int(t.get("conflict_runs") or 0)})
+
+
+def results_record(a, root, cfg):
+    t = store.load_ticket(root, a.id)
+    if a.role not in ("reviewer", "verifier"):
+        raise Refused("results record: --role reviewer|verifier")
+    if not re.fullmatch(r"[0-9a-f]{40}", a.head or ""):
+        raise Refused(f"results record: --head must be a full commit SHA, got {a.head!r}")
+    # A killed run's output is never read: the build loop passes --output even when the run wrote none.
+    text = Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""
+    if a.killed:
+        st = "KILLED"
+    else:
+        parsed = status.parse(text)
+        st = parsed["status"] or "UNKNOWN"
+    if not a.killed:  # every Commit: line must name the head; with none, the verdict is for no known commit
+        lines = re.findall(r"^Commit:.*$", text, re.M)
+        if not lines:
+            raise Refused("results record: the output has no Commit: line")
+        for line in lines:
+            cm = re.match(r"Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", line)
+            if not cm:
+                raise Refused(f"results record: Commit: {line[len('Commit:'):].strip()} is not a commit id")
+            if not a.head.startswith(cm.group(1).lower()):
+                raise Refused(f"results record: the output says Commit: {cm.group(1)}, not the head {a.head[:12]}")
+    stale = t.get("head") is not None and a.head != t.get("head")
+    rows = [store.record_result(root, t["id"], a.head, a.role, st, a.run)]
+    if a.role == "verifier" and not a.killed:
+        # Heading and emphasis marks may wrap the line (`## Gate suite: PASS`, `**Gate suite:** PASS`);
+        # other text before `Gate suite:` is prose, not a verdict.
+        m = re.search(r"^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$", text, re.M)
+        ci = (m.group(1), m.group(2).strip(" \t\r*") or None) if m else ("FAIL", "missing Gate suite line")
+        mp = root / "runs" / str(a.run) / "meta.yaml"
+        skipped = (store.read_yaml(mp) or {}).get("gate_skipped") if a.run and mp.exists() else None
+        rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1],
+                                        {"skipped": skipped} if skipped else None))
+    ev = "result.stale-discarded" if stale else "result.recorded"
+    for r in rows:
+        store.log_event(root, ev, ticket=t["id"], head=a.head, role=r["role"], status=r["status"], run=a.run)
+    out({"ok": True, "id": t["id"], "head": a.head, "stale": stale, "rows": [{k: r[k] for k in ("role", "status")} for r in rows]})
+
+
+def results_show(a, root, cfg):
+    t = store.load_ticket(root, a.id)
+    head = t.get("head")
+    rows = store.results_for(root, head) if head else {}
+    missing = [r for r in store.RESULT_ROLES if r not in rows]
+    out({"ok": True, "id": t["id"], "head": head, "rows": {k: v["status"] for k, v in rows.items()}, "missing": missing})
+
+
+DECLARED_RE = re.compile(r"^\s*(?:[-*]\s+)?Protected paths:\s*(none|`[^`]+`(?:\s*,\s*`[^`]+`)*)\s*\.?\s*$")
+
+
+def _in_repo(globs: list[str]) -> list[str]:
+    """The patterns a repository diff can match: one starting `~` or `/` names a path outside it."""
+    return [g for g in globs if not g.startswith(("~", "/"))]
+
+
+def declared_paths(spec_text: str) -> list[str]:
+    """The entries of each `Protected paths:` line (DECLARED_RE) in the spec's `## Risk` section, in
+    order. The section runs from a line that is exactly `## Risk` to the next line starting `## ` or
+    `=== `; a line inside a fenced code block neither starts nor ends it and declares nothing."""
+    entries, in_risk = [], False
+    for line, in_fence in specstore.lines_outside_fences(spec_text):
+        if in_fence:
+            continue
+        if line.startswith(("## ", "=== ")):
+            in_risk = line.rstrip() == "## Risk"
+        elif in_risk and (m := DECLARED_RE.match(line)) and m.group(1) != "none":
+            entries += re.findall(r"`([^`]+)`", m.group(1))
+    return _in_repo(entries)
+
+
+def undeclared_protected(root: Path, cfg: dict, t: dict, head: str) -> tuple[list[str], str]:
+    """(the changed protected paths of `t` at `head` that the pinned spec does not declare, sorted;
+    where the declarations were read, for the refusal). Changed is `integration...head`. The pinned
+    spec is the parent's approved version, or the ticket's own when it has no parent; a path in the
+    ticket's `accepted_paths` counts as declared (`resolve --accept-paths`)."""
+    sid = t.get("parent") or t["id"]
+    av = (store.load_ticket(root, sid) if sid != t["id"] else t)["spec"]["approved_version"]
+    where = f"in {sid} spec v{av}" if av is not None else f"({sid} has no approved spec)"
+    patterns = [g for globs in (cfg.get("protected_paths") or {}).values()
+                for g in ([globs] if isinstance(globs, str) else list(globs or []))]
+    repo = gitops.repo_root()
+    integ = gitops.integration_branch(cfg, repo)
+    changed = gitops.changed_files(repo, integ, head, _in_repo(patterns))
+    if not changed:
+        return [], where
+    spec = root / "specs" / sid / f"v{av}.md"
+    declared = declared_paths(spec.read_text(encoding="utf-8")) if av is not None and spec.exists() else []
+    ok = set(gitops.changed_files(repo, integ, head, declared)) | set(t.get("accepted_paths") or [])
+    return sorted(p for p in changed if p not in ok), where
+
+
+def _branch_tip(repo: Path, t: dict) -> str:
+    """The ticket's head, refused unless it is the tip of its branch."""
+    head = t.get("head")
+    if not head or gitops.rev(repo, t["branch"]) != head:
+        raise Refused(f"{t['id']} head {head} is not the branch tip; run ticket head")
+    return head
+
+
+def merge_cmd(a, root, cfg):
+    """Rule-4 checks (part G) in the local stand-in: ci PASS + APPROVE + VERIFIED on the current
+    head, every changed protected path declared by the pinned spec (piece 8), head contains the
+    integration branch; then a local --no-ff merge. Exit 2 names the first failing condition;
+    'BLOCKED from merge gate' parks for a human; 'head does not contain main' is the conflict-run
+    signal."""
+    t = store.load_ticket(root, a.id)
+    if t["status"] not in ("ready-for-merge", "checks-in-flight"):
+        raise Refused(f"{t['id']} is {t['status']}, not ready-for-merge")
+    repo = gitops.repo_root()
+    integ = gitops.integration_branch(cfg, repo)
+    head = _branch_tip(repo, t)
+    rows = store.results_for(root, head)
+    for role, want in (("ci", "PASS"), ("reviewer", "APPROVE"), ("verifier", "VERIFIED")):
+        got = (rows.get(role) or {}).get("status")
+        if got != want:
+            raise Refused(f"{role} is {got or 'missing'} for {head[:9]}, need {want}")
+    undeclared, where = undeclared_protected(root, cfg, t, head)
+    if undeclared:
+        store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="protected paths not declared",
+                        paths=undeclared)
+        raise Refused(f"BLOCKED from merge gate: protected paths not declared {where}: {', '.join(undeclared)}")
+    with gitops.MergeLock(repo):
+        if not gitops.head_contains(repo, head, integ):
+            t["merge_refused"] = "head does not contain main"
+            t["conflict_runs"] = 0  # unfixed conflict runs since this refusal
+            store.save_ticket(root, t)
+            store.log_event(root, "merge.refused", ticket=t["id"], head=head, reason="head does not contain main")
+            raise Refused(f"head does not contain main ({integ} moved; merge it into {t['branch']} and re-check)")
+        before, after = gitops.merge_no_ff(repo, head, integ, f"Merge {t['branch']}: {t['title']} ({t['id']})")
+    t.update({"status": "merged", "merge": {"base_before": before, "main_after": after}, "merge_refused": None})
+    t["history"].append({"ts": store.now(), "from": "ready-for-merge", "to": "merged", "by": "merge", "head": head})
+    store.save_ticket(root, t)
+    store.log_event(root, "merge.done", ticket=t["id"], head=head, base_before=before, main_after=after)
+    released = []
+    if t.get("parent"):
+        parent = store.load_ticket(root, t["parent"])
+        if parent.get("parent_base") is None:
+            parent["parent_base"] = before
+            store.save_ticket(root, parent)
+        for s in store.subtickets_of(root, t["parent"]):
+            if s["status"] == "waiting-dependencies" and all(
+                    store.load_ticket(root, dep)["status"] in subtickets.SATISFIED for dep in s["depends_on"]):
+                store.record_transition(root, s, "ready-for-implementer", "merge")
+                released.append(s["id"])
+    gitops.remove_worktree(repo, root / "worktrees" / t["id"])
+    out({"ok": True, "id": t["id"], "state": "merged", "base_before": before, "main_after": after, "released": released})
+
+
+REVIEWER_STATUSES = ("APPROVE", "REQUEST-CHANGES", "ESCALATE", "KILLED")
+VERIFIER_STATUSES = ("VERIFIED", "FAILED", "SPEC-DEFECT", "KILLED")
+MAX_CONFLICT_RUNS = 2
+
+
+def ticket_join(a, root, cfg):
+    """The PR-loop join as a decision, read from the results table for the current head. The
+    dispatcher and the tests both ask here, so the routing lives in one place:
+    merge | revise (round +1) | conflict (same round) | wait | park, each with its reason."""
+    t = store.load_ticket(root, a.id)
+    head = t.get("head")
+    rows = store.results_for(root, head) if head else {}
+    st = {r: (rows.get(r) or {}).get("status") for r in store.RESULT_ROLES}
+    rnd, mx = t["round"]["pr"], cfg["max_rounds"]["pr"]
+
+    def decide(decision: str, reason: str, **extra):
+        out({"ok": True, "id": t["id"], "head": head, "rows": st, "round": rnd, "decision": decision, "reason": reason, **extra})
+
+    if t.get("merge_refused"):
+        if int(t.get("conflict_runs") or 0) >= MAX_CONFLICT_RUNS:
+            return decide("park", f"conflict: head still does not contain main after {MAX_CONFLICT_RUNS} conflict runs")
+        return decide("conflict", "head does not contain main: the implementer merges the integration branch into its branch, same round")
+    missing = [r for r in ("reviewer", "verifier", "ci") if st[r] is None]
+    if st["verifier"] == "KILLED" and st["ci"] is None:
+        missing.remove("ci")  # a killed verifier writes no ci row
+    if missing:
+        return decide("wait", f"results missing for the current head: {', '.join(missing)}", missing=missing)
+    for role, known in (("reviewer", REVIEWER_STATUSES), ("verifier", VERIFIER_STATUSES)):
+        if st[role] not in known:
+            return decide("park", f"harness-bug: unknown STATUS {st[role]} from {role}")
+    killed = [r for r in ("reviewer", "verifier") if st[r] == "KILLED"]
+    if killed:
+        return decide("park", f"budget kill: {', '.join(killed)}")
+    if st["reviewer"] == "ESCALATE":
+        return decide("park", "ESCALATE from reviewer")
+    if st["verifier"] == "SPEC-DEFECT":
+        return decide("park", "SPEC-DEFECT from verifier")
+    if st == {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}:
+        return decide("merge", "ci PASS + APPROVE + VERIFIED on the current head")
+    red = ", ".join(f"{r} {v}" for r, v in st.items() if v not in ("APPROVE", "VERIFIED", "PASS"))
+    if rnd < mx:
+        return decide("revise", f"{red}; implementer round {rnd + 1}", round_op="pr:+1")
+    return decide("park", f"max-round cutoff ({red} at round {rnd})")
+
+
+def ticket_parent_check(a, root, cfg):
+    """When every sub-ticket of the current plan is merged, the parent moves to ready-for-parent-verify
+    (part G); sub-tickets a later plan superseded do not count."""
+    parent = store.load_ticket(root, a.id)
+    every = store.subtickets_of(root, parent["id"])
+    if not every:
+        raise Refused(f"{parent['id']} has no sub-tickets")
+    subs, superseded = subtickets.split_plan(every)
+    if all(s["status"] == "merged" for s in subs) and parent["status"] == "planned":
+        store.record_transition(root, parent, "ready-for-parent-verify", "parent-check")
+    reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
+    out({"ok": True, "id": parent["id"], "state": parent["status"],
+         "subtickets": {s["id"]: s["status"] for s in subs}, "superseded": [s["id"] for s in superseded],
+         "reuse": reuse})
+
+
+def _verifier_rows(root: Path, tid: str) -> list[str]:
+    """`<head> · <ticket> · <STATUS> · <run_id>` per verifier row in results/ for the parent and
+    its sub-tickets, oldest first. results/ is a later build item; absent → no rows."""
+    res = root / "results"
+    rows = []
+    if res.exists():
+        for p in sorted(res.rglob("*.yaml")):
+            r = store.read_yaml(p) or {}
+            if str(r.get("ticket", "")).split(".")[0] == tid and r.get("role") == "verifier":
+                rows.append(f"{r.get('head')} · {r.get('ticket')} · {r.get('status')} · {r.get('run_id')}")
+    return rows
+
+
+def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
+    """The run id of a sub-ticket's VERIFIED verifier run that stands for the parent-close run
+    (design doc routing table, Merge gate row), or None when the parent needs its own run."""
+    # factory: one sub-ticket only, and scenario coverage is read from scenario names occurring in
+    # the sub-ticket's text; widen only when the store can check a coverage map per sub-ticket.
+    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
+    if len(subs) != 1 or not t.get("parent_base"):
+        return None
+    s = subs[0]
+    after = (s.get("merge") or {}).get("main_after")
+    if s["status"] != "merged" or not after or not s.get("head"):
+        return None
+    repo = gitops.repo_root()
+    if gitops.integration_tip(cfg, repo) != after:
+        return None
+    row = store.results_for(root, s["head"]).get("verifier") or {}
+    rid = row.get("run_id")
+    mp = root / "runs" / str(rid) / "meta.yaml"
+    if row.get("status") != "VERIFIED" or not rid or not mp.exists():
+        return None
+    m = store.read_yaml(mp) or {}
+    if m.get("status") != "VERIFIED" or m.get("head") != s["head"] or m.get("base") != t["parent_base"]:
+        return None
+    spec = root / "specs" / t["id"] / f"v{t['spec'].get('approved_version')}.md"
+    sub = root / "specs" / s["id"] / "subticket.md"
+    if not spec.exists() or not sub.exists():
+        return None
+    names = specstore.scenario_names(spec.read_text(encoding="utf-8"))
+    text = sub.read_text(encoding="utf-8")
+    return rid if names and all(n in text for n in names) else None
+
+
+def _parent_close_verified(root: Path, cfg: dict, t: dict) -> str | None:
+    """The run that verifies the parent: every current sub-ticket merged (a superseded one does not
+    count), and a finished verifier run on the parent itself said VERIFIED on a head that contains
+    every one of those merges (a run from before the last merge does not count); else a
+    sub-ticket's run that stands for it; else None."""
+    subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
+    if any(s["status"] != "merged" for s in subs):
+        return None
+    repo = gitops.repo_root()
+    for rid, m in store.ticket_runs(root, t["id"], "verifier"):
+        if m.get("status") != "VERIFIED" or not m.get("head"):
+            continue
+        if all(gitops.head_contains(repo, m["head"], s["merge"]["main_after"]) for s in subs if s["merge"].get("main_after")):
+            return rid
+    return _reused_subticket_run(root, cfg, t)
+
+
+def archive_cmd(a, root, cfg):
+    t = store.load_ticket(root, a.id)
+    if not specstore.is_active(root):
+        raise Refused("no spec store (factory init not run)")
+    if not specstore.change_dir(root, t["id"]).exists():
+        raise Refused(f"{t['id']} has no change folder to archive")
+    errors = specstore.applies(root, specstore.delta_ops_of_change(root, t["id"]))
+    if errors:
+        raise Refused("archive does not apply: " + "; ".join(errors))
+    if store.subtickets_of(root, t["id"]) and not _parent_close_verified(root, cfg, t):
+        raise Refused(f"{t['id']} has sub-tickets but no VERIFIED parent-close verifier run on the integration branch")
+    res = specstore.archive(root, t["id"], _verifier_rows(root, t["id"]))
+    store.log_event(root, "change.archived", ticket=t["id"], **res)
+    out({"ok": True, "id": t["id"], **res})
