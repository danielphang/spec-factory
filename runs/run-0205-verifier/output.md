Commit: a78de4b5a03a3c2f87e9976542035fb4a1ab0f07 (branch `factory/T-0023.2`, base `2e61b852d1da27a85208eb94c8d10b8a5557e2c7`, which is also `main`)

Setup:
- PR: the given worktree, clean (`git status --short` empty), after `uv sync --frozen` under the HOME wrapper.
- Base: a fresh clone of `~/dev/spec-factory` at `2e61b85` in `scratch/base`, with its own `uv sync --frozen`.
- Fixtures: the parent's GIVEN block was extracted verbatim from input.md and run once under bash with `TMPDIR=scratch/fx`. It wrote `t0023-parent.sh`, `t0023-closed.sh` and `t0023-wf.mjs`.
- Each WHEN was extracted verbatim from the sub-ticket's acceptance lines (input.md lines 87-117). Each ran under `/opt/homebrew/bin/bash` from the checkout root, inside `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; export TMPDIR=<scratch>/fx; <WHEN>)`.

Per criterion:
- NEW | A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling | base: `exit=2 parked pr=0` / `ruling=missing` / `in_input=0` | PR: `exit=0 ready-for-implementer pr=0` / `ruling=kept` / `in_input=1` | PASS
- REGRESSION | A ruling on a critic ESCALATE still returns the ticket to the critic | base: not run | PR: `exit=0 ready-for-critic` | PASS
- NEW | A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list | base: `exit=2 parked` / `in_input=0 listed=0` | PR: `exit=0 ready-for-planner` / `in_input=1 listed=2` | PASS
- NEW | A re-plan is refused while a sub-ticket is not merged | base: `names=0` / `parked spec-v1.yaml ` | PR: `names=1` / `parked spec-v1.yaml ` under bash | PASS. Under zsh the same WHEN prints `names=2`; see ESCALATIONS.
- NEW | A later plan's sub-tickets take the next free ids and may depend on a merged sibling | base: `"ready": []` only | PR: `"id": "T-0001.3"` / `"depends_on": ["T-0001.2"]` / `"ready": ["T-0001.3"]` | PASS
- REGRESSION | A plan that reuses an existing sub-ticket id is refused and writes nothing | base: not run | PR: `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml ` | PASS
- NEW | The README describes the new resolve verbs | base: `replan=0 gap=1` | PR: `replan=1 gap=0` | PASS
- NEW | Intermediate check, the changelog entry carries this seam's clause | base: `51 CONTIGUOUS` / `1` | PR: `51 CONTIGUOUS` / `4` | PASS
- NEW | Intermediate check, the new test files pass (`uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_resolve_rulings.py tests/factory/test_replan.py`) | base: exit 4, `ERROR: file or directory not found: tests/factory/test_resolve_rulings.py`, as expected for a criterion about new files | PR: `20 passed in 11.33s` | PASS. To show the tests are meaningful, I copied both PR test files into a second clean clone at base and ran them there. Result: `14 failed, 6 passed`. One example: the reused-label test got `T-0001.1 already exists` where it expects the new message. The 6 that pass on base cover unchanged behaviour.
- REGRESSION | The harness suite passes with an uncommitted harness edit | base: not run | PR: `235 passed in 209.04s (0:03:29)` | PASS. A `/tmp/t0023-suite.NVdKhV` directory was present afterwards. `ps` shows it belongs to a concurrent run, `run-0206-reviewer`, which is running the same scenario. It is not left over from this run.
- REGRESSION | The change adds no whitespace errors | base: not run | PR: `exit=0` | PASS

Gate suite: PASS
- `(export HOME=…; git diff --check main...HEAD)`: no output, rc=0.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `235 passed in 173.72s (0:02:53)`, with no failures or errors.

Probes:
- `subtickets.parse` with existing ids `T-0001.1` to `T-0001.10` and a 2-sub-ticket plan, whose deps are `T-0001.10, .2` and `ST-1, T-0001.1` → the plan gets `T-0001.11` and `T-0001.12`, with deps `['T-0001.10','T-0001.2']` and `['T-0001.11','T-0001.1']`. Numbering takes the numeric maximum, not the string maximum, and the shorthand and label aliases resolve → OK
- `parse` with gapped existing ids `.1` and `.3` → the new sub-ticket gets `T-0001.4`. A dependency on a non-existent `T-0001.7` is still refused with "not a sub-ticket of this plan". A head `T-0001.2` that reuses an existing id is refused with the spec's message. With no `existing`, a first plan numbers `.1` and `.2` → OK
- CLI run on a scratch store with 11 merged sub-tickets:
  - `--replan` before the parent is parked → refused, `T-0001 is ready-for-parent-verify`.
  - After the park → `exit=0 ready-for-planner`. The planner input lists `T-0001.1` to `T-0001.11` in numeric order, under the spec's heading and first line.
  - A second `--replan` while the parent is `ready-for-planner` → refused. Only `ruling-1.md` and `resolve-1.yaml` were written.
  - Result → OK
- Not-merged refusal scenario run verbatim in zsh 5.9 → `names=2`. zsh's MULTIOS sends stdout into the pipe as well as to `/dev/null`, and the harness echoes each refusal as a JSON `error` on stdout as well as on stderr (design, H2 evidence). The code's refusal text is correct. Only the counting depends on the shell → CONCERN, not FAIL. Details under ESCALATIONS.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command and both gates ran on the clean PR head. Each NEW command failed on a fresh base clone for the reason the spec states and passed on the PR. The probes show the numbering and dependency logic is not special-cased to `.3`.
ESCALATIONS:
- The scenario "A re-plan is refused while a sub-ticket is not merged" depends on the shell. It prints `names=1` under bash, which is the spec's expected result, and `names=2` under zsh, the default shell in this environment's tool runner. The cause is `2>&1 >/dev/null |` combined with zsh MULTIOS: the stdout JSON copy of the refusal also reaches grep. The implementer reported the same thing. Decision for the operator: either run this change's scenarios under bash or sh, or, at the next spec revision, change the WHEN to send stderr to a file and grep that file.
