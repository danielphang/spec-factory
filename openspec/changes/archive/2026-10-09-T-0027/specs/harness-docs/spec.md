## ADDED Requirements

### Requirement: The critic's rubric asks about cross-ticket dependencies
The critic's system prompt MUST tell it to check each scenario against approved changes not yet archived and to require the scenario's setup to hold whichever of the two merges first, and the runtime critic prompt SHALL stay a copy of `docs/prompts/03-spec-critic.md` with its round placeholder filled.

#### Scenario: A critic run's system prompt carries the cross-ticket rule
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; R=$(bin/factory run start --role critic --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); echo "rule=$(grep -c 'whichever of the two merges first' $FACTORY_STATE/runs/${R:-none}/system-prompt.txt 2>/dev/null)")`
- THEN it prints exactly `rule=1`

#### Scenario: The runtime critic prompt stays a copy of the documented one
- WHEN `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)`
- THEN it prints exactly `copies=same`

### Requirement: The documents record spec amendment, spec drift and the cross-ticket check
`docs/changelog.md` SHALL gain one entry, numbered without a gap, covering the amend command with its intent flag, the drift check and the critic's cross-ticket check; `docs/design.md` SHALL name `factory spec amend` and `--intent unchanged`, carry a Spec drift paragraph and give the critic the approved changes not yet archived in its routing row; `dev/build-harness.spec.md` SHALL name `factory spec amend` and spec drift; README SHALL list the command under "Where a human decides" and the feature under Built; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. ' docs/changelog.md | grep -F 'factory spec amend'); echo "$E" | grep -c .; echo "$E" | grep -oF -e '--intent' -e 'in flight' -e tasks.md -e 'spec drift' -e 'not yet archived' -e whichever | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `6`

#### Scenario: The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input
- WHEN `(echo "amend=$(grep -c 'factory spec amend' docs/design.md | awk '{print ($1 > 0)}') intent=$(grep -c -- '--intent unchanged' docs/design.md | awk '{print ($1 > 0)}') drift=$(grep -c '^\*\*Spec drift\.\*\*' docs/design.md) row=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c 'not yet archived') build=$(grep -c 'factory spec amend' dev/build-harness.spec.md | awk '{print ($1 > 0)}') build_drift=$(grep -ci 'spec drift' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `amend=1 intent=1 drift=1 row=1 build=1 build_drift=1`

#### Scenario: README lists the amend command and the drift check
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' README.md); B=$(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' README.md); echo "amend=$(echo "$H" | grep -c 'factory spec amend' | awk '{print ($1 > 0)}') intent=$(echo "$H" | grep -c -- '--intent' | awk '{print ($1 > 0)}') built=$(echo "$B" | grep -c '^- \*\*Spec amendment and drift\.\*\*')")`
- THEN it prints exactly `amend=1 intent=1 built=1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`
