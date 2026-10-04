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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0042-spec_writer/output.md`

## Ticket (Triage output)

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

## Request (raw)

---
title: Build spec: a spec pinned before `factory init` has no change folder; say how its parent closes
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` part K (`factory archive`) and part B "Spec store"; `plans/P0-intake-skeleton.md` (the three pilot specs). The spec store activates when `factory init` creates `openspec/`; a store's specs pinned before that are one text each, with no `openspec/changes/<ID>/` folder.

**What happened (2026-10-01, Nanobot green):** the harness gained the spec store (`fffeddcf6`) while three pilot tickets (SPEC-21, SPEC-26, SPEC-27) were already `planned` with old-format specs pinned. `planned` has no routing edge back to the writer, so the only pipeline path to a four-part spec is a fresh ticket per request (triage, writer and critic again, 12–56M context tokens each). Left as they are, each pilot's parent-close VERIFIED will run `factory archive`, which exits 2 ("no change folder to archive") and parks the parent, as the rules say. Nothing in the documents says what the operator does with such a park.

**Why it matters:** every store that adopts the spec store after its first tickets has this cohort. Without a stated path the parks read as harness bugs, and each operator re-decides between re-intake and a hand archive.

**Proposed fix (spec K, one sentence; P0 plan, one line):** a parent whose pinned spec has no change folder (pinned before `factory init`, or in a store where `init` has not run) closes without archive: `archive` reports `no change folder` as a distinct refusal, and the resolution rule for that park is "close the parent as applied; its spec is not current truth, re-intake it as a new ticket if current truth should carry it". The P0 plan records the three pilots as that cohort.

**Fix as implemented on the Nanobot side:** none yet; `factory archive` already refuses with `has no change folder to archive` (green `fffeddcf6`).


## Answer 1

Answer to Triage's question. Taken as the recommended default under the operator's standing take-the-recommendation rule; reversible at the spec gate.

**(a).** Part K names "no change folder" and "no spec store" as distinct archive refusals. Their park resolves by closing the parent as applied: current truth and `decisions.md` are not updated, and the spec is re-intaken as a new ticket if current truth should carry it. Add the case to the design doc's park and resolution lists, with a Changelog entry. The P0 plan records SPEC-21, SPEC-26 and SPEC-27 as that cohort.

Context the writer can rely on: green's live store was initialised on 2026-10-01 (`820290e0d`); the three pilots stay old-format and are built as planned (Driver's default, taken). Green's `factory archive` already refuses with `has no change folder to archive` and `no spec store (factory init not run)` (`fffeddcf6`).
