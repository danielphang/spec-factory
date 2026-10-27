Sub-ticket: T-0059.1, `factory truth check` replays every current-truth scenario, and the gate runs it (parent T-0059, issue #120, approved spec v4). Branch `factory/T-0059.1`, head `2588b55`, base `db28eb1`.

## What changed

The new command `factory truth check` replays the scenarios in current truth. Current truth is the store's record of required behaviour: one spec per area, called a capability. Each scenario is a shell command, its WHEN, and the output it must print, its THEN. Until now nothing ran these scenarios again after their own ticket closed. With this change, this repo's merge gate runs the replay as its last command.

**A. `factory/truth.py` (new, 297 lines): the replay.**
- **Inputs.** The store comes from `--store`, else `FACTORY_STATE`, else the instance's own store. The checkout under test is `git rev-parse --show-toplevel` of the caller's directory.
- **Folding.** The command finds the ticket under test from the store's layout: `worktrees/<id>`, or `runs/<run>/wt` plus that run's `meta.yaml`. It folds in the approved delta of that ticket's parent, or of the ticket itself if it has no parent. It also folds the delta of every unarchived change whose ticket is not closed and has a merged sub-ticket. Deltas are folded in id order, each checked against the text folded so far and applied with `specstore.apply_delta`. A delta that does not apply refuses the check with exit 2 and names its ticket.
- **Reading a scenario.** It reads each scenario's single WHEN, its THEN, its GIVEN blocks and its double-quoted references to other scenarios.
- **The exact-print rule** is `expected()`, following the grammar in design part A.
- **Skips.** The five skip reasons are checked in the spec's order.
- **Running.** Capabilities run at the same time, one thread each. Each capability gets a fresh `HOME` and `TMPDIR`, and every `FACTORY_*` variable is removed from its environment. Scenarios run in file order under `bash -c`, after the GIVEN blocks they need, and each block runs once per capability.
- **Output.** One line per scenario, and under each failure the expected lines, the printed lines (at most 40), the exit status and the last five stderr lines. The last line gives the counts and the wall time. The exit code is 1 when any scenario failed.
- **Parser.** `add_parser()` builds the `truth check` parser, so `cli.py` stays small.

**B. `factory/cli.py` (899 lines, unchanged count).**
- One import, and one `truth.add_parser(sp)` call in `build_parser()`.
- `("truth", "check")` is added to `READ_ONLY`, and its comment is updated.
- `"truth"` is added to both tuples in `main()`, so the command refuses `--accept-harness` with the same message and runs before the instance refusal, the fence and the lock. The message names `factory truth check`.
- That branch now returns `a.fn(a) or 0`, so the command's exit code reaches the shell. `init_cmd`, `paths_cmd` and `stats_cmd` return `None` (no `return` statement), so they still exit 0.
- Callers of `main()`, found by grep: `factory/__main__.py`, `factory/drive.py:63`, `tests/factory/clean_harness_cli.py:28` and `tests/factory/test_store_migrate.py:164`. None of them runs `truth`, and the return value only changed for that command.

**C. `.factory/instance.yaml`.** After the suite command, the comment line and the last gate entry are added verbatim from design part C.

**D. Documents.**
- README, "Where a human decides": the read-only list now ends `log tail`, `truth check`, `paths` and `stats`.
- README: a new subsection, "Replaying current truth with `factory truth check`", six lines with no figures, placed before "What is built and what is not".
- README: a two-line Built entry.
- README, "Accepting a harness revision": the one sentence there now reads "`paths`, `stats` and `truth check` only read, so they skip both checks on any store and refuse `--accept-harness`, as `init` does". It is reworded, not just extended; see Known gaps.
- README: the status date is now 2026-10-26.
- README grows by exactly 11 lines, to 1,224.
- `docs/design.md`: a new paragraph, `**Replaying current truth.**`, placed immediately before `**Routing table.**`. `truth check` is added to the fence paragraph's read-only list and to the lock clause in `**Role-context block.**`.
- `docs/changelog.md`: entry 79, which names #120. The numbering is contiguous.

**E. Restated scenarios.** E changes only the spec store, at archive. This branch has no code for it; the restated scenarios' results are below.

## Acceptance results

I ran every WHEN from the worktree at the head commit, through the HOME wrapper with `TMPDIR` in my scratch directory. A small runner, `scratch/runwhen.sh`, ran each GIVEN block once and then each WHEN. The WHENs were extracted verbatim from `openspec/changes/T-0059/specs/*/spec.md`, which I diffed against v4 and found identical. Every "after" output below matches its THEN exactly. The 14-line transitions block was compared with `diff` against the THEN's fenced block and printed `SAME 14`. All 34 "after" runs were made at `eb6d383`. The only later commit, `2588b55`, renames one helper inside `tests/factory/test_truth.py`, and the suite and ruff were re-run after it.

| Scenario | Label | Before (db28eb1) | After |
|---|---|---|---|
| Each scenario of a fixture truth gets one result line… | NEW | `exit=2` only | the 16 expected lines, ending `16 scenarios: 11 passed, 2 failed, 3 skipped; wall time N s` |
| The first line names the checkout, the store and the folded deltas… | NEW | nothing | `truth check: G against S; folded: T-0002`, `  expected:`, `    hello`, `  got:`, `    hullo`, `  exit 0` |
| --capability limits the run… | NEW | `one: exit=2 0 0`, `unknown: exit=2 named=0`, `no-truth: exit=2`, … | `one: exit=0 2 2`, `unknown: exit=2 named=1`, `no-truth: exit=2`, `no-git: exit=2` |
| Capabilities run at the same time | NEW | nothing | `together` |
| Prose THENs, missing GIVEN blocks and WHENs the caller skips… | NEW | nothing | the 5 expected lines, ending `16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s` |
| On a checker's checkout of a sub-ticket… | NEW | nothing | the 5 expected lines (`folded: T-0001, T-0002`, …) |
| The implementer's worktree folds the same deltas | NEW | nothing | `truth check: W against S; folded: T-0001, T-0002`, then the SKIPPED alpha line |
| From the integration branch only an open ticket's delta… | NEW | nothing | `PASS alpha: The greeting is printed exactly`, the SKIPPED gamma line, `PASS gamma: Gamma prints two` |
| A folded delta that no longer applies is refused… | NEW | `exit=2 named=0 results=0` | `exit=2 named=1 results=0` |
| truth check reads a live store with a run in flight… | NEW | `here=2 inside=2 store=unchanged total=factory: error: argument cmd: invalid choice: 'truth' …` | `here=0 inside=0 store=unchanged total=0 scenarios: 0 passed, 0 failed, 0 skipped locked=2` |
| truth check refuses --accept-harness and names config | NEW | `exit=2 hint=0 json=0` | `exit=2 hint=1 json=1` |
| The instance's last gate command is the truth check… | NEW | `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"` | `  - "{integration}/bin/factory truth check --store {integration}/.factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'"` |
| The truth check on this checkout reports no failure in the capabilities this change restates | NEW | `exit=2 ` | `exit=0 failed=0` |
| README, the design doc and the changelog describe the truth check | NEW | `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0` | `readonly=yes section=yes built=yes accepting=yes design=yes design-fence=yes changelog=1` |
| README, the design doc and the changelog describe the refusal route | REGRESSION (restated form) | — | `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, `CONTIGUOUS`, `entries=1 terms=3` |
| Implementer and verifier run prompts carry the declared-path rule | REGRESSION | — | `implementer declared=1 notunder=1 undeclared=1`, `verifier declared=1 notunder=1 undeclared=1` |
| Status transitions write the same events and history entries | REGRESSION | — | the 14 expected lines (`diff` empty) |
| Spec pinning and planner-run refusals keep their text | REGRESSION (restated form) | — | the 4 expected `{"ok": false, …}` lines |
| The dispatcher parks a refused store command with the same reason | REGRESSION | — | the 3 expected lines |
| The spec parser gives the same result as the base on every spec in the store | REGRESSION | — | `files=394 checks=6134 differ=0` |
| The refactored harness has no unused imports or variables | REGRESSION | — | `All checks passed!`, exit 0 (re-run at `2588b55`: same) |
| The harness suite passes and no existing test file changes | REGRESSION | — | `658 passed in 111.08s (0:01:51)`, nothing after it (`git diff --name-only --diff-filter=DMR main...HEAD -- tests` is empty at `2588b55`) |
| The drift checks live in factory/drift.py | REGRESSION | — | `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` |
| The shared helpers and the live-store fence live in factory/common.py | REGRESSION | — | `_add_spec_version _in_flight _integration_head _rel fence out` |
| Instance and store setup live in factory/setup.py | REGRESSION | — | the expected 14 names |
| The gates live in factory/gates.py | REGRESSION | — | the expected 18 names |
| The human decisions live in factory/human.py | REGRESSION | — | the expected 15 names |
| factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines | REGRESSION | — | `899 3` |
| Unmarked writes from inside the target are refused while a run is in flight, init included | REGRESSION | — | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` |
| The refusal names the throwaway store and not the marker | REGRESSION | — | `rule=1 state=1 marker=0 json=1 inside=1` |
| A harness acceptance is refused while a run is in flight | REGRESSION | — | `accept=2 store=unchanged` |
| A launch copy is written unmarked while a run is in flight… | REGRESSION | — | `launch=0 new=2 copies=1 store=unchanged` |
| The flag with init, paths or stats is refused… | REGRESSION | — | `init:`/`paths:`/`stats: exit=2 named=1 hint=1 json=1`, `target=unchanged`, `fresh: exit=2 files=0` |
| Without the flag paths and stats still run under another lock… | REGRESSION | — | `paths=0 stats=0 config=2 accept=0 lock=accepted` |

"Before" outputs come from `scratch/before/new-out.txt`. One note on the before column: my first "after" attempt at the live-store scenario printed `here=1 inside=1 … locked=1`. The cause was in my runner, not the code. The runner had not run that scenario's live-store-guard fixture, and the fixture's `run start` was also refused while the harness edits were uncommitted. Re-run after commit with its fixture, the scenario printed the line in the table.

Gate commands, each run exactly as written, at `2588b55`:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` exited 0: `658 passed in 112.90s (0:01:52)`.

**The full gate replay, as operator step 1 will run it.** I ran `bin/factory truth check --store <live store> --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'` from this worktree against the live store at `2588b55`. It exited 0:
- `339 scenarios: 276 passed, 0 failed, 63 skipped; wall time 128 s`;
- `folded: T-0059`, because this worktree is the store's `worktrees/T-0059.1`;
- the 63 skips are 34 scenarios in T-0059's delta, 13 WHENs that run the suite (the 14th is inside the delta) and 16 prose THENs.

The live store's `git status --porcelain` held 10 entries before and after the run: the operator's own uncommitted edits, unchanged.

On `eb6d383`, the same replay printed 1 failure: harness-suite's "The shared constants and wrappers are defined once" printed `ticket=2`. My new test file defined its own `ticket()` helper, which repeats a name the shared test helpers already define. Commit `2588b55` renames it to `write_ticket`. After that, the harness-suite capability alone prints `16 scenarios: 4 passed, 0 failed, 12 skipped`, and the full replay above is clean.

## Tests added/changed

- Added `tests/factory/test_truth.py`, 6 tests, about 13 s under xdist. I wrote the tests after the code. To check that they test the change, I ran them on an export of base `db28eb1`, where all 6 fail.
  - The exact-print rule: 14 forms that read and 9 that must not. These run in one Python subprocess from the repo root, because `tests/factory` is itself a package named `factory`.
  - Every skip reason, plus a GIVEN block reused through a quoted reference.
  - The failure detail: the 40-line cap, the `… 5 more lines` line, the exit status, stderr, and a THEN that says "exits 0".
  - The fold, from the integration checkout, an implementer worktree, and a checker checkout whose ticket has no parent. It also checks that the later delta's id wins, and that a scenario of another capability with the same name still runs.
  - A refused delta, where nothing runs.
  - The refusals: unknown capability, no current truth, caller outside git, and `--accept-harness`.
- No existing test changed.

## Known gaps and uncertainties

1. **Size.** The change is larger than the spec estimated. `factory/truth.py` is 297 lines against about 200, and its tests are 203 lines against about 150; the whole diff is 535 lines added and 18 deleted, against about 370. I did not compress the code to meet the estimate.
2. **A repeated check.** `specstore.applies` reads current truth from files, but the fold must check against text folded in memory, and `factory/specstore.py` is out of scope. So `fold()` repeats its ADDED/MODIFIED/REMOVED check in three lines, with the same error texts, and a comment says so. I also count `parse_delta`'s own errors as reasons to refuse, under the spec's "on any error, refuse".
3. **Folded scenarios are keyed by capability and name.** The spec says to record each scenario name of a folded delta with its id. I key it by capability and scenario name instead, so a same-named scenario in another capability still runs; a test covers this. With no duplicate names across capabilities today, the two readings give the same result on the live store.
4. **One skip reason the spec does not list.** A scenario with more than one THEN line is skipped as `has more than one THEN line`, mirroring the WHEN reason. The spec defines "the THEN" as "the one line", but lists no reason for two. An awk count over all 16 current-truth files found no such scenario, so this changes nothing today.
5. **Scenario splitting is reused indirectly.** `specstore.scenario_blocks` only reads delta parts of a spec version, so I prefix each capability's text with a dummy `=== specs/x/spec.md` line to reuse it. A comment says so. Duplicate scenario names within one capability would collapse to one, as they do elsewhere in the harness.
6. **README wording beyond the spec's letter.** In "Accepting a harness revision", adding `truth check` to the existing sentence as written would have grown README to 12 lines, one over the 11-line limit. I reworded the sentence instead. It stays one sentence, and the existing check that counts such sentences still passes: harness-docs' "README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy" is a PASS line in the full replay. To stay within the same limit, "Related work and history" gains no `#120` entry.
7. **A stale comment.** The comment above `gate_commands` in `.factory/instance.yaml` still says "whitespace errors…, then the harness's own suite". The new entry has its own comment line, as design C specifies, but the header comment does not mention the third command.
8. **Not tested on macOS's own shell.** The command runs the `bash` on `PATH`, which was Homebrew bash 5.3.9 here. Nothing was run under macOS's `/bin/bash` 3.2.
9. `factory:` markers added: none.

## Out-of-scope observations

- Running `bin/factory` leaves `factory/__pycache__/` in a checkout, because the launcher does not set `PYTHONDONTWRITEBYTECODE`. It is git-ignored, so nothing shows in `git status`.
- Two current-truth scenarios that measure a change against `main` (harness-code's "Every definition keeps its exact text…" and harness-suite's "The only existing test file changed is the stats test") are skipped as prose today. The spec's Risk section names them. An exact-print scenario of that kind added later would fail every gate.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION command printed its THEN on this branch, both gate commands pass, and the full live replay reports 0 failed.
ESCALATIONS: none
