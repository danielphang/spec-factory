## Critic review — T-0006 spec v1 (P0-5 prose-only gate + symbol count)

Round 1. Spot-checks run from `~/dev/spec-factory` (branch `main`); reads of `~/dev/nanobot-upstream` were read-only.

### What I verified

- Cited paths exist and say what the spec says: `plans/P0-intake-skeleton.md:46` is the P0-5 bullet with the whole-file grep; `:56` is the row `| Code identifiers in acceptance | "doubled", ten relint commits | 0 (P0-5) |`; `prompts/02-spec-writer.md:24-26` and `docs/spec-factory.md:269-272` carry the inline-script allowance; `issues/06_p05_grep_vs_inline_scripts.md` is the originating issue; `~/dev/nanobot-upstream/knowledge_vault/spec_factory/runs/run-0004-critic/output.md:109` is the quoted `[NIT] #2 — A1/A2 name internal symbols`; `P0_MEASUREMENTS.md:8` carries the manual "0 outside code fences" note. `grep -rn 'P0-5\|Code identifiers' docs specs plans prompts README.md issues` hits only plan lines 46/56 and issues 04/06, as stated.
- Evidence table reproduced on the reference store: whole-file grep gives 1 / 1 / 5 for T-0001/v1.md, T-0001.md, T-0003.md; the restated awk|grep gives 0 / 0 / 0. T-0003's five hits are `def skill`, `def summary`, `def need` (lines 172, 186, 193, 226, 235). T-0001/v1 Acceptance has 2 column-0 fence lines and 8 at any indentation.
- Acceptance commands, all eight, run on the unchanged checkout: 1 prints `3`, 2 prints `1`, 3 prints `count: 0`, 4 prints `0`, 5 `same`, 6 `rows-same`, 7 `unchanged`, 8 `check=0`. Every "fails today" / "passes today" claim matches.
- Proposed change simulated: a scratch copy of the plan with the restated P0-5 line (`\140` escapes, one `grep -c` span) survives criterion 1's `grep | sed | sh -c` extraction and prints `0` on fixture 1; the restated command prints `1` on fixture 2. The triage's column-0 pipeline prints `1` and `0` on the same fixtures, confirming both defects the spec describes.
- Counting rules 1-5 implemented independently (scratchpad, ~45 lines of Python) and run on fixture 3: prints exactly the six lines criterion 3 pins, `count: 6`. On T-0001/v1.md and T-0003.md it prints exactly the two and four names quoted under Evidence. The rules as written are sufficient to reproduce the pinned outputs.
- Discriminating power: whole-file grep fails 1 (`3`); column-0 de-fencing fails 1 (`1`); fence-unaware section toggle fails 2 (`0`); an empty or absent block fails 3 (`count: 0`); a bare `grep -o 'nanobot(\.\w+)+'` over fenced Acceptance code fails 3 (`8` lines, adds `nanobot.agent` and `nanobot.agent.gov`).
- `awk version 20200816` on this machine, as stated.

### Findings

[SHOULD-FIX] #6 Proposed change C, counting rule 3
Problem: "Any dotted reference `PKG.x[.y…]` elsewhere in fenced code" relies on "elsewhere" to exclude the `from PKG.mod import …` lines consumed by rule 2; an implementer who re-scans those lines gets `nanobot.agent` and `nanobot.agent.gov` too and prints 8, not 6.
Evidence: scanning all fenced Acceptance lines of fixture 3 for `\bnanobot(\.\w+)+` yields `nanobot.agent`, `nanobot.agent.gov`, `nanobot.agent.loop.AgentLoop.run`; my rule-2-first implementation yields the pinned six. Criterion 3 catches the misreading, so this is not blocking, but the implementer should not have to discover the rule from a failing check.
Suggested fix: add to rule 3 "lines matched by rule 2 or by `import PKG.x as A` are not re-scanned; the module path in a `from` import is not itself counted."

No other findings I would defend. The two counting choices (per-spec distinct names; `mock.patch` string targets counted) are stated openly in both the spec and the plan text it prescribes, so rubric 4 is satisfied. Out-of-scope list is sensible; the un-reconciled P0-5 path (`knowledge_vault/sanitized_specs/` vs the as-built `knowledge_vault/spec_factory/specs/`) is correctly left to a separate finding. No protected path is touched; `plans/` is not protected. Risk section's weakening note (a writer could hide a stale symbol in a fence) is honest and is exactly what option c chose to observe rather than gate.

### Out-of-scope observations

- Criteria 5-8 compare the working tree to `main` while the checkout is on `main`. They pin the right thing when run before committing; if the implementer commits to `main` first they pass vacuously. This is the repo's convention, not this spec's defect.
- Paragraph C says to run the symbol block "from the green checkout"; the block is pure text processing and needs only `python3`, as criterion 3 (run from `~/dev/spec-factory`) shows. The phrasing is about where the spec files live, not a dependency; harmless.
- `docs/spec-factory.md:262-276` under Out of scope is a slightly wide range (262 is the Size rule); the allowance and never-names rule sit at 265-276. Not worth a revision.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high — every cited path, every base-side Acceptance output and both Evidence symbol lists were reproduced by command this session, and the one ambiguity found is caught by criterion 3.
ESCALATIONS: none
