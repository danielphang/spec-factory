Sub-ticket: T-0023.4 (plan seam T-0023-S3, "Store and instance setup"), parent T-0023 approved spec v2 (issue #39). Branch `factory/T-0023.4`, one commit `3bf4577` on base `cf6e2bc`, in worktree `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0023.4`.

## What changed

This fixes three harness defects in how a store and an instance are set up. The store is the folder where the factory keeps a ticket's records. An instance is a target repository's `.factory/` directory: its settings, its briefing and its store. Before this change, run records failed `git diff --check`. `init` on a throwaway store left half an instance. A relative path in a `FACTORY_*` variable was resolved against the harness's own checkout.

**Part C (H3): run records are exempt from whitespace checks.** Run records copy diffs and agent output verbatim, so `git diff --check` over store commits reported their trailing spaces.
- C1, `factory/store.py`: adds `STORE_GITATTRIBUTES`, which is one comment line plus `runs/** -whitespace`, and `ensure_gitattributes(root)`. It has the same semantics as `ensure_gitignore`. Both now call one private helper, `_ensure_block(path, block)`, which holds the body `ensure_gitignore` had (coding rule 1: reuse over a second copy).
- C2, `factory/cli.py`: `init_cmd` calls it beside `ensure_gitignore`, and lists `.gitattributes` first in `written` when it was absent. `run_start` calls it beside its `ensure_gitignore` call, after every refusal of `run start`.

**Part E (H6): no half instance, and a missing briefing refuses.**
- E1, `init_cmd`: when `instance.yaml` does not exist, it builds the text and parses it in memory. It then computes the store in use. If that store is not the instance's own, `init` refuses with exit 2 before any write. The message uses the spec's wording and names `FACTORY_STATE` and the store. The docstring now says this.
- E2, `factory/compose.py` `compose`: it refuses with `store.Refused` (exit 2) when `<instance>/context.md` is not a file. The message uses the spec's wording. `run_compose` writes `input.md` only after `compose` returns, so nothing is written.

**Part F (H7): relative environment paths resolve from the caller's directory.**
- F1, `factory/instance.py`: adds `env_path(name)`. It returns None when the variable is unset or empty. Otherwise it applies `expanduser()` and joins a relative path onto `caller_cwd()`, which is `FACTORY_CWD`, else the working directory. An absolute path is resolved as given and never consults the working directory.
- F2: `env_path` replaces the five raw reads: `instance.find` and `init_cmd` for `FACTORY_INSTANCE`, `instance.repo_root` for `FACTORY_REPO`, and `instance.state_root` and `store.state_root` for `FACTORY_STATE`. `not_found_message` still quotes the raw value. The module docstring of `factory/instance.py` says relative values come from the caller's directory. Removing those reads left `import os` unused in `cli.py` and `store.py`, so both imports are dropped. Ruff reported them as F401.

**J1, J3 and J4 (documents).**
- `docs/changelog.md` entry 51 gains the S3 clause from J1, on the same line.
- `README.md`, "How the harness finds a target": appends J3's sentence verbatim. I also added one sentence before it: "`FACTORY_STATE` names a store to use instead, and `FACTORY_REPO` a repo root." `FACTORY_REPO` appeared nowhere else in the README, and `FACTORY_STATE` is first explained further down. The README's own "Reader first" rule asks for a gloss at first use (writing rule 2).
- J4: the status-header date already reads 2026-10-04, which is today's date, so it is unchanged.

Callers of each function this diff changes, from `grep -rn` over `factory/` and `bin/`:
- `store.ensure_gitignore`: `cli.py` `run_start` (:221), `_start_build_run` (:243) and `init_cmd` (:888). Its behaviour is unchanged, and the existing `.gitignore` tests in `tests/factory/test_run_scratch.py` pass.
- `instance.find`: `require`, and `paths_cmd` (:905).
- `instance.repo_root`: `gitops.repo_root`, `own_state_root` and `init_cmd`.
- `instance.state_root`: `store.state_root`, `init_cmd` and `paths_cmd`.
- `store.state_root`: `cli.main` (:1201).

The fix sits in these shared resolvers, so every command gets it. No caller was changed.

## Acceptance results

Each command ran verbatim through the wrapper from the worktree root. The GIVEN block was written once with `TMPDIR` set to this run's scratch directory.

| Scenario | Kind | Before (base `cf6e2bc`) | After (`3bf4577`) |
|---|---|---|---|
| Run records in a store pass whitespace checks and other store files do not | NEW | `runs=2`, `other=2` | `runs=0`, `other=2` |
| A run start adds the whitespace rule to an existing store | NEW | `rule=0` | `rule=1` |
| init refuses to create an instance on a throwaway store and writes nothing | NEW | `exit=0 instance=written store=written names_state=0` | `exit=2 instance=none store=none names_state=1` |
| A missing briefing refuses the compose with exit 2 | NEW | `exit=1 input=none names_context=1` | `exit=2 input=none names_context=1` |
| Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory | NEW | `state=0 instance=0 repo=0` | `state=1 instance=1 repo=1` |
| An absolute FACTORY_STATE is used as given | REGRESSION | `absolute=1` | `absolute=1` |
| The README says relative paths resolve from the caller's directory | NEW | `0` | `1` |
| The changelog records the change in order | NEW | `51 CONTIGUOUS`, `6` | `51 CONTIGUOUS`, `9` |
| Intermediate check, the new test file passes | NEW | `no tests ran`, exit 4 (no file) | `13 passed`, exit 0 |
| The harness suite passes with an uncommitted harness edit | REGRESSION | not run | `254 passed in 201.75s (0:03:21)` |
| The change adds no whitespace errors | REGRESSION | not run | `exit=0` |

What the "after" results show:
- `runs=0`, `other=2`: a committed run record no longer fails the check, but a store file outside `runs/` still does.
- `exit=2 … store=none`: `init` on a throwaway store now writes neither an instance nor the store.
- The missing-briefing compose now exits 2 with a refusal instead of exit 1 from an uncaught `FileNotFoundError`. No `input.md` is written.
- `51 CONTIGUOUS`, `9`: entry 51 now holds all nine required words, and the numbering has no gap.
- `254 passed`: the full suite, including the new file, passes in a clone that has an uncommitted edit to `factory/status.py`.

Before the change, entry 51 already existed with the clauses of the three earlier seams, so the changelog check printed `6`.

Gates, each run exactly as written from the worktree:
- `(export HOME=…; git diff --check main...HEAD)`: no output, exit 0. `main` is at `cf6e2bc`, the base.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `254 passed in 193.60s (0:03:13)`.

## Tests added/changed

- Added `tests/factory/test_store_setup.py`, 13 cases, all black-box through `bin/factory`. Each case uses a throwaway store or the lock-exempt `init` and `paths` commands, so the file passes mid-edit.
  - C3, five cases: `init` writes the rule and lists `.gitattributes` first, and a second `init` writes nothing; `run start` adds the rule to a store without one; an existing file with no final newline keeps its lines and gains the rule once; an existing rule is not duplicated; `git diff --check` exempts a committed `runs/` record but still reports `store/notes.md`.
  - E3, three cases: the `init` refusal, with its message and no writes in the target or the store; `init` with `FACTORY_STATE` naming the instance's own store still creates the instance; the compose refusal, with its message, no traceback and no `input.md`.
  - F3, five cases: relative `FACTORY_STATE`, `FACTORY_INSTANCE` and `FACTORY_REPO` through `paths`; an absolute `FACTORY_STATE` from `/`; `init` finding an instance through a relative `FACTORY_INSTANCE`. The last case covers `init_cmd`'s own read of the variable, which `paths` does not reach.
- Before the fix, 11 of the 13 failed. Two passed: "an existing rule is not duplicated" and "an absolute FACTORY_STATE is used as given". Both are regression guards with nothing to fix on the base.
- No existing test changed.

## Known gaps and uncertainties

- After a refused compose, the run stays `running`, and the ticket keeps it in `in_flight`. The old crash left the same state. E2 asks only for the refusal, so I did not add a cleanup.
- The E1 refusal checks only the store in use. A `FACTORY_INSTANCE` naming a directory that has no instance yet, combined with `FACTORY_STATE` elsewhere, is refused the same way. That is the rule as specified.
- `env_path` resolves `FACTORY_CWD` through `caller_cwd()` only for a relative value. An absolute value behaves exactly as before.
- I extracted `_ensure_block` from `ensure_gitignore` rather than copying its body. The existing `.gitignore` tests in `tests/factory/test_run_scratch.py` cover it, and they pass.
- The README gloss sentence goes beyond J3's verbatim text, for the reason given above.
- No store's `.gitattributes` is committed. The parent's Operator steps leave that to the operator after the runtime moves.
- factory: markers added: none.
- Lint: ruff is not a gate here. `ruff check factory tests/factory/test_store_setup.py` prints `All checks passed!`.

## Out-of-scope observations

- Relative file arguments still resolve against the harness checkout, which is the same class of defect as H7. One example is `ticket new --file rel.md`: `bin/factory` changes directory first, so `Path(a.file)` at `factory/cli.py:60` resolves against the harness. The same holds for `--output-file` (:294), `--file` (:345, :405, :1024), `--output` (:489), `--edit` (:655) and `--answer` (:744). The workflows pass absolute paths, so they are not affected.
- `/tmp/t0023-suite.g5G5PW`, timestamped 08:28 today, was left by an earlier run of the suite scenario. My run started later and removed its own directory. I did not delete it.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command and both gates were run on `3bf4577` and printed the expected output; the only judgment calls are the `_ensure_block` extraction and the one-sentence README gloss.
ESCALATIONS: none
