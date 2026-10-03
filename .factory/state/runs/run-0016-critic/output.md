## Critic review — T-0001 spec v1 (round 1)

### What I checked

Checkout: `~/dev/spec-factory` `main` at `9458a7b` (`git rev-parse --short HEAD`), matching the spec's Evidence header.

Cited paths, all read this run and all as the spec quotes them:
- `specs/build-harness.md:270` is the single-line `**STATUS parser**` paragraph with "the next non-blank line must match `^CONFIDENCE:`" and "`none` iff exactly `none`"; `:275` has `park --reason 'harness-bug: unknown STATUS <s>'`; `:202` has "logs `escalation.queued` when the list is not `none`."; `:208` ends the `meta.yaml` field list with "status, workflow_run_id."; `:346` is item 8 (Parser); `:454` is item 84 and `:456` is `### Gates (every seam)`; `:460` ends "Items 68–72, 78, 79, 82 are local-only." Item 9 (`:347`), which 85(c) builds on, is not in the bare-repo list, so adding 85 to the local-only list is consistent with how that sentence classifies items 67+.
- `docs/spec-factory.md:74` is the third bullet under "Rules the table relies on:" (`:70`) and opens with the sentence part D replaces; `:112` is the harness-bug sentence; `:196-201` is the OUTPUT block; `## Changelog` at `:605`, item 33 at `:641` (single line), `## Appendix` at `:645`, no item 34 today. `grep -n -i pars` matches only `:64`.
- `prompts/00-preamble.md:50-56` is byte-for-byte the OUTPUT block at `docs/spec-factory.md:196-201`.
- `intake/harness/factory/status.py` lines 3–7 and 40–43 say and do what the spec says: `re.fullmatch(r"none\.?", esc_head, re.I) and not tail` → empty list; anything else is an item. The reference `~/dev/nanobot-upstream/factory/status.py` (read only, branch `feat/lionbot-v3`, last touched by `053a7bd5e`) is the same rule. So "the as-built reference does not implement option b" is correct, and the spec is right not to lean on it.
- `intake/state/requests/T-0001.md` Answer 1: option (b), prose kept "for example on the `run.finished` log event or the run's meta", `None of …` is NOT none, green follow-up out of scope. The spec's A2 (meta.yaml) and A3 (regex) are the two open readings Triage left; both are stated in the spec and A3 is flagged for the operator. No silent decision.

Acceptance commands:
- Ran items 1–10 as written on `main`. Every "today" value matches: 1→`1`, 2→`no none-head pattern`, 3→`**last** parse failure`, 4→`0`, 5→`1`, 6→`0`, 7→`0`, 8→`0`, 9→`0`, 10→`docs/spec-factory.md:1` / `prompts/00-preamble.md:1`.
- Ran items 2, 3 and 4 against the proposed text itself (part A paragraph and item 85, copied out of the spec with the `> ` stripped): 2→`misclassified: []` (the extracted pattern is `(?i)^none\s*($|[.,;:—–-])`), 3→`**last** continuation escalations_note parse failure verbatim`, 4→`8`. So the NEW items fail today for the stated reason and pass against the proposed change, and item 2 is a real semantic check of the rule, not a wording grep.
- `yaml.safe_dump({'escalations_note': 'none. The boundary was observed'})` emits the plain scalar line item 85(c) expects.

Scope: two files, ~16 lines, one PR. "Tests to change: none" is right for a documents repo; item 8 is kept and criterion 11 guards it. Protected paths: `prompts/` untouched (criterion 10), nothing under `intake/**`, the reference tree or `~/.nanobot/` written. Consistency: item 41 (`:392`) already treats a non-empty list as the `escalation.queued` trigger, so part B's wording change agrees with it; open tickets T-0005–T-0007 are on other surfaces.

### Findings

[SHOULD-FIX] 6 — Proposed change, part A, the new `**STATUS parser**` paragraph ("The **head** is the rest of the `ESCALATIONS:` line")
Problem: the head is not said to be trimmed, but the `none`-head pattern is anchored with `^`, and every real trailer has a space after the colon (`ESCALATIONS: none`), so an implementer who takes "the rest of the line" literally classifies every `none` as an escalation item.
Evidence: the paragraph text in the spec; `ESCALATIONS: none` at `specs/build-harness.md:344` and in item 85(b). Item 85(b) (`→ "escalations": []`) would catch the literal reading, which is why this is not blocking; the as-built parser strips (`status.py:35`), the spec just doesn't say so.
Suggested fix: write "the rest of the `ESCALATIONS:` line, trimmed" (and, if you want the same for labels, "lines are matched after trimming").

[NIT] 6 — Proposed change, part A, "`run finish` writes that head verbatim to the run's `meta.yaml` as `escalations_note:` (`null` otherwise)"
Problem: for a bare `none` / `none.` head it is not clear whether `escalations_note` is `null` or the string `none`; "that head" reads as the none-with-prose head, but nothing in item 85 pins it.
Evidence: item 85(c) only tests the prose case; (b) tests `ESCALATIONS: none` for routing but not for `escalations_note`.
Suggested fix: one clause, e.g. "the note is written only when prose follows the `none` head; bare `none` writes `null`", and optionally add `escalations_note: null` to 85(b)'s expectation.

No blocking issues. The rubric items that matter here are 2 and 4: the NEW criteria are grounded in output I reproduced, item 2 is a genuine behavioural check of the decided rule, and the two judgement calls Triage left open are written down and flagged rather than buried.

### Prior findings

n/a (round 1)

STATUS: APPROVE
CONFIDENCE: high — every cited line was re-read on `9458a7b`, acceptance 1–10 reproduced today's values, and 2–4 were run against the proposed text; the only gaps found are wording that item 85 would catch anyway
ESCALATIONS:
- A3 (the `none`-head rule `(?i)^none\s*($|[.,;:—–-])`) is Triage's reading of Answer 1, adopted by the spec; the operator should confirm it at the spec gate, as the spec itself asks (in particular that case-insensitive `None.` counts as none).
