Commit: 090939d6428bff085890aa5d1b9d384bb8915c78 (branch `factory/T-0029.1`, base `7d57998169bf08563fe33fcd098729fae200c4b9`; worktree clean, `git merge-base main HEAD` = base)

Setup: every command ran from the worktree root under the HOME wrapper after `uv sync --frozen`, with `TMPDIR` set to this run's scratch directory. The fixture `t0029-prompt.sh` was written there with the spec's block, verbatim. The base was a `git clone` of the worktree into the scratch directory, checked out at `7d57998` with a local `main` at the same SHA, also `uv sync --frozen`.

Per criterion:
- NEW | Implementer and verifier run prompts carry the declared-path rule | base: `implementer declared=0 notunder=0 undeclared=0`, `verifier declared=0 notunder=0 undeclared=0` (fails as the spec states: the rule is absent) | PR: `implementer declared=1 notunder=1 undeclared=1`, `verifier declared=1 notunder=1 undeclared=1` | PASS
- REGRESSION | All three run prompts keep the undeclared-path rule and the reviewer keeps check 6 | base: not run | PR: `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1` | PASS
- NEW | The design blocks and their copies carry the rule and stay in step | base: `implementer copy=SAME rule=0 fill=unchanged`, `verifier copy=SAME rule=0 fill=unchanged` (fails as the spec states: `rule=0`) | PR: `implementer copy=SAME rule=1 fill=unchanged`, `verifier copy=SAME rule=1 fill=unchanged` | PASS
- REGRESSION | The code reviewer and preamble copies do not change | base: not run | PR: `changed=0` | PASS
- NEW | The changelog records the declared-path rule in a contiguous entry | base: `CONTIGUOUS`, `0` (fails as the spec states: no entry names `#49`) | PR: `CONTIGUOUS`, `1` | PASS
- REGRESSION | The declared-path change adds no whitespace errors | base: not run | PR: `exit=0` | PASS
- REGRESSION | Intermediate check: harness suite | base: not run | PR: `310 passed in 242.53s (0:04:02)`, exit 0, nothing skipped or deselected | PASS (this is also gate 2; see below)

Gate suite: PASS
- `(export HOME=...; git diff --check main...HEAD)`: no output, exit 0.
- `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `310 passed in 242.53s (0:04:02)`, exit 0. Run from the worktree with the shell's `TMPDIR` set to this run's scratch directory (outside the repository and the store), not `/tmp`; the suite's result does not depend on that choice as far as this run shows.

Probes:
- Diff shape: `git diff --numstat main...HEAD` → 6 files, 37 insertions, 0 deletions (changelog 1, design.md 12, each of the four prompt files 6). Matches the spec's prototype → OK.
- Bullet text, byte for byte: extracted the six lines starting at the rule in each of the four prompt files and at both places in `docs/design.md` (lines 586 and 700) and `cmp`'d them against the spec's bullet → IDENTICAL in all six places; each file has exactly one occurrence (design.md two). The line after each bullet is blank, then `PR DESCRIPTION` (implementer copies) or `OUTPUT` (verifier copies), so the bullet is the last under RULES → OK.
- Composed reviewer prompt: `prompt reviewer | grep -c 'A protected path the sub-ticket declares is not an escalation'` → `0`, and `not under ESCALATIONS` → 0 occurrences. The rule reaches only the two intended roles; the reviewer's block in design.md still equals `docs/prompts/06-code-reviewer.md` (`copy=SAME`) → OK.
- Changelog entry 55 (`docs/changelog.md:59`): one line, opens `After issue #49 (2026-10-04)`, contains `10 implementer and verifier runs` and `30 of the 205`, followed by a blank line and the `Declined:` line. It also contains `26 of 139`, but only inside its closing "Rejected: the retro's figure of 26 of 139 items" clause, which the spec's Decisions section asks for; the count the entry uses is 10/30 of 205 → OK.

Out-of-scope observations:
- None beyond those the spec and PR already record (check 6's "merge gate" wording; the rule reaches runs only after the runtime upgrade and `--accept-harness`).

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command printed its THEN lines on the head, each NEW command failed on the base for exactly the reason the spec states, both gates exited 0 (310 passed), and the probes show the identical bullet in all five places with no other change.
ESCALATIONS: none
