# Changes requested at the spec gate for T-0036 (#75), operator, 2026-10-08

1. Acceptance must check the index headings' instruction paragraphs, as the critic's SHOULD-FIX on rubric 2 says. The Decisions make those paragraphs the only place a role learns that the list is complete, that it opens a deferred item by its path, and that citing a path hands the capability to the critic. In the existing WHEN commands, count one fixed sentence from each paragraph: the `grep ' <ticket id> '` instruction in the decision index, and the sentence in the capability index saying that citing a path sends that capability in full. Add both to the THEN lines, so a build that emits only the bullet lines fails.
2. Apply the critic's two rubric-6 SHOULD-FIX items: the README bullet in design part C, and the Operator steps. Gloss the terms the critic named.
3. Nothing else changes: same design, same Decisions, same scope.
