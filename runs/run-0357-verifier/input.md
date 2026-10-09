## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0357-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0357-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0357-verifier/wt` (branch `factory/T-0037.1`, base `51e2af7f1737f5fc4d9780ea725710dc1112702f`, head `2f3fcef2f7a433585b85e99aedf9302133c01002`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0037.1

T-0037.1 / Send the whole decision log to the spec writer, critic and planner again, removing #75's decision filter (#75 follow-up)
Depends on: none
Parallel-safe: yes

Parent: T-0037, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does
- The capabilities each role receives and triage's input are unchanged by the whole log
- The harness suite passes with the whole decision log
- The design, README and changelog describe the whole decision log and no decision index
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0037/v2.md`

=== proposal.md
## Problem
Since issue #75, a recent change that trimmed each agent's input to save context, three agent roles can miss a standing rule that every ticket must follow. Those roles are the spec writer, which writes a ticket's spec; the critic, which reviews it; and the planner, which splits an approved spec into pieces of work. The rules sit in the decision log, `decisions.md`, one line per standing decision with its date and the ticket that made it. Since #75, a decision line reaches those roles in full only when it was logged against their own ticket, or when its text names a capability they receive in full. A capability is one current-truth spec: the store's record of how one part of the system behaves today, where the store is the factory's per-repository record of tickets, specs and decisions. Every other line is reduced to one entry per ticket in a "decision index", with a `grep` command the role may run to read it.

No decision line in either store names a capability, so the filter hides every rule that some other ticket made. In the operator's replay of a Nanobot ticket, the spec writer put new code in a module that a standing decision rules out, and the critic did not notice. Both had seen that decision only as an index line. The operator has chosen to send the whole decision log to these three roles again and to keep the rest of #75, the capability filter. The cost is about 34 kB more input per run on this repo's store and about 75 kB more on the Nanobot store.

## Root cause
`add_decisions` in `factory/compose.py:226-255` keeps a decision line only when it is logged against the ticket or names a selected capability, as a whole word. A cross-cutting standing decision names no capability, so for any ticket with a `Capabilities:` line it is reduced to an index entry. The writer, critic and planner then follow only the rules they choose to open.

## Out of scope
- Triage's input: still the capability index and no decision line.
- Which capabilities the writer and critic receive in full, the capability index and its lines, and the triage prompt's `Capabilities:` line. The only change to #75's capability half is one clause of the index note (Decision 2).
- The current-truth requirement "A ticket whose triage output names no capabilities receives today's inputs". It stays true as written.
- `dev/build-harness.spec.md` and every `docs/prompts/` file: none states the decision filter.
- Any new scoping of the decision log, such as #54's product and implementation tagging.
- The contents of `decisions.md`, and the status cell of #78's history rows in `README.md` and `dev/issues.md`, which the operator's `dev:` commits keep.
- The runtime move itself (Operator steps).

## Open questions
none

## Decisions
- The spec writer, critic and planner receive `decisions.md` whole whenever it holds any text, whatever capabilities their ticket names. The decision index and its `grep` instruction are removed. This is the operator's Answer 1, already standing in `decisions.md` as the 2026-10-09 T-0037 line. Rejected: the request's rule of sending lines that name no capability in full and filtering the rest. On today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
- The capability index note loses its clause ", and the decisions that name it to the critic and the planner,"; the rest of the note stays word for word. Rejected: keeping the clause, which would tell the writer that citing a path is how decisions reach the critic and planner. That is no longer so. This edits one sentence of #75's capability half, which the triage assumption kept byte for byte.
- The planner's decision part no longer reads triage's capability names or the approved spec's citations. It reads the whole log, as before #75.
- The decision part is measured in this spec's Evidence, before and after, on both stores. No new file or harness command records it.

## Risk
Blast radius: the input of every spec writer, critic and planner run on every target that adopts this harness revision. Each grows by the size of its log, about 34 kB here and 75 kB on Nanobot per run (Evidence). Triage, implementer, reviewer and verifier inputs do not change. A mistake here would drop decisions from those inputs or break the capability half. The NEW role-inputs scenario and the two REGRESSION scenarios cover both.
Protected paths touched: harness, `factory/**`, through `factory/compose.py`. The other files changed are `tests/factory/test_capability_index.py` (existing tests, listed under Tests to change), `docs/design.md`, `docs/changelog.md` and `README.md`, none of them protected. No `docs/prompts/` file changes.

## Operator steps
- Merging this change does not by itself change what the roles receive. Tickets run from the runtime, a separate checkout of the harness pinned to one commit (`~/dev/spec-factory-harness`), and a merge into `main` never moves it. #75 is merged but held from the runtime until this fix merges. After merge, move the runtime once to the merge commit, so that #75 and this fix ship together (README, "Upgrading the runtime", step 1).
- Each target repository runs only the harness commit recorded in its `harness.lock`, and refuses its store after a runtime move until it accepts the new commit. In each target that should adopt this change, run any store command once with `--accept-harness <sha>`, where `<sha>` is the runtime's new commit (README, "Upgrading the runtime", step 2).
- On the first spec writer run in each target after that, check that its `input.md` holds `## Decision log (decisions.md): standing decisions, read-only` and no `## Decision index`.

=== design.md
## Proposed change
A. `factory/compose.py`, the decision log in role inputs.
   1. `add_decisions` (`:226-255`) takes no argument. When `decisions.md` is missing or holds only whitespace it adds nothing, as today. Otherwise it calls `add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")` and returns. Remove the filtering (`:235-243`), the trimmed "Decision log ... logged against this ticket or naming a capability given in full" block (`:244-246`) and the whole "Decision index" section with its `title()` helper and `grep` instruction (`:247-255`).
   2. The callers become `add_decisions()`. For the spec writer (`:273`) and the critic (`:292`) they stay right after `add_truth(sel)`, so the log still follows current truth and the capability index. The planner (`:315`) no longer calls `selected()`. Its comment says the planner gets no current truth and the whole log.
   3. `CAPABILITY_INDEX_NOTE` (`:138-142`) becomes, word for word: "This list is complete: every current-truth capability not given in full above has one line here. Open a capability at its path before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, sends that capability in full to the critic, so cite under Evidence each capability you open."
   4. `selected()`, `add_truth()`, the capability index and the triage branch stay as they are. `input_sources` lists `decisions.md` for these three roles whenever the log holds text, as the `add` helper already does.
B. `tests/factory/test_capability_index.py`: replace the decision-filter tests (Tests to change) with tests of the whole log: with `Capabilities: beta`, and with `Capabilities: none`, each of the spec writer, critic and planner inputs holds the whole-log heading followed by every fixture line, and no `Decision index`. Update the module docstring and the note text. Keep `test_a_whitespace_only_log_still_adds_nothing` and the part-B4 test as they are.
C. Documents.
   1. `docs/design.md:94`, §Harness, "Spec store" paragraph. Replace its last two sentences, from "They and the planner receive the decision log's lines ..." to the end, with: "They and the planner receive the whole decision log, `decisions.md`, when it holds any text, whatever capabilities the ticket names: a standing decision often names no capability, yet every ticket must follow it. A ticket whose latest triage output has no `Capabilities:` line gets every current-truth spec in full."
   2. `README.md`, the role table.
      - Spec writer row (`:85`): replace "the decision log's lines for this ticket and those capabilities, and a decision index for the rest, one line per other ticket" with "the whole decision log".
      - Spec critic row (`:86`): replace "the decision log's lines for this ticket and those capabilities, and a decision index for the rest" with "the whole decision log".
      - Planner row (`:87`): replace "the decision log's lines for this ticket and its capabilities, and a decision index for the rest" with "the whole decision log".
      - Bump the Status line's date to the day of the change, per "Maintaining this page". The terms row for "ruling, decision log" (`:128`) is already true and stays.
   3. `docs/changelog.md`: add entry 61 after entry 60, in that list's form, starting `61. After issue #78 (2026-10-09), where`. It says what went wrong: #75's filter reduced every decision of another ticket to an index line, because no line names a capability, and in the replay a writer broke a cross-cutting decision while the critic missed it. It says what changed: the three roles receive the whole log again, the decision index and its `grep` command are gone, and the capability index stays. It gives the size change as measured on 2026-10-09 (Evidence table), rounded: the decision part of each input grows from under 3 kB to about 36 kB here, and from about 5 kB to about 80 kB on Nanobot. It names the rejected alternative, the request's rule of filtering only lines that name a capability (Decision 1).

## Tests to change
- `tests/factory/test_capability_index.py:1-9`, module docstring: says the writer, critic and planner get only the decision lines of their ticket and capabilities, plus an index. Follows Decision 1.
- `tests/factory/test_capability_index.py:22` (`CITES`) and `:122-126` in `test_writer_gets_the_named_capability_in_full_and_an_index_line_for_each_other`: pin the note clause that Decision 2 removes.
- `tests/factory/test_capability_index.py:194-203`, helpers `decision_block` and `decision_index`: build the trimmed-log heading and the decision index that Decision 1 removes.
- `tests/factory/test_capability_index.py:206-217`, `test_each_role_gets_its_ticket_s_and_its_capabilities_decisions_and_an_index_of_the_rest`: expects OTHER-LINE left out and an index. Follows Decision 1 (and Decision 3 for the planner).
- `tests/factory/test_capability_index.py:220-224`, `test_a_decision_index_line_carries_the_ticket_s_title`: the index no longer exists. Follows Decision 1.
- `tests/factory/test_capability_index.py:227-232`, `test_no_kept_line_leaves_only_the_index_and_no_decisions_source`: expects no `## Decision log` and no `decisions.md` source with `Capabilities: none`. Both now appear. Follows Decision 1.
- `tests/factory/test_capability_index.py:235-238`, `test_every_line_kept_leaves_no_decision_index`: expects the trimmed-log heading. Follows Decision 1.

=== specs/role-inputs/spec.md
## REMOVED Requirements
### Requirement: The spec writer, critic and planner receive in full only the decisions of their ticket and its capabilities, and a decision index for the rest
Reason: the filter hid every cross-cutting standing decision, because no decision line names a capability; the three roles receive the whole decision log instead (the operator's answer to #78).

## ADDED Requirements
### Requirement: The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names
Whenever `decisions.md` holds any text, the spec writer, critic and planner inputs SHALL hold it whole, under the heading `## Decision log (decisions.md): standing decisions, read-only`, and SHALL list it in `input_sources`, whether or not the ticket's latest finished triage output has a `Capabilities:` line; they MUST hold no decision index. Triage MUST still receive no decision line, and the capabilities each role receives in full, with the capability index, MUST stay as they are.

#### Scenario: With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; for v in W C P; do eval f=\$$v; echo "$v: own=$(grep -c OWN-LINE $f) beta-line=$(grep -c BETA-LINE $f) gamma-line=$(grep -c GAMMA-LINE $f) other=$(grep -c OTHER-LINE $f) whole=$(grep -cxF '## Decision log (decisions.md): standing decisions, read-only' $f) index=$(grep -c '^## Decision index' $f) grep-cmd=$(grep -cF "grep ' <ticket id> '" $f) note-decisions=$(grep -cF 'and the decisions that name it' $f) source=$(grep -cx -- '- decisions.md' $(dirname $f)/meta.yaml)"; done)`
- THEN it prints exactly `W: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1`, then the same with `C:`, then the same with `P:`. OTHER-LINE, logged against another ticket and naming no capability, reaches all three roles. No role gets a decision index or its `grep` instruction, and the capability index note no longer speaks of decisions.

#### Scenario: The capabilities each role receives and triage's input are unchanged by the whole log
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; for v in W C P; do eval f=\$$v; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) alpha-index=$(y alpha) gamma-index=$(y gamma) cites=$(grep -cF 'sends that capability in full to the critic' $f)"; done; f=$I; echo "triage: alpha-index=$(y alpha) beta-index=$(y beta) gamma-index=$(y gamma) bodies=$(grep -c -- '-BODY' $f) decisions=$(grep -c -- '-LINE' $f)")`
- THEN it prints exactly `W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1`, then `C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0`, then `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0`

#### Scenario: The harness suite passes with the whole decision log
Run with TMPDIR unset or outside any `.factory/` instance: some suite tests need a directory outside every instance.
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory >/dev/null 2>&1; echo "suite=$?")`
- THEN it prints exactly `suite=0`

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents describe the whole decision log for the spec writer, critic and planner
`docs/design.md` and the README's Spec writer, Spec critic and Planner rows MUST say that those roles receive the whole decision log, and neither MUST mention a decision index. `docs/changelog.md` SHALL have an entry for issue #78, with no whitespace error in the change.

#### Scenario: The design, README and changelog describe the whole decision log and no decision index
- WHEN `(echo "design-index=$(grep -c 'decision index' docs/design.md) design-whole=$(grep -c 'They and the planner receive the whole decision log' docs/design.md) readme-index=$(grep -c 'decision index' README.md) readme-whole=$(grep -E '^\| (Spec writer|Spec critic|Planner) \(' README.md | grep -c 'the whole decision log') changelog=$(grep -c '^[0-9]*\. After issue #78 ' docs/changelog.md)"; git diff --check main...HEAD && echo whitespace=ok)`
- THEN it prints exactly `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`, then `whitespace=ok`

=== verification.md
## Acceptance
- With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does → NEW; on `main` (`51e2af7`) it prints `W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1`, `C: ... gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 ...` and `P: ... other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 ...` (Evidence): OTHER-LINE is missing from all three and a decision index is present.
- The capabilities each role receives and triage's input are unchanged by the whole log → REGRESSION; on `main` it prints exactly the expected four lines (run through the fixture with a throwaway HOME).
- The harness suite passes with the whole decision log → REGRESSION; on `main` (`51e2af7`) with a throwaway HOME and the default TMPDIR it printed `suite=0` (384 passed).
- The design, README and changelog describe the whole decision log and no decision index → NEW; on `main` it prints `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`.

## PR description (the implementer's output)

Sub-ticket: T-0037.1 (parent T-0037, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0037/v2.md`). Branch `factory/T-0037.1`, one commit `2f3fcef` on base `51e2af7`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0037.1`.

## What changed
Three agent roles were missing standing rules. Since #75, the spec writer (writes a ticket's spec), the critic (reviews that spec) and the planner (splits an approved spec into pieces of work) received only some lines of the decision log, `decisions.md`, in full. The decision log holds one line per standing decision. A line counted only if it was logged against their own ticket or named a capability they received in full. A capability is one current-truth spec, the store's record of how one part of the system behaves today. No decision line names a capability, so every other ticket's decision reached these roles only as a line in a "decision index". This change sends them the whole log again.

- **A. `factory/compose.py`.**
  - `add_decisions` now takes no argument. It adds `decisions.md` whole under `## Decision log (decisions.md): standing decisions, read-only` when the file holds any text, and adds nothing otherwise, as before. The line filter, the trimmed-log block and the "Decision index" section, with its `title()` helper and `grep` instruction, are removed.
  - Callers: `add_decisions` is a closure inside `compose()`. `git grep -n add_decisions` finds only its three calls, for the spec writer (`:250`), the critic (`:269`) and the planner (`:292`). All three are now `add_decisions()`. The writer and critic calls still follow `add_truth(sel)`. The planner no longer calls `selected()`.
  - `CAPABILITY_INDEX_NOTE` (`:138-142`) loses the clause ", and the decisions that name it to the critic and the planner,". It now matches the spec's text word for word. Its only use is in `add_truth` (`:223`).
  - `selected()`, `add_truth()`, the capability index and the triage branch are unchanged.
- **B. `tests/factory/test_capability_index.py`.** The decision-filter tests are replaced by one parametrized test, `test_each_role_gets_the_whole_decision_log_and_no_decision_index`. It runs with `Capabilities: beta` and with `Capabilities: none`. For each of the spec writer, critic and planner it checks three things: the input holds the whole-log heading followed by every fixture line; it holds no `Decision index` and no `<ticket id>` grep instruction; and `decisions.md` is in its `input_sources`. The module docstring and the note text in the writer test are updated. `test_a_whitespace_only_log_still_adds_nothing` and the part-B4 test are unchanged.
- **C. Documents.**
  - `docs/design.md:94`: the last two sentences of the "Spec store" paragraph are replaced with the spec's text.
  - `README.md`: the Spec writer, Spec critic and Planner rows of the role table now say "the whole decision log". The Status date moves to 2026-10-09, the store's UTC date for this change.
  - `docs/changelog.md`: entry 61, "After issue #78 (2026-10-09)". It gives what went wrong, what changed, the measured size change (under 3 kB to about 36 kB here; about 5 kB to about 80 kB on Nanobot) and the rejected alternative.

Protected paths touched: `factory/compose.py`, part of the harness. The spec's Risk section declares it. No `docs/prompts/` file and no other protected path changed.

## Acceptance results
The role-input scenarios depend on a GIVEN fixture. It was written from the current-truth `role-inputs` spec (`openspec/specs/role-inputs/spec.md:13-48`) with `TMPDIR` set to this run's scratch directory, and run from the worktree after `uv sync --frozen`. Every command ran inside the throwaway-HOME wrapper.

- **With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does (NEW).**
  - Before, on `51e2af7`:
    ```
    W: own=1 beta-line=1 gamma-line=0 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1
    C: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=1 source=1
    P: own=1 beta-line=1 gamma-line=1 other=0 whole=0 index=1 grep-cmd=1 note-decisions=0 source=1
    ```
    This is the failure the spec describes. OTHER-LINE, a decision logged against another ticket that names no capability, reaches no role, and each role gets a decision index.
  - After, on `2f3fcef`:
    ```
    W: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1
    C: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1
    P: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1
    ```
    This matches the THEN exactly. Every decision line reaches all three roles. No role gets a decision index or its `grep` instruction, and the capability index note no longer mentions decisions.
- **The capabilities each role receives and triage's input are unchanged by the whole log (REGRESSION).** After, on `2f3fcef`:
  ```
  W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1
  C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1
  P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0
  triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0
  ```
  This matches the THEN exactly, and the base printed the same four lines: #75's capability half is intact, and triage still gets no decision line.
- **The harness suite passes with the whole decision log (REGRESSION).** After, on `2f3fcef`, with the default macOS `TMPDIR` (`/var/folders/...`, outside every instance), it printed `suite=0`.
- **The design, README and changelog describe the whole decision log and no decision index (NEW).**
  - Before, on `51e2af7`: `design-index=1 design-whole=0 readme-index=3 readme-whole=0 changelog=0`, then `whitespace=ok`.
  - After, on `2f3fcef`: `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`, then `whitespace=ok`. This matches the THEN exactly.
- **Gates, each run exactly as written, from the worktree, on `2f3fcef`.**
  - `git diff --check main...HEAD` exited 0.
  - `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `382 passed in 292.40s`. The base had 384. The net -2 is this change: it removes four tests and adds one test with two parameter cases.

## Tests added/changed
All in `tests/factory/test_capability_index.py`, and every change is on the spec's Tests to change list. Because this edits an existing test file, the PR goes to a human gate.

| Change | Lines on base | Why |
|---|---|---|
| Module docstring rewritten | `:1-9` | It described the decision filter and index (Decision 1) |
| `CITES` constant removed; the writer test's note text drops the clause | `:22`, `:122-126` | They pinned the note clause that Decision 2 removes |
| Helpers `decision_block` and `decision_index` removed | `:194-203` | They built the trimmed-log heading and the decision index (Decision 1) |
| `test_each_role_gets_its_ticket_s_and_its_capabilities_decisions_and_an_index_of_the_rest` removed | `:206-217` | It expected OTHER-LINE left out and an index (Decisions 1 and 3) |
| `test_a_decision_index_line_carries_the_ticket_s_title` removed | `:220-224` | The index no longer exists (Decision 1) |
| `test_no_kept_line_leaves_only_the_index_and_no_decisions_source` removed | `:227-232` | With `Capabilities: none` the log and its source now appear (Decision 1) |
| `test_every_line_kept_leaves_no_decision_index` removed | `:235-238` | It expected the trimmed-log heading (Decision 1) |
| Added `test_each_role_gets_the_whole_decision_log_and_no_decision_index`, parametrized with `Capabilities: beta` and `Capabilities: none` | new, in place of the removed block | Part B: each role holds the whole log, no index, and the `decisions.md` source |

The new test failed on the base code: 3 failed and 15 passed in the file, the writer-note test plus both parameter cases. It passed after the code change: 39 passed together with `tests/factory/test_decision_log.py`, whose whole-log test at `:205-215` passes before and after, as the spec says.

## Known gaps and uncertainties
- The `others` parameter of the test helpers `setup` and `build` (`test_capability_index.py:71-96`) now has no caller. Only the removed title test used it. The helpers are not on the Tests to change list, so they are left as they are. Likewise, the fifth fixture line `OTHER2-LINE` was written for the removed word-boundary test. It is still checked, as one of the lines the whole log must carry.
- The README Status date is 2026-10-09, the UTC date the store and the spec use. The operator's local date was still 2026-10-08 (PDT) when this ran.
- factory: markers added: none.
- The Operator steps are not done here: moving the runtime and running `--accept-harness` in each target.

## Out-of-scope observations
- To keep step 2's NEW-before output, the fixture's throwaway stores were created under this run's scratch directory, which is inside `.factory/`. This worked because the fixture sets `FACTORY_INSTANCE` itself. The suite itself was run with `TMPDIR` outside every instance, as its scenario requires.

## Responses to findings
n/a (round 1)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command printed its THEN exactly on `2f3fcef`, both NEW commands printed the spec's "before" output on `51e2af7`, and both gates passed.
ESCALATIONS: none

## Diff `51e2af7f1737f5fc4d9780ea725710dc1112702f...2f3fcef2f7a433585b85e99aedf9302133c01002`

diff --git a/README.md b/README.md
index 8518e67..322d463 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-08. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-09. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -82,9 +82,9 @@ directories and `models` entries use.
 | Role | Reads | Ends with `STATUS:` | What the harness keeps |
 |---|---|---|---|
 | Triage (`triage`) | the request; the capability index, one line per current-truth capability with its spec's path and requirement names; after a human answer, its own earlier output | ACCEPT · CLARIFY · NEEDS-HUMAN · REJECT | the title and type, copied onto the ticket |
-| Spec writer (`spec_writer`) | triage's output, the request; current truth in full for the capabilities triage named, and the capability index for the rest; the decision log's lines for this ticket and those capabilities, and a decision index for the rest, one line per other ticket; after a revision request, the critic's findings and its own previous spec; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
-| Spec critic (`critic`) | the spec version; current truth in full for the capabilities triage named or the spec cites, and the capability index for the rest; the decision log's lines for this ticket and those capabilities, and a decision index for the rest; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
-| Planner (`planner`) | the approved spec; the decision log's lines for this ticket and its capabilities, and a decision index for the rest; rulings; any sub-tickets that already exist | PLANNED · ESCALATE | the plan, `plans/<ticket>.md`, and one sub-ticket per piece, with its dependencies |
+| Spec writer (`spec_writer`) | triage's output, the request; current truth in full for the capabilities triage named, and the capability index for the rest; the whole decision log; after a revision request, the critic's findings and its own previous spec; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
+| Spec critic (`critic`) | the spec version; current truth in full for the capabilities triage named or the spec cites, and the capability index for the rest; the whole decision log; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
+| Planner (`planner`) | the approved spec; the whole decision log; rulings; any sub-tickets that already exist | PLANNED · ESCALATE | the plan, `plans/<ticket>.md`, and one sub-ticket per piece, with its dependencies |
 | Implementer (`implementer`) | where it works (its worktree, branch, base commit and the wrapped gate commands), the sub-ticket, the pinned spec; on a revision, both checkers' findings and the gate result | READY-FOR-REVIEW · BLOCKED | its commits on branch `factory/<sub-ticket>` and the head commit; the message itself is the PR description |
 | Code reviewer (`reviewer`) | the sub-ticket, the pinned spec, the PR description, the diff; from round 2, both checkers' findings from the previous round; any ruling | APPROVE · REQUEST-CHANGES · ESCALATE | a verdict for that commit, `results/<commit>/reviewer.yaml` |
 | Verifier (`verifier`) | the same as the code reviewer; the final run on a parent gets the spec, where it works, and any ruling | VERIFIED · FAILED · SPEC-DEFECT | a verdict for that commit, `verifier.yaml`, and the gate result, `ci.yaml` |
diff --git a/docs/changelog.md b/docs/changelog.md
index 6b3d210..c0cf9e8 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -62,5 +62,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 58. After issue #73 (2026-10-07), where the spec writer took a third of all workflow context tokens (309M of 866M; a median of 29 agent calls and 5.3M tokens per run), because every call re-sends the start-up context and everything read so far, and where the critic ran the test suite and built prototype clones of the change on its own initiative, though its grounding is meant to stay within two paths and one command per claim. The spec writer prompt gains a RULES bullet, Turn economy: put independent reads and commands in one turn, read a line range once grep has found it, send long output to a file in the run's scratch directory and grep or tail it, and write the spec in as few writes as possible. The critic's PROCESS keeps its minimum spot-check and caps any one claim at two paths and one command; it runs no test suite and builds nothing, and a claim it could settle only by building becomes a finding for the writer or a question. It gains the same reading rules. No rubric item, round limit or required spec section changes, and the shared preamble does not change. Rejected: a shared preamble line, which would reach every role.
 59. After issue #74 (2026-10-08), where the operator's replay of three past intakes (#49, #51, #57), with the same inputs and bases, found that #73's spec writer rules cut its tokens by about 37% at the same quality, but that its critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk on #51 and, on #57, the brace-list declaration bug that the earlier prompt had confirmed with a scratch git test. The critic's PROCESS drops the per-claim cap (at most two paths and one command for any one claim) and the no-build rule (no clone, worktree or prototype), and says the critic may run a small experiment in its scratch directory to confirm a finding. It keeps its minimum spot-check, the rule that it runs no test suite, the rule for picking an acceptance command, the rule that a claim needing a suite run or a build of the change is a finding or a question, and the three reading rules. `docs/principles.md` principle 2 keeps the critic's no-suite rule, and its Spiking section drops the two-path bound and says that vetting a whole approach is still the spec writer's or a spike's job. The spec writer prompt is unchanged from #73.
 60. After issue #75 (2026-10-08), where every spec writer and critic input carried all of current truth and the whole decision log, whatever its ticket touched: one spec writer input on this repo's store was 171.6 kB, of which 123.9 kB was current truth and 32.4 kB the log, and the Nanobot store adds about 480 kB to each writer input. Triage now receives the capability index, one line per current-truth capability with its size, spec path and requirement names, and names the capabilities a request touches on a new `Capabilities:` output line. The spec writer and critic receive those capabilities in full, plus each one their spec cites by path, and the capability index for the rest. They and the planner receive the decision-log lines of the ticket and of those capabilities, and a decision index for the rest: one line per other ticket, with a `grep` command that reads its lines. A ticket whose triage output has no `Capabilities:` line keeps the whole of both. The projection for the Nanobot store's last ten tickets is a mean writer input of 101 kB and a maximum of 167 kB, against 521 kB and 635 kB before; that still misses the request's 40 kB and 100 kB targets, because the rest of a writer input lies outside this change. Rejected: `factory spec show` and `factory decision show` commands, because a command run from inside a role must clear the live-store fence, the guard that refuses store commands while a role runs, and find the instance; a path needs neither.
+61. After issue #78 (2026-10-09), where #75's filter reduced every decision logged against another ticket to a line of the decision index, because no line in either store's decision log names a capability: in the operator's replay of a Nanobot ticket, the spec writer put new code in a module that another ticket's standing decision rules out, and the critic missed it. The spec writer, critic and planner receive the whole decision log again, whatever capabilities their ticket names. The decision index and its `grep` command are gone; the capability index stays. Measured on 2026-10-09, the decision part of each of their inputs grows from under 3 kB to about 36 kB on this repo's store, and from about 5 kB to about 80 kB on the Nanobot store. Rejected: the request's rule of sending in full the lines that name no capability and filtering the rest, because on today's logs it sends every line anyway, and it could still hide a cross-cutting decision that happens to name a capability.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index f0c9315..c9bfdf3 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -91,7 +91,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | `tasks.md` | The sub-tickets and coverage map | Planner, or the harness when it skips the planner |
 | `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |
 
-`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. Triage receives the capability index: one line per current-truth capability, with its size, the absolute path of its spec and its requirement names. Triage names the capabilities the request touches on its `Capabilities:` line. The spec writer and the critic receive those capabilities in full, plus each one whose `specs/<name>/spec.md` path the spec they work from cites, and the capability index for the rest (routing table). They and the planner receive the decision log's lines logged against the ticket or naming one of those capabilities, and a decision index for the rest: one line per other ticket, with the `grep` command that reads its lines from `decisions.md`. A ticket whose latest triage output has no `Capabilities:` line gets the whole of both: every current-truth spec, and `decisions.md` when it holds any text.
+`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. Triage receives the capability index: one line per current-truth capability, with its size, the absolute path of its spec and its requirement names. Triage names the capabilities the request touches on its `Capabilities:` line. The spec writer and the critic receive those capabilities in full, plus each one whose `specs/<name>/spec.md` path the spec they work from cites, and the capability index for the rest (routing table). They and the planner receive the whole decision log, `decisions.md`, when it holds any text, whatever capabilities the ticket names: a standing decision often names no capability, yet every ticket must follow it. A ticket whose latest triage output has no `Capabilities:` line gets every current-truth spec in full.
 
 **Routing table.** The dispatcher (piece 2) is this table and nothing else. Each row: a STATUS a role emits, what runs next, and what it receives. "Receives" adds to the INPUT the role prompt already declares. Both follow the role-context block (above).
 
diff --git a/factory/compose.py b/factory/compose.py
index 16cafe6..213355c 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -138,8 +138,8 @@ def without_evidence(text: str) -> str:
 CAPABILITY_INDEX_NOTE = (
     "This list is complete: every current-truth capability not given in full above has one line here. Open a "
     "capability at its path before you rely on it. A spec that cites a capability's path, as "
-    "`openspec/specs/<name>/spec.md`, sends that capability in full to the critic, and the decisions that name it "
-    "to the critic and the planner, so cite under Evidence each capability you open.")
+    "`openspec/specs/<name>/spec.md`, sends that capability in full to the critic, so cite under Evidence each "
+    "capability you open.")
 
 _ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
 
@@ -223,36 +223,13 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             parts.append("\n## Capability index: current truth not given in full above\n\n" + CAPABILITY_INDEX_NOTE
                          + "\n\n" + capability_index(rest))
 
-    def add_decisions(sel: set[str] | None) -> None:
-        # an empty log (the one `factory init` creates) carries nothing, so it is no input
+    def add_decisions() -> None:
+        # the whole log, whatever capabilities the ticket names: a standing decision often names no
+        # capability, yet every ticket must follow it (#78). An empty log (the one `factory init`
+        # creates) carries nothing, so it is no input.
         p = root / "decisions.md"
-        text = p.read_text(encoding="utf-8") if p.exists() else ""
-        if not text.strip():
-            return
-        if sel is None:
+        if p.exists() and p.read_text(encoding="utf-8").strip():
             add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")
-            return
-        named = [re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(c)}(?![A-Za-z0-9_-])") for c in sel]
-        kept, rest = [], {}
-        for line in filter(str.strip, text.splitlines()):
-            f = line.split(maxsplit=2)
-            # a line without a date and a ticket id cannot be indexed, so it is kept
-            if len(f) < 3 or f[1] == tid or any(r.search(f[2]) for r in named):
-                kept.append(line)
-            else:
-                rest.setdefault(f[1], []).append(f[0])
-        if kept:
-            add("decisions.md", "Decision log (decisions.md): the standing decisions logged against this ticket "
-                f"or naming a capability given in full, read-only. The full log is `{p}`", lambda _: "\n".join(kept))
-        if rest:
-            def title(t_id: str) -> str:
-                tp = store.ticket_path(root, t_id)
-                return str(store.read_yaml(tp).get("title") or "") if tp.exists() else ""
-            parts.append("\n## Decision index: decisions not given in full above\n\nThis list is complete: every "
-                         "ticket with a decision not given in full above has one line here. Read a ticket's decisions "
-                         f"with `grep ' <ticket id> ' {p}`.\n\n"
-                         + "".join(f"- {k} ({len(d)} decision{'s' * (len(d) > 1)}, {min(d)} to {max(d)}): "
-                                   f"{title(k)}".rstrip() + "\n" for k, d in rest.items()))
     if role == "triage":
         add(t["request"], "Request (raw, with any answers appended)")
         every = current_truth(root)
@@ -270,7 +247,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         add(t["request"], "Request (raw)")
         sel = selected(f"specs/{tid}/v{version}.md" if version >= 1 else None)
         add_truth(sel)
-        add_decisions(sel)
+        add_decisions()
         if rnd >= 1 and version >= 1:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
@@ -289,7 +266,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         add(f"specs/{tid}/v{version}.md", f"Spec under review (v{version})")
         sel = selected(f"specs/{tid}/v{version}.md")
         add_truth(sel)
-        add_decisions(sel)
+        add_decisions()
         if rnd >= 2 and version >= 2:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
@@ -312,7 +289,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         if av is None:
             raise store.Refused(f"{tid} has no approved spec version")
         add_spec(f"specs/{tid}/v{av}.md", f"Approved spec (v{av}, pinned)")
-        add_decisions(selected(f"specs/{tid}/v{av}.md"))  # no current truth for the planner, so no index
+        add_decisions()  # no current truth for the planner, and the whole log
         for p in _approvals(root, tid, "ruling"):
             add(str(p.relative_to(root)), "Human ruling")
         subs = store.subtickets_of(root, tid)
diff --git a/tests/factory/test_capability_index.py b/tests/factory/test_capability_index.py
index eb934a1..9ac00dd 100644
--- a/tests/factory/test_capability_index.py
+++ b/tests/factory/test_capability_index.py
@@ -1,11 +1,11 @@
-"""The capability index and the decision index (spec-factory T-0036, issue #75).
+"""The capability index (spec-factory T-0036, issue #75) and the whole decision log (T-0037, #78).
 
 Triage names the capabilities a request touches on a `Capabilities:` line, from a capability index
 in its input. The spec writer and critic then receive those capabilities in full, plus the ones
-their spec cites by `specs/<name>/spec.md`, and one index line for every other capability. The
-writer, critic and planner receive the decision-log lines of their ticket and those capabilities,
-and one index line per other ticket. A ticket whose triage output has no `Capabilities:` line keeps
-the whole of both. Black-box through `bin/factory`.
+their spec cites by `specs/<name>/spec.md`, and one index line for every other capability. A ticket
+whose triage output has no `Capabilities:` line gets every capability in full. The writer, critic
+and planner receive the whole decision log whatever capabilities their ticket names: a standing
+decision often names no capability. Black-box through `bin/factory`.
 """
 from __future__ import annotations
 
@@ -19,7 +19,6 @@ import yaml
 REPO = Path(__file__).resolve().parents[2]
 BIN = REPO / "bin" / "factory"
 CAPS = ("alpha", "beta", "gamma")
-CITES = "the decisions that name it to the critic and the planner"
 SPEC = "\n".join([
     "=== proposal.md", "## Problem", "Beta is lax.", "## Evidence", "Read `openspec/specs/gamma/spec.md`.",
     "## Decisions", "none", "## Risk", "none", "=== design.md", "## Proposed change", "A. Tighten beta.",
@@ -122,8 +121,7 @@ def test_writer_gets_the_named_capability_in_full_and_an_index_line_for_each_oth
     head = ("\n## Capability index: current truth not given in full above\n\nThis list is complete: every "
             "current-truth capability not given in full above has one line here. Open a capability at its path "
             "before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, "
-            "sends that capability in full to the critic, and " + CITES + ", so cite under Evidence each "
-            "capability you open.\n\n")
+            "sends that capability in full to the critic, so cite under Evidence each capability you open.\n\n")
     assert head + index_line(s, "alpha") + index_line(s, "gamma") in text
     assert sources(s, r["spec_writer"]) == [f"runs/{r['triage']}/output.md", "requests/T-0001.md",
                                             "openspec/specs/beta/spec.md", "decisions.md"]
@@ -189,53 +187,19 @@ def test_the_latest_finished_triage_run_decides(tmp_path):
     assert "ALPHA-BODY" in text and "BETA-BODY" not in text
 
 
-# ----- part B6: decision lines of this ticket and its capabilities, an index line per other ticket -
+# ----- the whole decision log, whatever capabilities the ticket names (T-0037) --------------------
 
-def decision_block(store: Path, lines: list[str]) -> str:
-    return ("\n## Decision log (decisions.md): the standing decisions logged against this ticket or naming a "
-            f"capability given in full, read-only. The full log is `{store / 'decisions.md'}`\n\n"
-            + "\n".join(lines) + "\n")
+WHOLE_LOG = "\n## Decision log (decisions.md): standing decisions, read-only\n\n"
 
 
-def decision_index(store: Path, lines: list[str]) -> str:
-    return ("\n## Decision index: decisions not given in full above\n\nThis list is complete: every ticket with "
-            "a decision not given in full above has one line here. Read a ticket's decisions with "
-            f"`grep ' <ticket id> ' {store / 'decisions.md'}`.\n\n" + "".join(f"{x}\n" for x in lines))
-
-
-def test_each_role_gets_its_ticket_s_and_its_capabilities_decisions_and_an_index_of_the_rest(tmp_path):
-    s, r = build(tmp_path, "Capabilities: beta")
-    w = text_of(s, r["spec_writer"])
-    assert decision_block(s, DECISIONS[:2]) in w
-    assert decision_index(s, ["- T-0008 (1 decision, 2026-10-03 to 2026-10-03):",
-                              "- T-0009 (2 decisions, 2026-10-04 to 2026-10-06):"]) in w
-    for role in ("critic", "planner"):
-        text = text_of(s, r[role])
-        assert decision_block(s, DECISIONS[:3]) in text, role
-        assert decision_index(s, ["- T-0009 (2 decisions, 2026-10-04 to 2026-10-06):"]) in text, role
+@pytest.mark.parametrize("caps_line", ["Capabilities: beta", "Capabilities: none"])
+def test_each_role_gets_the_whole_decision_log_and_no_decision_index(tmp_path, caps_line):
+    s, r = build(tmp_path, caps_line)
     for role in ("spec_writer", "critic", "planner"):
-        assert "OTHER-LINE" not in text_of(s, r[role]) and "OTHER2-LINE" not in text_of(s, r[role]), role
-
-
-def test_a_decision_index_line_carries_the_ticket_s_title(tmp_path):
-    s, r = build(tmp_path, "Capabilities: beta", ["2026-10-05 T-0002 later", "2026-10-04 T-0002 earlier"],
-                 others=("Rotate the logs",))
-    assert decision_index(s, ["- T-0002 (2 decisions, 2026-10-04 to 2026-10-05): Rotate the logs"]) \
-        in text_of(s, r["spec_writer"])
-
-
-def test_no_kept_line_leaves_only_the_index_and_no_decisions_source(tmp_path):
-    s, r = build(tmp_path, "Capabilities: none", ["2026-10-04 T-0009 OTHER-LINE logs rotate weekly."])
-    text = text_of(s, r["spec_writer"])
-    assert "## Decision log" not in text and "OTHER-LINE" not in text
-    assert decision_index(s, ["- T-0009 (1 decision, 2026-10-04 to 2026-10-04):"]) in text
-    assert "decisions.md" not in sources(s, r["spec_writer"])
-
-
-def test_every_line_kept_leaves_no_decision_index(tmp_path):
-    s, r = build(tmp_path, "Capabilities: beta", DECISIONS[:2])
-    text = text_of(s, r["spec_writer"])
-    assert decision_block(s, DECISIONS[:2]) in text and "Decision index" not in text
+        text = text_of(s, r[role])
+        assert WHOLE_LOG + "\n".join(DECISIONS) + "\n" in text, role
+        assert "Decision index" not in text and "<ticket id>" not in text, role
+        assert "decisions.md" in sources(s, r[role]), role
 
 
 def test_a_whitespace_only_log_still_adds_nothing(tmp_path):
