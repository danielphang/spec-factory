# Ruling on T-0030.1 (BLOCKED from implementer), operator, 2026-10-07

Operator's choice in the Green session: "Retry once as is".

The previous run (run-0312) was refused by Claude Code's auto-mode permission check ("Code from External") before it changed anything, and stopped correctly. Nothing about the spec, base or branch is wrong.

Build the sub-ticket as specified, from the start of the process. If the permission check refuses a command again, do not try to reach the same result through another tool or another form of the command. Stop, change nothing further, and report BLOCKED with the refused command and the reason it gave. The operator will then add a permission rule.
