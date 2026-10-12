Commit: c30b80f45a39824b71c7064cc22e2563a53f9438

How this was run. The PR head was checked out in the run worktree (`wt`, clean, HEAD `c30b80f`, `main` = base `57b46e1`). The base was checked out as a detached worktree in this run's scratch directory, then removed afterwards. Every command was copied verbatim into `scratch/cmds.txt`. A grep confirmed that each of the 25 commands appears byte for byte in input.md. Each command ran through the "Running code" wrapper with a fresh HOME and `TMPDIR` set to the scratch directory, so M reads its script from `scratch/t0047-moved.py`. That script was extracted verbatim from the scenario block in `specs/T-0047/v2.md`. Logs are in `scratch/pr.log`, `scratch/base.log`, `scratch/suites.log` and `scratch/gate-pytest.log`.

Per criterion:
- NEW | gates module listing (`import factory.gates && grep … factory/gates.py …`) | base: `ModuleNotFoundError: No module named 'factory.gates'`, exit 1, nothing on stdout (the reason the spec gives) | PR: `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`, exit 0, exact match | PASS
- NEW | docs counts (`echo "$(grep -c 'factory/gates.py. .ticket_join., …' README.md) … factory/gates.py 2>/dev/null)"`) | base: `0 1 0 1 ` (as the spec states) | PR: `1 0 1 0 3` | PASS
- NEW (intermediate) | `uv run --frozen python -B -c 'import factory.gates'` | base: ModuleNotFoundError, exit 1 | PR: exit 0, no output | PASS
- NEW (intermediate) | `git diff --check main...HEAD -- README.md docs/principles.md` | base: no output, exit 0 (an empty diff, so it passes by construction) | PR: no output, exit 0 | PASS (see ESCALATIONS 1)
- REGRESSION | drift module scenario | base: not run | PR: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` | PASS
- REGRESSION | common module scenario | base: not run | PR: `_add_spec_version _in_flight _integration_head _rel fence out` | PASS
- REGRESSION | setup module scenario | base: not run | PR: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate` | PASS
- REGRESSION | M `(uv run --frozen python -B ${TMPDIR:-/tmp}/t0047-moved.py)` | base (for reference): `pairs=2 added=0 removed=0 lines=35` | PR: `pairs=3 added=0 removed=0 lines=46`, nothing after it (46 ≤ 100) | PASS
- REGRESSION | R1 | base: not run | PR: `factory/__main__.py factory/drive.py factory/stats.py` | PASS
- REGRESSION | R2 | base: not run | PR: `7 True True` | PASS
- REGRESSION | R3 `uvx ruff check --select F factory` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R4 (t0047-suite) | base: not run | PR: `576 passed in 547.53s (0:09:07)`, no line after it | PASS
- REGRESSION | R5 | base: not run | PR: `0 0` | PASS
- REGRESSION | R6 | base: not run | PR: `0` | PASS
- REGRESSION | R7 | base: not run | PR: `0 2 2` | PASS
- REGRESSION | R8 | base: not run | PR: `0` | PASS
- REGRESSION | R9 | base: not run | PR: `0` | PASS
- REGRESSION | R10 | base: not run | PR: `0 12 1` | PASS
- REGRESSION | R11 `uvx ruff check --select F401,F841 factory tests` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R12 (t0044-suite) | base: not run | PR: `576 passed in 548.13s (0:09:08)`, no line after it | PASS
- REGRESSION | R13 | base: not run | PR: `0` (exit 1, which is how `grep -c` exits on zero matches; base also gives `0`, exit 1) | PASS
- REGRESSION | R14 | base: not run | PR: `0 1` | PASS
- REGRESSION | R15 | base: not run | PR: `1 1` | PASS
- REGRESSION | R16 | base: not run | PR: `0` (exit 1 from `grep -c`, the same on base) | PASS
- REGRESSION | R17 | base: not run | PR: `1 1` | PASS
- REGRESSION | R18 | base: not run | PR: `0 1 1 1` | PASS
- REGRESSION | R19 | base: not run | PR: `1 1 2` | PASS

Gate suite: PASS
  `git diff --check main...HEAD`: exit 0, no output.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `576 passed in 552.19s (0:09:12)`.

Probes:
- AST comparison of base `factory/cli.py` with PR `factory/gates.py` and `factory/cli.py`. This check is independent of M. Script: `scratch/probe_ast.py`, run with `git show` on both SHAs. → All 18 definitions in gates.py are byte-identical to their base text and appear in the base order. None is still defined in cli.py. No base definition went missing, and no definition left in cli.py changed its text. → OK
- References to moved names through the CLI module, such as `cli.MAX_CONFLICT_RUNS` or `cli.merge_cmd`, in `factory/`, `tests/`, `bin/` and `agents/`; also any test monkeypatch or `mock.patch` of the CLI namespace. → None found. Outside `gates.py` and `cli.py`, no file names a moved name, so moving them breaks no attribute access. cli.py uses only the 10 names it imports: the 7 commands in `build_parser`, `_parent_close_verified` at line 161, and `_branch_tip` and `undeclared_protected` in `resolve` at lines 829-830. → OK
- Edge inputs to the moved `declared_paths`, called from its new module and from base `cli`: empty text; `Protected paths: none`; a list with a trailing `.` that mixes `~/…` with repo paths; a declaration line outside `## Risk`; a `## Risk` line inside a code fence; a malformed unquoted entry. → Both commits give identical results: `[]`, `[]`, `['factory/cli.py', 'factory/gates.py']`, `['b']`, `[]`. The parser now dispatches `ticket head|join|parent-check`, `results record|show`, `merge` and `archive` to `factory.gates.*`. `gates.Refused is cli.Refused` is True. → OK
- Process-level CLI: `merge`, `results record --role bogus`, `ticket join`, `archive` and `ticket head` on a nonexistent ticket, run from a directory inside the live store's `runs/`. → PR and base give the same exit code (2) and the same refusal for every command: the live-store fence refuses all four write commands, and `ticket join` stops at the harness-lock check. Only the harness SHA in that message differs. The fence still guards the moved commands. Nothing was written. → OK

Other observations, not blocking:
- The docs edits match the sub-ticket. `README.md:9` now reads 2026-10-12, the day of the change. `README.md:1171` now names `factory/gates.py`. In `docs/principles.md:106-109` the paragraph is re-wrapped at 100 columns: the new lines are 99, 96, 99 and 5 columns, and "`factory/gates.py` (`merge`)" stays on one line.
- The PR description says `factory/cli.py` also imports `_branch_tip` and `undeclared_protected`, which the sub-ticket does not list. The import is needed, because `resolve` stays in cli.py until part E and calls both (cli.py:829-830). Without it, R3 would report F821 (undefined name).

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance and gate command ran exactly as written on `c30b80f`, and each NEW criterion that can discriminate failed on base for the reason the spec gives. An independent AST check and behaviour probes show the moved code is byte-identical and behaves the same as on base.
ESCALATIONS:
1. The sub-ticket labels `git diff --check main...HEAD -- README.md docs/principles.md` a NEW intermediate check. It cannot fail on base, because on base `main...HEAD` is an empty diff. It is a guard against whitespace errors, not a criterion that tells base and PR apart, and the gate's `git diff --check main...HEAD` already covers it. I did not count this as a SPEC-DEFECT, because the check passing on both commits says nothing about whether the change works. Future plans should label such guards REGRESSION.
