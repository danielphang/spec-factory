### ST-4 / Documents: design doc, build spec, changelog, README and the instance page
Depends on: ST-1, ST-2, ST-3
Parallel-safe: yes

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part D, items D1 to D5.
- D1: the "Receives" column of the routing table in `docs/design.md`, in five rows. The round-2 critic row says the previous version arrives as a diff when that is smaller. Four rows say the spec arrives without Evidence and Responses.
- D2: the critic's round-2 input in `dev/build-harness.spec.md`, in the sentence that contains "round ≥ 2: prior findings".
- D3: one entry in `docs/changelog.md`, numbered next with no gap. The last entry on `main` today is 57; re-derive the number at build time. The entry names the seven definitions with `factory-implementer` among them, the fence and its limit, the `agent call failed` park, `inlineRoles` as the fallback, the `effort` map, and the trimmed inputs with the round-2 diff.
- D4: `README.md`, following its "Maintaining this page" section:
  - "Starting a run": roles run as their registered agents, inline mode is the fallback, what happens when the definitions are missing, and how to recover.
  - The checker fence and its limit, including the `python3` and workspace-trust requirements.
  - The `effort:` map, and removal of the "Per-role effort settings" bullet.
  - `run start --inline`.
  - Re-derived figures, this ticket and issues #24 and #22 under "Related work and history", and a new status date.
- D5: `.factory/README.md` "Running": dispatch without `inlineRoles`, and drop "this repo adds no `.claude/agents/`".

Acceptance:
- NEW. "The changelog records registered agents, trimmed inputs and effort as its last entry".
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e factory-implementer -e Evidence -e effort -e diff -e inlineRoles | sort -u | grep -c .)`
  THEN it prints `CONTIGUOUS`, then `5`.
- NEW. "The routing table and build spec describe the trimmed spec and the diff, and no prompt changes".
  WHEN the parent's command as written (`critic_diff`, `trimmed_rows`, `build_spec`, `prompts` from `git diff --name-only main...HEAD -- docs/prompts factory/prompts`).
  THEN it prints exactly `critic_diff=1 trimmed_rows=4 build_spec=1 prompts=0`.
- NEW. "README and the instance page describe registered roles, the park and effort".
  WHEN the parent's command as written.
  THEN it prints exactly `inline_everywhere=0 parks=1 effort_map=1 effort_not_built=0 instance_inline=0`.
- REGRESSION. "The role-agents change adds no whitespace errors".
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`.
- REGRESSION. Every scenario of ST-1, ST-2 and ST-3 still prints its THEN, and the gate suite passes. This sub-ticket changes no code, so these are a check that the documents' branch carries the merged code unchanged.

Interim tests: none
Tests to change: none
Protected paths:
- infra: `.factory/README.md`.

Out of scope:
- Every code, agent definition and test file.
- `docs/prompts/**` and `factory/prompts/**`, which must not change.
- The operator steps in the parent: installing the definitions, the fence probe, dropping `inlineRoles`, and measurement. These are for the operator after merge, not for this sub-ticket.

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
