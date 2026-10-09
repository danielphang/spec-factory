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
