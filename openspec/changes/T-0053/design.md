## Proposed change

A. Create `docs/standards.md` with the text of `.factory/store/requests/T-0053.md` lines 29-174,
   byte for byte, ending in one newline: from the line `# Writing and design standards` to the
   line ending `(commit, run id, ticket), then what was not done.` Copy it with `sed -n '29,174p'`
   rather than retyping it. Check: `sed 1d docs/standards.md | LC_ALL=C shasum -a 256` prints
   `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`.

B. In README's "Where things live" table, replace the `docs/writing.md` row with one row whose
   first cell names `docs/writing.md` and `docs/standards.md`. Suggested text:
   `` | `docs/writing.md`, `docs/standards.md` | The writing standard for every section a person
   reads; the preamble names the runtime's copy. `docs/standards.md` collects it with the
   operator's other writing and design standards in one file that can be copied out of the repo;
   no prompt reads it | `` (one line). Add no line elsewhere in README. Per "Maintaining this
   page", set the status header's date to the merge date if it differs; that changes no line
   count.

C. In `docs/north-star.md`, line 21 becomes exactly:
   `The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).`
   No other line of the file changes.

D. In `docs/changelog.md`, add one entry after the last numbered entry (today 72), before the
   closing "Declined:" paragraph, separated by blank lines like its neighbours. Number it with the
   next free number. It opens `<n>. After issue #110 (2026-10-13), ` and names
   `docs/standards.md`, `docs/writing.md` and `docs/north-star.md`: the standards were spread over
   four places and are now in one self-contained file; no prompt names it, so no role's behaviour
   changes; README's `docs/writing.md` row now names it; the north-star sentence names the target
   as a port of the Nanobot chat bot. It must not name the private product.

Size: about 146 new lines, 3 changed lines. One sub-ticket.

## Tests to change

none. `grep -rn 'north-star\|Where things live\|standards.md' tests/factory` matches nothing.

