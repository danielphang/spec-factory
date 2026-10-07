## Review of T-0033 spec v1 (round 1)

What I checked myself, on `main` at `d226a4d` (`git rev-parse --short HEAD`), with a throwaway `HOME` and `TMPDIR` set to this run's scratch directory:

- Cited paths and lines. `factory/cli.py` `merge_cmd` is lines 645-687 and reads no changed path, no `protected_paths` and no spec. The `--ruling` branch of `resolve` (lines 866-876) sends every ESCALATE whose reason lacks "planner" to `ready-for-critic`. Check 6 of `factory/prompts/reviewer.md`, `docs/prompts/06-code-reviewer.md` and the §6 block of `docs/design.md` ends "the merge gate will require a human approval" at the lines cited. `docs/design.md` lines 21, 23, 47, 48, 105, 109, 139, 154 and 387, `dev/build-harness.spec.md` lines 246 and 377, `factory/prompts/spec_writer.md` line 80 and `factory/workflows/build.js` lines 194-200 hold the text the spec quotes. `factory/workflows/build.js` line 56 exposes a refusal's JSON `error` on the clerk result, so part B's `m.error.startsWith('BLOCKED ')` has something to read, in the same form the run-start check already uses at lines 81-84.
- Acceptance commands. The GIVEN fixture ran as written (41 lines). Merge-gate scenario 1 printed `exit=0 blocked=0 named=0 declared=0 main=moved merged`: today the undeclared `core/b.py` and `bin/tool` merge. Human-resolution scenario 4 printed `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`: the reviewer's escalation ruling goes to the critic with the ESCALATE row still in place. Both match verification.md.
- Git semantics the design relies on. In a scratch repository, `git diff --name-only --no-renames main...H` on a rename lists `core/b.py docs/b.py`; `-- ':(glob)core/**'` lists `core/a.py` and `core/new/c.py`, `':(glob)core/*'` lists only `core/a.py`, and `':(glob)~/.secret/**'` lists nothing and exits 0. A bare directory entry (`core`, `core/`) under glob magic also matches its files, so a declared directory works.
- Rubric 1, tests pinning overturned behaviour. `grep -rn "ESCALATE from reviewer" tests/factory/` finds nothing. `test_resolve_rulings.py` line 98 parametrises only `ESCALATE from critic` and `ESCALATE from planner`. No merge test's branch changes a path the fixture instance (`.factory/instance.yaml`, `.factory/harness.lock`, `.factory/context.md`) or the template protects. "Tests to change: none" holds.
- Evidence figures. The last 20 first-parent merges on `main`, diffed with `--no-renames` against this instance's in-repo globs: `merges=20 protected=18`. The Nanobot tickets named in Operator step 2 are all `awaiting-spec-gate` and T-0021 is `planned` (read from `~/dev/nanobot-upstream/.factory/store/tickets/`, nothing written). This instance's T-0026, T-0027, T-0031 are `ready-for-planner` and T-0030 `planned`, as Risk says. Issue #57 is in `dev/issues.md` line 64. The 2026-10-07 T-0033 line is in `decisions.md`.
- Rulings already reach the checkers: `factory/compose.py` lines 249 and 271 add every `ruling-*.md` to the implementer, reviewer and verifier input, so C.2's "as they already do" is true.

The design is sound and the scenarios discriminate: another ticket's declaration, a rename out of the tree, a "Not touched" line, a `*`-for-`**` matcher and an all-backticks reader each fail a scenario. One finding blocks, on the writing standard.

### Findings

[BLOCKING] 6 proposal.md, first paragraph of Evidence, Decisions and Operator steps
Problem: Each of these sections opens with a term specific to this system that no human-facing section has glossed, so the standard's reader has to infer: Evidence paragraph 1 uses "GIVEN block" and "verifier" (the Problem only ever says "both reviewing agents"); Decisions bullet 1 uses "instance" and "`decisions.md`"; Operator step 1 uses "the runtime", "harness revision" and "the Nanobot instance".
Evidence: Read the Problem, Evidence, Decisions and Operator steps as the operator the rubric describes against `docs/writing.md` rules 2 and 6. "instance" first appears at Decisions bullet 1; "runtime" first appears at Operator step 1; "verifier" first appears at Evidence paragraph 1. None is defined anywhere in those sections. The Problem itself is good: its first paragraph says what is wrong and for whom, and glosses protected paths, the merge gate, the operator, sub-tickets and the Risk section.
Suggested fix: One sentence each, where the term first appears: name the two checking agents in the Problem (the reviewer reads the diff, the verifier runs the tests) and use those names from then on; say an instance is one repository the factory runs on, and `decisions.md` its standing-decision log; say the runtime is the pinned checkout of the harness that each instance has accepted, and that "the Nanobot instance" is the fork at `~/dev/nanobot-upstream`; write "the fixture script this spec gives" instead of "GIVEN block" in Evidence.

[SHOULD-FIX] 6 proposal.md, Problem and Evidence
Problem: Two concepts carry two names each, against rule 9: the Problem says "the main branch", Evidence and Decisions say "the integration branch"; the Problem says "reviewing agents", later text says "reviewer", "verifier", "checkers" and "checks".
Evidence: Problem paragraph 1 ("merged into the main branch") against Evidence bullet 1 ("the integration branch moved") and Decisions bullet 4 ("`<integration>`"). Problem paragraph 1 ("both reviewing agents") against Evidence paragraph 1 ("reviewer and verifier") and Decisions bullet 8 ("The checkers that re-run").
Suggested fix: Pick "integration branch (the branch the factory merges into, `main` here)" at first use and keep it, and name reviewer and verifier once (see the blocking finding) so "checkers" can be dropped or introduced as "the two checkers, reviewer and verifier".

[SHOULD-FIX] 4 proposal.md Decisions bullet 2 and design.md D.2
Problem: A brace list such as `factory/prompts/{preamble,planner}.md` passes the regular expression as one entry, git does not expand it, so the spec writer's habit the Evidence documents would produce a declaration that parks every sub-ticket touching those files, and nothing in the spec-writer FORMAT line or the Decisions says one path or glob per entry.
Evidence: Evidence bullet 5 records T-0022's brace list. The regex in A.1 accepts `` `[^`]+` `` for an entry. The proposed FORMAT line in D.2 shows the shape but gives no rule against brace lists. My scratch check: `:(glob)` matches `*` and `**` only; a brace is literal.
Suggested fix: Add to the FORMAT line's third row, or a fourth, "one path or glob per entry; no brace lists", and one clause in Decisions bullet 2 saying a brace list is one literal entry that matches nothing.

[NIT] 2 specs/merge-gate/spec.md and specs/human-resolution/spec.md
Problem: Three branches in the design have no scenario: the refusal's "(<id> has no approved spec)" wording in A.2 for a ticket with no parent and no approved spec, and the two secondary refusals of `--accept-paths` in C.1 (head not the branch tip; no undeclared path left).
Evidence: The only no-parent merge fixture in current truth (`t0025-gate.sh`) changes `x.txt`, which no instance protects, so the first branch is exercised nowhere; no scenario exercises the other two.
Suggested fix: Leave the acceptance list as it is and let the new test file cover the three in one or two cases, or say in design.md that the new test file covers them.

[NIT] 5 design.md E.1
Problem: After E.1, piece 9 of `docs/design.md` (line 49, "Human surface") still says people "review protected PRs", a per-PR review this change removes.
Evidence: `sed -n 49p docs/design.md`: "Where people approve specs, answer escalations, review protected PRs, reply to requesters, and read the weekly audit sample."
Suggested fix: Add to E.1 a one-line change of that phrase to "answer a merge refused for an undeclared protected path", or leave it and say so.

Out-of-scope observations: `dev/build-harness.spec.md` lines 208 and 314 still list `approve-pr` and `approvals/ID/pr-SHA.yaml`; they stay correct for guardrail paths, which keep their per-PR approval, so nothing to change here. The T-0032 decision line of 2026-10-07 attributes the T-0028.1 by-hand ruling to issue #41's budget-kill and EMPTY-OUTPUT route; this spec, with the ruling file as evidence, shows it was a reviewer ESCALATE misroute. Someone may want to amend that line later.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high; every cited line, both reproduced scenarios, the git pathspec behaviour, the 18-of-20 count and the test search were checked on `d226a4d`, and the one blocking finding is a writing-standard gap whose fix is a few sentences.
ESCALATIONS: none
