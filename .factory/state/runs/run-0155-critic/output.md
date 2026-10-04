## Findings

[BLOCKING] 6 Operator steps, step 1 and step 2
Problem: The operator steps use "runtime", "ci row", "head" and `--accept-harness` with no gloss anywhere in the human-facing sections, so an operator new to this system cannot tell when step 1 is due ("before the runtime moves") or what to compare in it ("the ci row recorded for that head").
Evidence: Read Problem, Evidence, Decisions and Operator steps as the rubric's reader. "Runtime" first appears in Risk ("after the runtime moves to this change"), which is not a human-facing section, and is never defined. "ci row" and "head" appear only in Operator steps step 1 and in Evidence's gate-line bullet (`role: ci, status: FAIL`), neither of which says what a results row or a head is. `--accept-harness` appears once, in step 2, undefined. The writing standard's own rule 2 example is this exact term.
Suggested fix: Open Operator steps with two sentences: "The runtime is the pinned checkout of the harness that runs tickets; a merge into `main` reaches it only when the operator moves it, after which each instance accepts the new revision with `--accept-harness <revision>`. The store keeps one result row per checker for a sub-ticket's latest commit, its head; the ci row is the test-suite verdict read from the verifier's `Gate suite:` line." Then keep the steps as written.

[SHOULD-FIX] 6 Problem, first paragraph
Problem: "store files" and "the Nanobot port" are used before either is introduced; the first is this system's name for its state directory and the second is a project-internal reference (writing standard rule 6).
Evidence: Paragraph 1: "has to dig through store files" and "On the Nanobot port on 2026-10-04 this stalled six approved tickets at once." Paragraph 2 glosses role, run, planner, parent, park and queue, but not store or the port. Not raised as BLOCKING on its own: a technical reader can take "store files" as plain English, and the port is named only as the place the count came from.
Suggested fix: "has to dig through the store, the directory of files where the factory keeps every ticket, run and result" and "On the factory's other instance, the Nanobot repository, this stalled six approved tickets at once on 2026-10-04."

[SHOULD-FIX] 2 specs/harness-docs/spec.md, "The README no longer describes a planning step in intake"
Problem: `grep -c "planning step" README.md` → `0` tests the phrase, not the behaviour; an implementer who rewords lines 83-85 while still describing intake planning passes it, and one who writes the required sentence with the words "planning step" fails it.
Evidence: README line 83 reads "The intake script also contains a planning step, but it only runs when ..."; `grep -c "planning step" README.md` printed `1` today. Design part E asks for "one sentence saying the intake script stops at the spec gate" without naming words the test could check.
Suggested fix: Pin the replacement wording in part E (for example "The intake script stops at the spec gate") and make the scenario check both that sentence's count is `1` and that `intake script also contains` is `0`.

[NIT] 4 Risk, pre-approval paragraph
Problem: The paragraph says the gate is pre-approved under the policy "which names #33", but the policy's #33 entry names only intake Plan removal, build start-up repair and the parent-check park (parts A, B, C1); parts C2 and D ride on the policy's general small-blast-radius rule, not on the #33 line.
Evidence: `.factory/answers/queue-preapproval-policy.md` line 7: "#33 (intake Plan phase removal, build start-up repair, park on parent-check refusal)"; line 6 gives the general rule ("no loosened check, a handful of files, reversible by moving the runtime back"). The request `T-0018.md` does bundle the gate-line part (its lines 26-30), so the scope is the ticket's; only the sentence overstates what the policy names.
Suggested fix: "The policy names #33's parts A, B and C1; C2 and D fall under its small-blast-radius rule (no loosened check, a handful of files, reversible by moving the runtime back)."

## Checks run

- Cited paths and lines: `factory/workflows/intake.js` lines 7, 35, 74-104, 172-189, 191; `factory/workflows/build.js` lines 64-101, 190, 205-213; `factory/cli.py` lines 366-403 (`Path(a.file)` at 381), 480 (the anchored regex), 594 (`has no sub-tickets`), 406-427 (`ready-implementers` keys); `docs/design.md` line 644, `docs/prompts/07-verifier.md` line 37, `factory/prompts/verifier.md` line 38 (step 4 differs from the design block as the spec says; the rest is identical); `README.md` lines 83-85 and 276; `dev/build-harness.spec.md` lines 275, 285, 320; `docs/changelog.md` entry 46 then "Declined:"; `.factory/answers/queue-preapproval-policy.md`. All as cited. HEAD is `429d218`.
- Ran the two gate-line scenarios on today's tree: the four marked forms all gave `FAIL|missing Gate suite line`; the three plain forms gave exactly the three expected lines. The awk block-copy check printed `SAME`. The prompt grep printed `0 0 1` for each of the three files. `grep -c "planning step" README.md` → `1`; `grep -c "heading or emphasis marks" dev/build-harness.spec.md` → `0`.
- Ran three driver scenarios with node v24: "Intake leaves an approved ticket" printed `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`, `run run-0004-planner PLANNED`; "Build creates the missing sub-tickets" printed `returned planned`, no `T-0001.1` line, and grep's "No such file" for `T-0001.1.yaml`; "A failed agent call in intake" printed `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-`, `run run-0001-triage running`. Each NEW item fails today for the reason verification.md states.
- Tests to change: no test under `tests/factory/` reads intake's `meta.phases`, `AGENT_NAME` or the Plan phase; `ready-implementers` tests read `ready` and `resumable` only; `test_coding_standard.py` pins the spec writer, implementer and retro prompts as verbatim copies, not the verifier; existing gate-line fixtures use plain `Gate suite:` lines (`test_shepherd.py` lines 266, 411, 492, 578; `test_results_commit.py` line 22) and still match the proposed regex. "none" holds.
- Decision on `subtickets` key: the existing `ready-implementers` keys cannot distinguish a parent with no sub-tickets from one whose sub-tickets are all merged (merged ids appear in no list), so the new key is needed, not a convenience.
- Scope: four fixes, about 170 lines, one PR; the request bundles all four and the rubric's "lettered part the intent does not need" does not apply.

STATUS: REVISE
CONFIDENCE: high, every cited path and three NEW scenarios were checked by hand on the stated commit; the one BLOCKING is a gloss the operator steps need, not a design defect.
ESCALATIONS: none
