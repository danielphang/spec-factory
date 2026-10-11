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

STATUS: REVISE
CONFIDENCE: high, every cited path, store record and both spot-run acceptance commands checked on this checkout; the two blocking items are a gloss and one missing still-drift case, both small
ESCALATIONS: none
