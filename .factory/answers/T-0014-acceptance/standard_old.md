# Writing standard

The spec factory's agents write most of their output for other agents. Some of it is read by a
person, and that person decides on it: the operator approving a spec at the spec gate (the one
point where a human signs off a design before code is written), a reviewer reading a PR
description, anyone answering an escalation (a problem an agent hands to a human). This page is
how to write for that person.

**The reader.** Technical: knows databases, locks, RPCs, agents and context windows. New to this
system: has not read the design document and does not know the factory's names for things. If the
target repository's briefing (the text every role reads first) names a different reader, write
for that reader instead.

**Scope.** Every section a person reads: a spec's Problem, Evidence, Open questions, Decisions and
Operator steps; a PR description's What changed and Known gaps; each ESCALATIONS item; a
NEEDS-HUMAN question; and a retro proposal. Everything else is written for the next agent.

Each rule below is one you can check in your own output before you hand it in. Each has an
example taken from the factory's own writing, and its rewrite.

## 1. The first paragraph says what is wrong, or what this is, and for whom.
Check: a reader who stops after the first paragraph can say what the problem is and who has it.
Before (operator review of the overview draft, 2026-10-03, finding 3): the page opened on the
system's parts as if its reader already knew the project; the operator's note was "consider
audience and what they know and don't know".
After: "Spec Factory turns a written request into merged, tested code, using a chain of AI agents
and a few human sign-offs. This page is for an engineer seeing the project for the first time."

## 2. A term specific to this system is glossed at first use with what it does or why it exists.
Check: underline every name the factory made up; the first use of each says what it does.
General technical concepts are not glossed.
Before (operator review of the overview draft, 2026-10-03, finding 1): `--accept-harness` appeared
as a node in a diagram with no statement of what requires it.
After: "Each target repository runs only the harness commit it has accepted, recorded in its
`harness.lock`. When the harness is upgraded, the operator accepts the new commit for that
repository with `--accept-harness <commit>`; until then the harness refuses to run there."

## 3. One idea per sentence; no parenthetical holds a second idea.
Check: delete each parenthetical; if the sentence loses a claim, that claim needs its own sentence.
Before (operator review of the overview draft, 2026-10-03, finding 2): "the build half in
local-commit mode (no remote, no PR, no CI service: the verifier runs the instance's
`gate_commands` and its result is the `ci` row; …)".
After: "The build half commits locally. There is no remote, no PR and no CI service. The verifier
runs the repository's check commands and records the result where a CI result would go."

## 4. A diagram comes after the words needed to read it, with a caption that states its one claim.
Check: every box and arrow is named in the text above the diagram, and the caption is one claim.
Before (run-0054-planner, the T-0012 plan): "Order and parallelism:" followed directly by an
ASCII graph of six sub-ticket ids joined by arrows, with no caption; what an arrow meant came in
the bullets after it.
After: "An arrow means 'must merge before'. Sub-tickets .1 and .2 run in parallel; .3 waits for
both; .6 merges last." Then the graph, captioned "Part E (.6) is the last change to harness code."

## 5. A command is shown with what its output shows.
Check: every quoted output is followed by what it means for the claim it supports.
Before (run-0052-spec_writer, Evidence): "docs-moved-and-split printed `old_tracked=0`;
changelog-moved-verbatim printed `SAME` / `declined=1 numbering=CONTIGUOUS in_design=0`".
After: "docs-moved-and-split printed `old_tracked=0`: no file is still tracked at an old path.
changelog-moved-verbatim printed `SAME`: the moved changelog matches the old one entry for entry;
`numbering=CONTIGUOUS`: its entries are numbered with no gaps."

## 6. Project-internal references are introduced, or moved to a closing note.
Check: each ticket id, issue number, answer or decision id, session name or person is either
introduced by what it is, or appears only in a closing note.
Before (run-0014-triage, ESCALATIONS): "A3: Answer 1's "whole word `none` (word boundary)" would
also match `None of …`".
After: "A3 (what counts as a `none` answer): the operator's first answer said "whole word `none`",
which would also match `None of …`."

## 7. Lead with the problem; the mechanism comes second.
Check: the first sentence says what is broken or what the reader must do; the how comes after.
Before (run-0062-verifier, ESCALATIONS): "Stale branch base, which is a harness/process issue.
The verifier was given base `20849b6`, but the head forks at `cdb1c67` …, so the instance's
second gate … cannot pass on this head as built."
After: "The test gate cannot pass on this branch: it was cut from `main` before the change it
depends on merged. Decide: update the branch and re-verify, or accept the trial-merge evidence."

## 8. State a choice and the alternative rejected; do not write an essay defending it.
Check: one sentence for the choice, one for each alternative rejected and why.
Before (run-0054-planner, opening paragraph): six sentences on how each part is reviewed
differently, why merging any two "would mix those review modes in one diff", and why D and F,
though small enough to merge, stay separate.
After: "Six sub-tickets, one per lettered part. Rejected: merging the renames (D) with the design
prose (F), because the prose edits would hide inside a rename diff."

`README.md` is a worked example of these rules applied to a whole page.
