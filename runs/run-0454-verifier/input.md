## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0454-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0454-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0454-verifier/wt` (branch `factory/T-0044.1`, base `0ba4e4f637a6ab019774f439727b5a15ddc425cf`, head `53047c59fcd462510650e752a40d3d294f0486fc`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0044.1

T-0044.1 / De-bloat A: delete dead code, redundant lines and stale docstrings in the harness
Depends on: none
Parallel-safe: yes

Parent: T-0044, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The four dead definitions are gone and nothing names them
- No harness or test file names the force-push setting
- Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write
- No harness module has three blank lines in a row
- The three stale texts are gone
- The repo-root helper takes no argument and every caller passes none
- The harness has no unused imports or variables
- The harness suite passes, and only the force-push test lines change under tests
- A second intake run on a ticket is refused with the same text
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0044/v2.md`

=== proposal.md
## Problem

The harness is the Python program (`factory/`) that runs the spec factory, a pipeline of AI agents that turns a written request into merged code. Each agent has one job and is called a role: triage, spec writer, critic, planner, implementer, reviewer or verifier. The harness starts each role's run, keeps the ticket store (the records of every request and run) and guards the merge. It carries code that nothing runs, a setting that nothing reads, a few lines that repeat work already done, and comments that are no longer true. None of it changes what the harness does. All of it costs every reader attention, and some of it misleads.

One example: each repository the factory runs on has a configuration file made from a template, and that template still offers a `force_push_allowed` switch. An operator who sets it to `true` gets nothing. No code reads it, and the implementer's instructions hardcode "never rebase". Another example: the docstring at the top of the store module promises a commit-and-push step that was never built.

This ticket only removes and tidies. No refusal, verdict, route or message that a role or an operator can reach changes. The one message whose wording changes cannot be reached through any command (Root cause, item 9).

## Root cause

Each item is code left behind by an earlier design.
1. `factory/gitops.py:202-211` `run_gates`: the harness once ran the gate commands itself. The verifier runs them now.
2. `factory/store.py:15-21` `STATES`: the state list now lives in the instance's `routing` config.
3. `factory/specstore.py:20` `OPS`: `parse_delta` hardcodes `(ADDED|MODIFIED|REMOVED)` at `:130`.
4. `factory/store.py:29-32` `load_config`: every caller uses `instance.load_config`.
5. `force_push_allowed`: it once filled the `{force-push allowed}` placeholder of a rendered implementer prompt and told a server-side hook whether to allow force-pushes (`dev/build-harness.spec.md` D9). Neither the render step nor the hook exists in this harness, and the shipped prompt hardcodes "never rebase".
6. `factory/cli.py:234` `prompt_name = a.role`: a rename with one use.
7. `factory/cli.py:207-212`: two branches raise the same refusal for disjoint role sets.
8. `factory/cli.py:377`: `_start_build_run` writes the store's `.gitignore` block, and run start writes it again at `:229` for every role. `store.ensure_gitignore` is idempotent (`_ensure_block`), and `init` writes the same block (`:1469`).
9. `factory/compose.py:420`: written when compose supported only some roles. `compose` takes the role from the run's `meta.yaml` (`compose.py:190`), which only `run start` writes. Run start refuses any role outside `ROLES` (`cli.py:200-201`), and `compose` has a branch for every role in `ROLES` (`compose.py:278`, `288`, `310`, `333`, `350`). So the refusal is reachable only from a hand-edited `meta.yaml`.
10. `factory/store.py:3` and `factory/specstore.py:8-9`: docstrings that describe plans and stores as they were.
11. `factory/gitops.py:18-19` `repo_root(cfg)`: the parameter outlived the move of repo resolution into `factory/instance.py`.
12. `factory/cli.py:1967-1970`: four blank lines.

## Out of scope

- `factory/prompts/**` and `docs/prompts/**`: no prompt changes, including the implementer's "never rebase" line.
- `docs/design.md:144` and `:623`, which describe the `{force-push allowed}` placeholder, and `dev/build-harness.spec.md`, which names `force_push_allowed` (D9, item 80, lines 144, 238, 241, 541). See Decisions.
- The live `.factory/instance.yaml` files of both instances (protected; an extra key is ignored). See Operator steps.
- The `placeholders` key and `store migrate` (#83).
- The Workflow scripts' dead lines (`build.js` `MAX_PR`, `AGENT_NAME`), which #89 deletes with the scripts.
- Every refusal text reachable through a command, every verdict, route and log event.
- The other de-bloat tickets, T-0045 to T-0048.

## Open questions

none

## Decisions

- Every change must add or change at least one requirement in the spec store, the folder of requirement files that says what the harness does. That folder holds one file per capability, a named area of behaviour. For example, build-dispatch covers how role runs are started and routed. The store refuses a change with no such addition (`factory/specstore.py:202`: "no delta part"). Triage, the first role, which accepts the request, named no capability, because nothing here changes behaviour. This change therefore adds a new capability, `harness-code`, to hold the checks that the removed code stays gone. It also adds to build-dispatch one requirement that pins the in-flight refusal this change merges, since no existing requirement covers it. Rejected: putting the removal checks in build-dispatch, which describes how runs are started, not what the source contains.
- `gitops.repo_root` keeps its name and loses its parameter. All 12 callers become `gitops.repo_root()`. Rejected: deleting the wrapper and calling `instance.repo_root()`, which would also move imports in `compose.py` and `gitops.py` for no gain.
- Of the two writes of the store's `.gitignore` block when a build role starts, the one inside the build-role setup function `_start_build_run` (`cli.py:377`) goes. The call at `:229` covers every role. Rejected: removing `:229`, which would leave triage, spec writer, critic and planner runs without the write.
- The two in-flight refusals become one condition over the five roles, written as an explicit list: `("triage", "spec_writer", "critic", "planner", "implementer")`. Rejected: `a.role not in ("reviewer", "verifier")`, which would silently cover a role added later.
- The refusal in compose, the step that writes a run's input file, keeps its place at `compose.py:420` and changes its text to `compose: unknown role {role}`. Rejected: deleting that branch, because a hand-edited run record would then get an empty input and no error.
- The store module's docstring keeps only its first line. Rejected: keeping "Every write goes through here", a claim this ticket did not verify.
- The design documents that still describe `force_push_allowed` stay as they are, and the gap is recorded here. Changing `docs/design.md` would need a changelog entry and a re-copied `docs/prompts/05-implementer.md`, and prompts are out of this round. In practice the setting has done nothing since the shipped prompt hardcoded "never rebase".

## Risk

Low. Only removals and renames inside `factory/`, plus two test edits that follow the removed key. A downstream import of a removed symbol would break. No code outside this repo imports from `factory/`; the Nanobot instance runs this repo's harness from the runtime checkout. T-0046 (#99, shared helpers) also edits `factory/cli.py`. The lines named here do not overlap the lines it names, but whichever merges second may need a text merge. T-0047 (#100, split `cli.py`) should be planned against the tree after this merges.

Protected paths: none

## Operator steps

1. Optional, at any time after merge: delete the line `force_push_allowed: false` from `~/dev/spec-factory/.factory/instance.yaml` (line 34) and from `~/dev/nanobot-upstream/.factory/instance.yaml` (line 65). With or without the line, nothing changes, because no code reads the key.

=== design.md
## Proposed change

About 50 changed lines, all in `factory/` plus two test files. One sub-ticket.

A. **Dead definitions.** Delete:
- `run_gates` with its docstring (`factory/gitops.py:202-211`), and the blank lines before it that would then trail the file;
- `STATES` (`factory/store.py:15-21`);
- `OPS` (`factory/specstore.py:20`);
- `load_config` (`factory/store.py:29-32`), with one of the two blank-line pairs around it.

Keep `RESULT_ROLES` and `Refused`. Run `uvx ruff check --select F401,F841 factory tests` afterwards. No import should become unused, but if one does, remove it.

B. **The unread setting.** Delete the line `force_push_allowed: false` from `factory/instance.template.yaml` (line 45) and from `tests/factory/fixtures/instance/instance.yaml` (line 22). In `tests/factory/test_instance.py`, line 109 drops `and cfg["force_push_allowed"] is False`. Line 354's key tuple drops `"force_push_allowed",`, and the tuple is re-wrapped if needed. Leave the `set(cfg) == set(tpl)` assertion at line 113 unchanged: both sides lose the key.

C. **Run start (`factory/cli.py` `run_start`).**
- Replace the two in-flight branches (`:207-208` and `:211-212`) with one, placed where the implementer branch is now, before the reviewer/verifier branch:
  `if a.role in ("triage", "spec_writer", "critic", "planner", "implementer") and t["in_flight"]:`
  `    raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")`
  The reviewer/verifier branch (`:209-210`) and every later check keep their order.
- Delete `prompt_name = a.role` (`:234`). Line 236 reads `(PROMPTS / f"{a.role}.md")`.
- Delete `store.ensure_gitignore(root)` inside `_start_build_run` (`:377`). Keep the call at `:229` and the one in `init` (`:1469`).
- Cut the four blank lines at `:1967-1970` to two.

D. **Stale text.**
- `factory/store.py`: delete line 3 and the blank line 2, so the module docstring is its first line alone.
- `factory/specstore.py:8-9`: end the sentence at "(specs pinned as one text)." by dropping ", so the live pilot store is unaffected". Re-wrap the line if it becomes short.
- `factory/compose.py:420`: change the message to `f"compose: unknown role {role}"`.

E. **`gitops.repo_root`.** Change the signature to `def repo_root() -> Path:`. Replace each `gitops.repo_root(cfg)` with `gitops.repo_root()`: one in `compose.py:110`, eleven in `cli.py`. Where a caller's `cfg` then goes unused, ruff F841 does not fire, because `cfg` is a parameter. Leave such parameters alone.

No change to `README.md`: no command, state, stop or path changes. No change to `docs/` or `dev/` (proposal, Decisions).

## Tests to change

- `tests/factory/test_instance.py` lines 109 and 354: each asserts the `force_push_allowed` key that part B removes from the template and the fixture (Decision: the unread setting is deleted). Remove only the key from each assertion.
- `tests/factory/fixtures/instance/instance.yaml` line 22: the fixture must keep the template's keys, because line 354 compares them. Delete the key line.

=== specs/harness-code/spec.md
## ADDED Requirements

### Requirement: The harness keeps no definition, setting or comment that nothing uses or that is no longer true
The harness source under `factory/` SHALL carry no definition that nothing calls or reads, no instance setting that no code reads, and no comment or message that describes behaviour the harness no longer has. It MUST keep every behaviour that a command can reach.

#### Scenario: The four dead definitions are gone and nothing names them
- WHEN `echo "$(grep -nE '^(def run_gates\(|STATES = |OPS = |def load_config\()' factory/gitops.py factory/store.py factory/specstore.py | wc -l | tr -d ' ') $(grep -rnF --include='*.py' -e 'gitops.run_gates' -e 'store.STATES' -e 'specstore.OPS' -e 'store.load_config' factory tests | wc -l | tr -d ' ')"`
- THEN it prints `0 0`

#### Scenario: No harness or test file names the force-push setting
- WHEN `grep -rn --exclude-dir=__pycache__ force_push_allowed factory tests | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write
- WHEN `echo "$(grep -c prompt_name factory/cli.py) $(grep -c "already has run {t\[.in_flight.\]\[0\]} in flight" factory/cli.py) $(grep -c 'store.ensure_gitignore(root)' factory/cli.py)"`
- THEN it prints `0 2 2`

#### Scenario: No harness module has three blank lines in a row
- WHEN `awk 'FNR==1{n=0} /^$/{n++; if(n==3) print FILENAME":"FNR; next} {n=0}' factory/*.py | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: The three stale texts are gone
- WHEN `grep -nF -e 'commit-and-push' -e 'live pilot store is unaffected' -e 'not supported yet' factory/*.py | wc -l | tr -d ' '`
- THEN it prints `0`

#### Scenario: The repo-root helper takes no argument and every caller passes none
- WHEN `echo "$(grep -n 'repo_root(cfg' factory/*.py | wc -l | tr -d ' ') $(grep -o 'gitops.repo_root()' factory/*.py | wc -l | tr -d ' ') $(grep -c '^def repo_root() -> Path:$' factory/gitops.py)"`
- THEN it prints `0 12 1`

#### Scenario: The harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes, and only the force-push test lines change under tests
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0044-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only main...HEAD -- tests)`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and every later line, if any, is `tests/factory/fixtures/instance/instance.yaml` or `tests/factory/test_instance.py`

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: A role run does not start on a ticket that already has a run in flight
`factory run start` for triage, spec_writer, critic, planner or implementer SHALL refuse, with exit 2 and nothing written, when the ticket already has a run in flight. The error MUST read `<ticket id> already has run <first in-flight run id> in flight`.

#### Scenario: A second intake run on a ticket is refused with the same text
The second start carries `FACTORY_DISPATCH=1`, the marker that lets a command past the live-store fence, so the command reaches the run-start check rather than the fence.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && FACTORY_DISPATCH=1 $B run start --role triage --ticket T-0001 2>&1 >/dev/null; echo "exit=$?"; ls $T/tgt/.factory/state/runs)`
- THEN it prints `T-0001 already has run run-0001-triage in flight`, then `exit=2`, then `run-0001-triage` as the only run directory

=== verification.md
## Acceptance

- The four dead definitions are gone and nothing names them → NEW; today it prints `4 0`.
- No harness or test file names the force-push setting → NEW; today it prints `4`.
- Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write → NEW; today it prints `2 3 3`.
- No harness module has three blank lines in a row → NEW; today it prints `1` (`factory/cli.py:1969`, the third of the four blank lines at `:1967-1970`).
- The three stale texts are gone → NEW; today it prints `3`.
- The repo-root helper takes no argument and every caller passes none → NEW; today it prints `13 0 0`.
- The harness has no unused imports or variables → REGRESSION; today it prints `All checks passed!`.
- The harness suite passes, and only the force-push test lines change under tests → REGRESSION; today `577 passed` and no diff under `tests`. The implementer's in-flight refusal and the plan whole-spec refusal keep their coverage through the existing suite. The second half shows that their test files are unchanged.
- A second intake run on a ticket is refused with the same text → REGRESSION; today it prints the three lines shown, run on `0ba4e4f`.

## PR description (the implementer's output)

Sub-ticket: T-0044.1 (parent T-0044, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0044/v2.md`)
Branch: `factory/T-0044.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0044.1`, head `53047c59fcd462510650e752a40d3d294f0486fc`, one commit on base `0ba4e4f637a6ab019774f439727b5a15ddc425cf` (`main`'s tip when the branch was made).

## What changed

This change only removes and tidies code in the harness, the Python package `factory/` that runs the spec factory. No refusal, verdict, route or log event that a command can reach changes. 8 files, 20 insertions, 57 deletions.

A. **Dead definitions.** These are deleted:
- `run_gates` in `factory/gitops.py`, with its docstring and the two blank lines before it. The file now ends at `remove_worktree(repo, temp)`. `subprocess` is still used at `gitops.py:32` and `:80`, so its import stays.
- `STATES` in `factory/store.py`.
- `load_config` in `factory/store.py`, with one of the two blank-line pairs around it.
- `OPS` in `factory/specstore.py`.

`RESULT_ROLES` and `Refused` stay. Ruff reports no unused import afterwards.

B. **The unread setting.** The line `force_push_allowed: false` is deleted from `factory/instance.template.yaml` and from `tests/factory/fixtures/instance/instance.yaml`. In `tests/factory/test_instance.py`, line 109 drops `and cfg["force_push_allowed"] is False`, and line 354's key tuple drops `"force_push_allowed",`. The tuple still fits on its two lines, so it was not re-wrapped. The `set(cfg) == set(tpl)` assertion at line 113 is unchanged.

C. **Run start, in `factory/cli.py`.**
- The implementer and the intake roles each had an in-flight check with the same refusal text. They are now one check, in the implementer branch's old place, before the reviewer/verifier branch: `if a.role in ("triage", "spec_writer", "critic", "planner", "implementer") and t["in_flight"]:`. ("In flight" means the ticket already has a run that has started and not finished.) The reviewer/verifier branch and every later check keep their order.
- `prompt_name = a.role` is deleted. The role prompt is now read from `PROMPTS / f"{a.role}.md"`.
- `store.ensure_gitignore(root)` is deleted from `_start_build_run`. The call in `run_start` (now `cli.py:227`) and the one in `init` (now `cli.py:1465`) stay.
- The four blank lines after `build_parser` are cut to two.

D. **Stale text.**
- The docstring of `factory/store.py` is now only its first line. The promise of a "commit-and-push" step and "Every write goes through here" are gone.
- `factory/specstore.py`: the sentence now ends at "(specs pinned as one text)." It was not re-wrapped: joining it to the line above would pass 100 characters.
- `factory/compose.py`: the role refusal in compose now reads `compose: unknown role {role}`. Compose is the step that writes a run's input file.

E. **`gitops.repo_root`.** The signature is now `def repo_root() -> Path:`. I grepped every caller (`grep -n 'repo_root' factory/*.py tests -r`) and found 12 calls to `gitops.repo_root(cfg)`: 11 in `cli.py` and 1 in `compose.py:110`. All 12 now call `gitops.repo_root()`. The calls to `instance.repo_root(...)` at `cli.py:1339`, `:1435` and `:1530` and in `instance.py` are a different function and were left alone. In `tests/`, `repo_root` appears only in a test name (`test_instance.py:247`, which tests `instance.repo_root`). No caller's `cfg` parameter became unused: each one still passes `cfg` to `gitops.integration_branch`. So no parameter changed.

`README.md`, `docs/` and `dev/` are unchanged, as the spec says.

## Acceptance results

All commands were run from the worktree through the running-code wrapper (a fresh temporary HOME). The "after" runs were on head `53047c5`. The full "after" output is in `scratch/accept-after.txt`.

| Scenario | Kind | Before (on `0ba4e4f`) | After |
|---|---|---|---|
| The four dead definitions are gone and nothing names them | NEW | `4 0` | `0 0` |
| No harness or test file names the force-push setting | NEW | `4` | `0` |
| Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write | NEW | `2 3 3` | `0 2 2` |
| No harness module has three blank lines in a row | NEW | `1` | `0` |
| The three stale texts are gone | NEW | `3` | `0` |
| The repo-root helper takes no argument and every caller passes none | NEW | `13 0 0` | `0 12 1` |
| The harness has no unused imports or variables (`uvx ruff check --select F401,F841 factory tests`) | REGRESSION | not run (regression) | `All checks passed!`, exit 0 |
| The harness suite passes, and only the force-push test lines change under tests | REGRESSION | not run (regression) | `577 passed in 390.55s (0:06:30)`, then `tests/factory/fixtures/instance/instance.yaml` and `tests/factory/test_instance.py` |
| A second intake run on a ticket is refused with the same text | REGRESSION | not run (regression) | `T-0001 already has run run-0001-triage in flight`, then `exit=2`, then `run-0001-triage` |

Every NEW "before" value matches the value the spec's `verification.md` gives for today.

Gate commands, each run exactly as written from the worktree on `53047c5`:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `577 passed in 388.61s (0:06:28)`, exit 0. The output is in `scratch/gate-pytest.txt`.

## Tests added/changed

- `tests/factory/test_instance.py` line 109: removed only `and cfg["force_push_allowed"] is False`. The key no longer exists in the template, so the assertion would raise `KeyError`. This line is listed under the spec's Tests to change.
- `tests/factory/test_instance.py` line 354: removed only `"force_push_allowed",` from the key tuple. The same reason applies, and the line is listed.
- `tests/factory/fixtures/instance/instance.yaml` line 22: deleted the key line. Line 354 compares the fixture's keys with the template's keys, and the line is listed.
- No test was added. The NEW acceptance commands are the checks for this change. They are grep and ruff commands over the source, and they failed before the change as the spec describes. A new test file would also break the suite scenario, which allows only the two files above to change under `tests/`. The existing suite still covers the merged in-flight refusal, as `verification.md` notes, and the second-intake scenario checks its text end to end.

## Known gaps and uncertainties

- The `.gitignore` write removed from `_start_build_run` used to run before the worktree was created. Now the only write at run start comes after `_start_build_run` returns. Suppose a build run is refused after its worktree was created, for example by a failing `environment_sync`. That run start no longer writes the store's `.gitignore` block. In practice the block is already there: `init` writes it, and so does every earlier role's run start on the same store (triage onward). `_ensure_block` is idempotent. The spec's Decisions accept this choice. I did not add a test for this path.
- `uv run` created a `.venv` in the worktree. Git ignores it, and `git status` is clean.
- factory: markers added: none.

## Out-of-scope observations

- The module docstring at `factory/gitops.py:5` says the target repo is `repo_root` (FACTORY_REPO, else the parent of the instance directory). That is still accurate after part E, so it was left alone.
- `docs/design.md` and `dev/build-harness.spec.md` still describe `force_push_allowed`. The spec leaves them on purpose (proposal, Out of scope and Decisions). The live `instance.yaml` files of both instances still carry the key. Deleting it there is the spec's optional operator step.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW command failed before the change and passes after, with the spec's exact values. Both gates and all three regression commands pass on head `53047c5`.
ESCALATIONS: none

## Diff `0ba4e4f637a6ab019774f439727b5a15ddc425cf...53047c59fcd462510650e752a40d3d294f0486fc`

diff --git a/factory/cli.py b/factory/cli.py
index c1149ca..8373b4b 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -204,12 +204,10 @@ def run_start(a, root, cfg):
     ready = cfg["ready_state"][a.role]
     if t["status"] != ready and not parent_close:
         raise Refused(f"{t['id']} is {t['status']}, not {ready}")
-    if a.role == "implementer" and t["in_flight"]:
+    if a.role in ("triage", "spec_writer", "critic", "planner", "implementer") and t["in_flight"]:
         raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
     if a.role in ("reviewer", "verifier") and any(a.role in r for r in t["in_flight"]):
         raise Refused(f"{t['id']} already has a {a.role} run in flight")
-    if a.role in ("triage", "spec_writer", "critic", "planner") and t["in_flight"]:
-        raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
     if a.role == "implementer" and t.get("parent"):
         _check_drift(root, cfg, t)
         _check_sibling_tests(root, cfg, t)
@@ -231,9 +229,8 @@ def run_start(a, root, cfg):
     (d / "scratch").mkdir(exist_ok=True)
     if baseline:
         store.write_yaml(d / "tripwire.yaml", baseline)
-    prompt_name = a.role
     preamble = instance.fill_preamble((PROMPTS / "preamble.md").read_text(encoding="utf-8"), cfg)
-    role_prompt = instance.fill_standards((PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8"))
+    role_prompt = instance.fill_standards((PROMPTS / f"{a.role}.md").read_text(encoding="utf-8"))
     sysp = preamble.rstrip() + "\n\n" + role_prompt
     store.write_text(d / "system-prompt.txt", sysp)
     t["in_flight"].append(rid)
@@ -253,7 +250,7 @@ def _check_sibling_tests(root: Path, cfg: dict, t: dict) -> None:
         return
     parent = store.load_ticket(root, t["parent"])
     base = parent.get("parent_base")
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
     merges = [s["merge"] for s in store.subtickets_of(root, parent["id"])
               if s["id"] != t["id"] and s["status"] == "merged"
@@ -325,7 +322,7 @@ def _test_drift(root: Path, cfg: dict, parent: dict, sub_text: str) -> list[str]
     base = (store.read_yaml(rec) or {}).get("integration_head") if rec.exists() else None
     if not base:
         return []
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     if not gitops.git(repo, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", check=False):
         return []
     tip = gitops.rev(repo, gitops.integration_branch(cfg, repo))
@@ -372,9 +369,8 @@ def _start_build_run(root: Path, cfg: dict, t: dict, meta: dict, d: Path, parent
     detached checkout of the head it checks, plus the diff written as runs/<id>/diff.patch. Each
     checkout then runs the instance's `environment_sync`, if set (`_sync_environment`)."""
     sync = compose.environment_sync(cfg)
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     integ = gitops.integration_branch(cfg, repo)
-    store.ensure_gitignore(root)
     meta["round"] = t["round"]["pr"]
     meta["gate_skipped"] = []  # only a checker of a sub-ticket's diff skips a gate command
     if meta["role"] == "implementer":
@@ -435,7 +431,7 @@ def run_cleanup(a, root, cfg):
     meta = store.read_yaml(d / "meta.yaml")
     wt = Path(meta.get("worktree") or "")
     if meta.get("role") in ("reviewer", "verifier") and wt.exists():
-        gitops.remove_worktree(gitops.repo_root(cfg), wt)
+        gitops.remove_worktree(gitops.repo_root(), wt)
     out({"ok": True, "run_id": a.run, "removed": str(wt) if wt else None})
 
 
@@ -545,7 +541,7 @@ def _text_from(a, root) -> str:
 def _integration_head(cfg: dict) -> str | None:
     """The integration branch's head in the target repo, or None when the repo or branch does not resolve."""
     try:
-        repo = gitops.repo_root(cfg)
+        repo = gitops.repo_root()
         return gitops.rev(repo, gitops.integration_branch(cfg, repo))
     except (Refused, OSError):
         return None
@@ -838,7 +834,7 @@ def ticket_head(a, root, cfg):
     t = store.load_ticket(root, a.id)
     if not t.get("branch"):
         raise Refused(f"{t['id']} has no branch yet")
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     head = gitops.rev(repo, t["branch"])
     changed = head != t.get("head")
     t["head"] = head
@@ -939,7 +935,7 @@ def undeclared_protected(root: Path, cfg: dict, t: dict, head: str) -> tuple[lis
     where = f"in {sid} spec v{av}" if av is not None else f"({sid} has no approved spec)"
     patterns = [g for globs in (cfg.get("protected_paths") or {}).values()
                 for g in ([globs] if isinstance(globs, str) else list(globs or []))]
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     integ = gitops.integration_branch(cfg, repo)
     changed = gitops.changed_files(repo, integ, head, _in_repo(patterns))
     if not changed:
@@ -967,7 +963,7 @@ def merge_cmd(a, root, cfg):
     t = store.load_ticket(root, a.id)
     if t["status"] not in ("ready-for-merge", "checks-in-flight"):
         raise Refused(f"{t['id']} is {t['status']}, not ready-for-merge")
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     integ = gitops.integration_branch(cfg, repo)
     head = _branch_tip(repo, t)
     rows = store.results_for(root, head)
@@ -1216,7 +1212,7 @@ def resolve(a, root, cfg):
         if st != "parked" or not reason.startswith("BLOCKED from merge gate:"):
             raise Refused("--accept-paths applies to a merge gate park (BLOCKED from merge gate); "
                           f"{t['id']} is {st} ({reason or 'no park'})")
-        head = _branch_tip(gitops.repo_root(cfg), t)
+        head = _branch_tip(gitops.repo_root(), t)
         paths, _ = undeclared_protected(root, cfg, t, head)
         if not paths:
             raise Refused(f"nothing to accept: {t['id']} has no undeclared protected path at {head[:9]}")
@@ -1693,7 +1689,7 @@ def _reused_subticket_run(root: Path, cfg: dict, t: dict) -> str | None:
     after = (s.get("merge") or {}).get("main_after")
     if s["status"] != "merged" or not after or not s.get("head"):
         return None
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     if gitops.rev(repo, gitops.integration_branch(cfg, repo)) != after:
         return None
     row = store.results_for(root, s["head"]).get("verifier") or {}
@@ -1721,7 +1717,7 @@ def _parent_close_verified(root: Path, cfg: dict, t: dict) -> str | None:
     subs = subtickets.split_plan(store.subtickets_of(root, t["id"]))[0]
     if any(s["status"] != "merged" for s in subs):
         return None
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     runs = root / "runs"
     for d in sorted(runs.iterdir()) if runs.exists() else []:
         mp = d / "meta.yaml"
@@ -1966,8 +1962,6 @@ def build_parser() -> argparse.ArgumentParser:
     return ap
 
 
-
-
 # ----- live-store fence: only the dispatcher writes a live store during a run ------------------
 
 # `paths` and `stats` never reach the fence (main() runs them before it); they are listed so this set
diff --git a/factory/compose.py b/factory/compose.py
index 84e9d38..893a8f8 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -107,7 +107,7 @@ def gate_commands(cfg: dict) -> list[str]:
     branch: the gate script and its baseline come from the integration branch, never from the branch
     under test, so a change cannot weaken its own gate."""
     from factory import gitops  # local: compose is otherwise git-free
-    repo = gitops.repo_root(cfg)
+    repo = gitops.repo_root()
     co = gitops.checkout_of(repo, gitops.integration_branch(cfg, repo)) or repo
     return [g.replace("{integration}", str(co)) for g, _ in gate_entries(cfg)]
 
@@ -417,5 +417,5 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             for p in _approvals(root, tid, "ruling"):
                 add(str(p.relative_to(root)), "Human ruling")
     else:
-        raise store.Refused(f"compose: role {role} not supported yet")
+        raise store.Refused(f"compose: unknown role {role}")
     return "".join(parts), sources
diff --git a/factory/gitops.py b/factory/gitops.py
index b20da26..253f6bd 100644
--- a/factory/gitops.py
+++ b/factory/gitops.py
@@ -15,7 +15,7 @@ from pathlib import Path
 from factory import instance, store
 
 
-def repo_root(cfg: dict | None = None) -> Path:
+def repo_root() -> Path:
     return instance.repo_root()
 
 
@@ -197,15 +197,3 @@ def merge_no_ff(repo: Path, sha: str, into: str, message: str) -> tuple[str, str
     finally:
         if temp is not None:
             remove_worktree(repo, temp)
-
-
-def run_gates(cwd: Path, commands: list[str]) -> tuple[bool, str]:
-    """Run the repo's gate commands in `cwd`; (all passed, combined output)."""
-    outs = []
-    ok = True
-    for cmd in commands:
-        cp = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
-        outs.append(f"$ {cmd}\n{cp.stdout}{cp.stderr}".rstrip())
-        if cp.returncode != 0:
-            ok = False
-    return ok, "\n\n".join(outs)
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
index 1167da8..fdad9a0 100644
--- a/factory/instance.template.yaml
+++ b/factory/instance.template.yaml
@@ -42,7 +42,6 @@ run_env: {}
 # wrapper, after the environment files are copied (for example `uv sync --frozen`). null means none.
 # A failure refuses the run.
 environment_sync: null
-force_push_allowed: false
 models:
   triage: opus
   spec_writer: opus
diff --git a/factory/specstore.py b/factory/specstore.py
index 05f1ea7..2e31ea4 100644
--- a/factory/specstore.py
+++ b/factory/specstore.py
@@ -6,7 +6,7 @@ Current truth is `openspec/specs/<capability>/spec.md`. A ticket's change is the
 text is split on its `=== <path>` lines. Only `archive` writes current truth. `decisions.md` has
 three writers, all through `record_decision`: `archive`, `decision add` and `resolve --decision`.
 The store is active once `init` has created `openspec/`; a store without it keeps the P0
-behaviour (specs pinned as one text), so the live pilot store is unaffected.
+behaviour (specs pinned as one text).
 """
 from __future__ import annotations
 
@@ -17,7 +17,6 @@ from pathlib import Path
 
 from factory import store
 
-OPS = ("ADDED", "MODIFIED", "REMOVED")
 FIXED_PARTS = ("proposal.md", "design.md", "verification.md")
 DELTA_RE = re.compile(r"^specs/([a-z0-9]+(?:-[a-z0-9]+)*)/spec\.md$")
 PART_RE = re.compile(r"^=== (\S+).*$", re.M)  # the path is the first token after "=== "
diff --git a/factory/store.py b/factory/store.py
index bd61475..9e12804 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -1,7 +1,4 @@
-"""Ticket store on disk: tickets/, requests/, specs/, plans/, runs/, log/ under the state dir.
-
-Every write goes through here so a later sub-ticket can add commit-and-push in one place.
-"""
+"""Ticket store on disk: tickets/, requests/, specs/, plans/, runs/, log/ under the state dir."""
 from __future__ import annotations
 
 import datetime as dt
@@ -12,13 +9,6 @@ from pathlib import Path
 
 import yaml
 
-STATES = [
-    "ready-for-triage", "waiting-requester", "ready-for-spec-writer", "ready-for-critic",
-    "awaiting-spec-gate", "ready-for-planner", "planned", "parked", "closed",
-    # build half (sub-tickets, and the parent after all of them merged)
-    "waiting-dependencies", "ready-for-implementer", "checks-in-flight", "ready-for-merge",
-    "merged", "ready-for-parent-verify",
-]
 RESULT_ROLES = ("reviewer", "verifier", "ci")
 
 
@@ -26,12 +16,6 @@ class Refused(Exception):  # noqa: N818
     """A guard refused the operation: exit 2, store unchanged, nothing logged."""
 
 
-def load_config() -> dict:
-    """The resolved instance's `instance.yaml` (factory/instance.py); refused when none is found."""
-    from factory import instance  # local: instance imports Refused from here
-    return instance.load_config()
-
-
 def state_root(cfg: dict | None = None) -> Path:
     """FACTORY_STATE, else the instance's `state_dir` under its repo root."""
     from factory import instance
diff --git a/tests/factory/fixtures/instance/instance.yaml b/tests/factory/fixtures/instance/instance.yaml
index bdfaa20..0d9a1af 100644
--- a/tests/factory/fixtures/instance/instance.yaml
+++ b/tests/factory/fixtures/instance/instance.yaml
@@ -19,7 +19,6 @@ integration_branch: null
 # example a lockfile the target repo git-ignores). A tracked file does not belong here: copying it in
 # would mask the branch's own version.
 environment_files: ["uv.lock"]
-force_push_allowed: false
 models:
   triage: opus
   spec_writer: opus
diff --git a/tests/factory/test_instance.py b/tests/factory/test_instance.py
index e1cbf66..39a1083 100644
--- a/tests/factory/test_instance.py
+++ b/tests/factory/test_instance.py
@@ -106,7 +106,7 @@ def test_init_writes_instance_yaml_from_the_template(target):
     assert cfg["state_dir"] == ".factory/state"
     assert cfg["protected_paths"] == {"infra": [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]}
     assert cfg["gate_commands"] == []
-    assert cfg["integration_branch"] is None and cfg["environment_files"] == [] and cfg["force_push_allowed"] is False
+    assert cfg["integration_branch"] is None and cfg["environment_files"] == []
     assert "request_dir" not in cfg
     for key in ("placeholders", "max_rounds", "models", "ready_state", "routing"):
         assert cfg[key] == tpl[key], key
@@ -351,6 +351,6 @@ def test_conftest_points_the_suite_at_the_fixture_instance():
     tpl = yaml.safe_load((REPO / "factory" / "instance.template.yaml").read_text())
     assert cfg["environment_files"] == ["uv.lock"] and cfg["gate_commands"] == ["git diff --check main...HEAD"]
     for key in ("state_dir", "protected_paths", "placeholders", "max_rounds", "integration_branch",
-                "force_push_allowed", "models", "ready_state", "routing"):
+                "models", "ready_state", "routing"):
         assert cfg[key] == tpl[key], key
     assert (fixture / "context.md").is_file()
