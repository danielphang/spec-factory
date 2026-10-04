## ADDED Requirements
### Requirement: The documents describe registered role agents, trimmed inputs and effort
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; the design doc's routing table and the build spec SHALL describe the trimmed spec and the round-2 diff; README SHALL describe registered roles, the `agent call failed` park and the `effort:` map and SHALL no longer tell every target to run inline or list per-role effort as not built; `.factory/README.md` SHALL no longer say this repo adds no `.claude/agents/`; no prompt copy SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records registered agents, trimmed inputs and effort as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e factory-implementer -e Evidence -e effort -e diff -e inlineRoles | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The routing table and build spec describe the trimmed spec and the diff, and no prompt changes
- WHEN `(echo "critic_diff=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c diff) trimmed_rows=$(grep -e '^| Human spec gate | Approved' -e '^| Planner | PLANNED' -e '^| Implementer | READY-FOR-REVIEW' -e '^| Merge gate | CI green' docs/design.md | grep -c Evidence) build_spec=$(grep 'round ≥ 2: prior findings' dev/build-harness.spec.md | grep -c diff) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `critic_diff=1 trimmed_rows=4 build_spec=1 prompts=0`

#### Scenario: README and the instance page describe registered roles, the park and effort
- WHEN `(Q=$(printf '\140'); R=$(tr '\n' ' ' < README.md | tr -s ' '); I=$(tr '\n' ' ' < .factory/README.md | tr -s ' '); echo "inline_everywhere=$(echo "$R" | grep -o 'inlineRoles: true. on every target' | grep -c .) parks=$(echo "$R" | grep -o 'agent call failed' | grep -c . | awk '{print ($1 > 0)}') effort_map=$(grep -c "${Q}effort:${Q}" README.md | awk '{print ($1 > 0)}') effort_not_built=$(grep -c 'Per-role effort settings' README.md) instance_inline=$(echo "$I" | grep -o 'adds no .\.claude/agents/.' | grep -c .)")`
- THEN it prints exactly `inline_everywhere=0 parks=1 effort_map=1 effort_not_built=0 instance_inline=0`

#### Scenario: The role-agents change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

