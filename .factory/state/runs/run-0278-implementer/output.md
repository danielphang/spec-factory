Sub-ticket: T-0022.1 (ST-1 / Sibling tests), parent T-0022 (issue #40), spec v1. Branch `factory/T-0022.1` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0022.1`, base `c2750bf`, head `771ee0e` (two commits: `8f1d356` is the change, `771ee0e` is a one-line correction to the build spec).

## What changed

Some background first. The **planner** is the agent that splits an approved spec into **sub-tickets**, which are built and merged one at a time. Sub-tickets of the same spec are **siblings**. Until now, only the spec's own approved "Tests to change" list allowed an implementer to edit an existing test. That stopped a sub-ticket whenever it had to change a test an earlier sibling had added, because that test did not exist when the spec was approved. This change lets the planner list such a test, and the harness checks the entry in git before the implementer starts. It also fixes two causes of avoidable parks in the agents' instructions.

- **A. Planner prompt.** The prompt now tells the planner to label each check NEW or REGRESSION against the sub-ticket's own base, instead of copying the label from the whole spec. It adds an "Interim tests" field. "Tests to change" may now list `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``. The block was changed the same way in `docs/design.md` §4, `docs/prompts/04-planner.md` and `factory/prompts/planner.md`, and the three copies are byte-identical in that block.
- **B. The sibling-tests check.**
  - `factory/subtickets.py` gains `PLAN_FIELDS`, `SIBLING_TEST_RE` and `sibling_tests(text)`. They read `(added by …)` entries only inside the "Tests to change" field. The field ends at the next planner field or heading. `::<test>` suffixes are dropped and repeated files are listed once.
  - `factory/gitops.py` gains `first_added(repo, base, tip, path)`. It returns None when the file existed at `base`. Otherwise it returns the oldest `--diff-filter=A` commit in `base..tip`.
  - `factory/cli.py` gains `_check_sibling_tests`, which `run_start` calls for an implementer run of a sub-ticket. The call comes after the in-flight guards and before `tripwire.baseline`, so a refusal writes nothing. A listed file passes when the parent has a `parent_base` and the file's first add lies inside some merged sibling's recorded merge: reachable from `main_after` and not from `base_before`. Otherwise `run start` exits 2 with `BLOCKED from harness: Tests to change lists <path> as added by a sibling, but no merged sibling of <parent> added it since <base9>; list it in the parent spec's Tests to change, or remove it`. If no sibling has merged yet, `(no sibling has merged)` takes the place of `since <base9>`.
  - In `factory/workflows/build.js`, `runRole` parks the sub-ticket with the refusal's JSON `error` word for word when it starts with `BLOCKED `. Every other refusal still parks as `harness-bug: run start …`. `resolve --ruling` already accepted a `BLOCKED` park, so it was not changed.
  - New test file: `tests/factory/test_sibling_tests.py`.
- **C. Spec writer and critic prompts.** The spec writer gets the RULES bullet "Tests a decision overturns", placed before "Open questions stay open". Critic rubric 1 gets three lines: a test that pins the old behaviour and is missing from "Tests to change" is a finding. Both edits are in all three copies of each prompt.
- **D. Preamble and code reviewer prompts.** The guardrail sentence in the preamble, and the reviewer's test-integrity check, now also accept a test the sub-ticket lists as added by an earlier sibling. Both edits are in all three copies of each prompt.
- **E. Documents.**
  - `docs/design.md`:
    - The piece 8 row gets the sibling sentence and the GitHub-column clause.
    - The Spec approval row is reworded.
    - A new one-line paragraph, `**Tests a sibling added.**`, comes before "Only the dispatcher writes…".
  - `docs/changelog.md`: new entry 54, "After issue #40 (2026-10-04)". It ends with the rejected alternative.
  - `dev/build-harness.spec.md`: the `run start` guards get the refusal, piece 8 gets the checked entry, and `runRole` gets the BLOCKED park. The second commit says the park belongs to `build.js` and not to "both scripts", because `intake.js` never starts an implementer.
  - `README.md`: a new Built bullet "Sibling tests check." after "Live-store fence", and a new case in the Unstick row's `--ruling F` note.

Callers of what I changed:
- `run_start` is reached only through the CLI's `set_defaults(fn=run_start)` (`factory/cli.py:1357`).
- `runRole` is called five times, all inside `build.js`. They all share the one refusal branch I edited.
- I added no other caller to an existing function. `head_contains` is reused unchanged; it already has three other callers.

## Acceptance results

Every command was run from the worktree with a fresh HOME, in zsh, and `TMPDIR` set to this run's `scratch/tmp`. The GIVEN block was written once, exactly as the spec gives it. Before = base `c2750bf`; after = head `771ee0e`. The outputs on `8f1d356` and `771ee0e` match exactly (`diff` printed nothing).

| Scenario | Label | Before | After |
|---|---|---|---|
| merged sibling's file accepted, Scope mention ignored | REGRESSION | `exit=0 ready-for-implementer runs=1` | `exit=0 ready-for-implementer runs=1` |
| listed test predates plan / no sibling / never added | NEW | 3× `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer` | 3× `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer` |
| build parks with harness reason, ruling returns it | NEW | `park T-0001.2: budget kill: implementer` / `ruling=2 parked` | `park T-0001.2: BLOCKED from harness:` / `ruling=0 ready-for-implementer` |
| planner copies | NEW | 3× `own=0 sibling=0 interim=0 copied=1`, `verbatim` | 3× `own=1 sibling=1 interim=1 copied=0`, `verbatim` |
| writer/critic copies | NEW | `writer=0 critic=0` on all three lines | `design: writer=1 critic=1`, `docs/prompts: writer=1 critic=1`, `factory/prompts: writer=1 critic=1` |
| preamble/reviewer copies | NEW | `guard=0 review=0` on all three lines | `design: guard=1 review=1`, `docs/prompts: guard=1 review=1`, `factory/prompts: guard=1 review=1` |
| system prompts of real runs | NEW | `planner own=0 sibling=0 guard=0 writer=0 critic=0` | `planner own=1 sibling=1 guard=1 writer=1 critic=1` |
| design doc and build spec | NEW | `piece8=0 gate=0 stale=1 check=0 build=0` | `piece8=1 gate=1 stale=0 check=1 build=1` |
| changelog | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| README | NEW | `built=0 ruling=0` | `built=1 ruling=1` |
| no whitespace errors | REGRESSION | `exit=0` | `exit=0` |

Every NEW item failed on the base exactly as `verification.md` and the plan's table say, and printed its THEN after the change. A full refusal text, from the `tests/test_operator.py` fixture: `BLOCKED from harness: Tests to change lists tests/test_operator.py as added by a sibling, but no merged sibling of T-0001 added it since 6cd4bf63b; list it in the parent spec's Tests to change, or remove it`. The build driver printed that same text as the park reason.

Gates, each run exactly as written, from the worktree on `771ee0e` with a clean tree:
- `(export HOME=…; git diff --check main...HEAD)` → exit 0, no output.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` → `310 passed in 253.42s`.
- The suite again with `TMPDIR=$(mktemp -d /tmp/t0022-suite.XXXXXX)`, as the harness-suite scenario in current truth sets it → `310 passed in 275.70s`. That run started on `8f1d356`. The only later change is a wording edit to `dev/build-harness.spec.md`, which no test reads (`grep -rln build-harness.spec tests/factory` prints nothing).
- 310 = 300 existing tests (`--collect-only --ignore tests/factory/test_sibling_tests.py` prints `300 tests collected`) + 10 new. The spec's figure of 265 is from `0b1abad`, before T-0025's tests merged.
- `ruff check` (default rules) on the three changed modules and the new test: `All checks passed!`. `node --check factory/workflows/build.js`: exit 0.

## Tests added/changed

New file `tests/factory/test_sibling_tests.py`, 10 cases. It is black-box: it drives `bin/factory` and `build.js` as subprocesses on a throwaway store and a scratch target repository, built like the spec's `t0022-sib.sh` fixture.
- A merged sibling's file is accepted, with and without a `::test` suffix (2 cases).
- A file that predates the plan, was added by a direct commit, or was never added is refused (3 cases). Each refusal: exit 2, error starts `BLOCKED from harness: ` and names the file and parent, no run directory, no branch, status unchanged, `in_flight` empty.
- With no sibling merged and no `parent_base`, the file is refused with `(no sibling has merged)`.
- A file added by a sibling, deleted, then re-added by a direct commit is accepted, because the first add counts. I checked that this case catches a wrong fix: with `--reverse` removed from `first_added`, it fails (`1 failed`).
- The build workflow parks the sub-ticket with the harness's reason and nothing else, and `resolve --ruling` returns it to `ready-for-implementer`. This case needs `node` on PATH. It asserts that node is there rather than skipping.
- An `(added by …)` mention in a Parallel-safe line, in the form the stored Nanobot sub-ticket T-0002.6 uses, is ignored.
- The field ends at the next plan field (Protected paths) and at a heading (the shared plan context the store appends). A line that names no plan field stays inside the field. Bold field names and `::test` suffixes are read.

With the code changes stashed, 6 of the 10 fail. The 4 that pass on base are the two accept cases, the re-add case and the Parallel-safe case. They guard against a check that refuses too much, so on base, where nothing is checked, they pass by design. No existing test was changed.

## Known gaps and uncertainties

- **I reused `head_contains` instead of adding `is_ancestor`, which differs from the spec's B.2.** `gitops.head_contains(repo, head, base)` already runs `git merge-base --is-ancestor base head`, which is exactly the `is_ancestor(repo, a, b)` the spec asks for. The coding standard's rule 1 is to reuse before writing. Nothing in acceptance names `is_ancestor`. One difference: `head_contains` does not capture git's stderr, so an unknown SHA in a merge record would print a git error on the CLI's stderr before the refusal.
- Sibling merge records are used only when both `merge.main_after` and `merge.base_before` are set. The spec names only `main_after`. `merge_cmd` always writes both, so this changes nothing in practice. Without the second condition, a record missing `base_before` would accept any add reachable from `main_after`.
- **The park passes planner-written text to a shell.** The refusal names a path taken from planner-written text, and `build.js`'s `park()` puts the reason inside a double-quoted `sh -c` string, escaping only `"`. `SIBLING_TEST_RE` excludes backticks and whitespace, but a path such as `$(cmd)` with no spaces would still be expanded by the clerk's shell. Today's `harness-bug:` parks already pass stderr text through the same path; this change adds planner-controlled text to it. I did not change `park()`, because it is outside this sub-ticket's parts.
- `first_added` relies on git's default history simplification to find the add commit on a sibling's merged branch. I verified this only for the `--no-ff` merges that `merge_cmd` makes, in the tests and the fixture.
- The build-dispatch test needs `node` on PATH, as the spec's scenarios do. Without node, that case fails instead of skipping.
- factory: markers added: none.

## Out-of-scope observations

- The new planner text says a sub-ticket with an `(added by …)` line "must depend on that sibling". The harness accepts any merged sibling, as Decision 2 of the spec intends. The critic noted the same; nothing enforces the dependency.
- The README rule "Ground truth only above 'Where this can go'" says a thing is listed as Built only after it has run on a real ticket. The new Built bullet follows the spec and the existing "Tripwire" and "Live-store fence" bullets, which say "tested, and has not yet fired on a real ticket". The page's rule and its practice disagree. That disagreement predates this change.
- The parent's Operator steps (re-plan and re-spec Nanobot's T-0002 on a copy of its store) are for the operator after merge. I did not run them.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN on the final head, every NEW item was seen failing on the base first, and both gates passed on the final commit. The deliberate differences from the spec (reusing `head_contains`, requiring `base_before`) are listed above.
ESCALATIONS: none
