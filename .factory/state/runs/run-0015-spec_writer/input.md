## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0015-spec_writer/output.md`

## Ticket (Triage output)

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

## Request (raw)

---
title: STATUS parser rule rejects real model output: CONFIDENCE wraps onto a second line
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` part H, "STATUS parser": *the next non-blank line must match `^CONFIDENCE:`; the next `^ESCALATIONS:`*. Also the preamble's OUTPUT block (`CONFIDENCE: high | medium | low, with one line of reason`).

**What happened (P0 run, 2026-10-01, Nanobot green):** the first real Triage run (Opus) ended

```
STATUS: NEEDS-HUMAN
CONFIDENCE: high — every claim above is a grep, a file read, or a command run on this
checkout and cited by path and line; the one thing I could not settle is …
ESCALATIONS:
1. …
```

A parser written to the spec's rule read `checkout and cited…` as "not ESCALATIONS", returned a parse failure, and the dispatcher parked the ticket as `harness-bug: unknown STATUS UNKNOWN`. The verdict was a valid NEEDS-HUMAN with a well-formed question.

**Why it matters:** "one line of reason" is a prompt instruction; a long model wraps it. A parser that treats a wrapped line as a parse failure turns every verbose-but-correct verdict into a harness-bug park, which is the one outcome the routing table says is never the model's fault.

**Proposed fix (design doc + spec H):** CONFIDENCE is the first non-blank line after the last STATUS line; ESCALATIONS is the *next labelled line* (`^ESCALATIONS:`) after it; lines between them are CONFIDENCE continuation. Keep the rest (last STATUS wins; `none` iff exactly `none`).

**Fix as implemented on the Nanobot side:** `factory/status.py` at `0f2e29136` on `feat/lionbot-v3` (test `test_status_parse_accepts_a_wrapped_confidence_line`). Design-doc text not yet changed; awaiting review.

**Second instance, same day (T-0001 v3, run-0006):** the Spec writer emitted

```
STATUS: READY-FOR-CRITIC
(The change is still too large for one PR, so **Proposed change** stays marked NEEDS-SPLIT …)
CONFIDENCE: high — …
ESCALATIONS: none. The `~/.nanobot/**` boundary was observed throughout — …
```

Two more departures from the OUTPUT block: commentary between STATUS and CONFIDENCE, and
prose after `none` on the ESCALATIONS line. Both were valid verdicts parked as harness bugs
under the strict rule. The fix now on green (`factory/status.py`): CONFIDENCE is the next
*labelled* line after the last STATUS, ESCALATIONS the next labelled line after that, lines
between are continuation, and `none` followed by prose is still none. Proposed design-doc
wording should match that, since the prompt's "one line of reason" is not something a
parser can rely on.


## Answer 1

Operator decision (2026-10-01, Triage's question on `none` + prose): option **(b), none for routing, prose kept.**

- An ESCALATIONS head that is the whole word `none` (word boundary; `Nonetheless …` and `None of …` are NOT none) followed by prose on the same line routes as no escalation: nothing goes to the human queue.
- The prose is not dropped: it is kept with the run (for example on the `run.finished` log event or the run's meta) where an auditor can see it.
- A `none` head followed by further item lines is not none: every line from the head on is an escalation item, verbatim.
- Everything else in Triage's reading stands (wrapped CONFIDENCE, commentary before CONFIDENCE, next-labelled-line rule; last STATUS wins; missing CONFIDENCE or ESCALATIONS is still a parse failure).

Note: the reference harness on green (`053a7bd5e`) currently routes `none` + prose to the human queue (option c), as an interim default. Bringing green in line with this decision is a follow-up there, out of scope for this ticket.
