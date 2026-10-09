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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0371-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0371-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v3)

=== proposal.md
## Problem

When the factory builds two approved designs close together, the one that merges first can make the other's approved acceptance checks impossible to pass. The factory has no command to correct the approved design afterwards. It also has no check that catches the conflict before an agent has spent a build on it. The operator pays in blocked builds, hand-written instructions and repeated agent runs. On the Nanobot target, one ticket closed at 15.1M tokens across five build passes, mostly for this reason.

Some terms used below. The factory turns a request, called a ticket, into merged code through a chain of AI agents, called roles. The spec is the ticket's design. Its scenarios are the runnable checks the code must pass. The spec gate is the one human sign-off on a spec before code is written. At the gate the harness pins the spec: it freezes the approved version, and every later role reads that version. The store is the directory where the factory keeps tickets, spec versions and the records of agent runs. A pinned spec is also written out as the ticket's change folder in the store; a store set up without that layout has no spec store. The planner is the role that splits a ticket into sub-tickets, and it leaves its task list, `tasks.md`, in the change folder. Each sub-ticket is built by the implementer role on its own branch, checked by two checker roles, and merged on its own into the integration branch, the repository's main line. When every sub-ticket has merged and a final check passes, archive writes the change folder's scenarios into current truth. Current truth is the store's record of how the system behaves now; later specs are written against it. A run is in flight while a role is working on a ticket. A ticket is parked when the pipeline stops it and hands it to a human. An implementer that cannot go on parks its sub-ticket with the status BLOCKED. A ruling is a human's written instruction, filed with the ticket, that the harness hands to later role runs.

Three things are missing:

- **No way to amend.** Only the gate writes a spec version. A ruling can tell the builders to change a scenario's setup, so the build goes on, but archive still writes the unamended scenario into current truth, where it fails when anyone re-runs it. Nor does anything separate a correction (a scenario's setup, a precondition, a wording fix) from a change of what the ticket is for. A change of that kind, patched in under sub-tickets already merged for the old intent, would leave merged code that no longer matches its spec.
- **No check at the gate.** The critic is the role that grades a spec before the operator sees it. It is not asked whether a scenario depends on behaviour that another approved, unmerged ticket changes, and its input does not list those tickets.
- **No check at build start.** Between writing a spec and building a sub-ticket, other tickets merge. One may add a test that pins behaviour the spec changes. A sub-ticket's scenarios may also need a sibling sub-ticket that has not merged. Today the implementer or a checker finds out, after a run has been spent.

This ticket adds three things. The first is a human-only command that amends a pinned spec when the amendment keeps the spec's intent; it refuses a change of intent and says what a restart would keep and discard. The second is a drift check before a sub-ticket's first implementer run. The third is the critic's cross-ticket check, with the list of approved changes that check needs.

## Evidence

The incidents behind this ticket. Each is read in the store named. Nanobot is a second repository the factory works on, with its own store at `~/dev/nanobot-upstream/.factory/store`. Its tickets have their own numbers: Nanobot's T-0027 is not this ticket.

| Date | Where | What broke | What it cost |
|---|---|---|---|
| 2026-10-03 | this repo, T-0012 | A scenario could not pass as written: its whitespace check covered the store's own records. | The operator edited the pinned `specs/T-0012/v3.md` in place by hand. `.factory/store/approvals/T-0012/amendment-1.md` records "Applied in place to `specs/T-0012/v3.md` (the pinned version every checker reads)". No command made the edit. |
| 2026-10-04 | Nanobot, T-0008 (its spec 05, typing) | Nanobot T-0002 (its spec 20) merged first and made WhatsApp groups fail closed without a policy file. Two pinned scenarios of T-0008 create none, so they cannot pass. | Implementer BLOCKED (run-0166). Rulings in `approvals/T-0008.1/ruling-1.md` and `approvals/T-0008/ruling-1.md` say "Test setup only. No behaviour change, and no change to any THEN". Archive would still write the unamended scenarios. |
| 2026-10-07 | this repo, T-0032.1 | `tests/factory/test_gate_paths.py`, added by T-0028.1, asserted the opposite of the spec's part B.2. T-0032's spec was written 2026-10-04 23:23–23:57 (runs 0292 and 0294), T-0028.1 merged 2026-10-05 15:09, and T-0032 was approved 2026-10-07 05:21. | Implementer BLOCKED (run-0304), an operator ruling, one more implementer run and both checkers again. The test arrived after the spec was written but before it was pinned. |
| 2026-10-09 | Nanobot, T-0031 (its spec 34) | Three separate breaks. T-0031.4's acceptance named sibling T-0031.2 as "already merged", but T-0031.2 waited on Nanobot's T-0027 and had not merged. T-0031.2 broke 8 tests that Nanobot's T-0027 (its spec 22) added after T-0031's spec was written. T-0031.5 broke 1 test that its sibling T-0031.4 added, which checked the last lines of an output. | A verifier SPEC-DEFECT (run-0380) and a re-run of the checks; implementer BLOCKED twice (run-0391, run-0399), each with a ruling and another implementer run. The store records 13 implementer runs for 5 sub-tickets. Five of them are catch-up runs (`resolution: conflict` in their `meta.yaml`), made while Nanobot's T-0027 sub-tickets merged in between. The operator's change request gives 15.1M tokens for the ticket. I could not check that figure, which needs the workflow transcripts. |

Today's behaviour, on a scratch store and target (the GIVEN fixture of the first scenario below, run on an unmodified clone of `main` at `b002c95`):

- `bin/factory spec amend T-0001 --file x --reason r --intent unchanged` prints `factory spec: error: argument sub: invalid choice: 'amend' (choose from 'add', 'tasks')` and exits 2. No command writes a spec version after the gate.
- A later implementer run on T-0001.2 receives v1 (`amended=0 old=1 run_version=1`): only a ruling could tell it otherwise. Archive then writes v1's scenario into current truth (`hello=0 hi=1`). That is the harm the ruling workaround leaves behind.
- A sub-ticket whose acceptance names an unmerged sibling starts its implementer (`runs=1`). So does one whose spec names `src/greet.py` after a later commit changed that file and added `tests/test_greet.py`: the build runs the implementer instead of parking.
- A critic run's input lists no other approved change (`listed=0`), and its system prompt has no cross-ticket rule (`rule=0`).

How often a drift check would park, measured on both stores' history. For each sub-ticket with an implementer run, I took the integration-branch commit when its parent's approved version was added (from the store's log) as the start. The base of its first implementer run was the end. I applied part D's two rules to the commits between them. The "known incidents" are the BLOCKED and SPEC-DEFECT runs whose escalation names a test or scenario that another merge broke.

| Store | Sub-tickets | Test rule would park | Known incidents it catches | Sibling rule would park |
|---|---|---|---|---|
| this repo | 36 | 17 | 2 of 2 (T-0025.1, T-0032.1) | 2 |
| Nanobot | 43 | 29 | 7 of 8 (misses T-0022.1, whose breaking merge changed no file the spec names) | 5: T-0031.4, the real case; three T-0002 sub-tickets that did start too early, when their dependency records were empty (a bug since fixed); and T-0027.2 |

So the test rule catches nearly every known case, and it also parks about half the sub-tickets that had no problem. Decisions and Risk say what that costs.

The design already allows amending. `docs/design.md:110` says "the human amends the spec and re-plans". `docs/design.md:113` says "The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive." The build spec, `dev/build-harness.spec.md:315`, specifies a `resolve --amend-spec FILE` flag that was never built.

The operator approved parts A and B of issue #44 as one ticket (`.factory/answers/operator-decisions-2026-10-04.md`: "#44: approve parts A (spec amend, human-only, logged) and B (critic cross-ticket check) as one ticket, pre-approved"). On 2026-10-09 the operator sent the approved v2 back (`.factory/store/approvals/T-0027/changes-1.md`) to fold in issue #50, which asks `spec amend` to declare intent and refuse a change of intent, and to add the drift check.

I prototyped the change in a clone of `main` at `b002c95`: about 275 changed lines of harness code and prompt, plus stub documents. Every scenario below printed its THEN line there. On an unmodified clone, each scenario labelled NEW printed the failure given in verification.md. The full harness suite passed on both clones, `408 passed`. On the prototype, the three current-truth scenarios of the sibling-tests check (build-dispatch) printed the same lines as before.

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

## Responses

To the operator's change request of 2026-10-09 (`approvals/T-0027/changes-1.md`), on approved v2:
- 1, fold in issue #50 (amend declares intent) → FIXED. `--intent unchanged|changed` is required. `unchanged` is checked against the Problem, the Decisions and each requirement's statement. `changed`, or a failed check, is refused with a note on what is merged and what a restart discards, naming both restart paths. Issue #50's part B, a critic run on every amendment, is replaced by that mechanical check (Decisions). Its part C, the triggers and the amend-or-restart rule in the README, is in design part E. New scenario: "An amendment declared or found to change intent is refused, naming what a restart keeps and discards". v2's archive scenario no longer changes a Decisions line, which is now an intent change.
- 2, drift check at build start → FIXED, as design part D, with both kinds of drift the request names. One departure: drift is counted from when the approved version was written, not from when it was pinned, because T-0032.1's test arrived between the two (Evidence). The test rule is a heuristic. Its measured park rate is in Evidence and Risk, and I flag it under ESCALATIONS.
- 3, evidence → FIXED. The incidents table adds Nanobot T-0031 and this repo's T-0032.1, each checked in its store. The 15.1M-token figure is the operator's; I could not check it.
- 4, `Protected paths:` line → FIXED. Risk declares seven paths on the line the merge gate reads.
- 5, keep the critic's cross-ticket check → kept, as parts B and C. One change: the list leaves out a ticket sent back into the spec loop, as this ticket is now. Its old change folder still exists, but it is no longer an approved change. New scenario: "A change sent back to the spec writer leaves the critic's list".

## Out-of-scope observations

- After `request-changes`, the spec writer's input does not include the spec it wrote before. `compose.py` adds the previous version only when `round.spec >= 1`, and `request-changes` resets the round to 0. I read v2 from `specs/T-0027/v2.md` directly.
- In this repo's store, `openspec/changes/` still holds the folders of closed tickets T-0026 and T-0030. Part B skips closed tickets, so they do not reach the critic. Why they were not archived is not checked here.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

### Requirement: An implementer starts only when each sibling-added test it may change came from a merged sibling
`factory run start --role implementer` on a sub-ticket MUST refuse with exit 2, writing no run, worktree, branch or in-flight entry, with an error that starts `BLOCKED from harness: ` and names the file, when a line `` `<file>` (added by <ID>) `` inside its "Tests to change" field names a file that existed at the parent's base, or whose first adding commit on the integration branch since that base lies inside no merged sibling's recorded merge. It SHALL accept a file a merged sibling's merge added, and SHALL ignore such a line outside that field.

#### Scenario: A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0022-sib.sh <<'EOF'
# Sourced from the repo root with E set to a test file path. Builds a scratch store whose parent
# T-0001 is planned as ST-1 and ST-2: ST-2 depends on ST-1 and lists `$E` under Tests to change as
# added by ST-1. Builds a scratch target whose main holds tests/test_old.py from before the plan,
# tests/test_interim.py from ST-1's recorded merge, and tests/test_operator.py from a later direct
# commit that is no sibling's merge. ST-2's Scope line mentions tests/test_old.py in the same form.
# T-0001.1 is merged; T-0001.2 is ready for its implementer.
T22=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T22/store FACTORY_REPO=$T22/t FACTORY_INTEGRATION_BRANCH=main
printf '# Fixture\n\nThe bot should do the thing.\n' > $T22/req.md && printf '## Problem\nx\n' > $T22/spec.md
bin/factory ticket new --file $T22/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T22/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T22/t && mkdir $T22/t/tests && echo 'def test_old(): pass' > $T22/t/tests/test_old.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm base && A=$(git -C $T22/t rev-parse HEAD)
git -C $T22/t checkout -qb sib && echo 'def test_interim(): pass' > $T22/t/tests/test_interim.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm interim && git -C $T22/t checkout -q main
git -C $T22/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' sib && B=$(git -C $T22/t rev-parse HEAD)
echo 'def test_operator(): pass' > $T22/t/tests/test_operator.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm operator
printf 'ST-1 / Interim\nDepends on: none\nParallel-safe: yes\nInterim tests: `tests/test_interim.py`, broken by ST-2\n\nST-2 / Final\nDepends on: ST-1\nParallel-safe: yes\nScope: B, which reads `tests/test_old.py` (added by the base commit)\nTests to change:\n- `%s` (added by ST-1): ST-2 replaces the interim behaviour\nProtected paths: none\n' "$E" > $T22/plan.md
bin/factory subticket add T-0001 --file $T22/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$B'" >/dev/null
bin/factory ticket set T-0001 "parent_base='$A'" >/dev/null
bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0022-build.mjs <<'EOF'
// node t0022-build.mjs, from the checkout under test after sourcing t0022-sib.sh: runs
// factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE. Each clerk command runs
// for real (sh -c, from this checkout, environment unchanged); each role run returns an empty
// output, which the workflow records as a killed run. Prints each park, as `park <id>: <reason>`.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p') runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `exit=0 ready-for-implementer runs=1`

#### Scenario: A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(for E in tests/test_old.py tests/test_operator.py tests/test_never.py; do (. ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >$T22/o 2>/dev/null; x=$?; J=$(tail -1 $T22/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: ') names=$(echo "$J" | grep -cF "$E") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) branch=$(git -C $FACTORY_REPO branch --list 'factory/T-0001.2' | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints three lines, each exactly `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`

### Requirement: The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it
When an implementer's run start is refused with an error that starts `BLOCKED `, the build workflow SHALL park the sub-ticket with that error, verbatim, as the reason, so that `factory resolve <id> --ruling F` MUST accept the park and return the sub-ticket to `ready-for-implementer`.

#### Scenario: The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(E=tests/test_old.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(BLOCKED from harness:\).*/\1/'; printf 'Ruling: x\n' > $T22/r.md; bin/factory resolve T-0001.2 --ruling $T22/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')")`
- THEN it prints exactly `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`

### Requirement: The build asks the whole-spec step before it runs the planner
At `ready-for-planner`, `factory/workflows/build.js` MUST first run `plan whole-spec`. On `"planner": "skipped"` it SHALL move the parent to `planned` and build the sub-ticket with no planner run. On any other success it SHALL run the planner as before. On a refusal it MUST park the parent with `harness-bug: plan whole-spec: <error>`.

#### Scenario: A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "skipped", "reason": "fixture", "subtickets": [{"id": "T-0001.1"}]}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": false, "error": "T-0001 has no approved spec"}, "exit": 2}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`, one per line

#### Scenario: A spec that needs the planner still gets a planner run
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "needed", "reason": "the spec writer marked it NEEDS-SPLIT"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "stub stop"}, "exit": 2}}')`
- THEN it prints exactly `start: planner`, then `park: harness-bug: subticket add: stub stop`

### Requirement: A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT
When a role run ends without an output file, or with a blank one, whatever the agent call returned, `run finish` MUST record it as `EMPTY-OUTPUT` and never as `KILLED`. The workflow MUST keep the agent's non-blank last message as that run's `last-message.md` and re-dispatch the same role once. A second `EMPTY-OUTPUT` in a row SHALL park the ticket as `EMPTY-OUTPUT from <role>`, with no result row for that run.

#### Scenario: A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0032-checks.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# whose branch factory/T-0001.1 holds one commit; T-0001.1 is at checks-in-flight on that head $H,
# with no result rows, so the build runs both checkers on it.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
git -C $T23/t checkout -qb factory/T-0001.1 && echo x > $T23/t/x.txt && git -C $T23/t add x.txt
git -C $T23/t -c user.email=f@x -c user.name=f commit -qm work && git -C $T23/t checkout -q main
H=$(git -C $T23/t rev-parse factory/T-0001.1)
bin/factory ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0032-build.mjs <<'EOF'
// node t0032-build.mjs '<plays JSON>', from the checkout under test after sourcing t0023-parent.sh
// and t0032-checks.sh: runs factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE.
// Each clerk command runs for real (sh -c, from this checkout, environment unchanged). Each role
// run plays the next entry of its role's list in <plays> (the last one repeats):
//   {"say": "<text>"}     returns <text> (or null) as its final message and writes no output file;
//   {"write": "<STATUS>"} writes an output with the run's head as its Commit: line (and, for the
//                         verifier, "Gate suite: PASS") and that STATUS, and returns the same text.
// Prints each park, as `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const plays = JSON.parse(process.argv[2]), n = {}
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const list = plays[r[2]] || [{ say: '' }]
  n[r[2]] = (n[r[2]] || 0) + 1
  const p = list[Math.min(n[r[2]], list.length) - 1]
  if ('say' in p) return p.say
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = `Commit: ${head}\n` + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') + `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(M="Both suite runs are still in progress; I'll write the review once the monitor reports their final lines."; . ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs "{\"reviewer\": [{\"say\": \"$M\"}], \"verifier\": [{\"write\": \"VERIFIED\"}]}"; for r in reviewer verifier; do echo "$r: $(for d in $(ls -d $FACTORY_STATE/runs/*-$r); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')"; done; echo "kept=$(find $FACTORY_STATE/runs -path '*-reviewer/last-message.md' -exec grep -lxF "$M" {} + | grep -c .) $(bin/factory results show T-0001.1 | tail -1 | grep -o '"rows": {[^}]*}')")`
- THEN it prints exactly `park T-0001.1: EMPTY-OUTPUT from reviewer`, then `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` (two reviewer runs, both empty), then `verifier: VERIFIED `, then `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` (both last messages kept verbatim, apostrophe included; no reviewer row, so a `--redispatch` re-runs only the reviewer)

#### Scenario: One empty reviewer run followed by a real one routes on the real one
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once. The first reviewer call returns `null`; the verifier's SPEC-DEFECT gives the join a fixed stop.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"say": null}, {"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: EMPTY-OUTPUT APPROVE `

#### Scenario: An implementer that returns nothing twice parks as EMPTY-OUTPUT
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once. In that fixture every role run returns an empty string.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs; echo "implementer: $(for d in $(ls -d $FACTORY_STATE/runs/*-implementer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.2: EMPTY-OUTPUT from implementer`, then `implementer: EMPTY-OUTPUT EMPTY-OUTPUT `

#### Scenario: An intake role's second empty output in a row parks as EMPTY-OUTPUT
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once. The stub store answers every `run finish` with `EMPTY-OUTPUT`.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "run_id": "run-0009-x", "status": "EMPTY-OUTPUT", "escalations": []}}}')`
- THEN it prints exactly `start: triage`, then `start: triage`, then `park: EMPTY-OUTPUT from triage`

### Requirement: A role run that writes its output runs once and routes on its STATUS
A role run whose output file holds a STATUS MUST NOT be re-dispatched, and the build SHALL route on that STATUS as before.

#### Scenario: A reviewer that writes its output runs once
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: APPROVE `

### Requirement: The build counts only the current plan's sub-tickets
The build MUST NOT park a parent for a superseded sub-ticket the human closed, and SHALL dispatch the current plan's ready sub-tickets. A closed sub-ticket of the current plan MUST still park the parent with `sub-ticket closed by a human: <id>`.

#### Scenario: The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored", "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. In `t0022-build.mjs` every role run returns an empty string, so the implementer of the dispatched sub-ticket ends EMPTY-OUTPUT twice.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001.4: EMPTY-OUTPUT from implementer`

#### Scenario: A sub-ticket of the current plan that a human closed still parks the parent
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" and "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001: sub-ticket closed by a human: T-0001.2`

### Requirement: A parent's final check and close count only the current plan's sub-tickets
`factory ticket parent-check` SHALL move a planned parent to `ready-for-parent-verify` when every current sub-ticket has merged, and `ticket transition <parent> --to closed` MUST accept a VERIFIED final check whatever its superseded sub-tickets' states.

#### Scenario: With the new plan merged, the re-planned parent reaches its final check and closes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null; echo "check: $(bin/factory ticket parent-check T-0001 | tail -1 | grep -o '"state": "[^"]*"')"; R=$(bin/factory run start --role verifier --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); if [ -n "$R" ]; then H=$(sed -n "s/^head: '*\([0-9a-f]*\).*/\1/p" $FACTORY_STATE/runs/$R/meta.yaml); printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $FACTORY_STATE/runs/$R/output.md; bin/factory run finish $R >/dev/null 2>&1; fi; bin/factory ticket transition T-0001 --to closed --by t >/dev/null 2>&1; echo "close=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `check: "state": "ready-for-parent-verify"`, then `close=0 closed`

### Requirement: The build parks a merge the gate blocked, with the gate's reason
When `factory merge` is refused with an error that starts `BLOCKED `, `factory/workflows/build.js` MUST park the sub-ticket with that error, verbatim, as the reason, and SHALL NOT record it as a harness bug.

#### Scenario: The build parks a merge refused for protected paths with the gate's reason
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED on the current head"}}, "merge": {"out": {"ok": false, "error": "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"}, "exit": 2}}')`
- THEN it prints exactly `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`

## Current truth: gate-commands

# gate-commands

## Requirements

### Requirement: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them
Each `gate_commands` entry SHALL be a command string or a mapping of `command` and an optional `paths` list of git pathspecs. When a reviewer or verifier run starts on a sub-ticket, the harness MUST mark SKIPPED, with its reason, each command whose paths the diff from base to head touches none of. It MUST list that command apart from the commands to run, and record it in the run's `meta.yaml`. A command with no `paths` SHALL always be listed to run.

#### Scenario: A gate command scoped to paths is skipped for a diff that touches none of them
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0028-sub.sh <<'EOF'
# Sourced from the repo root, with $1 the file the sub-ticket's one commit changes (docs/b.md or
# src/a.txt) and $2 `scoped` or `plain`. Builds a scratch instance and target. `scoped` gives the
# gate the unscoped command `git diff --check main...HEAD` and the command `sh -c 'exit 7'` scoped
# to `src/`; `plain` keeps the fixture's one unscoped command. Sub-ticket T-0001.1 reaches
# checks-in-flight with that commit as its head; a verifier run is started and composed on it.
# Leaves $B (the CLI), $T, $I (the implementer run), $R and $V (the verifier run and its
# directory), $H (the head) and $COMPOSE (that compose's exit code).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^gate_commands:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
if [ "$2" = scoped ]; then
  printf '%s\n' 'gate_commands:' '  - "git diff --check main...HEAD"' "  - {command: \"sh -c 'exit 7'\", paths: [\"src/\"]}" >> $T/inst/instance.yaml
else
  printf '%s\n' 'gate_commands: ["git diff --check main...HEAD"]' >> $T/inst/instance.yaml
fi
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/src $T/t/docs && echo a > $T/t/src/a.txt && echo b > $T/t/docs/b.md
git -C $T/t add -A && git -C $T/t commit -q -m init
printf '# F\n\nDo x.\n' > $T/req.md && printf '## Problem\nx\n' > $T/spec.md
$B ticket new --file $T/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
$B spec add T-0001 --file $T/spec.md >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
I=$($B run start --role implementer --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
echo more >> $T/store/worktrees/T-0001.1/$1 && git -C $T/store/worktrees/T-0001.1 commit -q -am change
$B run finish $I --status-override READY-FOR-REVIEW >/dev/null && $B ticket head T-0001.1 >/dev/null
$B ticket transition T-0001.1 --to checks-in-flight --by t --round pr:init >/dev/null
R=$($B run start --role verifier --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); V=$T/store/runs/$R
H=$(git -C $T/t rev-parse factory/T-0001.1)
$B run compose $R >/dev/null 2>&1; COMPOSE=$?
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -vc 'exit 7') skipped=$(grep '^SKIPPED' $V/input.md 2>/dev/null | grep -F 'exit 7' | grep -c 'src/') meta=$(grep -c 'exit 7' $V/meta.yaml | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `compose=0 run=1 skipped=1 meta=1`

#### Scenario: A diff that touches a scoped command's paths runs that command
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh src/a.txt scoped && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -cF 'exit 7') skipped=$(grep -c '^SKIPPED' $V/input.md 2>/dev/null)")`
- THEN it prints exactly `compose=0 run=1 skipped=0`

#### Scenario: A gate command with no paths runs on every diff, as today
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && echo "compose=$COMPOSE run=$(grep -F 'Gate commands' $V/input.md | grep -cF 'git diff --check main...HEAD') skipped=$(grep -c '^SKIPPED' $V/input.md)")`
- THEN it prints exactly `compose=0 run=1 skipped=0`

### Requirement: A skipped command is recorded on the gate result, and the merge still needs that result to pass
When a verifier's result is recorded, the `ci` row MUST list each command that verifier run skipped, with status SKIPPED and its reason. `factory merge` SHALL still refuse unless that row is PASS.

#### Scenario: A skipped gate command is recorded on the gate result, and the merge still needs a passing gate
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && for g in FAIL PASS; do printf 'Commit: %s\nGate suite: %s\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' $H $g > $T/v.md; printf 'Commit: %s\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' $H > $T/r.md; $B results record T-0001.1 --head $H --role verifier --output $T/v.md --run $R >/dev/null; $B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0003-reviewer >/dev/null; $B merge T-0001.1 >/dev/null 2>&1; m=$?; C=$T/store/results/$H/ci.yaml; echo "$g: merge=$m recorded=$(grep -q 'exit 7' $C && grep -q SKIPPED $C && echo yes || echo no)"; done)`
- THEN it prints exactly `FAIL: merge=2 recorded=yes`, then `PASS: merge=0 recorded=yes`

### Requirement: The implementer is given every gate command
The implementer's input SHALL list every gate command to run, scoped or not, and no SKIPPED line.

#### Scenario: The implementer is still given every gate command
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md scoped && $B run compose $I >/dev/null 2>&1; echo "compose=$? both=$(grep -F 'Gate commands' $T/store/runs/$I/input.md 2>/dev/null | grep -F 'git diff --check main...HEAD' | grep -cF 'exit 7') skipped=$(grep -c '^SKIPPED' $T/store/runs/$I/input.md 2>/dev/null)")`
- THEN it prints exactly `compose=0 both=1 skipped=0`

### Requirement: A malformed gate entry refuses every build role's run start
A `gate_commands` entry MUST make `run start` refuse with exit 2 for the implementer, reviewer or verifier, naming `gate_commands` and creating no run, when it is anything other than one of these: a string; or a mapping with a non-empty string `command`, an optional non-empty list of non-empty strings `paths`, and no other key.

#### Scenario: A malformed gate entry refuses a checker's run start and creates no run
Needs the GIVEN block of "A gate command scoped to paths is skipped for a diff that touches none of them" run once.
- WHEN `(for bad in '{command: "true", path: ["src/"]}' '{command: "true", paths: "src/"}'; do (. ${TMPDIR:-/tmp}/t0028-sub.sh docs/b.md plain && grep -v '^gate_commands:' $T/inst/instance.yaml > $T/i.yaml && echo "gate_commands: [$bad]" >> $T/i.yaml && mv $T/i.yaml $T/inst/instance.yaml && n=$(ls $T/store/runs | wc -l) && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T/err; echo "exit=$? new_runs=$(( $(ls $T/store/runs | wc -l) - n )) named=$(grep -c 'gate_commands' $T/err)"); done)`
- THEN it prints exactly `exit=2 new_runs=0 named=1`, twice

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location. The change MUST add no whitespace errors.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The build spec calls the store branch factory-store
- WHEN `(Q=$(printf '\140'); echo "old_name=$(grep -c "${Q}tickets${Q}\|refs/heads/tickets\|HEAD:tickets" dev/build-harness.spec.md) new_name=$(grep -c 'factory-store' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints `old_name=0 new_name=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The planner labels checks per sub-ticket and may list tests an earlier sibling added
Every copy of the planner prompt (the `docs/design.md` §4 block, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`) SHALL tell the planner to label each check against the sub-ticket's own base, to name interim tests, and to list a sibling-added test as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``; it MUST no longer say to label checks "the same way", and the design block and its `docs/prompts/` copy SHALL stay byte-identical.

#### Scenario: Every planner copy labels per sub-ticket and lists sibling tests
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-planner.txt; sed -n '/^## 4\. Planner/,/^## 5\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/04-planner.md factory/prompts/planner.md; do echo "own=$(grep -c "against this sub-ticket's own base" $f) sibling=$(grep -cF '(added by <sibling ID>)' $f) interim=$(grep -c '^  Interim tests: ' $f) copied=$(grep -c 'labelled NEW or REGRESSION the same way' $f)"; done; cmp -s $X docs/prompts/04-planner.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `own=1 sibling=1 interim=1 copied=0`, then `verbatim`

### Requirement: The spec writer lists the tests a decision overturns, and the critic checks for one left off
Every copy of the spec writer prompt SHALL carry the RULES bullet that starts `- Tests a decision overturns: `, and every copy of the critic prompt SHALL say under rubric 1 that a test pinning the old behaviour and `missing from "Tests to change" is a finding`.

#### Scenario: Every spec writer and critic copy carries the decision-overturns rule
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-sw.txt; for h in '2\. Spec writer' '3\. Spec critic'; do sed -n "/^## $h/,/^## [0-9]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: writer=$(grep -c '^- Tests a decision overturns: ' $X) critic=$(grep -c 'from "Tests to change" is a finding' $X)"; echo "docs/prompts: writer=$(grep -c '^- Tests a decision overturns: ' docs/prompts/02-spec-writer.md) critic=$(grep -c 'from "Tests to change" is a finding' docs/prompts/03-spec-critic.md)"; echo "factory/prompts: writer=$(grep -c '^- Tests a decision overturns: ' factory/prompts/spec_writer.md) critic=$(grep -c 'from "Tests to change" is a finding' factory/prompts/critic.md)")`
- THEN it prints exactly `design: writer=1 critic=1`, then `docs/prompts: writer=1 critic=1`, then `factory/prompts: writer=1 critic=1`

### Requirement: The preamble and the code reviewer accept a checked sibling entry
Every copy of the preamble SHALL allow an existing test listed `in your sub-ticket as added by an earlier sibling`, and every copy of the code reviewer prompt SHALL not block a test `the sub-ticket lists it there as added by an earlier sibling`.

#### Scenario: Every preamble and reviewer copy accepts a sibling entry
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-pr.txt; for h in 'Shared preamble' '6\. Code reviewer'; do sed -n "/^## $h/,/^## [0-9A-Z]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $X) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' $X)"; echo "docs/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' docs/prompts/00-preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' docs/prompts/06-code-reviewer.md)"; echo "factory/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' factory/prompts/preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' factory/prompts/reviewer.md)")`
- THEN it prints exactly `design: guard=1 review=1`, then `docs/prompts: guard=1 review=1`, then `factory/prompts: guard=1 review=1`

### Requirement: Role runs receive the new rules
The system prompt that `run start` writes for a planner, spec writer and critic run SHALL contain that role's new rule and the new preamble sentence.

#### Scenario: Planner, spec writer and critic runs get the new rules in their system prompts
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2 3; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-planner >/dev/null; bin/factory ticket set T-0002 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0003 status=ready-for-critic >/dev/null; for p in planner:T-0001 spec_writer:T-0002 critic:T-0003; do bin/factory run start --role ${p%%:*} --ticket ${p##*:} >/dev/null 2>&1; done; P=$(ls $FACTORY_STATE/runs/*-planner/system-prompt.txt); W=$(ls $FACTORY_STATE/runs/*-spec_writer/system-prompt.txt); C=$(ls $FACTORY_STATE/runs/*-critic/system-prompt.txt); echo "planner own=$(grep -c "against this sub-ticket's own base" $P) sibling=$(grep -cF '(added by <sibling ID>)' $P) guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $P) writer=$(grep -c '^- Tests a decision overturns: ' $W) critic=$(grep -c 'from "Tests to change" is a finding' $C)")`
- THEN it prints exactly `planner own=1 sibling=1 guard=1 writer=1 critic=1`

### Requirement: The documents record the sibling-tests check
`docs/design.md` SHALL describe the check in a paragraph that starts `**Tests a sibling added.**`, in piece 8 and in the spec approval gate row, and SHALL no longer call the gate's list the only authorization to alter an existing test; `dev/build-harness.spec.md` SHALL name the `BLOCKED from harness` refusal; `docs/changelog.md` SHALL gain an entry for issue #40 and stay numbered without a gap; `README.md` SHALL describe the check and the new `--ruling` case; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec describe the check
- WHEN `(echo "piece8=$(grep '^| 8 |' docs/design.md | grep -c 'added by that sibling') gate=$(grep '^| Spec approval |' docs/design.md | grep -c 'a test an earlier sibling added') stale=$(grep -c 'which is the only authorization to alter an existing test' docs/design.md) check=$(grep -c '^\*\*Tests a sibling added\.\*\*.*BLOCKED from harness:' docs/design.md) build=$(grep -c 'BLOCKED from harness' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `piece8=1 gate=1 stale=0 check=1 build=1`

#### Scenario: The changelog records issue 40's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #40 ' docs/changelog.md | grep -oF -e 'own base' -e 'added by' -e 'BLOCKED from harness' -e 'Decision' -e 'critic rubric 1' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the sibling tests check and its ruling
- WHEN `(echo "built=$(grep -c '^- \*\*Sibling tests check\.\*\*' README.md) ruling=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'a test no merged sibling added')")`
- THEN it prints exactly `built=1 ruling=1`

#### Scenario: The sibling-tests change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the declared-path rule
The "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md` SHALL carry the declared-path rule and stay verbatim copies of `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. The run copies under `factory/prompts/` SHALL differ from those files only by the fills they had on `main`. The code reviewer and preamble copies MUST NOT change. `docs/changelog.md` SHALL gain one entry for issue #49, numbered without a gap, and the change MUST add no whitespace errors.

#### Scenario: The design blocks and their copies carry the rule and stay in step
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) rule=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -c 'A protected path the sub-ticket declares is not an escalation') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`. `copy=SAME`: the design block equals its `docs/prompts/` file. `rule=1`: that file carries the rule. `fill=unchanged`: the run copy under `factory/prompts/` differs from the documented copy only where it did on `main`.

#### Scenario: The code reviewer and preamble copies do not change
- WHEN `(echo "changed=$(git diff --name-only main...HEAD -- factory/prompts/reviewer.md factory/prompts/preamble.md docs/prompts/06-code-reviewer.md docs/prompts/00-preamble.md | grep -c .)")`
- THEN it prints exactly `changed=0`

#### Scenario: The changelog records the declared-path rule in a contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The declared-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the small-change lane
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap. `docs/design.md`, `dev/build-harness.spec.md` and `README.md` SHALL describe the whole-spec sub-ticket and gate-command paths. No prompt copy SHALL change, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the small-change lane as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc, build spec and README describe both skips, and no prompt copy changes
- WHEN `(echo "design=$(grep -c 'whole-spec' docs/design.md | awk '{print ($1 > 0)}') gate=$(grep '^| 11 | Gate runner' docs/design.md | grep -c 'SKIPPED') build=$(grep -c 'plan whole-spec' dev/build-harness.spec.md | awk '{print ($1 > 0)}') readme=$(grep -c 'plan whole-spec' README.md | awk '{print ($1 > 0)}') skipped=$(grep -c 'SKIPPED' README.md | awk '{print ($1 > 0)}') stale=$(grep -c 'The build workflow runs the planner, which' README.md) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -c .)")`
- THEN it prints exactly `design=1 gate=1 build=1 readme=1 skipped=1 stale=0 prompts=0`

#### Scenario: The small-change lane adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: Every role is told to wait for its own commands
Every copy of the shared preamble SHALL carry the bullet that starts `- Run every command in the foreground and wait for it to finish.` and says `Never end your turn while a command you started is still running`. The design block and both files MUST stay byte-identical, and every role run's system prompt SHALL carry the bullet.

#### Scenario: Every preamble copy carries the wait rule and the copies stay identical
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-pre.txt; sed -n '/^## Shared preamble/,/^## [0-9]/p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/00-preamble.md factory/prompts/preamble.md; do echo "fg=$(grep -c '^- Run every command in the foreground and wait for it to finish\.$' $f) end=$(tr '\n' ' ' < $f | tr -s ' ' | grep -c 'Never end your turn while a command you started is still running')"; done; cmp -s $X docs/prompts/00-preamble.md && cmp -s docs/prompts/00-preamble.md factory/prompts/preamble.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `fg=1 end=1`, then `verbatim`

#### Scenario: Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer reviewer verifier; do P=$(prompt $r); echo "$r fg=$(echo "$P" | grep -c 'Never end your turn while a command you started is still running') judge=$(echo "$P" | grep -c 'Do not run the test suite or the gate commands')"; done)`
- THEN it prints exactly `implementer fg=1 judge=0`, `reviewer fg=1 judge=1`, `verifier fg=1 judge=0`, one per line

### Requirement: The code reviewer judges the diff and leaves the suite and the gate to the verifier
Every copy of the code reviewer prompt SHALL say `Do not run the test suite or the gate commands: the verifier runs them on the same head`, and SHALL allow a narrow command that confirms a specific finding. No existing line of that prompt MAY be removed, and the verifier prompt MUST NOT change. The reviewer's composed input MUST NOT list the gate commands, while the implementer's and the verifier's inputs still SHALL.

#### Scenario: Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "judge=$(echo "$J" | grep -c 'Do not run the test suite or the gate commands: the verifier runs them on the same head') narrow=$(echo "$J" | grep -c 'You may run a narrow command to confirm a specific finding')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed) removed=$(git diff main...HEAD -- docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md | grep -v '^---' | grep -c '^-') verifier_changed=$(git diff --name-only main...HEAD -- docs/prompts/07-verifier.md factory/prompts/verifier.md | grep -c .)")`
- THEN it prints three lines, each exactly `judge=1 narrow=1`, then `copy=SAME fill=unchanged removed=0 verifier_changed=0`

#### Scenario: The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && for r in reviewer verifier implementer; do [ $r = implementer ] && bin/factory ticket set T-0001.1 status=ready-for-implementer 'in_flight=[]' >/dev/null; R=$(bin/factory run start --role $r --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); bin/factory run compose ${R:-none} >/dev/null 2>&1; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "$r gates=$(grep -c 'Gate commands (run each from your worktree' $I 2>/dev/null) told=$(grep -c 'The verifier runs the gate commands on this head; you do not run them' $I 2>/dev/null)"; done)`
- THEN it prints exactly `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0`, one per line

### Requirement: The documents record the empty-output route
`docs/design.md` SHALL state the EMPTY-OUTPUT rule and its two routing-table rows, and SHALL list a second EMPTY-OUTPUT among the park reasons. `dev/build-harness.spec.md` SHALL describe EMPTY-OUTPUT and `run last-message`, and SHALL no longer describe a KILLED condition or seam. `README.md` SHALL no longer say that a run is parked for exceeding a budget, and SHALL describe the empty-output retry. `docs/changelog.md` SHALL gain an entry for issue #41, numbered without a gap. The change MUST add no whitespace errors.

#### Scenario: The design doc states the EMPTY-OUTPUT rule, its rows and its park
- WHEN `(echo "rule=$(grep -c '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md) rows=$(grep -c '^| Any role | EMPTY-OUTPUT' docs/design.md) parks=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -c 'a second EMPTY-OUTPUT in a row') kill=$(grep -c 'never recorded as a budget kill' docs/design.md)")`
- THEN it prints exactly `rule=1 rows=2 parks=1 kill=1`

#### Scenario: The build spec describes EMPTY-OUTPUT and no longer a KILLED condition
- WHEN `(echo "stale=$(grep -c 'KILLED condition\|KILLED seam' dev/build-harness.spec.md) empty=$(grep -c 'EMPTY-OUTPUT' dev/build-harness.spec.md | awk '{print ($1 > 0)}') note=$(grep -c 'run last-message' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `stale=0 empty=1 note=1`

#### Scenario: README drops the budget park and describes the empty-output retry
- WHEN `(echo "budget=$(grep -c 'exceeding its budget\|over budget' README.md) built=$(grep -c '^- \*\*Empty output\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'ended without output twice')")`
- THEN it prints exactly `budget=0 built=1 unstick=1`

#### Scenario: The changelog records issue 41 without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #41 ' docs/changelog.md | grep -oF -e EMPTY-OUTPUT -e foreground -e 'last message' -e 're-dispatched once' -e 'gate commands' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The empty-output change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The spec writer and the critic carry the turn-economy rules
Every copy of the spec writer prompt SHALL tell it to batch independent reads and commands, read line ranges once grep has found them, keep long output in a scratch file, and write the spec in as few writes as it can. Every copy of the critic prompt SHALL carry the same reading rules, its minimum spot-check, a rule that it runs no test suite, the rule for picking an acceptance command, a sentence allowing a small experiment in its scratch directory to confirm a finding, and the rule that turns a claim needing a suite run or a build of the change into a finding or a question; it MUST NOT cap a claim at a number of paths and commands or forbid a clone, worktree or prototype. Each design block MUST stay byte-identical to its `docs/prompts/` copy, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); printf '%s\n' 'Put independent reads and commands in one turn' 'read that line range, not the whole file' 'to a file in your scratch directory and grep or tail it' > $T/both; { cat $T/both; echo 'Write the spec in as few writes as you can'; } > $T/spec_writer; { cat $T/both; printf '%s\n' 'Spot-check at least 2 cited paths and 1 acceptance command yourself' 'Run no test suite' 'Pick an acceptance command that runs no test suite' 'small experiment in your scratch directory' 'is a finding for the writer, or a question'; } > $T/critic; printf '%s\n' 'Ground any one claim' 'build nothing' 'no clone, worktree or prototype' > $T/gone; for r in "2. Spec writer|02-spec-writer.md|spec_writer" "3. Spec critic|03-spec-critic.md|critic"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) gone=$(for g in docs/prompts/$c factory/prompts/$f.md; do tr '\n' ' ' < $g | tr -s ' ' | grep -oF -f $T/gone; done | grep -c .) fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged`, then `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged`. `doc` and `run` count the kept or added phrases found in the documented copy and the run copy, each joined into one line so a phrase may wrap; `gone` counts the removed phrases found in either.

### Requirement: Spec writer and critic runs receive the turn-economy rules
The system prompt that `run start` writes for a spec writer run SHALL contain the writer's turn-economy rule. The one it writes for a critic run SHALL contain the critic's reading rules, its no-suite rule and the sentence allowing a small scratch experiment, and MUST NOT contain the per-claim cap or the no-build rule.

#### Scenario: A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0002 status=ready-for-critic >/dev/null; bin/factory run start --role spec_writer --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role critic --ticket T-0002 >/dev/null 2>&1; W=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0001-spec_writer/system-prompt.txt | tr -s ' '); C=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0002-critic/system-prompt.txt | tr -s ' '); echo "spec_writer batch=$(printf "%s" "$W" | grep -c 'Put independent reads and commands in one turn') writes=$(printf "%s" "$W" | grep -c 'Write the spec in as few writes as you can')"; echo "critic batch=$(printf "%s" "$C" | grep -c 'Put independent reads and commands in one turn') suite=$(printf "%s" "$C" | grep -c 'Run no test suite') scratch=$(printf "%s" "$C" | grep -c 'small experiment in your scratch directory') cap=$(printf "%s" "$C" | grep -c 'Ground any one claim') build=$(printf "%s" "$C" | grep -c 'build nothing')")`
- THEN it prints exactly `spec_writer batch=1 writes=1`, then `critic batch=1 suite=1 scratch=1 cap=0 build=0`

### Requirement: Nothing else in the two prompts changes
The spec writer prompt copies SHALL stay as #73 left them at `05cf8f9`. In the critic prompt copies, everything before the PROCESS section and everything from ANTI-GOODHARTING on SHALL stay byte for byte as on `main`. No other file under `docs/prompts/`, `factory/prompts/` or `agents/` SHALL change.

#### Scenario: The writer prompt is as #73 left it, and only the critic's PROCESS changes
- WHEN `(T=$(mktemp -d); n=0; for x in "docs/prompts/03-spec-critic.md|1,/^PROCESS\$/p" "docs/prompts/03-spec-critic.md|/^ANTI-GOODHARTING/,\$p" "factory/prompts/critic.md|1,/^PROCESS\$/p" "factory/prompts/critic.md|/^ANTI-GOODHARTING/,\$p"; do f=${x%%|*}; s=${x#*|}; git show main:$f | sed -n "$s" > $T/a; sed -n "$s" $f > $T/b; [ -s $T/a ] || n=$((n+100)); cmp -s $T/a $T/b || { n=$((n+1)); echo "changed: $f $s"; }; done; echo "sections_changed=$n writer=$(git diff --name-only 05cf8f9 HEAD -- docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md | grep -c .) others=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -vxF -e docs/prompts/03-spec-critic.md -e factory/prompts/critic.md | grep -c .)")`
- THEN it prints only `sections_changed=0 writer=0 others=0`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL hold one entry for issue #73, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's no-suite rule among its mechanisms, SHALL no longer say the critic builds nothing, and SHALL say part B.2 is done by #41 for the code reviewer and by #73 for the critic.

#### Scenario: Principle 2 names the critic's no-suite rule and no longer its build ban
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "entries73=$(grep -c '^[0-9]*\. After issue #73 ' docs/changelog.md) implemented=$(printf '%s' "$P" | grep -c 'runs no test suite (#73') builds=$(printf '%s' "$P" | grep -c 'builds nothing') status=$(printf '%s' "$P" | grep -c 'done by #41 for the code reviewer and by #73 for the critic')")`
- THEN it prints exactly `CONTIGUOUS`, then `entries73=1 implemented=1 builds=0 status=1`

### Requirement: The documents record the critic revert
`docs/changelog.md` SHALL gain one entry for issue #74 as its last numbered entry, numbered without a gap, that records the replay result and the two removed rules. The Spiking section of `docs/principles.md` SHALL no longer bound the critic to two paths and one command or say it does not build, SHALL say the critic may run a small scratch check, SHALL say vetting a whole approach belongs to the spec writer or a spike, and SHALL record the replay. The change MUST add no whitespace errors.

#### Scenario: The changelog records the revert as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#74' -e replay -e 'per-claim cap' -e 'no-build rule' -e 'no test suite' -e UV_PYTHON_INSTALL_DIR -e brace-list | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `7`

#### Scenario: The Spiking section allows a small scratch check and records the replay
- WHEN `(X=$(sed -n '/^## Spiking/,$p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "bound=$(printf '%s' "$X" | grep -c 'two paths, one command') nobuild=$(printf '%s' "$X" | grep -c 'it does not build') scratch=$(printf '%s' "$X" | grep -c 'small scratch check') whole=$(printf '%s' "$X" | grep -c 'vetting a whole approach belongs to the spec writer') replay=$(printf '%s' "$X" | grep -c 'replay')")`
- THEN it prints exactly `bound=0 nobuild=0 scratch=1 whole=1 replay=1`

#### Scenario: The critic revert adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the capability index
The triage prompt's design block, its `docs/prompts/` copy and the runtime prompt SHALL each carry the `Capabilities:` output line. `docs/design.md`, `dev/build-harness.spec.md` and the README's Triage, Spec writer and Spec critic rows MUST describe the capability index. `docs/changelog.md` MUST have an entry for issue #75, with no whitespace error in the change.

#### Scenario: The prompt copies, design, build spec, README and changelog name the capability index
- WHEN `(echo "docs-copy=$(grep -c '^Capabilities:' docs/prompts/01-triage.md) runtime=$(grep -c '^Capabilities:' factory/prompts/triage.md) changelog=$(grep -c '^[0-9]*\. After issue #75 ' docs/changelog.md) design=$(grep -q 'capability index' docs/design.md && echo y || echo n) build-spec=$(grep -q 'capability index' dev/build-harness.spec.md && echo y || echo n) readme=$(grep -E '^\| (Triage|Spec writer|Spec critic) \(' README.md | grep -c 'capability index')"; git diff --check main...HEAD && echo whitespace=ok)`
- THEN it prints exactly `docs-copy=1 runtime=1 changelog=1 design=y build-spec=y readme=3`, then `whitespace=ok`

### Requirement: The documents describe the whole decision log for the spec writer, critic and planner
`docs/design.md` and the README's Spec writer, Spec critic and Planner rows MUST say that those roles receive the whole decision log, and neither MUST mention a decision index. `docs/changelog.md` SHALL have an entry for issue #78, with no whitespace error in the change.

#### Scenario: The design, README and changelog describe the whole decision log and no decision index
- WHEN `(echo "design-index=$(grep -c 'decision index' docs/design.md) design-whole=$(grep -c 'They and the planner receive the whole decision log' docs/design.md) readme-index=$(grep -c 'decision index' README.md) readme-whole=$(grep -E '^\| (Spec writer|Spec critic|Planner) \(' README.md | grep -c 'the whole decision log') changelog=$(grep -c '^[0-9]*\. After issue #78 ' docs/changelog.md)"; git diff --check main...HEAD && echo whitespace=ok)`
- THEN it prints exactly `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`, then `whitespace=ok`

### Requirement: The documents record superseded plans
`docs/design.md` SHALL say, in its rule for a sub-ticket closed by the human, that a new plan from a later approved version supersedes the earlier plan's unmerged sub-tickets. `dev/build-harness.spec.md` SHALL describe the `superseded` list of `ready-implementers`. `README.md` SHALL carry a "Re-plan after a re-spec" bullet. `docs/changelog.md` SHALL hold one entry for issue #77, numbered without a gap. The change MUST NOT touch any prompt copy, workflow script or agent template, and MUST add no whitespace errors.

#### Scenario: The design doc, build spec, README and changelog record superseded plans
- WHEN `(echo "design=$(grep 'sub-ticket closed by the human' docs/design.md | grep -c supersede) build-spec=$(grep 'ready-implementers PARENT' dev/build-harness.spec.md | grep -c superseded) readme=$(grep -c '^- \*\*Re-plan after a re-spec\.\*\*' README.md) changelog=$(grep '^[0-9]*\. After issue #77 ' docs/changelog.md | grep -oF -e superseded -e planned_from -e 'Depends on' | sort -u | grep -c .) $(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)")`
- THEN it prints exactly `design=1 build-spec=1 readme=1 changelog=3 CONTIGUOUS`

#### Scenario: The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors
- WHEN `(echo "whitespace=$(git diff --check main...HEAD >/dev/null && echo ok || echo bad) untouched=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts factory/workflows agents | grep -c .)")`
- THEN it prints exactly `whitespace=ok untouched=0`

### Requirement: The prompts tell the reviewer what the gate checks and the spec writer how to declare
Every copy of the code reviewer prompt (the `docs/design.md` §6 block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`) SHALL carry check 6's new last sentence and MUST NOT say `will require a human approval`. Every copy of the spec writer prompt SHALL give the `Protected paths:` line under Risk and the rule of one path or glob per entry with no brace lists. Each design block and its `docs/prompts/` file MUST stay byte-identical, and each `factory/prompts/` copy SHALL differ from its `docs/prompts/` file only where it did on `main`.

#### Scenario: Every reviewer prompt copy states what the merge gate checks
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "gate=$(echo "$J" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval, and refuses and parks one it does not declare") promise=$(echo "$J" | grep -c 'will require a human approval')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `gate=1 promise=0`, then `copy=SAME fill=unchanged`

#### Scenario: Every spec writer prompt copy gives the declaration line
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-sw.txt; T=$(mktemp -d); sed -n '/^## 2\. Spec writer/,/^## 3\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; do echo "reads=$(grep -c 'declared on one line the merge gate reads:$' $f) form=$(grep -c '^ *Protected paths: none | .<path or glob>., .<path or glob>.$' $f) braces=$(grep -c '^ *one path or glob per entry, no brace lists$' $f)"; done; git show main:factory/prompts/spec_writer.md > $T/a; git show main:docs/prompts/02-spec-writer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/02-spec-writer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `reads=1 form=1 braces=1`, then `copy=SAME fill=unchanged`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `dev/build-harness.spec.md` SHALL describe the same rule; `docs/changelog.md` SHALL gain an entry for issue #57 and stay numbered without a gap; `README.md` SHALL describe the check and `--accept-paths`; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec drop the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') piece9=$(grep -c 'review protected PRs' docs/design.md) gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md) build=$(grep -c 'protected path pyproject.toml needs human approval on H' dev/build-harness.spec.md) build_new=$(grep '^25\. ' dev/build-harness.spec.md | grep -c 'not declared')")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

#### Scenario: The protected-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose current sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; a sub-ticket that a later plan superseded SHALL NOT count, and with any current sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

#### Scenario: A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null && bin/factory ticket set T-0001 status=ready-for-parent-verify >/dev/null && bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null && echo 'Re-plan: one more fix.' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=0 ready-for-planner`

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

### Requirement: Accepting the refused paths returns the sub-ticket to its checks, which then merge
`factory resolve <id> --accept-paths F`, on a park whose reason starts `BLOCKED from merge gate:`, MUST write F as the ticket's next ruling, add the head's undeclared protected paths to the ticket's `accepted_paths`, keep every result row, and return the ticket to `checks-in-flight`; `factory merge` SHALL then merge it. On any other park it MUST refuse with exit 2, writing nothing, with an error containing `--accept-paths applies to`.

#### Scenario: Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The scenario parks the sub-ticket with the gate's own error, as the build does.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: core/b.py is part of the approved design.\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>&1; echo "accept=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') rows=$(ls $FACTORY_STATE/results/$H | grep -c yaml) ruling=$(cmp -s $T/ru.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo kept || echo missing)"; $B merge T-0001.1 >/dev/null 2>&1; echo "merge=$? on_main=$(git -C $T/t diff --name-only $M main | grep -c 'core/b\.py')")`
- THEN it prints exactly `accept=0 checks-in-flight rows=3 ruling=kept`, then `merge=0 on_main=1`

#### Scenario: Accepting paths is refused on any other park and writes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: x\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>$T/err; echo "accept=$? refused=$(grep -c 'accept-paths applies to' $T/err) $($B ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)")`
- THEN it prints exactly `accept=2 refused=1 parked rulings=0`

### Requirement: A ruling on a merge gate's refusal sends the sub-ticket back to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts `BLOCKED from merge gate:` SHALL return the sub-ticket to `ready-for-implementer` at the same round, and the next implementer input SHALL contain F.

#### Scenario: A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: take core/b.py out of this change.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "ruling=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') reason=$(echo "$E" | grep -c '^BLOCKED from merge gate: ')"; R=$($B run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take core/b.py out of this change.')")`
- THEN it prints exactly `ruling=0 ready-for-implementer reason=1`, then `in_input=1`

### Requirement: A ruling on a reviewer's escalation returns the sub-ticket to its checks
`factory resolve <id> --ruling F` on a park whose reason starts `ESCALATE from reviewer` MUST write F as the ticket's next ruling and return the ticket to `checks-in-flight` at the same round. It MUST set aside the head's rows that did not pass, by the rule `--redispatch` uses, and the next reviewer input SHALL contain F.

#### Scenario: A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'docs/d.md' && printf "Commit: $H\nSTATUS: ESCALATE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/e.md && $B results record T-0001.1 --head $H --role reviewer --output $T/e.md --run run-0003-reviewer >/dev/null && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: the escalation is settled.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')"; R=$($B run start --role reviewer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: the escalation is settled.')")`
- THEN it prints exactly `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` (the reviewer's ESCALATE row set aside, the passing verifier and gate rows kept), then `in_input=1`

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

## Current truth: merge-gate

# merge-gate

## Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`

### Requirement: The merge gate refuses a changed protected path the pinned spec does not declare
`factory merge` MUST refuse with exit 2, merging nothing and changing no ticket field, when a path in `git diff --name-only --no-renames <integration>...<head>` matches an in-repo `protected_paths` glob and is neither declared on a `Protected paths:` line of the Risk section of the pinned spec nor in the ticket's `accepted_paths`. Its error SHALL start `BLOCKED from merge gate: ` and name each such path and no declared one. A declaration in another ticket's spec, or a Risk line in any other form, SHALL declare nothing.

#### Scenario: An undeclared protected path is refused at merge, by name, and nothing merges
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0033-gate.sh <<'EOF'
# Sourced from the repo root, with $1 the line T-0001's approved spec carries in its Risk section
# (each ^ in it stands for a backtick) and $2 the changes the sub-ticket's one commit makes,
# space-separated: `p` appends to file p (creating it), `p-` deletes p, `p>q` renames p to q.
# Builds a scratch instance whose protected paths are `core/**`, `bin/tool` and `~/.secret/**`,
# and a target whose main holds core/a.py, core/b.py, bin/tool and docs/d.md. T-0002's approved
# spec declares `core/b.py`. T-0001 is planned as T-0001.1, whose branch factory/T-0001.1 holds
# that one commit, head $H, with reviewer APPROVE, verifier VERIFIED and gate PASS recorded on $H;
# T-0001.1 is at checks-in-flight. Leaves $B, $T, $H and $M (main's tip).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^protected_paths:\|^  infra:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
printf '%s\n' 'protected_paths:' '  harness: ["core/**", "bin/tool"]' '  credentials: ["~/.secret/**"]' >> $T/inst/instance.yaml
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/core $T/t/bin $T/t/docs && for f in core/a.py core/b.py bin/tool docs/d.md; do echo x > $T/t/$f; done
git -C $T/t add -A && git -C $T/t commit -q -m init
for id in T-0001 T-0002; do
  [ $id = T-0001 ] && L=$(printf '%s' "$1" | tr '^' '\140') || L='Protected paths: `core/b.py`'
  printf "# F $id\n\nDo x.\n" > $T/req.md
  printf '=== proposal.md\n## Problem\nx\n## Risk\nBlast radius: small.\n%s\n=== design.md\n## Proposed change\nA. x\n' "$L" > $T/spec.md
  $B ticket new --file $T/req.md >/dev/null
  $B ticket transition $id --to ready-for-spec-writer --by t >/dev/null && $B spec add $id --file $T/spec.md >/dev/null
  $B ticket transition $id --to ready-for-critic --by t --round spec:init >/dev/null
  $B ticket transition $id --to awaiting-spec-gate --by t >/dev/null && $B approve-spec $id >/dev/null
done
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
$B ticket transition T-0001 --to planned --by t >/dev/null
git -C $T/t checkout -q -b factory/T-0001.1
for f in $(echo "$2"); do
  case $f in
    *'>'*) mkdir -p $T/t/$(dirname ${f#*>}) && git -C $T/t mv ${f%%>*} ${f#*>} ;;
    *-) git -C $T/t rm -q ${f%-} ;;
    *) mkdir -p $T/t/$(dirname $f) && echo y >> $T/t/$f && git -C $T/t add $f ;;
  esac
done
git -C $T/t commit -q -m work && H=$(git -C $T/t rev-parse HEAD) && git -C $T/t checkout -q main && M=$(git -C $T/t rev-parse main)
$B ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/r.md
$B results record T-0001.1 --head $H --role verifier --output $T/v.md --run run-0001-verifier >/dev/null
$B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py bin/tool docs/d.md' && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; J=$(tail -1 $T/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from merge gate: ') named=$(echo "$J" | grep -o 'core/b\.py\|bin/tool' | sort -u | grep -c .) declared=$(echo "$J" | grep -c 'core/a\.py\|docs/d\.md') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved) $($B ticket show T-0001.1 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight`. `named=2`: the error names both undeclared protected paths. `declared=0`: it names neither the declared protected path nor the unprotected one.

#### Scenario: Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The three cases: T-0001 declares nothing while T-0002 declares `core/b.py`; the sub-ticket renames `core/b.py` out of the protected tree; T-0001's only mention of `core/b.py` is a line `Not touched: ` followed by it.
- WHEN `(for c in 'Protected paths: none|core/b.py' 'Protected paths: none|core/b.py>docs/b.py' 'Not touched: ^core/b.py^|core/b.py'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; echo "exit=$x named=$(tail -1 $T/o | grep -c 'core/b\.py') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved)"); done)`
- THEN it prints three lines, each exactly `exit=2 named=1 main=unchanged`

### Requirement: A declared or unprotected path merges with no further approval
`factory merge` SHALL merge, as before, a sub-ticket whose changed protected paths are all declared on its pinned spec's `Protected paths:` line, by exact path or glob, and one that changes no protected path.

#### Scenario: A declared protected path, or an unprotected one, merges with no further approval
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(for c in 'Protected paths: ^core/**^, ^bin/tool^|core/a.py core/new/c.py bin/tool' 'Protected paths: none|docs/d.md docs/e.md'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `exit=0 merged`, twice

## Current truth: role-escalations

# role-escalations

## Requirements

### Requirement: The implementer and verifier leave declared protected paths out of ESCALATIONS
The system prompt of every implementer and verifier run SHALL say that a protected path the sub-ticket declares is not an escalation, that the code reviewer lists declared paths once for each head it reviews, that the role may name them but not under ESCALATIONS, and that a protected path the sub-ticket does not declare still goes under ESCALATIONS.

#### Scenario: Implementer and verifier run prompts carry the declared-path rule
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0029-prompt.sh <<'EOF'
# Sourced from the repo root of the checkout under test. Defines `prompt <role>`: starts one run of
# that role (implementer, reviewer or verifier) on a scratch target with a throwaway store, and
# prints the run's system prompt on one line, runs of spaces squeezed.
T29=$(cd "$(mktemp -d)" && pwd -P); B29=$PWD/bin/factory
git init -q -b main $T29/tgt && git -C $T29/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
(cd $T29/tgt && $B29 init --repo-name demo >/dev/null 2>&1)
printf '# F\n\nDo x.\n' > $T29/req.md
(cd $T29/tgt && FACTORY_STATE=$T29/s $B29 ticket new --file $T29/req.md >/dev/null)
prompt() (
  cd $T29/tgt && export FACTORY_STATE=$T29/s
  case $1 in
    implementer) $B29 ticket set T-0001 status=ready-for-implementer 'in_flight=[]' >/dev/null ;;
    *) $B29 ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git rev-parse HEAD) >/dev/null ;;
  esac
  R=$($B29 run start --role $1 --ticket T-0001 --model opus 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
  tr '\n' ' ' < $T29/s/runs/${R:-none}/system-prompt.txt 2>/dev/null | tr -s ' '
)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer verifier; do P=$(prompt $r); echo "$r declared=$(echo "$P" | grep -c 'A protected path the sub-ticket declares is not an escalation') notunder=$(echo "$P" | grep -c 'but not under ESCALATIONS') undeclared=$(echo "$P" | grep -c 'still goes under ESCALATIONS when the sub-ticket does not declare it')"; done)`
- THEN it prints exactly `implementer declared=1 notunder=1 undeclared=1`, then `verifier declared=1 notunder=1 undeclared=1`

### Requirement: Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
The system prompts of implementer, code reviewer and verifier runs MUST still carry the preamble's rule to escalate a protected path that the approved spec's Risk section does not declare. The code reviewer's prompt MUST still carry check 6's rule to ESCALATE a path the sub-ticket does not declare and to list a declared one under ESCALATIONS. Check 6 SHALL say that the merge gate merges a path the approved spec's Risk section declares with no further approval, and SHALL NOT promise a human approval at merge.

#### Scenario: All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
- THEN it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line

#### Scenario: The reviewer run prompt says what the merge gate checks
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P=$(prompt reviewer); echo "gate=$(echo "$P" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval") promise=$(echo "$P" | grep -c 'will require a human approval')")`
- THEN it prints exactly `gate=1 promise=0`

## Current truth: role-inputs

# role-inputs

## Requirements

### Requirement: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest
When a ticket's latest finished triage output has a `Capabilities:` line, the spec writer and critic inputs SHALL hold in full only the current-truth capabilities that line names or the spec they work from cites by its `specs/<name>/spec.md` path. They MUST hold, for every other capability, one index line with its absolute spec path and its requirement names, under an instruction that citing a capability's path sends it in full to the critic. The planner SHALL receive no current truth.

#### Scenario: A ticket naming one capability composes inputs with only that capability in full and an index line for each other one
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0036-store.sh <<'EOF'
# Sourced from the repo root, with $1 the Capabilities line that T-0001's triage output carries
# (empty for none). Builds a throwaway store holding three capabilities, alpha, beta and gamma,
# each with one requirement whose text carries a marker (ALPHA-BODY, BETA-BODY, GAMMA-BODY), and a
# decision log of four lines: OWN-LINE logged against T-0001, BETA-LINE and GAMMA-LINE naming those
# capabilities, OTHER-LINE logged against T-0009 and naming none. T-0001's triage run ends ACCEPT
# with that line. Its spec writer run is composed; the spec it returns changes beta and cites
# `openspec/specs/gamma/spec.md` under Evidence. A critic run is composed on that spec; the spec is
# approved and a planner run is composed. Leaves $S (the store) and the input.md of each run:
# $I (triage), $W (spec writer), $C (critic), $P (planner).
T=$(cd "$(mktemp -d)" && pwd -P); S=$T/store
export FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance FACTORY_STATE=$S FACTORY_REPO=$PWD
start() { bin/factory run start --role $1 --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/'; }
finish() { printf '%s\nSTATUS: %s\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' "$2" "$3" > $T/out.md; bin/factory run finish $1 --output-file $T/out.md >/dev/null; }
printf '# Fixture\n\nMake beta stricter.\n' > $T/req.md
bin/factory ticket new --file $T/req.md >/dev/null && bin/factory init >/dev/null
for c in alpha beta gamma; do U=$(echo $c | tr a-z A-Z); mkdir -p $S/openspec/specs/$c
  printf '# %s\n\n## Requirements\n\n### Requirement: The %s part works\n%s-BODY The %s part SHALL work.\n' $c $c $U $c > $S/openspec/specs/$c/spec.md; done
printf '%s\n' "2026-10-01 T-0001 OWN-LINE decided for this ticket." "2026-10-02 T-0007 BETA-LINE beta keeps its default." \
  "2026-10-03 T-0008 GAMMA-LINE gamma stays read-only." "2026-10-04 T-0009 OTHER-LINE logs rotate weekly." > $S/decisions.md
R=$(start triage); bin/factory run compose $R >/dev/null; I=$S/runs/$R/input.md
finish $R "$(printf 'Type: feature\nTitle: Fixture\nSummary: Make beta stricter.\n%s' "$1")" ACCEPT
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
R=$(start spec_writer); bin/factory run compose $R >/dev/null; W=$S/runs/$R/input.md
finish $R "$(printf '%s\n' '=== proposal.md' '## Problem' 'Beta is lax.' '## Evidence' 'Read `openspec/specs/gamma/spec.md`.' \
  '## Decisions' 'none' '## Risk' 'none' '=== design.md' '## Proposed change' 'A. Tighten beta.' '=== specs/beta/spec.md' \
  '## MODIFIED Requirements' '### Requirement: The beta part works' 'The beta part SHALL work strictly.' '#### Scenario: strict' \
  '- WHEN `true`' '- THEN it exits 0' '=== verification.md' '## Acceptance' '- strict → NEW; today lax')" READY-FOR-CRITIC
bin/factory spec add T-0001 --from-run $R >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
R=$(start critic); bin/factory run compose $R >/dev/null; C=$S/runs/$R/input.md
finish $R "Findings: none." APPROVE
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null && bin/factory approve-spec T-0001 >/dev/null
R=$(start planner); bin/factory run compose $R >/dev/null; P=$S/runs/$R/input.md
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; for v in W C P; do eval f=\$$v; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) alpha-index=$(y alpha) gamma-index=$(y gamma) cites=$(grep -cF 'sends that capability in full to the critic' $f)"; done)`
- THEN it prints exactly `W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1`, then `C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0`. The writer gets beta, which triage named. The critic also gets gamma, whose path the spec cites. A capability's index line holds both its spec's absolute path and its requirement name. The writer's and critic's capability index carries its instruction paragraph once; the planner has no capability index.

### Requirement: A ticket whose triage output names no capabilities receives today's inputs
When a ticket's latest finished triage output has no `Capabilities:` line, the spec writer and critic SHALL receive every current-truth capability in full, and all three roles SHALL receive the whole decision log, as before this change.

#### Scenario: Without a Capabilities line every capability and every decision reach the writer, critic and planner
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh ''; for v in W C P; do eval f=\$$v; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) own=$(grep -c OWN-LINE $f) beta-line=$(grep -c BETA-LINE $f) gamma-line=$(grep -c GAMMA-LINE $f) other=$(grep -c OTHER-LINE $f)"; done)`
- THEN it prints exactly `W: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1`, then `C: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1`, then `P: alpha=0 beta=0 gamma=0 own=1 beta-line=1 gamma-line=1 other=1`

#### Scenario: The harness suite passes with the new inputs
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory >/dev/null 2>&1; echo "suite=$?")`
- THEN it prints exactly `suite=0`

### Requirement: Triage receives the capability index and is asked to name the capabilities a request touches
A triage run's input SHALL hold one capability index line per current-truth capability, with its absolute spec path and its requirement names, and no capability body or decision. Its system prompt MUST ask for a `Capabilities:` output line.

#### Scenario: A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; f=$I; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; echo "triage: alpha-index=$(y alpha) beta-index=$(y beta) gamma-index=$(y gamma) bodies=$(grep -c -- '-BODY' $f) decisions=$(grep -c -- '-LINE' $f) asks=$(grep -c '^Capabilities:' $(dirname $f)/system-prompt.txt)")`
- THEN it prints exactly `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0 asks=1`

### Requirement: The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names
Whenever `decisions.md` holds any text, the spec writer, critic and planner inputs SHALL hold it whole, under the heading `## Decision log (decisions.md): standing decisions, read-only`, and SHALL list it in `input_sources`, whether or not the ticket's latest finished triage output has a `Capabilities:` line; they MUST hold no decision index. Triage MUST still receive no decision line, and the capabilities each role receives in full, with the capability index, MUST stay as they are.

#### Scenario: With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; for v in W C P; do eval f=\$$v; echo "$v: own=$(grep -c OWN-LINE $f) beta-line=$(grep -c BETA-LINE $f) gamma-line=$(grep -c GAMMA-LINE $f) other=$(grep -c OTHER-LINE $f) whole=$(grep -cxF '## Decision log (decisions.md): standing decisions, read-only' $f) index=$(grep -c '^## Decision index' $f) grep-cmd=$(grep -cF "grep ' <ticket id> '" $f) note-decisions=$(grep -cF 'and the decisions that name it' $f) source=$(grep -cx -- '- decisions.md' $(dirname $f)/meta.yaml)"; done)`
- THEN it prints exactly `W: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1`, then the same with `C:`, then the same with `P:`. OTHER-LINE, logged against another ticket and naming no capability, reaches all three roles. No role gets a decision index or its `grep` instruction, and the capability index note no longer speaks of decisions.

#### Scenario: The capabilities each role receives and triage's input are unchanged by the whole log
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; for v in W C P; do eval f=\$$v; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) alpha-index=$(y alpha) gamma-index=$(y gamma) cites=$(grep -cF 'sends that capability in full to the critic' $f)"; done; f=$I; echo "triage: alpha-index=$(y alpha) beta-index=$(y beta) gamma-index=$(y gamma) bodies=$(grep -c -- '-BODY' $f) decisions=$(grep -c -- '-LINE' $f)")`
- THEN it prints exactly `W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1`, then `C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0`, then `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0`

#### Scenario: The harness suite passes with the whole decision log
Run with TMPDIR unset or outside any `.factory/` instance: some suite tests need a directory outside every instance.
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory >/dev/null 2>&1; echo "suite=$?")`
- THEN it prints exactly `suite=0`

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on exactly one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses when more than one remote carries the store branch
`factory init` MUST refuse with exit 2, creating no store and no local branch, when the own store is missing, no local `factory-store` exists and more than one remote carries it; the refusal MUST name each `<remote>/factory-store`.

#### Scenario: init on a clone with two remotes carrying the store branch refuses and names both
- GIVEN the three fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

```sh
cat > ${TMPDIR:-/tmp}/t0025-old.sh <<'EOF'
# Sourced from the repo root: a target whose store is a plain directory tracked on main, as both
# instances keep it today. Leaves the shell in the target; PRE is the commit that last tracked it.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
mkdir -p .factory/state && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
git add -A && git commit -q -m "instance, with its store on main" && PRE=$(git rev-parse HEAD)
EOF
cat > ${TMPDIR:-/tmp}/t0025-b1.sh <<'EOF'
# Sourced from the repo root: a target whose store at .factory/state is already a git worktree of
# an unborn factory-store branch, built with git alone (so it is the same layout whatever the
# harness does), then given an instance by init. Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
git worktree add -q --orphan -b factory-store .factory/state && echo /.factory/state/ >> "$(git rev-parse --git-path info/exclude)"
$B init --repo-name demo >/dev/null 2>&1
EOF
cat > ${TMPDIR:-/tmp}/t0025-gate.sh <<'EOF'
# Sourced from the repo root: a target made by init, its instance committed on main, and T-0001 on
# branch factory/T-0001 with reviewer APPROVE, verifier VERIFIED and gate PASS on its head H.
# Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance
git checkout -q -b factory/T-0001 && echo x > x.txt && git add x.txt && git commit -q -m work
H=$(git rev-parse HEAD) && git checkout -q main
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
$B ticket set T-0001 status=checks-in-flight branch=factory/T-0001 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/rv.md
$B results record T-0001 --head $H --role verifier --output $T25/v.md --run run-0001-verifier >/dev/null
$B results record T-0001 --head $H --role reviewer --output $T25/rv.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
- THEN it prints `exit=2 store=none local_branch=0 names=1,1`

### Requirement: init refuses to run from inside the store checkout
`factory init`, run with `FACTORY_INSTANCE` unset from a directory whose git top level is a checkout of `factory-store`, or is the store of the instance found from that directory or a checkout of the same repository inside that store, MUST refuse with exit 2 and write nothing, whichever commit the store has checked out, so that it never creates an instance inside the live store; other commands run from there SHALL still find the live instance, and `init` in a separate repository under the store SHALL still create that repository's instance.

#### Scenario: init from a scratch directory inside the store checkout refuses and leaves the store unchanged
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init from the store checkout on a detached HEAD refuses
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init in a separate repository under a run's scratch directory still creates its instance
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 instance=written live=ready-for-triage`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH, and verify the copy before removing anything;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

### Requirement: A spec that needs one sub-ticket becomes that sub-ticket without a planner run
`factory plan whole-spec <parent>`, on a parent at `ready-for-planner` with an approved spec, MUST act when four conditions hold: the parent has no sub-ticket; it has no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a requirement line, naming seams. It MUST then create one sub-ticket `<parent>.1`, ready for its implementer, whose text names every scenario of the approved spec. It MUST log `plan.skipped` with the reason, and report `"planner": "skipped"`. Otherwise it SHALL report `"planner": "needed"` with the reason and write nothing.

#### Scenario: A spec that needs one sub-ticket becomes that sub-ticket without a planner run
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0028-plan.sh <<'EOF'
# Sourced from the repo root, with $1 the STATUS a spec writer run ends with (READY-FOR-CRITIC or
# NEEDS-SPLIT) and $2 one more line for the spec's design part (empty for none). Builds a scratch
# store whose T-0001 has one spec writer run with that status. Its output, a spec with two labelled
# scenarios, becomes spec v1 and is approved, so T-0001 is ready-for-planner. Leaves $B and $T.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
export FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
W=$($B run start --role spec_writer --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
sed 's/^|//' > $T/store/runs/$W/output.md <<EOS
|=== proposal.md
|## Problem
|x
|=== design.md
|## Proposed change
|A. Do x.
|$2
|=== specs/demo/spec.md
|## ADDED Requirements
|### Requirement: X
|It SHALL do x.
|#### Scenario: First check
|- WHEN \`true\`
|- THEN it exits 0
|#### Scenario: Second check
|- WHEN \`true\`
|- THEN it exits 0
|=== verification.md
|## Acceptance
|- First check → NEW; fails today
|- Second check → REGRESSION
|STATUS: $1
|CONFIDENCE: high, fixture
|ESCALATIONS: none
EOS
$B run finish $W >/dev/null && $B spec add T-0001 --from-run $W >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? planner=$(tail -1 $T/o | sed -n 's/.*"planner": "\([a-z]*\)".*/\1/p') subs=$(ls $T/store/tickets | tr '\n' ' ')"; echo "state=$($B ticket show T-0001.1 2>/dev/null | sed -n 's/^status: //p') $($B ticket ready-implementers T-0001 2>/dev/null | tail -1 | grep -o '"ready": \[[^]]*\]') names=$(grep -cxF -e '- First check' -e '- Second check' $T/store/specs/T-0001.1/subticket.md 2>/dev/null) logged=$($B log tail --event plan.skipped --ticket T-0001 | grep -c .)")`
- THEN it prints exactly `exit=0 planner=skipped subs=T-0001.1.yaml T-0001.yaml `, then `state=ready-for-implementer "ready": ["T-0001.1"] names=2 logged=1`

#### Scenario: A spec the writer split, or a parent a planner already ran on, still goes to the planner and nothing is written
Needs the GIVEN block of "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" run once. The three cases are a NEEDS-SPLIT spec, a spec with a `### Size and seams` heading, and a parent with an earlier planner run.
- WHEN `(for c in 'NEEDS-SPLIT|' 'READY-FOR-CRITIC|### Size and seams' 'READY-FOR-CRITIC|planner-ran'; do (s=${c%%|*}; x=${c#*|}; [ "$x" = planner-ran ] && e='' || e=$x; . ${TMPDIR:-/tmp}/t0028-plan.sh $s "$e" && if [ "$x" = planner-ran ]; then P=$($B run start --role planner --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); $B run finish $P --status-override ESCALATE >/dev/null; fi; $B plan whole-spec T-0001 > $T/o 2>&1; echo "exit=$? planner=$(tail -1 $T/o | sed -n 's/.*"planner": "\([a-z]*\)".*/\1/p') subs=$(ls $T/store/tickets | tr '\n' ' ')logged=$($B log tail --event plan.skipped | grep -c .)"); done)`
- THEN it prints exactly `exit=0 planner=needed subs=T-0001.yaml logged=0`, three times

### Requirement: The whole-spec step refuses where a planner run would
`factory plan whole-spec` MUST refuse with exit 2, writing nothing, on a parent that is not at `ready-for-planner`, has a run in flight, or has no approved spec. A refusal for the wrong state SHALL name the state with `not ready-for-planner`.

#### Scenario: The whole-spec step refuses a parent that is not ready for its planner
Needs the GIVEN block of "A spec that needs one sub-ticket becomes that sub-ticket without a planner run" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0028-plan.sh READY-FOR-CRITIC '' && $B ticket transition T-0001 --to planned --by t >/dev/null && $B plan whole-spec T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -c 'not ready-for-planner' $T/err) subs=$(ls $T/store/tickets | tr '\n' ' ')")`
- THEN it prints exactly `exit=2 named=1 subs=T-0001.yaml `

### Requirement: A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets
A sub-ticket SHALL record the parent's approved version it was planned from, and that record MUST NOT follow later changes to its `spec` record. Once a parent has a sub-ticket planned from a later version, each of its sub-tickets that is not merged and was planned from an earlier version MUST be listed as superseded and left out of every other list `ticket ready-implementers` returns except `subtickets`. Its record SHALL be kept. `subticket add` SHALL report and log the sub-tickets it supersedes. A record with no plan version SHALL fall back to its `spec.approved_version`.

#### Scenario: After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0038-respec.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh. T-0001 was planned at approved spec v1 as
# T-0001.1 (merged), T-0001.2 (closed by a human with no commits) and T-0001.3 (waiting on
# T-0001.2, never started). The human parked the parent, sent it back to the spec gate and approved
# an edited spec, v2, so T-0001 is ready for its planner again, as Nanobot T-0024 was.
printf 'ST-1 / Base\nDepends on: none\nParallel-safe: yes\n\nST-2 / Dropped\nDepends on: none\nParallel-safe: yes\n\nST-3 / Unstarted\nDepends on: ST-2\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null
bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null
bin/factory ticket park T-0001 --reason "sub-ticket closed by a human: T-0001.2" >/dev/null
bin/factory resolve T-0001 --to spec-gate >/dev/null
printf '## Problem\nx, amended\n' > $T23/spec2.md
bin/factory approve-spec T-0001 --edit $T23/spec2.md >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && A=$(bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1) && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; R=$(bin/factory ticket ready-implementers T-0001 | tail -1); echo "add: $(echo "$A" | grep -o '"superseded": \[[^]]*\]')"; for k in ready closed superseded; do echo "$k: $(echo "$R" | grep -o "\"$k\": \[[^]]*\]")"; done; echo "kept=$(ls $FACTORY_STATE/tickets | tr '\n' ' ')logged=$(cat $FACTORY_STATE/log/*.jsonl | grep '"event": "subtickets.superseded"' | grep -c '"T-0001.2", "T-0001.3"')")`
- THEN it prints exactly `add: "superseded": ["T-0001.2", "T-0001.3"]`, `ready: "ready": ["T-0001.4"]`, `closed: "closed": []`, `superseded: "superseded": ["T-0001.2", "T-0001.3"]`, `kept=T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.4.yaml T-0001.yaml logged=1`, one per line

#### Scenario: The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. The first part moves T-0001.3's `spec` record to v2, as an amendment under approved T-0027 would. The second part clears `planned_from` on every record, as on a record made before this change.
- WHEN `( (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && bin/factory ticket set T-0001.3 spec.version=2 spec.approved_version=2 >/dev/null && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; echo "moved: $(bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"superseded": \[[^]]*\]')"); (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; for i in 1 2 3 4; do bin/factory ticket set T-0001.$i planned_from= >/dev/null 2>&1; done; echo "unrecorded: $(bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"superseded": \[[^]]*\]')"))`
- THEN it prints exactly `moved: "superseded": ["T-0001.2", "T-0001.3"]`, then `unrecorded: "superseded": ["T-0001.2", "T-0001.3"]`

#### Scenario: A second plan at the same approved version supersedes nothing
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && printf 'ST-1 / Extra\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null 2>&1; echo "exit=$?"; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]\|"remaining": \[[^]]*\]')`
- THEN it prints exactly `exit=0`, then `"ready": ["T-0001.2"]`, then `"remaining": ["T-0001.2", "T-0001.3"]`

### Requirement: A new plan may not depend on a sub-ticket it supersedes
`factory subticket add` MUST refuse with exit 2, writing no sub-ticket, a plan whose `Depends on:` line names a sub-ticket that the plan supersedes, and the refusal SHALL name that sub-ticket.

#### Scenario: A plan that depends on an old unmerged sub-ticket is refused and writes nothing
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.3\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>$T23/err; echo "exit=$? names=$(grep -c 'T-0001.3' $T23/err) $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints exactly `exit=2 names=1 T-0001.1.yaml T-0001.2.yaml T-0001.3.yaml T-0001.yaml `

### Requirement: The planner is told which sub-tickets its plan will supersede
When a plan made at the parent's approved version would supersede existing sub-tickets, the planner's input SHALL name them on one line after the existing sub-ticket list, and that list SHALL be unchanged.

#### Scenario: A re-specced parent's planner input names the sub-tickets its plan supersedes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "said=$(cat $I 2>/dev/null | grep -cxF 'Not merged and planned from an earlier approved version, so a new plan supersedes them and may not depend on them: T-0001.2, T-0001.3') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / Base: merged' -e '- T-0001.2 / Dropped: closed' -e '- T-0001.3 / Unstarted: waiting-dependencies')")`
- THEN it prints exactly `said=1 listed=3`

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
2026-10-04 T-0025 The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
2026-10-04 T-0025 A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
2026-10-04 T-0025 The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
2026-10-04 T-0025 `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
2026-10-04 T-0025 When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
2026-10-04 T-0025 With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
2026-10-04 T-0025 In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
2026-10-04 T-0025 The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
2026-10-04 T-0025 A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
2026-10-04 T-0025 `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
2026-10-04 T-0025 The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
2026-10-04 T-0025 An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.
2026-10-04 T-0022 A sub-ticket's "Tests to change" may list a test file that an earlier sibling of the same parent added, one line each: `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The harness reads only lines of that form inside the "Tests to change" field, and checks the file, not the test function. Rejected: checking test functions. The implementer rule puts new tests in new files, so a file is what a sibling adds, and git records files.
2026-10-04 T-0022 A listed file counts as added by a sibling when it is absent at the parent's `parent_base`, and the first commit since then on the integration branch that added it lies inside one merged sibling's recorded merge (reachable from its `main_after`, not from its `base_before`). Any merged sibling of the parent counts, including those from an earlier plan. The sibling ID on the line is for the reader and is not matched. Rejected: matching the named ID, because the planner's IDs (`ST-1`) differ from the store's (`T-0001.1`) and the operator's rule names no particular sibling.
2026-10-04 T-0022 The check runs in `run start` for every implementer run of a sub-ticket: first dispatch, fix rounds and catch-up runs. Every dispatch passes through that one place. Rejected: checking when the plan is added, when no sibling has merged yet. Rejected: checking at the merge gate, after the implementer has already edited the test. Rejected: checking where a waiting sub-ticket is released, which happens in two places and never for a sub-ticket with no dependencies.
2026-10-04 T-0022 A failed check refuses the run start with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness:` and names the file. The build workflow parks the sub-ticket with that error as the reason, so `resolve --ruling` handles it like an implementer's BLOCKED. That is what the operator's "parks for the operator, as today" describes. Rejected: a new kind of park with its own resolve verb. Rejected: having `run start` park the ticket itself, which would break the rule that a refusal writes nothing.
2026-10-04 T-0022 The preamble's guardrail sentence and the code reviewer's test-integrity check also accept a sibling entry that the harness has checked. Without them, the implementer and reviewer would still treat the edit as forbidden, and the park would remain.
2026-10-04 T-0022 The earlier sibling names the tests a later sibling will break under a new planner field, "Interim tests". The harness does not read it.
2026-10-04 T-0022 The critic's check for an omitted test goes under rubric 1 (Grounded), where the requester asked for it.
2026-10-04 T-0022 The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator compares side by side, is an Operator step, not an acceptance scenario. Running it needs the Nanobot store and real agents, which a verifier must not touch.
2026-10-04 T-0032 Empty role output (#41, T-0032): labelled EMPTY-OUTPUT with the last message, re-dispatched once automatically, parked on a second; the code reviewer judges the diff and leaves the test suite and gates to the verifier.
2026-10-04 T-0029 Only the code reviewer lists declared protected paths, once for each head it reviews. The implementer and verifier may name them in their output, but not under ESCALATIONS. This is a standing decision: a later prompt change should not give another role a declared-path notice. The operator pre-approved it on 2026-10-04 (`.factory/answers/operator-decisions-2026-10-04.md`), under the standing decision that removing clearly redundant work is allowed when every refusal still fires.
2026-10-04 T-0029 A fix round makes a new head, so it gets its own reviewer notice, as today. Rejected: one notice per sub-ticket. A fix round can change a declared path again, and the operator would not hear about it.
2026-10-04 T-0029 The new rule also keeps one escalation for a declared path: when the change does something to it that the spec does not describe. An undeclared path still escalates as well. Rejected: the retro's wording "the reviewer lists declared paths for the merge gate". No local merge check reads the declaration, so that sentence would teach the roles something false.
2026-10-04 T-0029 The implementer and verifier get the same bullet word for word, as the last bullet under RULES. That way one text is checked in both prompts.
2026-10-04 T-0029 The changelog records the count re-derived from the store log (10 runs, 30 of 205 items). Rejected: the retro's 26 of 139, which its own table contradicts with 38.
2026-10-04 T-0029 Acceptance checks the composed run prompts and the document copies. The request's own check (on the next build, one notice per head, from the reviewer) is kept as an operator step. Rejected: an acceptance item that waits for a real build. The verifier cannot run one, and how a model follows a prompt rule is not something a check on one commit can prove.
2026-10-05 T-0028 Part A overturns the cut in T-0016's spec. The path-scoped gate skip is built as the operator pre-approved it, with no repository's configuration changed. Rejected: cutting it again because it would have skipped almost no past run. The request expects a small saving here and still asks for the mechanism. Part A is a separate part, so the operator can delete it and its scenarios at the gate.
2026-10-05 T-0028 A gate command's `paths` are git pathspecs. A command is skipped when `git diff --name-only <base>...<head> -- <paths>` lists no file. Include entries (`src/`) and exclude entries (`:(exclude)dev/`) both work. Rejected: a glob matcher of our own, a second matching rule that could disagree with git's. Standing: later tickets and instance configs use pathspec semantics.
2026-10-05 T-0028 If this repository's suite is ever scoped, its paths should exclude what it does not read rather than list what it does: `:(exclude)dev/` and `:(exclude)README.md`. Rejected: the requester's inclusion list, which leaves out `.gitignore` and any new top-level file, so it would skip the suite on changes that fail it.
2026-10-05 T-0028 The harness decides the skip when a reviewer or verifier run starts on a sub-ticket. It reads the live instance's configuration and that run's base and head. The verifier is told which commands are skipped, so it does not decide. Rejected: letting the verifier judge relevance, which no record could check.
2026-10-05 T-0028 Each skipped command is recorded twice: in the checker run's `meta.yaml` (`gate_skipped`) and on the `ci` row (`skipped`). Each entry has the command, `status: SKIPPED` and the reason. The row's PASS or FAIL still comes from the verifier's `Gate suite:` line, over the commands that ran.
2026-10-05 T-0028 A malformed gate entry refuses every implementer, reviewer and verifier run start with exit 2, before a run is created. A malformed entry is anything other than a string, or a mapping with a non-empty string `command` and an optional non-empty list of non-empty strings `paths`, with no other key. Rejected: treating a typo such as `path:` as unscoped. The operator would believe a scope is in force that is not.
2026-10-05 T-0028 An empty `paths` list is refused. Rejected: reading it as "covers nothing", which would skip the command on every diff.
2026-10-05 T-0028 The planner is skipped when all of these hold, and otherwise runs as today: the parent has no sub-ticket and no earlier planner run; its latest spec-writer run did not end NEEDS-SPLIT; and its approved spec has no `##` or `###` heading, other than a `### Requirement:` line, that contains the word seam or seams. This sorts all thirteen past parents as they were built (Evidence). Rejected: the requester's "exactly one lettered part", which would have skipped none of the nine. Rejected: NEEDS-SPLIT alone, which would have built T-0025's two parts, about 470 lines, as one sub-ticket. Standing: the planner runs only for a spec that is split, re-planned or already planned once.
2026-10-05 T-0028 To force the planner on a spec that meets every condition, the operator adds a `### Size and seams` heading in a gate edit (`approve-spec --edit`). No new flag.
2026-10-05 T-0028 The whole-spec sub-ticket is `<parent>.1`, at `ready-for-implementer`, with no dependency. Its text names every scenario of the approved spec, one `- <name>` line each. For everything else it points to the spec: every lettered part, the spec's labels, its Tests to change and its Risk list. Because it names every scenario, the parent closes on its VERIFIED run under the existing rule (part C).
2026-10-05 T-0028 The store records the skip three ways: a `plan.skipped` event in the log with its reason, the parent's plan file (`plans/<parent>.md`), and the change folder's `tasks.md` when the repository has a spec store. A planner-made plan writes the same two files.
2026-10-05 T-0028 A spec already applied on `main`, the planner's most frequent ESCALATE, is caught after the skip by the implementer's step 2 and by the verifier's base run of NEW checks (design part B, table). The catch costs an implementer run in place of a planner run. Rejected: a harness check of "already applied", which would need the agents' judgment of what the spec asks for.
2026-10-07 T-0032 Retry-once-then-park on a role's unusable output (#41's EMPTY-OUTPUT) is the general mechanism: later refusal kinds (#68 format, #67 spec-lint) register with it rather than adding their own. resolve --ruling should also accept a budget-kill or EMPTY-OUTPUT park (rulings had to be placed by hand on T-0029.1 and T-0028.1).
2026-10-07 T-0032 An empty output is `EMPTY-OUTPUT`, never a budget kill. That covers a missing or empty output file, an agent call that returns blank text, and one that returns `null` (a user skip or a terminal API error). Rejected: keeping a budget-kill path for some of these. The harness enforces no budget, and the agent call reports no reason (Evidence).
2026-10-07 T-0032 Standing, from the operator's answer, already in `decisions.md` as the 2026-10-04 T-0032 line, for both parts: the empty-output route, and the reviewer leaving the suite and the gate to the verifier. Later changes follow both.
2026-10-07 T-0032 `EMPTY-OUTPUT` is decided in one place, `run finish`. The workflows no longer send `--status-override KILLED` for an empty return, so `run finish` reads the output file for every run. Rejected: a second override value in the scripts. It would label a run empty even when its output file was written.
2026-10-07 T-0032 The retry is counted inside one workflow run: one re-dispatch, then a park. Rejected: a counter in the store. It would add a ticket field for a case that a human already watches, because a workflow that stops is restarted by hand.
2026-10-07 T-0032 A thrown agent call is not re-dispatched. It carries its own error text, including the error thrown when the turn's token ceiling is spent, so it is the one stop the harness can name.
2026-10-07 T-0032 The last message is kept by a new command, `factory run last-message RUN --text=…`, called only after `run finish` has returned `EMPTY-OUTPUT`. The text is the last 4000 characters, as one shell single-quoted word. Rejected: passing it on every `run finish`, which would put each role's whole output through every clerk command.
2026-10-07 T-0032 A second empty output parks as `EMPTY-OUTPUT from <role>`, in the same form as the other role parks, and lists both runs. The last messages stay in the run directories, not in the reason.
2026-10-07 T-0032 A checker's second empty output parks before any result row is recorded for it. `resolve --redispatch` then re-runs only that checker, because the other checker's passing rows stand. Rejected: an `EMPTY-OUTPUT` result row and a join rule for it, a new row status for the same outcome.
2026-10-07 T-0032 The reviewer's input no longer lists the gate commands. It says that the verifier runs them, as the design's routing table already declares (`docs/design.md:126`).
2026-10-07 T-0032 The `budget kill` join reason is kept for hand-recorded `KILLED` rows. Rejected: renaming it, which would change three existing tests for a case no one reported.
2026-10-07 T-0032 `build.js:137` (the implementer's `budget kill` park) is removed. `run finish` can no longer return `KILLED` to the workflow, so the line would never run.
2026-10-07 T-0033 Protected paths at merge (#57, T-0033): the pinned spec's Risk list is the authorization; an undeclared changed protected path is refused at merge and parks for a ruling; no per-head approval step. All instances.
2026-10-08 T-0034 The critic keeps its minimum check, at least 2 cited paths and 1 acceptance command per review. It gains a cap of at most 2 paths and 1 command for any one claim. Rejected: replacing the minimum with the cap, which would let a critic approve having checked nothing. `docs/principles.md`'s Spiking section states the bound per claim ("Grounding a claim … two paths, one command").
2026-10-08 T-0034 The critic runs no test suite and builds nothing (no clone, worktree or prototype of the change). It runs an acceptance command only as the spec gives it, and picks one that runs no test suite. Standing: a later change to the critic prompt keeps this rule, as principle 2 requires.
2026-10-08 T-0034 A claim the critic could settle only by running a test suite or building the change is a finding for the writer, or a question, and the critic says what it could not check. The finding's severity follows the existing rubric. Rubric item 2 ("NEW items fail today") stays unchanged.
2026-10-08 T-0034 The writer and the critic get the same three reading sentences: batch independent reads and commands, read a line range once grep has found it, and send long output to a scratch file and grep or tail it. Only the writer gets "write the spec in as few writes as you can". The critic writes one verdict and needs no such rule.
2026-10-08 T-0034 No shared preamble line. The rules go only in the two role prompts. Rejected: a preamble line, which would reach every role, including the implementer and verifier, which the request does not cover.
2026-10-08 T-0034 The rules are added as new lines only, so no existing line of either prompt changes. The writer's rule is the last RULES bullet of the documented copy. The critic's rules follow its existing PROCESS line.
2026-10-08 T-0034 `docs/principles.md` records the critic's new rule under principle 2 and corrects principle 2's status line, which says "reader roles run no suites" was done by #41 alone.
2026-10-08 T-0034 The request's acceptance, a replay of 2–3 approved intakes with old and new prompts, is an Operator step. Running it needs live model runs, and judging spec quality side by side is a human call. The scenarios check the text the roles receive.
2026-10-08 T-0035 This change overturns part of a standing decision, one that later tickets must keep, recorded on 2026-10-08 for T-0034, the ticket that applied #73: "The critic runs no test suite and builds nothing ... Standing: a later change to the critic prompt keeps this rule". The no-test-suite half stands. The no-build half and the per-claim cap (T-0034's other 2026-10-08 decision) are removed. Authority: the operator's choice in `.factory/answers/T-0034-acceptance-2026-10-08.md`. Standing: later changes to the critic prompt keep the no-suite rule and do not re-add a per-claim cap or a no-build rule without new evidence.
2026-10-08 T-0035 The critic prompt gains one sentence that allows a small experiment in its scratch directory to confirm a finding. Without it, the kept sentence "A claim you could settle only by ... building the change is a finding" reads as the old ban. The kept sentence still covers building or trying out the change itself, which the request's item C (its `docs/principles.md` change) leaves to the writer or to a spike, a ticket built only to test whether an approach works. Rejected: deleting the kept sentence. The triage role, which sorts a request before the spec writer sees it, asked to keep it, and it still tells the critic what to do with a claim it cannot check.
2026-10-08 T-0035 The no-suite line gains its reason, "the implementer and the verifier run it", as the request's item B (its list of what the critic keeps) gives. `Pick an acceptance command that runs no test suite, and run it as the spec gives it.` and the Turn economy paragraph stay word for word.
2026-10-08 T-0035 The Spiking section records the replay result, as the request's item C asks ("Record the replay result"). The changelog entry records it too.
2026-10-08 T-0035 Of the current-truth requirements that #73 added, four are restated (MODIFIED), because each states the rule being removed or forbids removing a critic line. Other current-truth requirements that check the diff of their own change (for example "The documents record the live-store guard", which expects no prompt copy to change) are left as they are, as #73 left them. Their scenarios describe their own change, not standing behaviour.
2026-10-08 T-0035 "Writer unchanged from #73" is checked as no difference from `05cf8f9` in either writer prompt file, plus the writer's design block equal to its `docs/prompts/` copy. Together these mean the design block is unchanged too.
2026-10-09 T-0036 Triage names the capabilities on a new output line, `Capabilities:`, chosen from a capability index added to its input. A token that names no current-truth capability, such as `none` or `new`, is ignored.
2026-10-09 T-0036 Which capabilities a role receives in full: the names on triage's line, plus each existing capability whose `specs/<name>/spec.md` path appears in the spec the role works from. For the writer that is its previous version on a revision round. For the critic it is the version under review. For the planner it is the approved version, read whole, Evidence included. A writer that opens a capability and cites its path under Evidence therefore hands it to the critic. This keeps the request's rule that the critic sees the writer's list plus whatever the writer opened.
2026-10-09 T-0036 A ticket whose latest finished triage output has no `Capabilities:` line gets today's inputs, the whole of current truth and the whole log. This covers tickets triaged before this change, T-0036 among them. Rejected: sending only the index in that case, which would cut those tickets' inputs with no list to cut by.
2026-10-09 T-0036 An index line for a capability gives its name, its size, the absolute path of its spec and its requirement names. Rejected: the request's "one-sentence purpose", because no capability spec on either store has a purpose paragraph (Evidence).
2026-10-09 T-0036 A decision line goes in full when it is logged against this ticket, or when its text names a capability sent in full as a whole word. The log's other lines are indexed one line per ticket: ticket id, number of decisions, first and last date, and the ticket's title. The index heading gives the command `grep ' <ticket id> ' <absolute path of decisions.md>`. Rejected: one index line per decision, which comes to tens of kilobytes on Nanobot (240 lines, median 278 bytes).
2026-10-09 T-0036 A role opens deferred items by path, with its own file reads or `grep`. No `factory spec show` or `factory decision show` command is added. Rejected: those commands, because a command run from inside a role must clear the live-store fence and find the instance from the role's working directory. A path needs neither, and it is how compose already points at full specs (Evidence).
2026-10-09 T-0036 The instructions live in the index headings. They say the list is complete, that anything in it is opened by its path, and that citing a path hands the capability to the critic. Rejected: editing the writer and critic prompts, which would put the same words in two more protected copies.
2026-10-09 T-0036 A run's `input_sources` lists only the files sent in full. An index adds no source.
2026-10-09 T-0036 The standing 2026-10-04 T-0024 decision says that `decisions.md` "keeps reaching the spec writer, critic and planner". It still does: in full for the lines this ticket touches, and line by line for the rest through the index and its `grep` command.
2026-10-09 T-0036 Acceptance does not hold this change to the request's 40 kB mean and 100 kB maximum. The projection gives a mean of 101 kB and a maximum of 167 kB for the Nanobot store's last ten tickets, and the remainder lies outside this change (Problem, Evidence). The operator steps measure the real figures after the change runs.
2026-10-09 T-0036 The docs use one name for the new index, "capability index".
2026-10-09 T-0037 Decision log in role inputs (#78, T-0037): the spec writer, critic and planner get decisions.md whole; #75's decision filter is removed; any future scoping must not be able to drop a cross-cutting standing decision (see #54).
2026-10-09 T-0037 The spec writer, critic and planner receive `decisions.md` whole whenever it holds any text, whatever capabilities their ticket names. The decision index and its `grep` instruction are removed. This is the operator's Answer 1, already standing in `decisions.md` as the 2026-10-09 T-0037 line. Rejected: the request's rule of sending lines that name no capability in full and filtering the rest. On today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
2026-10-09 T-0037 The capability index note loses its clause ", and the decisions that name it to the critic and the planner,"; the rest of the note stays word for word. Rejected: keeping the clause, which would tell the writer that citing a path is how decisions reach the critic and planner. That is no longer so. This edits one sentence of #75's capability half, which the triage assumption kept byte for byte.
2026-10-09 T-0037 The planner's decision part no longer reads triage's capability names or the approved spec's citations. It reads the whole log, as before #75.
2026-10-09 T-0037 The decision part is measured in this spec's Evidence, before and after, on both stores. No new file or harness command records it.
2026-10-09 T-0038 Each sub-ticket records `planned_from`, the parent's approved version when the sub-ticket was created. Nothing changes it afterwards. Rejected: reading `spec.approved_version`, which approved T-0027 moves forward on amendment.
2026-10-09 T-0038 Superseded is computed whenever sub-tickets are read, not stored. A sub-ticket is superseded when it has not merged and its `planned_from` is lower than the highest `planned_from` among its parent's sub-tickets. Rejected: the request's mark written at re-plan time. That needs a write on every path that adds a plan and a migration for stores that already hold such sub-tickets, such as Nanobot T-0024. Also rejected: comparing with the parent's current approved version. That would supersede the live plan after a T-0027 amendment that keeps it.
2026-10-09 T-0038 A record without `planned_from`, or with it null, falls back to its `spec.approved_version`. With neither, the sub-ticket counts as current.
2026-10-09 T-0038 A plan made from the same approved version supersedes nothing. This covers `resolve --replan` after a failed final check, and a second plan added by hand. The design ties a new plan to an amended spec (`docs/design.md:109`). To replace a plan without changing intent, the operator approves with `approve-spec --edit`, which always makes a new version. This is a standing decision.
2026-10-09 T-0038 Merged sub-tickets are never superseded. They count toward the close, the final check must contain their merges, and a new plan may depend on them.
2026-10-09 T-0038 `subticket add` refuses, writing nothing, a plan whose `Depends on:` names a sub-ticket that the plan supersedes. Rejected: accepting it. The dependant would wait forever, because a superseded sub-ticket is never dispatched.
2026-10-09 T-0038 `subticket add` reports the sub-ticket ids it newly supersedes under `superseded` and logs a `subtickets.superseded` event. Nothing is deleted, and every id stays taken.
2026-10-09 T-0038 `ticket ready-implementers` keeps `subtickets` as every sub-ticket id. `build.js` reads an empty list as "planned with none", and `dev/build-harness.spec.md:286` documents it that way. Every other list there leaves superseded sub-tickets out, and the new `superseded` list names them.
2026-10-09 T-0038 The planner is told which sub-tickets its plan will supersede, on one line after the existing list. With none, its input is byte-identical to today.
2026-10-09 T-0038 The name is "superseded", as the request and triage use it, and in the same sense as `results/<head>/superseded-<n>/`: a record kept but no longer counted.
2026-10-09 T-0033 The authorization is the pinned spec's Risk section. The pinned spec is the version the operator approved at the spec gate. For a sub-ticket, that is its parent's approved version (`specs/<parent>/v<approved_version>.md`). A ticket with no parent uses its own approved version. A ticket with no approved spec declares nothing. This is standing for every instance, from the operator's 2026-10-05 answer. It is already the 2026-10-07 T-0033 line in `decisions.md`, the factory's log of standing decisions that later tickets must follow.
2026-10-09 T-0033 The gate reads declarations from one fixed line in the Risk section: `Protected paths: none`, or `Protected paths: ` followed by one or more backticked paths or globs, separated by commas. An optional list marker (`- ` or `* `) may come before it, and an optional full stop after it. Each entry is one path or one glob. A brace list such as `factory/prompts/{a,b}.md` is one literal entry, which git does not expand, so it matches no file and declares nothing. A Risk line in any other shape declares nothing, and so does a line inside a fenced code block. Several such lines declare their union. Standing: specs declare protected paths only this way. Rejected: reading every backticked path in Risk, because today's Risk sections also put the paths they promise not to touch in backticks (Evidence). Rejected: the planner's per-sub-ticket `Protected paths:` field, which an agent writes and no human approves.
2026-10-09 T-0033 A changed path is "protected" when it matches one of the instance's in-repo `protected_paths` globs. It is "declared" when it matches a declared entry. Both matches use git's glob pathspecs (`:(glob)<pattern>`, so `**` crosses directories and `*` does not). This follows the 2026-10-05 T-0028 decision that the harness never adds a glob matcher of its own. Patterns that start with `~` or `/` are skipped.
2026-10-09 T-0033 The changed paths are those of `git diff --name-only --no-renames <integration branch>...<head>`, measured from the merge base; the head is the commit the gate is judging. Once the head contains the integration branch, that is exactly what the merge adds. `--no-renames` lists both sides of a move (Evidence). Rejected: the triage's "parent base". A catch-up run is an implementer run that merges the integration branch into a sub-ticket's branch that has fallen behind. After one, a diff from the parent's base counts other tickets' merged changes against this sub-ticket.
2026-10-09 T-0033 The gate runs this check after the three recorded results and before the containment check and the merge lock. A change that will be refused costs no catch-up run.
2026-10-09 T-0033 A refusal exits 2 and changes no ticket field. It logs one `merge.refused` event with the paths. Its error starts `BLOCKED from merge gate: ` and names each undeclared path, sorted and comma-separated. It names no declared path and uses no backtick, `$` or double quote, because the build workflow passes the reason through a shell command.
2026-10-09 T-0033 The build workflow parks the sub-ticket with that error, verbatim, as the reason. It already does the same for the harness's `BLOCKED from harness:` refusal at run start.
2026-10-09 T-0033 The human answers that park with one of two commands. `resolve --ruling F` sends the change back. It uses the existing BLOCKED route: the sub-ticket returns to its implementer with F in its input, and its round count (the number of fix cycles it may use) is not reset. The new `resolve --accept-paths F` accepts the paths under the approved design. It records F as the sub-ticket's next ruling. It adds the undeclared paths, recomputed on the current head, to a ticket field `accepted_paths`, which the gate treats as declared. It returns the sub-ticket to `checks-in-flight`, the state in which the reviewer and verifier judge it, with its recorded results kept, so the build merges it on its next pass. Rejected: one acceptance per head, because a catch-up run makes a new head and the same paths would park again. Rejected: amending the pinned spec's Risk section, because no command amends a pinned spec yet (T-0027 asks for one). An acceptance adds paths only for that sub-ticket and leaves every other merge condition in force.
2026-10-09 T-0033 `--accept-paths` refuses, with exit 2 and nothing written, on a park whose reason does not start `BLOCKED from merge gate:`. Its error starts `--accept-paths applies to`. It also refuses when the head is not the branch tip, or when no undeclared protected path remains.
2026-10-09 T-0033 A ruling on a park whose reason starts `ESCALATE from reviewer` returns the sub-ticket to `checks-in-flight`, round count unchanged. Its recorded results are set aside as `--redispatch` sets them aside: an APPROVE reviewer result is kept, and a VERIFIED verifier result with a PASS gate result is kept. Every other result moves to `superseded-<n>/`. The reviewer and verifier runs that follow receive the ruling, as they already do (`factory/compose.py` lines 278 and 300). This overturns `docs/design.md` line 109, which sends a reviewer ESCALATE to the implementer with the round count reset. Rejected: that route, because the 2026-10-05 escalation needed no code change. The re-run reviewer can still return REQUEST-CHANGES when a ruling asks for a fix.
2026-10-09 T-0033 Check 6 of the reviewer prompt keeps its first two sentences and adds "for the record" to the list of declared paths. Its last sentence says what the gate does: it merges a declared path with no further approval, and refuses and parks one the approved spec does not declare.
2026-10-09 T-0033 No per-head approval is added for paths that change the factory's own rules (option 3 of the operator's answer). The answer leaves it open for this spec gate. Adding it is a gate edit to this spec (a new lettered part) or a later ticket.
2026-10-09 T-0030 T-0030 (#24 A+C) closed as partly applied: part C merged (T-0030.3); parts A, B and per-role effort moved to #65 (backlog review 2026-10-09). Current truth was not folded for this ticket.
2026-10-09 T-0026 T-0026 (#47) withdrawn: merged into #65 at the backlog review 2026-10-09; the Workflow scripts it would change retire with #65.
