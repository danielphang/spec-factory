### ST-1 / Role commands drop an inherited VIRTUAL_ENV, and build checkouts start with a synced environment
Depends on: none
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0031/v3.md` (T-0031, approved spec v3). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: every lettered part of the parent's Proposed change, A to F.

Notes for the implementer: `main` has moved since the spec was checked at `b002c95` (T-0027 merged). The code the spec names is unchanged, but its line numbers have moved. Re-locate it before you edit. Lines checked on `main` at `2bd9969`:
- `wrap()` and `run_env()`: `factory/compose.py:147-168`.
- The "Where you work" block: `factory/compose.py:343-354`. The SKIPPED lines are at 352 and `parts.append(where)` is at 354.
- `_start_build_run()`: `factory/cli.py:361-392`.
- The `meta.yaml` write is at `factory/cli.py:227` and the in-flight append at 238. Both still come after `_start_build_run` returns at 226.

The changelog's last entry is now 65, so this change appends 66, the next free number, as part F allows.

Acceptance:
Run each item from the repository root of the checkout under test, after `uv sync --frozen`. Use the GIVEN fixture block of the first scenario, written once, exactly as the parent spec gives it.
- NEW. A role's wrapper and its wrapped gate command drop an inherited virtual environment.
  WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && for c in "$(wrapper $S/runs/$R/input.md ". $T31/probe.sh")" "$(gate $S/runs/$R/input.md)"; do VIRTUAL_ENV=$V PYTHONHOME=$V PATH=$V/bin:$PATH sh -c "$c"; done)`
  THEN it prints exactly two lines, each `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh`.
- NEW. An implementer's worktree is synced through the wrapper at every dispatch, and its input says so.
  WHEN the parent's command for this scenario, verbatim (it sets `SYNC="'env > synced.env'"`, starts the implementer twice with a fake `VIRTUAL_ENV` on `PATH`, and finishes the first run with `--status-override KILLED` in between).
  THEN it prints exactly `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1`, then `again: synced=yes`.
- NEW. A checker's checkout is synced before the checker starts, and its input says so.
  WHEN the parent's command for this scenario, verbatim (a reviewer start on a commit on `factory/T-0001.1`).
  THEN it prints exactly `synced=yes ve=0 venv_on_path=0 noted=1`.
- NEW. A failed sync refuses the run start with a one-line reason, keeps its output in a log, and leaves no run or checker checkout.
  WHEN the parent's command for this scenario, verbatim (`SYNC="'echo sync-\$((1+1)) >&2; exit \$((2+1))'"`, then an implementer start and a reviewer start).
  THEN it prints exactly `implementer: exit=2 named=1 code=1 shell_chars=0 logged=1`, then `reviewer: exit=2 named=1 code=1 shell_chars=0 logged=1`, then `in_flight=1 checker_checkouts=0 meta=0`.
- REGRESSION. Without environment_sync, run start and the input are as before.
  WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && echo "started=$([ -n "$R" ] && echo yes || echo no) noted=$(grep -c 'already synced' $S/runs/$R/input.md) recorded=$(grep -c '^environment_sync:' $S/runs/$R/meta.yaml) files=$(git -C $S/worktrees/T-0001.1 status --porcelain --untracked-files=all | grep -c .)")`
  THEN it prints exactly `started=yes noted=0 recorded=0 files=0`.
- NEW. The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes.
  WHEN the parent's command for this scenario, verbatim.
  THEN it prints exactly `design=1 design_venv=1 build_spec=1 template=1 readme=1 readme_venv=1 prompts=0`.
- NEW. The changelog records the environment sync as its last entry.
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e environment_sync -e VIRTUAL_ENV -e PYTHONHOME -e 'already synced' | sort -u | grep -c .)`
  THEN it prints `CONTIGUOUS`, then `4`.
- REGRESSION. The environment-sync change adds no whitespace errors.
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`.
- Intermediate check, REGRESSION. The harness suite passes with the two listed test edits and the new `tests/factory/test_environment_sync.py`, and with no other existing test changed.
  WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
  THEN it reports no failures.

Interim tests: none

Tests to change: the parent's list, and nothing else:
- `tests/factory/test_run_isolation.py`: the `WRAP` constant (line 22) only. It gains the part A prefix, as the parent gives it.
- `tests/factory/test_gate_paths.py`: the `want` line (line 217) only, in `test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does`. It gains the part A prefix, as the parent gives it.

Protected paths: `factory/compose.py`, `factory/cli.py`, `factory/instance.template.yaml` (the parent's whole Risk list).

Out of scope:
- Setting `environment_sync` on either instance (Operator steps).
- Anything on T-0031.1's v2 branch.
- `build.js` park-reason quoting.
- Other leak paths, such as `PYTHONPATH` and `CONDA_PREFIX`.
- A time limit on the sync.
- Any prompt copy under `docs/prompts/` or `factory/prompts/`.

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The spec's design asks for one PR of about 225 lines with one changelog entry. Its parts depend on each other through the same code and tests. Part A (the wrapper prefix) is what makes the sync's environment clean in part C, and the sync scenarios check both at once (`ve=0 venv_on_path=0`). Parts B to D share `factory/compose.py` and `factory/cli.py` and one new test file. Part F writes one changelog entry for A to D. Splitting A from B–D would need two changelog entries or a document part that waits on both, and two serial merges on the same two files. That adds a re-verify round and makes neither review nor rollback easier.

This plan supersedes T-0031.1, which was planned from v2 and is parked. Its branch `factory/T-0031.1` holds one commit (`f13e707`) built to v2. The new sub-ticket does not depend on it and does not build on that branch.
