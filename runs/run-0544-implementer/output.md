Sub-ticket: T-0049.1 (`.factory/store/tickets/T-0049.1.yaml`; parent T-0049, approved spec v1 at `.factory/store/specs/T-0049/v1.md`)
Branch: `factory/T-0049.1`, one commit `17fba14` on base `81482fe`. Only `README.md` changed: 67 lines added, 2 removed. Over the whole page that is 1,109 lines before and 1,174 after.

## What changed

The README's flow diagram showed only the simple path: a request becomes a spec, a human approves it, and the build closes the ticket. It drew none of the ways a spec changes. This change adds a second diagram that draws them. It also corrects the clerk node in the first diagram. The clerk is the agent that relays records to the store, and it exists only when the pipeline runs as a Workflow script. Everything is in `README.md`.

- **A. New subsection "How a spec changes and feeds later tickets"**, placed between the first diagram's caption and `### Ticket states`, with one blank line before that heading. It has a prose paragraph, then the diagram, then a two-line caption. The diagram's edges, its three `classDef` lines and its subgraph title `"a later ticket"` match the spec exactly. Two sentences differ from the spec's text so that they stay true to the code:
  - The spec said "a human approves the newest version". The README now says "a human approves a version, the newest by default". `approve-spec --version N` can approve an earlier version (`factory/human.py:135`, `factory/cli.py:787`).
  - The spec said "its planner receives the decision log only". The README now says "its planner receives the decision log but no current truth". The planner also receives the approved spec (`factory/compose.py:324-325`), so "only" was too strong.
- **B. Clerk node** (the first diagram's line 209). It now says that the clerk exists on the Workflow-script path only, that the launch copy carries the settings the clerk does not relay, and that `factory drive` needs no clerk. The launch copy is the copy of the Workflow script that `factory launch-script` writes with the instance's settings filled in. No other line of that diagram changed.
- **C. Regeneration table.** The `| How a ticket moves |` row of "Regenerating this page from scratch" now also names the modules the new diagram is drawn from: `factory/human.py`, `factory/subtickets.py`, `factory/drift.py`, `factory/specstore.py` and `factory/compose.py`. I checked that every function it names exists: `approve_spec` (human.py:130), `request_changes` (164), `spec_amend` (31), `resolve` (179), `split_plan` (subtickets.py:159), `_check_drift` (drift.py:42), `archive` (specstore.py:398) and `compose` (compose.py:176).
- **D. Status date.** No edit. The **Status** row already reads "as of 2026-10-19", which is the day of this change.
- **E. Edge-to-code table.** I re-checked every line number against the base `81482fe` by reading each cited range. Most were right. I corrected these:
  - `factory/specstore.py`: the spec cited 405-414 and 415-417. The fold into current truth is at 407-415 and the Decisions lines at 416-418. Line 405 writes `verification.md`.
  - `factory/workflows/intake.js`: the spec cited 203-204 for REVISE. It is 203-205, because the transition back to the spec writer is on 205.
  - `factory/compose.py`: the spec cited 265-270 for the triage index. The index text continues to 271.

| Edge in the new diagram | Route in the code at `81482fe` |
|---|---|
| Spec writer → spec versions, "each output is the next version" | `factory/drive.py:288,294`, `factory/workflows/intake.js:184,188` (`spec add --from-run`); `factory/cli.py:407-410` `spec_add`; `factory/common.py:29-39` `_add_spec_version` |
| spec versions → Spec critic | `factory/compose.py:297-298` (the critic reads `specs/<id>/v<version>.md`) |
| Spec critic → Spec writer, "revise · once" | `factory/drive.py:315-322` (REVISE, below the round limit); `factory/workflows/intake.js:203-205` |
| Spec critic → Spec gate, "approve" | `factory/drive.py:307-308`; `factory/workflows/intake.js:197-198` |
| Spec gate → Spec writer, "request-changes · notes" | `factory/human.py:164-176`; `factory/cli.py:790`; the notes reach the writer at `factory/compose.py:293-294` |
| Spec gate → change folder, "approve-spec pins vN · --edit F pins F as vN+1" | `factory/human.py:130-161` (`--edit` at 146, `specstore.pin` at 148); `factory/cli.py:788` |
| change folder → Planner, or the whole spec as one sub-ticket | `factory/drive.py:336-354`; `factory/cli.py:499-515` `_planner_needed`, 518-546 `plan_whole_spec` |
| Planner → sub-tickets, "planned_from … supersedes …" | `factory/cli.py:487` (in `_create_subtickets`, used by both); `factory/cli.py:461-473`; `factory/subtickets.py:159-175` `split_plan`, `superseded_by_plan`; the next free ids at `factory/compose.py:329-330` |
| sub-tickets → drift check | `factory/cli.py:195-197` (`run start` for an implementer); `factory/drift.py:42-50` |
| drift check → implementer · checks · merge, "no drift" | `factory/drift.py:56` (no findings, no refusal) |
| drift check → parked ticket, "BLOCKED: spec drift" | `factory/drift.py:57-58` (the refusal starts `BLOCKED from harness: spec drift`); parked as given by `factory/drive.py:190-196` |
| implementer · checks · merge → Verifier, "every sub-ticket merged" | `factory/drive.py:403-418` |
| Verifier → parked ticket, "fails" | `factory/drive.py:417-418` |
| parked ticket → next version pinned, "spec amend · intent unchanged" | `factory/human.py:31-98` (plan kept at 76-79); `factory/cli.py:717` |
| next version pinned → implementer, "resolve --ruling F" | `factory/human.py:236-237`; with a ruling on file the drift check is skipped, `factory/drift.py:50` |
| parked ticket → Spec gate, "resolve --to spec-gate · re-spec" | `factory/human.py:265-270`; `factory/cli.py:799` |
| parked ticket → Planner, "resolve --replan F · every sub-ticket merged" | `factory/human.py:278-290`; `factory/cli.py:803` |
| Verifier → archive, "verified" | `factory/drive.py:421`; `factory/gates.py:291-303` `archive_cmd` |
| archive → current truth, "folds the changes" | `factory/specstore.py:407-415` |
| archive → decision log, "appends the Decisions lines" | `factory/specstore.py:416-418` |
| a human → decision log, "appends a line" | `factory/human.py:330-334` (`decision add`), 190-196 (`resolve --decision`); `factory/specstore.py:6-7` |
| Triage → Spec writer · critic, "Capabilities: line" | `factory/compose.py:28-42` `triage_capabilities`, 210-218 `selected` |
| current truth → Triage, "index of every capability" | `factory/compose.py:265-271` |
| current truth → Spec writer · critic, "named capabilities in full · index of the rest" | `factory/compose.py:220-229`, 280-281, 299-300 |
| decision log → Spec writer · critic, "the whole log" | `factory/compose.py:231-237`, 282, 301 |
| decision log → Planner, "the whole log · no current truth" | `factory/compose.py:325` |
| clerk node (part B) | `factory/workflows/build.js:18-20` (the launch copy carries the settings), 45-50 `clerk()`; `factory/drive.py:1-5` (no clerk) |

## Acceptance results

I ran every command from the worktree under the fresh-HOME wrapper. All nine are in one script, `scratch/acc.sh`, which runs under `bash`. Each command is copied verbatim from the spec.

| Scenario | Kind | Before (`81482fe`) | After (`17fba14`) |
|---|---|---|---|
| The spec's-life diagram draws every route after the critic | NEW | `classes=0 request=no edit=no amend=no respec=no replan=no ruling=no planned=no drift=no truth=no log=no writers=no later=0` | `classes=3 request=yes edit=yes amend=yes respec=yes replan=yes ruling=yes planned=yes drift=yes truth=yes log=yes writers=yes later=4` |
| The clerk node names the Workflow-script path, the launch copy and factory drive | NEW | `clerk=1 workflow=0 launch=0 drive=0` | `clerk=1 workflow=1 launch=1 drive=1` |
| Both diagrams of How a ticket moves have balanced quotes and brackets | NEW | `blocks=1 bad=0` | `blocks=2 bad=0` |
| The How a ticket moves row names the five modules | NEW | `row=1 names=0` | `row=1 names=5` |
| README is at most 1,185 lines | REGRESSION | — | `readme=within` (1,174 lines) |
| README describes init's report of a differing agent copy | REGRESSION | — | `row=1 step=1 missing=1` |
| The changelog records issue 108 in one entry without a numbering gap | REGRESSION | — | `CONTIGUOUS`, `1`, `3` |
| README stays within its line budget and both documents pass the whitespace check | REGRESSION | — | `readme=within`, `check=0` |
| The README, the design doc and the changelog describe the launch copy and the route back to checks | REGRESSION | — | `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within`, `CONTIGUOUS`, `entries=1 terms=3`, `exit=0` |

Each NEW command printed exactly what `verification.md` predicted before the change, and exactly what its THEN line requires after it. Every REGRESSION command printed its expected output after the change, so none needed a run on the base.

Gate commands, each run exactly as written on `17fba14`:
- `git diff --check main...HEAD` printed nothing and exited 0. `main` is `81482fe`, the base.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `615 passed in 164.22s` and exited 0.

## Tests added/changed

None. The spec's "Tests to change" is none, and no test reads README's text. The NEW checks are the acceptance commands themselves.

## Known gaps and uncertainties

- **No real Mermaid render.** The diagram check is structural only. It checks balanced quotes and brackets, the opening `flowchart LR` and a closed fence; it does not parse the diagram. That rendering check is the spec's operator step after merge: open `README.md` on GitHub and confirm that both diagrams render.
- **Simplifications kept from the spec.** The diagram and prose say these things, and the code allows more:
  - `spec amend` is drawn from "parked ticket". The command never checks for a park. Its refusals are about other things, such as a sub-ticket, a ticket at the gate, a closed ticket, or runs in flight (`factory/human.py:37-51`).
  - The drift check's "for example when a test changed there" leaves out its other trigger: an unmerged sibling sub-ticket named in the Acceptance that the sub-ticket does not depend on (`factory/drift.py:43-45`, 55).
  - `resolve --to spec-gate` accepts any parked ticket that has a spec version, not only a parent (`factory/human.py:268`).

  The spec fixes the diagram's edges, so I did not change them. The prose uses "for example" and "a parked parent", which stay true.
- **README is one line longer than the spec's prototype**: 1,174 lines instead of 1,173. The reworded gate sentence wraps onto one more line. It is still 11 lines under the 1,185 budget.
- **The budget figure is not raised by this branch.** The three `harness-docs` requirements that hard-code 1,110 are restated as 1,185 under MODIFIED in the parent's capability spec. `archive` writes them into current truth when the ticket closes, so this branch does not edit current truth.

## Out-of-scope observations

- The first diagram's subgraph labels, "(agents, driven by the script)", still describe only the Workflow-script path. The parent spec notes this and leaves them as they are.
- The spec's edge table cited `factory/specstore.py` and `factory/workflows/intake.js` lines that were off by one or two at `81482fe`. They are corrected in the table above.

## Responses to findings

Not applicable: this is round 1.

Protected paths: none touched. The parent's Risk section declares none.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All nine acceptance commands and both gates pass on `17fba14`, and every diagram edge was checked against the code at `81482fe`; only the GitHub render is unverified, and the spec leaves it to the operator.
ESCALATIONS: none
