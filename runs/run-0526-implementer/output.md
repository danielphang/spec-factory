Sub-ticket: T-0053.1 (parent T-0053, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0053/v2.md`)
Branch: `factory/T-0053.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0053.1`, one commit `21f90c4` on base `525d73f`. `main` was still at `525d73f` when I branched, so the changelog's next free number was 73.

## What changed

The operator's writing and design standards now sit in one self-contained file, `docs/standards.md`. No prompt names it, so no role (one of the factory's agents, each run from a fixed prompt) behaves differently. Four files changed: 147 lines added, 2 changed.

- **A.** New `docs/standards.md`, 146 lines. I made it with `sed -n '29,174p' .factory/store/requests/T-0053.md`, so it is a byte-for-byte copy and was not retyped. It starts at `# Writing and design standards` and ends at `  (commit, run id, ticket), then what was not done.` plus one newline. `sed 1d docs/standards.md | LC_ALL=C shasum -a 256` prints `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`, which is the hash the spec requires.
- **B.** `README.md`: in "Where things live", I replaced the `docs/writing.md` row (line 1027) with the spec's suggested one-line row, which names both `docs/writing.md` and `docs/standards.md`. README is still 1,106 lines. The status header already said "as of 2026-10-13", today's date, so I left it alone.
- **C.** `docs/north-star.md` line 21 now reads exactly `The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).` No other line changed.
- **D.** `docs/changelog.md`: I added entry 73, which starts `73. After issue #110 (2026-10-13), `. It sits after entry 72 and before the closing "Declined:" paragraph, with a blank line on each side. It says:
  - the standards were spread over four places;
  - `docs/standards.md` now holds them in one self-contained file;
  - no prompt, `docs/prompts/` file or `docs/writing.md` names the new file, so no role's behaviour changes;
  - README's `docs/writing.md` row now names it;
  - the north-star sentence calls the target a port of the Nanobot chat bot;
  - two options were rejected: editing `docs/writing.md` (that would be a prompt change) and adding a new README row (it would not fit the line budget).

  `git diff | grep '^+' | grep -i lionbot` matches nothing, so no added line names the private product.

## Acceptance results

I ran every command from the worktree through the running-code wrapper. "Before" is base `525d73f`; "after" is commit `21f90c4`.

| Scenario | Kind | Before | After | What "after" shows |
|---|---|---|---|---|
| The standards file holds the approved text | NEW | `title=0 body=e3b0c442…b855` | `title=1 body=010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e` | The file has a `# ` title, and the text after it matches the approved hash. |
| Where things live names the standards file | NEW | `row=0` | `row=1` | Exactly one row in the table names the file. |
| Nothing a role reads names the standards file | REGRESSION | `readers=0` | `readers=0` | No prompt, `docs/writing.md`, `factory/` or `agents/` file names it. |
| The north-star sentence names a port of the Nanobot chat bot | NEW | `line=0 serves=1` | `line=1 serves=1` | The sentence now has the new wording, and it is still the only "serves" sentence. |
| The changelog records issue 110 in one entry without a numbering gap | NEW | `entries=0 terms=0`, `CONTIGUOUS` | `entries=1 terms=3`, `CONTIGUOUS` | One entry names all three files, and the numbering still has no gap. |
| README is at most 1,110 lines (current truth) | re-run | `readme=within` (per the spec) | `readme=within` | README is still 1,106 lines. |
| The maintained documents pass git's whitespace check in full (current truth) | re-run | `exit=0` (per the spec) | `exit=0` | This covers the new file, because the check reads all of `docs/`. |

All four NEW scenarios printed the spec's "today" output before the change, so the spec matched the code.

Gate commands, each run exactly as written:
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `584 passed in 141.51s (0:02:21)`, exit 0.

## Tests added/changed

None. This is a documentation-only change, and the spec's acceptance checks are shell scenarios. The spec lists no tests to change, and `grep -rn 'north-star\|Where things live\|standards.md' tests/factory` finds nothing there.

## Known gaps and uncertainties

- The changelog wording is mine, not the operator's. It makes three claims about the rest of the repo, and I checked only the first:
  - The golden set (the fixed tickets in `docs/golden.md` that every prompt change is replayed on) has no baseline yet. I took this from the spec's Problem section. README's `docs/golden.md` row describes the file that way, but I did not open `docs/golden.md` to confirm the baseline table is empty.
  - Every role prompt names `docs/writing.md`. I took this from the spec. The preamble of my own system prompt does name it.
  - Rule 4 ("stating" for "that states") and the other small differences between the appendix's section 2 and `docs/writing.md` are kept as the operator wrote them. The spec puts this out of scope.
- Part D's order rule: if T-0052 or issue #109 merges into `main` before this branch and takes number 73, this entry must become 74 when the branch is merged with `main`. The numbering scenario would catch a duplicate 73.

## Out-of-scope observations

The private product's name still appears in other tracked public files. The spec lists them: `docs/golden.md`, `tests/factory/test_decision_log.py`, and the frozen `dev/build-harness.spec.md` and `dev/build-harness.plan.md`. Issue #111 owns that cleanup. I did not touch them.

## Protected paths

None touched. The diff changes only `README.md`, `docs/standards.md` (new), `docs/north-star.md` and `docs/changelog.md`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every scenario and both gates ran on commit `21f90c4` and gave the spec's expected output, and the standards text matches the approved SHA-256.
ESCALATIONS: none
