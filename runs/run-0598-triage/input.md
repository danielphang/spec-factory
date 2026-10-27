## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
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
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0598-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0598-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Benchmark: about 10 upstream fix PRs with tests, the factory against one plain session, scored on the hidden tests"
---

**Problem, for the gate:** every quality bar the factory has is its own: the critic's rubric, `docs/writing.md`, the golden set, current truth. None of them says whether the factory does better than working without it. Without an outside bar, factory work can improve how it follows its own rules and still not help.

**Requirements from the operator (2026-10-19):**
- **A. A benchmark with known answers.** About 10 merged fix PRs from the public upstream project, HKUDS/nanobot. Each PR fixes a stated issue and adds or changes tests.
  - Each task is the issue's text, run against a throwaway checkout of upstream at the PR's parent commit. Neither arm ever sees the PR's diff or its tests.
  - **Factory arm:** the factory, in a throwaway store (`FACTORY_STATE`), never a live one.
  - **Baseline arm:** one plain Claude Code session given the same text, with the operator reviewing its result the way they review a merge.
  - **Score:** the PR's own tests, applied after the run, decide pass or fail. Beside the score, each arm records operator time, operator decisions, tokens and wall time.
- **B. The method in `docs/benchmark.md`:** how tasks are chosen, how the arms are kept blind to the answer, how a task is scored, and how a result goes into a review. Results go in the review, not in this repo's docs.
- **C. The spend is approved at the gate:** about 10 factory intakes and builds, plus 10 plain sessions.

**Serves:** the north star's primary metric, correct changes per hour of operator attention, measured against a counterfactual.

**Out of scope:** the private fork. Only public upstream code and issues are used.


Issue: https://github.com/danielphang/spec-factory/issues/118 (operator, 2026-10-19). Uses #117's measures where they exist.


## Answer 1

Option 2 (Green for the operator, 2026-10-26; the operator may strike it at the gate): operator time is derived from timestamps, with no hand count. The factory arm uses the throwaway store's gate and ruling events and its session transcripts; the baseline arm uses the timestamps of the operator's messages in the session transcript. The benchmark says in its method that this measures interactions, not attention, and undercounts reading and review time. This keeps the north star's rule that nobody types a number. Standing for the benchmark only; whether the store ever records operator time is a later ticket's decision, which this one does not pre-empt.

## Capability index: every capability in current truth

Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest.

- build-dispatch, 113 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it; The driver takes a ticket through intake on the intake script's route; The driver takes an approved ticket through the build on the build script's route; Each role run is one headless claude process with its role's prompt, model and tool limits; A role process's reply is recorded with its run; The checkers run at once, and sub-tickets run concurrently up to a limit; The driver reports each step on one line and in a status file; A stopped driver ends its role processes and resumes from the stored state; The driver marks its own store calls, never its role processes, and passes a configured effort; The Workflow scripts keep working beside the driver; A drive refuses to start on a ticket that is already being worked; A role run does not start on a ticket that already has a run in flight; Run start takes each role's model from the instance and refuses a --model that names another; A Workflow run whose relayed configuration names the wrong model parks at that role's run start; Existing callers of run start keep working; The EMPTY-OUTPUT park says when a role ended its turn waiting on a command; A Workflow run launched from its launch copy runs each role on the instance's model, whatever the clerk relays; factory launch-script writes a launch copy that differs from its script in one line, wherever factory config would run; A launch copy runs only for the instance it was written for; A store reply the clerk relays over several lines still parses; Claude Code's attribution footer below the trailer is not an escalation; run finish records a run's tokens from its transcript when the run has no reply usage; A run a Workflow script starts carries its transcript's tokens; A drive run whose process gave no usable reply carries its transcript's tokens; A spec that spec add refuses as malformed goes back to the spec writer as a new round; A spec refused in the last round parks the ticket with the refusal
- factory-stats, 36 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/factory-stats/spec.md`: factory stats counts runs and verdicts per role and model; factory stats groups parks by normalised reason and counts gate and merge decisions; factory stats ties each spec defect caught downstream to the runs that wrote and critiqued the spec; factory stats reports each role's cost from run records first and transcripts second; The transcript cost report counts each message once; factory stats reproduces the hand count on the two live stores; factory stats --scorecard reports the north star's measures for each instance, for a window and the window before; factory stats without --scorecard prints sections A to D as before; factory escape add records an escape against a merged change, and the scorecard counts it; factory intervention add records an intervention made outside the CLI, and the scorecard counts it
- gate-commands, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start; The gate's suite command finishes in under three minutes
- harness-code, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-code/spec.md`: The harness keeps no definition, setting or comment that nothing uses or that is no longer true; Each operation the harness repeated has one definition; Sharing an operation changes no refusal, park reason, event or parse result; The command-line code has one module per job; Splitting the command-line code changes no definition; Only the entry point, the driver and the stats report import the CLI module; The split harness passes its suite and its name checks
- harness-docs, 102 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment; The documents describe the driver; The documents record the sibling-merge exception and the start-failure ruling; The documents record the driver's exemption and its same-ticket guard; The documents record factory stats; The documents name the module that holds each moved gate command; The documents record that run start owns each role's model; The documents record the parallel suite and the waiting park reason; The maintained documents carry no whitespace errors; The build documents under dev/ are frozen as history; README's claims about what has run match the stores; README describes each mechanism in one section; README defines each term once; History lives in the changelog; README stays within its line budget; docs/standards.md holds the operator's writing and design standards; README points to docs/standards.md; No role prompt reads docs/standards.md; The north star names its target without the private product; The documents record the standards file; The documents record the template fix and init's report of a differing agent copy; The documents record the launch copy and the route back to checks; README draws how a spec changes and feeds later tickets; The clerk node says it exists only on the Workflow-script path; The diagrams of How a ticket moves are well formed; The regeneration table names the modules the spec's-life diagram is drawn from; The documents record the footer rule, the unreadable agent copy and the --accept-harness refusal; The north star says how the factory's work is measured and reviewed; The north star holds the rule for factory work; README shows the north star on its first screen; README's filing steps state the rule for factory work; README's Where things live names the new files; CONTRIBUTING.md says how work is proposed and chosen; STATUS.md holds the north star, the baseline's figures, the focus, the queue and the experiments; The review template holds the six sections a review fills in; The baseline review is the operator's baseline, verbatim; The new pages' relative links resolve; The changelog records issue 116; The documents record the scorecard, escape and intervention records, and workflow token records; The documents record the format check at spec add and its route back to the spec writer
- harness-suite, 22 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock; Test files share code only through helper modules; Each shared test helper is written once; The refactor keeps every test and assertion but the one duplicate; A suite run writes nothing into the checkout; One harness-suite run finishes in under three minutes; Two harness-suite runs at once each finish in under five minutes; The suite's stand-in agent replies when several copies of one role start at once; This change keeps every test and assertion but the two the waiting park reason changes; The suite tests the launch copy, a reformatted reply and the route back to checks, and changes no existing test; The suite passes with this change, which changes only the stats test the --accept-harness refusal overturns; The suite passes with this change, which changes only the two test files its decisions overturn
- human-resolution, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks; A ruling returns a sub-ticket whose implementer run failed to start; A sub-ticket parked by a harness-bug after its implementer finished returns to its checks
- live-store-guard, 18 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock; factory stats reads any store under any harness revision and writes nothing; init, paths and stats refuse --accept-harness and name a command that accepts it
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 17 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived; The spec writer's run after a refused draft receives the refusal and that draft
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- spec-format-check, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-format-check/spec.md`: spec add refuses a malformed spec where current truth is enabled; approve-spec keeps its own check; spec add is unchanged where current truth is not enabled, and for a NEEDS-HUMAN draft
- store-setup, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched; Every role agent template has valid frontmatter; The harness suite fails on a role agent template with broken frontmatter; init reports an agent copy that differs from its template and never overwrites it
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede

## Your previous Triage output (the question you asked is answered above)

Type: feature

Title: Benchmark the factory against one plain Claude Code session on about 10 upstream Nanobot fix PRs, each scored by that PR's own tests

Summary:
Every quality bar the factory has today is its own: the critic's rubric, `docs/writing.md`, the golden set and current truth (the store's record of what each capability must do). None of them shows whether using the factory beats working without it. The operator wants an outside bar with known answers. The bar is about 10 merged fix PRs from the public upstream project, HKUDS/nanobot. Each PR fixes a stated issue and adds or changes tests. Each task is given as the issue's text, against a throwaway checkout of upstream at the PR's parent commit. Two arms run it, and neither ever sees the PR's diff or tests. The factory arm runs in a throwaway store (a store pointed to by `FACTORY_STATE`, never a live one). The baseline arm is one plain Claude Code session, whose result the operator reviews the way they review a merge. After the run, the PR's own tests decide pass or fail. Beside the score, each arm records operator time, operator decisions, tokens and wall time. The method goes in a new `docs/benchmark.md`, which says how tasks are chosen, how the arms are kept blind, how a task is scored and how a result goes into a review. The results go in a review, not in this repo's docs. The spend, about 10 factory intakes and builds plus 10 plain sessions, is approved at the spec gate.

Evidence:
- Request: issue #118 (https://github.com/danielphang/spec-factory/issues/118), operator, 2026-10-19. It says "Uses #117's measures where they exist". #117 is the scorecard in `factory stats`, built as T-0056.
- The benchmark is already named as an outside comparison. `docs/north-star.md:56` reads: "The upstream benchmark: merged fix pull requests from the public upstream Nanobot project, each run by the factory and by a plain session, and scored by that pull request's own tests." `STATUS.md:42` lists it third in the queue.
- No duplicate exists. The only ticket for #118 is this one, T-0060 (`dev/issues.md:121`). T-0055's spec lists the benchmark as out of scope and points to T-0060. No other open or closed ticket in `.factory/store/tickets/` has "benchmark" in it.
- There are enough candidate tasks. I listed the last 400 merged upstream PRs with "fix" in the title, back to 2026-07-14, using `gh pr list --repo HKUDS/nanobot --state merged --search "fix in:title" --limit 400`. 379 touch a file with "test" in its path. 39 of those also carry a closing-issue link, for example #6071 → issue #6070 and #6232 → issue #6231. That is enough to choose about 10.
- A throwaway store is supported today. `factory/instance.py:14` reads: "FACTORY_STATE overrides it". `README.md:616` describes a throwaway store as "`FACTORY_STATE` pointing elsewhere, as every test does".
- Operator time is not in the store. `docs/north-star.md:36-37` reads: "The store records operator decisions, not operator time. Until it records time, the scorecard counts operator decisions and interventions per change in place of hours of operator attention." Lines 40-41 read: "Until it computes a number, a review writes 'not yet computed' rather than count it by hand." The baseline review of 2026-10-19 is the one stated exception.

Capabilities: harness-docs, factory-stats, store-setup

Assumptions:
- This is my inference: the ticket's code change is `docs/benchmark.md`, plus the doc updates the repo's conventions require. Those are a row in README's "Where things live" and a `docs/changelog.md` entry. Running the 10 tasks needs the operator at both arms' gates. So the runs would be operator steps after the merge, and an implementer would not do them. The spec writer should confirm this split at the gate.
- This is my inference: "results go in the review, not in this repo's docs" means a review file under `docs/reviews/`, written from `docs/reviews/TEMPLATE.md`. It does not mean `docs/benchmark.md` or `docs/design.md`.
- This is my inference: the factory arm needs a factory instance on each throwaway upstream checkout, set up with `factory init`. That is why store-setup is named. I have not checked whether `init` works unchanged on a bare upstream checkout.
- Keeping the arms blind is in scope as the request states it. I noticed two leak paths the method will have to address. First, a full clone of upstream contains every later commit, including the PR's own. Second, both arms' sessions can reach GitHub and the local Nanobot fork, whose history holds upstream's commits. I am naming these as risks. I am not adding them as requirements.
- Choosing 39 linked candidates down to about 10 is part of the method (requirement B). I have not checked whether each candidate's tests fail at the parent commit and pass after the fix.
- Suggested priority, which is the operator's call: p1, matching its third place in the queue on `STATUS.md`.

Question for human:
How should each arm's operator time be measured? The request asks for operator time beside the score. The store does not record operator time. `docs/north-star.md` also says a review writes "not yet computed" rather than count a number by hand. The baseline arm has no store at all, so even its operator decisions would have to be counted from somewhere else. The spec writer cannot settle this without overruling the north star.
1. The operator logs it by hand. For each task and arm, the operator writes down the start and end of each stretch of attention in a benchmark log. `docs/benchmark.md` records this as a second stated exception to the "not by hand" rule, alongside the baseline review. This is the most accurate option. It costs the operator a little time on every task.
2. It is derived from timestamps, with no hand count. The factory arm uses the throwaway store's gate and ruling events plus its session transcripts. The baseline arm uses the timestamps of the operator's messages in the session transcript. This keeps the "not by hand" rule. It measures interactions rather than attention, so it can undercount reading and review time.
3. The benchmark reports operator time as "not yet computed" in both arms. The arms are compared on decisions and interventions only, as the scorecard does today, until the store records time. This changes the request as written, which names operator time.
Is the answer a standing decision, so that later tickets measuring operator time follow it too, for example a future store record of operator time?

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. The intent, the deliverable and the task supply are clear and checked. How to measure operator time is a real conflict with a written rule. Whether the runs themselves belong to this ticket is my inference.
ESCALATIONS: none
