Type: bug

Title: Build spec / design doc / P0 plan: a parent whose pinned spec has no change folder (or whose store has no spec store) closes as applied after its archive refusal, instead of leaving an unexplained park

Summary: Some parents had their specs pinned before `factory init` created `openspec/`, so they have no `openspec/changes/<ID>/` folder. At parent close, `factory archive` will refuse with exit 2, and part H then parks the parent. Nothing in the documents says what the operator does with that park. The requester wants the documents to name the case and give one resolution for it. Per the operator's answer (option (a)):
- Part K of `specs/build-harness.md` names "no change folder" and "no spec store" as distinct `archive` refusals.
- Their park resolves by closing the parent as applied. Current truth and `decisions.md` are not updated. The spec is re-intaken as a new ticket if current truth should carry it.
- The design doc's park and resolution lists carry the case, with a Changelog entry.
- `plans/P0-intake-skeleton.md` records SPEC-21, SPEC-26 and SPEC-27 as that cohort.

Evidence:
- Request: `intake/state/requests/T-0010.md` (source commit `3d2ef71`). Operator answer: `intake/answers/T-0010.md`, "**(a).**", taken as the recommended default under the standing take-the-recommendation rule; "reversible at the spec gate". Recorded in commit `555c119` ("intake(T-0010): triage NEEDS-HUMAN; default (a) taken").
- Gap, re-checked on this checkout (HEAD `555c119`):
  - `grep -n -i "no change folder\|no spec store" specs/build-harness.md docs/spec-factory.md plans/P0-intake-skeleton.md` finds nothing.
  - `specs/build-harness.md:315` (part K, `factory archive ID`) names only one refusal: a delta that does not apply → exit 2.
  - `specs/build-harness.md:285` (part H): "`factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`". So any exit 2 parks.
  - `specs/build-harness.md:193` (part B, Spec store): "`factory init` creates `openspec/config.yaml` …". `:311` (`approve-spec`) is where pinning happens.
  - `docs/spec-factory.md:94`: "A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans … or closes the parent." The same "does not apply" wording is on `:80`, `:89` and `:123`. None of these covers a missing change folder or a missing spec store.
  - The Changelog section exists at `docs/spec-factory.md:650`.
  - `plans/P0-intake-skeleton.md:52` says "three real faux-specs" and `:116` says "which three faux-specs to use is your call". The pilots are not named today.
- Reference harness (read only; `~/dev/nanobot-upstream`, branch `feat/lionbot-v3`):
  - `factory/cli.py:439` `Refused("no spec store (factory init not run)")`
  - `factory/cli.py:441` `Refused(f"{t['id']} has no change folder to archive")`
  - This matches the answer's context line citing `fffeddcf6`.
  - `git log -1 820290e0d`: "store: factory init — OpenSpec tree … pilots stay old-format". This matches the answer's statement that green's live store was initialised and the pilots stay old-format.
- Pilot cohort (checked read only in run-0040): T-0001 SPEC-21, T-0002 SPEC-26 and T-0003 SPEC-27 are all `status: planned`, with pinned `approved_version`s, and green's `openspec/changes/` is empty.
- Requester quote: "Nothing in the documents says what the operator does with such a park."
- No duplicate. T-0001..T-0009 in `intake/state/tickets/` are closed. T-0008 created the archive step and sent pilot migration to the Nanobot side (`intake/answers/T-0008-2.md` A1).

Assumptions (triage inferences, not stated by the requester):
- A1: "close the parent as applied" means the parent reaches `closed` through the existing human close path (the resolution list's "closes the parent"). It does not mean a new automatic transition. Under option (a), part H's park-on-exit-2 behaviour is unchanged. Option (c), which skips the park, was not chosen.
- A2: The resolution applies only to the two new refusals ("no change folder", "no spec store"). The existing "does not apply" park keeps its current resolution (amend and re-plan, or close).
- A3: No `prompts/` file needs re-copying. The park and resolution lists are routing-rule text, not prompt blocks. The writer should confirm this by checking whether any edited line sits inside a block that `prompts/` copies.
- A4: Recording the pilots in the P0 plan adds new text to that plan (one line). It does not correct anything there. Per the answer, the pilots "are built as planned".
- A5: Acceptance should be checkable with grep/diff from `~/dev/spec-factory`, as the run context requires. Example: Given part K, when the operator reads `factory archive`, then it names "no change folder" and "no spec store" as distinct exit-2 refusals and states their park resolution. The new criteria fail on this checkout today (the grep above finds nothing), so passing them later is real evidence.
- Suggested priority (a suggestion only; priority is a human call): low-medium. No pilot has reached parent close yet.

Reason: Intent is clear and the product decision is settled by the operator's answer (a); no facts are missing.

STATUS: ACCEPT
CONFIDENCE: high, because the decision is answered in `intake/answers/T-0010.md`, and every document anchor and reference refusal was re-read on this checkout (HEAD `555c119`) and green (`factory/cli.py:439,441`, `820290e0d`).
ESCALATIONS: none
