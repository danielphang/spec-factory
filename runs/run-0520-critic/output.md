## Critic review, round 2 (spec v2 for issue #108)

Reviewed per the convergence rule: whether the round-1 findings were resolved, and the text the v1→v2 diff changed (Evidence bullet 1, Decisions bullet 5, Risk paragraph 2, Operator steps, design part C's test paragraph, design D.3, verification.md's opening line and the new Responses section). Unchanged text was not re-reviewed.

What I checked myself, from `~/dev/spec-factory` at `525d73f` (`git rev-parse --short HEAD`; the diff claims the base is unchanged since v1, and the `main` HEAD confirms it):

- Changed text against the repo. Design part C names `git_repo`, `cli` and `js` in `tests/factory/_cli.py`: they are defined at lines 60, 23 and 43, and the file's docstring (lines 1-5) says "A test file imports them from here, never from another test file", as the spec states. The `target` fixture it refers to is `tests/factory/test_instance.py:31-38`: four lines, `git_repo` then `cli(..., "init", "--repo-name", "demo")`. D.3 cites README line 9 ("Current state as of 2026-10-13") and "Maintaining this page": line 1069 says a change to a command "bumps the date in the status header". Both hold. `factory/setup.py:180-184` is still the copy loop with the single `if not exists` branch, and `out({...})` with `agents` is at 203-204.
- Operator steps' new check, run as written, read only: the `cmp` loop over the six templates against `~/dev/nanobot-upstream/.claude/agents/` printed `same` six times, as the Responses section says it does today. It is a read-only command on the protected path, so the v1 problem (running `factory init` in the live Nanobot target) is gone.
- Acceptance commands run as written under the running-code wrapper (neither runs the suite): the frontmatter scenario printed `keys=ok` for clerk and stub and `keys=unparsed` for planner, spec-critic, spec-writer and triage; the README scenario printed `row=0 step=0 missing=1`. Both match verification.md's "today" results.
- Glosses in the human-facing sections, read as the gate operator: Evidence bullet 1 now explains the wrapper; Decisions bullet 5 now explains the store and `FACTORY_STATE`; Risk paragraph 2 now explains the runtime checkout and `--accept-harness`; Operator steps now opens with both the runtime-checkout gloss and the Driver gloss before using either. No new term of art is introduced without a gloss in the changed text.
- Approved changes not yet archived: none, so no scenario has a merge-order dependency.
- Not checked, as in round 1: the suite-fails scenario and the prototype's `590 passed` (both need a suite run); Claude Code's own frontmatter parser (the spec says so itself).

Findings

[NIT] 6 design.md, part C, test paragraph
Problem: "add no new setup code" and "do not import that fixture" read together could make an implementer think a local fixture is forbidden, when the only way to build the target without importing from `test_instance.py` is a local fixture of the same four lines calling `git_repo` and `cli`.
Evidence: `tests/factory/test_instance.py:31-38` is the fixture; `_cli.py` lines 1-5 forbid importing it from another test file; `_cli.py` has no fixture of its own that returns an initialised target.
Suggested fix: Say "build the target with the shared helpers (`git_repo`, `cli`, `js` from `tests/factory/_cli.py`), in a fixture local to the new file, the way `test_instance.py`'s `target` fixture does", and drop "add no new setup code".

Prior findings
- [BLOCKING] 6, Operator steps unglossed "the Driver" and "the runtime upgrade": RESOLVED. The step opens with both glosses; Risk uses the same gloss; the check is now read only.
- [SHOULD-FIX] 6, "fresh-HOME wrapper", "instance's own store", "throwaway store" unglossed: RESOLVED. Evidence bullet 1, Decisions bullet 5 and verification.md's opening line carry the glosses.
- [NIT] 3, part D omits the README status-header date bump: RESOLVED. D.3 names line 9 and the merge date, and notes no line-count change.
- Out-of-scope observation, new init tests overlap `test_instance.py`: addressed in design part C with the shared helpers, without touching the existing test, which keeps "Tests to change: none" true.

Out-of-scope observations
- none new.

STATUS: APPROVE
CONFIDENCE: high; every round-1 finding is fixed in the text with the gloss the finding asked for, every path and line the changed text cites exists at `525d73f`, and the two acceptance commands and the operator check I ran print what the spec says they print today.
ESCALATIONS: none
