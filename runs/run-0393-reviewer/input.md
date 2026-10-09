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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0393-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0393-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0393-reviewer/wt` (branch `factory/T-0027.4`, base `bfc764cd4f533b6909678da16564f5f8e2359bc0`, head `d9c8a4d40544b62dd11214a9fc41887b28c3e778`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0027.4

### ST-4 / The documents record spec amendment, spec drift and the cross-ticket check (part E)
Depends on: ST-1, ST-2, ST-3
Parallel-safe: yes

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`. Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part E, except item 1 (the critic rubric block), which ST-2 landed. In `docs/design.md`: E items 2 (the `**Spec drift.**` paragraph after `**Tests a sibling added.**`), 3 (the Spec store sentence on `factory spec amend ... --intent unchanged`), 4 (line 113) and 5 (the `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic |` row). In `docs/changelog.md`: one new entry, 65, after 64 and before the closing `Declined:` line, covering all of A, B, C and D as part E lists. In `dev/build-harness.spec.md`: the `factory resolve` bullet (line 315) and the Spec store paragraph (line 193). In `README.md`: the Amend row, the Unstick row's `--ruling F` list, the `**Spec amendment and drift.**` Built bullet, and the status date. Describe what ST-1 to ST-3 built, read from the merged code. Read README's "Maintaining this page" section first.

Acceptance:
- NEW. The changelog records the change in one contiguous entry. THEN `CONTIGUOUS`, then `1`, then `6`.
- NEW. The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input. THEN `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1`.
- NEW. README lists the amend command and the drift check. THEN `amend=1 intent=1 built=1`.
- REGRESSION. The change adds no whitespace errors: WHEN `(git diff --check main...HEAD; echo "exit=$?")`. THEN only `exit=0`.
- REGRESSION (intermediate). The runtime critic prompt stays a copy of the documented one: `copies=same`. ST-4 must not touch the critic block.
- REGRESSION (intermediate). The harness suite passes, as in ST-1. `tests/factory/test_writing_standard.py` and the other document checks are in it.

Interim tests: none
Tests to change: none
Protected paths: none
Out of scope: any code or prompt file; the critic block of `docs/design.md` and its `docs/prompts/` copy (ST-2).

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

Sub-ticket: T-0027.4 (ST-4, part E of T-0027): `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0027/v3.md`, branch `factory/T-0027.4`, head `d9c8a4d40544b62dd11214a9fc41887b28c3e778`, base `bfc764cd4f533b6909678da16564f5f8e2359bc0`

## What changed

T-0027 adds three features to the factory (the harness that turns a ticket into merged code through a chain of AI agent roles):

- `factory spec amend`, a human-only command that corrects an approved spec after the spec gate (the human sign-off on a design), when the correction keeps the ticket's intent.
- The spec drift check, which parks a sub-ticket (one buildable piece of a ticket) before its first implementer run when its spec has gone stale.
- The critic's cross-ticket check. The critic is the role that grades a spec before the gate.

Sibling sub-tickets ST-1 to ST-3 built these in code. This sub-ticket records them in the documents. I described the features from the merged code: `factory/cli.py` `spec_amend`, `_restart_note`, `_add_spec_version`, `_check_drift`, `_sibling_drift` and `_test_drift`, and `factory/compose.py` `add_approved_changes`. No code or prompt file changed. The critic rubric block and its `docs/prompts/` copy are untouched.

Part E, item by item:

- **`docs/design.md`, item 2.** A new `**Spec drift.**` paragraph follows `**Tests a sibling added.**`. It covers the `specs/<id>/v<n>.yaml` record of `integration_head`. It says when the check runs: at `run start`, before the sibling-tests check, and only while the sub-ticket has no finished implementer run and no ruling on file. It gives both rules, the `BLOCKED from harness: spec drift:` refusal, and how the human resolves it (amend, rule, or both).
- **`docs/design.md`, item 3.** The Spec store paragraph gains sentences after "work from the delta the human approved". They name `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged` and say who runs it and when. They say it refuses while a run is in flight, what `--intent unchanged` keeps and what may change, and that a change of intent is refused with a restart note. The re-pin keeps `tasks.md`. Sub-tickets move to the new version, and no plan is superseded. The record is `approvals/<id>/amendment-<n>.md` with the `spec.amended` event, and the command changes no ticket state.
- **`docs/design.md`, item 4.** The PR-loop resolution rule (line 113) now reads "amend the sub-ticket or the pinned spec (`factory spec amend`, intent unchanged) first".
- **`docs/design.md`, item 5.** In the `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic |` row, the Receives column gains "every other approved change not yet archived, with its decisions".
- **`docs/changelog.md`.** Entry 65 is added after 64 and before `Declined:`. It is one entry covering A to D. It gives the incidents, the amend command and its `--intent` check, the restart note, the refusals (in flight, sub-ticket, at the gate, closed or archived, malformed), the kept `tasks.md` and the record. It also covers the head record and both spec drift rules, the measured 9-of-10 catch rate, the critic's "not yet archived" input with the "whichever" rule, and the four rejected alternatives from the spec's Decisions.
- **`dev/build-harness.spec.md`, line 315 (the `factory resolve` bullet).** `[--amend-spec FILE]` is removed from the signature. Its description is replaced with "`resolve` has no `--amend-spec`: it was built instead as `factory spec amend PARENT --file F --reason LINE --intent unchanged` (doc §Spec store)", followed by what the built command does. The bullet's second `--amend-spec` mention, on a parked parent, now names the route the Decisions give: `--to spec-gate`, then `approve-spec ID --edit FILE`.
- **`dev/build-harness.spec.md`, line 193 (the Spec store paragraph).** Two additions. `run compose` gives the critic `## Approved changes not yet archived`, with the inclusion rule and the `none` and left-out cases from `compose.py`. Every stored version writes `v<N>.yaml`, and a sub-ticket's first implementer `run start` checks spec drift (doc §Harness, Spec drift). In the same paragraph, "`approve-spec` or `--amend-spec` pins" now reads "`approve-spec` or `spec amend` pins", because the flag does not exist.
- **`README.md`.** Four changes:
  - An **Amend** row in "Where a human decides". It names the three triggers, the amend-or-restart rule and what `--intent changed` prints, and says the amendment moves no ticket.
  - The Unstick row's `--ruling F` list gains "the harness parked a sub-ticket for spec drift".
  - A Built bullet `**Spec amendment and drift.**`, which glosses spec drift and ends "It is tested, and has not yet fired on a real ticket."
  - Two edits beyond the four listed items. See Known gaps.

## Acceptance results

All commands ran from the worktree inside the fresh-HOME wrapper.

| Command | Before (head `bfc764c`) | After (head `d9c8a4d`) |
|---|---|---|
| NEW: the changelog records the change in one contiguous entry | `CONTIGUOUS`, `0`, `0` | `CONTIGUOUS`, `1`, `6` |
| NEW: the design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input | `amend=0 intent=0 drift=0 row=0 build=0 build_drift=0` | `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1` |
| NEW: README lists the amend command and the drift check | `amend=0 intent=0 built=0` | `amend=1 intent=1 built=1` |
| REGRESSION: the change adds no whitespace errors | — | `exit=0` |
| REGRESSION (intermediate): the runtime critic prompt stays a copy of the documented one | `copies=same` | `copies=same` |

What each result means:

- **Changelog.** `CONTIGUOUS`: the entries are numbered with no gap. `1`: exactly one entry names `factory spec amend`. `6`: that entry contains all six required phrases.
- **Design doc and build spec.** Each `1` means the required text is present: the amend command, `--intent unchanged`, the drift paragraph, the critic row, and both mentions in the build spec.
- **README.** The Amend row and `--intent` sit inside "Where a human decides", and the Built bullet is present.
- **Whitespace.** The diff adds no whitespace errors.
- **Critic prompt.** The critic block is untouched.

The before results match the spec's "fails today" outputs.

Gates, each run exactly as written from the worktree at `d9c8a4d`:
- `git diff --check main...HEAD`: exit 0, no output. The diff adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `486 passed in 404.51s`. That includes `tests/factory/test_writing_standard.py` and the other document checks, so no document check broke.

## Tests added/changed

None. The sub-ticket lists no interim tests and no tests to change. This sub-ticket edits documents only, and its acceptance commands are the document checks.

## Known gaps and uncertainties

- **README edits beyond the four listed items.** The sub-ticket's README scope lists four items. The briefing also says "A change to a command, state, stop or path updates [README] in the same ticket", and README's "Maintaining this page" rule makes a stale sentence a reviewer finding. So I made two more small edits:
  - The Spec critic row of "What each role reads and writes" now lists "every other approved spec not yet archived, with its decisions".
  - The store layout tree under "What the factory keeps in a target" now shows `v<n>.yaml` beside `specs/<T>/v<n>.md`, and `amendment-<n>.md (spec amend)` under `approvals/<T>/`.

  If the reviewer judges these out of scope, they are separate hunks and revert cleanly.
- **The extra `dev/build-harness.spec.md` edits inside the named passages.** These are the "`approve-spec` or `spec amend` pins" wording in the Spec store paragraph and the parked-parent `--amend-spec` mention in the resolve bullet. Both are in the two passages the sub-ticket names. I changed them because leaving them would contradict "`resolve` has no `--amend-spec`".
- **The status date was not bumped.** README already says "Current state as of 2026-10-09", and `date -u +%F` prints 2026-10-09, so there was nothing to bump.
- **Issue dates in the changelog.** Entry 65 dates issues #44 and #50 as 2026-10-04. I read that from `gh issue view` (`createdAt` 2026-10-04T17:39Z and 2026-10-04T21:26Z).
- **Measured figures.** The "9 of 10 known breaks" and "about half of all sub-tickets" figures come from the parent spec's Evidence table: 2 of 2 plus 7 of 8 breaks caught, and 17 of 36 plus 29 of 43 sub-tickets parked. I did not re-measure them.
- **No AGENTS.md.** This repository has no `AGENTS.md` (`ls -a` of the worktree), so process step 1's AGENTS.md read had nothing to read.

## Out-of-scope observations

- `dev/build-harness.spec.md` still names `--amend-spec` in build case 48 (line 410), cases 77, 83 and 84 (lines 453, 459, 460), and the round-4 responses (lines 533, 541). These are historical test cases and responses, which this sub-ticket does not cover.
- `resolve --amend-subticket` is in the build spec's signature but not in `factory/cli.py` (`grep -n 'amend-subticket\|amend_subticket' factory/cli.py` finds nothing).
- `docs/design.md:60`, the Tests a sibling added paragraph, also says "amend the sub-ticket or the pinned spec". Part E item 4 names only line 113, so I left line 60 alone.
- `dev/issues.md:51` still lists issue #44 as "T-0027 (spec approved; queued)". The issue index changes when the ticket closes, not in this sub-ticket.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its expected line and both gates passed on `d9c8a4d`; the open questions are only the two small README edits beyond the listed items, which I disclosed above.
ESCALATIONS: none

## Diff `bfc764cd4f533b6909678da16564f5f8e2359bc0...d9c8a4d40544b62dd11214a9fc41887b28c3e778`

diff --git a/README.md b/README.md
index a428339..51be5e8 100644
--- a/README.md
+++ b/README.md
@@ -83,7 +83,7 @@ directories and `models` entries use.
 |---|---|---|---|
 | Triage (`triage`) | the request; the capability index, one line per current-truth capability with its spec's path and requirement names; after a human answer, its own earlier output | ACCEPT · CLARIFY · NEEDS-HUMAN · REJECT | the title and type, copied onto the ticket |
 | Spec writer (`spec_writer`) | triage's output, the request; current truth in full for the capabilities triage named, and the capability index for the rest; the whole decision log; after a revision request, the critic's findings and its own previous spec; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
-| Spec critic (`critic`) | the spec version; current truth in full for the capabilities triage named or the spec cites, and the capability index for the rest; the whole decision log; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
+| Spec critic (`critic`) | the spec version; current truth in full for the capabilities triage named or the spec cites, and the capability index for the rest; the whole decision log; every other approved spec not yet archived, with its decisions; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
 | Planner (`planner`) | the approved spec; the whole decision log; rulings; any sub-tickets that already exist | PLANNED · ESCALATE | the plan, `plans/<ticket>.md`, and one sub-ticket per piece, with its dependencies |
 | Implementer (`implementer`) | where it works (its worktree, branch, base commit and the wrapped gate commands), the sub-ticket, the pinned spec; on a revision, both checkers' findings and the gate result | READY-FOR-REVIEW · BLOCKED | its commits on branch `factory/<sub-ticket>` and the head commit; the message itself is the PR description |
 | Code reviewer (`reviewer`) | the sub-ticket, the pinned spec, the PR description, the diff; from round 2, both checkers' findings from the previous round; any ruling | APPROVE · REQUEST-CHANGES · ESCALATE | a verdict for that commit, `results/<commit>/reviewer.yaml` |
@@ -428,7 +428,8 @@ git ignores them.
 │       │                          the path is state_dir in instance.yaml
 │       ├── requests/<T>.md        each request as filed; requests/index.yaml records its source file
 │       ├── tickets/<T>.yaml       state, rounds, park reason, head commit; sub-tickets are <T>.<k>.yaml
-│       ├── specs/<T>/v<n>.md      every spec version; specs/<T>.<k>/subticket.md for each sub-ticket
+│       ├── specs/<T>/v<n>.md      every spec version, with v<n>.yaml: the integration head it was
+│       │                          written against; specs/<T>.<k>/subticket.md for each sub-ticket
 │       ├── plans/<T>.md           the planner's plan
 │       ├── runs/run-NNNN-<role>/  one per role run: system-prompt.txt, input.md, output.md,
 │       │   │                      meta.yaml (status, model, base, head), diff.patch for checkers
@@ -437,7 +438,8 @@ git ignores them.
 │       ├── results/<commit>/      reviewer.yaml, verifier.yaml, ci.yaml: the verdicts on that commit;
 │       │                          superseded-<n>/ holds rows set aside by a re-check
 │       ├── approvals/<T>/         spec-v<n>.yaml (approve-spec), changes-<n>.md (request-changes),
-│       │                          ruling-<n>.md and resolve-<n>.yaml (resolve)
+│       │                          ruling-<n>.md and resolve-<n>.yaml (resolve), amendment-<n>.md
+│       │                          (spec amend)
 │       ├── openspec/specs/<cap>/  current truth: one spec per capability
 │       ├── openspec/changes/<T>/  a pinned spec as changes to current truth;
 │       │                          moved to openspec/changes/archive/<date>-<T>/ when it closes
@@ -794,7 +796,8 @@ FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLE
 |---|---|---|
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, or the harness blocked an implementer whose sub-ticket lists a test no merged sibling added; a ruling on the code reviewer's escalation re-runs the checks, with the ruling in their input) · `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design, and the sub-ticket returns to its checks; `--ruling F` sends the sub-ticket back to its implementer instead) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, an accepted protected path, a re-check, a re-plan, a re-scope, or closing |
+| **Amend** | `factory spec amend T-n --file F --reason "<line>" --intent unchanged`, on an approved spec before archive, while no run is in flight on the ticket or its sub-tickets | that the approved spec must change after the gate, because another ticket merged first, a checker found a scenario that cannot pass as written, or you changed your mind. Amend only when the Problem, the Decisions and every requirement's statement stay as approved; otherwise restart, by re-spec and re-plan or by close and re-file. `--intent changed` prints what a restart keeps and discards. Later runs receive the amended version, but the amendment moves no ticket: resume it as usual, for example with `--ruling F` |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, the harness blocked an implementer whose sub-ticket lists a test no merged sibling added, or the harness parked a sub-ticket for spec drift; a ruling on the code reviewer's escalation re-runs the checks, with the ruling in their input) · `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design, and the sub-ticket returns to its checks; `--ruling F` sends the sub-ticket back to its implementer instead) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, an accepted protected path, a re-check, a re-plan, a re-scope, or closing |
 | **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included. It appends one dated line to the target's decision log, `decisions.md`, which the spec writer, critic and planner receive with their input | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
@@ -860,6 +863,18 @@ path above is relative to the store.
   sub-ticket added the file. If none did, the sub-ticket parks as blocked, and the human rules on it
   as on any blocked build ("Where a human decides"). Any other existing test still changes only if
   the approved spec lists it. It is tested, and has not yet fired on a real ticket.
+- **Spec amendment and drift.** An approved spec can go stale while its sub-tickets are built:
+  another ticket merges first, or a scenario turns out unable to pass as written.
+  `factory spec amend` replaces the approved spec with a corrected version, when the correction
+  keeps what the ticket is for ("Where a human decides"). Later runs receive the corrected version,
+  and archive writes its scenarios into current truth. Spec drift is a change since the spec was
+  written that the spec did not plan for. Before a sub-ticket's first implementer run, the harness
+  checks for two kinds: the sub-ticket's acceptance checks name another sub-ticket of the same
+  spec that has not merged and is not one of its dependencies, or a test changed beside a file the
+  spec names, and no "Tests to change" list names it. On drift the sub-ticket parks as blocked,
+  and the human amends the spec or rules on it. The critic also receives every other approved spec
+  not yet archived, and blocks a scenario whose setup would not hold whichever of the two tickets
+  merges first. It is tested, and has not yet fired on a real ticket.
 - **Re-plan after a re-spec.** When the human sends a planned parent back to the spec gate and
   approves a new spec version, the planner splits it again under the same parent. Each sub-ticket
   records the approved version it was planned from. The new plan supersedes the old plan's
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index e18390b..4b989d6 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -190,7 +190,7 @@ history: []
 
 Spec text `specs/<ID>/v<N>.md` (every version the writer returns, with its STATUS/CONFIDENCE/ESCALATIONS trailer removed: the text above its last `STATUS:` line, as item 42 requires); sub-ticket text `specs/<ID>/subticket.md`.
 
-**Spec store** (doc §Harness, Spec store). `factory init` creates `openspec/config.yaml` (`schema: spec-factory`), `openspec/schemas/spec-factory/schema.yaml` (the artifacts of OpenSpec's `spec-driven`, `proposal`, `specs` with `generates: specs/**/*.md`, `design` and `tasks`, plus `verification` with `generates: verification.md` and `requires: [specs]`), an empty `openspec/specs/` and an empty `decisions.md`. Pinning a version (K) splits it on its `=== <path>` lines (the path is the first token after `=== `; text before the first such line is dropped) into `openspec/changes/<ID>/<path>`. A version pinned before `factory init` created `openspec/` has no change folder; its parent's archive refuses (K). A version is **well-formed** when every path is `proposal.md`, `design.md`, `verification.md` or `specs/<capability>/spec.md` with a kebab-case capability, each at most once, with at least one delta part; every delta part has at least one `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements` heading, and every `### Requirement:` line sits under one of them and has a name unique within its part; and the `## Acceptance` of `verification.md` labels every `#### Scenario:` name of the delta parts exactly once, `NEW` or `REGRESSION`, and labels no other name. Any other version is malformed. Every spec that `approve-spec` or `--amend-spec` pins must be well-formed, so every build case that approves a spec (items 43–53, 60, 61, 64, 77, 83, 84) needs a well-formed four-part `spec_writer-1.md` stub. `verification.md` is the writer's part plus `## Critic rounds`: per critic run of the ticket, oldest first, `round <n> · spec v<N> · <run_id> · <STATUS>` and its findings verbatim. `tasks.md` comes from `factory spec tasks`. No role writes `openspec/` or `decisions.md`. Only `factory archive` (K) writes `openspec/specs/`. `decisions.md` has three writers, each appending `<YYYY-MM-DD> <ID> <line>` (UTC date): `factory archive` (K); `factory decision add ID TEXT` (K), at any ticket state; and `factory resolve ID --answer FILE` or `--close` with `--decision TEXT` (K). `run compose` gives a `decisions.md` that holds any text to the spec writer and critic after current truth, and to the planner after the approved spec.
+**Spec store** (doc §Harness, Spec store). `factory init` creates `openspec/config.yaml` (`schema: spec-factory`), `openspec/schemas/spec-factory/schema.yaml` (the artifacts of OpenSpec's `spec-driven`, `proposal`, `specs` with `generates: specs/**/*.md`, `design` and `tasks`, plus `verification` with `generates: verification.md` and `requires: [specs]`), an empty `openspec/specs/` and an empty `decisions.md`. Pinning a version (K) splits it on its `=== <path>` lines (the path is the first token after `=== `; text before the first such line is dropped) into `openspec/changes/<ID>/<path>`. A version pinned before `factory init` created `openspec/` has no change folder; its parent's archive refuses (K). A version is **well-formed** when every path is `proposal.md`, `design.md`, `verification.md` or `specs/<capability>/spec.md` with a kebab-case capability, each at most once, with at least one delta part; every delta part has at least one `## ADDED Requirements`, `## MODIFIED Requirements` or `## REMOVED Requirements` heading, and every `### Requirement:` line sits under one of them and has a name unique within its part; and the `## Acceptance` of `verification.md` labels every `#### Scenario:` name of the delta parts exactly once, `NEW` or `REGRESSION`, and labels no other name. Any other version is malformed. Every spec that `approve-spec` or `spec amend` pins must be well-formed, so every build case that approves a spec (items 43–53, 60, 61, 64, 77, 83, 84) needs a well-formed four-part `spec_writer-1.md` stub. `verification.md` is the writer's part plus `## Critic rounds`: per critic run of the ticket, oldest first, `round <n> · spec v<N> · <run_id> · <STATUS>` and its findings verbatim. `tasks.md` comes from `factory spec tasks`. No role writes `openspec/` or `decisions.md`. Only `factory archive` (K) writes `openspec/specs/`. `decisions.md` has three writers, each appending `<YYYY-MM-DD> <ID> <line>` (UTC date): `factory archive` (K); `factory decision add ID TEXT` (K), at any ticket state; and `factory resolve ID --answer FILE` or `--close` with `--decision TEXT` (K). `run compose` gives a `decisions.md` that holds any text to the spec writer and critic after current truth, and to the planner after the approved spec. After the decision log, `run compose` gives the critic `## Approved changes not yet archived`: one entry per other folder under `openspec/changes/` whose ticket is neither closed nor in `ready-for-spec-writer`, `ready-for-critic` or `awaiting-spec-gate`, with its id, title, state, folder path, the requirements its deltas add, modify or remove, and its Decisions lines; the body is `none` when no folder qualifies, and the section is left out when `openspec/changes/` does not exist. Every spec version stored by `spec add`, `approve-spec --edit` or `spec amend` also writes `specs/<ID>/v<N>.yaml` with `integration_head`, the integration branch's head then, or null when it does not resolve. A sub-ticket's first implementer `run start` checks spec drift against the parent's approved version and refuses with `BLOCKED from harness: spec drift:` (doc §Harness, Spec drift).
 
 States: `ready-for-triage`, `waiting-requester`, `ready-for-spec-writer`, `ready-for-critic`, `ready-for-spec-gate`, `ready-for-planner`, `waiting-dependencies`, `ready-for-implementer`, `checks-in-flight`, `ready-for-checks` (after a checker `--redispatch`; only the roles without a row on the current head run), `ready-for-merge`, `merged`, `ready-for-parent-verify` (parent only: every sub-ticket merged, one verifier run on `main` pending), `parked`, `closed`, `running`.
 
@@ -312,7 +312,7 @@ No API key in any run: the CLI authenticates from the owner's login. Keys only i
 - `factory approve-spec ID [--version N] [--edit FILE]`: pins `approved_version` (edited text saved as a new version first), copies "Tests to change" and Risk paths into the ticket, `approvals/ID/spec-v<N>.yaml`, writes the pinned version as the change folder (B; event `change.pinned`; exit 2 with nothing written when the version is malformed (B) or a delta does not apply to current truth: an ADDED requirement name already in `openspec/specs/<capability>/spec.md`, or a MODIFIED or REMOVED name not in it), → `ready-for-planner`, and **exports** the pinned text to `knowledge_vault/sanitized_specs/<ID>.md` (`factory export ID`; event `spec.exported`; the export directory is a config key for the later `specs/` → `tickets/` rename).
 - `factory request-changes ID --notes FILE`: `round.spec: 0`, → `ready-for-spec-writer`.
 - `factory approve-pr ID --head SHA` → `approvals/ID/pr-SHA.yaml`; `factory approve-guardrail ID --head SHA` → `approvals/ID/guardrail-SHA.yaml`.
-- `factory resolve ID (--answer FILE | --ruling FILE [--to implementer] [--amend-subticket FILE] [--amend-spec FILE] | --redispatch [--budget USD] | --close | --to spec-gate) [--decision TEXT]` (doc §Routing rules, resolution list): `--answer` on `waiting-requester` or a triage/spec-writer `NEEDS-HUMAN` → appended to `requests/<ID>.md` under `## Answer <n>`, ticket back to the asking role's ready state, with the asking role's previous output (the `output.md` of its most recent finished run on the ticket) added to that role's next input (doc §Routing rules) (CLARIFY and NEEDS-HUMAN are questions: `--ruling` on them → exit 2 `use --answer`); `--ruling` on a park from BLOCKED, a critic ESCALATE or a planner ESCALATE → the emitting role's ready state, **same round**, the ruling in that role's next input; `--ruling` on a PR loop at max rounds, a SPEC-DEFECT or a reviewer ESCALATE (`--to implementer`, the default there) → `round.pr: 0`, ruling becomes findings input, `ready-for-implementer`; `--amend-subticket` replaces `specs/<ID>/subticket.md`; `--amend-spec` writes `specs/<parent>/v<N+1>.md`, re-pins `approved_version` and rewrites the change folder as `approve-spec` does (`## Critic rounds` kept; the same well-formed and applies-to-current-truth checks, exit 2 with nothing re-pinned when FILE fails them), writes `approvals/<parent>/spec-v<N+1>.yaml`, re-exports; in-flight siblings keep the version their `meta.yaml` `spec_version` names (their `input.md` is already written, I.2) and the human decides whether to re-plan; `--redispatch` → the killed role's ready state, round unchanged, and `--budget USD` sets the ticket's `budget_usd`, copied into the redispatched run's `meta.yaml` (recorded, not enforced per agent in v0, E7); `--to spec-gate`; `--close`. `--close` on a sub-ticket also parks its parent (`parked.reason: sub-ticket <ID> closed`), as a parent-close FAILED or SPEC-DEFECT does (H); on a parked parent, `--amend-spec FILE` re-pins the spec and moves the parent to `ready-for-planner` (re-plan: the planner's new sub-tickets take the next free ids under the same parent, merged ones stay `merged`), or `--close` closes the parent and its unmerged sub-tickets (doc §Routing rules). Each writes `approvals/ID/resolve-<n>.yaml`, event `human.resolved`. `--decision TEXT`, valid only with `--answer` or `--close`, also appends `<YYYY-MM-DD> <ID> <TEXT>` to `decisions.md` once that mode's own checks pass, keeps the line as `decision` in the `resolve-<n>.yaml` record and the ticket history, and logs `decision.recorded` (`ticket`, `by`, `line`, `via`); alone, with any other mode, or with blank or multi-line TEXT → exit 2, nothing written.
+- `factory resolve ID (--answer FILE | --ruling FILE [--to implementer] [--amend-subticket FILE] | --redispatch [--budget USD] | --close | --to spec-gate) [--decision TEXT]` (doc §Routing rules, resolution list): `--answer` on `waiting-requester` or a triage/spec-writer `NEEDS-HUMAN` → appended to `requests/<ID>.md` under `## Answer <n>`, ticket back to the asking role's ready state, with the asking role's previous output (the `output.md` of its most recent finished run on the ticket) added to that role's next input (doc §Routing rules) (CLARIFY and NEEDS-HUMAN are questions: `--ruling` on them → exit 2 `use --answer`); `--ruling` on a park from BLOCKED, a critic ESCALATE or a planner ESCALATE → the emitting role's ready state, **same round**, the ruling in that role's next input; `--ruling` on a PR loop at max rounds, a SPEC-DEFECT or a reviewer ESCALATE (`--to implementer`, the default there) → `round.pr: 0`, ruling becomes findings input, `ready-for-implementer`; `--amend-subticket` replaces `specs/<ID>/subticket.md`; `resolve` has no `--amend-spec`: it was built instead as `factory spec amend PARENT --file F --reason LINE --intent unchanged` (doc §Spec store), which writes `specs/<parent>/v<N+1>.md`, makes it `approved_version`, re-pins the change folder keeping `tasks.md` (the same well-formed and applies-to-current-truth checks, exit 2 with nothing written when FILE fails them), moves each sub-ticket not `merged` or `closed` to the new version, writes `approvals/<parent>/amendment-<n>.md`, logs `spec.amended`, and changes no ticket state; it refuses while any run is in flight on the parent or its sub-tickets, and refuses a change of intent; `--redispatch` → the killed role's ready state, round unchanged, and `--budget USD` sets the ticket's `budget_usd`, copied into the redispatched run's `meta.yaml` (recorded, not enforced per agent in v0, E7); `--to spec-gate`; `--close`. `--close` on a sub-ticket also parks its parent (`parked.reason: sub-ticket <ID> closed`), as a parent-close FAILED or SPEC-DEFECT does (H); on a parked parent, a new spec goes through `--to spec-gate` and `approve-spec ID --edit FILE`, which moves the parent to `ready-for-planner` (re-plan: the planner's new sub-tickets take the next free ids under the same parent, merged ones stay `merged`), or `--close` closes the parent and its unmerged sub-tickets (doc §Routing rules). Each writes `approvals/ID/resolve-<n>.yaml`, event `human.resolved`. `--decision TEXT`, valid only with `--answer` or `--close`, also appends `<YYYY-MM-DD> <ID> <TEXT>` to `decisions.md` once that mode's own checks pass, keeps the line as `decision` in the `resolve-<n>.yaml` record and the ticket history, and logs `decision.recorded` (`ticket`, `by`, `line`, `via`); alone, with any other mode, or with blank or multi-line TEXT → exit 2, nothing written.
 - `factory decision add ID TEXT`: appends `<YYYY-MM-DD> <ID> <TEXT>` (UTC date, TEXT stripped) to `decisions.md`, creating it when absent (no `factory init` needed), for a ticket in any state, closed included; event `decision.recorded` with `via: decision add`. An unknown ID, or blank or multi-line TEXT → exit 2, nothing written.
 - `factory archive ID` (harness identity; `build.js` runs it on the parent-close VERIFIED, H): (1) appends `## Verifier results` to `openspec/changes/<ID>/verification.md`, one line per verifier row in `results/` for the parent's and its sub-tickets' heads, oldest first, `<head> · <ticket> · <STATUS> · <run_id>`; (2) applies every delta to `openspec/specs/<capability>/spec.md` (created with `# <capability>` and `## Requirements` when absent): ADDED appends the requirement block, MODIFIED replaces the block whose `### Requirement:` name matches, REMOVED deletes it; (3) moves `openspec/changes/<ID>` to `openspec/changes/archive/<YYYY-MM-DD>-<ID>` (UTC date); (4) appends `<YYYY-MM-DD> <ID> <line>` to `decisions.md` per line of `proposal.md`'s `## Decisions` other than `none`. One commit, event `change.archived`. Refusals, each exit 2 with nothing written, checked in this order before (1): no `openspec/` → `no spec store (factory init not run)`; no `openspec/changes/<ID>/` (its spec was pinned before `factory init`) → `<ID> has no change folder to archive`; a delta that does not apply. H parks the parent on each. A park for no spec store or no change folder is resolved by `factory resolve ID --close`, which closes the parent as applied: `openspec/specs/` stays unchanged and archive appends nothing to `decisions.md` (the human logs any decision with `factory decision add`), and if current truth should carry the spec, it is re-intaken as a new ticket (doc §Routing rules, resolution list).
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 7b76a46..4c0c3f6 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -66,5 +66,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 62. After issue #77 (2026-10-08), where Nanobot ticket T-0024 was sent back to the spec gate after planning and approved at a new version: its new plan's sub-ticket was created, but the old plan's sub-ticket that the operator had closed parked the parent at once, and only moving that sub-ticket's record out of the store's `tickets/` by hand let the build go on. Each sub-ticket now records `planned_from`, the parent's approved version when it was created, which nothing changes afterwards. Once a parent has a sub-ticket planned from a later version, its sub-tickets that have not merged and were planned from an earlier one are superseded: kept with their ids and records, but left out of `ready-implementers` (listed under `superseded`), the final check, the close, archive and `resolve --replan`. Merged ones stay merged and count. `subticket add` reports and logs the sub-tickets it supersedes, and refuses a plan whose `Depends on` names one; the planner's input names them. A record without `planned_from` falls back to its `spec.approved_version`, and a second plan at the same approved version supersedes nothing. Rejected: a superseded mark written at re-plan time, which needs a migration for stores that already hold such sub-tickets; and comparing with the parent's current approved version, which would supersede the live plan after a spec amendment that keeps it.
 63. After issue #57 (2026-10-05), where the merge gate merged changes to protected paths without reading any declaration of them, while the code reviewer's prompt promised that the gate would require a human approval: the approved spec's Risk section is now the authorization. The spec writer declares every protected path the change will touch on one line of Risk, `Protected paths: none` or `Protected paths:` followed by backticked entries, one path or glob per entry, with no brace lists; the human approves that line at the spec gate. At merge, the gate compares the changed paths, from the merge base with the integration branch and with both sides of a move, against the instance's in-repo protected globs and the pinned spec's line. It refuses each undeclared protected path by name, with an error that starts `BLOCKED from merge gate`, and the build parks the sub-ticket with that error. The human answers the park with `resolve --accept-paths F`, which accepts those paths for that sub-ticket and returns it to its checks, whose passing results stand, or with `resolve --ruling F`, which sends it back to its implementer at the same round. A ruling on a reviewer's ESCALATE now returns the sub-ticket to its checks, with the results that did not pass set aside, instead of to the spec critic, a step that never runs for a sub-ticket. Check 6 of the code reviewer prompt says what the gate does, the spec writer's FORMAT gives the declaration line, and the design's gate lines, piece 7, piece 8, piece 9 and the resolution rules drop the per-PR approval for protected paths. Rejected: reading every backticked path in Risk, since Risk sections also name paths they promise not to touch; and a human approval on every change to a protected path, which would have stopped 18 of the last 20 merges in this repository.
 64. After issue #76 (2026-10-09), where five of the seven role prompts, triage, planner, implementer, code reviewer and verifier, lacked the reading rules that #73 gave the spec writer and critic, though the implementer and verifier run test suites and other long commands, and every later turn re-sends what a run has read. Each of the five prompts gains the critic's Turn economy bullet, word for word: put independent reads and commands in one turn, read a line range once grep has found it, and send long output to a file in the run's scratch directory and grep or tail it. The spec writer's sentence on writing the spec in as few writes as possible stays out. The bullet goes directly before the declared-path rule in the implementer's and verifier's RULES, last in the code reviewer's WHAT YOU RUN, and last in the planner's and triage's RULES. #74's replay (entry 59) found that these rules cut the spec writer's tokens by about 37% at the same quality, but it tested the critic's reading rules only together with a cap on checking, and that pair saved nothing and made the critic check less. Nothing else in the five prompts changes, and the hook that would refuse whole-file reads and uncapped searches stays with #65. The runtime moves to these prompts only after the operator's replay of past implementer and verifier runs, with the old and the new prompts, holds quality. Rejected: a shared preamble line, which would also reach the spec writer and critic, which already carry the rules.
+65. After issues #44 and #50 (2026-10-04), where scenarios approved at the spec gate could not pass once another ticket merged first, and nothing could correct the pinned spec: on the Nanobot target, two scenarios of its ticket T-0008 created no policy file after a merged ticket made one mandatory, rulings let the build go on, and archive would still have written the unamended scenarios into current truth; here, T-0012's pinned spec was edited in place by hand, and a test that merged after T-0032's spec was written blocked T-0032.1's implementer. A human now amends a pinned spec with `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged`. It writes F as the next version and makes it the approved one, which every later role run receives. It re-pins the change folder but keeps the planner's `tasks.md`, so archive writes the amended scenarios. `--intent` is required: the harness checks that the Problem, every Decisions line, and each requirement's name, operation and statement are unchanged. It refuses `--intent changed`, or any such difference, with a restart note that names the merged sub-tickets a restart keeps, the unmerged ones it discards, and the commands to re-spec and re-plan or to close and re-file. It also refuses, writing nothing, while any run is in flight on the ticket or its sub-tickets, on a sub-ticket, at the gate, on a closed or archived ticket, and for a version that fails the gate's checks. Each amendment is recorded in `approvals/<ticket id>/amendment-<n>.md`, logged as `spec.amended`, and changes no ticket state. Every stored spec version now records the integration branch's head in `specs/<ticket id>/v<n>.yaml`. Before a sub-ticket's first implementer run, `run start` checks for spec drift: its Acceptance names an unmerged sibling it does not depend on, or a test file changed since its parent's approved version was written, in a commit that also changed a file the design names, and no Tests to change list names it. Drift refuses the run with an error that starts `BLOCKED from harness: spec drift:`, and the build parks the sub-ticket; the human amends, rules, or both, and a ruling on file stops the check. Measured on both stores' history, the test rule would have caught 9 of 10 known breaks and parks about half of all sub-tickets. The critic now receives every other approved change not yet archived, with the requirements it changes and its decisions, and its rubric item 5 makes a scenario BLOCKING when its setup would not hold whichever of the two tickets merges first. Rejected: the build spec's unbuilt `resolve --amend-spec`, because an amendment may be needed while the ticket is not stopped; a critic run on every amendment, which needs a new route; running each scenario at build start, whose expected failure is prose a program cannot compare; and a new park status for drift, which needs a new `resolve` route.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index e982666..19d37e6 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -59,6 +59,8 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Tests a sibling added.** A sub-ticket's "Tests to change" may list a test file that an earlier sibling sub-ticket of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The planner writes these lines, so the spec gate never saw them; the harness checks them instead. Before each implementer run of a sub-ticket, `run start` reads the lines of that form inside the sub-ticket's "Tests to change" field, and nowhere else, and checks each file, not the test function. The file passes when it is absent at the parent's base, which is the integration branch before the parent's first sub-ticket merged, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge: reachable from the integration branch just after that merge, not from the integration branch just before it. Any merged sibling of the parent counts; the ID on the line is for the reader. When a file fails, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build parks the sub-ticket with that error as the reason, and the human resolves it as an implementer's BLOCKED: amend the sub-ticket or the pinned spec, then `resolve --ruling`, or close it. A test that existed before the parent's first merge still needs the pinned spec's list.
 
+**Spec drift.** Between the writing of a spec and the build of one of its sub-tickets, other tickets merge, and a sibling that the sub-ticket's checks rely on may not have merged yet. The harness checks for this before the implementer spends a run on it. Every spec version the store keeps, from `spec add`, a gate edit or `spec amend`, records the integration branch's head when it was stored, as `integration_head` in `specs/<ticket id>/v<n>.yaml`; the value is null when the target repo or branch does not resolve. Before a sub-ticket's implementer run, `run start` checks for drift, ahead of the sibling-tests check. It checks only while the sub-ticket has no finished implementer run and no ruling on file. Two rules find drift. The sibling rule: the sub-ticket's Acceptance field names, by id or by plan label as a whole token, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. The test rule counts from the head recorded with the parent's approved version. It is skipped when that version has no record, because it was stored before the record existed, or when the head is null or not a commit in the target repo. For each first-parent commit on the integration branch since that head that changed a file the version's design part names, each test file the commit changed is a finding, unless the design's `## Tests to change` or the sub-ticket's "Tests to change" lists it. Named files are the design part's backticked paths that exist at the integration branch's head, other than test files and `.md` documents, which nearly every ticket edits. A test file's name starts with `test_`, ends `_test.<ext>`, or contains `.test.`. The test rule approximates "a test pins behaviour the spec changes". Measured on two stores' history, it would have caught 9 of 10 known breaks, and it parks about half of all sub-tickets. On drift, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build parks the sub-ticket with that error as the reason. The human amends the spec (`factory spec amend`, Spec store below), rules, or both; `resolve --ruling` returns the sub-ticket to its implementer, and the ruling on file stops the check from repeating.
+
 **Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
@@ -91,7 +93,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | `tasks.md` | The sub-tickets and coverage map | Planner, or the harness when it skips the planner |
 | `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |
 
-`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. Triage receives the capability index: one line per current-truth capability, with its size, the absolute path of its spec and its requirement names. Triage names the capabilities the request touches on its `Capabilities:` line. The spec writer and the critic receive those capabilities in full, plus each one whose `specs/<name>/spec.md` path the spec they work from cites, and the capability index for the rest (routing table). They and the planner receive the whole decision log, `decisions.md`, when it holds any text, whatever capabilities the ticket names: a standing decision often names no capability, yet every ticket must follow it. A ticket whose latest triage output has no `Capabilities:` line gets every current-truth spec in full.
+`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. After the gate, only `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged` changes the pinned version. A human runs it on a parent ticket whose spec is approved and not yet archived, when another ticket's merge or a checker's finding shows the approved spec is wrong; no workflow script or role prompt names it. It refuses while any run is in flight on the ticket or its sub-tickets. `--intent unchanged` keeps the Problem section, every Decisions line, and each requirement's name, operation and statement, whitespace aside. Scenarios, their setup, Evidence, design text and Tests to change may change. The harness checks that claim against the approved version. It refuses a change of intent, and always refuses `--intent changed`, with a restart note: the merged sub-tickets, which a restart keeps; the unmerged ones, which it discards; and the two ways to restart, re-spec and re-plan through the spec gate, or close and re-file. It also refuses a version that fails the gate's own checks. The amended version becomes the approved one, so every later role run receives it. The re-pin rewrites the change folder as the gate does, but keeps the planner's `tasks.md`, and archive writes the amended scenarios. Each sub-ticket not merged or closed moves to the new version and keeps the version its plan was made from, so an amendment supersedes no plan. The amendment is recorded in `approvals/<ticket id>/amendment-<n>.md`, with the reason, each scenario changed, added or removed, each sub-ticket merged before it, and the diff, and logged as `spec.amended`. It changes no ticket state; the human resumes the ticket by the usual routes. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. Triage receives the capability index: one line per current-truth capability, with its size, the absolute path of its spec and its requirement names. Triage names the capabilities the request touches on its `Capabilities:` line. The spec writer and the critic receive those capabilities in full, plus each one whose `specs/<name>/spec.md` path the spec they work from cites, and the capability index for the rest (routing table). They and the planner receive the whole decision log, `decisions.md`, when it holds any text, whatever capabilities the ticket names: a standing decision often names no capability, yet every ticket must follow it. A ticket whose latest triage output has no `Capabilities:` line gets every current-truth spec in full.
 
 **Routing table.** The dispatcher (piece 2) is this table and nothing else. Each row: a STATUS a role emits, what runs next, and what it receives. "Receives" adds to the INPUT the role prompt already declares. Both follow the role-context block (above).
 
@@ -110,7 +112,7 @@ Rules the table relies on:
   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent. A new plan made from a later approved version supersedes the earlier plan's sub-tickets that have not merged: they keep their records and ids, are no longer dispatched, and neither park the parent nor hold back its close. Merged ones stay merged and count toward the close.
   - An archive refused for no change folder or no spec store parks the parent the same way, but its spec never entered the spec store: the human closes the parent as applied. Current truth is not updated, and archive appends nothing to `decisions.md`; the human logs any decision with `factory decision add`. If current truth should carry the spec, it is re-intaken as a new ticket.
   - A reviewer ESCALATE returns to its checks with the ruling in both checkers' input, same round. Its results that did not pass are set aside, so the reviewer runs again; a ruling that asks for a fix becomes the reviewer's REQUEST-CHANGES.
-  - A PR loop at max rounds or a SPEC-DEFECT returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
+  - A PR loop at max rounds or a SPEC-DEFECT returns to the implementer with the round reset and the human's ruling as findings, or the ticket closes. The human may amend the sub-ticket or the pinned spec (`factory spec amend`, intent unchanged) first; the amended version is what the implementer and checkers receive. There is no merge-gate override. A budget-killed run, or a ticket parked on a second EMPTY-OUTPUT, re-dispatches the same role on the same inputs, same round (the human may raise that run's budget or amend the sub-ticket first), or the ticket closes. In-flight siblings keep the spec version they received; the human decides whether to re-plan.
 
 | From | STATUS | Next | Receives |
 |---|---|---|---|
@@ -119,7 +121,7 @@ Rules the table relies on:
 | Triage | NEEDS-HUMAN | Human queue | The question |
 | Triage | CLARIFY | Requester, via piece 9; ticket parks until answered | The missing-info list |
 | Triage | REJECT | Closed | — |
-| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo, current truth and the decision log, as the Spec store paragraph describes, read-only; round 2+: prior findings, the writer's responses, previous spec version |
+| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo, current truth and the decision log, as the Spec store paragraph describes, read-only; every other approved change not yet archived, with its decisions; round 2+: prior findings, the writer's responses, previous spec version |
 | Spec writer | NEEDS-HUMAN | Human queue | Open questions |
 | Critic | APPROVE | Human spec gate | Spec + critic output |
 | Critic | REVISE | Spec writer (round +1) if round < {2}, else Human queue | Findings, the spec version they apply to |
