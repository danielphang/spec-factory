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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0523-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0523-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

# Add docs/standards.md: the operator's consolidated writing and design standards, self-contained and exportable (spec-factory #110)

**What:** add the operator's consolidated writing and design standards to this repo as one self-contained document, `docs/standards.md`, that can be exported. They have lived in separate places until now: the twelve rules of `docs/writing.md`, the spec format in the spec-writer prompt, report rules from a target repo's `AGENTS.md`, and corrections the operator gave in conversation (2026-09-16 to 2026-09-29), which until now existed only in session memory.

**Why a separate document, not an edit to `docs/writing.md`:** every role prompt points to `docs/writing.md` (`factory/instance.py:174-176`, the `{writing standard}` placeholder), so editing it changes what every role writes. That is a prompt change, which waits for the golden-set baseline (#96 row 4a). No prompt names a new document, so role behaviour stays the same.

**Content:** the operator's text (operator, 2026-10-13, via the Driver session) with the details of the private target removed. This repo is public, so the document names no private repository or person. It has seven sections:
1. the reader;
2. the twelve rules with a check each, unchanged from `docs/writing.md`;
3. the operator's dated corrections, including the length budgets;
4. reports and records;
5. the spec format;
6. design-page conventions;
7. comments, issues and messages to peers.

**Also:** `docs/north-star.md:21` names the private port by its product name. Reword it to say "a port of the Nanobot chat bot".

**Order:** after T-0052 (#108) and #109.

**Requirements from the operator:**
- Add `docs/standards.md` with exactly the text in the appendix below. Its title line may change; nothing else in the text changes. It must stay self-contained, so it can be copied out of the repo and still make sense.
- Don't edit `docs/writing.md`, any `docs/prompts/` file, any role prompt, or `factory/**`.
- Point to it from README's "Where things live" table, or from another place a reader of `docs/` will find it. README has a 1,110-line budget (harness-docs current truth) and may be at the limit when this builds. If a row doesn't fit, the spec says how: replace a line, or ask the operator at the gate to raise the budget.
- Reword `docs/north-star.md:21` so it doesn't name the private port's product. For example: "its targets (today, a port of the Nanobot chat bot)".
- Add a changelog entry.

## Appendix: the text of docs/standards.md

# Writing and design standards

What this is: every standing instruction for how specs, design pages, reports and records are
written across the spec factory and the repositories it builds, collected into one file so the
standards can be recreated without the repos, the harness or any one session's memory. Who it is for:
the operator, and any agent asked to write for the operator.

Sources, in order of authority: `docs/writing.md` (the twelve rules), the factory's
spec-writer prompt (the reader and the spec format), each target repository's `.factory/context.md`
(that repo's reader), the target repository's `AGENTS.md` (report style), and the operator's own
corrections given in conversation 2026-09-16 to 2026-09-29, which until now lived only in a
session's memory notes. Where a rule's origin matters it is dated.

## 1. The reader

Deeply technical: knows databases, tables, locks, RPCs, agents and context windows. New to this
system: has not read its design document and does not know its function, command, file or state
names, or why a particular line of code exists. A reader who stops after the first paragraph can
say what is wrong and for whom.

A target repository's `.factory/context.md` can narrow the reader: for example, the operator, who
knows that codebase well but not the pipeline's vocabulary. Gloss harness terms (pinned, parked, parent-close, archive,
exit codes) on first use. File-and-function detail goes under Evidence and Root cause, never in
the Problem section.

## 2. The twelve rules (from `docs/writing.md`)

Each rule has a check you can run on your own text before handing it in.

| # | Rule | Check |
|---|---|---|
| 1 | The first paragraph says what is wrong, or what this is, and for whom. | Stop after paragraph one; can you name the problem and who has it? |
| 2 | A term specific to this system is glossed at first use with what it does or why it exists. General technical concepts are not glossed. | Underline every made-up name; its first use says what it does. |
| 3 | One idea per sentence; no parenthetical holds a second idea. | Delete each parenthetical; if a claim is lost, it needs its own sentence. |
| 4 | A diagram comes after the words needed to read it, with a caption stating its one claim. | Every box and arrow is named in the text above it. |
| 5 | A command is shown with what its output shows. | Every quoted output is followed by what it means for the claim. |
| 6 | Project-internal references are introduced, or moved to a closing note. | Each ticket id, issue number, decision id, session or person is introduced by what it is, or sits in a closing note. |
| 7 | Lead with the problem; the mechanism comes second. | First sentence: what is broken or what the reader must do. |
| 8 | State a choice and the alternative rejected; do not write an essay defending it. | One sentence for the choice, one per rejected alternative and why. |
| 9 | One name per concept: no synonyms, no name shared by two concepts. | Each term keeps the name it got at first use. |
| 10 | One mode per section: explanation, how-to and reference do not share a heading. | Label each section; a section with two labels is split. |
| 11 | A heading states what is under it. | Read only the headings; each predicts its section. |
| 12 | Parallel facts go in a table. | Three or more items with the same kinds of fact become rows, one column per kind. |

Two worked examples, kept because they are the ones most often violated:

- Rule 2, before: `--accept-harness` appeared in a diagram with no statement of what requires it.
  After: "Each target repository runs only the harness commit it has accepted, recorded in its
  `harness.lock`. When the harness is upgraded, the operator accepts the new commit with
  `--accept-harness <commit>`; until then the harness refuses to run there."
- Rule 7, before: "Stale branch base, which is a harness/process issue. The verifier was given base
  `20849b6`, but the head forks at `cdb1c67`…" After: "The test gate cannot pass on this branch: it
  was cut from `main` before the change it depends on merged. Decide: update the branch and
  re-verify, or accept the trial-merge evidence."

## 3. Operator corrections given in conversation

These are rules the operator stated directly. They apply to replies, specs, pages, commit messages,
ledgers and comments alike.

| Date | Rule | The operator's words, and why |
|---|---|---|
| 2026-09-16 | Direct and compact. Lead with the answer. Facts as short declaratives or a table. Keep the caveat, tradeoff or number that changes a decision; drop wrapping and narration. | "make your response style more direct, less mannered prose, less verbose but not dropping nuance." |
| 2026-09-17 | The same for everything written. State the fact and its source (command, SHA, file:line); reasoning goes in the commit message once; a code comment states the invariant, not the history. | "[a spec] at 561 lines is crazy work … an entire essay for PATH composition is a place we should not be." Everything written is read back many times into large contexts; a verbose doc is paid for at reads × later calls. |
| 2026-09-17 | Length budgets: a spec's normative half ≤150 lines; a profile ≤100; a cold-read record ≤60; a notes cell ≤3 sentences; a Done entry is the fixed fields, one line each. Do not rewrite closed specs for style; trim when opened for another reason. | The budgets were in an earlier maintenance-workflow document that no longer has them, so this table is now their record. |
| 2026-09-24 | Every decision id or obligation id carries a short parenthetical reminder of what it decides, on every mention. | "A bare id makes the message unreadable without the register open." |
| 2026-09-24 | Scope one unit per message: one spec, one ticket, one section. No batch-wide sweeps. | |
| 2026-09-29 | Report findings as what they mean first, mechanism second. A decision row that carries a recommendation is taken by default, recorded and reported; ask only when there is no lean or the choice is irreversible. Never re-ask after a go. | |
| ongoing | Pressure-test a proposal before presenting it: the root why, the failure modes, and an independent counter-proposal. State a concern in a sentence or two, then deliver. | |

The trap that catches a writer: copying the shape of the neighbouring record. Older entries were
written before the budgets and are long; patterning a new one on them breaks the rule even when the
rule was read the same session. Write to the rule, not to the file's median entry.

## 4. Reports and records (from the target repo's `AGENTS.md`)

- A report leads with what changed for the operator and what it cost; paths and mechanisms go
  below.
- Before any message that claims done or verified, ground it: state from commands, every quoted
  identifier read back, every figure from the command that produced it. Before saying a check
  passed, prove it ran on the claimed tree in a fresh environment.
- Ledgers and command logs are written for the cold reader: explicit why, not just what.
- No ledgers where the store is the record: the factory's store log replaces TASKS.md and Done
  entries.

## 5. The spec format (from the spec-writer prompt)

A spec is a change folder: `proposal.md`, `design.md`, `specs/<capability>/spec.md`, `tasks.md`.

| Section | Contents |
|---|---|
| Problem | What is wrong or missing, for whom, in plain words for the operator at the spec gate; each term of art glossed on first use; detail goes below. |
| Evidence | Actual output, logs, metrics, repro steps; each quoted output followed by what it means. |
| Root cause | Files and functions if known; "unknown" is allowed. |
| Out of scope | What must not change. |
| Open questions | none, or a list. |
| Decisions | none, or one line per design call, including each answered open question, with the alternative rejected. |
| Risk | Blast radius; protected paths declared on one line the merge gate reads. |
| Operator steps | Optional: actions on live or protected state only the operator can perform, after merge. |
| Proposed change (design) | Lettered parts A, B, C, specific enough to follow. |
| Tests to change | none, or the existing tests the change breaks, and why. |
| ADDED / MODIFIED / REMOVED Requirements | The delta on the capability spec, one part per capability changed; reuse a current-truth capability where the behaviour already lives. |

Anti-Goodharting: the critic scores against a rubric; satisfy each item's intent, not its wording.
A spec padded with generic criteria to look thorough is a failed spec. On revision, answer each
critic finding with FIXED and what changed.

## 6. Design pages and reports delivered as pages

Used for two earlier pages, a feature design and a cleanup report. These conventions were applied
but never written down before this file.

- **Open with what changes for the reader and what it cost.** First paragraph: the outcome in the
  reader's terms, the date, and what was not lost. A one-line meta row under it: where it was
  applied, how it was rehearsed and reviewed, how it is reverted.
- **Figures block next.** Three or four numbers that justify the page, each with a one-line label;
  a "live check" line under them quoting the command or log line that proves the headline number.
- **"One step left for you" callout** when the page asks the operator to do something: the exact
  edit, the exact command, and why the writer could not do it (for example, a safety check
  blocked the edit).
- **What changed, as numbered steps**, each with its commit id as a tag, each step revertible on
  its own.
- **What the review caught**: a short register of findings an independent critic raised before the
  change went live, each with its category and what was done.
- **Not done, and why**: deferred items with their reason, stale content left in place, and the
  decisions still open, each named by its id and a reminder of what it decides.
- **Decision register** for a design page: one row per decision, id, the question, the
  recommendation, the alternative rejected; a decision with a recommendation is taken by default.
- **How to undo**: the exact commands, the tag or backup that marks the state before, and whether
  a restart is needed.
- **A full table at the end** for anything with many rows (every skill, every job), with filters
  and a search box, and a key paragraph defining each category used in the table.
- **Privacy**: no chat contents, phone numbers, messaging-platform user ids or private people's
  names on a page, in a spec, a test, a commit or a public post. Neutral roles ("the requester",
  "a group member") where a role is needed. Nothing public references a private repository.
- Pages follow the twelve rules above; a page is not a place to escape them.

## 7. Comments, issues and messages to peers

- A comment answering a question on a page answers the question in the first sentence, then
  grounds it (file, command, log line), then says what was changed because of it, if anything.
- An issue filed from an agent's run record states: asked, did (with evidence), should have, impact,
  and an optional one-line possible fix marked as a guess. Primary evidence only; a summary stream
  is never a citation.
- A message to a peer session leads with the one fact the peer must act on, then the identifiers
  (commit, run id, ticket), then what was not done.

## Capability index: every capability in current truth

Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest.

- build-dispatch, 83 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it; The driver takes a ticket through intake on the intake script's route; The driver takes an approved ticket through the build on the build script's route; Each role run is one headless claude process with its role's prompt, model and tool limits; A role process's reply is recorded with its run; The checkers run at once, and sub-tickets run concurrently up to a limit; The driver reports each step on one line and in a status file; A stopped driver ends its role processes and resumes from the stored state; The driver marks its own store calls, never its role processes, and passes a configured effort; The Workflow scripts keep working beside the driver; A drive refuses to start on a ticket that is already being worked; A role run does not start on a ticket that already has a run in flight; Run start takes each role's model from the instance and refuses a --model that names another; A Workflow run whose relayed configuration names the wrong model parks at that role's run start; Existing callers of run start keep working; The EMPTY-OUTPUT park says when a role ended its turn waiting on a command
- factory-stats, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/factory-stats/spec.md`: factory stats counts runs and verdicts per role and model; factory stats groups parks by normalised reason and counts gate and merge decisions; factory stats ties each spec defect caught downstream to the runs that wrote and critiqued the spec; factory stats reports each role's cost from run records first and transcripts second; The transcript cost report counts each message once; factory stats reproduces the hand count on the two live stores
- gate-commands, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start; The gate's suite command finishes in under three minutes
- harness-code, 26 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-code/spec.md`: The harness keeps no definition, setting or comment that nothing uses or that is no longer true; Each operation the harness repeated has one definition; Sharing an operation changes no refusal, park reason, event or parse result; The command-line code has one module per job; Splitting the command-line code changes no definition; Only the entry point, the driver and the stats report import the CLI module; The split harness passes its suite and its name checks
- harness-docs, 69 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment; The documents describe the driver; The documents record the sibling-merge exception and the start-failure ruling; The documents record the driver's exemption and its same-ticket guard; The documents record factory stats; The documents name the module that holds each moved gate command; The documents record that run start owns each role's model; The documents record the parallel suite and the waiting park reason; The maintained documents carry no whitespace errors; The build documents under dev/ are frozen as history; README's claims about what has run match the stores; README describes each mechanism in one section; README defines each term once; History lives in the changelog; README stays within its line budget
- harness-suite, 17 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock; Test files share code only through helper modules; Each shared test helper is written once; The refactor keeps every test and assertion but the one duplicate; A suite run writes nothing into the checkout; One harness-suite run finishes in under three minutes; Two harness-suite runs at once each finish in under five minutes; The suite's stand-in agent replies when several copies of one role start at once; This change keeps every test and assertion but the two the waiting park reason changes
- human-resolution, 21 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks; A ruling returns a sub-ticket whose implementer run failed to start
- live-store-guard, 14 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock; factory stats reads any store under any harness revision and writes nothing
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- store-setup, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede
