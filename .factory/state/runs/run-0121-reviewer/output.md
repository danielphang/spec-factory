Commit: c64183ac7d10f6286136a0b419764d05202736fc (branch `factory/T-0014.1`, forks from `main` at `ba4618a`; `431e349` on `main` is not an ancestor, so the merge-base diff is the one that counts)

## What I checked, in the role's order

1. Test integrity. `git diff --name-only ba4618a..HEAD` prints `docs/writing.md` only. No test file, CI config, AGENTS.md, skill or prompt is touched. Nothing to block on.
2. Correctness against the spec. All seven acceptance commands re-run in the review worktree and gave the THEN outputs:
   - 1: `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4`
   - 2: `9:111 10:111 11:111 12:111 `
   - 3: `writing=yyyyyy readme=nyyyny`
   - 4: `intro=0 rules=111011101111 misplaced=0`
   - 5: `lines=131 wide=0 removed=0 ws=clean` (131 is below 140 and equals the spec's scratch build)
   - 6: `changed=[docs/writing.md]`
   - 7: covered by the full gate run below, which includes `tests/factory/test_writing_standard.py`
   Intermediate check (wording). I extracted parts A, B (the six table cells, backticks stripped) and C from the pinned design.md in my input (44 lines) and the 45 added lines from `git diff ba4618a..HEAD -- docs/writing.md`. Line by line, the only difference is one trailing blank line after rule 12 (`diff` output: `44a45 > `), which design.md requires ("a blank line after each rule"). Joined and whitespace-normalised, `diff` prints nothing (exit 0). The inserted text matches design.md word for word; the implementer did not rewrap, so even the line breaks match.
   Placement. Part A sits directly after "example taken from the factory's own writing, and its rewrite." as a continuation of that paragraph (diff hunk at old line 19). Part B lines sit after each rule's Check text and before its `Before (` line on rules 1, 2, 3, 5, 6, 7 only (criterion 4 confirms `misplaced=0`). Part C sits after rule 8's After paragraph and before the closing `README.md` line.
3. Scope. Only `docs/writing.md`; additions only (`removed=0` against `e703c1b`). Nothing outside parts A, B, C.
4. Silent behavior changes. None. The file is read by roles from the runtime checkout, which this merge does not move; the spec's Operator steps own that.
5. Security and data safety. Not applicable; a prose file.
6. Protected paths. None touched. `docs/writing.md` is not under `.factory/`, `factory/`, `bin/factory`, `agents/`, `pyproject.toml`, `uv.lock`, `docs/prompts/`, the reference harness or credentials.
7. Maintainability. Nothing to raise.
8. PR description. What changed says in words what was added and where, glosses "writing standard" and "role" at first use, and records the wording check with its method. Known gaps names the untested-first point and the main-moved point honestly and explains why each is harmless. The base it names (`ba4618a`) is the branch's real fork point; the harness header's `431e349` is `main`'s tip, and the implementer's note on this is correct. Readable at the gate as written.

Gate commands, run from the review worktree exactly as written:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `126 passed in 116.64s (0:01:56)`.

## Findings

none

## Prior findings

none (round 1)

## Out-of-scope observations

- The harness header for this run names base `431e3492…`, which is `main`'s tip, not the branch's fork point `ba4618a`. A two-dot diff from `431e349` shows a spurious one-line deletion in `dev/issues.md`; the three-dot diff the harness actually included, and criterion 6's merge-base diff, do not. Worth knowing for anyone reading the raw header; it is not a defect in this ticket.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance command and both gates were re-run in the review worktree and gave the expected output, and the inserted text was compared with design.md and matched exactly.
ESCALATIONS: none
