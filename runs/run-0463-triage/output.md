Type: chore

Title: De-bloat C: give each operation the harness writes out several times one shared helper, with no change in behaviour

Summary:
The requester wants eight operations to each have one shared definition instead of several hand-written copies across `factory/cli.py`, `drive.py`, `store.py`, `compose.py`, `specstore.py`, `stats.py` and `cost.py`, because a fix can miss one of the copies. The eight are: finding the runs of a ticket, reading the event log, recording a status transition, listing the runs in flight on a ticket and its sub-tickets, reading the integration-branch tip, a few smaller repeats in `cli.py`, the failure parks in `drive.py` (a park stops a ticket for a human, with a reason), and the section and block walks in `specstore.py`. Nothing a user or operator sees may change: every refusal string, park reason, log event shape and verdict stays as it is, and the existing tests pass without edits to their assertions. Splitting `cli.py` into modules (#100, T-0047), the STATUS-trailer search (#68) and the Workflow scripts (#89) are out of scope. The requester rates the risk low to medium and asks that item 8, which touches how an archived spec is written into current truth, go last.

Evidence:
- Issue https://github.com/danielphang/spec-factory/issues/99, from the 2026-10-11 de-bloat sweep (#96 row 2a), with line references taken at `927bc53`.
- I checked every pattern at the current `main`, `2b9baf5`. De-bloat A (T-0044.1) has merged since `927bc53` and changed `cli.py`, `compose.py`, `specstore.py` and `store.py` (`git diff --stat 927bc53 HEAD -- factory/`: 8 files, +20 −57), so some line numbers have moved by a few lines. All the patterns are still there:
  - Runs scan: `compose.py:16` `_runs_for`, `compose.py:413`, `specstore.py:269` `critic_rounds`, `cli.py:1712` `_parent_close_verified`, `store.py:116` `clear_scratch`.
  - Log reads: `cli.py:674` (`_recorded_plan_run`), `cli.py:1761` (`log_tail`), `stats.py:72`, `cost.py:129`.
  - Transition records: `ticket.transition` is logged at `cli.py:177`, `821`, `1003` and `1067`. The fifth one, at `cli.py:1122`, is in `approve_spec`, which the request leaves alone.
  - In-flight scan: `cli.py:602-603` and `drive.py:626`.
  - Integration-branch tip: `gitops.rev(repo, gitops.integration_branch(cfg, repo))` at `cli.py:254`, `328`, `545` and `1693`.
  - Checker cleanup: `call("run", "cleanup", rid)` at `drive.py:226`, `234` and `575`.
  - Park text: `grep -c 'harness-bug:' factory/drive.py` gives 24 at HEAD. The request says the park pattern appears 18 times, and the grep count also matches lines that are not parks.
  - The ruling prefix `harness-bug: run start implementer:` is at `cli.py:1187`.
  - The `specstore.py` functions are at `:76` `lines_outside_fences`, `:102` `requirement_blocks`, `:158` `acceptance_labels`, `:305` `decisions_of`, `:324` `scenario_blocks`, `:350` `intent_of` and `:392` `apply_delta`.
- The tests the request relies on all exist under `tests/factory/`: `test_parent_close_reuse.py`, `test_cost_once.py`, `test_shepherd.py`, `test_spec_store.py`, `test_spec_amend.py`, `test_decision_log.py`, `test_drive.py`, `test_drive_build.py` and `test_drive_guard.py`. So do the Workflow scripts `factory/intake.js` and `factory/build.js`.
- Duplicate search: there is no duplicate among tickets T-0035 to T-0048. The related tickets are:
  - T-0044 (De-bloat A, dead code), closed.
  - T-0045 (De-bloat B, test helpers), planned. It is about the tests, not the harness code.
  - T-0047 (De-bloat D, splitting `cli.py`). The request names it as out of scope and as following this ticket.
  - T-0048 (De-bloat E, docs).

Capabilities: harness-code, build-dispatch, human-resolution, spec-amendment, sub-ticket-planning, factory-stats

Assumptions:
- (inference) The helper names and the module each helper goes in (`store.events`, `store.record_transition`, `store.in_flight_runs`, a gitops helper, `section(text, heading)`) are the requester's suggestions, not requirements. The requirement is one definition per pattern, with behaviour unchanged.
- (inference) The spec writer must take line numbers from the current `main`, not from `927bc53`. The acceptance check that the grep counts fall needs before-and-after counts measured on the same base.
- (inference) The "~90 lines" in the title is an estimate, not an acceptance threshold. The requester asks for the line change per file to be reported, not for a target.
- (inference) `cost.py` may keep its own log reader, as the request allows, because `test_cost_once.py` loads that file by its path.
- (inference) The capabilities listed are the ones whose behaviour the refactor must keep:
  - park reasons and the ruling prefix (build-dispatch, human-resolution);
  - the messages from spec amend and approve, and `apply_delta`'s writes to current truth (spec-amendment);
  - the PLANNED planner-run refusal (sub-ticket-planning);
  - the stats and cost readers (factory-stats);
  - no unused definitions (harness-code).
  No capability's requirements change.
- Suggested priority (a suggestion; priority is a human call): after T-0045 and before T-0047, since T-0047 is meant to follow this ticket.

Reason: The intent is clear and the scope is bounded, with exclusions named. The behaviour to keep is stated as runnable checks: the full suite passes with unchanged assertions, and the set of distinct park prefixes and every refusal string stays the same. No product or design decision is needed.

STATUS: ACCEPT
CONFIDENCE: high — I checked every named pattern, test and script at HEAD `2b9baf5`; the only differences from the request are small line-number shifts and the `harness-bug:` grep count (24, not 18), both noted above.
ESCALATIONS: none
