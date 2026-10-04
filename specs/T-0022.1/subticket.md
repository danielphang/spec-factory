## ST-1 / Sibling tests: per-sub-ticket labels, the harness check, prompts and documents
Depends on: none
Parallel-safe: yes

Parent: T-0022 (issue #40), the approved spec v1 pinned in the store under `specs/T-0022/`. Read it for context. Do NOT implement parts outside this sub-ticket.

  Scope: all of the parent's parts.
    - A: planner block in `docs/design.md` §4, `docs/prompts/04-planner.md` and `factory/prompts/planner.md`, kept byte-identical in that block.
    - B.1 to B.5:
      - `PLAN_FIELDS` and `sibling_tests` in `factory/subtickets.py`.
      - `first_added` and `is_ancestor` in `factory/gitops.py`.
      - `_check_sibling_tests` in `run_start` in `factory/cli.py`, placed before `tripwire.baseline`.
      - The `BLOCKED ` refusal park in `runRole` in `factory/workflows/build.js`.
      - The new `tests/factory/test_sibling_tests.py`.
    - C: the spec writer RULES bullet and the critic rubric 1 lines, in all three copies of each.
    - D: the preamble guardrail sentence and the code reviewer's test-integrity line, in all three copies of each.
    - E.1 to E.6:
      - `docs/design.md`: piece 8, the Spec approval row, and the `**Tests a sibling added.**` paragraph.
      - `docs/changelog.md`: the "After issue #40 (2026-10-04)" entry.
      - `dev/build-harness.spec.md`: lines 203, 245 and 275.
      - `README.md`: the Built bullet and the Unstick row.
  Acceptance (WHEN command and THEN result exactly as in the parent's spec files; label is the verification.md label, re-checked against this sub-ticket's base `c2750bf` above):
    - "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored". WHEN: the parent's GIVEN block, run once, then its `(E=tests/test_interim.py; . …t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 …)` command. THEN `exit=0 ready-for-implementer runs=1`. REGRESSION.
    - "A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts". WHEN: the `for E in tests/test_old.py tests/test_operator.py tests/test_never.py` command. THEN three lines, each `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`. NEW.
    - "The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back". WHEN: the `node …t0022-build.mjs` then `resolve --ruling` command. THEN `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`. NEW.
    - "Every planner copy labels per sub-ticket and lists sibling tests". THEN three lines of `own=1 sibling=1 interim=1 copied=0`, then `verbatim`. NEW.
    - "Every spec writer and critic copy carries the decision-overturns rule". THEN `design: writer=1 critic=1`, `docs/prompts: writer=1 critic=1`, `factory/prompts: writer=1 critic=1`. NEW.
    - "Every preamble and reviewer copy accepts a sibling entry". THEN `design: guard=1 review=1`, `docs/prompts: guard=1 review=1`, `factory/prompts: guard=1 review=1`. NEW.
    - "Planner, spec writer and critic runs get the new rules in their system prompts". THEN `planner own=1 sibling=1 guard=1 writer=1 critic=1`. NEW.
    - "The design doc and build spec describe the check". THEN `piece8=1 gate=1 stale=0 check=1 build=1`. NEW.
    - "The changelog records issue 40's change without a numbering gap". THEN `CONTIGUOUS`, then `5`. NEW.
    - "README describes the sibling tests check and its ruling". THEN `built=1 ruling=1`. NEW.
    - "The sibling-tests change adds no whitespace errors". WHEN `(git diff --check main...HEAD; echo "exit=$?")`. THEN only `exit=0`. REGRESSION.
    - The gate suite is the parent's gate, not a scenario. Run `uv run --frozen pytest -q -p no:cacheprovider tests/factory` with pytest's temporary directory under `/tmp`, as current truth's harness-suite scenario sets it. Every test must pass, including the new `tests/factory/test_sibling_tests.py`. REGRESSION for the existing tests. The new file's cases are NEW:
      - each build-dispatch scenario case;
      - an unmerged sibling (no `parent_base`) refuses;
      - a file that was added, deleted and re-added counts by its first add;
      - `sibling_tests` ignores a mention in the Parallel-safe line, as in the stored sub-ticket T-0002.6.
  Tests to change: none. This is the parent's list. The new test file is added, not changed.
  Protected paths: the parent's full Risk list.
    - Harness: `factory/cli.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/workflows/build.js`, `factory/prompts/{preamble,planner,spec_writer,critic,reviewer}.md`.
    - Generated: `docs/prompts/{00-preamble,02-spec-writer,03-spec-critic,04-planner,06-code-reviewer}.md`, each re-copied from its design-doc block.
  Out of scope, as the parent's Out of scope lists it:
    - An implementer editing a test on its own judgement.
    - A merge-gate comparison of changed tests with "Tests to change".
    - Any harness check of NEW and REGRESSION labels.
    - Any harness read of "Interim tests".
    - `agents/**`, `.factory/**`, `bin/factory`, `pyproject.toml` and `uv.lock`.
    - Any write to a store record or to `~/dev/nanobot-upstream`.
    - The parent's Operator steps: the re-plan and re-spec of Nanobot's T-0002. These are for the operator after merge, not for this sub-ticket.

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The spec allows two seams: the prompt texts (A, C, D) and the harness check (B). I did not take that split, for three reasons:

- The new prompt texts in A and D tell every role that "the harness checks" a sibling entry. If the prompts merged before B, every role would be told about a check that does not run yet.
- The parent's changelog scenario needs one "After issue #40" entry that names both the prompt changes ("own base", "Decision", "critic rubric 1") and the harness check ("added by", "BLOCKED from harness"). Two PRs would have to share that one entry, and both would edit `docs/design.md` and `README.md`.
- The change is about 180 lines plus one new test file. Both seams touch protected paths, so each would need the operator's protected-path approval at merge. Splitting would make that approval happen twice and give review or rollback nothing in return.

I checked the labels against this sub-ticket's own base, today's `main` at `c2750bf`. The spec's prototype ran at `0b1abad`, and T-0025's merges have moved `main` since then. Every scenario in the table below was run from `~/dev/spec-factory` with a fresh HOME and `TMPDIR` set to this run's scratch directory. Each one printed exactly the "today" output that `verification.md` gives:

| Scenario | Output on `c2750bf` |
|---|---|
| merged-sibling REGRESSION | `exit=0 ready-for-implementer runs=1` |
| refused | three lines of `exit=0 blocked=0 names=0 runs=1 branch=1 ready-for-implementer` |
| build park | `park T-0001.2: budget kill: implementer`, then `ruling=2 parked` |
| planner copies | `own=0 sibling=0 interim=0 copied=1` ×3, then `verbatim` |
| writer/critic | design `writer=0 critic=0` |
| preamble/reviewer | design `guard=0 review=0` |
| design/build spec | `piece8=0 gate=0 stale=1 check=0 build=0` |
| changelog | `CONTIGUOUS`, then `0` |
| README | `built=0 ruling=0` |

So every NEW label still fails on this base, and the parent's labels hold unchanged. The system-prompt scenario was not run: the role prompts it reads from are unchanged, and the planner-copy checks above already print `own=0` on them. The spec's anchors still hold on `c2750bf`:

- `factory/cli.py`: `run_start` at :198, `tripwire.baseline` at :212, the BLOCKED ruling at :748.
- `factory/workflows/build.js`: `runRole` at :66, with the `harness-bug: run start` park at :68.
- `docs/design.md`: piece 8 row at :46, Spec approval row at :146, the "Only the dispatcher writes a live store" paragraph at :56.
- `dev/build-harness.spec.md`: lines :203, :245 and :275.
- `README.md`: "Live-store fence" at :471, the Unstick row at :437.
- `factory/subtickets.py`: `FIELD_RE` and `_is_heading` exist.
- `tests/factory/test_sibling_tests.py` does not exist yet.
