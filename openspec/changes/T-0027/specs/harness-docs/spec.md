## ADDED Requirements

### Requirement: The documents record spec amendment and the cross-ticket check
`docs/changelog.md` SHALL gain one entry, numbered without a gap, covering the amend command and the critic's cross-ticket check; `docs/design.md` SHALL name `factory spec amend` and give the critic the approved changes not yet archived in its routing row; `dev/build-harness.spec.md` SHALL name `spec amend`; README's "Where a human decides" SHALL list `factory spec amend`; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the amendment change in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | grep -c 'spec amend'; grep '^[0-9]*\. ' docs/changelog.md | grep 'spec amend' | grep -oF -e 'in flight' -e tasks.md -e 'not yet archived' -e whichever | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `4`

#### Scenario: The design doc and build spec name the amend command and the critic's new input
- WHEN `(echo "amend=$(grep -c 'factory spec amend' docs/design.md | awk '{print ($1 > 0)}') row=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c 'not yet archived') build=$(grep -c 'spec amend' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `amend=1 row=1 build=1`

#### Scenario: README lists the amend command under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); echo "amend=$(echo "$H" | grep -c 'factory spec amend' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `amend=1`

#### Scenario: The amendment change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`
