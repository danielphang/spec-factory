### ST-2 / Effort per role: the instance's `effort:` map reaches the agent call and the run record
Depends on: ST-1
Parallel-safe: no (it edits the same `run_start` in `factory/cli.py` and the same `runRole` in both workflow scripts as ST-1, so it runs after it)

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B, items B1 to B4.
- B1: `run_start` validates `cfg.get("effort")`. It refuses with exit 2 before reserving a run id, and the refusal names the bad entry.
- B2: `effort` is written to `meta.yaml` and to the JSON output.
- B3: the real role call in `runRole` in both workflow scripts passes `effort: start.effort` only when that is set. The store-command agent (the clerk) and the stub calls keep `'low'`.
- B4: a commented example in `factory/instance.template.yaml`. No live key is added.

Acceptance:
- NEW. "The intake workflow gives triage the effort the instance sets and records it".
  WHEN the parent's command as written (a scratch instance per case, `effort: {triage: high}` with inline mode, then no map with registered mode, then `t0030-e2e.mjs`, then a read of `meta.yaml`).
  THEN it prints exactly `role effort=high clerk effort=low meta_effort=high inline=true`, then `role effort=none clerk effort=low meta_effort=null inline=false`.
- NEW. "The build workflow passes the run's effort to each build role's agent call".
  WHEN `(node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/build.js "$(sed 's/"run finish"/"run start": {"out": {"ok": true, "run_id": "run-0009-x", "worktree": "\/w", "effort": "max"}}, "run finish"/' ${TMPDIR:-/tmp}/t0030-build.json)")`
  THEN it prints exactly `factory-planner effort=max`, `factory-implementer effort=max`, `factory-reviewer effort=max`, `factory-verifier effort=max`, `clerk effort=low`, one per line.
- NEW. "An effort map with an unknown level or role is refused".
  WHEN the parent's command as written (`triage: extreme`, then `triag: high`, each in a copy of `tests/factory/fixtures/instance`).
  THEN it prints exactly `exit=2 named=1 runs=0`, twice, one per line.
- REGRESSION, because ST-1 made each of these true:
  - "Every agent type the workflows ask for has a definition": the seven `=defined` lines.
  - "A build run before the build-role agents register parks the sub-ticket": the two lines given in ST-1.
  - "A workflow in a session with no factory agents stops at its first store command": the `stopped: ...` line twice.
- REGRESSION. The gate suite passes.

Interim tests: none
Tests to change: none
Protected paths:
- harness: `factory/cli.py`, `factory/instance.template.yaml`, `factory/workflows/intake.js`, `factory/workflows/build.js`.

Out of scope:
- Agent definitions and the fence (ST-1).
- `factory/compose.py` (ST-3).
- Documents, including README's "Per-role effort settings" bullet (ST-4).
- The clerk's model and its fixed `'low'` effort.
- An `effort` key in any agent definition.
- Any live `effort:` key in a shipped `instance.yaml`.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v2) names four parts, A to D, and says D lands last. I keep those seams. One change from the spec's "A, B and C are independent": A and B both edit `run_start` in `factory/cli.py` and `runRole` in both workflow scripts (`factory/workflows/intake.js`, `factory/workflows/build.js`). Run in parallel, they would collide, so B waits for A. C edits only `factory/compose.py` and runs alongside them.

Grounding (checked on `main` at `d226a4d`, with the spec's GIVEN block written to this run's scratch directory and every command run under a throwaway HOME):
- `ls agents/` gives six files, with no implementer, reviewer or verifier.
- The four REGRESSION scenarios already print what they expect on `main`: the build park (`run finish run-0009-x --status-override KILLED`, then the `agent call failed: implementer` park), `stopped: agent type 'factory-clerk' not found after 1 agent call(s)` twice, and the rewritten-spec critic (`removed=0 keep100=1 other100=1 prior_findings=1`).
- Three NEW scenarios print the "today" lines in `verification.md`: the agent-type scenario (`factory-implementer=missing`, and the same for reviewer and verifier), the small-diff critic (`removed=0 added=0 keep100=2 prior_findings=1`), and the intake effort scenario (`... meta_effort=absent inline=absent`, twice).
- The only existing test the spec changes is `tests/factory/test_instance.py:89` (`assert len(agents) == 6`). Two existing round-2 critic tests check the input text: `tests/factory/test_p0_cli.py:170` asserts `"v1 body" in cinp`, and `tests/factory/test_shepherd.py:123-124` asserts the sources and `## Responses`. Neither should break under C. In the first test, v1 is 22 bytes, so the diff is larger and v1 stays whole. In both, the sources stay unchanged and `## Responses` comes from the current version.

All commands below run from `~/dev/spec-factory`, inside the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Every scenario that names a `t0030-*` file needs the spec's GIVEN block (scenario "Every agent type the workflows ask for has a definition") run once first. "Gate suite" means the instance's two gate commands, `git diff --check main...HEAD` and `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, the second after `uv sync --frozen`.

---
