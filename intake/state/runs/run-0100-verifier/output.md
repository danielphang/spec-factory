Commit: 2d86d96440218508f3f7ba8bf66d5987458d71a7

How run: I made two fresh `git clone --no-local` copies of `~/dev/spec-factory` in a scratch directory, one detached at head `2d86d96` and one at base `600b8d4`. In both, local `main` was set to `600b8d4`. Each ran `uv sync --frozen` first (`uvsync=0`). The shell was bash, with `VIRTUAL_ENV` unset (the parent shell had it pointing at another repo's venv), along with `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `FACTORY_INTEGRATION_BRANCH`. A script pulled every WHEN from the input (the parent scenarios' `- WHEN` lines and the intermediate checks), so nothing was retyped. For the parent scenarios I used `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, the `parent_base` in `intake/state/tickets/T-0012.yaml`. Head's merge-base with `main` is now `600b8d4` itself: the head is merge `2d86d96`, with parents `3d5afc0` and `600b8d4`. `git status --porcelain` was empty after every run on both clones.

Per criterion:

| Label | Criterion | Base `600b8d4` | PR `2d86d96` | Result |
|---|---|---|---|---|
| NEW | intake-holds-only-live-store | `left=168` | `left=0` | PASS |
| NEW | pilot-store-and-answers-kept-byte-identical | `kept=0 of 135` | `kept=135 of 135` | PASS (note 1) |
| NEW | instance-b-opens-every-ticket | `tickets=0 failed=0` | `tickets=18 failed=0` | PASS |
| NEW | instance-b-config | `no instance config` / `context=` | `True True True` / `context=3` | PASS |
| NEW | readme-has-install-and-layout | 5 `missing:` lines (git clone, uv sync, factory init, factory paths, .factory/), then `checked` | `checked` | PASS |
| REGRESSION | no-old-paths-in-live-files | `exit=1` | `exit=1` | PASS |
| NEW | lock-is-base-revision | `head: .factory/harness.lock: No such file or directory` / `lock=stale` / `harness_paths_changed=0` | `lock=current` / `harness_paths_changed=0` | PASS |
| NEW | instance-b-keys | `FileNotFoundError … '.factory/instance.yaml'`, then `TypeError` (`instance` is null) | `False [] intake/state True` / `True True` | PASS |
| NEW | records-moved-as-pure-renames | `0` / `pilot=0 of 148 answers=0 of 14` | `0` / `pilot=148 of 148 answers=14 of 14` | PASS |
| REGRESSION | live-store-untouched | `0` | `0` | PASS |
| REGRESSION | role-prompt-text-unchanged | `changed=0 of 14` | `changed=0 of 14` | PASS |
| REGRESSION | harness-files-in-repo | `agents=6 green_only=0` | `agents=6 green_only=0` | PASS |
| REGRESSION | harness-history-carried | `0` | `0` | PASS |
| REGRESSION | docs-moved-and-split | `old_tracked=0` | `old_tracked=0` | PASS |
| REGRESSION | changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` | same | PASS |
| REGRESSION | design-text-kept | `0` | `0` | PASS |
| REGRESSION | prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` | same | PASS |
| REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `116 passed in 104.09s (0:01:44)` | `sync=0` / `116 passed in 104.18s (0:01:44)` | PASS |
| REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS |
| REGRESSION | whitespace (sub-ticket diff): `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS |

Every NEW criterion fails on base for the reason the spec gives: the `.factory/` files and the moves do not exist yet. Every NEW criterion passes on the PR. In records-moved-as-pure-renames, the first line (`0`) is the same on both sides, but the criterion still fails on base on its second line.

Note 1: the THEN says `kept=134 of 134`, with both numbers equal. The parent base `cdb1c67` already has 135 distinct contents. The extra one is `intake/answers/T-0012-gate-edit.md`, added at the parent base after the spec's "today" (`f082708`). The real condition, both numbers equal, holds. This is count drift, not a defect. It is unchanged from round 1.

Gate suite: PASS
Run in `/Users/dphang/dev/spec-factory/intake/state/runs/run-0100-verifier/wt` at head `2d86d96`, with `VIRTUAL_ENV` and `FACTORY_*` unset, after `uv sync --frozen` (exit 0):
- `git diff --check main...HEAD` → exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `116 passed in 125.74s (0:02:05)`, exit 0.
- `git status --porcelain` was empty before and after.

Probes:
1. **The merge commit's scope.** Command: `git diff --name-only 3d5afc0 2d86d96 | grep -v '^intake/state/' | wc -l` → `0`. `git merge-base --is-ancestor main HEAD` → yes. Round 2's own change is `git diff --name-only 302f70b 3d5afc0`, which gives exactly `.factory/README.md`, `.factory/context.md` and `README.md`. → OK
2. **Diff shape against `main`.** Command: `git diff -M --name-status main...HEAD`. Result: 162 `R100` entries; `R062 intake/instance/config.yaml → .factory/instance.yaml`; `A .factory/{README.md,context.md,harness.lock}`; `M README.md`; `D intake/{HARNESS_PIN,README.md,instance/context.md,instance/preamble.md,setup.sh}`. Nothing under `intake/state/**`, `factory/`, `agents/`, `tests/` or `docs/`. With `-c diff.renames=false`, `git diff --check` flags 7 files, which matches the ticket's prediction for the pilot records. → OK
3. **Lock after the main merge.** `.factory/harness.lock` is `010d1b00c5835c7022a72771c63f63f8b6ab3707`. The harness revision (`git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`) gives the same SHA at HEAD and at `main`. → OK
4. **Lock edge inputs** (a copy of `.factory/` via `FACTORY_INSTANCE`, with `FACTORY_REPO=$PWD`, running `ticket show T-0012`):
   - all-zero lock → exit 2 with `harness 010d1b0… is not the revision this instance accepted (0000…); rerun with --accept-harness 010d1b0… to accept it`;
   - empty lock file → exit 2 with `(none)`;
   - correct SHA with no trailing newline → exit 0.
   → OK
5. **Dirty harness, with and without `--accept-harness`.** I appended a line to `factory/__init__.py` in the head clone.
   - `bin/factory ticket show T-0012` → exit 2, `… has uncommitted changes:` / `factory/__init__.py`.
   - `bin/factory --accept-harness <rev> ticket show T-0012` → exit 2, same message.
   - After `git checkout factory/__init__.py` → exit 0.

   The new `README.md` text ("`--accept-harness` does not clear that, so commit or discard the edits first") and the new `.factory/README.md` sentence match this behaviour, which closes my round-1 ESCALATION 1. → OK
6. **Walk-up and new text.**
   - `../bin/factory ticket show T-0012` run from `docs/` → exit 0.
   - `git grep -nE '[^/a-z_]prompts/|^prompts/' -- README.md .factory/README.md .factory/context.md .factory/instance.yaml` → rc=1, so no bare `prompts/`.
   - The new Output paragraph in `.factory/context.md` (lines 43-47) is word for word the Output paragraph of `factory/context.template.md` (line 17 on). It is not one of the two paragraphs E.2 says to keep (acceptance commands, design-doc conventions).

   → OK

STATUS: VERIFIED
CONFIDENCE: high. All 20 acceptance commands were extracted verbatim and run on fresh clones of head and base, and they gave the expected NEW/REGRESSION pattern. Both gates ran in the given worktree and exited 0. The probes confirm the lock, the dirty-harness refusal and the corrected wording on the merged head.
ESCALATIONS:
1. Protected path `intake/**` (infra) is touched, as the sub-ticket declares: `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed; `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/`; `intake/state/**` and `intake/.gitignore` are not changed by the branch's own commits. The merge gate needs the human approval that this declaration implies.
2. For the record: the pilot count is 135, not the THEN's 134 (note 1). The "both numbers equal" condition holds.
