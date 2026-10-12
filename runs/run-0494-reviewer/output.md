## Review of T-0047.4 (Move the human decisions to factory/human.py, leaving factory/cli.py under 900 lines)

Commit: 9349e5762e727e570bf0bd0e7ceb90c865387a71 (base 43265a02f3ad943ebed963d7246495418c3d2ee8, one commit)

### What I checked, in the role's order

1. **Test integrity.** The diff touches only `factory/cli.py` and `factory/human.py` (`git diff --stat 43265a0..HEAD`: 2 files, +327/-319). Nothing under `tests/` changed. No test patches a name that moved: `grep -rnE 'cli\.(_by|_approval_dir|_next_n|_copy_record|_supersede|_set_aside_failed_rows|_restart_note|_refuse_unless_applies|approve_spec|request_changes|resolve|decision_add|spec_amend|getpass|shutil|difflib)\b' tests` prints nothing, so no patch point moved out of reach.

2. **Correctness.** The 13 definitions the sub-ticket names are in `factory/human.py` in their `factory/cli.py` order (`_restart_note`, `spec_amend` from the spec/plan section first; `_by` through `decision_add` from the human-surface section after). The moved text is byte-identical: I ran the parent's moved-text script (copied verbatim from the spec block into my scratch directory) on this head and it printed `pairs=4 added=0 removed=0 lines=54` with nothing after it, which means no top-level definition changed text across the three earlier merges and this branch, and the whole split has added 54 lines of its 100-line budget. `uv run --frozen python -B -c 'import factory.human'` in a fresh HOME exits 0 and prints nothing. `uvx ruff check --select F factory` prints `All checks passed!`, so no moved body lost an import and `factory/cli.py` keeps no unused one. `factory/cli.py` is 882 lines (`wc -l`), below 900. `build_parser` reaches every moved command through the new import (`factory/cli.py:23`; `set_defaults(fn=...)` at lines 734, 800, 804, 815, 820). No moved helper is still referenced from `factory/cli.py`, `factory/drive.py`, `factory/stats.py` or `factory/__main__.py` (grep prints nothing).

3. **Scope.** Only part E. No rename, no body edit, no doc or test change. The `# ----- human surface (K-lite)` comment was dropped; its section in `factory/cli.py` is now empty, and the three earlier sub-tickets took the same choice (no `# -----` comment exists in `drift.py`, `common.py`, `setup.py` or `gates.py`), so the five modules are consistent.

4. **Silent behaviour changes.** None. `factory.human` imports `factory.gates` and `factory.common`, never `factory.cli`, so no import cycle; `factory/cli.py` imports `factory.human` at module load exactly as it does the other four modules.

5. **Security and data safety.** A pure move; no new I/O, no new paths.

6. **Protected paths.** `factory/cli.py` and `factory/human.py` are touched; both are declared by the sub-ticket and by the parent spec's Risk section. Listed under ESCALATIONS for the record.

7. **Coding standard.** No new helper, type or dependency: the only new lines are the module docstring and twelve import lines. Lean already.

8. **PR description.** What changed says in words what moved and why the one deviation from the sub-ticket text was made; "human decisions" is glossed on first use. Known gaps is honest about the `fence` import, the unwrapped move script and the slow suite. `factory:` markers: none added, none needed.

### Findings

None.

Note, not a finding: the sub-ticket's scope line says `factory/human.py` imports `fence` from `factory.common`. No moved body calls that function; `spec_amend` binds a local string also named `fence` (`factory/human.py:86-88`). Importing it would be an unused import and fail R3 and R11, so the implementer rightly followed the design's governing rule, "the imports its definitions use" (design, Proposed change). The sub-ticket text, not the code, is wrong here; the acceptance name list does not mention `fence`, so nothing in acceptance is affected.

### Prior findings

None (round 1).

### Out-of-scope observations

- The `# ----- spec store (doc §Harness, Spec store; part K)` comment at `factory/cli.py:592` now heads only `stats_cmd`, which Decision 4 keeps in `factory/cli.py`. Already noted by the implementer; a one-line comment fix for a later ticket, not this one.
- `factory/cli.py`'s docstring still reads "P0 subset of the build-harness spec, part B/K", which the parent spec's Root cause section calls out and leaves alone.

STATUS: APPROVE
CONFIDENCE: high. The moved-text script, ruff F, a fresh-interpreter import and the line count were each run on head 9349e57 and printed the expected result; the diff is a verbatim cut-and-paste with only import-line changes around it.
ESCALATIONS: protected paths touched, both declared by the sub-ticket and the approved spec's Risk section: `factory/cli.py`, `factory/human.py`
