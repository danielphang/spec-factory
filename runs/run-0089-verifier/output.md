Commit: be292addbee09d9b2709fd84b54e63de8e9f6477 (branch `factory/T-0012.4`; harness revision `010d1b00c5835c7022a72771c63f63f8b6ab3707`)

Method:
- **PR:** the given worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0089-verifier/wt` at `be292ad`. `git status --porcelain` was empty before and after every run. `uv sync --frozen` exited 0.
- **Base:** a scratch clone of the worktree, detached at `6921dfd8eaccb5fb9d2fb7440c20291c18c165c9`, with its own `uv sync --frozen` (exit 0).
- **Commands:** I pulled each parent WHEN out of `intake/state/specs/T-0012/v3.md` with a script, not by retyping. All 30 commands are byte-identical to the copies in input.md. The intermediate WHENs came from input.md the same way.
  - missing-lock-refused is lock-mismatch-refused with its `printf '%040d\n' 0 2>/dev/null > $T/.factory/harness.lock` replaced by `rm -f $T/.factory/harness.lock`. The script asserted that this text appears exactly once before replacing it.
  - Every command ran with `bash` from the tree's root, with `FACTORY_INSTANCE/REPO/STATE/INTEGRATION_BRANCH` unset.
- **Diff:** `git diff --stat main...HEAD` shows 4 files, 340 insertions and 1 deletion: `factory/cli.py`, `factory/instance.py`, `tests/factory/test_harness_lock.py` (new) and `tests/factory/test_instance.py` (+1). The `test_instance.py` change is exactly the one line the operator ruled under Tests to change. No assertion is altered.

Per criterion:
| Label | Criterion | Base `6921dfd` | PR `be292ad` | Result |
|---|---|---|---|---|
| NEW | lock-mismatch-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS |
| NEW | accept-current-revision-rewrites-lock | `init=0` / `exit=2 lock_is_rev=no logged=0` (argparse does not know `--accept-harness`) | `init=0` / `exit=0 lock_is_rev=yes logged=1` | PASS |
| REGRESSION | accept-other-revision-refused | `init=0` / `exit=2 lock=0000000000000000000000000000000000000000 tickets=0` (vacuous: unknown option) | same | PASS |
| REGRESSION | throwaway-store-ignores-lock | `init=0` / `exit=0 ticket=[T-0001.yaml]` | same | PASS |
| NEW | dirty-harness-refused | `init=0` / `exit=0 tickets=1 names=0` | `init=0` / `exit=2 tickets=0 names=1` | PASS |
| NEW | missing-lock-refused | `init=0` / `exit=0 tickets=1 hint=0` | `init=0` / `exit=2 tickets=0 hint=1` | PASS |
| REGRESSION | init-and-paths-exempt | `paths=0 init=0 lock=0000000000000000000000000000000000000000` | same | PASS |
| REGRESSION | accept-does-not-override-dirty | `exit=2 lock_same=yes tickets=0` (vacuous: unknown option) | same | PASS |
| REGRESSION | harness-files-in-repo | `agents=6 green_only=0` | same | PASS |
| REGRESSION | role-prompt-text-unchanged | `changed=0 of 14` | same | PASS |
| REGRESSION | init-creates-instance-in-throwaway-target | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` | same | PASS |
| REGRESSION | store-command-from-subdirectory-uses-target-instance | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` | same | PASS |
| REGRESSION | command-outside-any-instance-refused | `exit=2 created=0 names_instance=1` | same | PASS |
| REGRESSION | factory-instance-override-from-elsewhere | `init=0` / `found=1` | same | PASS |
| REGRESSION | composed-input-opens-with-instance-context | `init=0` / `first=[CTX-MARKER for demo]` | same | PASS |
| REGRESSION | run-system-prompt-names-instance | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` | same | PASS |
| REGRESSION | paths-name-harness-workflows-and-instance | `init=0` / `True True True True` | same | PASS |
| REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `92 passed in 92.71s (0:01:32)` | `sync=0` / `116 passed in 89.62s (0:01:29)` | PASS |
| REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS |
| REGRESSION | whitespace (sub-ticket diff) | — | `git diff --check main...HEAD; echo exit=$?` → `exit=0` | PASS |

Notes on the table:
- **The four NEW criteria** each fail at base for the reason the spec gives: the lock is not enforced, and `--accept-harness` does not exist. Each passes on the PR.
- **The four REGRESSION C criteria** pass at base only vacuously. At base, argparse rejects `--accept-harness` with exit 2, and the throwaway-store and exempt paths were never checked. That matches the operator's relabel. The new tests are what discriminate here (`116 - 92 = 24` new cases).
- **Extra check:** whitespace-clean with `BASE=$(git rev-parse main)` also printed `exit=0`.

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `116 passed in 87.19s (0:01:27)`, exit 0. An earlier run gave `116 passed in 97.49s`.

Probes (worktree's `bin/factory`; dirty cases on a fresh local clone with its own `uv sync --frozen`):
| Probe | Result | Verdict |
|---|---|---|
| `FACTORY_STATE` names the own store through a symlink plus a trailing slash, lock mismatched | `exit=2 tickets=0`, mismatch message | OK: the own-store test resolves paths, so this does not bypass the lock |
| Lock holds the correct revision with CRLF | `exit=0 tickets=1` | OK |
| `--accept-harness <rev>` when the lock already matches | `exit=0`, lock unchanged, 1 `harness.accepted` event | OK |
| `--accept-harness` written after the subcommand | `exit=2`, lock unchanged, no ticket | OK: C.3 says it goes before the subcommand |
| `--accept-harness ''` and `--accept-harness "<rev> "` (trailing space) | both `exit=2`, lock unchanged | OK: not special-cased to `1234567` |
| `harness.lock` is a directory | `exit=2 tickets=0`, message shows `(none)` | OK |
| Dirty clone: change staged only, in nested `factory/workflows/build.js` | `exit=2`, path named | OK |
| Same clone after `git reset --hard` | `exit=0`, ticket created | OK |
| Dirty clone: tracked `factory/__init__.py` deleted | `exit=2`, path named | OK |
| Dirty clone: edits outside the harness paths only (`docs/design.md`, untracked `tests/factory/zz.txt`) | `exit=0` | OK |

Nothing suggests the fix is special-cased to the tested inputs.

STATUS: VERIFIED
CONFIDENCE: high. I ran every criterion and both gates myself on the given head and base, with commands taken byte-for-byte from the pinned spec. The probes cover the boundaries the C criteria leave open.
ESCALATIONS:
- Non-blocking, outside this sub-ticket's criteria (B behaviour, already on main): a relative `--file` path for `ticket new` resolves against the harness checkout, not the caller's working directory. `bin/factory` changes into the harness before running. My first probe run, with `--file r.md` from a target directory, failed with `no such file <harness>/r.md`. The spec scenarios all pass absolute `$T/r.md`, so no criterion catches this.
- Non-blocking, already in the implementer's Known gaps: the B and C tests drive own-store targets, so the suite fails when run from a dev checkout with uncommitted harness edits. C.4 refuses them by design. The gate runs on committed heads and is unaffected. Whether those tests should drive a clean clone instead is a design question for a later ticket.
