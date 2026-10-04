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

## Critic rounds

round 1 · spec v2 · run-0227-critic · REVISE

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

round 2 · spec v3 · run-0229-critic · APPROVE

## Spot checks (round 2; base `3a3f58c`, clean clone under this run's scratch, fresh HOME)

Changed text only, per the convergence rule.

Paths and symbols: `tests/factory/test_instance.py:21` is `STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")`, and `cli()` at `:25-27` builds the environment from `os.environ` minus `STRIP` and then applies `**extra`, so an explicit `FACTORY_DISPATCH="1"` argument wins over the strip, as Tests to change says. `:271-274` is `test_composed_input_opens_with_the_instance_context` with its `cli(target, "run", "compose", run.name)` call. `factory/instance.py:141-166` `guard()`: uncommitted edits refused first, then `--accept-harness` rewrites the lock and logs `harness.accepted` inside the function, then the lock check; so the new Decisions bullet (fence before the lock, else a fenced `--accept-harness` would write before it was refused) matches the code. `factory/cli.py:1202` is the `instance.guard(...)` call in `main()`. `docs/changelog.md` still ends at entry 51.

Acceptance command run on base: the new scenario "A marked write from a harness checkout with an uncommitted edit is still refused" printed `exit=2 lock=1 store=unchanged`; stderr's first line was `harness <clone> has uncommitted changes:`, as the REGRESSION line in Acceptance states. (My exported `TMPDIR` was not honoured by `mktemp` in the sandbox, so the scenario's scratch target landed under the system temp directory; it is a fresh git repository either way and no protected path was touched.)

The prototype-side results (fence refusal from a dirty checkout, `1 failed, 253 passed` with the marker exported before the one test is marked) are the writer's. Round 1 accepted the prototype's shape from the code; the v3 additions follow from the same code, so I accept them again.

## Prior findings (round 1)

- [BLOCKING] 6 Decisions, first bullet: RESOLVED. Problem now glosses instance, instance B, current truth and `decisions.md` before Decisions uses them; Evidence glosses "closed as applied"; Decisions no longer cites "Answer 1" or a bare "#37", and names the Driver session as the one that runs instance A. Read in order as the gate operator, every term of art in Decisions now has an earlier gloss.
- [NIT] 2 Tests to change (`STRIP`): RESOLVED. `FACTORY_DISPATCH` is added to `STRIP` in the same file, with a reason and a prototype result for each direction; Risk lists the tuple under guardrail paths.
- [NIT] 5 design.md A.4 / Risk (fence before the lock): RESOLVED. Design part C adds the sentence; Decisions gains the bullet with the rejected ordering and why; a new REGRESSION scenario checks that a marked write still meets the lock, and it prints the stated result on base.

## Findings

No blocking issues. No new findings on the changed text.

## Out-of-scope observations

- Carried from round 1, unchanged and accepted by the writer: `t0024-e2e.mjs` runs clerk commands with the environment unchanged, so an exported marker would let it pass without part B; the first scenario fails in that case, so the set still catches it.

round 1 · spec v4 · run-0233-critic · APPROVE

Spec under review: T-0024 v4 (the live-store fence). The ticket was reset after the gate send-back, so this is a fresh round for this run; I still read it against the five requested changes listed under Responses and the round-1/round-2 critic findings that v3 resolved.

## What I checked

Cited paths and symbols, on `abaa75a` in `~/dev/spec-factory`:
- `factory/cli.py` lines 223 (`scratch` mkdir), 231 (`in_flight.append`), 247 (`worktrees/<ticket>`), 259 (`d / "wt"`), 312-313 (`in_flight.remove`), 434 (`ticket_ready_implementers`), 619 (`ticket_parent_check`), 638-639 (`_by()` = `getpass.getuser()`), 845 (`init_cmd`), 870 (`root = instance.state_root(inst, cfg)`), 885 (`shutil.copyfile` of agent files), 917 (`spec_tasks`), 1063 (`--by required=True`), 1193 (`main`), 1201 (`root = store.state_root(cfg)` followed by `instance.guard`). All as cited.
- `factory/instance.py`: `caller_cwd()` (41, resolves `FACTORY_CWD` or cwd), `find()` (55), `own_state_root()` (93, resolved), `is_own_store()` (105), `guard()` (141). Design A.3 uses only symbols that exist, and both paths it compares are already `.resolve()`d, so `Path.is_relative_to` (Python 3.11 per `pyproject.toml`) is sound.
- `factory/workflows/intake.js:26` and `build.js:21` build `ENV`; `:52` / `:43` tell the clerk "from the repository root". `README.md:102-103` and `:365-368` hold the two sentences the change rewrites. `tests/factory/test_instance.py:21` (`STRIP`), `:25-32` (`cli()`), `:132-137`, `:271-276` as cited.
- Log and store: `log/2026-10.jsonl:995` is the `store.initialised` event with the three files and six agent paths; `:997` and `:1006` are run-0196's and run-0198's escalations; `:1121-1123` and `:1136-1141` give the two in-flight operator writes. run-0196 meta: started 13:16:09, finished 13:47:49, T-0023. `openspec/specs/` holds the six capabilities named. Commit `81294c8` says what the spec quotes. `git diff 3a3f58c HEAD --stat -- factory bin tests README.md docs dev` prints nothing. `.claude/` is absent. `grep -rn FACTORY_DISPATCH factory bin docs dev .factory/instance.yaml` finds nothing. The committed `tickets/T-0024.yaml` at HEAD has `in_flight: []`.

Acceptance commands I ran myself on base, through the fresh-`HOME` wrapper with `TMPDIR` in this run's scratch directory:
- "Unmarked writes from inside the target are refused while a run is in flight, init included": `init=0 new=0 transition=0 decision=0 store=changed agents=written` (matches the stated today result; `init` from a subdirectory of a target with a run in flight rewrote the agent files).
- "The refusal names the throwaway store and not the marker": `rule=0 state=0 marker=0 json=0 inside=0`.
- "A harness acceptance is refused while a run is in flight": `accept=0 store=changed`.
- "Writes from a finished run's scratch directory are refused with no run in flight": `idle=1 new=0 decision=0 store=changed`. The scratch directory survives `run finish`, so the scenario's `cd $W` is valid.
- "A marked write from the repository root still writes while a run is in flight": `decision=0 finish=0 cleared=1` (regression baseline holds).
- "Every clerk command of both workflows carries the marker": `intake: sent unmarked=6`, `build: sent unmarked=2`.
- The five documentation scenarios: `CONTIGUOUS` / `2`; `first=0 command=0 unnamed=0 export=0 rundirs=0`; `stale=1 listed=0`; `bullet=1 stale=1`. All match the stated today results, so every NEW item fails today for the reason given.

I could not re-run the prototype: the spec writer's clones lived in run-0230/run-0231 scratch directories, which the harness has cleared. The `254 passed` and negative-control figures rest on the writer's report. The negative controls are specific enough (which scenario detects which missing part, with the exact output) that I accept them.

The five gate changes under Responses are present in the text: the location rule (design A.3, a new requirement with two NEW scenarios, Decisions bullet with the two rejected variants); the README paragraph first under "Where a human decides" with a scenario that checks each claim; the verifier-in-flight correction with evidence at `cli.py:231` and `:312-313`; the named suite-guard follow-up; the two-call-site build order ahead of #46. The main() call site the design names (after `root = store.state_root(cfg)`, before `instance.guard`) exists exactly as described, and the `init_cmd` call site at `:870` comes before every write for an existing instance.

## Findings

[SHOULD-FIX] 6 Operator steps, step 1
Problem: "move the runtime" is this system's name for the detached worktree the factory runs from, and nothing earlier in the spec glosses it; the operator at the gate meets it first here.
Evidence: `grep -n runtime` over the spec body finds the word only in Evidence ("runtime scenario", a different sense) and in this step. The step does point to README "Upgrading the runtime" (`README.md:225`), which is where the term is defined, so the reader is told where to look rather than left to infer. That is why I rate this SHOULD-FIX rather than BLOCKING under rubric 6: the standard's rule 2 wants the gloss inline, but the reader is not translating.
Suggested fix: "move the runtime, the checkout the factory runs from, to the merged revision and accept it in each target, as README 'Upgrading the runtime' says".

[NIT] 1 Evidence, "The lasting effect"
Problem: the citation `dev/issues.md:19` points at issue #11's row, which says nothing about closing as applied.
Evidence: `sed -n 19p dev/issues.md` is the #11 row; "closed as applied ... no spec store on this instance" is in the #19 and #23 rows at `dev/issues.md:26` and `:30`.
Suggested fix: cite `dev/issues.md:26` (or `:26,30`).

[NIT] 4 Risk table, row "A role inside a code checkout that tracks its own `.factory/`"
Problem: "Committed copies carry no in-flight runs" is stated as a property of the store, but it holds only because the operator commits the store between steps; a commit taken mid-run would carry a non-empty list.
Evidence: HEAD's `tickets/T-0024.yaml` has `in_flight: []`, and no committed ticket I sampled lists a run, so it is true today. The consequence of a violation is benign (a write to the checkout's own copy is refused), so nothing changes in the design.
Suggested fix: "Committed copies carry no in-flight runs while the operator commits the store between steps, as today".

No blocking issues. The rubric items hold: paths and outputs are real; every NEW scenario fails today for the stated reason and the stub-detecting controls are described; the change fits one PR with two touched harness files, two workflow one-liners and documents; Tests to change names one test and one tuple with a verified reason each; the location rule, marker name, read-only list, lock order and the cut parts B and C are all recorded as decisions with their rejected alternatives; it does not conflict with #46 and states the build order. I would bet on this spec producing a correct PR.

Prior findings (round 1 and 2 critics, carried in v3 and unchanged here): RESOLVED. Gate changes 1-5 under Responses: RESOLVED as described above.

## Out-of-scope observations
- The e2e scenario's stub agent runs each clerk command with `sh -c` from the checkout under test, which for instance B is the live repository root. `FACTORY_INSTANCE` is passed explicitly, so it never touches the live instance; worth remembering if the scenario is ever copied without that argument.
