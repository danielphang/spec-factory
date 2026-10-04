Commit: d45f0601ba30199152da28af556513dd2fc0caf0

How it was run: the PR head is the worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0141-verifier/wt` at `d45f060` (clean, `main` = merge-base = `924513e`). The base is a `git archive 924513e` extract in a scratch directory outside the repo. Every acceptance command ran with bash from each root, copied from the sub-ticket. The `fx` function was copied from `.factory/state/specs/T-0016/v1.md`; a `diff` of my copy against the spec's block was empty. This run's own prompt is the old verifier prompt (step 3: run every command on base), so REGRESSION commands also ran on base.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | implementer-runs-regression-checks-once | `design.md new=0 after=0 old=1` / `05-implementer.md new=0 after=0 old=1` / `implementer.md new=0 after=0 old=1` | `design.md new=1 after=1 old=0` / `05-implementer.md new=1 after=1 old=0` / `implementer.md new=1 after=1 old=0` | PASS
- NEW | verifier-runs-regression-on-base-only-on-failure | `design.md new=0 onfail=0 old=1 defect=1 gate=2` / `07-verifier.md new=0 onfail=0 old=1 defect=1 gate=1` / `verifier.md new=0 onfail=0 old=1 defect=1 gate=1` | `design.md new=1 onfail=1 old=0 defect=1 gate=2` / `07-verifier.md new=1 onfail=1 old=0 defect=1 gate=1` / `verifier.md new=1 onfail=1 old=0 defect=1 gate=1` | PASS
- NEW | one-run-serves-scenario-and-gate | `design.md=0 05-implementer.md=0 07-verifier.md=0 implementer.md=0 verifier.md=0 ` | `design.md=2 05-implementer.md=1 07-verifier.md=1 implementer.md=1 verifier.md=1 ` | PASS
- REGRESSION | changed-blocks-copied-verbatim | `05-implementer verbatim` / `07-verifier verbatim` | `05-implementer verbatim` / `07-verifier verbatim` | PASS
- NEW | one-sub-ticket-parent-closes-on-its-verified-run (`fx one`) | `one: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` | `one: subs=1 ready-for-parent-verify reuse=run-0004-verifier closed parent_runs=0 verified_by=run-0004-verifier` | PASS
- REGRESSION | parent-close-run-still-required-otherwise (`fx moved/two/uncovered`) | `moved: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` / `two: subs=2 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` / `uncovered: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=` | the same three lines | PASS
- NEW | rule-recorded-in-design-build-spec-readme-changelog | `design=0 buildspec=0 readme=0 changelog=missing` | `design=1 buildspec=1 readme=1 changelog=before-declined` | PASS

Every NEW base output equals the "today" output in the parent's `verification.md`, so each NEW criterion fails on base for the reason the spec states. On base `fx one` prints `reuse=None` because `parent-check` has no `reuse` field (`.get` returns None) and the close is refused.

Gate suite: PASS
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `136 passed in 149.17s (0:02:29)`, exit 0. This includes the 5 new tests in `tests/factory/test_parent_close_reuse.py` and the two edited `test_shepherd.py` tests.
- Tests to change: `git diff 924513e...HEAD -- tests/factory/test_shepherd.py` is `2 insertions(+)`, both the line `f.git("commit", "-q", "--allow-empty", "-m", "another change on main")`. No other line is touched and no assertion is removed.

Probes (variants of `fx`, run on the PR head; each in its own `mktemp -d`):
- The parent's own parent-close run. `main` moved, then a VERIFIED verifier run on T-0001 at the new `main`, then close → `reuse=None closed parent_runs=1 verified_by=run-0005-verifier`. The normal path still closes, and `verified_by` names the parent's own run, not a sub-ticket's. → OK
- The results row says VERIFIED, but the run's `meta.yaml` was edited to `status: FAILED` → `reuse=None refused`. Condition (3) reads the run record itself, not only the results row. → OK
- The sub-ticket text says `asked oncemore` where the scenario is `asked once` → `reuse=run-0004-verifier closed`. A longer word containing the scenario name counts as naming it. The spec chose "each name occurs in the text", and the PR lists this under Known gaps. It is not special-casing to the tested inputs. → CONCERN (minor, see ESCALATIONS)
- `archive` on a reused close, inside `fx` → refused with `no spec store (factory init not run)`. That is because `fx` never runs `factory init`, so it says nothing about reuse. The pytest test `test_a_single_sub_ticket_parent_closes_and_archives_on_its_verified_run`, which has a spec store, covers archive with a reused run, and it passed in the suite. → OK
- Read-through of `build.js` phase 3 (no runnable check exists). The new `parent-check` call falls back to the verifier when `pc.ok` is false or `reuse` is null. A wrong `reuse` value relayed by the clerk cannot close the parent on its own: `archive_cmd` and `ticket_transition` each re-run `_parent_close_verified` in the CLI. `openspec/` sits under the store root (`factory/specstore.py:48`), so `archive` makes no commit to `main`, and condition (2) still holds when the close follows the archive. → OK

STATUS: VERIFIED
CONFIDENCE: high. All seven acceptance commands match their THEN lines on the PR and the "today" lines on base, both gates pass at `d45f060`, and the probes show the reuse rule rejects a tampered run record and keeps the normal path's `verified_by`.
ESCALATIONS:
- Scenario coverage is a plain substring match (`factory/cli.py`, `_reused_subticket_run`: `all(n in text for n in names)`). A sub-ticket whose text contains a longer name with the scenario name inside it (`asked oncemore` for `asked once`) counts as covering that scenario, and the parent can then close without its own run. This follows the spec's wording, so it is not a FAIL. If the operator wants it tighter, matching whole names (for example on word boundaries) is a follow-up ticket.
