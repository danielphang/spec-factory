Type: bug

Title: Spec drift check parks a sub-ticket for its own sibling's merge; no resolve route back from a harness-bug park before the first implementer run

Summary:
The spec drift check falsely parks sub-tickets. This check runs before a sub-ticket's first implementer run. It parks the sub-ticket when a test file changed on the integration branch after its spec was approved. It counts the merges of the sub-ticket's own siblings as drift. Siblings are the other sub-tickets of the same parent ticket, and the plan expects their merges. This happened twice while #65 was being built: T-0040.2 and T-0040.3 were both parked because T-0040.1 had merged and added `tests/factory/test_drive.py`. The requester needs the check to skip a merged sibling's merge commit while still parking for commits from other tickets. The suite should cover a two-part plan in which part A adds a test file and also changes a file the design names, and part B still starts without a park.
The comment adds a second need. A sub-ticket parked with a `harness-bug:` reason before its first implementer run has no `resolve` option that returns it. The operator had to hand-edit the park reason to get T-0040.3 moving again. The requester asks for a resolve route for that case.

Evidence:
- Request: "T-0040.2 (part B) was then parked before its first implementer run with: `BLOCKED from harness: spec drift: tests/factory/test_drive.py changed by 2ad4d8c52 since spec v4 was written at 37848dbb0`." "This is not drift. The plan has part A create that file, and part B's sub-ticket says part B may import from it."
- Verified: `git show --stat 2ad4d8c52` in `~/dev/spec-factory` is "Merge factory/T-0040.1: The driver core and the intake phase (T-0040.1)". It adds `tests/factory/test_drive.py` (303 lines) and changes `factory/cli.py`. So the commit the check blamed is the parent's own sibling merge.
- Verified: `factory/cli.py:316-347` (`_test_drift`) runs `rev-list --first-parent --reverse <integration_head>..<tip>` and flags every test file changed by a commit that also touched a design-named file. It never consults the parent's merged sub-tickets. In contrast, `_check_sibling_tests` (`factory/cli.py:245-269`) reads each merged sibling's `merge.main_after` / `merge.base_before` and treats those commits as expected.
- Verified: `docs/design.md:62` ("Spec drift") gives the test rule with no sibling exception. The build-dispatch requirement at `.factory/store/openspec/specs/build-dispatch/spec.md:243-244` does the same. So both the design and current truth describe the behaviour that produces the false positive, and the fix changes them as well as the code.
- Verified: `.factory/store/tickets/T-0040.3.yaml:26-33` shows the second instance. The reason is `harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/factory/test_drive.py changed by 2ad4d8c52 …; tests/factory/test_drive_build.py changed by 18fbe88ba …`. The original refusal follows it, re-encoded as a Python dict. `18fbe88` is "Merge factory/T-0040.2", another sibling merge. A resolve by `dphang` with `ruling-1.md` then returned the sub-ticket to `ready-for-implementer`.
- Verified: in `factory/cli.py:1183-1185`, `resolve --ruling` refuses unless the park reason starts with `ESCALATE` or `BLOCKED`. In `factory/cli.py:1223-1225`, `--redispatch` refuses unless the park came from `checks-in-flight` or `ready-for-merge`. No route accepts a `harness-bug:` park from `ready-for-implementer`, as the comment says.
- Verified: the driver (`factory/drive.py:179-186`) and `factory/workflows/build.js:79-84` both park a run-start refusal verbatim when its error starts with `BLOCKED `. The `harness-bug:` wrapping on T-0040.3 came from the Workflow script's clerk re-encoding the JSON error. That matches the requester's note that "the clerk half goes away with #65's driver".
- Workaround in use: `resolve <sub> --ruling F`, applied to T-0040.2 and, after a hand correction logged as `park.corrected`, to T-0040.3.
- No Nanobot-side harness fix is cited, and none was checked.
- Duplicates: none. This request is issue #85 in `dev/issues.md:89` ("not in intake (p1, bug)"), and T-0041 is its own ticket. No other ticket in `.factory/store/tickets/` covers the drift false positive.

Capabilities: build-dispatch, human-resolution, harness-docs

Assumptions:
- (Inference) "A merged sibling" means any sub-ticket of the same parent with status `merged` and a recorded `merge.main_after`. This follows the precedent of `_check_sibling_tests`. Whether sub-tickets of a superseded plan also count is for the spec writer to decide.
- (Inference) The design doc's "Spec drift" paragraph, the build-dispatch requirement and `docs/changelog.md` change with the code. The briefing requires this for any change to documented behaviour.
- (Inference) The requester left the shape of the new resolve route open. They said only that one is needed for "a harness-bug park before an implementer run". The spec writer should choose and state it. One option is to widen `--ruling` to accept such a park and return it to `ready-for-implementer`. Another is to widen `--redispatch` to retry from `ready-for-implementer`. Either way, a park that is neither from that state nor a `harness-bug:` park should still be refused as it is today. If the spec writer finds this needs an operator call, it goes to the spec gate as an open question.
- (Inference) The clerk re-encoding in the Workflow scripts is out of scope. The requester says it goes away with the driver, and #89 retires the scripts.
- Suggested priority (suggestion only): p1, matching the index entry. The bug has parked 2 of the 3 sub-tickets of the last multi-part ticket.

Reason: Intent is clear and backed by evidence checked in this checkout. The design choice left open (the form of the resolve route) is small and fits the spec gate. It does not need a product decision before a spec is written.

STATUS: ACCEPT
CONFIDENCE: medium. The drift false positive is confirmed in code, design text and ticket history. The resolve-route half is a less specific request, and its shape is left to the spec writer.
ESCALATIONS: none
