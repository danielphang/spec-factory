## ADDED Requirements

### Requirement: docs/standards.md holds the operator's writing and design standards
`docs/standards.md` SHALL open with a `# ` title line, and the text after that line SHALL be the operator's approved standards text, whose SHA-256 is `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`; a change to that text modifies this requirement in its own spec.

#### Scenario: The standards file holds the approved text
- WHEN `(f=docs/standards.md; echo "title=$(head -1 $f 2>/dev/null | grep -c '^# ') body=$(sed 1d $f 2>/dev/null | LC_ALL=C shasum -a 256 | cut -c1-64)")`
- THEN it prints exactly `title=1 body=010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`

### Requirement: README points to docs/standards.md
README's "Where things live" table SHALL have exactly one row naming `docs/standards.md`.

#### Scenario: Where things live names the standards file
- WHEN `(echo "row=$(sed -n '/^## Where things live/,/^## Related work and history/p' README.md | grep '^| ' | grep -c 'docs/standards.md')")`
- THEN it prints exactly `row=1`

### Requirement: No role prompt reads docs/standards.md
No file under `docs/prompts/`, `factory/` or `agents/`, and not `docs/writing.md`, SHALL name `docs/standards.md`, so adding it changes no role's behaviour; a spec that changes prompts may modify this requirement.

#### Scenario: Nothing a role reads names the standards file
- WHEN `(echo "readers=$(grep -rlF 'standards.md' docs/prompts docs/writing.md factory agents | grep -c .)")`
- THEN it prints exactly `readers=0`

### Requirement: The north star names its target without the private product
`docs/north-star.md` SHALL describe the factory's current target as "a port of the Nanobot chat bot" in its one sentence on whom the factory serves.

#### Scenario: The north-star sentence names a port of the Nanobot chat bot
- WHEN `(echo "line=$(grep -cxF 'The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).' docs/north-star.md) serves=$(grep -c '^The factory serves its own development' docs/north-star.md)")`
- THEN it prints exactly `line=1 serves=1`

### Requirement: The documents record the standards file
`docs/changelog.md` SHALL hold exactly one entry opening `<n>. After issue #110 `, naming `docs/standards.md`, `docs/writing.md` and `docs/north-star.md`, and its entries SHALL stay numbered without a gap.

#### Scenario: The changelog records issue 110 in one entry without a numbering gap
- WHEN `(E=$(grep '^[0-9]*\. After issue #110 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'docs/standards.md' -e 'docs/north-star.md' -e 'docs/writing.md' | sort -u | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)`
- THEN it prints exactly `entries=1 terms=3`, then `CONTIGUOUS`

