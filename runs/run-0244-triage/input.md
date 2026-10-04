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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0244-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0244-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Planner and spec writer: per-sub-ticket labels, sibling tests a sub-ticket invalidates, tests a decision overturns"
labels: "harness"
---
**Planner and spec writer: make each sub-ticket's acceptance and test permissions right the first time.** These are prompt changes only. Under the queue policy, the acceptance is an operator-reviewed re-plan before the runtime moves.

**Problem:** sub-tickets park for reasons the planner or spec writer could have foreseen. Each park costs a full role run, plus a human relabel or ruling.
1. **Labels copied from the parent.** The planner labels a check NEW when it already passes at that sub-ticket's own base, either because it is an invariant or because an earlier sibling already made it true. The verifier parks it as a SPEC-DEFECT. Retro trial P1: spec-factory T-0012.2, .5 and .6 (three SPEC-DEFECT parks), T-0012.4 (four vacuous NEW checks), T-0014 and T-0015 pre-dispatch relabels.
2. **A sibling's interim tests become untouchable.** An earlier sub-ticket ships tests that pin its interim behaviour. The next sub-ticket changes that behaviour as the plan intends, but has "Tests to change: none", so it BLOCKs. Evidence: Nanobot T-0002.4 → .5 ("list-edit subcommands not yet available"), 2026-10-04; spec-factory T-0012.3 → .4 (2026-10-03). Retro item 10.
3. **Existing tests pin a behaviour a decision changes.** An upstream test pins exactly the behaviour that an approved decision changes, and the spec's "Tests to change" omits it. Nanobot T-0002.2 (exact CLI metadata vs decision D22), 2026-10-04.

**Proposed change** (prompt text in `docs/design.md` §2 and §4, re-copied to `docs/prompts/` and `factory/prompts/`):
- A. **Planner: labels per sub-ticket.** Each acceptance check is labelled against that sub-ticket's own base: the integration branch with its dependencies merged. A check that already passes there, whether an invariant or something a sibling made true, is REGRESSION, not NEW.
- B. **Planner: sibling tests a sub-ticket invalidates.** For each sub-ticket, list under "Tests to change" every test an earlier sibling adds that this sub-ticket's planned change will break, with the reason. The earlier sibling's sub-ticket text names those tests as interim.
- C. **Spec writer: tests a decision overturns.** For each Decision that changes existing behaviour, find the existing tests that pin the old behaviour and list them under "Tests to change", with the decision they follow. The critic checks this, under rubric 1, grounded.

**Not proposed:** letting the implementer edit a test on its own judgement, even if declared in the PR. That loosens a guardrail, and needs the operator's decision if ever wanted.

**Acceptance:** re-plan Nanobot T-0002 from its approved spec under the new prompts. The plan must list T-0002.4's interim tests under T-0002.5's "Tests to change", and label each check against its own base. Re-run spec writing on T-0002's request, and its "Tests to change" must name the CLI-metadata tests D22 overturns. The operator reviews both side by side before the runtime moves.


---

Operator: spec gate pre-approved under the queue policy (`.factory/answers/queue-preapproval-policy.md`).


## Answer 1

Operator, 2026-10-04 (approving the Green session's recommendations, efficiency ledger and decisions page): option 1.

The planner may list, under a sub-ticket's "Tests to change", tests that an earlier sibling sub-ticket of the same parent added (and only those), with the reason. The harness verifies it: each such test must first appear in a merge of a sibling sub-ticket of this parent (`git log --diff-filter=A` on the integration branch since the parent's base, attributed to a sibling's merge). Otherwise the sub-ticket parks for the operator, as today. Tests that existed before the parent's approved spec still need the spec's own "Tests to change". The gate is pre-approved under the queue policy.

## Your previous Triage output (the question you asked is answered above)

Type: feature (prompt change to the planner and spec writer; harness label)

Title: Planner and spec writer: label checks per sub-ticket, and list the tests a sibling or a decision overturns

Summary:
Sub-tickets park for reasons the planner or spec writer could have foreseen. A park is the harness stopping a ticket until a human relabels it or rules on it, and each one costs a full role run. The requester wants three prompt changes so that each sub-ticket's acceptance labels and test permissions are right the first time:
- A. The planner labels each check NEW (must fail before the change) or REGRESSION (must pass before and after) against that sub-ticket's own base, not by copying the parent's label.
- B. The planner lists, under a sub-ticket's "Tests to change", the tests an earlier sibling sub-ticket adds that this sub-ticket will break. The earlier sibling's text marks those tests as interim.
- C. The spec writer lists the existing tests that each behaviour-changing Decision overturns, and the critic checks for omissions.
The requester rules out letting the implementer edit a test on its own judgement.

Evidence:
I checked each claim against the prompts and the run records.

| Claim | What I found |
|---|---|
| Planner copies the parent's label | `docs/design.md:495`, `docs/prompts/04-planner.md:33`, `factory/prompts/planner.md:33` and the runtime copy all say intermediate checks are "labelled NEW or REGRESSION the same way". No text mentions the sub-ticket's own base. |
| Planner may only take a subset of the parent's tests | Same three files, line 34 (design.md:496): "Tests to change: none \| the subset of the parent's list this one touches". |
| Spec writer has no rule for tests a Decision overturns | `docs/design.md:362` says only "existing tests the intended change breaks, and why". Critic rubric 3 (`docs/design.md:399`) checks that listed tests are really broken. It does not check for missing ones. |
| T-0012.2, .5 and .6 parked as SPEC-DEFECT; T-0012.4 BLOCKED | `.factory/state/tickets/T-0012.{2,5,6}.yaml` each have `reason: SPEC-DEFECT from verifier`. `T-0012.4.yaml:26` has `reason: BLOCKED from implementer`. |
| Nanobot T-0002.5 blocked on T-0002.4's interim tests | `~/dev/nanobot-upstream/.factory/state/runs/run-0147-implementer/output.md:87`: "The 8 failures are the T-0002.4 tests that pin the old "not yet available" behaviour, and they passed on the base." |
| Nanobot T-0002.2 blocked on a test that D22 overturns | `run-0129-implementer/output.md:102`. Line 136 of `test_interactive_agent_routes_a_complete_user_turn` asserts that the CLI's metadata is exactly `{"_wants_stream": True}`. D22 (the CLI marker) adds `_local_cli: True`, "so no correct implementation of D22 passes this assertion unchanged." |

The request names no Nanobot-side commit, and Nanobot carries only `.factory/`. So no as-built fix exists to check. I did not verify the T-0014 and T-0015 relabels or T-0012.4's "four vacuous NEW checks".

No duplicate exists. This is issue #40 (`dev/issues.md:49`, "not in intake"), filed as T-0022. #36/T-0019 part D changed the planner's field-line format, which does not overlap. No other request or spec mentions per-sub-ticket labels or interim tests.

Assumptions:
- (Assumption) Parts A and C change no authority. Under A the planner labels its own checks, as it does now. Under C the human still approves the "Tests to change" list at the spec gate. The queue policy (`.factory/answers/queue-preapproval-policy.md`) pre-approves "per-sub-ticket NEW/REGRESSION labels" by name. It does not name B or C.
- (Assumption) "The integration branch with its dependencies merged" means the base the harness gives the sub-ticket's worktree.
- (Assumption) The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator reviews side by side, is an Operator step, not a runnable Acceptance item. The spec writer will need runnable criteria as well, such as greps of the new prompt text across `docs/design.md`, `docs/prompts/` and `factory/prompts/`. Running the planner against Nanobot's store would need a throwaway copy, because `~/dev/nanobot-upstream/**` is a protected path.
- Suggested priority (a suggestion only): p1. Each avoided park saves a full role run, and T-0002 is the v3.5 port's live ticket.

Question for human:
Part B changes who may authorize a test edit. Today the human-approved spec's "Tests to change" is "the only authorization to alter an existing test" (`docs/design.md:142`). The planner may only take a subset of that list. No human sees the plan before sub-tickets dispatch. The implementer and reviewer for a sub-ticket read both its plan text and the pinned parent spec (`factory/compose.py:175-176`, `192-193`). As far as I can tell, no harness code enforces "Tests to change" (a grep for it under `factory/`, outside `prompts/`, returns nothing). The rule is held only by those roles' prompts. Under B, a planner-written list would authorize changing tests that a human never approved. The request itself treats letting an agent edit a test on its own judgement as loosening a guardrail. Which rule should B follow?

1. **The planner's list is enough, for sibling tests only.** A sub-ticket's "Tests to change" may also name tests that an earlier sibling of the same parent added, and only those. Line 142 is amended to say so. This is the cheapest option, but an agent authorizes the edit and no human sees it. That arguably falls outside the queue policy's "no loosened check".
2. **The planner lists them and a human still approves them.** Any test the plan adds beyond the parent's list goes to the operator once, before dispatch: one approval for the plan, not one park per sub-ticket. Authority stays with the human. This adds a gate step that does not exist today.
3. **No interim tests in committed files.** The planner checks a sibling's interim behaviour only with that sub-ticket's acceptance commands. It never plans a committed test that a later sibling must break. Authority does not change. This narrows how the planner may plan, and may not fit every split.

Is the answer a standing decision that later tickets must follow? It sets who may authorize a test edit after the spec gate, so I expect yes.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. Every prompt line and park cited above was read in the files. The only open point is the authority question in B, which the queue policy does not cover.
ESCALATIONS: Part B would move authority over existing-test edits from the spec gate to the planner, which runs after the gate. The queue policy pre-approves part A only. B needs the operator's ruling (question above) before it is specced as pre-approved.
