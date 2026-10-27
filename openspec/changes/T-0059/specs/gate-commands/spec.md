## ADDED Requirements

### Requirement: This instance's gate replays current truth with the integration checkout's harness
`.factory/instance.yaml` SHALL list, as its last gate command, `factory truth check` run by the integration checkout's `bin/factory` on the integration checkout's store, skipping each scenario whose WHEN runs the harness suite. On this change's checkout and this repo's live store, the check SHALL report no failure in the capabilities this change restates or whose scenarios reuse a restated fixture.

#### Scenario: The instance's last gate command is the truth check on the integration checkout's store
- WHEN `(sed -n '/^gate_commands:/,/^[a-z_]*:/p' .factory/instance.yaml | grep '^  - ' | tail -1)`
- THEN it prints exactly `  - "{integration}/bin/factory truth check --store {integration}/.factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'"`

#### Scenario: The truth check on this checkout reports no failure in the capabilities this change restates
Run from the checkout under test, a worktree of this repo, after `uv sync --frozen`, with `git` and `node` on `PATH`. The store is this repo's live store, found from the checkout's git common directory. It names four capabilities so that, once in current truth, it never replays itself.
- WHEN `(I=$(cd "$(git rev-parse --git-common-dir)/.." && pwd -P); bin/factory truth check --store $I/.factory/store --capability role-escalations --capability harness-code --capability harness-docs --capability live-store-guard > ${TMPDIR:-/tmp}/t0059-live.txt 2>&1; echo "exit=$? $(tail -1 ${TMPDIR:-/tmp}/t0059-live.txt | sed -n 's/.* \([0-9][0-9]*\) failed.*/failed=\1/p')")`
- THEN it prints exactly `exit=0 failed=0`

