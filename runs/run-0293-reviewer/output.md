Commit: 090939d6428bff085890aa5d1b9d384bb8915c78 (branch `factory/T-0029.1`, base `7d57998169bf08563fe33fcd098729fae200c4b9`, which is also `main` in the worktree)

Per the human ruling on this piece, I did not run the test suite or the gate commands. The verifier passed both on this head (run-0287, 310 passed). I ran narrow foreground checks only.

## What I checked

1. Test integrity. `git diff --name-only 7d57998...HEAD` touching `tests/`, `README.md`, `dev/`, `agents/`, `bin/`, `.factory/`, `pyproject.toml`, `uv.lock`: 0 files. The diff is 6 files, 37 insertions, 0 deletions (`git diff --stat`). No test changed, weakened or added. "Tests to change: none" holds.

2. Correctness. The inserted bullet is byte-identical to the spec's block in all six places: the md5 of the six grep'd lines in `factory/prompts/implementer.md`, `factory/prompts/verifier.md`, `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md` and both occurrences in `docs/design.md` is `a0da41faa63de4be39e6f22f1866c4f6`, the same as the md5 of the spec's text typed from the design. Each run prompt carries it once and it is the last RULES bullet: the line after it is blank, then `PR DESCRIPTION` (implementer, `factory/prompts/implementer.md:49`) or `OUTPUT` (verifier, `factory/prompts/verifier.md:39`). No other prompt file carries the string (`grep -c` over `factory/prompts/*.md` and `docs/prompts/*.md`: 0 everywhere else). The document scenario, run as written: `implementer copy=SAME rule=1 fill=unchanged`, `verifier copy=SAME rule=1 fill=unchanged`. Reviewer and preamble copies: `changed=0`. Changelog: `CONTIGUOUS`, then `1`; entry 55 (`docs/changelog.md:61`) opens "After issue #49 (2026-10-04)", gives 10 runs and 30 of 205, states the five points design B lists, names check 6 as unchanged, rejects the retro's 26 of 139, and sits before the "Declined:" line. `git diff --check main...HEAD`: `exit=0`. I did not re-run the composed-prompt scenario (it starts runs via `bin/factory`); the verifier covered it and the text it greps is confirmed present in both run prompt files.

3. Scope. Only parts A and B. Nothing in the reviewer prompt, preamble, code, README or `dev/`.

4. Silent behaviour changes. None beyond the intended one: implementer and verifier runs that start after the runtime accepts this revision see one more rule. No routing or merge logic is touched.

5. Security and data safety. Prose only. Nothing.

6. Protected paths. Touched exactly as the sub-ticket declares; listed under ESCALATIONS below.

7. Coding standard. No code. Lean already.

8. PR description. What changed glosses protected path, declared path, ESCALATIONS and head at first use and says in words what changed. Known gaps are honest about what the checks cannot prove and about the TMPDIR condition. Readable by the operator at the gate.

## Findings

None.

## Prior findings

Not applicable: round 1 (two earlier reviewer runs on this head returned no review).

## Out-of-scope observations

- The spec's own note stands: check 6 in the reviewer prompt says "the merge gate will require a human approval", which the local merge does not read. Separate ticket, as the sub-ticket says.

STATUS: APPROVE
CONFIDENCE: high. The change is 37 added prose lines; I confirmed the bullet text byte-for-byte in all six places, the copy-equality, changelog, reviewer-unchanged and whitespace scenarios from the worktree, and no test or code file is touched.
ESCALATIONS:
- Protected paths touched, every one declared by the sub-ticket and the spec's Risk section: harness `factory/prompts/implementer.md`, `factory/prompts/verifier.md`; generated `docs/prompts/05-implementer.md`, `docs/prompts/07-verifier.md`; guardrail (agent prompts) the same four files plus the "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md`. Each change is the one six-line bullet the spec dictates; nothing else in those files moved.
