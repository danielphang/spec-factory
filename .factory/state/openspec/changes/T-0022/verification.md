## Acceptance

Each NEW item's failure was observed on an unchanged clone of `main` at `0b1abad`, and each THEN on a prototype of the change. Every command was copied verbatim from this spec and run in zsh through the fresh-HOME wrapper. The three build-dispatch scenarios and the system-prompt scenario were also run in bash, with the same output.

- A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored → REGRESSION. It prints `exit=0 ready-for-implementer runs=1` today, because nothing checks the field. It guards against a check that refuses too much, or that reads the Scope line.
- A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts → NEW. Today each of the three lines prints `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer`. The run starts, and its run directory and branch are created.
- The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back → NEW. Today it prints `park T-0001.2: budget kill: implementer`, because the implementer ran and the stub returned nothing. Then it prints `ruling=2 parked`.
- Every planner copy labels per sub-ticket and lists sibling tests → NEW. Today each line prints `own=0 sibling=0 interim=0 copied=1`, then `verbatim`.
- Every spec writer and critic copy carries the decision-overturns rule → NEW. Today it prints `writer=0 critic=0` on all three lines.
- Every preamble and reviewer copy accepts a sibling entry → NEW. Today it prints `guard=0 review=0` on all three lines.
- Planner, spec writer and critic runs get the new rules in their system prompts → NEW. Today it prints `planner own=0 sibling=0 guard=0 writer=0 critic=0`.
- The design doc and build spec describe the check → NEW. Today it prints `piece8=0 gate=0 stale=1 check=0 build=0`.
- The changelog records issue 40's change without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`.
- README describes the sibling tests check and its ruling → NEW. Today it prints `built=0 ruling=0`.
- The sibling-tests change adds no whitespace errors → REGRESSION. It prints `exit=0` on `main`, where the range is empty, and on the prototype.

Gate suite, not a scenario: `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, with pytest's temporary directory under `/tmp` as the harness-suite scenario in current truth sets it. Every test passes, including the new `tests/factory/test_sibling_tests.py`. The prototype without that file printed `265 passed`.

## Critic rounds

round 1 · spec v1 · run-0263-critic · APPROVE

## Critic review, round 1: T-0022 (planner labels per sub-ticket; sibling-added tests; tests a decision overturns)

### What I checked

All checks ran in `~/dev/spec-factory` at `0b1abad` (the revision the spec cites), through the fresh-HOME wrapper, with scratch files under this run's scratch directory.

Cited paths and symbols (rubric 1), all present as cited:
- `docs/design.md:507-510` holds the planner's Acceptance / "Tests to change" lines; `docs/prompts/04-planner.md:33-34` and `factory/prompts/planner.md:33-34` hold the same two lines, and the three copies are byte-identical today (`cmp`).
- `docs/design.md:46` (piece 8), `:146` (Spec approval row with "the only authorization to alter an existing test"), `:235` and `factory/prompts/preamble.md:63` (the guardrail sentence), `:376` (spec writer FORMAT), `:405` and `:413` (critic rubric 1 and 3), `:585-588` and `factory/prompts/reviewer.md:10` (test-integrity check).
- `factory/cli.py`: `run_start` at 198, `tripwire.baseline` at 212, `merge_cmd` at 528, the `merge` write at 553, `parent_base` at 560-561, the `--ruling` branch at 748-753, which already accepts a `BLOCKED` park and routes it to `ready-for-implementer`. `factory/workflows/build.js:68` is `runRole`, parking every refused start as `harness-bug: run start …`. `FIELD_RE` and `_is_heading` exist in `factory/subtickets.py`; `integration_branch` and `rev` exist in `factory/gitops.py`.
- The Evidence grep (`Tests to change|tests_to_change|diff-filter` over `factory bin agents`, minus `factory/prompts/`) prints exactly three `agents/` lines, as stated.
- The three verifier outputs (run-0057, run-0071, run-0092) carry the quoted SPEC-DEFECT reasons. In the Nanobot store, `git log --diff-filter=A -- tests/policy/test_commands.py` prints `37b8a9796 … (T-0002.4)`, and the only `(added by` in any stored sub-ticket is T-0002.6's Parallel-safe line.
- Insertion anchors exist: `- Open questions stay open.` (`factory/prompts/spec_writer.md:34`, `docs/design.md:332`), `**Only the dispatcher writes a live store during a run.**` (`docs/design.md:56`), README `## What is built and what is not` / `**Built**` (352-354), the Live-store fence bullet (377), the Unstick row (343), `dev/build-harness.spec.md` 203 / 245 / 275. The changelog's last entry is 52, so the new entry is 53; the awk check prints `CONTIGUOUS` today.

Acceptance commands run on unchanged `main` (rubric 2). Every NEW item fails today exactly as `verification.md` states, and the two REGRESSION items pass:
- build-dispatch scenario 1 (REGRESSION): `exit=0 ready-for-implementer runs=1`. The fixture's `ticket set … "merge.base_before='$A'"` writes the nested `merge` record, and `subticket add` accepts the `Interim tests:` and multi-line `Tests to change:` fields; the stored `specs/T-0001.2/subticket.md` carries the `(added by ST-1)` line inside that field and the Scope mention outside it.
- build-dispatch scenario 2 (NEW): three lines of `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer`.
- build-dispatch scenario 3 (NEW): `park T-0001.2: budget kill: implementer`, then `ruling=2 parked`.
- harness-docs planner scenario: three lines of `own=0 sibling=0 interim=0 copied=1`, then `verbatim`. System-prompt scenario: `planner own=0 sibling=0 guard=0 writer=0 critic=0`. Design/build-spec scenario: `piece8=0 gate=0 stale=1 check=0 build=0`. Changelog scenario: `CONTIGUOUS`, then `0`.
- Suite: `pytest --collect-only` collects 265 tests today, matching the prototype's `265 passed` without the new file. No test under `tests/factory/` pins the planner's "the same way" text, the preamble's guardrail sentence or the gate row's wording (grep); `test_design_block_equals_its_prompt_copy` compares design blocks with `docs/prompts/` copies, which part E re-copies. "Tests to change: none" holds.

Design points I traced (rubrics 4, 5):
- The refusal placement is sound: raising before `tripwire.baseline` and `next_run_id` writes nothing, which scenario 2's `runs=0 branch=0` would catch.
- The ancestor rule (`ancestor of main_after, not of base_before`) assigns a first-add commit to exactly one sibling when several have merged, since sibling n's `base_before` is sibling n-1's `main_after`.
- Operator steps are runnable as written: `instance.guard` and `fence` apply only to the instance's own store (`factory/instance.py:141-148`, `factory/cli.py:1210`), so the dev checkout's `bin/factory` can run against the Nanobot instance with a throwaway `FACTORY_STATE` without the lock refusing or the instance being written. `store.subtickets_of` scans the tickets directory, so deleting `T-0002.*.yaml` is enough for a from-scratch plan.
- Overlap with T-0025 (store on its own branch) and T-0027 (may edit the critic prompt) is declared under Risk; neither changes where `specs/<id>/subticket.md` lives or what this change reads.

The relayed operator request ("approve everything … slashing clearly redundant work") concerns the efficiency ledger, already recorded in `decisions.md` (T-0022, 2026-10-04). It does not change this review's rubric; the verdict below stands on the checks above.

### Findings

[NIT] 6 Decisions, bullets 3 and 4
Problem: `run start`, `exit 2` and `resolve --ruling` appear without a gloss, so the gate reader has to infer that `run start` is the harness command that reserves and prepares one agent run, and `resolve --ruling` the operator's command that answers a parked ticket.
Evidence: Decisions bullets 3-4; neither term is glossed in Problem or Evidence. Not the section's first paragraph, so not blocking.
Suggested fix: add a short appositive at each first use, for example "`run start`, the command that prepares one agent run" and "`resolve --ruling`, the operator's command for answering a parked ticket".

[NIT] 1 Evidence, "The parks happened"
Problem: the Nanobot citation `run-0147-implementer/output.md:87` is two lines off; the quoted sentence is at line 89 (line 87 is the CONFIDENCE line, which also names the T-0002.4 tests).
Evidence: `grep -n "cannot pass until three T-0002.4 tests" ~/dev/nanobot-upstream/.factory/state/runs/run-0147-implementer/output.md` prints `89:…`. The `run-0129…:102` citation is exact.
Suggested fix: change `:87` to `:89`.

No BLOCKING or SHOULD-FIX findings. The spec is grounded, every NEW scenario fails today for the stated reason and would catch a stub (the refusal must carry the exact prefix, name the file, and leave no run, branch or status change), the scope fits one PR with its two seams named, every protected path the change touches is declared, and the human-facing sections read without a translator.

### Out-of-scope observations

- `docs/prompts/02-spec-writer.md`, `03-spec-critic.md` and `06-code-reviewer.md` already differ from their `factory/prompts/` counterparts (`{400}` / `{2}` placeholders, and an extra acceptance-items bullet in `factory/prompts/spec_writer.md`). The spec's parts C and D add identical lines to each copy, which is correct; the pre-existing drift is not this ticket's.
- Part A's prompt says a sub-ticket with an `(added by …)` line "must depend on that sibling", while the harness accepts any merged sibling (Decision 2 says why). The prompt rule is unenforced; that is consistent with the Out of scope list and needs no change here.
