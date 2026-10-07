### ST-3 / Each role's input cut to the spec sections it uses, and a round-2 critic diff
Depends on: none
Parallel-safe: yes

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part C, items C1 to C4, all in `factory/compose.py`.
- C1: a helper that removes the `## Evidence` and `## Responses` sections. Lines inside a fenced code block do not end a section.
- C2: the helper is used for the planner's "Approved spec" (`factory/compose.py:199` on `main`), the implementer's and checkers' "Parent spec" (lines 238 and 256), and the parent-close verifier's spec (line 253). Each heading keeps its current words, including "verify every scenario on main". Each heading adds that Evidence and Responses are left out, and gives the full spec's absolute path. `input_sources` stays unchanged, and `subticket.md` is not cut.
- C3: a round-2 critic gets a `difflib.unified_diff` with 3 lines of context, in place of the previous version (line 192), when the diff is smaller in bytes. Otherwise it gets the version whole. The heading names which one the input holds.
- C4: every other input stays unchanged.

Line numbers are from `main` at `d226a4d`. The spec's Root cause cites lines on `c2750bf`, which have since moved.

Acceptance:
- NEW. "Downstream roles get every spec section but Evidence and Responses, and the full spec's path".
  WHEN the parent's command as written (`. ${TMPDIR:-/tmp}/t0030-spec.sh`, then `marks` on composed planner, implementer, reviewer, verifier and parent-close inputs).
  THEN it prints exactly `planner: evidence=0 responses=0 kept=9 full=1`, `implementer: evidence=0 responses=0 kept=9 full=1`, `reviewer: evidence=0 responses=0 kept=9 full=1`, `verifier: evidence=0 responses=0 kept=9 full=1`, `parent-close: evidence=0 responses=0 kept=9 full=1`, one per line.
- NEW. "A round-2 critic receives a small revision as a diff".
  WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh small) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) added=$(grep -cx -- '+NEW-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
  THEN it prints exactly `removed=1 added=1 keep100=1 prior_findings=1`.
- REGRESSION. "A round-2 critic receives a rewritten spec's previous version whole".
  WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh rewrite) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) other100=$(grep -cx 'other line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
  THEN it prints exactly `removed=0 keep100=1 other100=1 prior_findings=1`. This passes on `main` today.
- REGRESSION. The gate suite passes, including `tests/factory/test_p0_cli.py` and `tests/factory/test_shepherd.py`, which check round-2 critic inputs and `input_sources`.

Interim tests: none
Tests to change: none
Protected paths:
- harness: `factory/compose.py`.

Out of scope:
- The triage and spec writer inputs, and the critic's current spec.
- What spec writers put in Evidence (issue #23).
- Agent definitions, effort and documents (ST-1, ST-2, ST-4).
- `factory/cost.py`.

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
