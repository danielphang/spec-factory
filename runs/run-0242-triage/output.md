Type: feature

Title: Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels

Summary:
The operator watches factory runs in the Claude Code workflow view, both in the terminal (`/workflows`) and in the mobile app. Every row there names a ticket by its bare id, such as `triage T-0012` or `clerk: run start triage`. The operator cannot remember which id is which task, so each glance means a lookup. The request asks the two workflow scripts, `factory/workflows/intake.js` and `factory/workflows/build.js`, to add a short title beside the id in three places:
- a narrator line at the start of a run giving the ticket, its short title and its state, plus the GitHub issue number when the request names one;
- a narrator line at each step that changes the ticket's state;
- every agent label, including those of the clerk agents that run the store commands.

A narrator line is a `log()` message that the Workflow tool prints above the progress tree. Routing, store calls and STATUS handling must not change. Only the label and log text changes.

Evidence:
- Request: the card reads `factory-intake`, agent rows read `triage T-0012` or `clerk: run start triage`. The operator "reviews on the phone and cannot remember which number is which task. Every glance means looking up `T-0018` or `#31`."
- Operator, 2026-10-04 (relayed by the harness as the user request for this run): "I would like some 1-liner snippet besides just identifiers like "T-0018" or "GH-#31" so i dont have to do the lookup … file it but just get to it."
- I confirmed the current labels on this checkout. The clerk label is built as `` `clerk: ${label}` `` at `factory/workflows/intake.js:54` and `factory/workflows/build.js:45`. The role labels are `` `${role} ${TICKET}` `` and `` `${role} (stub) ${TICKET}` `` (intake.js:97 and :91), and `` `${role} ${ticket}` `` (build.js:88 and :82). None of them carries a title.
- The title is already available to both scripts. intake.js:126 and build.js:198 call `ticket show <id> --json` for the parent ticket, and build.js:126 makes the same call for each sub-ticket. The JSON carries `"title"` (`factory/cli.py:88`).
- One claim in the request does not match the code. The request says "the scripts never call `log()`", but they do: intake.js:72, 112, 113 and 166, and build.js:63, 111, 112, 172, 176 and 232. Those lines name the ticket by bare id only (for example `` `${TICKET} parked: ${reason}` ``) or by run id (`` `${role} ${runId}: ${fin.status}` ``). So the problem stands, and part B of the request means extending these existing lines and adding lines for transitions that do not log yet.
- The card's name and description come from the fixed `meta` literal at the top of each script (intake.js:1-3, build.js:1-3). The request accepts that these cannot change at run time.
- No duplicate. No ticket title under `.factory/state/tickets/` and no row in `dev/issues.md` (issues 1-45) covers workflow labels or narrator lines. This request is ticket T-0026 itself.

Assumptions (my inferences, labelled as such):
- A1 (a gap in how the request can be accepted). The request's acceptance is "a stub-mode run of each workflow (the existing fixtures)". The workflow scripts cannot run under pytest. `tests/factory/test_shepherd.py` lines 9-11 say so and apply the same routing table in Python instead. No test in `tests/factory/` reads a workflow agent label. So a stub-mode run needs the Claude Code Workflow runtime, which is an operator step and not a shell command. The briefing requires acceptance commands that run as written from `~/dev/spec-factory`. I assume the spec writer will add shell checks, such as greps over the two scripts showing every `label:` and `log(` names the ticket's short title. The stub-mode run becomes an Operator step, together with the request's own confirmation that `log()` lines appear in the mobile view. Part D's "the stub-mode tests that read labels" has no such tests to keep passing on this checkout.
- A2 (calls made before the title is known). The first two clerk calls in each script run before the title is known: `config` and `ticket show` itself (intake.js:123 and :126). I assume those two keep their current labels.
- A3 (where the issue number comes from). The request says the GitHub issue number comes from a request header `issue:` or a `#NN` in the title. T-0026's own request has no `issue:` header (`.factory/state/requests/T-0026.md` lines 1-4). `ticket show --json` does not return the request's front matter. So the spec writer has to decide where the script reads the issue number. Any new CLI output field it adds is a store CLI change under `factory/`.
- A4 (a protected path, declared by the request). `factory/workflows/*.js` is a protected harness path. The request names those files as the change, so the spec's Risk section should declare them.
- A5 (no README change). The README does not quote label or log text. Line 487 points at the workflow scripts for "How a ticket moves", which this change leaves alone. So I assume the README needs no change.
- Priority (suggestion only): low risk and small. The operator has pre-approved it and asked for it to be done promptly.

Reason: ACCEPT. The intent is clear: show a short title beside every ticket id in the workflow view. The operator has already decided the product question by pre-approving it. A1-A3 are for the spec writer to settle and need no product call.

STATUS: ACCEPT
CONFIDENCE: high. The labels, the existing `log()` calls and the title source were all checked against this checkout's code. The one gap (A1, a stub-mode run cannot be a shell command) affects how the spec writer frames acceptance, not the intent.
ESCALATIONS: none
