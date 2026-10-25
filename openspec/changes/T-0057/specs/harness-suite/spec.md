## ADDED Requirements

### Requirement: The suite passes with this change, which changes only the two test files its decisions overturn
The harness suite SHALL pass with this change; among existing test files this change MUST modify or delete only `tests/factory/test_spec_store.py` and `tests/factory/test_shepherd.py`, and each test file it adds SHALL fail, with at least one failed test, against the harness code of the change's base.

#### Scenario: The suite passes, only the two listed test files change, and every added test file fails on the base
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends. The base is `git merge-base HEAD main`. Its tree is unpacked into that directory, and the added files are copied in beside its tests.
- WHEN `(P=$(mktemp -d /tmp/t0057-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; B=$(git merge-base HEAD main); echo "changed=$(git diff --name-only --diff-filter=DMR $B HEAD -- tests | sort | paste -sd, -) added=$(git diff --name-only --diff-filter=A $B HEAD -- tests | grep -c '/test_[^/]*\.py$')"; mkdir $P/base && git archive $B | tar -x -C $P/base && for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests); do mkdir -p $P/base/${f%/*} && cp $f $P/base/$f; done; for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests | grep '/test_[^/]*\.py$'); do echo "$f on the base: $(cd $P/base && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider $f 2>&1 | tail -1 | sed 's/ in [0-9.]*s.*//')"; done; rm -rf "$P")`
- THEN the first line reports a number of passed tests and no `failed` or `error`. The second is `changed=<list> added=<n>`, where `<list>` is empty or a comma-separated subset of `tests/factory/test_shepherd.py,tests/factory/test_spec_store.py`, and n is at least 1. Then n lines follow, each `<added test file> on the base: <pytest summary>`, and every summary includes `failed`

