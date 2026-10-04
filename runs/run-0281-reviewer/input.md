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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0281-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0281-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0281-reviewer/wt` (branch `factory/T-0022.1`, base `c2750bf9c18ca6e37e4cfec439a0a9ef42f318d6`, head `771ee0ec14ec755265f969c709ee3a4099d5160d`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0022.1

## ST-1 / Sibling tests: per-sub-ticket labels, the harness check, prompts and documents
Depends on: none
Parallel-safe: yes

Parent: T-0022 (issue #40), the approved spec v1 pinned in the store under `specs/T-0022/`. Read it for context. Do NOT implement parts outside this sub-ticket.

  Scope: all of the parent's parts.
    - A: planner block in `docs/design.md` §4, `docs/prompts/04-planner.md` and `factory/prompts/planner.md`, kept byte-identical in that block.
    - B.1 to B.5:
      - `PLAN_FIELDS` and `sibling_tests` in `factory/subtickets.py`.
      - `first_added` and `is_ancestor` in `factory/gitops.py`.
      - `_check_sibling_tests` in `run_start` in `factory/cli.py`, placed before `tripwire.baseline`.
      - The `BLOCKED ` refusal park in `runRole` in `factory/workflows/build.js`.
      - The new `tests/factory/test_sibling_tests.py`.
    - C: the spec writer RULES bullet and the critic rubric 1 lines, in all three copies of each.
    - D: the preamble guardrail sentence and the code reviewer's test-integrity line, in all three copies of each.
    - E.1 to E.6:
      - `docs/design.md`: piece 8, the Spec approval row, and the `**Tests a sibling added.**` paragraph.
      - `docs/changelog.md`: the "After issue #40 (2026-10-04)" entry.
      - `dev/build-harness.spec.md`: lines 203, 245 and 275.
      - `README.md`: the Built bullet and the Unstick row.
  Acceptance (WHEN command and THEN result exactly as in the parent's spec files; label is the verification.md label, re-checked against this sub-ticket's base `c2750bf` above):
    - "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored". WHEN: the parent's GIVEN block, run once, then its `(E=tests/test_interim.py; . …t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 …)` command. THEN `exit=0 ready-for-implementer runs=1`. REGRESSION.
    - "A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts". WHEN: the `for E in tests/test_old.py tests/test_operator.py tests/test_never.py` command. THEN three lines, each `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`. NEW.
    - "The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back". WHEN: the `node …t0022-build.mjs` then `resolve --ruling` command. THEN `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`. NEW.
    - "Every planner copy labels per sub-ticket and lists sibling tests". THEN three lines of `own=1 sibling=1 interim=1 copied=0`, then `verbatim`. NEW.
    - "Every spec writer and critic copy carries the decision-overturns rule". THEN `design: writer=1 critic=1`, `docs/prompts: writer=1 critic=1`, `factory/prompts: writer=1 critic=1`. NEW.
    - "Every preamble and reviewer copy accepts a sibling entry". THEN `design: guard=1 review=1`, `docs/prompts: guard=1 review=1`, `factory/prompts: guard=1 review=1`. NEW.
    - "Planner, spec writer and critic runs get the new rules in their system prompts". THEN `planner own=1 sibling=1 guard=1 writer=1 critic=1`. NEW.
    - "The design doc and build spec describe the check". THEN `piece8=1 gate=1 stale=0 check=1 build=1`. NEW.
    - "The changelog records issue 40's change without a numbering gap". THEN `CONTIGUOUS`, then `5`. NEW.
    - "README describes the sibling tests check and its ruling". THEN `built=1 ruling=1`. NEW.
    - "The sibling-tests change adds no whitespace errors". WHEN `(git diff --check main...HEAD; echo "exit=$?")`. THEN only `exit=0`. REGRESSION.
    - The gate suite is the parent's gate, not a scenario. Run `uv run --frozen pytest -q -p no:cacheprovider tests/factory` with pytest's temporary directory under `/tmp`, as current truth's harness-suite scenario sets it. Every test must pass, including the new `tests/factory/test_sibling_tests.py`. REGRESSION for the existing tests. The new file's cases are NEW:
      - each build-dispatch scenario case;
      - an unmerged sibling (no `parent_base`) refuses;
      - a file that was added, deleted and re-added counts by its first add;
      - `sibling_tests` ignores a mention in the Parallel-safe line, as in the stored sub-ticket T-0002.6.
  Tests to change: none. This is the parent's list. The new test file is added, not changed.
  Protected paths: the parent's full Risk list.
    - Harness: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/{preamble,planner,spec_writer,critic,reviewer}.md`.
    - Generated: `docs/prompts/{00-preamble,02-spec-writer,03-spec-critic,04-planner,06-code-reviewer}.md`, each re-copied from its design-doc block.
  Out of scope, as the parent's Out of scope lists it:
    - An implementer editing a test on its own judgement.
    - A merge-gate comparison of changed tests with "Tests to change".
    - Any harness check of NEW and REGRESSION labels.
    - Any harness read of "Interim tests".
    - `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml` and `uv.lock`.
    - Any write to a store record or to `~/dev/nanobot-upstream`.
    - The parent's Operator steps: the re-plan and re-spec of Nanobot's T-0002. These are for the operator after merge, not for this sub-ticket.

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The spec allows two seams: the prompt texts (A, C, D) and the harness check (B). I did not take that split, for three reasons:

- The new prompt texts in A and D tell every role that "the harness checks" a sibling entry. If the prompts merged before B, every role would be told about a check that does not run yet.
- The parent's changelog scenario needs one "After issue #40" entry that names both the prompt changes ("own base", "Decision", "critic rubric 1") and the harness check ("added by", "BLOCKED from harness"). Two PRs would have to share that one entry, and both would edit `docs/design.md` and `README.md`.
- The change is about 180 lines plus one new test file. Both seams touch protected paths, so each would need the operator's protected-path approval at merge. Splitting would make that approval happen twice and give review or rollback nothing in return.

I checked the labels against this sub-ticket's own base, today's `main` at `c2750bf`. The spec's prototype ran at `0b1abad`, and T-0025's merges have moved `main` since then. Every scenario in the table below was run from `~/dev/spec-factory` with a fresh HOME and `TMPDIR` set to this run's scratch directory. Each one printed exactly the "today" output that `verification.md` gives:

| Scenario | Output on `c2750bf` |
|---|---|
| merged-sibling REGRESSION | `exit=0 ready-for-implementer runs=1` |
| refused | three lines of `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer` |
| build park | `park T-0001.2: budget kill: implementer`, then `ruling=2 parked` |
| planner copies | `own=0 sibling=0 interim=0 copied=1` ×3, then `verbatim` |
| writer/critic | design `writer=0 critic=0` |
| preamble/reviewer | design `guard=0 review=0` |
| design/build spec | `piece8=0 gate=0 stale=1 check=0 build=0` |
| changelog | `CONTIGUOUS`, then `0` |
| README | `built=0 ruling=0` |

So every NEW label still fails on this base, and the parent's labels hold unchanged. The system-prompt scenario was not run: the role prompts it reads from are unchanged, and the planner-copy checks above already print `own=0` on them. The spec's anchors still hold on `c2750bf`:

- `factory/cli.py`: `run_start` at :198, `tripwire.baseline` at :212, the BLOCKED ruling at :748.
- `factory/workflows/build.js`: `runRole` at :66, with the `harness-bug: run start` park at :68.
- `docs/design.md`: piece 8 row at :46, Spec approval row at :146, the "Only the dispatcher writes a live store" paragraph at :56.
- `dev/build-harness.spec.md`: lines :203, :245 and :275.
- `README.md`: "Live-store fence" at :471, the Unstick row at :437.
- `factory/subtickets.py`: `FIELD_RE` and `_is_heading` exist.
- `tests/factory/test_sibling_tests.py` does not exist yet.

## Parent spec (v1, pinned)

=== proposal.md
## Problem

Work in the spec factory stops and waits for the operator more often than it needs to. Each stop costs a full agent run plus the operator's time, and three of the recurring causes could have been seen coming when the work was planned or specified. The spec factory turns a written request into merged code using a chain of AI agents. A **spec** is the approved design for one request.

Some background. One agent, the **planner**, splits a spec into **sub-tickets**: pieces that are built and merged one after another, each by its own **implementer** agent on its own branch. Sub-tickets of the same spec are **siblings**. A sub-ticket **parks** when the harness stops it until a human rules. The harness is the code that runs the agents and enforces their rules.

The three avoidable causes:

1. **Check labels copied from the whole spec.** Each acceptance check is labelled NEW or REGRESSION. A NEW check must fail before the change, so a pass shows the change did something. A REGRESSION check must pass both before and after. The planner copies each label from the whole spec. A sub-ticket, though, starts from the **integration branch** (the branch every sub-ticket merges into) with its earlier siblings already merged. So a check that an earlier sibling already made pass, or one that always passed, is still labelled NEW. The verifier, the agent that runs the checks, then reports a defective spec, and the sub-ticket parks.
2. **Tests that an earlier sibling added cannot be changed.** An earlier sibling ships tests that pin its interim behaviour. The next sibling changes that behaviour, as the plan intends, and those tests now fail. An implementer may change an existing test only if the spec's "Tests to change" list names it. A human approves that list at the **spec gate**, the sign-off before any code is written, and at that point the sibling's tests did not exist yet. So the implementer stops and reports itself blocked.
3. **A decision overturns a test that nobody listed.** A spec's Decisions section can change behaviour that an existing test pins. Nothing tells the spec writer to look for such tests. Nothing tells the critic, the agent that reviews the spec, to check that they are listed. The implementer then blocks on the test that was left off.

The operator has ruled on who may authorize the second case. The planner may list, for a sub-ticket, tests that an earlier sibling of the same spec added. The harness must check in git that each such test really came from a sibling's merge. If it did not, the sub-ticket parks, as it would today. A test that existed before the spec's first merge still needs the spec gate's list. This change makes that ruling work and fixes the other two causes in the agents' instructions.

## Evidence

All commands ran in `~/dev/spec-factory` at `0b1abad` (today's `main`), or in clones of it in this run's scratch directory.

**The planner copies the label and may list only the spec's tests.** Every copy of the planner prompt says the same:

```
docs/design.md:509:    it needs, labelled NEW or REGRESSION the same way
docs/design.md:510:  Tests to change: none | the subset of the parent's list this one touches
```

`docs/prompts/04-planner.md:33-34` and `factory/prompts/planner.md:33-34` hold the same two lines. "The same way" means as the whole spec labelled them. A sub-ticket's list may only be a subset of the spec's list, so the planner has no way to authorize a test a sibling adds.

**Only the spec gate authorizes a test edit.** `docs/design.md:146` (the spec approval gate) calls the approved "Tests to change" list "the only authorization to alter an existing test". The preamble every agent reads says the same: "only those listed under "Tests to change" in the human-approved spec" (`docs/design.md:235`, `factory/prompts/preamble.md:63`). The code reviewer blocks any changed test "unless the spec lists that test" (`docs/design.md:588`, `factory/prompts/reviewer.md:10`).

**Nothing makes the spec writer look for tests a decision overturns.** The spec writer's format asks only for "existing tests the intended change breaks, and why" (`docs/design.md:376`). The critic checks that listed tests are "genuinely" broken (`docs/design.md:413`). Nothing checks for a test that is missing.

**The parks happened.** In this repository, the verifier returned SPEC-DEFECT, its verdict for a defective spec, on three sub-tickets of one spec. Each time a NEW check already passed at the sub-ticket's own start:

| Sub-ticket | Verifier run | What the verifier found |
|---|---|---|
| T-0012.2 | run-0057 | `records-untouched` printed `0` on base and PR: "it passes on base too" |
| T-0012.5 | run-0071 | `responses-unchanged`: "on base it compares the file with itself and passes before any edit" |
| T-0012.6 | run-0092 | `no-old-paths-in-live-files` printed `exit=1` on base and PR, because "T-0012.2 and T-0012.5 have already cleaned" those files |

The first two are checks that always pass. The third passed because earlier siblings had already done the work. On the Nanobot repository, which the factory also builds, two sub-tickets of its spec T-0002 parked as "BLOCKED from implementer". Its sub-ticket T-0002.5 (`run-0147-implementer/output.md:87`) reported "The gate suite cannot pass until three T-0002.4 tests may change": the tests pinned T-0002.4's interim "not yet available" replies. `git log --diff-filter=A -- tests/policy/test_commands.py` there prints `37b8a9796 … (T-0002.4)`: the file was new in that earlier sibling. Its sub-ticket T-0002.2 (`run-0129-implementer/output.md:102`) reported that `test_interactive_agent_routes_a_complete_user_turn` pins exact CLI metadata, which decision D22 changes. D22 is that spec's decision to mark messages from the local command line. The spec's "Tests to change" left that test off.

**No harness code enforces "Tests to change" today.** `grep -rn "Tests to change\|tests_to_change\|diff-filter" factory bin agents`, leaving out `factory/prompts/`, prints only three lines from `agents/` prompt templates. No code reads the list. The merge step, `merge_cmd` (`factory/cli.py:528`), checks only the checkers' verdicts and that the branch contains the integration branch.

**The data a harness check needs is already recorded.** When a sub-ticket merges, `merge_cmd` writes `merge: {base_before, main_after}` on it (`factory/cli.py:553`). Those are the integration branch's commits just before and just after its merge. On the first sibling's merge it also writes the parent's `parent_base` (`factory/cli.py:560-561`), the integration branch before any sibling merged. So git can tell which sibling's merge first added a file.

**A prototype of this change works.** I built parts A to E in a scratch clone and ran every scenario of this spec on it and on an unchanged clone. On the unchanged clone, each NEW scenario printed the wrong output that `verification.md` gives. On the prototype, each printed its THEN. The REGRESSION scenarios printed their THEN on both. The harness suite passed on the prototype, `265 passed`. So no existing test breaks. I also ran the prototype's reader over every sub-ticket text stored in both repositories' stores. It found no entry: no existing sub-ticket would be refused. The one text that uses the phrase "(added by" (Nanobot T-0002.6) uses it in its Parallel-safe field, which the check does not read.

## Root cause

- Labels: the planner prompt block (`docs/design.md` §4, lines 507-509, and its copies) tells the planner to copy each check's label from the whole spec.
- Sibling tests: the same block limits a sub-ticket's "Tests to change" to a subset of the spec's list (line 510). `docs/design.md:46` (piece 8, the guardrail rule) and `:146` (the spec approval gate) make the spec gate the only authority for a test edit. The preamble (`:233-235`) and the code reviewer's first check (`:585-588`) repeat that rule.
- Decisions: the spec writer's FORMAT (`docs/design.md:376`) and the critic's rubric (`:405`, `:413`) never ask whether a behaviour-changing Decision overturns an existing test.
- Run start, `run_start` in `factory/cli.py:198`, refuses an implementer run only for state and in-flight reasons. The build workflow's `runRole` (`factory/workflows/build.js:68`) parks every refused run start as `harness-bug: …`, which `resolve --ruling` does not accept (`factory/cli.py:748`).

## Out of scope

- The implementer may not change a test on its own judgement, even if it says so in its PR description. The requester ruled this out.
- The merge gate still does not compare a diff's changed tests with "Tests to change". It does not today (`factory/cli.py:528`), and this change does not add that.
- A test that existed before the spec's first sub-ticket merged can still change only if the approved spec lists it.
- The harness does not check the planner's NEW and REGRESSION labels. Part A is a prompt rule.
- The harness does not read the new "Interim tests" field.
- The agent definition templates in `agents/` are not changed. They are stale copies already: `agents/factory-planner.md` differs from `factory/prompts/planner.md` before this change. They tell the agent to read the run's `system-prompt.txt` first, which carries the new text.
- No record in either store is edited, and nothing under `~/dev/nanobot-upstream` is written.

## Open questions

none

## Decisions

- A sub-ticket's "Tests to change" may list a test file that an earlier sibling of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The harness reads only lines of that form inside the "Tests to change" field, and checks the file, not the test function. Rejected: checking test functions. The implementer rule puts new tests in new files, so a file is what a sibling adds, and git records files.
- A listed file counts as added by a sibling when it is absent at the parent's `parent_base`, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge (reachable from its `main_after`, not from its `base_before`). Any merged sibling of the parent counts, including those from an earlier plan. The sibling ID on the line is for the reader and is not matched. Rejected: matching the named ID, because the planner's IDs (`ST-1`) differ from the store's (`T-0001.1`) and the operator's rule names no particular sibling.
- The check runs in `run start` for every implementer run of a sub-ticket: first dispatch, fix rounds and catch-up runs. Every dispatch passes through that one place. Rejected: checking when the plan is added, when no sibling has merged yet. Rejected: checking at the merge gate, after the implementer has already edited the test. Rejected: checking where a waiting sub-ticket is released, which happens in two places and never for a sub-ticket with no dependencies.
- A failed check refuses the run start with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build workflow parks the sub-ticket with that error as the reason, so `resolve --ruling` handles it like an implementer's BLOCKED. That is what the operator's "parks for the operator, as today" describes. Rejected: a new kind of park with its own resolve verb. Rejected: having `run start` park the ticket itself, which would break the rule that a refusal writes nothing.
- The preamble's guardrail sentence and the code reviewer's test-integrity check also accept a sibling entry that the harness has checked. Without them, the implementer and reviewer would still treat the edit as forbidden, and the park would remain.
- The earlier sibling names the tests a later sibling will break under a new planner field, "Interim tests". The harness does not read it.
- The critic's check for an omitted test goes under rubric 1 (Grounded), where the requester asked for it.
- The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator compares side by side, is an Operator step, not an acceptance scenario. Running it needs the Nanobot store and real agents, which a verifier must not touch.

## Risk

- Protected paths this change touches. Harness: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/workflows/build.js`, and `factory/prompts/{preamble,planner,spec_writer,critic,reviewer}.md`. Generated: `docs/prompts/{00-preamble,02-spec-writer,03-spec-critic,04-planner,06-code-reviewer}.md`, each re-copied from its design-doc block. The PR therefore needs the operator's protected-path approval at merge. It does not touch `.factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**` or `~/.nanobot/**`.
- Guardrail paths: the agent prompts above change, which is the point of this ticket. One new test file is added, `tests/factory/test_sibling_tests.py`. No existing test changes.
- Blast radius. Once an instance accepts the new harness revision, the preamble change reaches every role run on that instance. The new refusal fires only for an implementer run of a sub-ticket whose "Tests to change" field has an `(added by …)` line. No stored sub-ticket in either repository has one today. The workflow change affects only a run start refusal whose error starts `BLOCKED `. No such refusal exists today.
- A wrong check would park a legitimate sub-ticket. The operator then amends the sub-ticket's text and rules, as with any BLOCKED park. A check that is too loose would let a planner authorize an edit to a test that existed before the spec. The scenarios cover both directions.
- Overlap with tickets in flight. T-0025, the store's move to its own branch, is being built and edits README and the changelog. T-0027, the request to amend a pinned spec, may edit the critic prompt. The changelog check finds this entry by its text, not by its position, so merge order does not matter. Text conflicts are resolved at merge.

## Operator steps

These checks use real agents on the Nanobot repository's records. Only the operator should run them. Do them after this change merges, and before the Nanobot instance accepts the new harness revision, which is what makes its runs use the new prompts. Work on a copy of Nanobot's store, so nothing in that repository is written.

1. Copy `~/dev/nanobot-upstream/.factory/state` to a throwaway directory `C`. In `C`, delete `tickets/T-0002.*.yaml`, so that the planner plans from scratch. From `~/dev/spec-factory`, run with `FACTORY_INSTANCE=~/dev/nanobot-upstream/.factory FACTORY_STATE=C`: `bin/factory ticket set T-0002 status=ready-for-planner in_flight=[]`, then `bin/factory run start --role planner --ticket T-0002`, then `bin/factory run compose <run>`. Run one planner agent on the composed input. Do not run the build workflow: its build phase would create branches in the Nanobot repository. Check the plan. The sub-ticket that makes the list-edit subcommands available should list the earlier sibling's `tests/policy/test_commands.py` tests under "Tests to change" as `(added by …)`. That earlier sibling should name them under "Interim tests". Each check should be labelled against its own sub-ticket's base.
2. In the same copy, set T-0002 to `ready-for-spec-writer` and run one spec writer run the same way. Its "Tests to change" should name `tests/cli/test_agent_interactive.py::test_interactive_agent_routes_a_complete_user_turn` with decision D22, the marker for messages from the local command line.
3. Compare both outputs with the original plan and spec side by side. If either check fails, do not accept the revision on the Nanobot instance; reopen this ticket.

=== design.md
## Proposed change

Size: about 180 changed lines plus one new test file, so one PR. The planner may split it into two seams: the prompt texts (A, C, D, with their part of E), and the harness check (B, with the rest of E).

**A. Planner: labels per sub-ticket, interim tests, sibling entries.** In the planner block of `docs/design.md` §4 and its verbatim copies `docs/prompts/04-planner.md` and `factory/prompts/planner.md`, replace these four lines:

```text
  Acceptance: the parent's scenarios it covers, each as its WHEN command,
    THEN result and verification.md label, plus any intermediate checks
    it needs, labelled NEW or REGRESSION the same way
  Tests to change: none | the subset of the parent's list this one touches
```

with:

```text
  Acceptance: the parent's scenarios it covers, each as its WHEN command
    and THEN result, plus any intermediate checks it needs. Label each
    NEW or REGRESSION against this sub-ticket's own base: the integration
    branch with its dependencies merged. A check that already passes
    there, as an invariant or because an earlier sibling made it true,
    is REGRESSION, whatever the parent's verification.md label says.
  Interim tests: none | each new test file this one adds that a later
    sibling will break, with that sibling's ID
  Tests to change: none | the subset of the parent's list this one
    touches, plus each test an earlier sibling adds that this one's
    change breaks, one line each:
    - `<file>[::<test>]` (added by <sibling ID>): <reason>
    This one must depend on that sibling. Before each implementer run,
    the harness checks that a merged sibling added the file, and parks
    the sub-ticket if not. A test that existed before the parent's first
    merge goes here only if the parent's list names it.
```

All three files must stay byte-identical in that block.

**B. The sibling-tests check.**

1. `factory/subtickets.py`: add `PLAN_FIELDS`, the planner's field names in lower case: `scope`, `acceptance`, `interim tests`, `tests to change`, `protected paths`, `out of scope`, `depends on`, `parallel-safe`, `coverage map`. Add a function `sibling_tests(text) -> list[str]`. It walks the sub-ticket text line by line. A line that matches `FIELD_RE` with a key in `PLAN_FIELDS`, or a heading line (`_is_heading`), opens a new field. The function reads only lines inside the `tests to change` field, from its own line to the next field or heading. On those lines it finds every `` `<path>` (added by <anything>) `` with ``re.compile(r"`([^`\s]+)`\s*\(added by\s+[^)]+\)")``, drops any `::<test>` suffix, and returns the file paths in order without repeats. A mention anywhere else, such as a Scope or Parallel-safe line, is ignored.
2. `factory/gitops.py`: add `first_added(repo, base, tip, path) -> str | None`. It returns None when `git cat-file -e <base>:<path>` succeeds, because the file existed at the base. Otherwise it returns the first line of `git log --diff-filter=A --reverse --format=%H <base>..<tip> -- <path>`, or None. Add `is_ancestor(repo, a, b) -> bool`, which runs `git merge-base --is-ancestor a b`.
3. `factory/cli.py`: in `run_start`, after the in-flight guards and before `tripwire.baseline(cfg)` (line 212), add: when `a.role == "implementer"` and the ticket has a `parent`, call a new `_check_sibling_tests(root, cfg, t)`. That function reads `specs/<id>/subticket.md` and returns when `sibling_tests` finds nothing. Otherwise it loads the parent's `parent_base`, the integration branch's tip (`gitops.integration_branch` and `gitops.rev`), and the `merge` record of every other sub-ticket of the parent whose status is `merged` and whose `merge.main_after` is set. A path passes when `parent_base` is set, `first_added` returns a commit, and for some sibling that commit is an ancestor of `main_after` and not of `base_before`. The first path that fails raises `Refused`, with a message that starts exactly `BLOCKED from harness: ` and names the path and the parent. The form used in the prototype was `BLOCKED from harness: Tests to change lists <path> as added by a sibling, but no merged sibling of <parent> added it since <base[:9]>; list it in the parent spec's Tests to change, or remove it`. When `parent_base` is unset, it said `(no sibling has merged)` in place of `since …`. Because it raises before `tripwire.baseline` and before the run id is reserved, a refusal writes no run directory, worktree, branch or `in_flight` entry.
4. `factory/workflows/build.js`, `runRole` (line 68): when `start.ok` is false and `start.error` starts with `BLOCKED `, park with `start.error` verbatim as the reason. Every other refusal keeps today's `harness-bug: run start <role>: <stderr>`. `resolve --ruling` (`factory/cli.py:748`) already accepts a park reason that starts with `BLOCKED` and returns the sub-ticket to `ready-for-implementer`. Its next run start checks again, so the human amends the sub-ticket text, or the pinned spec, before ruling.
5. A new test file, `tests/factory/test_sibling_tests.py`, with the cases of the build-dispatch scenarios below. Each case builds a scratch store with `FACTORY_STATE` and a scratch git target, like the existing suite. Add three cases more: a sibling that has not merged (no `parent_base`) refuses; a file a sibling added, deleted later and re-added by another commit is still accepted, because the first add counts; and `sibling_tests` returns nothing for the T-0002.6-style Parallel-safe mention.

**C. Spec writer and critic: tests a decision overturns.**

- In the spec writer block of `docs/design.md` §2, `docs/prompts/02-spec-writer.md` and `factory/prompts/spec_writer.md`, insert this bullet in RULES directly before "- Open questions stay open.":

```text
- Tests a decision overturns: for each Decision that changes existing
  behaviour, search the existing tests for ones that pin the old
  behaviour, and list each under "Tests to change" with the decision it
  follows. One left off blocks the implementer later.
```

- In the critic block of `docs/design.md` §3, `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`, put these lines directly after the rubric line "1. Grounded: cited paths and symbols exist; evidence is real output.":

```text
   For each Decision that changes existing behaviour, search the tests
   for the old behaviour yourself: a test that pins it and is missing
   from "Tests to change" is a finding.
```

**D. Preamble and code reviewer accept a checked sibling entry.**

- Preamble (`docs/design.md` "Shared preamble", `docs/prompts/00-preamble.md`, `factory/prompts/preamble.md`, all three byte-identical): replace `only those listed under "Tests to change" in the human-approved spec).` with these lines:

```text
only those listed under "Tests to change" in the human-approved spec, or
in your sub-ticket as added by an earlier sibling, which the harness
checks).
```

- Code reviewer (`docs/design.md` §6, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`): replace `   are BLOCKING unless the spec lists that test under "Tests to change".` with these lines:

```text
   are BLOCKING unless the spec lists that test under "Tests to change",
   or the sub-ticket lists it there as added by an earlier sibling.
```

**E. Documents.**

1. `docs/design.md`, piece 8 row (line 46), "What it must do": after "is that row for exactly the tests listed", end that sentence there and add: "A test file an earlier sibling sub-ticket of the same parent added is also covered when the sub-ticket lists it as added by that sibling and the sibling-tests check has passed (Tests a sibling added, below);" before "any other guardrail…". In the "GitHub gives you" cell, after `not in the pinned spec's "Tests to change"`, add "or among the sub-ticket's checked sibling entries".
2. `docs/design.md`, the Spec approval row (line 146): replace "which is the only authorization to alter an existing test" with "which is the only authorization to alter a test that existed before the parent's first sub-ticket merged; a test an earlier sibling added needs only the sub-ticket's checked entry (piece 8)".
3. `docs/design.md`, a new paragraph directly before "**Only the dispatcher writes a live store during a run.**", one line, starting `**Tests a sibling added.**`. It says: the entry form; that the planner writes these lines and the spec gate never saw them; the rule of B.3, with "parent's base" glossed as the integration branch before its first sub-ticket merged; the refusal (exit 2, nothing written, a reason that starts `BLOCKED from harness:` and names the file); that the build parks the sub-ticket with that reason and the human resolves it as an implementer's BLOCKED (amend the sub-ticket or pinned spec, then `resolve --ruling`, or close); and that a test that existed before the parent's first merge still needs the pinned spec's list.
4. `docs/changelog.md`: one new numbered entry after the last one, starting `<n>. After issue #40 (2026-10-04), `. It covers the per-sub-ticket labels ("own base"), the `(added by <sibling ID>)` entries and "Interim tests", the check and its `BLOCKED from harness:` park, the preamble and reviewer change, "the spec writer lists the tests each behaviour-changing Decision overturns", and "critic rubric 1". It ends with "Rejected: letting the implementer edit a test on its own judgement." Numbering stays contiguous.
5. `dev/build-harness.spec.md`, kept consistent with the design. Line 203 (`run start` guards): add the sibling-tests refusal after the in-flight guard, citing doc §Harness, "Tests a sibling added". Line 245 (piece 8): an existing test file is also allowed when one of the sub-ticket's `(added by <ID>)` lines that `run start` checked names it. Line 275 (`runRole`): a refusal whose JSON `error` starts `BLOCKED ` parks with that error verbatim, so `resolve --ruling` applies.
6. `README.md`. Under "What is built and what is not", "Built", add a bullet after "Live-store fence" that starts `- **Sibling tests check.**`. It says, in plain words: a planner may let a sub-ticket change a test file that an earlier sub-ticket of the same spec added; before each implementer run the harness checks in git that a merged earlier sub-ticket added it; otherwise the sub-ticket parks as blocked and the human rules on it as on any blocked build; any other existing test still needs the approved spec's list; it is tested and has not yet fired on a real ticket. In "Where a human decides", in the **Unstick** row, change `--ruling F`'s note to "(a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added)". The status date is already 2026-10-04.

## Tests to change

none. With the prototype of A to E, `.venv/bin/python -m pytest -q -p no:cacheprovider tests/factory`, with `TMPDIR` set to a fresh directory under `/tmp`, printed `265 passed`. The tests that compare prompt copies (`tests/factory/test_instance.py`, `test_run_scratch.py`, `test_writing_standard.py`, `test_decision_log.py`) still pass, because every copy changes together. No Decision of this change overturns behaviour that an existing test pins. That suite run is the search part C asks for.

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: An implementer starts only when each sibling-added test it may change came from a merged sibling
`factory run start --role implementer` on a sub-ticket MUST refuse with exit 2, writing no run, worktree, branch or in-flight entry, with an error that starts `BLOCKED from harness: ` and names the file, when a line `` `<file>` (added by <ID>) `` inside its "Tests to change" field names a file that existed at the parent's base, or whose first adding commit on the integration branch since that base lies inside no merged sibling's recorded merge. It SHALL accept a file a merged sibling's merge added, and SHALL ignore such a line outside that field.

#### Scenario: A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0022-sib.sh <<'EOF'
# Sourced from the repo root with E set to a test file path. Builds a scratch store whose parent
# T-0001 is planned as ST-1 and ST-2: ST-2 depends on ST-1 and lists `$E` under Tests to change as
# added by ST-1. Builds a scratch target whose main holds tests/test_old.py from before the plan,
# tests/test_interim.py from ST-1's recorded merge, and tests/test_operator.py from a later direct
# commit that is no sibling's merge. ST-2's Scope line mentions tests/test_old.py in the same form.
# T-0001.1 is merged; T-0001.2 is ready for its implementer.
T22=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T22/store FACTORY_REPO=$T22/t FACTORY_INTEGRATION_BRANCH=main
printf '# Fixture\n\nThe bot should do the thing.\n' > $T22/req.md && printf '## Problem\nx\n' > $T22/spec.md
bin/factory ticket new --file $T22/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T22/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T22/t && mkdir $T22/t/tests && echo 'def test_old(): pass' > $T22/t/tests/test_old.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm base && A=$(git -C $T22/t rev-parse HEAD)
git -C $T22/t checkout -qb sib && echo 'def test_interim(): pass' > $T22/t/tests/test_interim.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm interim && git -C $T22/t checkout -q main
git -C $T22/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' sib && B=$(git -C $T22/t rev-parse HEAD)
echo 'def test_operator(): pass' > $T22/t/tests/test_operator.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm operator
printf 'ST-1 / Interim\nDepends on: none\nParallel-safe: yes\nInterim tests: `tests/test_interim.py`, broken by ST-2\n\nST-2 / Final\nDepends on: ST-1\nParallel-safe: yes\nScope: B, which reads `tests/test_old.py` (added by the base commit)\nTests to change:\n- `%s` (added by ST-1): ST-2 replaces the interim behaviour\nProtected paths: none\n' "$E" > $T22/plan.md
bin/factory subticket add T-0001 --file $T22/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$B'" >/dev/null
bin/factory ticket set T-0001 "parent_base='$A'" >/dev/null
bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0022-build.mjs <<'EOF'
// node t0022-build.mjs, from the checkout under test after sourcing t0022-sib.sh: runs
// factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE. Each clerk command runs
// for real (sh -c, from this checkout, environment unchanged); each role run returns an empty
// output, which the workflow records as a killed run. Prints each park, as `park <id>: <reason>`.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p') runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `exit=0 ready-for-implementer runs=1`

#### Scenario: A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(for E in tests/test_old.py tests/test_operator.py tests/test_never.py; do (. ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >$T22/o 2>/dev/null; x=$?; J=$(tail -1 $T22/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: ') names=$(echo "$J" | grep -cF "$E") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) branch=$(git -C $FACTORY_REPO branch --list 'factory/T-0001.2' | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints three lines, each exactly `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`

### Requirement: The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it
When an implementer's run start is refused with an error that starts `BLOCKED `, the build workflow SHALL park the sub-ticket with that error, verbatim, as the reason, so that `factory resolve <id> --ruling F` MUST accept the park and return the sub-ticket to `ready-for-implementer`.

#### Scenario: The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(E=tests/test_old.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(BLOCKED from harness:\).*/\1/'; printf 'Ruling: x\n' > $T22/r.md; bin/factory resolve T-0001.2 --ruling $T22/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')")`
- THEN it prints exactly `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The planner labels checks per sub-ticket and may list tests an earlier sibling added
Every copy of the planner prompt (the `docs/design.md` §4 block, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`) SHALL tell the planner to label each check against the sub-ticket's own base, to name interim tests, and to list a sibling-added test as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``; it MUST no longer say to label checks "the same way", and the design block and its `docs/prompts/` copy SHALL stay byte-identical.

#### Scenario: Every planner copy labels per sub-ticket and lists sibling tests
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-planner.txt; sed -n '/^## 4\. Planner/,/^## 5\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/04-planner.md factory/prompts/planner.md; do echo "own=$(grep -c "against this sub-ticket's own base" $f) sibling=$(grep -cF '(added by <sibling ID>)' $f) interim=$(grep -c '^  Interim tests: ' $f) copied=$(grep -c 'labelled NEW or REGRESSION the same way' $f)"; done; cmp -s $X docs/prompts/04-planner.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `own=1 sibling=1 interim=1 copied=0`, then `verbatim`

### Requirement: The spec writer lists the tests a decision overturns, and the critic checks for one left off
Every copy of the spec writer prompt SHALL carry the RULES bullet that starts `- Tests a decision overturns: `, and every copy of the critic prompt SHALL say under rubric 1 that a test pinning the old behaviour and `missing from "Tests to change" is a finding`.

#### Scenario: Every spec writer and critic copy carries the decision-overturns rule
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-sw.txt; for h in '2\. Spec writer' '3\. Spec critic'; do sed -n "/^## $h/,/^## [0-9]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: writer=$(grep -c '^- Tests a decision overturns: ' $X) critic=$(grep -c 'from "Tests to change" is a finding' $X)"; echo "docs/prompts: writer=$(grep -c '^- Tests a decision overturns: ' docs/prompts/02-spec-writer.md) critic=$(grep -c 'from "Tests to change" is a finding' docs/prompts/03-spec-critic.md)"; echo "factory/prompts: writer=$(grep -c '^- Tests a decision overturns: ' factory/prompts/spec_writer.md) critic=$(grep -c 'from "Tests to change" is a finding' factory/prompts/critic.md)")`
- THEN it prints exactly `design: writer=1 critic=1`, then `docs/prompts: writer=1 critic=1`, then `factory/prompts: writer=1 critic=1`

### Requirement: The preamble and the code reviewer accept a checked sibling entry
Every copy of the preamble SHALL allow an existing test listed `in your sub-ticket as added by an earlier sibling`, and every copy of the code reviewer prompt SHALL not block a test `the sub-ticket lists it there as added by an earlier sibling`.

#### Scenario: Every preamble and reviewer copy accepts a sibling entry
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-pr.txt; for h in 'Shared preamble' '6\. Code reviewer'; do sed -n "/^## $h/,/^## [0-9A-Z]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $X) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' $X)"; echo "docs/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' docs/prompts/00-preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' docs/prompts/06-code-reviewer.md)"; echo "factory/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' factory/prompts/preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' factory/prompts/reviewer.md)")`
- THEN it prints exactly `design: guard=1 review=1`, then `docs/prompts: guard=1 review=1`, then `factory/prompts: guard=1 review=1`

### Requirement: Role runs receive the new rules
The system prompt that `run start` writes for a planner, spec writer and critic run SHALL contain that role's new rule and the new preamble sentence.

#### Scenario: Planner, spec writer and critic runs get the new rules in their system prompts
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2 3; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-planner >/dev/null; bin/factory ticket set T-0002 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0003 status=ready-for-critic >/dev/null; for p in planner:T-0001 spec_writer:T-0002 critic:T-0003; do bin/factory run start --role ${p%%:*} --ticket ${p##*:} >/dev/null 2>&1; done; P=$(ls $FACTORY_STATE/runs/*-planner/system-prompt.txt); W=$(ls $FACTORY_STATE/runs/*-spec_writer/system-prompt.txt); C=$(ls $FACTORY_STATE/runs/*-critic/system-prompt.txt); echo "planner own=$(grep -c "against this sub-ticket's own base" $P) sibling=$(grep -cF '(added by <sibling ID>)' $P) guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $P) writer=$(grep -c '^- Tests a decision overturns: ' $W) critic=$(grep -c 'from "Tests to change" is a finding' $C)")`
- THEN it prints exactly `planner own=1 sibling=1 guard=1 writer=1 critic=1`

### Requirement: The documents record the sibling-tests check
`docs/design.md` SHALL describe the check in a paragraph that starts `**Tests a sibling added.**`, in piece 8 and in the spec approval gate row, and SHALL no longer call the gate's list the only authorization to alter an existing test; `dev/build-harness.spec.md` SHALL name the `BLOCKED from harness` refusal; `docs/changelog.md` SHALL gain an entry for issue #40 and stay numbered without a gap; `README.md` SHALL describe the check and the new `--ruling` case; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec describe the check
- WHEN `(echo "piece8=$(grep '^| 8 |' docs/design.md | grep -c 'added by that sibling') gate=$(grep '^| Spec approval |' docs/design.md | grep -c 'a test an earlier sibling added') stale=$(grep -c 'which is the only authorization to alter an existing test' docs/design.md) check=$(grep -c '^\*\*Tests a sibling added\.\*\*.*BLOCKED from harness:' docs/design.md) build=$(grep -c 'BLOCKED from harness' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `piece8=1 gate=1 stale=0 check=1 build=1`

#### Scenario: The changelog records issue 40's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #40 ' docs/changelog.md | grep -oF -e 'own base' -e 'added by' -e 'BLOCKED from harness' -e 'Decision' -e 'critic rubric 1' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the sibling tests check and its ruling
- WHEN `(echo "built=$(grep -c '^- \*\*Sibling tests check\.\*\*' README.md) ruling=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'a test no merged sibling added')")`
- THEN it prints exactly `built=1 ruling=1`

#### Scenario: The sibling-tests change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance

Each NEW item's failure was observed on an unchanged clone of `main` at `0b1abad`, and each THEN on a prototype of the change. Every command was copied verbatim from this spec and run in zsh through the fresh-HOME wrapper. The three build-dispatch scenarios and the system-prompt scenario were also run in bash, with the same output.

- A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored → REGRESSION. It prints `exit=0 ready-for-implementer runs=1` today, because nothing checks the field. It guards against a check that refuses too much, or that reads the Scope line.
- A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts → NEW. Today each of the three lines prints `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer`. The run starts, and its run directory and branch are created.
- The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back → NEW. Today it prints `park T-0001.2: budget kill: implementer`, because the implementer ran and the stub returned nothing. Then it prints `ruling=2 parked`.
- Every planner copy labels per sub-ticket and lists sibling tests → NEW. Today each line prints `own=0 sibling=0 interim=0 copied=1`, then `verbatim`.
- Every spec writer and critic copy carries the decision-overturns rule → NEW. Today it prints `writer=0 critic=0` on all three lines.
- Every preamble and reviewer copy accepts a sibling entry → NEW. Today it prints `guard=0 review=0` on all three lines.
- Planner, spec writer and critic runs get the new rules in their system prompts → NEW. Today it prints `planner own=0 sibling=0 guard=0 writer=0 critic=0`.
- The design doc and build spec describe the check → NEW. Today it prints `piece8=0 gate=0 stale=1 check=0 build=0`.
- The changelog records issue 40's change without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`.
- README describes the sibling tests check and its ruling → NEW. Today it prints `built=0 ruling=0`.
- The sibling-tests change adds no whitespace errors → REGRESSION. It prints `exit=0` on `main`, where the range is empty, and on the prototype.

Gate suite, not a scenario: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, with pytest's temporary directory under `/tmp` as the harness-suite scenario in current truth sets it. Every test passes, including the new `tests/factory/test_sibling_tests.py`. The prototype without that file printed `265 passed`.

## PR description (the implementer's output)

Sub-ticket: T-0022.1 (ST-1 / Sibling tests), parent T-0022 (issue #40), spec v1. Branch `factory/T-0022.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0022.1`, base `c2750bf`, head `771ee0e` (two commits: `8f1d356` is the change, `771ee0e` is a one-line correction to the build spec).

## What changed

Some background first. The **planner** is the agent that splits an approved spec into **sub-tickets**, which are built and merged one at a time. Sub-tickets of the same spec are **siblings**. Until now, only the spec's own approved "Tests to change" list allowed an implementer to edit an existing test. That stopped a sub-ticket whenever it had to change a test an earlier sibling had added, because that test did not exist when the spec was approved. This change lets the planner list such a test, and the harness checks the entry in git before the implementer starts. It also fixes two causes of avoidable parks in the agents' instructions.

- **A. Planner prompt.** The prompt now tells the planner to label each check NEW or REGRESSION against the sub-ticket's own base, instead of copying the label from the whole spec. It adds an "Interim tests" field. "Tests to change" may now list `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The block was changed the same way in `docs/design.md` §4, `docs/prompts/04-planner.md` and `factory/prompts/planner.md`, and the three copies are byte-identical in that block.
- **B. The sibling-tests check.**
  - `factory/subtickets.py` gains `PLAN_FIELDS`, `SIBLING_TEST_RE` and `sibling_tests(text)`. They read `(added by …)` entries only inside the "Tests to change" field. The field ends at the next planner field or heading. `::<test>` suffixes are dropped and repeated files are listed once.
  - `factory/gitops.py` gains `first_added(repo, base, tip, path)`. It returns None when the file existed at `base`. Otherwise it returns the oldest `--diff-filter=A` commit in `base..tip`.
  - `factory/cli.py` gains `_check_sibling_tests`, which `run_start` calls for an implementer run of a sub-ticket. The call comes after the in-flight guards and before `tripwire.baseline`, so a refusal writes nothing. A listed file passes when the parent has a `parent_base` and the file's first add lies inside some merged sibling's recorded merge: reachable from `main_after` and not from `base_before`. Otherwise `run start` exits 2 with `BLOCKED from harness: Tests to change lists <path> as added by a sibling, but no merged sibling of <parent> added it since <base9>; list it in the parent spec's Tests to change, or remove it`. If no sibling has merged yet, `(no sibling has merged)` takes the place of `since <base9>`.
  - In `factory/workflows/build.js`, `runRole` parks the sub-ticket with the refusal's JSON `error` word for word when it starts with `BLOCKED `. Every other refusal still parks as `harness-bug: run start …`. `resolve --ruling` already accepted a `BLOCKED` park, so it was not changed.
  - New test file: `tests/factory/test_sibling_tests.py`.
- **C. Spec writer and critic prompts.** The spec writer gets the RULES bullet "Tests a decision overturns", placed before "Open questions stay open". Critic rubric 1 gets three lines: a test that pins the old behaviour and is missing from "Tests to change" is a finding. Both edits are in all three copies of each prompt.
- **D. Preamble and code reviewer prompts.** The guardrail sentence in the preamble, and the reviewer's test-integrity check, now also accept a test the sub-ticket lists as added by an earlier sibling. Both edits are in all three copies of each prompt.
- **E. Documents.**
  - `docs/design.md`:
    - The piece 8 row gets the sibling sentence and the GitHub-column clause.
    - The Spec approval row is reworded.
    - A new one-line paragraph, `**Tests a sibling added.**`, comes before "Only the dispatcher writes…".
  - `docs/changelog.md`: new entry 54, "After issue #40 (2026-10-04)". It ends with the rejected alternative.
  - `dev/build-harness.spec.md`: the `run start` guards get the refusal, piece 8 gets the checked entry, and `runRole` gets the BLOCKED park. The second commit says the park belongs to `build.js` and not to "both scripts", because `intake.js` never starts an implementer.
  - `README.md`: a new Built bullet "Sibling tests check." after "Live-store fence", and a new case in the Unstick row's `--ruling F` note.

Callers of what I changed:
- `run_start` is reached only through the CLI's `set_defaults(fn=run_start)` (`factory/cli.py:1357`).
- `runRole` is called five times, all inside `build.js`. They all share the one refusal branch I edited.
- I added no other caller to an existing function. `head_contains` is reused unchanged; it already has three other callers.

## Acceptance results

Every command was run from the worktree with a fresh HOME, in zsh, and `TMPDIR` set to this run's `scratch/tmp`. The GIVEN block was written once, exactly as the spec gives it. Before = base `c2750bf`; after = head `771ee0e`. The outputs on `8f1d356` and `771ee0e` match exactly (`diff` printed nothing).

| Scenario | Label | Before | After |
|---|---|---|---|
| merged sibling's file accepted, Scope mention ignored | REGRESSION | `exit=0 ready-for-implementer runs=1` | `exit=0 ready-for-implementer runs=1` |
| listed test predates plan / no sibling / never added | NEW | 3× `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer` | 3× `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer` |
| build parks with harness reason, ruling returns it | NEW | `park T-0001.2: budget kill: implementer` / `ruling=2 parked` | `park T-0001.2: BLOCKED from harness:` / `ruling=0 ready-for-implementer` |
| planner copies | NEW | 3× `own=0 sibling=0 interim=0 copied=1`, `verbatim` | 3× `own=1 sibling=1 interim=1 copied=0`, `verbatim` |
| writer/critic copies | NEW | `writer=0 critic=0` on all three lines | `design: writer=1 critic=1`, `docs/prompts: writer=1 critic=1`, `factory/prompts: writer=1 critic=1` |
| preamble/reviewer copies | NEW | `guard=0 review=0` on all three lines | `design: guard=1 review=1`, `docs/prompts: guard=1 review=1`, `factory/prompts: guard=1 review=1` |
| system prompts of real runs | NEW | `planner own=0 sibling=0 guard=0 writer=0 critic=0` | `planner own=1 sibling=1 guard=1 writer=1 critic=1` |
| design doc and build spec | NEW | `piece8=0 gate=0 stale=1 check=0 build=0` | `piece8=1 gate=1 stale=0 check=1 build=1` |
| changelog | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| README | NEW | `built=0 ruling=0` | `built=1 ruling=1` |
| no whitespace errors | REGRESSION | `exit=0` | `exit=0` |

Every NEW item failed on the base exactly as `verification.md` and the plan's table say, and printed its THEN after the change. A full refusal text, from the `tests/test_operator.py` fixture: `BLOCKED from harness: Tests to change lists tests/test_operator.py as added by a sibling, but no merged sibling of T-0001 added it since 6cd4bf63b; list it in the parent spec's Tests to change, or remove it`. The build driver printed that same text as the park reason.

Gates, each run exactly as written, from the worktree on `771ee0e` with a clean tree:
- `(export HOME=…; git diff --check main...HEAD)` → exit 0, no output.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` → `310 passed in 253.42s`.
- The suite again with `TMPDIR=$(mktemp -d /tmp/t0022-suite.XXXXXX)`, as the harness-suite scenario in current truth sets it → `310 passed in 275.70s`. That run started on `8f1d356`. The only later change is a wording edit to `dev/build-harness.spec.md`, which no test reads (`grep -rln build-harness.spec tests/factory` prints nothing).
- 310 = 300 existing tests (`--collect-only --ignore tests/factory/test_sibling_tests.py` prints `300 tests collected`) + 10 new. The spec's figure of 265 is from `0b1abad`, before T-0025's tests merged.
- `ruff check` (default rules) on the three changed modules and the new test: `All checks passed!`. `node --check factory/workflows/build.js`: exit 0.

## Tests added/changed

New file `tests/factory/test_sibling_tests.py`, 10 cases. It is black-box: it drives `bin/factory` and `build.js` as subprocesses on a throwaway store and a scratch target repository, built like the spec's `t0022-sib.sh` fixture.
- A merged sibling's file is accepted, with and without a `::test` suffix (2 cases).
- A file that predates the plan, was added by a direct commit, or was never added is refused (3 cases). Each refusal: exit 2, error starts `BLOCKED from harness: ` and names the file and parent, no run directory, no branch, status unchanged, `in_flight` empty.
- With no sibling merged and no `parent_base`, the file is refused with `(no sibling has merged)`.
- A file added by a sibling, deleted, then re-added by a direct commit is accepted, because the first add counts. I checked that this case catches a wrong fix: with `--reverse` removed from `first_added`, it fails (`1 failed`).
- The build workflow parks the sub-ticket with the harness's reason and nothing else, and `resolve --ruling` returns it to `ready-for-implementer`. This case needs `node` on PATH. It asserts that node is there rather than skipping.
- An `(added by …)` mention in a Parallel-safe line, in the form the stored Nanobot sub-ticket T-0002.6 uses, is ignored.
- The field ends at the next plan field (Protected paths) and at a heading (the shared plan context the store appends). A line that names no plan field stays inside the field. Bold field names and `::test` suffixes are read.

With the code changes stashed, 6 of the 10 fail. The 4 that pass on base are the two accept cases, the re-add case and the Parallel-safe case. They guard against a check that refuses too much, so on base, where nothing is checked, they pass by design. No existing test was changed.

## Known gaps and uncertainties

- **I reused `head_contains` instead of adding `is_ancestor`, which differs from the spec's B.2.** `gitops.head_contains(repo, head, base)` already runs `git merge-base --is-ancestor base head`, which is exactly the `is_ancestor(repo, a, b)` the spec asks for. The coding standard's rule 1 is to reuse before writing. Nothing in acceptance names `is_ancestor`. One difference: `head_contains` does not capture git's stderr, so an unknown SHA in a merge record would print a git error on the CLI's stderr before the refusal.
- Sibling merge records are used only when both `merge.main_after` and `merge.base_before` are set. The spec names only `main_after`. `merge_cmd` always writes both, so this changes nothing in practice. Without the second condition, a record missing `base_before` would accept any add reachable from `main_after`.
- **The park passes planner-written text to a shell.** The refusal names a path taken from planner-written text, and `build.js`'s `park()` puts the reason inside a double-quoted `sh -c` string, escaping only `"`. `SIBLING_TEST_RE` excludes backticks and whitespace, but a path such as `$(cmd)` with no spaces would still be expanded by the clerk's shell. Today's `harness-bug:` parks already pass stderr text through the same path; this change adds planner-controlled text to it. I did not change `park()`, because it is outside this sub-ticket's parts.
- `first_added` relies on git's default history simplification to find the add commit on a sibling's merged branch. I verified this only for the `--no-ff` merges that `merge_cmd` makes, in the tests and the fixture.
- The build-dispatch test needs `node` on PATH, as the spec's scenarios do. Without node, that case fails instead of skipping.
- factory: markers added: none.

## Out-of-scope observations

- The new planner text says a sub-ticket with an `(added by …)` line "must depend on that sibling". The harness accepts any merged sibling, as Decision 2 of the spec intends. The critic noted the same; nothing enforces the dependency.
- The README rule "Ground truth only above 'Where this can go'" says a thing is listed as Built only after it has run on a real ticket. The new Built bullet follows the spec and the existing "Tripwire" and "Live-store fence" bullets, which say "tested, and has not yet fired on a real ticket". The page's rule and its practice disagree. That disagreement predates this change.
- The parent's Operator steps (re-plan and re-spec Nanobot's T-0002 on a copy of its store) are for the operator after merge. I did not run them.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN on the final head, every NEW item was seen failing on the base first, and both gates passed on the final commit. The deliberate differences from the spec (reusing `head_contains`, requiring `base_before`) are listed above.
ESCALATIONS: none

## Diff `c2750bf9c18ca6e37e4cfec439a0a9ef42f318d6...771ee0ec14ec755265f969c709ee3a4099d5160d`

diff --git a/README.md b/README.md
index fd3121b..b12591e 100644
--- a/README.md
+++ b/README.md
@@ -434,7 +434,7 @@ FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLE
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, or an implementer reported itself blocked) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-plan, a re-scope, or closing |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added) · `--redispatch` (re-run the checks on the same commit after an outside fix) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, a re-check, a re-plan, a re-scope, or closing |
 | **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
@@ -474,6 +474,12 @@ next, how many rounds, what the checkers receive, when a merge is allowed, when
   store's `runs/` or `worktrees/` is refused even with the marker. The fence stops a role's tools,
   such as its test suite, from changing the live records by accident; it is not isolation. It is
   tested, and has not yet fired on a real ticket.
+- **Sibling tests check.** The planner may let a sub-ticket change a test file that an earlier
+  sub-ticket of the same spec added, for example a test that pinned that earlier sub-ticket's
+  interim behaviour. Before each implementer run, the harness checks in git that a merged earlier
+  sub-ticket added the file. If none did, the sub-ticket parks as blocked, and the human rules on it
+  as on any blocked build ("Where a human decides"). Any other existing test still changes only if
+  the approved spec lists it. It is tested, and has not yet fired on a real ticket.
 
 **Not built**
 
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 4019123..f7a97bb 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -200,7 +200,7 @@ CLI (the **store CLI** of doc §Harness table piece 1 — read, transition, reco
 - `factory intake [<dir>]` (default `knowledge_vault/specs`): `request new` for every `*.md` not yet imported (content hash in `requests/index.yaml`); prints `imported N, skipped M (already imported)` and the IDs. It does not run anything; the `/factory` skill then launches `intake.js` per ID.
 - `factory ticket new --type (retro|revert) --branch B [--reverts SHA] [--output FILE]` (harness or human): no-sub-ticket PR record (piece 5) with `head` from `git ls-remote`; `--reverts` required for `revert`, refused unless SHA is a `merged` ticket's `head`; `--type retro` also writes `retros/<date>.yaml` (proposals with their metrics, prior-proposal verdicts) from the retro run's output `FILE`. It then runs `factory gate-run ID --head <head>` (L) so the ticket has its ci row. Other types → exit 2 `use factory request new`.
 - `factory ticket show ID`; `factory ticket set ID key=value` (logged); `factory ticket transition ID --to STATE --by RUN [--round spec|pr:+1|reset|init]` (the clerk's one write for routing; `init` sets the counter to 1 if 0). **Guards (doc §Harness table piece 2: "put the round and routing guards in the CLI, not the clerk"):** exit 2, store unchanged, nothing logged, when `+1` would take the counter above `config.yaml` `max_rounds` (`round.spec 2 is at max_rounds 2`), or when `(current status, STATE)` is not an edge of the routing table stored in `config.yaml` `routing:` (the doc §Routing table rows plus the resolution rules; `no route ready-for-triage → merged`). `factory ticket park ID --reason R --outputs RUN,RUN [--question PATH]`.
-- `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model: M`, default `config.yaml` `models[R]`; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
+- `factory run start --role R --ticket ID|none --head SHA|none [--model M]` → prints `run_id`, writes `runs/<run_id>/{meta.yaml,system-prompt.txt}` and creates the empty `runs/<run_id>/scratch/` for the run's temporary files, which the store's `.gitignore` excludes (`model: M`, default `config.yaml` `models[R]`; `budget_usd` copied from the ticket), appends the id to `in_flight`. **Guards:** exit 2, nothing written, when the ticket is not in R's ready state (`T-0001 is ready-for-triage, not ready-for-critic`; ready states: triage `ready-for-triage`, spec_writer `ready-for-spec-writer`, critic `ready-for-critic`, planner `ready-for-planner`, implementer `ready-for-implementer`, reviewer/verifier `checks-in-flight` or `ready-for-checks`, verifier also `ready-for-parent-verify`; retro runs with `--ticket none`), or when the ticket's branch already has a run in `in_flight` (implementer, retro: any run; reviewer, verifier: a run of the same role) — `ticket/T-0001 already has run <id> in flight`; or, for an implementer run of a sub-ticket, when a `` `<file>` (added by <ID>) `` line in its "Tests to change" field names a file that existed at the parent's `parent_base` or whose first adding commit on the integration branch since then lies inside no merged sibling's recorded `merge` (doc §Harness, "Tests a sibling added") — `BLOCKED from harness: Tests to change lists <file> as added by a sibling, but no merged sibling of <parent> added it since <base>; …`. **Run id reservation:** after the guards pass and before anything else is written, `run start` reserves the run's directory by creating `runs/<run_id>/` create-exclusive (an mkdir that fails when the path already exists); on a collision it takes the next id and tries again. Two starts on one store at the same moment, whatever their tickets or roles, therefore never share a run directory, and the id is final before its `meta.yaml` is written. A refused start reserves nothing (item 70).
 - `factory run compose RUN` (**the one input mechanism**, critic S2) → writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares for `(role, round, resolution)` — the "with input =" lists in H, read from the store and `~/factory/clone` — and records their paths as `input_sources:` and the pinned spec version it used as `spec_version:` in `meta.yaml` (a run keeps that version even if the spec is re-pinned while it is in flight, K). The file opens with the repo's role-context block (doc §Harness), ahead of those sources; it is not a store path, so it is not one of the `input_sources:` (its text is in `input.md`). The text `agent()` receives is only `Your entire input is ~/factory/state/runs/<run_id>/input.md; read it first.` No input text is composed anywhere else.
 - `factory run finish RUN --output-file F [--status-override KILLED]` → writes `output.md`, parses STATUS (H), removes the id from `in_flight`, prints `STATUS CONFIDENCE ESCALATIONS` as JSON, logs `escalation.queued` when the list is non-empty (H).
 - `factory spec add ID --file F` → `spec.version += 1`, `specs/ID/v<N>.md`; `factory spec tasks PARENT --run RUN` → writes that planner run's `output.md`, trailer removed as for spec text (above), to `openspec/changes/<PARENT>/tasks.md` (exit 2 unless RUN is a `PLANNED` planner run of PARENT); `factory subticket add PARENT --file F --depends-on IDS --parallel-safe yes|no` → sub-ticket in `ready-for-implementer` or `waiting-dependencies`.
@@ -242,7 +242,7 @@ Runtime: `factory/hooks/pre-receive` is a `#!/bin/sh` shim installed into `~/fac
 4. **`refs/heads/main`** (merge gate). Only `harness`; fast-forward only. `H = new`; ticket with `head == H`. Normal conditions, first failure named:
    - `results/H/{ci,reviewer,verifier}.yaml` = `PASS`,`APPROVE`,`VERIFIED` (`missing: ci, reviewer, verifier for H`);
    - `git merge-base --is-ancestor old H` (`head H does not contain main <old>`);
-   - piece 8, per path in `git diff --name-only old H`: protected glob or **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`protected path <p> needs human approval on H` / `guardrail path <p> needs human approval on H`); existing test file (test glob, present in `old`) modified or deleted → in `spec.tests_to_change` of the pinned version (`existing test <p> modified; not in Tests to change of pinned spec v<N>`); new test file → nothing.
+   - piece 8, per path in `git diff --name-only old H`: protected glob or **non-test guardrail glob** → `approvals/<ID>/pr-H.yaml` must exist (`protected path <p> needs human approval on H` / `guardrail path <p> needs human approval on H`); existing test file (test glob, present in `old`) modified or deleted → in `spec.tests_to_change` of the pinned version, or named by one of the sub-ticket's `(added by <ID>)` lines that `run start` checked (`existing test <p> modified; not in Tests to change of pinned spec v<N>`); new test file → nothing.
    - **Exception (doc §Harness table piece 7; the only one), two branches:**
      - *retro*: `type: retro`, `parent: null`, every changed path matches a non-test guardrail glob (the doc's list: CI config, AGENTS.md, skills, prompts — `factory/hooks/**`, `paths.yaml`, `identities.yaml`, `factory/workflows/**` are protected, S5) → conditions become `ci PASS` + head contains main + `approvals/<ID>/guardrail-H.yaml` (human-pushed).
      - *revert*: `type: revert`, `parent: null`, `reverted_head: X` the `head` of a `merged` ticket `T` whose record holds `merge: {base_before: B, main_after: A}` (written by `factory merge`, G), the branch human-pushed (rule 1: no role may push `revert/*`), and `git diff old H` equals `git diff A B` — the inverse of that change proposal's diff, main-before-merge against main-after-merge (E5: a clean `git revert` produces exactly this patch and an extra hunk breaks it) → the same three conditions. Piece 8 on a revert: files present in `A` and absent in `B` (files the reverted PR added) and the tests `T`'s pinned spec listed under "Tests to change" are exempt, `approvals/<ID>/guardrail-H.yaml` being the piece-8 row for them; any other existing test modified or deleted → the normal piece-8 refusal.
@@ -272,7 +272,7 @@ Both scripts are plain JS per E7; they hold the routing, the join and the round
 
 **STATUS parser** (`factory/status.py`, used by `run finish` and `results record`; doc §Routing rules): the **last** line matching `^STATUS:\s*(\S+)` gives the STATUS. CONFIDENCE is the first line after it matching `^CONFIDENCE:`, and ESCALATIONS the first line after that matching `^ESCALATIONS:`; lines between labelled lines are continuation (a wrapped CONFIDENCE reason, commentary between STATUS and CONFIDENCE), never a parse failure. No `CONFIDENCE:` line after the last STATUS, or no `ESCALATIONS:` line after that CONFIDENCE → parse failure → unknown STATUS. The **head** is the rest of the `ESCALATIONS:` line, trimmed; the list is the head plus every non-blank line after it to EOF, each item as written (a leading `- ` or `* ` marker stripped, item 8). A **`none` head** matches `(?i)^none\s*($|[.,;:—–-])`: `none` in any case, then end of line or punctuation, never a space and a word, so `none`, `none.` and `none. The boundary was observed` are `none` heads and `Nonetheless …`, `None of …` are not. The list is empty iff nothing non-blank follows the head and the head is empty or a `none` head; a `none` head with prose after it on its line therefore routes as no escalation, and `run finish` writes that head verbatim to the run's `meta.yaml` as `escalations_note:` (written only when the list is empty and prose follows the `none` head; every other shape, including bare `none` and a `none` head with lines below it, writes `null`) so an auditor reads it with the run. A `none` head followed by any further non-blank line is a real list, every line from the head on an item, verbatim (a wrapped `none` prose line is such a line: when the parser is unsure, the text goes to the human queue). The parser reads no severities: doc §Human gates' rule that REVISE and REQUEST-CHANGES carry at least one BLOCKING finding is the checker's to keep, and every stub that models them (items 38, 44, 46) includes a BLOCKING line.
 
-Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start … --model MODELS[role]` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, model: MODELS[role], label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; **KILLED condition** `out === null || out.trim() === ''` (I.5) → clerk `factory run finish RUN --status-override KILLED`; else clerk `factory run finish RUN --output-file -` with `out`. **A thrown `agent()`** (stub or real call) is finished the same way, clerk `factory run finish RUN --status-override KILLED` (in `build.js`, then clerk `factory run cleanup RUN` for a reviewer or verifier), and parks the ticket `agent call failed: <role>: <error>` with the run id as outputs; `runRole` returns `null`, on which every caller returns. The clerk returns only `{stdout, exit, stderr}`; the script parses `run_id` from `run start`'s JSON and `{status, escalations}` from `run finish`'s. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the KILLED seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.
+Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start … --model MODELS[role]` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return; in `build.js`, a refusal whose JSON `error` starts `BLOCKED ` parks with that error verbatim instead, so `resolve --ruling` applies); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, model: MODELS[role], label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; **KILLED condition** `out === null || out.trim() === ''` (I.5) → clerk `factory run finish RUN --status-override KILLED`; else clerk `factory run finish RUN --output-file -` with `out`. **A thrown `agent()`** (stub or real call) is finished the same way, clerk `factory run finish RUN --status-override KILLED` (in `build.js`, then clerk `factory run cleanup RUN` for a reviewer or verifier), and parks the ticket `agent call failed: <role>: <error>` with the run id as outputs; `runRole` returns `null`, on which every caller returns. The clerk returns only `{stdout, exit, stderr}`; the script parses `run_id` from `run start`'s JSON and `{status, escalations}` from `run finish`'s. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the KILLED seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.
 
 `intake.js` (`args: {ticket, stubs?}`):
 1. `phase('Triage')`: `runRole('triage', …)` with input = request, answers appended (+ after an `--answer`: Triage's previous output, K); `ACCEPT` → clerk `transition --to ready-for-spec-writer` (title/type from the output); `REJECT` → `closed`; `NEEDS-HUMAN` → `park --question`; `CLARIFY` → `transition --to waiting-requester` + clerk `factory reply ID --file -` (piece 9: writes `<source dir>/<file>.reply.md` next to the request, appends to `queue.md`, event `reply.sent`); then **return**. Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'` + `harness-bug` event; always return.
diff --git a/docs/changelog.md b/docs/changelog.md
index 0f39316..7e4a414 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -55,5 +55,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 51. After issue #39 (2026-10-04), a batch of harness defects found in real runs: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested. `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling and the existing sub-tickets listed in its input. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones. A park reason always ends with the failing command's error text. The workflows fall back to the refusal's JSON `error`, then to the exit code. A redispatch sets aside only the rows that did not pass, and the build re-runs only the checkers with no row on the commit. The store's `.gitattributes` marks run records `-whitespace`, written by `init` and `run start`. `init` refuses to create an instance on a throwaway store, and a missing `context.md` refuses a compose with exit 2. A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory.
 52. After issue #45 (2026-10-04), where a spec writer's test run executed `init` from inside its scratch directory and initialised this repository's live store, writing a spec store, `decisions.md` and six agent files: the store CLI fences an instance's own store. A write run from inside the store's `runs/` or `worktrees/` is refused, with or without the marker and with or without a run in flight. While any run is in flight on the store, a write without `FACTORY_DISPATCH=1` in its environment is refused. The read-only commands stay open, and any command given `--accept-harness` counts as a write. Both workflow scripts put `FACTORY_DISPATCH=1` in front of every clerk command; the operator puts it in front of one command at a time and never exports it. A refusal is exit 2, writes nothing, and advises a throwaway `FACTORY_STATE` without naming the marker. The fence is checked before the harness lock, so the marker cannot get past the lock. Declined from the request: a preamble line telling roles to use a throwaway store, because the incident came from the test suite rather than a command the role typed; and a tripwire on the store root, because role runs and other tickets' clerk commands legitimately write the store during a run, so a comparison could not tell whose write it saw.
 53. After issue #46 (2026-10-04), where each store commit on the integration branch sent every sub-ticket waiting to merge back for a catch-up merge and a second round of checks that could not change the verdict: the store moves to its own branch, `factory-store`, checked out as a git worktree at the store's path and never merged into the integration branch, so a store commit no longer moves that branch; the merge gate is unchanged. A store path must be one the integration branch has never tracked, because at a once-tracked path a checkout of an older commit overwrites live records and a checkout back deletes them. `init` creates a missing own store as a worktree of an unborn `factory-store` branch, which needs no commit, or checks out the branch where it exists locally or on exactly one remote, which restores the store on a clone, and adds the store to the repo's git exclude file. It refuses when more than one remote carries the branch, naming each, and at a once-tracked path. With `FACTORY_INSTANCE` unset it refuses from inside the store checkout, on its branch or on a detached HEAD, so it can no longer build a phantom instance inside the live store; a separate repository under a run's scratch directory still gets its own instance. Every refusal comes before the first write. An existing store that is a plain directory is left alone, and `init` reports `store_branch` in its JSON. A new command, `factory store migrate --to PATH`, moves such a store: it refuses, writing nothing, unless the store in use is the instance's own and not yet on its branch, no `factory-store` branch exists, the integration branch is checked out, no run is in flight, no git worktree lies under the store, every store file is committed, PATH does not exist, lies outside the old store and was never tracked, and `instance.yaml` has a `state_dir:` line; it then starts `factory-store` at one commit whose tree is the store as last committed and whose message names that commit, checks it out at PATH, copies the files git ignores there and verifies them byte for byte, undoing its own worktree and branch and exiting 1 on a mismatch, and only then untracks and deletes the old directory, adds PATH to the exclude file and rewrites only the value of `state_dir`; it commits and pushes nothing.
+54. After issue #40 (2026-10-04), where sub-tickets parked for three causes that were visible when the work was planned or specified: a NEW check copied from the whole spec already passed at the sub-ticket's own start; an implementer could not change a test an earlier sibling sub-ticket had added to pin its interim behaviour, because only the spec gate's "Tests to change" list authorized a test edit and that test did not exist at the gate; and a spec's Decision overturned an existing test that nobody listed. The planner labels each check NEW or REGRESSION against the sub-ticket's own base, the integration branch with its dependencies merged, not by the parent's label. An earlier sibling names the new test files a later sibling will break under "Interim tests", which the harness does not read. A sub-ticket's "Tests to change" may list a test file an earlier sibling added, as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. Before each implementer run, `run start` checks in git that the file was absent at the parent's base and was first added inside a merged sibling's recorded merge; otherwise it refuses with exit 2, writing nothing, with an error that starts `BLOCKED from harness:`, and the build parks the sub-ticket with that error so `resolve --ruling` returns it to its implementer. The preamble and the code reviewer accept such a checked entry. The spec writer lists the tests each behaviour-changing Decision overturns, and critic rubric 1 makes a missing one a finding. A test that existed before the parent's first merge still needs the pinned spec's list. Rejected: letting the implementer edit a test on its own judgement.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 2f9781d..f08bbcc 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -43,7 +43,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | 5 | Change proposal | A unit of review: a branch, its base, its head commit, and a place for the PR description and findings. Approvals attach to the head commit. Fix rounds push to the same branch, which is the ticket's identity | Pull requests | A branch naming convention (`ticket/<id>`) plus a record in the ticket store holding base, head SHA, and the description. GitLab MRs or Gerrit changes are direct equivalents |
 | 6 | Commit-bound results | Reviewer, verifier, and CI results are stored against a specific head SHA. A new push makes prior results stale; a result arriving for a head that is no longer current is discarded | Check runs and commit statuses; required checks re-run on push | A `results` table keyed by `(head_sha, role)`. The merge condition queries the *current* head only, so stale rows never match |
 | 7 | Merge gate | Nothing reaches main without CI green, APPROVE and VERIFIED on the current head, a head that contains current main, and a human approval record where piece 8 requires it. A bug in a prompt cannot bypass this. One exception, stated here and nowhere else, for two kinds of PR with no sub-ticket: a retro PR whose diff touches only non-test guardrail paths, and a human-authored revert whose diff the gate verifies is exactly the inverse of one merged change proposal's diff (main before that merge against main after it, both recorded in the store at merge time). Either merges on CI green, head contains main, and a human approval on that head recorded under the guardrail-changes gate; the human reads the whole diff, which stands in for APPROVE and VERIFIED. A no-sub-ticket PR that fails this test is closed and logged to the human queue | Branch protection with required checks and required reviews. Required checks cannot be waived per PR, so the exception needs a harness-emitted check that reports success for exception PRs | A server-side pre-receive hook on main that checks the results table, or a single merge bot that alone can write to main and checks the conditions before fast-forwarding. Either works; the hook is stricter |
-| 8 | Guardrail and protected paths | If the diff touches a guardrail or protected path, the merge gate requires an approval row signed by a human identity. For existing tests, the spec gate's approval of "Tests to change" is that row for exactly the tests listed; any other guardrail or protected path needs a human approval on the PR itself. The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it. | CODEOWNERS with required owner review for CI config, AGENTS.md, skills, prompts, and protected paths. Not for tests: CODEOWNERS fires on added files too. Existing tests get a required check that fails when a test file is modified or deleted and not in the pinned spec's "Tests to change" (on a revert: files the reverted PR added and the tests its pinned spec listed under "Tests to change" are exempt, and the revert's human approval is the piece-8 row for them) | A path list checked in the merge gate, with the same modified-or-deleted rule for test files. Keep the list in the repo under CI config, so it is itself a guardrail path |
+| 8 | Guardrail and protected paths | If the diff touches a guardrail or protected path, the merge gate requires an approval row signed by a human identity. For existing tests, the spec gate's approval of "Tests to change" is that row for exactly the tests listed. A test file an earlier sibling sub-ticket of the same parent added is also covered when the sub-ticket lists it as added by that sibling and the sibling-tests check has passed (Tests a sibling added, below); any other guardrail or protected path needs a human approval on the PR itself. The harness code (its package, entry point, agent templates and dependency lock) is itself a protected path in the repo that holds it. | CODEOWNERS with required owner review for CI config, AGENTS.md, skills, prompts, and protected paths. Not for tests: CODEOWNERS fires on added files too. Existing tests get a required check that fails when a test file is modified or deleted and not in the pinned spec's "Tests to change" or among the sub-ticket's checked sibling entries (on a revert: files the reverted PR added and the tests its pinned spec listed under "Tests to change" are exempt, and the revert's human approval is the piece-8 row for them) | A path list checked in the merge gate, with the same modified-or-deleted rule for test files. Keep the list in the repo under CI config, so it is itself a guardrail path |
 | 9 | Human surface | Where people approve specs, answer escalations, review protected PRs, reply to requesters, and read the weekly audit sample. Every decision writes back to the store as a record: who, when, which spec version or head SHA | Issue comments, PR reviews, approvals | The tracker's UI plus notifications (Slack, email) with links. The approval must be a stored, attributable record the merge gate can check, not a chat message |
 | 10 | Audit log | Every transition, every agent output, every human decision, append-only. The weekly audit and the retro read from here | Issue and PR timelines, Actions logs | An append-only table or log stream. Store full agent outputs as artifacts keyed by run id. If it isn't logged, the retro can't see it |
 | 11 | Gate runner | Runs `{gate commands}` (build, lint, typecheck, tests) on a head SHA and records PASS/FAIL against it (piece 6) | Actions CI | Any CI. Without one, the verifier runs the gates as step 4 of its prompt, and its "Gate suite" line is recorded as the CI result. Separate CI is better because it isn't an agent |
@@ -53,6 +53,8 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Tripwire on live files.** An instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list. A `~/` entry means the account's home directory, never the `HOME` variable, so a run under a throwaway `HOME` still watches the real files. The lists hold files only: a directory, or an entry that is neither absolute nor `~/`, refuses `run start`. `run start` records a SHA-256 of each listed file, or that it is absent, in a baseline in the run's directory, which the store's `.gitignore` excludes so no store commit carries a digest of a live secret. The run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A file created, deleted or modified counts as changed. A changed `park` file parks the ticket with the reason `tripwire: <files> changed during <run>`. The reason says "during", not "by", because runs on other tickets and the operator's own edits can overlap a run, and the tripwire cannot tell them apart. On a ticket already parked or closed, the same reason is queued as an escalation instead. A changed `escalate` file queues an escalation and the run goes on; that list is for files with legitimate outside writers. No event, reason or output names more than a file's path: nothing prints a file's contents. The workflow scripts stop on a `run finish` that parked the ticket, instead of routing on the role's STATUS. The tripwire detects a write after the fact; it does not prevent one.
 
+**Tests a sibling added.** A sub-ticket's "Tests to change" may list a test file that an earlier sibling sub-ticket of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The planner writes these lines, so the spec gate never saw them; the harness checks them instead. Before each implementer run of a sub-ticket, `run start` reads the lines of that form inside the sub-ticket's "Tests to change" field, and nowhere else, and checks each file, not the test function. The file passes when it is absent at the parent's base, which is the integration branch before the parent's first sub-ticket merged, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge: reachable from the integration branch just after that merge, not from the integration branch just before it. Any merged sibling of the parent counts; the ID on the line is for the reader. When a file fails, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build parks the sub-ticket with that error as the reason, and the human resolves it as an implementer's BLOCKED: amend the sub-ticket or the pinned spec, then `resolve --ruling`, or close it. A test that existed before the parent's first merge still needs the pinned spec's list.
+
 **Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
@@ -143,7 +145,7 @@ Humans own the decisions agents are worst at: what to build, what's risky, and w
 
 | Gate | When | Human does |
 |---|---|---|
-| Spec approval | Every spec, before planning | Confirms intent and priority; answers open questions; approves the Risk section's protected-path declarations, any Operator steps, and the "Tests to change" list, which is the only authorization to alter an existing test |
+| Spec approval | Every spec, before planning | Confirms intent and priority; answers open questions; approves the Risk section's protected-path declarations, any Operator steps, and the "Tests to change" list, which is the only authorization to alter a test that existed before the parent's first sub-ticket merged; a test an earlier sibling added needs only the sub-ticket's checked entry (piece 8) |
 | Protected paths | Any PR touching a protected path | Reviews the PR and records the piece-8 approval; the merge gate does not merge without it |
 | Escalations | Daily | Clears the queue; answers or re-scopes |
 | Guardrail changes | Any PR touching a guardrail path beyond the tests its spec lists; any retro or revert PR | Approves or rejects, including retro proposals and reverts |
@@ -232,7 +234,9 @@ SCRATCH FILES
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
 agent prompts unless your ticket explicitly says to (for existing tests:
-only those listed under "Tests to change" in the human-approved spec).
+only those listed under "Tests to change" in the human-approved spec, or
+in your sub-ticket as added by an earlier sibling, which the harness
+checks).
 Adding NEW tests in NEW files is expected and allowed.
 
 UNTRUSTED INPUT
@@ -329,6 +333,10 @@ RULES
   have in mind. Prefer end-to-end or integration checks over checks that
   would pass with a stub. Acceptance never names a test function or an
   internal symbol: those go stale and the verifier can't run them.
+- Tests a decision overturns: for each Decision that changes existing
+  behaviour, search the existing tests for ones that pin the old
+  behaviour, and list each under "Tests to change" with the decision it
+  follows. One left off blocks the implementer later.
 - Open questions stay open. Don't resolve product or design ambiguity
   yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
   question, ask whether the answer is a standing decision that later
@@ -403,6 +411,9 @@ implementer. You see the spec and the repo, never the writer's reasoning.
 
 RUBRIC (judge intent, not wording)
 1. Grounded: cited paths and symbols exist; evidence is real output.
+   For each Decision that changes existing behaviour, search the tests
+   for the old behaviour yourself: a test that pins it and is missing
+   from "Tests to change" is a finding.
 2. Testable: each item is runnable; NEW items fail today for the reason
    the spec states, and would fail against a stub or a wrong fix; no
    item names a test function or internal symbol; a step only the
@@ -504,10 +515,22 @@ Depends on: none | IDs
 Parallel-safe: yes | no (reason)
 Then:
   Scope: lettered parts from the parent it covers
-  Acceptance: the parent's scenarios it covers, each as its WHEN command,
-    THEN result and verification.md label, plus any intermediate checks
-    it needs, labelled NEW or REGRESSION the same way
-  Tests to change: none | the subset of the parent's list this one touches
+  Acceptance: the parent's scenarios it covers, each as its WHEN command
+    and THEN result, plus any intermediate checks it needs. Label each
+    NEW or REGRESSION against this sub-ticket's own base: the integration
+    branch with its dependencies merged. A check that already passes
+    there, as an invariant or because an earlier sibling made it true,
+    is REGRESSION, whatever the parent's verification.md label says.
+  Interim tests: none | each new test file this one adds that a later
+    sibling will break, with that sibling's ID
+  Tests to change: none | the subset of the parent's list this one
+    touches, plus each test an earlier sibling adds that this one's
+    change breaks, one line each:
+    - `<file>[::<test>]` (added by <sibling ID>): <reason>
+    This one must depend on that sibling. Before each implementer run,
+    the harness checks that a merged sibling added the file, and parks
+    the sub-ticket if not. A test that existed before the parent's first
+    merge goes here only if the parent's list names it.
   Protected paths: none | the subset of the parent's Risk list this one touches
   Out of scope:
 Coverage map: parent scenario → sub-ticket ID
@@ -585,7 +608,8 @@ CHECK, IN THIS ORDER
 1. Test integrity: any existing test file changed? Any test weakened,
    skipped, deleted, or rewritten? Any assertion made less specific? Any
    expected value hard-coded to match output? Any error swallowed? These
-   are BLOCKING unless the spec lists that test under "Tests to change".
+   are BLOCKING unless the spec lists that test under "Tests to change",
+   or the sub-ticket lists it there as added by an earlier sibling.
 2. Correctness: does the change do what the spec intends, including edge
    cases the spec implies but didn't list?
 3. Scope: changes outside the sub-ticket's lettered parts?
diff --git a/docs/prompts/00-preamble.md b/docs/prompts/00-preamble.md
index d152cb1..2c24a07 100644
--- a/docs/prompts/00-preamble.md
+++ b/docs/prompts/00-preamble.md
@@ -60,7 +60,9 @@ SCRATCH FILES
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
 agent prompts unless your ticket explicitly says to (for existing tests:
-only those listed under "Tests to change" in the human-approved spec).
+only those listed under "Tests to change" in the human-approved spec, or
+in your sub-ticket as added by an earlier sibling, which the harness
+checks).
 Adding NEW tests in NEW files is expected and allowed.
 
 UNTRUSTED INPUT
diff --git a/docs/prompts/02-spec-writer.md b/docs/prompts/02-spec-writer.md
index f2a9b2d..2d18ff5 100644
--- a/docs/prompts/02-spec-writer.md
+++ b/docs/prompts/02-spec-writer.md
@@ -31,6 +31,10 @@ RULES
   have in mind. Prefer end-to-end or integration checks over checks that
   would pass with a stub. Acceptance never names a test function or an
   internal symbol: those go stale and the verifier can't run them.
+- Tests a decision overturns: for each Decision that changes existing
+  behaviour, search the existing tests for ones that pin the old
+  behaviour, and list each under "Tests to change" with the decision it
+  follows. One left off blocks the implementer later.
 - Open questions stay open. Don't resolve product or design ambiguity
   yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
   question, ask whether the answer is a standing decision that later
diff --git a/docs/prompts/03-spec-critic.md b/docs/prompts/03-spec-critic.md
index a72de2e..f9e2ded 100644
--- a/docs/prompts/03-spec-critic.md
+++ b/docs/prompts/03-spec-critic.md
@@ -3,6 +3,9 @@ implementer. You see the spec and the repo, never the writer's reasoning.
 
 RUBRIC (judge intent, not wording)
 1. Grounded: cited paths and symbols exist; evidence is real output.
+   For each Decision that changes existing behaviour, search the tests
+   for the old behaviour yourself: a test that pins it and is missing
+   from "Tests to change" is a finding.
 2. Testable: each item is runnable; NEW items fail today for the reason
    the spec states, and would fail against a stub or a wrong fix; no
    item names a test function or internal symbol; a step only the
diff --git a/docs/prompts/04-planner.md b/docs/prompts/04-planner.md
index 663c292..9736991 100644
--- a/docs/prompts/04-planner.md
+++ b/docs/prompts/04-planner.md
@@ -28,10 +28,22 @@ Depends on: none | IDs
 Parallel-safe: yes | no (reason)
 Then:
   Scope: lettered parts from the parent it covers
-  Acceptance: the parent's scenarios it covers, each as its WHEN command,
-    THEN result and verification.md label, plus any intermediate checks
-    it needs, labelled NEW or REGRESSION the same way
-  Tests to change: none | the subset of the parent's list this one touches
+  Acceptance: the parent's scenarios it covers, each as its WHEN command
+    and THEN result, plus any intermediate checks it needs. Label each
+    NEW or REGRESSION against this sub-ticket's own base: the integration
+    branch with its dependencies merged. A check that already passes
+    there, as an invariant or because an earlier sibling made it true,
+    is REGRESSION, whatever the parent's verification.md label says.
+  Interim tests: none | each new test file this one adds that a later
+    sibling will break, with that sibling's ID
+  Tests to change: none | the subset of the parent's list this one
+    touches, plus each test an earlier sibling adds that this one's
+    change breaks, one line each:
+    - `<file>[::<test>]` (added by <sibling ID>): <reason>
+    This one must depend on that sibling. Before each implementer run,
+    the harness checks that a merged sibling added the file, and parks
+    the sub-ticket if not. A test that existed before the parent's first
+    merge goes here only if the parent's list names it.
   Protected paths: none | the subset of the parent's Risk list this one touches
   Out of scope:
 Coverage map: parent scenario → sub-ticket ID
diff --git a/docs/prompts/06-code-reviewer.md b/docs/prompts/06-code-reviewer.md
index 5ab0419..38d5596 100644
--- a/docs/prompts/06-code-reviewer.md
+++ b/docs/prompts/06-code-reviewer.md
@@ -7,7 +7,8 @@ CHECK, IN THIS ORDER
 1. Test integrity: any existing test file changed? Any test weakened,
    skipped, deleted, or rewritten? Any assertion made less specific? Any
    expected value hard-coded to match output? Any error swallowed? These
-   are BLOCKING unless the spec lists that test under "Tests to change".
+   are BLOCKING unless the spec lists that test under "Tests to change",
+   or the sub-ticket lists it there as added by an earlier sibling.
 2. Correctness: does the change do what the spec intends, including edge
    cases the spec implies but didn't list?
 3. Scope: changes outside the sub-ticket's lettered parts?
diff --git a/factory/cli.py b/factory/cli.py
index 23abdcf..803f0e3 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -209,6 +209,8 @@ def run_start(a, root, cfg):
         raise Refused(f"{t['id']} already has a {a.role} run in flight")
     if a.role in ("triage", "spec_writer", "critic", "planner") and t["in_flight"]:
         raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
+    if a.role == "implementer" and t.get("parent"):
+        _check_sibling_tests(root, cfg, t)
     baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
     rid = store.next_run_id(root, a.role)
     model = a.model or cfg["models"][a.role]
@@ -235,6 +237,33 @@ def run_start(a, root, cfg):
     out({"ok": True, "run_id": rid, "role": a.role, "model": model, "worktree": meta.get("worktree"), "head": meta.get("head")})
 
 
+def _check_sibling_tests(root: Path, cfg: dict, t: dict) -> None:
+    """Doc §Harness, "Tests a sibling added": each file the sub-ticket's "Tests to change" lists as
+    added by a sibling must be absent at the parent's base, and first added on the integration
+    branch by a commit inside one merged sibling's recorded merge (reachable from its main_after,
+    not from its base_before). Else refused, so the build parks the sub-ticket as BLOCKED."""
+    sub = root / "specs" / t["id"] / "subticket.md"
+    paths = subtickets.sibling_tests(sub.read_text(encoding="utf-8")) if sub.exists() else []
+    if not paths:
+        return
+    parent = store.load_ticket(root, t["parent"])
+    base = parent.get("parent_base")
+    repo = gitops.repo_root(cfg)
+    tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
+    merges = [s["merge"] for s in store.subtickets_of(root, parent["id"])
+              if s["id"] != t["id"] and s["status"] == "merged"
+              and (s.get("merge") or {}).get("main_after") and s["merge"].get("base_before")]
+    for path in paths:
+        added = gitops.first_added(repo, base, tip, path) if base else None
+        if added and any(gitops.head_contains(repo, m["main_after"], added)
+                         and not gitops.head_contains(repo, m["base_before"], added) for m in merges):
+            continue
+        since = f"since {base[:9]}" if base else "(no sibling has merged)"
+        raise Refused(f"BLOCKED from harness: Tests to change lists {path} as added by a sibling, but no merged "
+                      f"sibling of {parent['id']} added it {since}; list it in the parent spec's Tests to change, "
+                      f"or remove it")
+
+
 def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent_close: bool) -> None:
     """Worktrees for the build roles (build spec I.3, local stand-in): the implementer gets the
     ticket's branch (created from the integration branch at first dispatch); each checker gets a
diff --git a/factory/gitops.py b/factory/gitops.py
index 5f21637..0acc227 100644
--- a/factory/gitops.py
+++ b/factory/gitops.py
@@ -80,6 +80,15 @@ def head_contains(repo: Path, head: str, base: str) -> bool:
     return subprocess.run(["git", "merge-base", "--is-ancestor", base, head], cwd=repo).returncode == 0
 
 
+def first_added(repo: Path, base: str, tip: str, path: str) -> str | None:
+    """The first commit in `base..tip` that added `path`, or None: also None when `path` already
+    existed at `base`. A file added, deleted and added again counts by its first add."""
+    if subprocess.run(["git", "cat-file", "-e", f"{base}:{path}"], cwd=repo, capture_output=True).returncode == 0:
+        return None
+    out = git(repo, "log", "--diff-filter=A", "--reverse", "--format=%H", f"{base}..{tip}", "--", path)
+    return out.splitlines()[0] if out else None
+
+
 def diff(repo: Path, base: str, head: str) -> str:
     return git(repo, "diff", f"{base}...{head}")
 
diff --git a/factory/prompts/critic.md b/factory/prompts/critic.md
index a22c9f0..257d808 100644
--- a/factory/prompts/critic.md
+++ b/factory/prompts/critic.md
@@ -3,6 +3,9 @@ implementer. You see the spec and the repo, never the writer's reasoning.
 
 RUBRIC (judge intent, not wording)
 1. Grounded: cited paths and symbols exist; evidence is real output.
+   For each Decision that changes existing behaviour, search the tests
+   for the old behaviour yourself: a test that pins it and is missing
+   from "Tests to change" is a finding.
 2. Testable: each item is runnable; NEW items fail today for the reason
    the spec states, and would fail against a stub or a wrong fix; no
    item names a test function or internal symbol; a step only the
diff --git a/factory/prompts/planner.md b/factory/prompts/planner.md
index 663c292..9736991 100644
--- a/factory/prompts/planner.md
+++ b/factory/prompts/planner.md
@@ -28,10 +28,22 @@ Depends on: none | IDs
 Parallel-safe: yes | no (reason)
 Then:
   Scope: lettered parts from the parent it covers
-  Acceptance: the parent's scenarios it covers, each as its WHEN command,
-    THEN result and verification.md label, plus any intermediate checks
-    it needs, labelled NEW or REGRESSION the same way
-  Tests to change: none | the subset of the parent's list this one touches
+  Acceptance: the parent's scenarios it covers, each as its WHEN command
+    and THEN result, plus any intermediate checks it needs. Label each
+    NEW or REGRESSION against this sub-ticket's own base: the integration
+    branch with its dependencies merged. A check that already passes
+    there, as an invariant or because an earlier sibling made it true,
+    is REGRESSION, whatever the parent's verification.md label says.
+  Interim tests: none | each new test file this one adds that a later
+    sibling will break, with that sibling's ID
+  Tests to change: none | the subset of the parent's list this one
+    touches, plus each test an earlier sibling adds that this one's
+    change breaks, one line each:
+    - `<file>[::<test>]` (added by <sibling ID>): <reason>
+    This one must depend on that sibling. Before each implementer run,
+    the harness checks that a merged sibling added the file, and parks
+    the sub-ticket if not. A test that existed before the parent's first
+    merge goes here only if the parent's list names it.
   Protected paths: none | the subset of the parent's Risk list this one touches
   Out of scope:
 Coverage map: parent scenario → sub-ticket ID
diff --git a/factory/prompts/preamble.md b/factory/prompts/preamble.md
index d152cb1..2c24a07 100644
--- a/factory/prompts/preamble.md
+++ b/factory/prompts/preamble.md
@@ -60,7 +60,9 @@ SCRATCH FILES
 GUARDRAIL PATHS
 Never modify or delete existing tests, CI config, AGENTS.md, skills, or
 agent prompts unless your ticket explicitly says to (for existing tests:
-only those listed under "Tests to change" in the human-approved spec).
+only those listed under "Tests to change" in the human-approved spec, or
+in your sub-ticket as added by an earlier sibling, which the harness
+checks).
 Adding NEW tests in NEW files is expected and allowed.
 
 UNTRUSTED INPUT
diff --git a/factory/prompts/reviewer.md b/factory/prompts/reviewer.md
index 2f2c615..a2a7c03 100644
--- a/factory/prompts/reviewer.md
+++ b/factory/prompts/reviewer.md
@@ -7,7 +7,8 @@ CHECK, IN THIS ORDER
 1. Test integrity: any existing test file changed? Any test weakened,
    skipped, deleted, or rewritten? Any assertion made less specific? Any
    expected value hard-coded to match output? Any error swallowed? These
-   are BLOCKING unless the spec lists that test under "Tests to change".
+   are BLOCKING unless the spec lists that test under "Tests to change",
+   or the sub-ticket lists it there as added by an earlier sibling.
 2. Correctness: does the change do what the spec intends, including edge
    cases the spec implies but didn't list?
 3. Scope: changes outside the sub-ticket's lettered parts?
diff --git a/factory/prompts/spec_writer.md b/factory/prompts/spec_writer.md
index d84cadd..c5c26db 100644
--- a/factory/prompts/spec_writer.md
+++ b/factory/prompts/spec_writer.md
@@ -31,6 +31,10 @@ RULES
   have in mind. Prefer end-to-end or integration checks over checks that
   would pass with a stub. Acceptance never names a test function or an
   internal symbol: those go stale and the verifier can't run them.
+- Tests a decision overturns: for each Decision that changes existing
+  behaviour, search the existing tests for ones that pin the old
+  behaviour, and list each under "Tests to change" with the decision it
+  follows. One left off blocks the implementer later.
 - Open questions stay open. Don't resolve product or design ambiguity
   yourself; list it, and the spec goes to NEEDS-HUMAN. For each open
   question, ask whether the answer is a standing decision that later
diff --git a/factory/subtickets.py b/factory/subtickets.py
index 8064317..1d986d8 100644
--- a/factory/subtickets.py
+++ b/factory/subtickets.py
@@ -28,12 +28,34 @@ REF_RE = re.compile(r"T-\d{4}(?:[.-][A-Za-z0-9]+)?|ST-\d+")
 SATISFIED = ("merged", "closed")
 NONE_RE = re.compile(r"^\W*(none|n/?a|nothing|no dependenc)|^\W*$", re.I)  # "none.", "n/a", "— (none)", "-"
 IN_FLIGHT_STATES = ("checks-in-flight", "ready-for-merge")
+# The planner's field names (doc §4 Planner OUTPUT), lower case: a line naming one opens that field.
+PLAN_FIELDS = ("scope", "acceptance", "interim tests", "tests to change", "protected paths", "out of scope",
+               "depends on", "parallel-safe", "coverage map")
+SIBLING_TEST_RE = re.compile(r"`([^`\s]+)`\s*\(added by\s+[^)]+\)")
 
 
 def _is_heading(line: str) -> bool:
     return bool(re.match(r"^#{1,4}\s+\S", line))
 
 
+def sibling_tests(text: str) -> list[str]:
+    """The test files a sub-ticket's "Tests to change" field lists as added by an earlier sibling
+    (`` `<file>[::<test>]` (added by <ID>) ``), in order, without repeats. The field runs from its
+    own line to the next plan field or heading; the same form anywhere else is ignored."""
+    paths: list[str] = []
+    inside = False
+    for line in text.splitlines():
+        f = FIELD_RE.match(line)
+        if (f and f.group(1).strip().lower() in PLAN_FIELDS) or _is_heading(line):
+            inside = bool(f) and f.group(1).strip().lower() == "tests to change"
+        if inside:
+            for m in SIBLING_TEST_RE.finditer(line):
+                path = m.group(1).split("::", 1)[0]
+                if path not in paths:
+                    paths.append(path)
+    return paths
+
+
 def parse(planner_output: str, parent: str, existing=()) -> list[dict]:
     """Split a PLANNED planner output into sub-tickets, in plan order. Each: id (<parent>.<n>),
     label (the planner's id), title, depends_on (sibling ids, existing sub-ticket ids, plus other
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index b3b5438..24ebe7a 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -65,7 +65,12 @@ async function park(ticket, reason, outputs, phase) {
 
 async function runRole(role, ticket, phase) {
   const start = await clerk(`${BIN} run start --role ${role} --ticket ${ticket} --model ${MODELS[role]}`, phase, `run start ${role} ${ticket}`)
-  if (!start.ok) { await park(ticket, `harness-bug: run start ${role}: ${start.stderr || ''}`, [], phase); return null }
+  if (!start.ok) {
+    // A refusal that starts `BLOCKED ` is the harness blocking the run (the sibling-tests check): park
+    // with it verbatim, so `resolve --ruling` treats it as an implementer's BLOCKED.
+    const blocked = typeof start.error === 'string' && start.error.startsWith('BLOCKED ')
+    await park(ticket, blocked ? start.error : `harness-bug: run start ${role}: ${start.stderr || ''}`, [], phase); return null
+  }
   const runId = start.run_id
   const comp = await clerk(`${BIN} run compose ${runId}`, phase, `run compose ${role}`)
   if (!comp.ok) { await park(ticket, `harness-bug: run compose ${role}: ${comp.stderr || ''}`, [runId], phase); return null }
diff --git a/tests/factory/test_sibling_tests.py b/tests/factory/test_sibling_tests.py
new file mode 100644
index 0000000..a66bfff
--- /dev/null
+++ b/tests/factory/test_sibling_tests.py
@@ -0,0 +1,231 @@
+"""The sibling-tests check (issue #40, part B): a sub-ticket's "Tests to change" may list a test file
+an earlier sibling of the same parent added, as `` `<file>` (added by <ID>) ``. Before each
+implementer run, `run start` checks in git that a merged sibling's recorded merge added the file;
+otherwise it refuses with an error that starts `BLOCKED from harness: `, writing nothing, and the
+build parks the sub-ticket with that error so `resolve --ruling` returns it to its implementer.
+
+Each case builds the spec's t0022-sib.sh fixture: a throwaway store (FACTORY_STATE) whose parent
+T-0001 is planned as ST-1 and ST-2, and a scratch target repository (FACTORY_REPO) whose main holds
+tests/test_old.py from before the plan, tests/test_interim.py from ST-1's recorded merge, and
+tests/test_operator.py from a later direct commit that is no sibling's merge.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+
+PLAN = """ST-1 / Interim
+Depends on: none
+Parallel-safe: yes
+Interim tests: `tests/test_interim.py`, broken by ST-2
+
+ST-2 / Final
+Depends on: ST-1
+Parallel-safe: yes
+Scope: B, which reads `tests/test_old.py` (added by the base commit)
+Tests to change:
+- `{path}` (added by ST-1): ST-2 replaces the interim behaviour
+Protected paths: none
+"""
+
+# Drives factory/workflows/build.js on parent T-0001: each clerk command runs for real, each role run
+# returns an empty output (a killed run). Prints each park as `park <id>: <reason>`.
+BUILD_DRIVER = r"""
+import { readFileSync } from 'node:fs'
+import { spawnSync } from 'node:child_process'
+const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
+const agent = async (prompt) => {
+  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
+  if (!m) return ''
+  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
+  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
+}
+const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
+const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
+await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
+  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
+"""
+
+
+class Fixture:
+    def __init__(self, tmp_path: Path):
+        self.tmp = tmp_path
+        self.store = tmp_path / "store"
+        self.target = tmp_path / "t"
+        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_REPO": str(self.target),
+                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def git(self, *argv: str) -> str:
+        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=self.target,
+                            capture_output=True, text=True, check=True)
+        return cp.stdout.strip()
+
+    def commit(self, msg: str, **files: str | None) -> str:
+        for name, body in files.items():
+            p = self.target / "tests" / f"{name}.py"
+            if body is None:
+                p.unlink()
+            else:
+                p.parent.mkdir(parents=True, exist_ok=True)
+                p.write_text(body)
+        self.git("add", "-A")
+        self.git("commit", "-qm", msg)
+        return self.git("rev-parse", "HEAD")
+
+    def status(self, tid: str) -> str:
+        return yaml.safe_load((self.store / "tickets" / f"{tid}.yaml").read_text())["status"]
+
+    def runs(self) -> list[str]:
+        d = self.store / "runs"
+        return sorted(p.name for p in d.iterdir()) if d.exists() else []
+
+    def branch(self) -> str:
+        return self.git("branch", "--list", "factory/T-0001.2")
+
+
+def build(tmp_path: Path, path: str, merged: bool = True, readd: bool = False, plan_text: str | None = None) -> Fixture:
+    """The t0022-sib.sh fixture with `path` listed under ST-2's Tests to change. `merged=False` leaves
+    T-0001.1 unmerged and the parent with no parent_base. `readd=True` adds two direct commits after
+    ST-1's merge: one deletes tests/test_interim.py, the next adds it again. `plan_text` replaces the
+    plan."""
+    f = Fixture(tmp_path)
+    req, spec = tmp_path / "req.md", tmp_path / "spec.md"
+    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
+    spec.write_text("## Problem\nx\n")
+    f.ok("ticket", "new", "--file", str(req))
+    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+    f.ok("spec", "add", "T-0001", "--file", str(spec))
+    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+    f.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+    f.ok("approve-spec", "T-0001")
+    subprocess.run(["git", "init", "-q", "-b", "main", str(f.target)], check=True)
+    base = f.commit("base", test_old="def test_old(): pass\n")
+    f.git("checkout", "-qb", "sib")
+    f.commit("interim", test_interim="def test_interim(): pass\n")
+    f.git("checkout", "-q", "main")
+    f.git("merge", "-q", "--no-ff", "-m", "Merge ST-1", "sib")
+    after = f.git("rev-parse", "HEAD")
+    f.commit("operator", test_operator="def test_operator(): pass\n")
+    if readd:
+        f.commit("drop interim", test_interim=None)
+        f.commit("re-add interim", test_interim="def test_interim(): assert True\n")
+    plan = tmp_path / "plan.md"
+    plan.write_text(plan_text or PLAN.format(path=path))
+    f.ok("subticket", "add", "T-0001", "--file", str(plan))
+    f.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+    if merged:
+        f.ok("ticket", "set", "T-0001.1", "status=merged", f"merge.base_before='{base}'", f"merge.main_after='{after}'")
+        f.ok("ticket", "set", "T-0001", f"parent_base='{base}'")
+    f.ok("ticket", "set", "T-0001.2", "status=ready-for-implementer")
+    return f
+
+
+def start(f: Fixture) -> subprocess.CompletedProcess:
+    return f.cli("run", "start", "--role", "implementer", "--ticket", "T-0001.2")
+
+
+def assert_refused(f: Fixture, cp: subprocess.CompletedProcess, path: str) -> str:
+    assert cp.returncode == 2, cp.stderr
+    error = json.loads(cp.stdout.strip().splitlines()[-1])["error"]
+    assert error.startswith("BLOCKED from harness: ") and path in error and "T-0001" in error
+    assert f.runs() == [] and f.branch() == "" and f.status("T-0001.2") == "ready-for-implementer"
+    assert yaml.safe_load((f.store / "tickets" / "T-0001.2.yaml").read_text())["in_flight"] == []
+    return error
+
+
+@pytest.mark.parametrize("path", ["tests/test_interim.py", "tests/test_interim.py::test_interim"])
+def test_a_test_file_a_merged_sibling_added_may_be_listed_and_a_mention_outside_the_field_is_ignored(tmp_path, path):
+    f = build(tmp_path, path)
+    cp = start(f)
+    assert cp.returncode == 0, cp.stderr
+    assert f.status("T-0001.2") == "ready-for-implementer"
+    assert [r for r in f.runs() if r.endswith("-implementer")] != []
+
+
+@pytest.mark.parametrize("path", ["tests/test_old.py", "tests/test_operator.py", "tests/test_never.py"])
+def test_a_listed_test_that_predates_the_plan_came_from_no_sibling_or_was_never_added_is_refused(tmp_path, path):
+    f = build(tmp_path, path)
+    error = assert_refused(f, start(f), path)
+    assert "since " in error
+
+
+def test_a_listed_test_is_refused_while_no_sibling_has_merged(tmp_path):
+    f = build(tmp_path, "tests/test_interim.py", merged=False)
+    error = assert_refused(f, start(f), "tests/test_interim.py")
+    assert "(no sibling has merged)" in error
+
+
+def test_a_file_a_sibling_added_then_deleted_and_re_added_counts_by_its_first_add(tmp_path):
+    f = build(tmp_path, "tests/test_interim.py", readd=True)
+    cp = start(f)
+    assert cp.returncode == 0, cp.stderr
+
+
+def test_the_build_parks_the_blocked_sub_ticket_with_the_harness_reason_and_a_ruling_sends_it_back(tmp_path):
+    node = shutil.which("node")
+    assert node, "node must be on PATH: this case runs factory/workflows/build.js"
+    f = build(tmp_path, "tests/test_old.py")
+    driver = tmp_path / "t0022-build.mjs"
+    driver.write_text(BUILD_DRIVER)
+    cp = subprocess.run([node, str(driver)], capture_output=True, text=True, env=f.env, cwd=REPO)
+    parks = [ln for ln in cp.stdout.splitlines() if ln.startswith("park ")]
+    assert len(parks) == 1 and parks[0].startswith("park T-0001.2: BLOCKED from harness: "), cp.stdout + cp.stderr
+    assert "tests/test_old.py" in parks[0]
+    parked = yaml.safe_load((f.store / "tickets" / "T-0001.2.yaml").read_text())
+    assert parked["status"] == "parked" and parked["parked"]["reason"].startswith("BLOCKED from harness: ")
+    ruling = tmp_path / "r.md"
+    ruling.write_text("Ruling: x\n")
+    f.ok("resolve", "T-0001.2", "--ruling", str(ruling))
+    assert f.status("T-0001.2") == "ready-for-implementer"
+
+
+def test_a_mention_in_the_parallel_safe_line_is_not_a_sibling_entry(tmp_path):
+    # The form of a stored sub-ticket (Nanobot T-0002.6): `(added by ...)` in its Parallel-safe line,
+    # here naming a file that predates the plan, which a Tests to change entry would have to refuse.
+    plan = PLAN.split("ST-2 / Final")[0] + (
+        "ST-2 / Final\n"
+        "- Depends on: ST-1\n"
+        "- Parallel-safe: yes with ST-1. It edits `tests/test_old.py` (added by ST-1), and no sibling edits it.\n"
+        "- Tests to change: none\n"
+        "- Protected paths: none\n")
+    f = build(tmp_path, "", plan_text=plan)
+    cp = start(f)
+    assert cp.returncode == 0, cp.stderr
+
+
+def test_the_field_ends_at_the_next_plan_field_or_heading_and_takes_bold_bullets_and_test_suffixes(tmp_path):
+    # Inside the field: two entries for one sibling-added file (bold field name, `::<test>` suffixes)
+    # pass, and a line naming no plan field still belongs to it, so its file is checked and refused.
+    # Outside it: the same form naming a file that predates the plan, in the Protected paths field
+    # before it and in the plan's shared context, which the store appends under a heading.
+    plan = "Grounding: `tests/test_old.py` (added by ST-1)\n\n" + PLAN.split("ST-2 / Final")[0] + (
+        "## ST-2 / Final\n"
+        "**Depends on:** ST-1\n"
+        "**Parallel-safe:** yes\n"
+        "**Protected paths:** `tests/test_old.py` (added by ST-1)\n"
+        "**Tests to change:**\n"
+        "- `tests/test_interim.py::test_interim` (added by ST-1): reason\n"
+        "- `tests/test_interim.py::test_other` (added by ST-1): reason\n"
+        "  Reason: also `tests/test_never.py` (added by ST-1)\n")
+    f = build(tmp_path, "", plan_text=plan)
+    text = (f.store / "specs" / "T-0001.2" / "subticket.md").read_text()
+    assert "## Shared plan context" in text and text.count("`tests/test_old.py` (added by ST-1)") == 2
+    error = assert_refused(f, start(f), "tests/test_never.py")
+    assert "tests/test_old.py" not in error and "tests/test_interim.py" not in error
