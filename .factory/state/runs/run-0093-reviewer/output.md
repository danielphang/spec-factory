Commit: 302f70bb99f5c4518ddb94de12db22653aa57385 (branch `factory/T-0012.6`, one commit over base `f4be7ec826121021c2c247fba9ae56db68e658e9`; `main` in the worktree is that base)

## What I checked, in the role's order

1. **Test integrity.** `git diff --name-only main...HEAD -- tests/factory factory bin/factory agents pyproject.toml uv.lock` → `0` files. No test file, harness file or dependency lock is touched. `git diff --name-status -M100% main...HEAD | grep -v '^R100'` lists exactly 11 non-rename entries: 4 added under `.factory/` (`README.md`, `context.md`, `harness.lock`, `instance.yaml`), 1 modified (`README.md`), 6 deleted under `intake/` (`HARNESS_PIN`, `README.md`, `instance/{config.yaml,context.md,preamble.md}`, `setup.sh`). 162 entries are `R100` renames.

2. **Correctness against E.1–E.6.** I re-ran every acceptance command from the worktree root with `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` and `VIRTUAL_ENV` unset, after `uv sync --frozen`:
   - intake-holds-only-live-store → `left=0`.
   - pilot-store-and-answers-kept-byte-identical → `kept=135 of 135` with BASE = branch base, and the same with BASE = parent base `cdb1c67`. The drift from the spec's 134: `git diff --name-status f082708 f4be7ec -- intake/answers intake/green-pilot` shows one addition, `intake/answers/T-0012-gate-edit.md` (the parent's own gate edit, committed at `cdb1c67`); `f082708` has 134 distinct contents, `cdb1c67` and the base have 135. Both numbers equal, as the THEN requires.
   - instance-b-opens-every-ticket → `tickets=18 failed=0`, with `state` resolving to `<worktree>/intake/state`.
   - instance-b-config → `True True True`, `context=3`.
   - readme-has-install-and-layout → only `checked`.
   - no-old-paths-in-live-files → `exit=1` on HEAD. On the guard's purpose (Known gap 1): I ran the same patterns at `main` over the base's equivalent files and it matches `intake/instance/config.yaml:2` (`intake/setup.sh`), `:3` (`HARNESS_PIN`), `:9` (`generated: ["prompts/**"]`) and `intake/instance/preamble.md:38`. So the check passing at base was vacuous (`.factory/*` did not exist), the guard does bite on a straight copy, and the implementer's rewrite of the header and the `generated` glob is what makes it pass. Proceeding was right.
   - lock-is-base-revision → `lock=current`, `harness_paths_changed=0`. `.factory/harness.lock` = `010d1b00c5835c7022a72771c63f63f8b6ab3707` = `git log -1 --format=%H main -- factory bin/factory agents pyproject.toml uv.lock`.
   - instance-b-keys → `False [] intake/state True`, then `True True`.
   - records-moved-as-pure-renames → `0`, then `pilot=148 of 148 answers=14 of 14`.
   - live-store-untouched → `0`.
   - Regressions: role-prompt-text-unchanged `changed=0 of 14`; harness-files-in-repo `agents=6 green_only=0`; docs-moved-and-split `old_tracked=0`; green-harness-still-present prints `green keeps its harness`; harness-suite-passes-after-uv-sync `sync=0` then `116 passed in 132.99s`.
   - `git status --porcelain` is empty after all of the above, so the 18 `ticket show` calls wrote nothing to the tracked store.
   - **E.1 "every other key unchanged"**: a yaml key diff of `main:intake/instance/config.yaml` against `.factory/instance.yaml` gives removed `['request_dir']`, added `['harness']`, changed values `['repo_name', 'state_dir', 'protected_paths', 'gate_commands']` (`environment_files` was already `[]`; only its comment changed). The key set equals `factory/instance.template.yaml`'s key set exactly (missing: `[]`, extra: `[]`).
   - **Lock is enforced on this store, not skipped**: a copy of `.factory/` with an all-zero lock, run with `FACTORY_REPO=$PWD FACTORY_INSTANCE=<copy> bin/factory ticket show T-0001`, exits 2 with `harness 010d1b0… is not the revision this instance accepted (0000…); rerun with --accept-harness …`.
   - **README/briefing claims against the code**: `factory/cli.py:40` resolves `--file` with `Path(a.file).expanduser().resolve()` after `bin/factory:10` has done `cd "$HERE"`, so `README.md`'s "an absolute path" caveat is correct; `cli.py:1012` makes `request-changes --notes` required, matching step 6; `cli.py:786` prints `restart the session so the agents register`; `factory/workflows/intake.js:10-15` and `build.js:10,17` accept `instance`; `factory/store.py:next_run_id` allocates by atomic `mkdir`, so dropping "One ticket at a time: the store allocates run ids without a lock" from `.factory/README.md` is justified. `tests/factory/conftest.py:17-18` pins `FACTORY_INSTANCE` to the fixture and defaults `FACTORY_REPO`, which is why the suite stays off this repo's new `.factory/`.
   - E.2 content: `.factory/context.md` names `docs/design.md`+`docs/changelog.md` (l.5-6), `docs/prompts/` (l.7), `dev/` with its four files (l.9-11), the harness paths with the install and test commands (l.12-15), the two checkouts (l.20-25), green as instance A read only (l.27-30), and keeps the acceptance-command and design-doc-convention rules with updated paths (l.32-35). `README.md` carries all E.6 items (what, Install with `git clone`/`uv sync --frozen`, the six five-minute steps including `scriptPath` and `{ticket, repo, instance}` and `approve-spec`, the nine-row layout table, How updates work).

3. **Scope.** Nothing outside E.1–E.6 and the E.5 removals/moves. `README.md` is the only file outside `.factory/` and `intake/`, and E.6 asks for it.

4. **Silent behavior changes.** After merge, a `bin/factory` run from `~/dev/spec-factory`'s root finds instance B and is lock-checked against `intake/state`; that is the intent. `intake/setup.sh` is gone, so the gitignored `intake/harness/` copy that this parent's in-flight builds run on can no longer be rebuilt, but it is not deleted by this PR, and the parent's Risk section and operator step 2 already say it dies after close. Nothing else a caller would notice.

5. **Security and data safety.** No secrets, no destructive operations. `~/.nanobot/` not read. `~/dev/nanobot-upstream` read only by `git cat-file`/`git show`/`git log` in the acceptance commands.

6. **Protected paths.** `intake/**` (deletions and moves out) and `.factory/**` (new files) are both `infra`; both are declared in the sub-ticket's Protected paths. Listed under ESCALATIONS; the merge gate needs a human approval.

7. **Maintainability.** Nothing that will cause real problems.

## Findings

- [NIT] `.factory/context.md:43-45`: the Output paragraph still says the output file "is the only file you may create or modify" → every implementer run on instance B is briefed with a rule its role must break (it commits in its worktree). Pre-existing text, carried over because E.2 says to keep the existing rules; the implementer disclosed it (Known gap 6) and `factory/context.template.md` already has wording that fits the implementer. Not for this sub-ticket; a later briefing edit.

No BLOCKING or SHOULD-FIX findings.

## Out-of-scope observations

- The parent-level whitespace-clean scenario (`git diff --check cdb1c67 HEAD`) fails because of store run records committed on `main` under `intake/state/runs/`, as the implementer reports. That is a parent-close problem, not this diff: the sub-ticket's own `git diff --check main...HEAD` exits 0.
- `.factory/README.md:51-57` and `README.md:126-130` describe `~/dev/spec-factory-harness`, which operator step 2 creates. Until then the dev checkout's `bin/factory` is what runs (as instance-b-opens-every-ticket shows). E.1 requires the path, so this is expected, not a defect.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every gate and acceptance command was re-run on `302f70b` and gave the THEN output; the diff is 162 pure renames plus 11 files I read in full; the one judgment call (a NEW guard that passed vacuously at base) was checked and the guard bites on the copied text.
ESCALATIONS: protected paths touched, both declared in the sub-ticket: infra `intake/**` (`intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*` removed; `answers/` and `green-pilot/` moved out as 100% renames; `intake/state/**` and `intake/.gitignore` unchanged) and infra `.factory/**` (`instance.yaml`, `context.md`, `harness.lock`, `README.md` created; `answers/`, `green-pilot/` moved in). Human approval required at the merge gate.
