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

STATUS: REVISE
CONFIDENCE: high, every Evidence figure reproduced by running the spec's own commands; the blocking finding rests on T-0044's design text and the two cited test lines, both read.
ESCALATIONS: none
