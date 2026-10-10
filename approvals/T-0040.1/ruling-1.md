Operator ruling, 2026-10-09, on run-0405's BLOCKED report.

The "stopped driver" scenario's count was a defect in the spec, not in your build. Design A.7 names the run id both in the `running` list and on the `last:` line, so `grep -c 'run-0001-triage'` counts 2. The approved spec is amended (intent unchanged): the check now counts only the `running` list's entry, `grep -c '^- run: run-0001-triage'`, and still expects `running=1`. Keep design A.7 as built. Re-run that scenario as now written, confirm the rest of the acceptance results still hold on your head, and hand off as usual.
