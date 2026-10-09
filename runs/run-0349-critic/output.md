Spec critic, T-0037 v1 (issue #78: the spec writer, critic and planner get `decisions.md` whole again).

What I checked, on `main` (`51e2af7`), with a throwaway HOME:
- `factory/compose.py:138-142` is `CAPABILITY_INDEX_NOTE` with the clause ", and the decisions that name it to the critic and the planner,"; `:226-255` is `add_decisions`, whose whole-log branch at `:232-234` runs only when `selected()` (`:205-213`) returns `None`, that is when triage wrote no `Capabilities:` line; filtering `:235-243`, trimmed heading `:244-246`, index with `grep` `:247-255`; callers at `:273`, `:292`, `:315`. All as the spec cites.
- `tests/factory/test_capability_index.py`: docstring `:1-9`, `CITES` at `:22` used only at `:125`, helpers `:194-203`, the four decision tests `:206-238`. These are the only tests in `tests/factory/`, `factory/`, `docs/prompts/` and `agents/` that pin the trimmed heading, the index or the note clause (grep for `Decision index`, `decision_index`, `naming a capability given in full`, `decisions that name it`). `test_a_whitespace_only_log_still_adds_nothing` (`:241`) and the part-B4 tests (`:248` on) assert the whole-log heading and no index, so they pass after the change. `tests/factory/test_decision_log.py:205-215` expects the whole-log heading. "Tests to change" is complete and names only tests the change breaks.
- Docs: `docs/design.md:94` holds the two sentences C.1 replaces and is the file's only `decision index` match; `README.md:85-87` are the three rows and the only three matches; `README.md:9` is the Status line, `:963` "Maintaining this page"; `docs/changelog.md:64` is entry 60, no entry 61 exists. `dev/build-harness.spec.md:193` does say `run compose` gives a non-empty `decisions.md` to the writer, critic and planner, with no filter. No `docs/prompts/` file mentions the index.
- Ran the harness-docs scenario as given: `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`. Matches Evidence and the NEW claim.
- Ran the NEW role-inputs scenario through the `t0036-store.sh` fixture from current truth: the three lines match the Evidence block byte for byte (`other=0 whole=0 index=1 grep-cmd=1`, `note-decisions=1` for W and C, `0` for P). It fails today for the stated reason, and a stub that only drops the index without adding the whole log would still fail (`whole=0`, `other=0`).
- The standing decision exists: `.factory/store/decisions.md` last line is the 2026-10-09 T-0037 line the spec quotes. The spec's Decision 1 restates it; no hidden product choice.
- Sizes: this repo's log is 109 lines, 35,991 B, as the table says. The Nanobot log is 266 lines, 79,997 B today (read-only `wc`), not 254 / 76,342 B.
- Not checked: the suite scenario and the post-change outputs of the two role-inputs scenarios, which need the build; the implementer and verifier run those. Scenario 2's REGRESSION claim rests on `add_truth` and the note's remaining text, which A.3 and A.4 keep, so I expect it to hold.

Findings

[BLOCKING] 6 Operator steps, first bullet
Problem: "move the runtime once" and "`factory --accept-harness <sha> <command>`" are terms specific to this system that no human-facing section glosses, so an operator new to the system cannot tell from the spec why merging the PR does not by itself change what the roles receive, or what "moving the runtime" is.
Evidence: Problem, Evidence, Decisions and Operator steps never say what the runtime is; the only hint is the Out of scope line "The runtime move itself". `docs/writing.md:32` requires a gloss at first use.
Suggested fix: open the bullet with a clause such as "The factory runs from a separate runtime checkout that a merge into `main` does not change; after merge, move that runtime once ... and adopt the new revision in each target with `factory --accept-harness <sha> <command>` (README, 'Upgrade')".

[NIT] 1 Evidence, size table, Nanobot row; design.md C.3 (changelog figures)
Problem: the Nanobot log is 266 lines and 79,997 B today, so the table's 254 / 76,342 B and the changelog's "76.4 kB" are already stale; the store is live and will drift further.
Evidence: `wc -lc ~/dev/nanobot-upstream/.factory/store/decisions.md` → `266 79997`.
Suggested fix: date the measurement in the table caption ("measured 2026-10-09") and round the changelog figures to "about 36 kB here and about 80 kB on Nanobot", or state them as of that date.

[NIT] 6 Problem, first paragraph
Problem: "the store" is used inside the gloss of capability ("the store's record of how one part of the system behaves today") without being glossed itself.
Evidence: no earlier sentence says what the store is.
Suggested fix: "the store, the factory's per-repo record of specs, tickets and decisions".

No finding on scope: one PR, the out-of-scope list is sensible, every protected path touched (`factory/compose.py`) is declared under Risk, and Decision 2's one-clause edit to #75's note is called out rather than made silently. No conflict with the role-inputs current truth that stays (the no-`Capabilities:` requirement remains true) or with #54, which the T-0037 decision line already constrains.

STATUS: REVISE
CONFIDENCE: high, the one blocking item is a missing gloss with a one-clause fix; every cited path, line range, test and today's output of both NEW scenarios checked out.
ESCALATIONS: none
