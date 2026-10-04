## Problem

The STATUS parser rule in `specs/build-harness.md` part H (line 270) reads the trailer by position: CONFIDENCE has to be the very next non-blank line after the last STATUS, and ESCALATIONS the line right after that. Real model output breaks that shape. A CONFIDENCE reason wraps onto a second line, or a remark sits between STATUS and CONFIDENCE. Under the strict rule both are parse failures, and parse failures are parked as `harness-bug: unknown STATUS` (spec H line 275, doc line 112). So a valid verdict reaches the human queue as a harness fault. The routing table says that outcome is never the model's fault, and it stalls the ticket.

There is a second gap. The operator decided (Answer 1, option b) that `ESCALATIONS: none. <prose>` with nothing after it routes as no escalation and the prose is kept with the run. Neither document says this today. Spec H says "`none` iff exactly `none`", and doc line 74 queues any non-empty ESCALATIONS line.

The people affected are the operator, whose queue fills with false harness bugs, and the harness builder, who is following spec H as written.

## Evidence

All of this is on `~/dev/spec-factory` `main` at `9458a7b`.

- **The rule as written**, `specs/build-harness.md:270`: "the **last** line matching `^STATUS:\s*(\S+)`; the next non-blank line must match `^CONFIDENCE:`; the next `^ESCALATIONS:`; … `none` iff exactly `none`. Any other shape → parse failure → unknown STATUS." `grep -c 'next non-blank line must match' specs/build-harness.md` returns `1`.
- **Where a failure goes:** `specs/build-harness.md:275` says "Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'`". `docs/spec-factory.md:112` says "Any STATUS not in this table is a harness bug".
- **The design doc has no trailer-parsing rule.** `grep -n -i "pars" docs/spec-factory.md` matches only line 64 ("Clerk, parsing, routing"). Line 74 says "A non-empty ESCALATIONS line is copied to the human queue …".
- **The prompt instruction** "CONFIDENCE: high | medium | low, with one line of reason" is at `docs/spec-factory.md:200` and `prompts/00-preamble.md:54`. It is identical in both, and `grep -c` returns 1 in each file.
- **Reproduction.** I wrote a parser that implements line 270 literally and compared it with this repo's `intake/harness/factory/status.py`. I ran both read-only (`PYTHONDONTWRITEBYTECODE=1`, `sys.dont_write_bytecode`), and afterwards `git status` showed nothing new under `intake/harness`. Actual output:
  ```
  wrapped CONFIDENCE (instance 1):        strict -> parse failure            as-built -> NEEDS-HUMAN, ['1. foo']
  commentary before CONFIDENCE (inst. 2): strict -> parse failure            as-built -> READY-FOR-CRITIC, []
  none + prose (instance 2):              strict -> ['none. The boundary was observed throughout']
                                          as-built -> ['none. The boundary was observed throughout']
  none + prose + items:                   strict -> ['none. x', '- extra line']   as-built -> ['none. x', 'extra line']
  Nonetheless / None of:                  both -> one item each, verbatim
  no CONFIDENCE / no ESCALATIONS:         both -> parse failure
  earlier STATUS in body:                 both -> REVISE (last wins)
  ```
  The ticket summary says each of the three shapes parked a verdict, and that needs a correction. The `none` + prose shape is not a parse failure under the strict rule. It gets queued as an escalation item. Instance 2 was parked because of its commentary line. The decision still requires a change for this shape: under both the strict rule and the as-built parser, the prose goes to the human queue (option c), and the operator chose option b.
- **The as-built reference does not implement option b.** Its docstring and code (`status.py` lines 3–7 and 40–43) make the list empty only for `none` with an optional period and nothing else. This also settles Triage's out-of-scope note: the docstring has been updated and no longer describes the strict rule. Following the reference would therefore not satisfy the decision, and the new rule below has to be written out in the spec.

## Root cause

`specs/build-harness.md` part H, the **STATUS parser** paragraph (line 270), defines the trailer by line position and an exact-match `none`. The prompt only asks the model for "one line of reason" (`docs/spec-factory.md:200`), and a parser cannot rely on that. `docs/spec-factory.md` §Routing rules (line 74) never says how the trailer is read, or what an ESCALATIONS line that starts with `none` and then carries prose means. There are two smaller gaps that follow from this. B's `run finish` (line 202) "logs `escalation.queued` when the list is not `none`". C's `meta.yaml` field list (line 208) has no field for the kept prose.

## Proposed change

Only two files change: `docs/spec-factory.md` and `specs/build-harness.md`. That is about 11 lines added and 5 removed, which I applied in a scratch clone (see Acceptance). The preamble's OUTPUT block stays as it is, so `prompts/` is not re-copied. "One line of reason" is still the right instruction to the model. The parser just stops relying on it.

**Decisions taken here.** Triage left these to the Spec writer, or asked for a sharper rule:
- **A2 (where the kept prose lives):** the run's `meta.yaml`, as a new field `escalations_note:`. It is per run, it sits next to `status`, and `retro-input` and `audit-sample` already read it. The `run.finished` event does not change.
- **A3 (what counts as a `none` head):** the regex `(?i)^none\s*($|[.,;:—–-])`. That is `none` in any case, followed by end of line or one of `.` `,` `;` `:` `-` `–` `—`, possibly after spaces. A space followed by a word never counts. So `none`, `none.`, `None`, `none. The boundary…` and `none — x` are `none` heads. `Nonetheless …`, `None of …`, `none of it` and `nonexistent` are not. Anything that does not match is an escalation item. When the parser is unsure, the text goes to the human queue, which is the safe direction. Under ESCALATIONS I ask the operator to confirm this rule at the spec gate.

**A. `specs/build-harness.md` part H: replace the whole STATUS parser paragraph (line 270) with:**

> **STATUS parser** (`factory/status.py`, used by `run finish` and `results record`; doc §Routing rules): the **last** line matching `^STATUS:\s*(\S+)` gives the STATUS. CONFIDENCE is the first line after it matching `^CONFIDENCE:`, and ESCALATIONS the first line after that matching `^ESCALATIONS:`; lines between labelled lines are continuation (a wrapped CONFIDENCE reason, commentary between STATUS and CONFIDENCE), never a parse failure. No `CONFIDENCE:` line after the last STATUS, or no `ESCALATIONS:` line after that CONFIDENCE → parse failure → unknown STATUS. The **head** is the rest of the `ESCALATIONS:` line; the list is the head plus every non-blank line after it to EOF, each item as written (a leading `- ` or `* ` marker stripped, item 8). A **`none` head** matches `(?i)^none\s*($|[.,;:—–-])`: `none` in any case, then end of line or punctuation, never a space and a word, so `none`, `none.` and `none. The boundary was observed` are `none` heads and `Nonetheless …`, `None of …` are not. The list is empty iff nothing non-blank follows the head and the head is empty or a `none` head; a `none` head with prose after it on its line therefore routes as no escalation, and `run finish` writes that head verbatim to the run's `meta.yaml` as `escalations_note:` (`null` otherwise) so an auditor reads it with the run. A `none` head followed by any further non-blank line is a real list, every line from the head on an item, verbatim. Anything else is an item: when the parser is unsure, the text goes to the human queue. The parser reads no severities: doc §Human gates' rule that REVISE and REQUEST-CHANGES carry at least one BLOCKING finding is the checker's to keep, and every stub that models them (items 38, 44, 46) includes a BLOCKING line.

The paragraph has to stay a single line that starts with `**STATUS parser**`, because Acceptance 2 and 3 find it that way.

**B. `specs/build-harness.md` parts B and C:**
- Line 202 (`factory run finish`): change "logs `escalation.queued` when the list is not `none`." to "logs `escalation.queued` when the list is non-empty (H)."
- Line 208 (the `meta.yaml` field list): change "status, workflow_run_id." to "status, escalations_note, workflow_run_id."

**C. `specs/build-harness.md` Acceptance:** add a new subsection right after item 84 and before `### Gates (every seam)`:

> ### Trailer parser [S1]
>
> 85. **Trailer shapes (H) [S1]:** with `t() { printf "$1" > t.md; factory status parse t.md; }`: (a) wrapped CONFIDENCE, `t 'STATUS: NEEDS-HUMAN\nCONFIDENCE: high — every claim is a grep on this\ncheckout and cited by path\nESCALATIONS:\n1. q\n'` → `"status": "NEEDS-HUMAN"`, `"escalations": ["1. q"]`; (b) commentary, `t 'STATUS: READY-FOR-CRITIC\n(still too large for one PR)\nCONFIDENCE: high, x\nESCALATIONS: none\n'` → `"status": "READY-FOR-CRITIC"`, `"escalations": []`; (c) `none` + prose, `t 'STATUS: APPROVE\nCONFIDENCE: high, x\nESCALATIONS: none. The boundary was observed\n'` → `"escalations": []`, and `factory run finish <run_id> --output-file t.md` on a run started as in item 9 → no `escalation.queued` line for that run and its `meta.yaml` has `escalations_note: none. The boundary was observed`; (d) `t 'STATUS: APPROVE\nCONFIDENCE: high, x\nESCALATIONS: none. x\n- extra line\n'` → `"escalations": ["none. x", "extra line"]`; (e) (c) with the head `Nonetheless the key leaked`, then `None of the gates ran` → one item each, verbatim; (f) (a) without its `CONFIDENCE:` line, or without its `ESCALATIONS:` line → `"status": null`, `"error"` beginning `parse failure`; (g) item 8's three cases unchanged [NEW]

Also, in the line under `### Gates` that ends "Items 68–72, 78, 79, 82 are local-only.", change that sentence to "Items 68–72, 78, 79, 82, 85 are local-only."

Item 85 covers the seven Given/When/Then behaviours from the ticket, (a) through (g), for whoever builds or fixes the harness. Item 8 is not edited.

**D. `docs/spec-factory.md` §Routing table, "Rules the table relies on":** replace the opening sentence of the third bullet (line 74), "- A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route.", with the two-bullet text below. The rest of that bullet, from "Only NEEDS-HUMAN, CLARIFY, …" on, stays word for word and follows on the same line:

> - The dispatcher reads a role's trailer by its labels, not by line position. The last `STATUS:` line wins; CONFIDENCE is the next line labelled `CONFIDENCE:` after it, and ESCALATIONS the next line labelled `ESCALATIONS:` after that. Lines between labelled lines are continuation (a wrapped reason, a remark), so a verbose but well-formed verdict routes on its STATUS. A trailer with no CONFIDENCE or no ESCALATIONS line after its last STATUS is a parse failure, which routes as a STATUS not in this table.
> - A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. Only NEEDS-HUMAN, CLARIFY, … *(unchanged remainder)*

**E. `docs/spec-factory.md` §Changelog:** append after item 33:

> 34. After two real runs parked valid verdicts as harness bugs (2026-10-01), the trailer is read by its labels: a wrapped CONFIDENCE reason or a remark between STATUS and CONFIDENCE is continuation, not a parse failure; an ESCALATIONS line of `none` followed by prose routes as none and the prose is kept with the run; `none` with further lines below it is a real list.

## Acceptance

Run all of these from `~/dev/spec-factory`, with the PR branch checked out and `main` as its base. I ran every command on `main` (`9458a7b`) and on a scratch clone with parts A–E applied and committed. The two results quoted for each item come from those two runs.

1. `grep -c 'next non-blank line must match' specs/build-harness.md` → `0` [NEW: today `1`, the strict rule at line 270]
2. `python3 -c "import re;p=next((l for l in open('specs/build-harness.md',encoding='utf-8') if l.startswith('**STATUS parser**')),'');m=re.search(r'\(\?i\)\^none[^'+chr(96)+']*',p);r=re.compile(m.group(0)) if m else None;Y=['none','none.','None','NONE','none. The boundary was observed','none, see above','none — the boundary held'];N=['Nonetheless the key leaked','None of the gates ran','none of it','nonexistent'];print('no none-head pattern' if r is None else 'misclassified: %r' % ([s for s in Y if not r.match(s)]+[s for s in N if r.match(s)]))"` → `misclassified: []`. This reads the `none`-head pattern straight out of the spec's parser paragraph and runs it on the decided examples. [NEW: today `no none-head pattern`]
3. `grep '^\*\*STATUS parser\*\*' specs/build-harness.md | grep -o -e '\*\*last\*\*' -e 'continuation' -e 'parse failure' -e 'escalations_note' -e 'verbatim' | sort -u | tr '\n' ' '` → `**last** continuation escalations_note parse failure verbatim`. The paragraph keeps last-STATUS-wins and the parse failure, and adds continuation, the kept note and verbatim items. [NEW: today `**last** parse failure`]
4. `grep '^85\. ' specs/build-harness.md | grep -o -e 'NEEDS-HUMAN' -e 'READY-FOR-CRITIC' -e 'none\. The boundary was observed' -e 'extra line' -e 'Nonetheless' -e 'None of' -e 'parse failure' -e 'escalations_note' | sort -u | wc -l | tr -d ' '` → `8`. All seven requested cases are present in the harness acceptance list. [NEW: today `0`, there is no item 85]
5. `grep -c 'escalation.queued` when the list is not `none`' specs/build-harness.md` → `0` [NEW: today `1`, line 202]
6. `grep -c 'status, escalations_note, workflow_run_id' specs/build-harness.md` → `1` [NEW: today `0`]
7. `grep -c 'Items 68–72, 78, 79, 82, 85 are local-only\.' specs/build-harness.md` → `1` [NEW: today `0`]
8. `awk '/^Rules the table relies on:/{f=1} /^\| From \| STATUS/{f=0} f' docs/spec-factory.md | grep -c -e 'continuation' -e 'kept with the run'` → `2`. The doc's routing rules now state both the label rule and the `none` + prose rule. [NEW: today `0`]
9. `awk '/^## Changelog/{f=1} /^## Appendix/{f=0} f' docs/spec-factory.md | grep -c '^34\. .*continuation.*none'` → `1` [NEW: today `0`]
10. `git diff --exit-code main...HEAD -- prompts/ && grep -c '^CONFIDENCE: high | medium | low, with one line of reason$' docs/spec-factory.md prompts/00-preamble.md` → exit 0, `docs/spec-factory.md:1` and `prompts/00-preamble.md:1`. The OUTPUT block and the protected `prompts/` copies are unchanged. [REGRESSION]
11. `git diff main...HEAD -- specs/build-harness.md | grep -c '^-8\. Parser'` → `0`. Item 8, which covers last-STATUS-wins and the missing-CONFIDENCE failure, is not edited. [REGRESSION]
12. `git diff --name-only main...HEAD | grep -v -x -e docs/spec-factory.md -e specs/build-harness.md` → no output, exit 1. No other path is touched. [REGRESSION]
13. `git diff --check main...HEAD` → no output, exit 0 [REGRESSION]

## Tests to change

none. This repo holds documents. Item 8 of the spec's Acceptance list is kept word for word (criterion 11).

## Out of scope

- Must not change: the preamble's OUTPUT block (`docs/spec-factory.md:196-201`) and every file under `prompts/`.
- Must not change: item 8 of `specs/build-harness.md`.
- Must not change: last-STATUS-wins, and the rule that a missing CONFIDENCE or ESCALATIONS is a parse failure.
- Must not change: the routing table's harness-bug row (doc line 112, spec H line 275).
- Bringing the reference harness (`~/dev/nanobot-upstream/factory/status.py`) and this repo's copy under `intake/harness/` in line with option b. Answer 1 calls that a follow-up on green, and both paths are protected.
- `plans/` (the Planner's output) and the `run.finished` event's payload.

## Open questions

none. Triage's A3 rule is adopted as stated above and is flagged under ESCALATIONS for the operator to confirm at the spec gate. It does not block this spec.

## Risk

The blast radius is documents only, about 16 changed lines in `docs/spec-factory.md` and `specs/build-harness.md`. I touched no protected path. `prompts/` is unchanged (criterion 10), and `intake/**`, `~/dev/nanobot-upstream/**` and `~/.nanobot/**` are not written. I ran the parser in `intake/harness` read-only, and no `.pyc` file was written.

Downstream, both harness copies diverge from the documents on `none` + prose until the green follow-up lands. The reference parser still queues that prose (option c). So item 85(c) will fail against the as-built harness. That is expected, and it is the follow-up's job, not this PR's.

The `none`-head regex errs toward escalating. If it is wrong in that direction, the only cost is noise in the human queue. No escalation is ever dropped.

## Responses

n/a (round 1)

## Out-of-scope observations

- `intake/harness/factory/status.py` uses `STATUS_RE = ^STATUS:\s*(\S+)\s*$`, which needs the STATUS token to be alone on its line. Spec H's `^STATUS:\s*(\S+)` also accepts trailing text, such as `STATUS: APPROVE (see note)`. The parser and the spec disagree here, and this ticket does not cover it.
- The as-built parser strips leading `-`, `*` and spaces from tail items (`lstrip("-* ")`), so `* bold` loses characters it should keep. Spec item 8 only implies stripping a list marker.

STATUS: READY-FOR-CRITIC
CONFIDENCE: medium — every criterion was run on main and on a scratch clone with A–E applied, and every cited line was re-read; but the meta.yaml `escalations_note` location (A2) and the `none`-head regex (A3) are my choices pending the spec gate
ESCALATIONS:
- A3 (meaning of a `none` head): this spec adopts `(?i)^none\s*($|[.,;:—–-])`, so `none` in any case followed by end of line or punctuation counts, and a space plus a word (`None of …`, `none of it`) never does. Answer 1's "word boundary" would also match `None of …`. The operator should confirm at the spec gate, or say whether lowercase-only, or other punctuation such as `(`, was meant.
