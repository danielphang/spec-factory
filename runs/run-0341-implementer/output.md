Sub-ticket: T-0036.1, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0036.1/subticket.md` (parent T-0036, approved spec v2). Branch `factory/T-0036.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0036.1`, base `9a25809`, head `15c9d2f6498f40909e4a6fc270cd5639772997c8` (one commit).

## What changed

The spec writer, critic and planner now receive the whole spec store only when a ticket's triage output gives no list of capabilities. The spec store has two parts. Current truth is one document per capability saying what that part of the system does now. The decision log, `decisions.md`, holds standing decisions. Before this change, every writer and critic input carried all of current truth and the whole log. With this change, triage names the capabilities a request touches. Each of the three roles then receives those in full, plus a complete index of the rest that it can open by path.

**A. Triage names the capabilities.**
- `factory/compose.py`, triage branch: after the request, it appends `## Capability index: every capability in current truth`, with the instruction paragraph the spec gives and one index line per capability. With no current truth, nothing is appended. The index adds no `input_sources` entry.
- The triage prompt is edited identically in three places: the `docs/design.md` §1 block, its copy `docs/prompts/01-triage.md`, and the runtime prompt `factory/prompts/triage.md`.
  - INPUT names the capability index.
  - Step 4 adds "Name the current-truth capabilities the request touches, from the capability index."
  - OUTPUT gains a line after `Evidence:`, at column 0: `Capabilities: (names from the capability index, comma-separated; none` with the continuation `  if the request touches none)`. It is wrapped so that every new line fits in 72 characters; the longest is 72.

**B. Compose sends the selected capabilities in full and an index of the rest.** All of this is in `factory/compose.py`.
- New module functions:
  - `triage_capabilities(root, tid)` (B1). It reads the latest finished triage run's `output.md` and takes the first line starting `Capabilities:`. The rest of that line is split on commas and whitespace, and backticks and periods are stripped from each token. Tokens that name no current-truth capability are dropped. It returns None when there is no such run, no output file or no such line.
  - `cited_capabilities(root, text)` (B2): each capability whose `specs/<name>/spec.md` appears in `text`.
  - `capability_index(paths)` (B3): one line per capability, `- <name>, <ceil(bytes/1000)> kB, `<absolute path>`: <req>; <req>`. Requirement names come from the existing `specstore.requirement_blocks` (reuse rung 1).
  - `CAPABILITY_INDEX_NOTE`, the instruction paragraph in the spec's exact words.
- The inner `selected(spec_rel)` builds the set of capabilities a role receives in full (B4): triage's names plus the ones the role's spec cites, read whole. That spec is `specs/<tid>/v<version>.md` for the writer when version ≥ 1, the version under review for the critic, and the approved version for the planner. Without a `Capabilities:` line the set is None, and both helpers behave exactly as before.
- `add_truth(sel)` (B5) adds each selected capability in full, in path order, as before. It then appends `## Capability index: current truth not given in full above` for the rest. When every capability is selected, it appends nothing.
- `add_decisions(sel)` (B6) sorts each log line one of two ways:
  - Kept in full: the line's second field is the ticket id, or its text names a selected capability. A name only counts when no letter, digit, `-` or `_` touches either end of it. The kept lines go under the new heading, which names the absolute path of the log. `decisions.md` is a source only when at least one line is kept.
  - Indexed: every other line, grouped by ticket under `## Decision index: decisions not given in full above`. The section opens with the exact `grep ' <ticket id> ' <path>` paragraph. Each ticket gets one line, `- <id> (<n> decision(s), <first> to <last>): <title>`, with the title read from `tickets/<id>.yaml`.
  - An empty or whitespace-only log still adds nothing.
- Planner (B7): it calls `add_decisions(selected(approved version))` only, so it gets no current truth and no capability index.

**C. Documents.**
- `docs/design.md`:
  - The §Harness "Spec store" paragraph's last two sentences are replaced by a description of B. It covers the triage index and line, what the writer and critic get in full and indexed, the decision lines and decision index for all three roles, and the fallback.
  - Routing rows "New request" (adds "the capability index"), "Triage ACCEPT" and "Spec writer READY-FOR-CRITIC" now say "as the Spec store paragraph describes".
- `docs/changelog.md`: entry 60, "After issue #75 (2026-10-08), where …". It gives the Evidence figures, the change, the projection and the rejected `show` commands.
- `dev/build-harness.spec.md`: the writer's input in part H (intake step 2) reads as the spec gives it. The critic's input stays "(as for the writer)". Item 90 gains a sentence: it holds because the `accept-approve` stub triage output (`tests/factory/fixtures/stubs/accept-approve/triage-1.md`, read) has no `Capabilities:` line.
- `README.md`:
  - The Triage, Spec writer and Spec critic rows name the capability index. The Triage row glosses it at first use: one line per current-truth capability, with its spec's path and requirement names.
  - The Planner row gains only the decision-index clause.
  - The status date goes from 2026-10-06 to 2026-10-08.

Callers of what changed (coding rule 2): `add_truth` and `add_decisions` are closures inside `compose()`. `grep -rn 'add_truth\|add_decisions' factory/` finds only the calls in the writer branch (`compose.py:272-273`), the critic branch (`:291-292`) and the planner branch (`:315`). The three new module functions are called only from `compose.py`.

## Acceptance results

All were run from the worktree under the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN block and each WHEN were extracted verbatim from `specs/T-0036/v2.md` into scratch files.

**1. A ticket naming one capability composes inputs with only that capability in full and an index line for each other one → NEW**
- Before, on base `9a25809`:
  ```
  W: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0
  C: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0
  P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0
  ```
  This matches the spec's "today" output.
- After, at `15c9d2f`:
  ```
  W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1
  C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1
  P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0
  ```
  This is exactly the expected output. The writer gets only beta, and the critic also gets gamma, which the spec cites.

**2. Decisions of other tickets and capabilities reach each role as one index line per ticket → NEW**
- Before: each of the three lines read `own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n grep-cmd=0`, which matches the spec.
- After:
  ```
  W: own=1 beta-line=1 gamma-line=0 other=0 indexed=T-0008,T-0009 log-path=y grep-cmd=1
  C: own=1 beta-line=1 gamma-line=1 other=0 indexed=T-0009 log-path=y grep-cmd=1
  P: own=1 beta-line=1 gamma-line=1 other=0 indexed=T-0009 log-path=y grep-cmd=1
  ```
  This is exactly the expected output.

**3. Without a Capabilities line every capability and every decision reach the writer, critic and planner → REGRESSION**
- After:
  ```
  W: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1
  C: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1
  P: alpha=0 beta=0 gamma=0 own=1 beta-line=1 gamma-line=1 other=1
  ```
  This is exactly the expected output. It printed the same before the change.

**4. The harness suite passes with the new inputs → REGRESSION**
- After: `suite=0`.

**5. A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line → NEW**
- Before: `triage: alpha-index=n beta-index=n gamma-index=n bodies=0 decisions=0 asks=0`.
- After: `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0 asks=1`, which is the expected output.

**6. The prompt copies, design, build spec, README and changelog name the capability index → NEW**
- Before: `docs-copy=0 runtime=0 changelog=0 design=n build-spec=n readme=0`, then `whitespace=ok`.
- After: `docs-copy=1 runtime=1 changelog=1 design=y build-spec=y readme=3`, then `whitespace=ok`, which is the expected output.

**Gates, run exactly as written on `15c9d2f`:**
- `(export HOME=…; git diff --check main...HEAD)`: no output, exit 0. The whitespace check passes.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `384 passed in 250.44s`. That is the 364 tests on `main` plus the 20 new ones.

## Tests added/changed

- Added `tests/factory/test_capability_index.py`, a new file with 20 tests. They run black-box through `bin/factory` on throwaway stores and cover:
  - Writer: named capability in full, index lines with exact text, `input_sources`.
  - Critic: cited capabilities added, the instruction paragraph appears once.
  - Planner: no current truth and no index.
  - kB rounding: 2001 bytes shows 3 kB, 2000 bytes shows 2 kB.
  - `Capabilities:` parsing: backticks, a trailing period, no space after a comma, unknown names, `none`, an empty line.
  - Every capability named: no index.
  - The latest finished triage run decides.
  - Decision lines kept or indexed per role, including `beta-two`, `beta_x` and `xbeta2` not matching `beta`. Index lines with pluralisation and a date range, and a ticket title.
  - A log with nothing kept: index only and no `decisions.md` source. A log with everything kept: no index.
  - A whitespace-only log.
  - Fallback without the line.
  - Triage: index text, its position after the request, no source added. No index without current truth.
  - The prompt line in both copies, after `Evidence:`, with new lines of at most 72 characters.
- No existing test was changed. The spec's "Tests to change" is none.
- I watched the new tests fail first: 15 failed and 5 passed on base. The 5 that passed pin behaviour that already held on base: planner gets no truth, all capabilities named, whitespace-only log, fallback, and no index without truth.

## Known gaps and uncertainties

- **The README rule conflicts with the spec.** The README's "Maintaining this page" says behaviour appears above "Where this can go" only after it has run on a real ticket. The spec (C) requires the role rows to describe the capability index now, but it reaches real tickets only after the runtime moves to this revision. I followed the spec. The reviewer may want the rows held until the upgrade.
- **Parentheses around the list are not stripped.** Following B1, only backticks and periods are stripped. A triage output that copies the template's parentheses, such as `Capabilities: (beta, gamma)`, yields the tokens `(beta` and `gamma)`. Both are dropped, so the writer gets no capability in full and the index for all. Nothing is hidden, since the index lists everything, but the cut is wrong for that ticket.
- **Only the first line counts.** Only the first line starting `Capabilities:` is read. Names wrapped onto a continuation line are ignored.
- **Matching is case-sensitive.** A decision line is matched to a capability case-sensitively, so `Beta` does not match `beta`. B6 does not say either way. Capability names are lower-case kebab.
- **`decision(s)` is pluralised.** I read `<n> decision(s)` as pluralisation: `1 decision`, `2 decisions`.
- **The date range uses min and max.** "First date to last date" is computed as the smallest and largest date. For the append-only log this equals first and last appearance.
- **Short lines are kept in full.** A log line with fewer than three fields cannot be indexed by ticket, so it is kept. Neither store has one: every line on both matches `<date> <T-id> <text>`, checked with grep.
- **A capability's title stays empty.** A missing or empty title leaves the index line ending at `):`, with trailing space removed.
- **A delta header counts as a citation.** `cited_capabilities` is a plain substring test. A spec's own `=== specs/<name>/spec.md` delta header therefore counts as a citation, which hands a capability the spec modifies to the critic and planner. The acceptance fixture relies on this: the critic expects beta.
- **No measured effect on real stores.** The size targets are not held by acceptance (spec Decisions). I did not measure real-store input sizes; that is operator step 1.
- factory: markers added: none.

## Out-of-scope observations

- `README.md:795` (the "Record" row) still says `decisions.md` is received by "the spec writer, critic and planner … with their input". That is now true only in part: the lines of the ticket and its capabilities, plus an index. Spec C does not list this row.
- The README terms table has no "capability index" or "decision index" row. Each is glossed at first use in the role table instead.
- `docs/prompts/01-triage.md` already had four lines of 73 characters before this change, so "line width stays at 72" was not strictly true of the block before. No new line exceeds 72.

Protected paths touched, all declared in the spec's Risk list:
- harness: `factory/compose.py`, `factory/prompts/triage.md`
- generated: `docs/prompts/01-triage.md`, re-copied identically to the edited `docs/design.md` §1 block, which `test_decision_log.py`'s block-equals-copy test checks.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command prints exactly its expected output and both gates pass on the committed head (384 passed).
ESCALATIONS: none
