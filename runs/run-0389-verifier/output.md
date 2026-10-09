Commit: 7c21daea30f6dd1d79a3c78ad92c5d40b383522b (branch `factory/T-0027.2`, clean worktree; `git diff --stat main...HEAD` shows only the 5 files in the PR, 224 insertions)

How I ran it: the PR head was the run worktree. The base, 92e7038 (equal to `main`), was extracted with `git archive` into `scratch/base`. Each tree got its own `uv sync --frozen`. Each tree got one fresh-HOME shell with `VIRTUAL_ENV` unset and `TMPDIR` set to a per-tree scratch dir. In that shell the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" ran once (exit 0 on both trees), then each command ran in order. I diffed the GIVEN block and the three NEW WHEN commands, as saved to scratch, against the spec text in input.md, and they were identical.

Per criterion:
- NEW | "The critic's input lists approved changes not yet archived, other than its own" | base: `listed=0 self=0 decision=0 requirement=0`, `after_archive: heading=0 listed=0` (matches the spec's "fails today") | PR: `listed=1 self=0 decision=1 requirement=1`, `after_archive: heading=1 listed=0` | PASS
- NEW | "A change sent back to the spec writer leaves the critic's list" | base: `listed=0 self=0 decision=0 requirement=0`, `respec: heading=0 listed=0` (matches) | PR: `listed=1 self=0 decision=1 requirement=1`, `respec: heading=1 listed=0` | PASS
- NEW | "A critic run's system prompt carries the cross-ticket rule" | base: `rule=0` (matches) | PR: `rule=1` | PASS
- REGRESSION | `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)` | base: not run (on the base tree it also printed `copies=same`) | PR: `copies=same` | PASS
- REGRESSION (intermediate) | `grep -c 'whichever of the two merges first' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md` | base: not run (on the base tree it printed `0` for each file, exit 1, so the line is new) | PR: `docs/design.md:1`, `docs/prompts/03-spec-critic.md:1`, `factory/prompts/critic.md:1` | PASS
- REGRESSION (intermediate) | harness suite | base: not run | PR: see gate suite, `486 passed` | PASS
- REGRESSION (intermediate) | `git diff --check main...HEAD` | base: not run | PR: no output, exit 0 | PASS

Gate suite: PASS
  `(export HOME=...; git diff --check main...HEAD)`: no output, exit 0.
  `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `486 passed in 307.37s (0:05:07)`. This includes the 13 new tests in `tests/factory/test_critic_approved_changes.py`.

Probes (on the PR head, each with the spec's GIVEN fixture plus extra tickets):
- A third ticket was approved with two capabilities and two Decisions lines, then parked, while a fourth was under review → the parked ticket is listed as `### T-0002: Third (parked)` with `Changes: demo: ADDED Shouts; other: ADDED Whispers` and both decisions. A `ready-for-planner` ticket is listed too. A stray file `stray-file.txt` in `openspec/changes/` is ignored. `sources` holds `openspec/changes/T-0001/proposal.md` and `openspec/changes/T-0002/proposal.md` → OK.
- Self-skip on its own: the reviewed ticket T-0003 was given its own change folder, forced to `planned` (outside the spec-loop skip list), and its critic input recomposed → only T-0001 and T-0002 are listed, so the own-id skip works independently of the status skip → OK.
- A spec writer's run input (role `spec_writer`) → `section=0`. The section reaches only the critic → OK.
- A malformed delta file in another ticket's change folder → compose exits 0 and the entry reads `Changes: none`. No critic run crashes on someone else's bad folder → OK.
- `proposal.md` deleted from a listed change folder → compose exits 0. The entry reads `Decisions: none` and adds no source. This matches the gap the PR states → OK.
- A Decisions section that contains a fenced code block → the fence lines (```` ``` ````) and the line inside the fence show up as `- ` decision lines. The cause is the existing `specstore.decisions_of` (factory/specstore.py:306-320), which this PR does not change. The design says to use that helper as-is → OK for this sub-ticket. Logged under out-of-scope observations.

Protected paths touched, all declared by the sub-ticket: `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`. `docs/design.md` changed only in the critic block (4 lines under rubric item 5), as the scope says.

Out-of-scope observations:
- `specstore.decisions_of` does not skip fenced lines inside `## Decisions`. Fenced lines in a proposal's Decisions section therefore reach the critic, and every other caller, as decisions. This predates the PR.
- The spec's commands create their throwaway stores with `mktemp -d`. On macOS that puts them in the system temp dir (`/private/var/folders/...`) even when `TMPDIR` points elsewhere. My probe stores landed there too, not under this run's scratch directory.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran exactly as written on both trees. Each NEW one failed on base with the spec's stated output and passed on the PR. Both gates passed, and the probes showed nothing special-cased to the tested inputs.
ESCALATIONS: none
