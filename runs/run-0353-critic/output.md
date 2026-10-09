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

STATUS: APPROVE
CONFIDENCE: high, every round-1 finding is fixed as described, every changed figure and cite re-checked against the repo and both stores, and both NEW scenarios still fail today for the stated reason.
ESCALATIONS: none
