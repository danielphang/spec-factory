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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0014-triage/output.md`

## Request (raw, with any answers appended)

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

## Your previous Triage output (the question you asked is answered above)

Type: bug

Title: STATUS parser parks valid verdicts as harness bugs when the trailer departs from the strict three-line shape

Summary: The spec's STATUS parser rule (`specs/build-harness.md` part H) requires the line right after the last STATUS line to be `CONFIDENCE:` and the next one `ESCALATIONS:`. Real model output breaks that shape in three ways: CONFIDENCE wraps onto a second line, commentary sits between STATUS and CONFIDENCE, and prose follows `none` on the ESCALATIONS line. Each one parked a valid verdict as `harness-bug: unknown STATUS`. The requester wants spec H, and the design doc where it governs the trailer, to define a parser that accepts these shapes. It should keep "last STATUS wins" and still treat `none` as none when prose follows it. The fix already runs in the reference harness. Only the design documents are missing.

Duplicate search:
- `issues/02`–`issues/07` (the parked drafts behind T-0002…T-0007) are about other things: clerk schema, re-ask input, agents dir, protected live state, the P0-5 grep and a single-target harness. Checked by reading the `title:` line of each file.
- No duplicate exists in the local store (`intake/state/requests/index.yaml`: T-0001 is this request, from `issues/01_status_parser.md`).
- I did not search GitHub issues. Filing to GitHub is on hold until `gh auth` is restored (`issues/README.md`).

Evidence:
- Spec rule, `specs/build-harness.md:270`: "the **last** line matching `^STATUS:\s*(\S+)`; the next non-blank line must match `^CONFIDENCE:`; the next `^ESCALATIONS:` … `none` iff exactly `none`. Any other shape → parse failure → unknown STATUS."
- Where an unknown STATUS goes, `specs/build-harness.md:275`: "Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'`". Design doc rule, `docs/spec-factory.md:112`: "Any STATUS not in this table is a harness bug: park the ticket in the human queue and log it."
- Prompt instruction, `docs/spec-factory.md:200` (copied verbatim into `prompts/00-preamble.md`): "CONFIDENCE: high | medium | low, with one line of reason".
- Instance 1 (Triage, Opus, P0 run 2026-10-01): CONFIDENCE wrapped onto a second line, and the result was a parse failure and a park as `harness-bug: unknown STATUS UNKNOWN` (quoted in the request).
- Instance 2 (Spec writer, T-0001 v3, run-0006): a parenthetical sat between STATUS and CONFIDENCE, and the line read `ESCALATIONS: none. The ~/.nanobot/** boundary was observed throughout — …`. This was also parked as a harness bug (quoted in the request).
- I checked the reference harness (`~/dev/nanobot-upstream`, branch `feat/lionbot-v3`, read only):
  - `0f2e29136` (the P0 skeleton commit the request cites) already allows continuation lines after CONFIDENCE. `git show 0f2e29136:factory/status.py` contains "CONFIDENCE may wrap onto continuation lines; ESCALATIONS: is the next labelled line." It still required CONFIDENCE as the first non-blank line and an exact `none`.
  - The fix for the second instance is `c0753caf7` ("factory(status): CONFIDENCE and ESCALATIONS are the next labelled lines, not the next lines"). The request does not give this SHA. Its diff changes the CONFIDENCE match to "first line starting `CONFIDENCE:` after STATUS". It also changes `none` from exact match to `esc_head.lower().startswith("none")`.
  - `tests/factory/test_p0_cli.py:205` and `:214` cover the wrapped case and the commentary + `none.` prose case.
  - `intake/harness/factory/status.py` in this repo is byte-identical to `c0753caf7:factory/status.py` (`diff` printed nothing).
- I ran this repo's harness copy of `parse()` against the as-built behaviour:
  - Wrapped CONFIDENCE → `NEEDS-HUMAN`, escalations `['1. foo']`.
  - Commentary plus `none. The boundary…` → `READY-FOR-CRITIC`, escalations `[]`.
  - Missing CONFIDENCE → `{"status": None, "error": "parse failure: no CONFIDENCE line after STATUS"}`. So spec acceptance item 8's failure case (`specs/build-harness.md:346`) still holds.
  - **`ESCALATIONS: Nonetheless the auth path needs review` → escalations `[]`.** The as-built prefix match silently drops a real escalation.

Assumptions (my inferences, not stated by the requester):
- A1: The design-doc change means the trailer wording, or a sentence saying how the trailer is parsed. The design doc has no parser rule today: `grep -n -i "pars" docs/spec-factory.md` matches only line 64, a model-table row. Any edit to the OUTPUT block at `docs/spec-factory.md:197-201` also requires re-copying `prompts/00-preamble.md` (a protected path, changed only by re-copying) and a Changelog entry (`docs/spec-factory.md:605`).
- A2: "`none` followed by prose" means the word `none` followed by a word boundary, not any line starting with the letters n-o-n-e. The requester's evidence (`none. The …`) fits the narrow reading. The as-built `startswith("none")` is wider than that.
- A3: The rest of the rule stays as stated in spec H: last STATUS wins, the list runs to EOF, and a missing CONFIDENCE or ESCALATIONS is still a parse failure.
- Priority (suggestion only): high. Every verbose but correct verdict currently parks as a harness bug. That blocks the pipeline and wrongly charges the harness bug to the model.

Question for human:
How should the parser treat an ESCALATIONS line that starts with `none` and then carries prose (`ESCALATIONS: none. The boundary was observed …`)? This is a call about the safety channel: `docs/spec-factory.md:74` says "A non-empty ESCALATIONS line is copied to the human queue". `none` with prose is a non-empty line. The as-built rule also drops "Nonetheless …" and "None of the gate commands ran …" without a trace. Options:
- (a) **None, prose dropped.** `none` as a whole word followed by anything counts as none. The spec words this as a word boundary, which fixes "Nonetheless". "none — except X" is still dropped. This matches the requester's proposal and green's intent.
- (b) **None for routing, prose kept.** `none` + prose routes as none but the prose is logged with the run (for example on `run.finished`), so an auditor can see it. Nothing goes to the human queue.
- (c) **Conservative: anything beyond exactly `none` is an escalation.** Keep `none` iff exactly `none` (current spec text) and copy `none` + prose to the human queue. This costs false-positive queue items, never a dropped escalation.
The rest of the request (wrapped CONFIDENCE, commentary before CONFIDENCE, next-labelled-line rule) needs no decision. A Spec writer can take it once this question is answered.

Out-of-scope observations:
- The docstring of `intake/harness/factory/status.py` (and green's `factory/status.py`) still describes the old strict rule ("the next non-blank line must be CONFIDENCE: … `none` iff exactly `none`"). Both are protected or read-only paths for this run, so I did not touch them.
- The as-built tail handling is also undecided: `ESCALATIONS: none. x` followed by `- extra line` returns `['extra line']`, dropping the head and keeping the tail. Whichever option is chosen should state this case.

STATUS: NEEDS-HUMAN
CONFIDENCE: medium — the bug and the as-built fix were checked by file reads, `git show`, `diff` and running the parser, but GitHub was not searched for duplicates and A1 (what "design doc" covers) is my inference
ESCALATIONS: none
