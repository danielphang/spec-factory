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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0239-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0239-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0239-reviewer/wt` (branch `factory/T-0024.1`, base `d2a51436922119790099d7c6ea6cb8f59bb87b9f`, head `74bc15d3dfae4cb43242ab567558b4a728e779f4`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0024.1

### T-0024-1 / Live-store fence, dispatcher marker and its documents
Depends on: none
Parallel-safe: yes

Parent: T-0024 (#45), approved spec v5 (`.factory/state/specs/T-0024/`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: all of the parent's design:
- A.1 to A.6: the read-only set, the in-flight union, `fence()` with the order location, then marker, then in flight, the call in `main()` before `instance.guard`, the call in `init_cmd` right after `root`, and the new test file.
- B: `'FACTORY_DISPATCH=1'` at the start of `ENV` in `factory/workflows/intake.js` and `factory/workflows/build.js`.
- C: the `docs/design.md` paragraph, the `docs/changelog.md` entry, and the README edits (the opening paragraph of "Where a human decides", the "Built" bullet, the in-flight sentence, the "Current truth" bullet and the status date).
- Tests to change.

Acceptance: run every command from the root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`, and each one through the fresh-HOME wrapper. Run the GIVEN fixture block from "Unmarked writes from inside the target are refused while a run is in flight, init included" once, first.
- NEW: Unmarked writes from inside the target are refused while a run is in flight, init included.
  - WHEN its `t0024-inflight.sh` command with `init`, `ticket new`, `ticket transition` and `decision add`
  - THEN `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`
- NEW: The refusal names the throwaway store and not the marker.
  - THEN `rule=1 state=1 marker=0 json=1 inside=1`
- NEW: A harness acceptance is refused while a run is in flight.
  - THEN `accept=2 store=unchanged`
- NEW: Marked writes from a run's scratch directory or a worktree directory are refused, init included.
  - THEN `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`
- NEW: Writes from a finished run's scratch directory are refused with no run in flight.
  - THEN `idle=1 new=2 decision=2 store=unchanged`
- REGRESSION: Read commands still answer while a run is in flight.
  - THEN `show=0 config=0 log=0 results=0 inside=0`
- REGRESSION: A marked write from the repository root still writes while a run is in flight.
  - THEN `decision=0 finish=0 cleared=1`
- REGRESSION: A throwaway store is not fenced, even from a run's scratch directory.
  - THEN `init=0 new=0`
- REGRESSION: With no run in flight, unmarked commands write as before.
  - THEN `new=0 decision=0`
- REGRESSION: A marked write from a harness checkout with an uncommitted edit is still refused.
  - THEN `exit=2 lock=1 store=unchanged`
- NEW: Every clerk command of both workflows carries the marker.
  - WHEN `node t0024-count.mjs` on each workflow
  - THEN `intake: sent unmarked=0`, then `build: sent unmarked=0`
- REGRESSION: An intake run against a real store reaches its end with its run in flight.
  - WHEN `node t0024-e2e.mjs`
  - THEN `returned=closed stored=closed`
- NEW: The changelog records the guard as its last entry.
  - THEN `CONTIGUOUS`, then `5`
- NEW: The design doc names the marker and the run-directory rule, and no prompt copy changes.
  - THEN `design=1 dirs=1 prompts=0`
- NEW: README tells the operator how to write during a run, first thing under Where a human decides.
  - THEN `first=1 command=1 unnamed=1 export=1 rundirs=1`
  - Note: the scenario reads line 3 of the section, so the bold marker sentence must sit on the line right after the heading's blank line.
- NEW: README says the final verifier run is listed as in flight.
  - THEN `stale=0 listed=1`
- NEW: README no longer says the factory's capabilities never entered the spec store.
  - THEN `bullet=1 stale=0`
- REGRESSION: The guard change adds no whitespace errors.
  - WHEN `git diff --check main...HEAD`
  - THEN `exit=0`
- Gate suite (the parent's intermediate check, not a separate scenario):
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, with pytest's temporary directory under `/tmp`, as the current-truth suite command sets it
  - THEN every test passes, the new `tests/factory/test_live_store_guard.py` included
  - Run it a second time with `FACTORY_DISPATCH=1` exported in the calling shell. Every test must still pass, which shows that the `STRIP` change takes effect.

Tests to change:
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context`: pass `FACTORY_DISPATCH="1"` to the `run compose` `cli(...)` call.
- `tests/factory/test_instance.py`: add `"FACTORY_DISPATCH"` to the `STRIP` tuple (:21).

Protected paths:
- harness: `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`
- guardrail: `tests/factory/test_instance.py`, limited to the two items under Tests to change

Out of scope:
- `factory/instance.py`. The fence is added in `factory/cli.py`, and it only calls the existing `instance.is_own_store`, `own_state_root` and `caller_cwd`.
- `agents/**`, `factory/prompts/**`, `docs/prompts/**`, `dev/build-harness.spec.md`, `bin/factory`, `.factory/**`, `pyproject.toml` and `uv.lock`.
- `test_init_refused_outside_a_git_work_tree` and the suite's assumption that its temporary directory lies outside every repository.
- Parts B and C of the request (the preamble line and the tripwire): the spec cuts both.
- Logging refused attempts.
- Any call site beyond the two in `main()` and `init_cmd`. The store-branch change (#46, T-0025) rebases on exactly these two.

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The change is small: about 25 lines in `factory/cli.py`, one line in each workflow script, one new test file, one existing test and its helper's `STRIP` tuple, and the documents. It cannot be split into parts that each merge cleanly:
- Part A without part B breaks dispatch. With the fence in place and no marker in `intake.js`, the scenario "An intake run against a real store reaches its end with its run in flight" prints `returned=parked stored=ready-for-triage` (spec Evidence, negative controls). Main would then hold a harness that parks every intake.
- Part B without part A adds an environment variable that nothing reads. It is harmless, but its NEW scenario would be the only thing it proves.
- Part C cannot trail A and B. The briefing requires a change to a command, state, stop or path to update `README.md` in the same ticket, and the README paragraph documents the refusal that A adds.
- The existing-test change (`FACTORY_DISPATCH="1"` on the `run compose` call, and `"FACTORY_DISPATCH"` in `STRIP`) has to land with A. Without it the gate suite fails on A, because the in-flight rule refuses that call.

Splitting would add a merge and a re-verify and would make no review or rollback easier.

Checked on this checkout (`~/dev/spec-factory`, HEAD `d2a5143`):
- `git diff abaa75a HEAD --stat -- factory bin tests README.md docs dev` prints nothing, so the spec's base still holds for the code and documents.
- `factory/instance.py` defines `caller_cwd` (:41), `find` (:55), `own_state_root` (:93), `is_own_store` (:105) and `guard` (:141).
- In `factory/cli.py`, `main()` has `root = store.state_root(cfg)` followed by `instance.guard(...)`, and `init_cmd` has `root = instance.state_root(inst, cfg)`. These are the two call sites in design A.4 and A.5.
- `intake.js` and `build.js` both build `ENV` and then `BIN` as the spec describes.
- `tests/factory/test_instance.py:21` is `STRIP`, and `:271` is `test_composed_input_opens_with_the_instance_context`, with its `run compose` call at `:274`.
- The last changelog entry is 51.
- README has the stale sentence at :102 and "never entered it" at :367.
- `FACTORY_DISPATCH` appears nowhere under `factory`, `bin`, `docs`, `dev`, `tests` or `README.md`.
- `tests/factory/test_live_store_guard.py` does not exist yet.

## Parent spec (v5, pinned)

=== proposal.md
## Problem
Any agent that the factory starts to work on a ticket can change the factory's live records for the repository it is working in. Such an agent is a role run. It can do this by running the harness's own command-line tool, `bin/factory`, from anywhere inside that repository.

Each repository the factory works on has an instance: the factory's configuration and records for that repository, kept in the repository's `.factory/` directory. The live records are the live store: the instance's own store under `.factory/state/`. It holds the tickets, the run records, the event log and the spec store, and it decides what the factory does next. Two parties are meant to write it. One is the dispatcher, the workflow script that starts role runs and records their results; it writes through a helper agent called the clerk, which runs one tool command at a time. The other is the human operator, together with the runner sessions that launch workflows for the operator.

Nothing stops a role run from writing it as well. The tool finds its store by walking up from the directory it is run in. A role works inside the target repository, and so do its scratch directory and the temporary directories of the tests it runs. Role runs already get a throwaway home directory, but that does not help here, because the store is not under the home directory.

This has already happened here. This repository is itself a target of the factory, and its instance is called instance B. On 2026-10-04 a spec-writer role run ran the harness's test suite with its temporary directory set inside its scratch directory. One test runs the tool's `init` command and expects it to be refused outside a git repository. Instead, the command found instance B and initialised its live store. That created three things:
- a spec store, the record of what the system currently does. The factory calls that record current truth, and each closed ticket's spec is archived into it.
- `decisions.md`, the store's standing decision log. Later spec writers, critics and planners read it.
- six agent definition files, which would have changed every later Claude Code session started in this repository.

The agent files were removed by hand. The spec store and the decision log are still in use, and one later ticket has already closed into current truth.

Two parties are affected. The operator's store can be changed by an agent, and nothing records which run made the change. Every later ticket on that instance is also affected, because its routing depends on what the store holds.

The change adds a fence to the tool, with two rules. Both apply only to commands that could write the live store; read commands stay open.
- **Where the command runs from.** A write is refused when it is run from inside the store's run directories (`runs/`) or code checkouts (`worktrees/`). Role runs do their work there, and the operator and the clerk never do. This rule holds at all times, and no marker lifts it.
- **Whether a run is in flight.** While any role run is in flight on the live store, meaning started and not yet finished, a write from anywhere is refused unless it carries the marker `FACTORY_DISPATCH=1` in its environment. The dispatcher puts the marker on every clerk command. The operator puts it in front of a single command when they must write during a run.

The fence guards against accidents. It is not a security boundary. The operator has decided to keep the spec store the incident created.

## Evidence
- **The event.** The store log records a `store.initialised` event with no run attached: `.factory/state/log/2026-10.jsonl:995`, `"ts": "2026-10-04T13:35:44+00:00"`. Its files are `openspec/config.yaml`, `openspec/schemas/spec-factory/schema.yaml` and `decisions.md`. Its `agents` are six `/Users/dphang/dev/spec-factory/.claude/agents/factory-*.md` paths.
- **The run.** Only run-0196 was in flight then (`runs/run-0196-spec_writer/meta.yaml`: started `13:16:09`, finished `13:47:49`, ticket T-0023). Its own escalation (`log/2026-10.jsonl:997`) gives the route: "I set `TMPDIR` inside my scratch directory, which is inside this repository. The suite's `test_init_refused_outside_a_git_work_tree` then ran `init` against this repo's instance on its own store." That test runs `bin/factory init` as a subprocess from its temporary directory (`tests/factory/test_instance.py:25-32`, `:132-137`). A second spec-writer run, run-0198, repeated the test the same way (`log/2026-10.jsonl:1006`). It wrote nothing new only because the files already existed.
- **The lasting effect.** `.factory/state/openspec/specs/` now holds six capabilities: build-dispatch, harness-docs, harness-suite, human-resolution, store-setup and sub-ticket-planning. Commit `81294c8` says that T-0023 "closed by archive into current truth" and that the spec store "was created by a stray 'factory init' from intake run-0196". Before the incident, this instance's tickets closed as applied, meaning they were marked done with no archive step, because there was no spec store (`dev/issues.md:19`). This instance was never meant to have agent files (`.factory/state/specs/T-0012/v1.md:71`). `ls ~/dev/spec-factory/.claude` prints "No such file or directory", so they are gone now. A repeat of the suite route would write them again.
- **Base for this version.** `abaa75a`. The harness code, tests and documents are unchanged since the previous version's base: `git diff 3a3f58c HEAD --stat -- factory bin tests README.md docs dev` prints nothing.
- **Reproduced on this checkout.** I ran every runtime scenario of this change on a clean clone of base and on a clone carrying a prototype of parts A and B below, each with a fresh `HOME`. The prototype is 25 added lines in `factory/cli.py` and one changed line in each workflow script. Results, base then prototype:
  - "Unmarked writes from inside the target are refused while a run is in flight, init included" printed `init=0 new=0 transition=0 decision=0 store=changed agents=written`, then `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`. On base every write succeeds from a subdirectory of a target with a run in flight, and `init` writes the agent files again. On the prototype every write is refused and nothing changes.
  - "Marked writes from a run's scratch directory or a worktree directory are refused, init included" printed `scratch_decision=0 scratch_init=0 worktree_new=0 store=changed agents=written`, then `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`. The marker does not get a write through from inside the store.
  - "Writes from a finished run's scratch directory are refused with no run in flight" printed `idle=1 new=0 decision=0 store=changed`, then `idle=1 new=2 decision=2 store=unchanged`. `idle=1` shows the store had nothing in flight, so only the location rule could refuse.
- **The incident's route, reproduced with the marker exported.** I set up a scratch target, started a run and finished it, so nothing was in flight. I removed its agent files and spec store. Then I ran only `test_init_refused_outside_a_git_work_tree` with `TMPDIR` inside that finished run's scratch directory and `FACTORY_DISPATCH=1` exported. Base printed `1 failed` with `agents=written specstore=written`: `init` succeeded and rewrote both. The prototype printed `1 failed` with `agents=none specstore=none`. Its assertion message shows `init` refused with `role runs may not write the live store (<target>/.factory/state; called from inside its runs/); use a throwaway FACTORY_STATE`. So the location rule alone stops the incident, even with an idle store and an exported marker. The test still fails, because it expects a different refusal; that test's assumption is out of scope.
- **Negative controls.** I committed the prototype with the location rule disabled and with the marker removed from `intake.js` only. The scratch-and-worktree scenario then printed `scratch_decision=0 scratch_init=0 worktree_new=0 store=changed agents=written`, and the finished-run scenario printed `new=0 decision=0 store=changed`: both scenarios detect a missing location rule. The end-to-end scenario, "An intake run against a real store reaches its end with its run in flight", printed `returned=parked stored=ready-for-triage` instead of `returned=closed stored=closed`: the clerk's own `run finish` was refused. So the marker is what lets the dispatcher through, and that scenario detects a missing marker.
- **Suite.** The current-truth suite command (pytest's temporary directory under `/tmp`, an uncommitted harness edit) gave `254 passed` on the prototype, and `254 passed` again with `FACTORY_DISPATCH=1` exported in the calling shell. With the test change below reverted and the marker exported, `tests/factory/test_instance.py` gave `1 failed, 21 passed`, so an exported marker no longer hides that change.
- **The marker does not get past the harness lock.** In a harness clone with an uncommitted edit, on a target with a run in flight, a marked `decision add` printed `exit=2 lock=1 store=unchanged` on base and on the prototype: the lock's uncommitted-edit refusal still applies.
- **Where roles, the clerk and the operator work.** Each run's scratch directory is `<store>/runs/<id>/scratch` (`factory/cli.py:223`). An implementer's checkout is `<store>/worktrees/<ticket>` (`:247`), and a checker's is `<store>/runs/<id>/wt` (`:259`). The clerk is told to run its command "from the repository root" of the harness checkout (`factory/workflows/intake.js:52`, `build.js:43`), and the harness checkout is never under a store. A role is not always inside the store, though. This repository's briefing tells roles to run `cd ~/dev/spec-factory && <cmd>`, and this run's own shell started in another repository's directory. See Risk.
- **The operator writes while runs are in flight.** This happened twice today on this store:
  - T-0025 was filed at `17:50:05` (`log/2026-10.jsonl:1122-1123`) while run-0220 was in flight (`:1121`).
  - The operator's answer to this ticket was recorded at `18:15:46-47` (`:1137-1139`) while run-0223-critic was in flight (started `18:13:51`, finished `18:21:01`, `:1136` and `:1141`).

  Under this change, both commands need the marker.
- **The requester's proposed exemption for humans does not match the code.** Human commands take no `--by`. `approve-spec`, `request-changes`, `resolve` and `decision add` record the operating-system user name (`factory/cli.py:638-639`, `_by()`). `ticket transition` requires `--by` on every call (`factory/cli.py:1063`), so a role would supply it too.
- **Three commands that look like reads write the store.** `ticket ready-implementers` saves sub-tickets and logs transitions (`factory/cli.py:434`). `ticket parent-check` saves the parent (`:619`). `spec tasks` writes a file and logs (`:917`). `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` call no store writer.
- **The parent-close verifier run is listed as in flight.** That is the final verifier run on a parent ticket after all its sub-tickets merge. `run_start` appends every run it starts to the ticket's in-flight list, this one included (`factory/cli.py:231`), and `run finish` removes it (`:312-313`). README says the opposite (`README.md:102`). The fence relies on the code's behaviour, so this change corrects the README sentence.
- **Part A does not exist yet.** `grep -rn FACTORY_DISPATCH` finds nothing in `factory/`, `bin/`, `docs/`, `dev/` or `.factory/instance.yaml`, and nothing in `~/dev/nanobot-upstream/factory` or `.factory`.

## Root cause
- `factory/instance.py:55` `find()`: when `FACTORY_INSTANCE` is unset, the instance is the nearest `.factory/instance.yaml` above the caller's directory. Any directory inside the repository resolves to the live instance. That includes a role's scratch directory, `runs/<id>/scratch/` inside the store, and any temporary directory under it.
- `factory/cli.py:1193` `main()` and `factory/cli.py:845` `init_cmd()` check only the harness lock and the uncommitted-edit refusal (`instance.guard`, `factory/instance.py:141`) before writing the live store. Neither asks whether a role run is in flight, or where the command was run from. `init_cmd` takes its instance from the git top level of the caller's directory and copies the agent files at `factory/cli.py:885`.
- The suite's `test_init_refused_outside_a_git_work_tree` (`tests/factory/test_instance.py:132`) assumes its temporary directory lies outside every repository. The scratch rule puts a role's temporary files inside the store, which is inside the repository. Together these turned a refusal test into a live `init`.

## Out of scope
- The test suite's assumption that its temporary directory lies outside every repository. After this change, that test fails without writing the live store. See Out-of-scope observations.
- Writes that bypass `bin/factory`, such as an editor or a shell redirect into `.factory/`. `.factory/**` is already a protected path in every role's rules. Isolating role runs at the operating-system level is issue #37, a separate investigation.
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
- A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
- The location rule is checked first, then the marker, then the in-flight list.
- The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
- The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
- The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
- A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
- The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
- A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
- The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
- The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
- Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
- Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.

## Risk
- **Blast radius.** Every target that runs this harness: this repository (instance B), and the Nanobot fork (instance A) after it upgrades. Two effects on the operator and runner sessions:
  - While a run is in flight there, any store write without the marker is refused with exit 2. That includes filing a ticket, `resolve`, `decision add`, `approve-spec`, `ticket set`, and `--accept-harness` on any command.
  - A store write run from inside the store's `runs/` or `worktrees/` is always refused, marked or not.

  The workflow scripts carry the marker and the clerk runs from the harness checkout, so intake and build are unaffected. A refused command writes nothing, so the failure is loud and safe.
- **Where the fence does not reach.** These routes stay open after this change:

  | Route | Why the fence misses it | What still limits it |
  |---|---|---|
  | A role running a command from outside the store, such as the repository root, with a copied marker or one its session inherited | The location rule fires only inside the store's `runs/` and `worktrees/`. Roles do not always work there: this repository's briefing tells them to run `cd ~/dev/spec-factory && <cmd>` | The refusal never names the marker. README says to prefix one command and never to export it. `.factory/**` is protected in every role's rules |
  | A process a role left running after its run finished, such as a background test run (#41), writing from outside its run directory | Once no run is in flight, the in-flight rule is off | From inside its run directory it is now refused. A workflow starts the next run seconds after the last one finishes |
  | A killed run that the operator clears while its agent is still running, writing from outside its run directory | Same: clearing the run drops it from the in-flight list | Same. The operator clears a run only after its workflow has stopped |
  | A role inside a code checkout that tracks its own `.factory/` | The walk-up finds the checkout's copy of the instance, not the live one, so neither rule sees the live store. Committed copies carry no in-flight runs | Such a write lands in the checkout. It reaches the live store only through a merged commit under `.factory/**`, a protected path the reviewer checks. A checkout that does not track `.factory/` walks up to the live instance and is refused by the location rule |
  | A role writing the files directly, not through `bin/factory` | The fence lives in the tool | `.factory/**` is protected in every role's rules. #37 |
  | A role run of one instance writing another instance that has nothing in flight, from outside that instance's store | That store is idle, and the caller is not inside it | Out of scope |

- **Interaction with the tripwire (#38).** None. The tripwire compares the files it lists inside `run finish` and inside a `ticket set` that drops a run. Both are marked when the dispatcher sends them. An operator who clears a stale run with a marked command gets the same comparison as today.
- **Interaction with the store branch (#46, T-0025).** This ticket builds first, and #46 rebases on it. Both edit `init_cmd` and `main()` in `factory/cli.py`. This change adds one fence call in each, so #46 keeps that call ahead of every write it adds.
  - The fence reads in-flight runs from `tickets/*.yaml` under the store in use, and takes `runs/` and `worktrees/` under the instance's own store path, which comes from `state_dir`. If #46 moves the store to a git worktree at a new path, both rules follow `state_dir` and need no change.
  - The design review found a case that #46 must fix: run from inside a store that is its own git worktree, `init` takes that worktree as the repository and creates a new instance there. This fence does not see that, because a new instance has no in-flight runs and its own store does not contain the caller. Once #46's `init` resolves the live instance instead, this change's location rule refuses that `init`, with or without a run in flight.
  - #46's migration steps write the live store, so they run with nothing in flight or with the marker, from the repository root.
  - Both changes touch `README.md`, `docs/design.md` and the changelog. The second to merge takes the next changelog number. This spec's changelog scenario checks the last entry rather than a fixed number.
- **Not a security boundary.** See Decisions.
- **Protected paths this change touches:**
  - harness: `factory/cli.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`;
  - guardrail: one existing test and the `STRIP` tuple its file's helper uses, both in `tests/factory/test_instance.py` (Tests to change).
- **Not touched:** `.factory/**`, `agents/**`, `bin/factory`, `docs/prompts/**`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

## Gate edit (Green session, operator-delegated, 2026-10-04)

From the Fable design review round 2 (`.factory/answers/design-review-45-46/round-2.md`), which found this spec CLEAR: N1 option (b), the throwaway-store scenario runs `init` from the target root instead of a run's scratch directory, so it stays true once #46 moves the store into its own worktree (its point, that throwaway stores are not fenced, is unchanged; `ticket new` still runs from the scratch directory); N3, a store with no `tickets/` yet has no runs in flight.

## Operator steps
1. After merge, between builds, move the runtime and accept the new revision in each target, as README "Upgrading the runtime" says. Run the `--accept-harness` command from the repository root, when no run is in flight on that store or with the marker in front of it.
2. Tell each runner session, the Nanobot Driver included, before its next intake or build: prefix a store write made during a run with `FACTORY_DISPATCH=1`, never export it, and run store writes from the repository root, never from inside the store's `runs/` or `worktrees/`.

## Out-of-scope observations
- The suite guard is a separate follow-up and is not filed in `dev/issues.md`. run-0198 suggested it. `test_init_refused_outside_a_git_work_tree` still fails when `TMPDIR` lies inside a run's scratch directory. After this change it fails safely, refused by the fence, but a verifier on this instance that sets `TMPDIR` into its scratch would still see a failing gate.
- A role in a code checkout that runs `init` writes `.claude/agents/` in that checkout. `.claude/**` is not a protected path, so only review would stop such a commit.
- In this environment `mktemp -d` ignored `TMPDIR`, so the scenario fixtures' targets were created under the system temporary directory, not this run's scratch directory. They hold only scratch targets.

=== design.md
## Proposed change
**A. The fence, in `factory/cli.py`.**
1. Add the read-only set as `(command, subcommand)` pairs: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths`.
2. "Runs in flight" are the union of the `in_flight` lists over `tickets/*.yaml` in the store in use. Sub-tickets are ticket files too. A store with no `tickets/` directory yet (an instance whose store is not created) has no runs in flight.
3. Add one fence function `fence(inst, cfg, root)`. It does nothing unless the store in use is the instance's own (`instance.is_own_store`). Then, in this order:
   - **Location.** Let `own = instance.own_state_root(inst, cfg)` and `cwd = instance.caller_cwd()`. If `cwd` lies under `own / "runs"` or `own / "worktrees"` (`Path.is_relative_to`; both paths are already resolved), raise `Refused`. This holds whatever `FACTORY_DISPATCH` says and whether or not a run is in flight.
   - **Marker.** If `os.environ.get("FACTORY_DISPATCH") == "1"`, return.
   - **In flight.** If at least one run is in flight, raise `Refused`.

   Both refusals use `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<own store>; called from inside its runs/` (or `worktrees/`) for the location rule, and `<store>; in flight: <comma-separated run ids>` for the in-flight rule. Neither names the marker. `main()`'s existing `Refused` handler gives exit 2, stderr and `{"ok": false, "error": ...}`.
4. In `main()`, after `root = store.state_root(cfg)` (`factory/cli.py:1201`) and before `instance.guard(...)`, call `fence(inst, cfg, root)` when the command is not in the read-only set or `--accept-harness` was given. Calling it before the guard means a fenced `--accept-harness` rewrites no lock.
5. In `init_cmd`, call `fence(inst, cfg, root)` on the line right after `root = instance.state_root(inst, cfg)` (`factory/cli.py:870`). For an existing instance this comes before any write: `context.md`, `harness.lock`, agent files, `.gitignore`, `.gitattributes`, the spec store. A brand-new instance has no tickets, so `init` on a new repository is not fenced by the in-flight rule. Keep it to these two call sites, so the store-branch change (#46) can rebase on them.
6. Add the new behaviour's tests in a new file, such as `tests/factory/test_live_store_guard.py`. Cover both rules: an unmarked write with a run in flight, a marked write from a run's scratch directory and from under `worktrees/`, and a write from a finished run's scratch directory with nothing in flight. Its subprocess helper drops `FACTORY_DISPATCH` from the inherited environment, so a runner that exported it cannot change the result.

**B. The marker, in the workflow scripts.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, start `ENV` with `'FACTORY_DISPATCH=1'`. Then `BIN`, and with it every clerk command, carries it unconditionally. The clerk needs no change; it already runs from the harness checkout.

**C. Documents.**
- `docs/design.md`: a new paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". Like its neighbours it is one line. It states:
  - the location rule: a write run from inside the own store's `runs/` or `worktrees/` is refused, marker or not, run in flight or not;
  - the in-flight rule: live store only, in flight only, the read-only list, `--accept-harness`;
  - the `FACTORY_DISPATCH=1` marker, set by both workflow scripts, and the operator's per-command use of it;
  - the refusal: exit 2, writes nothing, names a throwaway `FACTORY_STATE`, never names the marker;
  - that it guards against accidents and is not isolation;
  - that the fence is checked before the harness lock, so a fenced command never reaches the lock or its `--accept-harness`, and a marked command still meets the lock unchanged.
- `docs/changelog.md`: one new entry, numbered after the current last entry (52 if nothing else lands first). It names `FACTORY_DISPATCH`, "in flight", `runs/` and `worktrees/`, the throwaway store and exit 2. It says that parts B and C of the request were declined, and why.
- `README.md`:
  - In "Where a human decides", the first paragraph under the heading, before the table, opens with this bold sentence on its own line: "**While a run is in flight, put `FACTORY_DISPATCH=1` in front of every store write you make.**" The paragraph then:
    - shows the exact command form in a code block, for example `FACTORY_DISPATCH=1 $RUNTIME/bin/factory decision add T-n "<line>"`;
    - says that without it the write is refused with exit 2, and that the refusal text deliberately does not name the marker, so that a role reading it is not told how to get past it; its "use a throwaway FACTORY_STATE" advice is for roles, not for the operator;
    - says to never export the marker, because every role run started from that shell would inherit it;
    - says to run store writes from the repository root: from inside the store's `runs/` or `worktrees/` every write is refused and the marker does not help;
    - says that a run left in flight by a stopped workflow is cleared with `FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLED`.
  - A "Built" bullet for the fence, saying it is tested and has not yet fired on a real ticket.
  - In "How a ticket moves", replace the sentence at `README.md:102-103` ("While that final run is in progress the ticket's record does not list it as in flight, so a ticket at this step can look idle for a few minutes.") with one saying that while that final run is in progress, the ticket's record lists it as in flight, like any other run.
  - In "Not built", rewrite the "Current truth for the factory itself" bullet: the spec store holds only the capabilities that tickets have changed since it was created, not the whole factory. Remove "never entered it" and quote no count, since each archive changes it.
  - Bump the status date, per "Maintaining this page".
- `docs/prompts/` and `factory/prompts/` do not change.

## Tests to change
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context` (line 271; the call is at line 274). Its `run compose` call stands for the dispatcher's own command. It runs on a scratch instance's live store, from the target's root, while the triage run that `_start_triage` just started is in flight, so the in-flight rule refuses it. Change: pass `FACTORY_DISPATCH="1"` to that one `cli(...)` call. Verified on the prototype: with the marker exported and this change reverted, the file gave `1 failed, 21 passed`; with it, the suite gave `254 passed`.
- The same file's `STRIP` tuple (`tests/factory/test_instance.py:21`), the variables its `cli()` helper drops from the inherited environment. Add `"FACTORY_DISPATCH"` to it. Without this, a runner shell that exported the marker would make the test above pass with or without its change, and every own-store case in the file would skip the in-flight rule. An explicit `FACTORY_DISPATCH="1"` argument still wins, because `cli()` applies its arguments after the strip. Verified on the prototype: `254 passed` with the marker exported.
- No other existing test changes. No existing test runs a write on its own store from inside that store's `runs/` or `worktrees/`; the suite passed in full on the prototype.

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
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
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

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
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
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance
- Unmarked writes from inside the target are refused while a run is in flight, init included → NEW. Today it prints `init=0 new=0 transition=0 decision=0 store=changed agents=written`: every write succeeds, and `init` writes the agent files again.
- The refusal names the throwaway store and not the marker → NEW. Today it prints `rule=0 state=0 marker=0 json=0 inside=0`: every write succeeds, so there is no refusal text.
- A harness acceptance is refused while a run is in flight → NEW. Today it prints `accept=0 store=changed`: the lock is rewritten and a `harness.accepted` event is logged.
- Marked writes from a run's scratch directory or a worktree directory are refused, init included → NEW. Today it prints `scratch_decision=0 scratch_init=0 worktree_new=0 store=changed agents=written`: all three writes succeed, and `init` from the scratch directory writes the agent files again.
- Writes from a finished run's scratch directory are refused with no run in flight → NEW. Today it prints `idle=1 new=0 decision=0 store=changed`: with nothing in flight, both writes succeed from inside the store.
- Read commands still answer while a run is in flight → REGRESSION. Prints `show=0 config=0 log=0 results=0 inside=0` on base and on the prototype.
- A marked write from the repository root still writes while a run is in flight → REGRESSION. Prints `decision=0 finish=0 cleared=1` on base and on the prototype.
- A throwaway store is not fenced, even from a run's scratch directory → REGRESSION. Prints `init=0 new=0` on base and on the prototype.
- With no run in flight, unmarked commands write as before → REGRESSION. Prints `new=0 decision=0` on base and on the prototype.
- A marked write from a harness checkout with an uncommitted edit is still refused → REGRESSION. Prints `exit=2 lock=1 store=unchanged` on base and on the prototype. It would catch an implementation that lets the marker skip the lock as well as the fence.
- Every clerk command of both workflows carries the marker → NEW. Today it prints `intake: sent unmarked=6`, then `build: sent unmarked=2`: no clerk command carries the marker.
- An intake run against a real store reaches its end with its run in flight → REGRESSION. Prints `returned=closed stored=closed` on base and on the prototype. With the fence but without the marker in `intake.js` it prints `returned=parked stored=ready-for-triage`, so this scenario catches a missing or partial part B.
- The changelog records the guard as its last entry → NEW. Today it prints `CONTIGUOUS`, then `2`: the last entry, 51, mentions only two of the five terms (`exit 2`, `throwaway`).
- The design doc names the marker and the run-directory rule, and no prompt copy changes → NEW. Today it prints `design=0 dirs=0 prompts=0`.
- README tells the operator how to write during a run, first thing under Where a human decides → NEW. Today it prints `first=0 command=0 unnamed=0 export=0 rundirs=0`: README does not mention the marker, and the section opens with its table.
- README says the final verifier run is listed as in flight → NEW. Today it prints `stale=1 listed=0` (`README.md:102`).
- README no longer says the factory's capabilities never entered the spec store → NEW. Today it prints `bullet=1 stale=1` (`README.md:367`).
- The guard change adds no whitespace errors → REGRESSION. Prints `exit=0` on base.
- The gate suite (`uv run --frozen pytest -q -p no:cacheprovider tests/factory`) covers the test and helper listed under Tests to change, and the new test file. It is not a separate scenario.

How this version was checked. Base is `abaa75a`. I cloned base and a prototype of parts A and B into this run's scratch directory and ran the twelve runtime scenarios on both, each through the fresh-`HOME` wrapper, with `TMPDIR` set to this run's scratch directory. Each printed the base and prototype results stated above. I also ran the negative controls and the incident's route described under Evidence, and the harness suite on the prototype through the current-truth suite command: `254 passed`, and `254 passed` with the marker exported. I ran the six documentation scenarios on `main` in the dev checkout, read-only, and each printed the "today" result above. In this environment `mktemp -d` ignored `TMPDIR`, so the fixture targets were created under the system temporary directory; the results do not depend on where they live.

## Responses
Changes requested at the spec gate (the design review's findings, sent back by the Green session on the operator's behalf):
- 1, SHOULD-FIX (review finding 2): a second trigger that does not depend on the marker → FIXED. Design A.3 adds the location rule: a write whose caller's directory (`instance.caller_cwd()`) lies under the own store's `runs/` or `worktrees/` is refused with exit 2 and nothing written, even with `FACTORY_DISPATCH=1`. It holds with or without a run in flight, which also closes the left-over-process and cleared-run routes for a process working in its run directory. A new requirement has two NEW scenarios. A marked `decision add` and `init` from `<store>/runs/<id>/scratch`, and a marked `ticket new` from under `<store>/worktrees/`, are refused. Writes from a finished run's scratch directory are refused with nothing in flight. The marked-write scenario now runs from the repository root and still passes. With the marker exported and the store idle, the incident's own test is refused by this rule alone (Evidence). One limit, stated under Risk rather than claimed closed: a role does not always work under the store. This repository's briefing tells roles to `cd ~/dev/spec-factory`, and this run's shell started in another repository. A copied or inherited marker used from there still gets through. Decisions and Problem still say the fence is not a security boundary.
- 2, NOTE (review finding 9): make the README paragraph unmissable → FIXED. Design C makes it the first paragraph under "Where a human decides", before the table. It opens with a bold sentence and shows the exact command form in a code block. It says the refusal deliberately does not name the marker and why, says never to export it, says to write from the repository root, and gives the stale-run clearing command. A new NEW scenario checks each of these.
- 3, NOTE (review Q6): README's line on the parent-close verifier → FIXED. Design C replaces the sentence at `README.md:102-103`, and a new NEW scenario checks it. Evidence cites `factory/cli.py:231` (append) and `:312-313` (removal). The item moved from Out-of-scope observations into scope.
- 4, NOTE (review finding 10): name the suite-guard follow-up → FIXED. Out-of-scope observations names it: run-0198's suggestion, not filed in `dev/issues.md`, a test that still fails, now safely, when `TMPDIR` is inside a run's scratch directory.
- 5, build order, before the store-branch change (#46) → FIXED. Design A.4 and A.5 keep exactly two fence call sites: one line in `main()` before the lock, and one line in `init_cmd` right after `root` is loaded. Risk states the order and what #46 must keep, and that #46's own `init` fix is what lets this location rule cover `init` run from inside a store worktree.

Earlier rounds: the round-2 critic's findings were answered in the previous version (glossing, `STRIP`, fence-before-lock order) and those changes are kept.

## PR description (the implementer's output)

Sub-ticket: T-0024.1 (parent T-0024, issue #45, spec v5): Live-store fence, dispatcher marker and its documents
Branch: `factory/T-0024.1`, base `d2a51436922119790099d7c6ea6cb8f59bb87b9f`, head `74bc15d3dfae4cb43242ab567558b4a728e779f4` (one commit)

## What changed

A role run is an agent the factory starts to work on one ticket. Before this change, a role run could write the live store, which holds the factory's live records for a repository under `.factory/state/`, by running `bin/factory` from anywhere inside that repository. That is how a spec writer's test suite initialised this repository's store on 2026-10-04. After this change, the tool refuses such writes in two cases. The first is a write run from inside the store's run directories (`runs/`) or code checkouts (`worktrees/`). The second is a write made without the dispatcher's marker, `FACTORY_DISPATCH=1`, while any run is in flight. The dispatcher is the workflow script that starts role runs, and it now puts the marker on every command it sends.

- **A.1–A.5, the fence, in `factory/cli.py`.**
  - `READ_ONLY` is the set of `(command, subcommand)` pairs that are never fenced: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`.
  - `_in_flight(root)` returns the union of the `in_flight` lists over `tickets/*.yaml`, sub-tickets included. A store with no `tickets/` directory has nothing in flight.
  - `fence(inst, cfg, root)` acts only when `instance.is_own_store(...)` is true. It checks in this order:
    1. Location: if `instance.caller_cwd()` lies under `own_state_root/runs` or `own_state_root/worktrees`, the write is refused, whatever the marker says.
    2. Marker: if `FACTORY_DISPATCH == "1"`, the write goes through.
    3. In flight: if any run is in flight, the write is refused.

    Both refusals use the spec's text, `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. Neither names the marker.
  - `main()` calls the fence between `root = store.state_root(cfg)` and `instance.guard(...)`, for any command outside `READ_ONLY` and for any command given `--accept-harness`. The guard is the harness lock check. `init_cmd` calls the fence on the line right after `root = instance.state_root(inst, cfg)`. These are the only two call sites. `import os` was added.
  - Callers, per coding rule 2. `main()` is called by `python -m factory` (`bin/factory`) and by `tests/factory/clean_harness_cli.py:28`. `init_cmd` is reached only through the parser's `set_defaults(fn=init_cmd)` (`factory/cli.py:1146`). `fence` is called only at `cli.py:872` and `:1235`.
- **A.6, the new test file.** `tests/factory/test_live_store_guard.py` has 11 tests. They cover:
  - unmarked writes refused while a run is in flight, from the target root and from a subdirectory: `ticket new`, `ticket transition`, `decision add`, `ticket set`;
  - `init` refused without rewriting the agent files;
  - `--accept-harness` refused without changing the store;
  - reads that still answer, from the root and from a run's scratch directory;
  - a marked write from the root that goes through;
  - a value other than `1` (`FACTORY_DISPATCH=yes`) that is not taken as the marker;
  - idle unmarked writes that go through;
  - a throwaway store that is not fenced;
  - marked writes refused from a run's scratch directory (`decision add`, `init`, `ticket new`) and from under `worktrees/` (`ticket new`, `init`);
  - writes from a finished run's scratch directory refused while nothing is in flight.

  The file reuses `cli`, `git_repo`, `js` and `tree` from `test_instance.py`. That `cli` now drops `FACTORY_DISPATCH` from the inherited environment, so a runner shell that exported the marker cannot change a result.
- **B, the marker.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, `ENV` now starts with `'FACTORY_DISPATCH=1'`. Every clerk command is built from `BIN`, so each one carries the marker. The clerk is the helper agent that runs one store command at a time for the workflow.
- **C, the documents.**
  - `docs/design.md`: a new one-line paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". It covers the location rule, the in-flight rule, the read-only list and `--accept-harness`, the marker and the operator's per-command use of it, and the refusal. It also says the fence is checked before the lock, and that it guards against accidents and is not isolation.
  - `docs/changelog.md`: entry 52, placed after 51 and before the "Declined:" line. It names `FACTORY_DISPATCH`, in flight, `runs/` and `worktrees/`, the throwaway store and exit 2. It says why the request's preamble line and its store-root tripwire were declined.
  - `README.md`, in five places:
    - "Where a human decides" now opens with the bold marker sentence on line 3 of the section. After it come a gloss of "in flight", the read-only list, the command form in a code block, the deliberately-unnamed-marker explanation, "Never export the marker", the rule to write from the repository root and not from `runs/` or `worktrees/`, and the command that clears a stale run.
    - A "Live-store fence" bullet under Built. It says the fence is tested and has not yet fired on a real ticket.
    - The sentence about the final verifier run now says it is listed as in flight like any other run.
    - The "Current truth for the factory itself" bullet is rewritten without "never entered it" and without a count.
    - The status date: see Known gaps.
- **Tests to change.** In `tests/factory/test_instance.py`, `"FACTORY_DISPATCH"` was added to `STRIP`. The tuple is wrapped onto a second line because it is longer than before. `test_composed_input_opens_with_the_instance_context` now passes `FACTORY_DISPATCH="1"` to its `run compose` call. No other existing test changed.

## Acceptance results

All commands ran from the worktree root after `uv sync --frozen`, through the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. The three GIVEN fixture files went there too. I wrote them with the Write tool, not by running the spec's `cat >` block, because the permission classifier refused my first attempt: it extracted the block with `sed` and ran it with `sh`. A line-by-line `grep -xF` against `input.md` confirmed that the three files and all 18 WHEN commands match the spec verbatim. As the spec writer also saw, `mktemp -d` ignored `TMPDIR`, so the scratch targets were created under `/var/folders/.../T/`. Logs: `scratch/base.txt` is base `d2a5143`; `scratch/after.txt` is head `74bc15d`.

| Scenario | Kind | Before (base) | After (head) |
|---|---|---|---|
| Unmarked writes refused while in flight, init included | NEW | `init=0 new=0 transition=0 decision=0 store=changed agents=written` | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` |
| Refusal names throwaway store, not marker | NEW | `rule=0 state=0 marker=0 json=0 inside=0` | `rule=1 state=1 marker=0 json=1 inside=1` |
| Harness acceptance refused while in flight | NEW | `accept=0 store=changed` | `accept=2 store=unchanged` |
| Marked writes from scratch / worktree refused | NEW | `scratch_decision=0 scratch_init=0 worktree_new=0 store=changed agents=written` | `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none` |
| Finished run's scratch refused, nothing in flight | NEW | `idle=1 new=0 decision=0 store=changed` | `idle=1 new=2 decision=2 store=unchanged` |
| Reads answer while in flight | REGRESSION | `show=0 config=0 log=0 results=0 inside=0` | `show=0 config=0 log=0 results=0 inside=0` |
| Marked write from repo root goes through | REGRESSION | `decision=0 finish=0 cleared=1` | `decision=0 finish=0 cleared=1` |
| Throwaway store not fenced | REGRESSION | `init=0 new=0` | `init=0 new=0` |
| Idle unmarked writes go through | REGRESSION | `new=0 decision=0` | `new=0 decision=0` |
| Marker does not lift the lock | REGRESSION | `exit=2 lock=1 store=unchanged` | `exit=2 lock=1 store=unchanged` |
| Every clerk command carries the marker | NEW | `intake: sent unmarked=6` / `build: sent unmarked=2` | `intake: sent unmarked=0` / `build: sent unmarked=0` |
| Intake e2e reaches its end with its run in flight | REGRESSION | `returned=closed stored=closed` | `returned=closed stored=closed` |
| Changelog's last entry records the guard | NEW | `CONTIGUOUS` / `2` | `CONTIGUOUS` / `5` |
| Design doc names marker and run dirs; no prompt copy changes | NEW | `design=0 dirs=0 prompts=0` | `design=1 dirs=1 prompts=0` |
| README opens "Where a human decides" with the marker | NEW | `first=0 command=0 unnamed=0 export=0 rundirs=0` | `first=1 command=1 unnamed=1 export=1 rundirs=1` |
| README: final verifier listed as in flight | NEW | `stale=1 listed=0` | `stale=0 listed=1` |
| README: no "never entered it" | NEW | `bullet=1 stale=1` | `bullet=1 stale=0` |
| No whitespace errors | REGRESSION | `exit=0` | `exit=0` |

What the results mean:
- Every NEW scenario printed its spec's "today" value on base and its expected value on head.
- Every REGRESSION scenario printed its expected value on head, so no REGRESSION scenario needed a base re-run.
- On head, `store=unchanged` and `agents=none` show that a refused write left the target's `.factory/` and `.claude/` byte-for-byte unchanged.
- `marker=0` shows that no stderr or JSON output contains `FACTORY_DISPATCH`.
- `returned=closed` shows that the dispatcher's own marked `run finish` still goes through while its run is in flight.

Gate commands, run on head `74bc15d` from the worktree, each exactly as written:
- `(export HOME=...; git diff --check main...HEAD)` gave exit 0 and no output.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` gave `265 passed in 222.59s`. `TMPDIR` was inherited as `/var/folders/.../T/`, which is outside every repository. That is 254 existing tests plus the 11 new ones.
- The same suite with `FACTORY_DISPATCH=1` exported in the calling shell and `TMPDIR` set to a fresh `/tmp/t0024-suite.XXXXXX` gave `265 passed in 222.52s`. An exported marker therefore changes no result. That run used `TMPDIR=$P uv run ...`, so it is an extra run and not the gate command as written.

TDD record: before the `cli.py` change, the new test file gave `7 failed, 4 passed`. The 4 that passed are the regression cases: reads, a marked write from the root, idle writes, and the throwaway store. After the change it gave `11 passed`.

Side-effect check: during my runs this worktree's `git status` stayed clean apart from my own edits. The live store's log grew from 1192 to 1196 lines. The 4 new lines are another ticket's workflow (T-0025: `run-0235-spec_writer` finished, `run-0237-critic` started), not this run.

## Tests added/changed

- Added `tests/factory/test_live_store_guard.py`, a new file with 11 tests. Each covers one rule of design A.3 or one requirement of the spec.
- Changed `tests/factory/test_instance.py`, both items listed under the spec's Tests to change:
  - `STRIP` gains `"FACTORY_DISPATCH"`. Without it, a runner shell with the marker exported would hide the in-flight rule from every own-store case in the file.
  - `test_composed_input_opens_with_the_instance_context` passes `FACTORY_DISPATCH="1"` to `run compose`. That call stands in for the dispatcher's command on a live store with a triage run in flight, so the in-flight rule would otherwise refuse it.

## Known gaps and uncertainties

- **Status date.** The README status header already said "as of 2026-10-04", which is today, so the bump in "Maintaining this page" left it unchanged.
- **Rejected fixture block.** The classifier refused the GIVEN block when I extracted it from `input.md` and ran it with `sh`, so I wrote the same three files with the Write tool and verified them line by line. A reviewer who wants the literal block run should run it themselves.
- **`_in_flight` and empty ticket files.** `_in_flight` reads every `tickets/*.yaml` on each fenced write. An empty or non-mapping ticket file would make `.get` raise, giving exit 1 instead of a refusal. Every ticket file the harness writes is a mapping, so I added no handling.
- **Unreachable `paths` entry.** `READ_ONLY` includes `("paths", None)` as design A.1 lists it. `main()` handles `paths` before the fence, so that entry is never reached; it does no harm.
- **Sentences other docs could still contradict.** I did not search `docs/design.md` beyond the new paragraph for older sentences that the fence now contradicts. For example, a sentence saying any role may run store commands could now be stale. I found none in the paragraphs next to the new one.
- `factory:` markers added: none.

## Out-of-scope observations

- `test_init_refused_outside_a_git_work_tree` still assumes its temporary directory lies outside every repository. The spec leaves it out of scope. After this change, with `TMPDIR` inside a run's scratch directory, that test would fail because the fence refuses `init`. It would no longer write the live store.
- Several other test files have their own `STRIP` tuple and `cli` helper without `FACTORY_DISPATCH`: `test_store_setup.py`, `test_harness_lock.py`, `test_writing_standard.py` and `test_coding_standard.py`. With the marker exported, the suite still passed in full, so none of them depends on it today. A later own-store test in those files with a run in flight could pass for the wrong reason in a shell that exported the marker.
- In both workflow scripts, `ENV ? ENV + ' ' : ''` is now always true. I left it alone, because removing it would be a drive-by edit.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 18 scenarios printed the expected output before and after, and the gate suite passed 265 of 265 with and without the marker exported. The one uncertainty is that the fixture files were written with the Write tool rather than by the spec's `cat >` block; they were verified line by line.
ESCALATIONS:
- The permission classifier refused the spec's GIVEN fixture block when I extracted it from `input.md` with `sed` and ran it with `sh`. To get past that I wrote the three fixture files with the Write tool, using the spec's exact text, and confirmed with `grep -xF` that every line matches `input.md`. The fixtures used are therefore identical to the spec's. If the auditor wants the GIVEN block itself run, they need to run it or allow it.

## Diff `d2a51436922119790099d7c6ea6cb8f59bb87b9f...74bc15d3dfae4cb43242ab567558b4a728e779f4`

diff --git a/README.md b/README.md
index 7f76ee3..fca1ac0 100644
--- a/README.md
+++ b/README.md
@@ -99,8 +99,8 @@ the integration branch has not moved since it merged: the sub-ticket's verifier
 the same code against the same starting point. On success the harness folds the spec into current truth and closes the
 ticket. If the target has no spec store yet (no `openspec/` tree), the fold is refused and the
 ticket parks; the human then closes it as applied with `resolve --close`, and current truth is
-not updated. While that final run is in progress the ticket's record does not list it as in flight, so
-a ticket at this step can look idle for a few minutes.
+not updated. While that final run is in progress, the ticket's record lists it as in flight, like
+any other run.
 
 At any step a role can say it needs a human: a question, an escalation, a blocked build. The
 harness parks the ticket. So does running out of rounds, or a run exceeding its budget. A human
@@ -312,6 +312,30 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 
 ## Where a human decides
 
+**While a run is in flight, put `FACTORY_DISPATCH=1` in front of every store write you make.**
+A run is in flight from `run start` until `run finish` records its result. While any run on a
+target is in flight, the harness refuses every write to that target's store that lacks this
+marker. A write is any command except `ticket show`, `ticket join`, `results show`, `config`,
+`status parse`, `log tail` and `paths`; a command given `--accept-harness` is always a write. The
+workflow scripts already put the marker on their own commands. Put it in front of one command at
+a time:
+
+```
+FACTORY_DISPATCH=1 $RUNTIME/bin/factory decision add T-n "<line>"
+```
+
+Without the marker the write is refused with exit 2, and nothing is written. The refusal text
+deliberately does not name the marker, so that a role reading it is not told how to get past it.
+Its advice to "use a throwaway FACTORY_STATE" is meant for roles, not for you. Never export the
+marker: every role run started from that shell would inherit it. Run store writes from the
+repository root. From inside the store's `runs/` or `worktrees/`, where roles do their work, every
+write is refused, and the marker does not help. A run left in flight by a workflow that stopped
+keeps the refusal in place; clear it with:
+
+```
+FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLED
+```
+
 | | Command | What you decide |
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
@@ -350,6 +374,12 @@ next, how many rounds, what the checkers receive, when a merge is allowed, when
   killed runs included. A changed `park` file parks the ticket; a changed `escalate` file is queued
   for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not
   yet fired on a real ticket.
+- **Live-store fence.** While a run is in flight on a target, a write to its store without the
+  `FACTORY_DISPATCH=1` marker is refused. The workflow scripts mark their own commands, and the
+  operator marks one command at a time ("Where a human decides"). A write run from inside the
+  store's `runs/` or `worktrees/` is refused even with the marker. The fence stops a role's tools,
+  such as its test suite, from changing the live records by accident; it is not isolation. It is
+  tested, and has not yet fired on a real ticket.
 
 **Not built**
 
@@ -363,9 +393,9 @@ next, how many rounds, what the checkers receive, when a merge is allowed, when
 - **Per-role effort settings.** Each role has a model; none has an effort level.
 - **A status page.** `factory report TICKET` would render where a ticket is from the store alone.
   Today you read the store's YAML or ask the session running it.
-- **Current truth for the factory itself.** The spec store exists, but the factory's own
-  capabilities were built before it and never entered it. This page is the hand-written stand-in
-  until they are written from the tests.
+- **Current truth for the factory itself.** The spec store holds only the capabilities that
+  tickets have changed since it was created, not the whole factory. This page is the hand-written
+  stand-in for the rest until they are written from the tests.
 
 ## Where this can go
 
diff --git a/docs/changelog.md b/docs/changelog.md
index c0f63ab..9a0fa26 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -53,5 +53,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 49. After the 2026-10-04 Nanobot incident, where a role's tests overwrote the live bot's permission file and nothing in the factory noticed: an instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list, files only, with `~` meaning the account's home and never `HOME`. `run start` records a SHA-256 of each file, or that it is absent, in a per-run baseline that the store's `.gitignore` excludes, and refuses a directory or an entry that is neither absolute nor `~/`. Each run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A changed `park` file parks the ticket with `tripwire: <files> changed during <run>`, "during" because overlapping runs and the operator's own edits cannot be told apart; on a ticket already parked or closed the reason is queued as an escalation instead. A changed `escalate` file queues an escalation and the run goes on. Nothing prints a file's contents, and the workflow scripts stop on a `run finish` that parked the ticket instead of routing on the role's STATUS. The tripwire detects a write after the fact; it does not prevent one. The incident's code-level cause, a test module that imported a path function by name before the fixture replaced it, gives the coding standard rule 6: a test reaches a patched path through its module's attribute, and a new path outside the repository ships with a test guard that fails any test resolving it outside `tmp_path`; rule 4 lists rule 6 among the rules whose findings take no tag.
 50. After issue #35 (2026-10-04), where runs at the same time shared one session scratchpad and a verifier mixed another run's stale checkout into its base results (`23 failed, 103 passed` from two trees): every run gets its own scratch directory, `runs/<run id>/scratch/` in the store. `run start` creates it for every role after every guard has passed, and always makes sure the store's `.gitignore` excludes it; `ensure_gitignore` now writes its commented block only to an absent or empty file and otherwise appends only the lines a file lacks, never a second copy. The composer names the directory's absolute path in a "Scratch directory" section after "Running code". The shared preamble gains SCRATCH FILES, between RUNNING CODE and GUARDRAIL PATHS: put every file made for the run's own use there, never in a session scratchpad, a repository checkout or another run's directory, and this takes precedence over any other instruction to use a session scratchpad. Saving a ticket whose status changes to anything but `parked` removes the scratch directory of each finished run of that ticket, so a parked ticket keeps its files for the human and they go once it moves on.
 51. After issue #39 (2026-10-04), a batch of harness defects found in real runs: the harness suite passes with an uncommitted harness edit. Own-store tests that are not about that refusal run a test-only launcher that stubs it. The refusal itself is unchanged and still tested. `resolve --ruling` also takes an implementer's BLOCKED park and returns the sub-ticket to its implementer at the same round, with the ruling in its input. `resolve PARENT --replan F` sends a parked parent whose sub-tickets all merged back to the planner, with F as a ruling and the existing sub-tickets listed in its input. Sub-tickets that a later plan adds take the next free ids and may depend on merged ones. A park reason always ends with the failing command's error text. The workflows fall back to the refusal's JSON `error`, then to the exit code. A redispatch sets aside only the rows that did not pass, and the build re-runs only the checkers with no row on the commit. The store's `.gitattributes` marks run records `-whitespace`, written by `init` and `run start`. `init` refuses to create an instance on a throwaway store, and a missing `context.md` refuses a compose with exit 2. A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory.
+52. After issue #45 (2026-10-04), where a spec writer's test run executed `init` from inside its scratch directory and initialised this repository's live store, writing a spec store, `decisions.md` and six agent files: the store CLI fences an instance's own store. A write run from inside the store's `runs/` or `worktrees/` is refused, with or without the marker and with or without a run in flight. While any run is in flight on the store, a write without `FACTORY_DISPATCH=1` in its environment is refused. The read-only commands stay open, and any command given `--accept-harness` counts as a write. Both workflow scripts put `FACTORY_DISPATCH=1` in front of every clerk command; the operator puts it in front of one command at a time and never exports it. A refusal is exit 2, writes nothing, and advises a throwaway `FACTORY_STATE` without naming the marker. The fence is checked before the harness lock, so the marker cannot get past the lock. Declined from the request: a preamble line telling roles to use a throwaway store, because the incident came from the test suite rather than a command the role typed; and a tripwire on the store root, because role runs and other tickets' clerk commands legitimately write the store during a run, so a comparison could not tell whose write it saw.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index d8f32c8..c0ece7e 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -53,6 +53,8 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Tripwire on live files.** An instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list. A `~/` entry means the account's home directory, never the `HOME` variable, so a run under a throwaway `HOME` still watches the real files. The lists hold files only: a directory, or an entry that is neither absolute nor `~/`, refuses `run start`. `run start` records a SHA-256 of each listed file, or that it is absent, in a baseline in the run's directory, which the store's `.gitignore` excludes so no store commit carries a digest of a live secret. The run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A file created, deleted or modified counts as changed. A changed `park` file parks the ticket with the reason `tripwire: <files> changed during <run>`. The reason says "during", not "by", because runs on other tickets and the operator's own edits can overlap a run, and the tripwire cannot tell them apart. On a ticket already parked or closed, the same reason is queued as an escalation instead. A changed `escalate` file queues an escalation and the run goes on; that list is for files with legitimate outside writers. No event, reason or output names more than a file's path: nothing prints a file's contents. The workflow scripts stop on a `run finish` that parked the ticket, instead of routing on the role's STATUS. The tripwire detects a write after the fact; it does not prevent one.
 
+**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
+
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
 **Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
diff --git a/factory/cli.py b/factory/cli.py
index b28aff7..f08aaec 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -9,6 +9,7 @@ import argparse
 import datetime as dt
 import getpass
 import json
+import os
 import re
 import shutil
 import subprocess
@@ -868,6 +869,7 @@ def init_cmd(a):
         created.append(str(cfg_path))
     cfg = instance.load_config(inst)
     root = instance.state_root(inst, cfg)
+    fence(inst, cfg, root)
     agents: list[str] = []
     if instance.is_own_store(inst, cfg, root):
         ctx = inst / "context.md"
@@ -1190,6 +1192,36 @@ def build_parser() -> argparse.ArgumentParser:
 
 
 
+# ----- live-store fence: only the dispatcher writes a live store during a run ------------------
+
+READ_ONLY = {("ticket", "show"), ("ticket", "join"), ("results", "show"), ("config", None),
+             ("status", "parse"), ("log", "tail"), ("paths", None)}
+
+
+def _in_flight(root: Path) -> list[str]:
+    """Every run in flight on the store: the union of its tickets' in_flight lists."""
+    return [rid for p in sorted((root / "tickets").glob("*.yaml"))
+            for rid in store.read_yaml(p).get("in_flight") or []]
+
+
+def fence(inst: Path, cfg: dict, root: Path) -> None:
+    """Refuse a write to the instance's own store from inside its runs/ or worktrees/ (marker or
+    not), or while a run is in flight there unless FACTORY_DISPATCH=1. Accidents, not isolation."""
+    if not instance.is_own_store(inst, cfg, root):
+        return
+    own, cwd = instance.own_state_root(inst, cfg), instance.caller_cwd()
+    for sub in ("runs", "worktrees"):
+        if cwd.is_relative_to(own / sub):
+            raise Refused(f"role runs may not write the live store ({own}; called from inside its {sub}/); "
+                          "use a throwaway FACTORY_STATE")
+    if os.environ.get("FACTORY_DISPATCH") == "1":
+        return
+    runs = _in_flight(root)
+    if runs:
+        raise Refused(f"role runs may not write the live store ({root}; in flight: {', '.join(runs)}); "
+                      "use a throwaway FACTORY_STATE")
+
+
 def main(argv: list[str] | None = None) -> int:
     a = build_parser().parse_args(argv)
     try:
@@ -1199,6 +1231,8 @@ def main(argv: list[str] | None = None) -> int:
         inst = instance.require()  # refused when no instance is found: nothing is written
         cfg = instance.load_config(inst)
         root = store.state_root(cfg)
+        if (a.cmd, getattr(a, "sub", None)) not in READ_ONLY or a.accept_harness:
+            fence(inst, cfg, root)  # before the lock, so a fenced --accept-harness rewrites nothing
         instance.guard(inst, cfg, root, a.accept_harness)  # the harness lock (design C.2-C.4)
         a.fn(a, root, cfg)
         return 0
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 75703a7..b3b5438 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -18,7 +18,7 @@ const INSTANCE = args.instance
 let STATE = args.state || null  // set from `factory config` below when not given
 // target = the repo the implementer works in (default: the instance's repo, the parent of its `.factory/`);
 // integration = the branch merged into (default: config integration_branch, else the target's current branch).
-const ENV = [INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : '',
+const ENV = ['FACTORY_DISPATCH=1', INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : '',
   args.target ? `FACTORY_REPO=${args.target}` : '', args.integration ? `FACTORY_INTEGRATION_BRANCH=${args.integration}` : ''].filter(Boolean).join(' ')
 const BIN = `${ENV ? ENV + ' ' : ''}${REPO}/bin/factory`
 const PREFIX = args.agentPrefix || 'factory-'
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index 7503603..7f0c561 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -23,7 +23,7 @@ const TICKET = args.ticket
 const REPO = args.repo
 const INSTANCE = args.instance
 let STATE = args.state || null  // set from `factory config` below when not given
-const ENV = [INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : ''].filter(Boolean).join(' ')
+const ENV = ['FACTORY_DISPATCH=1', INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : ''].filter(Boolean).join(' ')
 const BIN = `${ENV ? ENV + ' ' : ''}${REPO}/bin/factory`
 const PREFIX = args.agentPrefix || 'factory-'
 // inlineRoles: the .claude/agents/factory-* definitions are not registered in this session (the
diff --git a/tests/factory/test_instance.py b/tests/factory/test_instance.py
index 5feff9e..e1cbf66 100644
--- a/tests/factory/test_instance.py
+++ b/tests/factory/test_instance.py
@@ -18,7 +18,8 @@ import yaml
 REPO = Path(__file__).resolve().parents[2]
 BIN = REPO / "bin" / "factory"
 CLEAN_CLI = Path(__file__).resolve().parent / "clean_harness_cli.py"
-STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")
+STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD",
+         "FACTORY_DISPATCH")
 NOT_FOUND = "no .factory/instance.yaml found from {cwd}; run factory init --repo-name NAME, or set FACTORY_INSTANCE"
 
 
@@ -271,7 +272,7 @@ def _start_triage(target: Path, request_file: Path) -> Path:
 def test_composed_input_opens_with_the_instance_context(target, request_file):
     (target / ".factory" / "context.md").write_text("CTX-MARKER for demo\nsecond line\n")
     run = _start_triage(target, request_file)
-    cp = cli(target, "run", "compose", run.name)
+    cp = cli(target, "run", "compose", run.name, FACTORY_DISPATCH="1")
     assert cp.returncode == 0, cp.stderr
     text = (run / "input.md").read_text()
     assert text.startswith("CTX-MARKER for demo\nsecond line\n## Output file\n")
diff --git a/tests/factory/test_live_store_guard.py b/tests/factory/test_live_store_guard.py
new file mode 100644
index 0000000..c98e23e
--- /dev/null
+++ b/tests/factory/test_live_store_guard.py
@@ -0,0 +1,168 @@
+"""The live-store fence (T-0024): only the dispatcher writes an instance's own store during a run.
+
+Two rules, both for every command outside the read-only list:
+- location: a write run from inside the own store's `runs/` or `worktrees/` is refused, with or
+  without `FACTORY_DISPATCH=1` and with or without a run in flight;
+- in flight: while any run is in flight on the own store, a write without `FACTORY_DISPATCH=1` is
+  refused.
+
+Black-box through `bin/factory` in scratch target repos. The `cli` helper drops FACTORY_DISPATCH
+from the inherited environment (test_instance.STRIP), so a runner that exported the marker cannot
+change a result; a case that needs the marker passes it explicitly.
+"""
+from __future__ import annotations
+
+from pathlib import Path
+
+import pytest
+
+from .test_instance import cli, git_repo, js, tree
+
+RULE = "role runs may not write the live store"
+
+
+@pytest.fixture
+def target(tmp_path: Path) -> Path:
+    t = git_repo(tmp_path / "target")
+    cp = cli(t, "init", "--repo-name", "demo")
+    assert cp.returncode == 0, cp.stderr
+    req = tmp_path / "r.md"
+    req.write_text("# demo\n\nDo the thing.\n")
+    assert cli(t, "ticket", "new", "--file", str(req)).returncode == 0
+    return t
+
+
+def state(target: Path) -> Path:
+    return target / ".factory" / "state"
+
+
+def start_triage(target: Path) -> str:
+    cp = cli(target, "run", "start", "--role", "triage", "--ticket", "T-0001")
+    assert cp.returncode == 0, cp.stderr
+    return js(cp)["run_id"]
+
+
+def snapshot(target: Path) -> dict[str, bytes]:
+    return {**tree(target / ".factory"), **tree(target / ".claude")}
+
+
+def request(tmp_path: Path) -> str:
+    p = tmp_path / "r2.md"
+    p.write_text("# other\n\nDo another thing.\n")
+    return str(p)
+
+
+def assert_refused(cp, *details: str) -> None:
+    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
+    assert RULE in cp.stderr and "use a throwaway FACTORY_STATE" in cp.stderr
+    assert "FACTORY_DISPATCH" not in cp.stderr + cp.stdout
+    assert js(cp) == {"ok": False, "error": cp.stderr.strip()}
+    for d in details:
+        assert d in cp.stderr
+
+
+# ----- in flight ------------------------------------------------------------------------------
+
+def test_unmarked_writes_are_refused_while_a_run_is_in_flight(target, tmp_path):
+    rid = start_triage(target)
+    (target / "sub").mkdir()
+    before = snapshot(target)
+    for cwd in (target, target / "sub"):
+        for argv in (("ticket", "new", "--file", request(tmp_path)),
+                     ("ticket", "transition", "T-0001", "--to", "closed", "--by", "t"),
+                     ("decision", "add", "T-0001", "x"),
+                     ("ticket", "set", "T-0001", "title=y")):
+            assert_refused(cli(cwd, *argv), f"{state(target).resolve()}; in flight: {rid}")
+    assert snapshot(target) == before
+
+
+def test_init_is_refused_while_a_run_is_in_flight_and_rewrites_nothing(target):
+    start_triage(target)
+    agents = target / ".claude"
+    for p in sorted(agents.rglob("*"), reverse=True):
+        p.unlink() if p.is_file() else p.rmdir()
+    agents.rmdir()
+    before = snapshot(target)
+    assert_refused(cli(target, "init", "--repo-name", "x"))
+    assert snapshot(target) == before and not agents.exists()
+
+
+def test_a_harness_acceptance_is_refused_while_a_run_is_in_flight(target):
+    start_triage(target)
+    lock = (target / ".factory" / "harness.lock").read_text().strip()
+    before = snapshot(target)
+    assert_refused(cli(target, "--accept-harness", lock, "ticket", "show", "T-0001"))
+    assert snapshot(target) == before
+
+
+def test_reads_answer_while_a_run_is_in_flight(target):
+    rid = start_triage(target)
+    for cwd in (target, state(target) / "runs" / rid / "scratch"):
+        for argv in (("ticket", "show", "T-0001"), ("config",), ("log", "tail"),
+                     ("results", "show", "T-0001"), ("paths",)):
+            cp = cli(cwd, *argv)
+            assert cp.returncode == 0, (argv, cp.stderr)
+
+
+def test_a_marked_write_from_the_repository_root_goes_through(target):
+    rid = start_triage(target)
+    assert cli(target, "decision", "add", "T-0001", "marked", FACTORY_DISPATCH="1").returncode == 0
+    cp = cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1")
+    assert cp.returncode == 0, cp.stderr
+    assert js(cli(target, "ticket", "show", "T-0001", "--json"))["in_flight"] == []
+
+
+def test_only_the_value_1_is_the_marker(target):
+    start_triage(target)
+    assert_refused(cli(target, "decision", "add", "T-0001", "x", FACTORY_DISPATCH="yes"))
+
+
+def test_with_no_run_in_flight_unmarked_writes_go_through(target, tmp_path):
+    rid = start_triage(target)
+    assert cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1").returncode == 0
+    assert cli(target, "ticket", "new", "--file", request(tmp_path)).returncode == 0
+    assert cli(target, "decision", "add", "T-0001", "after").returncode == 0
+
+
+def test_a_throwaway_store_is_not_fenced(target, tmp_path):
+    rid = start_triage(target)
+    other = tmp_path / "s"
+    assert cli(target, "init", FACTORY_STATE=str(other)).returncode == 0
+    scratch = state(target) / "runs" / rid / "scratch"
+    cp = cli(scratch, "ticket", "new", "--file", request(tmp_path), FACTORY_STATE=str(other))
+    assert cp.returncode == 0, cp.stderr
+
+
+# ----- location -------------------------------------------------------------------------------
+
+def test_marked_writes_from_a_runs_scratch_directory_are_refused(target, tmp_path):
+    rid = start_triage(target)
+    scratch = state(target) / "runs" / rid / "scratch"
+    before = snapshot(target)
+    for argv in (("decision", "add", "T-0001", "x"), ("init", "--repo-name", "x"),
+                 ("ticket", "new", "--file", request(tmp_path))):
+        assert_refused(cli(scratch, *argv, FACTORY_DISPATCH="1"),
+                       f"{state(target).resolve()}; called from inside its runs/")
+    assert snapshot(target) == before
+
+
+def test_marked_writes_from_under_worktrees_are_refused(target, tmp_path):
+    start_triage(target)
+    wt = state(target) / "worktrees" / "T-0001" / "sub"
+    wt.mkdir(parents=True)
+    before = snapshot(target)
+    for argv in (("ticket", "new", "--file", request(tmp_path)), ("init",)):
+        assert_refused(cli(wt, *argv, FACTORY_DISPATCH="1"),
+                       f"{state(target).resolve()}; called from inside its worktrees/")
+    assert snapshot(target) == before
+
+
+def test_writes_from_a_finished_runs_scratch_directory_are_refused(target, tmp_path):
+    rid = start_triage(target)
+    assert cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1").returncode == 0
+    assert js(cli(target, "ticket", "show", "T-0001", "--json"))["in_flight"] == []
+    scratch = state(target) / "runs" / rid / "scratch"
+    before = snapshot(target)
+    assert_refused(cli(scratch, "ticket", "new", "--file", request(tmp_path)), "called from inside its runs/")
+    assert_refused(cli(scratch, "decision", "add", "T-0001", "x", FACTORY_DISPATCH="1"), "called from inside its runs/")
+    assert snapshot(target) == before
