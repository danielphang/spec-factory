## Problem

Some specs were pinned before `factory init` created `openspec/`. A parent whose spec was pinned that way has no `openspec/changes/<ID>/` folder. Its parent-close VERIFIED runs `factory archive`, which exits 2, and `build.js` parks the parent (build spec part H). The documents name only one archive refusal, "a delta that does not apply", and its resolution is to amend the spec and re-plan, or to close. A store where `factory init` has not run at all has the same gap. So the operator who finds this park has no stated path. Without one, the park looks like a harness bug, and each operator decides again between re-intake and archiving by hand. This affects every store that adopts the spec store after its first tickets. Today that means green's three pilots: SPEC-21, SPEC-26 and SPEC-27.

The operator chose option (a) (`intake/answers/T-0010.md`):
- Part K names "no change folder" and "no spec store" as separate refusals.
- That park is resolved by closing the parent as applied. Current truth and `decisions.md` are not updated, and the spec is re-intaken as a new ticket if current truth should carry it.
- The design doc's park and resolution lists carry the case, with a Changelog entry.
- The P0 plan records the three pilots as that cohort.

## Evidence

All commands were run from `~/dev/spec-factory` (branch `main`, HEAD `555c119`) unless noted.

- `grep -n -i "no change folder\|no spec store" specs/build-harness.md docs/spec-factory.md plans/P0-intake-skeleton.md` returns no output, exit 1.
- In `specs/build-harness.md`:
  - Line 315 (K, `factory archive ID`) ends "A delta that does not apply → exit 2, nothing written." It names no other refusal.
  - Line 285 (H) reads "`VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`". So every exit 2 parks, and the stderr text becomes the park reason.
  - Line 193 (B, Spec store): "`factory init` creates `openspec/config.yaml` … Pinning a version (K) splits it … into `openspec/changes/<ID>/<path>`." Nothing covers a version pinned before init.
  - Line 314 (K, `resolve`): "`--close` closes the parent and its unmerged sub-tickets". This is the existing human close path the resolution uses. Item 84 (line 458) already exercises `--close` on a parked parent.
  - Line 160 says `factory init` "creates the `tickets` branch and its checkout"; the store's working tree is called the `tickets` checkout below. Line 202 defines `factory ticket park ID --reason R --outputs RUN,RUN [--question PATH]`.
  - Item 88 (line 474) pins `specs/T-0001/v1.md` with `AS daniel factory approve-spec T-0001 --version 1` and checks `openspec/changes/T-0001/`. Item 89 (line 475) tests only the "does not apply" archive refusal. The last acceptance item is 90 (line 476). Line 482 reads "Items needing the bare repo: … 88, 89, 90."
- In `docs/spec-factory.md`, "does not apply" is the only archive park in each of these places:
  - Line 80 (Spec store): "A delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing) writes nothing and parks the parent."
  - Line 89 (park list): "Only NEEDS-HUMAN, … a parent-close FAILED, and an archive that does not apply (Spec store) park the ticket."
  - Line 94 (resolution list): "A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (…) or closes the parent."
  - Line 123 (merge-gate row): "FAILED, SPEC-DEFECT or an archive that does not apply parks the parent in the human queue".
  - The Changelog is at line 650. Its last numbered entry is 39 (line 692). `Declined:` is at line 694.
  - `grep -c 'factory init' docs/spec-factory.md` → `0`; `grep -c 'openspec/' docs/spec-factory.md` → `3`. The design doc names the `openspec/` tree but never the CLI command, so the doc text below says "before the repo had an `openspec/` tree", not "before `factory init`".
- None of the lines to be edited is inside a block that `prompts/` copies:
  - The design doc's first fenced block opens at line 163. Every edit is at line 123 or earlier, or in the Changelog (lines 650–694), which lies between the fences that close at line 648 and open at line 700 (critic round 1 confirmed these fence lines).
  - `grep -l archive prompts/*` returns no output, exit 1.
  - So no `prompts/` file needs re-copying, which confirms triage assumption A3 (no `prompts/` re-copy).
- In `plans/P0-intake-skeleton.md`, line 52 reads "## What you measure (three real faux-specs)", line 100 is `## Risk`, and line 116 reads "which three faux-specs to use is your call". `grep -c SPEC-21 plans/P0-intake-skeleton.md` returns `0`.
- Reference harness, read only (`~/dev/nanobot-upstream`, `feat/lionbot-v3`):
  - `factory/cli.py` `archive_cmd` refuses, in order: no spec store (`no spec store (factory init not run)`), then no change folder (`<ID> has no change folder to archive`), then a delta that does not apply. It does not check the ticket's status.
  - Reproduced in a scratch store (`FACTORY_STATE` pointed at a new directory under the session scratchpad, `PYTHONDONTWRITEBYTECODE=1`, green's `.venv/bin/python -m factory`): `ticket new --file r.md` → `T-0001`; `archive T-0001` → stderr `no spec store (factory init not run)`, exit 2; `init`; `archive T-0001` → stderr `T-0001 has no change folder to archive`, exit 2. The log holds only `request.created`, `ticket.created`, `store.initialised`; no `change.archived`. `git status` in `~/dev/nanobot-upstream` afterwards shows only a pre-existing `webui/package-lock.json` modification, not from this run.
  - The commit that initialised green's live store says the three pilot specs (T-0001, T-0002, T-0003) were pinned before init, have no change folder, and that a later `factory archive` on them parks the parent by design.
  - In `knowledge_vault/spec_factory/tickets/`: T-0001 is `SPEC-21: Session Health Monitoring`, T-0002 is `SPEC-26: …`, T-0003 is `SPEC-27: …`; all `status: planned`, with `approved_version` 3, 2 and 1. `openspec/changes/` is empty.

## Root cause

When the spec store was added, the documents did not cover tickets pinned before the store existed. Part K of `specs/build-harness.md` (`factory archive ID`) lists one refusal, and part B (Spec store) assumes every pinned version has a change folder. The design doc's Spec store paragraph, park list, resolution list and merge-gate row (`docs/spec-factory.md` lines 80, 89, 94 and 123) do the same. The reference harness already refuses both missing-folder cases with exit 2. Part H turns that exit into a park whose resolution nothing documents.

## Proposed change

All edits are in three files. Part H's park-on-exit-2 behaviour is unchanged (triage A1: no new automatic transition). The existing "does not apply" resolution is unchanged (A2).

**A. `specs/build-harness.md`, part K, `factory archive ID` bullet (line 315).** Replace the final sentence "A delta that does not apply → exit 2, nothing written." with:

> Refusals, each exit 2 with nothing written, checked in this order before (1): no `openspec/` → `no spec store (factory init not run)`; no `openspec/changes/<ID>/` (its spec was pinned before `factory init`) → `<ID> has no change folder to archive`; a delta that does not apply. H parks the parent on each. A park for no spec store or no change folder is resolved by `factory resolve ID --close`, which closes the parent as applied: `openspec/specs/` and `decisions.md` stay unchanged, and if current truth should carry the spec, it is re-intaken as a new ticket (doc §Routing rules, resolution list).

**B. `specs/build-harness.md`, part B, Spec store paragraph (line 193).** After the sentence ending "into `openspec/changes/<ID>/<path>`.", insert:

> A version pinned before `factory init` created `openspec/` has no change folder; its parent's archive refuses (K).

**C. `specs/build-harness.md`, acceptance.** Under "### Spec store [S3, S4]", after item 90, add:

> 91. ⟨bare⟩ **Archive refusals without a change folder (K):** T-0001 pinned as in item 88's first half (`specs/T-0001/v1.md`, `AS daniel factory approve-spec T-0001 --version 1`). (a) On the `tickets` checkout, `git rm -r -q openspec/changes/T-0001 && git commit -q -m setup`; then `factory archive T-0001` → exit 2, stderr `T-0001 has no change folder to archive`. (b) Then `mv openspec ../openspec.aside` on the `tickets` checkout; `factory archive T-0001` → exit 2, stderr `no spec store (factory init not run)`. In (a) and (b) the `tickets` checkout's `git rev-parse HEAD` and `git status --porcelain` are the same after the command as before it, and `factory log tail --event change.archived` gained no line [NEW]

In the line "Items needing the bare repo: … 88, 89, 90.", change the ending to "88, 89, 90, 91.".

The setup in (a) is mechanical and does not depend on what `approve-spec` does without `openspec/`. The resolution (`resolve --close` on the resulting park) is not a separate acceptance step: it is the existing `--close` on a parked parent, which item 84 already exercises, so a step for it would pass against today's spec and prove nothing.

**D. `docs/spec-factory.md`, routing text.**
1. Line 80 (Spec store). Replace "A delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing) writes nothing and parks the parent." with:

   > An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree).

2. Line 89 (park list). Replace "and an archive that does not apply (Spec store)" with "and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store)".

3. Line 94 (resolution list). Keep the line as it is. Insert a new bullet directly after it, at the same indent (`  - `):

   > An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth and `decisions.md` are not updated; if current truth should carry the spec, it is re-intaken as a new ticket.

4. Line 123 (merge-gate row). Replace "FAILED, SPEC-DEFECT or an archive that does not apply parks the parent in the human queue" with "FAILED, SPEC-DEFECT or an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) parks the parent in the human queue".

**E. `docs/spec-factory.md`, Changelog.** After entry 39, append:

> 40. After the pilot specs on Nanobot green (2026-10-01): archive has two more refusals, no change folder (a spec pinned before the repo had an `openspec/` tree) and no spec store. Each parks the parent like a delta that does not apply, but the human closes that parent as applied: current truth and `decisions.md` are not updated, and the spec is re-intaken as a new ticket if current truth should carry it.

**F. `plans/P0-intake-skeleton.md`.** Add one line, a new paragraph directly before "## Risk" (line 100):

> The three pilots are SPEC-21, SPEC-26 and SPEC-27 (green's T-0001, T-0002, T-0003). Their specs were pinned before `factory init` created `openspec/` (2026-10-01), so they have no change folder: each parent-close `factory archive` refuses with `no change folder`, the parent parks, and the human closes it as applied (build spec K).

Leave line 116 (the planner's recorded trailer) unedited. Triage A4 (the pilot line is added text, not a correction): the pilots are recorded, not corrected.

No `prompts/` file changes (see Evidence).

## Acceptance

Run every command from `~/dev/spec-factory`. Each command was run on `555c119` and gave the "today" value shown.

- `sed -n '/^### K\./,/^### L\./p' specs/build-harness.md | grep 'factory archive ID' | grep 'no spec store' | grep -c 'no change folder'` → `1` [NEW; today `0`: the bullet names only "A delta that does not apply"]
- `sed -n '/^### K\./,/^### L\./p' specs/build-harness.md | grep 'factory archive ID' | grep 'resolve ID --close' | grep 'as applied' | grep -c 'new ticket'` → `1` [NEW; today `0`: K states no resolution for an archive park]
- `sed -n '/^### K\./,/^### L\./p' specs/build-harness.md | grep 'factory archive ID' | grep -ci 'delta that does not apply'` → `1` [REGRESSION; today `1`]
- `grep -cF "park --reason 'archive: <stderr>'" specs/build-harness.md` → `1` (part H still parks on every archive exit 2) [REGRESSION; today `1`]
- `grep '^\*\*Spec store\*\*' specs/build-harness.md | grep -c 'no change folder'` → `1` [NEW; today `0`]
- `grep '^91\. ' specs/build-harness.md | grep -F 'no spec store (factory init not run)' | grep -F 'T-0001 has no change folder to archive' | grep -c 'git rm -r'` → `1` (both refusals, with a mechanical setup) [NEW; today `0`: the last item is 90]
- `grep -c '^Items needing the bare repo:.* 91\.' specs/build-harness.md` → `1` [NEW; today `0`: the list ends "88, 89, 90."]
- `grep 'Only NEEDS-HUMAN' docs/spec-factory.md | grep 'no change folder' | grep -c 'no spec store'` → `1` [NEW; today `0`: the park list names only "an archive that does not apply"]
- `grep '^  - ' docs/spec-factory.md | grep 'no change folder' | grep 'no spec store' | grep 'as applied' | grep -c 'new ticket'` → `1` [NEW; today `0`: no resolution bullet names such a case]
- `grep -cxF '  - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent.' docs/spec-factory.md` → `1` (the "does not apply" resolution is unchanged) [REGRESSION; today `1`]
- `sed -n '1,/^## Changelog/p' docs/spec-factory.md | grep -c 'no change folder'` → `4`: the Spec store paragraph, the park list, the new resolution bullet and the merge-gate row [NEW; today `0`]
- `sed -n '/^## Changelog/,/^Declined:/p' docs/spec-factory.md | grep '^40\. ' | grep 'no change folder' | grep -c 'as applied'` → `1` [NEW; today `0`: the last entry is 39]
- `grep -c 'factory init' docs/spec-factory.md` → `0` (the design doc keeps naming the tree, not the CLI command) [REGRESSION; today `0`]
- `grep 'SPEC-21' plans/P0-intake-skeleton.md | grep 'SPEC-26' | grep 'SPEC-27' | grep -c 'no change folder'` → `1` [NEW; today `0`: the pilots are not named]
- `grep -c 'which three faux-specs to use is your call' plans/P0-intake-skeleton.md` → `1` (the planner's trailer is not rewritten) [REGRESSION; today `1`]
- `grep -l archive prompts/*; git diff --stat main...HEAD -- prompts/ | wc -l` → no file listed, then `0` (no prompt block carries the edited text, and `prompts/` is untouched) [REGRESSION; today the same]
- `git diff --check main...HEAD` → no output, exit 0 [REGRESSION; today exit 0]

## Tests to change

none. Item 91 is a new acceptance item in the build spec. Items 84, 88, 89 and 90 and the rest are untouched, and no test file exists in this repo.

## Out of scope

- Part H of `specs/build-harness.md` and its park-on-exit-2 behaviour. No automatic close and no skip of the park: option (c) was not chosen.
- The resolution for "a delta that does not apply" (amend and re-plan, or close).
- The `resolve --close` semantics in K. They are used as written, with no new flag and no new `closed_reason` value.
- Any `prompts/` file, `AGENTS.md`, skills, the reference harness at `~/dev/nanobot-upstream/**`, and the pilots' tickets or specs on green.
- Migrating the pilots to four-part specs. Per the answer, they are built as planned.

Out-of-scope observations:
- Part K's `approve-spec` says it "writes the pinned version as the change folder" without saying what happens when `openspec/` is absent. The reference harness pins without a folder in that case, which is how a "no spec store" park can arise in practice. Item 91 no longer depends on this. A separate ticket could decide whether `approve-spec` should refuse there instead.
- `factory spec tasks` (B, run by `build.js` phase Plan) has the same unstated case: a parent with an active store but no change folder. The reference harness refuses it with exit 2 (`has no change folder (no pinned version)`). Green's pilots are past planning, so they do not hit it, but a pre-init parent that is still `ready-for-planner` when `init` runs would. A separate ticket.
- The reference `factory ticket park` refuses a ticket in status `planned`, a state the build spec's state list does not name. Not relevant here (a parent at parent close is `ready-for-parent-verify`), noted only as drift.
- A parent closed as applied is recorded only as a human `--close`. Nothing in the ticket marks the close as "applied". An auditor tells it apart from an abandoned parent only by the preceding `parked.reason` (`archive: … no change folder …`) in its history. If retro metrics need to count these separately, that is a later ticket.

## Open questions

none. The operator's answer (a) settles the product decision. Triage A1–A4 were checked against the documents and adopted as written:
- A1: "close as applied" uses the existing human `--close`; no new automatic transition.
- A2: the resolution covers only the two new refusals.
- A3: no `prompts/` file needs re-copying.
- A4: the pilot line is added text, not a correction.

## Risk

The blast radius is documents only: `specs/build-harness.md` (parts B and K, one new acceptance item, and the bare-repo item list), `docs/spec-factory.md` (four routing-text edits, one new resolution bullet, Changelog entry 40), and `plans/P0-intake-skeleton.md` (one new paragraph). This changes the build spec, so a harness built from it gains item 91. Both of item 91's refusals were reproduced against the reference harness in a scratch store (Evidence); the full ⟨bare⟩ item, with `approve-spec` and the `tickets` checkout, was not run. Protected paths touched: none. `prompts/**` is not touched because no edited line is in a copied block, and `intake/**`, `~/dev/nanobot-upstream/**` and `~/.nanobot/**` are not touched (the reference was only executed against a scratch `FACTORY_STATE`, with bytecode writes off).

## Responses

- [BLOCKING] Proposed change C, item 91 (b) setup — FIXED. Item 91 now uses a mechanical, store-independent setup: T-0001 pinned as in item 88, then `git rm -r -q openspec/changes/T-0001 && git commit -q -m setup` on the `tickets` checkout for the no-change-folder case, then `mv openspec ../openspec.aside` for the no-spec-store case. The "pinned before `factory init`" parenthetical is gone from the item and stays only in the prose of B and K. Nothing in the item depends on what `approve-spec` does without `openspec/`. The "no change" check is now `git rev-parse HEAD` and `git status --porcelain` before and after, which works even with `openspec/` moved aside. The acceptance grep now checks for both exact stderr messages and `git rm -r`. I ran both refusals against the reference harness in a scratch store (Evidence): exit 2 with exactly these messages, no `change.archived`.
- [SHOULD-FIX] D.1 wording — FIXED, with different words from the suggestion. The garbled clause now reads "no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree)". I did not use "before `factory init`" because `grep -c 'factory init' docs/spec-factory.md` → `0`: the design doc names the `openspec/` tree and never the CLI command. Changelog entry 40 (E) follows the same wording, and a REGRESSION item keeps `factory init` out of the doc. The B, K and P0-plan text still says `factory init`, which those documents do use. The `grep -c 'no change folder'` → `4` count is unchanged.
- [NIT] Reference SHAs in Evidence — FIXED. The reference commit SHAs and branch-head SHA are removed. The evidence now describes the behaviour and the commit message's content, plus a scratch-store reproduction.
- [NIT] Item 91 (c) tests only the existing `--close` — FIXED by removing (c). Item 84 already covers `--close` on a parked parent, so (c) would pass against today's spec. Keeping it would also have needed a park setup (`factory ticket park … --outputs RUN,RUN`, line 202) with no natural run to name. The resolution stays specified in K's text (A) and the doc (D.3), and the K grep criteria check it.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high, because every anchor and "today" value was re-run on `555c119`, and both refusals in item 91 were reproduced against the reference CLI in a scratch store
ESCALATIONS: none
