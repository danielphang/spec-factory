# Review of T-0057.1, round 1

Commit: 3fdcda3e76e891e79e7949c78b78cef051f1dfd2 (branch `factory/T-0057.1`, base `11080b100b31c70c69cc1867960819270d134a23`)

## Verdict

APPROVE. The change does what spec v2 asks, in every lettered part, and I found nothing that blocks a merge. Two NITs below; neither needs a new commit.

## What I checked, and how

I read the whole diff and confirmed each name it relies on in the worktree. I ran one narrow command, an import of the four changed Python modules, to settle the one question the diff raised that reading could not: whether `compose.py` importing `human.py` closes an import cycle. It does not. Details follow in the order the role prescribes.

1. **Test integrity.** Two existing test files change, `tests/factory/test_spec_store.py` and `tests/factory/test_shepherd.py`. Both are listed under the spec's "Tests to change", and each edit is the one the spec prescribes:
   - `test_item_88_gate_refuses_a_delta_that_does_not_apply_and_a_malformed_version` now asserts `spec add` refuses with `spec not added` and `no-such-req`, then `approve-spec --edit` refuses with `no-such-req`. Its later assertions stay (`test_spec_store.py:170-176`).
   - `test_an_empty_op_heading_counts_as_a_heading_and_a_slash_label_is_no_label` and `test_acceptance_labels_allow_ordinary_punctuation_but_not_a_choice` switch to `approve-spec --edit <file>` with the same refusal texts (`test_spec_store.py:339-343`, `363-366`).
   - `test_writer_and_critic_receive_current_truth_as_input_sources` now feeds a well-formed MODIFIED spec; both `input_sources` assertions are unchanged (`test_spec_store.py:49`).
   - `test_the_gate_refuses_a_delta_that_does_not_fit_current_truth` dispatches the writer with `route=False`, which the fixture already supports (`_fixtures.py:534`), asserts the `spec add --from-run` refusal, and that the ticket stays `ready-for-spec-writer` (`test_shepherd.py:163-167`). `_fixtures.py` is unchanged.
   No assertion is weakened, skipped or hard-coded. The two T-0056 test files named in the human ruling are untouched.

2. **Correctness.**
   - A, `factory/cli.py:409-413`: the check runs only when `specstore.is_active(root)` and the source is not a `--from-run` run whose `meta.yaml` says NEEDS-HUMAN. `_text_from` runs first and goes through `_run_dir`, which refuses a run with no `meta.yaml` (`cli.py:164-168`), so the later `read_yaml` of that file cannot miss. The walrus inside the `out({...})` literal binds `n` before the `path` value is built, since dict entries evaluate left to right. `cli.py` is 899 lines, under the 900 that current truth pins.
   - B, `factory/drive.py:301-320`: `why` is the first stderr line, the prefix guard falls through to the old `_harness_bug("spec add", …)` park, `cur = max(rnd, 1)`, the last-round park sanitises backtick, `$` and `\` with `re.sub` (`re` is already imported, `drive.py:34`), the round increment goes through `ticket set`, and `continue` returns to the top of the `while True` loop with `state` still `ready-for-spec-writer` (`drive.py:291-293`), so the writer runs again. The later `spec:init` transition leaves a round of 2 alone, because `_apply_round` only sets 1 when the round is 0 (`store.py:196-198`); that is why the first scenario ends at `spec=2`.
   - C, `factory/workflows/intake.js:190-207`: the same steps. `MAX` and `round` exist (`intake.js:53`, `159`, `164`). `park()` wraps the reason in double quotes and turns `"` into `'` (`intake.js:78-82`), so after the `[`$\\]` replacement nothing in the reason is special to `sh` inside those quotes. Every `run finish` still passes `--transcripts` (`intake.js:128`, `drive.py:235`, `242`, `600`), as the ruling requires.
   - D, `factory/compose.py:65-77` and `310-314`: `_refusal` returns None when a `spec.added` event names the run as `source`, which is the field `_add_spec_version` logs (`common.py:38`), or when `output.md` is missing. Otherwise it runs the same check on the trailer-stripped output. The section is added through the existing `add()` with its `edit` callback (`compose.py:213`), so the path lands in `input_sources`. The `elif` sits after the NEEDS-HUMAN branch, so a NEEDS-HUMAN draft keeps its old heading. A stored draft that the critic sent back yields no section, because its run is a `spec.added` source.
   - E: the README paragraph matches the spec's six lines word for word, the flowchart edge is `W -- "spec refused, a round left" --> W`, the Spec writer row is still one line, the design-doc row matches the spec's text and sits before the NEEDS-HUMAN row, and changelog entry 78 follows 77 and opens `78. After issue #105 (2026-10-12), where`. `git diff --numstat` for README prints `8 7`: one line net.
   - F: one new file, `tests/factory/test_spec_add_refusal.py`, covers the refusal and its empty write, the NEEDS-HUMAN exemption and the bare store, both runners' route back to the writer with the input section and source, both runners' last-round park with the quoted reason, and the REVISE-then-refusal park.

3. **Scope.** Every change falls under parts A to F. The one edit outside the spec's text is the two-line merge in `_text_from` (`cli.py:398-400`), which changes no behaviour and which the PR description declares with its reason.

4. **Silent behaviour changes.** `spec add --file` by an operator now refuses a malformed spec on a store with current truth. The spec's first and second Decisions ask for exactly that, and the README paragraph now says it. Nothing else a caller would notice.

5. **Security and data safety.** The only text from an agent's output that reaches a shell is the park reason, and it is sanitised as the spec requires, in both runners. A refusal writes nothing to the store, as the spec's Decisions require. No secrets, no destructive operations.

6. **Protected paths.** `factory/cli.py`, `factory/compose.py`, `factory/drive.py` and `factory/workflows/intake.js`. The parent spec's Risk section declares all four. Listed under ESCALATIONS for the record.

7. **Coding standard.** Rule 1: `_refusal` is the one new helper, and nothing in the repo derives a refusal from the store, so it sits on rung 6. The new test file's stand-in `claude` and node runner are new copies rather than the fixture's, because the fixture's stand-in writes only a trailer (`_fixtures.py:238-240`) and the spec forbids changing `_fixtures.py`; see the out-of-scope note. Rule 2: the PR description names both callers of `_text_from` and all four callers of `_refuse_unless_applies`. Rule 3: no shortcut that needs a marker, and the description says "markers added: none". Rule 5: "refusal", "round" and "spec add" are the spec's own names. Rule 6: no path outside the repository is patched or added. Lean already.

8. **PR description.** "What changed" glosses the spec writer, the critic, the spec gate, current truth and a round before using them, and says in words what each part does. "Known gaps" is candid about the dense `spec_add` lines, the node stand-in for the clerk, the derived refusal section and the one untested fall-through. The operator at the gate can read it as is.

## Findings

- [NIT] `factory/cli.py:413`: the result dict binds `n` with a walrus inside a 150-character `out({...})` call → a reader has to know that dict entries evaluate left to right to see that `path` is built after `n` exists. Correct as written, and not actionable here: the file has no headroom under its 900-line cap, and splitting it is a design decision. Noted so the next change to `cli.py` knows the cost.
- [NIT] `factory/drive.py:304-306` and `factory/workflows/intake.js:192`: the fall-through to the `harness-bug: spec add:` park, for a refusal that does not start `spec not added: `, has no test → a later edit could drop the guard without a failure. The spec's part F does not ask for one, and the PR description says why the attempt was removed, so this is a note, not a request.

Prior findings: none (round 1).

## Out-of-scope observations

- The fixture's stand-in `claude` (`tests/factory/_fixtures.py:222-247`) takes a `write` play but cannot write a body, so `test_spec_add_refusal.py` carries its own stand-in and its own node runner for `intake.js`. A later ticket could give the fixture's stand-in a `body` play and fold the test's copy into it. This change could not, because the spec forbids changing `_fixtures.py`.
- `cli.py` is at 899 of 900 lines. The next change that adds one line to it must split the spec commands out first.
- The Shepherd fixture's `route()` (`_fixtures.py:576`) still asserts that `spec add` succeeds for every writer status, as the implementer notes. No current story trips it.

STATUS: APPROVE
CONFIDENCE: high. Every part of the spec's Proposed change is present and I confirmed each name, variable and loop the diff relies on in the worktree; the one question reading could not settle, an import cycle through `human.py`, I ran and it is clear. The verifier runs the suite and the gate commands on this head.
ESCALATIONS: protected paths touched, all declared in the parent spec's Risk section: `factory/cli.py`, `factory/compose.py`, `factory/drive.py`, `factory/workflows/intake.js`.
