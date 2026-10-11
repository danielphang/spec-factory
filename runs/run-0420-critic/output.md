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

STATUS: APPROVE
CONFIDENCE: high, both blocking findings resolved with the changed scenario run on this checkout and printing the stated today output, including the new `merge` case whose refusal names the merge commit; Tests to change rechecked for the new case
ESCALATIONS: none
