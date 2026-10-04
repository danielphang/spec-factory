## Proposed change

### Size and seams (NEEDS-SPLIT)

About 665 changed lines in all, roughly half of them new tests. That is over one reviewable PR. The parts are lettered A to G, then I and J. There is no part H, so that a step id such as I1 never reads as one of the requester's items H1 to H9. The planner may build one sub-ticket per lettered part. The suggested grouping is four seams, each holding whole items that touch the same code:

| Seam | Parts (items) | About | Scenarios |
|---|---|---|---|
| S1, resolve verbs and re-plan | A (H1), I (H9), J1-J2 | 235 lines | every `human-resolution` scenario except the two redispatch ones; both `sub-ticket-planning` scenarios; "The README describes the new resolve verbs" |
| S2, dispatcher and redispatch | B (H2), D (H4), J1 | 170 lines | every `build-dispatch` scenario; "A redispatch after a killed reviewer keeps the verifier's passing rows"; "A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval" |
| S3, store and instance setup | C (H3), E (H6), F (H7), J1, J3 | 190 lines | every `store-setup` scenario; "The README says relative paths resolve from the caller's directory" |
| S4, suite on an edited checkout | G (H8), J1 | 60 lines | both `harness-suite` scenarios |

Every seam adds its clause to changelog entry 51 and runs "The change adds no whitespace errors". "The changelog records the change in order" passes only once all four clauses are in, so it is NEW for the last seam to merge. Every seam edits `docs/changelog.md`, and S1, S2 and S3 all edit `factory/cli.py`, so no seam is parallel-safe. None depends on another's code.

**A. `--ruling` accepts a BLOCKED park** (H1; `factory/cli.py` `resolve`)
- A1. In the `--ruling` branch, accept a parked ticket whose reason starts with `ESCALATE` or `BLOCKED`. For `BLOCKED` the target is `ready-for-implementer`. `ESCALATE` keeps today's targets. Keep the `use --answer` refusal for NEEDS-HUMAN and CLARIFY parks. The other refusal becomes `--ruling applies to an ESCALATE or BLOCKED park; <id> is <state> (<reason>)`.
- A2. Nothing else changes. The ruling is copied to the next `approvals/<id>/ruling-<n>.md`, the round is not touched, and compose already hands the ruling to the implementer.
- A3. New test file `tests/factory/test_resolve_rulings.py`, driven through `bin/factory` on scratch stores. It covers the BLOCKED ruling's state, unchanged round, ruling file and implementer input, and the ESCALATE routes as before.

**B. A park reason always carries the error** (H2; `factory/workflows/build.js` and `factory/workflows/intake.js`, `clerk()` only)
- B1. In the no-JSON branch, `stderr` becomes `res.stderr || \`exit ${res.exit}, no JSON on stdout\``.
- B2. After the existing line that copies `res.stderr`, add: when `parsed.ok === false` and `parsed.stderr` is empty, set `parsed.stderr` to `parsed.error`, else `` `exit ${res.exit}, no error text` ``.
- B3. Leave every reason template (`<prefix>: ${x.stderr || ''}`) as it is. With B1 and B2 none of them can end blank. A refused archive now parks as `archive: no spec store (factory init not run)`.

**C. Run records are exempt from whitespace checks** (H3; `factory/store.py` and `factory/cli.py`)
- C1. Add `STORE_GITATTRIBUTES`: a comment line saying run records embed verbatim diffs and outputs whose whitespace is not the store's to fix, then the line `runs/** -whitespace`. Add `ensure_gitattributes(root)` with the same semantics as `ensure_gitignore`. An absent or empty file gets the block. An existing file keeps its own lines and gains only the non-comment lines it lacks.
- C2. Call it from `init_cmd`, beside `ensure_gitignore`. Put `.gitattributes` first in `written` when it was absent, as `.gitignore` already is. Also call it from `run_start`, beside `ensure_gitignore` (line 222), which runs after every refusal of `run start`.
- C3. New test file `tests/factory/test_store_setup.py`, shared with parts E and F. It covers: the file written by `init` and by `run start`; existing lines kept and nothing duplicated; and `git diff --check` exempting a committed `runs/` record but not another store file.

**D. A redispatch keeps rows that passed** (H4; `factory/cli.py` `resolve`, `factory/workflows/build.js` `buildOne`)
- D1. In the `--redispatch` branch, set aside `reviewer.yaml` unless its status is `APPROVE`. Set aside `verifier.yaml` and `ci.yaml` together unless the verifier is `VERIFIED` and ci is `PASS`. Keep the `superseded-<n>/` naming. Create the directory only when something moves. Log `results.superseded` with the roles moved. Update the comment above the branch.
- D2. In `buildOne`, record whether the implementer ran in this pass of the loop. When it did, run both checkers, as today. When the loop entered at `checks-in-flight` (a redispatch or a resumed sub-ticket), first run `results show ST` through the clerk. Run the reviewer when `missing` contains `reviewer`. Run the verifier when `missing` contains `verifier` or `ci`. A refused `results show` parks with `harness-bug: results show: <error>`. With no checker to run, go straight to `ticket join`.
- D3. New test file `tests/factory/test_redispatch_rows.py`. It covers a KILLED reviewer with a passing verifier, a SPEC-DEFECT verifier with an approving reviewer, all rows passing (nothing moved, no directory created) and no rows at all.

**E. No half instance; a missing briefing refuses** (H6; `factory/cli.py` `init_cmd`, `factory/compose.py` `compose`)
- E1. In `init_cmd`, when `instance.yaml` does not exist, build its text, load it in memory and compute the store in use from it. If that is not the instance's own store, refuse with exit 2 before writing anything: `factory init: <instance> has no instance.yaml, and FACTORY_STATE names another store (<store>); create the instance with FACTORY_STATE unset, then init that store`. Update the docstring.
- E2. In `compose`, before reading the briefing, refuse with `store.Refused` when `<instance>/context.md` is not a file: `<path> is missing: it is the role-context block every role reads first; run factory init with FACTORY_STATE unset to create it from the template`. No `input.md` is written.
- E3. Tests in `tests/factory/test_store_setup.py`.

**F. Relative environment paths resolve from the caller's directory** (H7; `factory/instance.py`, `factory/store.py`, `factory/cli.py`)
- F1. Add `instance.env_path(name) -> Path | None`. It returns None when the variable is unset or empty. Otherwise it applies `expanduser()`, joins a still-relative path onto `caller_cwd()`, and returns `.resolve()`.
- F2. Use it for `FACTORY_INSTANCE` in `find` and `init_cmd`, for `FACTORY_REPO` in `repo_root`, and for `FACTORY_STATE` in `instance.state_root` and `store.state_root`. `not_found_message` keeps quoting the raw value. Update the module docstring of `factory/instance.py`.
- F3. Tests in `tests/factory/test_store_setup.py`, through `factory paths`.

**G. The suite runs mid-edit** (H8; tests only)
- G1. New file `tests/factory/clean_harness_cli.py`, not collected because it is not named `test_*`. It runs the CLI as `bin/factory` does. It sets `FACTORY_CWD` to the working directory, changes into the harness checkout (two levels above the file), and puts it first on `sys.path`. It replaces `factory.instance.harness_changes` with a function that returns `[]`, then exits with `factory.cli.main(sys.argv[1:])`. Its docstring says it is test-only and stubs only the uncommitted-edit refusal (design item C.4). The lock comparison (design items C.2 and C.3) still runs.
- G2. `tests/factory/test_harness_lock.py` `cli`: when `harness` is this checkout and the subcommand is neither `init` nor `paths`, run `[sys.executable, <clean_harness_cli.py>, *argv]`. The subcommand is the first argument that is not `--accept-harness` or its value. Otherwise run `harness/bin/factory`, as today. Clone cases, including the uncommitted-edit refusal tests, keep the clone's real `bin/factory`. Replace module docstring lines 8-10 with that rule.
- G3. `tests/factory/test_instance.py` `cli`: run the launcher unless `argv[0]` is `init` or `paths`. Those two commands are exempt from the lock and keep exercising `bin/factory`'s own hand-over of the caller's directory. Add `import sys`.
- G4. A prototype of G1-G3 in a clone with an uncommitted edit printed `215 passed` (Evidence).

**I. Re-plan after a failed parent-close check** (H9; `factory/subtickets.py`, `factory/cli.py`, `factory/compose.py`)
- I1. `subtickets.parse(planner_output, parent, existing=())`. `existing` holds the ids of the parent's sub-tickets already in the store. Number new sub-tickets from the highest existing index plus 1, or from 1 when there are none. Refuse a head label that is in `existing`: `<label>: <label> is already a sub-ticket of <parent>; give the new sub-ticket another id`. In `Depends on:`, a reference that names an existing sub-ticket is kept as a dependency. Check that after the new-id and label lookups and before the "not a sub-ticket of this plan" refusal. Update the module docstring.
- I2. `subticket_add` passes the parent's existing sub-ticket ids, from `store.subtickets_of`. Its other checks are unchanged.
- I3. `resolve`: add `--replan FILE`, tried after `--redispatch` and before `--close`. Refuse unless the ticket is parked. Refuse when it has no sub-tickets: `--replan applies to a parent with sub-tickets; <id> has none`. Refuse when any sub-ticket is not `merged`, naming each one with its state: `--replan needs every sub-ticket merged: T-0001.2 is closed`. Otherwise copy FILE to the next `approvals/<id>/ruling-<n>.md` and move the ticket to `ready-for-planner` with kind `replan`, the ruling path in the record, and the round unchanged. Add `a.replan` to the modes that `--decision` refuses. Add `--replan F` to the "resolve needs one of" message.
- I4. `compose`, the `planner` branch: when `store.subtickets_of(root, tid)` is not empty, append, after the rulings, a section headed `## Sub-tickets already under <tid>`. Its first line reads: "A new plan's sub-tickets are numbered after these. A `Depends on:` line may name any of these ids." Then one line per sub-ticket, in id order: `- <id> / <title>: <status>`. With no sub-tickets, the planner's input is unchanged. No change to `build.js`: it runs Plan from `ready-for-planner`, then `subticket add --run`, which now numbers after the merged sub-tickets.
- I5. New test file `tests/factory/test_replan.py`. It covers: the re-plan move, the ruling, the planner input with its sub-ticket list, the not-all-merged refusal and the no-sub-tickets refusal; a first plan's planner input with no sub-ticket section; numbering after existing sub-tickets; a dependency on a merged sibling; the reused-label refusal with nothing written; and a first plan still numbered from `.1`.

**J. Documents**
- J1. `docs/changelog.md`: after entry 50 and before `Declined:`, add entry `51. After issue #39 (2026-10-04), a batch of harness defects found in real runs:`. Each seam adds one clause. The seam that merges first creates the entry, and later seams add their clause to it without a new number. Between them the clauses must use each of these words: `BLOCKED`, `--replan`, `next free`, `error text`, `redispatch`, `-whitespace`, `context.md`, `relative` and `uncommitted`.
  - S1: `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling and the existing sub-tickets listed in its input. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones.
  - S2: a park reason always ends with the failing command's error text. The workflows fall back to the refusal's JSON `error`, then to the exit code. A redispatch sets aside only the rows that did not pass, and the build re-runs only the checkers with no row on the commit.
  - S3: the store's `.gitattributes` marks run records `-whitespace`, written by `init` and `run start`. `init` refuses to create an instance on a throwaway store, and a missing `context.md` refuses a compose with exit 2. A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory.
  - S4: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested.
- J2. (S1) `README.md`, "Where a human decides", Unstick row: `--ruling F` (a role escalated) becomes `--ruling F` (a role escalated, or an implementer reported itself blocked). Add `` · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) ``. In the "Gap, as of today" paragraph, delete its first two sentences. The tripwire sentence then reads: "A ticket the tripwire parked returns with a plain `ticket transition` to the state its record names as `parked.from`, once the operator has checked the named files; a checker park can use `resolve --redispatch` instead."
- J3. (S3) `README.md`, the "How the harness finds a target" paragraph: append "A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` is taken from the directory the command runs in."
- J4. Each seam that edits `README.md` sets the status-header date to its merge date.
- J5. `docs/design.md` and `dev/build-harness.spec.md`: no change. The design already states the BLOCKED ruling (line 98), the re-plan under the same parent (line 100), re-dispatching only the killed role (line 102) and comment-only ledger rows (line 696). The build spec's line 314 already sends a re-plan through `ready-for-planner`. Its `--amend-spec` stays unbuilt and out of scope.

## Tests to change

- `tests/factory/test_shepherd.py` `test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix`. Part D keeps a reviewer row that passed, so:
  - line 585 expects `f.results(st) == {"reviewer": "APPROVE"}` and `superseded-1` holding `["ci.yaml", "verifier.yaml"]`;
  - line 587, which re-runs the reviewer, is removed;
  - the docstring's "the old rows are set aside" becomes "the rows that did not pass are set aside".
- `tests/factory/test_harness_lock.py`: the `cli` helper and module docstring lines 8-10 (part G2). No assertion changes.
- `tests/factory/test_instance.py`: the `cli` helper and one import (part G3). No assertion changes.

I read the other tests that touch what this change affects, and grepped the suite for every listing of a store's or instance's files (`iterdir`, `rglob`, `written`). None needs a change:
- `tests/factory/test_spec_store.py` line 151 checks only that a second `init` writes nothing, which stays true.
- `tests/factory/test_instance.py` line 79 lists `.factory/`, not the store; lines 147 and 157 check `written` on an `init` that runs after the store already has `.gitattributes`.
- `tests/factory/test_harness_lock.py` lines 47 and 69 and `tests/factory/test_instance.py` line 42 snapshot a tree around a refused command, which stops before `run start` writes anything.
- `tests/factory/test_run_scratch.py` line 163 and `tests/factory/test_tripwire.py` line 230 list one run's directory, not the store root.
- Every plan in the suite starts a parent's sub-tickets at `.1`, which part I keeps. No suite test composes a planner input for a ticket that already has sub-tickets.

