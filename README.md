# Spec Factory

An AI software pipeline: eight agent roles, a harness that enforces the wiring rules, a routing table, and human gates.

- `docs/spec-factory.md` — the design document (roles, harness pieces, routing, gates, changelog).
- `prompts/` — each role's system prompt, extracted verbatim from the design doc. `00-preamble.md` goes at the top of every role.
- `specs/<ticket>.md` — a spec: the Spec writer's output for one ticket, approved at the human gate. `build-harness.md` is the spec for building the harness itself, produced by running the pipeline on the design doc (bootstrap run).
- `plans/<ticket>.md` — the Planner's decomposition of the spec of the same name into ordered sub-tickets. One plan per spec; same filename, one stage later.
- `plans/P0-intake-skeleton.md` — the first walking skeleton: a cut through the build-harness plan that runs the intake half (Triage → Spec writer ⇄ Critic → gate → Planner) on real faux-specs before any enforcement is built.

Fill in `{braces}` per repo. The design doc is the source of truth; `prompts/` is regenerated from it.
