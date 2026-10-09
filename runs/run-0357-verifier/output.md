Commit: 2f3fcef2f7a433585b85e99aedf9302133c01002 (branch `factory/T-0037.1`, base `51e2af7f1737f5fc4d9780ea725710dc1112702f`)

How this was run: the PR head was the run worktree `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0357-verifier/wt`, which had a clean status and HEAD at `2f3fcef`. The base was a detached worktree at `51e2af7` under this run's scratch directory, removed after use. Both got `uv sync --frozen`. Every command ran inside the throwaway-HOME wrapper and under bash. The role-input scenarios need a GIVEN fixture. I wrote it from the current-truth spec, `.factory/store/openspec/specs/role-inputs/spec.md:13-47`, into `TMPDIR=<scratch>/tmp`, the same TMPDIR for base and PR. Both suite runs used the default macOS TMPDIR (`/var/folders/...`), which is outside every instance, as the suite scenario requires.

Per criterion:
- NEW | "With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does" | base: `W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1` / `C: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1` / `P: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 source=1`, which is the failure verification.md states | PR: `W: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1`, then the same with `C:` and `P:`. This is the THEN exactly | PASS
- REGRESSION | "The capabilities each role receives and triage's input are unchanged by the whole log" | base: the same four lines as the PR | PR: `W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1` / `C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1` / `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0` / `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0`. This is the THEN exactly | PASS
- REGRESSION | "The harness suite passes with the whole decision log" | base: not run | PR: `suite=0` | PASS
- NEW | "The design, README and changelog describe the whole decision log and no decision index" | base: `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`, which is the failure verification.md states | PR: `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`, then `whitespace=ok`. This is the THEN exactly | PASS

Gate suite: PASS
  `git diff --check main...HEAD` exited 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory` exited 0 and printed `382 passed in 279.92s (0:04:39)`. The PR description explains the change from the base's 384: the PR removes four tests and adds one test with two parameter cases, which matches the diff.

Probes. For each probe I edited a copy of the fixture so that it installs a chosen `decisions.md`, or none, before any role input is composed. The probes ran on the PR head.
- A 3,005-line log, with `Capabilities: beta`. The log holds a line with no date or ticket id, an indented line, a line whose only capability-like word is the substring "betamax", and 3,000 bulk lines from other tickets. → Each of W, C and P holds the whole-log heading followed by the file's text verbatim (checked as a substring with Python). All 3,000 bulk lines are present, there is no decision index, and `decisions.md` is in each run's `input_sources`. Each input is about 138 kB. → OK
- The same log with no `Capabilities:` line, and with `Capabilities: none`. → The output is identical to the beta case: the whole log verbatim, with no index, in all three roles. → OK
- A log holding only whitespace, and a missing `decisions.md`. → No `## Decision log` heading, no decision index and no `decisions.md` source in W, C or P. The empty-log behaviour is unchanged. → OK
- Leftovers. `git grep -i 'decision index'` outside `docs/changelog.md` finds only the new tests' "not in" assertions and an old answer record under `.factory/answers/`, which is a closed record. `git diff --stat` shows that no `docs/prompts/` file changed. `uvx ruff check` on `factory/compose.py` and the test file finds the same six findings on base and PR, so the change adds no lint finding. → OK

Protected paths: the PR changes `factory/compose.py` (harness), which the spec's Risk section declares. It changes no other protected path.

STATUS: VERIFIED
CONFIDENCE: high, because each acceptance command printed its THEN exactly on `2f3fcef`, both NEW commands printed the stated failure on `51e2af7`, both gates passed, and the probes showed the whole log passes through verbatim whatever the Capabilities line says.
ESCALATIONS: none
