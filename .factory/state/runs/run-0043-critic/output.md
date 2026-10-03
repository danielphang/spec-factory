## Critic review — T-0010 spec v1 (round 1)

Spot-checks run from `~/dev/spec-factory` at `555c119` (branch `main`) and, read only, `~/dev/nanobot-upstream` (`feat/lionbot-v3`).

Grounding verified:
- `grep -n -i "no change folder\|no spec store"` over the three documents → no output, exit 1, as stated.
- `specs/build-harness.md` line 315 ends exactly "A delta that does not apply → exit 2, nothing written."; line 285 carries "park --reason 'archive: <stderr>'"; line 193 is the `**Spec store**` paragraph with "into `openspec/changes/<ID>/<path>`."; line 314 is `factory resolve` with `--close`; items 89 and 90 are at lines 475–476; line 482 ends "88, 89, 90."; `### K.` opens at 307 and `### L.` at 317, so the K/L sed window in the acceptance commands is correct.
- `docs/spec-factory.md` lines 80, 89, 94, 123 contain the exact substrings the spec replaces; `## Changelog` at 650, entry 39 at 692, `Declined:` at 694; fences close at 648 and open at 700, first fence opens at 163, so no edited line sits in a copied block; `grep -l archive prompts/*` → exit 1.
- `plans/P0-intake-skeleton.md`: line 52 and 116 read as quoted; `grep -c SPEC-21` → 0; `## Risk` is at line 100.
- Acceptance "today" values: every NEW command gives `0` and every REGRESSION command gives `1` (or exit 0 for `git diff --check`) on this checkout, as the spec states. I ran all ten grep/sed items plus `git diff --check`.
- Reference harness `factory/cli.py` `archive_cmd` (lines 436–447): `is_active` refusal, then `change_dir(...).exists()` refusal with message `f"{t['id']} has no change folder to archive"`, then `applies`, then write. The order and both messages match proposed text A. `resolve --close` (lines 389–392) refuses only an already-closed ticket, so the resolution path exists as written.
- Commit `820290e0d` exists with the quoted subject and body line; T-0001/2/3 titles are SPEC-21/26/27, all `status: planned`; `openspec/changes/` is empty. The reference branch has moved one commit past the cited `0a5eb7238` (now `564e9367e`; `0a5eb7238` is an ancestor); nothing the spec relies on changed.

Findings:

[BLOCKING] 4, 6 — Proposed change C, item 91 (b)
Problem: The precondition "a parent `T-000m` that has no `openspec/changes/T-000m/` (its spec pinned before `factory init`)" cannot be produced by a harness built from this build spec without an undeclared decision, because K says `approve-spec` "writes the pinned version as the change folder (B; …)" and nothing in B or K says what `approve-spec` does when `openspec/` is absent.
Evidence: `sed -n '307,316p' specs/build-harness.md | grep approve-spec` → "pins `approved_version` … writes the pinned version as the change folder (B; event …)". The spec's own Out-of-scope observations say this behaviour "is not stated" and defer it to a separate ticket, yet item 91 (b)'s setup depends on it. The reference harness happens to pin without a folder when the store is inactive, but the rubric forbids leaning on reference behaviour the spec does not state; an implementer who makes `approve-spec` refuse without `openspec/` (a reasonable reading of K) cannot run (b) and must ask.
Suggested fix: Make (b)'s setup mechanical and store-independent, e.g. "with `openspec/` restored, item 88's T-0001 after `openspec/changes/T-0001/` is removed on the `tickets` checkout: `factory archive T-0001` → exit 2, stderr `T-0001 has no change folder to archive`", keep (c) on the same ticket, drop the "pinned before `factory init`" parenthetical from the item (it stays in the prose of B and K), and update the item-91 acceptance grep from `resolve T-000m --close` to the ticket id actually used.

[SHOULD-FIX] 6 — Proposed change D.1 (doc line 80 replacement)
Problem: "no change folder, because the spec was pinned before the store had a spec store" is garbled (the store is the spec store) and is the one sentence in the design doc that explains the case to a reader.
Evidence: Quoted text of D.1 in the spec; the parallel sentences in A, B, E and F all say "pinned before `factory init`".
Suggested fix: "no change folder, because the spec was pinned before `factory init` created the store; and no spec store at all." The acceptance count (`grep -c 'no change folder'` → 4) is unaffected.

[NIT] 1 — Evidence section
Problem: The spec copies reference-harness commit SHAs (`0a5eb7238`, `820290e0d`) into the spec, which the run context says never to do.
Evidence: Evidence bullets "Reference harness, read only (… at `0a5eb7238`)" and "`git log -1 820290e0d`". Both SHAs are real and the described code matches, so this does not affect correctness; it only pins the document to reference internals.
Suggested fix: Keep the behavioural description and drop the SHAs, or leave as is — not worth a round on its own.

[NIT] 2 — Proposed change C, item 91 (c)
Problem: (c) exercises only the pre-existing `resolve --close` on a parked ticket, so it would pass against a harness built from today's spec; it records the chosen resolution rather than testing new behaviour.
Evidence: K line 314 already defines `--close` on a parked parent; reference `cli.py` lines 389–392 implement nothing archive-specific.
Suggested fix: None required; keeping it as the documented resolution is reasonable. Flagged so no one reads it as proof the harness changed.

Rubric items not flagged: scope fits one PR with a sensible out-of-scope list and an empty "Tests to change" (no test files exist in this repo); no conflict with part H or the "does not apply" resolution, both left verbatim and guarded by REGRESSION items; `prompts/` untouched is proven rather than asserted; Risk declares no protected path and none is touched by A–F.

Prior findings: n/a (round 1).

STATUS: REVISE
CONFIDENCE: high — every cited line, every acceptance "today" value and the reference refusal order were verified by command; the one blocking finding is a setup dependency the spec itself names as unstated.
ESCALATIONS: none
