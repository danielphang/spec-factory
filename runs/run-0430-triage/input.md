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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0430-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0430-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "factory stats: catch rate and cost by role, parks by reason, gate decisions, read from the store so the retro and the operator see which checks pay (measured: reviewer changed 4 of 94 outcomes)"
---

**Problem, for the gate:** the factory records every outcome that would tell us which checks pay for themselves, and nothing reads them. Parks and their reasons, gate decisions, SPEC-DEFECT and FAILED verdicts, BLOCKED implementers, budget kills, and post-merge reverts all sit in the store log and the run records. Finding out that the code reviewer changed an outcome 4 times in 94 runs took a hand-written script over both stores. The retro reads one ticket at a time and cannot see a rate.

**Evidence (2026-10-07, both stores, every run on record; the script is the one that produced these figures and should become the command):**

| Role | Runs | Changed the outcome | What it caught |
| --- | --: | --: | --- |
| Code reviewer (Fable) | 94 | 4 | 3 REQUEST-CHANGES, 1 ESCALATE; 1 BLOCKING finding in total; budget-killed 5 times |
| Verifier (Opus) | 108 | 9 | 5 SPEC-DEFECT, 4 FAILED (3 of the 4 environment or base-commit, not code) |
| Spec critic (Fable) | 84 | 19 REVISE | 14 of 16 BLOCKING on spec-factory were rubric 6, gate readability |
| Implementer | 111 | 18 BLOCKED | Nearly all "spec, plan or dependency is wrong" |
| Human | | 82 parks | 30 NEEDS-HUMAN from triage |

The implementer is the best spec critic the factory has, because implementation is the first step where the spec meets something that can fail: code is verifiable, so the implementer is the spec's feedback loop the way tests are the code's (operator, 2026-10-07). The verifier's catches are spec defects; the reviewer on the most expensive model agreed with the author 96 times in 100. None of this was visible until counted. Background: OpenHands' production critic only beat random once it was trained on real outcomes (PR merge, code survival) rather than benchmarks; the factory has the equivalent labels and discards them. Extended reading: https://github.com/danielphang/spec-factory/discussions/69.

**Proposed change:** `factory stats [--since DATE] [--store PATH ...]`, read-only, over the store log, `runs/*/meta.yaml` and `runs/*/output.md`:

- A. **Catch rate by role**: runs, verdict distribution, outcome-changing verdicts (REQUEST-CHANGES, ESCALATE, FAILED, SPEC-DEFECT, REVISE, BLOCKED), BLOCKING finding count, budget kills, by role and by model.
- B. **Where tickets stop**: parks by normalised reason (run ids and ticket ids stripped), gate decisions (`human.resolved` approve vs request-changes), conflicts, archive refusals.
- C. **Where defects were found vs where they were introduced**: SPEC-DEFECT and implementer BLOCKED counted against the spec's writer and critic runs, so the upstream miss rate is a number.
- D. **Cost beside catch**: context tokens and wall time per role from `factory/cost.py`, next to A, so the table reads "this role costs X and changes Y outcomes".
- E. The retro's input gains the stats for the ticket's store, and `docs/design.md`'s model-per-role table cites the current A and D as the evidence it says a retro diff needs.

**Decisions:** read-only; no model; the normalisation of park reasons is a fixed list of regexes in the module, extended when a new reason appears. Post-merge reverts are out of reach until a store records them; a `ticket revert` event is a separate ticket if wanted.

**Acceptance the writer can make runnable:** `factory stats` on a fixture store with known runs prints the table above with the known counts; on the two live stores it reproduces the figures in Evidence within the differences the writer explains; the retro's `input.md` contains the stats section; the command refuses nothing and writes nothing.

**Out of scope:** acting on the numbers (the reviewer trial is a note on #64); within-run stuck detection; a trained critic.

**Risk:** none to the pipeline; the command is read-only. A wrong normalisation misleads the operator, so the regex list is in the acceptance fixture.


## Comment

Owner's notes (Green, 2026-10-07), for the spec writer:
- Part D's per-role cost must count each message id once. `factory/cost.py` double-counts streamed blocks today, about 2.05× (#61). #70 either builds on #61's fix or includes it; the figures in Evidence were counted once per message id and are not affected.
- After #65, each run's meta.yaml carries `total_cost_usd` and a session id from `claude -p`. Decide which source is canonical for cost: run records (cheap, present for every run after #65) or transcripts (the only source for runs before it). Proposed: run records when present, transcripts as fallback, and the output says which.
- Baseline caveat for #64's reviewer trial: #41 just shipped and the reviewer no longer runs the suite, so the trial measures from a cleaner baseline than the 4/94 above.

## Comment

Absorbs #61: #70 needs once-per-message counting. (Backlog review 2026-10-09 (operator accepted all recommendations, https://claude.ai/artifact/YFxBSP2bJwqewUUyMf7TU7).)

## Comment

Add to part A (2026-10-09, from the nanobot suite-run question): **pre-hand-off gate failures per implementer run**, counted from the implementer's output (a gate command that failed and was fixed before READY-FOR-REVIEW), beside verifier gate FAILs. It decides whether the implementer's full gate run before hand-off earns its cost (about one full-suite run, now 67–222 s on nanobot, mean 132 s today) against the fix round it prevents (an implementer turn plus a reviewer and a verifier at about 1M tokens each). Corrected figures for the record: today's 23 nanobot verifier runs ran the full parallel suite once each (24 lines; the second "passed in" line per run is the serial tests/cli/test_commands.py gate, mean 26 s), so there is no double run; the full suite averaged 78 s on Oct 4 and 132 s today, growing within the day as T-0031 added tests.

## Context (2026-10-11)

First after #86 in the #96 intake list. Operator decisions of 2026-10-11 that bind it: the retro (#42) is built after this ticket as a consumer of it; #94 (does a critic REVISE predict anything downstream) is a query it should make easy. The golden-set baseline (docs/golden.md, #80 part E) records per entry and role: calls, turns, tokens, suite runs, the verdict and whether it changed an outcome, operator decisions asked for.

## Capability index: every capability in current truth

Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest.

- build-dispatch, 69 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it; The driver takes a ticket through intake on the intake script's route; The driver takes an approved ticket through the build on the build script's route; Each role run is one headless claude process with its role's prompt, model and tool limits; A role process's reply is recorded with its run; The checkers run at once, and sub-tickets run concurrently up to a limit; The driver reports each step on one line and in a status file; A stopped driver ends its role processes and resumes from the stored state; The driver marks its own store calls, never its role processes, and passes a configured effort; The Workflow scripts keep working beside the driver; A drive refuses to start on a ticket that is already being worked
- gate-commands, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start
- harness-docs, 65 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; Nothing else in the two prompts changes; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; The reading rules are the only change to the role prompts; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment; The documents describe the driver; The documents record the sibling-merge exception and the start-failure ruling; The documents record the driver's exemption and its same-ticket guard
- harness-suite, 2 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock
- human-resolution, 21 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks; A ruling returns a sub-ticket whose implementer run failed to start
- live-store-guard, 13 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- store-setup, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede
