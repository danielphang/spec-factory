Type: bug

Title: Check a spec's format when the spec is added, and send a format error back to the spec writer instead of to the human gate

Summary:
A spec can pass the critic's review and the operator's approval and still be refused by the harness's own format check. The critic is the agent that reviews each spec. The human gate is the step where the operator approves a spec before any code is written. Today the format check runs when the operator approves, not when the spec writer's draft is stored. The requester wants the same check to run when the draft is stored (`bin/factory spec add`). A malformed spec is then refused there with the same message, and no version is stored. Under the operator's Answer 1 (option B), the refusal does not park the ticket. Both runners send the spec back to the spec writer with the format check's message, as a new spec round that counts against the round limit. The ticket parks only when the rounds run out. The requester's acceptance: a spec whose label line wraps before the arrow is refused at `spec add` and adds no version; a valid spec still adds; `approve-spec` keeps its check. The requester offers two optional extras and leaves them to the spec: relaxing the label pattern, or naming the exact label form in the spec writer's prompt.

Evidence:
- Request (issue https://github.com/danielphang/spec-factory/issues/105): for T-0047 on 2026-10-12, the critic approved in round 1 and the operator approved at the gate. Then `approve-spec` refused with `spec not pinned: scenario '…' has no NEW/REGRESSION label in verification.md` for three scenarios. The operator had to redo the approval as a format-only edit, which became spec v2.
- Operator's Answer 1 (2026-10-19): option B, a standing decision. "A form error the harness can detect goes back to the role that produced it, and does not park." The answer names both runners, `factory/drive.py` (the driver) and `factory/workflows/intake.js` (the intake Workflow script), and says the protected paths are declared.
- Checked again on `main` at 3e4705a. `spec add` does no format check: `spec_add` (`factory/cli.py:407`) calls `_add_spec_version` (`factory/common.py:29`), which writes the version and nothing else.
- Checked on `main` at 3e4705a. The check runs in `_refuse_unless_applies` (`factory/human.py:115-120`), which calls `specstore.validate` and then `specstore.applies`. It runs at `approve-spec` (`factory/human.py:142`) and `spec amend` (`factory/human.py:66`), in both cases only when the store has current truth enabled (`specstore.is_active`, `factory/human.py:140` and `:62`). Archive checks separately (`factory/gates.py:293`). The request names `factory/cli.py` for these paths. They have since moved out of `cli.py`, but the claim holds.
- Checked on `main` at 3e4705a. Today a refused `spec add` parks the ticket as a harness bug. The driver does this at `factory/drive.py:294-296`, the intake script at `factory/workflows/intake.js:188-189`. The critic's REVISE route is the existing route back to the spec writer: it raises the round with `spec:+1` and parks as `max rounds` once the limit is reached (`factory/drive.py:318-325`; `factory/workflows/intake.js:204-211`).
- Checked against the store. In `specs/T-0047/v1.md`, lines 500 and 515 put `→ REGRESSION` on a continuation line, not on the line that names the scenario. Line 509 is on one line but reads `→ REGRESSION in its new form.`.
- Checked by running the pattern (previous triage round), and re-read on `main` at 3e4705a, where it is unchanged: `LABEL_RE` (`factory/specstore.py:25`) lets only punctuation follow the label, never a word. So it rejects the line-509 text.
- Checked against the store log. `spec.added` for T-0047 v1 came from run-0478-spec_writer at 17:33, and v2 came from a gate edit at 18:07. A refusal writes no log event, so the log cannot show the refusal message. I took the message from the request.
- Duplicates: none found. T-0057 is this ticket. No open or recently closed ticket covers a format check at `spec add`. The request names no reference-harness commit, so there is no as-built fix to check.

Capabilities: build-dispatch, role-inputs, harness-docs, harness-suite

Assumptions:
- Inferred: the check at `spec add` should be the one `approve-spec` runs, the format check plus the check that the spec's changes apply to current truth. Like `approve-spec`, it should run only when current truth is enabled.
- Inferred: `approve-spec`, `spec amend` and archive keep their checks unchanged.
- Inferred from Answer 1: the spec writer's next run must receive the format check's message, or it cannot fix the error. Today a spec writer's later round gets the critic's verdict. How the message reaches the writer's input is for the spec to settle. It touches role-inputs.
- Inferred from Answer 1: a format refusal in the last allowed round parks the ticket, as the critic's REVISE route does when the rounds run out. The park should carry the format check's message.
- Inferred: a `spec add` refusal for any other reason (not a format or apply error) keeps today's `harness-bug` park. The answer covers form errors the harness can detect, nothing else.
- Open, for the spec to settle. When the spec writer returns NEEDS-HUMAN, both runners store its draft through `spec add` and ignore the result (`factory/drive.py:288`; `factory/workflows/intake.js:184`). That draft has open questions and may not be well formed. If `spec add` refuses it, the draft is not stored for the operator. The likely intent is to skip the check for such drafts, or to keep ignoring the result. The request does not say which.
- Inferred: README's description of how a ticket moves through intake changes, because a new route back to the spec writer is added. The briefing requires README to change in the same ticket.
- Inferred: every option changes protected harness paths (`factory/**`). The spec's Risk section must declare them. Answer 1 says they are declared.
- Suggested priority (a suggestion; priority is the operator's call): medium. Each occurrence costs one gate decision and one gate edit. The request names one occurrence.

Question for human / Missing info / Reason: none. Answer 1 settled the open question.

STATUS: ACCEPT
CONFIDENCE: high. I re-checked every code reference on `main` at 3e4705a, the operator's answer settles the route, and the remaining open point (NEEDS-HUMAN drafts) is a design detail the spec can settle.
ESCALATIONS: none
