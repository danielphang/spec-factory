## ADDED Requirements

### Requirement: The documents record the sibling-merge exception and the start-failure ruling
`docs/design.md`'s Spec drift paragraph SHALL name `main_after` as not drift and its routing rules SHALL name the `harness-bug: run start implementer` ruling; `dev/build-harness.spec.md` SHALL name that ruling; README's Unstick row SHALL name it, and its "Spec amendment and drift" bullet SHALL say a sibling's merge is not drift and SHALL no longer say the check has not yet fired; `docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; no prompt copy SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The design doc, build spec, README and changelog record both changes, and no prompt copy changes
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; B=$(sed -n '/^- \*\*Spec amendment and drift\.\*\*/,/^- \*\*Re-plan after a re-spec\.\*\*/p' README.md); echo "design-drift=$(y $(grep '^\*\*Spec drift\.\*\*' docs/design.md | grep -c main_after)) design-ruling=$(y $(grep -c 'harness-bug: run start implementer' docs/design.md)) buildspec=$(y $(grep -c 'harness-bug: run start implementer' dev/build-harness.spec.md)) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c 'harness-bug: run start implementer')) bullet-sibling=$(y $(echo "$B" | grep -c 'not drift')) bullet-stale=$(y $(echo "$B" | grep -c 'has not yet fired')) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#85' -e main_after -e 'harness-bug: run start implementer' | sort -u | grep -c .)`
- THEN it prints exactly `design-drift=yes design-ruling=yes buildspec=yes unstick=yes bullet-sibling=yes bullet-stale=no prompts=0`, then `CONTIGUOUS`, then `3`

#### Scenario: The sibling-merge change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

