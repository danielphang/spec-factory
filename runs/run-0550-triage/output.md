Type: bug

Title: Check a spec's format when the spec is added, so a format error reaches the spec writer and not the human gate

Summary:
A spec can pass the critic's review and the operator's approval and still be refused by the harness's own format check. The critic is the agent that reviews each spec. The human gate is the step where the operator approves a spec before any code is written. The format check runs only after the operator approves, not when the spec writer's draft is stored. The requester wants the same check to run when the draft is stored (`bin/factory spec add`). Then a malformed spec is refused there with the same message, no version is stored, and the operator never sees a form error. The requester's acceptance: a spec whose label line wraps before the arrow is refused at `spec add` and adds no version; a valid spec still adds; `approve-spec` keeps its check. Fixing the label pattern itself, or naming the exact form in the spec writer's prompt, is offered as optional and left to the spec.

Evidence:
- Request (issue https://github.com/danielphang/spec-factory/issues/105): for T-0047 on 2026-10-12, the critic approved in round 1 and the operator approved at the gate. Then `approve-spec` refused with `spec not pinned: scenario '…' has no NEW/REGRESSION label in verification.md` for three scenarios. The operator had to redo the approval as a format-only edit, which became spec v2.
- Checked on `main` (788a201). `spec add` does no format check. `spec_add` (`factory/cli.py:407`) calls `_add_spec_version` (`factory/common.py:29`), which writes the version and nothing else.
- Checked on `main`. The check runs at three points: `approve-spec` (`factory/human.py:142`, via `_refuse_unless_applies` at `factory/human.py:115-120`), `spec amend` (`factory/human.py:66`) and archive (`factory/gates.py:297`). `approve-spec` runs it only when the store has current truth enabled (`specstore.is_active`, `factory/human.py:140`). The request names `factory/cli.py` for these paths. They have since moved out of `cli.py`, but the claim holds.
- Checked against the store. In `specs/T-0047/v1.md`, lines 500 and 515 put `→ REGRESSION` on a continuation line, not on the line that names the scenario. Line 509 is on one line but reads `→ REGRESSION in its new form.`.
- Checked by running the pattern. `LABEL_RE` (`factory/specstore.py:25`) rejects the line-509 text. It accepts `- X → REGRESSION` and `- X → REGRESSION. in its new form`: only punctuation may follow the label, never a word.
- Checked against the store log. `spec.added` T-0047 v1 came from run-0478-spec_writer at 17:33. v2 came from a gate edit at 18:07. A refusal writes no log event, so the log cannot show the refusal message itself. I took the message from the request.
- The request names no reference-harness commit. There is no as-built fix to check.

Capabilities: build-dispatch, harness-docs

Assumptions:
- Inferred: the check at `spec add` should be the same one `approve-spec` runs: the format check plus the check that the spec's changes apply to current truth. Like `approve-spec`, it should run only when current truth is enabled.
- Inferred: `approve-spec`, `spec amend` and archive keep their checks unchanged.
- Open, and the spec must settle it. When the spec writer returns NEEDS-HUMAN, the driver stores the spec writer's draft through `spec add` and ignores the result (`factory/drive.py:288`; `factory/workflows/intake.js:184`). That draft has open questions and may not be well formed. If `spec add` refuses it, the draft is not stored for the operator. The likely intent is to skip the check for such drafts, but the request does not say so.
- Suggested priority (a suggestion; priority is the operator's call): medium. Each case costs one gate decision plus one gate edit, and the request names one occurrence.

Question for human:
The request says a refusal at `spec add` would make "the spec writer's run fail the way it fails today for other `spec add` refusals", and that "the writer fixes it in its own round". Today a refused `spec add` does not go back to the spec writer. Both the driver (`factory/drive.py:294-297`) and the intake script (`factory/workflows/intake.js:188-189`) park the ticket as `harness-bug: spec add: …`, so the operator still has to act. Which route should a format refusal take?

- A. Park, as today's route already does. The only change is the refusal at `spec add`. The error reaches the operator before the critic runs, not after the gate, and the operator still re-dispatches by hand. This is the smallest change. It saves the critic run and the gate edit, but not the operator decision.
- B. Send the spec back to the spec writer. The driver and the intake script start a new spec writer run with the validator's message as a new spec round, which counts against the round limit. They park only when the rounds run out. This matches "the writer fixes it in its own round" and removes the operator decision. It needs a new route in both `drive.py` and `intake.js`, and the message must be added to the spec writer's input.
- C. Store the version as today, and give the validator's verdict to the critic. The critic's existing REVISE route then sends the spec back to the spec writer. No new route is needed, but the version is still stored. That contradicts the requester's acceptance ("adds no version").

Is the answer a standing decision that later tickets must follow? For example: "a form error the harness can detect goes back to the role that produced it, and does not park"?

STATUS: NEEDS-HUMAN
CONFIDENCE: high. I checked every code and store claim on `main`, and the request's own premise about the current refusal route is contradicted by `drive.py` and `intake.js`.
ESCALATIONS: The request rests on a premise the code contradicts. It says a refused `spec add` sends the spec writer back to fix the error in its own round. Today such a refusal parks the ticket for the operator (`factory/drive.py:294-297`, `factory/workflows/intake.js:188-189`). Which route a format refusal should take is a design decision, put to the operator above. Every option changes protected harness paths (`factory/**`). The spec's Risk section must declare them.
