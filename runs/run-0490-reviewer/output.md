Commit: c30b80f45a39824b71c7064cc22e2563a53f9438

## Review of T-0047.3 (part D: move the gates to `factory/gates.py`, name it in the README and the principles)

Round 1. I read the full diff and confirmed the points below with narrow commands in the worktree
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0490-reviewer/wt` at head `c30b80f`.

### 1. Test integrity
No file under `tests/` changed: `git diff --name-only 57b46e1..HEAD -- tests | wc -l` printed `0`.
Nothing to flag.

### 2. Correctness
- Pure move. I parsed the base `factory/cli.py` and the head's `factory/cli.py` plus
  `factory/gates.py` with `ast` and compared every top-level function, class and assignment by its
  exact source text: `added 0 removed 0`. No moved body was retyped or edited.
- Order kept. `grep -nE '^(def |[A-Z_]+ =)' factory/gates.py` lists the 18 definitions in the order
  the sub-ticket and the parent's part D give: `ticket_head` … `ticket_parent_check`, then
  `_verifier_rows` … `archive_cmd`.
- The seven commands stay wired into the parser: `p.set_defaults(fn=...)` for `ticket_head` (cli.py:1006),
  `ticket_join` (1009), `ticket_parent_check` (1012), `results_record` (1081), `results_show` (1084),
  `merge_cmd` (1087), `archive_cmd` (1110).
- `factory/cli.py` still uses `_parent_close_verified` (161), `_branch_tip` (829) and
  `undeclared_protected` (830), and imports exactly those three helpers plus the seven commands.
  The only lines added to `factory/cli.py` are the two-line `from factory.gates import (...)`
  (cli.py:24-25); every other change in that file is a deletion.
- `factory/gates.py` does not import `factory.cli` (grep found no match), so Decision 12 and the
  import-cycle risk in the parent's Risk section hold. Every name it imports (`re`, `Path`,
  `gitops`, `specstore`, `status`, `store`, `subtickets`, `out`, `Refused`) is used in a moved body.
- Docs: `README.md:9` reads `Current state as of 2026-10-12`; `README.md:1171` names
  `factory/gates.py` for `ticket_join`, `merge_cmd`, `archive_cmd`; `docs/principles.md:106-109` has
  the new sentence, lines of 99, 93, 96 and 6 columns, with "`factory/gates.py` (`merge`)" on one
  line. Matches the sub-ticket's text.

### 3. Scope
The two imports the sub-ticket does not list, `_branch_tip` and `undeclared_protected`, are
required: `resolve` (cli.py:829-830) calls both and stays in `factory/cli.py` until part E. Without
them the module fails F821 and `resolve --accept-paths` raises `NameError`. This is the sub-ticket's
listing being incomplete, not a scope expansion; the PR description's Known gaps says so and names
the follow-up (T-0047.4 drops them when `resolve` moves, caught by R11 if not). Accepted.

No other file changed. `README.md` and `docs/principles.md` edits are limited to the three
locations the sub-ticket names.

### 4. Silent behaviour changes
None. No body changed (ast comparison above), parser wiring is intact, and the import of `Refused`
and `out` in `gates.py` resolves to the same objects `cli.py` used.

### 5. Security and data safety
Nothing new: no new I/O, no new paths, no credentials touched.

### 6. Protected paths
`factory/cli.py` and `factory/gates.py` are touched. Both are declared by the sub-ticket's
"Protected paths" line and by the parent spec v2's Risk section. Listed under ESCALATIONS for the
record only.

### 7. Coding standard
Lean already. The change adds a one-line docstring, `from __future__ import annotations` and nine
import lines; nothing to tag. The wrapped import at cli.py:24-25 (103 and 109 columns) sits in a
file where lines over 100 columns are already common (cli.py:49, 85-88, 163, 170, ... on the
unchanged lines), so it is consistent with the file and not a finding.

### 8. PR description
What changed opens by glossing "the gates", says in words what moved and why the two extra imports
exist, and Known gaps names the one uncertainty and its follow-up. Readable at the gate.

Findings:
- [NIT] PR description: Known gaps: the coding standard's rule 3 asks Known gaps to list each
  `factory:` marker added or say "factory: markers added: none"; the section says neither. → The
  operator has to infer from "moved byte for byte" that no marker was added. A one-line addition.

Prior findings: none (round 1).

Out-of-scope observations:
- The section comment at `factory/cli.py` `# ----- build half: sub-tickets, results, merge ...`
  now heads a section with no results or merge code. The implementer noted the same; rewording it
  belongs to T-0047.4 or a later tidy, not here.

STATUS: APPROVE
CONFIDENCE: high. The ast comparison shows no definition changed, the parser wiring and all callers resolve, and no test file changed; the only departure from the sub-ticket's text (two extra imports) is required for `resolve` to run and is disclosed.
ESCALATIONS: protected paths `factory/cli.py` and `factory/gates.py` touched; both are declared in the sub-ticket and in the parent spec v2's Risk section, so the merge gate needs no further approval. Listed for the record.
