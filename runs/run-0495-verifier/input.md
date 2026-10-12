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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0495-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0495-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0495-verifier/wt` (branch `None`, base `62030967710765e996fb3d752386f9ce8dec6abc`, head `122e949a9d865f40c3db3104b4908e29e67b5021`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Parent spec (v2, pinned): verify every scenario on main. Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`

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
