Commit: 372a47c8831d3a988f8cb7ae5759b15d4ad73632 (branch `factory/T-0012.1`, base `cdb1c6769ecc39208e62edc65578f62f5a23908f`; reviewed in `intake/state/runs/run-0059-reviewer/wt`, which `git status --porcelain --ignored` shows clean apart from `!! .venv/`)

Round 1.

## What I checked, in the role's order

1. **Test integrity.** No existing test in this repo (none existed at base). `tests/factory/**` arrives as 75 new files, and the sub-ticket's byte check (`import-byte-identical`) run by me prints `differ=0 of 69` against green at G = `7c0a0353d3d0759f0942ab2ab96395aff8f70f29`; that set includes every `tests/factory/*.py` and fixture. `git ls-files factory bin/factory tests/factory agents` has no file outside green's set. `bin/factory` keeps mode `100755`. Nothing weakened, skipped or rewritten.

2. **Correctness against A.1–A.6.**
   - A.1/A.2: imported history reachable from the filtered tip `6b8370d` is 31 commits, 28 non-merge (`git rev-list --count [--no-merges] 6b8370d`). Every path in that history is under `factory/`, `bin/factory`, `tests/factory/` or `agents/factory-*` (`git log 6b8370d --name-only --format= | sort -u` filtered to anything else prints nothing). `scripts/full_suite_gate.py` never appears. The three green-only files appear in history only, as the spec allows (Decisions, "may appear in the imported history").
   - A.3: `097fb01` is a true two-parent merge (`cdb1c67` + `6b8370d`); `git diff-tree -r 6b8370d 097fb01 -- factory bin/factory tests/factory agents` is empty and `git diff-tree --name-status cdb1c67 097fb01` is 72 `A`, so the merge added green's tree unaltered and changed nothing of `main`'s.
   - A.4 (`dd375f5`): touches only the three overlay paths. `cmp` shows `context.md` and `preamble.md` identical to `intake/instance/*`; `diff intake/instance/config.yaml factory/config.yaml` is exactly `5c5 state_dir: ../state → intake/state` and `26c26 environment_files: [] → ["uv.lock"]`. Against green's config the overlay differs only in the per-repo header, `repo_name`, `state_dir`, `request_dir`, `protected_paths`, `gate_commands`, `integration_branch` and `environment_files`; `placeholders`, `max_rounds`, `models`, `ready_state` and `routing` (the keys the imported tests read) are green's. Preamble differs from green's and from `prompts/00-preamble.md` on lines 1 and 38 only.
   - A.5 (`372a47c`): `pyproject.toml` is the spec's eleven lines verbatim; `.gitignore` is the three required entries; `uv lock --check` → `lock=0`; the lock resolves pyyaml 6.0.3 and pytest 9.1.1 with cp311 wheels present, so `requires-python >=3.11` is honoured.
   - A.6: from a deleted `.venv`, `env -u VIRTUAL_ENV uv sync --frozen` → `sync=0`; `PYTHONDONTWRITEBYTECODE=1 uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `70 passed in 111.57s`. `uv run --frozen python -c 'import sys,yaml;…'` printed this worktree's `.venv`, `6.0.3`, `3.12.13`, so the run used the branch's own fresh environment.
   - Sub-ticket acceptance, all run by me: harness-history-carried `0`; harness-files-in-repo (interim) `agents=6 green_only=2`; role-prompt-text-unchanged (interim) `changed=1 of 14`, the 1 being the preamble (`docs/prompts/00-preamble.md` does not exist on this branch, and the overlay preamble differs from `prompts/00-preamble.md` on lines 1 and 38 anyway, as the ticket predicts); overlay-is-this-repo's-instance `overlay=same` / `intake/state ['uv.lock']` / no `gate_script_present`; project-files only `lock=0`; cut-anchor-still-valid `0` with green HEAD `7c0a035` = G; green-harness-still-present `green keeps its harness` and porcelain count `0`; gate `git diff --check main...HEAD` → `exit=0`.

3. **Scope.** `git diff --name-only main...HEAD` outside the import set is exactly `.gitignore`, `pyproject.toml`, `uv.lock`. Nothing under `intake/`, `docs/`, `dev/`, `.factory/`. No behaviour code was edited (B, C untouched).

4. **Silent behaviour changes.** The only one is the spec-mandated interim: `factory/config.yaml:5` `state_dir: intake/state` resolves through `store.REPO_ROOT / cfg["state_dir"]` (`factory/store.py:15,41`) to the live store of whichever checkout `bin/factory` runs from, with no lock until part C. The implementer reports it under Known gaps; the spec (A.4) asks for exactly this value. See NIT 2 below for a related hazard.

5. **Security / data safety.** No secrets in the diff (`uv.lock` holds only PyPI URLs and hashes). `~/.nanobot/` not referenced. Nothing destructive.

6. **Protected / guardrail paths.** `reference_harness ~/dev/nanobot-upstream/**`: read-only use declared by the sub-ticket; confirmed unwritten (`git -C ~/dev/nanobot-upstream status --porcelain -- factory bin/factory tests/factory .claude/agents | wc -l` → `0`, green HEAD still G). Guardrail paths: agent prompts (`agents/factory-*.md`, `factory/prompts/*.md`) and tests arrive as new files byte-identical to green, as the parent's Risk declares. `intake/**` and `prompts/**` untouched. Listed under ESCALATIONS as declared.

7. **Maintainability.** Nothing beyond the NITs.

## Findings

- [NIT] `097fb01` (merge commit subject): `Merge /private/tmp/claude-501/…/scratchpad/imp/g into factory/T-0012.1` → a throwaway scratch path becomes a permanent subject on `main`, and the subject does not say what was imported. The ticket prescribes `--no-edit`, so this is the command's output, not a deviation; an amend of the merge message (not a rebase) would fix it without linearising history. Not blocking.
- [NIT] `factory/config.yaml:26` `environment_files: ["uv.lock"]` plus `factory/gitops.py:68-79` `copy_environment_files` (overwrites `dest/uv.lock` from the integration checkout) → if anyone drives a ticket in this repo through the in-repo `bin/factory` before T-0012.6, a branch that changes `uv.lock` is tested with `main`'s lock. The parent already names this (E.1 sets `[]` for that reason) and A.4 requires `["uv.lock"]` so the suite passes, so this is spec-intended interim state; the operator should keep using `intake/harness/` until E, as the implementer says.

## Prior findings

None (round 1).

## Out-of-scope observations

- `factory/config.yaml:1-3,13` keeps `intake/instance/config.yaml`'s header comments (`intake/setup.sh`, `HARNESS_PIN`, "No test suite exists here until #19 part A") and `request_dir: ../../issues`. They would match the parent scenario no-old-paths-in-live-files, but T-0012.3 deletes the file; nothing to do here.
- The lock pins pytest 9.1.1 and Python was 3.12.13 at resolution; the suite was run only on 3.12 (by the implementer and by me).

STATUS: APPROVE
CONFIDENCE: high. Every sub-ticket acceptance item, the suite (70 passed from a fresh `.venv`) and the gate were re-run by me in the review worktree and matched the THEN values; the byte and history checks are mechanical and green was confirmed unmodified.
ESCALATIONS: declared protected/guardrail paths involved, per sub-ticket and parent Risk: reference_harness `~/dev/nanobot-upstream/**` (read only, cloned to scratch; confirmed unchanged); agent prompts `agents/factory-*.md` and `factory/prompts/*.md` and tests `tests/factory/**` added as new files byte-identical to green. No undeclared protected path touched.
