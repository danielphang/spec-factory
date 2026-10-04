## ADDED Requirements
### Requirement: Downstream roles receive the pinned spec without Evidence and Responses
The composed input of the planner, implementer, reviewer and verifier, the parent-close verifier included, SHALL hold every section of the pinned spec except `## Evidence` and `## Responses`, and MUST name the full spec file's absolute path.

#### Scenario: Downstream roles get every spec section but Evidence and Responses, and the full spec's path
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0030-spec.sh && marks planner $(comp planner T-0001) && marks implementer $(comp implementer T-0001.1) && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H30 >/dev/null && marks reviewer $(comp reviewer T-0001.1) && marks verifier $(comp verifier T-0001.1) && bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null && marks parent-close $(comp verifier T-0001))`
- THEN it prints exactly `planner: evidence=0 responses=0 kept=9 full=1`, `implementer: evidence=0 responses=0 kept=9 full=1`, `reviewer: evidence=0 responses=0 kept=9 full=1`, `verifier: evidence=0 responses=0 kept=9 full=1`, `parent-close: evidence=0 responses=0 kept=9 full=1`, one per line

### Requirement: A round-2 critic receives the smaller of the diff and the previous version
A round-2 critic's input MUST hold the unified diff from the previous spec version to the current one when that diff is smaller than the previous version, and SHALL hold the previous version whole otherwise, with its prior findings in both cases.

#### Scenario: A round-2 critic receives a small revision as a diff
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh small) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) added=$(grep -cx -- '+NEW-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
- THEN it prints exactly `removed=1 added=1 keep100=1 prior_findings=1`

#### Scenario: A round-2 critic receives a rewritten spec's previous version whole
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh rewrite) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) other100=$(grep -cx 'other line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
- THEN it prints exactly `removed=0 keep100=1 other100=1 prior_findings=1`

