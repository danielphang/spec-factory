## Proposed change

**A. The test rule skips merged siblings' merges** (`factory/cli.py`, `_test_drift`). Before the first-parent walk, collect the `merge.main_after` of every sub-ticket of the parent (`store.subtickets_of(root, parent["id"])`) whose status is `merged` and whose `main_after` is set. In the walk, `continue` past any commit in that set before diffing it. Do not skip merge commits in general. Nothing else in the rule changes: a later commit that changes the same test file is still found, and the refusal still names the last such commit. Update the function's docstring and `_check_drift`'s docstring to say a merged sibling's merge is not drift.

**B. A ruling returns an implementer whose run failed to start** (`factory/cli.py`, `resolve`, the `--ruling` branch). Let `start_bug` be true when the park reason starts with `harness-bug: run start implementer:` and `parked["from"]` is `ready-for-implementer`. Accept the park when it starts with `ESCALATE` or `BLOCKED`, or when `start_bug` is true. Route `start_bug` exactly as `BLOCKED`: write F as the next `approvals/<id>/ruling-<n>.md` and `move("ready-for-implementer", "ruling", …)`, round unchanged. Change the refusal text to Decision 4's. The `use --answer` refusal for question parks stays as it is.

**C. Suite cases** in a new file, `tests/factory/test_drift_siblings.py`, built like `tests/factory/test_spec_drift.py`'s fixtures:
- A two-part plan where part A's recorded `--no-ff` merge adds a test file and changes a design-named file: part B's implementer run starts.
- The same, plus a later direct commit on the integration branch that changes a test beside a design-named file: refused, naming only that commit's test. A later direct commit that changes A's test file again: refused, naming the later commit.
- The same, plus a branch that is no sub-ticket's recorded merge, merged `--no-ff` into the integration branch, changing a design-named file and a test: refused, naming that test and the merge commit, and not A's test.
- A merged sub-ticket of an earlier, superseded plan whose merge adds a test beside a design-named file is not drift.
- `--ruling` on a `harness-bug: run start implementer:` park from `ready-for-implementer` returns the sub-ticket to `ready-for-implementer` with the ruling file written. `--ruling` stays refused, writing nothing, on `harness-bug: run start reviewer:` from `checks-in-flight` and on `harness-bug: run compose implementer:`.

**D. Documents.**
- `docs/design.md`, the **Spec drift** paragraph: add that a first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans, is not counted, because the plan expects its siblings' changes. Other merges still count.
- `docs/design.md`, the routing rules' resolution list (the bullet beginning "BLOCKED, a critic ESCALATE, and a planner ESCALATE"): add that a sub-ticket parked `harness-bug: run start implementer:` from `ready-for-implementer` returns to its implementer with the ruling, same round.
- `dev/build-harness.spec.md`: in the `factory resolve` CLI entry, add the same `--ruling` case. In the spec-store paragraph's drift sentence, add that a merged sibling's merge is not drift.
- `README.md`: in "Where a human decides", the **Unstick** row's `--ruling F` list gains "the harness failed to start an implementer run (a `harness-bug: run start implementer:` park)". In the **Spec amendment and drift** bullet under Built, add a sentence saying that a merge of another sub-ticket of the same spec is not drift. Replace that bullet's "It is tested, and has not yet fired on a real ticket", which is now false: the check has fired on real sub-tickets. Bump the status date.
- `docs/changelog.md`: one new entry, the last numbered, contiguous, "After issue #85 (2026-10-10), …", naming the two false parks, the `main_after` skip and the `harness-bug: run start implementer:` ruling route.
- No `docs/prompts/` or `factory/prompts/` file changes: no prompt block is edited.

## Tests to change

- `tests/factory/test_resolve_rulings.py::test_a_ruling_on_any_other_state_is_refused_and_names_both_park_kinds`: line 126 asserts the old refusal text, `--ruling applies to an ESCALATE or BLOCKED park; T-0001 is …`. Decision 4 changes that text, so the assertion changes to the new text. The cases it parametrizes (a `budget kill: reviewer` park and no park) stay refused, and the test's other assertions stay.

