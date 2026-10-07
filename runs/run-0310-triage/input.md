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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0310-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0310-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Merge gate does not check protected paths; the reviewer prompt promises a check that local mode never runs"
labels: "harness"
---
**Where:** `factory/cli.py` `merge_cmd` (the merge gate); the reviewer prompt's protected-path check (`factory/prompts/reviewer.md`, `docs/design.md` §6 and `docs/prompts/06-code-reviewer.md`).

**Problem:** the code reviewer's prompt says that a declared protected-path change goes under ESCALATIONS, "the merge gate will require a human approval". The local merge gate checks none of this. It checks the ticket state, that the commit is the branch tip, the three result rows, and that the commit contains the integration branch, but never the paths the change touches. A reviewer's APPROVE with protected paths listed under ESCALATIONS merges anyway, and an undeclared protected-path change merges if both checkers pass it. The factory edits its own harness and prompts, so this is the gate that guards self-modification.

**Evidence:**
- #56 part D (independent review, 2026-10-05).
- Confirmed on 2026-10-04: T-0028.1 (#48) parked because its reviewer escalated `factory/store.py`, a 3-line change the approved spec asks for in part A.5 but whose Risk list does not declare it. The reviewer (run-0298) noted that "no merge check reads the declaration" in local mode.
- T-0029 (#49) had already recorded the same wording mismatch as out of scope.

**Proposed change:**
- A. The approved spec's Risk list is the authorization; the human approves it at the spec gate. Do not add a second approval step.
- B. At merge, the gate lists the paths changed between the parent base and the judged commit. It refuses when a changed path matches `protected_paths` and the pinned spec's Risk list does not declare it, naming each path. The refusal parks for a human ruling (accept under the approved design, or send back).
- C. The reviewer prompt's check 6 is reworded to match: declared paths are listed for the record, an undeclared one is an ESCALATE, and the sentence about the merge gate describes what the gate actually checks.
- D. Tests: an undeclared protected change is refused; a declared one merges; a declaration in a different ticket's spec does not count; a change to the factory's own rules (`instance.yaml`, prompts) is covered.

**Priority:** first after #41.

From #56 part D; filed by the Green session.



## Comments

Related gap found 2026-10-05 while applying the operator's ruling on T-0028.1 (#48): `resolve --ruling` sends any ESCALATE park whose reason doesn't name the planner to `ready-for-critic` (cli.py, `resolve`), including a sub-ticket parked by its code reviewer, which should return to its checks. The ruling had to be placed by hand in `approvals/T-0028.1/ruling-1.md`, followed by `resolve --redispatch`. Fold into this ticket: a reviewer ESCALATE on a sub-ticket resolves back to `checks-in-flight` with the ruling in the checkers' input. (The same hand placement was needed for a budget-kill park on T-0029.1; #41's spec covers that one.)


Issue: https://github.com/danielphang/spec-factory/issues/57


## Answer 1

# T-0033 (#57): answer to triage's question

Option 1: the approved Risk list is the authorization. At merge, the gate refuses any changed protected path that the pinned spec's Risk list does not declare, names each one, and parks the ticket for a human ruling. A declared path merges with no further approval. The design doc's per-PR approval text (lines 21, 23, 48, 154) and the reviewer's check 6 are reworded to match, with a changelog entry and re-copied prompt files.

Standing: yes. It is harness behaviour, so it applies to every instance, including the Nanobot fork.

Source: the operator approved this rule on 2026-10-05, when approving the follow-ups to the #56 review ("Yes, do it"). The rule approved was: "the approved spec's Risk list *is* the authorization. At merge, refuse any changed protected path the pinned spec didn't declare." Measured cost of the alternative: 19 of the last 20 merges here touched a protected path. Because this changes a documented human gate, the spec goes to the operator at the spec gate and is not covered by the pre-approval policy. Option 3 (a per-head approval for paths that change the factory's own rules) remains open to the operator there.

Answered by the Green session on the operator's 2026-10-05 approval.

## Your previous Triage output (the question you asked is answered above)

Type: bug

Title: Merge gate does not check protected paths, and the reviewer prompt promises a check it never runs

Summary: The merge gate is the last check before the harness merges a sub-ticket's branch into `main`. It merges a change to a protected path (a path whose change needs human sign-off, such as the harness's own code and prompts) without looking at which paths the change touches. So a reviewer's APPROVE that lists protected paths under ESCALATIONS still merges. An undeclared protected-path change also merges if both checkers pass it. Because the factory edits its own harness and prompts, this gate is the one meant to guard self-modification. The requester also asks to fold in a related routing bug: `resolve --ruling` on a sub-ticket that its code reviewer parked sends it to the critic, when it should go back to its checks with the ruling in the checkers' input.

Evidence:
- Request #57 (https://github.com/danielphang/spec-factory/issues/57), from #56 part D (independent review, 2026-10-05).
- The gate checks no paths. I read `factory/cli.py` `merge_cmd` (lines 645-687). It checks four things: the ticket state, that the head is the branch tip, the ci PASS / reviewer APPROVE / verifier VERIFIED rows, and that the head contains the integration branch. No line reads the diff's paths, `protected_paths` or the spec's Risk list.
- The prompt promises the check. `factory/prompts/reviewer.md` line 24-27, check 6: "If it does, list them under ESCALATIONS, finish the review, and give the STATUS the code earns; the merge gate will require a human approval." The same text is in `docs/design.md` line 640-643 and `docs/prompts/06-code-reviewer.md`.
- The design doc says the same. `docs/design.md` line 21 lists "a PR touching a protected path" as one of five human gates. Line 48 (piece 8, the guardrail and protected-path piece) and line 154 add that "the merge gate does not merge without" a human approval row.
- The gap was hit in a real run. T-0028.1 (#48) parked on 2026-10-04 because its reviewer (run-0298) escalated a 3-line change to `factory/store.py`. The approved spec asks for that change in part A.5, but its Risk list does not declare the file. The reviewer noted that no merge check reads the declaration.
- The routing bug is real. `factory/cli.py` `resolve`, the `--ruling` branch: any ESCALATE park whose reason does not contain "planner" goes to `ready-for-critic`. T-0028.1's park reason was "ESCALATE from reviewer" (`.factory/store/tickets/T-0028.1.yaml`). The operator's ruling had to be placed by hand at `.factory/store/approvals/T-0028.1/ruling-1.md`. That file says why: "`resolve --ruling` routes a sub-ticket's reviewer escalation to the critic."
- T-0029 (#49) had already recorded the wording mismatch as out of scope.
- Duplicate search: there is none. T-0033 in the store is this request. #56 is the umbrella review it came from. The T-0028 and T-0029 tickets are closed. Neither added a path check to `merge_cmd`.

Assumptions (my inferences, not the requester's statements):
- In the requester's words, "parent base" means the `main` commit the sub-ticket's branch started from. The gate would compare that with the commit it is judging.
- In this repo almost every merge touches a protected path. The command I ran checked the last 20 merge commits on `main` for changes under `factory/`, `bin/factory`, `agents/`, `pyproject.toml`, `uv.lock`, `docs/prompts/` or `.factory/`. It reported "19 of 20 recent merges touch protected paths". This matters for the question below.
- The routing fold-in covers only an ESCALATE raised by a sub-ticket's code reviewer. A budget-kill park (the harness stopping a role that ran over its limit) is #41's, as the comment says.

Question for human:
How should the merge gate decide that a protected-path change may merge? The requester's proposal (part A) changes a documented gate, so I am not accepting it as a plain bug fix. The design doc (lines 21, 23, 48 and 154) asks for a human approval on each PR that touches a protected path. The proposal instead treats approving the spec's Risk list at the spec gate as that approval. The spec gate is the point where the operator signs off a design before any code is written. In this repo 19 of the last 20 merges touched a protected path, so the choice decides whether nearly every merge waits for a human.
1. The approved Risk list is the authorization (the requester's proposal). At merge, the gate refuses any changed protected path that the pinned spec's Risk list does not declare. It names each such path and parks the ticket for a human ruling. A declared path merges with no further approval. The design doc's per-PR gate (lines 21, 23, 48, 154) and reviewer check 6 are reworded to match, with a changelog entry and re-copied prompt files.
2. Build the design as written. Any changed protected path needs a human-signed approval row for that head, whether the spec declares it or not. An undeclared path is also refused. Only the reviewer prompt's wording changes. Nearly every merge in this repo would then wait for the operator.
3. Split by class. Declared paths merge on the Risk approval, as in option 1. But paths that change the factory's own rules (the harness, `.factory/`, prompts) also need a per-head human approval row, as in option 2. The design doc names the classes that need this.

Is the answer a standing decision that later tickets must follow? For example, should every target instance, including the Nanobot fork, use the same rule for protected paths at merge?

Suggested priority (a suggestion only): the requester asks for "first after #41". #41 closed and went live on 2026-10-07 (`dev/issues.md`, runtime `8bfa72d`), so this would be next.

Out-of-scope observations:
- `factory/prompts/reviewer.md` and `docs/prompts/06-code-reviewer.md` differ in one line: line 52 says "After round 2" in one file and "After round {2}" in the other. That is the expected placeholder fill and not a defect. I note it only because a fix for part C re-copies the block.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. I read the gate's code, the design doc's gate text and the T-0028.1 records directly; the conflict between proposal A and design.md lines 21, 48 and 154 is in the text itself.
ESCALATIONS: none
