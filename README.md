# Spec Factory

An AI software pipeline: eight agent roles, a harness that enforces the wiring rules, a routing table, and human gates.

- `docs/design.md` — the design document (roles, harness pieces, routing, gates). Its changelog is `docs/changelog.md`.
- `docs/prompts/` — each role's system prompt, extracted verbatim from the design doc. `00-preamble.md` goes at the top of every role.
- `dev/build-harness.spec.md` — the spec for building the harness itself, produced by running the pipeline on the design doc (bootstrap run).
- `dev/build-harness.plan.md` — the Planner's decomposition of that spec into ordered sub-tickets.
- `dev/P0-intake-skeleton.md` — the first walking skeleton: a cut through the build-harness plan that runs the intake half (Triage → Spec writer ⇄ Critic → gate → Planner) on real faux-specs before any enforcement is built.
- `dev/issues.md` — the index of this repo's GitHub issues and where each one stands.

Fill in `{braces}` per repo. The design doc is the source of truth; `docs/prompts/` is regenerated from it.
