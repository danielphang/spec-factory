## Acceptance
- With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does → NEW; on `main` (`51e2af7`) it prints `W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1`, `C: ... gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 ...` and `P: ... other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 ...` (Evidence): OTHER-LINE is missing from all three and a decision index is present.
- The capabilities each role receives and triage's input are unchanged by the whole log → REGRESSION; on `main` it prints exactly the expected four lines (run through the fixture with a throwaway HOME).
- The harness suite passes with the whole decision log → REGRESSION; on `main` (`51e2af7`) with a throwaway HOME and the default TMPDIR it printed `suite=0` (384 passed).
- The design, README and changelog describe the whole decision log and no decision index → NEW; on `main` it prints `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`.

## Responses
- [BLOCKING] Operator steps, runtime and `--accept-harness` not glossed → FIXED. The first Operator step now says what the runtime is (a separate checkout of the harness pinned to one commit, which a merge into `main` never moves) and why merging alone changes nothing. A new second step says what `harness.lock` and `--accept-harness <sha>` do. Both cite README "Upgrading the runtime" (`README.md:539-545`), whose steps they follow.
- [NIT] Nanobot size figures stale → FIXED. Re-measured on 2026-10-09 with the same mirror script: Nanobot is 266 lines and 79,997 B, before 4,875 B (27 tickets indexed, 0 lines kept), after 80,061 B; spec-factory unchanged at 109 lines, 2,581 B before and 36,055 B after. The table caption is dated and notes the Nanobot log is live. The Problem and Risk figures moved from 72 kB to 75 kB. Changelog part C.3 now gives rounded figures as of that date: under 3 kB to about 36 kB here, about 5 kB to about 80 kB on Nanobot.
- [NIT] "the store" unglossed in Problem → FIXED. The capability gloss now ends "where the store is the factory's per-repository record of tickets, specs and decisions". I also introduced issue #75 at first use as "a recent change that trimmed each agent's input to save context" (writing standard rule 6).
- Not a finding, but strengthened: the suite REGRESSION claim now rests on a full run, not a subset. On `main` with a throwaway HOME and the default TMPDIR, the suite scenario's command printed `suite=0` (384 passed); Evidence and Acceptance say so.

## Critic rounds

round 1 · spec v1 · run-0349-critic · REVISE

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

round 2 · spec v2 · run-0353-critic · APPROVE

Spec critic, T-0037 v2 (issue #78: the spec writer, critic and planner get `decisions.md` whole again), round 2.

What I checked, on `main` (`51e2af7`), with a throwaway HOME, limited to my round-1 findings and the text that changed:
- Operator steps, first bullet: the claim "#75 is merged but held from the runtime" is true. `deedbb9` (the T-0036.1 merge) is on `main`; the runtime checkout `~/dev/spec-factory-harness` is at `c56388c` and `.factory/harness.lock` holds `9a87c3e`, both before that merge. README "Upgrading the runtime" is the heading at `README.md:539`, with the two steps the bullets follow (`:541-545`). The Responses cite `README.md:539-545`; correct.
- Operator steps, second bullet: `harness.lock` is glossed in the README at `:368` as the accepted harness revision, and the bullet's own gloss ("the harness commit recorded in its `harness.lock`, and refuses its store after a runtime move until it accepts the new commit") matches the briefing's description of the instance's behaviour.
- Evidence, size bullet: `wc -lc` gives 266 / 79,997 B for the Nanobot log and 109 / 35,991 B here, as the table now says. The new capability counts hold: 11 current-truth specs under `.factory/store/openspec/specs/`, 25 under the Nanobot store's. Read-only.
- Evidence, docs bullet: ran the harness-docs scenario as given. `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`. Matches.
- Evidence, today's-behaviour block: wrote the `t0036-store.sh` fixture from current truth into my scratch directory and ran the NEW role-inputs scenario as given. Output matched the spec's three lines byte for byte (`other=0 whole=0 index=1 grep-cmd=1`, `note-decisions=1` for W and C, `0` for P). It still fails today for the stated reason.
- Problem, first paragraph: #75 is now introduced at first use, and "the store" is glossed inside the capability gloss. Read as the operator new to the system: every term specific to this system in Problem, Evidence, Decisions and Operator steps now has a gloss at or before first use.
- Not checked: the suite scenario's `384 passed` (the implementer and verifier run the suite; 380 + 4 from v1's split run agrees with it) and the post-change outputs of the two role-inputs scenarios, which need the build.

Findings

None blocking. The unchanged parts of the spec I reviewed in round 1 (cited paths, Tests to change, Risk, scope, consistency with the T-0037 decision line and the role-inputs current truth that stays) are as they were, and I raise nothing new on them.

Prior findings (round 1):
- [BLOCKING] 6 Operator steps, runtime and `--accept-harness` unglossed → RESOLVED. The first bullet now says what the runtime is and why a merge alone changes nothing; the second says what `harness.lock` and `--accept-harness <sha>` do; both point at the README section that holds the two steps, and that section exists at the cited lines.
- [NIT] 1 Evidence size table, Nanobot row stale → RESOLVED. Figures re-measured and dated, the live-store caveat is stated, the changelog part gives rounded figures as of that date, and Problem and Risk carry the same 75 kB.
- [NIT] 6 Problem, "the store" unglossed → RESOLVED.

## Verifier results

2f3fcef2f7a433585b85e99aedf9302133c01002 · T-0037.1 · VERIFIED · run-0357-verifier
