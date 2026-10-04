## Critic review, round 1

Checked on `main` at `3b87d6c` (`git rev-parse --short HEAD`), from `~/dev/spec-factory`.

### What I verified

Grounding (rubric 1):
- Every cited path and range exists and says what the spec says: `factory/prompts/implementer.md:5-7` (step 2 runs all acceptance commands), `factory/prompts/verifier.md:9-14` (step 3 runs them all on base), `docs/design.md` blocks at ~492 and ~607, `factory/cli.py:153-157` (close refused without `_parent_close_verified`), `494-538` (`merge_cmd`, `--no-ff`, head must contain main), `586-600` (`ticket_parent_check`, no skip), `860-877` (`_parent_close_verified`), `889` (archive gate), `factory/workflows/build.js:217-222` (unconditional parent-close verifier), `tests/factory/test_shepherd.py:227-228` and `487-488`, `docs/design.md:82` and `:126`, `dev/build-harness.spec.md:285`, `README.md:94`. Symbols `store.subtickets_of`, `store.results_for`, `specstore.scenario_names`, `gitops.rev`, `gitops.integration_branch` exist; tickets carry `spec.approved_version` and `parent_base`; results rows carry `run_id`; verifier run `meta.yaml` carries `base`, `head`, `status`.
- Evidence table: summed `wall_s` from the 18 run `meta.yaml` files gives 1,754 / 1,878 / 1,650 s; parent-close runs 330 / 244 / 386 s; shares 19% / 13% / 23%. Suite times quoted from `run-0131`, `run-0132` (`output.md:16`, gate line `:25` repeats `112.14s`) and `run-0134` (`output.md:16`) match; six runs sum to 572.8 s.
- `git rev-parse <sha>^{tree}`: e703c1b/01f7524 → 6edc60e, 89e8b7d/fcc8756 → b65b1c3, 27d6d63/530c9ef → 197f557. Parent bases 0759162 / 431e349 / 61d92be equal `run-0110` / `run-0124` / `run-0132` bases. Scenario coverage of sub-ticket text 9/9, 7/7, 10/10. T-0012 has six sub-tickets and `run-0102` is SPEC-DEFECT. `530c9ef` touches `factory/cli.py` and `factory/instance.py`; `fcc8756` only `docs/writing.md`. `~/dev/nanobot-upstream` has no `factory/` directory.

Acceptance commands run as written (rubric 2):
- `implementer-runs-regression-checks-once`: all three lines `new=0 after=0 old=1`.
- `verifier-runs-regression-on-base-only-on-failure`: `design.md new=0 onfail=0 old=1 defect=1 gate=2`, the other two `… gate=1`. The second design.md "A gate failure" is at `docs/design.md:88`, outside the verifier block, so `gate=2` stays correct after part B.
- `one-run-serves-scenario-and-gate`: all five `=0`.
- `changed-blocks-copied-verbatim`: `05-implementer verbatim`, `07-verifier verbatim`.
- `rule-recorded-…`: `design=0 buildspec=0 readme=0 changelog=missing`.
- `fx one`: `one: subs=1 ready-for-parent-verify reuse=None refused parent_runs=0 verified_by=`. `fx moved|two|uncovered`: the three lines exactly as the THEN states. The fixture's sub-ticket verifier run records `base` equal to the parent's `parent_base` and `head` equal to the merged head, so condition (3) of part C is satisfiable by this fixture and the NEW scenario would fail against a stub that ignores the base. Run ids land as `run-0004-verifier`.
- Gates: `git diff --check main...HEAD` → `check=0`; `131 passed in 92.40s`.

### Findings

[SHOULD-FIX] 3 Tests to change, second test
Problem: `test_a_parent_does_not_close_by_a_plain_transition_before_its_parent_close_run` does not break under part C, so its listed reason is wrong and the edit is to a guardrail file without need.
Evidence: `built_to_implementer` (`tests/factory/test_shepherd.py:390-393`) runs `init`, so the spec store is active and the change folder exists. After part C, `ticket_transition` at `factory/cli.py:153-157` finds `_parent_close_verified` truthy and then refuses with "verified but not archived: run `archive`" (`cli.py:158-159`), still exit 2 with state unchanged. The assertion at `:488` checks only `returncode == 2` and the state, so it passes. The first test does break: `archive` at `:227` would succeed instead of refusing.
Suggested fix: either drop the second test from Tests to change, or keep the edit with the true reason (the refusal it tests would come from the archive check instead of the parent-close check, so the extra `main` commit keeps the test testing what its name says).

[SHOULD-FIX] 6 Decisions, first bullet
Problem: "The path-scoped gate skip" opens Decisions with a term the human-read sections have not glossed; its only gloss is in Out of scope, which the writing standard does not count.
Evidence: Problem and Evidence never name it; Out of scope line 1 defines it. By the rubric's letter this is BLOCKING, but the gloss sits six lines above and the bullet's own second sentence says what breaks, so a gate reader is not lost. I am not blocking on it.
Suggested fix: open the bullet with "The request's path-scoped gate skip, which would skip a gate command when the diff touches none of its declared paths, is cut."

[NIT] 1 Evidence, parent-close verifier paragraph
Problem: `output.md:44` does not exist; `run-0134-verifier/output.md` has 39 lines.
Evidence: `wc -l`; the whitespace-gate note is at line 27 ("Main equals HEAD in a parent close, so this diff is empty").
Suggested fix: `output.md:27`.

[NIT] 6 Decisions, fourth bullet
Problem: "the integration branch" appears without being tied to `main`, which is the name the Problem section uses.
Evidence: Problem says "the branch is merged" and "`main`"; Decisions says "integration branch"; README glosses the pair, the spec does not.
Suggested fix: "`main` (the integration branch)" at first use.

### Judgement beyond the rubric

- Part C's reuse condition is the right shape: tree identity is guaranteed by the merge gate rather than asserted, the base match is read from run metadata, and scenario coverage is checked by name against the pinned spec. The fallback is today's behaviour. The accepted loss (one independent run) is stated with its evidence.
- Parts A and B keep each refusal as its own sentence, and the scenarios pin the spec-defect and gate-failure sentences. A verifier reading the new step 3 cannot skip a NEW base run without ignoring an explicit sentence.
- One PR is reasonable: four harness files, three prompt copies, four records, one new test file, two one-line test edits.

### Out-of-scope observations

- The harness briefing says green is on `feat/lionbot-v3`; `git -C ~/dev/nanobot-upstream branch --show-current` prints `feat/lionbot-v3.5`. The spec's "no `factory/` directory on its current branch" is correct either way.

STATUS: APPROVE
CONFIDENCE: high. Every cited path, figure and SHA re-derived from the store and git; every acceptance command run on `3b87d6c` and matching the stated today-output; the fixture's recorded metadata shows the reuse condition is testable.
ESCALATIONS: none
