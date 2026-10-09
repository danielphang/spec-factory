Commit: 9aa97bf43d815b288ca4dd1cf89cbde4dac55103

Setup: I ran the PR head in the given worktree (`wt`). I ran the base `f4ea041` (`main`) in a fresh clone at `scratch/base`, with a detached checkout and its `main` branch pointed at that SHA. Each tree got its own `uv sync --frozen`. I wrote the fixtures `t0022-sib.sh`, `t0022-build.mjs`, `t0023-parent.sh`, `t0023-closed.sh`, `t0023-wf.mjs` and `t0038-respec.sh` from the GIVEN blocks in specs T-0022 v1, T-0023 v2 and T-0038 v2, under `TMPDIR=scratch/tmp`. Each WHEN was copied byte for byte from the pinned spec. The copy in `input.md` is identical (checked with diff). Each ran under bash from the tree's root, inside the HOME wrapper.

Per criterion:
- NEW | After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept | base: `add: ` / `ready: "ready": ["T-0001.4"]` / `closed: "closed": ["T-0001.2"]` / `superseded: ` / `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=0` | PR: `add: "superseded": ["T-0001.2", "T-0001.3"]` / `ready: "ready": ["T-0001.4"]` / `closed: "closed": []` / `superseded: "superseded": ["T-0001.2", "T-0001.3"]` / `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=1` | PASS
- NEW | The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version | base: `moved: ` / `unrecorded: ` | PR: `moved: "superseded": ["T-0001.2", "T-0001.3"]` / `unrecorded: "superseded": ["T-0001.2", "T-0001.3"]` | PASS
- REGRESSION | A second plan at the same approved version supersedes nothing | base: not run | PR: `exit=0` / `"ready": ["T-0001.2"]` / `"remaining": ["T-0001.2", "T-0001.3"]` | PASS (it also printed the same on base, in the same pass)
- NEW | A plan that depends on an old unmerged sub-ticket is refused and writes nothing | base: `exit=0 names=0 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml ` | PR: `exit=2 names=1 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.yaml ` | PASS
- NEW | A re-specced parent's planner input names the sub-tickets its plan supersedes | base: `said=0 listed=3` | PR: `said=1 listed=3` | PASS
- NEW | The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one | base: `park T-0001: sub-ticket closed by a human: T-0001.2` | PR: `park T-0001.4: EMPTY-OUTPUT from implementer` | PASS
- REGRESSION | A sub-ticket of the current plan that a human closed still parks the parent | base: not run | PR: `park T-0001: sub-ticket closed by a human: T-0001.2` | PASS
- NEW | With the new plan merged, the re-planned parent reaches its final check and closes | base: `check: "state": "planned"` / `close=2 planned` | PR: `check: "state": "ready-for-parent-verify"` / `close=0 closed` | PASS
- REGRESSION | A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list | base: not run | PR: `exit=0 ready-for-planner` / `in_input=1 listed=2` | PASS
- REGRESSION | A re-plan is refused while a sub-ticket is not merged | base: not run | PR: `names=1` / `parked spec-v1.yaml ` | PASS
- NEW | A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets | base: `exit=2 parked` | PR: `exit=0 ready-for-planner` | PASS
- NEW | The design doc, build spec, README and changelog record superseded plans | base: `design=0 build-spec=0 readme=0 changelog=0 CONTIGUOUS` | PR: `design=1 build-spec=1 readme=1 changelog=3 CONTIGUOUS` | PASS
- REGRESSION | The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors | base: not run | PR: `whitespace=ok untouched=0` | PASS

Every NEW command failed on base with exactly the "today" output in the spec's verification.md, and printed its THEN exactly on the PR. No NEW criterion passes on both trees.

Gate suite: PASS
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `391 passed in 308.12s (0:05:08)`.

Changed files (`git diff --name-only main...HEAD`): `README.md`, `dev/build-harness.spec.md`, `docs/changelog.md`, `docs/design.md`, `factory/cli.py`, `factory/compose.py`, `factory/subtickets.py`, and the new `tests/factory/test_superseded_plan.py`. The three harness files are the ones the spec's Risk section declares. No existing test was changed.

Probes (scripts `scratch/probe1.sh` and `scratch/probe2.sh`, run on the PR):
- Three plans on one parent. v1 planned T-0001.1 (merged), .2 (closed) and .3 (waiting). v2 planned .4 (not merged) and .5 (merged). v3 planned .7, which depends on .5. Results: the v2 add reported `["T-0001.2", "T-0001.3"]`. A second v2 plan (.6) reported `[]` and logged no second event. The v3 add reported `["T-0001.4", "T-0001.6"]`. `ready-implementers` gave `ready: [T-0001.7]`, `remaining: [T-0001.7]`, `closed: []` and `superseded: [.2, .3, .4, .6]`. The `planned_from` values were `1 1 1 2 2 2 3`. The rule works across more than two plans: merged v1 and v2 work still counts, and every older unmerged sub-ticket is superseded. → OK
- On that store, a fourth plan whose `Depends on` names T-0001.6, an unmerged v2 sub-ticket, is refused with exit 2: `T-0001.8 (ST-1) depends on T-0001.6, which this plan supersedes`. No ticket was written. `parent-check` then counts only `.1`, `.5` and `.7`, and lists the four superseded ones. The refusal is not tied to the scenario's ids. → OK
- `plan whole-spec` on a fresh parent (the one-sub-ticket path, with no planner run) writes `planned_from=1` on T-0001.1, so both creation paths record the field. → OK
- A parent whose whole v1 plan merged, then re-specced to v2 and re-planned: the add reports `"superseded": []`. Merged work is never superseded. → OK
- A hand-set non-integer value (`ticket set T-0001.1 planned_from=abc`) makes `ticket ready-implementers` exit with `{"ok": false, "error": "TypeError: '>' not supported between instances of 'int' and 'str'"}`. In a build, that would park the parent with the error. No harness path writes such a value, no criterion covers it, and the PR's Known gaps names it. → CONCERN (outside the criteria; not a FAIL)

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran verbatim on both trees and matched the spec's "today" and THEN outputs exactly, the full suite passed, and the probes show the rule is general, not fitted to the scenario ids.
ESCALATIONS:
- A hand-edited sub-ticket record whose `planned_from` (or `spec.approved_version`) is not an integer makes every command that splits the plan fail with a TypeError, which would park the parent. These commands are `ready-implementers`, `parent-check`, the close, `resolve --replan`, `subticket add` and the planner's compose. Only a manual `ticket set` can write such a value, and the spec asks for no guard. The operator may want a follow-up that refuses non-integer values in `ticket set` or ignores them in `split_plan`.
