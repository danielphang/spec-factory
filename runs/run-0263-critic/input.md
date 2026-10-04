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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0263-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0263-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v1)

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

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
