Commit: da50576fd4215aa31d4d8091e089c8f50cb791e5 (branch `factory/T-0031.2`, base `2bd99697e3bdbe0ae735294afae1b3109070d7c6`)

How it ran. Each checkout got `uv sync --frozen` (exit 0) and then the parent's GIVEN fixture block, written once. All of this ran through the running-code wrapper, with a fresh HOME and `TMPDIR` set to this run's scratch directory. I copied the scenario commands into `scratch/acc.sh`. To confirm the copy was exact, I extracted the WHEN lines from `input.md` and diffed them against the file: no difference. I also diffed the GIVEN block against the spec's text, and the sub-ticket's four inline commands against the parent's: no difference in either. The calling shell had a real inherited `VIRTUAL_ENV` (`/Users/dphang/dev/nanobot/.venv-test`). The base ran in a detached worktree at `2bd9969` under scratch, which I removed afterwards. Raw output is in `scratch/acc-pr.txt` and `scratch/acc-base.txt`.

Per criterion:
- NEW | wrapper and wrapped gate drop the inherited venv (S1) | base: two lines `ve=<T31>/venv ph=<T31>/venv fake_python=1 cache=/tmp/t31-cache home=fresh` | PR: two lines `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh` | PASS
- NEW | implementer synced at every dispatch (S2) | base: `first: synced=no ve= venv_on_path=0 cache=0 home=fresh noted=0` / `again: synced=no` | PR: `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1` / `again: synced=yes` | PASS
- NEW | checker synced (S3) | base: `synced=no ve= venv_on_path=0 noted=0` | PR: `synced=yes ve=0 venv_on_path=0 noted=1` | PASS
- NEW | failed sync refuses (S4) | base: `implementer: exit=0 named=0 code=0 shell_chars=0 logged=0` / `reviewer: exit=0 named=0 code=0 shell_chars=0 logged=0` / `in_flight=0 checker_checkouts=1 meta=2` | PR: `implementer: exit=2 named=1 code=1 shell_chars=0 logged=1` / `reviewer: exit=2 named=1 code=1 shell_chars=0 logged=1` / `in_flight=1 checker_checkouts=0 meta=0` | PASS
- REGRESSION | without environment_sync (S5) | base: not run | PR: `started=yes noted=0 recorded=0 files=0` | PASS
- NEW | documents name the sync and the venv, no prompt copy changes (S6) | base: `design=0 design_venv=0 build_spec=0 template=0 readme=0 readme_venv=0 prompts=0` | PR: `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0` | PASS
- NEW | changelog's last entry (S7) | base: `CONTIGUOUS` / `0` | PR: `CONTIGUOUS` / `4` | PASS
- REGRESSION | `(git diff --check main...HEAD; echo "exit=$?")` | base: not run | PR: `exit=0` | PASS
- REGRESSION (intermediate) | `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | base: not run | PR: `496 passed in 310.48s` | PASS (this is also the gate run below)

Every NEW criterion fails on the base exactly as the parent's verification.md "today" lines say, and passes on the PR.

Gate suite: PASS
- `(export HOME=...; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: exit 0, `496 passed in 310.48s (0:05:10)`.

Scope checks:
- `git diff --stat 2bd9969...HEAD` shows 10 files.
- The existing tests changed are only `tests/factory/test_run_isolation.py` (the `WRAP` constant) and `tests/factory/test_gate_paths.py` (the `want` line). Each matches the parent's prototype text. Between them they have 6 changed `+`/`-` lines.
- The protected paths touched are `factory/compose.py`, `factory/cli.py` and `factory/instance.template.yaml`. All three are declared in the spec's Risk line.
- Nothing under `docs/prompts/` or `factory/prompts/` changed.

Probes (scripts: `scratch/probe_wrap.sh`, `scratch/probe_sync.sh`):
- Wrapper from `compose.wrap` under sh, bash, zsh and dash, with `VIRTUAL_ENV="/tmp/my venv"`, its `bin` repeated twice in `PATH`, plus a `.../bin/` trailing-slash entry → every exact `/tmp/my venv/bin` entry is removed, the trailing-slash entry stays (exact match, by design), and both variables are unset. → OK
- `VIRTUAL_ENV=""` → `PATH` is unchanged and the variables are unset. With no venv and a trailing empty `PATH` entry → `PATH` is unchanged. With a venv and an empty middle entry (`/usr/bin::/bin:/v/bin`) → `/usr/bin::/bin`, so the empty entry is kept and only the venv bin is removed. → OK
- `environment_sync: '   '` (whitespace only) → exit 2, `environment_sync must be one shell command ...`, no worktree and no run directory. → OK
- A sync that prints 20000 lines to stdout and to stderr and succeeds → run start's stdout is one line, that line is the JSON `run_id` line, and stderr is empty. → OK
- The same sync but `exit 7` → the refusal is one line. The log has 40004 lines, `exit: 7`, and the output in full. → OK
- A failed sync (`exit 4`) at the parent-close verifier → exit 2 with the one-line refusal. The run directory holds only `environment-sync.log`, there is no `/runs/` checkout, no `meta.yaml`, and nothing is in flight. → OK
- A sync command that itself contains a backtick (``echo `true` >/dev/null``) → the "Environment:" input line puts it inside backticks unescaped, so the inline code breaks in the rendered input. This is cosmetic, and only for operator-chosen commands that contain backticks. It is outside the criteria. → CONCERN (minor, not a FAIL)

Notes on the PR description's stated deviations (checked, not failures):
- `environment_sync(cfg)` is also called in `run_start` before the run id is reserved, so a malformed value leaves no run directory. The whitespace probe confirmed this.
- The build-spec addition is an indented sub-item of I.3, not a renumbered I.4. S6 only checks that `environment_sync` is named, and the renumbering concern is reasonable.

STATUS: VERIFIED
CONFIDENCE: high. All nine acceptance commands ran verbatim on the PR head and printed the expected output. Every NEW one failed on the base as the spec predicts, both gates passed, and the probes found no special-casing.
ESCALATIONS: none
