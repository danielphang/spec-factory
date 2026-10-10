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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0399-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0399-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "factory drive: an external Python driver runs the workflows and every role as a headless claude -p run; the clerk and the Workflow scripts go away (#24 part B)"
labels: "harness"
---
**Where:** a new `factory drive TICKET` command (Python, in `factory/`), replacing `factory/workflows/intake.js` and `build.js`; `agents/` (from #24 A); the README's "Starting a run" and "What depends on Claude Code".

**Problem:** every store command in a workflow goes through a clerk agent, because a Workflow-tool script cannot run a command itself. Measured on 2026-10-05 over this session's 97 workflow runs, counted once per message: the clerk was 2,236 agents and 4,476 calls, and 143M of 866M workflow context tokens (17%). It is also most of the wall-clock overhead between steps, and the source of the clerk's own failure modes (re-encoded JSON, #2). The operator deferred removing it on 2026-10-04, then chose this approach on 2026-10-05 after seeing the figures.

**Proposed change (operator's choice: the external driver, not batching inside the Workflow tool):**
- A. `factory drive TICKET [--phase intake|build]` runs the same routing as today's scripts in Python. It calls the store functions directly, with no subprocess and no clerk. The routing table, round limits, refusals and the #45 fence stay in the CLI unchanged.
- B. Each role runs as a headless Claude Code process from its run's working directory:
  `claude -p --agent factory-<role> --model <models[role]> --output-format json`
  plus a tool allowlist per role and `--permission-mode dontAsk`. Do not use `--bare`: it needs a separate API key and does not use the operator's subscription. The run's JSON reply (`result`, `session_id`, `total_cost_usd`) is recorded in the run's `meta.yaml`. That gives per-run cost without parsing transcripts (#61).
- C. The two checkers run as two concurrent processes. Independent sub-tickets run concurrently, up to a configured limit.
- D. Try `--system-prompt-file <run>/system-prompt.txt` in place of Claude Code's default prompt. Measure the start-up context before and after; keep it only if the roles still behave (#24 A's 44k-per-call figure is the baseline).
- E. Visibility in place of `/workflows`: the driver prints one line per step and writes a status file in the store, so `factory ticket show` and #17 (`factory report`) work from records alone.
- F. Keep the Workflow scripts working until the driver has run one intake and one build end to end on a real ticket. Then retire them, with the README updated.

**Open points for the spec:** whether concurrent `claude -p` runs conflict (not documented; test it). How a running driver is stopped and resumed, which ties to #53's recorded stop. Whether the driver runs in the background of a runner session or as its own process.

**Acceptance the writer can make runnable:** the same ticket fixture driven by `factory drive` and by the Workflow script reaches the same states with the same records. No clerk run appears. The per-ticket token totals are recorded beside the 2026-10-05 figures.

**Sequence:** after #24 A+C, because the driver runs roles through the registered agent definitions part A adds. The routing must not change. The workflow scripts and the dispatcher are protected (`harness` class), so this goes through the spec gate.

Source for the `claude -p` flags and billing: Claude Code's headless and CLI reference docs, read 2026-10-05.

Split from #24 part B; filed by the Green session.



## Comments (scope added since filing)

Related, future direction: #66 proposes that the Python driver's routing be compiled from a per-workflow graph file rather than hand-written, so variant workflows (#64 bounded, #62 explorers) become a graph each. Operator's ruling 2026-10-05: let this hand-written driver mature first; #66 waits until #65 has run real tickets and #64 exists as a hand-written variant.
Option to measure once the driver exists (operator question, 2026-10-07): one Claude conversation per role per ticket, resumed across rounds (`claude -p --resume <session>`, session id recorded in the run's meta.yaml). Keeps role separation (a critic's conversation never contains the writer's) and removes round-2 re-investigation, which was most of the spec writer's 16.7 min on T-0015. Costs: a role carries its own earlier misreadings forward (the fresh process was a free second opinion); context grows across rounds, bounded by max_rounds and Claude Code's auto-compaction. Apply to writer and implementer first; critic optional; never across roles or tickets. Not a default; measure writer round-2 wall time with and without.
Scope change (operator, 2026-10-07): #24 part A (an agent definition for every role, with the checkers' file tools withheld) moves here. T-0030.1 was refused twice by this session's auto-mode permission check ("Code from External": its fixtures generate and run Claude Code agent files), so it stays parked. #65 no longer waits on #24 A: the driver passes each role its prompt with `--system-prompt-file` or `--append-system-prompt-file`, and sets each role's tools with `--tools`/`--allowedTools` and a permission mode, which also gives the checkers the tool fence part A wanted. Part C (trimmed role inputs) merged as T-0030.3 and is live at runtime 5426ff2. T-0030.2 (effort per role) maps to `--effort` in the driver.
Caution on the per-role persistent conversation option (research pressure test, 2026-10-07): self-preference bias studies (Wataoka et al. 2024, arXiv 2410.21819; follow-up arXiv 2604.22891) show LLM judges score familiar, low-perplexity text higher, more so for stronger models, and a 2026 study on 250 CVE patches (arXiv 2603.18740) found that framing a change as bug-free cuts detection 16–93%, almost entirely through false negatives. A persistent **writer** or **implementer** conversation is fine: they revise their own work. A persistent **critic** or **reviewer** conversation is not: a checker that has already approved most of a text will under-find on round 2. Keep checkers fresh per round.
Absorbs #22: Per-role effort becomes claude -p --effort in the driver; T-0030.2 withdrawn. (Backlog review 2026-10-09 (operator accepted all recommendations, https://claude.ai/artifact/YFxBSP2bJwqewUUyMf7TU7).)
Absorbs #28: The chat relay goes away with the Workflow scripts. (Backlog review 2026-10-09 (operator accepted all recommendations, https://claude.ai/artifact/YFxBSP2bJwqewUUyMf7TU7).)
Absorbs #47: The Workflow scripts retire with #65; the per-step title moves to #65's status output; T-0026 withdrawn. (Backlog review 2026-10-09 (operator accepted all recommendations, https://claude.ai/artifact/YFxBSP2bJwqewUUyMf7TU7).)
Another clerk failure (2026-10-09, T-0027.2): the reviewer's `run finish` succeeded (log: run.finished APPROVE), but the clerk returned the JSON pretty-printed across lines, the workflow read it as a failure, and parked the piece as 'harness-bug: run finish reviewer:' with empty stderr. Redispatched; the reviewer runs again. The driver calling bin/factory directly removes this failure mode.


Issue: https://github.com/danielphang/spec-factory/issues/65

## Capability index: every capability in current truth

Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest.

- build-dispatch, 35 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it
- gate-commands, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start
- harness-docs, 59 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; Nothing else in the two prompts changes; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; The reading rules are the only change to the role prompts; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment
- harness-suite, 2 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock
- human-resolution, 18 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks
- live-store-guard, 13 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- store-setup, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede
