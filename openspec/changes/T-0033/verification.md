## Acceptance

Each NEW item's failure today was observed on `main` at `d226a4d` with a throwaway `HOME`, running the WHEN as written, except where an item says otherwise. `main` is now `220ebdc`. That change touches only `factory/compose.py` and adds `tests/factory/test_role_inputs.py`; `git diff --quiet d226a4d 220ebdc -- factory/cli.py factory/workflows/build.js factory/prompts docs dev README.md` exits 0. Rulings still reach the implementer, reviewer and verifier inputs there (`factory/compose.py` lines 278 and 300). I did not re-run the scenarios on `220ebdc` in this round: running the fixture script was refused by this session's tool permissions.

- An undeclared protected path is refused at merge, by name, and nothing merges → NEW. Today it prints `exit=0 blocked=0 named=0 declared=0 main=moved merged`: the merge goes through with `core/b.py` and `bin/tool` undeclared.
- Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing → NEW. Today it prints `exit=0 named=0 main=moved` three times.
- A declared protected path, or an unprotected one, merges with no further approval → REGRESSION. It prints `exit=0 merged` twice today. It guards against a gate that refuses too much, or that chokes on the out-of-repo `~/.secret/**` pattern.
- The build parks a merge refused for protected paths with the gate's reason → NEW. Today it prints `park: harness-bug: merge: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`.
- Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through → NEW. Today it prints `accept=2 parked rows=3 ruling=missing`, then `merge=2 on_main=1`. The first merge already went through, and `--accept-paths` is an unknown argument.
- Accepting paths is refused on any other park and writes nothing → NEW. Today it prints `accept=2 refused=0 parked rulings=0`. Argparse refuses the unknown flag, with no `--accept-paths applies to` text.
- A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling → NEW. Today it prints `ruling=2 parked reason=0`, then `in_input=0`. The merge went through, so the park reason is empty and `--ruling` refuses it.
- A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling → NEW. Today it prints `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`.
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 → REGRESSION. It prints the expected four lines today.
- The reviewer run prompt says what the merge gate checks → NEW. Today it prints `gate=0 promise=1`.
- Every reviewer prompt copy states what the merge gate checks → NEW. Today it prints `gate=0 promise=1` three times, then `copy=SAME fill=unchanged`.
- Every spec writer prompt copy gives the declaration line → NEW. Today it prints `reads=0 form=0 braces=0` three times, then `copy=SAME fill=unchanged`. The `braces` count is new in v2. I did not run the whole scenario, but `grep -c 'no brace lists' docs/design.md docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md` on `220ebdc` printed `0` for each file, so no copy holds the line today.
- The design doc and build spec drop the per-PR approval for protected paths → NEW. Today it prints `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0`. The `piece9` count is new in v2; On `220ebdc`, `grep -c 'review protected PRs' docs/design.md` printed `1`, which is line 49.
- The changelog records issue 57's change without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`.
- README describes the protected-path check and the new resolve verb → NEW. Today it prints `built=0 unstick=0 merges=0`.
- The protected-path change adds no whitespace errors → REGRESSION.

## Responses

- [BLOCKING] 6, unglossed terms in Evidence, Decisions and Operator steps. FIXED. The Problem now names the two agents that check a sub-ticket, the reviewer (reads the diff) and the verifier (runs the test suite and acceptance commands), and glosses instance, harness, park and ruling. Evidence paragraph 1 says "the fixture script this spec gives under the first merge-gate scenario" in place of "GIVEN block", and glosses the build workflow where it first appears. Decisions bullet 1 glosses the pinned spec and `decisions.md` (the factory's log of standing decisions that later tickets must follow); later bullets gloss catch-up run, round count and `checks-in-flight`. Operator step 1 glosses the runtime (the pinned checkout of the harness, `~/dev/spec-factory-harness`), the harness commit each instance accepts in its `harness.lock`, and names the Nanobot instance as the fork at `~/dev/nanobot-upstream`. Step 2 glosses a gate edit.
- [SHOULD-FIX] 6, two names per concept. FIXED. The Problem introduces "the integration branch (the branch the factory merges into, `main` here)", and every later human-facing sentence uses that name. "Reviewing agents" and "checkers" are gone from proposal.md: it says "the reviewer and verifier" throughout, and "recorded results" for what v1 called rows. The design.md resolution-rule text that goes into `docs/design.md` keeps "checks" and "checkers", which are that document's own terms.
- [SHOULD-FIX] 4, brace lists. FIXED. Decisions bullet 2 now says each entry is one path or one glob, and that a brace list is one literal entry that git does not expand, so it declares nothing. D.2's FORMAT gains a fourth line, `one path or glob per entry, no brace lists`. The spec-writer scenario checks it (`braces=1`), and A.1 says an entry goes to git as given. The new test file covers a brace-list entry being refused.
- [NIT] 2, three untested branches. FIXED as suggested. The design.md opening now lists the cases the new test file must cover: the no-approved-spec wording, both secondary `--accept-paths` refusals, plus a fenced `Protected paths:` line and a brace-list entry. The acceptance list is unchanged apart from the two added counts.
- [NIT] 5, piece 9 still says "review protected PRs". FIXED. E.1 changes line 49's phrase to "answer merges refused for an undeclared protected path", Evidence lists line 49 among the per-PR places, and the design-doc scenario checks it (`piece9=0`).
- Change not asked for by a finding: A.1 now reads the Risk section with `specstore.lines_outside_fences`, so a `Protected paths:` line quoted inside a fenced code block declares nothing. This follows the section rule `compose.without_evidence` adopted on `main` since v1 (`220ebdc`). Without it, a spec that quotes an example declaration in its Risk section would authorize the example's paths.
- Critic's out-of-scope note on the 2026-10-07 T-0032 line in `decisions.md`. The note says that line attributes T-0028.1's by-hand ruling to the budget-kill and EMPTY-OUTPUT route, while it was a reviewer ESCALATE misroute. This spec leaves the decision log unchanged. The Evidence bullet "The case that exposed the gap" records the correct cause, with the ruling file as the source.

## Critic rounds

round 1 · spec v1 · run-0316-critic · REVISE

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

round 2 · spec v2 · run-0319-critic · APPROVE

## Review of T-0033 spec v2 (round 2)

What I checked myself, on `main` at `5426ff2` (`git rev-parse --short HEAD`), with a throwaway `HOME` and `TMPDIR` set to this run's scratch directory:

- Where `main` is. The spec says `main` is `220ebdc`; it is now `5426ff2`. `git log --oneline 220ebdc..HEAD` is one commit, and `git diff --stat 220ebdc HEAD` touches only `.factory/answers/T-0030.1-ruling-2026-10-07.md` and one row of `dev/issues.md`. `git diff --quiet d226a4d 220ebdc -- factory/cli.py factory/workflows/build.js factory/prompts docs dev README.md` exits 0, as the Evidence says. Nothing this spec reads or edits has moved since the round-1 evidence.
- New symbols A.1 relies on. `specstore.lines_outside_fences` is `factory/specstore.py` line 77: it yields `(line, in_fence)` and a fence at any indentation toggles. `compose.without_evidence` is `factory/compose.py` line 94 and reads the spec through that generator, cutting a section at a line that starts `## ` or `=== ` only outside a fence. `factory/cli.py` already imports `specstore` (line 21) and uses the generator at line 502, so the implementer has a pattern to copy. The rulings reach the reviewer and verifier inputs at `factory/compose.py` lines 278 and 300, as cited.
- Acceptance commands, run as written. The fixture (41 lines) and merge-gate scenario 1 printed `exit=0 blocked=0 named=0 declared=0 main=moved merged`. The reviewer-escalation ruling scenario printed `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml`, then `in_input=0`. The spec-writer prompt scenario, with the new `braces` count, printed `reads=0 form=0 braces=0` three times, then `copy=SAME fill=unchanged`. The design-doc scenario, with the new `piece9` count, printed `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0`. All four match verification.md's "today" lines, so the writer's unrun v2 items fail today for the stated reasons.
- The code the parts edit is where the spec says: `merge_cmd` at `factory/cli.py` 645 with `MergeLock` at 662; `resolve`'s `--ruling` branch at 865-876 still sends a non-planner ESCALATE to `ready-for-critic`; `factory/workflows/build.js` 194-200 still asks the join again after a refusal and files it as `harness-bug: merge:`. The `--decision` guard at line 826 lists the modes C.1 must extend.
- Tests to change. The test file added since v1, `tests/factory/test_role_inputs.py`, matches `Risk|merge|ruling` on one line, a `## Risk` heading inside its fixture spec text; it exercises no merge or ruling route. `grep -rn 'review protected PRs\|piece-8 approvals' tests/factory/` finds nothing, so the new E.1 edits break no test. "Tests to change: none" still holds.
- Writing standard, read as the operator new to this system. The Problem's first paragraph says what is wrong (undeclared protected-path changes merge) and for whom (the operator who approved a spec that never said so), and now glosses instance, harness, operator, spec gate, sub-ticket, reviewer, verifier, merge gate and integration branch. The first paragraph of Evidence, Decisions and Operator steps each uses only terms the Problem or its own first sentence has glossed. The design.md text that goes into `docs/design.md` keeps that document's "checks" and "checkers", which is right.

### Findings

[NIT] 6 proposal.md, Decisions bullet 9
Problem: "a VERIFIED verifier result with a PASS gate result" uses "gate" for the recorded `ci` row, while every other sentence in these sections uses "the gate" for the merge gate, so one name covers two concepts (rule 9).
Evidence: Decisions bullet 5 ("The gate runs this check") and bullet 6 ("A refusal exits 2") mean the merge gate; bullet 9 means the `ci` row the Evidence calls "`ci` PASS" (bullet 3). No other section has the clash.
Suggested fix: Write "a PASS `ci` result (the gate suite)" or "a PASS test-suite result" in bullet 9; no other change.

### Prior findings (round 1)

- [BLOCKING] 6, unglossed terms in Evidence, Decisions and Operator steps: RESOLVED. The Problem names and glosses the terms; "GIVEN block" is gone from Evidence; Decisions bullet 1 glosses the pinned spec and `decisions.md`; Operator step 1 glosses the runtime, `harness.lock` and the Nanobot instance; step 2 glosses a gate edit.
- [SHOULD-FIX] 6, two names per concept: RESOLVED. "Integration branch" is introduced in the Problem and used throughout; "reviewing agents" and "checkers" are gone from proposal.md. The one residue is the NIT above.
- [SHOULD-FIX] 4, brace lists: RESOLVED. Decisions bullet 2 states the one-entry rule and that a brace list declares nothing; D.2 adds the FORMAT line; the spec-writer scenario's `braces` count fails today (verified above); the new test file covers a refused brace-list entry.
- [NIT] 2, three untested branches: RESOLVED. The design.md opening lists five cases the new test file covers, including the two I named and the no-approved-spec wording.
- [NIT] 5, piece 9: RESOLVED. E.1 changes line 49 and the design-doc scenario's `piece9` count fails today (verified above).

The change not asked for by a finding (reading the Risk section with `specstore.lines_outside_fences`) is sound: it reuses the section rule `main` adopted in `220ebdc`, and without it a quoted example declaration in a Risk section would authorize paths. The spec also says plainly that v2's scenarios were not re-run; I re-ran four of them and they match.

Out-of-scope observations: none new. The round-1 note on the 2026-10-07 T-0032 decision line stands; the spec records the correct cause in Evidence and leaves the log alone, which is right for this ticket.
