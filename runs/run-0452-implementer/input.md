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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0452-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0452-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0044.1` (branch `factory/T-0044.1`, base `0ba4e4f637a6ab019774f439727b5a15ddc425cf`, head `0ba4e4f637a6ab019774f439727b5a15ddc425cf`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

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
