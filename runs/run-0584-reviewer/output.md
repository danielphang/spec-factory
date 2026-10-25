Commit: fa0d3b5e26a0c591316cfa2d56b46156f742d293 (branch `factory/T-0056.2`, base `b863e4ec2b2c147e6133e73fc9ba5d50f2b6f494`)

## Review

Checked in the role's order, by reading the diff and confirming each helper it leans on in the worktree.

1. **Test integrity.** `git diff --stat b863e4e...fa0d3b5` touches six files: `README.md`, `factory/cli.py`, `factory/human.py`, `factory/instance.template.yaml`, `factory/stats.py` and the new `tests/factory/test_scorecard.py`. No existing test file changes. "Tests to change: none" holds.

2. **Correctness.** The scorecard follows design part C as written. I traced each definition against the code:
   - Windows (C2): `since` comes from `parse_when`, which returns an aware UTC datetime (`factory/stats.py:49`, `factory/cost.py:113`), so `since - (end - since)` and `_bound`'s `astimezone` are safe. `_bound` prints `YYYY-MM-DD` only at midnight UTC.
   - Changes: the last `ticket.transition` to `closed` wins because `_load` sorts events by `_ts` (`factory/stats.py:82`) and `closed[tid]` is overwritten in order; a parent with no `merge.done` for itself or `<parent>.N` is dropped via `merges[t]`.
   - Escapes, decisions, interventions, the 2-second rule, runs by status, wall, lead, the three cells' formats: each matches C3 line for line (`factory/stats.py:288-337`).
   - `_instance` walks `Path.parents` nearest first, matches `state_dir` resolved against the directory, refuses a non-boolean `target_is_factory` only on the instance that owns the store, and runs for every store before any output is built (`factory/stats.py:343`), so a refusal prints no partial table.
   - `escape_add`: the five refusals come before `log_event`; the digest is SHA-256 of the UTF-8 `--issue` text; the event holds `ticket`, `issue_sha256`, `by` and an optional `note`; the printed JSON holds the hash and never the text. `intervention_add`: one event, `ticket`/`note` only when given, `id` in the output only with a ticket.
   - Fence: both new commands are `(cmd, "add")` pairs absent from `READ_ONLY` (`factory/cli.py:863`), so `main` fences them unmarked (`factory/cli.py:881`). The test `test_the_fence_refuses_both_records_unmarked_while_a_run_is_in_flight` exercises that with the existing helpers.
   - The new test file reproduces the acceptance fixture's figures and asserts all 25 expected lines, both transcript lines, both refusals, the no-instance and wrong-`state_dir` cases, an off-midnight bound, and that the store tree is byte-identical after a run.

3. **Scope.** Everything in the diff is in parts B1, B2, C1 to C4, D, E2, E4, E5 and E6. `report()` and sections A to D are untouched; `stats_cmd` only chooses between `stats.report` and `stats.scorecard`. `human.py` adds exactly the two names the harness-code scenario lists.

4. **Silent behaviour changes.** None found. Without `--scorecard`, `stats_cmd` calls `report()` with the same arguments as before.

5. **Security and data safety.** The `--issue` text reaches neither the log, stdout nor stderr; the test asserts the link text is in no file under the store. Both commands write one appended log line and nothing else.

6. **Protected paths.** `factory/cli.py`, `factory/human.py`, `factory/stats.py`, `factory/instance.template.yaml`: all under `factory/**`, declared by the sub-ticket and by the parent spec's Risk section. Listed under ESCALATIONS for the record.

7. **Coding standard.** Every new helper sits on a named rung: `_instance`, `_bound`, `_hours`, `_run_tokens`, `_measures` reuse `_load`, `_parent`, `_table`, `read_yaml`, `match_transcripts`, `transcript_usage` and `instance.DIRNAME`/`CONFIG_NAME`; the hash and median come from `hashlib` and `statistics`. No duplicate of an existing helper. The 2-second scan is O(transitions × decisions) and the PR description discloses it; it is not a `factory:` marker case at today's log sizes. Lean already.

8. **PR description.** What changed leads with what the operator can now do, glosses the north star, escapes, interventions and the fence, and names callers of the one edited function. Known gaps are specific and honest. Readable by the operator at the gate.

## Findings

- [NIT] factory/human.py:344: the sub-ticket check runs before `load_ticket`, where design B1 loads the ticket first → a sub-ticket id with no ticket file gets the "record on its parent" message instead of `no ticket …`. Both exit 2 and write nothing; the acceptance scenario checks only the exit code. Disclosed in Known gaps; no change needed.
- [NIT] factory/stats.py:329: `all()` over an empty list is true, so a change with no finished runs counts as "every run has tokens" with 0 tokens and pulls the median down → a store where a change's run records were lost would print a low median labelled as complete. The design's literal wording allows it and no real change merges without an implementer run. Disclosed in Known gaps.
- [NIT] factory/cli.py:888: a `--scorecard` refusal prints `{"ok": false, "error": …}` on stdout through the CLI's common path, where design C1 says nothing on stdout → a review that pipes stdout on a refused run gets one JSON line. This is how every other `factory` refusal already behaves and the acceptance scenario passes; disclosed in Known gaps. The operator can rule either way at the gate.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. Every definition in design C3 and B1/B2 maps to a line I read, the helpers the code calls exist with the shapes it assumes, no existing test changed, and the new tests pin the acceptance figures.
ESCALATIONS:
- Protected paths touched, all declared by the sub-ticket and the parent spec's Risk section (`factory/**`): `factory/cli.py`, `factory/human.py`, `factory/stats.py`, `factory/instance.template.yaml`. For the record; the merge gate needs no further approval.
- The implementer reports the harness suite passing but over its three-minute bound on both base and branch, under a load average of 44 to 50. The verifier times it on this head; if it is still over on an idle machine, that is an environment question for the operator, not a defect in this change.
