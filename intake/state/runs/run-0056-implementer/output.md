Sub-ticket: T-0012.1 (`/Users/dphang/dev/spec-factory/intake/state/tickets/T-0012.1.yaml`; parent spec `intake/state/specs/T-0012/v3.md`)
Branch: `factory/T-0012.1` in worktree `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.1`. Base `cdb1c67`, head `372a47c`. There is no remote, so the PR is the branch plus this description.

Commits on the branch over main:
- `097fb01`: merge of green's filtered harness history. This is the `git pull --no-rebase --allow-unrelated-histories --no-edit <scratch>/g HEAD` the ticket prescribes. It brings in 31 commits from the filtered clone, 28 of them non-merge.
- `dd375f5`: the interim overlay (A.4).
- `372a47c`: `pyproject.toml`, `uv.lock` and the root `.gitignore` (A.5).

## What changed

**A.1. Scratch clone.** I ran `git clone -q --no-local --single-branch --branch feat/lionbot-v3 ~/dev/nanobot-upstream g` in a scratch directory outside both repos (`…/scratchpad/imp/g`). The clone's tip is `7c0a0353d3d0759f0942ab2ab96395aff8f70f29`, "Merge factory/T-0002.1: …", which is exactly G. Nothing was run in `~/dev/nanobot-upstream`.

**A.2. History filter.** In the clone only, I ran `git filter-repo --path factory/ --path bin/factory --path tests/factory/ --path-glob '.claude/agents/factory-*' --path-rename .claude/agents/:agents/`.
- Result: 31 commits and 72 files. That is the 69 the byte check covers, plus the three per-repo files.
- Outside `factory/` and `tests/`, the only files are `agents/factory-{clerk,planner,spec-critic,spec-writer,stub,triage}.md` and `bin/factory`.
- `scripts/full_suite_gate.py` is not in the filtered paths, so it was never imported.

**A.3. Import.** I ran the prescribed `git pull --no-rebase --allow-unrelated-histories --no-edit <scratch>/g HEAD` on `factory/T-0012.1`. It merged without conflicts and created 75 files in total over the three commits.

**A.4. Interim overlay** (`dd375f5`):
- `factory/prompts/context.md` is now a byte copy of `intake/instance/context.md`.
- `factory/prompts/preamble.md` is now a byte copy of `intake/instance/preamble.md`.
- `factory/config.yaml` is now a copy of `intake/instance/config.yaml` with exactly two lines changed (`diff intake/instance/config.yaml factory/config.yaml`):
  - `5c5`: `state_dir: ../state` → `state_dir: intake/state`
  - `26c26`: `environment_files: []` → `environment_files: ["uv.lock"]`
- No other imported file was touched.

**A.5. Project files** (`372a47c`):
- `pyproject.toml` contains exactly what the spec lists: `[project]` with name `spec-factory`, version `0.0.0`, `requires-python >=3.11` and `dependencies = ["pyyaml>=6"]`; `[dependency-groups] dev = ["pytest>=8"]`; and `[tool.uv] package = false`.
- `uv.lock` is the output of `uv lock`: "Resolved 8 packages", with pyyaml 6.0.3 and pytest 9.1.1.
- `.gitignore` has three lines: `.venv/`, `__pycache__/`, `.pytest_cache/`.
- Imports checked: across `factory/*.py` and `tests/factory/*.py`, `yaml` and `pytest` are the only third-party imports, so no other dependency is needed.

**A.6. Suite check.** See Acceptance results below. It reports `70 passed`.

## Acceptance results

All of these ran from the worktree root with bash. The "after" run used `env -u VIRTUAL_ENV` and started from a deleted `.venv`, so `uv sync` built a fresh environment. At that point `main` was `cdb1c67` and HEAD was `372a47c`.

| Criterion | Before (base `cdb1c67`) | After (`372a47c`) |
|---|---|---|
| harness-history-carried (NEW) | `24` | `0` |
| harness-suite-passes-after-uv-sync (NEW) | `sync=2` / `no tests ran in 0.00s` | `sync=0` / `70 passed in 109.27s (0:01:49)` |
| harness-files-in-repo, interim (NEW) | ten `missing …` lines, then `agents=0 green_only=0` | only `agents=6 green_only=2` |
| role-prompt-text-unchanged, interim (NEW) | `changed=14 of 14` | `changed=1 of 14` |
| import-byte-identical (NEW) | `differ=69 of 69` | `differ=0 of 69` |
| overlay-is-this-repo's-instance (NEW) | `FileNotFoundError: … 'factory/config.yaml'`, no `overlay=same` | `overlay=same`, then `intake/state ['uv.lock']`, and no `gate_script_present` |
| project-files (NEW) | `lock=2` and three `missing …` lines (no `.gitignore`) | only `lock=0` |
| cut-anchor-still-valid (NEW) | `0` | `0` |
| green-harness-still-present (REGRESSION) | `green keeps its harness`, porcelain count `0` | `green keeps its harness`, porcelain count `0` |
| whitespace, sub-ticket diff (REGRESSION) | `exit=0` | `exit=0` |
| Gate `git diff --check main...HEAD` | (empty range) | no output, exit 0 |

**cut-anchor-still-valid** already printed `0` before the change. That is expected: it checks green, not this branch, and it stayed `0` at merge time, so there is nothing to escalate.

**Where the remaining `changed=1 of 14` comes from.** I checked separately:
- All six `agents/factory-*.md` files are byte-identical to green's at G (`cmp` of the full files, not only after the `grep -v` filter).
- The seven role prompts pass, since import-byte-identical covers them.
- The one failure is the preamble comparison. On this branch, `docs/prompts/00-preamble.md` does not exist yet (T-0012.2 creates it). Even against `prompts/00-preamble.md`, the overlay preamble differs on line 1 (repo name filled) and line 38 (protected-path line filled). That is the expected overlay difference, which T-0012.3 replaces.

**Proof the suite ran on this tree in a fresh env:**
- `uv run --frozen python -c 'import sys,yaml;print(sys.prefix, yaml.__version__)'` printed `/Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.1/.venv 6.0.3`.
- `pytest --co` printed `rootdir: /Users/dphang/dev/spec-factory/intake/state/worktrees/T-0012.1` and `70 tests collected`.

**Control: the overlay's `environment_files` is what makes the suite pass.** I set `environment_files: []` in `factory/config.yaml` without committing and ran `tests/factory/test_shepherd.py::test_worktrees_get_the_integration_checkout_s_untracked_lockfile`. It printed `1 failed`. After `git checkout -- factory/config.yaml`, the same test printed `1 passed`, and `git status --porcelain factory` was empty. This matches the parent's Evidence that this repo's config without `uv.lock` gives `1 failed, 69 passed`.

## Tests added/changed

None. `tests/factory/**` (7 test `.py` files, `__init__.py` and fixtures) arrives as new files. Import-byte-identical shows they are byte-identical to green at G. No test file was edited.

## Known gaps and uncertainties

- **Merge commit subject.** Because of the prescribed `--no-edit`, the import merge `097fb01` has git's default subject, which contains my scratch path: `Merge /private/tmp/claude-501/…/scratchpad/imp/g into factory/T-0012.1`. I did not amend it, because the ticket fixes the command. It is cosmetic, but the path will be in `main`'s history forever.
- **Which store the overlay config points at.** `factory/config.yaml` has `state_dir: intake/state`, relative to the checkout root. Once this merges, running `~/dev/spec-factory/bin/factory` without `FACTORY_STATE` resolves to the live store `~/dev/spec-factory/intake/state`, and nothing locks it (the lock is part C). The intended interim behaviour is "this repo's instance", but the operator should keep driving tickets through `intake/harness/` until E. The imported tests are not affected, because they all set `FACTORY_STATE` to throwaway stores. In this worktree, `intake/state` resolves to the worktree's tracked copy of the store, and nothing ran against it: `git status --porcelain --ignored` shows only `!! .venv/`.
- **Stale text in the overlay config.** The config carries `intake/instance/config.yaml` verbatim apart from the two required lines, so it keeps text that no longer fits:
  - `request_dir: ../../issues`, which no harness code reads;
  - header comments that mention `intake/setup.sh`, `HARNESS_PIN`, and "No test suite exists here until #19 part A".

  I left them alone because the spec asks only for those two changes, and B deletes the file.
- **Python version.** `uv lock` resolved with the CPython 3.12.13 found on this machine. The lock covers `requires-python >=3.11`, but I ran the suite only on 3.12.
- **Shell environment.** My shell inherits `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`. uv ignores it for this project and prints a warning. The recorded "after" run unset it.

## Out-of-scope observations

- The overlay preamble's protected-path line does not name the harness code (`factory/**`, `bin/factory`, `agents/**`, `pyproject.toml`, `uv.lock`). Until E adds the `harness` class, later sub-tickets that edit harness paths will not be flagged as touching protected paths by the preamble text.
- The scratch clone and filtered repo are still at `/private/tmp/claude-501/-Users-dphang-dev-nanobot/c69bfd1d-97a6-43e3-9d5a-a517c28d382c/scratchpad/imp/g`. Nothing references them.

## Responses to findings

Round 1: none.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance item and the gate was run after the change in a fresh `.venv` and printed exactly the THEN output, and a control run showed the overlay's `uv.lock` setting is what keeps the suite at 70 passed.
ESCALATIONS: none
