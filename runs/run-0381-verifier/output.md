Commit: d085ca0b1cd5f084c4065c186c5467d6fd82b9ae (branch `factory/T-0027.2`; base 89290547a33a6091860c850fdda7ff285b409fa0, which is also `main`)

How I ran it: PR head in the given worktree; base as a `git archive` export of 8929054 in this run's scratch directory. Each tree got `uv sync --frozen`. Every command ran inside the fresh-HOME wrapper with `TMPDIR` set to scratch. I extracted the GIVEN block and each WHEN command verbatim from input.md with sed/awk, ran the GIVEN block once per tree (exit 0 on both), and then ran the commands.

Per criterion:
- NEW | "The critic's input lists approved changes not yet archived, other than its own" | base: `listed=0 self=0 decision=0 requirement=0` / `after_archive: heading=0 listed=0` | PR: `listed=1 self=0 decision=1 requirement=1` / `after_archive: heading=1 listed=0` | PASS. Base fails for the reason the spec gives: I ran a diagnostic copy on base, and the critic run starts and composes, but its input.md has no such section (headings stop at `## Acceptance`).
- NEW | "A change sent back to the spec writer leaves the critic's list" | base: `listed=0 self=0 decision=0 requirement=0` / `respec: heading=0 listed=0` | PR: `listed=1 self=0 decision=1 requirement=1` / `respec: heading=1 listed=0` | PASS
- NEW | "A critic run's system prompt carries the cross-ticket rule" | base: `rule=0` | PR: `rule=1` | PASS
- REGRESSION | `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)` | base: not run | PR: `copies=same` | PASS
- REGRESSION (intermediate) | `grep -c 'whichever of the two merges first' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md` | base: not run (it gives 0 in each file, as the PR description says) | PR: `docs/design.md:1`, `docs/prompts/03-spec-critic.md:1`, `factory/prompts/critic.md:1` | PASS
- REGRESSION (intermediate) | harness suite | base: not run | PR: `431 passed in 298.92s` | PASS (this is also the gate run below)
- REGRESSION (intermediate) | `git diff --check main...HEAD` | base: not run | PR: no output, exit 0 | PASS (this is also the gate run below)

Gate suite: PASS
  `(export HOME=...; git diff --check main...HEAD)`: exit 0, no output.
  `(export HOME=...; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `431 passed in 298.92s (0:04:58)`, with no failures or errors.

Scope check: the diff touches five files. In `docs/design.md`, the 4 added lines sit only in the critic block, under rubric item 5 (lines 463-466). The same 4 lines go into `docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md`. `factory/compose.py` gains `add_approved_changes()` (+28 lines), called once, right after `add_decisions()` in the critic branch. There is one new test file, `tests/factory/test_critic_approved_changes.py`, with 10 test functions, one of them run for 4 statuses. No existing test changed. The protected paths it touches are `factory/compose.py`, `factory/prompts/critic.md` and `docs/prompts/03-spec-critic.md`. The sub-ticket declares all three.

Probes:
- The setup is a store with a spec store. Its current truth holds "Greets", archived from T-0001. Four other tickets are approved: T-0002 (MODIFIED Greets, with one Decisions line wrapped onto two lines and one containing backticks and a colon), T-0003 (two ADDED requirements, empty Decisions section), T-0005 (approved, then parked) and T-0006 (the reviewed ticket). `changes/` also holds a folder `T-9999` with no ticket record and a stray file `notes.txt`. → The section lists T-0002, T-0003 and T-0005 in name order, each with its status. T-0002 shows `Changes: demo: MODIFIED Greets`, and its wrapped decision is joined into one line. T-0003 shows `Changes: other: ADDED Alpha; other: ADDED Beta` and `Decisions: none`. `archive`, `T-9999`, `notes.txt` and the reviewed ticket's own folder are skipped. Each listed `proposal.md` appears in the compose `sources`. → OK
- In the same store, `ticket set T-0003 status=closed`, then recompose. → Only T-0002 and T-0005 remain. → OK
- A store without `factory init` has no `openspec/`. → The critic run composes, and its input has no `## Approved changes not yet archived` heading. → OK
- The probes found nothing special-cased to the scenario fixture. The ticket ids, capabilities, operations and states all come from the store.

Out-of-scope observations:
- In probe 1, `approve-spec` approved T-0003 and T-0005 even though both ADD the same requirements, "Alpha" and "Beta", to the same capability. The gate accepts two unarchived changes that collide like this, and the second archive would presumably fail. The new section shows both entries side by side, so the critic can now see the collision. This sub-ticket does not ask for more than that.
- `add_approved_changes()` writes `Decisions: none` on one line when a proposal has no Decisions lines. The design's entry format does not cover an empty Decisions list, so this choice is reasonable, and nothing checks it.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance and gate command myself, on the PR head and on the base. The base failures match the spec's "fails today" outputs for the stated reason, and the probes show the code is not fitted to the scenario's fixture.
ESCALATIONS: none
