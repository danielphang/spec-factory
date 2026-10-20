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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0551-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0551-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "Four small harness defects: drive counts Claude Code's footer as escalations, one scenario fails under macOS sh, init exits 1 on an unreadable agent copy, and --accept-harness is silently ignored by init, paths and stats"
---

**Problem, for the gate:** four small defects, each with its own issue below. Two of them hit the Nanobot target's work:
- #88 put a false escalation in run-0418's record.
- #115 made an `--accept-harness` look accepted when it was not, on 2026-10-19.

#113 would make the current-truth check (#120) report a regression the code did not cause. #114 breaks `factory init` on any target that has an unreadable agent copy. They go together because each is small, and none of them changes routing.

**Serves (rule B of #116):** escapes and operator interventions per change: each of these defects is a misleading record or a failed command that a person has to notice and work around.

## #88: factory drive: Claude Code's attribution footer after the trailer is parsed as escalations

Found by the Driver on Nanobot, 2026-10-10, at harness `4bfedc7`.

### What happened

The drive log line for run-0418-implementer (T-0035.1) reads `READY-FOR-REVIEW (+2 escalations)`, but the run escalated nothing. Its `output.md` ends with:

```
ESCALATIONS: none

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

`meta.yaml` records `escalations: ["none", "🤖 Generated with [Claude Code](...)"]`, and `run finish` logged a false `escalation.queued` event.

### Cause

There are two causes.

1. **Parser.** `factory/status.py` follows the operator's 2026-10-01 rule (b): a `none` head with further lines is a real list. So any line after the trailer becomes an escalation item, and the `none` head becomes one too.
2. **Footer.** Roles run by `factory drive` are `claude -p` processes, which carry Claude Code's default attribution behaviour. Workflow subagents did not. Of 422 Nanobot runs, only run-0418 has the footer, and it is the drive's first build run.

### Impact

No routing branches on the escalation list. Only the log and `meta.yaml` read it. The cost is a false item in the escalation record and a misleading drive log line.

### Fix (for the spec to choose)

- Turn off attribution for role processes in `drive.py`. Look up the actual Claude Code setting first; do not guess its name.
- And/or have the parser drop a known attribution footer after the trailer, with a suite case built from run-0418's tail. Rule (b) is unchanged for real item lines.


## #113: A T-0054 current-truth scenario fails under macOS /bin/sh (bash 3.2): unparenthesised case inside $( )

a current-truth scenario from T-0054 fails under macOS's `/bin/sh` whatever the code does, so a later verifier that runs current truth with that shell will report a regression the code did not cause.

**Evidence:** T-0054's verifier (run-0540, 2026-10-19). The build-dispatch scenario "Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance" holds `$(case "$C" in $T/tmp/factory-launch-*/$s.js) echo own-dir;; *) echo none;; esac)`. Under `/bin/sh` (bash 3.2.57) that prints `syntax error near unexpected token 'newline'` and `where= echo own-dir;; …`; under bash 5.3 and zsh it prints its THEN. `sh -n` does not catch it. Bash before 4 misreads an unparenthesised `case` pattern inside `$( )`.

**Proposed change:** rewrite that `case` with leading parentheses on each pattern (`(pattern)`), or as a `[ ]` test, in `openspec/specs/build-dispatch/spec.md`. Optionally, a harness-docs check that no current-truth scenario has a `case` inside `$( )` without the leading parenthesis.

**Not in scope:** any code change.


## #114: factory init exits 1 on an unreadable agent copy since #108; list it as a stale copy instead

since T-0052 (#108), `factory init` exits 1 with no JSON when a target's `.claude/agents/factory-*.md` copy exists but cannot be read. Before, it skipped such a copy and exited 0.

**Evidence:** T-0052's verifier (run-0532, 2026-10-14): `chmod 000` on one copy, then `factory init` → exit 1, `factory: PermissionError`, no JSON output. On the base, the same setup exited 0. The implementer disclosed it under Known gaps; round 2 fixed the same shape for a directory in place of a copy (it is listed instead).

**Proposed change:** treat an unreadable copy as the directory case is treated: list it under `stale_agents` with a note that it could not be read, print it on stderr, and exit 0.

**Not in scope:** overwriting any copy.


## #115: `--accept-harness` with `init`, `paths` or `stats` silently accepts nothing

**What is wrong:** `factory --accept-harness <sha> paths` (and the same flag with `init` or `stats`) accepts nothing, but it looks as if it did. The lock stays as it was, and `paths` still prints `harness_revision` as normal. The operator learns the harness was not accepted only when the next write refuses.

**Evidence:** on the Nanobot target on 2026-10-19, `--accept-harness e12ca71… paths` left `harness.lock` unchanged. Running the same flag with `ticket show` accepted it. The cause is in `factory/cli.py:853-855` at `4c61f84`: `main()` runs `init`, `paths` and `stats` before `instance.guard()`, and so never reads `a.accept_harness`. The comment at line 851 says so ("ignore --accept-harness"), but nothing tells the operator.

**Proposed change:** `main()` refuses `--accept-harness` with `init`, `paths` or `stats`, with exit 2. The message names a command that does accept it, such as `config`. A test covers each of the three commands. README's "Accepting a harness revision" says which commands accept the flag.

**Out of scope:** what the lock guard does for every other command.


**Must not change:** the escalation rule (b) for real item lines (#88), what the lock guard does for other commands (#115), and that init never overwrites an agent copy (#114).

Issues: https://github.com/danielphang/spec-factory/issues/88, /113, /114, /115.

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
