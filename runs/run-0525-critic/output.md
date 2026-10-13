## Spec critic review, round 1 (T-0053 / issue #110)

### What I checked

Cited paths and claims, all from `~/dev/spec-factory` at `525d73f` (clean tree):
- `ls docs/` lists the nine entries the spec gives; no `docs/standards.md`.
- `factory/instance.py:170-175` is `fill_standards`, and it fills `{writing standard}` with the harness checkout's `docs/writing.md` path, as Evidence says.
- `docs/north-star.md:21` is one 101-character line holding the whole "The factory serves ..." sentence; line 22 is empty. Part C's "line 21 becomes exactly ... No other line changes" is therefore well-formed, and the one-line `grep -cxF` scenario can match it. 27 lines of that file already exceed 100 characters, so the new 112-character line breaks no convention of the file.
- `wc -l README.md` prints 1106. The `docs/writing.md` row is README line 1027, inside "Where things live" (line 1015) and before "Related work and history" (line 1036); the range holds 17 `| ` rows. The current-truth requirement caps README at 1,110 (input line 672). T-0052's design item 3 allows README up to four more lines, as Evidence says.
- `.factory/store/requests/T-0053.md` line 29 is `# Writing and design standards`; line 174 ends `(commit, run id, ticket), then what was not done.`; `sed -n '29,174p' | sed 1d | LC_ALL=C shasum -a 256` prints `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`, the spec's hash; the range has no tab and no trailing space. 174-29+1 = 146 lines, matching the Size line.
- `docs/changelog.md` ends with entry 72 then the "Declined:" paragraph, as Part D says.
- `grep -rn 'north-star\|Where things live\|standards.md' tests/factory` matches nothing; `test_writing_standard.py` and `test_coding_standard.py` pin the prompt blocks and `docs/writing.md`, which this change leaves untouched. "Tests to change: none" holds.
- `dev/issues.md` names none of #109, #110, #111, consistent with the Risk note.

Acceptance commands run on base through the running-code wrapper (no test suite): scenario 1 printed `title=0 body=e3b0c442...b855`, scenario 2 `row=0`, scenario 3 `readers=0`, scenario 4 `line=0 serves=1`, each as verification.md states for "today". Scenarios 1, 2 and 4 fail today for the stated reason and would fail against a stub (wrong text, no row, product name kept). I did not run the prototype; Evidence's prototype result (README stays 1,106 lines) follows from a one-line row replacement and I take it on that basis.

Consistency with T-0052 (approved, not archived): T-0052 edits README line 463, lines 579-587 and the status header, and appends a changelog entry with the next free number. This spec edits README line 1027 and appends with the next free number. Neither scenario set depends on the other's text; the CONTIGUOUS check and the 1,110 cap hold in either merge order. No conflict.

Not a hidden decision, but worth the operator's eye at the gate: Part B's replacement row is a long single table line; README already has such lines, and zero growth is what the budget asks for.

### Findings

[NIT] 6 proposal.md, Problem, first paragraph
Problem: "the spec-writer prompt" is used before "role" and "prompt" are glossed in the second paragraph; a reader new to this system meets it with only "(the spec format)" as a hint.
Evidence: Problem paragraph 1 vs paragraph 2 ("A role is one of the factory's agents ... each run from a fixed prompt").
Suggested fix: write "the prompt that drives the spec-writer agent (the spec format)" in paragraph 1, or move the role gloss up one paragraph.

No blocking issues. The spec is grounded, each NEW scenario fails today for the stated reason, the change fits one PR, the ride-along fixes are declared and small, and the only overlapping work (T-0052) is absorbed by the next-free-number rule and the zero-growth row.

STATUS: APPROVE
CONFIDENCE: high — every cited path, line and hash checked against the tree; four of the five NEW/REGRESSION scenarios run on base and matched; only the prototype's line count is taken from the spec.
ESCALATIONS: none
