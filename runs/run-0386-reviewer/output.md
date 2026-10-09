Commit: 49cc429424c1eb02708268bf4ecb0f251bfe8ae7 (branch `factory/T-0027.3`, base 8dfc64b61f9d927e9f82fa9704f382cffefa60cf)

Files in the diff (`git diff --name-only base..head`): `factory/cli.py`, `factory/subtickets.py`, `tests/factory/test_spec_drift.py` (new). No existing test file changed.

## Checks, in the required order

1. **Test integrity.** No existing test file is touched; the only test change is the new file `tests/factory/test_spec_drift.py`. It reuses `test_spec_amend`'s fixture by module attribute (`f = test_spec_amend.f`, line 28) and `test_sibling_tests.BUILD_DRIVER` without editing either. No assertion weakened, no skip, no hard-coded expected value: the test rule's expected commits come from `land()`'s returned sha, not from captured output. Clean.

2. **Correctness against part D.**
   - D.1 (`factory/cli.py:487-507`): `_add_spec_version` gains `cfg` and writes `specs/<id>/v<n>.yaml` with `integration_head` via `_integration_head`, which catches `Refused` (git failure, no branch) and `OSError` (repo path missing). All three callers pass `cfg` (`spec_add` :513, `spec_amend` :570, `approve_spec --edit` :1055); I grepped `_add_spec_version(` and found no fourth caller.
   - D.2 (`factory/subtickets.py:42-53`): `field_text` is the old `sibling_tests` loop with the field name as a parameter; `sibling_tests` now iterates its lines. The two are line-for-line equivalent, so `_check_sibling_tests` (its only caller) is unchanged in behaviour.
   - D.3 (`factory/cli.py:214`, `:275-358`): `_check_drift` runs for the implementer on a sub-ticket, before `_check_sibling_tests`, before `store.next_run_id` (line 220), so a refusal writes nothing. The skip uses `compose._runs_for(root, tid, "implementer", "")`, which returns only runs with `finished` set (`compose.py:24`), and the glob `approvals/<id>/ruling-*`, the name `resolve --ruling` writes (`cli.py:1139,1147,1160,1189`). Sibling rule: current plan via `split_plan(...)[0]`, transitive closure over `depends_on`, whole-token regex `(?<![\w.-])tok(?![\w-]|\.\d)` matching the design's wording exactly; labels are always `ST-n` or `T-nnnn.x` (`subtickets.py:25`), so no short-label false positives. Test rule: base from the parent's approved-version yaml, skipped when missing, null or not a commit (`rev-parse --verify --quiet base^{commit}` with `check=False`); named files are backticked design tokens present in `ls-tree -r tip`, minus test files and `.md`; listed files from the design's `## Tests to change` section and the sub-ticket's field, cut at `::`; first-parent `rev-list --reverse base..tip`, `diff --name-only --no-renames c^1 c`, keep the last commit per file. Message text matches the design's two finding forms and the `BLOCKED from harness: spec drift: ... Amend the spec (...) or rule (...)` shape. A root commit in the range gives an empty diff through `check=False` rather than an exception.
   - D.4: no change to `factory/workflows/build.js`; the new test `test_the_build_parks_a_drifted_subticket_and_a_ruling_lets_it_start` drives it and asserts the `park T-0001.1: BLOCKED from harness: spec drift: ` line.
   - Edge cases the spec implies: no record (version stored before this change) → sibling rule only, tested; a listed test with `::name` → cut, tested; a sibling named outside Acceptance → ignored, tested; amendment after the change → new record at the new head, tested.

3. **Scope.** Everything in the diff is part D. The `sibling_tests` refactor onto `field_text` is the design's own instruction ("found the same way `sibling_tests` finds") applied once instead of copied, and it keeps behaviour. No `gitops.py` change, no workflow change, no document change.

4. **Silent behaviour changes.** Two, both the spec asks for: every `spec add`/gate edit/amend writes one extra yaml file, and a sub-ticket's first implementer start can now be refused with a `BLOCKED` error. The implementer's Known gaps also notes that the suite's `conftest.py` points `FACTORY_REPO` at the harness checkout, so existing tests now record its head; with base == tip the range is empty and nothing is found. I agree it is harmless.

5. **Security and data safety.** Git is called through `subprocess` with argument lists, no shell. Values from the store (`integration_head`) reach git only as a revision argument. No deletion, no writes outside the store.

6. **Protected paths.** `factory/cli.py` and `factory/subtickets.py`, both declared by the sub-ticket and by the parent's Risk section. `factory/gitops.py` not touched. Listed under ESCALATIONS for the record.

7. **Coding standard.** Rule 1: the one new regex pair (`TEST_FILE_RE`, `TICK_RE`) and four helpers each do work no existing helper does; `_tests_to_change_section` reuses `specstore.lines_outside_fences` and `specstore._heading`. Rule 2: callers of the two changed functions are named in the PR description and I confirmed them by grep. Rule 3: one `factory:` marker (`cli.py:338`), listed in Known gaps. Rule 5: names match the spec's terms (drift, ruling, integration head). Rule 6: tests reach paths through `f.env`, no module-level import of a patched path. `uv run --frozen ruff check` on the three files: `All checks passed!`. Lean already.

8. **PR description.** What changed opens with the problem, glosses sub-ticket, scenario, implementer and ruling at first use, and gives a real refusal line. Known gaps names the marker, the `path:line` token limit, the closed-sibling case and the shared fixture. An operator at the gate could read it. No finding.

## Findings

- [NIT] factory/cli.py:329-330: `_test_drift` runs `git ls-tree -r --name-only tip` over the whole target repo before it knows whether `base..tip` has any commits → on the common case (nothing merged since the spec was written) every first implementer start pays one full tree listing for nothing. Reorder so the `rev-list` runs first and the function returns when it is empty. Not blocking: correctness is unaffected.

Prior findings: none (round 1).

## Out-of-scope observations

- My `ruff check` created an ignored `.ruff_cache/` in the review worktree beside the implementer's ignored `.venv/`. Neither is tracked.
- The `path:line` token limit in Known gaps (a design part that cites only `factory/cli.py:843` names no file for the test rule) is faithful to the design's "backticked tokens that exist as files". Worth a design note later; this repo's own specs use bare paths in design parts and `path:line` in Root cause, so the parent's design part is covered.

STATUS: APPROVE
CONFIDENCE: high. I read every changed line against part D and confirmed each helper signature it relies on (`_runs_for`, `gitops.git` with `check=False`, `read_yaml`, `lines_outside_fences`, `_heading`, label pattern, ruling file names) in the worktree; the only finding is a cost nit.
ESCALATIONS: none. Protected paths touched, all declared by the sub-ticket: `factory/cli.py`, `factory/subtickets.py`.
