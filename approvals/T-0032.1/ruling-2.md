# Ruling on T-0032.1 (BLOCKED from implementer), operator, 2026-10-06

Operator's choice in the Green session: "Retarget test, keep skip lines".

1. `tests/factory/test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it` is a test to change. It was added by T-0028.1 (`0e99fa7`) after this spec's evidence was taken, so the spec could not list it. Change its `t.checker("reviewer")` to `t.checker()`, which composes a verifier input. The test then checks the same behaviour on the role that still receives the gate commands. Change nothing else in that file.
2. Keep part B.2 as specified for the gate-commands sentence. The reviewer's "Where you work" paragraph says the verifier runs the gate commands and the reviewer does not.
3. Restore the "SKIPPED by the harness for this diff, do not run: `<cmd>`" lines in the reviewer's input, exactly as T-0028 produces them. They are consistent with "you do not run them". The current-truth `gate-commands` requirement ("a reviewer or verifier run ... MUST list that command apart from the commands to run") then stays true, and the pinned spec needs no MODIFIED delta.
4. Re-run the gate commands and record the result. Nothing else changes.
