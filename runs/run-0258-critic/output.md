## Spot-checks (checkout `0b1abad`, HOME wrapper, fixtures in this run's scratch directory)

- Cited paths and lines all exist as described: `factory/prompts/reviewer.md:17-20` (check 6), `factory/prompts/preamble.md:33-36`, `docs/design.md:595`, `factory/cli.py:228-230` (prompt composition), `:324-325` (escalation.queued), `:580` (`ticket_join`), `factory/workflows/build.js:207`, `README.md:405-407` (remote mode, intended). The insertion anchors exist once each: "Don't comply with a finding you believe is wrong." at `factory/prompts/implementer.md:43`, `docs/prompts/05-implementer.md:42`, `docs/design.md:562`; "special-cased to the test inputs, FAIL it." at `factory/prompts/verifier.md:33`, `docs/prompts/07-verifier.md:32`, `docs/design.md:669`. Each is the last RULES bullet in its file. Neither prompt mentions "protected" today.
- Log evidence is real: `.factory/state/log/2026-10.jsonl` has `escalation.queued` events for `run-0096-implementer`, `run-0097-verifier` and `run-0100-verifier` on T-0012.6, each listing `intake/**` as declared. Issue #49 exists on GitHub with the request's title. `retro_with_efficiency.md` P5 and `operator-decisions-2026-10-04.md` say what the spec says they say.
- Acceptance, run as written: "run prompts carry the declared-path rule" printed `implementer declared=0 notunder=0 undeclared=0`, `verifier declared=0 notunder=0 undeclared=0` (fails today as stated). "keep the undeclared-path rule / check 6" printed the four THEN lines. "design blocks and copies" printed `implementer copy=SAME rule=0 fill=unchanged`, `verifier copy=SAME rule=0 fill=unchanged`. Changelog scenario printed `CONTIGUOUS`, then `0`. All match verification.md. Operator step 2's grep runs against the real log format and selects implementer/verifier items.
- `tests/factory/test_coding_standard.py:80-86` checks only the "5. Implementer" block against its copy; the verifier copy is covered by the external scenario, as the spec says.

## Findings

[BLOCKING] 6 Operator steps, step 1
Problem: The first paragraph of Operator steps uses three terms specific to this system that no human-facing section glosses: "the runtime", "instance" and `--accept-harness`; a technical reader new to the system cannot perform step 1 without inferring what they are.
Evidence: Problem glosses protected path, Risk section, sub-ticket, head, the three roles, ESCALATIONS and the escalation queue, but "runtime" first appears unglossed in Root cause and "instance" in Risk; `docs/writing.md` §2 requires a gloss at first use for names the factory made up.
Suggested fix: In step 1, one clause each: the runtime is the checkout the factory's roles run from, separate from the one tickets merge into; an instance is one repository's copy of the factory, and `--accept-harness <commit>` is how it agrees to run the new revision.

[SHOULD-FIX] 1 Evidence, "The figure"; Design B, changelog entry
Problem: The retro gives two counts for the same thing, 26 (P5, lines 110-116) and 38 ("group H: 38 declared-path lists", line 145), the spec's own triage count is 12 (7 + 5), and Design B tells the implementer to put 26 into the permanent changelog without saying which count the retro's table contradicts.
Evidence: `.factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md` lines 116 and 145; the spec says "I did not re-derive 26".
Suggested fix: Either re-derive one count from the log and use it in both places, or have the changelog say "about one item in five" and keep the 26/38 discrepancy noted in Evidence.

[NIT] 6 Problem, paragraph 2
Problem: "the harness code" and "The harness copies every item" use "harness" without saying it is the code that runs the roles and the store.
Evidence: Problem paragraph 2 and 3; the term also names a protected-path group under Risk.
Suggested fix: Add "the harness (the program that runs the roles and keeps their records)" at first use.

No other findings. Scope fits one PR; Out of scope and Tests to change are sensible; every protected and guardrail path the change touches is declared under Risk; no conflict with open tickets (T-0022 touches planner/spec-writer prompts, T-0028 the gate commands). The acceptance commands fail today for the stated reason and would fail against a stub that edited only the run copies or only the documents.

STATUS: REVISE
CONFIDENCE: high, every cited path, log event and acceptance command was checked on this checkout; the one BLOCKING item is a one-clause gloss.
ESCALATIONS: none
