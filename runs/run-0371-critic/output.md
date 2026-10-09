Review of T-0027 spec v3 (round 1 on v3; the input carries no earlier findings of mine).

What I checked, on `~/dev/spec-factory` at `b002c95` (tree clean apart from an untracked `.factory/answers/T-0027-changes-2026-10-09.md`, a copy of `approvals/T-0027/changes-1.md`):

- Cited paths and symbols: `factory/cli.py:843` `approve_spec`, `:859` the `awaiting-spec-gate` refusal, `:862` the `_add_spec_version` call, `:395` `_add_spec_version` (two callers, `:407` and `:862`, as part D says), `:1564` the `spec` subparser with `add` and `tasks`, `:198` `run_start`, `:213` `_check_sibling_tests`; `factory/compose.py:265` critic branch, `:291` planner, `:334/:349/:352` implementer and checkers; `factory/specstore.py:290` `pin` with `shutil.rmtree` at `:296`, `:336` `archive`; `docs/design.md:110`, `:113`, `:456`; `docs/prompts/03-spec-critic.md:21` and `factory/prompts/critic.md:21`; `dev/build-harness.spec.md:315` (`--amend-spec FILE`) and `:193`; `factory/workflows/build.js:81-83`. All exist and say what the spec says. Every helper part A, B and D names exists: `_next_n` (cli.py:839), `subtickets_of` (store.py:228), `decisions_of`, `delta_ops_of_change`, `split_parts`, `DELTA_RE`, `lines_outside_fences`, `SCEN_RE`, `_heading`, `parse_delta`, `validate`, `applies`, `is_active`, `change_dir` (specstore.py), `split_plan`, `sibling_tests`, `PLAN_FIELDS` (subtickets.py), `gitops.rev`, `compose._runs_for`. Every CLI verb the scenarios use exists with the flags used (`ticket show --json`, `ticket set`, `ticket park --reason`, `resolve --to`, `request-changes --notes`, `log tail --event`, `archive`).
- Evidence records: `approvals/T-0012/amendment-1.md:5` carries the quoted "Applied in place" sentence; `run-0304-implementer` exists here; on Nanobot `run-0166-implementer`, `run-0380-verifier`, `run-0391-implementer`, `run-0399-implementer` and both T-0008 rulings exist (read only). `tests/factory/test_gate_paths.py` was added by commit `0e99fa7` (T-0028.1). `openspec/changes/` here holds T-0026 (closed), T-0027 (self, `ready-for-critic`), T-0030 (closed), T-0031 (`planned`): part B's list would hold one entry, T-0031, as Risk says. T-0039 is `awaiting-spec-gate`.
- Acceptance commands, run as given under a throwaway HOME, with the fixture in my scratch directory: "The runtime critic prompt stays a copy" prints `copies=same`; "A critic run's system prompt carries the cross-ticket rule" prints `rule=0`; scenario 1 prints `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged`; "A later implementer run receives the amended spec" prints `changed=0 merged=0 reason=0 logged=0` then `amended=0 old=1 run_version=1`; "Archive after an amendment" prints `archive=0 hello=0 hi=1`; the sibling-rule scenario prints `unmerged: blocked=0 names=0 runs=1 ready-for-implementer` then `merged: exit=2 runs=1`. Each matches the failure verification.md states for it.
- Tests pinning old behaviour (rubric 1): I searched `tests/factory/` for a pin on the `spec` subcommand set (`invalid choice`), on the critic rubric wording or the critic prompt copies, on `_add_spec_version`'s signature, on a listing of `specs/<id>/` (where the new `v<n>.yaml` lands), and on Acceptance fields naming an unmerged non-dependency sibling. None found: the only Acceptance fields in tests (`test_subtickets.py:183`, `test_parent_close_reuse.py:15-18`) name the sub-ticket itself or no sibling, and the `t0022-sib.sh` fixture adds its spec before the target repo exists, so its versions would record a null head and the test rule skips. "Tests to change: none" holds as far as a search can tell.
- Not checked: the drift measurement (17 of 36, 29 of 43, 9 of 10), the prototype's `408 passed`, and that the three current-truth sibling-tests scenarios print the same on the prototype. These need the suite or the build and are the verifier's.

Findings

[SHOULD-FIX] 6 design.md, part A, the restart note (and Decisions, the restart-note bullet)
Problem: The note prints each merged sub-ticket as `<id> / <title> (merge <main_after, 9 chars>)`, but the scenario that exercises it marks T-0001.1 merged with `ticket set status=merged`, which records no merge commit, so the implementer has to guess what to print when `merge.main_after` is absent.
Evidence: scenario "An amendment declared or found to change intent is refused" sets `status=merged` only; `t0022-sib.sh` shows the merge record lives in `merge.main_after`, set separately. The scenario greps `T-0001.1 / First`, so any choice passes it, but the output format is unspecified for that case.
Suggested fix: Say what the note prints when a merged sub-ticket has no `merge.main_after` (for example, `(merge unrecorded)`), in design part A.

[SHOULD-FIX] 6 proposal.md, Decisions, first paragraph
Problem: "the build spec's unbuilt `resolve --amend-spec`" uses "build spec", a term of this system, which no human-facing section has glossed; the rule names this BLOCKING, but I do not block on it because the Evidence paragraph gives the file's path and says it "specifies a flag that was never built", which tells the reader what it is in all but form.
Evidence: Problem glosses ticket, role, spec, gate, pin, store, change folder, planner, archive, current truth, run, parked, BLOCKED, ruling; neither Problem nor Evidence says what the build spec is. `resolve` is glossed in the same Decisions sentence ("acts on a ticket the pipeline has stopped").
Suggested fix: Gloss it once where it first appears, in Evidence: "The build spec, the harness's own build-and-acceptance document at `dev/build-harness.spec.md`, ...".

[NIT] 4 proposal.md, Decisions, "Human-only means..."
Problem: The argument that the in-flight refusal stops a role run from amending covers only a run on the same ticket; a role run on another ticket is stopped by the live-store guard instead, which the paragraph does not say.
Evidence: current truth live-store-guard, "Unmarked writes to a live store are refused while a role run is in flight there".
Suggested fix: Add one sentence naming the live-store guard as what stops a role run on another ticket.

[NIT] 2 specs/spec-amendment, scenario "An amendment is refused while a sub-ticket's run is in flight"
Problem: `names_run` greps stderr (`2>&1 >/dev/null`) while every other refusal scenario greps the JSON on stdout; both work (cli.py:1709-1710 prints the error to both), but a reader checking the scenarios against each other will pause on it.
Evidence: `factory/cli.py:1708-1711`.
Suggested fix: Grep stdout like the others, or leave it with a word that says the refusal is printed to both.

No blocking issues. The spec is NEEDS-SPLIT with its seams named, every NEW scenario I ran fails today for the stated reason, every protected path the design touches is on the `Protected paths:` line, and the overlap with T-0031's `run_start` edit is declared.

Prior findings: none in input.

STATUS: APPROVE
CONFIDENCE: medium — every cited path, symbol and six acceptance outputs check out; the park-rate figures and the prototype's suite result could not be checked without running the suite.
ESCALATIONS: none
