## ADDED Requirements

### Requirement: The suite passes with this change, which changes only the stats test the --accept-harness refusal overturns
The harness suite SHALL pass with this change, and among existing test files this change MUST modify or delete only `tests/factory/test_stats.py`.

#### Scenario: The harness suite passes
- WHEN `(uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1)`
- THEN its last line reports tests passed and no `failed` or `error`

#### Scenario: The only existing test file changed is the stats test
- WHEN `(git diff --name-only --diff-filter=MD $(git merge-base main HEAD) HEAD -- tests/factory)`
- THEN it prints nothing, or only `tests/factory/test_stats.py`

