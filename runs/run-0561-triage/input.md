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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0561-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0561-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Scorecard: factory stats reports the north star's measures per window, with escapes as a store record and a cost record for every run"
---

**Problem, for the gate:** the north star's measures cannot be read from the store today. Gate decisions and resolves are counted, but nothing counts:
- target changes merged per window;
- changes that later needed a fix or a revert (escapes);
- operator interventions made outside the CLI;
- lead time from request to merge.

Cost per change is mostly missing too. For 2026-10-08 to 2026-10-14 over both stores, `factory stats` section D gives the cost source as "none" for 23 of 26 triage runs and 64 of 66 implementer runs.

**Requirements from the operator (2026-10-19):**
- **A. A scorecard.** `factory stats` gains a scorecard section that compares two windows. For each window and target it gives:
  - target changes merged: tickets closed with a merge;
  - escapes: changes that later needed a fix or a revert;
  - operator decisions and interventions per change;
  - cost and wall time per change;
  - lead time from a request's creation to its merge.

  The output is Markdown that a review pastes in as it is.
- **B. Escapes are a store record.** `factory escape add <ticket> --issue <url> [--note]` records that a merged change needed a fix. The scorecard counts these records. The issue can be in a private tracker, so a public review shows only counts and ticket ids.
- **C. Every run records its cost**, whichever path started it: the Workflow scripts or `factory drive`. The spec finds why most runs have no cost record and fixes that at the source.
- **D. Tests:** a fixture store with known runs, merges and escapes gives known scorecard figures.

**Serves:** the north star's measures. Without them no later factory ticket can say which number it moves (#116, rule B).

**Out of scope:** the existing stats sections A to D stay as they are.


Issue: https://github.com/danielphang/spec-factory/issues/117 (operator, 2026-10-19).


## Answer 1

(a), decide by instance (operator, 2026-10-19). Each instance declares whether its target is the factory itself, for example with an `instance.yaml` setting. The scorecard counts that instance's merges as factory work, on a line of their own, and every merge in any other instance as a target change. Standing: T-0055's spec states it too.

On T-0055's open question 1 the operator chose (a): until the store records operator time, the scorecard counts operator decisions and interventions per change in place of hours, and says so. This request stands as written. Interventions made outside the CLI still need a record: offer options at the gate, as triage suggested.

## Capability index: every capability in current truth

Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest.

- build-dispatch, 99 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it; The driver takes a ticket through intake on the intake script's route; The driver takes an approved ticket through the build on the build script's route; Each role run is one headless claude process with its role's prompt, model and tool limits; A role process's reply is recorded with its run; The checkers run at once, and sub-tickets run concurrently up to a limit; The driver reports each step on one line and in a status file; A stopped driver ends its role processes and resumes from the stored state; The driver marks its own store calls, never its role processes, and passes a configured effort; The Workflow scripts keep working beside the driver; A drive refuses to start on a ticket that is already being worked; A role run does not start on a ticket that already has a run in flight; Run start takes each role's model from the instance and refuses a --model that names another; A Workflow run whose relayed configuration names the wrong model parks at that role's run start; Existing callers of run start keep working; The EMPTY-OUTPUT park says when a role ended its turn waiting on a command; A Workflow run launched from its launch copy runs each role on the instance's model, whatever the clerk relays; factory launch-script writes a launch copy that differs from its script in one line, wherever factory config would run; A launch copy runs only for the instance it was written for; A store reply the clerk relays over several lines still parses
- factory-stats, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/factory-stats/spec.md`: factory stats counts runs and verdicts per role and model; factory stats groups parks by normalised reason and counts gate and merge decisions; factory stats ties each spec defect caught downstream to the runs that wrote and critiqued the spec; factory stats reports each role's cost from run records first and transcripts second; The transcript cost report counts each message once; factory stats reproduces the hand count on the two live stores
- gate-commands, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start; The gate's suite command finishes in under three minutes
- harness-code, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-code/spec.md`: The harness keeps no definition, setting or comment that nothing uses or that is no longer true; Each operation the harness repeated has one definition; Sharing an operation changes no refusal, park reason, event or parse result; The command-line code has one module per job; Splitting the command-line code changes no definition; Only the entry point, the driver and the stats report import the CLI module; The split harness passes its suite and its name checks
- harness-docs, 80 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment; The documents describe the driver; The documents record the sibling-merge exception and the start-failure ruling; The documents record the driver's exemption and its same-ticket guard; The documents record factory stats; The documents name the module that holds each moved gate command; The documents record that run start owns each role's model; The documents record the parallel suite and the waiting park reason; The maintained documents carry no whitespace errors; The build documents under dev/ are frozen as history; README's claims about what has run match the stores; README describes each mechanism in one section; README defines each term once; History lives in the changelog; README stays within its line budget; docs/standards.md holds the operator's writing and design standards; README points to docs/standards.md; No role prompt reads docs/standards.md; The north star names its target without the private product; The documents record the standards file; The documents record the template fix and init's report of a differing agent copy; The documents record the launch copy and the route back to checks; README draws how a spec changes and feeds later tickets; The clerk node says it exists only on the Workflow-script path; The diagrams of How a ticket moves are well formed; The regeneration table names the modules the spec's-life diagram is drawn from
- harness-suite, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock; Test files share code only through helper modules; Each shared test helper is written once; The refactor keeps every test and assertion but the one duplicate; A suite run writes nothing into the checkout; One harness-suite run finishes in under three minutes; Two harness-suite runs at once each finish in under five minutes; The suite's stand-in agent replies when several copies of one role start at once; This change keeps every test and assertion but the two the waiting park reason changes; The suite tests the launch copy, a reformatted reply and the route back to checks, and changes no existing test
- human-resolution, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks; A ruling returns a sub-ticket whose implementer run failed to start; A sub-ticket parked by a harness-bug after its implementer finished returns to its checks
- live-store-guard, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock; factory stats reads any store under any harness revision and writes nothing
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- store-setup, 25 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched; Every role agent template has valid frontmatter; The harness suite fails on a role agent template with broken frontmatter; init reports an agent copy that differs from its template and never overwrites it
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede

## Your previous Triage output (the question you asked is answered above)

Type: feature

Title: Scorecard: `factory stats` reports the north star's measures per window, with escapes as a store record and a cost record for every run

Summary:
The operator cannot read the north star's measures from the store, so no factory ticket can say which number it moves. The store is the factory's record of every ticket and run. The north star is the project's stated goal and measures, in `docs/north-star.md`. The operator asks for four things:
- A. A scorecard section in `factory stats`. It compares two windows, per target, and gives five numbers: target changes merged, escapes, operator decisions and interventions per change, cost and wall time per change, and lead time from request to merge. The output is Markdown that a review pastes in unchanged.
- B. A new command, `factory escape add <ticket> --issue <url> [--note]`, that records a merged change that later needed a fix or a revert. The scorecard counts these records, and shows only counts and ticket ids, because the issue may sit in a private tracker.
- C. A cost record for every role run, whether the run was started by a Workflow script or by `factory drive`. The Workflow scripts are the Claude Code Workflow files that run intake and build. `factory drive` is the driver that starts each role as its own `claude` process. The spec must find why most runs have no cost record and fix that where the record is written.
- D. Tests: a fixture store with known runs, merges and escapes produces known scorecard figures.

The existing sections A to D of `factory stats` stay as they are.

Evidence:
- The request: issue https://github.com/danielphang/spec-factory/issues/117, filed by the operator on 2026-10-19.
- I reproduced the request's cost figures exactly. I ran `bin/factory stats --store <this store> --store <Nanobot store> --since 2026-10-08 --until 2026-10-14` from the runtime checkout, with no `--transcripts`. Section D printed `triage | opus | 26 | … | record 3, transcript 0, none 23` and `implementer | opus | 66 | … | record 2, transcript 0, none 64`. So 23 of 26 triage runs and 64 of 66 implementer runs have no cost source, as the request says. The other roles show the same pattern in that window: 41 of 44 spec writer runs and 59 of 61 reviewer runs have none.
- README already states the immediate cause, at `README.md:975-981`. Only a run started by `factory drive` carries a cost record, in its `meta.yaml`. Any other run has its tokens only in Claude Code's transcript, and transcripts carry no dollars. Requirement C asks for the fix at the source. This means the Workflow-script path must write a cost record. A transcript fallback in the report is not enough.
- No scorecard or escape code exists yet. `grep -rni "escape\|scorecard" factory/*.py bin/factory`, with regex-escape calls filtered out, finds nothing.
- The store already holds the inputs for lead time and merges. Each ticket file has `created` and a `history` of state changes, and `merge.main_after` records the merge commit. For example, `tickets/T-0054.yaml` has `created: '2026-10-19T05:14:33+00:00'` and `to: closed`. Its parent has `main_after: null`, so the merge has to be read from the sub-ticket. The spec has to decide this rule.
- A related ticket, T-0055 (issue #116, the north star's metric and review), is parked waiting on the operator. Its spec draft (`runs/run-0548-spec_writer/output.md`) contains two items this ticket must follow:
  - Open question 1 is marked "Standing: yes. The scorecard ticket, T-0056, must follow the answer." That draft's option (a) matches this request's wording: count decisions and interventions per change in place of hours.
  - Its first Decision says: "A change to the factory itself is factory work and does not count as [a target change]." That decision is not approved yet.

Capabilities: factory-stats, build-dispatch, live-store-guard, harness-docs

Assumptions:
- "Target" means one factory instance: a repository the factory builds, with its own store. This repository and the Nanobot fork are the two instances today. (Inference.)
- `factory escape add` writes to the store, so the live-store guard's rules for writes apply to it. That guard refuses unmarked writes while a role run is in flight. (Inference.)
- A fix under requirement C applies to new runs only. Past runs keep "none" unless the spec finds a source for them. (Inference.)
- Requirement C may be harder than it looks on the Workflow-script path. A Workflow run is an agent inside a Claude Code session, and I did not check whether the script can read that agent's tokens and dollars. If it cannot, the spec writer should report the gap, not record an estimate. (Unverified.)
- "Operator interventions made outside the CLI" leave no CLI event by definition. The spec writer must name the record that counts them, for example operator commits to the store branch. The spec writer should offer options rather than pick one silently. (Inference.)
- Suggested priority, a suggestion only: high. T-0055's draft names this ticket as the current focus and the top of the queue.

Question for human:
How should the scorecard decide which merged tickets count as "target changes"?

The request defines target changes merged as "tickets closed with a merge", per target. T-0055's draft says a change to the factory itself is not a target change. Every ticket in this repository's store changes the factory. So under T-0055's rule, this store's scorecard row always shows 0 target changes. Under the request's words, it shows every merge.
- (a) Recommended: decide by instance. Each instance declares whether its target is the factory itself. For example, `instance.yaml` could gain a setting for this. The scorecard counts that instance's merges as factory work, on their own line, and counts every merge in any other instance as a target change. This matches T-0055's draft and needs no per-ticket field.
- (b) Every ticket closed with a merge counts as a target change in its own instance's row, as the request's words say. A review reads this repository's row as factory work. T-0055's draft decision is then reworded to match.
- (c) Decide by ticket. Triage marks each ticket as factory work or target work, and the scorecard counts only target work. This adds a ticket field and a triage step, but would handle a target ticket that also changes the harness.

Is the answer a standing decision that later tickets must follow? If yes, T-0055's spec should state it too.

A related note, needing no answer here: if the operator answers T-0055's open question 1 with (a), this request stays as written. With (b) or (c), this ticket gains a requirement to record or estimate operator time.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. I reproduced the request's cost figures exactly from the stores, and the target-change conflict appears verbatim in T-0055's draft spec.
ESCALATIONS: none
