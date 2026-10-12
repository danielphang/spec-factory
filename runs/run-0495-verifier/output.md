Commit: 122e949a9d865f40c3db3104b4908e29e67b5021 (main; parent close of T-0047, sub-tickets .1-.4 merged)
Base: 62030967710765e996fb3d752386f9ce8dec6abc (main before the first T-0047 merge), checked out as a separate worktree in this run's scratch directory, which was removed afterwards.

Every command was run from the checkout root after `uv sync --frozen`, inside the fresh-HOME wrapper, exactly as written in the spec. The `t0047-moved.py` script was written verbatim from the spec's heredoc to `$TMPDIR`, with TMPDIR set to the scratch directory. A scenario's output is quoted only where it is short.

Per criterion:
- NEW | drift checks live in factory/drift.py | base: `ModuleNotFoundError: No module named 'factory.drift'`, nothing printed | PR: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` | PASS
- NEW | shared helpers and fence live in factory/common.py | base: ModuleNotFoundError `factory.common` | PR: `_add_spec_version _in_flight _integration_head _rel fence out` | PASS
- NEW | instance and store setup live in factory/setup.py | base: ModuleNotFoundError `factory.setup` | PR: the exact 14-name list in the spec | PASS
- NEW | gates live in factory/gates.py | base: ModuleNotFoundError `factory.gates` | PR: the exact 18-name list in the spec | PASS
- NEW | human decisions live in factory/human.py | base: ModuleNotFoundError `factory.human` | PR: the exact 13-name list in the spec | PASS
- NEW | cli.py keeps parser, entry point, role list, under 900 lines | base: `2020 3` | PR: `882 3` | PASS
- NEW | every definition keeps its exact text, at most 100 lines added | base: `pairs=0 added=0 removed=0 lines=0` | PR: `pairs=4 added=0 removed=0 lines=54`, nothing after it | PASS
- NEW | README and principles name gates.py | base: `0 1 0 1 ` (empty last count, as the spec states) | PR: `1 0 1 0 3` | PASS
- REGRESSION | only the entry point, driver and stats import factory.cli | base: not run | PR: `factory/__main__.py factory/drive.py factory/stats.py` | PASS
- REGRESSION | the CLI's entry points stay importable | base: not run | PR: `7 True True` | PASS
- REGRESSION | `uvx ruff check --select F factory` | base: not run | PR: `All checks passed!`, rc 0 | PASS
- REGRESSION | suite passes with no test file changed (t0047-suite) | base: not run | PR: `576 passed in 543.75s (0:09:03)`, nothing after it | PASS
- REGRESSION | four dead definitions gone | base: not run | PR: `0 0` | PASS
- REGRESSION | no force-push setting | base: not run | PR: `0` | PASS
- REGRESSION | run start in-flight refusal / rename / store-ignore (new form) | base: not run | PR: `0 2 2` | PASS
- REGRESSION | no three blank lines in a row | base: not run | PR: `0` | PASS
- REGRESSION | three stale texts gone | base: not run | PR: `0` | PASS
- REGRESSION | repo-root helper | base: not run | PR: `0 12 1` | PASS
- REGRESSION | `uvx ruff check --select F401,F841 factory tests` | base: not run | PR: `All checks passed!`, rc 0 | PASS
- REGRESSION | suite passes, only force-push test lines change (t0044-suite) | base: not run | PR: `576 passed in 385.98s (0:06:25)`, nothing after it | PASS
- REGRESSION | only the store module lists a ticket's runs | base: not run | PR: `0` | PASS
- REGRESSION | event log through a shared reader | base: not run | PR: `0 1` | PASS
- REGRESSION | one function records a status transition (new form) | base: not run | PR: `1 1` | PASS
- REGRESSION | spec amend and dispatcher don't build the in-flight list | base: not run | PR: `0` | PASS
- REGRESSION | one function reads the integration-branch tip | base: not run | PR: `1 1` | PASS
- REGRESSION | record copies, set-asides, planner checks, spec apply checks (new form) | base: not run | PR: `0 1 1 1` | PASS
- REGRESSION | failed-command park line and checker cleanup | base: not run | PR: `1 1 2` | PASS

Gate suite: PASS
  `git diff --check main...HEAD`: no output, rc 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 364.91s (0:06:04)`, rc 0.

The suite passed in all three runs. The one-time ordering flake the spec mentions did not appear.

Probes:
- Every command is still wired to the same function. I walked `build_parser()` on base and on the PR. Each has 36 subcommands, and each maps to a function of the same name. The 15 moved commands now resolve to `factory.gates`, `factory.human` or `factory.setup` → OK
- Whole-change comparison, with no help from the merge-commit filter. I ran the spec's AST comparison directly from base to head (`added=0 removed=0 lines=54`) and on each merge against its first parent: 700ce73 19, 57b46e1 16, 43265a0 11, 122e949 8 lines, all `added=0 removed=0`. The scenario's `pairs=4` figure is therefore not hiding an edit made outside the merge commits → OK
- Behaviour outside the suite. In a fresh temp git repo, base and PR each ran `bin/factory` through: `init --repo-name demo` twice (once fresh, once idempotent), `paths`, `approve-spec`, `merge`, `archive`, `ticket join`, `ticket head` and `results show` on a missing ticket, and `--help` for `resolve` and `decision add`. After paths were normalised, the two transcripts are byte-identical, including refusal text, JSON and exit codes (rc 2 for each refusal) → OK
- Import cycles: each of `factory.common`, `drift`, `setup`, `gates`, `human` and `cli` imports cleanly on its own in a fresh interpreter → OK
- The `shutil.copy2` patch point (Decision 6) is still reachable. `factory/setup.py:7` has `import shutil`, and `:311` calls `shutil.copy2(...)` through the module. That is the attribute `tests/factory/test_store_migrate.py:157-163` replaces → OK
- No test file changed. Scenarios 11 and 20 check this with `git diff main...HEAD -- tests`. On a parent close main equals HEAD, so that diff is empty whatever the change did. I checked against base instead: `git diff --name-only 6203096 HEAD` lists only `README.md`, `docs/principles.md` and the six `factory/` modules, with no `tests/` path. `git diff --check 6203096 HEAD` is clean → OK
- Docs: the README status date changed from 2026-10-11 to 2026-10-12. `README.md:1171` now names `factory/gates.py`. `docs/principles.md:106-109` is re-wrapped with no line over 99 columns, and "`factory/gates.py` (`merge`)" sits on one line → OK

Out-of-scope observations:
- The new `factory/drift.py` docstring (line 1) is 101 characters long. No criterion or configured lint checks line length, and the change works either way.
- On a parent close, the `git diff main...HEAD -- tests` half of scenarios 11 and 20 checks nothing, because main equals HEAD; the probe above compares against base instead. Future specs could compare against `git merge-base HEAD main` or against the parent's base.

STATUS: VERIFIED
CONFIDENCE: high. All 27 scenarios and both gates ran on 122e949 with the expected output. All 8 NEW scenarios fail on base for the reasons the spec states. Probes show identical command wiring, identical CLI behaviour and no definition text changed.
ESCALATIONS: none
