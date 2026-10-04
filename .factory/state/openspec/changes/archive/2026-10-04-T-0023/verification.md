## Acceptance

Every scenario that names `t0023-parent.sh`, `t0023-closed.sh` or `t0023-wf.mjs` needs the first scenario's GIVEN block run once; it writes those three files under `${TMPDIR:-/tmp}`. Every command runs from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each "today" result below came from running the GIVEN block and then the WHEN verbatim on `main` at `67447b1`, under a throwaway `HOME`. The exceptions are noted. In round 2 I re-ran the changed re-plan scenario and both `harness-suite` scenarios with `TMPDIR` set to my scratch directory, which lies inside this repository, to confirm they hold for a role that follows its scratch rule.

- A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling → NEW. Today it prints `exit=2 parked pr=0`, `ruling=missing`, `in_input=0`. The ruling is refused, and the implementer cannot start on a parked ticket.
- A ruling on a critic ESCALATE still returns the ticket to the critic → REGRESSION. Today it prints `exit=0 ready-for-critic`.
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list → NEW. Today it prints `exit=2 parked` and `in_input=0 listed=0`, because `--replan` is not an option, so the planner cannot start on the parked parent. Run in round 2.
- A re-plan is refused while a sub-ticket is not merged → NEW. Today it prints `names=0`: the refusal is argparse's unknown-option error, which names no sub-ticket. Then it prints `parked spec-v1.yaml `.
- A redispatch after a killed reviewer keeps the verifier's passing rows → NEW. Today it prints `kept: ` and `set aside: ci.yaml reviewer.yaml verifier.yaml `.
- A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval → NEW. Today it prints `kept: ` and `set aside: ci.yaml reviewer.yaml verifier.yaml `.
- A later plan's sub-tickets take the next free ids and may depend on a merged sibling → NEW. Today it prints only `"ready": []`. The add is refused (`ST-1: depends on T-0001.2, which is not a sub-ticket of this plan`), so no id or dependency line is printed.
- A plan that reuses an existing sub-ticket id is refused and writes nothing → REGRESSION. Today it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml ` (refused as `T-0001.1 already exists`). After the change it is refused by the reused-label check, not by `already exists`, and the reused label must never silently become `T-0001.3`.
- A refused archive or sub-ticket add parks with the refusal text → NEW. Today it prints `park: archive: `, `start: planner`, `park: harness-bug: subticket add: `.
- A refused run start during intake parks with the refusal text → NEW. Today it prints `start: triage`, `park: harness-bug: run start triage: `.
- A command that prints no JSON parks with its exit code → NEW. Today it prints `park: archive: `.
- A redispatched sub-ticket runs only the checker whose row was set aside → NEW. Today it prints `start: reviewer`, `start: verifier`, `park: stub stop`.
- After an implementer run both checkers run → REGRESSION. Today it prints `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`.
- Run records in a store pass whitespace checks and other store files do not → NEW. Today it prints `runs=2`, `other=2`.
- A run start adds the whitespace rule to an existing store → NEW. Today it prints `rule=0`.
- init refuses to create an instance on a throwaway store and writes nothing → NEW. Today it prints `exit=0 instance=written store=written names_state=0`.
- A missing briefing refuses the compose with exit 2 → NEW. Today it prints `exit=1 input=none names_context=1`, from the uncaught `FileNotFoundError`.
- Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory → NEW. Today it prints `state=0 instance=0 repo=0`.
- An absolute FACTORY_STATE is used as given → REGRESSION. Today it prints `absolute=1`.
- The harness suite passes with an uncommitted harness edit → NEW. Today the WHEN, run verbatim in round 2, prints `23 failed, 192 passed in 135.15s (0:02:15)`. Those 23 are the harness-lock refusals of H8, and the count matches the clone-and-`uv sync` run in Evidence. The `/tmp/t0023-suite.*` directory was gone afterwards.
- The uncommitted-edit refusal still holds on an instance's own store → REGRESSION. Today it prints `exit=2`, then `has uncommitted changes:`. Re-run in round 2.
- The changelog records the change in order → NEW. Today it prints `50 CONTIGUOUS` and then `0`. The `0` is derived, not run in this exact form: with no entry 51, `sed` prints nothing and `grep -c .` counts 0.
- The README describes the new resolve verbs → NEW. Today it prints `replan=0 gap=1`.
- The README says relative paths resolve from the caller's directory → NEW. Today it prints `0`.
- The change adds no whitespace errors → REGRESSION. Today it prints `exit=0` (empty range).

## Responses

- [BLOCKING] 6, Operator steps glosses: FIXED. Operator steps now opens by saying what the runtime is (the pinned copy of the harness), what an instance is (a repository the factory serves, with its own settings and store), and what `--accept-harness <commit>` does. The Driver session is glossed too.
- [SHOULD-FIX] 6/3, H1-H5 used for two things: FIXED. The items keep the requester's ids H1 to H9, and the Problem says so. The parts are now A to G, then I (re-plan, steps I1 to I5) and J (documents, steps J1 to J5). design.md says there is no part H, and why. The seam table, Risk and every step reference use the new letters.
- [SHOULD-FIX] 2, the suite scenario needs `TMPDIR` outside any work tree: FIXED by the second of the critic's options, with the choice written into the command so that no role has to make it. The WHEN now gives pytest a fresh `mktemp -d /tmp/t0023-suite.XXXXXX` as its `TMPDIR` and removes it at the end. I did not take the first option. Bounding git with `GIT_CEILING_DIRECTORIES` fixes only one of the four affected tests. A clean clone run with `TMPDIR` inside this repository printed `4 failed, 211 passed`, and three of those four fail because the instance walk-up finds this repository's `.factory/instance.yaml`, not because of git. Fixing all four needs its own design, so it is an out-of-scope observation. Run verbatim in round 2 with my own `TMPDIR` inside this repository, the new WHEN printed `23 failed, 192 passed`, the H8 baseline, with no extra failures. I also dropped the general "`TMPDIR` outside any git work tree" requirement from the first scenario and from Risk. The critic ran seven scenarios with `TMPDIR` inside the repository and got the stated results. I re-ran three more the same way. Each remaining scenario either builds its own git repository under `mktemp -d` or names its instance and store explicitly, so where `TMPDIR` lies does not change what it finds. I did not run those remaining scenarios that way.
- [SHOULD-FIX] 4, the re-planning planner does not know what merged: FIXED by the second suggestion. New step I4 makes `compose` list the parent's existing sub-tickets, with title and state, in the planner's input. The planner needs the list anyway: without the ids it cannot write the `Depends on: T-0001.2` that step I1 now accepts. A new Decision records this, and rejects asking the human to restate in the note what merged. The re-plan scenario now also checks the list (`listed=2`). Today it prints `in_input=0 listed=0`.
- [NIT] 6, Operator step 1 names a file that does not exist: FIXED. The check names `run-0102-verifier/input.md`, which exists. It quotes the full output line, `….input.md: whitespace: unset`, and the `unspecified` answer before the file is written. Both answers come from a scratch repo in round 2.
- [NIT] 6, Evidence H2 and H3: FIXED. H3 now says exit 2 means `git diff --check` found whitespace errors and exit 0 means none. H2 says T-0014, T-0016, T-0018 and T-0020 are four parent tickets that parked at their close. For "the retro" in H4 I did not use the suggested gloss "the retrospective trial on the Nanobot instance". `.factory/answers/retro-trial-2026-10-04/inputs.md` line 1 reads "Retro inputs: spec-factory instance B store", so the trial reviewed this repository's own store. H4 now says so.

Out-of-scope observations:
- `resolve --ruling` on a park reason `ESCALATE from reviewer` sends the sub-ticket to `ready-for-critic`, because every non-planner ESCALATE goes there (`factory/cli.py`, the `--ruling` branch). The design returns a reviewer ESCALATE to the implementer with the round reset (`docs/design.md` line 102).
- Four tests in `tests/factory/test_instance.py` assume their temporary directory lies outside every git repository and instance: `test_init_refused_outside_a_git_work_tree` (line 126), `test_command_outside_any_instance_refused_and_writes_nothing` (line 203), `test_no_fallback_even_with_a_store_named` (line 213) and `test_paths_outside_any_instance` (line 326). With `TMPDIR` inside an instance's repository, they act on that live instance. The first one runs `init` there, which is how the round-1 writer's run created this repository's `.claude/agents/`, `.factory/state/openspec/` and `.factory/state/decisions.md` (ESCALATIONS).
- `dev/build-harness.spec.md` line 314 describes `--amend-spec` on a parked parent, which is not built. This change adds `--replan` beside it without amending that text.

## Critic rounds

round 1 · spec v1 · run-0197-critic · REVISE

## Critic review, round 1 (spec v1, T-0023)

What I checked. Every cited line I opened matches the text the spec attributes to it: `factory/cli.py` 747-751 (the `--ruling` branch), 761-779 (`--redispatch`), 829 and 841-850 (`init_cmd`), 1170-1173 (the refusal's stderr line and JSON `error`); `factory/compose.py` 85 and 190-191; `factory/workflows/build.js` 41-56, 146-155, 191 and 256; `factory/workflows/intake.js` 50-64; `factory/subtickets.py` 48 and 84-85; `factory/instance.py` 46, 72, 89 and 137-139; `factory/store.py` 40; `docs/design.md` 98-102; `dev/build-harness.spec.md` 314; `.factory/instance.yaml` 61; `tests/factory/test_harness_lock.py` 8-10; `tests/factory/test_shepherd.py` 585-587; `README.md` 321. `results show` exists and prints `rows` and `missing` (`factory/cli.py` 519-524); `ticket set`, `ticket head`, `ticket parent-check` and `results record --killed` exist; `caller_cwd()` exists (`factory/instance.py` 38). `pyproject.toml` has `package = false`, so the symlinked `.venv` in the harness-suite scenario does import the clone's package, not this checkout's.

I ran the GIVEN block and then, verbatim, under a throwaway HOME and `TMPDIR` set to this run's scratch directory: the ESCALATE regression scenario (`exit=0 ready-for-critic`), the BLOCKED scenario (`exit=2 parked pr=0`, `ruling=missing`, `in_input=0`), the re-plan refusal (`names=0`, `parked spec-v1.yaml `), the later-plan scenario (refused with `ST-1: depends on T-0001.2, which is not a sub-ticket of this plan`, then `"ready": []`), and two node scenarios (`park: archive: `; `start: reviewer`, `start: verifier`, `park: stub stop`). Each equals the spec's stated "today" result, so the NEW items fail today for the reason given and the REGRESSION items pass. I also checked the three existing `init` assertions on `written` (`test_instance.py` 147 and 157, `test_spec_store.py` 151): each runs a second `init` on a store that already has `.gitattributes` by then, so part C2 leaves them true. The `init` tests strip `FACTORY_STATE` (`STRIP`, `test_instance.py` 19), so part E1 does not reach them.

### Findings

[BLOCKING] 6 — Operator steps, first paragraph
Problem: the paragraph tells the operator to wait until "the runtime has moved to a revision with this change and each instance has accepted it with `--accept-harness <revision>`", and none of `runtime`, `instance` or `--accept-harness` is glossed in the Problem, Evidence, Decisions or Operator steps; the only gloss of `runtime` sits in Risk, which the operator is not held to read.
Evidence: grep of the four human-facing sections for "runtime", "instance" and "accept-harness": `runtime` is first explained in Risk ("The runtime is the pinned checkout of the harness that runs tickets"); `--accept-harness` is explained nowhere in the spec, and it is the very example the writing standard uses for rule 2 (`docs/writing.md`).
Suggested fix: open Operator steps with one sentence such as "The factory runs from a pinned copy of the harness, the runtime; each repository it serves, an instance, adopts a new harness commit only when the operator accepts it with `--accept-harness <commit>`", then the steps as written.

[SHOULD-FIX] 6/3 — design.md, part H (steps H1-H5) against the Problem table (items H1-H9)
Problem: the spec uses `H1`..`H5` for two different things, the issue's items (H1 is the BLOCKED ruling) and part H's steps (H1 is `subtickets.parse`), in a NEEDS-SPLIT spec where the planner cuts by lettered part and the seam table maps "H (H9)".
Evidence: Problem table row `H1`; design.md "**H. Re-plan ...** (H9 ...)" followed by "- H1. `subtickets.parse(...)`"; Evidence bullet "**H1.**" refers to the ruling.
Suggested fix: rename the issue items (for example `#1`..`#9`, or keep the requester's numbering but write them as "item H1") or letter part H's steps differently, consistently in the seam table, Evidence, Root cause and Risk.

[SHOULD-FIX] 2 — specs/harness-suite/spec.md, "The harness suite passes with an uncommitted harness edit"
Problem: the scenario is valid only with `TMPDIR` outside any git work tree, but every agent's scratch directory, the only place the preamble lets it write, is inside this repository's work tree, so an implementer or verifier following the rules gets the writer's own invalid result (`27 failed`) and reports a correct change as not met.
Evidence: verification.md says the writer's verbatim run printed `27 failed, 188 passed` with `TMPDIR` inside the repo and quotes the clone-and-`uv sync` figure instead; the writer's out-of-scope note names the cause, `test_init_refused_outside_a_git_work_tree` assuming `tmp_path` is outside a repository. My scratch directory for this run is `.factory/state/runs/run-0197-critic/scratch`, inside the work tree.
Suggested fix: either bring that one test into part G and Tests to change (it can make the directory look like no repository with `GIT_CEILING_DIRECTORIES`, which is a test-only change), or state in the scenario that the verifier runs this one scenario with a `TMPDIR` under the system temp directory and records that exception in its output; today the spec leaves the verifier to choose between a rule and a spurious failure.

[SHOULD-FIX] 4 — Decisions, the `--replan` bullet, and design.md H4
Problem: on a re-plan the planner receives the approved spec, the decisions and the operator's note, but nothing that says which sub-tickets already merged, so whether it re-plans the whole spec or only the fix rests silently on what the operator wrote in F.
Evidence: `factory/compose.py` planner branch (lines ~153-159) adds the pinned spec, decisions and rulings only; design.md H4 says "No change to `compose`"; the design (line 100) says the human "re-plans (new sub-tickets under the same parent)" without saying what the planner is told.
Suggested fix: add one sentence to the `--replan` decision saying the note F must state which parts are merged and what remains, or have compose add the parent's sub-ticket list with states to the planner's input; either makes the choice visible.

[NIT] 6 — Operator steps, step 1
Problem: the check names `.factory/state/runs/run-0102-verifier/diff.patch`, which does not exist in this store; `git check-attr` answers for any path, so the check still works, but the operator will look for a file that is not there.
Evidence: `ls .factory/state/runs/run-0102-verifier/` prints `input.md meta.yaml output.md system-prompt.txt`; the whitespace findings in that run's output.md are about the Nanobot store's records under `intake/state/runs/`.
Suggested fix: name `run-0102-verifier/input.md`, or any store record that exists.

[NIT] 6 — Evidence, H2 and H3
Problem: H3 quotes `runs=2` and `other=2` without saying that exit 2 means `git diff --check` found whitespace errors (writing rule 5); H2 names `T-0014`, `T-0016`, `T-0018`, `T-0020` and "the retro" without saying what they are (rule 6).
Evidence: the Evidence bullets as written.
Suggested fix: add "exit 2: whitespace errors were reported" after the H3 figures, and "(the parked parents)" and "(the retrospective trial on the Nanobot instance)" at the H2 and H4 first uses.

### Not findings, noted so the writer does not change them
- The ESCALATE-from-reviewer routing to `ready-for-critic` is pre-existing and correctly left out of scope.
- `package = false` makes the harness-suite scenario's symlinked `.venv` sound: the clone's `python -m pytest` imports the clone's `factory`.
- The routing table's single `parked:` row covers sub-tickets too, so A1 and H3 need no routing change, as the spec says.

round 2 · spec v2 · run-0199-critic · APPROVE

## Critic review, round 2 (spec v2, T-0023)

What I checked. `main` is still at `67447b1`. Every cited symbol and line the changed text adds exists: `store.subtickets_of(root, parent)` (`factory/store.py` line 214, returns the records in id order, so step I4's "one line per sub-ticket, in id order" needs no sort); `compose`'s `planner` branch adds the rulings at lines 152-159, so "after the rulings" has a place; `run_start` calls `store.ensure_gitignore(root)` after its last refusal and after `meta.yaml` is written (`factory/cli.py` line 222), so step C2's "runs after every refusal" is right. Every line the new Tests-to-change paragraph cites holds what the spec says: `test_spec_store.py` 151 (second `init` writes `[]`), `test_instance.py` 42 (tree snapshot), 79 (`.factory/` listing), 147 and 157 (`written` on a second `init`), `test_harness_lock.py` 47 and 69 (tree and directory listings), `test_run_scratch.py` 163 and `test_tripwire.py` 230 (one run directory each). `git check-attr whitespace -- .factory/state/runs/run-0102-verifier/input.md` prints `.factory/state/runs/run-0102-verifier/input.md: whitespace: unspecified` today, as Operator step 1 says, and the file exists.

I ran six acceptance commands verbatim, under a throwaway `HOME`, with `TMPDIR` set to this run's scratch directory inside the repository, to test the writer's unverified claim that the scenarios no longer depend on where `TMPDIR` lies. Each printed the spec's stated "today" result: the re-plan scenario `exit=2 parked` and `in_input=0 listed=0`; init-refuses `exit=0 instance=written store=written names_state=0`; missing briefing `exit=1 input=none names_context=1`; relative paths `state=0 instance=0 repo=0`; whitespace `runs=2` and `other=2`; the suite scenario `23 failed, 192 passed in 136.67s (0:02:16)`, after which no `/tmp/t0023-suite.*` directory remained. `git status` of this repository was identical before and after, so the throwaway-store scenarios touched no live instance: `init_cmd` picks its instance from the git top level of the caller's directory (`factory/cli.py` line 829), and each scenario's `cd $T/tgt` is its own repository.

### Prior findings

- [BLOCKING] 6, Operator steps glosses: RESOLVED. The first paragraph now says what the runtime, an instance and `--accept-harness <commit>` are before any step uses them; step 2 glosses the Driver session.
- [SHOULD-FIX] 6/3, H1-H5 used for two things: RESOLVED. Items keep H1-H9; parts are A-G, I, J with no part H, and the seam table, Evidence, Root cause, Risk and every step reference agree.
- [SHOULD-FIX] 2, the suite scenario and `TMPDIR`: RESOLVED. The WHEN gives pytest `mktemp -d /tmp/t0023-suite.XXXXXX` and removes it; run verbatim today it prints the H8 baseline, not the spurious 27. The writer's reason for not taking the test fix (three of the four tests fail on the instance walk-up, not on git) matches `instance.find` (`factory/instance.py` lines 42-53, an unbounded walk-up). The remaining `TMPDIR` dependency the writer did not re-run is gone: see the six runs above.
- [SHOULD-FIX] 4, the planner does not know what merged: RESOLVED. Step I4 lists the existing sub-tickets in the planner's input, a Decision records it, and the re-plan scenario checks the list.
- [NIT] 6, Operator step 1 names a missing file: RESOLVED.
- [NIT] 6, Evidence H2 and H3 glosses: RESOLVED. The writer's correction on H4 is right: `.factory/answers/retro-trial-2026-10-04/inputs.md` line 1 reads "Retro inputs: spec-factory instance B store".

### Findings

No blocking issues.

[NIT] 6 — Evidence, bullet "H8, where the suite's temporary files go"
Problem: the bullet names four test functions, which an operator does not need and which the rubric keeps out of acceptance items; here it is Evidence, so it is allowed, and the names are useful to the implementer who must leave them alone.
Evidence: the bullet as written; the same four names appear under Out-of-scope observations in verification.md.
Suggested fix: none required; leave it.

### Not findings, noted so the writer does not change them
- The GIVEN fixture files go to `${TMPDIR:-/tmp}`, so a role with `TMPDIR` set to its scratch directory writes them there; only the suite scenario writes under `/tmp`, by the Decision that records it.
- The REGRESSION scenario "A plan that reuses an existing sub-ticket id" prints the same text today and after; the writer says why it still guards the change (the label must not silently become `T-0001.3`). Acceptable.

## Verifier results

3bf45779ddee6e0874ba3b1eda5170235ededfc1 · T-0023.4 · VERIFIED · run-0216-verifier
7463a1e5ad82c68d5a156ebb4d34689b890e09a1 · T-0023.3 · VERIFIED · run-0208-verifier
7463a1e5ad82c68d5a156ebb4d34689b890e09a1 · T-0023.3 · SPEC-DEFECT · run-0211-verifier
a1b271843cb2e99f2d4f845c57e0f47ec3799031 · T-0023.3 · VERIFIED · run-0213-verifier
a78de4b5a03a3c2f87e9976542035fb4a1ab0f07 · T-0023.2 · VERIFIED · run-0205-verifier
fa09a10f700a44ab7ce5881bf3daf5615ecbbb57 · T-0023.1 · VERIFIED · run-0202-verifier
