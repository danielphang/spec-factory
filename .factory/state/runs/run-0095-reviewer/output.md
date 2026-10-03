Commit: 302f70bb99f5c4518ddb94de12db22653aa57385 (branch `factory/T-0012.6`, one commit on `f4be7ec`)

## Review

Round 1. Checked in the worktree `intake/state/runs/run-0095-reviewer/wt`, with `FACTORY_STATE`, `FACTORY_INSTANCE`, `FACTORY_REPO`, `FACTORY_CWD` unset, after `uv sync --frozen` (which created the gitignored `.venv/`; `git status --porcelain` is empty before and after everything below).

**1. Test integrity.** `git diff --name-only main...HEAD -- tests/ factory/ bin/factory agents/ pyproject.toml uv.lock` prints nothing (`0`). No test file is touched, no harness code is touched. `git diff --name-status -M main...HEAD | grep -v '^R100'` lists exactly: `A .factory/README.md`, `A .factory/context.md`, `A .factory/harness.lock`, `R062 intake/instance/config.yaml → .factory/instance.yaml`, `M README.md`, and the five deletions `intake/HARNESS_PIN`, `intake/README.md`, `intake/instance/context.md`, `intake/instance/preamble.md`, `intake/setup.sh`. The other 162 entries are `R100`.

**2. Correctness against E.1–E.6.**
- E.1: yaml-diffed `main:intake/instance/config.yaml` against `.factory/instance.yaml` (pyyaml, key by key). Changed keys are only `repo_name`, `state_dir`, `protected_paths`, `gate_commands`, `harness` (added), `request_dir` (dropped). `placeholders`, `max_rounds`, `integration_branch`, `environment_files` (`[]` before and after), `force_push_allowed`, `models`, `ready_state`, `routing` are equal. Header comment no longer names `intake/setup.sh` or `HARNESS_PIN`; it names `factory/instance.template.yaml`, which exists on the branch.
- E.2: `.factory/context.md` names `docs/design.md`, `docs/changelog.md`, `docs/prompts/` (only after `docs/`), `dev/` with its four files, the harness paths and the suite command, `.factory/`, the two checkouts, green as instance A read-only, and keeps the acceptance-command and design-doc-convention paragraphs with paths updated.
- E.3: `.factory/harness.lock` = `010d1b00c5835c7022a72771c63f63f8b6ab3707` + newline. `git log -1 --format=%H -- factory bin/factory agents pyproject.toml uv.lock` gives the same SHA at HEAD, at the merge-base `f4be7ec`, and at today's `main` (`600b8d4`), so the lock is current for the merge.
- E.4: `.factory/README.md` carries the layout, the ticket→issue table, running, scope and the green-pilot section. The two editorial additions check out: T-0012's title in `intake/state/tickets/T-0012.yaml` is the #19 move (`dev/issues.md:26`), and `dev/issues.md:25` ties #18 to `green-pilot T-0002`. The two dropped sentences were false: T-0012 is open, and `factory/store.py:112-114` (`next_run_id`) allocates run ids with an atomic `mkdir`.
- E.5: `left=0`; `pilot=148 of 148 answers=14 of 14`; `-M100% --diff-filter=AD` count `0`; `live-store-untouched` `0`.
- E.6: `README.md` has install (`git clone`, `uv sync --frozen`, the suite), five-minute use (`factory init --repo-name`, "Restart the Claude Code session", `.factory/context.md` and `gate_commands`, `factory paths`, `ticket new`, Workflow call with `scriptPath` and `{ticket, repo, instance}`, `approve-spec`), the where-things-live table with all nine paths, and the updates paragraph (runtime checkout, lock, uncommitted-edit refusal, upgrade = move runtime then accept per target). Its claim that `ticket new --file` needs an absolute path is true: `bin/factory:9-10` exports `FACTORY_CWD` then `cd "$HERE"`, and `factory/cli.py:40` resolves `a.file` from there.

**Acceptance, re-run by me (all as written):**

| Check | Result |
|---|---|
| intake-holds-only-live-store | `left=0` |
| pilot-store-and-answers-kept-byte-identical | `kept=135 of 135` with BASE=`cdb1c67` (parent base) and with BASE=`f4be7ec` |
| instance-b-opens-every-ticket | `tickets=18 failed=0`; store unchanged after |
| instance-b-config | `True True True` / `context=3` |
| readme-has-install-and-layout | `checked` only |
| no-old-paths-in-live-files (REGRESSION, full pathspec) | `exit=1`; also `exit=1` over `.factory/README.md`, which is outside the pathspec |
| lock-is-base-revision | `lock=current` / `harness_paths_changed=0` |
| instance-b-keys | `False [] intake/state True` / `True True` |
| records-moved-as-pure-renames | `0` / `pilot=148 of 148 answers=14 of 14` |
| live-store-untouched | `0` |
| role-prompt-text-unchanged | `changed=0 of 14` (under `bash`; my first zsh attempt mangled `$G:factory`, that was my shell, not the tree) |
| harness-files-in-repo | `agents=6 green_only=0` |
| harness-history-carried | `0` |
| docs-moved-and-split | `old_tracked=0` |
| changelog-moved-verbatim | `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0` |
| design-text-kept | `0` |
| prompt-copies-moved-unchanged | `changed=0 of 10 VERBATIM` |
| green-harness-still-present | `green keeps its harness` |
| gate `git diff --check main...HEAD` | `exit=0`; with `-c diff.renames=false` seven files flagged, all under `.factory/green-pilot/` (the six `openspec/changes/archive/2026-10-03-T-000{1,2}/…` files and `runs/run-0015-implementer/input.md`), as the ticket predicts |
| gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory` | `116 passed in 90.16s`, no failed/error, pipeline exit 0 |

Lock enforcement is real, not skipped: a copy of `.factory/` with an all-zero `harness.lock`, run as `FACTORY_REPO=$PWD FACTORY_INSTANCE=<copy> bin/factory ticket show T-0001`, exits 2 with `harness 010d1b0… is not the revision this instance accepted (0000…); rerun with --accept-harness 010d1b0… to accept it`; the real `.factory/` opens `T-0012` with exit 0.

**3. Scope.** Every changed path is one E.1–E.6 names. No `docs/`, `dev/`, `factory/`, `agents/`, `tests/` change.

**4. Silent behavior changes.** After merge, `bin/factory` run from the dev checkout root resolves `.factory/` and the live `intake/state` store under the lock (and C.4's uncommitted-harness refusal). That is what instance-b-opens-every-ticket asks for and the spec's two-checkout Decision describes; not unasked-for. The in-flight build uses the gitignored `intake/harness/` copy, which is untouched (`intake/.gitignore` still ignores `harness/`); `intake/setup.sh` is gone, so that copy can no longer be rebuilt, which is E.5's intent.

**5. Security.** No secrets. `harness:` is a `/Users/dphang/...` absolute path, as E.1 requires and instance-b-keys checks via `expanduser`.

**6. Protected paths.** `intake/**` (infra) is touched exactly as the sub-ticket declares: removals of `README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames out of `answers/` and `green-pilot/`; `intake/state/**` and `intake/.gitignore` untouched. Listed under ESCALATIONS for the merge gate.

**Base drift.** The run context names base `600b8d4`, but the branch's merge-base with `main` is `f4be7ec`; `main` gained one commit (`600b8d4`, store bookkeeping) that touches only `intake/state/**` and `intake/.gitignore`-adjacent paths, none of which this branch changes (`comm -12` of the two file lists is empty). The merge will be clean and the lock stays current.

## Findings

- [NIT] `.factory/context.md:43-45`: the Output paragraph ("That is the only file you may create or modify") is carried verbatim from the old briefing and contradicts the implementer role, which commits in its own worktree by design → every implementer run under instance B is told it is breaking its briefing. Pre-existing, and E.2 says to keep the existing rules, so not a spec violation here; `factory/context.template.md` already has wording that covers the implementer, worth adopting in a later briefing edit.

Prior findings: none (round 1).

## Out-of-scope observations

- The sub-ticket's `kept=134 of 134` is stale: at `f082708` (the spec's "today") there were 13 answers and 134 distinct blobs; `intake/answers/T-0012-gate-edit.md` was added by the parent's recorded base `cdb1c67` (14 answers, 135 distinct). The THEN's condition, both numbers equal, holds.
- The implementer's Known gap 1 (no-old-paths-in-live-files passing before the change) is moot: the sub-ticket as dispatched to me already carries the operator's relabel to REGRESSION.
- The parent-level `whitespace-clean` (`git diff --check "$BASE" HEAD`, BASE=`cdb1c67`) is not this sub-ticket's gate and I did not re-run it; the implementer reports it fails on store run records committed to `main`. Close-time concern for the parent, not this PR.
- `dev/issues.md:26` still says #19 is "not in intake yet" (operator step 4).

STATUS: APPROVE
CONFIDENCE: high. Every acceptance item and both gate commands were re-run on `302f70b` and gave the THEN output; the yaml key diff, the lock SHA at HEAD/base/main, the rename counts and the lock-enforcement probe were checked directly, not taken from the PR description.
ESCALATIONS: protected path `intake/**` (infra) touched, as declared in the sub-ticket (removals of `intake/README.md`, `setup.sh`, `HARNESS_PIN`, `instance/*`; pure renames of `intake/answers/` and `intake/green-pilot/` to `.factory/`; `intake/state/**` and `intake/.gitignore` unchanged). Merge gate needs the human approval the declaration implies. No `generated`, `reference_harness` or `credentials` path was read or written beyond the read-only `git -C ~/dev/nanobot-upstream` commands the parent scenarios prescribe.
