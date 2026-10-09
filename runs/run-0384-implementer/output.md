Sub-ticket: T-0027.3 (ST-3, part D of `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`). Branch `factory/T-0027.3`, head `49cc429`, base `8dfc64b`. Worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0027.3`.

## What changed

The problem: a sub-ticket (one unit of a ticket's plan) can reach its implementer after another ticket's merge has broken one of its scenarios. A scenario is one of the spec's runnable checks. The implementer is the role that writes the sub-ticket's code. A sub-ticket's acceptance can also need a sibling that nothing makes merge first. Until now an agent run found this out. This change catches both cases at `run start`, before any run is spent. The harness then parks the sub-ticket as BLOCKED, which hands it to a human.

**D.1, the record (`factory/cli.py`).** `_add_spec_version` now takes `cfg`. After writing `specs/<id>/v<n>.md`, it writes `specs/<id>/v<n>.yaml` with one key, `integration_head`. That key holds the integration branch's head in the target repo, the commit the version was written against. It is null when the repo or the branch does not resolve. A new helper, `_integration_head(cfg)`, catches `Refused` from `gitops.rev`/`integration_branch`, and `OSError` for a repo path that does not exist. I grepped for callers of `_add_spec_version`. There are exactly three, and all three now pass `cfg`: `spec_add`, `approve_spec --edit` and ST-1's `spec_amend`. `spec_amend` changes in that one argument only.

**D.2, field text (`factory/subtickets.py`).** I added `field_text(text, name)`. It returns the lines of one plan field, from the field's own line to the next `PLAN_FIELDS` field or heading. `sibling_tests` had the same loop inline, so it now reads its "Tests to change" field through `field_text`. It still matches line by line, so its results do not change. `sibling_tests` has one caller, `_check_sibling_tests` in `cli.py`.

**D.3, the check (`factory/cli.py`).** `run_start` calls `_check_drift(root, cfg, t)` for the implementer on a sub-ticket. The call comes before `_check_sibling_tests`, and so before a run id is reserved. The check returns at once when the sub-ticket has a finished implementer run (`compose._runs_for`) or any `approvals/<id>/ruling-*` file. A ruling is a human's written instruction filed with the ticket. Otherwise it collects findings from two rules:
- `_sibling_drift`, the sibling rule. It takes the current plan from `split_plan(subtickets_of(parent))[0]` and the sub-ticket's transitive closure over `depends_on`. Each current sibling that is not `merged` and not in the closure is a finding when its id or label is a whole token in the Acceptance field. A whole token has no word character, `.` or `-` before it, and no word character, `-` or `.<digit>` after it.
- `_test_drift`, the test rule. It counts from the `integration_head` in `specs/<parent>/v<approved_version>.yaml`. It is skipped when there is no record, when the head is null, or when the head is not a commit in the target repo. Named files are the backticked tokens of the design part that exist at the tip, minus test files and `.md` files. Listed files are the backticked tokens, cut at `::`, of the design part's `## Tests to change` section (`_tests_to_change_section`) and of the sub-ticket's Tests to change field. For each first-parent commit in `base..tip` whose `diff --name-only --no-renames c^1 c` touches a named file, each unlisted test file it changes is a finding. The last such commit is kept. Test files match the spec's three patterns (`TEST_FILE_RE`).

Any finding raises `Refused("BLOCKED from harness: spec drift: <findings joined by '; '>. Amend the spec (`spec amend <parent>`) or rule (`resolve <id> --ruling F`)")`. A real refusal reads:
`BLOCKED from harness: spec drift: its Acceptance names T-0001.1 (ready-for-implementer), which has not merged and is not one of its dependencies; tests/test_greet.py changed by 8c94c0c92 since spec v1 was written at 1fffea596. Amend the spec (`spec amend T-0001`) or rule (`resolve T-0001.2 --ruling F`)`

**D.4.** No workflow change. `factory/workflows/build.js` already parks a `BLOCKED ` refusal. The acceptance run of the second NEW scenario shows it parking this one.

No helper was added to `factory/gitops.py`. The check calls the existing `gitops.git`, `gitops.rev`, `gitops.repo_root` and `gitops.integration_branch`.

## Acceptance results

Every command below ran from the worktree through `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; export TMPDIR=<scratch>; bash when-<name>.sh)`. Each `when-*.sh` is the WHEN text copied verbatim from `specs/T-0027/v3.md`. The GIVEN blocks for `t0027-amend.sh` (v3.md) and `t0022-build.mjs` (current truth `openspec/specs/build-dispatch/spec.md`) were run once first.

| Scenario | Before (base `8dfc64b`) | After (`49cc429`) |
|---|---|---|
| NEW: Acceptance names an unmerged sibling | `unmerged: blocked=0 names=0 runs=1 ready-for-implementer` / `merged: exit=2 runs=1` (as the spec's "fails today" says) | `unmerged: blocked=1 names=1 runs=0 ready-for-implementer` / `merged: exit=0 runs=1` |
| NEW: test changed beside a named file parks; ruling lets it start | `park T-0001.1: EMPTY-OUTPUT from implementer` / `greet=0 other=0 runs=2` / `ruled: exit=2 runs=2` (as described) | `park T-0001.1: BLOCKED from harness: spec drift:` / `greet=1 other=0 runs=0` / `ruled: exit=0 runs=1` |
| NEW (intermediate): `spec add` writes the record | `sed: .../specs/T-0001/v1.yaml: No such file or directory`, `0` | `1` |
| REGRESSION: unrelated, listed, amended | (passed on base too) `other: exit=0 runs=1` / `listed: exit=0 runs=1` / `amended: exit=0 runs=1` | `other: exit=0 runs=1` / `listed: exit=0 runs=1` / `amended: exit=0 runs=1` |
| REGRESSION: intent-unchanged amendment re-pins | `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged` | `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged` |
| REGRESSION: later implementer gets the amended spec | `changed=1 merged=1 reason=1 logged=1` / `amended=1 old=0 run_version=2` | same |
| REGRESSION (intermediate): current-truth sibling-tests scenarios in build-dispatch | see below | identical to base (`diff` empty) |
| REGRESSION (intermediate): `git diff --check main...HEAD` | | `check exit=0` |

The sibling-tests scenarios were the three build-dispatch WHENs that source `t0022-sib.sh`. I ran them on a `git archive` copy of base `8dfc64b` (with its own `uv sync --frozen`) and on the head. Both printed exactly:
```
exit=0 ready-for-implementer runs=1
exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer
exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer
exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer
park T-0001.2: BLOCKED from harness:
ruling=0 ready-for-implementer
```

Gates, each run exactly as written from the worktree on commit `49cc429`:
- `(export HOME=...; git diff --check main...HEAD)`: exit 0, no output.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `473 passed in 307.99s`. No existing test failed, so none had to be escalated.

## Tests added/changed

Added: `tests/factory/test_spec_drift.py`, 27 cases. It reuses `test_spec_amend`'s `f` fixture (the spec's t0027-amend.sh store) and `test_sibling_tests`'s `BUILD_DRIVER`. It covers:
- **The record.** `spec add` records main's head. A gate edit and an amendment each record the head at their own time. The head is null for a missing repo, for a directory that is not a repo, and for an integration branch that does not resolve.
- **The sibling rule.** A sub-ticket is refused until its sibling merges, whether the Acceptance field names the sibling by label or by id. A direct or transitive dependency is no finding. Longer tokens are no finding: `ST-10`, `T-0001.1.2`, `XST-1` and `ST-1-old`. A sibling named outside the Acceptance field is no finding.
- **The test rule.** A refusal names the file and the last commit, and it ignores an unnamed-file commit. All three test-file forms count. Test-only commits and unnamed-file commits are no finding. So is a test listed by the sub-ticket (with `::test` cut), or by the spec's design Tests to change. An amendment clears drift. With no record, only the sibling rule applies. A null or unknown recorded head skips the test rule.
- **When the check runs.** A ruling on file skips the check, and so does a finished implementer run. The build workflow parks the sub-ticket with `BLOCKED from harness: spec drift: `, and a `resolve --ruling` lets it start.

With the code changes stashed on base, 15 of the 27 fail and 12 pass. The 12 that pass are the "no finding" guards, which hold trivially when no check exists.

Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- `factory:` markers added: one, in `_test_drift`. The test rule runs one `git diff` per first-parent commit since the spec was written. The marker says to fold this into a single `git log --diff-merges=first-parent --name-only` call if that range grows to hundreds of commits.
- Named files are matched exactly, as the design says: backticked tokens that exist as files at the tip. A token like `factory/cli.py:843` or `` `factory/cli.py` (line 198) `` is not cut, so a `path:line` token names nothing. The parent spec's own design part uses bare paths. A design part that only cites `path:line` gets no test rule.
- The sibling rule treats a sibling with status `closed` as unmerged, because the design says "not `merged`". A closed sibling named in Acceptance would park the sub-ticket until a ruling.
- `sibling_tests` was refactored to read its field through the new `field_text` instead of keeping a second copy of the same loop. It still matches per line, and its existing tests (`test_sibling_tests.py`, `test_plan_fields.py`) pass unchanged. This is a small change to an existing function that the sub-ticket did not ask for by name; I made it so the field-finding rule lives in one place (coding standard rule 1).
- `test_spec_drift.py` binds `f = test_spec_amend.f` to share the fixture. Importing it by name made ruff report F811 on every test. Ruff is not a gate here, but the assignment avoids both the warning and a `noqa`.
- The suite's `conftest.py` points `FACTORY_REPO` at the harness checkout. So in existing tests, every `spec add` now records that checkout's current-branch head. This is harmless: the suite passes, and those specs' design parts name no files that their tests then change.
- The spec's commands call `mktemp -d`, and on this machine that used the OS temp directory (`/var/folders/...`) even with `TMPDIR` set to the scratch directory. The throwaway stores from the acceptance runs are therefore there, not under scratch.

## Out-of-scope observations

- The worktree gained an untracked `.venv/`, created by `uv run --frozen`. It is git-ignored and not committed.
- No reference implementation exists in `~/dev/nanobot-upstream`. A grep of its `*.py` files for `spec drift`, `_check_drift` and `integration_head` found nothing. So nothing here was checked against an as-built fix.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its expected lines after the change and its "fails today" lines before it, and both gates passed on the committed head.
ESCALATIONS: none

Protected paths touched, all declared by the sub-ticket: `factory/cli.py`, `factory/subtickets.py`. `factory/gitops.py` was not touched.
