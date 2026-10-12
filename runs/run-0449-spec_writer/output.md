=== proposal.md
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

## Responses

- [BLOCKING] 6 Decisions, first bullet → FIXED. The bullet now opens by glossing the spec store (the folder of requirement files that says what the harness does), a capability (a named area of behaviour, with build-dispatch as the example), and triage (the first role, which accepts the request). It quotes the store's refusal text instead of using "delta part" as a term. Evidence's last paragraph now glosses "current truth" (the archived requirement files) at its first use. While there, I also glossed the other factory names in the human sections: role, ticket store, the per-repository configuration file and its template, `factory run start`, `factory init`, the Workflow scripts, `_start_build_run` and compose. I also added a line after each Evidence output saying what it shows (writing standard rule 5).
- [SHOULD-FIX] 1 Evidence, last paragraph → FIXED. Both paths now read `.factory/store/openspec/specs/...`. I re-ran the check from `~/dev/spec-factory` at `0ba4e4f`: `ls .factory/store/openspec/specs/` lists 14 capabilities, including `harness-suite`, and `grep -rln 'already has run' .factory/store/openspec/specs/` lists no file (exit 1).
- [NIT] 1 Root cause item 12 and Design C, last bullet → FIXED. Both now say `:1967-1970`. Confirmed with `awk 'NR>=1966&&NR<=1971'`: line 1966 is `return ap`, lines 1967-1970 are empty and line 1971 is the fence comment. The Evidence paragraph and the Acceptance line for the blank-lines scenario now say the awk hit at `:1969` is the third of those four lines.

No scenario, command or expected result changed from v1. The critic ran each NEW scenario on `0ba4e4f` and got the "today" values listed above.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high; the three findings were wording and line-number fixes, and I re-checked each one on `0ba4e4f` (`git rev-parse --short HEAD` = `0ba4e4f`, the blank-line awk, and the store path listing and grep).
ESCALATIONS: none
