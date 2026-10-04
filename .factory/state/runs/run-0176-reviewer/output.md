Commit: 381f4c63f8877458600f60f5c92ca06ef274b128 (branch `factory/T-0019.2`, base `9853737e24b2acdc001546b399d2a5a8c3dd6d85`)

## What I checked, in the role's order

1. Test integrity. `git diff --name-only main...HEAD` prints exactly the six declared files; the only test file is the new `tests/factory/test_plan_fields.py`. No existing test changed, no assertion weakened, no skip or xfail added. The new file asserts exact tuples of `(label, state, depends_on, parallel_safe)` and an exact `tickets/` listing, so nothing is hard-coded to current output.
2. Correctness. I ran every acceptance WHEN of the sub-ticket from the worktree under `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)` after the fixture GIVEN block:
   - Dash-bulleted field lines: printed the exact expected three-element list (`ST-2` waits on `T-0001.1`, `ST-3` on `T-0001.2`, both `parallel_safe: true`, `ST-1` `false`).
   - Star-bulleted, bold, indented and plain lines: the exact expected list, `T-0001-C` labelled and `parallel_safe: false`.
   - Missing `Depends on:`: stderr `ST-2: no "Depends on:" line; write "Depends on: none" when it depends on nothing`, then `exit=2`, listing `T-0001.yaml` alone. `factory/cli.py:394-397` turns the `ValueError` into `Refused` before any sub-ticket is written, as the spec says.
   - Planner prompt: `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1`, `factory/prompts/planner.md 1 1 1 1 1`.
   - Block and copies identical: `SAME`.
   - Changelog: `1`, `CONTIGUOUS`, and `grep -cF "A plan's bulleted field lines lost every sub-ticket's dependencies" docs/changelog.md` prints `1`: entry 48 now carries the S2 clause, with no new number.
   - `git diff --check main...HEAD; echo "exit=$?"` printed only `exit=0`.
   - Gate suite under a throwaway HOME: `190 passed in 102.04s`, no failures.
   Edge probes beyond the spec: `* **Depends on:** none` (star bullet plus bold, which the old `\**` consumed wrongly) now reads; `- Depends on: .1` resolves to `T-0001.1`; a pairwise `Parallel-safe: yes with ST-2, not with ST-3` reads as `true`, which the spec keeps out of scope and the PR's Known gaps names. The regex at `factory/subtickets.py:21` is byte-for-byte the spec's C1 pattern, and `HEAD_RE` is unchanged.
3. Scope. Only parts C1 to C3, D, E1's S2 clause and F2. `dev/build-harness.spec.md` and `README.md` untouched, as the sub-ticket asks.
4. Silent behavior changes. One, and the spec asks for it: a plan whose sub-ticket lacks a `Depends on:` line, accepted before, is now refused. The 22 `Depends on` lines in the existing suite's plans cover every sub-ticket there (the suite passing confirms it). A second the PR already declares in Known gaps: a bulleted `Depends on:` or `Parallel-safe:` line inside a sub-ticket's Acceptance list is now read as the field. My probe with `- Depends on: nothing here` under `Acceptance:` confirmed it overrides the real line (here harmlessly, since `nothing` matches `NONE_RE`). Out of the spec's scope, and declared.
5. Security and data safety. No new I/O, no shell, no secrets. The new tests write only under `tmp_path`.
6. Protected paths. Declared by the sub-ticket: harness `factory/subtickets.py`, `factory/prompts/planner.md`; generated `docs/prompts/04-planner.md`. Listed under ESCALATIONS; the merge gate needs a human approval.
7. Coding standard: one `reuse:` finding below.
8. PR description: readable; one gloss gap below.

## Findings

- [BLOCKING] reuse: tests/factory/test_plan_fields.py:21-48: the `store` fixture re-implements three helpers the suite already has: `run` and `js` from `tests/factory/test_subtickets.py:70-77` (the same `subprocess.run` with `FACTORY_STATE` and `PYTHONDONTWRITEBYTECODE`, the same "last stdout line is JSON" decode) and the six-command approve sequence `approved_parent` from `tests/factory/test_build_startup.py:14-26`, whose body is line for line what lines 34-39 do → when the approve path changes (a new transition, a different `spec add` form), the one fixture in `test_build_startup.py` is updated and this copy breaks or, worse, keeps passing against a stale path. The repo already imports helpers across test modules (`test_build_startup.py:11`, `test_killed_checker.py:13`, `test_parent_close_reuse.py:13`). Replace with `from .test_subtickets import js, run` and `from .test_build_startup import approved_parent`, keeping only the `add(plan)` closure and its `root` attribute. net: -20 lines possible.
- [NIT] PR description: What changed: the first paragraph uses "planner" and "sub-ticket" without a gloss (writing rule 2). The sub-ticket section glosses neither, and a gate reader new to the factory meets both terms here first. One clause each ("the planner, the role that splits an approved spec into sub-tickets, units of work that each become one branch").

Prior findings: none (round 1).

## Notes for the gate

- The `BLOCKING` above is a test-code duplication finding under the coding standard's rule 4 table, not a correctness defect. The change does what the spec intends, every acceptance scenario passes on `381f4c6`, and the gate suite passes. If the operator prefers to waive the standard for test helpers, the code earns APPROVE on correctness.
- Disclosure: while listing callers I ran `git stash -q` in the review worktree by reflex. The worktree had no uncommitted changes, `git stash list` is empty and `git status --short` prints nothing afterward, so it changed nothing; I report it because a reviewer should not have issued it.

Out-of-scope observations:
- `agents/factory-planner.md` still shows the indented OUTPUT block; the spec and the PR already note it, and `agents/**` is protected.
- `factory/workflows/build.js` still parks a refused `subticket add` under `harness-bug:`, though after this change the refusal usually means a malformed plan. Already noted by the spec.

STATUS: REQUEST-CHANGES
CONFIDENCE: high. Every acceptance WHEN and both gates were re-run on 381f4c6 with the expected output; the one BLOCKING finding is a verified duplication of three existing helpers, each cited by file and line.
ESCALATIONS: protected paths touched, all declared by the sub-ticket: harness `factory/subtickets.py` and `factory/prompts/planner.md`; generated `docs/prompts/04-planner.md`. The merge gate needs a human approval for them.
