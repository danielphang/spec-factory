Commit: 381f4c63f8877458600f60f5c92ca06ef274b128 (branch `factory/T-0019.2`; base and `main` are both 9853737e24b2acdc001546b399d2a5a8c3dd6d85, which already holds S1)

How I ran it. Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0175-verifier/wt`, with a clean `git status` before and after. Steps:
- I ran the parent's fixture GIVEN block once, verbatim. It wrote `$TMPDIR/t0019-{parent,triage,impl,probe}.sh`.
- Then `uv sync --frozen` (Python 3.12.13).
- For base, I extracted `git archive 9853737` into a scratch directory and ran `uv sync --frozen` there. The base checks that need git (A7 and A9) ran in the PR worktree against `main...9853737`.
- Every WHEN ran verbatim under bash.

Per criterion:
- NEW | A1, "Dash-bulleted field lines keep their dependencies" | base: all three sub-tickets `"state": "ready-for-implementer", "depends_on": [], "parallel_safe": false` | PR: `[{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": false}, {"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}, {"id": "T-0001.3", "label": "ST-3", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": true}]`. This is exactly the expected list. | PASS
- REGRESSION | A2, "Star-bulleted, bold, indented and plain field lines read as before" | base: not run | PR: the exact expected list. `T-0001.1` is `[]`/true/ready, `T-0001.2` is `["T-0001.1"]`/true/waiting, and `T-0001.3` (label `T-0001-C`) is `["T-0001.2"]`/false/waiting. | PASS
- NEW | A3, "A sub-ticket with no Depends on line is refused" | base: the success JSON (`T-0001.2` with `"depends_on": []`), then `exit=0`, then `T-0001.1.yaml T-0001.2.yaml T-0001.yaml` | PR: stderr is `ST-2: no "Depends on:" line; write "Depends on: none" when it depends on nothing`, then `exit=2`, then `T-0001.yaml` alone. | PASS. One correction to the PR description: it says both refusal lines go to stderr. They do not. With the streams split (`>o 2>e`), the `{"ok": false, "error": ...}` JSON goes to stdout and only the plain message goes to stderr. The criterion only needs stderr to contain `ST-2` and `Depends on:`, which it does.
- NEW | A4, "The planner prompt shows the parsed lines in every copy" | base: `0 0 0 0 0` for each of the three files | PR: `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1`, `factory/prompts/planner.md 1 1 1 1 1` | PASS
- REGRESSION | A5, "The planner block and its copies stay identical" | base: not run | PR: `SAME` | PASS
- NEW | A6, "The changelog records the change in order" | base: `1` then `CONTIGUOUS`; the S2 clause is absent (`grep -cF "A plan's bulleted field lines lost every sub-ticket's dependencies" docs/changelog.md` prints `0`) | PR: `1` then `CONTIGUOUS`; the same grep prints `1`, and entry 48 carries the S2 clause in the parent E1 wording as its second sentence, with no new number. | PASS. On its own, the command's printed output already passes on base, because S1 merged entry 48 first. The plan foresaw this. The THEN's added condition, that the entry carries the S2 clause, fails on base and passes on the PR. So the criterion as written fails on base for the stated reason, and I do not class it as a SPEC-DEFECT. That added condition was checked by grep and by reading the diff, not by the command.
- REGRESSION | A7, "The change adds no whitespace errors" (`git diff --check main...HEAD; echo "exit=$?"`) | base: not run | PR: `exit=0` only | PASS
- REGRESSION | A8, "This repo's gate suite passes under a throwaway HOME" | base: not run | PR: `190 passed in 102.61s (0:01:42)`, exit 0. `tests/factory/test_plan_fields.py` alone gives `8 passed in 2.97s`. | PASS
- NEW | A9, "Intermediate check: only declared files change" | base: `git diff --name-only main...9853737` prints nothing | PR: exactly `docs/changelog.md`, `docs/design.md`, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`, `factory/subtickets.py`, `tests/factory/test_plan_fields.py`. No existing test changed, and `agents/`, `bin/`, `README.md` and `dev/build-harness.spec.md` are untouched. | PASS

Gate suite: PASS
- `git diff --check main...HEAD` ran exactly as written inside A7: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ran exactly as written: `190 passed in 102.17s (0:01:42)`, exit 0.
- The wrapped form (A8) also passed: 190 passed.
- Before the bare run, I grepped `tests/factory` and `factory` for `expanduser`, `Path.home`, `HOME` and `~/`. Nothing in the suite writes under the real home.

Probes (each through `bin/factory subticket add` on a fresh fixture store, PR head):
- `* **Depends on:** none` (star bullet plus bold), `  - Depends on: ST-1` (indented dash), and `-<TAB>Depends on: ST-1, ST-2` (tab after the dash, two dependencies) → all read: `[]`/true, `["T-0001.1"]`/true and `["T-0001.1","T-0001.2"]`/false, with exit 0. The pattern is general, not tied to the tested spellings. → OK
- Forms outside the accepted grammar: lowercase `- depends on:`, `-Depends on:` (no space after the bullet), `1. Depends on:` and `+ Depends on:` → each is refused, exit 2, naming `ST-1`, and only `T-0001.yaml` is written. These used to be silently accepted with no dependencies; now they fail loudly. → OK
- A first sub-ticket missing its line (`## ST-1` has only `- Parallel-safe: yes`) → refused naming `ST-1`, exit 2, nothing written. → OK
- A dependency on a later sibling (`ST-1` depends on `ST-2`) → `T-0001.1` is waiting on `["T-0001.2"]`. An unknown id (`ST-9`) gives the existing "cannot resolve" refusal, exit 2. An empty plan gives the existing "no sub-tickets found" refusal, exit 2. → OK
- Regression on real plans: I ran `factory.subtickets.parse` on all 8 plans in this repo's store (`.factory/state/plans/T-0012.md` to `T-0019.md`, read only) on the PR and on base. The output was identical, and none is newly refused. `T-0014` returns `[]` on both: that is the plan that was hand-normalised earlier, and `subticket add` still rejects it with its existing "no sub-tickets found" refusal, which is not this change. → OK

Out-of-scope observations:
- `agents/factory-planner.md` still holds the older, indented planner OUTPUT block. The spec already notes this, and it is a protected path.
- A bulleted `Depends on:` or `Parallel-safe:` line nested inside a sub-ticket's Acceptance list would now be read as the field, and a later line overrides an earlier one. The PR names this as a known gap. No plan in this store does it.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command verbatim on the head and every NEW command on base; both gates passed exactly as written; and the probes show the parser change is general and fails loudly on the forms it does not accept.
ESCALATIONS: none
