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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0229-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0229-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v3)

=== proposal.md
## Problem
Any agent that the factory starts to work on a ticket can change the factory's live records for the repository it is working in. Such an agent is a role run. It can do this by running the harness's own command-line tool, `bin/factory`, from anywhere inside that repository.

Each repository the factory works on has an instance: the factory's configuration and records for that repository, kept in the repository's `.factory/` directory. The live records are the live store: the instance's own store under `.factory/state/`. It holds the tickets, the run records, the event log and the spec store, and it decides what the factory does next. Two parties are meant to write it. One is the dispatcher, the workflow script that starts role runs and records their results; it writes through a helper agent called the clerk, which runs one tool command at a time. The other is the human operator, together with the runner sessions that launch workflows for the operator.

Nothing stops a role run from writing it as well. The tool finds its store by walking up from the directory it is run in. A role's shell starts inside the target repository, and so do its scratch directory and the temporary directories of the tests it runs. Role runs already get a throwaway home directory, but that does not help here, because the store is not under the home directory.

This has already happened here. This repository is itself a target of the factory, and its instance is called instance B. On 2026-10-04 a spec-writer role run ran the harness's test suite with its temporary directory set inside its scratch directory. One test runs the tool's `init` command and expects it to be refused outside a git repository. Instead, the command found instance B and initialised its live store. That created three things:
- a spec store, the record of what the system currently does. The factory calls that record current truth, and each closed ticket's spec is archived into it.
- `decisions.md`, the store's standing decision log. Later spec writers, critics and planners read it.
- six agent definition files, which would have changed every later Claude Code session started in this repository.

The agent files were removed by hand. The spec store and the decision log are still in use, and one later ticket has already closed into current truth.

Two parties are affected. The operator's store can be changed by an agent, and nothing records which run made the change. Every later ticket on that instance is also affected, because its routing depends on what the store holds.

The change adds a fence to the tool. While any role run is in flight on a live store, meaning started and not yet finished, the tool refuses every command that could write that store. A command is let through if it carries the marker `FACTORY_DISPATCH=1` in its environment. The dispatcher puts the marker on every clerk command. The operator puts it in front of a single command when they must write during a run. The operator has decided to keep the spec store the incident created.

## Evidence
- **The event.** The store log records a `store.initialised` event with no run attached: `.factory/state/log/2026-10.jsonl:995`, `"ts": "2026-10-04T13:35:44+00:00"`. Its files are `openspec/config.yaml`, `openspec/schemas/spec-factory/schema.yaml` and `decisions.md`. Its `agents` are six `/Users/dphang/dev/spec-factory/.claude/agents/factory-*.md` paths.
- **The run.** Only run-0196 was in flight then (`runs/run-0196-spec_writer/meta.yaml`: started `13:16:09`, finished `13:47:49`, ticket T-0023). Its own escalation (`log/2026-10.jsonl:997`) gives the route: "I set `TMPDIR` inside my scratch directory, which is inside this repository. The suite's `test_init_refused_outside_a_git_work_tree` then ran `init` against this repo's instance on its own store." That test runs `bin/factory init` as a subprocess from its temporary directory (`tests/factory/test_instance.py:25-32`, `:132-137`). A second spec-writer run, run-0198, repeated the test the same way (`log/2026-10.jsonl:1006`). It wrote nothing new only because the files already existed.
- **The lasting effect.** `.factory/state/openspec/specs/` now holds six capabilities: build-dispatch, harness-docs, harness-suite, human-resolution, store-setup and sub-ticket-planning. Commit `81294c8` says that T-0023 "closed by archive into current truth" and that the spec store "was created by a stray 'factory init' from intake run-0196". Before the incident, this instance's tickets closed as applied, meaning they were marked done with no archive step, because there was no spec store (`dev/issues.md:19`). This instance was never meant to have agent files (`.factory/state/specs/T-0012/v1.md:71`). `ls ~/dev/spec-factory/.claude` prints "No such file or directory", so they are gone now. A repeat of the suite route would write them again.
- **Reproduced on this checkout (base `3a3f58c`).** I ran the scenarios of this change on a clean clone of base and on a clone carrying a prototype of parts A and B (below), with `TMPDIR` in this run's scratch directory and a fresh `HOME`. The previous version's prototype was gone, so I rebuilt it for this version. The first scenario under live-store-guard printed `init=0 new=0 transition=0 decision=0 store=changed agents=written` on base. That means `init`, `ticket new`, `ticket transition` and `decision add` all succeeded from a subdirectory of a target with a run in flight, and `init` wrote the agent files again. On the prototype it printed `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`: every write was refused and nothing changed.
- **The suite route, reproduced (previous version's run, not repeated for this one).** I set up a scratch target with a triage run in flight on its own store, then deleted its agent files and spec store. Then I ran only `test_init_refused_outside_a_git_work_tree` with `TMPDIR` inside that target. Base printed `1 failed` with `agents=written specstore=written`: `init` succeeded and rewrote both. The prototype printed `1 failed` with `agents=none specstore=none`. Its assertion message shows `init` refused with `role runs may not write the live store (<target>/.factory/state; in flight: run-0001-triage); use a throwaway FACTORY_STATE`. The test still fails, because it expects a different refusal; that test's assumption is out of scope.
- **Prototype size and suite.** The prototype is 20 added lines in `factory/cli.py` and one changed line in each workflow script. The harness suite gave `254 passed` on base in the previous version's run, with `TMPDIR` under `/tmp` as the current-truth suite scenario does. On the prototype, with `FACTORY_DISPATCH` added to the test file's stripped variables but the one test not yet marked, and with the marker exported in the calling shell, it gave `1 failed, 253 passed`. The failure was `test_composed_input_opens_with_the_instance_context` (see Tests to change). That shows an exported marker no longer hides the missing change. With the test marked it gave `254 passed`, and `tests/factory/test_instance.py` alone, with the marker exported, gave `22 passed`.
- **Negative control for the marker.** I committed the prototype with the marker removed from `intake.js` only. The end-to-end scenario, "An intake run against a real store reaches its end with its run in flight", then printed `returned=parked stored=ready-for-triage` instead of `returned=closed stored=closed`: the clerk's own `run finish` was refused. So the marker is what lets the dispatcher through, and that scenario detects a missing marker.
- **The marker does not get past the harness lock.** In a harness clone with an uncommitted edit, on a target with a run in flight, an unmarked `decision add` was refused by the fence (`role runs may not write the live store ...`). The same command marked was refused by the lock (`has uncommitted changes:`), exit 2 both times. Base refuses the marked command the same way, so the new scenario for this is a regression check.
- **The operator writes while runs are in flight.** This happened twice today on this store:
  - T-0025 was filed at `17:50:05` (`log/2026-10.jsonl:1122-1123`) while run-0220 was in flight (`:1121`).
  - The operator's answer to this ticket was recorded at `18:15:46-47` (`:1137-1139`) while run-0223-critic was in flight (started `18:13:51`, finished `18:21:01`, `:1136` and `:1141`).

  Under this change, both commands need the marker.
- **The requester's proposed exemption for humans does not match the code.** Human commands take no `--by`. `approve-spec`, `request-changes`, `resolve` and `decision add` record the operating-system user name (`factory/cli.py:638-639`, `_by()`). `ticket transition` requires `--by` on every call (`factory/cli.py:1063`), so a role would supply it too.
- **Three commands that look like reads write the store.** `ticket ready-implementers` saves sub-tickets and logs transitions (`factory/cli.py:434`, body lines 13-14). `ticket parent-check` saves the parent (`:619`, body lines 11-12). `spec tasks` writes a file and logs (`:917`). `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` call no store writer.
- **No marked command starts a test run.** Apart from `run_gates`, every subprocess the harness package starts is `git` (`factory/cli.py:822`, `factory/gitops.py:32` and `:80`, `factory/instance.py:112` and `:125`). `run_gates` (`factory/gitops.py:165`), which would run gate commands, has no caller (`grep -rn run_gates factory/` finds only its definition). So the marker on a clerk command does not reach a test suite's subprocesses.
- **Part A does not exist yet.** `grep -rn FACTORY_DISPATCH` finds nothing in `factory/`, `bin/`, `docs/`, `dev/` or `.factory/instance.yaml`, and nothing in `~/dev/nanobot-upstream/factory` or `.factory`.

## Root cause
- `factory/instance.py:55` `find()`: when `FACTORY_INSTANCE` is unset, the instance is the nearest `.factory/instance.yaml` above the caller's directory. Any directory inside the repository resolves to the live instance. That includes a role's scratch directory, `runs/<id>/scratch/` inside the store, and any temporary directory under it.
- `factory/cli.py:1193` `main()` and `factory/cli.py:845` `init_cmd()` check only the harness lock and the uncommitted-edit refusal (`instance.guard`, `factory/instance.py:141`) before writing the live store. Neither asks whether a role run is in flight or who is calling. `init_cmd` takes its instance from the git top level of the caller's directory and copies the agent files at `factory/cli.py:885`.
- The suite's `test_init_refused_outside_a_git_work_tree` (`tests/factory/test_instance.py:132`) assumes its temporary directory lies outside every repository. The scratch rule puts a role's temporary files inside the store, which is inside the repository. Together these turned a refusal test into a live `init`.

## Out of scope
- The test suite's assumption that its temporary directory lies outside every repository. run-0198 suggested a guard in the suite, and that needs its own issue. After this change, the test fails without writing the live store.
- Writes that bypass `bin/factory`, such as an editor or a shell redirect into `.factory/`. `.factory/**` is already a protected path in every role's rules. Isolating role runs at the operating-system level is issue #37.
- The other routes the fence does not reach, listed under Risk.
- Part B of the request (a preamble line telling roles to use a throwaway store) is cut. See Decisions.
- Part C of the request (the tripwire watching the store root) is cut. See Decisions.
- The clerk agent definition (`agents/factory-clerk.md`), the shared preamble and its copies (`factory/prompts/preamble.md`, `docs/prompts/00-preamble.md`), and `dev/build-harness.spec.md` do not change. The build spec describes none of the comparable later guards: `grep -n -i "tripwire\|accept-harness\|uncommitted" dev/build-harness.spec.md` finds only an unrelated "uncommitted scripts" line (`:101`).
- Logging refused attempts. A refusal writes nothing, as every other refusal does.

## Open questions
none

## Decisions
- Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
- While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
- The fence acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
- The fence checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
- The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
- A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
- The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<store>; in flight: <run ids>); use a throwaway FACTORY_STATE`.
- A run left in flight by a dead workflow keeps the fence up. The operator clears it with a marked `run finish <run> --status-override KILLED`, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
- The fence guards against accidents, not against a determined agent. A role that reads the workflow scripts or README can copy the marker. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37, a separate investigation.
- The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
- Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
- Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.

## Risk
- **Blast radius.** Every target that runs this harness: this repository (instance B), and the Nanobot fork (instance A) after it upgrades. While a run is in flight there, any runner or operator command that writes the live store without the marker is refused with exit 2. That includes filing a ticket, `resolve`, `decision add`, `approve-spec`, `ticket set`, and `--accept-harness` on any command. The workflow scripts carry the marker, so intake and build are unaffected. A refused command writes nothing, so the failure is loud and safe.
- **Where the fence does not reach.** These routes stay open after this change:

  | Route | Why the fence misses it | What still limits it |
  |---|---|---|
  | A process a role left running after its run finished, such as a background test run (#41) | Once no run is in flight, the store is idle and unfenced | Short windows in practice: a workflow starts the next run seconds after the last one finishes |
  | A killed run that the operator clears while its agent is still running | Same: clearing the run drops it from the in-flight list | The operator clears a run only after its workflow has stopped |
  | A role inside a code checkout (an implementer's worktree or a checker's checkout, under `<store>/worktrees/`, `factory/gitops.py:6`) | The walk-up finds the checkout's own tracked copy of `.factory/`, not the live one. Committed copies carry no in-flight runs (none at `HEAD`) | Such a write lands in the checkout. It reaches the live store only through a merged commit under `.factory/**`, a protected path the reviewer checks. #46 (T-0025) would take the store out of code checkouts |
  | A shell that exports `FACTORY_DISPATCH=1` before Claude Code starts | Every role run inherits the variable, so the fence is off without notice | README says to prefix one command and never to export it |
  | A role writing the files directly, not through `bin/factory` | The fence lives in the tool | `.factory/**` is protected in every role's rules. #37 |
  | A role run of one instance writing another instance that has nothing in flight | That store is idle | Out of scope |

- **Interaction with the tripwire (#38).** None. The tripwire compares the files it lists inside `run finish` and inside a `ticket set` that drops a run. Both are marked when the dispatcher sends them. An operator who clears a stale run with a marked command gets the same comparison as today.
- **Interaction with the store branch (#46, T-0025).** The fence reads in-flight runs from `tickets/*.yaml` under the store in use. It compares that store's path with the instance's own store path, which comes from `state_dir`. T-0025's v2 spec proposes B1: a `factory-store` git worktree at a new path, `.factory/store`. Under B1 the fence follows `state_dir` and needs no change. Under B2 (no working copy), the fence's read would have to move to whatever read path B2 gives the store. T-0025's own migration steps write the live store, so they run with nothing in flight or with the marker. Both changes touch `README.md`, `docs/design.md` and the changelog. The second to merge takes the next changelog number, and this spec's changelog scenario checks the last entry rather than a fixed number.
- **Not a security boundary.** See Decisions.
- **Protected paths this change touches:**
  - harness: `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`;
  - guardrail: one existing test and the `STRIP` tuple its file's helper uses, both in `tests/factory/test_instance.py` (Tests to change).
- **Not touched:** `.factory/**`, `agents/**`, `bin/factory`, `docs/prompts/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

## Operator steps
1. After merge, between builds, move the runtime and accept the new revision in each target, as README "Upgrading the runtime" says. Run the `--accept-harness` command when no run is in flight on that store, or with the marker in front of it.
2. Tell each runner session, the Nanobot Driver included, before its next intake or build: prefix a store write made during a run with `FACTORY_DISPATCH=1`, and never export it.

## Out-of-scope observations
- `README.md:102-103` says the parent-close verifier run is not listed as in flight. `run_start` appends every run to the ticket's in-flight list, parent-close included (`factory/cli.py:200` and `:231`). The fence relies on the code's behaviour. If the README sentence were true, the fence would be down during that run. The sentence looks stale and is not changed here.
- A role in a code checkout that runs `init` writes `.claude/agents/` in that checkout. `.claude/**` is not a protected path, so only review would stop such a commit.

=== design.md
## Proposed change
**A. The fence, in `factory/cli.py`.**
1. Add the read-only set as `(command, subcommand)` pairs: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths`.
2. "Runs in flight" are the union of the `in_flight` lists over `tickets/*.yaml` in the store in use. Sub-tickets are ticket files too.
3. Add one fence function that raises `Refused` when all of these hold:
   - the store in use is the instance's own (`instance.is_own_store`);
   - at least one run is in flight;
   - `os.environ.get("FACTORY_DISPATCH") != "1"`.

   The message is exactly `role runs may not write the live store (<store>; in flight: <comma-separated run ids>); use a throwaway FACTORY_STATE`. `main()`'s existing `Refused` handler gives exit 2, stderr and `{"ok": false, "error": ...}`.
4. In `main()`, after `root = store.state_root(cfg)` and before `instance.guard(...)`, call the fence when the command is not in the read-only set or `--accept-harness` was given. Calling it before the guard means a fenced `--accept-harness` rewrites no lock.
5. In `init_cmd`, call the fence right after `cfg` and `root` are loaded for an existing instance, before any write: `context.md`, `harness.lock`, agent files, `.gitignore`, `.gitattributes`, the spec store. A brand-new instance has no tickets, so `init` on a new repository is never fenced.
6. Add the new behaviour's tests in a new file, such as `tests/factory/test_live_store_guard.py`. Its subprocess helper drops `FACTORY_DISPATCH` from the inherited environment, so a runner that exported it cannot change the result.

**B. The marker, in the workflow scripts.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, start `ENV` with `'FACTORY_DISPATCH=1'`. Then `BIN`, and with it every clerk command, carries it unconditionally. The clerk needs no change.

**C. Documents.**
- `docs/design.md`: a new paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". It states:
  - the rule from A: live store only, in flight only, the read-only list, `--accept-harness`;
  - the `FACTORY_DISPATCH=1` marker, set by both workflow scripts, and the operator's per-command use of it;
  - the refusal: exit 2, writes nothing, names a throwaway `FACTORY_STATE`, never names the marker;
  - that it guards against accidents and is not isolation;
  - that the fence is checked before the harness lock, so a fenced command never reaches the lock or its `--accept-harness`, and a marked command still meets the lock unchanged.
- `docs/changelog.md`: one new entry, numbered after the current last entry (52 if nothing else lands first). It names `FACTORY_DISPATCH`, "in flight", the throwaway store and exit 2. It says that parts B and C of the request were declined, and why.
- `README.md`:
  - a "Built" bullet for the fence, saying it is tested and has not yet fired on a real ticket;
  - in "Where a human decides", one paragraph: while a run is in flight on a store, the operator puts `FACTORY_DISPATCH=1` in front of a write; a stale in-flight run is cleared with a marked `run finish <run> --status-override KILLED`; never export the marker;
  - in "Not built", rewrite the "Current truth for the factory itself" bullet: the spec store holds only the capabilities that tickets have changed since it was created, not the whole factory. Remove "never entered it" and quote no count, since each archive changes it;
  - bump the status date, per "Maintaining this page".
- `docs/prompts/` and `factory/prompts/` do not change.

## Tests to change
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context` (line 271; the call is at line 274). Its `run compose` call stands for the dispatcher's own command. It runs on a scratch instance's live store while the triage run that `_start_triage` just started is in flight, so the fence refuses it. Change: pass `FACTORY_DISPATCH="1"` to that one `cli(...)` call. Verified on the prototype: `1 failed, 253 passed` without this change, `254 passed` with it.
- The same file's `STRIP` tuple (`tests/factory/test_instance.py:21`), the variables its `cli()` helper drops from the inherited environment. Add `"FACTORY_DISPATCH"` to it. Without this, a runner shell that exported the marker would make the test above pass with or without its change, and every own-store case in the file would skip the fence. An explicit `FACTORY_DISPATCH="1"` argument still wins, because `cli()` applies its arguments after the strip. Verified on the prototype with the marker exported: `1 failed, 253 passed` before the test above was marked, `22 passed` for the file after.
- No other existing test changes.

=== specs/live-store-guard/spec.md
## ADDED Requirements
### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target, as a role's test or scratch directory would be.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $T/tgt/.factory/state/openspec $T/tgt/.factory/state/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Reads, marked commands, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands and every command with `FACTORY_DISPATCH=1` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced; with no run in flight, unmarked writes SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; echo "show=$s config=$c log=$l results=$r")`
- THEN it prints exactly `show=0 config=0 log=0 results=0`

#### Scenario: Marked commands still write while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced while the live one has a run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_STATE=$T/s $B init >/dev/null 2>&1; i=$?; FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

=== specs/build-dispatch/spec.md
## ADDED Requirements
### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` and `README.md` SHALL describe the dispatcher marker; README SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `4`

#### Scenario: The design doc and README name the marker, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') readme=$(grep -c FACTORY_DISPATCH README.md | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 readme=1 prompts=0`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance
- Unmarked writes from inside the target are refused while a run is in flight, init included → NEW. Today it prints `init=0 new=0 transition=0 decision=0 store=changed agents=written`: every write succeeds, and `init` writes the agent files again.
- The refusal names the throwaway store and not the marker → NEW. Today it prints `rule=0 state=0 marker=0 json=0`: the write succeeds, so there is no refusal text.
- A harness acceptance is refused while a run is in flight → NEW. Today it prints `accept=0 store=changed`: the lock is rewritten and a `harness.accepted` event is logged.
- Read commands still answer while a run is in flight → REGRESSION. Prints `show=0 config=0 log=0 results=0` on base and on the prototype.
- Marked commands still write while a run is in flight → REGRESSION. Prints `decision=0 finish=0 cleared=1` on base and on the prototype.
- A throwaway store is not fenced while the live one has a run in flight → REGRESSION. Prints `init=0 new=0` on base and on the prototype.
- With no run in flight, unmarked commands write as before → REGRESSION. Prints `new=0 decision=0` on base and on the prototype.
- A marked write from a harness checkout with an uncommitted edit is still refused → REGRESSION. Prints `exit=2 lock=1 store=unchanged` on base and on the prototype. It would catch an implementation that lets the marker skip the lock as well as the fence.
- Every clerk command of both workflows carries the marker → NEW. Today it prints `intake: sent unmarked=6`, then `build: sent unmarked=2`: no clerk command carries the marker.
- An intake run against a real store reaches its end with its run in flight → REGRESSION. Prints `returned=closed stored=closed` on base and on the prototype. With the fence but without the marker in `intake.js` it prints `returned=parked stored=ready-for-triage`, so this scenario catches a missing or partial part B.
- The changelog records the guard as its last entry → NEW. Today it prints `CONTIGUOUS`, then `2`: the last entry, 51, mentions only two of the four terms.
- The design doc and README name the marker, and no prompt copy changes → NEW. Today it prints `design=0 readme=0 prompts=0`.
- README no longer says the factory's capabilities never entered the spec store → NEW. Today it prints `bullet=1 stale=1` (`README.md:367`).
- The guard change adds no whitespace errors → REGRESSION. Prints `exit=0` on base.
- The gate suite (`uv run --frozen pytest -q -p no:cacheprovider tests/factory`) covers the test and helper listed under Tests to change. It is not a separate scenario.

All runtime scenarios were run for the previous version on a clean clone of base `3a3f58c` and on a prototype clone, each with a fresh `HOME` and a `TMPDIR` under that run's scratch directory. The critic re-ran five of them on base and got the "today" results above. For this version I rebuilt the prototype and re-ran, with a fresh `HOME` and `TMPDIR` under this run's scratch directory: the first scenario (prototype only), the marker count and the end-to-end scenario (base and prototype), the end-to-end negative control, the new lock scenario (base and prototype) and the harness suite (prototype). Each printed the result stated above. The three documentation scenarios that read the current files were run on base only. The changelog scenario counted 2 on base, and the README scenario printed `bullet=1 stale=1`.

## Responses
Round 2 critic findings:
- [BLOCKING] 6, Decisions use "instance B" and `decisions.md` unglossed → FIXED. Problem now says what an instance is, that this repository is a target of the factory whose instance is called instance B, and that `init` created `decisions.md`, the store's standing decision log that later spec writers, critics and planners read. Problem also names current truth at first use. Evidence glosses "closed as applied". Decisions no longer cite "Answer 1" or a bare "#37", and the Nanobot Driver is introduced as the session that runs instance A.
- [NIT] 2, `STRIP` does not drop `FACTORY_DISPATCH` → FIXED. Tests to change now lists adding `FACTORY_DISPATCH` to `STRIP` in `tests/factory/test_instance.py:21`. Verified on the rebuilt prototype with the marker exported: `1 failed, 253 passed` before the one test was marked, so the export no longer hides a missing change; `254 passed` after, and `22 passed` for that file with the marker exported.
- [NIT] 5, the fence before the lock changes which refusal a dirty checkout prints → FIXED. Design part C adds that sentence to the design-doc paragraph. Decisions gains a bullet stating the order and the rejected alternative: after the lock, a fenced `--accept-harness` would rewrite the lock before it was refused. A new REGRESSION scenario checks that a marked command still meets the lock's uncommitted-edit refusal. On the prototype an unmarked write from a dirty checkout with a run in flight gets the fence's refusal, and the same write marked gets the lock's.
- Critic's out-of-scope observation on the end-to-end scenario inheriting an exported marker: no change. As the critic notes, the first scenario fails in that case, so the set still catches a missing part B.

Changes from v1, applying the operator's first answer (kept from v2):
- Open questions 1 and 2 are now Decisions, as the operator answered them.
- README's stale "never entered it" line is corrected in this ticket, with a new scenario. This ticket is the next one to touch README.
- The operator's design questions for the critic are answered in the spec. Risk gains a table of routes the fence does not reach, including a write between runs, after a run dies, and an exported marker. It also states the interactions with #38 and #46. Decisions now cover a stale in-flight run and why the read-only list is closed.
- A new NEW scenario covers `--accept-harness` while a run is in flight.
- The changelog scenario checks the last entry, not entry 52, so it holds whichever of this change and T-0025 merges first.
- The operator step for removing the spec store is gone. Keep needs no step.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)

## Your prior findings (round 1)

## Spot checks (base `3a3f58c`, clean clone, fresh HOME, TMPDIR under this run's scratch)

Paths and symbols: `factory/instance.py:55` `find()`, `:105` `is_own_store`, `:141` `guard`; `factory/cli.py:845` `init_cmd`, `:885` agent copy, `:1193` `main()` with `root = store.state_root(cfg)` then `instance.guard(...)` at `:1201-1202`, `:638-639` `_by()`, `:1063` `--by` required, `:231` `in_flight.append`; `factory/workflows/intake.js:26` and `build.js:21` build `ENV`; `tests/factory/test_instance.py:25` `cli(cwd, *argv, **extra)` takes env overrides, `:132` `test_init_refused_outside_a_git_work_tree`, `:271-274` the test to change; `README.md:367` "never entered it", `README.md:102-103` the parent-close sentence; `docs/design.md:54` "**Tripwire on live files.**"; changelog last entry is 51; `grep -rn FACTORY_DISPATCH factory bin docs dev .factory/instance.yaml` finds nothing; `run_gates` has only its definition. All as cited.

Acceptance commands run on base, each matching the Acceptance section's "today" line:
- Unmarked writes: `init=0 new=0 transition=0 decision=0 store=changed agents=written`
- Harness acceptance: `accept=0 store=changed`
- Marked commands (REGRESSION): `decision=0 finish=0 cleared=1`
- Clerk marker count: `intake: sent unmarked=6`, `build: sent unmarked=2`
- README: `bullet=1 stale=1`; changelog: `CONTIGUOUS`, `2`

The negative control (marker removed from `intake.js` parks the intake) is the writer's result; I did not rebuild the prototype. The spec's fix shape follows from the code I read, so I accept it.

## Findings

[BLOCKING] 6 Decisions, first bullet
Problem: The first paragraph of Decisions uses two system-specific terms no earlier human-facing section glossed: "Instance B" (the Problem calls it only "this repository"; the gloss "this repository (instance B)" first appears under Risk, after Decisions) and `decisions.md` (Evidence names it only as a file `init` created).
Evidence: Read Problem, Evidence and Decisions in order as the gate operator; "instance B" is not in Problem or Evidence; `decisions.md` appears in Evidence bullet 1 with no statement of what it is.
Suggested fix: Write "Instance B, the factory instance of this repository, keeps the spec store ..." and "already in `decisions.md`, the store's standing decision log that later roles read".

[NIT] 2 Tests to change
Problem: The existing `cli()` helper's `STRIP` tuple (`tests/factory/test_instance.py:21`) does not drop `FACTORY_DISPATCH`, so under a shell that exported the marker the changed test passes with or without its one-line edit, while the new test file protects itself.
Evidence: `STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")`.
Suggested fix: Since that file is already under Tests to change, add `FACTORY_DISPATCH` to `STRIP` in the same edit, or say in Tests to change why it is left alone.

[NIT] 5 design.md A.4 / Risk
Problem: Placing the fence before `instance.guard` changes which refusal a dirty checkout prints when a run is in flight on an own store (fence text, not "has uncommitted changes"), which the `guard` docstring's "refused first" ordering and the harness-suite current truth describe without that case.
Evidence: `factory/instance.py:141-151` docstring; current-truth scenario "The uncommitted-edit refusal still holds" uses a target with no run in flight, so it keeps passing.
Suggested fix: One sentence in the design-doc paragraph (C) saying the fence is checked before the harness lock, so a fenced command never reaches the lock or its acceptance.

## Out-of-scope observations
- The end-to-end scenario (`t0024-e2e.mjs`) runs clerk commands with the environment unchanged, so an exported marker in the runner's shell would let it pass even if part B were missing; the first scenario would then fail instead, so the set as a whole still catches it.

STATUS: REVISE
CONFIDENCE: high, every cited path and five acceptance commands checked on a clean clone of base; the only block is a first-use gloss the rubric names as blocking.
ESCALATIONS: none

## Previous spec version (v2)

=== proposal.md
## Problem
Any agent that the factory starts to work on a ticket can change the factory's live records for the repository it is working in. Such an agent is a role run. It can do this by running the harness's own command-line tool, `bin/factory`, from anywhere inside that repository.

The live records are the live store: the instance's own store under `.factory/state/`. It holds the tickets, the run records, the event log and the spec store, and it decides what the factory does next. Two parties are meant to write it. One is the dispatcher, the workflow script that starts role runs and records their results; it writes through a helper agent called the clerk, which runs one tool command at a time. The other is the human operator, together with the runner sessions that launch workflows for the operator.

Nothing stops a role run from writing it as well. The tool finds its store by walking up from the directory it is run in. A role's shell starts inside the target repository, and so do its scratch directory and the temporary directories of the tests it runs. Role runs already get a throwaway home directory, but that does not help here, because the store is not under the home directory.

This has already happened on this repository. On 2026-10-04 a spec-writer role run ran the harness's test suite with its temporary directory set inside its scratch directory. One test runs the tool's `init` command and expects it to be refused outside a git repository. Instead, the command found this repository's live instance and initialised it. That created two things:
- a spec store, the record of what the system currently does, into which later tickets are archived;
- six agent definition files, which would have changed every later Claude Code session started in this repository.

The agent files were removed by hand. The spec store is still in use, and one later ticket has already closed into it.

Two parties are affected. The operator's store can be changed by an agent, and nothing records which run made the change. Every later ticket on that instance is also affected, because its routing depends on what the store holds.

The change adds a fence to the tool. While any role run is in flight on a live store, meaning started and not yet finished, the tool refuses every command that could write that store. A command is let through if it carries the marker `FACTORY_DISPATCH=1` in its environment. The dispatcher puts the marker on every clerk command. The operator puts it in front of a single command when they must write during a run. The operator has decided to keep the spec store the incident created.

## Evidence
- **The event.** The store log records a `store.initialised` event with no run attached: `.factory/state/log/2026-10.jsonl:995`, `"ts": "2026-10-04T13:35:44+00:00"`. Its files are `openspec/config.yaml`, `openspec/schemas/spec-factory/schema.yaml` and `decisions.md`. Its `agents` are six `/Users/dphang/dev/spec-factory/.claude/agents/factory-*.md` paths.
- **The run.** Only run-0196 was in flight then (`runs/run-0196-spec_writer/meta.yaml`: started `13:16:09`, finished `13:47:49`, ticket T-0023). Its own escalation (`log/2026-10.jsonl:997`) gives the route: "I set `TMPDIR` inside my scratch directory, which is inside this repository. The suite's `test_init_refused_outside_a_git_work_tree` then ran `init` against this repo's instance on its own store." That test runs `bin/factory init` as a subprocess from its temporary directory (`tests/factory/test_instance.py:25-32`, `:132-137`). A second spec-writer run, run-0198, repeated the test the same way (`log/2026-10.jsonl:1006`). It wrote nothing new only because the files already existed.
- **The lasting effect.** `.factory/state/openspec/specs/` now holds six capabilities: build-dispatch, harness-docs, harness-suite, human-resolution, store-setup and sub-ticket-planning. Commit `81294c8` says that T-0023 "closed by archive into current truth" and that the spec store "was created by a stray 'factory init' from intake run-0196". Before the incident, this instance's tickets closed as applied because there was no spec store (`dev/issues.md:19`). This instance was never meant to have agent files (`.factory/state/specs/T-0012/v1.md:71`). `ls ~/dev/spec-factory/.claude` prints "No such file or directory", so they are gone now. A repeat of the suite route would write them again.
- **Reproduced on this checkout (base `3a3f58c`).** I ran every scenario of this change on a clean clone of base and on a clone carrying a prototype of parts A and B (below), with `TMPDIR` in this run's scratch directory and a fresh `HOME`. The first scenario under live-store-guard printed `init=0 new=0 transition=0 decision=0 store=changed agents=written` on base. That means `init`, `ticket new`, `ticket transition` and `decision add` all succeeded from a subdirectory of a target with a run in flight, and `init` wrote the agent files again. On the prototype it printed `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`.
- **The suite route, reproduced.** I set up a scratch target with a triage run in flight on its own store, then deleted its agent files and spec store. Then I ran only `test_init_refused_outside_a_git_work_tree` with `TMPDIR` inside that target. Base printed `1 failed` with `agents=written specstore=written`: `init` succeeded and rewrote both. The prototype printed `1 failed` with `agents=none specstore=none`. Its assertion message shows `init` refused with `role runs may not write the live store (<target>/.factory/state; in flight: run-0001-triage); use a throwaway FACTORY_STATE`. The test still fails, because it expects a different refusal; that test's assumption is out of scope.
- **Prototype size and suite.** The prototype is 21 added lines in `factory/cli.py` and one changed line in each workflow script. The harness suite, run with `TMPDIR` under `/tmp` as the current-truth suite scenario does, gave `254 passed` on base. On the prototype it gave `1 failed, 253 passed`. The failure was `test_composed_input_opens_with_the_instance_context` (see Tests to change). After the one-line change listed there it gave `254 passed`.
- **Negative control for the marker.** I committed the prototype with the marker removed from `intake.js` only. The end-to-end scenario, "An intake run against a real store reaches its end with its run in flight", then printed `returned=parked stored=ready-for-triage` instead of `returned=closed stored=closed`: the clerk's own `run finish` was refused. So the marker is what lets the dispatcher through, and that scenario detects a missing marker.
- **The operator writes while runs are in flight.** This happened twice today on this store:
  - T-0025 was filed at `17:50:05` (`log/2026-10.jsonl:1122-1123`) while run-0220 was in flight (`:1121`).
  - The operator's answer to this ticket was recorded at `18:15:46-47` (`:1137-1139`) while run-0223-critic was in flight (started `18:13:51`, finished `18:21:01`, `:1136` and `:1141`).

  Under this change, both commands need the marker.
- **The requester's proposed exemption for humans does not match the code.** Human commands take no `--by`. `approve-spec`, `request-changes`, `resolve` and `decision add` record the operating-system user name (`factory/cli.py:638-639`, `_by()`). `ticket transition` requires `--by` on every call (`factory/cli.py:1063`), so a role would supply it too.
- **Three commands that look like reads write the store.** `ticket ready-implementers` saves sub-tickets and logs transitions (`factory/cli.py:434`, body lines 13-14). `ticket parent-check` saves the parent (`:619`, body lines 11-12). `spec tasks` writes a file and logs (`:917`). `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` call no store writer.
- **No marked command starts a test run.** Apart from `run_gates`, every subprocess the harness package starts is `git` (`factory/cli.py:822`, `factory/gitops.py:32` and `:80`, `factory/instance.py:112` and `:125`). `run_gates` (`factory/gitops.py:165`), which would run gate commands, has no caller (`grep -rn run_gates factory/` finds only its definition). So the marker on a clerk command does not reach a test suite's subprocesses.
- **Part A does not exist yet.** `grep -rn FACTORY_DISPATCH` finds nothing in `factory/`, `bin/`, `docs/`, `dev/` or `.factory/instance.yaml`, and nothing in `~/dev/nanobot-upstream/factory` or `.factory`.

## Root cause
- `factory/instance.py:55` `find()`: when `FACTORY_INSTANCE` is unset, the instance is the nearest `.factory/instance.yaml` above the caller's directory. Any directory inside the repository resolves to the live instance. That includes a role's scratch directory, `runs/<id>/scratch/` inside the store, and any temporary directory under it.
- `factory/cli.py:1193` `main()` and `factory/cli.py:845` `init_cmd()` check only the harness lock and the uncommitted-edit refusal (`instance.guard`, `factory/instance.py:141`) before writing the live store. Neither asks whether a role run is in flight or who is calling. `init_cmd` takes its instance from the git top level of the caller's directory and copies the agent files at `factory/cli.py:885`.
- The suite's `test_init_refused_outside_a_git_work_tree` (`tests/factory/test_instance.py:132`) assumes its temporary directory lies outside every repository. The scratch rule puts a role's temporary files inside the store, which is inside the repository. Together these turned a refusal test into a live `init`.

## Out of scope
- The test suite's assumption that its temporary directory lies outside every repository. run-0198 suggested a guard in the suite, and that needs its own issue. After this change, the test fails without writing the live store.
- Writes that bypass `bin/factory`, such as an editor or a shell redirect into `.factory/`. `.factory/**` is already a protected path in every role's rules. Isolating role runs at the operating-system level is issue #37.
- The other routes the fence does not reach, listed under Risk.
- Part B of the request (a preamble line telling roles to use a throwaway store) is cut. See Decisions.
- Part C of the request (the tripwire watching the store root) is cut. See Decisions.
- The clerk agent definition (`agents/factory-clerk.md`), the shared preamble and its copies (`factory/prompts/preamble.md`, `docs/prompts/00-preamble.md`), and `dev/build-harness.spec.md` do not change. The build spec describes none of the comparable later guards: `grep -n -i "tripwire\|accept-harness\|uncommitted" dev/build-harness.spec.md` finds only an unrelated "uncommitted scripts" line (`:101`).
- Logging refused attempts. A refusal writes nothing, as every other refusal does.

## Open questions
none

## Decisions
- Instance B keeps the spec store run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner (operator, Answer 1; already in `decisions.md`). This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as the answer directs.
- While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker (operator, Answer 1; already in `decisions.md`). This is a standing decision for every runner session, the Nanobot Driver included.
- The fence acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's second answer assumes unmarked writes when nothing is in flight.
- The fence checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
- The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
- A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
- The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<store>; in flight: <run ids>); use a throwaway FACTORY_STATE`.
- A run left in flight by a dead workflow keeps the fence up. The operator clears it with a marked `run finish <run> --status-override KILLED`, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
- The fence guards against accidents, not against a determined agent. A role that reads the workflow scripts or README can copy the marker. That is recorded under Risk rather than designed around. Isolation is #37.
- Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
- Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.

## Risk
- **Blast radius.** Every target that runs this harness: this repository (instance B), and the Nanobot fork (instance A) after it upgrades. While a run is in flight there, any runner or operator command that writes the live store without the marker is refused with exit 2. That includes filing a ticket, `resolve`, `decision add`, `approve-spec`, `ticket set`, and `--accept-harness` on any command. The workflow scripts carry the marker, so intake and build are unaffected. A refused command writes nothing, so the failure is loud and safe.
- **Where the fence does not reach.** These routes stay open after this change:

  | Route | Why the fence misses it | What still limits it |
  |---|---|---|
  | A process a role left running after its run finished, such as a background test run (#41) | Once no run is in flight, the store is idle and unfenced | Short windows in practice: a workflow starts the next run seconds after the last one finishes |
  | A killed run that the operator clears while its agent is still running | Same: clearing the run drops it from the in-flight list | The operator clears a run only after its workflow has stopped |
  | A role inside a code checkout (an implementer's worktree or a checker's checkout, under `<store>/worktrees/`, `factory/gitops.py:6`) | The walk-up finds the checkout's own tracked copy of `.factory/`, not the live one. Committed copies carry no in-flight runs (none at `HEAD`) | Such a write lands in the checkout. It reaches the live store only through a merged commit under `.factory/**`, a protected path the reviewer checks. #46 (T-0025) would take the store out of code checkouts |
  | A shell that exports `FACTORY_DISPATCH=1` before Claude Code starts | Every role run inherits the variable, so the fence is off without notice | README says to prefix one command and never to export it |
  | A role writing the files directly, not through `bin/factory` | The fence lives in the tool | `.factory/**` is protected in every role's rules. #37 |
  | A role run of one instance writing another instance that has nothing in flight | That store is idle | Out of scope |

- **Interaction with the tripwire (#38).** None. The tripwire compares the files it lists inside `run finish` and inside a `ticket set` that drops a run. Both are marked when the dispatcher sends them. An operator who clears a stale run with a marked command gets the same comparison as today.
- **Interaction with the store branch (#46, T-0025).** The fence reads in-flight runs from `tickets/*.yaml` under the store in use. It compares that store's path with the instance's own store path, which comes from `state_dir`. T-0025's v2 spec proposes B1: a `factory-store` git worktree at a new path, `.factory/store`. Under B1 the fence follows `state_dir` and needs no change. Under B2 (no working copy), the fence's read would have to move to whatever read path B2 gives the store. T-0025's own migration steps write the live store, so they run with nothing in flight or with the marker. Both changes touch `README.md`, `docs/design.md` and the changelog. The second to merge takes the next changelog number, and this spec's changelog scenario checks the last entry rather than a fixed number.
- **Not a security boundary.** See Decisions.
- **Protected paths this change touches:**
  - harness: `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`;
  - guardrail: one existing test, `tests/factory/test_instance.py` (Tests to change).
- **Not touched:** `.factory/**`, `agents/**`, `bin/factory`, `docs/prompts/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

## Operator steps
1. After merge, between builds, move the runtime and accept the new revision in each target, as README "Upgrading the runtime" says. Run the `--accept-harness` command when no run is in flight on that store, or with the marker in front of it.
2. Tell each runner session, the Nanobot Driver included, before its next intake or build: prefix a store write made during a run with `FACTORY_DISPATCH=1`, and never export it.

## Out-of-scope observations
- `README.md:102-103` says the parent-close verifier run is not listed as in flight. `run_start` appends every run to the ticket's in-flight list, parent-close included (`factory/cli.py:200` and `:231`). The fence relies on the code's behaviour. If the README sentence were true, the fence would be down during that run. The sentence looks stale and is not changed here.
- A role in a code checkout that runs `init` writes `.claude/agents/` in that checkout. `.claude/**` is not a protected path, so only review would stop such a commit.

=== design.md
## Proposed change
**A. The fence, in `factory/cli.py`.**
1. Add the read-only set as `(command, subcommand)` pairs: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths`.
2. "Runs in flight" are the union of the `in_flight` lists over `tickets/*.yaml` in the store in use. Sub-tickets are ticket files too.
3. Add one fence function that raises `Refused` when all of these hold:
   - the store in use is the instance's own (`instance.is_own_store`);
   - at least one run is in flight;
   - `os.environ.get("FACTORY_DISPATCH") != "1"`.

   The message is exactly `role runs may not write the live store (<store>; in flight: <comma-separated run ids>); use a throwaway FACTORY_STATE`. `main()`'s existing `Refused` handler gives exit 2, stderr and `{"ok": false, "error": ...}`.
4. In `main()`, after `root = store.state_root(cfg)` and before `instance.guard(...)`, call the fence when the command is not in the read-only set or `--accept-harness` was given. Calling it before the guard means a fenced `--accept-harness` rewrites no lock.
5. In `init_cmd`, call the fence right after `cfg` and `root` are loaded for an existing instance, before any write: `context.md`, `harness.lock`, agent files, `.gitignore`, `.gitattributes`, the spec store. A brand-new instance has no tickets, so `init` on a new repository is never fenced.
6. Add the new behaviour's tests in a new file, such as `tests/factory/test_live_store_guard.py`. Its subprocess helper drops `FACTORY_DISPATCH` from the inherited environment, so a runner that exported it cannot change the result.

**B. The marker, in the workflow scripts.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, start `ENV` with `'FACTORY_DISPATCH=1'`. Then `BIN`, and with it every clerk command, carries it unconditionally. The clerk needs no change.

**C. Documents.**
- `docs/design.md`: a new paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". It states:
  - the rule from A: live store only, in flight only, the read-only list, `--accept-harness`;
  - the `FACTORY_DISPATCH=1` marker, set by both workflow scripts, and the operator's per-command use of it;
  - the refusal: exit 2, writes nothing, names a throwaway `FACTORY_STATE`, never names the marker;
  - that it guards against accidents and is not isolation.
- `docs/changelog.md`: one new entry, numbered after the current last entry (52 if nothing else lands first). It names `FACTORY_DISPATCH`, "in flight", the throwaway store and exit 2. It says that parts B and C of the request were declined, and why.
- `README.md`:
  - a "Built" bullet for the fence, saying it is tested and has not yet fired on a real ticket;
  - in "Where a human decides", one paragraph: while a run is in flight on a store, the operator puts `FACTORY_DISPATCH=1` in front of a write; a stale in-flight run is cleared with a marked `run finish <run> --status-override KILLED`; never export the marker;
  - in "Not built", rewrite the "Current truth for the factory itself" bullet: the spec store holds only the capabilities that tickets have changed since it was created, not the whole factory. Remove "never entered it" and quote no count, since each archive changes it;
  - bump the status date, per "Maintaining this page".
- `docs/prompts/` and `factory/prompts/` do not change.

## Tests to change
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context` (line 271; the call is at line 274). Its `run compose` call stands for the dispatcher's own command. It runs on a scratch instance's live store while the triage run that `_start_triage` just started is in flight, so the fence refuses it. Change: pass `FACTORY_DISPATCH="1"` to that one `cli(...)` call. Verified on the prototype: `1 failed, 253 passed` without this change, `254 passed` with it. No other existing test changes.

=== specs/live-store-guard/spec.md
## ADDED Requirements
### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target, as a role's test or scratch directory would be.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $T/tgt/.factory/state/openspec $T/tgt/.factory/state/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Reads, marked commands, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands and every command with `FACTORY_DISPATCH=1` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced; with no run in flight, unmarked writes SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; echo "show=$s config=$c log=$l results=$r")`
- THEN it prints exactly `show=0 config=0 log=0 results=0`

#### Scenario: Marked commands still write while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced while the live one has a run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_STATE=$T/s $B init >/dev/null 2>&1; i=$?; FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

=== specs/build-dispatch/spec.md
## ADDED Requirements
### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` and `README.md` SHALL describe the dispatcher marker; README SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `4`

#### Scenario: The design doc and README name the marker, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') readme=$(grep -c FACTORY_DISPATCH README.md | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 readme=1 prompts=0`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance
- Unmarked writes from inside the target are refused while a run is in flight, init included → NEW. Today it prints `init=0 new=0 transition=0 decision=0 store=changed agents=written`: every write succeeds, and `init` writes the agent files again.
- The refusal names the throwaway store and not the marker → NEW. Today it prints `rule=0 state=0 marker=0 json=0`: the write succeeds, so there is no refusal text.
- A harness acceptance is refused while a run is in flight → NEW. Today it prints `accept=0 store=changed`: the lock is rewritten and a `harness.accepted` event is logged.
- Read commands still answer while a run is in flight → REGRESSION. Prints `show=0 config=0 log=0 results=0` on base and on the prototype.
- Marked commands still write while a run is in flight → REGRESSION. Prints `decision=0 finish=0 cleared=1` on base and on the prototype.
- A throwaway store is not fenced while the live one has a run in flight → REGRESSION. Prints `init=0 new=0` on base and on the prototype.
- With no run in flight, unmarked commands write as before → REGRESSION. Prints `new=0 decision=0` on base and on the prototype.
- Every clerk command of both workflows carries the marker → NEW. Today it prints `intake: sent unmarked=6`, then `build: sent unmarked=2`: no clerk command carries the marker.
- An intake run against a real store reaches its end with its run in flight → REGRESSION. Prints `returned=closed stored=closed` on base and on the prototype. With the fence but without the marker in `intake.js` it prints `returned=parked stored=ready-for-triage`, so this scenario catches a missing or partial part B.
- The changelog records the guard as its last entry → NEW. Today it prints `CONTIGUOUS`, then `2`: the last entry, 51, mentions only two of the four terms.
- The design doc and README name the marker, and no prompt copy changes → NEW. Today it prints `design=0 readme=0 prompts=0`.
- README no longer says the factory's capabilities never entered the spec store → NEW. Today it prints `bullet=1 stale=1` (`README.md:367`).
- The guard change adds no whitespace errors → REGRESSION. Prints `exit=0` on base.
- The gate suite (`uv run --frozen pytest -q -p no:cacheprovider tests/factory`) covers the one test listed under Tests to change. It is not a separate scenario.

All runtime scenarios were run on a clean clone of base `3a3f58c` and on a prototype clone. Each run used a fresh `HOME` and a `TMPDIR` under this run's scratch directory. The three documentation scenarios that read the current files were run on base only. The changelog scenario counted 2 on base, and the README scenario printed `bullet=1 stale=1`.

## Responses
No critic findings yet. v1 went to the operator as NEEDS-HUMAN, and the critic has not reviewed it. Changes from v1, applying Answer 1:
- Open questions 1 and 2 are now Decisions, as the operator answered them.
- README's stale "never entered it" line is corrected in this ticket, with a new scenario. This ticket is the next one to touch README.
- The operator's design questions for the critic are answered in the spec. Risk gains a table of routes the fence does not reach, including a write between runs, after a run dies, and an exported marker. It also states the interactions with #38 and #46. Decisions now cover a stale in-flight run and why the read-only list is closed.
- A new NEW scenario covers `--accept-harness` while a run is in flight.
- The changelog scenario checks the last entry, not entry 52, so it holds whichever of this change and T-0025 merges first.
- The operator step for removing the spec store is gone. Keep needs no step.
