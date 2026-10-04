Type: chore (harness efficiency)

Title: Role commands drop an inherited VIRTUAL_ENV, and build checkouts start with a synced environment

Summary:
Two problems hit role runs, which are the agents the harness dispatches: implementer, reviewer and verifier. First, the shell each role runs in inherits `VIRTUAL_ENV` (and possibly `PYTHONHOME`) from the session that launched the factory. Second, a fresh build checkout has no `.venv`. A build checkout is the implementer's git worktree or a checker's detached checkout. Because of this, each role in turn discovers that `uv run --no-sync` acceptance commands build an empty environment and fail on imports. A checker can then mistake that import failure for a code failure. The requester wants three things:
- (A) The running-code wrapper unsets `VIRTUAL_ENV` and `PYTHONHOME` for every command it wraps. That wrapper is the `(export HOME=<throwaway>; <command>)` line every role is told to use, and it also wraps the gate commands.
- (B) An optional instance setting, `environment_sync:`, gives a command the harness runs once in each new build checkout, with `VIRTUAL_ENV` unset, before the role starts. If the setting is absent, behaviour stays as it is today.
- (C) When that sync has run, the role input says the environment is already synced, so roles do not sync again.
No check, gate command or acceptance criterion changes.

Evidence:
- Nanobot instance, run-0259-implementer (T-0022.1, 2026-10-04), at `~/dev/nanobot-upstream/.factory/state/runs/run-0259-implementer/output.md`. Line 59 says: "The worktree had no `.venv`, and the shell inherits `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` from blue. As written, an acceptance command with `uv run --no-sync` in a fresh worktree makes an empty env and fails on imports (`No module named 'loguru'`, `No module named pytest`). I ran `uv sync --all-extras --dev` in the worktree." Line 15 says the implementer reran everything after syncing and unsetting `VIRTUAL_ENV`. So the implementer lost a full attempt to this problem before getting real results.
- This repo shows the same inherited value. I ran `grep -rl VIRTUAL_ENV .factory/state/runs/*/output.md` and it matched 24 role runs across T-0012.x, T-0013.1, T-0019.1, T-0023.4 and T-0024.1. In run-0060-verifier (T-0012.1), line 3 says uv printed "does not match the project environment path `.venv` and will be ignored", and that "the PR worktree had no `.venv` before `suite.sh` ran". run-0216-verifier (T-0023.4), line 20, reports the same warning. I found no output for the T-0015 runs that the request cites. The other citations hold.
- The code as built today, which I read and did not run:
  - `factory/compose.py:74-78`: `wrap()` exports HOME and the `run_env` values and unsets nothing. `run_env` is the instance's map of extra variables for the wrapper to export.
  - `factory/compose.py:57-71`: `run_env` accepts only name-to-value pairs, so it has no way to unset a variable.
  - `factory/cli.py:246-262`: worktree and checkout setup copies `environment_files` and runs no command.
  - `factory/instance.template.yaml` and `.factory/instance.yaml` have no `environment_sync` key.
  So a new criterion for A or B would fail on this checkout today, which means it would prove something.
- The request gives no Nanobot-side harness commit. `grep -rn -E "VIRTUAL_ENV|environment_sync|PYTHONHOME"` over `~/dev/nanobot-upstream/.factory` turned up only notes in plans and specs, not a fix. There is no as-built fix to copy, so this is new work.
- Duplicate search: I grepped the open and closed tickets, requests and specs in `.factory/state`, plus `dev/issues.md`, for `VIRTUAL_ENV`, `environment_sync`, `PYTHONHOME` and `uv sync`. The only match was this request (T-0031). There is no duplicate.
- Operator, 2026-10-04: "efficiency first; pre-approved." The request's gate line puts it in the pre-approved class because it removes repeated discovery work and changes no check.

Assumptions (my inferences, not stated by the requester):
- The harness runs the sync command through the same wrapper as role commands: a throwaway HOME, the `run_env` exports, and `VIRTUAL_ENV`/`PYTHONHOME` unset. The protected-path rule requires this. On the Nanobot instance it also keeps the uv cache that `run_env` already points to.
- "Once at setup" means once each time the harness creates a checkout. An implementer re-dispatched to an existing worktree (`cli.py:249`, `if not wt.exists()`) does not need to sync again unless the spec writer finds the lock can change between rounds.
- If the sync fails, the run does not start, and the run is reported with a reason that names the sync. The request does not say this. The spec writer should state the behaviour so that a failed sync does not reach a checker as a code failure, which is the failure this ticket exists to remove.
- On this instance, the `gate_commands` use `uv run --frozen`, which syncs by itself. So the import failure is mainly a Nanobot problem (`--no-sync`), and here part A only removes the warning. Whether this repo's own `.factory/instance.yaml` sets `environment_sync` is up to the spec. Setting it touches the protected `infra` path, and the spec's Risk section must declare that.
- The change touches `factory/**` (the protected `harness` path) and the design doc. It needs a changelog entry, a consistent `dev/build-harness.spec.md`, any re-copied `docs/prompts/` block, and a README update if a configuration key is documented there.
- Suggested priority: soon. This is only a suggestion. The operator asked for efficiency first, and every Nanobot v3.5 build pays this cost.

Reason: The intent is clear and the operator pre-approved it on 2026-10-04. No product decision is open. The open details (failure handling, re-dispatch, whether this instance opts in) are spec-level and are listed under Assumptions for the spec writer.

STATUS: ACCEPT
CONFIDENCE: high. I confirmed the evidence in both stores, read the setup and wrapper code, and found no duplicate. Only the T-0015 citation did not check out.
ESCALATIONS: none
