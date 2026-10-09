## ADDED Requirements
### Requirement: The documents record the capability index
The triage prompt's design block, its `docs/prompts/` copy and the runtime prompt SHALL each carry the `Capabilities:` output line. `docs/design.md`, `dev/build-harness.spec.md` and the README's Triage, Spec writer and Spec critic rows MUST describe the capability index. `docs/changelog.md` MUST have an entry for issue #75, with no whitespace error in the change.

#### Scenario: The prompt copies, design, build spec, README and changelog name the capability index
- WHEN `(echo "docs-copy=$(grep -c '^Capabilities:' docs/prompts/01-triage.md) runtime=$(grep -c '^Capabilities:' factory/prompts/triage.md) changelog=$(grep -c '^[0-9]*\. After issue #75 ' docs/changelog.md) design=$(grep -q 'capability index' docs/design.md && echo y || echo n) build-spec=$(grep -q 'capability index' dev/build-harness.spec.md && echo y || echo n) readme=$(grep -E '^\| (Triage|Spec writer|Spec critic) \(' README.md | grep -c 'capability index')"; git diff --check main...HEAD && echo whitespace=ok)`
- THEN it prints exactly `docs-copy=1 runtime=1 changelog=1 design=y build-spec=y readme=3`, then `whitespace=ok`

