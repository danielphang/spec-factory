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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0142-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0142-verifier/wt` (branch `None`, base `924513ecb731b57f4396b602ff31a1169150b3e3`, head `3bf76422a3e58e1b44c1073213af737842159e2b`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Parent spec (v1, pinned): verify every scenario on main

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
