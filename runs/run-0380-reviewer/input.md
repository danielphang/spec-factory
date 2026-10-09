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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0380-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0380-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0380-reviewer/wt` (branch `factory/T-0027.2`, base `89290547a33a6091860c850fdda7ff285b409fa0`, head `d085ca0b1cd5f084c4065c186c5467d6fd82b9ae`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0027.2

### ST-2 / The critic sees approved changes not yet archived, and its rubric asks about them (parts B and C)
Depends on: none
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B, the `## Approved changes not yet archived` section in the critic branch of `factory/compose.py`, after `add_decisions()`, with its skip rules, entry format, `none` body, omission without `openspec/changes/`, and each listed `proposal.md` added to `sources`. Part C: the four rubric lines under item 5 in the design doc's critic block (`docs/design.md`, around line 462), re-copied into `docs/prompts/03-spec-critic.md`, and the runtime copy `factory/prompts/critic.md` with `2` where the others have `{2}`. Edit only the critic block of `docs/design.md`; part E's other design-doc edits are ST-4's. Add new tests in a new file under `tests/factory/` covering B's section with and without other changes.

Acceptance (the first two after the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" has been run once; that block uses only commands that exist on `main`):
- NEW. The critic's input lists approved changes not yet archived, other than its own. THEN `listed=1 self=0 decision=1 requirement=1`, then `after_archive: heading=1 listed=0`.
- NEW. A change sent back to the spec writer leaves the critic's list. THEN `listed=1 self=0 decision=1 requirement=1`, then `respec: heading=1 listed=0`.
- NEW. A critic run's system prompt carries the cross-ticket rule. THEN `rule=1`.
- REGRESSION. The runtime critic prompt stays a copy of the documented one: WHEN `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)`. THEN `copies=same`.
- REGRESSION (intermediate). The design doc's critic block and `docs/prompts/03-spec-critic.md` both carry the new lines: WHEN `grep -c 'whichever of the two merges first' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`. THEN each file reports `1`.
- REGRESSION (intermediate). The harness suite passes, as in ST-1.
- REGRESSION (intermediate). `git diff --check main...HEAD` exits 0, as in ST-1.

Interim tests: none
Tests to change: none
Protected paths: `factory/compose.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`
Out of scope: `spec amend` (ST-1); the drift check (ST-3); the design doc's Spec store, Spec drift, line-113 and routing-row edits, the changelog, the build spec and README (ST-4).

---

## Shared plan context (from the plan; applies to every sub-ticket)

The parent spec is NEEDS-SPLIT and names its seams: A stands alone; B and C go together; D needs A; E lands with each part or last. This plan follows them. The three code parts come first, each with its own new tests. The documents (E) come last in one sub-ticket, so the changelog gets one entry written once against what was built, and the first two code sub-tickets share no file and can run side by side. Splitting further would add merges, and every merge makes in-flight siblings re-verify, without making any part easier to review or roll back.

What I checked on `~/dev/spec-factory` `main` (8929054) before planning:
- Every helper the design names exists: `factory/cli.py` `run_start` (198), `_check_sibling_tests` (242), `_add_spec_version(root, t, text, source)` (395, four arguments today), `approve_spec` (843), the `spec` subparser (1564); `factory/specstore.py` `is_active`, `lines_outside_fences`, `_heading`, `split_parts`, `parse_delta`, `validate`, `applies`, `change_dir`, `pin`, `decisions_of`, `archive`, `delta_ops_of_change`, `DELTA_RE`, `SCEN_RE`; `factory/subtickets.py` `PLAN_FIELDS`, `sibling_tests`, `planned_from`, `split_plan`; `factory/gitops.py` `rev`; `factory/compose.py` `_runs_for` and the critic branch (265) with `add_decisions()`.
- `factory/workflows/build.js:81-83` already parks an implementer run start refused with an error that starts `BLOCKED `.
- `t0022-build.mjs`, which a drift scenario reuses, is written by a GIVEN block in current truth (`.factory/store/openspec/specs/build-dispatch/spec.md:82`) and reads only `FACTORY_STATE` and `FACTORY_REPO`.
- The critic rubric item 5 line is at `docs/design.md:462`, `docs/prompts/03-spec-critic.md:21` and `factory/prompts/critic.md:21`.
- The last changelog entry is 64, followed by the closing `Declined:` line, so this change's entry is 65.

One sequencing detail the design leaves implicit: part A calls `_add_spec_version(..., cfg)`, but the `cfg` parameter belongs to part D.1. ST-1 calls `_add_spec_version` with its current four arguments. ST-3 adds `cfg` and passes it from all three callers, `spec_amend` included. Nothing the spec asks for changes.

---

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`

=== proposal.md
## Problem

When the factory builds two approved designs close together, the one that merges first can make the other's approved acceptance checks impossible to pass. The factory has no command to correct the approved design afterwards. It also has no check that catches the conflict before an agent has spent a build on it. The operator pays in blocked builds, hand-written instructions and repeated agent runs. On the Nanobot target, one ticket closed at 15.1M tokens across five build passes, mostly for this reason.

Some terms used below. The factory turns a request, called a ticket, into merged code through a chain of AI agents, called roles. The spec is the ticket's design. Its scenarios are the runnable checks the code must pass. The spec gate is the one human sign-off on a spec before code is written. At the gate the harness pins the spec: it freezes the approved version, and every later role reads that version. The store is the directory where the factory keeps tickets, spec versions and the records of agent runs. A pinned spec is also written out as the ticket's change folder in the store; a store set up without that layout has no spec store. The planner is the role that splits a ticket into sub-tickets, and it leaves its task list, `tasks.md`, in the change folder. Each sub-ticket is built by the implementer role on its own branch, checked by two checker roles, and merged on its own into the integration branch, the repository's main line. When every sub-ticket has merged and a final check passes, archive writes the change folder's scenarios into current truth. Current truth is the store's record of how the system behaves now; later specs are written against it. A run is in flight while a role is working on a ticket. A ticket is parked when the pipeline stops it and hands it to a human. An implementer that cannot go on parks its sub-ticket with the status BLOCKED. A ruling is a human's written instruction, filed with the ticket, that the harness hands to later role runs.

Three things are missing:

- **No way to amend.** Only the gate writes a spec version. A ruling can tell the builders to change a scenario's setup, so the build goes on, but archive still writes the unamended scenario into current truth, where it fails when anyone re-runs it. Nor does anything separate a correction (a scenario's setup, a precondition, a wording fix) from a change of what the ticket is for. A change of that kind, patched in under sub-tickets already merged for the old intent, would leave merged code that no longer matches its spec.
- **No check at the gate.** The critic is the role that grades a spec before the operator sees it. It is not asked whether a scenario depends on behaviour that another approved, unmerged ticket changes, and its input does not list those tickets.
- **No check at build start.** Between writing a spec and building a sub-ticket, other tickets merge. One may add a test that pins behaviour the spec changes. A sub-ticket's scenarios may also need a sibling sub-ticket that has not merged. Today the implementer or a checker finds out, after a run has been spent.

This ticket adds three things. The first is a human-only command that amends a pinned spec when the amendment keeps the spec's intent; it refuses a change of intent and says what a restart would keep and discard. The second is a drift check before a sub-ticket's first implementer run. The third is the critic's cross-ticket check, with the list of approved changes that check needs.

## Root cause

- `factory/cli.py:843` `approve_spec` is the only command that sets `spec.approved_version` and calls `specstore.pin` (`cli.py:864`). It refuses unless the ticket is `awaiting-spec-gate` (`cli.py:859`). `_add_spec_version` (`cli.py:395`) writes a version but pins nothing. The `spec` subcommands are `add` and `tasks` (`cli.py:1564`).
- `factory/compose.py:334` hands an implementer `specs/<parent>/v<approved_version>.md`; the checkers (`compose.py:349`, `:352`) and the planner (`compose.py:291`) get the same version. So moving `approved_version` reaches every later run, and nothing moves it.
- `factory/specstore.py:290` `pin` deletes and rewrites the whole change folder (`shutil.rmtree(d)`, line 296). That would drop the planner's `tasks.md`.
- `factory/specstore.py:336` `archive` applies the deltas in the change folder, so only a re-pin changes what reaches current truth.
- `factory/cli.py:198` `run_start` checks an implementer's sub-ticket only for tests a sibling added (`_check_sibling_tests`, `cli.py:213`). No record says which integration-branch commit a spec version was written against, so no check can ask what changed since.
- `factory/compose.py:265`, the critic branch, adds the spec, current truth, the decision log and rulings, and nothing about other tickets. Rubric item 5 (`docs/design.md:456`, `docs/prompts/03-spec-critic.md:21`, `factory/prompts/critic.md:21`) says only "doesn't conflict with open tickets".

## Out of scope

- How a ticket moves after an amendment. The routes that exist stay as they are: `resolve --ruling` on a BLOCKED sub-ticket, `ticket transition` back to `ready-for-parent-verify`, `resolve --replan`.
- Amending a sub-ticket's own text (`specs/<id>/subticket.md`). T-0031.4's sibling case was in that text; a ruling handles it, as today.
- A restart command. The refusal names the existing commands; the factory never discards merged work by itself.
- Catch-up runs when two tickets' sub-tickets merge alongside each other.
- Running a sub-ticket's scenarios at build start (Decisions says why).
- Re-checking merged sub-tickets against amended scenarios. The final check on the merged result does that, as today.
- Giving the spec writer the list of approved changes not yet archived. Only the critic gets it here.
- Replacing the Nanobot target's existing rulings with amendments. That is the operator's call on that target.
- The gate's `approve-spec`, `--edit` and `resolve` behaviour, and `archive`'s refusals: unchanged.
- Tests that a decision overturns within one ticket: T-0022 (issue #40) built that check, and it is live.

## Open questions

none

## Decisions

- The command is `factory spec amend <parent> --file <F> --reason "<one line>" --intent unchanged|changed`, run by a human. Rejected: the build spec's unbuilt `resolve --amend-spec`. Each `resolve` mode acts on a ticket the pipeline has stopped, and an amendment may be needed while a ticket is `planned` and not stopped.
- `--intent` is required. With `unchanged`, the harness checks the claim: the amended version must keep the Problem section, every Decisions line, and each requirement's name, operation and statement (its text before its first scenario), whitespace aside. Scenarios, setup, Evidence, design text and Tests to change may change. Any other difference is refused as a change of intent, naming each one. `--intent changed` is always refused. Rejected: issue #50's critic run on every amendment, which needs a new route from the command to the critic; the mechanical check covers the same three things. Rejected: no flag, which lets a human make an intent change without saying so. This is a standing decision.
- A refused change of intent prints a restart note. The note lists each merged sub-ticket with its merge commit, which stays on the integration branch. It lists each unmerged one with its state and branch, which a restart discards. It names both ways to restart. The first re-specs and re-plans: `factory ticket park`, `factory resolve <id> --to spec-gate`, then `factory approve-spec <id> --edit F`, after which the new plan supersedes the unmerged sub-tickets. The second closes the ticket and re-files it: `factory resolve <id> --close` and `factory ticket new`. The factory never restarts by itself. This is a standing decision.
- An amendment changes no ticket state. The operator resumes the ticket with the routes that exist. Rejected: an amendment that also moves the ticket, which would duplicate those routes.
- `spec amend` refuses while any run is in flight on the parent or one of its sub-tickets. A parked or waiting sub-ticket does not block it. Rejected: refusing while any sub-ticket is unmerged, which would block the motivating case of a sub-ticket parked BLOCKED on a scenario it cannot pass. This is a standing decision.
- Human-only means that no workflow script and no role prompt names the command. A role run on the parent or a sub-ticket is in flight while it runs, so the in-flight refusal stops it. There is no identity check, because the harness runs under one identity.
- `spec amend` refuses, with exit 2 and nothing written, in these cases: a sub-ticket; a ticket with no approved version; a ticket at `awaiting-spec-gate`, where `approve-spec --edit` is the route; a closed ticket; a reason that is not one non-blank line; and, with a spec store, a ticket whose change folder is gone because it was archived. An amended version must pass the gate's own checks: it is well-formed, and its deltas apply to current truth.
- The re-pin keeps the planner's `tasks.md` in the change folder. The rest of the folder is rewritten as the gate writes it.
- Each sub-ticket that is neither merged nor closed has its spec record moved to the new version, so later runs record the version they received. Its `planned_from`, the version its plan was made from, does not change, so an amendment never supersedes a plan.
- The record is `approvals/<parent>/amendment-<n>.md`, numbered after any amendment file already there. It holds who, when, the reason, `Intent: unchanged`, the old and new version, and one line per scenario that differs: `- changed: <name>`, `- added: <name>` or `- removed: <name>`. It also holds a `- <id> / <title>: merged` line per sub-ticket merged before the amendment, and the unified diff. The log gets a `spec.amended` event. The amendment record is that version's approval record; no gate approval file is written.
- Every spec version records the integration branch's head when it was stored, in `specs/<id>/v<n>.yaml`; that covers `spec add`, a gate edit and `spec amend`. Drift is counted from the record of the parent's approved version. Rejected: counting from the pin, because T-0032.1's test arrived between writing and pinning. A version stored before this change has no record, so its sub-tickets get only the sibling rule.
- The drift check runs at `run start` of a sub-ticket's implementer, before the sibling-tests check. It runs only while the sub-ticket has no implementer run and no ruling on file. On drift it refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build already parks any `BLOCKED ` refusal with it as the reason. The human then amends the spec, rules, or both, and `resolve --ruling` returns the sub-ticket; the ruling also stops the check from repeating. Rejected: a new SPEC-DRIFT park status, as issue #50 proposed, which needs a new `resolve` route.
- Sibling rule: drift when the sub-ticket's Acceptance field names, by id or by plan label, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. This is a standing decision.
- Test rule: drift for each test file changed on the integration branch since the version's recorded head, by a first-parent commit that also changed a file the spec's design part names, and that neither the spec's Tests to change nor the sub-ticket's Tests to change lists. A test file's name starts with `test_`, or ends `_test.<ext>`, or contains `.test.`. Named files are the design part's backticked paths that exist at the integration head, except test files and `.md` documents, which every ticket here edits. This approximates "pins behaviour the spec changes": measured above, it catches 9 of 10 known incidents and would park about half the sub-tickets. Rejected: running each NEW scenario at build start and comparing it with the spec's "fails today" output (issue #50, part D). That output is prose, not something a program can compare. Rejected: a judge run per sub-ticket, which needs a new role and route.
- The critic's input gains a section, `## Approved changes not yet archived`. It lists each change folder whose ticket is neither closed nor back in the spec loop (`ready-for-spec-writer`, `ready-for-critic`, `awaiting-spec-gate`), other than the reviewed ticket's own. Each entry gives the ticket id, title, state, folder path, the requirements its deltas add, modify or remove, and its Decisions lines. The section reads `none` when the list is empty, and is left out when the store has no spec store. Rejected: whole proposals, which would multiply the critic's input.
- The cross-ticket rule extends the critic's rubric item 5 (Consistent). A scenario whose setup would not hold under one of the two merge orders is a BLOCKING finding that names the other ticket and its decision. This is a standing decision.

## Risk

Blast radius:
- One new human command, which touches only the ticket it names and its sub-tickets' spec records.
- Every `spec add` and gate edit writes one more small file, `specs/<id>/v<n>.yaml`.
- Every sub-ticket's first implementer run start gains the drift check. This is the main cost. Measured on history, the test rule would park 17 of 36 sub-tickets here and 29 of 43 on Nanobot, each for one human ruling or amendment, and catch 9 of the 10 known breaks before an implementer run. A park the operator judges harmless costs one ruling, which the implementer then receives.
- Every critic run on a store with a spec store gets one more input section, with one entry per approved change not yet archived. Today that is one entry here, T-0031.
- The critic prompt gains four lines in rubric item 5. No routing, state, gate or archive behaviour changes.

Overlap with other open tickets, checked under this ticket's own new rule:
- T-0031 here (role commands drop an inherited virtual environment; build checkouts run an optional `environment_sync` command) is approved, `planned`, and not yet archived. It also edits `run_start` in `factory/cli.py`, so text conflicts are likely, and a catch-up run resolves them. Its decision sets `environment_sync` on neither instance. The scenarios here start implementers with this checkout's instance configuration and never use the running-code wrapper, so they hold whichever ticket merges first.
- T-0039 (reading rules for five more roles) is at the spec gate, not approved. It edits other prompt blocks of `docs/design.md`, not the critic's.
- The documents checks below find this ticket's changelog entry by its content, not as the last entry, so they hold whichever ticket merges first.

Protected paths: `factory/cli.py`, `factory/specstore.py`, `factory/compose.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`

`factory/gitops.py` is declared for a git helper the drift check may add; the prototype did without one. The change also edits `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`, which are not protected, and adds new test files under `tests/factory/`.

## Operator steps

none
=== design.md
## Proposed change

NEEDS-SPLIT. The prototype's harness code is about 275 changed lines before tests and documents. With them the change is about 550 lines, over one reviewable PR. The seams are the lettered parts. A stands alone. B and C go together and stand alone. D needs A for the scenario where an amendment clears drift. E lands with each part, or last.

**A. `factory spec amend` (`factory/cli.py`, `factory/specstore.py`).** Add `amend` under the `spec` subparser: positional `id`, `--file` (required), `--reason` (required), `--intent` (required, `unchanged` or `changed`). Add `spec_amend(a, root, cfg)`. It runs these checks in this order. Each refusal raises `Refused`, so it exits 2 with `{"ok": false, "error": ...}` and nothing written.

1. The ticket has a `parent`: refuse, naming the parent.
2. `spec.approved_version` is None, or the status is `awaiting-spec-gate` or `closed`: refuse. At the gate, point to `approve-spec --edit`.
3. `--reason`, stripped, is empty or more than one line: refuse.
4. Any run id is in the `in_flight` list of the ticket or of any sub-ticket (`store.subtickets_of`): refuse, naming each run id.
5. `--intent changed`: refuse with `intent changed: ...` and the restart note.
6. `specstore.intent_changes(old, new)` is not empty: refuse with `intent changed (<each change>; ...)`, saying what `--intent unchanged` keeps, and the restart note.
7. With `specstore.is_active(root)`: the change folder `specstore.change_dir(root, id)` must exist (if it is gone, the ticket was archived). Then run `specstore.validate(text)` and `specstore.applies(root, deltas)` exactly as `approve_spec` runs them, and refuse with `spec not amended: <errors>`. The validator's own error texts, such as `has no NEW/REGRESSION label`, pass through.

The restart note is one paragraph that starts `Restart instead of amending.`. It lists the merged sub-tickets as `<id> / <title> (merge <main_after, 9 chars>)` and the rest that are not closed as `<id> / <title>: <status>[, branch <branch>]`, `none` for an empty list. It ends with the two restart paths in Decisions, naming the ticket id in each command.

Then write, in this order:
- Read the old pinned text, `specs/<id>/v<approved_version>.md`.
- Call `_add_spec_version(root, t, text, f"amend {file}", cfg)`.
- With a spec store: read `tasks.md` from the change folder if it exists, call `specstore.pin(root, id, text)`, then write `tasks.md` back.
- Set `spec.approved_version = n` and save.
- For each sub-ticket that is neither `merged` nor `closed`, set its `spec` to `{"version": n, "approved_version": n}` and save. Leave `planned_from` alone.
- Write `approvals/<id>/amendment-<k>.md`, with `k` from `_next_n(d, "amendment")`, so a hand-written `amendment-1.md` is counted. Content: a heading naming the ticket and `v<old> to v<n>`; `By <user> at <ts>.`; `Reason: <reason>`; `Intent: unchanged`; `## Scenarios changed`, one line per scenario as in Decisions, or `none`; `## Sub-tickets merged before this amendment`, one `- <id> / <title>: merged` line each, or `none`; `## Diff`, a fenced `difflib.unified_diff` of the old and new texts.
- Log `spec.amended` with `ticket`, `by`, `previous`, `version`, `reason` and `record`.
- Print `{"ok": true, "id", "version", "record"}`.

New helpers in `factory/specstore.py`:
- `scenario_blocks(text) -> dict[name, block]`: over every delta part (`split_parts`, `DELTA_RE`), each `#### Scenario:` block, from its heading line through the line before the next `##`, `###` or `####` heading, outside fences (`lines_outside_fences`, `SCEN_RE`, `_heading`). A scenario is changed when its name is in both versions and its block differs.
- `intent_of(text)` and `intent_changes(old, new) -> list[str]`. The intent is three things: the `## Problem` body of `proposal.md`; the `decisions_of` lines; and per delta part, per op, per requirement (`parse_delta`), the requirement block up to its first `#### Scenario:` line outside fences. Each is compared with whitespace runs collapsed. The result names `the Problem section`, `Decisions line removed: ...`, `Decisions line added: ...`, `requirement removed: <cap> <OP> <name>`, `requirement added: ...` and `requirement restated: ...`.

**B. The critic's input (`factory/compose.py`, critic branch, after `add_decisions()`).** When `<store>/openspec/changes/` exists, append a section headed exactly `## Approved changes not yet archived`. Go through the directories under it in name order. Skip `archive`, the reviewed ticket's own id, any id with no ticket record, and any id whose ticket is `closed`, `ready-for-spec-writer`, `ready-for-critic` or `awaiting-spec-gate`. Write one entry per remaining directory:

```
### <id>: <title> (<status>)
Change folder: `<absolute path>`
Changes: <capability>: <ADDED|MODIFIED|REMOVED> <requirement name>; ...
Decisions:
- <each line from specstore.decisions_of(proposal.md)>
```

Use `specstore.delta_ops_of_change` for the changes, and write `none` for an empty list. Add each listed `proposal.md` to the run's `sources`. With no entries, the section body is `none`. With no `openspec/changes/`, the section is left out.

**C. The critic rule (design doc block, `docs/prompts/03-spec-critic.md`, `factory/prompts/critic.md`).** Under rubric item 5, after its first line, add these four lines in all three copies. Keep each copy's existing differences: the runtime copy has `2` where the others have `{2}`.

```
   For each scenario, check whether it depends on behaviour that an
   approved change not yet archived (listed in your input) changes. If
   so, its setup must hold whichever of the two merges first; if it
   would not, that is BLOCKING: name that ticket and its decision.
```

**D. The drift check (`factory/cli.py`, `factory/subtickets.py`).**
1. Record. `_add_spec_version` takes `cfg` and, after writing the version, writes `specs/<id>/v<n>.yaml` with `integration_head`: `gitops.rev` of the integration branch in the target repo, or null when the repo or branch does not resolve. All three callers pass `cfg`: `spec_add`, `approve_spec --edit` and `spec_amend`.
2. Field text. Add `subtickets.field_text(text, name)`, the lines of one plan field, found the same way `sibling_tests` finds "Tests to change": from the field's own line to the next field in `PLAN_FIELDS`, or the next heading.
3. Check. In `run_start`, for the implementer on a sub-ticket, call `_check_drift(root, cfg, t)` before `_check_sibling_tests`. Return at once when the sub-ticket has a finished implementer run (`compose._runs_for`) or any `approvals/<id>/ruling-*` file. Otherwise collect findings:
   - Sibling rule. Take the current plan's sub-tickets (`subtickets.split_plan(store.subtickets_of(...))[0]`). Take the sub-ticket's dependency closure over their `depends_on`. For each other current sibling that is not `merged` and not in the closure, a finding when its id or `label` appears as a whole token in the Acceptance field text. A whole token is not preceded by a word character, `.` or `-`, and not followed by a word character, `-` or `.<digit>`. The finding reads `its Acceptance names <id> (<status>), which has not merged and is not one of its dependencies`.
   - Test rule. `base` is the `integration_head` recorded for the parent's approved version. Skip this rule when it is null or not a commit in the target repo. `tip` is the integration branch's head. Named files are the backticked tokens of the pinned spec's `design.md` part that exist as files at `tip`, are not test files, and do not end `.md`. Listed files are the backticked tokens, cut at `::`, of the design part's `## Tests to change` section and of the sub-ticket's "Tests to change" field. For each commit in `git rev-list --first-parent --reverse base..tip` whose `git diff --name-only --no-renames <c>^1 <c>` includes a named file, each test file it changes that is not listed is a finding, keeping the last such commit. A test file matches `(^|/)test_[^/]*$`, `_test\.[A-Za-z0-9]+$` or `\.test\.[A-Za-z0-9]+$`. The finding reads `<file> changed by <commit, 9 chars> since spec v<n> was written at <base, 9 chars>`.
   - With any finding, raise `Refused("BLOCKED from harness: spec drift: <findings joined by '; '>. Amend the spec (`spec amend <parent>`) or rule (`resolve <id> --ruling F`)")`. This happens before a run id is reserved, so nothing is written.
4. No workflow change. `factory/workflows/build.js:81-83` already parks any implementer run start refused with an error starting `BLOCKED `, with the error as the reason. `resolve --ruling` already accepts that park (`cli.py`, `resolve`).

**E. Documents.**
- `docs/design.md`:
  1. The rubric block in C.
  2. A paragraph `**Spec drift.**` after the `**Tests a sibling added.**` paragraph. It gives the record, when the check runs, both rules, the refusal and how the human resolves it.
  3. In the Spec store paragraph, after the sentence ending "work from the delta the human approved", say that after the gate only `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged` changes the pinned version. Say who runs it and when, what `--intent unchanged` keeps, that a change of intent is refused with a restart note, and that the re-pin keeps `tasks.md` and is recorded under `approvals/`.
  4. In line 113, after "amend the sub-ticket or the pinned spec", add "(`factory spec amend`, intent unchanged)".
  5. In the routing-table row `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic |`, add "every other approved change not yet archived, with its decisions" to Receives.
- `docs/changelog.md`: one new numbered entry, continuing the numbering. It names `factory spec amend` and `--intent`, says it refuses while a run is in flight and keeps `tasks.md`, describes the spec drift check, says the critic receives approved changes not yet archived, and gives the rule that a scenario's setup must hold whichever ticket merges first. If the parts land as separate sub-tickets, the first adds the entry and each later one extends it.
- `dev/build-harness.spec.md`: in the `factory resolve` bullet (line 315), mark `--amend-spec` as built instead as `factory spec amend PARENT --file F --reason LINE --intent unchanged` (doc §Spec store), and say `resolve` has no `--amend-spec`. In the Spec store paragraph (line 193), add that `run compose` gives the critic the approved changes not yet archived, and that a sub-ticket's first implementer `run start` checks spec drift (doc §Harness, Spec drift).
- `README.md`:
  - In "Where a human decides", add an **Amend** row to the table: `factory spec amend T-n --file F --reason "<line>" --intent unchanged`. Its "What you decide" cell names the three triggers: another ticket merged first, a checker found a scenario that cannot pass as written, or you changed your mind. It gives the rule: amend only when the Problem, the Decisions and every requirement's statement stay as approved; otherwise restart, by re-spec and re-plan or by close and re-file. `--intent changed` prints what a restart keeps and discards.
  - In the Unstick row's `--ruling F` list, add "the harness parked a sub-ticket for spec drift".
  - In "What is built and what is not", under Built, add a bullet `**Spec amendment and drift.**` that says what the command and the check do and ends "It is tested, and has not yet fired on a real ticket."
  - Bump the status date.

New tests, in new files under `tests/factory/`, driving `bin/factory` on a throwaway `FACTORY_STATE` and a scratch target, as `tests/factory/test_sibling_tests.py` does. Cover A's writes, each refusal and the intent check; B's section with and without other changes; and D's two rules, the ruling skip and the amendment that clears drift.

## Tests to change

none. The prototype ran the full suite (`408 passed`, the same count as on `main`), with the critic block edited in all three copies. The current-truth scenarios of the sibling-tests check printed the same lines on the prototype as on `main`.
=== specs/spec-amendment/spec.md
## ADDED Requirements

### Requirement: A human amends a pinned spec whose intent is unchanged
`factory spec amend PARENT --file F --reason LINE --intent unchanged`, on a ticket with an approved spec, before archive, with no run in flight on it or its sub-tickets, MUST write F as the next spec version and make it the approved one, re-pin the change folder from F while keeping its `tasks.md`, and SHALL leave merged sub-tickets merged.

#### Scenario: An intent-unchanged amendment re-pins the change and keeps the plan's tasks
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0027-amend.sh <<'EOF'
# Sourced from the repo root: a scratch store with a spec store, and a target repo whose main holds
# src/greet.py and src/other.py. T-0001's spec v1 was added with main at that commit, then approved.
# Its design names `src/greet.py`; its one requirement, "Greets", has one scenario, "Greeting is
# printed", running `echo hi`. $T27/v2.md differs from v1 only in that scenario (`echo hello`);
# $T27/v3.md also changes the Decisions line. T-0001 has no sub-tickets yet. Defines `plan TEXT`
# (adds the plan TEXT and moves T-0001 to planned) and `land FILE...` (one commit on main that
# writes each FILE).
T27=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T27/store FACTORY_REPO=$T27/t FACTORY_INTEGRATION_BRANCH=main
land() { for f in "$@"; do mkdir -p $T27/t/$(dirname $f) && echo "# $f" >> $T27/t/$f; done; git -C $T27/t add -A && git -C $T27/t -c user.email=f@x -c user.name=f commit -qm "land $*"; }
git init -q -b main $T27/t && land src/greet.py src/other.py
bin/factory init >/dev/null 2>&1
spec() { printf '=== proposal.md\n## Problem\nx\n## Decisions\n- %s\n=== design.md\n## Proposed change\nEdit `src/greet.py`.\n## Tests to change\nnone\n=== specs/demo/spec.md\n## ADDED Requirements\n### Requirement: Greets\nThe tool SHALL greet.\n\n#### Scenario: Greeting is printed\n- WHEN `%s`\n- THEN it prints `%s`\n=== verification.md\n## Acceptance\n- Greeting is printed → NEW\n' "$1" "$2" "$3"; }
spec 'Greet by default.' 'echo hi' 'hi' > $T27/v1.md && spec 'Greet by default.' 'echo hello' 'hello' > $T27/v2.md && spec 'Greet only when asked.' 'echo hello' 'hello' > $T27/v3.md
printf '# Fixture\n\nGreet.\n' > $T27/req.md
bin/factory ticket new --file $T27/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T27/v1.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
plan() { printf "$1" > $T27/plan.md && bin/factory subticket add T-0001 --file $T27/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; }
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' && bin/factory ticket set T-0001.1 status=merged >/dev/null && printf 'planner tasks\n' > $FACTORY_STATE/openspec/changes/T-0001/tasks.md; bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') pinned=$(grep -c 'echo hello' $FACTORY_STATE/openspec/changes/T-0001/specs/demo/spec.md) tasks=$(grep -c 'planner tasks' $FACTORY_STATE/openspec/changes/T-0001/tasks.md) first=$(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=0 "approved_version": 2 pinned=1 tasks=1 first=merged`

### Requirement: Later runs receive the amended spec, and the record names what changed
After an amendment, a role run that reads the pinned spec SHALL receive the amended version, and the amendment record MUST list each changed scenario and each sub-ticket merged before it, with the reason, and the log MUST record a `spec.amended` event.

#### Scenario: A later implementer run receives the amended spec, and the record lists what changed
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' && bin/factory ticket set T-0001.1 status=merged >/dev/null; bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; A=$FACTORY_STATE/approvals/T-0001/amendment-1.md; echo "changed=$(cat $A 2>/dev/null | grep -cxF -- '- changed: Greeting is printed') merged=$(cat $A 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged') reason=$(cat $A 2>/dev/null | grep -c 'Seed the greeting.') logged=$(bin/factory log tail --event spec.amended | grep -c '"ticket": "T-0001"')"; R=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "amended=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'echo hello') old=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -cw 'echo hi') run_version=$(sed -n 's/^spec_version: //p' $FACTORY_STATE/runs/${R:-none}/meta.yaml 2>/dev/null)")`
- THEN it prints exactly `changed=1 merged=1 reason=1 logged=1`, then `amended=1 old=0 run_version=2`

### Requirement: Archive writes the amended version into current truth
`factory archive` after an amendment SHALL write the amended version's scenarios into current truth, not the version first approved.

#### Scenario: Archive after an amendment writes the amended scenario
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; bin/factory archive T-0001 >/dev/null 2>&1; echo "archive=$? hello=$(grep -c 'echo hello' $FACTORY_STATE/openspec/specs/demo/spec.md) hi=$(grep -cw 'echo hi' $FACTORY_STATE/openspec/specs/demo/spec.md)")`
- THEN it prints exactly `archive=0 hello=1 hi=0`

### Requirement: An amendment that changes intent is refused with a restart note
`factory spec amend` MUST refuse with `"ok": false` and exit 2, writing nothing, when `--intent changed` is given or when the amended version changes the Problem, a Decisions line, or a requirement's name, operation or statement, and the refusal SHALL name each such change and say which sub-tickets have merged, which a restart would discard, and the commands to re-spec or to close and re-file.

#### Scenario: An amendment declared or found to change intent is refused, naming what a restart keeps and discards
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' && bin/factory ticket set T-0001.1 status=merged >/dev/null; for x in "v2.md changed" "v3.md unchanged"; do set -- $x; E=$(bin/factory spec amend T-0001 --file $T27/$1 --reason "r" --intent $2 2>/dev/null | tail -1); echo "intent=$2 exit_json=$(echo "$E" | grep -c '"ok": false') restart=$(echo "$E" | grep -c 'Restart instead') decision=$(echo "$E" | grep -c 'Decisions line') merged=$(echo "$E" | grep -c 'T-0001.1 / First') pending=$(echo "$E" | grep -c 'T-0001.2 / Second: ready-for-implementer') paths=$(echo "$E" | grep -c 'resolve T-0001 --to spec-gate.*resolve T-0001 --close')"; done; echo "$(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') versions=$(ls $FACTORY_STATE/specs/T-0001 | grep -c '\.md$') records=$(ls $FACTORY_STATE/approvals/T-0001 | grep -c '^amendment-')")`
- THEN it prints exactly `intent=changed exit_json=1 restart=1 decision=0 merged=1 pending=1 paths=1`, then `intent=unchanged exit_json=1 restart=1 decision=1 merged=1 pending=1 paths=1`, then `"approved_version": 1 versions=1 records=0`

### Requirement: An amendment that cannot be applied is refused and writes nothing
`factory spec amend` MUST refuse with `"ok": false` and exit 2, writing no version, record or pin, when the ticket was archived, when it is a sub-ticket, when the reason is not one line, when the version fails the gate's checks, or while a run is in flight on the ticket or one of its sub-tickets, and the in-flight refusal SHALL name the run.

#### Scenario: An amendment after archive is refused
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; bin/factory archive T-0001 >/dev/null 2>&1; echo "late=$(bin/factory spec amend T-0001 --file $T27/v1.md --reason "Too late." --intent unchanged 2>/dev/null | tail -1 | grep -c '"ok": false') changes=$(ls $FACTORY_STATE/openspec/changes | tr '\n' ' ')hello=$(grep -c 'echo hello' $FACTORY_STATE/openspec/specs/demo/spec.md)")`
- THEN it prints exactly `late=1 changes=archive hello=1`

#### Scenario: A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && grep -v '→ NEW' $T27/v2.md > $T27/bad.md; m=$(bin/factory spec amend T-0001 --file $T27/bad.md --reason "r" --intent unchanged 2>/dev/null | tail -1 | grep -c 'no NEW/REGRESSION label'); s=$(bin/factory spec amend T-0001.1 --file $T27/v2.md --reason "r" --intent unchanged 2>/dev/null | tail -1 | grep -c '"ok": false'); r=$(bin/factory spec amend T-0001 --file $T27/v2.md --reason "$(printf 'two\nlines')" --intent unchanged 2>/dev/null | tail -1 | grep -c '"ok": false'); echo "malformed=$m subticket=$s reason=$r $(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') v2=$(ls $FACTORY_STATE/specs/T-0001 | grep -c '^v2.md$') records=$(ls $FACTORY_STATE/approvals/T-0001 | grep -c '^amendment-')")`
- THEN it prints exactly `malformed=1 subticket=1 reason=1 "approved_version": 1 v2=0 records=0`

#### Scenario: An amendment is refused while a sub-ticket's run is in flight, naming the run
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; e=$(bin/factory spec amend T-0001 --file $T27/v2.md --reason "r" --intent unchanged 2>&1 >/dev/null); echo "exit=$? names_run=$(echo "$e" | grep -c 'run-0001-implementer') $(bin/factory ticket show T-0001 --json | tail -1 | grep -o '"approved_version": [0-9]*') v2=$(ls $FACTORY_STATE/specs/T-0001 | grep -c '^v2.md$') pinned_old=$(grep -cw 'echo hi' $FACTORY_STATE/openspec/changes/T-0001/specs/demo/spec.md) records=$(ls $FACTORY_STATE/approvals/T-0001 | grep -c '^amendment-')")`
- THEN it prints exactly `exit=2 names_run=1 "approved_version": 1 v2=0 pinned_old=1 records=0`
=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: A sub-ticket whose spec drifted parks before its first implementer run
`factory run start --role implementer` on a sub-ticket with no implementer run and no ruling on file MUST refuse with exit 2, writing no run, with an error that starts `BLOCKED from harness: spec drift: `, when its Acceptance field names a sibling of the current plan that has not merged and is not among its dependencies, or when a test file changed on the integration branch since the parent's approved version was written, in a commit that changed a file that version's design names, and no Tests to change list names it; the build SHALL park it with that error, and a ruling SHALL let the next run start.

#### Scenario: A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\nAcceptance:\n- REGRESSION: ST-1 scenarios still pass\n' && J=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1); echo "unmerged: blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: spec drift: ') names=$(echo "$J" | grep -c 'T-0001.1') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"; bin/factory ticket set T-0001.1 status=merged >/dev/null; bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "merged: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `unmerged: blocked=1 names=1 runs=0 ready-for-implementer`, then `merged: exit=0 runs=1`

#### Scenario: A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start
Needs the GIVEN blocks of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" and of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" (current truth, build-dispatch) run once. In `t0022-build.mjs` every role run returns an empty string.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && land src/other.py tests/test_other.py && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(spec drift:\).*/\1/'; R=$(bin/factory ticket show T-0001.1 --json | tail -1); echo "greet=$(echo "$R" | grep -c 'tests/test_greet.py') other=$(echo "$R" | grep -c 'tests/test_other.py') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"; printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "ruled: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `park T-0001.1: BLOCKED from harness: spec drift:`, then `greet=1 other=0 runs=0`, then `ruled: exit=0 runs=1`

### Requirement: Changes that leave a sub-ticket's spec intact do not park it
A sub-ticket's first implementer run SHALL start when the commits since its parent's approved version was written change no file that version's design names, when every test they change is listed under Tests to change, or when an amendment was written after them.

#### Scenario: Unrelated changes, a listed test and an amendment written after the change let the implementer start
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(for c in other listed amended; do (. ${TMPDIR:-/tmp}/t0027-amend.sh && T='\nTests to change: none\n'; [ $c = listed ] && T='\nTests to change:\n- \140tests/test_greet.py\140: pins the old greeting\n'; plan "ST-1 / First\nDepends on: none\nParallel-safe: yes$T" && if [ $c = other ]; then land src/other.py tests/test_other.py; else land src/greet.py tests/test_greet.py; fi && if [ $c = amended ]; then bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; fi; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "$c: exit=$? runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"); done)`
- THEN it prints exactly `other: exit=0 runs=1`, then `listed: exit=0 runs=1`, then `amended: exit=0 runs=1`
=== specs/role-inputs/spec.md
## ADDED Requirements

### Requirement: The critic sees approved changes not yet archived
A critic run's composed input on a store with a spec store MUST contain a section `## Approved changes not yet archived` that lists every other ticket's change folder whose ticket is neither closed nor back in the spec loop, each with its decisions and the requirements its deltas change, and SHALL drop a change once it is archived or sent back to the spec writer.

#### Scenario: The critic's input lists approved changes not yet archived, other than its own
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && spec 'Wave at night.' 'echo wave' 'wave' > $T27/w.md && printf '# Second\n\nWave.\n' > $T27/req2.md && bin/factory ticket new --file $T27/req2.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-spec-writer --by t >/dev/null && bin/factory spec add T-0002 --file $T27/w.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-critic --by t --round spec:init >/dev/null; R=$(bin/factory run start --role critic --ticket T-0002 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); sec() { bin/factory run compose ${R:-none} >/dev/null 2>&1; awk '/^## Approved changes not yet archived$/{on=1; print; next} /^## /{on=0} on' $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null; }; X=$(sec); echo "listed=$(echo "$X" | grep -c '^### T-0001: ') self=$(echo "$X" | grep -c '^### T-0002') decision=$(echo "$X" | grep -cxF -- '- Greet by default.') requirement=$(echo "$X" | grep -c 'Greets')"; bin/factory archive T-0001 >/dev/null 2>&1; X=$(sec); echo "after_archive: heading=$(echo "$X" | grep -c '^## Approved changes not yet archived$') listed=$(echo "$X" | grep -c '^### T-0001: ')")`
- THEN it prints exactly `listed=1 self=0 decision=1 requirement=1`, then `after_archive: heading=1 listed=0`

#### Scenario: A change sent back to the spec writer leaves the critic's list
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && spec 'Wave at night.' 'echo wave' 'wave' > $T27/w.md && printf '# Second\n\nWave.\n' > $T27/req2.md && bin/factory ticket new --file $T27/req2.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-spec-writer --by t >/dev/null && bin/factory spec add T-0002 --file $T27/w.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-critic --by t --round spec:init >/dev/null; R=$(bin/factory run start --role critic --ticket T-0002 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); sec() { bin/factory run compose ${R:-none} >/dev/null 2>&1; awk '/^## Approved changes not yet archived$/{on=1; print; next} /^## /{on=0} on' $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null; }; X=$(sec); echo "listed=$(echo "$X" | grep -c '^### T-0001: ') self=$(echo "$X" | grep -c '^### T-0002') decision=$(echo "$X" | grep -cxF -- '- Greet by default.') requirement=$(echo "$X" | grep -c 'Greets')"; bin/factory ticket park T-0001 --reason x >/dev/null && bin/factory resolve T-0001 --to spec-gate >/dev/null && printf 'redo\n' > $T27/n.md && bin/factory request-changes T-0001 --notes $T27/n.md >/dev/null; X=$(sec); echo "respec: heading=$(echo "$X" | grep -c '^## Approved changes not yet archived$') listed=$(echo "$X" | grep -c '^### T-0001: ')")`
- THEN it prints exactly `listed=1 self=0 decision=1 requirement=1`, then `respec: heading=1 listed=0`
=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The critic's rubric asks about cross-ticket dependencies
The critic's system prompt MUST tell it to check each scenario against approved changes not yet archived and to require the scenario's setup to hold whichever of the two merges first, and the runtime critic prompt SHALL stay a copy of `docs/prompts/03-spec-critic.md` with its round placeholder filled.

#### Scenario: A critic run's system prompt carries the cross-ticket rule
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; R=$(bin/factory run start --role critic --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); echo "rule=$(grep -c 'whichever of the two merges first' $FACTORY_STATE/runs/${R:-none}/system-prompt.txt 2>/dev/null)")`
- THEN it prints exactly `rule=1`

#### Scenario: The runtime critic prompt stays a copy of the documented one
- WHEN `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)`
- THEN it prints exactly `copies=same`

### Requirement: The documents record spec amendment, spec drift and the cross-ticket check
`docs/changelog.md` SHALL gain one entry, numbered without a gap, covering the amend command with its intent flag, the drift check and the critic's cross-ticket check; `docs/design.md` SHALL name `factory spec amend` and `--intent unchanged`, carry a Spec drift paragraph and give the critic the approved changes not yet archived in its routing row; `dev/build-harness.spec.md` SHALL name `factory spec amend` and spec drift; README SHALL list the command under "Where a human decides" and the feature under Built; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. ' docs/changelog.md | grep -F 'factory spec amend'); echo "$E" | grep -c .; echo "$E" | grep -oF -e '--intent' -e 'in flight' -e tasks.md -e 'spec drift' -e 'not yet archived' -e whichever | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `6`

#### Scenario: The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input
- WHEN `(echo "amend=$(grep -c 'factory spec amend' docs/design.md | awk '{print ($1 > 0)}') intent=$(grep -c -- '--intent unchanged' docs/design.md | awk '{print ($1 > 0)}') drift=$(grep -c '^\*\*Spec drift\.\*\*' docs/design.md) row=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c 'not yet archived') build=$(grep -c 'factory spec amend' dev/build-harness.spec.md | awk '{print ($1 > 0)}') build_drift=$(grep -ci 'spec drift' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1`

#### Scenario: README lists the amend command and the drift check
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' README.md); B=$(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' README.md); echo "amend=$(echo "$H" | grep -c 'factory spec amend' | awk '{print ($1 > 0)}') intent=$(echo "$H" | grep -c -- '--intent' | awk '{print ($1 > 0)}') built=$(echo "$B" | grep -c '^- \*\*Spec amendment and drift\.\*\*')")`
- THEN it prints exactly `amend=1 intent=1 built=1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`
=== verification.md
## Acceptance

- An intent-unchanged amendment re-pins the change and keeps the plan's tasks → NEW; today `spec amend` is not a command (`invalid choice: 'amend'`), so it prints `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged`
- A later implementer run receives the amended spec, and the record lists what changed → NEW; today no record or event exists and the implementer gets v1: `changed=0 merged=0 reason=0 logged=0`, then `amended=0 old=1 run_version=1`
- Archive after an amendment writes the amended scenario → NEW; today archive writes v1: `archive=0 hello=0 hi=1`
- An amendment declared or found to change intent is refused, naming what a restart keeps and discards → NEW; today both attempts fail in argparse with no JSON refusal: `intent=changed exit_json=0 restart=0 decision=0 merged=0 pending=0 paths=0`, then the same for `intent=unchanged`, then `"approved_version": 1 versions=1 records=0`
- An amendment after archive is refused → NEW; today the amend attempts fail in argparse with no JSON, and archive writes v1: `late=0 changes=archive hello=0`
- A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing → NEW; today each attempt fails in argparse with no JSON refusal: `malformed=0 subticket=0 reason=0 "approved_version": 1 v2=0 records=0`
- An amendment is refused while a sub-ticket's run is in flight, naming the run → NEW; today it exits 2 from argparse without naming the run: `exit=2 names_run=0 "approved_version": 1 v2=0 pinned_old=1 records=0`
- A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges → NEW; today the implementer starts at once, and the second start is refused because that run is in flight: `unmerged: blocked=0 names=0 runs=1 ready-for-implementer`, then `merged: exit=2 runs=1`
- A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start → NEW; today the implementer runs instead of parking: `park T-0001.1: EMPTY-OUTPUT from implementer`, then `greet=0 other=0 runs=2`, then `ruled: exit=2 runs=2`
- Unrelated changes, a listed test and an amendment written after the change let the implementer start → REGRESSION; guards against the drift check parking what it should not
- The critic's input lists approved changes not yet archived, other than its own → NEW; today the section does not exist: `listed=0 self=0 decision=0 requirement=0`, then `after_archive: heading=0 listed=0`
- A change sent back to the spec writer leaves the critic's list → NEW; today the section does not exist: `listed=0 self=0 decision=0 requirement=0`, then `respec: heading=0 listed=0`
- A critic run's system prompt carries the cross-ticket rule → NEW; today the critic prompt has no such rule: `rule=0`
- The runtime critic prompt stays a copy of the documented one → REGRESSION
- The changelog records the change in one contiguous entry → NEW; today no entry names `factory spec amend`: `CONTIGUOUS`, `0`, `0`
- The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input → NEW; today `amend=0 intent=0 drift=0 row=0 build=0 build_drift=0`
- README lists the amend command and the drift check → NEW; today `amend=0 intent=0 built=0`
- The change adds no whitespace errors → REGRESSION

## Out-of-scope observations

- After `request-changes`, the spec writer's input does not include the spec it wrote before. `compose.py` adds the previous version only when `round.spec >= 1`, and `request-changes` resets the round to 0. I read v2 from `specs/T-0027/v2.md` directly.
- In this repo's store, `openspec/changes/` still holds the folders of closed tickets T-0026 and T-0030. Part B skips closed tickets, so they do not reach the critic. Why they were not archived is not checked here.

## PR description (the implementer's output)

Sub-ticket: T-0027.2 (ST-2, parts B and C of `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`). Branch `factory/T-0027.2`, commit `d085ca0` on base `8929054`, in worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0027.2`.

## What changed

**B. The critic's input (`factory/compose.py`).** The critic is the role that grades a spec before the operator's sign-off. Its input now has a section headed `## Approved changes not yet archived`. A change folder is the store's copy of a ticket's approved spec, written when the operator approves it and moved away when the ticket is archived. The new section comes right after the decision log. It is written by a new local helper, `add_approved_changes()`, in `compose()`, called only in the critic branch. The helper reads the directories under `<store>/openspec/changes/` in name order. It skips:
- `archive`;
- the reviewed ticket's own id;
- an id with no ticket record;
- a ticket that is `closed`, `ready-for-spec-writer`, `ready-for-critic` or `awaiting-spec-gate`.

Each remaining folder gets one entry: `### <id>: <title> (<status>)`, then `Change folder: `<absolute path>``, then `Changes: <cap>: <OP> <requirement>; ...` from `specstore.delta_ops_of_change` (or `none`), then `Decisions:` with one `- <line>` per `specstore.decisions_of` line. Each listed `proposal.md` is added to the run's `sources`. With no entries the section body is `none`. Without `openspec/changes/` the section is left out.

**C. The critic rule.** The four lines from the spec go under rubric item 5 ("Consistent") in three copies: the design doc's critic block (`docs/design.md:463-466`), `docs/prompts/03-spec-critic.md` and the runtime copy `factory/prompts/critic.md`. The new lines contain no `{2}` placeholder, so all three copies get the same text. The runtime copy still equals the documented one with `{2}` filled. I edited only the critic block of `docs/design.md`.

Callers (coding standard rule 2): no existing function changed signature. The only new call is `add_approved_changes()`, from the critic branch of `compose()`.

## Acceptance results

All commands ran from the worktree, inside the running-code wrapper (a fresh temporary HOME), with `TMPDIR` set to this run's scratch directory. The GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" ran once before the commands.

- NEW: "The critic's input lists approved changes not yet archived, other than its own"
  - before: `listed=0 self=0 decision=0 requirement=0`, `after_archive: heading=0 listed=0` (matches the spec's "fails today")
  - after: `listed=1 self=0 decision=1 requirement=1`, `after_archive: heading=1 listed=0`
- NEW: "A change sent back to the spec writer leaves the critic's list"
  - before: `listed=0 self=0 decision=0 requirement=0`, `respec: heading=0 listed=0`
  - after: `listed=1 self=0 decision=1 requirement=1`, `respec: heading=1 listed=0`
- NEW: "A critic run's system prompt carries the cross-ticket rule"
  - before: `rule=0`
  - after: `rule=1`
- REGRESSION: "The runtime critic prompt stays a copy of the documented one". After: `copies=same`.
- REGRESSION (intermediate): `grep -c 'whichever of the two merges first' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`. After: `docs/design.md:1`, `docs/prompts/03-spec-critic.md:1`, `factory/prompts/critic.md:1`. Before: `0` in each.
- Gate: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)` printed nothing and exited 0.
- Gate: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` gave `431 passed in 313.56s`, including the 13 new tests.

## Tests added/changed

Added one new file, `tests/factory/test_critic_approved_changes.py`, with 13 tests. They drive `bin/factory` on a throwaway store and a scratch target repo.
- Another approved ticket is listed with its exact entry (folder, `Changes: demo: ADDED Greets`, decision). The reviewed ticket is not listed, and the other ticket's `proposal.md` is in `sources`.
- The entry shows the ticket's state (`planned`).
- After archive, the body reads `none`.
- Each of `closed`, `ready-for-spec-writer`, `ready-for-critic` and `awaiting-spec-gate` is left out (4 parametrized cases).
- A change sent back through park, `resolve --to spec-gate` and `request-changes` leaves the list.
- A folder with no ticket record and the `archive` folder are skipped.
- Entries follow folder-name order, and an empty delta reads `Changes: none`.
- With no other change, the body reads `none`.
- Without a spec store, the section is absent.
- A critic run's system prompt carries the four new rubric lines.

I watched 12 of the 13 fail before the change: the section was absent and the rule missing. The no-spec-store test passed before and after, as it should, because it checks that the section is absent.

Existing tests changed: none.

## Known gaps and uncertainties

- When a listed change's proposal has no Decisions lines, the entry reads `Decisions: none`. The design gives `none` only for an empty Changes list and does not say how to show empty decisions, so this is my choice.
- A change folder with no `proposal.md` is still listed, with `Decisions: none`, and nothing is added to `sources`.
- The section is composed for every critic run on a store with a spec store, round 1 and later rounds alike. The design names no round condition.
- factory: markers added: none.

## Out-of-scope observations

- The parent spec says this repo's live store still has change folders for closed tickets T-0026 and T-0030. Part B skips closed tickets, so the critic never sees them. I did not look into why they were never archived.
- `uv run` printed a warning that the inherited `VIRTUAL_ENV=/Users/dphang/dev/nanobot/.venv-test` does not match the project's `.venv` and was ignored. The suite ran in the project environment. T-0031 deals with this inherited environment.

## Protected paths touched

All three are declared in this sub-ticket: `factory/compose.py`, `factory/prompts/critic.md` and `docs/prompts/03-spec-critic.md`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its expected output, both gates passed on commit d085ca0, and the new tests failed before the change and pass after it.
ESCALATIONS: none

## Diff `89290547a33a6091860c850fdda7ff285b409fa0...d085ca0b1cd5f084c4065c186c5467d6fd82b9ae`

diff --git a/docs/design.md b/docs/design.md
index 0fbd24f..e982666 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -460,6 +460,10 @@ RUBRIC (judge intent, not wording)
 4. No hidden decisions: no product or design choice is made silently;
    every protected path the change will touch is declared under Risk.
 5. Consistent: doesn't conflict with open tickets or stated architecture.
+   For each scenario, check whether it depends on behaviour that an
+   approved change not yet archived (listed in your input) changes. If
+   so, its setup must hold whichever of the two merges first; if it
+   would not, that is BLOCKING: name that ticket and its decision.
 6. Sufficient: an implementer could start without asking a question, and
    the operator at the gate could read every human-facing section of the
    spec: Problem, Evidence, Open questions, Decisions and Operator steps.
diff --git a/docs/prompts/03-spec-critic.md b/docs/prompts/03-spec-critic.md
index 6c3f745..cb9150f 100644
--- a/docs/prompts/03-spec-critic.md
+++ b/docs/prompts/03-spec-critic.md
@@ -19,6 +19,10 @@ RUBRIC (judge intent, not wording)
 4. No hidden decisions: no product or design choice is made silently;
    every protected path the change will touch is declared under Risk.
 5. Consistent: doesn't conflict with open tickets or stated architecture.
+   For each scenario, check whether it depends on behaviour that an
+   approved change not yet archived (listed in your input) changes. If
+   so, its setup must hold whichever of the two merges first; if it
+   would not, that is BLOCKING: name that ticket and its decision.
 6. Sufficient: an implementer could start without asking a question, and
    the operator at the gate could read every human-facing section of the
    spec: Problem, Evidence, Open questions, Decisions and Operator steps.
diff --git a/factory/compose.py b/factory/compose.py
index f40d7c9..177d41b 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -230,6 +230,33 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         p = root / "decisions.md"
         if p.exists() and p.read_text(encoding="utf-8").strip():
             add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")
+
+    def add_approved_changes() -> None:
+        # for the critic's cross-ticket check (its rubric item 5): every other change folder whose
+        # ticket is past the gate and not closed, with the requirements it changes and its decisions
+        changes = specstore.root_dir(root) / "changes"
+        if not changes.is_dir():
+            return
+        entries = []
+        for d in sorted(p for p in changes.iterdir() if p.is_dir()):
+            cid = d.name
+            if cid in ("archive", tid) or not store.ticket_path(root, cid).exists():
+                continue
+            other = store.load_ticket(root, cid)
+            if other["status"] in ("closed", "ready-for-spec-writer", "ready-for-critic", "awaiting-spec-gate"):
+                continue
+            ops = [f"{cap}: {op} {name}" for cap, by_op in specstore.delta_ops_of_change(root, cid).items()
+                   for op, reqs in by_op.items() for name in reqs]
+            proposal = d / "proposal.md"
+            decisions = []
+            if proposal.exists():
+                sources.append(str(proposal.relative_to(root)))
+                decisions = specstore.decisions_of(proposal.read_text(encoding="utf-8"))
+            entries.append(f"### {cid}: {other['title']} ({other['status']})\nChange folder: `{d}`\n"
+                           f"Changes: {'; '.join(ops) or 'none'}\n"
+                           + ("Decisions:\n" + "".join(f"- {ln}\n" for ln in decisions) if decisions
+                              else "Decisions: none\n"))
+        parts.append("\n## Approved changes not yet archived\n\n" + ("\n".join(entries) if entries else "none\n"))
     if role == "triage":
         add(t["request"], "Request (raw, with any answers appended)")
         every = current_truth(root)
@@ -267,6 +294,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         sel = selected(f"specs/{tid}/v{version}.md")
         add_truth(sel)
         add_decisions()
+        add_approved_changes()
         if rnd >= 2 and version >= 2:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
diff --git a/factory/prompts/critic.md b/factory/prompts/critic.md
index c31f0d4..c973590 100644
--- a/factory/prompts/critic.md
+++ b/factory/prompts/critic.md
@@ -19,6 +19,10 @@ RUBRIC (judge intent, not wording)
 4. No hidden decisions: no product or design choice is made silently;
    every protected path the change will touch is declared under Risk.
 5. Consistent: doesn't conflict with open tickets or stated architecture.
+   For each scenario, check whether it depends on behaviour that an
+   approved change not yet archived (listed in your input) changes. If
+   so, its setup must hold whichever of the two merges first; if it
+   would not, that is BLOCKING: name that ticket and its decision.
 6. Sufficient: an implementer could start without asking a question, and
    the operator at the gate could read every human-facing section of the
    spec: Problem, Evidence, Open questions, Decisions and Operator steps.
diff --git a/tests/factory/test_critic_approved_changes.py b/tests/factory/test_critic_approved_changes.py
new file mode 100644
index 0000000..6eed6a3
--- /dev/null
+++ b/tests/factory/test_critic_approved_changes.py
@@ -0,0 +1,184 @@
+"""The critic's list of approved changes not yet archived (T-0027 part B).
+
+On a store with a spec store, a critic run's input carries `## Approved changes not yet archived`:
+one entry per change folder under `openspec/changes/` whose ticket is neither closed nor back in the
+spec loop, other than the reviewed ticket's own, each with its title, state, folder, the
+requirements its deltas change and its Decisions lines. Each listed `proposal.md` is an input
+source. The body is `none` with no such change, and the section is left out without a spec store.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+HEADING = "## Approved changes not yet archived"
+
+
+def spec(decision: str, requirement: str) -> str:
+    return (f"=== proposal.md\n## Problem\nx\n## Decisions\n- {decision}\n"
+            "=== design.md\n## Proposed change\nEdit `src/greet.py`.\n## Tests to change\nnone\n"
+            f"=== specs/demo/spec.md\n## ADDED Requirements\n### Requirement: {requirement}\nThe tool SHALL act.\n\n"
+            "#### Scenario: It acts\n- WHEN `echo hi`\n- THEN it prints `hi`\n"
+            "=== verification.md\n## Acceptance\n- It acts → NEW\n")
+
+
+class Store:
+    def __init__(self, tmp_path: Path, spec_store: bool = True):
+        self.tmp = tmp_path
+        self.root = tmp_path / "store"
+        target = tmp_path / "t"
+        subprocess.run(["git", "init", "-q", "-b", "main", str(target)], check=True)
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(target),
+                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
+        if spec_store:
+            self.ok("init")
+
+    def ok(self, *argv: str) -> dict:
+        cp = subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+        assert cp.returncode == 0, cp.stdout + cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def ticket(self, tid: str, title: str, text: str) -> None:
+        """A new ticket `tid` with spec v1 `text`, at ready-for-critic."""
+        req, sp = self.tmp / f"{tid}-req.md", self.tmp / f"{tid}-spec.md"
+        req.write_text(f"# {title}\n\nDo it.\n")
+        sp.write_text(text)
+        assert self.ok("ticket", "new", "--file", str(req))["id"] == tid
+        self.ok("ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t")
+        self.ok("spec", "add", tid, "--file", str(sp))
+        self.ok("ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+
+    def approve(self, tid: str) -> None:
+        self.ok("ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t")
+        self.ok("approve-spec", tid)
+
+    def critic(self, tid: str) -> tuple[str, list[str]]:
+        rid = self.ok("run", "start", "--role", "critic", "--ticket", tid)["run_id"]
+        return self.compose(rid)
+
+    def compose(self, rid: str) -> tuple[str, list[str]]:
+        sources = self.ok("run", "compose", rid)["sources"]
+        return (self.root / "runs" / rid / "input.md").read_text(), sources
+
+
+def section(text: str) -> list[str] | None:
+    """The section's lines, heading first, up to the next `## ` heading; None when it is absent."""
+    lines = text.splitlines()
+    if HEADING not in lines:
+        return None
+    i = lines.index(HEADING)
+    rest = lines[i + 1:]
+    end = next((k for k, ln in enumerate(rest) if ln.startswith("## ")), len(rest))
+    return [HEADING] + rest[:end]
+
+
+@pytest.fixture
+def two(tmp_path) -> Store:
+    """T-0001 "Greeter" approved and pinned (ready-for-planner); T-0002 "Waver" at ready-for-critic."""
+    s = Store(tmp_path)
+    s.ticket("T-0001", "Greeter", spec("Greet by default.", "Greets"))
+    s.approve("T-0001")
+    s.ticket("T-0002", "Waver", spec("Wave at night.", "Waves"))
+    return s
+
+
+def test_the_critic_gets_each_other_approved_change_with_its_requirements_and_decisions(two):
+    rid = two.ok("run", "start", "--role", "critic", "--ticket", "T-0002")["run_id"]
+    text, sources = two.compose(rid)
+    folder = two.root / "openspec" / "changes" / "T-0001"
+    sec = section(text)
+    assert sec is not None
+    body = [ln for ln in sec[1:] if ln.strip()]
+    assert body[0].startswith("### T-0001: Greeter (") and body[0].endswith(")")
+    assert body[1:] == [f"Change folder: `{folder}`", "Changes: demo: ADDED Greets", "Decisions:",
+                        "- Greet by default."]
+    assert not any(ln.startswith("### T-0002") for ln in sec)  # the reviewed ticket is not listed
+    assert "openspec/changes/T-0001/proposal.md" in sources
+    # it follows the spec under review, as part of the critic's context
+    assert text.index(HEADING) > text.index("## Spec under review (v1)")
+
+
+def test_the_entry_names_the_ticket_state(two):
+    two.ok("ticket", "set", "T-0001", "status=planned")
+    sec = section(two.critic("T-0002")[0])
+    assert "### T-0001: Greeter (planned)" in sec
+
+
+def test_an_archived_change_leaves_the_list_and_the_body_reads_none(two):
+    two.ok("archive", "T-0001")
+    text, sources = two.critic("T-0002")
+    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
+    assert not any("proposal.md" in s for s in sources)
+
+
+@pytest.mark.parametrize("status", ["closed", "ready-for-spec-writer", "ready-for-critic", "awaiting-spec-gate"])
+def test_a_closed_ticket_or_one_back_in_the_spec_loop_is_left_out(two, status):
+    two.ok("ticket", "set", "T-0001", f"status={status}")
+    text, sources = two.critic("T-0002")
+    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
+    assert "openspec/changes/T-0001/proposal.md" not in sources
+
+
+def test_a_change_sent_back_to_the_spec_writer_leaves_the_list(two):
+    rid = two.ok("run", "start", "--role", "critic", "--ticket", "T-0002")["run_id"]
+    assert "### T-0001: Greeter" in "\n".join(section(two.compose(rid)[0]))
+    notes = two.tmp / "notes.md"
+    notes.write_text("redo\n")
+    two.ok("ticket", "park", "T-0001", "--reason", "x")
+    two.ok("resolve", "T-0001", "--to", "spec-gate")
+    two.ok("request-changes", "T-0001", "--notes", str(notes))
+    assert [ln for ln in section(two.compose(rid)[0]) if ln.strip()] == [HEADING, "none"]
+
+
+def test_a_folder_with_no_ticket_and_the_archive_folder_are_skipped(two):
+    two.ok("archive", "T-0001")
+    stray = two.root / "openspec" / "changes" / "T-0099"
+    stray.mkdir()
+    (stray / "proposal.md").write_text("## Problem\nx\n## Decisions\n- stray\n")
+    text, sources = two.critic("T-0002")
+    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
+    assert not any(src.startswith("openspec/changes/") for src in sources)
+
+
+def test_entries_follow_folder_name_order_and_an_empty_delta_reads_none(two):
+    two.ticket("T-0003", "Third", spec("Third decision.", "Thirds"))
+    two.approve("T-0003")
+    demo = two.root / "openspec" / "changes" / "T-0003" / "specs" / "demo" / "spec.md"
+    demo.write_text("## ADDED Requirements\n")
+    sec = section(two.critic("T-0002")[0])
+    heads = [ln for ln in sec if ln.startswith("### ")]
+    assert [h.split(":")[0] for h in heads] == ["### T-0001", "### T-0003"]
+    i = sec.index(next(h for h in heads if h.startswith("### T-0003")))
+    assert sec[i + 2] == "Changes: none"
+
+
+def test_with_no_other_change_the_body_reads_none(tmp_path):
+    s = Store(tmp_path)
+    s.ticket("T-0001", "Only", spec("Only decision.", "Only"))
+    text, sources = s.critic("T-0001")
+    assert [ln for ln in section(text) if ln.strip()] == [HEADING, "none"]
+    assert not any(src.startswith("openspec/changes/") for src in sources)
+
+
+def test_without_a_spec_store_the_section_is_left_out(tmp_path):
+    s = Store(tmp_path, spec_store=False)
+    s.ticket("T-0001", "Only", spec("Only decision.", "Only"))
+    assert not (s.root / "openspec" / "changes").exists()
+    text, _ = s.critic("T-0001")
+    assert section(text) is None
+
+
+def test_a_critic_run_s_system_prompt_carries_the_cross_ticket_rule(tmp_path):
+    s = Store(tmp_path)
+    s.ticket("T-0001", "Only", spec("Only decision.", "Only"))
+    rid = s.ok("run", "start", "--role", "critic", "--ticket", "T-0001")["run_id"]
+    prompt = " ".join((s.root / "runs" / rid / "system-prompt.txt").read_text().split())
+    assert ("For each scenario, check whether it depends on behaviour that an approved change not yet archived "
+            "(listed in your input) changes. If so, its setup must hold whichever of the two merges first; if it "
+            "would not, that is BLOCKING: name that ticket and its decision.") in prompt
