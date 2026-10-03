Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

Reviewed in `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0009-reviewer/wt` (branch `factory/T-0001.1`, one commit over base `f8f40e0c5`). `git diff --stat f8f40e0c5...HEAD`: `factory/cli.py` (+14/-3), `tests/factory/test_results_commit.py` (new, 131 lines), `tests/factory/test_shepherd.py` (+1/-1). No other file touched; `git status` clean before and after my runs.

## Checks, in order

1. **Test integrity.** The only existing test file changed is `tests/factory/test_shepherd.py`, and the only changed line is 268: `--output str(red)` → `--output str(f.store / "runs" / ver.run_id / "output.md")`. That line is the one listed under the parent's "Tests to change". No assertion was touched (lines 269-271 unchanged). The substitute file is written by `f.dispatch` at `test_shepherd.py:648-649` with `Commit: HEAD` replaced by the ticket head, so the story still records a red verifier output (`Gate suite: FAIL`, `STATUS: FAILED`) and still asserts `{"reviewer": "APPROVE", "verifier": "FAILED", "ci": "FAIL"}` and the refused merge. Lines 327, 408-409, 489 and the stubs under `tests/factory/fixtures/stubs/` are unchanged (verified with `grep -n "Commit: HEAD"`). No skip/xfail, no weakened assertion. PASS.

2. **Correctness.** `factory/cli.py:431-443` at head. Without `--killed`: `re.findall(r"^Commit:.*$", text, re.M)` collects every line starting with `Commit:`; none → `Refused("...no Commit: line")`; each line is matched with `re.match(r"Commit:\s*`?([0-9a-fA-F]{7,40})`?\b", line)` → non-match refuses with `... is not a commit id`, mismatch refuses with today's message. With `--killed` (`:431-434`): the old first-match search, byte for byte. All refusals sit before `store.record_result` (`:445`) and `store.log_event` (`:451`); the only calls before the check are `store.load_ticket`, `Path.read_text` and `status.parse`, none of which writes (grepped `factory/status.py` and `load_ticket` for `write`/`log_event`: none). I ran all nine parent WHEN commands verbatim under bash from the worktree root; each printed its THEN line:
   - no-commit-line-is-refused → `exit=2 rows=[] events=0`
   - non-hex-commit-value-is-refused → `exit=2 rows=[] events=0`
   - later-commit-line-naming-another-commit-is-refused → `exit=2 rows=[] events=0`
   - verifier-without-commit-line-writes-no-ci-row → `exit=2 rows=[] events=0`
   - earlier-commit-line-naming-another-commit-is-refused → `exit=2 rows=[] events=0`
   - full-head-sha-is-recorded → `exit=0 rows=[reviewer.yaml ] events=1`
   - abbreviated-sha-in-backticks-is-recorded → `exit=0 rows=[ci.yaml verifier.yaml ] events=2`
   - killed-without-output-records-killed → `exit=0 rows=[verifier.yaml ] status=KILLED`
   - killed-with-cut-off-output-records-killed → `exit=0 rows=[verifier.yaml ] status=KILLED`
   Edge probes beyond the spec (same harness, head = forty zeros): `Commit: 0000000ABC` → refused as not a prefix (correct: the head is all zeros); 41 hex chars → refused `is not a commit id` (correct, `{7,40}` plus `\b` cannot match); `Commit: 0000000 (reviewed)` → accepted (trailing text stays allowed, as the spec decides); CRLF output → accepted (`\b` matches before `\r`); `**Commit:** 0000000` → refused `no Commit: line` (the spec's Risk accepts this); `  Commit: deadbeef00` indented plus a valid line → accepted, because an indented line is not "a line that starts with `Commit:`" (same anchor as today); `--killed` with `Commit: deadbeef00` → still refused on mismatch (today's behaviour kept). `tests/factory`: `64 passed in 99.52s`, exit 0 (55 + 9 new). PASS.

3. **Scope.** Three files, each inside parts A, B, C. Nothing in `factory/workflows/**`, roles, prompts, `--head` validation, stale rule or status parsing. PASS.

4. **Silent behaviour changes.** One, which the PR description discloses: a bare `Commit:` with the hex on the next line was accepted by the old `^Commit:\s*` (since `\s*` crosses newlines) and is now refused (`results record: Commit:  is not a commit id`, reproduced). The spec defines a `Commit:` line as one whose own value parses, so this is the spec's intent rather than collateral. The `--killed` path keeps the old cross-line match. No other caller-visible change: accepted outputs still produce the same rows, `ci` row and events (scenarios 6 and 7 above).

5. **Security and data safety.** No new inputs, no shell, no destructive operations. The change only adds refusals before any write. PASS.

6. **Protected paths.** None in the diff. The implementer reports that running the full-suite gate rewrote `webui/package-lock.json` in its working tree and that it restored the file; the commit does not contain it (`git diff --stat` above) and this worktree is clean. Noted under ESCALATIONS as an observation for the harness owner, not a protected-path change in this PR.

7. **Maintainability.** Nothing that will cause problems. The `--killed` branch repeats the grammar regex once; acceptable given the spec's "keep today's check exactly".

**Test file (part C).** `tests/factory/test_results_commit.py` drives `bin/factory` as a subprocess against a temporary `FACTORY_STATE`, mirroring `test_shepherd.py:579`. It derives the ticket id from `ticket new` stdout instead of assuming `T-0001`; refusal tests assert exit 2, the stderr reason, no files under `results/<head>/` and no `result.*` events; accept tests assert the exact row set, the exact event list and the row statuses; killed tests assert the single KILLED row. One test per parent scenario (9), matching the PR description. `ruff check` on `nanobot/` and on the two changed Python files: `All checks passed!`.

**Not run by me:** the full-suite gate (`scripts/full_suite_gate.py`). That is the verifier's check; the implementer's report that it passes only once `neonize` and `mcp==1.29.1` are installed into the worktree `.venv` is environmental and predates this change (reproduced by the implementer at base). I did not re-verify the "A without B breaks the merge-gate story" claim by experiment; it follows from `test_shepherd.py:264` writing `Commit: HEAD` into the file that line 268 recorded, which `factory/cli.py:439-440` now refuses.

## Findings

- [NIT] `factory/cli.py:440`: when a `Commit:` line has an empty value (bare `Commit:` or `Commit:` with the id on the next line) the message is `results record: Commit:  is not a commit id` (double space, nothing named) → the parked ticket's `harness-bug` reason tells the human only that some value failed, not that the line was empty. Correct refusal; message quality only.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. I read the whole diff at `e28db6a25`, re-ran all nine parent WHEN commands verbatim and eight edge probes from the worktree root, ran `tests/factory` (64 passed) and lint (clean), and confirmed the only existing-test edit is the declared line 268.
ESCALATIONS: none blocking. For the harness owner (from the PR description, outside this diff): the full-suite gate rewrites `webui/package-lock.json` (protected) during its run, and a worktree `.venv` synced strictly from `uv.lock` fails the gate on 10 tests (`neonize` not declared, `mcp` pinned 1.30.0 vs 1.29.1 in green's venv), identically at base. Neither is caused by or fixable in this sub-ticket.
