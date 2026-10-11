## Acceptance

- A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges → REGRESSION
- A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start → REGRESSION
- A merged sibling's merge is not drift, and a later commit or merge from elsewhere still is → NEW. Today, on `cce3d6f`, it prints `none: drift=1 greet=1 named=0 runs=0`, then `other: drift=1 greet=1 named=1 runs=0`, then `greet: drift=1 greet=1 named=1 runs=0`, then `merge: drift=1 greet=1 named=1 runs=0`. Part B is refused for its sibling's test, and every later refusal names the sibling's test too.
- A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts → NEW. Today it prints `ruling=2 parked kept=no drift=1`, then `start=2 runs=0`: `--ruling` refuses the park, and the sub-ticket stays parked.
- A ruling on a checker's or a compose step's harness-bug park is still refused → REGRESSION
- The design doc, build spec, README and changelog record both changes, and no prompt copy changes → NEW. Today it prints `design-drift=no design-ruling=no buildspec=no unstick=no bullet-sibling=no bullet-stale=yes prompts=0`, then `CONTIGUOUS`, then `0`.
- The sibling-merge change adds no whitespace errors → REGRESSION

## Responses

- [BLOCKING] 6, unglossed "store", "runtime checkout", "instance", `--accept-harness`: FIXED. Evidence bullet 1 now glosses the store at first use ("the factory's record of tickets, runs and log events, kept in `.factory/store/`"). Operator steps now says what the runtime checkout is, what an instance is, and what `--accept-harness <commit>` does and that an instance refuses to run until it is given. I also glossed three Problem terms the finding did not name but the same rule covers: the harness, the Workflow script and the driver.
- [BLOCKING] 2, no case pins that a non-sibling merge still parks: FIXED. The build-dispatch scenario gains case `merge`: a branch `ext`, which is no sub-ticket's recorded merge, commits `src/greet.py` with `tests/test_merge.py` and is merged `--no-ff`. Expected `merge: drift=1 greet=0 named=1 runs=0`. Run on a clone of `cce3d6f` it prints `merge: drift=1 greet=1 named=1 runs=0` today; with the prototype fix it prints the expected line, so a fix that skipped every merge commit would fail it. Design part C gains the matching suite case, part A says not to skip merge commits in general, Decision 2 says the same, and the Risk sentence now names all three still-drift cases. I used `tests/test_merge.py` rather than the suggested `tests/test_other.py` so the `named` count keeps its one pattern, `tests/test_$c.py`.
- [SHOULD-FIX] 2, `--short=9` can print more than 9 characters: FIXED. `named` now greps `changed by $(git -C $T27/t rev-parse HEAD | cut -c1-9)`, matching the code's `c[:9]` (`factory/cli.py:347`).
- [NIT] 6, revision cited as `f3a85bc`: FIXED. Evidence and verification.md now cite `cce3d6f`. `git diff --stat f3a85bc cce3d6f` shows only `dev/issues.md` changed, and I reran the drift scenario on `cce3d6f`.
- Out-of-scope observation (a hand-recorded fast-forward sibling merge): added one line under Out of scope. No design-doc sentence, since `factory merge` never fast-forwards.

## Critic rounds

round 1 · spec v1 · run-0418-critic · REVISE

Round 1 review of the v1 spec for issue #85 (sibling merges counted as spec drift; no resolve route for a `harness-bug: run start implementer:` park).

What I checked on `main` at `cce3d6f` (the spec cites `f3a85bc`; nothing it cites changed between the two):
- Cited paths and symbols: `factory/cli.py` `_check_sibling_tests` (def at line 245), `_check_drift` (276), `_test_drift` (316), the `--ruling` refusal (1183-1185), the `--redispatch` refusal (1223-1225); `factory/drive.py:179-186` and `factory/workflows/build.js:79-84` park a non-`BLOCKED ` run-start refusal as `harness-bug: run start <role>: …`; `store.subtickets_of` exists (`factory/store.py:230`); `store.park_ticket` records `parked.from` (`factory/store.py:154`). All as the spec says.
- Store evidence: `.factory/store/tickets/T-0040.1.yaml:53-55` and `T-0040.2.yaml:60-62` hold the cited `main_after` values; `T-0040.3.yaml:26-33` holds the harness-bug reason; the log holds the `ticket.parked` of T-0040.2 at 06:37:15 (from `ready-for-implementer`) and the `park.corrected` of T-0040.3 at 17:18:37. `git show --stat 2ad4d8c52` prints `factory/cli.py | 39` and `tests/factory/test_drive.py | 303`. `factory merge` does a `--no-ff` merge (`factory/cli.py:957`), so `main_after` is always a merge commit whose first-parent diff holds the whole sibling, which is what Decision 1 relies on.
- Document anchors: `docs/design.md:62` `**Spec drift.**`, `docs/design.md:109` the "BLOCKED, a critic ESCALATE, and a planner ESCALATE" bullet, `dev/build-harness.spec.md:318` the `factory resolve` entry and `:193` the Spec store paragraph with the drift sentence, `README.md:853` the Unstick row, `:920-931` the Spec amendment and drift bullet ending "has not yet fired on a real ticket", `README.md:9` the status date; `docs/changelog.md` last entry is 67; `dev/issues.md:89` lists #85.
- Acceptance commands run as written, through the running-code wrapper, with the `t0027-amend.sh` fixture written to my scratch directory:
  - harness-docs "The design doc, build spec, README and changelog record both changes…" printed `design-drift=no design-ruling=no buildspec=no unstick=no bullet-sibling=no bullet-stale=yes prompts=0`, `CONTIGUOUS`, `0`: exactly the "today" output verification.md states.
  - human-resolution "A ruling on a harness-bug park from an implementer's run start…" printed `ruling=2 parked kept=no drift=1`, then `start=2 runs=0`: exactly the stated "today" output, and the stored park was from `ready-for-implementer` with the harness-bug prefix.
- Tests pinning old behaviour: `grep -rn "ruling applies to" tests/factory` finds only `tests/factory/test_resolve_rulings.py:126`, which the spec lists. `tests/factory/test_spec_drift.py` has no test that merges a branch or asserts a merge commit counts as drift, and no other test asserts `--ruling` refuses a `harness-bug: run start implementer:` park. Tests to change is complete.
- Approved changes not yet archived: none, so rubric 5 raises nothing. #89 (retire the Workflow scripts) is consistent with the spec's choice not to touch `build.js`.

Findings

[BLOCKING] 6 proposal.md, Evidence first bullet and Operator steps step 1
Problem: the first paragraph of Evidence uses "the store's log" and the first paragraph of Operator steps uses "runtime checkout", "instance" and `--accept-harness`, none glossed anywhere in the spec, so the gate reader has to infer what the store is and what moving the runtime checkout means.
Evidence: read Problem, Evidence, Decisions and Operator steps as the new-to-this-system operator; "store" first appears in Evidence bullet 1 and "runtime checkout" / "instance" / `--accept-harness` only in Operator steps. The Problem's own glosses (parent, sub-ticket, sibling, drift check, park, ruling) are good and cover everything else.
Suggested fix: one clause each, for example "the store (the factory's record of tickets, runs and events)" at its first use, and in Operator steps "the runtime checkout (the copy of this repo the factory runs from, pinned to an accepted revision) … on each instance (each repository the factory serves)".

[BLOCKING] 2 specs/build-dispatch/spec.md, scenario "A merged sibling's merge is not drift, and a later commit from elsewhere still is"
Problem: the two still-drift cases (`other`, `greet`) are direct commits, so the obvious wrong fix, skipping every merge commit (or every commit with two parents) in the first-parent walk, passes all three cases while unflagging a non-sibling branch merged on main.
Evidence: in the WHEN, `land` makes plain commits on `main`; no case merges a branch that is not a recorded sibling merge. The Risk section says the `other` and `greet` cases "pin that other commits still park", but neither pins that a non-sibling merge still parks. Suite case C2 in design.md has the same gap.
Suggested fix: add a case (for example `merge`) where a second branch that is no sub-ticket's `main_after` is merged `--no-ff` into main changing `src/greet.py` and `tests/test_other.py`, expected `drift=1 greet=0 named=1 runs=0`, and mirror it in suite case C; then the Risk sentence is true.

[SHOULD-FIX] 2 specs/build-dispatch/spec.md, same scenario, `named=` count
Problem: `named` greps for `changed by $(git rev-parse --short=9 HEAD)` while the code prints `c[:9]`; `--short=9` prints more than 9 characters when 9 are ambiguous in that repo, so the match can fail on an unlucky hash in an otherwise correct build.
Evidence: `factory/cli.py:347` formats `c[:9]`; `git rev-parse --short=N` lengthens the output to stay unique. In a fresh throwaway repo of three or four commits this is very unlikely, so this is a flake, not a wrong expectation.
Suggested fix: use `$(git -C $T27/t rev-parse HEAD | cut -c1-9)`.

[NIT] 6 proposal.md, Evidence, "Reproduced on this checkout (`f3a85bc`)"
Problem: `main` has moved to `cce3d6f` (#90); harmless, since nothing the spec cites changed, but the reader may look for the revision.
Evidence: `git log --oneline -3`.
Suggested fix: none required; the implementer builds on current `main` anyway.

Not findings, noted for the writer: `git show --stat 2ad4d8c52` does print the two files as claimed (I first misread my own grep). The two REGRESSION labels in human-resolution and build-dispatch are right: the "still refused" cases are refused today by the prefix rule, and the fix narrows nothing they rely on.

Out-of-scope observations
- `README.md:919` and `:938-952` carry the same "It is tested, and has not yet fired on a real ticket" sentence for other features; the spec rightly touches only the drift bullet. The sibling-tests one (line 919) may also be stale after T-0040; not this ticket's concern.
- A sibling merged by hand with a fast-forward and recorded via `ticket set` would have a `main_after` that is not a merge commit; the exact-commit skip would then leave the sibling's earlier commits flagged. `factory merge` never does this, so no action, but worth a sentence in the design doc if the operator ever records merges by hand.

round 2 · spec v2 · run-0420-critic · APPROVE

Round 2 review of the v2 spec for issue #85 (sibling merges counted as spec drift; no resolve route for a `harness-bug: run start implementer:` park). Per the convergence rule I reviewed only the resolution of my round-1 findings and the text that changed between v1 and v2 (diffed the two versions in my input).

What I checked on `main` at `cce3d6f` (unchanged since round 1; working tree clean):
- The changed build-dispatch scenario "A merged sibling's merge is not drift, and a later commit or merge from elsewhere still is", run as written through the running-code wrapper with `t0027-amend.sh` written to my scratch directory: it printed `none: drift=1 greet=1 named=0 runs=0`, `other: drift=1 greet=1 named=1 runs=0`, `greet: drift=1 greet=1 named=1 runs=0`, `merge: drift=1 greet=1 named=1 runs=0`, exactly the "today" lines verification.md states. The `merge` case's refusal names `tests/test_merge.py changed by <the ext merge's first 9 hex>`, so the `named=` pattern with `cut -c1-9` matches the code's `c[:9]` (`factory/cli.py:347`), and the first-parent walk does diff a merge commit against its first parent (`factory/cli.py:343`, `git diff --name-only --no-renames {c}^1 {c}`). A fix that skipped every merge commit would print `merge: named=0` and fail the THEN, which is what the round-1 finding asked for.
- The harness-docs scenario, run as written: `design-drift=no design-ruling=no buildspec=no unstick=no bullet-sibling=no bullet-stale=yes prompts=0`, `CONTIGUOUS`, `0`, matching verification.md.
- Decision 1's "from the current plan or an earlier one": `store.subtickets_of` (`factory/store.py:228-236`) globs every `<parent>.*.yaml`, so superseded plans' sub-tickets are included, and `_check_sibling_tests` (`factory/cli.py:258`) reads the same list, as the Decision says.
- Tests pinning old behaviour, rechecked for the new `merge` case: `grep -n 'merge' tests/factory/test_spec_drift.py` finds nothing; no test asserts that a merge commit counts as drift. `grep -rn 'ruling applies to' tests/factory` still finds only `tests/factory/test_resolve_rulings.py:126`, which Tests to change lists with its line. Complete.
- Glosses: read Problem, Evidence, Decisions and Operator steps as the new operator. Harness, Workflow script, driver, store, runtime checkout, instance and `--accept-harness` are now glossed at first use. No first paragraph of those sections uses an unglossed term of art.
- Approved changes not yet archived: none, so rubric 5 raises nothing.

Prior findings
- [BLOCKING] 6, unglossed store / runtime checkout / instance / `--accept-harness`: RESOLVED. Evidence bullet 1 glosses the store; Operator steps step 1 glosses the runtime checkout, the instance and what `--accept-harness <commit>` does. The three extra Problem glosses (harness, Workflow script, driver) are correct and short.
- [BLOCKING] 2, no case pins that a non-sibling merge still parks: RESOLVED. The `merge` case merges branch `ext` with `--no-ff`, expects `merge: drift=1 greet=0 named=1 runs=0`, and today prints `greet=1`; design part A says not to skip merge commits in general, suite case C mirrors it, Decision 2 and Risk now say what the cases pin. Using `tests/test_merge.py` keeps the one `named` pattern; fine.
- [SHOULD-FIX] 2, `--short=9`: RESOLVED. `named` now uses `rev-parse HEAD | cut -c1-9`; confirmed matching on this run.
- [NIT] 6, revision `f3a85bc`: RESOLVED. Evidence and verification.md cite `cce3d6f`.
- Out-of-scope observation (hand-recorded fast-forward merge): taken into Out of scope; no design-doc sentence, which is right since `factory merge` never fast-forwards.

Findings

[NIT] 6 proposal.md, Decision 3, last sentence
Problem: "A failed `run compose` leaves its run in flight" uses `run compose` without saying what it is, and the operator cannot tell from the rest of the spec why that park must stay refused.
Evidence: `run compose` appears nowhere else in the human-facing sections; `factory/drive.py:191` parks it as `harness-bug: run compose <role>:`. Not a first paragraph, so not blocking.
Suggested fix: "A failed `run compose` (the step that writes a run's input after the run is created) leaves its run in flight, so …".

Not findings, noted for the writer: the Evidence suite line (512 passed, 8 failed, six from a temporary directory inside a git checkout) is honest and consistent with v1's 520; the implementer and verifier will run the suite properly. The "still refused" human-resolution scenario greps `--ruling applies to`, which Decision 4's new text still starts with, so the REGRESSION label holds after the change.

Out-of-scope observations
- As in round 1: `README.md` carries "It is tested, and has not yet fired on a real ticket" for other features too (the sibling-tests bullet at line 919 may also be stale after T-0040); the spec rightly touches only the drift bullet.
