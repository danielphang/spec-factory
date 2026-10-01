# P0: intake walking skeleton

Parent: `specs/build-harness.md` (v4). This is not a sub-ticket of `plans/build-harness.md`; it is a cut through it. It builds BH-1-lite, BH-4, and BH-5 and defers BH-2a, BH-2b, BH-3, BH-6, BH-7. Nothing built here is thrown away: the agent definitions, the `factory` CLI, and `intake.js` are the same files the full plan grows.

## Why first

Plan v2 builds the enforcement layer (bare repo, hook, identities, merge gate) before a faux-spec ever flows through a role. The first end-to-end flow is BH-5, four infrastructure sub-tickets in. The question that stalled the Nanobot port was spec quality, not enforcement. P0 answers that question before paying for enforcement, and it exercises the three things the spec marks not-verified on a Mac that don't need a bare repo: Workflow under `claude -p`, model alias strings in `agent()`, and the clerk-via-CLI pattern.

The design doc names v0 as "exercising the routing table, not producing trusted merges." P0 is v0 as designed.

## What it is

One workflow script driving the intake half of the routing table on real input:

```
knowledge_vault/specs/<file>.md
  → Triage (ACCEPT | NEEDS-HUMAN | CLARIFY | REJECT)
  → Spec writer ⇄ Spec critic, max {2} rounds
  → human gate (you read the spec in knowledge_vault/sanitized_specs/)
  → Planner
```

Parts, by the spec's lettering:

| Part | What | From plan v2 |
|---|---|---|
| A | `.claude/agents/factory-*.md` for Triage, Spec writer, Spec critic, Planner, clerk, stub; preamble file; `config.yaml` with `models:` from the doc's table | BH-4 (subset) |
| B-lite | `factory` CLI with four verbs: `ticket new`, `transition` (with the round guard and routing-edge guard), `record`, `run start/finish` writing `runs/<id>/meta.yaml` with `model` | BH-1 (subset) |
| H-intake | `factory/workflows/intake.js`: Triage → writer ⇄ critic join → gate → planner; clerk agent for every store write; `parallel()` unused here | BH-5 |
| K-lite | `factory approve-spec ID` and `factory resolve ID --answer FILE`, run as you | BH-3 (two verbs) |

Store: `tickets/*.yaml` in the working tree of the green checkout, committed by you. No `tickets` branch, no hook, no identities.

## What it skips, on purpose

Bare repo, pre-receive hook, per-role keys, merge gate, gate-run, implementer, reviewer, verifier, retro, parent-close run. Every skipped piece is enforcement or the PR loop. None is needed to learn whether intake produces specs you would build from.

## Acceptance (run as written, on the green checkout)

Black-box, numbered P0-1.. so they don't collide with the spec's 1–84. Each is NEW; today every one fails with `factory: command not found` or "no such workflow."

- P0-1 `factory ticket new --file knowledge_vault/specs/<any>.md` → `tickets/T-0001.yaml` exists with `status: ready-for-triage`, `round: {spec: 0}`.
- P0-2 `/factory run intake T-0001` with the `factory-stub` agents configured to emit `STATUS: ACCEPT` then `STATUS: READY-FOR-CRITIC` then `STATUS: APPROVE` → ticket ends `awaiting-spec-gate`; `runs/` holds three `meta.yaml` files, each with `role`, `model`, `started`, `finished`.
- P0-3 Same, stubs emit `REVISE` twice → ticket ends `parked` with reason `max rounds`, `round.spec: 2`, and no `transition` call set the counter by hand (grep the run log).
- P0-4 Stub emits `CLARIFY` → ticket `waiting-requester`; `factory resolve T-0001 --answer a.md` → `ready-for-triage`; `runs/` shows the answer in Triage's next `input.md`.
- P0-5 Real models, one real faux-spec: ticket reaches `awaiting-spec-gate`; `knowledge_vault/sanitized_specs/T-0001.md` exists in the spec FORMAT; `grep -cE 'test_[a-z_]+\(|def |::' knowledge_vault/sanitized_specs/T-0001.md` → 0.
- P0-6 `factory approve-spec T-0001` as you → `ready-for-planner`; `/factory run intake T-0001` continues → `plans/T-0001.md` exists with a coverage map whose item count equals the spec's Acceptance count.
- P0-7 Round-2 input: after a real REVISE, `runs/<critic round 2>/input.md` contains the round-1 findings text and the writer's Responses section.
- P0-8 `transition T-0001 --to ready-for-implementer` from `ready-for-triage` → exit 2, "not a routing edge."

## What you measure (three real faux-specs)

| Metric | Baseline from the port | P0 target |
|---|---|---|
| Rounds to critic APPROVE | n/a | ≤ 2 (the cutoff) |
| Code identifiers in acceptance | "doubled", ten relint commits | 0 (P0-5) |
| Your interventions per spec | "most interrupts were which-function questions" | count them; each one is a retro incident |
| Cost per spec | n/a | record; per-(role, model) from `meta.yaml` |
| Would you approve it at the gate unedited? | n/a | yes for ≥ 2 of 3 |

If ≥ 2 of 3 specs pass the gate unedited, the next walking step is BH-6 (the PR loop) on one of them, still without the hook. If not, the retro runs on the three transcripts before any more harness is built, and the fix is in the prompts, not the plan.

## Risk

- Protected paths touched: none (no infra, no keys, no dependencies beyond pyyaml).
- Workflow under `claude -p` unverified; fallback is an interactive session (same script).
- `agent()` model alias strings unverified; P0-2's `meta.yaml` check is where you find out.
- The working-tree store has no identity on writes. Fine for P0; it is why P0 cannot be used for merges.

## Tests to change: none.

## Out of scope

Everything in "What it skips." Also: the `/factory intake <dir>` bulk form (one ticket at a time is enough to measure), the audit sample, and any change to the frozen `SPEC_MAINTENANCE_WORKFLOW.md`.

STATUS: PLANNED
CONFIDENCE: medium (the unverified items above are exactly what P0 exists to verify)
ESCALATIONS: Nanobot gate commands still unknown (not needed until BH-6); which three faux-specs to use is your call.
