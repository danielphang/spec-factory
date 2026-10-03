Commit: 7c0a0353d3d0759f0942ab2ab96395aff8f70f29

Parent-close run. The head is the merge of factory/T-0002.1 at 7c0a0353d. The base is dd09a7cb1, the commit before that merge. Every acceptance command was run verbatim from the worktree root under bash, and on the head also under `zsh -f`. Both shells gave the same output.

Changes from base to head (`git diff --stat dd09a7cb1 7c0a0353d`): `factory/cli.py` (+3/-6) and the new file `tests/factory/test_killed_checker.py` (+35). The diff touches no file under `factory/workflows/**` and edits no existing test. The read is now `... if a.output and not a.killed else ""`. #16's killed-only `Commit:` branch was removed, as the design called for, and the `Commit:` checks are now gated by `if not a.killed:`.

Per criterion:
| Type | Command (scenario) | Base dd09a7cb1 | PR 7c0a0353d | Result |
|---|---|---|---|---|
| NEW | killed-verifier-without-output-file-parks-as-budget-kill | `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci` (stderr: `factory: FileNotFoundError: ... runs/R2/output.md`) | `reviewer=0 verifier=0 decision=park reason=budget kill: verifier` | PASS |
| NEW | killed-reviewer-without-output-file-parks-as-budget-kill | `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer` | `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer` | PASS |
| REGRESSION | killed-record-without-output-flag-still-records-killed | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| NEW | killed-output-naming-another-commit-records-killed | `exit=2 rows=[] status=` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| REGRESSION | unkilled-record-with-missing-output-file-still-fails | `exit=1 rows=[] events=0` | `exit=1 rows=[] events=0` | PASS |
| REGRESSION | factory-suite-passes-with-killed-checker-change (`PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`) | `68 passed in 68.62s`, exit 0 | `70 passed in 110.39s`, exit 0 | PASS |

Each NEW criterion fails on base for the reason the spec gives. The first two fail with `FileNotFoundError` on the missing output.md, and the fourth is refused with exit 2 by the `Commit:` check. Each passes on the PR, and every base output matches the spec's "today" text word for word.

The new test can fail on base. I copied base's `factory/`, `bin/` and `tests/factory/` into a scratch directory, added the PR's `test_killed_checker.py`, and ran it there. Result: `2 failed in 4.67s`, both from `results record ... --killed: factory: FileNotFoundError: ... runs/run-0007-{verifier,reviewer}/output.md`. I then put the PR's `factory/cli.py` into the same scratch copy and the result was `2 passed in 4.81s`. No file in the worktree was edited.

Gate suite: PASS
- `uv run ruff check nanobot/` printed `All checks passed!` and exited 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"` exited 0 with `5 failed, 7173 passed, 25 skipped in 128.52s`, `tests run: 7203`, "failure set is within the baseline (5 known failure(s))". The five failures are in tests/gateway/test_runtime.py, tests/cli/test_tui_launcher.py, tests/lionbot/test_service_log_paths.py (x2) and tests/config/test_config_paths.py. None of them is in tests/factory.

Probes. All were run on the head with `bin/factory` against throwaway stores:
- P1: killed, `--output` names a directory → `exit=0 rows=[verifier.yaml ] status=KILLED`. The output is not opened, as required. OK
- P2: killed verifier whose `--output` is a full `Commit: <head>` / `Gate suite: PASS` / `STATUS: VERIFIED` file → `exit=0 rows=[verifier.yaml ] status=KILLED`, with no `ci` row. The output's verdict is ignored and no ci row is written. OK
- P3: not killed, output says `Commit: deadbeef00` → `exit=2 rows=[]`. #16's stale-commit refusal still holds without `--killed`. OK
- P4: not killed, output has no `Commit:` line → `exit=2 rows=[]`. Still refused. OK
- P5: killed with a short `--head deadbeef` → `exit=2 rows=[]`. Head validation still runs before the killed path. OK
- P6: killed with `--output ''` → `exit=0 rows=[reviewer.yaml ] status=KILLED`. OK
- P7: not killed, valid APPROVE for the head → `exit=0 rows=[reviewer.yaml ] status=APPROVE`. The normal path is unchanged. OK

The fix is not special-cased to the tested inputs. It changes behaviour only when `--killed` is given.

Out-of-scope observations:
- `uv run` printed `warning: VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test does not match the project environment path .venv`. My shell inherited blue's venv in its environment, and uv ignored it and used the worktree's `.venv`. Results are not affected.
- `git status --short` in the worktree was empty after the gate run, so nothing was left modified.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command was run verbatim on both base and head, and every output matched the spec exactly. The new test fails on base code for the stated reason. The gate exited 0. The probes found no special-casing.
ESCALATIONS: none
