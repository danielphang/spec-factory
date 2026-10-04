## Acceptance

- Implementer and verifier run prompts carry the declared-path rule → NEW. Today it prints `implementer declared=0 notunder=0 undeclared=0`, then `verifier declared=0 notunder=0 undeclared=0`: neither prompt has the rule. I ran this on this checkout at `0b1abad`. On a scratch clone with parts A and B applied and committed, it printed the THEN lines.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → REGRESSION. It printed `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` both on this checkout and on the prototype clone.
- The design blocks and their copies carry the rule and stay in step → NEW. Today it prints `implementer copy=SAME rule=0 fill=unchanged`, then `verifier copy=SAME rule=0 fill=unchanged`: the copies agree, but none carries the rule. On the prototype clone it printed the THEN lines.
- The code reviewer and preamble copies do not change → REGRESSION. It prints `changed=0` on `main`, where the diff is empty, and on the prototype clone.
- The changelog records the declared-path rule in a contiguous entry → NEW. Today it prints `CONTIGUOUS`, then `0`: no numbered entry mentions `#49`. On the prototype clone, with entry 53, it printed the THEN lines.
- The declared-path change adds no whitespace errors → REGRESSION. `git diff --check main...HEAD` exited 0 on the prototype clone.

Every command was run in this round from the repository root under the HOME wrapper from "Running code", with `TMPDIR` set to this run's scratch directory for the fixture. The prototype clone is at `.factory/state/runs/run-0260-spec_writer/scratch/c`, built from `0b1abad` with parts A and B applied and committed. Its harness suite printed `265 passed`. That run used a pytest temporary directory under `/tmp`, as the current-truth suite scenario does.

## Responses

- [BLOCKING] 6, Operator steps step 1: FIXED. Step 1 now says what the runtime is (the checkout at `~/dev/spec-factory-harness` that runs execute from, which a merge does not change), what an instance is (one repository's own setup of the factory, naming this repo's and instance A), and what `--accept-harness <commit>` does (each instance runs only the commit it has accepted and refuses to run until it accepts the new one). The runtime is also glossed at its first use in Root cause, and an instance at its first use in Risk.
- [SHOULD-FIX] 1, the figure: FIXED by re-deriving one count from the log and using it everywhere. Evidence now lists the 10 implementer and verifier runs by number, says how the parser turned them into 30 of 205 items at `0b1abad` (18 implementer, 12 verifier), and records that the retro's 26 (line 116) and 38 (line 145) disagree. The Problem says "one item in seven" instead of "one in five". Design B tells the implementer to use 10 runs and 30 of 205, not 26 of 139, and Decisions records that choice. While checking by hand I also found that implementer runs 0096 and 0099 folded an unrelated flag into their declared-path item. Evidence now says so, and that the new rule still sends such a flag under ESCALATIONS.
- [NIT] 6, Problem, "harness": FIXED. The Problem's term list now opens with "The harness is the program that runs the factory's agents and keeps their records." The preamble is glossed at its first use in Evidence.

## Critic rounds

round 1 · spec v1 · run-0258-critic · REVISE

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

round 2 · spec v2 · run-0266-critic · APPROVE

## Round 2 review (checkout `0b1abad`, HOME wrapper, scratch under this run's directory)

Reviewed: whether the three round-1 findings were resolved, and the text that changed in v2 (Problem paragraphs 1-2 and 4, Evidence "The figure" and the new "One repeat did carry something extra" bullet, Root cause's runtime gloss, the new Decisions bullet on the changelog count, Risk's instance gloss, Operator steps step 1, Design B's count, verification.md's closing paragraph).

## Spot-checks

- The re-derived figure is right. I read `.factory/state/log/2026-10.jsonl` as committed at `0b1abad` with my own Python filter: 126 `escalation.queued` events, 205 items. The implementer and verifier events whose items are declared-path lists are exactly the ten the spec names (0063, 0096, 0099, 0109, 0177; 0064, 0097, 0100, 0110, 0179). Counting only the declared-path lines in those events, and leaving out the unrelated items the spec's Out of scope names (0109's "No undeclared protected path" and "No prompt-injection", 0177's fixture note, 0064's and 0097's out-of-scope remarks), gives 18 implementer and 12 verifier items, 30 in all. 30/205 is 14.6%, which "one in seven" states fairly.
- The extra flag is real: runs 0096 and 0099 each end their declared-path item with "Also flagged: the harness turned an approved and verified head into a fix round", as Evidence now says.
- The 35 queued events with no `run` field are all harness park notices (`factory/store.py:156`: archive, NEEDS-HUMAN, SPEC-DEFECT, budget kill), never a role's ESCALATIONS list, so Operator step 2's grep on `"run": "run-NNNN-(implementer|verifier)"` misses nothing it should catch.
- `--accept-harness <sha>` is the flag README documents (`README.md:215, 231, 345`); step 1's `<commit>` is the same thing.
- Acceptance re-run on this checkout: the changelog scenario printed `CONTIGUOUS`, then `0`; the design-blocks scenario printed `implementer copy=SAME rule=0 fill=unchanged`, then `verifier copy=SAME rule=0 fill=unchanged`. Both match verification.md's "today" lines. The changelog's last entry is 52, so Design B's "53, or 54 if issue #46's entry lands first" is correct.
- The retro's 38 is at `retro_with_efficiency.md:145` as cited. Its 26 is at line 118 ("Incidents: 26 declared-path lists queued by the implementer (16) and the verifier (10) out of 139"), not line 116.
- The prototype clone verification.md points at (`.factory/state/runs/run-0260-spec_writer/scratch/c`) no longer exists; the harness cleared that run's scratch. I could not re-check `265 passed` or "37 added lines across six files". Nothing in Acceptance depends on either figure, and the implementer rebuilds the change from Design A and B, so this is not a finding.

## Prior findings (round 1)

- [BLOCKING] 6, Operator steps step 1: RESOLVED. Step 1 now says what the runtime is (the checkout at `~/dev/spec-factory-harness` that runs execute from, which a merge does not move), what an instance is (one repository's own setup of the factory, naming this repo's and instance A), and what `--accept-harness <commit>` does. The runtime is also glossed at its first use in Root cause and an instance at its first use in Risk. A technical reader new to the system can perform step 1 without inferring anything.
- [SHOULD-FIX] 1, the figure: RESOLVED. One count, re-derived from the log and reproduced here independently, is used in Problem, Evidence, Decisions and Design B; the retro's two contradicting figures are recorded as rejected.
- [NIT] 6, Problem, "harness": RESOLVED. The term list opens with the gloss.

## Findings

[NIT] 1 Evidence, "The figure", last sub-bullet; Responses, second item
Problem: The retro's 26 is cited at line 116, but it is at line 118 (line 116 is a prose line of P5's "After" text).
Evidence: `sed -n '116p;118p' .factory/answers/retro-trial-2026-10-04/retro_with_efficiency.md`; my round-1 finding gave "lines 110-116" for P5, which likely led the writer here, so the error is partly mine.
Suggested fix: Change "line 116" to "line 118" in Evidence (the Responses section is history and can stay).

No other findings. The changed text introduces no new term of art without a gloss, no new decision, and no new path; Design A and B, the acceptance scenarios and Tests to change are unchanged from v1, where they were checked and fail today for the stated reason. Scope still fits one PR. Every protected and guardrail path the change touches is declared under Risk.

## Verifier results

090939d6428bff085890aa5d1b9d384bb8915c78 · T-0029.1 · VERIFIED · run-0287-verifier
