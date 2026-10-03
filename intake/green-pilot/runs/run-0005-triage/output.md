Type: bug

Title: A killed reviewer or verifier run parks as "harness-bug: results record <role>" instead of "budget kill: <role>"

Summary:
When a reviewer or verifier run is killed (it returns nothing, for example on a budget or session limit), the build loop should park the sub-ticket with reason `budget kill: <role>` so the operator knows to re-dispatch it. Today recording the kill crashes: the build loop passes `--output <run>/output.md` together with `--killed`, a killed run has no `output.md`, and `results record` reads the output file before it looks at `--killed`, so it fails with `FileNotFoundError` (exit 1). The build loop then parks the sub-ticket as `harness-bug: results record <role>`, which reads as a factory defect and hides the real cause. The requester prefers the fix in `results record` (do not read `--output` when `--killed` is given) so the dispatcher stays unchanged and the command works for either caller, with one test showing a killed checker parks as `budget kill: <role>`. The operator approved this fix at the spec gate in advance; it is built after #16 merges, because both change `results_record` in `factory/cli.py`.

Evidence:
- Request: GitHub https://github.com/danielphang/spec-factory/issues/18, found by the spec writer on the first end-to-end pilot (#16) as an out-of-scope observation; "Reproduced by the writer."
- Checked on this checkout (`~/dev/nanobot-upstream`, `feat/lionbot-v3` at `f8f40e0c5`):
  - `factory/cli.py:425` reads `Path(a.output).read_text(...)` whenever `--output` is given, before the `if a.killed:` branch at line 426.
  - `factory/workflows/build.js:139` passes `--output ${r.outputPath}` on every checker call and appends ` --killed` when the run's status is KILLED; `build.js:140` parks with `harness-bug: results record ${role}: <stderr>` when that call fails.
  - `build.js:91-93`: a killed run (empty or null return) is finished with `run finish <id> --status-override KILLED`. `factory/cli.py:255-258` (`run finish`) writes `output.md` only when `--output-file` is given, so a killed run with no agent-written file has none.
  - `factory/cli.py:531-533`: once both checker rows exist, the join already parks with `budget kill: <roles>` when a row is KILLED. The reason exists; only the recording step crashes first.
- Reproduced in a throwaway store (scratch dir; `ticket new` then `results record`, run from the repo root):
  - `FACTORY_STATE=$S bin/factory results record T-0001 --head 000…0 --role verifier --output $S/runs/R1/output.md --run R1 --killed` printed `{"ok": false, "error": "FileNotFoundError: [Errno 2] No such file or directory: '…/runs/R1/output.md'"}` with `exit=1 rows=[]`.
  - The same call without `--output` printed `"rows": [{"role": "verifier", "status": "KILLED"}]` with `exit=0 rows=[verifier.yaml ]`.
- Duplicate search: no duplicate. Searched spec-factory `issues/README.md` (lists #18 as "not in intake yet"), `intake/green-pilot/{requests,tickets,specs}` and green's `knowledge_vault/spec_factory/requests` (T-0001..T-0003 are SPEC-21, SPEC-26 and SPEC-27, which are unrelated). The nearest is #16 / green-pilot T-0001, which hardens the `Commit:` check in the same function. Its approved spec v1 says the `--killed` behaviour stays "exactly as today, with or without `--output`", and its scenario `killed-with-cut-off-output-records-killed` expects exit 0 and a KILLED row when the `--output` file exists. It does not cover a missing output file, so it is related but not a duplicate.

Assumptions (inferences, not stated by the requester):
- "Killed" covers both checker roles, reviewer and verifier, as the title and `--role reviewer|verifier` imply. A killed verifier still writes no `ci` row, as today (`cli.py:524-525`).
- A killed run whose agent did write a partial `output.md` should still record KILLED, and the fix should not regress #16's killed scenarios. The requester's wording ("does not read `--output` when `--killed` is given") would also drop the `Commit:` mismatch check that #16's spec keeps for killed runs with an output. Whether killed runs skip the output entirely, or only tolerate a missing file, is a detail for the spec writer to settle against the merged #16. It does not change the requester's intent.
- The fix lands in `factory/cli.py`, which is not a protected path. The alternative fix (change `build.js`) touches `factory/workflows/**`, which IS protected (infra). If the spec writer picks it, the spec's Risk section must declare that path.
- Suggested priority (suggestion only; priority is a human call): medium-high. Every budget-killed checker today parks with a misleading reason, but nothing is lost: the sub-ticket still parks for a human.
- Sequencing: build only after #16 (green-pilot T-0001) merges, as the operator note says, then rebase onto its `results_record`.

Reason: ACCEPT. The intent is clear and reproduced on this checkout. The requester chose the fix location, and the operator pre-approved the fix at the spec gate (the operator's note of 2026-10-03, and the relayed user message "Also the bug fix is auto approved"). No product decision is open.

STATUS: ACCEPT
CONFIDENCE: high. The defect is reproduced on this checkout (exit 1 with `FileNotFoundError` with `--output`, exit 0 with a KILLED row without it), and the `budget kill:` park path already exists in the join.
ESCALATIONS: none
