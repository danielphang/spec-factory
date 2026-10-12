Sub-ticket: T-0047.1, part of T-0047 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`). Branch `factory/T-0047.1`, commit `359b3c6` on base `6203096`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0047.1`.

## What changed

This change moves two groups of functions out of `factory/cli.py`. That file holds most of the harness's commands; the harness is the program that enforces the factory's rules. It is 2,020 lines long. The change only moves code. No command's behaviour changes, and no moved function's text changes. `factory/cli.py` is now 1,839 lines.

- **A. `factory/drift.py`, the spec-drift checks.** Before a sub-ticket's first implementer run, these checks refuse the run when the code has moved away from what the approved spec assumed. The module holds `_check_sibling_tests`, `TEST_FILE_RE`, `TICK_RE`, `_check_drift`, `_sibling_drift`, `_test_drift` and `_tests_to_change_section`. They were lines 249-370 of `factory/cli.py` and are moved byte for byte, in their original order. The module's header is a one-line docstring, then `from __future__ import annotations`, then `re`, `Path`, `gitops`, `specstore`, `store`, `subtickets` and `Refused`. `factory/cli.py` imports `_check_drift` and `_check_sibling_tests` by name for `run_start`.
- **B. `factory/common.py`, the shared helpers and the live-store fence.** The fence refuses a write to the live store from inside a role run. The module holds `out` (30-31), `_rel` (34-35), `_integration_head` (548-554), `_add_spec_version` (557-567), `_in_flight` (1964-1967) and `fence` (1970-1988). They are moved byte for byte, in their original order. The module's header is a one-line docstring, then `from __future__ import annotations`, then `json`, `os`, `Path`, `gitops`, `instance`, `store` and `Refused`. `READ_ONLY` and its comment stay in `factory/cli.py` beside `main`.
- **What `factory/cli.py` imports from the new modules.** It imports `out`, `_rel`, `_add_spec_version` and `fence`. It also imports `_in_flight`, because `store_migrate` still calls it (part C moves `store_migrate` later). It does not import `_integration_head`, because only `_add_spec_version` calls it. Neither new module imports `factory.cli`.
- **Imports `factory/cli.py` no longer uses.** None. Every one of its imports is still used, including `json`, `os` and `re`, as `ruff --select F401` confirms (R11 below).
- **Section comments.** No `# -----` section comment moved or was dropped. The drift code and `_integration_head`/`_add_spec_version` sat inside the "runs" and "spec / plan" sections. `out` and `_rel` came before the first section comment. All three of those sections still have code in `factory/cli.py`. The "live-store fence" section comment stays, because `READ_ONLY` and `main` are still under it.

## Acceptance results

All commands ran from the worktree through the "Running code" wrapper. `TMPDIR` was set to this run's scratch directory, which is where the M script lives.

| Check | Before (base `6203096`) | After (`359b3c6`) |
|---|---|---|
| NEW: The drift checks live in factory/drift.py | `ModuleNotFoundError: No module named 'factory.drift'`, nothing printed | `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` |
| NEW: The shared helpers and the live-store fence live in factory/common.py | `ModuleNotFoundError: No module named 'factory.common'`, nothing printed | `_add_spec_version _in_flight _integration_head _rel fence out` |
| NEW: M, every definition keeps its exact text | `pairs=0 added=0 removed=0 lines=0` | `pairs=1 added=0 removed=0 lines=19`, nothing after it |
| NEW (intermediate): each new module loads first in a fresh interpreter | failed (modules absent) | exit 0, nothing printed |

M is the spec's "moved, not rewritten" script. It compares every top-level definition's source text before and after the change. I copied it from the parent spec v2 with `awk` and ran the heredoc once, as written. `lines=19` uses 19 of the 100-line budget the four sub-tickets share.

REGRESSION checks, run once after the change. Every one passed, so none was re-run on base.

| Check | Output |
|---|---|
| R1 | `factory/__main__.py factory/drive.py factory/stats.py` |
| R2 | `7 True True` |
| R3 `uvx ruff check --select F factory` | `All checks passed!`, exit 0 |
| R4 | `576 passed in 571.87s (0:09:31)`, nothing after it |
| R5 | `0 0` |
| R6 | `0` |
| R7 | `0 2 2` |
| R8 | `0` |
| R9 | `0` |
| R10 | `0 12 1` |
| R11 `uvx ruff check --select F401,F841 factory tests` | `All checks passed!`, exit 0 |
| R12 | `576 passed in 577.86s (0:09:37)`, nothing after it |
| R13 | `0` |
| R14 | `0 1` |
| R15 | `1 1` |
| R16 | `0` |
| R17 | `1 1` |
| R18 | `0 1 1 1` |
| R19 | `1 1 2` |

Gates, each run exactly as written from the worktree:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 569.75s (0:09:29)`, exit 0.

Full logs are in `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0481-implementer/scratch/acc.log` and `gate.log`.

## Tests added/changed

None. The sub-ticket's Interim tests and Tests to change are both "none", and the spec's checks are its acceptance commands. `git diff --name-only main...HEAD -- tests` prints nothing.

## Known gaps and uncertainties

- `spec_amend`, still in `factory/cli.py`, assigns a local variable named `fence`, a Markdown code-fence string. That local hides the imported `fence` function inside `spec_amend`. Before this change it hid the module-level `fence` function in the same way, so behaviour is unchanged, and ruff's F checks pass. Part E moves `spec_amend` to `factory/human.py`, which imports `fence` too, so the hiding moves with it.
- The moves were made with a line-range script, not by hand. Byte-for-byte fidelity rests on the M check (`added=0 removed=0`). That check compares each definition's source text. It does not compare comments between definitions, and this part moved none.
- `factory:` markers added: none. The existing `factory:` comment in `_test_drift` moved with its function, unchanged.

## Out-of-scope observations

- The docstring of `factory/cli.py` still reads "P0 subset of the build-harness spec, part B/K". The parent spec names this as the root cause, but no part changes the docstring.

## Responses to findings

Round 1: none.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION check and both gates were run on `359b3c6` and gave the expected output, and M shows no definition changed.
ESCALATIONS: none
