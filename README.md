# Spec Factory

An AI software pipeline: eight agent roles, a harness that enforces the wiring rules, a routing table, and human gates.

- `docs/spec-factory.md` — the design document (roles, harness pieces, routing, gates, changelog).
- `prompts/` — each role's system prompt, extracted verbatim from the design doc. `00-preamble.md` goes at the top of every role.
- `specs/build-harness.md` — the spec for building the harness itself, produced by running the pipeline's Spec writer and Spec critic on the design doc (bootstrap run).

Fill in `{braces}` per repo. The design doc is the source of truth; `prompts/` is regenerated from it.
