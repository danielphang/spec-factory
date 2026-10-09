=== proposal.md
## Problem
Since issue #75, three agent roles can miss a standing rule that every ticket must follow. Those roles are the spec writer, which writes a ticket's spec; the critic, which reviews it; and the planner, which splits an approved spec into pieces of work. The rules sit in the decision log, `decisions.md`, one line per standing decision with its date and the ticket that made it. #75 cut each of those roles' input to save context: a decision line now reaches them in full only when it was logged against their own ticket, or when its text names a capability they receive in full. A capability is one current-truth spec, the store's record of how one part of the system behaves today. Every other line is reduced to one entry per ticket in a "decision index", with a `grep` command the role may run to read it.

No decision line in either store names a capability, so the filter hides every rule that some other ticket made. In the operator's replay of a Nanobot ticket, the spec writer put new code in a module that a standing decision rules out, and the critic did not notice. Both had seen that decision only as an index line. The operator has chosen to send the whole decision log to these three roles again and to keep the rest of #75, the capability filter. The cost is about 34 kB more input per run on this repo's store and about 72 kB more on the Nanobot store.

## Evidence
- Replay of #75 on Nanobot ticket T-0032, 2026-10-09 (the request): the new writer put its code in `nanobot/cron/session_sweep.py`. Standing decision T-0003 rules that out: lionbot code goes through upstream's extension points first. The original writer, given the whole log, followed T-0003, and the original critic confirmed it. The replay critic missed the conflict.
- The operator's answer (Answer 1, 2026-10-09) chose to drop the decision filter, remove the decision index and its `grep` instruction, and keep #75's capability half as built. It is already a standing decision, the last line of `.factory/store/decisions.md`: `2026-10-09 T-0037 Decision log in role inputs (#78, T-0037): the spec writer, critic and planner get decisions.md whole; ...`.
- The filter is `add_decisions` in `factory/compose.py:226-255` on `main` (`51e2af7`). Its whole-log branch (`:232-234`) runs only when `selected()` returns `None`, that is when triage's output has no `Capabilities:` line. The filtering (`:235-243`), the trimmed "Decision log" block (`:244-246`) and the "Decision index" section with its `grep` instruction (`:247-255`) follow. Callers: spec writer `:273`, critic `:292`, planner `:315`.
- The capability index note, `CAPABILITY_INDEX_NOTE` at `factory/compose.py:138-142`, tells the writer and critic that citing a capability's path sends "the decisions that name it to the critic and the planner". After this change every decision reaches those roles whatever is cited (Decision 2).
- Today's behaviour, from the fixture `t0036-store.sh` that current truth `role-inputs` defines, run on `main` with a throwaway HOME. The fixture's log has four lines: OWN-LINE (this ticket), BETA-LINE and GAMMA-LINE (naming those capabilities), OTHER-LINE (another ticket, naming none, the T-0003 case). With `Capabilities: beta`, the NEW scenario's command prints:
  ```
  W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1
  C: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1
  P: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 source=1
  ```
  OTHER-LINE reaches no role, and the writer misses GAMMA-LINE too.
- Size of the decision part of each spec writer, critic and planner input, measured for a new ticket (no decisions of its own) with a script that mirrors `compose.py:226-255` line for line and the whole-log heading (`scratch/measure.py` of this run). It selected every current-truth capability, and still no line was kept in full on either store. That confirms the triage count: no decision line names a capability.

  | Store | Log lines | Log size | Before (#75 filter): kept lines | Before: index | Before: total | After (whole log) |
  |---|---|---|---|---|---|---|
  | spec-factory | 109 | 35,991 B | 0 | 12 tickets | 2,581 B | 36,055 B |
  | Nanobot | 254 | 76,342 B | 0 | 27 tickets | 4,874 B | 76,406 B |

  The rise is about 33.5 kB per input on spec-factory and 71.5 kB on Nanobot. That agrees with the operator's estimates of writer input after the change: about 135 kB on spec-factory and about 235 kB on Nanobot.
- Docs that state #75's decision rule today: `docs/design.md:94` (the sentence ending "a decision index for the rest: one line per other ticket, with the `grep` command ..."), and the Spec writer, Spec critic and Planner rows of `README.md:85-87`. The docs scenario's command prints `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0` on `main`. No `docs/prompts/` file and no part of `dev/build-harness.spec.md` names the decision index. `dev/build-harness.spec.md:193` already says `run compose` gives `decisions.md` to the spec writer, critic and planner, with no filter.
- Tests that pin the filter: `tests/factory/test_capability_index.py:192-238` and the note text at `:22` and `:122-126` (Tests to change). `tests/factory/test_decision_log.py:205-215` already expects the whole-log heading and passes before and after.
- Harness suite on `main` with a throwaway HOME: a full run with TMPDIR set inside this repo's `.factory/` gave 380 passed and 4 failed, all 4 in `tests/factory/test_instance.py`, because those tests need a directory outside any factory instance. With the default TMPDIR, `test_instance.py`, `test_capability_index.py` and `test_decision_log.py` give 63 passed. The suite scenario therefore runs with the default TMPDIR.

## Root cause
`add_decisions` in `factory/compose.py:226-255` keeps a decision line only when it is logged against the ticket or names a selected capability, as a whole word. A cross-cutting standing decision names no capability, so for any ticket with a `Capabilities:` line it is reduced to an index entry. The writer, critic and planner then follow only the rules they choose to open.

## Out of scope
- Triage's input: still the capability index and no decision line.
- Which capabilities the writer and critic receive in full, the capability index and its lines, and the triage prompt's `Capabilities:` line. The only change to #75's capability half is one clause of the index note (Decision 2).
- The current-truth requirement "A ticket whose triage output names no capabilities receives today's inputs". It stays true as written.
- `dev/build-harness.spec.md` and every `docs/prompts/` file: none states the decision filter.
- Any new scoping of the decision log, such as #54's product and implementation tagging.
- The contents of `decisions.md`, and the status cell of #78's history rows in `README.md` and `dev/issues.md`, which the operator's `dev:` commits keep.
- The runtime move itself (Operator steps).

## Open questions
none

## Decisions
- The spec writer, critic and planner receive `decisions.md` whole whenever it holds any text, whatever capabilities their ticket names. The decision index and its `grep` instruction are removed. This is the operator's Answer 1, already standing in `decisions.md` as the 2026-10-09 T-0037 line. Rejected: the request's rule of sending lines that name no capability in full and filtering the rest. On today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
- The capability index note loses its clause ", and the decisions that name it to the critic and the planner,"; the rest of the note stays word for word. Rejected: keeping the clause, which would tell the writer that citing a path is how decisions reach the critic and planner. That is no longer so. This edits one sentence of #75's capability half, which the triage assumption kept byte for byte.
- The planner's decision part no longer reads triage's capability names or the approved spec's citations. It reads the whole log, as before #75.
- The decision part is measured in this spec's Evidence, before and after, on both stores. No new file or harness command records it.

## Risk
Blast radius: the input of every spec writer, critic and planner run on every target that adopts this harness revision. Each grows by the size of its log, about 34 kB here and 72 kB on Nanobot per run (Evidence). Triage, implementer, reviewer and verifier inputs do not change. A mistake here would drop decisions from those inputs or break the capability half. The NEW scenario and the two REGRESSION scenarios cover both.
Protected paths touched: harness, `factory/**`, through `factory/compose.py`. The other files changed are `tests/factory/test_capability_index.py` (existing tests, listed under Tests to change), `docs/design.md`, `docs/changelog.md` and `README.md`, none of them protected. No `docs/prompts/` file changes.

## Operator steps
- After merge, move the runtime once so that #75 and this fix ship together, and adopt it in each target with `factory --accept-harness <sha> <command>` (README, "Upgrade").
- On the first spec writer run in each store after that move, check that its `input.md` holds `## Decision log (decisions.md): standing decisions, read-only` and no `## Decision index`.

=== design.md
## Proposed change
A. `factory/compose.py`, the decision log in role inputs.
   1. `add_decisions` (`:226-255`) takes no argument. When `decisions.md` is missing or holds only whitespace it adds nothing, as today. Otherwise it calls `add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")` and returns. Remove the filtering (`:235-243`), the trimmed "Decision log ... logged against this ticket or naming a capability given in full" block (`:244-246`) and the whole "Decision index" section with its `title()` helper and `grep` instruction (`:247-255`).
   2. The callers become `add_decisions()`. For the spec writer (`:273`) and the critic (`:292`) they stay right after `add_truth(sel)`, so the log still follows current truth and the capability index. The planner (`:315`) no longer calls `selected()`. Its comment says the planner gets no current truth and the whole log.
   3. `CAPABILITY_INDEX_NOTE` (`:138-142`) becomes, word for word: "This list is complete: every current-truth capability not given in full above has one line here. Open a capability at its path before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, sends that capability in full to the critic, so cite under Evidence each capability you open."
   4. `selected()`, `add_truth()`, the capability index and the triage branch stay as they are. `input_sources` lists `decisions.md` for these three roles whenever the log holds text, as the `add` helper already does.
B. `tests/factory/test_capability_index.py`: replace the decision-filter tests (Tests to change) with tests of the whole log: with `Capabilities: beta`, and with `Capabilities: none`, each of the spec writer, critic and planner inputs holds the whole-log heading followed by every fixture line, and no `Decision index`. Update the module docstring and the note text. Keep `test_a_whitespace_only_log_still_adds_nothing` and the part-B4 test as they are.
C. Documents.
   1. `docs/design.md:94`, §Harness, "Spec store" paragraph. Replace its last two sentences, from "They and the planner receive the decision log's lines ..." to the end, with: "They and the planner receive the whole decision log, `decisions.md`, when it holds any text, whatever capabilities the ticket names: a standing decision often names no capability, yet every ticket must follow it. A ticket whose latest triage output has no `Capabilities:` line gets every current-truth spec in full."
   2. `README.md`, the role table.
      - Spec writer row (`:85`): replace "the decision log's lines for this ticket and those capabilities, and a decision index for the rest, one line per other ticket" with "the whole decision log".
      - Spec critic row (`:86`): replace "the decision log's lines for this ticket and those capabilities, and a decision index for the rest" with "the whole decision log".
      - Planner row (`:87`): replace "the decision log's lines for this ticket and its capabilities, and a decision index for the rest" with "the whole decision log".
      - Bump the Status line's date to the day of the change, per "Maintaining this page". The terms row for "ruling, decision log" (`:128`) is already true and stays.
   3. `docs/changelog.md`: add entry 61 after entry 60, in that list's form, starting `61. After issue #78 (2026-10-09), where`. It says what went wrong: #75's filter reduced every decision of another ticket to an index line, because no line names a capability, and in the replay a writer broke a cross-cutting decision while the critic missed it. It says what changed: the three roles receive the whole log again, the decision index and its `grep` command are gone, and the capability index stays. It gives the size change from the Evidence table: 2.6 kB to 36.1 kB here, 4.9 kB to 76.4 kB on Nanobot. It names the rejected alternative, the request's rule of filtering only lines that name a capability (Decision 1).

## Tests to change
- `tests/factory/test_capability_index.py:1-9`, module docstring: says the writer, critic and planner get only the decision lines of their ticket and capabilities, plus an index. Follows Decision 1.
- `tests/factory/test_capability_index.py:22` (`CITES`) and `:122-126` in `test_writer_gets_the_named_capability_in_full_and_an_index_line_for_each_other`: pin the note clause that Decision 2 removes.
- `tests/factory/test_capability_index.py:194-203`, helpers `decision_block` and `decision_index`: build the trimmed-log heading and the decision index that Decision 1 removes.
- `tests/factory/test_capability_index.py:206-217`, `test_each_role_gets_its_ticket_s_and_its_capabilities_decisions_and_an_index_of_the_rest`: expects OTHER-LINE left out and an index. Follows Decision 1 (and Decision 3 for the planner).
- `tests/factory/test_capability_index.py:220-224`, `test_a_decision_index_line_carries_the_ticket_s_title`: the index no longer exists. Follows Decision 1.
- `tests/factory/test_capability_index.py:227-232`, `test_no_kept_line_leaves_only_the_index_and_no_decisions_source`: expects no `## Decision log` and no `decisions.md` source with `Capabilities: none`. Both now appear. Follows Decision 1.
- `tests/factory/test_capability_index.py:235-238`, `test_every_line_kept_leaves_no_decision_index`: expects the trimmed-log heading. Follows Decision 1.

=== specs/role-inputs/spec.md
## REMOVED Requirements
### Requirement: The spec writer, critic and planner receive in full only the decisions of their ticket and its capabilities, and a decision index for the rest
Reason: the filter hid every cross-cutting standing decision, because no decision line names a capability; the three roles receive the whole decision log instead (the operator's answer to #78).

## ADDED Requirements
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

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents describe the whole decision log for the spec writer, critic and planner
`docs/design.md` and the README's Spec writer, Spec critic and Planner rows MUST say that those roles receive the whole decision log, and neither MUST mention a decision index. `docs/changelog.md` SHALL have an entry for issue #78, with no whitespace error in the change.

#### Scenario: The design, README and changelog describe the whole decision log and no decision index
- WHEN `(echo "design-index=$(grep -c 'decision index' docs/design.md) design-whole=$(grep -c 'They and the planner receive the whole decision log' docs/design.md) readme-index=$(grep -c 'decision index' README.md) readme-whole=$(grep -E '^\| (Spec writer|Spec critic|Planner) \(' README.md | grep -c 'the whole decision log') changelog=$(grep -c '^[0-9]*\. After issue #78 ' docs/changelog.md)"; git diff --check main...HEAD && echo whitespace=ok)`
- THEN it prints exactly `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`, then `whitespace=ok`

=== verification.md
## Acceptance
- With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does → NEW; on `main` (`51e2af7`) it prints `W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1`, `C: ... gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 ...` and `P: ... other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 ...` (Evidence): OTHER-LINE is missing from all three and a decision index is present.
- The capabilities each role receives and triage's input are unchanged by the whole log → REGRESSION; on `main` it prints exactly the expected four lines (run through the fixture with a throwaway HOME).
- The harness suite passes with the whole decision log → REGRESSION; on `main` the full suite gave 380 passed and 4 failed with TMPDIR inside `.factory/`, and those 4 (`test_instance.py`) pass with the default TMPDIR (Evidence).
- The design, README and changelog describe the whole decision log and no decision index → NEW; on `main` it prints `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high. I ran every scenario's command on `main` through the role-inputs fixture with a throwaway HOME, measured both stores with a mirror of the filter code, and checked each cited line on this checkout.
ESCALATIONS: none
