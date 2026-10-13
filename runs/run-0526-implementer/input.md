## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
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
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0526-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0526-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0053.1` (branch `factory/T-0053.1`, base `525d73fdd4d3a2d70f66961195f9f9e19ac44c7d`, head `525d73fdd4d3a2d70f66961195f9f9e19ac44c7d`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0053.1

T-0053.1 / Add `docs/standards.md`, the operator's writing and design standards in one self-contained file, point to it from README, and stop `docs/north-star.md` naming the private port (spec-factory #110)
Depends on: none
Parallel-safe: yes

Parent: T-0053, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The standards file holds the approved text
- Where things live names the standards file
- Nothing a role reads names the standards file
- The north-star sentence names a port of the Nanobot chat bot
- The changelog records issue 110 in one entry without a numbering gap
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0053/v2.md`

=== proposal.md
## Problem

The operator has no single written copy of their own standards for specs, design pages, reports
and records. The rules sit in four places: `docs/writing.md` (the twelve writing rules), the
spec-writer prompt (the spec format), a target repository's `AGENTS.md` (report style), and
corrections the operator gave in conversation, which survive only in one session's memory notes.
The operator has written them up as one document and wants it in this repo, as a file that still
makes sense when copied out of it.

The document must not change what any role writes. A role is one of the factory's agents
(triage, spec writer, implementer and so on), each run from a fixed prompt. Every role's prompt
already points at `docs/writing.md`, so editing that file would be a prompt change. Prompt changes
wait until a fixed set of replayed tickets (the golden set) has a baseline to measure them
against. So the standards go in a new file, `docs/standards.md`, that no prompt names.

Two small fixes ride along. This repo is public, and `docs/north-star.md` (the operator's statement
of what the factory is for) names the private port's product; it should say "a port of the
Nanobot chat bot" instead. And README, the repo's current-state page, has a line budget of 1,110
lines that another queued ticket may use up, so the pointer to the new file must not add a line.

## Root cause

Not a defect. The standards were never collected; `docs/north-star.md:21` was written before the
operator ruled that this public repo names no private product.

## Out of scope

- `docs/writing.md`, every `docs/prompts/` file, every role prompt, `agents/**` and `factory/**`
  stay unchanged. Pointing a prompt at `docs/standards.md` is a later prompt change.
- The appendix wording, including where its section 2 differs slightly from `docs/writing.md`'s
  rule headings (for example rule 4, "stating" for "that states"). The operator's text is exact.
- Other public mentions of the private product (see Out-of-scope observations at the end).

## Open questions

none

## Decisions

- The README pointer replaces the `docs/writing.md` row of "Where things live" with one row naming
  both files, so README does not grow. Rejected: a new row, which fits today (1,107 lines) but not
  once T-0052 uses its four lines. Rejected: asking the operator to raise the 1,110 budget, which
  a zero-growth row makes unnecessary.
- The title line stays `# Writing and design standards`, as in the appendix.
- The new requirement fixes the text after the title by its SHA-256. A later edit to
  `docs/standards.md` modifies that requirement in its own spec, where the operator approves the
  new text. Rejected: checking only that the file exists, which would not hold the operator's
  "exactly the text".
- Standing: no role prompt, `docs/writing.md`, `agents/` or `factory/` file names
  `docs/standards.md` until a spec that changes prompts says so. Its requirement is the record.
- The north-star sentence uses the operator's example wording verbatim.
- The changelog entry takes the next free number, whichever of T-0052, #109 or this ticket merges
  first.

## Risk

Documentation only: four files, no code, no prompt. The one shared-line risk is with T-0052 and
#109, which also append to `docs/changelog.md` and edit README; the next-free-number rule and the
zero-growth row absorb either order. #109 is open and not yet in `dev/issues.md`.
Protected paths: none

=== design.md
## Proposed change

A. Create `docs/standards.md` with the text of `.factory/store/requests/T-0053.md` lines 29-174,
   byte for byte, ending in one newline: from the line `# Writing and design standards` to the
   line ending `(commit, run id, ticket), then what was not done.` Copy it with `sed -n '29,174p'`
   rather than retyping it. Check: `sed 1d docs/standards.md | LC_ALL=C shasum -a 256` prints
   `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`.

B. In README's "Where things live" table, replace the `docs/writing.md` row with one row whose
   first cell names `docs/writing.md` and `docs/standards.md`. Suggested text:
   `` | `docs/writing.md`, `docs/standards.md` | The writing standard for every section a person
   reads; the preamble names the runtime's copy. `docs/standards.md` collects it with the
   operator's other writing and design standards in one file that can be copied out of the repo;
   no prompt reads it | `` (one line). Add no line elsewhere in README. Per "Maintaining this
   page", set the status header's date to the merge date if it differs; that changes no line
   count.

C. In `docs/north-star.md`, line 21 becomes exactly:
   `The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).`
   No other line of the file changes.

D. In `docs/changelog.md`, add one entry after the last numbered entry (today 72), before the
   closing "Declined:" paragraph, separated by blank lines like its neighbours. Number it with the
   next free number. It opens `<n>. After issue #110 (2026-10-13), ` and names
   `docs/standards.md`, `docs/writing.md` and `docs/north-star.md`: the standards were spread over
   four places and are now in one self-contained file; no prompt names it, so no role's behaviour
   changes; README's `docs/writing.md` row now names it; the north-star sentence names the target
   as a port of the Nanobot chat bot. It must not name the private product.

Size: about 146 new lines, 3 changed lines. One sub-ticket.

## Tests to change

none. `grep -rn 'north-star\|Where things live\|standards.md' tests/factory` matches nothing.

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: docs/standards.md holds the operator's writing and design standards
`docs/standards.md` SHALL open with a `# ` title line, and the text after that line SHALL be the operator's approved standards text, whose SHA-256 is `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`; a change to that text modifies this requirement in its own spec.

#### Scenario: The standards file holds the approved text
- WHEN `(f=docs/standards.md; echo "title=$(head -1 $f 2>/dev/null | grep -c '^# ') body=$(sed 1d $f 2>/dev/null | LC_ALL=C shasum -a 256 | cut -c1-64)")`
- THEN it prints exactly `title=1 body=010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`

### Requirement: README points to docs/standards.md
README's "Where things live" table SHALL have exactly one row naming `docs/standards.md`.

#### Scenario: Where things live names the standards file
- WHEN `(echo "row=$(sed -n '/^## Where things live/,/^## Related work and history/p' README.md | grep '^| ' | grep -c 'docs/standards.md')")`
- THEN it prints exactly `row=1`

### Requirement: No role prompt reads docs/standards.md
No file under `docs/prompts/`, `factory/` or `agents/`, and not `docs/writing.md`, SHALL name `docs/standards.md`, so adding it changes no role's behaviour; a spec that changes prompts may modify this requirement.

#### Scenario: Nothing a role reads names the standards file
- WHEN `(echo "readers=$(grep -rlF 'standards.md' docs/prompts docs/writing.md factory agents | grep -c .)")`
- THEN it prints exactly `readers=0`

### Requirement: The north star names its target without the private product
`docs/north-star.md` SHALL describe the factory's current target as "a port of the Nanobot chat bot" in its one sentence on whom the factory serves.

#### Scenario: The north-star sentence names a port of the Nanobot chat bot
- WHEN `(echo "line=$(grep -cxF 'The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).' docs/north-star.md) serves=$(grep -c '^The factory serves its own development' docs/north-star.md)")`
- THEN it prints exactly `line=1 serves=1`

### Requirement: The documents record the standards file
`docs/changelog.md` SHALL hold exactly one entry opening `<n>. After issue #110 `, naming `docs/standards.md`, `docs/writing.md` and `docs/north-star.md`, and its entries SHALL stay numbered without a gap.

#### Scenario: The changelog records issue 110 in one entry without a numbering gap
- WHEN `(E=$(grep '^[0-9]*\. After issue #110 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'docs/standards.md' -e 'docs/north-star.md' -e 'docs/writing.md' | sort -u | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)`
- THEN it prints exactly `entries=1 terms=3`, then `CONTIGUOUS`

=== verification.md
## Acceptance

Run from `~/dev/spec-factory` on the merged tree, through the running-code wrapper.

- The standards file holds the approved text → NEW. Today prints
  `title=0 body=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (no file; the
  hash of empty input).
- Where things live names the standards file → NEW. Today prints `row=0`.
- Nothing a role reads names the standards file → REGRESSION. Prints `readers=0` today; guards the
  operator's "no role behaviour changes".
- The north-star sentence names a port of the Nanobot chat bot → NEW. Today prints
  `line=0 serves=1`: the sentence exists but names the private product.
- The changelog records issue 110 in one entry without a numbering gap → NEW. Today prints
  `entries=0 terms=0`, then `CONTIGUOUS`.

Also re-run these current-truth scenarios from harness-docs. Both must still pass:
- "README is at most 1,110 lines": prints `readme=within` today (1,106 lines); must still hold
  whether or not T-0052 merged first.
- "The maintained documents pass git's whitespace check in full": prints `exit=0` today; covers
  the new file, since it checks all of `docs/`.

Run on base at `525d73f`: the five scenarios printed the "today" outputs above, and the two
current-truth scenarios printed `readme=within` and `exit=0`. Run on a scratch prototype of Parts
A to D: the four NEW scenarios printed their THEN outputs, and README stayed at 1,106 lines.

Out-of-scope observations: the private product name still appears in other public tracked files:
`docs/golden.md`, `tests/factory/test_decision_log.py`, and the frozen `dev/build-harness.spec.md`
and `dev/build-harness.plan.md` (`grep -rli` over the repo, excluding `.git` and `.factory`). The
frozen documents may never be edited (standing T-0048 decision). The others belong to the scrub
that #111 owns.
