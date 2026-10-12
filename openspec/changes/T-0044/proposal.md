## Problem

The harness is the Python program (`factory/`) that runs the spec factory, a pipeline of AI agents that turns a written request into merged code. Each agent has one job and is called a role: triage, spec writer, critic, planner, implementer, reviewer or verifier. The harness starts each role's run, keeps the ticket store (the records of every request and run) and guards the merge. It carries code that nothing runs, a setting that nothing reads, a few lines that repeat work already done, and comments that are no longer true. None of it changes what the harness does. All of it costs every reader attention, and some of it misleads.

One example: each repository the factory runs on has a configuration file made from a template, and that template still offers a `force_push_allowed` switch. An operator who sets it to `true` gets nothing. No code reads it, and the implementer's instructions hardcode "never rebase". Another example: the docstring at the top of the store module promises a commit-and-push step that was never built.

This ticket only removes and tidies. No refusal, verdict, route or message that a role or an operator can reach changes. The one message whose wording changes cannot be reached through any command (Root cause, item 9).

## Evidence

Checked on `main` at `0ba4e4f`, from `~/dev/spec-factory`.

Each dead definition exists, and nothing in `factory/` or `tests/` names it:
```
$ grep -nE '^(def run_gates\(|STATES = |OPS = |def load_config\()' factory/gitops.py factory/store.py factory/specstore.py | wc -l
4
$ grep -rnF --include='*.py' -e 'gitops.run_gates' -e 'store.STATES' -e 'specstore.OPS' -e 'store.load_config' factory tests | wc -l
0
```
The first count shows the four definitions exist. The second shows no code refers to any of them. A wider grep for the bare names (`run_gates`, `STATES`, `OPS`, `prompt_name`) over `factory bin tests agents docs/design.md README.md` finds only the definitions and the `prompt_name` pair. The `*STATES` names elsewhere (`INTAKE_STATES`, `BUILD_STATES`, `IN_FLIGHT_STATES`) are different names. The Workflow scripts in `factory/workflows/`, which drive the roles in order, name none of them.

The setting nothing reads:
```
$ grep -rn --exclude-dir=__pycache__ force_push_allowed factory tests
factory/instance.template.yaml:45:force_push_allowed: false
tests/factory/test_instance.py:109:    assert cfg["integration_branch"] is None and ... and cfg["force_push_allowed"] is False
tests/factory/test_instance.py:354:                "force_push_allowed", "models", "ready_state", "routing"):
tests/factory/fixtures/instance/instance.yaml:22:force_push_allowed: false
$ grep -n 'rebase' factory/prompts/implementer.md
23:   merge main into the branch (never rebase: force-push is not allowed here),
```
The four hits are the template, a test fixture and two test assertions; none is code that acts on the value. The implementer's prompt answers the question itself. `factory/instance.py` (`load_config`, lines 88-90) loads the configuration file as a plain dict and does not check for unknown keys. The template is read only by `factory init` (`factory/cli.py:1304`), which sets up a new repository. So a repository already running the factory that keeps the key is unaffected. Two such repositories have it: this one (`.factory/instance.yaml:34`) and the Nanobot fork (line 65 of its `.factory/instance.yaml`).

`factory run start`, the command that begins a role run, has redundant lines (`factory/cli.py:199-240`):
```
$ grep -c prompt_name factory/cli.py                                          # :234 sets it, :236 is its only use
2
$ grep -c "already has run {t\[.in_flight.\]\[0\]} in flight" factory/cli.py  # :208 implementer, :212 triage to planner, :778 plan whole-spec
3
$ grep -c 'store.ensure_gitignore(root)' factory/cli.py                       # :229 every role; :377 inside _start_build_run, which :227 calls first; :1469 init
3
```
The refusals at `:207-208` and `:211-212` raise the same text. Their role sets do not overlap: `implementer`, and `triage, spec_writer, critic, planner`. Between them sits the reviewer and verifier check at `:209-210`, which has its own text and stays. The third count shows the write of the store's `.gitignore` block runs twice when a build role starts.

Blank lines, and stale text:
```
$ awk 'FNR==1{n=0} /^$/{n++; if(n==3) print FILENAME":"FNR; next} {n=0}' factory/*.py
factory/cli.py:1969
$ grep -nF -e 'commit-and-push' -e 'live pilot store is unaffected' -e 'not supported yet' factory/*.py
factory/store.py:3:Every write goes through here so a later sub-ticket can add commit-and-push in one place.
factory/specstore.py:9:behaviour (specs pinned as one text), so the live pilot store is unaffected.
factory/compose.py:420:        raise store.Refused(f"compose: role {role} not supported yet")
```
The awk hit is the third of four blank lines at `factory/cli.py:1967-1970`; no other module has three in a row. Nothing in the harness pushes (`factory/gitops.py:5-6`: "Nothing here pushes."). Both stores in use have the requirement folder `openspec/`, so "the live pilot store" no longer names a store without one.

`gitops.repo_root` ignores its argument:
```
$ sed -n 18,19p factory/gitops.py
def repo_root(cfg: dict | None = None) -> Path:
    return instance.repo_root()
$ grep -n 'repo_root(cfg' factory/*.py | wc -l     # the definition plus 12 callers
13
```
The 12 callers are `factory/compose.py:110` and `factory/cli.py` lines 256, 328, 375, 438, 548, 841, 942, 970, 1219, 1696 and 1724. Triage counted 14; the grep above gives 12.

Baseline checks, each run through the running-code wrapper:
```
$ uvx ruff check --select F401,F841 factory tests
All checks passed!
$ uv run --frozen pytest -q -p no:cacheprovider tests/factory | tail -1
577 passed in 264.38s (0:04:24)
```
Today there are no unused imports or variables, and the whole harness suite passes.

The refusal of a second triage run while the first is still running, tried black box on a throwaway repository. Scenario "A second intake run on a ticket is refused with the same text" runs this:
```
T-0001 already has run run-0001-triage in flight
exit=2
run-0001-triage
```
The second start is refused with exit 2, and only the first run's directory exists.

Current truth is the set of archived requirement files: when a change merges, its requirements are copied into `.factory/store/openspec/specs/<capability>/spec.md`. Opened: `.factory/store/openspec/specs/harness-suite/spec.md`, for the form of the suite command. No current-truth requirement covers run start's in-flight refusal: `grep -rl 'already has run' .factory/store/openspec/specs/` lists no file. That is why this change adds one to build-dispatch.

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

