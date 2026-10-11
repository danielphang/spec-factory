Round 2 review of T-0043 spec v2 (`factory stats` and the once-per-message-id cost count). Per the convergence rule I reviewed the resolution of my round-1 findings and the text the v1→v2 diff changed; unchanged text was not re-reviewed.

What I checked, from `~/dev/spec-factory` at `main` `5215c5f` (clean tree):
- The new Evidence claims about `park.corrected`: `grep -rIn park.corrected factory bin tests` prints nothing, as stated. The live log has exactly one such event, at `.factory/store/log/` line 2158, `ts 2026-10-10T17:18:37+00:00`, ticket T-0040.3, with `previous`, `reason` and `by`. The Nanobot store's log has zero (`grep -c`, read only). The one real correction's `previous` equals, character for character, the reason of the single earlier `ticket.parked` on T-0040.3 (2026-10-10T07:12:26), so the Decisions' exact-match rule would apply it; and both the park and the correction are dated after the live scenario's cut (2026-10-07T12:00), so the live-store lines do not move, as the scenario's new note says.
- The new fixture lines: sourced the GIVEN block from my scratch directory through the wrapper. The s1 log holds the two `park.corrected` events at 2026-10-02T15:00 and 2026-10-09T12:00 with the stated `previous` texts, and the 10-02 correction's `previous` equals the 10-02T14:00 park's reason.
- The changed parks THEN by hand against the Decisions: with `--until 2026-10-08` the 10-02 correction applies (its park becomes `BLOCKED from harness: spec drift: tests/test_a.py ... <sha> ... <sha>`, cut to `BLOCKED from harness: spec drift`), the 10-09 correction is dated after `--until` and does not (`budget kill: reviewer` stays), the T-0003 park of 10-09 is outside the window, and s2 adds one `NEEDS-HUMAN from triage`. That gives 9 parks and, by count descending then code point (`BLOCKED from harness` < `BLOCKED from implementer` < `archive` < `archive: no spec store...` < `budget...` < `operator...` < `sub-ticket...`), exactly the seventeen lines stated. The decision rows are untouched by the new events.
- Acceptance commands run on `main` through the wrapper with the fixture: the parks scenario prints `exit=2` only, and `.venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |'` prints `| critic | fable-5 | 1 | 5 | 725 | 33 |`, both as verification.md states.
- The glosses: `FACTORY_STATE` is now defined where first used in Decisions, and the wrapper where first used in Evidence. The new `park.corrected` term is introduced in Evidence ("A human can correct a park's reason after the fact") before Decisions relies on it.
- Approved changes not yet archived: none, so rubric 5 raises nothing new.

What I could not check: the writer's `scratch/p.py` and its live-store output (another run's scratch directory; I run no suite and build nothing), and the two guard-side NEW scenarios, which need the change. Section C and D are unchanged and, as the writer says, read none of the new events.

Findings: none.

Prior findings (round 1):
- [BLOCKING] 6, `FACTORY_STATE` and "wrapper" unglossed → RESOLVED. Both glossed at first use in Decisions and Evidence (diff lines 1892, 1922).
- [SHOULD-FIX] 4, `park.corrected` not handled → RESOLVED. A rule is decided (count under the latest correction dated before `--until`, matched by ticket and exact `previous`; rejected options stated), carried into the requirement text, design part B, part D's tests and the fixture, with one applied and one post-window correction. The real event on record satisfies the exact-match rule.
- [SHOULD-FIX] 2, the live-store scenario is a snapshot → RESOLVED. The scenario now dates its lines (2026-10-11) and tells the verifier how to separate a store edit from a defect. Keeping it as acceptance is a defensible reading of the request; the only correction on record is after the cut.
- [NIT] 1, ten gate edits → RESOLVED ("nine ... and one an amendment", source quoted).
- [NIT] 6, "Written by" for an amendment → RESOLVED (`human` for any non-run source, `unknown` for no `spec.added` event).

Out-of-scope observations:
- The writer's observation on live-store-guard's second requirement (its "read-only list above" wording now also covers `drive`, and after this change `stats`) still stands; nothing more from me.

STATUS: APPROVE
CONFIDENCE: high. Every round-1 finding is addressed in the text; the new correction rule was checked against the one live event and the fixture by hand; two acceptance commands run on main print the stated output. The live figures and the guard scenarios still need the build.
ESCALATIONS: none
