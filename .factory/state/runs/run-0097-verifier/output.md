Commit: 3d5afc012b5a22fed48de58e7af9c8206c7c9fff

How run: two fresh `git clone --no-local` copies of `~/dev/spec-factory` in a scratch directory (`<scratchpad>/v97/{head,base}`). `head` was detached at `3d5afc0`, `base` at `600b8d4`, and local `main` was set to `600b8d4` in both. Each ran `uv sync --frozen` first (`head uvsync=0`, `base uvsync=0`). Every command ran under bash with `VIRTUAL_ENV`, `VIRTUAL_ENV_PROMPT`, `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `FACTORY_INTEGRATION_BRANCH` unset. `VIRTUAL_ENV` was set in my shell (to `~/dev/nanobot/.venv-test`), so I removed it explicitly. For the parent scenarios I used `BASE=cdb1c6769ecc39208e62edc65578f62f5a23908f`, the `parent_base` at `intake/state/tickets/T-0012.yaml:74`. A script pulled all 20 commands from `input.md`: the parent `#### Scenario` WHEN lines, the intermediate `- WHEN` lines and the whitespace command. Nothing was retyped.

Note on base: the branch's merge-base with `main` is `f4be7ec`, and `main` is `600b8d4`, one commit further on. That commit touches only `intake/state/**`. `main...HEAD` uses `f4be7ec`. Since round 1 (`302f70b`), only `.factory/README.md`, `.factory/context.md` and `README.md` changed (`git diff --name-only 302f70b HEAD`, 10 insertions and 6 deletions).

Per criterion:

| Label | Criterion | Base `600b8d4` | PR `3d5afc0` | Result |
|---|---|---|---|---|
| NEW | intake-holds-only-live-store | `left=168` | `left=0` | PASS |
| NEW | pilot-store-and-answers-kept-byte-identical | `kept=0 of 135` | `kept=135 of 135` | PASS (note 1) |
| NEW | instance-b-opens-every-ticket | `tickets=0 failed=0` | `tickets=18 failed=0` | PASS |
| NEW | instance-b-config | `no instance config` / `context=` | `True True True` / `context=3` | PASS |
| NEW | readme-has-install-and-layout | five `missing:` lines (git clone, uv sync, factory init, factory paths, .factory/), then `checked` | `checked` | PASS |
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
| REGRESSION | harness-suite-passes-after-uv-sync | `sync=0` / `116 passed in 127.19s (0:02:07)` | `sync=0` / `116 passed in 131.56s (0:02:11)` | PASS |
| REGRESSION | green-harness-still-present | `green keeps its harness` | same | PASS |
| REGRESSION | whitespace (sub-ticket diff): `git diff --check main...HEAD; echo "exit=$?"` | `exit=0` | `exit=0` | PASS |

Every NEW criterion fails on base for the reason the spec gives: the `.factory/` files, the README text and the moves do not exist yet. Every NEW criterion passes on the PR. For records-moved-as-pure-renames, the first line (`0`) is the same on both sides, but the criterion still fails on base on its second line. Every REGRESSION criterion passes on both sides.

Note 1: the THEN says `kept=134 of 134, both numbers equal`. The parent base `cdb1c67` already holds 135 distinct contents, because `intake/answers/T-0012-gate-edit.md` was added there (round 1, from `git diff --stat f082708 cdb1c67`). The THEN's actual condition, both numbers equal, holds. The count drifted; this is not a defect in the PR.

Gate suite: PASS
- Run from `/Users/dphang/dev/spec-factory/intake/state/runs/run-0097-verifier/wt` (HEAD `3d5afc0`), with `VIRTUAL_ENV` unset.
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `116 passed in 109.87s (0:01:49)`, exit 0. I ran it under bash to capture the exit code. An earlier run under zsh also gave `116 passed in 112.88s`.
- `git status --porcelain` in the worktree is empty afterwards.

Probes:
1. **The round-2 README claim, checked against behaviour.** On the head clone I appended `# probe` to `factory/__init__.py`, then ran `bin/factory --accept-harness 010d1b00c5835c7022a72771c63f63f8b6ab3707 ticket show T-0012` → exit 2, stderr `harness <clone> has uncommitted changes:` / `factory/__init__.py`. The new text in `README.md` and `.factory/README.md` ("`--accept-harness` does not clear that, so commit or discard the edits first") now matches parent C.4 and the code. Restored with `git checkout`. → OK
2. **The briefing's Output paragraph (`.factory/context.md`).** The new sentences are the wording of `factory/context.template.md:19-20`: "every role but the implementer … The implementer also changes files in its own worktree and commits there". The acceptance-command and design-doc-convention paragraphs that E.2 says to keep are not touched by the round-2 diff. → OK
3. **Lock file variants** (copies of `.factory/` used through `FACTORY_INSTANCE`, with `FACTORY_REPO` set to the clone):
   - empty lock → exit 2, `… accepted (none); rerun with --accept-harness …`;
   - a 7-character prefix of the revision → exit 2;
   - the revision with no trailing newline → exit 0;
   - the revision with leading and trailing spaces → exit 0.

   The comparison strips whitespace (C.2 says "stripped first line") and does not accept a prefix. So the passing instance-b-opens-every-ticket is not special-cased to the committed lock bytes. → OK
4. **Walk-up and merge.** `../bin/factory ticket show T-0012` run from `dev/` → exit 0. A `--no-ff` merge of `3d5afc0` into a local copy of `main` `600b8d4` is clean (`merge=0`). On the merged tree the lock is still `lock=current`, `tickets=18 failed=0` and `left=0`. The lock (`010d1b0…`) equals the harness revision at `main` too. → OK
5. **Stale paths in the rewritten text.** I grepped `README.md`, `.factory/README.md`, `.factory/context.md` and `.factory/instance.yaml`:
   - for a bare `prompts/` (`[^/a-z_]prompts/|^prompts/`) → no match (rc=1);
   - for `HARNESS_PIN`, `intake/setup.sh`, `docs/spec-factory.md` and `issues/README.md` → no match (rc=1).

   `.factory/README.md` is outside the gate's pathspec. → OK

STATUS: VERIFIED
CONFIDENCE: high. All 20 acceptance commands were extracted verbatim and run on fresh clones at head and base, and gave the expected NEW and REGRESSION pattern. Both gate commands were run as written in the given worktree and exited 0. The probes show the round-2 text matches the code's behaviour, and the lock and instance resolution work on inputs near the tested ones.
ESCALATIONS:
1. Protected path `intake/**` (infra) is touched exactly as the sub-ticket declares, unchanged since round 1:
   - `intake/README.md`, `setup.sh`, `HARNESS_PIN` and `instance/*` are removed;
   - `intake/answers/` and `intake/green-pilot/` are pure renames to `.factory/` (the `-M100% --diff-filter=AD` count is `0`);
   - `intake/state/**` and `intake/.gitignore` are untouched (`live-store-untouched` is `0`).

   The merge gate needs the human approval that this declaration implies.
2. Head `3d5afc0` still does not contain `main` `600b8d4`. That commit touches only `intake/state/**`, a trial merge is clean, and the lock stays current after it (probe 4). If the merge step requires the head to contain `main`, a main merge comes first.
3. For the record: the pilot count is 135, not the THEN's 134 (note 1). The "both numbers equal" condition holds.
