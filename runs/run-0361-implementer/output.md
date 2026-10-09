Sub-ticket: T-0033.1, "Merge gate merges protected-path changes the approved spec never declared, and the reviewer prompt promises a check the gate does not run". Parent T-0033, approved spec v2 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0033/v2.md`).
Branch: `factory/T-0033.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0033.1`
Commit: `ba3fea8154f74ccd5007fd25d18f8215e0b7f000` (one commit on base `2f7f75f3961d2bd20b2fb106bd587ff94dd7621f`)

## What changed

Before this change, the merge gate merged any change to a protected path once the reviewer and verifier passed it. A protected path is a file the instance (one repository the factory runs on) lists in `instance.yaml` as sensitive; here, that is the harness's own code and the prompt copies. Now the gate refuses each changed protected path that the approved spec does not declare. The human answers the refusal with one of two new or rerouted commands. The reviewer and spec writer prompts and the documents now say what the gate actually does.

**A. Merge gate** (`factory/cli.py`, `factory/gitops.py`)
- `gitops.changed_files(repo, base, head, globs)` lists the paths `base...head` changes that match git glob pathspecs (`:(glob)<p>`, with `--no-renames`). It existed with no caller anywhere in the repo (grep of the whole tree: only its definition). I extended it in place rather than adding a second diff helper.
- `cli.declared_paths(spec_text)` reads the `Protected paths:` lines of the `## Risk` section with the spec's regular expression. It uses `specstore.lines_outside_fences`, so a line in a fenced block declares nothing and does not end the section. Entries starting `~` or `/` are skipped.
- `cli.undeclared_protected(root, cfg, t, head)` returns the sorted undeclared paths and where it read the declarations. The pinned spec is the parent's approved version, or the ticket's own when it has no parent. A path in the ticket's `accepted_paths` counts as declared.
- `merge_cmd` calls it after the three result checks and before the merge lock. A refusal logs `merge.refused` with `paths`, changes no ticket field and raises `BLOCKED from merge gate: protected paths not declared in <id> spec v<n>: <p1>, <p2>`. With no approved spec, the error reads `... not declared (<id> has no approved spec): ...`. The docstring names the new condition.
- `_branch_tip(repo, t)` is the existing "head is the branch tip" check, moved out of `merge_cmd` so that `--accept-paths` refuses with the same wording.

**B. Build workflow** (`factory/workflows/build.js`): when `merge` is refused with an error starting `BLOCKED `, the build parks the sub-ticket with that error, verbatim. Before, it recorded the refusal as a harness bug. That is one `if` line plus a comment.

**C. Human resolution** (`factory/cli.py` `resolve`, `build_parser`)
- New `resolve --accept-paths F`. It is added to the parser with the spec's help text, to the `--decision` guard and to the "resolve needs one of" message. Its refusals run in this order, and nothing is written until all of them pass:
  1. The park reason must start `BLOCKED from merge gate:`.
  2. The head must be the tip of its branch.
  3. At least one undeclared protected path must remain (`nothing to accept: ...`).

  It then writes F as the next `ruling-<n>.md` and sets `accepted_paths` to the sorted union. It moves the ticket to `checks-in-flight` (the state in which the reviewer and verifier judge it), and no result row moves.
- In `--ruling`, a park reason starting `ESCALATE from reviewer` now returns the ticket to `checks-in-flight` at the same round. Before, it went to `ready-for-critic`. Results that did not pass are set aside first. The set-aside block came out of `--redispatch` into `_set_aside_failed_rows(root, t)`, which both branches call; `--redispatch` behaves as before. The move records `head` and `superseded`.
- A `BLOCKED from merge gate:` park already took the BLOCKED branch of `--ruling`, which goes to `ready-for-implementer` at the same round. The code is unchanged there except its comment; a new test covers the route.

**D. Prompts.** In `docs/design.md`, the §6 check 6 block now carries the spec's exact text. The §2 `## Risk` FORMAT line now carries the four lines from the spec. Both blocks were re-copied to `docs/prompts/06-code-reviewer.md` and `docs/prompts/02-spec-writer.md`, and the same text change was made to `factory/prompts/reviewer.md` and `factory/prompts/spec_writer.md`. Scenarios 11 and 12 check that each block and its copy are byte-identical (`copy=SAME`) and that the run copies keep their fills (`fill=unchanged`).

**E. Documents**
- `docs/design.md`: the line-21, line-23, piece 7, piece 8 (both columns), piece 9, resolution-rule, merge-gate-row and Protected-paths gate-row edits, as specified. In this file they sit 2 lines lower than the spec's numbers, because `main` moved; each was matched by its text.
- `dev/build-harness.spec.md`: the piece-8 bullet (line 246) and item 25.
- `docs/changelog.md`: new entry 63, "After issue #57 (2026-10-05), ...". Numbering stays contiguous.
- `README.md`:
  - The merge-gate row of the terms table now says the gate checks declared protected paths, and glosses "protected path".
  - The "Merges, one at a time." bullet gains the new condition and a sentence saying a refusal parks the sub-ticket.
  - A new **Protected paths at merge.** bullet sits under Built.
  - The Unstick row gains `--accept-paths F` and the reviewer-escalation route.

Callers of the existing functions this change touches (coding standard rule 2, found by grep):
- `merge_cmd` is reached only through `bin/factory merge`, from `build.js` and the tests.
- `resolve` is reached only through `bin/factory resolve`.
- `gitops.changed_files` had no caller.
- The redispatch block's only caller was `--redispatch`; `test_redispatch_rows.py` and the human-resolution redispatch scenarios still pass.

## Acceptance results

I ran every scenario as written, from the worktree root, in the HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN blocks are the spec's `t0033-gate.sh`, the current-truth `t0023-wf.mjs` from human-resolution and `t0029-prompt.sh` from role-escalations. I extracted them, and each WHEN line, from the spec files with a script, so no command was retyped. The "before" run was on base `2f7f75f` with `uv sync --frozen` done; the "after" run was on `ba3fea8`. Full logs: `.../run-0361-implementer/scratch/before.txt` and `after.txt`.

| # | Scenario | Label | Before (base) | After (`ba3fea8`) |
|---|---|---|---|---|
| 1 | An undeclared protected path is refused at merge, by name, and nothing merges | NEW | `exit=0 blocked=0 named=0 declared=0 main=moved merged` | `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight` |
| 2 | Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing | NEW | `exit=0 named=0 main=moved` ×3 | `exit=2 named=1 main=unchanged` ×3 |
| 3 | A declared protected path, or an unprotected one, merges with no further approval | REGRESSION | `exit=0 merged` ×2 | `exit=0 merged` ×2 |
| 4 | The build parks a merge refused for protected paths with the gate's reason | NEW | `park: harness-bug: merge: BLOCKED from merge gate: ...core/b.py` | `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py` |
| 5 | Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through | NEW | `accept=2 parked rows=3 ruling=missing` / `merge=2 on_main=1` | `accept=0 checks-in-flight rows=3 ruling=kept` / `merge=0 on_main=1` |
| 6 | Accepting paths is refused on any other park and writes nothing | NEW | `accept=2 refused=0 parked rulings=0` | `accept=2 refused=1 parked rulings=0` |
| 7 | A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling | NEW | `ruling=2 parked reason=0` / `in_input=0` | `ruling=0 ready-for-implementer reason=1` / `in_input=1` |
| 8 | A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling | NEW | `exit=0 ready-for-critic kept: ci.yaml reviewer.yaml verifier.yaml ` / `in_input=0` | `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` / `in_input=1` |
| 9 | All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 | REGRESSION | the 4 expected lines | `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` |
| 10 | The reviewer run prompt says what the merge gate checks | NEW | `gate=0 promise=1` | `gate=1 promise=0` |
| 11 | Every reviewer prompt copy states what the merge gate checks | NEW | `gate=0 promise=1` ×3, `copy=SAME fill=unchanged` | `gate=1 promise=0` ×3, `copy=SAME fill=unchanged` |
| 12 | Every spec writer prompt copy gives the declaration line | NEW | `reads=0 form=0 braces=0` ×3, `copy=SAME fill=unchanged` | `reads=1 form=1 braces=1` ×3, `copy=SAME fill=unchanged` |
| 13 | The design doc and build spec drop the per-PR approval for protected paths | NEW | `gates=1 either=1 onpr=1 piece8=0 piece9=1 gaterow=0 stale=1 reviewer_rule=0 old_route=1 build=1 build_new=0` | `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1` |
| 14 | The changelog records issue 57's change without a numbering gap | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| 15 | README describes the protected-path check and the new resolve verb | NEW | `built=0 unstick=0 merges=0` | `built=1 unstick=1 merges=1` |
| 16 | The protected-path change adds no whitespace errors | REGRESSION | `exit=0` | `exit=0` |

What the table shows:
- Every NEW scenario failed on the base exactly as `verification.md` predicted, so the spec matches the code it was written against.
- Every scenario prints its THEN line exactly on `ba3fea8`.
- The REGRESSION scenarios (3, 9 and 16) passed after the change, so no base re-run was needed.

Gates, on commit `ba3fea8`, from the worktree, each exactly as written:
- `(export HOME=...; git diff --check main...HEAD)`: no output, exit 0. The branch adds no whitespace errors.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `408 passed in 317.17s`. The whole harness suite passes, the new file included.

Also, not a gate: `ruff check` on the changed Python files printed `All checks passed!`. I also checked this change against its own Risk line, using the new `declared_paths` on `specs/T-0033/v2.md` and this instance's `protected_paths`. Every changed file under `factory/**` and `docs/prompts/**` is declared, so the new gate would merge this change as is.

## Tests added/changed

- Added `tests/factory/test_merge_protected_paths.py`: 17 cases on a Python port of the `t0033-gate.sh` fixture, all driven through `bin/factory`.
  - The refusal: its exact text, no backtick, `$` or double quote in it, main unchanged, ticket record unchanged, and one `merge.refused` event with sorted `paths`.
  - Five cases that declare nothing: another ticket's declaration, a move out of the protected tree, a Risk line in another form, a fenced line, and a brace-list entry.
  - Three cases that merge: a declared glob, a list marker with a trailing full stop, and unprotected paths only.
  - A ticket with no parent and no approved spec.
  - The build park, through `build.js` with a stub clerk.
  - `--accept-paths`: acceptance and then the merge; refusal on another park; refusal when the head is not the branch tip; refusal when nothing remains.
  - `--ruling` on a merge-gate park.
  - `--ruling` on a reviewer ESCALATE, with set-aside rows and the round unchanged.

  Before the code change, the file gave `14 failed, 3 passed`. The 3 that passed were the merge cases, which are regressions. After the change, all 17 pass.
- No existing test changed. The spec's "Tests to change" is none.

## Known gaps and uncertainties

- `factory:` markers added: none.
- The protected-path patterns are flattened in `undeclared_protected` with the same one-liner `instance.fill_preamble` uses (`[globs] if isinstance(globs, str) else list(globs or [])`). A shared helper would belong in `factory/instance.py`. That file is protected and the approved Risk line does not declare it, so I left it alone. The duplication is one expression.
- An entry that git rejects as a pathspec stops the gate with a git error instead of a `BLOCKED` refusal. I checked this: `` `../x` `` makes git exit 128 with "outside repository". In that case `merge` exits 2 with a `git diff ...` error, and the build parks the sub-ticket as `harness-bug: merge: ...`, not as a merge-gate park. The spec does not cover this. No current spec declares such an entry.
- The README status date stays `2026-10-09`. It already reads that date, which is today in UTC (this machine's local date is 2026-10-08). If the merge lands on a later date, the date needs moving at merge.
- The spec puts `--accept-paths` after `--ruling` in the order a mixed call takes, so `--ruling F --accept-paths G` runs `--ruling` only. The spec does not say what such a call should do, and I added no refusal for it.

## Out-of-scope observations

- The build spec's piece-8 wording (`protected path <p> not declared in the pinned spec v<N>`, one path per message) describes the unbuilt pre-receive design. It differs from the local gate's single `BLOCKED from merge gate: protected paths not declared in <id> spec v<n>: <p1>, <p2>` message. Both texts are as the spec dictates. They describe different gates, but a reader may expect them to match.
- `docs/design.md` line 76 (implementer model choice: "no protected path") and the sub-ticket `Protected paths:` field at line 574 are unchanged, as the spec's Out of scope says.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance scenario prints its THEN exactly on the commit, every NEW one failed on the base as described, and both gates pass (408 tests).
ESCALATIONS: none
