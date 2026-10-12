## Proposed change

Every part follows the same rules:

- Move each definition named below from `factory/cli.py` to its module, byte for byte. Keep the
  definitions in the order they had in `factory/cli.py`.
- Give each new module a one-line docstring that says its job, then
  `from __future__ import annotations`, then the imports its definitions use. Import other moved
  definitions by name from their new module, as in `from factory.common import _rel, out`.
- Never import `factory.cli` from a new module.
- In `factory/cli.py`, import by name what it still calls, and drop each import nothing uses any
  more.
- Move a `# -----` section comment with its code, or drop it where its section is now empty.
- Leave no run of three blank lines.

Line numbers are on `main` at `6203096`. Each part must leave the suite passing. The parts are in
build order, and each needs the ones before it as noted.

**A. `factory/drift.py`, the spec-drift checks.** Needs nothing. Moves `_check_sibling_tests`
(249-273), `TEST_FILE_RE` and `TICK_RE` (276-277), `_check_drift` (280-296), `_sibling_drift`
(299-318), `_test_drift` (321-358) and `_tests_to_change_section` (361-370). `factory/cli.py`
imports `_check_drift` and `_check_sibling_tests` for `run_start`.

**B. `factory/common.py`, shared helpers and the live-store fence.** Moves `out` (30-31), `_rel`
(34-35), `_integration_head` (548-554), `_add_spec_version` (557-567), `_in_flight` (1964-1967) and
`fence` (1970-1988). `READ_ONLY` and its comment stay in `factory/cli.py` beside `main`, which
reads it. `factory/cli.py` imports `out`, `_rel`, `_add_spec_version` and `fence`.

**C. `factory/setup.py`, setup.** Needs B. Moves `_git_toplevel` through `paths_cmd` (1294-1624):
`_git_toplevel`, `_new_instance_yaml`, `_revision`, `_refuse_inside_store`, `_head_branch`,
`_add_store_checkout`, `_exclude_store`, `_store_hint`, `init_cmd`, `STATE_DIR_LINE`,
`_ignored_files`, `_copy_mismatch`, `store_migrate` and `paths_cmd`. It uses `import shutil` for
`shutil.copy2` (Decision 6). `stats_cmd` stays (Decision 4).

**D. `factory/gates.py`, the gates, and the two doc lines.** Needs B. Moves `ticket_head`
(830-851), `results_record` (854-891), `results_show` (894-899), `DECLARED_RE` (902), `_in_repo`
(905-907), `declared_paths` (910-922), `undeclared_protected` (925-943), `_branch_tip` (946-951),
`merge_cmd` (954-1000), `REVIEWER_STATUSES`, `VERIFIER_STATUSES` and `MAX_CONFLICT_RUNS`
(1003-1005), `ticket_join` (1008-1045), `ticket_parent_check` (1048-1061), `_verifier_rows`
(1666-1676), `_reused_subticket_run` (1679-1708), `_parent_close_verified` (1711-1725) and
`archive_cmd` (1728-1741). `factory/cli.py` imports `_parent_close_verified` for
`ticket_transition`, and the commands for `build_parser`. Docs, in the same part:
- `README.md:1171`: replace "`factory/cli.py` `ticket_join`, `merge_cmd`, `archive_cmd`" with
  "`factory/gates.py` `ticket_join`, `merge_cmd`, `archive_cmd`".
- `README.md:9`: set the status date to the day of the change.
- `docs/principles.md:106-107`: replace "the guards in `factory/cli.py`:" and the next line's
  "`ticket transition`, `run start`, `merge`;" with "the guards in `factory/cli.py`
  (`ticket transition`, `run start`) and `factory/gates.py` (`merge`);". Re-wrap the paragraph
  at 100 columns, keeping "`factory/gates.py` (`merge`)" on one line.

**E. `factory/human.py`, human decisions.** Needs B and D. Moves `_restart_note` (576-589),
`spec_amend` (592-659), `_by` (1066-1067), `_approval_dir` (1070-1073), `_next_n` (1076-1077),
`_refuse_unless_applies` (1080-1085), `_copy_record` (1088-1092), `approve_spec` (1095-1126),
`request_changes` (1129-1141), `resolve` (1144-1252), `_supersede` (1255-1259),
`_set_aside_failed_rows` (1262-1282) and `decision_add` (1285-1289). It imports `_branch_tip` and
`undeclared_protected` from `factory.gates`, and `out`, `_rel`, `_add_spec_version` and `fence`
from `factory.common`. After this part, `factory/cli.py` is under 900 lines.

Which scenarios each part can pass:

| Part | Scenarios |
|---|---|
| A | "The drift checks live in factory/drift.py" |
| B | "The shared helpers and the live-store fence live in factory/common.py" |
| C | "Instance and store setup live in factory/setup.py" |
| D | "The gates live in factory/gates.py"; "The README and the principles name gates.py for the moved gate commands" |
| E | "The human decisions live in factory/human.py"; "factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines" |
| every part | every other scenario of this change |

## Tests to change

none. No test reads `factory/cli.py` as a file or calls any `factory.cli` name but `main`
(Evidence). The two patched functions stay reachable as before.

