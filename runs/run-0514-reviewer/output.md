Commit: 08ad85edf30076259c47b7fc816976f45270e805 (branch `factory/T-0048.1`, base `7231670`)

## How I reviewed

Read the whole diff (7 files, +142/-220: `.factory/context.md`, `README.md`, the three `dev/` build documents, `docs/changelog.md`, `docs/design.md`) against every lettered part of the approved spec v1 and the restated and added `harness-docs` scenarios. Ran narrow checks only, in the worktree, each cited with its finding or under Checks below. I did not run the suite or the gate commands.

## Checks, in order

1. **Test integrity.** No file under `tests/` changes (`git diff --stat 7231670 HEAD`: the seven files above). The spec's "Tests to change" is none, and no code, prompt or template file changes. Pass.

2. **Correctness against the spec's lettered parts.** Every sentence the spec dictates word for word is present as given:
   - A.1 header at line 3 of each build document, otherwise byte for byte as at `7231670`: I ran the scenario's command; it prints `header=1 rest=same` for all three files.
   - A.2 `.factory/context.md`: both edits as given; `grep -c build-harness .factory/context.md` prints `0`.
   - A.3 README `dev/` row as given.
   - B.1 to B.7 as given; B.8: README line 9 already reads `as of 2026-10-13`, the day of the change.
   - C.1 driver how-to paragraph is 6 lines, keeps exit 2 / nothing written, `drive/<ticket>.yaml`, the pid rule and the SIGKILL recovery; "refused like any write" and "other tickets are in flight" are gone. Fence Built entry 3 lines, names "Where a human decides".
   - C.2 driver Built entry 4 lines; "Running on another agent host" is 4 non-blank lines, no table, points to `docs/design.md`, "Running on another agent host" (that heading exists, `docs/design.md:868`).
   - C.3 the full skip condition is now in "The build workflow, step by step"; `grep -c 'has not moved since' README.md` prints `1`.
   - C.4 the "Where it runs" bullet uses the spec's sentence; `never moves the integration branch` appears once in the joined page.
   - C.5 every Built entry is within its line target, keeps its bold name, keeps the words the spec names (`SKIPPED`, `factory spec amend`, `is not drift`, `ended its turn waiting on a background command`), and carries the status B.5 assigns. The `docs/design.md` anchors each entry cites exist: `**Tripwire on live files.**` (line 58), `**Tests a sibling added.**` (60), `**Spec drift.**` (62), `**Routing table.**` (98).
   - C.6 "Not built" is one paragraph with the five facts, the hand-copy sentence in the spec's words, and the renamed bullet appears once (`README.md:1002`).
   - D.1 to D.5 as given. D.3 keeps all 19 issue references; its figures re-derive: `ls .factory/store/tickets` holds 51 `T-nnnn.yaml` and 64 `T-nnnn.n.yaml`.
   - D.6 entry 72 opens with the required words, sits between entry 71 and the "Declined:" line, and carries `frozen`, `build-harness.spec.md`, `context.md`, `41 and 11`, `harness-docs` and `not yet`.
   - E.1 to E.3 as given.
   - Entry 72 says "16 tickets from T-0031 to T-0051", where the spec's D.6 says T-0032. The store log (`.factory/store/log/2026-10.jsonl`) has `plan.skipped` for T-0031 as well as T-0032 onward, so the implementer's range is the true one and the spec's was off by one. The right call; the implementer flagged it (Known gaps 2). No finding.

3. **Scope.** Three edits go past the lettered line targets, all in README and all giving a home to detail the shorter Built entries dropped: how a skipped gate command is reported ("Adopting the factory in a repo"), the Code reviewer row of the roles table (line 41: "leaves the test suite and the gate commands to the verifier"), and the catch-up consequence in the store-branch bullet of "How the factory uses git". Each serves part C's one-home rule and is declared in the PR description. No finding.

4. **Silent behaviour changes.** None: no code, prompt, template or test changes.

5. **Security and data safety.** Nothing applies. The figures came from read-only `ls`, `git` and log reads; the PR description says the Nanobot store was read, not written.

6. **Protected paths.** `.factory/context.md` is under `.factory/**` (infra) and is declared on the approved spec's `Protected paths:` line. Listed under ESCALATIONS for the record; the merge gate merges it without further approval.

7. **Coding standard.** No code changes; nothing to tag.

8. **PR description.** What changed says in words what moved where and why, glosses the spec gate, the store and archive on first use, and Known gaps names each uncertainty with its cause. Readable at the gate. No finding.

## Findings

- [SHOULD-FIX] docs/design.md:70: the new pointer says `factory stats`'s first figures "are in `docs/principles.md`, principle 4, and changelog entry 70", but those two places hold only the code reviewer's figure (4 of 94, 3 BLOCKING). The critic's, the verifier's and the implementer's figures and every token count now live only in changelog entry 72 → a reader who follows the pointer does not find most of what the old line 70 held. Add "and entry 72" (or point to entry 72 alone). The spec dictated this sentence, so this deviates from its words; the governing check only requires `changelog entry 70` present and `94,860,442` absent, which the fix keeps. The implementer raised this as Known gaps 1; the operator may strike it at the gate.

No BLOCKING findings.

## Out-of-scope observations

- README's "Ground truth only" bullet (lines 1055-1058) still routes named work to "Not built", while the new "Not built" paragraph says everything under "Where this can go" is named work. The spec causes this: B.6 keeps the bullet's tail and C.6 dictates the paragraph's opening. A later README change could reconcile them; the implementer noted it (Known gaps 5).
- The spec's D.6 ticket range (T-0032) was off by one against the log; the spec's Evidence should be the place that gets corrected if anyone re-reads it.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every dictated sentence is in the diff as given; the frozen-document, briefing, line-count and store-figure checks I ran in the worktree print the spec's expected values; the one finding is a true-but-incomplete pointer the spec itself worded.
ESCALATIONS: `.factory/context.md` (infra, `.factory/**`) is touched and is declared on the approved spec's `Protected paths:` line; listed for the record, no action needed.
