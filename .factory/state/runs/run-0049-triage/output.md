Type: chore (structural refactor of both repos' layout; it also closes a functional gap: the factory cannot target a second repo without a hand copy)

Title: Move the harness into spec-factory and give each target repo a `.factory/` instance (instance B first; carries #7's harness side)

Summary:
The spec factory cannot be pointed at a second repository without copying its code out of the first one by hand: the harness lives inside the Nanobot fork (green, `feat/lionbot-v3`), and the only other install (this repo's `intake/`) is a `git archive` snapshot of it with three files overwritten, pinned by a hand-kept `HARNESS_PIN`. The requester wants the harness to live in the repo that owns its design (`~/dev/spec-factory`), with each target carrying a small `.factory/` instance that names the harness checkout, records the harness revision it has accepted, and holds its own config, role-context block and store. They also want the four concerns now mixed together (harness code, design doc + prompt copies, the working docs for building the factory, how it is installed) split into directories whose names say which is which. Scope ends when the installed harness runs this repo's own `.factory/` end to end and `factory init` produces a working instance in a throwaway target; moving green (instance A) over is a separate, paired ticket on instance A. The requester marks it NEEDS-SPLIT, with proposed parts A-F as the planner's seams.

Evidence:
- Duplicate search: `issues/README.md` and `intake/state/tickets/*.yaml` (T-0001..T-0011 all `status: closed`). #7 ("Harness instance is single-target", T-0007, closed, `b9379ec`, changelog 38) applied the doc side only; this request carries its open harness side, so it is not a duplicate. #13/#14 (open, not in intake) touch the same files (design doc §Harness/routing, build spec parts B, D, G, H, L) but ask for different changes. Those are sequencing overlaps, not duplicates. #19 in `issues/README.md` is this request ("not in intake yet"); this run is its intake as T-0012.
- I checked these quotes and facts on this checkout (`main` at `239ef5f`):
  - `README.md:11`: "Fill in `{braces}` per repo. The design doc is the source of truth; `prompts/` is regenerated from it." The request says line 13; it is actually line 11.
  - `docs/spec-factory.md:52`: "Where the block is kept, and how a harness serving more than one repo picks the right one, are not fixed here." The file is 759 lines (`wc -l`). The Changelog (from line 678) has 41 numbered items, and item 38 says "where the block is kept stays open".
  - `intake/README.md:1-6`: "# intake/ — SCRATCH … Delete the whole directory once the issues are filed and closed".
  - `intake/setup.sh` runs `git -C "$SRC" archive "$PIN" factory bin/factory`, then copies `instance/preamble.md`, `instance/context.md` and `instance/config.yaml` over the copy. `intake/HARNESS_PIN` is `7c0a0353d…` today. The body's `2986a2f` is superseded, as the operator's intake note says.
  - Five files reference the paths that would move (grep for `docs/spec-factory.md|specs/build-harness.md|plans/build-harness.md|plans/P0-intake-skeleton.md|issues/README`): `README.md`, `plans/build-harness.md`, `plans/P0-intake-skeleton.md`, `intake/README.md`, `intake/instance/context.md`. This matches the request's list.
- Reference harness (read only), `~/dev/nanobot-upstream` on `feat/lionbot-v3`, HEAD `7c0a0353d` ("Merge factory/T-0002.1 …"):
  - `.claude/agents/` holds six `factory-*.md` files (clerk, planner, spec-critic, spec-writer, stub, triage).
  - `factory/config.yaml:8` protects `infra: ["factory/workflows/**", "factory/config.yaml", …]`. `factory/prompts/**` is not listed, which matches the request's claim.
  - `factory/` has no `render.py`, so `factory render` is still unbuilt.
  - Grepping `tests/factory` for `knowledge_vault|nanobot/` returns nothing.
  - `grep -E "^\s*(async )?def test_"` over `tests/factory` counts 69 test functions. The operator says 70 tests (parametrization may explain the difference; I did not run pytest).
  - `factory/workflows/intake.js` lines 14 and 24-27 hold the `inlineRoles` fallback comment and flag the request cites.
  - The body's "green tip `f8f40e0c5`" is now an ancestor of HEAD.
- Requester's operator ruling: "highest priority once the first end-to-end pilot finishes". Operator note at intake: #16 and #18 are merged into green and closed; the latest pilot merge is `7c0a0353d`; #13 and #14 are still open.
- Side-by-side review linked by the requester: https://claude.ai/artifact/GbquRqWRR6y3ZR2pY1dXaK (operator-reviewed; I did not open it).

Assumptions (my inferences, labeled as such):
- ACCEPT, not NEEDS-HUMAN. The requester has already made the product and design calls: the design doc stays the prompt source and `render --check` stays; the harness is a pinned git checkout with an advisory lock and an explicit accept step; instance A's cutover is a separate ticket. The open choices are explicitly given to the planner: whether `intake/green-pilot/` becomes a second instance directory or is folded in, and which sub-ticket adds `uv run pytest tests` to this instance's gate.
- The operator's intake note amends part E: E moves everything except the live store, and the move of `intake/state/` → `.factory/state/` (plus removal of `intake/harness/`) becomes a scripted post-close step with its own check ("the store opens from `.factory/state/`, and `ticket show` on every ticket still works"). I read that recommendation as the requester's intent, because the harness cannot move the store it runs from in the middle of a ticket.
- The operator's facts replace the body's stale numbers. The history cut for part A goes at or after green `7c0a0353d`, and the moved test suite is about 70 tests, not 55.
- Part A extracts history with `git filter-repo`. I assume this must run on a fresh clone of green, never inside `~/dev/nanobot-upstream`, because filter-repo rewrites the repo it runs in and that path is read only for this instance (`reference harness` protected class). The request does not say this, but it follows from the protected-path rule.
- Green-specific files stay on green as instance A's overlay and are not moved here: `factory/config.yaml`, `factory/prompts/{context,preamble}.md`, `scripts/full_suite_gate.py` (operator note).
- Out of scope, as the requester listed: the simplifier role (#15), role-prompt wording, the routing table, the store schema, the OpenSpec tree. Role prompts move but their wording must not change.
- Suggested priority (a suggestion only; priority is a human call): p0, matching the request's label and the operator's ruling, now that its precondition (#16 and #18 closed) is met.

Question for human / Missing info / Reason: none blocking. For the Spec writer and Planner:
- Protected paths on instance B that this work touches: `intake/**` (`infra`, deleted or moved) and `prompts/**` (`generated`, moved and from then on written by `render`). The request's Risk section declares both, and the approved spec's Risk section must carry them forward.
- Sequencing against #13 and #14: either their doc edits land first, or part D carries them. The planner states which, per sub-ticket.

STATUS: ACCEPT
CONFIDENCE: medium. The intent, scope boundary and decisions are explicit, and the cited facts check out on both checkouts. But this is a large multi-part refactor whose body has stale numbers (corrected by the intake note), and I did not run green's test suite or open the linked review.
ESCALATIONS: none. This run wrote only its output file. The protected-path touches (`intake/**`, `prompts/**`) are declared in the request's Risk section and flagged above for the gate.
