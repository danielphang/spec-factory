## T-0019-S2 / Plan field lines: read bulleted lines, require a Depends on line, show the parsed lines in the planner prompt
Depends on: none
Parallel-safe: no (S1 also edits docs/design.md and docs/changelog.md)

Parent: T-0019 approved spec v2 (issue #36). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts C (C1 to C3), D, E1's S2 clause only, F2. Part E4 says `dev/build-harness.spec.md` does not change, so leave it alone.

Acceptance (each WHEN verbatim from the parent; run the fixture GIVEN block first, because these scenarios source `t0019-parent.sh`):
- Dash-bulleted field lines keep their dependencies. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\n- Depends on: none\n- Parallel-safe: no (alone)\n\n## ST-2 / Second\n- Depends on: ST-1\n- Parallel-safe: yes\n\n## ST-3 / Third\n- **Depends on:** ST-2\n- **Parallel-safe:** yes\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md | tail -1)`
  THEN the printed JSON's `subtickets` list is exactly `{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": false}`, `{"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}`, `{"id": "T-0001.3", "label": "ST-3", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": true}`
- Star-bulleted, bold, indented and plain field lines read as before. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\n* Depends on: none\n* Parallel-safe: yes\n\n## ST-2 / Second\n**Depends on:** ST-1\n**Parallel-safe:** yes\n\nT-0001-C / Third\n  Depends on: ST-2\n  Parallel-safe: no (same file)\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md | tail -1)`
  THEN the printed JSON's `subtickets` list is exactly `{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": true}`, `{"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}`, `{"id": "T-0001.3", "label": "T-0001-C", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": false}`
- A sub-ticket with no Depends on line is refused. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0019-parent.sh && printf '## ST-1 / First\nDepends on: none\nParallel-safe: yes\n\n## ST-2 / Second\nParallel-safe: yes\nScope: B\n' > $T19/plan.md && bin/factory subticket add T-0001 --file $T19/plan.md; echo "exit=$?"; ls $FACTORY_STATE/tickets)`
  THEN stderr contains `ST-2` and `Depends on:`, it prints `exit=2`, and the listing is `T-0001.yaml` alone
- The planner prompt shows the parsed lines in every copy. NEW.
  WHEN `for f in docs/design.md docs/prompts/04-planner.md factory/prompts/planner.md; do echo "$f $(grep -cxF 'ID / Title' $f) $(grep -cxF 'Depends on: none | IDs' $f) $(grep -cxF 'Parallel-safe: yes | no (reason)' $f) $(grep -cF 'A sub-ticket with no "Depends on:" line is refused.' $f) $(grep -cF 'Parallel-safe "yes" means safe alongside every sibling' $f)"; done`
  THEN it prints `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1` and `factory/prompts/planner.md 1 1 1 1 1`
- The planner block and its copies stay identical. REGRESSION.
  WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## 4\. Planner/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/04-planner.md && diff docs/prompts/04-planner.md factory/prompts/planner.md && echo SAME`
  THEN it prints `SAME`
- The changelog records the change in order. NEW.
  WHEN `grep -cE '^[0-9]+\. After issue #36 \(2026-10-04\)' docs/changelog.md; awk '/^[0-9]+\. /{n++; if ($1+0 != n) bad=1} END{print (bad?"GAP":"CONTIGUOUS")}' docs/changelog.md`
  THEN it prints `1` then `CONTIGUOUS`, and the entry carries the S2 clause from parent E1
- The change adds no whitespace errors. REGRESSION.
  WHEN `git diff --check main...HEAD; echo "exit=$?"`
  THEN it prints only `exit=0`
- This repo's gate suite passes under a throwaway HOME. REGRESSION.
  WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
  THEN it exits 0 with no failures, including the new `tests/factory/test_plan_fields.py`
- Intermediate check: only declared files change, and no existing test changes. NEW.
  WHEN `git diff --name-only main...HEAD | sort`
  THEN it prints exactly these files: `docs/changelog.md`, `docs/design.md`, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`, `factory/subtickets.py`, `tests/factory/test_plan_fields.py`

Tests to change: none. The new file is `tests/factory/test_plan_fields.py`.
Protected paths: harness `factory/subtickets.py`, `factory/prompts/planner.md`; generated `docs/prompts/04-planner.md`. The planner prompt is an agent prompt, and part D asks for that edit.
Out of scope:
- Parts A, B, E2, E3 and F1, and E1's S1 clause: they belong to T-0019-S1.
- `README.md`: the parent gives this seam no README part.
- Reading pairwise parallel-safety (`yes with A, not with B`); field lines in a numbered list or with a `+ ` bullet; `HEAD_RE`, which does not change.
- `agents/factory-planner.md`, `.factory/**`, `bin/factory`, the `harness-bug:` label in `factory/workflows/build.js`, `dev/build-harness.spec.md`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v2 of T-0019 (issue #36), in this run's input and the T-0019 spec store.

The parent marks itself NEEDS-SPLIT and names two seams (design.md, "Size and seams"). This plan keeps those two seams as they are: S1 for the throwaway-HOME wrapper, S2 for the plan field lines. The faults share no code, so neither sub-ticket depends on the other. A defect in one does not hold the other back, which is what the parent asks for. Both edit `docs/design.md` and `docs/changelog.md`, so neither is parallel-safe and the harness builds them one at a time. S1 is listed first, but nothing makes it merge first.

Shared notes for both sub-tickets:
- Fixtures. Most scenarios below need the four fixture scripts written by the GIVEN block of the first scenario in the parent's `specs/role-run-isolation/spec.md` ("A triage input's wrapper runs a command under a fresh HOME"). Run that block once, verbatim, at column 0, before running any scenario. S2 needs it too: its plan-parsing scenarios source `t0019-parent.sh`. Run every command from the root of your worktree, after `uv sync --frozen`.
- Changelog (parent E1). One entry for both sub-tickets, numbered after the last entry (47 on `main` at `1c5f6a7`), opening `<n>. After issue #36 (2026-10-04):`, placed after the last numbered entry and before `Declined:`. When you start, check `docs/changelog.md` on `main`. If no `After issue #36` entry is there, add it with your own clause only. If the other sub-ticket has already merged it, add your clause to that same entry and do not add a number.
- Running tests. Run the suite and any probe the way this change will require: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Never run tests with the real `HOME`.
