Type: bug

Title: STATUS parser parks valid verdicts as harness bugs when the trailer departs from the strict three-line shape

Summary: The STATUS parser rule in `specs/build-harness.md` part H expects the line right after the last STATUS line to be `CONFIDENCE:` and the line after that to be `ESCALATIONS:`. Real model output breaks that shape in three ways. CONFIDENCE wraps onto a second line, commentary sits between STATUS and CONFIDENCE, and prose follows `none` on the ESCALATIONS line. Each of these parked a valid verdict as `harness-bug: unknown STATUS`. The requester and the operator's answer ask for spec H, plus the design doc where it governs the trailer, to define this rule:
- CONFIDENCE is the next labelled line after the last STATUS, and ESCALATIONS is the next labelled line after CONFIDENCE.
- Lines between labelled lines are continuation.
- A `none` head followed by prose routes as no escalation, and the prose is kept with the run for audit.
- A `none` head followed by further item lines is a real escalation list, taken verbatim from the head on.
- These stay as they are: last STATUS wins, and a missing CONFIDENCE or ESCALATIONS is still a parse failure.

Requested behaviour (from the request and Answer 1; Given/When/Then, for the Spec writer to turn into commands):
- Given a trailer whose CONFIDENCE reason wraps onto a second line, when it is parsed, then the STATUS is the model's STATUS and the ESCALATIONS items are the ones that follow the `ESCALATIONS:` line. It is not a parse failure.
- Given a commentary line between `STATUS:` and `CONFIDENCE:`, when it is parsed, then the STATUS is kept. It is not a parse failure.
- Given `ESCALATIONS: none. <prose>` with nothing after it, when it is parsed, then nothing goes to the human queue and the prose is recorded with the run where an auditor can read it.
- Given `ESCALATIONS: none. <prose>` followed by item lines, then every line from the head on is an escalation item, verbatim.
- Given `ESCALATIONS: Nonetheless …` or `ESCALATIONS: None of …`, then the line is an escalation item.
- Given a trailer with no CONFIDENCE line, or no ESCALATIONS line, then it is still a parse failure.
- Given an earlier `STATUS:` line in the body, then the last one still wins.

Duplicate search: there is no duplicate.
- T-0001 is this request. It comes from `issues/01_status_parser.md`, which is listed in `intake/state/requests/index.yaml`.
- `issues/02`–`07` cover other subjects: the clerk schema, the Triage re-ask input, the agents dir, protected live state, the P0-5 grep and the single-target harness. I checked by file name this run and by `title:` line in the previous run.
- I did not search GitHub issues, because filing there is on hold (`issues/README.md`).

Evidence:
- **The spec rule**, `specs/build-harness.md:270` (re-read this run): "the **last** line matching `^STATUS:\s*(\S+)`; the next non-blank line must match `^CONFIDENCE:`; the next `^ESCALATIONS:`; … `none` iff exactly `none`. Any other shape → parse failure → unknown STATUS."
- **Where a parse failure goes:**
  - `specs/build-harness.md:275`: "Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'`"
  - `docs/spec-factory.md:112`: "Any STATUS not in this table is a harness bug: park the ticket in the human queue and log it."
- **The safety-channel rule this decision refines**, `docs/spec-factory.md:74`: "A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route."
- **The prompt instruction**, `docs/spec-factory.md:200`, copied verbatim to `prompts/00-preamble.md:54`: "CONFIDENCE: high | medium | low, with one line of reason".
- **Existing acceptance item 8**, `specs/build-harness.md:346`, covers last-STATUS-wins and the missing-CONFIDENCE failure. Both must keep passing.
- **Instance 1** (Triage, P0 run 2026-10-01): CONFIDENCE wrapped onto a second line, and the ticket was parked as `harness-bug: unknown STATUS UNKNOWN`. The trailer is quoted in the request.
- **Instance 2** (Spec writer, T-0001 v3, run-0006): a parenthetical sat between STATUS and CONFIDENCE, and the line read `ESCALATIONS: none. The ~/.nanobot/** boundary was observed throughout — …`. It was also parked as a harness bug. The trailer is quoted in the request.
- **Operator decision (Answer 1, 2026-10-01):** option (b), none for routing with the prose kept.
- **The as-built reference does NOT implement the decided `none` + prose rule.**
  - `intake/harness/factory/status.py` in this repo is byte-identical to green's `053a7bd5e:factory/status.py`. `diff` printed nothing.
  - I ran this repo's copy of `parse()` this run. It handles the shape cases correctly:
    - wrapped CONFIDENCE → `NEEDS-HUMAN`, `['1. foo']`
    - commentary before CONFIDENCE → STATUS kept
    - no CONFIDENCE → `parse failure: no CONFIDENCE line after STATUS`
    - no ESCALATIONS → `parse failure: no ESCALATIONS line after CONFIDENCE`
    - `Nonetheless …` and `None of …` → escalation items
    - `none. x` + `- extra line` → `['none. x', 'extra line']`
  - But it gives `ESCALATIONS: none. The boundary was observed` → `['none. The boundary was observed']`. That means it is queued to the human queue, which is option (c). Answer 1 confirms this is green's interim default.
  - So a criterion for the `none` + prose case cannot be satisfied by copying the as-built rule.

Assumptions (my inferences, not stated by the requester or operator):
- **A1. What the design-doc change covers.** It means two things. First, `docs/spec-factory.md:74` gains a qualifier for the `none` + prose head. Second, a sentence says how the trailer is parsed. The design doc has no parser rule today: `grep -n -i "pars" docs/spec-factory.md` matches only line 64. The OUTPUT block at `docs/spec-factory.md:196-201` should stay as it is, since "one line of reason" is still the right instruction to the model. If it is edited, `prompts/00-preamble.md` must be re-copied, which is a protected path. Either way the doc gets a Changelog entry (`## Changelog`, `docs/spec-factory.md:605`), and spec H line 270 must agree with the doc.
- **A2. Where the kept prose lives.** Answer 1 offers the `run.finished` log event or the run's `meta.yaml` as examples ("for example"). I take it as the Spec writer's choice of one, stated in spec H, and not both.
- **A3. What counts as a `none` head (this needs care).** Answer 1 says the head is the "whole word `none` (word boundary)" and that `None of …` is NOT none. A plain word-boundary match would accept `None of …`, because "None" is a whole word there, so the two statements need a sharper rule.
  - My reading: the head is `none`, case-insensitive, followed by end-of-line or punctuation (`.` `,` `;` `:` or a dash), never by a space and a word.
  - This covers both examples: `none. The …` is none, `None of …` is not.
  - The Spec writer must state the rule explicitly and test both examples. If the operator meant something else (for example, case-sensitive lowercase `none` only), the critic or spec gate should catch it. See ESCALATIONS.
- **A4. Bringing green's harness in line is out of scope.** Answer 1 says it is a follow-up on green. This ticket changes the design documents (`docs/`, `specs/`) only.
- **A5. Priority (suggestion only): high.** Every verbose-but-correct verdict currently parks as a harness bug, which stalls the pipeline and misattributes the fault.

Reason: n/a. The request is accepted: the intent is clear, and the one product decision (`none` + prose) was answered by the operator in Answer 1.

Out-of-scope observations:
- Green's `factory/status.py` (`053a7bd5e`) and this repo's harness copy route `none` + prose to the human queue (option c). That diverges from the decision until the follow-up on green lands. Answer 1 already notes this.
- The previous run's note that the `status.py` docstring describes the old strict rule may be stale. The `053a7bd5e` commit message says "Docstring updated". I did not re-read the docstring this run.

STATUS: ACCEPT
CONFIDENCE: medium — the cited lines were re-read and the parser was run on this checkout, but A3 (how to tell `none.` from `None of`) is my reading of Answer 1, not a stated rule, and GitHub was not searched for duplicates
ESCALATIONS:
- A3: Answer 1's "whole word `none` (word boundary)" would also match `None of …`, which the same answer says is not none. My working rule is `none`, case-insensitive, followed by end-of-line or punctuation, never by a space and a word. The operator should confirm this at the spec gate, or say if lowercase-only was meant.
