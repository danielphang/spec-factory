Commit: 2f3fcef2f7a433585b85e99aedf9302133c01002 (branch `factory/T-0037.1`, base `51e2af7f1737f5fc4d9780ea725710dc1112702f`)

## What I checked

1. Test integrity. The only test file changed is `tests/factory/test_capability_index.py`. Every hunk is on the spec's Tests to change list: the module docstring (`:1-9`), the `CITES` constant and the writer-note text (`:22`, `:122-126`), the helpers `decision_block` and `decision_index` (`:194-203`) and the four decision-filter tests (`:206-238`). `test_a_whitespace_only_log_still_adds_nothing` and the part-B4 test are untouched. The replacement test asserts the exact whole-log block, `WHOLE_LOG + "\n".join(DECISIONS) + "\n"`, for all three roles under both `Capabilities: beta` and `Capabilities: none`, plus no `Decision index`, no `<ticket id>` grep instruction, and `decisions.md` in `input_sources`. That is stronger than the spec's part B asks, not weaker. No assertion was loosened, no skip, no swallowed error.
2. Correctness against the spec's Proposed change.
   - A1: `add_decisions()` (`factory/compose.py:226-232` on the head) takes no argument, adds nothing when the file is missing or whitespace-only, and otherwise calls `add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")`. The filter, the trimmed-log block and the decision-index section with `title()` are gone. `re` and `store` are still imported and still used elsewhere (`_ENV_NAME` at `:145`; `store.read_yaml` etc.), so no dead import.
   - A2: `git grep -n add_decisions factory/compose.py` on the head gives the definition at `:226` and three calls at `:250`, `:269`, `:292`, all `add_decisions()`. Writer and critic calls still follow `add_truth(sel)`; the planner no longer calls `selected()`. `selected()` is still used by the writer and critic (`:248`, `:267`).
   - A3: `CAPABILITY_INDEX_NOTE` (`:138-142`) matches the spec's text word for word; I diffed it by eye against design.md A3.
   - C1: the `docs/design.md:94` replacement matches the spec's two sentences word for word. C2: the three README rows say "the whole decision log"; Status date bumped. C3: changelog entry 61 starts `61. After issue #78 (2026-10-09), where`, gives the failure, the change, the rounded sizes and the rejected alternative. `grep -n -i 'decision index' docs/design.md README.md docs/prompts/*.md dev/build-harness.spec.md` finds nothing; `dev/build-harness.spec.md:193` already says `run compose` gives `decisions.md` whole to the writer, critic and planner, so it is consistent without an edit, as the spec's Out of scope says.
   - Confirmed by a narrow run from the worktree with a throwaway HOME: `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_capability_index.py::test_each_role_gets_the_whole_decision_log_and_no_decision_index tests/factory/test_capability_index.py::test_writer_gets_the_named_capability_in_full_and_an_index_line_for_each_other` printed `3 passed in 4.71s`: both parameter cases of the new test and the edited writer-note test pass on the head.
3. Scope: five files, all named in the spec's Proposed change or Risk section. Nothing else.
4. Silent behavior changes: the planner no longer reads the approved spec through `selected()`; that function only reads and returns a set, so dropping the call has no side effect. Triage, implementer, reviewer and verifier branches are untouched.
5. Security and data safety: nothing new is read or written; the change removes a `read_yaml` of ticket files.
6. Protected paths: `factory/compose.py` (harness), declared in the spec's Risk section and in the PR description. Listed under ESCALATIONS below; the merge gate will want a human approval.
7. Coding standard: one `delete:` observation, below. The implementer's PR description names the callers of the changed function with the grep that found them (rule 2) and states `factory: markers added: none` (rule 3).
8. PR description: What changed leads with the problem, glosses spec writer, critic, planner, decision log and capability at first use, and says in words what changed per part. Known gaps are honest (unused `others` parameter, the UTC date, operator steps not done). Readable at the gate as written.

## Findings

- [NIT] delete: `tests/factory/test_capability_index.py:71-96`: the `others` parameter of `setup` and `build` has no caller once `test_a_decision_index_line_carries_the_ticket_s_title` is removed → a reader of the fixture looks for a use that does not exist. The coding standard's table gives `delete:` SHOULD-FIX; I lower it to NIT because the fix touches helper lines the spec's Tests to change list does not name, so this ticket may not make it, and the PR description already records it under Known gaps. Fold it into the next ticket that edits these helpers.

net: -3 lines possible (the `others` parameter and its two uses), outside this ticket's allowed test edits.

Prior findings: n/a (round 1)

STATUS: APPROVE
CONFIDENCE: high, every lettered part is in the diff as the spec words it, every test-file hunk is on the Tests to change list, and the new test and the edited writer-note test pass on the head in a narrow run.
ESCALATIONS: protected path `factory/compose.py` (harness, `factory/**`) is changed; the spec's Risk section declares it, so this is for the merge gate's human approval, not a stop.
