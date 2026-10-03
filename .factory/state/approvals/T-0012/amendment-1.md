# T-0012 amendment 1 (operator, 2026-10-03, at parent close)

Parent-close verifier run-0102 returned SPEC-DEFECT on scenario whitespace-clean: 29 of 30 scenarios pass and the gate passes (116 tests), but `git diff --check "$BASE" HEAD` reports trailing whitespace in harness-written run records under `intake/state/runs/` (`diff.patch`, `input.md`), which embed diffs with single-space context lines. The six sub-ticket merges are clean (`exit=0` each); outside the store the range exits 0.

Ruling: the scenario's range excludes the store (`-- . ':(exclude)intake/state' ':(exclude).factory/state'`). Records stay as written. Applied in place to `specs/T-0012/v3.md` (the pinned version every checker reads) and to its copy `specs/T-0012.md`; the gate approved v3 without this NOTE, and this file is the record of the change.

Follow-up (not this ticket): every later parent in a repo that tracks its store hits the same thing; a store-level `.gitattributes` (`runs/** -whitespace`) written by `init` would fix it once.
