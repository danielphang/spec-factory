Commit: 302f70bb99f5c4518ddb94de12db22653aa57385

How run: two fresh `git clone --no-local` copies of `~/dev/spec-factory` in a scratch directory. One was detached at head `302f70b` and one at base `600b8d4`, with local `main` set to `600b8d4` in both. Each ran `uv sync --frozen` (`uvsync=0`) first. The environment had `VIRTUAL_ENV`, `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `FACTORY_INTEGRATION_BRANCH` unset. For the parent scenarios, `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, the `parent_base` in `intake/state/tickets/T-0012.yaml`. Every WHEN was pulled from the input by a script that matched lines starting `- WHEN \``. Nothing was retyped. The gate commands ran in the given worktree.

Note on base: `main` = `600b8d4` is one commit ahead of the branch's merge-base `f4be7ec`. `git diff --name-only f4be7ec 600b8d4 | grep -v '^intake/state/'` prints nothing, so the extra commit only touches the store. `main...HEAD` uses `f4be7ec`.

## Per criterion

| Label | Criterion | Base `600b8d4` | PR `302f70b` | Result |
|---|---|---|---|---|
| NEW | intake-holds-only-live-store | `left=168` | `left=0` | PASS |
| NEW | pilot-store-and-answers-kept-byte-identical | `kept=0 of 135` | `kept=135 of 135` | PASS (see note 1) |
| NEW | instance-b-opens-every-ticket | `tickets=0 failed=0` | `tickets=18 failed=0` | PASS |
| NEW | instance-b-config | `no instance config` / `context=` | `True True True` / `context=3` | PASS |
| NEW | readme-has-install-and-layout | `missing:` for git clone, uv sync, factory init, factory paths, .factory/, then `checked` | `checked` | PASS |
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
| REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `116 passed in 85.96s` | `sync=0` / `116 passed in 85.10s` | PASS |
| REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS |
| REGRESSION | whitespace (sub-ticket diff): `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS |

Each NEW criterion fails on base for the reason the spec gives (the files and moves do not exist yet) and passes on the PR. For records-moved-as-pure-renames, the first line (`0`) is the same on both sides. The criterion still fails on base, on its second line.

Note 1: the THEN reads `kept=134 of 134, both numbers equal`. At the parent base `cdb1c67` there are already 135 distinct contents, and at `f082708` (the spec's "today") there are 134. The one added is `intake/answers/T-0012-gate-edit.md`, from `git diff --stat f082708 cdb1c67 -- intake/green-pilot intake/answers`. The THEN's real condition, both numbers equal, holds. This is count drift from the gate edit, not a defect.

## Gate suite: PASS

From `/Users/dphang/dev/spec-factory/intake/state/runs/run-0094-verifier/wt` (head `302f70b`):
- `git diff --check main...HEAD` exits 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gives `116 passed in 101.19s (0:01:41)` and exits 0.
- `git status --porcelain` is empty afterwards.

## Probes

1. **Each moved record checked path by path.** The 162 files under `intake/green-pilot` and `intake/answers` at merge-base `f4be7ec` were each compared with `HEAD:.factory/<same subpath>`. Result: `n=162 bad=0`, and 0 files under `.factory/{green-pilot,answers}` lack a source. → OK
2. **Diff shape.** `git diff -M --name-status main...HEAD` gives:
   - 163 R entries. All are R100 except one: `intake/instance/config.yaml → .factory/instance.yaml`, which shows as R062 only because git's rename detection pairs the old file with the new one.
   - 3 A: `.factory/{README.md,context.md,harness.lock}`.
   - 5 D: `HARNESS_PIN`, `intake/README.md`, `instance/context.md`, `instance/preamble.md`, `setup.sh`.
   - 1 M: `README.md`.

   After the change, `intake/` tracks only `intake/.gitignore` and `intake/state/**` (452 files). → OK
3. **`instance.yaml` compared key by key with the old config (yaml load).**
   - The only keys that differ are `repo_name`, `harness` (added), `state_dir`, `protected_paths`, `gate_commands` and `request_dir` (dropped), exactly the keys E.1 names. `environment_files` was already `[]`.
   - Key order is preserved apart from where `harness` was inserted.
   - The header comments no longer name `setup.sh` or `HARNESS_PIN`.

   → OK
4. **The lock file and the revision.** `.factory/harness.lock` is a single line: 40 hex characters and a newline (`010d1b00c5835c7022a72771c63f63f8b6ab3707`). It equals the harness revision both at `f4be7ec` and at `main` `600b8d4`. → OK
5. **Instance B's behaviour, run in the scratch head clone (throwaway store).**
   - **(a) Walk-up.** `../bin/factory ticket show T-0012` from `docs/` exits 0.
   - **(b) Preamble.** On a new throwaway ticket (`T-0013`), `run start --role triage` writes a `system-prompt.txt`:
     - line 1 is `You are one agent in a software pipeline: spec-factory (the design repo at ~/dev/spec-factory, branch main). Other agents check`;
     - 0 placeholders are left;
     - line 38 is `infra (.factory/**, intake/**), harness (factory/**, bin/factory, agents/**, pyproject.toml, uv.lock), generated (docs/prompts/**), reference_harness (~/dev/nanobot-upstream/**), credentials (~/.nanobot/**)`.
   - **(c) Compose.** `run compose` exits 0, and `input.md` begins with `.factory/context.md`.
   - **(d) Lock mismatch.** With an all-zero lock, `ticket show T-0012` exits 2 with `harness 010d1b0… is not the revision this instance accepted (0000…); rerun with --accept-harness …`.
   - **(e) Dirty harness.** After appending a line to `factory/__init__.py`, `ticket show` exits 2 with `has uncommitted changes:` / `factory/__init__.py`.
   - **(f) Restored.** With both restored, the command exits 0.

   So `tickets=18 failed=0` really passed the lock, not just walked past it. → OK
6. **The rewritten text.**
   - Bare `prompts/` (`[^/a-z_]prompts/|^prompts/`) does not appear in `.factory/context.md`, `README.md` or `.factory/README.md` (rc=1). No old paths appear in `.factory/README.md` either, which is outside the gate pathspec.
   - `context.md` names each item E.2 requires: `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, `dev/`, the harness paths and the test command, the two checkouts, and green as read-only.
   - `README.md` has each E.6 item: clone, `uv sync`, `init --repo-name`, "Restart the Claude Code session", `context.md` and `gate_commands`, `paths`, `scriptPath` with `{ticket, repo, instance}`, `approve-spec`, the layout table, and the update model.

   → OK, with one CONCERN on wording (see ESCALATIONS 1).
7. **`--accept-harness` with a dirty harness.** `bin/factory --accept-harness <rev> ticket show T-0012` with `factory/__init__.py` edited exits 2 with the uncommitted-changes error. Per C.4 that is correct. But `README.md` says targets refuse "uncommitted edits to the harness's code, until you run a command with `--accept-harness <sha>`", which suggests the flag clears it. → CONCERN (wording only, outside the criteria)

STATUS: VERIFIED
CONFIDENCE: high. All 20 acceptance commands were extracted verbatim, run on fresh clones at both head and base, and gave the expected NEW and REGRESSION pattern; both gates were run in the worktree and exited 0; the probes confirm the lock and the instance resolution really work on instance B.
ESCALATIONS:
1. `README.md` "How updates work" says targets refuse "uncommitted edits to the harness's code, until you run a command with `--accept-harness <sha>`". Probe 7 shows `--accept-harness` does not clear that refusal, which is correct per parent C.4. The sentence follows E.6's own wording, so the parent spec text is ambiguous here too. It should be a later doc fix, not a FAIL.
2. Head `302f70b` does not contain `main` `600b8d4`. The gap is one commit, and it touches only `intake/state/`. If the merge step requires the head to contain `main` (as in the `.4`/`.5` conflict runs), a main merge into `factory/T-0012.6` comes first. That merge must keep `.factory/harness.lock` current, which it will, since `600b8d4` touches no harness path.
3. For the record: the pilot count is 135, not the THEN's 134. The cause is `intake/answers/T-0012-gate-edit.md`, added at the parent base. The "both numbers equal" condition holds.
