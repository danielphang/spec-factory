# Changes requested on T-0031 (#51), operator, 2026-10-09

The build parked: T-0031.1's implementer was BLOCKED. `tests/factory/test_gate_paths.py::test_a_null_absent_or_unscoped_mapping_gate_runs_as_a_string_list_does` (line 217), added by #48 after this spec was written, builds its expected gate line from the old wrapper text. Part A adds a prefix to every wrapped gate command, so the test fails.

Re-spec against the current `main`:
1. List that test under "Tests to change", with the reason and the exact change: it expects the new wrapper prefix, and nothing else in the file changes. Then check the whole suite for any other test that pins the wrapper text or the build start-up, and list each one found.
2. Refresh the Evidence and line references: #48, #57, #75, #77 and #78 have changed `compose.py`, `cli.py` and `build.js` since 2026-10-04.
3. Declare protected paths on the Risk section's `Protected paths: ` line, now that #57 is live.
4. Keep the design and the Decisions unless the refresh shows a conflict.
The re-plan supersedes T-0031.1 (#77).
