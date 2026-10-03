Commit: f5d820346e2ed3edd2b8d160f280dc02d74d57f1 (branch `factory/T-0012.3`, base 51ea76c94740462b299941d40bf8a431d07ee9ba; `git rev-parse HEAD` in the worktree)

## What I checked, in the role's order

1. **Test integrity.** `git diff --name-status --no-renames main...HEAD -- tests/ docs/ intake/` lists only `A tests/factory/conftest.py`, `A tests/factory/fixtures/instance/context.md`, `A tests/factory/fixtures/instance/instance.yaml`, `A tests/factory/test_instance.py`. No existing test file is modified; nothing under `docs/` or `intake/` changes. The four imported test modules that drive `bin/factory` build their env as `{**os.environ, "FACTORY_STATE": str(store), ...}` (`tests/factory/test_p0_cli.py:21`, `test_results_commit.py:36`, `test_spec_store.py:19`, `test_subtickets.py:71`); `test_shepherd.py:625-628` does the same and sets `FACTORY_REPO` to its scratch target. So the conftest's `FACTORY_INSTANCE`/`FACTORY_REPO` reach every subprocess, and every imported test still runs on a throwaway store. The one imported `init` assertion (`test_spec_store.py:151`, `written == []` on the second run) still holds under the new `init`.

2. **Correctness against B.1–B.9 and C.1.** Verified by reading `factory/instance.py`, `factory/cli.py` (`init_cmd`, `paths_cmd`, `main`, `run_start`), `factory/store.py`, `factory/compose.py`, `factory/gitops.py`, `bin/factory`, both workflows, and by running every acceptance scenario from the worktree with bash (`uv sync --frozen` → `sync=0`; `.venv/bin/python` present):
   - harness-files-in-repo → `agents=6 green_only=0`
   - role-prompt-text-unchanged → `changed=0 of 14`
   - init-creates-instance-in-throwaway-target → `init=0` / `instance=[context.md harness.lock instance.yaml state ] agents=6 restart=1`
   - store-command-from-subdirectory-uses-target-instance → `init=0` / `new=0 tickets=[T-0001.yaml] harness_changes=0`
   - command-outside-any-instance-refused → `exit=2 created=0 names_instance=1`; stderr is exactly the B.1 text with the cwd filled
   - factory-instance-override-from-elsewhere → `init=0` / `found=1`
   - composed-input-opens-with-instance-context → `init=0` / `first=[CTX-MARKER for demo]`
   - run-system-prompt-names-instance → `init=0` / `line1=[You are one agent in a software pipeline: demo. Other agents check] placeholders=0 protects_instance=1`; line 38 of the written prompt is `  infra (.factory/instance.yaml, .factory/harness.lock, .factory/context.md)`
   - paths-name-harness-workflows-and-instance → `init=0` / `True True True True`; `harness_revision` equals `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` in the worktree (both `f5d8203…`)
   - init-refusals-and-idempotence → `outside_git=2` / `no_name=2` / `again=0 same=yes`
   - agent-pointer-replaced → four lines `old=0 new=1`; `git diff --stat main...HEAD -- agents/` is 4 files, 1 line each
   - workflows-take-instance → `intake 2` / `build 1`
   - no-old-paths (`-- README.md docs dev agents factory`) → `exit=1`
   - harness-history-carried → `0`
   - `cmp factory/prompts/preamble.md docs/prompts/00-preamble.md` → identical; the only brace placeholders in that block are line 1 `{repo name}` and line 38, which `fill_preamble` handles (`factory/instance.py:103-116`).
   - `main` (`factory/cli.py:1037-1046`) dispatches `init`/`paths` before `store.load_config()`, so the refusal path writes nothing (confirmed: `created=0` above). `a.cmd` exists: `add_subparsers(dest="cmd", required=True)` at `cli.py:897`.
   - `config_cmd` (`cli.py:874-875`) prints `state_dir: str(root)`, the resolved absolute store, which is what the workflows read when `state` is omitted; `ENV`/`BIN` are fixed before that read in both scripts, so the omitted `FACTORY_STATE` is compensated by `FACTORY_INSTANCE`, and `STATE` is used only for run-directory paths (`intake.js:80,92,93`; `build.js:70,88,89`). `node --check factory/workflows/intake.js` exits 0.
   - The shepherd tests pass `FACTORY_STATE` = scratch store and `FACTORY_REPO` = scratch target, so `is_own_store` is false there and `init` writes nothing into the scratch target's `.factory/` or `.claude/` (by design; see NIT 1).

3. **Scope.** Every changed file is in B.1–B.9 / C.1 or the two deletions the sub-ticket names. The `factory/__init__.py` docstring edit replaces a reference to the deleted `factory/config.yaml`; adjacent and harmless.

4. **Silent behaviour changes.** Disclosed in the PR and checked: `init` logs `store.initialised` only when it wrote something (required by `again=0 same=yes`, which checksums the store log); `init` JSON gains `instance`, `state`, `created`, `agents`; `init` now writes the store `.gitignore` (B.5 lists it). No consumer of the event exists in `factory/` beyond the emitter (`grep -rn store.initialised factory/` → `cli.py:784` only).

5. **Security / data safety.** `_new_instance_yaml` quotes `repo_name` and `harness` with `json.dumps`, which YAML reads back as double-quoted scalars (pinned by `test_init_repo_name_with_yaml_specials_round_trips`). No credentials paths read or written. Nothing destructive.

6. **Protected paths.** The committed diff touches none of instance B's protected classes: `git diff --stat main...HEAD -- intake` is empty, `docs/` is unchanged. The PR discloses that a baseline run on the *old* code wrote into the worktree's tracked copy of `intake/state/` and was reverted before any change; the worktree is clean (`git status --porcelain` empty before and after the gate run) and the live store's tickets still end at `T-0012.yaml`. Declared guardrail touches are exactly the four `agents/` pointer lines, `factory/prompts/preamble.md` becoming the design block, and new test files (parent Risk, sub-ticket "Protected paths").

7. **Gates, run from the worktree exactly as written:** `git diff --check main...HEAD` → nothing, exit 0. `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `92 passed in 111.27s`. Worktree clean afterwards.

## Findings

- [NIT] `factory/cli.py:759-776` (`init_cmd`): the instance's pieces (`context.md`, `harness.lock`, agent copies) are written only when the store in use is the instance's own. B.5's literal text has no such condition, and a fresh `FACTORY_STATE=/elsewhere factory init --repo-name demo` leaves `.factory/` holding only `instance.yaml` (I ran it: `factory=[instance.yaml ] claude=0`). → An operator who sets `FACTORY_STATE` while initialising gets a half instance until a later own-store `init`; after T-0012.4 the missing lock refuses the next own-store command with the `--accept-harness` hint, which is recoverable but surprising. The reading is the right call for the suite (the literal reading would write `harness.lock` into the tracked fixture and `.claude/agents/` into the harness checkout on every run) and it is disclosed (gap 1); flagging it so the gate confirms the reading and the spec's B.5 text records the condition at close.
- [NIT] `factory/compose.py:55`: `(instance.require() / "context.md").read_text(...)` raises `FileNotFoundError` when the briefing is missing, so `run compose` exits 1 with `factory: FileNotFoundError: …/.factory/context.md` instead of a `Refused` exit 2 (I ran it after deleting `context.md`). → Not reachable after a normal `init`; the message names the path, so the operator can recover. Harmless for this sub-ticket.
- [NIT] `factory/instance.py:56-59` (`not_found_message`): when `FACTORY_INSTANCE` names a directory without `instance.yaml`, stderr is `FACTORY_INSTANCE=<path> holds no instance.yaml; …`, not B.1's single `no .factory/instance.yaml found from <cwd>; …`. → More useful than the spec's text and still names `instance.yaml` (the parent scenario's check), but a verifier grepping the exact B.1 sentence in an override case would miss. Pinned by `test_factory_instance_without_instance_yaml_refused`.

No BLOCKING or SHOULD-FIX findings. I would merge this.

## Notes for the gate (not findings)

- `init` picks its instance as `FACTORY_INSTANCE`, else `<git top level>/.factory`, not by the walk-up (gap 2). This follows B.5's "works at the git top level" and is what lets the imported tests run `init` without touching the harness; a nested repo under another instance gets its own (pinned by `test_init_works_at_its_own_git_top_level_not_an_enclosing_instance`).
- `init --repo-name` refuses when the running harness has no git revision (`cli.py:767`, `_revision()` before any write), so a `git archive` copy of the harness cannot create an instance. Consistent with B.5's lock requirement; noted because today's `intake/harness/` is such a copy (it runs the old code, not this one).
- Workflows (B.8) are verified structurally and by the PR's described smoke run only; end-to-end behaviour waits for operator step 3, as the sub-ticket says.
- Pre-existing, out of this sub-ticket: `ticket new --file r.md` with a relative path resolves against the harness checkout, because `bin/factory` changes directory (I reproduced: `no such file …/wt/r.md` from a target repo). Operators now run from target repos, so this will surprise them; a follow-up should resolve `--file` against `FACTORY_CWD`.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every acceptance scenario and both gate commands were run from the worktree at f5d8203 with bash and printed the expected results; the three NITs are edge behaviours I reproduced, none of which the spec's scenarios or the imported tests reach.
ESCALATIONS: declared guardrail touches, for the gate's human approval as the parent Risk lists them: four one-line pointer replacements in `agents/factory-{triage,spec-writer,spec-critic,planner}.md`; `factory/prompts/preamble.md` replaced by the design doc's block (byte-identical to `docs/prompts/00-preamble.md`); new test files `tests/factory/conftest.py`, `tests/factory/fixtures/instance/*`, `tests/factory/test_instance.py`. No undeclared protected path is touched by the diff; the PR's disclosed transient write into the worktree's `intake/state/` copy on the old code was reverted and is absent from `main...HEAD`.
