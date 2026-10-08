## Proposed change

The four prompt files get added lines only. Each design doc block stays byte-identical to its `docs/prompts/` copy. Each run copy under `factory/prompts/` keeps the differences it has today from its documented copy: `400` and `2` filled in, and the writer's extra "Acceptance items describe behaviour" bullet.

**A. Spec writer: a turn-economy rule** (`docs/design.md` "## 2. Spec writer" block, `docs/prompts/02-spec-writer.md`, `factory/prompts/spec_writer.md`). Insert these seven lines directly after the line `  wrong just to get approved.` (the end of the "On revision" bullet; `docs/design.md:371`, line 58 of both other files). In the run copy they therefore come before the blank line and the "Acceptance items describe behaviour" bullet.

```
- Turn economy: every turn re-sends everything read so far, so a
  wasted turn or a long printout costs again on every later turn. Put
  independent reads and commands in one turn. Once grep has found the
  lines you need, read that line range, not the whole file. Send long
  output, such as a suite run or a scenario's output, to a file in your
  scratch directory and grep or tail it, rather than printing it in
  full. Write the spec in as few writes as you can, ideally one.
```

**B. Critic: a cap, no suites, no builds, and the same reading rules** (`docs/design.md` "## 3. Spec critic" block, `docs/prompts/03-spec-critic.md`, `factory/prompts/critic.md`). Keep the line `Spot-check at least 2 cited paths and 1 acceptance command yourself.` (`docs/design.md:461`, line 42 of both other files). Insert these twelve lines directly after it, before the blank line that precedes `ANTI-GOODHARTING (REVIEWER SIDE)`.

```
Ground any one claim with at most 2 paths and 1 command. Run no test
suite and build nothing: no clone, worktree or prototype of the change.
Pick an acceptance command that runs no test suite, and run it as the
spec gives it. A claim you could settle only by running a test suite or
building the change is a finding for the writer, or a question; say
what you could not check.
Turn economy: every turn re-sends everything read so far, so a wasted
turn or a long printout costs again on every later turn. Put
independent reads and commands in one turn. Once grep has found the
lines you need, read that line range, not the whole file. Send long
output to a file in your scratch directory and grep or tail it, rather
than printing it in full.
```

**C. Nothing else in the prompts.** No other line of the four files changes. The RUBRIC, CONVERGENCE (with its round limit) and OUTPUT sections of the critic, and the ROLE, INPUT, PROCESS and FORMAT sections of the writer, stay byte for byte. No other file under `docs/prompts/`, `factory/prompts/` or `agents/` changes.

**D. Documents.**
1. `docs/changelog.md`: one new numbered entry after the last one, before the closing `Declined:` line, continuing the numbering without a gap. The last entry on `main` today is 57, so the new entry is 58. Write it on one line, as every existing entry is. It must contain the phrases `#73`, `line range`, `scratch directory`, `no test suite` and `two paths and one command`. This text, used in the prototype, does:
   > 58. After issue #73 (2026-10-07), where the spec writer took a third of all workflow context tokens (309M of 866M; a median of 29 agent calls and 5.3M tokens per run), because every call re-sends the start-up context and everything read so far, and where the critic ran the test suite and built prototype clones of the change on its own initiative, though its grounding is meant to stay within two paths and one command per claim. The spec writer prompt gains a RULES bullet, Turn economy: put independent reads and commands in one turn, read a line range once grep has found it, send long output to a file in the run's scratch directory and grep or tail it, and write the spec in as few writes as possible. The critic's PROCESS keeps its minimum spot-check and caps any one claim at two paths and one command; it runs no test suite and builds nothing, and a claim it could settle only by building becomes a finding for the writer or a question. It gains the same reading rules. No rubric item, round limit or required spec section changes, and the shared preamble does not change. Rejected: a shared preamble line, which would reach every role.
2. `docs/principles.md`, principle 2:
   - The "Implemented by" sentence (lines 41–44) ends `` (#41, `factory/prompts/reviewer.md`, `factory/compose.py`). ``. Change that ending to `` (#41, `factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test suite and builds nothing (#73, `factory/prompts/critic.md`). ``.
   - Replace the status line (lines 45–46) with: `Status of #72 part B.2 (reader roles run no suites): done by #41 for the code reviewer and by #73 for the critic. The code reviewer is the only reader role that was given gate commands; the critic and triage never were, but the critic ran suites on its own initiative until #73.`
   - Wrap at the file's existing width (about 100 columns).

## Tests to change

none. No test pins the critic's PROCESS line or the absence of these rules. The tests that keep each design block equal to its `docs/prompts/` copy keep passing when parts A and B edit all three copies alike (prototype: `364 passed`).

