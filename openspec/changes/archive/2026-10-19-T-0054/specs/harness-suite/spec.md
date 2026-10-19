## ADDED Requirements

### Requirement: The suite tests the launch copy, a reformatted reply and the route back to checks, and changes no existing test
The harness suite SHALL pass with no existing test file changed or deleted. The test files this change adds SHALL each fail, with at least one failed test, when run against the harness code of the change's base.

#### Scenario: The suite passes, no existing test changes, and every test file this change adds fails on the base
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends. The base is `git merge-base HEAD main`; its tree is unpacked into that directory, and the added files are copied in beside its tests.
- WHEN `(P=$(mktemp -d /tmp/t0054-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; B=$(git merge-base HEAD main); echo "changed=$(git diff --name-only --diff-filter=DMR $B HEAD -- tests | grep -c .) added=$(git diff --name-only --diff-filter=A $B HEAD -- tests | grep -c '/test_[^/]*\.py$')"; mkdir $P/base && git archive $B | tar -x -C $P/base && for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests); do mkdir -p $P/base/${f%/*} && cp $f $P/base/$f; done; for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests | grep '/test_[^/]*\.py$'); do echo "$f on the base: $(cd $P/base && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider $f 2>&1 | tail -1 | sed 's/ in [0-9.]*s.*//')"; done; rm -rf "$P")`
- THEN the first line reports a number of passed tests and no `failed` or `error`; the second is `changed=0 added=<n>` with n at least 1; then n lines follow, each `<added test file> on the base: <pytest summary>`, where every summary includes `failed`

