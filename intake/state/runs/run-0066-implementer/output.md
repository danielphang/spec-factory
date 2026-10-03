Sub-ticket: T-0012.3 (`intake/state/specs/T-0012.3/subticket.md`; parent `intake/state/specs/T-0012/v3.md`). Branch `factory/T-0012.3`, one commit `f5d820346e2ed3edd2b8d160f280dc02d74d57f1` on base `51ea76c`.

## What changed (per lettered part)

**B.1 Resolver.** New `factory/instance.py` (117 lines).
- `find()` takes `FACTORY_INSTANCE` if it is set and holds `instance.yaml`. Otherwise it walks up from the caller's directory to the nearest `.factory/instance.yaml`.
- `bin/factory` now runs `export FACTORY_CWD="$PWD"` before its `cd "$HERE"`, so the package knows the caller's directory. Without that variable it falls back to `os.getcwd()`.
- `require()` raises `Refused` with `no .factory/instance.yaml found from <cwd>; run factory init --repo-name NAME, or set FACTORY_INSTANCE`.
- `cli.main` runs `store.load_config()` (which now calls the resolver) inside the `try`, so the refusal exits 2 before anything is written. `init` and `paths` skip that step.
- There is no fallback: `store.REPO_ROOT` and `store.CONFIG_PATH` are deleted.

**B.2 Where things come from.**
- `instance.load_config` reads `<instance>/instance.yaml`.
- `instance.repo_root` is `FACTORY_REPO`, else the instance directory's parent. `gitops.repo_root` now delegates to it; its docstring is updated.
- `store.state_root` is `FACTORY_STATE`, else `<repo root>/<state_dir>`.
- `FACTORY_INTEGRATION_BRANCH` is unchanged.

**B.3 Briefing.** `compose.compose` opens `input.md` with `<instance>/context.md`. `factory/prompts/context.md` is deleted.

**B.4 Preamble.**
- `factory/prompts/preamble.md` is now a byte copy of `docs/prompts/00-preamble.md`.
- `run start` calls `instance.fill_preamble`. It replaces `{repo name}` with `repo_name`, and replaces the exact line `  {auth, payments, migrations, infra, public API, dependencies}` with `  <class> (<glob>, <glob>), …` built from `protected_paths`.
- The seven role prompts are untouched.

**B.5 `factory init [--repo-name NAME]`** (`cli.init_cmd`).
- It exits 2 outside a git work tree. The instance is `FACTORY_INSTANCE` if set, else `.factory/` at the git top level.
- If `instance.yaml` is missing, it needs `--repo-name` (otherwise exit 2, nothing written). It then writes `instance.yaml` from the new `factory/instance.template.yaml`, filling `repo_name` and `harness` (the absolute path of the running checkout).
- Then, only when the store in use is the instance's own (see gap 1), it creates whichever of these is missing:
  - `context.md`, from the new `factory/context.template.md`;
  - `harness.lock`, holding the C.1 revision;
  - `<repo root>/.claude/agents/factory-*.md`, copied from `agents/`. If any agent file is written, it prints `restart the session so the agents register` to stderr.
- After that it does today's store init (`specstore.init`), plus the store `.gitignore` (`store.ensure_gitignore`).
- Idempotent: it logs `store.initialised` only when it wrote something.
- The template carries today's generic keys, with `integration_branch: null` and `environment_files: []`. It has no `request_dir`.

**B.6 `factory paths`** (`cli.paths_cmd`) prints one JSON object with:
- the absolute paths `harness` (the running checkout), `bin`, `intake_workflow` and `build_workflow`;
- `harness_revision`;
- `instance` and `state`, which are `null` when no instance is found.

It runs no check and writes nothing.

**C.1 only.** `instance.harness_revision()` is `git -C <running checkout> log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock`, and returns None outside git. `init` (lock) and `paths` use it. No lock enforcement (C.2–C.5).

**B.7 Agent pointers.** In `agents/factory-{triage,spec-writer,spec-critic,planner}.md`, the single pointer line is replaced with the spec's text. Nothing else in `agents/` changes.

**B.8 Workflows.** `intake.js` and `build.js` take `instance`.
- When it is given, every store command is prefixed with `FACTORY_INSTANCE=<instance>`.
- `state` is optional. When it is absent, `STATE` is taken from `factory config`'s `state_dir`, which is the absolute store path. If `config` fails, the workflow returns an error.
- `repo` stays the harness checkout. The header comments are updated.

**B.9 Tests.**
- New `tests/factory/conftest.py` sets `FACTORY_INSTANCE` to the new `tests/factory/fixtures/instance/`, and sets `FACTORY_REPO` to the harness checkout unless it is already set.
- The fixture's `instance.yaml` is the template values plus `environment_files: ["uv.lock"]` and `gate_commands: ["git diff --check main...HEAD"]`. It also has a `context.md`.
- New `tests/factory/test_instance.py` has 22 tests.
- Part A's interim `factory/config.yaml` is deleted. Git's rename detection shows it as renamed to the fixture; `--no-renames` shows a delete and an add.

**Also:** the one-line docstring in `factory/__init__.py` named the deleted `factory/config.yaml`; it now names `factory/instance.py` and the template.

## Acceptance results

Run from the worktree, after `uv sync --frozen` (`sync=0`), with `BASE=cdb1c67…` (the parent's recorded `parent_base`).
- **Before** = base `51ea76c`.
- **After** = the working tree before commit, re-run verbatim on head `f5d8203`. The results are the same.

Commands were extracted from the input file by a script, not retyped.

| Criterion | Before | After |
|---|---|---|
| harness-files-in-repo (NEW) | `agents=6 green_only=2` | `agents=6 green_only=0` |
| role-prompt-text-unchanged (NEW) | `changed=1 of 14` | `changed=0 of 14` |
| init-creates-instance-in-throwaway-target (NEW) | `init=2` / `instance=[] agents=0 restart=0` | `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1` |
| store-command-from-subdirectory-uses-target-instance (NEW) | `init=2` / `new=0 tickets=[] harness_changes=4` | `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0` |
| command-outside-any-instance-refused (NEW) | `exit=0 created=0 names_instance=0` | `exit=2 created=0 names_instance=1` |
| factory-instance-override-from-elsewhere (NEW) | `init=2` / `found=0` | `init=0` / `found=1` |
| composed-input-opens-with-instance-context (NEW) | `init=2` / `first=[]` | `init=0` / `first=[CTX-MARKER for demo]` |
| run-system-prompt-names-instance (NEW) | `init=2` / `line1=[] placeholders= protects_instance=` | `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1` |
| paths-name-harness-workflows-and-instance (NEW) | `init=2` / `no paths` | `init=0` / `True True True True` |
| init-refusals-and-idempotence (NEW) | `outside_git=2` / `no_name=0` / `again=0 same=yes` (`find: .factory: No such file…`: nothing was created) | `outside_git=2` / `no_name=2` / `again=0 same=yes` |
| agent-pointer-replaced (NEW) | four lines `old=1 new=0` | four lines `old=0 new=1` |
| workflows-take-instance (NEW) | `intake 0` / `build 0` | `intake 2` / `build 1` |
| no-old-paths, documents and harness (NEW) | `exit=0` (`factory/config.yaml` 3 lines, `factory/prompts/context.md` 6, `factory/prompts/preamble.md:38`) | `exit=1` |
| harness-history-carried (REGRESSION) | `0` | `0` |
| harness-suite-passes-after-uv-sync (REGRESSION) | `sync=0`, `70 passed in 69.68s` | `sync=0`, `92 passed in 71.28s (0:01:11)` |
| docs-moved-and-split (REGRESSION) | `old_tracked=0` | `old_tracked=0` |
| prompt-copies-moved-unchanged (REGRESSION) | `changed=0 of 10 VERBATIM` | `changed=0 of 10 VERBATIM` |
| green-harness-still-present (REGRESSION) | `green keeps its harness` | `green keeps its harness` |
| whitespace, sub-ticket diff (REGRESSION) | `exit=0` | `exit=0` |

Every NEW criterion failed before and passes after. Every REGRESSION passed before and after.

**Gates on head `f5d8203`, run exactly as written from the worktree:**
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` gave `92 passed in 81.46s` (70 imported + 22 new).
- `git status --porcelain` was empty afterwards, so the suite and the acceptance runs wrote nothing into the checkout.

**Before merge: every imported test runs on a throwaway store.** `grep -n 'str(BIN)' tests/factory/test_*.py` finds five subprocess helpers: `test_p0_cli.py:22`, `test_results_commit.py:37`, `test_shepherd.py:629`, `test_spec_store.py:20` and `test_subtickets.py:72`. Each builds its env with `"FACTORY_STATE": str(<tmp store>)`. `test_killed_checker.py` imports `built_to_implementer` from `test_shepherd` and has no subprocess helper of its own.

**Workflows (B.8):** the check here is structural only, plus a stub smoke run that is not a test in the repo.
- I wrapped each script as a function and ran it in node 24 with a fake `agent`. The clerk commands came out as `FACTORY_INSTANCE=/T/.factory /H/bin/factory config` (with `instance`), `FACTORY_STATE=/S /H/bin/factory …` (with `state`) and `FACTORY_INSTANCE=… FACTORY_REPO=/X …` (build with `target`).
- With only `instance` given, the role prompt read `/T/.factory/state/runs/run-0001-x/system-prompt.txt`, which is `STATE` taken from `config`.
- `node --check` passes on both scripts.
- End-to-end behaviour is exercised only by operator step 3 after close. I am not claiming more than that.

## Tests added/changed

- **Existing tests:** none changed. `git diff --name-status --no-renames main...HEAD -- tests/` lists only `A` entries. Nothing under `docs/` changed, and none of the seven role prompts changed.
- **`tests/factory/conftest.py` (new):** B.9, as specified.
- **`tests/factory/fixtures/instance/{instance.yaml,context.md}` (new):** B.9.
- **`tests/factory/test_instance.py` (new, 22 tests).** It covers:
  - `init`:
    - it creates the instance at the git top level from a nested subdirectory;
    - `instance.yaml` matches the template's keys and values;
    - a repo name with YAML special characters round-trips;
    - it refuses outside git, and refuses without `--repo-name`, writing nothing;
    - it is idempotent byte for byte, and recreates only the missing pieces;
    - on a throwaway store it initialises only that store;
    - under the suite's conftest env it writes nothing into the fixture or the harness checkout;
    - a nested repo gets its own instance.
  - The resolver:
    - a store command from a subdirectory uses the target's instance;
    - outside any instance it is refused with the exact message for `ticket show`, `ticket new` and `config`, and nothing is written;
    - `FACTORY_STATE` alone does not stand in for an instance;
    - the `FACTORY_INSTANCE` override works, and is refused when the directory has no `instance.yaml`;
    - the repo root is the instance's parent, and `FACTORY_REPO` and `FACTORY_STATE` override it and the store.
  - Compose: the input opens with the instance's `context.md`.
  - The preamble:
    - the system prompt equals the design block except the two filled lines, with the role prompt appended verbatim;
    - with several classes, the protected-path line lists every one;
    - `factory/prompts/preamble.md` is byte-identical to the design copy, and part A's overlay is gone.
  - `paths`, inside an instance and outside one, with the revision equal to `git log`.
  - The conftest points the suite at the fixture.
- **Watched fail:** I ran the new file against a scratch `git archive` copy of base `51ea76c` that had the conftest, fixture and templates added. The result was `9 failed, 2 passed, 10 errors` (the errors are the `target` fixture's `init`, which failed). The two that already pass on the old code are guard tests: suite-init-writes-nothing-into-harness and conftest-points-at-fixture. They pin the isolation, not new behaviour.

## Known gaps and uncertainties

1. **A reading the spec does not state: `init` writes the instance's pieces only when the store in use is the instance's own.** Those pieces are `context.md`, `harness.lock` and `.claude/agents/`. "Own store" uses C.2's condition: `FACTORY_STATE` unset, or resolving to `state_dir`.
   - Why: the imported tests run `factory init` with the conftest's `FACTORY_INSTANCE` (the fixture) and `FACTORY_REPO` (the harness checkout). A literal "today's init plus any missing pieces" would write `harness.lock` into `tests/factory/fixtures/instance/` and `.claude/agents/` into the harness checkout on every suite run.
   - With the reading, a throwaway-store `init` does exactly today's store init.
   - Pinned by `test_init_on_a_throwaway_store_initialises_only_that_store` and `test_the_suite_conftest_init_writes_nothing_into_the_harness`.
2. **`init` picks its instance from `FACTORY_INSTANCE`, else `<git top level>/.factory`, not by the walk-up.** This follows B.5 ("works at the git top level"), and it means a repo nested under another instance gets its own. Honouring `FACTORY_INSTANCE` is needed for the imported tests. If `FACTORY_INSTANCE` names a directory with no `instance.yaml`, `init --repo-name` creates it there.
3. **Today's `init` logged `store.initialised` on every call. It now logs only when something was written.** The scenario's `again=0 same=yes` checksums every file under `.factory/`, including the store's log, so it requires this. No existing test asserts on that event.
4. **`init` now writes the store's `.gitignore`** (B.5 lists it) and reports it as `".gitignore"` in `written`. Its JSON gains `instance`, `state`, `created` and `agents`.
5. **The restart line goes to stderr, so stdout keeps one JSON object.** The scenario counts it over stdout and stderr together (`restart=1`). `paths` JSON also carries `"ok": true`, which follows the CLI's convention.
6. **Choices the spec leaves open:**
   - `FACTORY_CWD` is the name I chose for the variable that hands over the caller's directory.
   - An empty `protected_paths` renders the line as `  none`.
   - `repo_name` and `harness` are written into the template as JSON-quoted strings, which YAML reads back exactly (tested with `:`, `"` and `#`). The fixture's `harness` is `null`; nothing in B reads that key.
7. **`factory/context.template.md` is my own wording.** It is a TODO stub listing what the briefing must state, ending with a generic "Output:" paragraph adapted from green's briefing. A reviewer may want different text.
8. **The workflows were checked only as described above.** They were not run end to end.
9. **Process disclosure, protected path.** My first baseline run of the acceptance commands on the old code wrote into this worktree's tracked copy of `intake/state/`: the old harness resolved its store next to its own code. It created `T-0013`, appended to `log/2026-10.jsonl` and `requests/index.yaml`, and added `openspec/` and `decisions.md`.
   - I reverted exactly those paths (`git checkout --` on the two files, `rm` on the four untracked paths) before making any change, and `git status` was clean afterwards.
   - The live store at `~/dev/spec-factory/intake/state` was not touched: its tickets end at `T-0012.yaml`.
   - That was the "today" failure mode `harness_changes=4`. After the change the same commands write only into their temp targets.

## Out-of-scope observations

- `ticket new --file` and `status parse` resolve a relative path against the harness checkout, because `bin/factory` changes into it. This is pre-existing, but now that operators run from target repos it will surprise them. Absolute paths work.
- `tests/factory/conftest.py` sets `FACTORY_REPO` only if it is unset, as B.9 specifies. When the suite runs as a gate from a process that already exports `FACTORY_REPO` (build.js with `target`), the imported tests inherit it. This is relevant to T-0012.6, which puts the suite in instance B's gate.
- `README.md` and `dev/build-harness.spec.md` still describe the old config location. They are rewritten in E and F.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command and both gates were run verbatim on head f5d8203 and printed the expected results. The two `init` readings (gaps 1–2) are the main thing for review.
ESCALATIONS: none
