Commit: 15c9d2f6498f40909e4a6fc270cd5639772997c8 (branch `factory/T-0036.1`, base `9a258097a5eb3feea060eca2cf3f5c7b8c65c072`, one commit)

## How I checked

Read the whole diff against the parent spec v2 (parts A, B1-B7, C) and the sub-ticket. Confirmed in the worktree the helpers the new code leans on: `_runs_for` (`factory/compose.py:16-26`) returns only runs whose `meta.yaml` has `finished`, so "latest finished triage run" (B1) holds; `add` (`:191-195`) takes an `edit` callable and records the source, so the kept-lines call at `:242-243` lists `decisions.md` only when a line is kept (B6); `store.ticket_path` (`factory/store.py:109`) and `specstore.requirement_blocks` (`factory/specstore.py:103`, a dict keyed by requirement name) exist and do what the index code needs. `store.load_ticket` (`store.py:113-117`) raises on a missing ticket, so the inner `title()` at `:247-250` with its own exists check is not a duplicate. Ran three of the new tests as a narrow confirmation of the decision-index and critic paths under the fresh-HOME wrapper: `3 passed in 4.52s`. Checked `docs/prompts/01-triage.md` equals the design doc's §1 block with `diff` (no output). Checked line widths: every line over 72 characters in both prompt copies (lines 12, 16, 25, 27 at 73; runtime 30-31) predates this change; no new line exceeds 72.

## Findings

1. Test integrity: no existing test file is in the diff. The only test change is the new file `tests/factory/test_capability_index.py`. Spec "Tests to change" is none. Clean.

2. Correctness: the diff does what B1-B7 say.
   - `triage_capabilities` (`factory/compose.py:41-53`): first `Capabilities:` line, split on `[,\s]+`, `` ` `` and `.` stripped, filtered to existing capabilities, order kept, None on no run, no output file or no line.
   - `cited_capabilities` (`:56-58`): substring `specs/<name>/spec.md`, as B2 says "anywhere in text". The delta header `=== specs/beta/spec.md` therefore counts; the spec's own fixture relies on it (critic expects beta), so this is the intended reading.
   - `selected` (`:205-213`): writer uses `v<version>` only when version >= 1; critic the version under review; planner the approved version read whole (B4). None propagates and both helpers take the old path exactly (`:220`, `:233-235`).
   - `add_truth` (`:215-226`): full specs in path order, index for the rest, nothing when none left; only full specs reach `input_sources` (B5).
   - `add_decisions` (`:228-258`): second field equals ticket id, or regex `(?<![A-Za-z0-9_-])name(?![A-Za-z0-9_-])` on the text field; heading text matches B6 word for word; index grouped by ticket in first-appearance order with min/max date and title (B6). Whitespace-only log still adds nothing (`:233-234`).
   - Triage branch (`:259-265`): index after the request, before any prior triage output, nothing without current truth (A1). No source added.
   - Planner (`:315`): decisions only, no truth, no capability index (B7).

3. Scope: every changed file is named in part C or the Risk list. The README status date bump is C's last item. Nothing outside the lettered parts.

4. Silent behavior changes: none beyond the spec. Inputs change only when a `Capabilities:` line exists, plus the triage index. The existing pinned heading `## Decision log (decisions.md): standing decisions, read-only` (`tests/factory/test_decision_log.py:215`) is untouched on the fallback path.

5. Security and data safety: nothing new. Paths written into inputs are the store's own absolute paths, which the spec asks for.

6. Protected paths: `factory/compose.py`, `factory/prompts/triage.md` (harness) and `docs/prompts/01-triage.md` (generated). All three are in the parent spec's Risk list. Listed under ESCALATIONS for the merge gate.

7. Coding standard: `capability_index` reuses `requirement_blocks` (rule 1 rung 1). `title()` needed because `load_ticket` raises on a missing ticket. Callers of `add_truth`/`add_decisions` named in the PR description (rule 2); both are closures with the three call sites the description lists. `factory:` markers: none, stated. Lean already.

8. PR description:
   - [NIT] PR description: What changed, first paragraph: "Each of the three roles then receives those in full, plus a complete index of the rest" → the planner receives no current truth and no capability index (B7, and the description's own Planner bullet), so a gate reader takes away that the planner gets capabilities. One clause, "the writer and critic receive those in full", fixes it.

No BLOCKING or SHOULD-FIX findings.

## Out-of-scope observations

- `README.md:795`, the Record row, still says `decisions.md` is "which the spec writer, critic and planner receive with their input". Still true in words, since every line reaches them in full or through the index, but it no longer says how. Spec C does not list the row; the implementer flagged it too. A follow-up to the README, not this ticket.
- The `Capabilities:` parser keeps parentheses (B1 lists only backticks and periods). A triage output that copies the template's parentheses, `Capabilities: (beta, gamma)`, yields no names and sends the index for everything. Spec-conformant; worth an eye in operator step 2.
- The spec's `decision(s)` placeholder is read as pluralisation (`1 decision`, `2 decisions`). The acceptance greps do not pin either form; the new tests pin this one.

Prior findings: none (round 1).

STATUS: APPROVE
CONFIDENCE: high, every part of B is traceable to a line in the diff, the fallback path is byte-for-byte the old code, no existing test moved, and the three tests I ran pass on this head.
ESCALATIONS: protected paths touched, all declared in the parent spec's Risk list: harness `factory/compose.py` and `factory/prompts/triage.md`; generated `docs/prompts/01-triage.md`, re-copied identically to the edited `docs/design.md` §1 block (diff printed nothing). The merge gate needs a human approval for these.
