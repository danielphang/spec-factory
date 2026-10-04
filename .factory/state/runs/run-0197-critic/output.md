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

STATUS: REVISE
CONFIDENCE: high — every cited line checked matches, seven acceptance commands reproduced the spec's "today" results exactly, and the one BLOCKING item is a writing-standard gap in the operator's section, not a design gap.
ESCALATIONS:
- The acceptance scenario "The harness suite passes with an uncommitted harness edit" cannot be run by a role that obeys SCRATCH FILES: a valid run needs `TMPDIR` outside any git work tree, and each run's scratch directory is inside this repository's work tree. A human decides whether the verifier may use the system temp directory for that one scenario, or the spec takes the test fix suggested above.
