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

STATUS: APPROVE
CONFIDENCE: high, every cited path and today-result I spot-checked matched; the prototype figures are the writer's, not re-run, because the prototype clone is gone
ESCALATIONS: none
