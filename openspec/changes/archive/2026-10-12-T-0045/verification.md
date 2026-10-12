## Acceptance

- No test file imports from another test file → NEW. Today it prints `cross-test imports: 27` and 27 sites in 14 files.
- The shared constants and wrappers are defined once → NEW. Today it prints `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1`.
- The approved-parent and empty-repository setups are written once → NEW. Today it prints `approved-parent sequences: 13` and `empty-commit repo setups: 11`, with their sites, none in `_cli.py`.
- Only the duplicate test and its assertions are gone → NEW. Today no `Merge factory/T-0045.` commit exists and HEAD is `main`, so nothing is compared. It prints `pair: 0`, `removed: 0`, `added: 0`, `missing: 0` (run on `0ba4e4f`).
- The suite is shorter → NEW. Today it prints `pairs: 0; test lines before: 0, after: 0, change: 0` (run on `0ba4e4f`).
- A suite run in a fresh clone passes and adds nothing to the checkout → NEW. Today it prints `577 passed in 283.89s (0:04:43)`, then `paths changed: 13`: `factory/__pycache__` and 12 `.pyc` files in it.

## Responses

- [BLOCKING] 5, "Only the duplicate test and its assertions are gone": FIXED. Both comparison scenarios now compare across each of this ticket's own merges (each `Merge factory/T-0045.<n>` against its first parent) plus the branch's unmerged commits, and add up the results. T-0044's assertion edits, or any other ticket's, are never in a compared pair, whichever order the tickets merge in. I checked this in a throwaway clone with a simulated part-A merge followed by a simulated T-0044 merge and an unmerged branch commit (Evidence, "Comparing only this ticket's own changes"). The THEN held, and T-0044's change was not counted. I did not take the suggested two-outcome THEN. T-0046, T-0047 and T-0048 touch the same files and would each need a clause (Decisions, round 2). Risk's "the verifier must attribute them" is removed. The "suite is shorter" scenario uses the same pairs, for the same reason.
- [SHOULD-FIX] 6, Decisions first bullet: FIXED. It now reads "the 190-line fixture in `test_shepherd.py` that drives a ticket through a whole build". design.md's D sizing says "the fixtures from `test_shepherd.py`".
- [SHOULD-FIX] 6, Problem first paragraph: FIXED. The first sentence now says who pays and how: every implementer who edits a test, once to find every copy and again when an edit breaks another file.
- [NIT] 2, "The shared constants and wrappers are defined once": FIXED. The requirement sentence now says the check stays as a standing guard.

## Critic rounds

round 1 · spec v1 · run-0456-critic · REVISE

Checks run (all from `~/dev/spec-factory` at `0ba4e4f`, under the fresh-HOME wrapper):
- Ran the three non-suite acceptance commands as the spec gives them. Output matched the Evidence exactly: `cross-test imports: 27` (14 files, including `test_drift_siblings.py:19-21` and `test_spec_drift.py:24-26`); `REPO=30 BIN=29 run=10 js=11 ticket=6 git_repo=2 approved_parent=1`; `approved-parent sequences: 13` and `empty-commit repo setups: 11` at the sites the spec lists.
- Cited paths: `test_instance.py:21-33, 40-45, 48-49` (STRIP/CLEAN_CLI/cli, git_repo, tree), `test_p0_cli.py:20-22, 118-124`, `test_redispatch_rows.py:26-28`, `test_empty_output.py:22-33, 61`, `test_build_startup.py:15-27` (its `approved_parent`), `test_cost_once.py:19-21`, `test_subtickets.py:179-181, 204`, `tests/factory/conftest.py` (sets two env vars, imports no harness module), `clean_harness_cli.py` (defines no `REPO`/`BIN`). All exist and say what the spec says.
- Helper shapes: 8 of the 10 `run` copies take `(store, *argv)`, 2 take `(env, *argv)`; the 6 `ticket` copies all read `tickets/<tid>.yaml`; 6 `js` copies assert exit 0, 5 do not. Matches Decisions.
- Assertion-comparison risk: none of the 13 five-call sites has an `assert` on its five lines, and only two sit inside test functions (`test_subtickets.py:164, 198`, which call an asserting `js`). So replacing them drops no assertion from a test function, and the `assertions missing: 2` claim holds for this ticket's own edits.
- `core/b.py` is an empty directory, born 2026-10-07 07:58; `core/` holds nothing else. Merge commits are titled `Merge factory/T-00NN.N: ...`, so the `--grep='^Merge factory/T-0045'` base rule works. This run's ticket is T-0045.
- Not run: the suite and the two scenarios that collect or run it (the verifier's job).

Findings:

[BLOCKING] 5 Scenario "Only the duplicate test and its assertions are gone", THEN; Risk, "Sequencing"
Problem: The THEN requires exactly 2 missing assertions, both from `test_p0_cli.py`, but T-0044 (De-bloat A, state `planned`, approved and not archived) changes two assertions in `tests/factory/test_instance.py`, so if T-0044 merges after this ticket's first sub-ticket and before a later verifier run, the command prints `assertions missing: 4` and the scenario fails although the change is correct.
Evidence: T-0044 `design.md:35` and its decision "the unread setting is deleted": `test_instance.py:109` drops `and cfg["force_push_allowed"] is False` and `:354` drops `"force_push_allowed",` from a tuple; both lines are inside test functions (`test_init_writes_instance_yaml_from_the_template`, `test_conftest_points_the_suite_at_the_fixture_instance`). The scenario's comparison is a set difference of `ast.unparse(assert)` per test function, so a changed assertion counts as missing. The base is "the commit before this ticket's first merge", which excludes T-0044 only if T-0044 merges first. The spec's own Risk says "the verifier must attribute them", which contradicts the THEN as written.
Suggested fix: Make the THEN hold under both merge orders, for example: "`assertions missing: 2`, both starting `test_p0_cli.py::test_run_finish_without_output_is_killed:`; or, when `git log --first-parent --oneline $B..HEAD --grep='^Merge factory/T-0044'` is non-empty, `assertions missing: 4` where the two extra lines start `test_instance.py::test_init_writes_instance_yaml_from_the_template:` and `test_instance.py::test_conftest_points_the_suite_at_the_fixture_instance:`", and name T-0044 and its decision in the scenario's setup text.

[SHOULD-FIX] 6 Decisions, first bullet
Problem: "the 190-line shepherd fixture" is a term specific to this suite that nothing in the human-facing sections glosses.
Evidence: "shepherd" appears first in Evidence's `test_shepherd.py:625` citation and in Out of scope, never with a gloss; the operator new to the system cannot tell what a shepherd is. The rubric's letter makes an unglossed system term in a section's first paragraph BLOCKING; I am not blocking on it because the decision reads without it (the size carries the point, "put a 190-line fixture beside eight-line wrappers"), and the verdict is REVISE anyway.
Suggested fix: Write "the 190-line fixture in `test_shepherd.py` that drives a ticket through a whole build" or similar on first use.

[SHOULD-FIX] 6 Problem, first paragraph
Problem: The first paragraph says what is wrong (every test file carries its own copy of the same helpers) but not for whom; the "for whom" sentence, "Every later ticket that touches tests pays this cost", is in the second paragraph.
Evidence: Read as the gate operator. The rubric's letter makes this BLOCKING; I am not blocking on it because the reader gets the answer two sentences later and the fix is a move, not new text.
Suggested fix: Move "Every later ticket that touches tests pays this cost" (or "so every implementer who edits a test pays twice: ...") into the first paragraph, before the bullet list.

[NIT] 2 Scenario "The shared constants and wrappers are defined once"
Problem: The counter walks every `tests/factory/*.py` at module level, so a later ticket that adds a test file with its own `REPO` breaks it; that is the intended standing rule, but the spec says so only in Decisions ("Standing: a later ticket ... moves it to one of these two modules").
Evidence: Command run; `clean_harness_cli.py` and `conftest.py` define none of the seven names today, so the target `=1` each is reachable.
Suggested fix: None required; optionally say in the requirement text that the check is meant to stay as a standing guard.

No other findings. Rubric 1: the only behaviour change is one deleted test; no test pins it. Rubric 3: NEEDS-SPLIT is marked with ordered seams A-D and a suggested D split; the out-of-scope list is sensible and the Tests to change list gives a per-file reason by part letter. Rubric 4: Protected paths: none is right, every path is under `tests/factory/`. Rubric 5: T-0044 adds no test file (checked its design and spec deltas), so the `REPO=1`-style scenarios do not depend on it; only the assertion comparison above does.

round 2 · spec v2 · run-0458-critic · APPROVE

Round 2 review of T-0045 v2. Scope: whether the round-1 findings are resolved, and the text that changed (Problem first paragraph, Evidence "Comparing only this ticket's own changes", Decisions first and last bullets, Risk "Sequencing", design.md D.1 and the `test_instance.py` line of Tests to change, the two rewritten comparison scenarios, the requirement sentence "standing guard", verification.md's two "Today" lines).

Checks run (all from `~/dev/spec-factory` at `0ba4e4f` on `main`, under the fresh-HOME wrapper where a command ran):
- Ran the rewritten "The suite is shorter" command as the spec gives it. Output: `pairs: 0; test lines before: 0, after: 0, change: 0`, matching verification.md.
- Cited paths for the new comparison rule: `factory/gitops.py:43` (`branch_of` returns `factory/{tid}`), `factory/gitops.py:192` (`git merge --no-ff -m <message> <sha>` in a temporary worktree of the integration branch), `factory/cli.py:990` (message `Merge {t['branch']}: {t['title']} ({t['id']})`). All exist and say what Evidence says. A real merge on `main` reads `Merge factory/T-0043.3: Record ... (T-0043.3)`, so `--grep='^Merge factory/T-0045[.]'` matches the merges this ticket will make and nothing else.
- Whether `main` resolves where the verifier runs: every role checkout is a `git worktree add` of the same repository (`factory/gitops.py:49, 51, 56`), so `git merge-base HEAD main` and `git log ... HEAD` work there. The `.venv` symlink assumption is the one the existing harness-suite scenario already makes.
- Merge order with T-0044: its design (`.factory/store/openspec/changes/T-0044/design.md:13, 35-36`) edits only `test_instance.py:109` and `:354` and `fixtures/instance/instance.yaml:22` on the test side; this spec moves `test_instance.py:21-33, 40-45, 48-49`. No overlapping lines, and the comparison pairs (each `Merge factory/T-0045.<n>` against its first parent, plus merge-base..HEAD) never span another ticket's merge. The round-1 failure mode is gone under both orders.
- `tests/factory/_cli.py` is not collected: the repo has no pytest configuration (`pyproject.toml` has no `[tool.pytest]`, no `pytest.ini`/`setup.cfg`/`tox.ini`), so the default `test_*.py` / `*_test.py` applies. `tests/factory/conftest.py` sets `FACTORY_INSTANCE` and `FACTORY_REPO` only, so adding the two bytecode lines conflicts with nothing there.
- Not run: the suite, and the collect-only comparison command (it compares nothing on `0ba4e4f`; on the real branch it is the verifier's job). I could not check that `pytest --collect-only` succeeds inside a `git archive` of a commit; the writer's Evidence reports it did in a throwaway clone, and a collection failure would show as `removed` lines, so a problem there fails the scenario loudly rather than silently.

Prior findings:
- [BLOCKING] 5, "Only the duplicate test and its assertions are gone" / Risk Sequencing: RESOLVED. The two scenarios now compare only this ticket's own merge pairs and the branch's unmerged commits and sum them, so T-0044 (and T-0046/47/48) are never in a compared pair. Rejecting my two-outcome THEN is right for the reason given: three more tickets touch the same files. Risk no longer asks the verifier to attribute anything.
- [SHOULD-FIX] 6, Decisions first bullet: RESOLVED. "the 190-line fixture in `test_shepherd.py` that drives a ticket through a whole build" glosses it; design.md's D sizing matches.
- [SHOULD-FIX] 6, Problem first paragraph: RESOLVED. First sentence now says who pays (every implementer who edits a test) and how (twice).
- [NIT] 2, "defined once" requirement: RESOLVED. The requirement sentence states the standing guard.

New findings on changed text: none that I would defend as blocking or should-fix. One note, not a finding: the comparison scenario's THEN requires `removed: 1` exactly, which holds for every sub-ticket's verifier run because the parts run in order and each branch is cut from `main` after the earlier part merged, so part A's merge is reachable from every later HEAD; if the planner ever reordered the parts so a branch did not contain part A, `removed: 0` would appear on that sub-ticket and the verifier would read it as a failure. The spec already says the parts run in order A, B, C, D and none is parallel-safe, so the planner has what it needs.

No other findings. Rubric 1: still one behaviour change (one deleted test), no test pins it. Rubric 3: NEEDS-SPLIT with ordered seams; Tests to change gives a per-file reason by part letter and now names the T-0044 lines it leaves alone. Rubric 4: Protected paths: none remains right. Rubric 5: checked above. Rubric 6: the human-facing sections read without a translator; "harness", "spec gate", "sub-ticket merge" and the fixture are glossed on first use.

## Verifier results

3478d1fddf4b207fdf0a04ba34ae5459ec11968c · T-0045.1 · VERIFIED · run-0461-verifier
a7368d0ff39c534d52cd4d4eecb9d3e463ee95d4 · T-0045.2 · VERIFIED · run-0469-verifier
c8308f2ba30e01db463ee09dff27b778e8819b39 · T-0045.3 · VERIFIED · run-0471-verifier
