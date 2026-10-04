Commit: 9300012d8c63e1304d27b0c47415928a6eb9d840 (branch `factory/T-0019.2`; base and `main` are both 9853737e24b2acdc001546b399d2a5a8c3dd6d85, which already holds S1)

How I ran it. Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0179-verifier/wt`. `git status --short` printed nothing before and after the run. Round 2 changed only `tests/factory/test_plan_fields.py`: `git diff --stat 381f4c6 HEAD` prints `1 file changed, 6 insertions(+), 29 deletions(-)`. I still re-ran everything on this head.
- I wrote the parent's four fixture scripts verbatim to `$TMPDIR/t0019-{parent,triage,impl,probe}.sh`. Then I ran `uv sync --frozen`, which gave Python 3.12.13.
- For base, I extracted `git archive 9853737` into a scratch directory and ran `uv sync --frozen` there. The A9 base check needs git, so it ran in the PR worktree against `main...9853737`.
- Every scenario command and probe ran under `HOME` set to a fresh `mktemp -d` directory. The one exception is the bare gate command, which ran exactly as written.

Per criterion:
- NEW | A1, "Dash-bulleted field lines keep their dependencies" | base: all three sub-tickets are `"state": "ready-for-implementer", "depends_on": [], "parallel_safe": false` | PR: `[{"id": "T-0001.1", "label": "ST-1", "state": "ready-for-implementer", "depends_on": [], "parallel_safe": false}, {"id": "T-0001.2", "label": "ST-2", "state": "waiting-dependencies", "depends_on": ["T-0001.1"], "parallel_safe": true}, {"id": "T-0001.3", "label": "ST-3", "state": "waiting-dependencies", "depends_on": ["T-0001.2"], "parallel_safe": true}]`, which is exactly the expected list | PASS
- REGRESSION | A2, "Star-bulleted, bold, indented and plain field lines read as before" | base: not run | PR: exactly the expected list. `T-0001.1` is `[]`/true/ready, `T-0001.2` is `["T-0001.1"]`/true/waiting, and `T-0001.3` (label `T-0001-C`) is `["T-0001.2"]`/false/waiting | PASS
- NEW | A3, "A sub-ticket with no Depends on line is refused" | base: the success JSON with `T-0001.2` at `"depends_on": []`, then `exit=0`, then `T-0001.1.yaml T-0001.2.yaml T-0001.yaml` | PR: stdout carries `{"ok": false, "error": "ST-2: no \"Depends on:\" line; ..."}`. stderr (captured on its own) is `ST-2: no "Depends on:" line; write "Depends on: none" when it depends on nothing`. Then `exit=2`, and the listing is `T-0001.yaml` alone | PASS
- NEW | A4, "The planner prompt shows the parsed lines in every copy" | base: `0 0 0 0 0` for each of the three files | PR: `docs/design.md 1 1 1 1 1`, `docs/prompts/04-planner.md 1 1 1 1 1`, `factory/prompts/planner.md 1 1 1 1 1` | PASS
- REGRESSION | A5, "The planner block and its copies stay identical" | base: not run | PR: `SAME` | PASS
- NEW | A6, "The changelog records the change in order" | base: `1` then `CONTIGUOUS`, because S1 merged entry 48 first, and `grep -cF "A plan's bulleted field lines lost every sub-ticket's dependencies" docs/changelog.md` prints `0` | PR: `1` then `CONTIGUOUS`, and the same grep prints `1`. Entry 48 carries the S2 clause in parent E1's wording as its second sentence, with no new number | PASS. The command's own output is the same on base and PR, which the plan foresaw. The THEN's added condition, that the entry carries the S2 clause, fails on base and passes on the PR. So the criterion fails on base for the stated reason, and I do not class it as a SPEC-DEFECT. I checked the added condition by grep and by reading the diff, not with the command.
- REGRESSION | A7, "The change adds no whitespace errors" (`git diff --check main...HEAD; echo "exit=$?"`) | base: not run | PR: `exit=0` only | PASS
- REGRESSION | A8, "This repo's gate suite passes under a throwaway HOME" | base: not run | PR: `190 passed in 111.15s (0:01:51)`, exit 0. That count includes `test_plan_fields.py` | PASS
- NEW | A9, "Intermediate check: only declared files change" | base: `git diff --name-only main...9853737` prints nothing | PR: exactly `docs/changelog.md`, `docs/design.md`, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`, `factory/subtickets.py`, `tests/factory/test_plan_fields.py` | PASS

New test file against base code: I copied `tests/factory/test_plan_fields.py` into the base extract. It gave `5 failed, 3 passed`: both refusal cases and 3 of the 4 bullet cases failed. The plain `* ` case already read on base. On the head the file passes as part of the 190.

Gate suite: PASS
- `git diff --check main...HEAD` ran exactly as written inside A7: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` ran exactly as written: `190 passed in 114.77s (0:01:54)`, exit 0. Before this bare run, I grepped `tests/factory` and `factory` for `expanduser`, `Path.home`, `"HOME"`, `$HOME` and `~/`. Every `HOME` hit sets `HOME` to a temporary directory or is test data, and every `expanduser` resolves a path given by an environment variable or argument. Nothing in the suite writes under the real home.

Probes (each through `bin/factory subticket add` on a fresh fixture store, PR head):
- 25 sub-tickets chained ST-1 → … → ST-25, using `- ` bullets with mixed bold and plain field names → 25 created. Each depends exactly on the one before it, ST-1 is parallel-safe and none of the others are. The parser does not depend on the size or shape of the test plans. → OK
- CRLF line endings with `- ` bullets, and `- Depends On:` with a capital O → read correctly: `ST-2` depends on `["T-0001.1"]` and is waiting, exit 0. → OK
- `- Depends on:` third of three missing (`ST-3` has only `- Parallel-safe: yes`) → stderr names `ST-3`, exit 2, only `T-0001.yaml` written. → OK
- `- Depends on:` with an empty value → accepted as no dependencies. Separately, a sub-ticket whose only `Depends on:` text sits in a nested Acceptance bullet (`  - Depends on: ST-1 is merged first`) → read as the field, so the sub-ticket gets `["T-0001.1"]` and is not refused. → CONCERN, outside the criteria. The empty value is the existing `NONE_RE` rule (`^\W*$`). The nested-bullet reading is the gap the PR declares under Known gaps. Neither shows special-casing, and neither breaks a stated criterion.

Out-of-scope observations:
- `agents/factory-planner.md` still holds the older, indented planner OUTPUT block. The spec already notes this, and `agents/**` is a protected path.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command on this head with the fixture written verbatim, ran every NEW command on base, and both gate commands passed exactly as written. The probes show the parser change is general.
ESCALATIONS:
- An empty `Depends on:` line passes the new check. The new rule refuses a sub-ticket with no `Depends on:` line, but a bare `- Depends on:` still counts as "none", because of the existing `NONE_RE` empty-value rule. A planner that leaves the value blank still gets no dependencies without a word. The spec does not cover this case. The operator decides whether a later ticket should refuse it.
- A bulleted `Depends on:` line nested in a sub-ticket's Acceptance list is read as the field, as the PR's Known gaps says. It can also stand in for a missing top-level line, so that sub-ticket is not refused.
- Protected paths touched, all declared by the sub-ticket: harness `factory/subtickets.py` and `factory/prompts/planner.md`, and generated `docs/prompts/04-planner.md`. The merge gate needs a human approval for them.
