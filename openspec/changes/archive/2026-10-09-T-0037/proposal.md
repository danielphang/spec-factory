## Problem
Since issue #75, a recent change that trimmed each agent's input to save context, three agent roles can miss a standing rule that every ticket must follow. Those roles are the spec writer, which writes a ticket's spec; the critic, which reviews it; and the planner, which splits an approved spec into pieces of work. The rules sit in the decision log, `decisions.md`, one line per standing decision with its date and the ticket that made it. Since #75, a decision line reaches those roles in full only when it was logged against their own ticket, or when its text names a capability they receive in full. A capability is one current-truth spec: the store's record of how one part of the system behaves today, where the store is the factory's per-repository record of tickets, specs and decisions. Every other line is reduced to one entry per ticket in a "decision index", with a `grep` command the role may run to read it.

No decision line in either store names a capability, so the filter hides every rule that some other ticket made. In the operator's replay of a Nanobot ticket, the spec writer put new code in a module that a standing decision rules out, and the critic did not notice. Both had seen that decision only as an index line. The operator has chosen to send the whole decision log to these three roles again and to keep the rest of #75, the capability filter. The cost is about 34 kB more input per run on this repo's store and about 75 kB more on the Nanobot store.

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
  `other=0` on every line: OTHER-LINE reaches no role. `gamma-line=0` for W: the writer misses GAMMA-LINE too. `index=1 grep-cmd=1`: each role gets a decision index with its `grep` command.
- Size of the decision part of each spec writer, critic and planner input, measured on 2026-10-09 for a new ticket with no decisions of its own. The script mirrors `compose.py:226-255` line for line and adds the whole-log heading for "After" (`scratch/measure.py` of this run). It selected every current-truth capability (11 here, 25 on Nanobot), and still kept no line in full on either store. That confirms the triage count: no decision line names a capability. The Nanobot store is live, so its log will have grown by the time this ships.

  | Store | Log lines | Log size | Before (#75 filter): kept lines | Before: index | Before: total | After (whole log) |
  |---|---|---|---|---|---|---|
  | spec-factory | 109 | 35,991 B | 0 | 12 tickets | 2,581 B | 36,055 B |
  | Nanobot | 266 | 79,997 B | 0 | 27 tickets | 4,875 B | 80,061 B |

  The rise is about 33.5 kB per input on spec-factory and 75 kB on Nanobot. That is in line with the operator's estimates of writer input after the change: about 135 kB on spec-factory and about 235 kB on Nanobot.
- Docs that state #75's decision rule today: `docs/design.md:94` (the sentence ending "a decision index for the rest: one line per other ticket, with the `grep` command ..."), and the Spec writer, Spec critic and Planner rows of `README.md:85-87`. The docs scenario's command prints `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0` on `main`: the design doc and all three README rows still describe the decision index, and no changelog entry for #78 exists. No `docs/prompts/` file and no part of `dev/build-harness.spec.md` names the decision index. `dev/build-harness.spec.md:193` already says `run compose` gives `decisions.md` to the spec writer, critic and planner, with no filter.
- Tests that pin the filter: `tests/factory/test_capability_index.py:192-238` and the note text at `:22` and `:122-126` (Tests to change). `tests/factory/test_decision_log.py:205-215` already expects the whole-log heading and passes before and after.
- Harness suite on `main` (`51e2af7`), with a throwaway HOME and the default TMPDIR: the suite scenario's command printed `suite=0`, with `384 passed in 229.97s`. With TMPDIR set inside this repo's `.factory/`, 4 tests in `tests/factory/test_instance.py` fail, because they need a directory outside every factory instance; the suite scenario therefore runs with TMPDIR unset or outside any instance.

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
Blast radius: the input of every spec writer, critic and planner run on every target that adopts this harness revision. Each grows by the size of its log, about 34 kB here and 75 kB on Nanobot per run (Evidence). Triage, implementer, reviewer and verifier inputs do not change. A mistake here would drop decisions from those inputs or break the capability half. The NEW role-inputs scenario and the two REGRESSION scenarios cover both.
Protected paths touched: harness, `factory/**`, through `factory/compose.py`. The other files changed are `tests/factory/test_capability_index.py` (existing tests, listed under Tests to change), `docs/design.md`, `docs/changelog.md` and `README.md`, none of them protected. No `docs/prompts/` file changes.

## Operator steps
- Merging this change does not by itself change what the roles receive. Tickets run from the runtime, a separate checkout of the harness pinned to one commit (`~/dev/spec-factory-harness`), and a merge into `main` never moves it. #75 is merged but held from the runtime until this fix merges. After merge, move the runtime once to the merge commit, so that #75 and this fix ship together (README, "Upgrading the runtime", step 1).
- Each target repository runs only the harness commit recorded in its `harness.lock`, and refuses its store after a runtime move until it accepts the new commit. In each target that should adopt this change, run any store command once with `--accept-harness <sha>`, where `<sha>` is the runtime's new commit (README, "Upgrading the runtime", step 2).
- On the first spec writer run in each target after that, check that its `input.md` holds `## Decision log (decisions.md): standing decisions, read-only` and no `## Decision index`.

