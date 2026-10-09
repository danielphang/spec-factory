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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0355-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0355-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0037.1` (branch `factory/T-0037.1`, base `51e2af7f1737f5fc4d9780ea725710dc1112702f`, head `51e2af7f1737f5fc4d9780ea725710dc1112702f`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

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
