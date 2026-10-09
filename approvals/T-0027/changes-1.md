# Changes requested on T-0027 (#44), operator, 2026-10-09 (backlog review)

#50 was merged into #44 at the backlog review. Re-spec T-0027 to include it, and update the evidence.

1. Fold in #50: `spec amend` declares intent. An intent-unchanged amendment (setup, precondition, wording) is amended in place and logged. An intent change is refused, with a note on what is merged and what a restart discards, and goes to re-plan or re-file.
2. Add a drift check at build start. Before a sub-ticket's first implementer run, check that its acceptance scenarios and the pinned spec's "Tests to change" still hold against the current integration branch. Two things count as drift: a test that changed or was added since the spec was pinned and pins behaviour the spec changes, and a scenario that names a sibling which cannot merge yet. A drift parks the piece with a named reason, so the operator can amend before an implementer run is spent.
3. Evidence to add: Nanobot T-0031 (SPEC-34) closed 2026-10-09 at 15.1M tokens across intake and five build passes, mostly from cross-ticket ordering. One acceptance named a sibling that could not merge yet (SPEC-DEFECT, then a redispatch). Two blocks were tests from an earlier ticket or a sibling that pinned exact output (8 T-0027 tests, 1 sibling test). Several catch-up rounds came from T-0027 merging alongside. Also spec-factory T-0032.1 (#41), blocked on a test #48 had added after its spec was written.
4. Since #57 is live, the Risk section declares its protected paths on the `Protected paths: ` line.
5. Keep the critic check for cross-ticket dependencies that #44 already specifies.
