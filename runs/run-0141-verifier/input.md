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
  `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
  `intake/state/` until an operator step moves it.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
it only to observe what a fix does there today; never write there, and never copy its test names,
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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0141-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0141-verifier/wt` (branch `factory/T-0016.1`, base `924513ecb731b57f4396b602ff31a1169150b3e3`, head `d45f0601ba30199152da28af556513dd2fc0caf0`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0016.1

T-0016.1 / Run REGRESSION checks and gates once, and let a single-sub-ticket parent close on its sub-ticket's VERIFIED run
  Parent: T-0016, approved spec v1 (`.factory/state/specs/T-0016/v1.md`). Read it for context. Do NOT implement parts outside this sub-ticket.
  Depends on: none
  Parallel-safe: yes (it is the only sub-ticket)
  Scope: parts A, B, C, D and E of the parent, all of them.
    - A: implementer step 2, step 5 and the PR DESCRIPTION line, in the design block `## 5. Implementer` (`docs/design.md`), `docs/prompts/05-implementer.md` (re-copied verbatim from the block) and `factory/prompts/implementer.md` (keeps its own step 5 gate wording and step 6 rebase wording).
    - B: verifier step 3, the new step 4 sentence and the OUTPUT `Per criterion:` line, in `## 7. Verifier` (`docs/design.md`), `docs/prompts/07-verifier.md` (re-copied verbatim) and `factory/prompts/verifier.md` (keeps its own step 4 gate wording). Verdict rules unchanged.
    - C: `_reused_subticket_run` in `factory/cli.py` with conditions (1) to (4) and one `factory:` comment naming its limit; `_parent_close_verified` returns a run id; `ticket_transition` to `closed` records `verified_by`; `ticket parent-check` adds `reuse`; `factory/workflows/build.js` phase 3 calls `parent-check` first and skips the verifier when `reuse` names a run.
    - D: `docs/design.md` Merge gate row (line 126) and Archive paragraph (line 82); `dev/build-harness.spec.md:285`; `docs/changelog.md` entry 45 before `Declined:`; `README.md` "How a ticket moves" sentence and status date.
    - E: new file `tests/factory/test_parent_close_reuse.py`; the one-line edit to each of the two `test_shepherd.py` tests below.
  Acceptance (all from the parent's `verification.md`; run with bash from the root of the checkout under test):
    - implementer-runs-regression-checks-once (NEW)
      WHEN `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; for f in docs/design.md docs/prompts/05-implementer.md factory/prompts/implementer.md; do echo "${f##*/} new=$(n '2. Run the NEW acceptance commands first.' $f) after=$(n 'A REGRESSION command that fails here' $f) old=$(n '2. Run the acceptance commands first.' $f)"; done`
      THEN `design.md new=1 after=1 old=0`, `05-implementer.md new=1 after=1 old=0`, `implementer.md new=1 after=1 old=0`, one per line
    - verifier-runs-regression-on-base-only-on-failure (NEW)
      WHEN `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; for f in docs/design.md docs/prompts/07-verifier.md factory/prompts/verifier.md; do echo "${f##*/} new=$(n '3. Run the NEW commands on the base you were given' $f) onfail=$(n 'Run a REGRESSION command on base only when it fails on the PR' $f) old=$(n '3. Run the same commands on the base you were given' $f) defect=$(n 'is a SPEC-DEFECT, not a pass or a fail' $f) gate=$(n 'A gate failure' $f)"; done`
      THEN `design.md new=1 onfail=1 old=0 defect=1 gate=2`, `07-verifier.md new=1 onfail=1 old=0 defect=1 gate=1`, `verifier.md new=1 onfail=1 old=0 defect=1 gate=1`, one per line
    - one-run-serves-scenario-and-gate (NEW)
      WHEN `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; for f in docs/design.md docs/prompts/05-implementer.md docs/prompts/07-verifier.md factory/prompts/implementer.md factory/prompts/verifier.md; do printf '%s=%s ' "${f##*/}" "$(n 'ran a gate command exactly as written' $f)"; done; echo`
      THEN `design.md=2 05-implementer.md=1 07-verifier.md=1 implementer.md=1 verifier.md=1` (a trailing space is allowed)
    - changed-blocks-copied-verbatim (REGRESSION)
      WHEN `q=$(printf '\140\140\140'); for s in "5. Implementer:05-implementer" "7. Verifier:07-verifier"; do f=${s##*:}; sed -n "/^## ${s%%:*}\$/,/^$q\$/p" docs/design.md | sed "1,/^${q}text\$/d;\$d" | cmp -s - docs/prompts/$f.md && echo "$f verbatim" || echo "$f differs"; done`
      THEN `05-implementer verbatim` then `07-verifier verbatim`
    - one-sub-ticket-parent-closes-on-its-verified-run (NEW)
      GIVEN the function `fx` exactly as written in the parent spec's GIVEN for this scenario (copy it verbatim; it works only under `mktemp -d`)
      WHEN `fx one`
      THEN `one: subs=1 ready-for-parent-verify reuse=run-0004-verifier closed parent_runs=0 verified_by=run-0004-verifier`
    - parent-close-run-still-required-otherwise (REGRESSION)
      GIVEN `fx` as above, in the same bash session
      WHEN `for v in moved two uncovered; do fx $v; done`
      THEN exactly `moved: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`, `two: subs=2 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`, `uncovered: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`, one per line
    - rule-recorded-in-design-build-spec-readme-changelog (NEW)
      WHEN `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; echo "design=$(n 'stands for the parent-close run' docs/design.md) buildspec=$(n 'stands for the parent-close run' dev/build-harness.spec.md) readme=$(n 'already checked the same code' README.md) changelog=$(awk '/^45\. /{e=NR} /^Declined:/{d=NR} END{print (e>0 && e<d) ? "before-declined" : "missing"}' docs/changelog.md)"`
      THEN `design`, `buildspec` and `readme` each 1 or more, and `changelog=before-declined`
    - Intermediate checks: none. The gate commands (`git diff --check main...HEAD` and `uv run --frozen pytest -q -p no:cacheprovider tests/factory`) run in every verifier run; the suite gate covers the new test file and the two edited `test_shepherd.py` tests. The `build.js` skip has no runnable check: the reviewer checks it against part C, and the parent's Operator step 2 observes it.
  Tests to change: `tests/factory/test_shepherd.py::test_the_planned_ticket_is_built_checked_merged_and_archived` and `tests/factory/test_shepherd.py::test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_run`, each gaining only `f.git("commit", "-q", "--allow-empty", "-m", "another change on main")` after the sub-ticket merges and before `f.parent_check(tid)`. No assertion removed or weakened.
  Protected paths: harness: `factory/cli.py`, `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/workflows/build.js`; generated: `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md` (re-copied from the changed design blocks only).
  Out of scope: the path-scoped gate skip; the clerk agent and typed role agents (#24); the whitespace gate's empty comparison on a parent-close run; what spec writers put in acceptance lists; any change to NEW checks' before and base runs, the gate commands, the merge gate, the join decision, conflict runs, or parent closes with two or more sub-tickets; `.factory/**` (including `instance.yaml`), `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`; moving the runtime checkout (operator step 1).

## Parent spec (v1, pinned)

=== proposal.md
## Problem

Every ticket the factory builds runs the target repository's full test suite about six times, and only two of those runs can change the outcome. The cost falls on the operator, who waits for each build. On this repository a suite run takes 80 to 110 seconds. On the Nanobot port, with about 7,600 tests and 32 tickets queued, it will be the largest cost of every build. The operator wants this fixed before those builds start.

Some terms used below. A ticket's spec is split by a planner agent into sub-tickets, each built by one implementer agent on its own branch. A verifier agent then checks the branch, and the branch is merged. When every sub-ticket has merged, one more verifier run, the parent-close run, checks the whole spec on the merged code. Only then does the ticket close. Each spec lists acceptance checks: shell commands with expected output. A NEW check must fail before the change and pass after it. A REGRESSION check must pass both before and after. The gate commands are the repository's own checks, here a whitespace check and the test suite. The verifier runs them on every branch it checks.

Three kinds of run cannot change the verdict:

1. The implementer runs every acceptance check before editing, and the verifier runs every check again on the code before the change. For a REGRESSION check, that run only confirms what was already known: the spec writer saw it pass on `main`. Only NEW checks need the before-run, because they must be seen to fail first.
2. When a ticket had one sub-ticket and `main` has not moved since it merged, the parent-close run checks the same files as the sub-ticket's verifier, against the same starting commit, with the same checks. The last three tickets were all like this. Their parent-close runs took 13 to 23% of each build and all returned the sub-ticket's verdict.
3. Within one verifier run, an acceptance check that runs the test suite and the gate step that runs it again are two runs of the same suite on the same commit.

Every refusal the checks give today must still happen. A NEW check that does not fail first is still a spec defect. A failing REGRESSION check still fails the branch. A failing test suite still fails the branch.

## Evidence

Run records in this repository's store (`.factory/state/runs/<run>/meta.yaml` for `wall_s`, the run's time in seconds, and `output.md` for what it ran):

| Ticket | Build runs, total time | Parent-close run | Share | Sub-tickets |
|---|---|---|---|---|
| T-0013 | 0108–0112, 1,754 s | run-0112, 330 s | 19% | 1 |
| T-0014 | 0118–0125, 1,878 s | run-0125, 244 s | 13% | 1 |
| T-0015 | 0130–0134, 1,650 s | run-0134, 386 s | 23% | 1 |

The totals add up each run's own time. Reviewer and verifier run in parallel, so the wall-clock build is shorter.

Suite runs inside the T-0015 build, from the run outputs:
- Implementer `run-0131`: the `gates-pass` REGRESSION check before editing, `126 passed in 101.27s`, and after, `131 passed in 83.81s`; then the gate step again (`output.md:43`, `131 passed`, no time given).
- Sub-ticket verifier `run-0132`: `gates-pass` on base, `126 passed in 108.52s`, and on head, `131 passed in 112.14s` (`output.md:16`). Its gate line repeats `112.14s`, so it reported one head run twice.
- Parent-close verifier `run-0134`: base `126 passed in 85.29s`, head `131 passed in 81.77s` (`output.md:16`). Its whitespace gate compared `main` with itself (`output.md:44`).

That is at least six suite runs, about 570 s of suite time. Of those, one implementer run after the edit and one verifier run on the head can change a verdict.

The parent-close run checked the same tree as the sub-ticket's verifier in all three builds. `git rev-parse <sub-ticket head>^{tree}` equals `git rev-parse <parent-close head>^{tree}` for e703c1b/01f7524, 89e8b7d/fcc8756 and 27d6d63/530c9ef, so `same_tree=yes` three times. Each sub-ticket's verifier base equals the parent's recorded base: 0759162, 431e349 and 61d92be. Each sub-ticket text names every scenario of its parent's pinned spec (9 of 9, 7 of 7, 10 of 10, by `grep -F` of each `#### Scenario:` name in `specs/<id>.1/subticket.md`). All three parent-close runs returned VERIFIED. The only parent-close run that did not was T-0012's `run-0102`, SPEC-DEFECT. That ticket had six sub-tickets, so the rule below would not have skipped it.

Today the parent cannot close without its own run. This black-box check, the GIVEN fixture of the scenarios below, was run on `main` at `3b87d6c`. It drives `bin/factory` against a scratch repository and store, with one sub-ticket merged and `main` unmoved:
`one: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`
`refused` means `ticket transition T-0001 --to closed` exits 2: no VERIFIED parent-close run exists.

Part of the request's evidence is wrong. It says T-0014 and T-0015 changed only documents. T-0014's merge `fcc8756` touched only `docs/writing.md`. T-0015's merge `530c9ef` also changed `factory/cli.py` and `factory/instance.py`. The suite also reads documents: `docs/writing.md`, `docs/coding.md` and `docs/design.md` against `docs/prompts/*` (`tests/factory/test_writing_standard.py:19,65,77`, `tests/factory/test_coding_standard.py:20,74,86`).

Gates on `main` at `3b87d6c`: `git diff --check main...HEAD` exit 0, and `131 passed in 103.02s`.

No reference fix exists: the request names no Nanobot commit, and `~/dev/nanobot-upstream` has no `factory/` directory on its current branch.

## Root cause

- Implementer step 2 runs "the acceptance commands first", all of them (`factory/prompts/implementer.md:5-7`; design block `docs/design.md:492-494`; copy `docs/prompts/05-implementer.md`).
- Verifier step 3 runs "the same commands on the base", all of them (`factory/prompts/verifier.md:9-14`; `docs/design.md:607-612`; `docs/prompts/07-verifier.md`). Step 4 runs the gate commands again, even when a step 2 check has just run them on the same head.
- `factory/workflows/build.js:217-222` always starts a parent-close verifier run. `_parent_close_verified` (`factory/cli.py:860-877`) accepts only a VERIFIED verifier run on the parent itself. It gates both `ticket_transition` to `closed` (`factory/cli.py:153-157`) and `archive_cmd` (`factory/cli.py:889`). `ticket_parent_check` (`factory/cli.py:586-600`) reports no way to skip the run.
- The merge gate already guarantees the tree identity the skip relies on. `merge_cmd` (`factory/cli.py:494-538`) merges only a head that contains `main`, with `--no-ff`. So when `main` has not moved since that merge, its tree is the merged head's tree.

## Out of scope

- The request's path-scoped gate skip, where a gate command is skipped when the diff touches none of its declared paths. It is cut from this ticket; see Decisions.
- The clerk agent and typed role agents (the requester's own exclusion; issue #24).
- The whitespace gate's empty comparison on a parent-close run (`git diff --check main...HEAD` with HEAD = `main`). The parent-close runs that still happen keep it as today.
- What a spec writer puts in acceptance lists, such as the customary `gates-pass` scenario. Part B makes it cost no extra suite run.
- NEW checks: still run before and after by the implementer, and on base and head by the verifier.
- Gate commands, the merge gate, the join decision, conflict runs, and parent closes with two or more sub-tickets.
- `.factory/**`, including `instance.yaml`.

## Open questions

none

## Decisions

- The path-scoped gate skip is cut. A correct path list for this repository covers `docs/**`, because the suite reads `docs/design.md`, `docs/prompts/*`, `docs/writing.md` and `docs/coding.md`. With that list it would have skipped no suite run in the last three builds. Its saving is on Nanobot and unmeasured, and a path list that misses one file the suite reads silently drops a refusal. Rejected: shipping it with the requester's list, which would skip the suite on a prompt-block edit that fails it today.
- A REGRESSION check runs once, after the change. It runs on the base only when it fails after the change. That base run tells "this change broke it" from "it was already failing". So the implementer still stops when the spec does not match reality, and pays for the base run only on a failure. Rejected: dropping the base run outright, which would leave the implementer unable to tell the two apart.
- A check that already ran a gate command exactly as written on the same commit counts as that gate's run, for both the implementer and the verifier.
- A parent closes on its sub-ticket's VERIFIED run when all of these hold: the parent has exactly one sub-ticket, and it is merged; the integration branch is still at that sub-ticket's merge commit; the results row for the merged head is VERIFIED, from a run whose base is the parent's recorded base; and the sub-ticket's text names every `#### Scenario:` of the parent's pinned spec. Otherwise the parent-close run happens as today. Rejected: matching trees alone, which would accept a sub-ticket told to check fewer scenarios. Also rejected: parsing the verifier's per-criterion rows, which are free text; `run-0132` and `run-0134` order their fields differently.
- A parent closed this way loses the second, independent verifier run on the same code. It is accepted because the three builds where this rule would have applied all got the same verdict from both runs.
- The parent's close records which verifier run it closed on (`verified_by`), its own or the reused one, so an auditor can tell the two apart.
- A reused close still goes through `archive` and its refusals, unchanged.
- `README.md`'s "How a ticket moves" changes in this ticket, because it describes a step that this change removes in one case. The first real build after the runtime upgrade confirms it (Operator step 2).

## Risk

Blast radius: every implementer and verifier run, through their prompts, and every parent close with one sub-ticket. If the prompt text is misread, a verifier could skip a NEW check's base run. That would lose spec-defect detection. The wording keeps the NEW base run as its own sentence, and scenario `verifier-runs-regression-on-base-only-on-failure` checks that the spec-defect and gate-failure sentences stay. If the reuse condition is too loose, a parent could close on a verification that did not cover the whole spec. The condition is checked by the store CLI, not by an agent, and the fallback is today's run.

Protected paths touched:
- harness: `factory/cli.py`, `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/workflows/build.js`.
- generated: `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`, each re-copied from its changed design block.

Guardrail paths: the implementer and verifier prompts, which this ticket changes by design. Also the existing test file `tests/factory/test_shepherd.py`, where only the two tests under "Tests to change" are edited, so the PR goes to the human gate. Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`.

## Operator steps

1. After merge, move the runtime checkout to the merge commit and accept it with `--accept-harness`, as for every harness change. Builds keep today's behaviour until then.
2. On the next real build, compare each run's `wall_s` with T-0015's: implementer 451 s, sub-ticket verifier 381 s, parent-close verifier 386 s. Note whether the implementer and verifier outputs show one suite run each on the passing path. If the parent had one sub-ticket, check that the build log shows no parent-close run and that the parent's history names `verified_by`. Record the result on the issue. This step is an observation, not acceptance.

=== design.md
## Proposed change

A. **Implementer: REGRESSION checks and gates run once, after the edit.** Edit all three copies the same way: the design block `## 5. Implementer` in `docs/design.md`, its verbatim copy `docs/prompts/05-implementer.md`, and the runtime copy `factory/prompts/implementer.md`. The runtime copy keeps its existing differences: the gate-command wording in step 5 and the rebase wording in step 6.
- Step 2 becomes:
  ```
  2. Run the NEW acceptance commands first. They should fail as
     described. If one behaves otherwise, stop and escalate: the spec
     doesn't match reality. REGRESSION commands passed on main when the
     spec was written, so they run once, after your change (step 5).
  ```
- Step 5 becomes the following design form. The runtime copy keeps "the gate commands listed in your input under "Where you work", each exactly as written" in place of `{gate commands}`:
  ```
  5. Run every acceptance command, then the full local gates:
     {gate commands}. A command that already ran a gate command exactly
     as written on this commit is that gate's run; don't repeat it. A
     REGRESSION command that fails here: run it on the base you branched
     from. If it fails there too, the spec doesn't match reality; stop
     and escalate.
  ```
- The PR DESCRIPTION line becomes `Acceptance results: each command + actual output (NEW: before and after; REGRESSION: after, and base if it failed)`.

B. **Verifier: REGRESSION checks on head only, and no second gate run.** Edit the three copies (`## 7. Verifier` in `docs/design.md`, `docs/prompts/07-verifier.md`, `factory/prompts/verifier.md`) the same way. The runtime copy keeps its own step 4 gate wording.
- Step 3 becomes:
  ```
  3. Run the NEW commands on the base you were given (the base branch,
     or for a parent close the main SHA before the parent's first merge).
     NEW criteria should fail there and pass on the PR. A NEW criterion
     that passes on both, or fails on base for a different reason than
     the spec states (e.g. its test doesn't exist yet), is a SPEC-DEFECT,
     not a pass or a fail. Run a REGRESSION command on base only when it
     fails on the PR, and report both results.
  ```
- Step 4 gains a second sentence: `A step 2 command that ran a gate command exactly as written on the PR is that gate's run; don't repeat it.`
- The OUTPUT line `Per criterion: …` gains `(base: not run, for a REGRESSION that passed on the PR)`.
- The verdict rules are unchanged: a failing REGRESSION is FAIL, a gate failure is FAILED, and a wrong NEW is SPEC-DEFECT.

C. **Parent close reuses a single sub-ticket's VERIFIED run.**
- `factory/cli.py`: add `_reused_subticket_run(root, cfg, t) -> str | None`. It returns the run id when every condition below holds, and `None` otherwise:
  - (1) `store.subtickets_of` gives exactly one sub-ticket `s`, with `status == "merged"` and `s["merge"]["main_after"]` set, and the parent has `parent_base`.
  - (2) `gitops.rev(repo, gitops.integration_branch(cfg, repo)) == s["merge"]["main_after"]`.
  - (3) `store.results_for(root, s["head"])["verifier"]` has status `VERIFIED` and a `run_id`, and that run's `meta.yaml` has `status: VERIFIED`, `head == s["head"]` and `base == t["parent_base"]`.
  - (4) `specstore.scenario_names()` of `specs/<parent>/v<approved_version>.md` is non-empty, and each name occurs in `specs/<s id>/subticket.md`.

  Mark it with one `factory:` comment that names the limit: one sub-ticket only, and scenario coverage read from names in the sub-ticket's text.
- `_parent_close_verified` returns the id of the run that verifies the parent instead of `True`/`False`. That is the parent's own VERIFIED run, found as today, or else `_reused_subticket_run`. Its callers keep their truthiness test.
- `ticket_transition` to `closed` on a parent adds `verified_by: <run id>` to the history entry it appends.
- `ticket_parent_check` adds `"reuse": <run id or null>` to its JSON. The value is `_reused_subticket_run` when the parent's status is `ready-for-parent-verify` after the check, and `null` otherwise. The check stays a read apart from the state move it already makes.
- `factory/workflows/build.js`, phase 3: at the start of Close, clerk `ticket parent-check PARENT` (the parent may arrive already in `ready-for-parent-verify` on a resumed build). If `reuse` names a run, `log()` that the sub-ticket's run stands for the parent-close run, start no verifier, and go to `archive`, with that run id as the park outputs. Otherwise run the verifier exactly as today. The archive, transition and park handling stay as they are.

D. **Records.**
- `docs/design.md` routing table, Merge gate row (line 126): after "one verifier run on main against the parent's full Acceptance list (…)", add one sentence. It says that when the parent has one sub-ticket, `main` has not moved since its merge, the sub-ticket's text names every scenario of the parent's pinned delta, and its VERIFIED run checked the merged head against the parent's recorded base, that run stands for the parent-close run and no new run starts. The phrase "stands for the parent-close run" must appear.
- `docs/design.md` Archive paragraph (line 82): "After the parent-close run returns VERIFIED" becomes "After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row)".
- `dev/build-harness.spec.md:285`: in the description of the parent-close run, add the `parent-check` `reuse` field and the skip, using the phrase "stands for the parent-close run".
- `docs/changelog.md`: add entry 45 after 44 and before "Declined:". It says what changed: REGRESSION checks run once after the change, one gate run per commit, and a single-sub-ticket parent closes on its sub-ticket's VERIFIED run. It names the trigger: issue #31, from the T-0013 to T-0015 build timings.
- `README.md`, "How a ticket moves", the paragraph that begins "When every sub-ticket has merged": after its first sentence, add a sentence saying the final run is skipped when the spec had one sub-ticket, that sub-ticket was told to check every scenario, and the integration branch has not moved since it merged. The sentence ends "the sub-ticket's verifier already checked the same code against the same starting point." Bump the status date, per "Maintaining this page".

E. **Tests.** Add a new file, `tests/factory/test_parent_close_reuse.py`, in the style of the Shepherd fixture. It covers: a single sub-ticket parent closes and archives with no parent verifier run, and `verified_by` names the sub-ticket's run; `main` moved, two sub-tickets, a sub-ticket text missing a scenario, and a VERIFIED row whose run base differs from `parent_base` each leave `reuse` null and the plain close refused. Edit the two existing tests listed below.

## Tests to change

- `tests/factory/test_shepherd.py::test_the_planned_ticket_is_built_checked_merged_and_archived` and `tests/factory/test_shepherd.py::test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_run`. Both build one sub-ticket from the `accept-approve` plan, whose text names the parent's only scenario, and leave `main` unmoved. Under part C that parent closes on the sub-ticket's run. So the first test's `archive` refusal assertion (line 227-228) and the second's refused-transition assertion (line 487-488) would fail. Change: each test gains one line, `f.git("commit", "-q", "--allow-empty", "-m", "another change on main")`, after the sub-ticket merges and before `f.parent_check(tid)`. The parent-close run they exist to test is then still required. No assertion is removed or weakened.

=== specs/build-checks/spec.md
## ADDED Requirements

### Requirement: regression-checks-run-once-after-the-change
The implementer and verifier prompts SHALL run a REGRESSION acceptance check once, after the change or on the head under check, and on the base only when it fails there. They SHALL keep NEW checks' before or base runs and every existing refusal.

#### Scenario: implementer-runs-regression-checks-once
- WHEN (bash, from `~/dev/spec-factory`) `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; for f in docs/design.md docs/prompts/05-implementer.md factory/prompts/implementer.md; do echo "${f##*/} new=$(n '2. Run the NEW acceptance commands first.' $f) after=$(n 'A REGRESSION command that fails here' $f) old=$(n '2. Run the acceptance commands first.' $f)"; done`
- THEN it prints `design.md new=1 after=1 old=0`, `05-implementer.md new=1 after=1 old=0` and `implementer.md new=1 after=1 old=0`, one per line

#### Scenario: verifier-runs-regression-on-base-only-on-failure
- WHEN (bash, from `~/dev/spec-factory`) `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; for f in docs/design.md docs/prompts/07-verifier.md factory/prompts/verifier.md; do echo "${f##*/} new=$(n '3. Run the NEW commands on the base you were given' $f) onfail=$(n 'Run a REGRESSION command on base only when it fails on the PR' $f) old=$(n '3. Run the same commands on the base you were given' $f) defect=$(n 'is a SPEC-DEFECT, not a pass or a fail' $f) gate=$(n 'A gate failure' $f)"; done`
- THEN it prints `design.md new=1 onfail=1 old=0 defect=1 gate=2`, `07-verifier.md new=1 onfail=1 old=0 defect=1 gate=1` and `verifier.md new=1 onfail=1 old=0 defect=1 gate=1`, one per line

#### Scenario: one-run-serves-scenario-and-gate
- WHEN (bash, from `~/dev/spec-factory`) `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; for f in docs/design.md docs/prompts/05-implementer.md docs/prompts/07-verifier.md factory/prompts/implementer.md factory/prompts/verifier.md; do printf '%s=%s ' "${f##*/}" "$(n 'ran a gate command exactly as written' $f)"; done; echo`
- THEN it prints `design.md=2 05-implementer.md=1 07-verifier.md=1 implementer.md=1 verifier.md=1` (a trailing space is allowed)

#### Scenario: changed-blocks-copied-verbatim
- WHEN (bash, from `~/dev/spec-factory`) `q=$(printf '\140\140\140'); for s in "5. Implementer:05-implementer" "7. Verifier:07-verifier"; do f=${s##*:}; sed -n "/^## ${s%%:*}\$/,/^$q\$/p" docs/design.md | sed "1,/^${q}text\$/d;\$d" | cmp -s - docs/prompts/$f.md && echo "$f verbatim" || echo "$f differs"; done`
- THEN it prints `05-implementer verbatim` then `07-verifier verbatim`

=== specs/parent-close/spec.md
## ADDED Requirements

### Requirement: single-sub-ticket-parent-closes-on-its-verified-run
A parent ticket with exactly one merged sub-ticket SHALL close without a parent-close verifier run when all of these hold: the integration branch is still at that sub-ticket's merge commit; the sub-ticket's merged head has a VERIFIED verifier result whose run checked it against the parent's recorded base; and the sub-ticket's text names every scenario of the parent's pinned spec. In every other case the parent MUST still require its own VERIFIED parent-close run.

#### Scenario: one-sub-ticket-parent-closes-on-its-verified-run
- GIVEN (bash, from `~/dev/spec-factory`; it creates and removes its own scratch repository and store under `mktemp -d` and touches nothing in the checkout) this function is defined:
  ```bash
  fx() {
    local R=$PWD S=$PWD/tests/factory/fixtures/stubs/accept-approve T p i w h r st subs=T-0001.1; T=$(mktemp -d)
    export FACTORY_STATE=$T/state FACTORY_REPO=$T/repo FACTORY_INTEGRATION_BRANCH=main PYTHONDONTWRITEBYTECODE=1
    f() { "$R/bin/factory" "$@"; }
    j() { python3 -c 'import json,sys; print(json.loads(sys.stdin.read().strip().splitlines()[-1]).get(sys.argv[1]))' "$1"; }
    g() { git -c user.email=f@x -c user.name=f "$@"; }
    git init -q -b main $T/repo && g -C $T/repo commit -q --allow-empty -m init
    printf '# Fixture\n\nDo the thing.\n' > $T/req.md; f ticket new --file $T/req.md >/dev/null
    f spec add T-0001 --file $S/spec_writer-1.md >/dev/null
    for st in ready-for-spec-writer ready-for-critic awaiting-spec-gate; do f ticket transition T-0001 --to $st --by workflow >/dev/null; done
    f approve-spec T-0001 >/dev/null; p=$(f run start --role planner --ticket T-0001 | j run_id)
    case $1 in
      two) subs="T-0001.1 T-0001.2"; awk '/^Coverage map/{print "T-0001.2 / Do the other thing\n  Depends on: T-0001.1\n  Parallel-safe: yes\n"} {print}' $S/planner-1.md ;;
      uncovered) sed 's/asked once/the check/g' $S/planner-1.md ;;
      *) cat $S/planner-1.md ;;
    esac > $FACTORY_STATE/runs/$p/output.md
    f run finish $p >/dev/null; f plan add T-0001 --from-run $p >/dev/null; f subticket add T-0001 --run $p >/dev/null; f ticket transition T-0001 --to planned --by workflow >/dev/null
    for st in $subs; do
      i=$(f run start --role implementer --ticket $st | j run_id); w=$FACTORY_STATE/worktrees/$st
      echo x > $w/$st.txt; g -C $w add . && g -C $w commit -q -m $st; cp $S/implementer-1.md $FACTORY_STATE/runs/$i/output.md; f run finish $i >/dev/null
      h=$(f ticket head $st | j head); f ticket transition $st --to checks-in-flight --by workflow --round pr:init >/dev/null
      for r in reviewer verifier; do i=$(f run start --role $r --ticket $st | j run_id); sed "s/Commit: HEAD/Commit: $h/" $S/$r-1.md > $FACTORY_STATE/runs/$i/output.md
        f run finish $i >/dev/null; f run cleanup $i >/dev/null; f results record $st --head $h --role $r --output $FACTORY_STATE/runs/$i/output.md --run $i >/dev/null; done
      f ticket transition $st --to ready-for-merge --by workflow >/dev/null; f merge $st >/dev/null
    done
    [ "$1" = moved ] && g -C $T/repo commit -q --allow-empty -m "another change on main"
    echo "$1: subs=$(ls $FACTORY_STATE/tickets | grep -c '^T-0001\.[0-9]') $(f ticket parent-check T-0001 | j state) reuse=$(f ticket parent-check T-0001 | j reuse) $(f ticket transition T-0001 --to closed --by workflow >/dev/null 2>&1 && echo closed || echo refused) parent_runs=$(cat $FACTORY_STATE/runs/*-verifier/meta.yaml | grep -c '^ticket: T-0001$') verified_by=$(sed -n 's/^ *verified_by: //p' $FACTORY_STATE/tickets/T-0001.yaml)"
    rm -rf $T; unset FACTORY_STATE FACTORY_REPO FACTORY_INTEGRATION_BRANCH
  }
  ```
- WHEN `fx one`
- THEN it prints `one: subs=1 ready-for-parent-verify reuse=run-0004-verifier closed parent_runs=0 verified_by=run-0004-verifier`

#### Scenario: parent-close-run-still-required-otherwise
- GIVEN `fx` as in one-sub-ticket-parent-closes-on-its-verified-run, in the same bash session
- WHEN `for v in moved two uncovered; do fx $v; done`
- THEN it prints exactly `moved: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`, `two: subs=2 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` and `uncovered: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`, one per line

### Requirement: reuse-rule-recorded
The design document, the build spec, the README and the changelog SHALL state when a sub-ticket's VERIFIED run stands for the parent-close run.

#### Scenario: rule-recorded-in-design-build-spec-readme-changelog
- WHEN (bash, from `~/dev/spec-factory`) `n() { tr '\n' ' ' < "$2" | tr -s ' ' | grep -oF -- "$1" | wc -l | tr -d ' '; }; echo "design=$(n 'stands for the parent-close run' docs/design.md) buildspec=$(n 'stands for the parent-close run' dev/build-harness.spec.md) readme=$(n 'already checked the same code' README.md) changelog=$(awk '/^45\. /{e=NR} /^Declined:/{d=NR} END{print (e>0 && e<d) ? "before-declined" : "missing"}' docs/changelog.md)"`
- THEN `design`, `buildspec` and `readme` are each 1 or more, and `changelog=before-declined`

=== verification.md
## Acceptance

Run every command with bash from the root of the `~/dev/spec-factory` checkout under test. The parent-close fixture needs `git` and `python3` and writes only under `mktemp -d`. "Today" means `main` at `3b87d6c`, where every today output below was observed. No scenario repeats the gate commands, because the verifier runs them in every run (its step 4). On `3b87d6c` they give `check=0` and `131 passed`.

- implementer-runs-regression-checks-once → NEW; today each of the three lines prints `new=0 after=0 old=1`: every copy still runs all acceptance commands before editing.
- verifier-runs-regression-on-base-only-on-failure → NEW; today it prints `design.md new=0 onfail=0 old=1 defect=1 gate=2`, `07-verifier.md new=0 onfail=0 old=1 defect=1 gate=1` and `verifier.md new=0 onfail=0 old=1 defect=1 gate=1`. Step 3 still runs every command on base. `defect` and `gate` are the same today and after: the spec-defect and gate-failure refusals are kept.
- one-run-serves-scenario-and-gate → NEW; today it prints `design.md=0 05-implementer.md=0 07-verifier.md=0 implementer.md=0 verifier.md=0`: no copy lets a check's suite run count as the gate run.
- changed-blocks-copied-verbatim → REGRESSION; today it prints `05-implementer verbatim` then `07-verifier verbatim`.
- one-sub-ticket-parent-closes-on-its-verified-run → NEW; today it prints `one: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`. The parent cannot close without its own parent-close run, and `parent-check` has no `reuse` field.
- parent-close-run-still-required-otherwise → REGRESSION; today it prints the three lines in its THEN.
- rule-recorded-in-design-build-spec-readme-changelog → NEW; today it prints `design=0 buildspec=0 readme=0 changelog=missing`.

Not covered by a runnable check: the `build.js` skip in part C. That script runs only inside the workflow runtime. The reviewer checks it against part C, and Operator step 2 observes it on the first real build.

## Responses

none

## PR description (the implementer's output)

Sub-ticket: T-0016.1 (parent T-0016, approved spec v1). Branch `factory/T-0016.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0016.1`, base `924513ecb731b57f4396b602ff31a1169150b3e3`, head `d45f0601ba30199152da28af556513dd2fc0caf0` (two commits: `50fd7a3` the change, `d45f060` a fix to the new test file).

## What changed

Each build used to run the full test suite about six times when only two of those runs could change the verdict. It also started a parent-close run that repeated a check already made. A parent-close run is the final verifier run on the merged code, made after every sub-ticket has merged. This change removes the runs that cannot change a verdict. Every refusal the checks gave before still happens.

- **A. Implementer prompt.** Changed in three places: the design block `## 5. Implementer` in `docs/design.md`, its copy `docs/prompts/05-implementer.md` (re-copied from the block), and the runtime prompt `factory/prompts/implementer.md`.
  - Step 2 now runs only the NEW checks before the edit. A NEW check is one that must fail before the change.
  - Step 5 runs every acceptance check, then the gates. A check that already ran a gate command exactly as written on the same commit counts as that gate's run.
  - A REGRESSION check is one that must pass both before and after. One that fails at step 5 is run on the base. If it fails there too, the implementer stops and escalates.
  - The PR DESCRIPTION line now reads `NEW: before and after; REGRESSION: after, and base if it failed`.
  - The runtime copy keeps its own differences: the gate wording in step 5 ("the gate commands listed in your input under "Where you work", each exactly as written") and the no-rebase wording in step 6.
- **B. Verifier prompt.** Changed in the same three places: `## 7. Verifier`, `docs/prompts/07-verifier.md` and `factory/prompts/verifier.md`.
  - Step 3 runs only the NEW checks on the base. It runs a REGRESSION check on the base only when that check fails on the PR.
  - Step 4 gains the sentence that a step 2 command which ran a gate command exactly as written on the PR is that gate's run.
  - The `Per criterion:` line gains `(base: not run, for a REGRESSION that passed on the PR)`.
  - The verdict rules did not change. A wrong NEW check is SPEC-DEFECT, and a gate failure is FAILED. The runtime copy keeps its own step 4 gate wording.
- **C. Parent close can reuse a run** (`factory/cli.py`, `factory/workflows/build.js`).
  - New `_reused_subticket_run(root, cfg, t)` returns a run id only when spec conditions (1) to (4) all hold:
    1. The parent has exactly one sub-ticket, it is merged and has `main_after`, and the parent has `parent_base`.
    2. The integration branch is still at that `main_after`.
    3. The `verifier` results row for the merged head is VERIFIED with a `run_id`. That run's `meta.yaml` has `status: VERIFIED`, `head` equal to the merged head, and `base` equal to `parent_base`.
    4. The parent's pinned `specs/<id>/v<approved_version>.md` has at least one scenario, and every scenario name occurs in `specs/<sub id>/subticket.md`.
  - `_parent_close_verified` now returns the id of the run that verifies the parent, or `None`. That is the parent's own VERIFIED run, found as before, or else the reused run. Both callers keep their truth test: `ticket_transition` (`factory/cli.py:157`) and `archive_cmd` (`factory/cli.py:926`). I found them with `grep -rn _parent_close_verified factory bin tests agents`, and there are no other callers.
  - `ticket_transition` to `closed` on a parent adds `verified_by: <run id>` to the history entry it appends.
  - `ticket parent-check` adds `"reuse"` to its JSON. The value is a run id when the parent is `ready-for-parent-verify`, and `null` otherwise. The command makes no other change to the store.
  - `build.js` phase 3 now starts with clerk `ticket parent-check`. If `reuse` names a run, the script logs that the run stands for the parent-close run and starts no verifier. It then goes to `archive` with that run id as the park outputs. Otherwise the verifier runs as before. Archive, transition and park handling are unchanged.
  - Callers of `parent-check`: `build.js` phase 2 (it reads only `state`, so the new field does not affect it), the new call in phase 3, and the tests.
- **D. Records.**
  - `docs/design.md` Archive paragraph (line 82) and the Merge gate row of the routing table (line 126) now carry the rule, including "stands for the parent-close run".
  - `dev/build-harness.spec.md:285` describes the `parent-check` `reuse` field and the skip.
  - `docs/changelog.md` has entry 45, after 44 and before `Declined:`.
  - `README.md` "How a ticket moves" gains one sentence, which ends "the sub-ticket's verifier already checked the same code against the same starting point."
- **E. Tests.** A new file, `tests/factory/test_parent_close_reuse.py`, plus a one-line edit to each of the two listed tests in `test_shepherd.py`.

## Acceptance results

All commands were run with bash from the worktree root, before any edit and again at the final head `d45f060`. Every before output matches the "today" output in the parent's `verification.md`, and every after output matches the THEN line.

| Scenario | Label | Before (at `924513e`) | After (at `d45f060`) |
|---|---|---|---|
| implementer-runs-regression-checks-once | NEW | `design.md new=0 after=0 old=1` / `05-implementer.md new=0 after=0 old=1` / `implementer.md new=0 after=0 old=1` | `design.md new=1 after=1 old=0` / `05-implementer.md new=1 after=1 old=0` / `implementer.md new=1 after=1 old=0` |
| verifier-runs-regression-on-base-only-on-failure | NEW | `design.md new=0 onfail=0 old=1 defect=1 gate=2` / `07-verifier.md new=0 onfail=0 old=1 defect=1 gate=1` / `verifier.md new=0 onfail=0 old=1 defect=1 gate=1` | `design.md new=1 onfail=1 old=0 defect=1 gate=2` / `07-verifier.md new=1 onfail=1 old=0 defect=1 gate=1` / `verifier.md new=1 onfail=1 old=0 defect=1 gate=1` |
| one-run-serves-scenario-and-gate | NEW | `design.md=0 05-implementer.md=0 07-verifier.md=0 implementer.md=0 verifier.md=0 ` | `design.md=2 05-implementer.md=1 07-verifier.md=1 implementer.md=1 verifier.md=1 ` |
| changed-blocks-copied-verbatim | REGRESSION | `05-implementer verbatim` / `07-verifier verbatim` | `05-implementer verbatim` / `07-verifier verbatim` |
| one-sub-ticket-parent-closes-on-its-verified-run (`fx one`) | NEW | `one: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` | `one: subs=1 ready-for-parent-verify reuse=run-0004-verifier closed parent_runs=0 verified_by=run-0004-verifier` |
| parent-close-run-still-required-otherwise (`fx moved/two/uncovered`) | REGRESSION | `moved: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` / `two: subs=2 … reuse=None refused …` / `uncovered: subs=1 … reuse=None refused …` | the same three lines, unchanged |
| rule-recorded-in-design-build-spec-readme-changelog | NEW | `design=0 buildspec=0 readme=0 changelog=missing` | `design=1 buildspec=1 readme=1 changelog=before-declined` |

What the results show:
- The `defect` and `gate` counts are the same before and after. The spec-defect and gate-failure refusals are kept in every copy.
- `fx one` shows the new close: the parent closes with no verifier run of its own (`parent_runs=0`), and its history names the sub-ticket's run.
- The three REGRESSION lines show that every other case still refuses the close.
- I ran `fx` exactly as written in the parent spec's GIVEN.

Gates at `d45f060`:
- `git diff --check main...HEAD`: exit 0, no output. No whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `136 passed in 217.97s`. The suite passed in full: 131 existing tests and the 5 new ones.

The first suite run, at `50fd7a3`, gave `1 failed, 135 passed`. The failure was in my own new test `test_a_parent_close_run_is_still_required_with_two_sub_tickets`. Both sub-tickets wrote the same file with the same content, so the second implementer's `git commit` had nothing to commit. Commit `d45f060` gives each sub-ticket its own file. The production code did not change between the two runs.

## Tests added/changed

- **Added** `tests/factory/test_parent_close_reuse.py`, which reuses `built_to_implementer` from `test_shepherd.py` the way `test_killed_checker.py` does. Before the `cli.py` change, all 5 tests failed with `KeyError: 'reuse'`. After it, all 5 pass.

  | Test | What it checks |
  |---|---|
  | `test_a_single_sub_ticket_parent_closes_and_archives_on_its_verified_run` | `parent-check` reports `reuse` equal to the sub-ticket's verifier run. `archive` and then the plain close both succeed. The last history entry has `verified_by` set to that run. No verifier run exists for the parent, and current truth holds the scenario. |
  | `…when_main_moved_after_the_merge` | An empty commit on `main` after the merge leaves `reuse` null. The close and `archive` are both refused, and no parent verifier run exists. |
  | `…with_two_sub_tickets` | Both sub-ticket texts name the scenario, and `main` has not moved since the last merge. `reuse` is still null and the close is refused. |
  | `…when_the_sub_ticket_misses_a_scenario` | The sub-ticket text does not name `asked once`. `reuse` is null and the close is refused. |
  | `…when_the_verified_run_had_another_base` | The branch has two commits. After the verifier run starts, `main` fast-forwards to the branch's first commit, so the merge still goes through, but `parent_base` is not the verifier run's `base`. `reuse` is null and the close is refused. |

- **Changed**, both listed under "Tests to change": `test_shepherd.py::test_the_planned_ticket_is_built_checked_merged_and_archived` and `test_shepherd.py::test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_run`.
  - Each gains only `f.git("commit", "-q", "--allow-empty", "-m", "another change on main")`, after the sub-ticket merges and before `f.parent_check(tid)`.
  - The reason: both tests build one sub-ticket that names the parent's only scenario and leave `main` unmoved, so under part C their parent would close on the sub-ticket's run. With `main` moved, the parent-close run they exist to test is required again.
  - No assertion was removed or weakened.

## Known gaps and uncertainties

- **One `factory:` marker added**, at `factory/cli.py:867`. It names the limit: one sub-ticket only, and scenario coverage is read from scenario names found in the sub-ticket's text. It names the upgrade trigger: widen it only when the store can check a coverage map per sub-ticket.
- **Scenario names are matched as plain substrings.** A scenario named `asked once` also counts as covered by a sub-ticket text that says only `asked once more`. Real scenario names are kebab-case and longer, which makes such a clash unlikely. The spec chose "each name occurs in" the text.
- **The `build.js` skip has no automated test.** That script runs only inside the workflow runtime. I checked that it parses, by compiling it as an async function body with node. Its logic needs review against part C, and Operator step 2 will observe it on the first real build.
- **The base-mismatch test uses a constructed history.** It fast-forwards `main` to a commit inside the branch while the verifier runs. That is the only way I found to reach "VERIFIED, but the run's base differs from `parent_base`" through the CLI with one sub-ticket. It exercises condition (3)'s base comparison through real commands, not by editing store files.
- **A reused close has no second, independent verifier run.** The spec's Decisions accept this.
- **The README edit is ahead of a real run.** "Maintaining this page" says a behaviour appears above "Where this can go" only after it has run on a real ticket. The spec's Decisions chose to change "How a ticket moves" in this ticket, and Operator step 2 confirms it on the first real build. The status-header date was already 2026-10-03, today, so bumping it left the text unchanged.
- **I ran every acceptance command before the edit**, as this run's prompt (the old step 2) required. That includes the REGRESSION ones. The new step 2 applies from the next run after the runtime upgrade.
- **The first `fx` run used `python3` from the PATH.** `bin/factory` falls back to it because the worktree had no `.venv` until `uv run` created one. The later runs used the project venv, and the outputs were the same.

## Out-of-scope observations

- `factory/workflows/build.js` lines 3 and 7, the `meta` description and the Close phase detail, still say every build makes one parent-close verifier run. They are labels, not behaviour. I left them because part C does not name them.
- The README's "While that final run is in progress…" sentence still holds for the runs that happen. With a reused close, that step finishes at once.

## Responses to findings

None. This is the first round.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All seven acceptance commands match their THEN lines at the final head, both gates pass (check exit 0, 136 passed), and the five new tests failed before the `cli.py` change and pass after it. The `build.js` skip is the one part checked only by reading it.
ESCALATIONS: none

## Diff `924513ecb731b57f4396b602ff31a1169150b3e3...d45f0601ba30199152da28af556513dd2fc0caf0`

diff --git a/README.md b/README.md
index c4cfdf4..9a44899 100644
--- a/README.md
+++ b/README.md
@@ -92,7 +92,10 @@ to merge in a `main` that moved; or park for a human. A merge is a local `--no-f
 judged commit into the integration branch, one merge at a time.
 
 When every sub-ticket has merged, one more verifier run checks the whole spec against the
-integration branch. On success the harness folds the spec into current truth and closes the
+integration branch. That final run is skipped when the spec had one sub-ticket, that sub-ticket
+was told to check every acceptance scenario of the spec (a command with its expected output), and
+the integration branch has not moved since it merged: the sub-ticket's verifier already checked
+the same code against the same starting point. On success the harness folds the spec into current truth and closes the
 ticket. If the target has no spec store yet (no `openspec/` tree), the fold is refused and the
 ticket parks; the human then closes it as applied with `resolve --close`, and current truth is
 not updated. While that final run is in progress the ticket's record does not list it as in flight, so
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index bf9c79c..d811724 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -282,7 +282,7 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 
 `build.js` (`args: {ticket}`), run after `factory approve-spec`:
 1. `phase('Plan')` (only when the parent is `ready-for-planner`; a re-run starts from the stored state, so a `--ruling` on a planner ESCALATE re-runs the planner with the ruling in its input): `runRole('planner')` with the pinned spec; `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket (`depends_on`, `parallel_safe`); `ESCALATE` → park, return.
-2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79); `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When the parent reaches `ready-for-parent-verify` (G): `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
+2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79); `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When the parent reaches `ready-for-parent-verify` (G), or a re-run finds it there: clerk `factory ticket parent-check PARENT` first. Its `reuse` field names a run when the parent has exactly one sub-ticket and it is merged, `main` is still at that sub-ticket's merge commit, the results row for the merged head is VERIFIED from a run whose base is the parent's `parent_base`, and the sub-ticket's text names every scenario of the pinned spec; that run stands for the parent-close run: no verifier run starts, the build goes to `factory archive PARENT` with that run id as the park outputs, and the close records it as `verified_by` (`null` → as follows). Otherwise `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
 3. `buildOne(st)`: loop:
    - `runRole('implementer', st, …, {isolation: 'worktree'})`; the implementer's worktree is created on current `main` at dispatch (doc §Routing table, Planner row), input = sub-ticket, pinned parent spec, AGENTS.md (+ round ≥ 2: both checker outputs, CI result, or the human ruling); `BLOCKED` → park, return; `READY-FOR-REVIEW` → clerk `factory ticket head ST` (from `git ls-remote`), `transition --to checks-in-flight --round pr:init`.
    - **Checkers in parallel, fresh contexts** (`parallel` is the join barrier, E7): `[rev, ver] = await parallel([() => runRole('reviewer', …), () => runRole('verifier', …)])` with input = `git diff main...head`, PR description, sub-ticket, parent spec (+ round ≥ 2: both prior outputs, the implementer's Responses); the clerk makes each a fresh checkout `~/factory/runs/<run_id>/wt` of the head; each result → clerk `results record` (stale rule applies; the `Commit:` line must equal the current head).
diff --git a/docs/changelog.md b/docs/changelog.md
index 6fe5e03..b07d351 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -46,5 +46,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 42. After issue #19 (2026-10-02): the harness lives in this repo and each target repo carries a `.factory/` instance: `instance.yaml`, `context.md` (the role-context block, prepended by the composer), `harness.lock` (the accepted harness revision; any other revision is refused until a human accepts it) and the store. The harness finds the instance by walking up from the working directory, and its own code is a protected path in the repo that holds it. The design doc splits into `docs/design.md` and this changelog, the prompt copies move to `docs/prompts/`, and the working documents for building the factory move to `dev/`.
 43. After issue #23 (2026-10-03), where the operator's review of the overview draft found the same three failures the factory's own outputs show (an unglossed term, a parenthetical holding a second idea, a page that assumed its reader knew the project): a one-page writing standard, `docs/writing.md`, holds eight rules an agent can check in its own output, each with a before-and-after example from the factory's own writing. The shared preamble's OUTPUT block gains one line: every section a person reads follows the standard at `{writing standard}`, a placeholder the harness fills when a run starts with the path of `docs/writing.md` in the harness checkout that runs it; the role-context block also names who reads what the roles write. Critic rubric 6 widens from the Problem section to every human-facing section of a spec (Problem, Evidence, Open questions, Decisions, Operator steps), still BLOCKING on a Problem that does not say what is wrong and for whom or a first paragraph with an unglossed term specific to this system; other departures from the standard are SHOULD-FIX or NIT. The code reviewer gains check 8, whether the operator could read the PR description's What changed and Known gaps, which is SHOULD-FIX, never BLOCKING. The briefing template gains a line naming the reader of the repo's documents.
 44. After issue #20 (2026-10-03), because nothing stopped a coding agent from building more than its ticket needs: a coding standard, `docs/coding.md`, the twin of the writing standard. It opens with a precedence rule (a target repository's own instructions win where they disagree with it) and holds five rules an agent can check in its own output, each with a `Check:` line, the code-design principle it applies and a before-and-after example: reuse before writing, taking the first rung of a check order that holds; grep every caller and fix a shared function once; mark each deliberate shortcut with a `factory:` comment naming its limit and upgrade trigger; tag each over-building review finding; and one name per concept from spec to code. The review tags are `reuse:` (BLOCKING) and `stdlib:`, `native:`, `yagni:` and `delete:` (SHOULD-FIX), and a review pass ends with `net: -N lines possible` or `Lean already.` The implementer's step 4 gains a line pointing to the standard at `{coding standard}`, and the code reviewer's check 7 is replaced by one: its old "Maintainability, only where it will cause real problems" text is gone. The harness fills `{coding standard}` when a run starts, with the path of `docs/coding.md` in the harness checkout that runs it, through the same helper that fills `{writing standard}`, now applied to the role prompt as well as the preamble. The spec writer gains a rule to cut any part the ticket's intent does not need, naming it under Out of scope, and critic rubric 3 makes such a part a finding. The retro's input names the marker ledger, one row per `factory:` comment in the code on the integration branch; this is design only, and the harness code that builds the ledger waits for the ticket that builds the retro. The check order and the tag vocabulary are adapted from ponytail (DietrichGebert/ponytail, MIT).
+45. After issue #31 (2026-10-03), from the T-0013 to T-0015 build timings, where a parent-close run took 13 to 23% of each build and only two of about six test-suite runs per build could change a verdict: a REGRESSION acceptance check runs once, after the change. The implementer runs only the NEW checks before editing, and runs a REGRESSION check on its base only when it fails after the change; the verifier runs a REGRESSION check on base only when it fails on the PR. One gate run per commit: an acceptance check that already ran a gate command exactly as written on the same commit is that gate's run, for the implementer and the verifier. A parent with one sub-ticket closes on that sub-ticket's VERIFIED run when `main` has not moved since it merged, the run checked the merged head against the parent's recorded base, and the sub-ticket's text names every scenario of the parent's pinned spec; the run stands for the parent-close run, `ticket parent-check` reports it as `reuse`, and the close records it as `verified_by`. Every other parent still gets its own parent-close run, and every refusal is kept: a NEW check that does not fail first is a SPEC-DEFECT, a failing REGRESSION check fails the branch, and a gate failure is FAILED. The requested path-scoped gate skip was cut: a correct path list for this repository covers `docs/**`, which would have skipped no suite run in those builds.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 2575e23..ac7d892 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -79,7 +79,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | `tasks.md` | The sub-tickets and coverage map | Planner |
 | `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |
 
-`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth and `decisions.md`. The spec writer and the critic receive every current-truth spec with their input (routing table).
+`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth and `decisions.md`. The spec writer and the critic receive every current-truth spec with their input (routing table).
 
 **Routing table.** The dispatcher (piece 2) is this table and nothing else. Each row: a STATUS a role emits, what runs next, and what it receives. "Receives" adds to the INPUT the role prompt already declares. Both follow the role-context block (above).
 
@@ -123,7 +123,7 @@ Rules the table relies on:
 | Reviewer | ESCALATE | Human queue | Output |
 | Verifier | SPEC-DEFECT | Human queue | Verifier output |
 | Merge gate | Head does not contain current main | Implementer (same round, conflict run): merge main into the branch, or rebase where {force-push allowed} | Conflict output; the new head re-runs CI and both checkers |
-| Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main + piece-8 approvals | Merge; then dispatch sub-tickets that depended on this one. When all sub-tickets have merged, one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label): VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue | Parent-close run: pinned parent spec; head = current main; base = the main SHA recorded before the parent's first sub-ticket merged; `{gate commands}` |
+| Merge gate | CI green + APPROVE + VERIFIED on current head + head contains main + piece-8 approvals | Merge; then dispatch sub-tickets that depended on this one. When all sub-tickets have merged, one verifier run on main against the parent's full Acceptance list (every scenario of its pinned delta, with its `verification.md` label). When the parent has one sub-ticket, `main` has not moved since that sub-ticket merged, the sub-ticket's text names every scenario of the parent's pinned delta, and its VERIFIED run checked the merged head against the parent's recorded base, that run stands for the parent-close run and no new run starts. VERIFIED archives the change (Spec store), then closes the parent; FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue | Parent-close run: pinned parent spec; head = current main; base = the main SHA recorded before the parent's first sub-ticket merged; `{gate commands}` |
 | Weekly audit done, or on demand | — | Retro | Full outputs behind every outcome signal since the last retro (piece 10), current instruction files, every proposal still under evaluation with its metric, and per-role run and outcome counts, broken down by model, for the period and for each prior proposal's window, and the marker ledger: one row per `factory:` comment in the code on the integration branch, with file:line, limit and upgrade trigger, flagged `no-trigger` where it names none, composed by the harness when the retro runs |
 | Retro | PROPOSED | Guardrail-changes gate (human); on approval, the no-sub-ticket merge row | PR |
 | Retro | NO-CHANGES | Log only | — |
@@ -489,14 +489,20 @@ ROLE: Implementer. You complete exactly one sub-ticket and open a PR.
 
 PROCESS
 1. Read the sub-ticket, its parent, and AGENTS.md.
-2. Run the acceptance commands first. NEW criteria should fail as
-   described; REGRESSION criteria should pass. If any behaves otherwise,
-   stop and escalate: the spec doesn't match reality.
+2. Run the NEW acceptance commands first. They should fail as
+   described. If one behaves otherwise, stop and escalate: the spec
+   doesn't match reality. REGRESSION commands passed on main when the
+   spec was written, so they run once, after your change (step 5).
 3. Write or extend tests that capture the intended behavior. Watch them
    fail.
 4. Make the smallest change that makes them pass for the right reason.
    Follow the coding standard at {coding standard}.
-5. Run the full local gates: {gate commands}.
+5. Run every acceptance command, then the full local gates:
+   {gate commands}. A command that already ran a gate command exactly
+   as written on this commit is that gate's run; don't repeat it. A
+   REGRESSION command that fails here: run it on the base you branched
+   from. If it fails there too, the spec doesn't match reality; stop
+   and escalate.
 6. Open a PR using the format below. On a fix round: check out the
    existing branch, push fix commits to it, and replace the PR
    description, including Responses to findings. On a conflict run:
@@ -525,7 +531,7 @@ RULES
 PR DESCRIPTION
 Sub-ticket: <link>
 What changed: per lettered part
-Acceptance results: each command + actual output (before and after)
+Acceptance results: each command + actual output (NEW: before and after; REGRESSION: after, and base if it failed)
 Tests added/changed: list, and why each change was needed
 Known gaps and uncertainties:
 Out-of-scope observations:
@@ -604,13 +610,16 @@ PROCESS
    branch, or main for a parent-close run.
 2. Run every acceptance command from the sub-ticket exactly as written.
    Record the actual output.
-3. Run the same commands on the base you were given (the base branch,
-   or for a parent close the main SHA before the parent's first merge). NEW criteria should fail
-   there and pass on the PR; REGRESSION criteria pass on both. A NEW
-   criterion that passes on both, or fails on base for a different
-   reason than the spec states (e.g. its test doesn't exist yet), is a
-   SPEC-DEFECT, not a pass or a fail.
+3. Run the NEW commands on the base you were given (the base branch,
+   or for a parent close the main SHA before the parent's first merge).
+   NEW criteria should fail there and pass on the PR. A NEW criterion
+   that passes on both, or fails on base for a different reason than
+   the spec states (e.g. its test doesn't exist yet), is a SPEC-DEFECT,
+   not a pass or a fail. Run a REGRESSION command on base only when it
+   fails on the PR, and report both results.
 4. Run the full gate suite: {gate commands}. A gate failure is FAILED.
+   A step 2 command that ran a gate command exactly as written on the
+   PR is that gate's run; don't repeat it.
 5. Probe: try 2-3 inputs near the tested ones (boundaries, empty, large,
    malformed). You're checking whether it works, or only works for the
    tested cases.
@@ -628,7 +637,7 @@ RULES
 
 OUTPUT
 Commit: <head SHA you verified>
-Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
+Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL (base: not run, for a REGRESSION that passed on the PR)
 Gate suite: PASS/FAIL, with failing output
 Probes: input → result → OK / CONCERN
 STATUS: VERIFIED | FAILED | SPEC-DEFECT (precedence: SPEC-DEFECT > FAILED)
diff --git a/docs/prompts/05-implementer.md b/docs/prompts/05-implementer.md
index efe4204..fcf1e89 100644
--- a/docs/prompts/05-implementer.md
+++ b/docs/prompts/05-implementer.md
@@ -2,14 +2,20 @@ ROLE: Implementer. You complete exactly one sub-ticket and open a PR.
 
 PROCESS
 1. Read the sub-ticket, its parent, and AGENTS.md.
-2. Run the acceptance commands first. NEW criteria should fail as
-   described; REGRESSION criteria should pass. If any behaves otherwise,
-   stop and escalate: the spec doesn't match reality.
+2. Run the NEW acceptance commands first. They should fail as
+   described. If one behaves otherwise, stop and escalate: the spec
+   doesn't match reality. REGRESSION commands passed on main when the
+   spec was written, so they run once, after your change (step 5).
 3. Write or extend tests that capture the intended behavior. Watch them
    fail.
 4. Make the smallest change that makes them pass for the right reason.
    Follow the coding standard at {coding standard}.
-5. Run the full local gates: {gate commands}.
+5. Run every acceptance command, then the full local gates:
+   {gate commands}. A command that already ran a gate command exactly
+   as written on this commit is that gate's run; don't repeat it. A
+   REGRESSION command that fails here: run it on the base you branched
+   from. If it fails there too, the spec doesn't match reality; stop
+   and escalate.
 6. Open a PR using the format below. On a fix round: check out the
    existing branch, push fix commits to it, and replace the PR
    description, including Responses to findings. On a conflict run:
@@ -38,7 +44,7 @@ RULES
 PR DESCRIPTION
 Sub-ticket: <link>
 What changed: per lettered part
-Acceptance results: each command + actual output (before and after)
+Acceptance results: each command + actual output (NEW: before and after; REGRESSION: after, and base if it failed)
 Tests added/changed: list, and why each change was needed
 Known gaps and uncertainties:
 Out-of-scope observations:
diff --git a/docs/prompts/07-verifier.md b/docs/prompts/07-verifier.md
index 4ec580c..4ef112c 100644
--- a/docs/prompts/07-verifier.md
+++ b/docs/prompts/07-verifier.md
@@ -6,13 +6,16 @@ PROCESS
    branch, or main for a parent-close run.
 2. Run every acceptance command from the sub-ticket exactly as written.
    Record the actual output.
-3. Run the same commands on the base you were given (the base branch,
-   or for a parent close the main SHA before the parent's first merge). NEW criteria should fail
-   there and pass on the PR; REGRESSION criteria pass on both. A NEW
-   criterion that passes on both, or fails on base for a different
-   reason than the spec states (e.g. its test doesn't exist yet), is a
-   SPEC-DEFECT, not a pass or a fail.
+3. Run the NEW commands on the base you were given (the base branch,
+   or for a parent close the main SHA before the parent's first merge).
+   NEW criteria should fail there and pass on the PR. A NEW criterion
+   that passes on both, or fails on base for a different reason than
+   the spec states (e.g. its test doesn't exist yet), is a SPEC-DEFECT,
+   not a pass or a fail. Run a REGRESSION command on base only when it
+   fails on the PR, and report both results.
 4. Run the full gate suite: {gate commands}. A gate failure is FAILED.
+   A step 2 command that ran a gate command exactly as written on the
+   PR is that gate's run; don't repeat it.
 5. Probe: try 2-3 inputs near the tested ones (boundaries, empty, large,
    malformed). You're checking whether it works, or only works for the
    tested cases.
@@ -30,7 +33,7 @@ RULES
 
 OUTPUT
 Commit: <head SHA you verified>
-Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
+Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL (base: not run, for a REGRESSION that passed on the PR)
 Gate suite: PASS/FAIL, with failing output
 Probes: input → result → OK / CONCERN
 STATUS: VERIFIED | FAILED | SPEC-DEFECT (precedence: SPEC-DEFECT > FAILED)
diff --git a/factory/cli.py b/factory/cli.py
index d8bfade..2b2bae0 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -150,10 +150,12 @@ def ticket_transition(a, root, cfg):
     t = store.load_ticket(root, a.id)
     frm = t["status"]
     _check_edge(cfg, frm, a.to)
+    verified_by = None
     if a.to == "closed" and store.subtickets_of(root, t["id"]):
         # A parent closes through its parent-close run (then archive). A human who wants it closed
         # without one says so with `resolve --close`.
-        if not _parent_close_verified(root, cfg, t):
+        verified_by = _parent_close_verified(root, cfg, t)
+        if not verified_by:
             raise Refused(f"{t['id']} has sub-tickets: it closes after a VERIFIED parent-close run (or `resolve {t['id']} --close`)")
         if specstore.is_active(root) and specstore.change_dir(root, t["id"]).exists():
             raise Refused(f"{t['id']} is verified but not archived: run `archive {t['id']}` first")
@@ -161,7 +163,8 @@ def ticket_transition(a, root, cfg):
     t["status"] = a.to
     if a.to != "parked":
         t["parked"] = None
-    t["history"].append({"ts": store.now(), "from": frm, "to": a.to, "by": a.by, "round": dict(t["round"])})
+    t["history"].append({"ts": store.now(), "from": frm, "to": a.to, "by": a.by, "round": dict(t["round"]),
+                         **({"verified_by": verified_by} if verified_by else {})})
     store.save_ticket(root, t)
     store.log_event(root, "ticket.transition", ticket=t["id"], **{"from": frm, "to": a.to, "by": a.by, "round": t["round"]})
     out({"ok": True, "id": t["id"], "state": t["status"], "round": t["round"]})
@@ -595,8 +598,9 @@ def ticket_parent_check(a, root, cfg):
         parent["history"].append({"ts": store.now(), "from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
         store.save_ticket(root, parent)
         store.log_event(root, "ticket.transition", ticket=parent["id"], **{"from": frm, "to": "ready-for-parent-verify", "by": "parent-check"})
+    reuse = _reused_subticket_run(root, cfg, parent) if parent["status"] == "ready-for-parent-verify" else None
     out({"ok": True, "id": parent["id"], "state": parent["status"],
-         "subtickets": {s["id"]: s["status"] for s in subs}})
+         "subtickets": {s["id"]: s["status"] for s in subs}, "reuse": reuse})
 
 
 # ----- human surface (K-lite) -----------------------------------------------------
@@ -857,12 +861,45 @@ def _verifier_rows(root: Path, tid: str) -> list[str]:
     return rows
 
 
-def _parent_close_verified(root: Path, cfg: dict, t: dict) -> bool:
-    """Every sub-ticket merged, and a finished verifier run on the parent itself said VERIFIED on a
-    head that contains every one of those merges (a run from before the last merge does not count)."""
+def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
+    """The run id of a sub-ticket's VERIFIED verifier run that stands for the parent-close run
+    (design doc routing table, Merge gate row), or None when the parent needs its own run."""
+    # factory: one sub-ticket only, and scenario coverage is read from scenario names occurring in
+    # the sub-ticket's text; widen only when the store can check a coverage map per sub-ticket.
+    subs = store.subtickets_of(root, t["id"])
+    if len(subs) != 1 or not t.get("parent_base"):
+        return None
+    s = subs[0]
+    after = (s.get("merge") or {}).get("main_after")
+    if s["status"] != "merged" or not after or not s.get("head"):
+        return None
+    repo = gitops.repo_root(cfg)
+    if gitops.rev(repo, gitops.integration_branch(cfg, repo)) != after:
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
+    """The run that verifies the parent: every sub-ticket merged, and a finished verifier run on the
+    parent itself said VERIFIED on a head that contains every one of those merges (a run from before
+    the last merge does not count); else a sub-ticket's run that stands for it; else None."""
     subs = store.subtickets_of(root, t["id"])
     if any(s["status"] != "merged" for s in subs):
-        return False
+        return None
     repo = gitops.repo_root(cfg)
     runs = root / "runs"
     for d in sorted(runs.iterdir()) if runs.exists() else []:
@@ -873,8 +910,8 @@ def _parent_close_verified(root: Path, cfg: dict, t: dict) -> bool:
         if m.get("ticket") != t["id"] or m.get("role") != "verifier" or m.get("status") != "VERIFIED" or not m.get("head"):
             continue
         if all(gitops.head_contains(repo, m["head"], s["merge"]["main_after"]) for s in subs if s["merge"].get("main_after")):
-            return True
-    return False
+            return d.name
+    return _reused_subticket_run(root, cfg, t)
 
 
 def archive_cmd(a, root, cfg):
diff --git a/factory/prompts/implementer.md b/factory/prompts/implementer.md
index 2d1d573..70d76e8 100644
--- a/factory/prompts/implementer.md
+++ b/factory/prompts/implementer.md
@@ -2,15 +2,21 @@ ROLE: Implementer. You complete exactly one sub-ticket and open a PR.
 
 PROCESS
 1. Read the sub-ticket, its parent, and AGENTS.md.
-2. Run the acceptance commands first. NEW criteria should fail as
-   described; REGRESSION criteria should pass. If any behaves otherwise,
-   stop and escalate: the spec doesn't match reality.
+2. Run the NEW acceptance commands first. They should fail as
+   described. If one behaves otherwise, stop and escalate: the spec
+   doesn't match reality. REGRESSION commands passed on main when the
+   spec was written, so they run once, after your change (step 5).
 3. Write or extend tests that capture the intended behavior. Watch them
    fail.
 4. Make the smallest change that makes them pass for the right reason.
    Follow the coding standard at {coding standard}.
-5. Run the full local gates: the gate commands listed in your input
-   under "Where you work", each exactly as written.
+5. Run every acceptance command, then the full local gates:
+   the gate commands listed in your input under "Where you work", each
+   exactly as written. A command that already ran a gate command exactly
+   as written on this commit is that gate's run; don't repeat it. A
+   REGRESSION command that fails here: run it on the base you branched
+   from. If it fails there too, the spec doesn't match reality; stop
+   and escalate.
 6. Open a PR using the format below. On a fix round: check out the
    existing branch, push fix commits to it, and replace the PR
    description, including Responses to findings. On a conflict run:
@@ -39,7 +45,7 @@ RULES
 PR DESCRIPTION
 Sub-ticket: <link>
 What changed: per lettered part
-Acceptance results: each command + actual output (before and after)
+Acceptance results: each command + actual output (NEW: before and after; REGRESSION: after, and base if it failed)
 Tests added/changed: list, and why each change was needed
 Known gaps and uncertainties:
 Out-of-scope observations:
diff --git a/factory/prompts/verifier.md b/factory/prompts/verifier.md
index 60d5e5a..305f813 100644
--- a/factory/prompts/verifier.md
+++ b/factory/prompts/verifier.md
@@ -6,15 +6,17 @@ PROCESS
    branch, or main for a parent-close run.
 2. Run every acceptance command from the sub-ticket exactly as written.
    Record the actual output.
-3. Run the same commands on the base you were given (the base branch,
-   or for a parent close the main SHA before the parent's first merge). NEW criteria should fail
-   there and pass on the PR; REGRESSION criteria pass on both. A NEW
-   criterion that passes on both, or fails on base for a different
-   reason than the spec states (e.g. its test doesn't exist yet), is a
-   SPEC-DEFECT, not a pass or a fail.
+3. Run the NEW commands on the base you were given (the base branch,
+   or for a parent close the main SHA before the parent's first merge).
+   NEW criteria should fail there and pass on the PR. A NEW criterion
+   that passes on both, or fails on base for a different reason than
+   the spec states (e.g. its test doesn't exist yet), is a SPEC-DEFECT,
+   not a pass or a fail. Run a REGRESSION command on base only when it
+   fails on the PR, and report both results.
 4. Run the full gate suite: the gate commands listed in your input under
    "Where you work", each exactly as written. A gate failure (any command
-   exiting non-zero) is FAILED.
+   exiting non-zero) is FAILED. A step 2 command that ran a gate command
+   exactly as written on the PR is that gate's run; don't repeat it.
 5. Probe: try 2-3 inputs near the tested ones (boundaries, empty, large,
    malformed). You're checking whether it works, or only works for the
    tested cases.
@@ -32,7 +34,7 @@ RULES
 
 OUTPUT
 Commit: <head SHA you verified>
-Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
+Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL (base: not run, for a REGRESSION that passed on the PR)
 Gate suite: PASS/FAIL, with failing output
 Probes: input → result → OK / CONCERN
 STATUS: VERIFIED | FAILED | SPEC-DEFECT (precedence: SPEC-DEFECT > FAILED)
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 39de0a7..e5a1529 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -217,11 +217,20 @@ if (state === 'planned') {
 // --- phase 3: Close (one verifier run on the integration branch against the parent spec)
 if (state === 'ready-for-parent-verify') {
   phase('Close')
-  const v = await runRole('verifier', TICKET, 'Close')
-  if (!v) return { ticket: TICKET, state: 'parked' }
-  if (v.status !== 'VERIFIED') { await park(TICKET, `${v.status} from parent-close verifier`, [v.runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
+  // Asked again here: a resumed build may arrive already in ready-for-parent-verify. `reuse` names a
+  // single sub-ticket's VERIFIED run that stands for the parent-close run (doc routing table, Merge gate row).
+  const pc = await clerk(`${BIN} ticket parent-check ${TICKET}`, 'Close', 'parent-check')
+  let runId = pc.ok && pc.reuse ? pc.reuse : null
+  if (runId) {
+    log(`${TICKET}: sub-ticket verifier run ${runId} stands for the parent-close run; no new verifier run`)
+  } else {
+    const v = await runRole('verifier', TICKET, 'Close')
+    if (!v) return { ticket: TICKET, state: 'parked' }
+    if (v.status !== 'VERIFIED') { await park(TICKET, `${v.status} from parent-close verifier`, [v.runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
+    runId = v.runId
+  }
   const arch = await clerk(`${BIN} archive ${TICKET}`, 'Close', 'archive')
-  if (!arch.ok) { await park(TICKET, `archive: ${arch.stderr || ''}`, [v.runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
+  if (!arch.ok) { await park(TICKET, `archive: ${arch.stderr || ''}`, [runId], 'Close'); return { ticket: TICKET, state: 'parked' } }
   await transition(TICKET, 'closed', null, 'Close')
   return { ticket: TICKET, state: 'closed', archived_to: arch.archived_to }
 }
diff --git a/tests/factory/test_parent_close_reuse.py b/tests/factory/test_parent_close_reuse.py
new file mode 100644
index 0000000..178789b
--- /dev/null
+++ b/tests/factory/test_parent_close_reuse.py
@@ -0,0 +1,101 @@
+"""A parent with one sub-ticket closes on that sub-ticket's VERIFIED run (T-0016 part C).
+
+The rule (docs/design.md routing table, Merge gate row): when the parent has exactly one sub-ticket,
+the integration branch has not moved since it merged, the sub-ticket's text names every scenario of
+the parent's pinned spec, and its VERIFIED run checked the merged head against the parent's recorded
+base, that run stands for the parent-close run. In every other case the parent still needs its own.
+Driven through the store CLI with the Shepherd fixture, as build.js does in phase 3.
+"""
+from __future__ import annotations
+
+import yaml
+
+from .test_shepherd import built_to_implementer
+
+TWO_COVERING = ("T-0001.1 / First\n  Depends on: none\n  Parallel-safe: yes\n  Acceptance: asked once\n\n"
+                "T-0001.2 / Second\n  Depends on: T-0001.1\n  Parallel-safe: yes\n  Acceptance: asked once\n\n"
+                "Coverage map: asked once → T-0001.1, T-0001.2\n")
+UNCOVERED = ("T-0001.1 / Do the thing\n  Depends on: none\n  Parallel-safe: yes\n  Acceptance: the check\n\n"
+             "Coverage map: the check → T-0001.1\n")
+
+
+def _parent_verifier_runs(f, tid: str) -> list[str]:
+    return [p.parent.name for p in (f.store / "runs").glob("*-verifier/meta.yaml")
+            if yaml.safe_load(p.read_text())["ticket"] == tid]
+
+
+def _build(f, st: str, file: str = "thing.txt"):
+    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md", file=file)
+    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
+    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md")
+    assert f.state(st) == "merged"
+    return ver
+
+
+def _assert_parent_close_still_required(f, tid: str) -> None:
+    pc = f.ok("ticket", "parent-check", tid)
+    assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] is None
+    cp = f.cli("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
+    assert cp.returncode == 2 and "closes after a VERIFIED parent-close run" in cp.stderr
+    cp = f.cli("archive", tid)
+    assert cp.returncode == 2 and "no VERIFIED parent-close verifier run" in cp.stderr
+    assert f.state(tid) == "ready-for-parent-verify" and _parent_verifier_runs(f, tid) == []
+
+
+def test_a_single_sub_ticket_parent_closes_and_archives_on_its_verified_run(tmp_path):
+    f, tid, (st,) = built_to_implementer(tmp_path)
+    ver = _build(f, st)
+    pc = f.ok("ticket", "parent-check", tid)
+    assert pc["state"] == "ready-for-parent-verify" and pc["reuse"] == ver.run_id
+    # build.js phase 3 with `reuse` set: no verifier run, straight to archive, then the close
+    f.ok("archive", tid)
+    f.ok("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
+    t = f.ticket(tid)
+    assert t["status"] == "closed" and t["history"][-1]["verified_by"] == ver.run_id
+    assert _parent_verifier_runs(f, tid) == []
+    truth = (f.store / "openspec" / "specs" / "thing" / "spec.md").read_text()
+    assert "#### Scenario: asked once" in truth
+
+
+def test_a_parent_close_run_is_still_required_when_main_moved_after_the_merge(tmp_path):
+    f, tid, (st,) = built_to_implementer(tmp_path)
+    _build(f, st)
+    f.git("commit", "-q", "--allow-empty", "-m", "another change on main")
+    _assert_parent_close_still_required(f, tid)
+
+
+def test_a_parent_close_run_is_still_required_with_two_sub_tickets(tmp_path):
+    f, tid, (a, b) = built_to_implementer(tmp_path, TWO_COVERING)
+    _build(f, a, "a.txt")
+    _build(f, b, "b.txt")
+    assert f.repo_rev("main") == f.ticket(b)["merge"]["main_after"]  # main has not moved since the last merge
+    _assert_parent_close_still_required(f, tid)
+
+
+def test_a_parent_close_run_is_still_required_when_the_sub_ticket_misses_a_scenario(tmp_path):
+    f, tid, (st,) = built_to_implementer(tmp_path, UNCOVERED)
+    assert "asked once" not in (f.store / "specs" / st / "subticket.md").read_text()
+    _build(f, st)
+    _assert_parent_close_still_required(f, tid)
+
+
+def test_a_parent_close_run_is_still_required_when_the_verified_run_had_another_base(tmp_path):
+    """main moves to a commit the branch already contains after the verifier started: the merge goes
+    through, but the VERIFIED run checked the head against a base older than the parent's."""
+    f, tid, (st,) = built_to_implementer(tmp_path)
+    f.dispatch("implementer", st, stub="accept-approve/implementer-1.md")
+    first = f.ticket(st)["head"]
+    wt = f.store / "worktrees" / st
+    (wt / "more.txt").write_text("more\n")
+    f.git("add", "more.txt", cwd=wt)
+    f.git("commit", "-q", "-m", "more", cwd=wt)
+    f.ok("ticket", "head", st)
+    f.dispatch("reviewer", st, stub="accept-approve/reviewer-1.md")
+    ver = f.dispatch("verifier", st, stub="accept-approve/verifier-1.md", route=False)
+    f.git("merge", "-q", "--ff-only", first)
+    f.route("verifier", st, ver.run_id, ver.status)
+    assert f.state(st) == "merged"
+    meta = yaml.safe_load((f.store / "runs" / ver.run_id / "meta.yaml").read_text())
+    assert meta["status"] == "VERIFIED" and meta["head"] == f.ticket(st)["head"]
+    assert meta["base"] != f.ticket(tid)["parent_base"] == first
+    _assert_parent_close_still_required(f, tid)
diff --git a/tests/factory/test_shepherd.py b/tests/factory/test_shepherd.py
index 7c128d3..921dd0b 100644
--- a/tests/factory/test_shepherd.py
+++ b/tests/factory/test_shepherd.py
@@ -221,6 +221,7 @@ def test_the_planned_ticket_is_built_checked_merged_and_archived(tmp_path):
     assert (f.repo / "thing.txt").read_text() == "the thing\n"  # main is checked out here, so the merge lands in the working tree
     assert f.git("show", "main:thing.txt").strip() == "the thing"
     assert f.ticket(tid)["parent_base"] == f.ticket(st)["merge"]["base_before"]
+    f.git("commit", "-q", "--allow-empty", "-m", "another change on main")
 
     # | When all sub-tickets have merged | one verifier run on main against the parent's full Acceptance list |
     assert f.parent_check(tid) == "ready-for-parent-verify"
@@ -483,6 +484,7 @@ def test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_r
     f.dispatch("implementer", st)
     f.dispatch("reviewer", st)
     f.dispatch("verifier", st)
+    f.git("commit", "-q", "--allow-empty", "-m", "another change on main")
     assert f.parent_check(tid) == "ready-for-parent-verify"
     cp = f.cli("ticket", "transition", tid, "--to", "closed", "--by", "workflow")
     assert cp.returncode == 2 and f.state(tid) == "ready-for-parent-verify"
