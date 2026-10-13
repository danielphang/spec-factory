Sub-ticket: T-0048.1 (parent T-0048, approved spec v1, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0048/v1.md`)
Branch: `factory/T-0048.1`, one commit `08ad85e` on base `7231670`. 7 files, 142 insertions, 220 deletions.

This change shortens the two documents the operator reads at every spec gate and makes them true.
The spec gate is the human review where a spec is approved before code is written. The documents are
`README.md`, the page saying what the factory does today, and `docs/design.md`.
- README goes from 1,191 to 1,106 lines.
- Its false "not yet run" claims are corrected from the stores' logs. The store is the factory's
  per-repo record of tickets, runs and verdicts.
- Each mechanism is described in one section, and other mentions point to that section.
- History moves to `docs/changelog.md`.
- The three finished build documents under `dev/` are frozen. The briefing every agent reads first
  no longer asks each change to keep them in step.

No code, test, or prompt file changes.

## What changed

**A. Freeze the `dev/` build documents.**
- `dev/build-harness.spec.md`, `dev/build-harness.plan.md`, `dev/P0-intake-skeleton.md`: the spec's
  "Frozen as history" header is inserted at line 3, followed by one blank line. Nothing else in these
  files changes, and scenario 48 checks this byte for byte against `7231670`.
- `.factory/context.md` (a protected path the spec declares): the `dev/` bullet now reads as the
  spec gives it. The design-change sentence no longer names `dev/build-harness.spec.md`, so the file
  names no `build-harness` path.
- README's `dev/` row in "Where things live" now says those three documents are frozen as history.

**B. Correct the stale claims.**
- README line 94: a run with no output is run once more and then parks its ticket. README no longer
  says such a run is "recorded as killed".
- These claims now say the feature has run:
  - the one-sub-ticket path, on both targets;
  - the driver, `factory drive`, which took real tickets through intake and the build on the
    chat-bot target;
  - the path skip, which is recorded on a real sub-ticket;
  - the re-plan after a re-spec, which has fired;
  - the protected-path refusal, which has fired and was accepted with `--accept-paths`.
- The per-run scratch directory sentence no longer says it is untried.
- These claims are kept, because they are still true:
  - the tripwire has not yet fired;
  - the sibling-tests check has not yet fired;
  - the drift check's sibling-merge exception has not yet run;
  - "Neither target sets it yet", in the effort entry.
- The "Ground truth only" rule now admits a thing once it is built and tested. It asks each entry to
  say whether the thing has yet run on a real ticket. The rest of that bullet stays.
- `docs/design.md` line 3 now reads ``Daniel · first written 2026-09-30; every change since is in `docs/changelog.md` ``.
- The README status date was already 2026-10-13, the day of this change, so it is unchanged.
- I checked each correction against the logs. The logs are read only; the Nanobot store is the
  other target's store.
  - `plan.skipped` events: 16 tickets here, from T-0031 to T-0051. There are 5 on the Nanobot store.
  - Driver replies: 15 `reply.json` files on the Nanobot store.
  - Path skip: `ci.yaml` with `SKIPPED` for `ticket: T-0036.1` on the Nanobot store.
  - Re-plan: `subtickets.superseded` for T-0031 at 2026-10-09T18:11:03.
  - Protected-path refusal: `merge.refused` "protected paths not declared" for T-0044.1 at
    2026-10-12T02:14:17, then `human.resolved` `kind: accept-paths` at 04:37:24.

**C. One home per mechanism in README.**
- The live-store fence blocks store writes while an agent run is in flight. Its home is "Where a
  human decides", which is unchanged.
  - The driver how-to paragraph about the fence is 6 lines. It keeps the exemption and the
    same-ticket guard: exit 2 and nothing written, the `drive/<ticket>.yaml` check, what to do about
    a pid that is not a driver, and the SIGKILL recovery.
  - It drops "refused like any write" and "even while runs of other tickets are in flight".
  - The fence's Built entry is 3 lines and points to "Where a human decides".
- The driver's home is its how-to section.
  - The file-tool limits sentence moved from the driver's Built entry into the how-to.
  - The Built entry is 4 lines.
  - "Running on another agent host" is 5 non-blank lines with no table. It points to
    `docs/design.md`, "Running on another agent host".
- The final check's skip has its full condition and reason in "The build workflow, step by step".
  "How a ticket moves" keeps one pointer sentence. "has not moved since" now appears once.
- The store branch's home is "How the factory uses git".
  - The target bullet in "Where it runs" now uses the spec's sentence.
  - The store-commit sentences at old lines 619-620 and 828 are dropped.
  - The Built entry is 2 lines.
  - "never moves the integration branch" now appears once. It is in "How the factory uses git",
    whose bullet also absorbs the catch-up consequence from old line 619.
- Built entries. Each keeps its bold name and is within its line target:
  - Build, local-only: 5 lines (target 6). It keeps `SKIPPED`.
  - Spec store: 2 lines.
  - Tripwire: 4 lines.
  - Sibling tests: 4 lines.
  - Spec amendment and drift: 5 lines (target 6). It keeps "factory spec amend", "Where a human
    decides" and "is not drift".
  - Re-plan: 4 lines.
  - Empty output: 5 lines (target 6). It keeps the waiting phrase.
  - Protected paths: 4 lines.
  - Per-role effort: unchanged.
  - `factory stats`: 3 lines. The `factory/cost.py` history is dropped.
- "Not built" is now one paragraph with no bullets. It gives the five facts from C.6 and keeps the
  hand-copy sentence word for word. The bullet in "Where this can go" is renamed "**Current truth for
  the factory itself.**".
- The `inlineRoles` how-to now points to "What depends on Claude Code" instead of repeating what the
  flag does.

**D. History to the changelog.**
- These sentences are dropped from README:
  - the 2026-10-04 overlap of 41 and 11 runs;
  - the `factory/cost.py` double count;
  - both store-move sentences;
  - the regeneration pass's "(today this caught two: ...)".
- "Related work and history" is now a list. It keeps every one of the 19 issue references, each
  beside what it names.
- After the list, it names instances A and B, points to `docs/changelog.md` and `dev/issues.md`,
  and gives re-derived figures:
  - 51 tickets and 64 sub-tickets: `ls .factory/store/tickets`.
  - Runtime commit `9dbd4f8`: `git -C ~/dev/spec-factory-harness rev-parse --short HEAD`.
  - Harness revision `5e00a1f`: `bin/factory paths` printed `"harness_revision": "5e00a1f5..."`,
    which equals `.factory/harness.lock`.
- `docs/design.md:70`: the text after "prints the evidence a change to this table needs" now reads
  "; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog
  entry 70." This is the spec's wording.
- `docs/changelog.md`: new entry 72 for #101, after entry 71 and before the "Declined:" line. It
  records parts A to F and F's rules, the corrected claims with their tickets, and the rejected
  options. It also keeps the per-role `factory stats` figures that line 70 no longer carries (see
  Known gaps 1).

**E. Glossary.**
- The four rows for target, instance, store branch and runtime become one row pointing to "Where it
  runs". "Where it runs" defines all four.
- The merge-gate row no longer defines a protected path. A new `protected path` row follows it.
- The **Record** row no longer restates who reads the decision log.

**F. `harness-docs` current truth.**
- No repository file changes for this part. The pinned spec's delta is that change; archive applies
  it when the ticket closes. Archive is the step that folds an approved spec into current truth.

**Moves beyond the literal line targets.** I made three small moves so that detail the shorter
Built entries dropped keeps one home in README:
- "Adopting the factory in a repo" now says how a skipped gate command is reported. The checkers are
  told it is SKIPPED with the reason, the skip is recorded with the gate result, and the implementer
  still gets every command.
- The Code reviewer row in the roles table now says the reviewer leaves the test suite and the gate
  commands to the verifier.
- "How the factory uses git" took the catch-up consequence of a store commit, as described under C.

## Acceptance results

All 55 WHEN commands were extracted verbatim from the input. Each ran under bash from the worktree
root through the fresh-HOME wrapper. Logs are in the scratch directory: `base.txt` is on `7231670`,
before the change, and `final.txt` is on `08ad85e`.

NEW, before → after:
- Each build document carries the header and is otherwise unchanged:
  - before: `header=0 rest=changed`, for each of the three files;
  - after: `dev/build-harness.spec.md header=1 rest=same`, `dev/build-harness.plan.md header=1 rest=same`, `dev/P0-intake-skeleton.md header=1 rest=same`.
- The briefing no longer asks a change to keep the build spec in step:
  - before: `buildspec=3 frozen=0 readme=0`;
  - after: `buildspec=0 frozen=1 readme=1`.
- README no longer calls run features untried, and keeps the claims that are still true:
  - before: `stale=7 replan=1 paths=1 drive=1 tripwire=1 sibling=1 effort=1`;
  - after: `stale=0 replan=0 paths=0 drive=0 tripwire=1 sibling=1 effort=1`.
- The Built rule asks for run status, and the design doc's date line points to the changelog:
  - before: `rule=0 date=0 old=1`;
  - after: `rule=1 date=1 old=0`.
- Each Built entry is a short pointer, and each mechanism's detail has one home:
  - before: `fence=long driver=long tripwire=long sibling=long drift=long empty=long paths=long stats=long host=long skip=2 store=3 drivefence=1 notbuilt=5`;
  - after: `fence=pointer driver=pointer tripwire=pointer sibling=pointer drift=pointer empty=pointer paths=pointer stats=pointer host=pointer skip=1 store=1 drivefence=0 notbuilt=0`.
- The glossary points to Where it runs and defines protected path once:
  - before: `rows=4 pointer=0 protected=0 merge=1 record=1`;
  - after: `rows=0 pointer=1 protected=1 merge=0 record=0`.
- README keeps its issue references and drops the moved history, and the changelog records the move:
  - before: `history=5 refs=19 figures=1 pointer=0 entries=0 terms=0`, then `CONTIGUOUS`;
  - after: `history=0 refs=19 figures=0 pointer=1 entries=1 terms=6`, then `CONTIGUOUS`.
- README is at most 1,110 lines:
  - before: `readme=over`;
  - after: `readme=within`. `wc -l README.md` prints 1106.

All eight before-outputs match the spec's verification.md.

REGRESSION, after: all 47 print exactly their THEN on `08ad85e`.
- Their output is identical to the base run line for line. The one exception is "The reviewer's
  input no longer hands it the gate commands...", which cannot run without its setup.
- That scenario needs two setup blocks from current truth. I extracted the shell blocks of "A ruling
  on a BLOCKED park..." (human-resolution) and "A reviewer that ends its turn waiting..."
  (build-dispatch). I ran them once with `TMPDIR` set to the scratch `tmp/`.
- It then printed `reviewer gates=0 told=1`, `verifier gates=1 told=0`,
  `implementer gates=1 told=0`. This matches its THEN.
- Examples of the restated changelog checks:
  - "The changelog records the change in order" printed `CONTIGUOUS`, then `9`.
  - "The changelog records issue 106 as entry 71..." printed `CONTIGUOUS`, `1`, `5`.
  - "The maintained documents pass git's whitespace check in full" printed `exit=0`.
- No REGRESSION command failed, so none needed a run on base.

Gate commands, run exactly as written from the worktree on `08ad85e`:
- `git diff --check main...HEAD`: exit 0, with no output. `main` is `7231670`.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `584 passed in 139.56s`, exit 0.

## Tests added/changed

None. The spec's "Tests to change" is none. No test reads `README.md`, `dev/`, `docs/changelog.md`
or `.factory/context.md`, and this change edits no code. The checks for this change are the
acceptance scenarios above.

## Known gaps and uncertainties

1. **The new pointer on `docs/design.md:70` is only partly backed.** It says the first `factory stats`
   figures are in principle 4 and changelog entry 70. In fact both hold only the code reviewer's
   figure (4 of 94 runs, 3 BLOCKING findings).
   - Before this change, line 70 was the only place with the other roles' figures and the token
     counts.
   - So that this history is not lost, entry 72 records them word for word: the critic's 19 of 84,
     the verifier's 8 of 108 and 1 of 5, and the implementer's 18 of 111, with their tokens.
   - I used the spec's exact pointer wording and did not add "and entry 72". The operator may want
     the pointer to name entry 72 too.
2. **I wrote a different ticket range than the spec.** Spec D.6 names "T-0032 to T-0051" for the
   one-sub-ticket path. This store's log has `plan.skipped` for T-0031 too, and for T-0048, this
   ticket. Entry 72 says "16 tickets from T-0031 to T-0051 here, five on the Nanobot store". No check
   reads this phrase.
3. **README has 4 lines of slack.** It is 1,106 lines against the 1,110 budget; the prototype had
   1,101. Two things account for the difference: the Adopting sentence I added, and "Related work and
   history" written as a list.
4. **Some detail is now only in `docs/design.md`.** It left README with the shortened Built entries:
   - Re-plan: a new plan may not depend on a sub-ticket it supersedes, and old merged sub-tickets
     count as done.
   - Drift: the two kinds of drift. The critic's cross-ticket check is still in the Spec critic
     row.
   - Empty output: the sentence that no time or token budget is enforced.
   - Tripwire: that killed runs are included and that no file contents are printed.
   - The OpenSpec origin phrase.
   - The agent-host comparison table, which is at `docs/design.md:868`.
5. **The "Ground truth only" bullet is slightly at odds with the new "Not built" paragraph.** Spec B.6
   keeps the bullet's tail, which still says named work belongs under "Not built". The new "Not
   built" paragraph sends named work to "Where this can go".
6. **The live-store fence entry's status sentence is shorter.** It now reads "It has fired on a real
   target, when a stopped workflow left a run in flight". This fits the 3-line limit; the meaning is
   unchanged.
7. **The figures will go stale.** "51 tickets and 64 sub-tickets" was counted while this ticket was
   in flight, and the 64 includes T-0048.1. They stay true only until the next ticket is filed.
8. **The `dev/issues.md` row for #101 is not updated.** The spec does not ask for it. The row is
   normally updated when the ticket closes.

## Out-of-scope observations

- README "Parallel builds across tickets have not been tried": the spec noted this too, and I did
  not check it against the logs.
- `factory/cli.py:1`'s docstring cites "the build-harness spec". That file is harness code and
  protected.
- README "Where this can go" lists "**Many targets.**" as intended. Two targets already run on one
  runtime ("Where it runs"), so that bullet may describe something partly built. I did not change it,
  because that section changes only with the design.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 55 acceptance scenarios and both gate commands passed on the committed head, and every corrected claim was checked against the store logs.
ESCALATIONS: none
