Commit: 359b3c6c88c10f308523d7d733baf60b5797cdcc (branch `factory/T-0047.1`, base 6203096)

## What I checked, in the role's order

1. Test integrity: no file under `tests/` changed (`git diff --name-only 6203096..HEAD -- tests` prints nothing). The diff touches only `factory/cli.py`, `factory/common.py` and `factory/drift.py` (`git diff --stat`: 3 files, +200/-181).
2. Correctness: the moves are byte for byte and in original order. I ran the parent spec's "moved, not rewritten" script, copied from `specs/T-0047/v2.md` into my scratch directory, on the head: `pairs=1 added=0 removed=0 lines=19`, nothing after it. No top-level definition's text changed, and the change adds 19 lines to `factory/*.py` (2,020 → 2,039 by `wc -l`). Each new module loads first in a fresh interpreter (`import factory.drift`, then `import factory.common`, both exit 0, no output), so there is no import cycle. `uvx ruff check --select F factory` prints `All checks passed!`, so no moved body lost an import. `factory/common.py` defines exactly `out _rel _integration_head _add_spec_version _in_flight fence`; `factory/drift.py` exactly `_check_sibling_tests TEST_FILE_RE TICK_RE _check_drift _sibling_drift _test_drift _tests_to_change_section`, both in their `factory/cli.py` order. Neither imports `factory.cli`. `READ_ONLY` and its comment stay in `factory/cli.py` (line 1807) beside `main`.
3. Scope: `factory/cli.py` imports `_add_spec_version, _in_flight, _rel, fence, out` and `_check_drift, _check_sibling_tests` (lines 23-24). `_in_flight` is still called at `factory/cli.py:1390` inside `store_migrate`, which part C moves later, so importing it is required, and the sub-ticket allows "anything else of these it still calls". `_integration_head` is not imported and nothing in `factory/cli.py` calls it. Nothing from parts C, D or E moved.
4. Silent behaviour changes: none. Call sites at `factory/cli.py:213-214` (`run_start`), `:1274` (`init_cmd`) and `:1826` (`main`) are unchanged text. The `# -----` section comments all still head non-empty sections, including "live-store fence" at line 1804, which still covers `READ_ONLY` and `main`. No run of three blank lines (`awk` check prints `0`). `json`, `os` and `re` are still used in `factory/cli.py` (10, 5 and 2 uses), so no import was wrongly kept or dropped.
5. Security and data safety: nothing new; no path, subprocess or write added.
6. Protected paths: all three files touched are declared in the sub-ticket and in the spec's Risk section. Listed under ESCALATIONS for the record.
7. Coding standard: a pure move adds no helper. Lean already.
8. PR description: readable by the operator; glosses harness, drift checks and fence at first use; What changed and Known gaps are in words. One figure is off, below.

## Findings

- [NIT] PR description: What changed: "`factory/cli.py` is now 1,839 lines" → `wc -l factory/cli.py` on 359b3c6 prints `1841`. The writing standard asks that a quoted figure come from the command that produced it; the operator who re-runs `wc -l` sees a different number and has to decide whether the diff is what the description says. The M result (`lines=19`, 2,020 + 19 = 2,039 total across the three files) is consistent with 1,841, so the code is right and only the prose figure is wrong.

The Known gaps item on `spec_amend`'s local `fence` string hiding the imported `fence` function is accurate (`factory/cli.py:495-504`); it hid the module-level function the same way before this change, and ruff's F rules pass.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high. The spec's own moved-not-rewritten script, the fresh-interpreter imports and ruff F all pass on 359b3c6, the three changed files are the three the sub-ticket declares, and no test changed.
ESCALATIONS: protected paths touched, all declared in the sub-ticket and the approved spec's Risk section: `factory/cli.py`, `factory/common.py`, `factory/drift.py`. For the record only; no undeclared path.
