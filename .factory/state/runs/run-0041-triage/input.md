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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0041-triage/output.md`

## Request (raw, with any answers appended)

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

## Your previous Triage output (the question you asked is answered above)

Type: bug

Title: Build spec / P0 plan: say how a parent closes when its pinned spec has no change folder (pinned before the spec store existed), instead of leaving an unexplained `archive` park

Summary: Some parents had their specs pinned before `factory init` created `openspec/`. The three green pilots are examples: SPEC-21, SPEC-26 and SPEC-27, all `planned` with old-format specs. These parents have no `openspec/changes/<ID>/` folder. At parent close, `factory archive` will refuse with exit 2, and part H then parks the parent. Nothing in the documents says what the operator does with that park, so each operator has to decide between re-intake and archiving by hand. The requester wants the documents to name this case and give one resolution for it. The requester's suggested resolution: close the parent as applied, with no current-truth update, and re-intake the spec as a new ticket if current truth should carry it. The P0 plan would record the three pilots as that cohort.

Evidence:
- Request: `intake/state/requests/T-0010.md`, which matches `issues/10_pre_init_pinned_specs.md` (`diff` gave no output). Source commit `3d2ef71`.
- The build spec covers only one archive refusal. `specs/build-harness.md:315` (part K, `factory archive`) ends "A delta that does not apply → exit 2, nothing written". It says nothing about a missing change folder. `grep -n -i "no change folder" specs/build-harness.md docs/spec-factory.md plans/P0-intake-skeleton.md` finds nothing.
- Part H (`specs/build-harness.md:285`): "`VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`". So any exit 2 parks, which matches the requester's claim.
- Part B (`specs/build-harness.md:193`): "`factory init` creates `openspec/config.yaml` …". The change folder is written only when a version is pinned (`approve-spec`, K at `:311`; `--amend-spec`, `:314`).
- The design doc names only one archive park, and gives it a resolution:
  - `docs/spec-factory.md:89`: "an archive that does not apply (Spec store) park[s] the ticket".
  - `docs/spec-factory.md:94`: "an archive that does not apply … parks the parent: the human amends the spec and re-plans … or closes the parent".
  - `docs/spec-factory.md:80` and `:123` say the same.
  - A missing change folder is not "a delta that does not apply", so the documents do not cover this park.
- Reference harness, read only. `~/dev/nanobot-upstream` is on `feat/lionbot-v3`, and `git log -1 fffeddcf6` gives "factory(spec store): OpenSpec tree … init, gate pinning, spec tasks, archive".
  - In `factory/cli.py` `archive_cmd`, the refusals are, in order:
    - `Refused("no spec store (factory init not run)")`
    - `Refused(f"{t['id']} has no change folder to archive")`
    - `Refused("archive does not apply: …")`
  - `factory/store.py:24`: `Refused` is "exit 2, store unchanged".
  - No reference workflow calls `archive` yet: grep under `factory/` finds only the `cli.py` parser entry and `specstore.py`. So the requester's statement that the pilots will be parked describes what the spec says will happen. It has not been observed.
- Pilot cohort, checked read only in green's `knowledge_vault/spec_factory/`:
  - T-0001 "SPEC-21: Session Health Monitoring": `status: planned`, `approved_version: 3`.
  - T-0002 "SPEC-26 …": `planned`, `approved_version: 2`.
  - T-0003 "SPEC-27 …": `planned`, `approved_version: 1`.
  - `openspec/changes/` is empty.
- Requester quote: "Nothing in the documents says what the operator does with such a park." The requester's cost figure, "12–56M context tokens each" for re-intake, was not verified.
- Related operator rulings on T-0008 (OpenSpec schema):
  - `intake/answers/T-0008-2.md` A1: "migrating green's pilot specs (SPEC-21, SPEC-27) … are Nanobot-side follow-ups, outside this ticket".
  - `intake/answers/T-0008-3.md` #4: "An archive refusal reuses the existing parent-park resolution (amend the spec and re-plan, or close)."
  - Read together, the current rule may already cover this park. But it was written for the "does not apply" refusal, and it does not say what "close" means for current truth.
- Duplicate search: no duplicate. T-0001..T-0009 in `intake/state/tickets/` are all closed. T-0008 (OpenSpec tree) is the closest; it created the archive step but left the pilot migration to the Nanobot side (A1 above). T-0010 is this request's own ticket.

Assumptions (triage inferences, not stated by the requester):
- A1 (cohort scope): in the build spec's own world, `factory init` creates the `tickets` branch that `approve-spec` writes to. So a spec pinned before init can only exist in a store that predates the spec store, such as the P0 store and its green pilots. Whether build-spec part K needs the sentence at all, or only the P0 plan does, depends on the decision below.
- A2 (two refusals): the request's parenthetical "(pinned before `factory init`, or in a store where `init` has not run)" covers two refusals that are separate in the reference: "no spec store" and "no change folder". I assume the requester means both, with the same resolution.
- A3 (location): the request is labelled `design-doc`, but its "Where" names only `specs/build-harness.md` (K, B) and `plans/P0-intake-skeleton.md`. Any new park or resolution case would also touch the design doc's park list and resolution list (`docs/spec-factory.md:89`, `:94`), so it would need a Changelog entry. Those are routing-rule text, not prompt blocks, so no `prompts/` re-copy is expected.
- A4 (P0 plan): `plans/P0-intake-skeleton.md` does not name the three pilots today. It says "three real faux-specs" (line 52), and its ESCALATIONS line (116) says "which three faux-specs to use is your call". Recording them would be new text, not a correction.
- A5 (`planned`): `planned` is a state in the reference harness (`factory/store.py:20`). It does not appear in `specs/build-harness.md` or `docs/spec-factory.md`. The requester's point that "`planned` has no routing edge back to the writer" is about the reference, not the documents.
- Suggested priority (a suggestion only; priority is a human call): low-medium. No pilot has reached parent close, and no reference workflow runs `archive` yet.

Question for human: How should the documents resolve a parent-close `archive` refusal caused by a missing change folder or a missing spec store (a spec pinned before the spec store existed)?
- (a) Requester's proposal. Name "no change folder" (and "no spec store") as distinct archive refusals in part K. Their park resolves by closing the parent as applied: current truth and `decisions.md` are not updated, and the spec is re-intaken as a new ticket if current truth should carry it. Add the case to the design doc's park and resolution lists, with a Changelog entry. The P0 plan records SPEC-21, SPEC-26 and SPEC-27 as that cohort. Suggested default: it is the cheapest option and fits T-0008 A1, which already sent pilot migration to the Nanobot side.
- (b) Reuse the existing rule. Name the refusal in part K, and say its park takes the existing archive-park resolution (`docs/spec-factory.md:94`; T-0008 answer #4). The operator either runs `--amend-spec` with a well-formed four-part version, which writes the change folder, re-plans, and archives at the next parent close, or runs `--close`. No new resolution rule; the P0 plan notes the pilots will take this path.
- (c) Prevent the park. Parents pinned before the spec store are marked when it activates, and parent close for them skips `archive` and goes straight to `closed`, with a logged event. Nothing parks. This changes harness behaviour (parts B and H, plus a new acceptance item), not just documentation.

STATUS: NEEDS-HUMAN
CONFIDENCE: high, because the spec gap, the design doc's single archive-park case, the reference refusal text and the pilot states were each checked by grep or read on the cited files; the open item is a choice of rule, not a missing fact.
ESCALATIONS: none
