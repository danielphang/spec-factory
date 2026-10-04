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
