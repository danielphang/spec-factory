Critic, round 2 (spec v3).

What I checked myself:
- `~/dev/spec-factory` `main` is at `9b6a771`, one intake commit past the spec's `b4d0f90` (`git log --oneline b4d0f90..HEAD` → `9b6a771 intake(T-0009): critic APPROVE round 1, awaiting gate`); `git diff --stat b4d0f90 HEAD -- docs specs prompts README.md plans` and the same against `4cd8d12` are both empty, so "today" still holds for every document.
- Every OLD anchor in parts A–L (26 strings, including the three new in v3) matches exactly once in its file (`grep -c -F`); the `- \`factory resolve ID (` bullet is the only such bullet in part K and the last before `### L.`; `### Gates (every seam)` is preceded by item 86 and a blank line.
- Trial apply: my own script applied A–L to a scratch clone of `main`, re-copied the two prompts with the part G `awk` commands, and committed. `git diff --stat main...HEAD` → `4 files changed, 97 insertions(+), 29 deletions(-)` (doc 60, writer prompt 29, planner prompt 8, build spec 29), `git diff --check` exit 0. Identical to the spec's figures.
- All 20 Acceptance commands, run as written on the clone and on `main`. Clone: the four parts; the mapped `proposal.md:Problem;…` string; `7 0`; clean + `4` (exit 0); clean + `3`; `10`; `3`; `2`; `2`; `CONTIGUOUS LAST-IS-SPEC-STORE`; `9 3 0`; `6`; 13–16 empty; 17 empty (exit 1); 18 empty; 19 empty (exit 1); 20 clean (exit 0). `main`: empty; `:Problem;…`; `0 1`; `0` (exit 1); `0`; `0`; `0`; `0`; `0`; `CONTIGUOUS LAST-IS-OTHER`; `0 0 1`; `6`; 13–20 as on the clone. Every result matches the spec's quoted results; every NEW item fails today for the stated reason.
- Build spec B, `factory run compose`: "the 'with input =' lists in H, read from the store and `~/factory/clone`" (line 202); H `intake.js` step 2 holds both lists part K edits (line 277); part H adds `openspec/` to the store listing (line 152). Item 42's writer `input_sources` is written as an exact list and the critic's as "exactly `[specs/T-0001/v1.md]`"; items 37 and 86 say "lists"; `factory init` is a defined command (8 mentions). So the item-42 reasoning (empty `openspec/specs/` after init) and the item-37/86 reasoning hold.
- Reference harness (read only): `factory/status.py:54 def strip_trailer`, `factory/cli.py:244 return status.strip_trailer(...)`, `factory/cli.py:269 rel = f"plans/{t['id']}.md"`. The trailer claim in part I is as built.
- `factory request new` (4 mentions), `park --reason` (6 mentions) and the stub-case driver (`args: {ticket, stubs}`; `factory run build T-0001 --stubs …`) exist in the build spec, so items 88 and 89 are expressible with its vocabulary.

Prior findings (round 1):
1. [BLOCKING] current truth declared but never composed — RESOLVED. K1/K2 put current truth into both H input lists, with the `input_sources:` rule; compose reads those lists from the store and `openspec/` is in the store (part H); item 89 covers a non-empty current truth; Acceptance 11 counts both compose texts (`9 3 0`, verified).
2. [SHOULD-FIX] "verbatim" vs trailer-stripped storage — RESOLVED. Part I: "trailer removed: the text above its last `STATUS:` line, as item 42 requires"; `factory spec tasks` and item 88 say the same for `tasks.md`.
3. [NIT] two Author-cell deviations — RESOLVED (both named with reasons after the table).
4. [NIT] "malformed" undefined — RESOLVED (well-formed rule in part I; J1 says "malformed (B)").
5. [NIT] stale "Acceptance line itself" — RESOLVED (D1; Acceptance 3 checks presence of the new phrase and absence of the old, `7 0` verified).

New findings on changed text:

[SHOULD-FIX] 6, 3 — Part J (J1 `approve-spec` refusal, J2 `--amend-spec` "rewrites the change folder as `approve-spec` does")
Problem: After J1 every spec that reaches `approve-spec` must be a well-formed four-part version, which silently changes the precondition of every existing ⟨wf⟩⟨bare⟩ build item that runs "on an approved spec" (43–53, 77, 83, 84: their `spec_writer-1.md` stubs must now be four-part documents) and of item 83's `--amend-spec spec2.md`, and J2 leaves open whether `--amend-spec` applies the same well-formed/does-not-apply refusal (exit 2, nothing re-pinned) or re-pins first.
Evidence: J1 text; build spec line 398 "Driver: … on an approved spec"; item 83 `--amend-spec spec2.md` → `approved_version: 2`; the reference harness today has only intake-side stub cases (`tests/factory/fixtures/stubs/{accept-approve,clarify,reject,revise-twice}`), so the build cases' stubs are still to be written and nothing in the spec tells their author the new shape is mandatory; "Tests to change: none" is correct for this repo but the consequence is undeclared anywhere.
Suggested fix: One sentence in part L's heading paragraph or under Risk ("every case whose spec is approved needs a well-formed `spec_writer-1.md`; `--amend-spec FILE` applies the same check and exits 2 with nothing re-pinned when FILE fails it"), and the matching clause in J2.

[NIT] 6 — Part I, well-formed rule
Problem: A version with no delta part is well-formed under the rule as written ("every delta part has…" holds vacuously), which gives a change with zero scenarios, so the parent-close verifier has nothing to run and returns VERIFIED trivially.
Evidence: Part I rule; FORMAT "one part per capability changed"; K4 "every delta scenario".
Suggested fix: Add "at least one delta part" to the well-formed rule, or say zero is allowed and the parent-close run is then vacuous.

Rubric items with no finding: 1 (all anchors and the reference-harness symbols exist; the OpenSpec quotes were confirmed in round 1 and are unchanged), 2 (all 20 items reproduce; the three new build-spec items fail today as E1/E2 like their neighbours), 4 (the two Author deviations and the `spec-driven` correction are declared; protected `prompts/` files and guardrail blocks declared under Risk), 5 (T-0007 and T-0009 overlap claims re-checked: no shared OLD text; routing From/STATUS cells unchanged, Acceptance 16).

Out-of-scope observations:
- The spec's checkout SHA (`b4d0f90`) is one commit stale; documents identical, so nothing in the spec depends on it. The implementer should expect Changelog 39 and items 87–89 to still be the right numbers unless T-0009 merges first.
- The approve-spec sentence after J1 lists "pins `approved_version` … `approvals/ID/spec-v<N>.yaml`, writes the pinned version as the change folder (… exit 2 with nothing written …)" in an order that reads as pin-then-refuse; item 87 pins the real behaviour (`approved_version: 1`, no `spec-v2.yaml`), so an implementer has the answer, but the bullet could say "checks first".
- Reference-harness `plan add` / `plans/<ID>.md` duplication with `factory spec tasks`: unchanged from round 1, still not this ticket's defect.

STATUS: APPROVE
CONFIDENCE: high — every anchor, the diff stat and all 20 commands reproduced on my own clone on both sides; the one BLOCKING finding from round 1 is resolved by text I verified against the build spec's compose mechanism; the remaining findings are clarifications an implementer can resolve from items 87 and 83 without changing the outcome.
ESCALATIONS: none
