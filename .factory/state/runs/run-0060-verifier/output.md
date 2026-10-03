Commit: 372a47c8831d3a988f8cb7ae5759b15d4ad73632 (branch `factory/T-0012.1`, worktree `/Users/dphang/dev/spec-factory/intake/state/runs/run-0060-verifier/wt`; `git status --porcelain --ignored` empty before the run, `!! .venv/` only after it). Base `cdb1c6769ecc39208e62edc65578f62f5a23908f` = `main` = merge-base, checked out detached in a scratch clone (`git clone --no-local` of `~/dev/spec-factory`, then `checkout --detach cdb1c67`). Green: `feat/lionbot-v3` = `7c0a0353d3d0759f0942ab2ab96395aff8f70f29` = G before and after the run.

How the commands were run: every WHEN was extracted verbatim from `input.md` by line number (lines 57, 60, 63, 66, 69, 388, 395, 402, 409, 588) with a Python script into `scratchpad/ver60/{fast,venv,suite,gate}.sh`, printed, eyeballed against the input, and executed with `bash` from each checkout's root. Shell inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test`; uv printed its "does not match the project environment path `.venv` and will be ignored" warning on stderr in the overlay item and used the worktree's own `.venv` (proof below). The PR worktree had no `.venv` before `suite.sh` ran, so `uv sync` built it fresh.

Per criterion (base `cdb1c67` → PR `372a47c`):

| Criterion | Kind | Command | Base | PR | Result |
|---|---|---|---|---|---|
| harness-history-carried | NEW [specs/harness-home, input.md:395] | `G=$(git -C ~/dev/nanobot-upstream log -1 … --grep='^Merge factory/T-0002.1' …); comm -23 <(green subjects) <(local subjects) \| wc -l` | `24` | `0` | PASS |
| harness-suite-passes-after-uv-sync | NEW [specs/harness-home, input.md:402] | `uv sync --frozen -q >/dev/null 2>&1; echo "sync=$?"; PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 \| tail -1` | `sync=2` / `no tests ran in 0.00s` | `sync=0` / `70 passed in 112.70s (0:01:52)` | PASS (N=70, no `failed`/`error`) |
| harness-files-in-repo, interim | NEW (intermediate) [input.md:388] | parent's harness-files-in-repo loop + `echo "agents=… green_only=…"` | ten `missing …` lines (`factory/cli.py` … `tests/factory/test_p0_cli.py`), then `agents=0 green_only=0` | only `agents=6 green_only=2` | PASS |
| role-prompt-text-unchanged, interim | NEW (intermediate) [input.md:409] | parent's 14-way cmp loop | `changed=14 of 14` | `changed=1 of 14` | PASS |
| import-byte-identical | NEW (intermediate) [input.md:57] | 69-file `cmp` against `G`, overlay paths excluded | `differ=69 of 69` | `differ=0 of 69` | PASS |
| overlay-is-this-repo's-instance | NEW (intermediate) [input.md:60] | `cmp -s factory/prompts/context.md intake/instance/context.md && cmp -s factory/prompts/preamble.md intake/instance/preamble.md && echo overlay=same; uv run --frozen python -c "…print(c['state_dir'], c['environment_files'])"; test -e scripts/full_suite_gate.py && echo gate_script_present` | no `overlay=same`; `FileNotFoundError: … 'factory/config.yaml'` | `overlay=same`, then `intake/state ['uv.lock']`, no `gate_script_present` | PASS |
| project-files | NEW (intermediate) [input.md:63] | `uv lock --check >/dev/null 2>&1; echo "lock=$?"; for s in .venv/ __pycache__/ .pytest_cache/; do grep -qxF "$s" .gitignore \|\| echo "missing $s"; done` | `lock=2`, `grep: .gitignore: No such file`, three `missing …` | only `lock=0` | PASS |
| cut-anchor-still-valid | NEW (intermediate; guard) [input.md:66] | `git -C ~/dev/nanobot-upstream log --oneline "$G"..feat/lionbot-v3 -- factory/prompts .claude/agents \| wc -l` | `0` | `0` | PASS as a guard (see ESCALATIONS: it checks green, not the branch, and the ticket states it prints `0` today) |
| green-harness-still-present | REGRESSION [specs/self-instance, input.md:588] + porcelain | `git -C ~/dev/nanobot-upstream cat-file -e feat/lionbot-v3:factory/cli.py && … && echo "green keeps its harness"`; `git -C ~/dev/nanobot-upstream status --porcelain -- factory bin/factory tests/factory .claude/agents \| wc -l` | `green keeps its harness` / `0` | `green keeps its harness` / `0` (also `0` after the suite ran) | PASS |
| whitespace (sub-ticket diff) | REGRESSION [input.md:69] | `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS |

Proof the suite ran on this tree in a fresh env: `uv run --frozen python -c 'import sys,yaml;print(sys.prefix, yaml.__version__)'` → `/Users/dphang/dev/spec-factory/intake/state/runs/run-0060-verifier/wt/.venv 6.0.3`; `pytest --co` → `70 tests collected`, `rootdir: /Users/dphang/dev/spec-factory/intake/state/runs/run-0060-verifier/wt`.

Gate suite: PASS. `git diff --check main...HEAD` from the worktree: no output, exit 0.

Probes:
- Overlay config shape → `diff intake/instance/config.yaml factory/config.yaml` prints exactly `5c5` (`state_dir: ../state` → `state_dir: intake/state`) and `26c26` (`environment_files: []` → `environment_files: ["uv.lock"]`); nothing else → OK (matches A.4).
- Overlay preamble vs green's preamble at G → differs on lines 1 and 38 only; vs `prompts/00-preamble.md` also lines 1 and 38 only, the same two lines `intake/instance/preamble.md` differs on. Overlay `context.md` and `config.yaml` are not green's (`cmp` → different) → OK: the 1 in `changed=1 of 14` is the preamble, as the ticket says.
- Agent templates, full-file `cmp` against `G:.claude/agents/*.md` without the `grep -v` filter → 0 of 6 differ → OK.
- File-set containment → `git diff --name-only main...HEAD`: 75 files, 0 outside `factory/**`, `bin/factory`, `tests/factory/**`, `agents/**`, `pyproject.toml`, `uv.lock`, `.gitignore`; `-- intake` → 0. Symmetric difference between green's 72 harness files at G (`.claude/agents/` renamed to `agents/`) and the PR's 72 under those paths → empty → OK.
- Imported history → the merge `097fb01` has parents `cdb1c67` and `6b8370d`; `6b8370d` carries 31 commits, 28 non-merge, tip subject = G's subject; branch has 2 root commits; paths touched in imported history outside the expected set → 0; `.claude/` paths left → 0; reverse `comm -13` (harness-path subjects here but not in green) → empty → OK.
- Mode bits → `bin/factory` is `100755` on both sides; `comm -3` over mode+path for all 69 compared files → 0 mismatches → OK.
- Whitespace of all added paths against the empty tree → exit 0 → OK.
- `uv.lock` → 8 packages, `pyyaml 6.0.3`, `pytest 9.1.1`, `requires-python = ">=3.11"` → OK.
- Control in a scratch `git archive` copy (not the PR): `test_shepherd.py::test_worktrees_get_the_integration_checkout_s_untracked_lockfile` → `1 passed` as shipped; with `environment_files: []` in that copy only → `1 failed`. PR worktree porcelain stayed `0`. → OK: the overlay's `uv.lock` line is live, not vestigial; the fix is not special-cased to the tested inputs.
- Green after everything: `status --porcelain` shows one line, ` M webui/package-lock.json`, mtime `2026-09-19 00:05:13` (two weeks before this run) and outside the criterion's pathspec → pre-existing, nothing written by this run → OK.

Not verified: the interpreter version uv picked for the worktree `.venv` (the suite passed on it; I did not print `sys.version`).

Out-of-scope observations:
- The import merge subject is `Merge /private/tmp/claude-501/…/scratchpad/imp/g into factory/T-0012.1` (1 commit matches `scratchpad`). Cosmetic, produced by the prescribed `--no-edit`.
- `factory/config.yaml` carries `intake/instance/config.yaml` verbatim except the two lines, so `state_dir: intake/state` makes `bin/factory` from the repo root address the live store with no lock until part C, and stale header text (`request_dir`, `HARNESS_PIN`, `intake/setup.sh` mentions) rides along. Per A.4 and deleted by B; not a criterion here.
- The overlay preamble's protected-path line does not name the harness code; E adds the `harness` class.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran as written under bash on both checkouts and printed exactly the THEN output (and the ticket's "today" output on base); the suite built its own `.venv` from nothing and collected 70 tests from this worktree; probes show the import is complete, mode-exact, path-contained, and the only hand-written deltas are the two config lines and the two preamble lines the ticket calls for.
ESCALATIONS: judgment call for the auditor, not a blocker: cut-anchor-still-valid is labelled NEW but prints `0` on base and PR alike, which the role rules call a SPEC-DEFECT when a NEW criterion passes on both. I did not apply that, because the item is declared as a guard on green's state ("Today it prints `0`"; "anything else means … escalate instead of merging") and it did its job; it cannot discriminate base from PR by design. Suggest the planner label such environmental guards as a precondition rather than NEW so the rule does not fire on them.
