Commit: a86d154a75c6545d91f87cc79a007d2fe16e5df3 (branch `factory/T-0039.1`, base b002c95b18b3cd1dad4329cdc4e13b6fe71b18af)

How I ran it: the PR was checked in the given worktree `wt/` (where `main` = b002c95). The base was checked in a fresh clone under `scratch/base`, with `main` and HEAD both set to b002c95. I ran `uv sync --frozen` in each first. I copied the six WHEN commands verbatim from `.factory/store/specs/T-0039/v2.md` into `scratch/cmds/c1..c6.sh`. I copied the GIVEN fixture from `.factory/store/openspec/specs/role-escalations/spec.md` into `scratch/cmds/given.sh` and ran it once per checkout before scenario 3. Every command ran under `bash`, inside the fresh-HOME wrapper, with `TMPDIR` set to a directory under `scratch/tmp/`. Logs are in `scratch/acc-pr.txt`, `scratch/acc-base.txt` and `scratch/suite.txt`. `git status --short` was empty in `wt/` after every run.

Per criterion:
- NEW | The five role prompts carry the critic's reading paragraph in every copy | base: each of the five lines printed `<role> copy=SAME doc=0 run=0 writes=0 fill=unchanged` (the failure the spec predicts) | PR: `triage copy=SAME doc=1 run=1 writes=0 fill=unchanged`, then the same for planner, implementer, reviewer and verifier | PASS
- REGRESSION | Only the paragraph is added, and no other prompt changes | base: not run | PR: `extra=0 deleted=0 others=0` | PASS
- NEW | Implementer, reviewer and verifier runs receive the reading paragraph | base: `implementer preamble=1 economy=0 writes=0`, and the same for reviewer and verifier | PR: `implementer preamble=1 economy=1 writes=0`, `reviewer preamble=1 economy=1 writes=0`, `verifier preamble=1 economy=1 writes=0` | PASS
- NEW | Triage and planner runs receive the reading paragraph | base: `triage preamble=1 economy=0 writes=0`, `planner preamble=1 economy=0 writes=0` | PR: `triage preamble=1 economy=1 writes=0`, `planner preamble=1 economy=1 writes=0` | PASS
- NEW | The changelog records the reading rules for the five roles as its last entry | base: `63 CONTIGUOUS`, `terms=2 footer=1` | PR: `64 CONTIGUOUS`, `terms=7 footer=1` | PASS
- REGRESSION | The reading-rules change adds no whitespace errors | base: not run | PR: `exit=0` | PASS

Each NEW criterion failed on base for the reason verification.md gives, and its base output matches the predicted output exactly.

Gate suite: PASS
  `(export HOME=...; git diff --check main...HEAD)`: no output, rc=0.
  `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `418 passed in 288.85s (0:04:48)`, rc=0.

Probes:
- Is the added text really the critic's? I joined `factory/prompts/critic.md` into one line and searched it for the spec's paragraph → `critic=1`. The five roles carry the critic's sentence word for word. The prompt shows no rewording → OK.
- Does the declared-path rule stay last? I listed the `- ` bullets under RULES in the implementer and verifier run copies, and under WHAT YOU RUN in the reviewer. In the implementer and verifier, Turn economy comes directly before the declared-path bullet, and that bullet is still last. In the reviewer, Turn economy is the last bullet of WHAT YOU RUN. This matches design parts A and B → OK.
- Does the new test catch drift? In a throwaway clone of the PR head, I made two mutations. I moved the verifier run-copy bullet to after the declared-path bullet. I changed one word in `docs/prompts/06-code-reviewer.md`, so it no longer matches the design block. I then ran `tests/factory/test_turn_economy.py` → `2 failed, 8 passed`. The placement tests for the reviewer and the verifier failed. The verifier's run-prompt test still passed, as expected: it checks only that the paragraph is present, and placement is the other test's job. The test checks the property, not just the tested inputs → OK.
- Does the result depend on the shell? I ran the "Only the paragraph is added" command under `zsh`, this machine's login shell, instead of `bash`. It printed `extra=0 deleted=0 others=538`. zsh does not split the unquoted `$F` into words, so the `grep -vxF` exclusion breaks. Under `bash` it prints the expected `extra=0 deleted=0 others=0`. Nothing in this change causes this. The command assumes a POSIX shell, which the spec does not say → CONCERN (in the spec's command, not the PR; see ESCALATIONS).

Protected paths the sub-ticket declares, all changed as design parts A to C describe: `factory/prompts/{implementer,verifier,reviewer,planner,triage}.md` and `docs/prompts/{05-implementer,07-verifier,06-code-reviewer,04-planner,01-triage}.md`. The diff touches no undeclared protected path. The other changed files are `docs/design.md`, `docs/changelog.md` and the new `tests/factory/test_turn_economy.py`.

STATUS: VERIFIED
CONFIDENCE: high, because every acceptance command matched its predicted base and PR output exactly, both gates passed on a86d154, and the mutation probe shows the new test tracks the property rather than fixed inputs.
ESCALATIONS:
- The acceptance commands in spec v2 assume a POSIX shell, but the spec does not say so. Run under zsh, this machine's default shell, the "Only the paragraph is added" command prints `others=538` instead of `others=0`, because zsh does not word-split the unquoted `$F`. Under bash it passes. It is a false failure, not a false pass, but a verifier or operator who pastes the command into zsh will see a failure the change did not cause. A possible fix, for a later ticket: state "run under bash" in the spec template's command preamble.
