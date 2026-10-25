## Proposed change

One PR. The prototype's diff is about 75 lines of harness and documents, plus the test edits and new tests.

**A. `spec add` runs the format check** (`factory/cli.py`). In `spec_add`, read the text as today. If `specstore.is_active(root)`, and the source is not a `--from-run` run whose `meta.yaml` records `status: NEEDS-HUMAN`, call `_refuse_unless_applies(root, text, "spec not added")` before `_add_spec_version`. Import `_refuse_unless_applies` from `factory.human`, alongside the names `cli.py` already imports from there. Keep the function in `factory/human.py`, where `openspec/specs/harness-code/spec.md` pins it. `cli.py` must stay under 900 lines.

**B. The driver's route** (`factory/drive.py`, `intake`). Where `spec add` returns not ok:
- Let `why` be the first line of the stripped `stderr`. If it does not start `spec not added: `, park with `_harness_bug("spec add", added)` as today.
- Let `cur = max(rnd, 1)`. If `cur >= self.max_spec`, park with `"max rounds: " + <why with each backtick, $ and \ replaced by '>`, with outputs the writer's run id. Return `{"ticket", "state": "parked", "rounds": cur, "reason": "max rounds"}`.
- Otherwise call `ticket set <T> round.spec=<cur + 1>`. If that is not ok, park with `_harness_bug("round increment refused", st)`. Then set `rnd = cur + 1`, write one step line saying the spec went back to the writer in round `rnd`, with `why`, and `continue` the loop in state `ready-for-spec-writer`.

No other line in `drive.py` formats a `harness-bug: … stderr` reason. Current truth pins that count at 1.

**C. The intake script's route** (`factory/workflows/intake.js`). The same steps at the `spec add` call (line 188). `why` is the first line of the trimmed `added.stderr`. The round step is a clerk call of `${BIN} ticket set ${TICKET} round.spec=${cur + 1}`, labelled `round increment`. The park reason replaces `` ` ``, `$` and `\` with `'` (`/[`$\\]/g`) before `park()`. `log()` the same message the driver steps. The return values match B.

**D. The writer's next input** (`factory/compose.py`, the `spec_writer` branch). After the NEEDS-HUMAN case on `prev`, add a branch for a `prev` that ended `READY-FOR-CRITIC` or `NEEDS-SPLIT` when `specstore.is_active(root)`. Compute the refusal: `None` if any `spec.added` event in `store.log_lines(root)` has `source` equal to `prev`'s run id, or if its `output.md` is missing. Otherwise run `_refuse_unless_applies` on `status.strip_trailer(<output>)` with `"spec not added"`, and catch `store.Refused` for its text. When there is a refusal, `add()` the run's `output.md` under the heading `Your previous output, which the harness refused to store as a spec version`. Its body opens with `The harness refused it with: <refusal>`, then the output. That records the path in `input_sources`. `compose.py` may import `_refuse_unless_applies` from `factory.human`; nothing `human.py` imports reaches `compose.py`.

**E. Documents.**
- E1. `README.md`, "The intake workflow, step by step". Replace the paragraph's lines 2-7 (from `spec writer; REJECT closes` to `back to triage.`) with these six lines:
  ```
  spec writer; REJECT closes the ticket; CLARIFY waits for the requester; NEEDS-HUMAN parks. The
  harness saves the spec as a new version only if it is well-formed and fits current truth; if not, it
  goes back to the writer, using up a round. The critic's REVISE sends it back once; a second REVISE,
  or a refused spec in the last round, parks. NEEDS-SPLIT, a spec that names how to split an oversized
  request, goes to the critic like READY-FOR-CRITIC. APPROVE moves the ticket to the spec gate, where
  intake stops. The human approves or sends it back; a requester's answer returns a ticket to triage.
  ```
  In the flowchart below it, after the `W -- "READY-FOR-CRITIC or NEEDS-SPLIT" --> K…` line, add `  W -- "spec refused, a round left" --> W`.
- E2. `README.md`, "What each role reads and writes", Spec writer row. After the words "after a revision request, the critic's findings and its own previous spec;", add "after a spec that `spec add` refused, the refusal and that output;". The row stays one line.
- E3. `docs/design.md`, routing table. Before the `| Spec writer | NEEDS-HUMAN |` row, add `| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT, and `spec add` refuses the spec: malformed, or its changes do not apply to current truth | Spec writer (round +1) if round < {2}, else Human queue | The refusal and the refused output |`.
- E4. `docs/changelog.md`: one entry, the next free number, opening `<n>. After issue #105 (2026-10-12), where`. It says that `approve-spec` refused a spec the critic had approved, over three labels. It says that `spec add` now runs the same check. It says that a refused spec goes back to the spec writer as a new round, and parks with the refusal when no round is left. It names `spec add`, `approve-spec` and the round.

E1 adds one line net (the flowchart edge). E2 to E4 add none to README.

**F. Tests.** At least one new test file, for example `tests/factory/test_spec_add_refusal.py`, that fails on the base. Cover `spec add`'s refusal and its empty write, the NEEDS-HUMAN exemption, and the driver's route on a refused draft. Change the five tests below and no other existing test file.

## Tests to change

- `tests/factory/test_spec_store.py::test_item_88_gate_refuses_a_delta_that_does_not_apply_and_a_malformed_version`. It asserts that `spec add` stores a delta that does not apply (exit 0), then that `approve-spec --version 2` refuses it. It follows the first Decision: `spec add` now refuses that delta. Change: assert that `spec add` refuses with `spec not added` and `no-such-req`, then that `approve-spec --edit` of the same file refuses with `no-such-req`. Keep its later assertions: no approved v2, no `spec-v2.yaml`, v1's change folder intact.
- `tests/factory/test_spec_store.py::test_an_empty_op_heading_counts_as_a_heading_and_a_slash_label_is_no_label`. It stores two malformed versions with `spec add` and checks `approve-spec --version 2|3`. Same Decision. Change: check `approve-spec --edit <file>`, with the same refusal texts.
- `tests/factory/test_spec_store.py::test_acceptance_labels_allow_ordinary_punctuation_but_not_a_choice`. It stores each bad label through `spec add` and checks `approve-spec --version`. Same Decision. Change: check `approve-spec --edit <file>` for each bad label, with the same `no NEW/REGRESSION label` assertion.
- `tests/factory/test_spec_store.py::test_writer_and_critic_receive_current_truth_as_input_sources`. Its writer output, `=== proposal.md\n## Problem\nx\n`, is malformed, so `spec add` now stores no v1 and the critic's `input_sources` lose `specs/T-0001/v1.md`. Same Decision. Change: the writer's output becomes a well-formed spec whose change applies to the test's `status-parser` truth, for example the file's `FOUR_PART` with `ADDED` replaced by `MODIFIED`. The two `input_sources` assertions stay as they are.
- `tests/factory/test_shepherd.py::test_the_gate_refuses_a_delta_that_does_not_fit_current_truth`. It expects the second ticket's misfit delta to be stored, to reach the gate and to be refused by `approve-spec`. It follows the first and third Decisions: the delta is now refused at `spec add`, and the ticket stays with the spec writer. Change: dispatch the second ticket's spec writer with `route=False`, then assert that `spec add --from-run` refuses with `ADDED 'the-thing' is already in current truth`, and that the ticket stays `ready-for-spec-writer`. `tests/factory/_fixtures.py` does not change.

