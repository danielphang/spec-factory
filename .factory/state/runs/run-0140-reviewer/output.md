Commit: d45f0601ba30199152da28af556513dd2fc0caf0 (branch `factory/T-0016.1`, base `924513ecb731b57f4396b602ff31a1169150b3e3`, two commits `50fd7a3` and `d45f060`)

## What I checked, in the required order

1. **Test integrity.** `git diff main...HEAD --stat` touches one existing test file, `tests/factory/test_shepherd.py`, with 2 insertions and 0 deletions. Both insertions are the line `f.git("commit", "-q", "--allow-empty", "-m", "another change on main")`, one in each of the two tests the spec lists under "Tests to change" (`test_shepherd.py:224` and `:487`), each placed after the sub-ticket's merge and before `f.parent_check(tid)`. No assertion is removed, loosened or re-ordered. The new file `tests/factory/test_parent_close_reuse.py` adds five tests, none skipped, with assertions on `reuse`, the refusal exit code and message, `verified_by`, and the absence of a parent verifier run. Clean.

2. **Correctness against the spec.** I re-ran every acceptance command from the sub-ticket with bash from the worktree root at `d45f060`:
   - implementer-runs-regression-checks-once: `design.md new=1 after=1 old=0` / `05-implementer.md new=1 after=1 old=0` / `implementer.md new=1 after=1 old=0`. Matches THEN.
   - verifier-runs-regression-on-base-only-on-failure: `design.md new=1 onfail=1 old=0 defect=1 gate=2` / `07-verifier.md new=1 onfail=1 old=0 defect=1 gate=1` / `verifier.md new=1 onfail=1 old=0 defect=1 gate=1`. Matches THEN; the `defect` and `gate` counts show the SPEC-DEFECT and gate-failure refusals are still in every copy.
   - one-run-serves-scenario-and-gate: `design.md=2 05-implementer.md=1 07-verifier.md=1 implementer.md=1 verifier.md=1`. Matches.
   - changed-blocks-copied-verbatim: `05-implementer verbatim` / `07-verifier verbatim`. The two `docs/prompts/` files equal their design blocks byte for byte.
   - one-sub-ticket-parent-closes-on-its-verified-run, with `fx` copied verbatim from the parent spec: `one: subs=1 ready-for-parent-verify reuse=run-0004-verifier closed parent_runs=0 verified_by=run-0004-verifier`. Matches: the parent closed with no verifier run of its own and recorded the sub-ticket's run.
   - parent-close-run-still-required-otherwise: `moved: … reuse=None refused parent_runs=0 verified_by=`, `two: subs=2 … reuse=None refused …`, `uncovered: subs=1 … reuse=None refused …`. All three still refuse the plain close.
   - rule-recorded-in-design-build-spec-readme-changelog: `design=1 buildspec=1 readme=1 changelog=before-declined`. Matches.
   - I also ran the three grep-based NEW scenarios against `main` (`924513e`) via `git show main:<file>`: `new=0 after=0 old=1` on all three implementer copies, `new=0 onfail=0 old=1 defect=1 gate=2|1|1` on the verifier copies, and `design=0 buildspec=0 readme=0`. The NEW checks fail on the base as the spec says they should.

   Code read against part C (`factory/cli.py:864-896`): conditions (1) to (4) are each present and in the spec's form. (1) `len(subs) != 1`, `status == "merged"`, `merge.main_after` set, `parent_base` set, plus a `head` check the spec implies. (2) `gitops.rev(repo, integration_branch) == main_after`. (3) results row `status == VERIFIED` with a `run_id`, and that run's `meta.yaml` with `status: VERIFIED`, `head == s["head"]`, `base == parent_base`; `store.record_result` (`factory/store.py:186`) writes `status` and `run_id`, and `run start` writes `base` and `head` into meta (`factory/cli.py:245,258`), so the keys exist. (4) `specstore.scenario_names` (`factory/specstore.py:154`) on the pinned `v<approved_version>.md`, non-empty, each name a substring of `subticket.md`. `_parent_close_verified` (`cli.py:899-917`) returns the run directory name for the parent's own run, else falls through to `_reused_subticket_run`; both callers (`ticket_transition` `cli.py:157`, `archive_cmd` `cli.py:926`) keep a truthiness test, and I confirmed with grep there are no others. `ticket_transition` appends `verified_by` only when set (`cli.py:166-167`). `ticket_parent_check` computes `reuse` only in `ready-for-parent-verify` and writes nothing new to the store (`cli.py:601`).

   `factory/workflows/build.js:217-234`, read against part C since it has no runnable check: phase 3 now calls `ticket parent-check` first, takes `pc.reuse` when `pc.ok`, logs the stand-in sentence, skips `runRole('verifier')`, and passes `[runId]` as the park outputs to `archive`; the non-reuse path is the old code unchanged, with `runId = v.runId`. If the parent-check clerk fails, `runId` is null and the verifier runs as today, which is the safe fallback. Phase 2 (`build.js:206-209`) reads only `pc.state`, so the new field does not change it.

3. **Scope.** Twelve files, each named in parts A to E of the sub-ticket. `docs/design.md`'s 37 changed lines are the Archive paragraph (line 82), the Merge gate row (line 126), and the `## 5. Implementer` and `## 7. Verifier` blocks only. Nothing outside the lettered parts.

4. **Silent behavior changes.** One, and the spec asks for it: `ticket parent-check` now runs `git rev-parse` on the integration branch when the parent is `ready-for-parent-verify`, where before it touched no git state. A missing repo or branch would turn into a `Refused` exit 2 from a command that used to be a pure store read. By the time a parent is `ready-for-parent-verify` a merge into that branch has already happened, so the branch exists in every path the build takes. Not a finding.

5. **Security and data safety.** No new inputs reach a shell; `gitops.git` passes argv lists. Reads under the store only. No destructive operation added.

6. **Protected paths.** Touched: `factory/cli.py`, `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/workflows/build.js` (harness), `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md` (generated). All six are declared in the sub-ticket's "Protected paths" line and the parent's Risk section. Listed under ESCALATIONS below; the merge gate will want a human approval.

7. **Coding standard.** `_reused_subticket_run` carries one `factory:` comment naming the limit (one sub-ticket; coverage read from names in the sub-ticket text) and the upgrade trigger (a per-sub-ticket coverage map in the store) (`cli.py:867-868`). It reuses `store.subtickets_of`, `store.results_for`, `store.read_yaml`, `gitops.rev`, `gitops.integration_branch`, `specstore.scenario_names`; the inline `meta.yaml` read follows the existing pattern in `_parent_close_verified` and `compose.py`, and no run-meta helper exists to reuse. The new test file reuses `built_to_implementer` from `test_shepherd.py`. Lean already.

8. **PR description.** What changed and Known gaps are written as prose, per part, and gloss `parent-close run`, NEW and REGRESSION at first use. Known gaps names the marker, the substring match, the untested `build.js` skip and the constructed base-mismatch history, which is what an operator needs. One gloss gap, below.

Gates at `d45f060`, run by me: `git diff --check main...HEAD` exit 0, no output; `uv run --frozen pytest -q -p no:cacheprovider tests/factory` → `136 passed in 203.26s`, exit 0.

## Findings

- [NIT] PR description: What changed, part C, conditions 1 to 3: `main_after` and `parent_base` are store field names used without saying what they hold (the integration-branch commit after the sub-ticket's merge; the `main` commit before the parent's first merge). A reader new to the project cannot tell from the description what "the integration branch is still at that `main_after`" compares. Writing standard rule 2; prose only, the code is unaffected.

Prior findings: none (round 1).

## Out-of-scope observations

- `factory/workflows/build.js:3,7`: the `meta` description and the Close phase detail still say every build makes one parent-close verifier run. Labels only; part C does not name them. The implementer noted the same.
- `agents/` holds no implementer, reviewer or verifier definition, so there is no fourth copy of either prompt to keep in step. A grep for the old step-2 and step-3 wording across `README.md`, `dev/`, `docs/`, `factory/`, `agents/` and `tests/` finds nothing outside the changelog.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance command matches its THEN line on the head and the NEW ones fail on the base; both gates pass on my own run (check exit 0, 136 passed); the two edited tests gained only the listed line; the `build.js` skip, which has no runnable check, matches part C on reading.
ESCALATIONS: protected paths touched, all declared by the sub-ticket and the spec's Risk section, so a human approval is required at the merge gate: harness `factory/cli.py`, `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `factory/workflows/build.js`; generated `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`.
