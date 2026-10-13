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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0528-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0528-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0528-reviewer/wt` (branch `factory/T-0053.1`, base `525d73fdd4d3a2d70f66961195f9f9e19ac44c7d`, head `21f90c4e2d6ef5d8180c954ff3c2ff02711744aa`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

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

## PR description (the implementer's output)

Sub-ticket: T-0053.1 (parent T-0053, approved spec v2, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0053/v2.md`)
Branch: `factory/T-0053.1` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0053.1`, one commit `21f90c4` on base `525d73f`. `main` was still at `525d73f` when I branched, so the changelog's next free number was 73.

## What changed

The operator's writing and design standards now sit in one self-contained file, `docs/standards.md`. No prompt names it, so no role (one of the factory's agents, each run from a fixed prompt) behaves differently. Four files changed: 147 lines added, 2 changed.

- **A.** New `docs/standards.md`, 146 lines. I made it with `sed -n '29,174p' .factory/store/requests/T-0053.md`, so it is a byte-for-byte copy and was not retyped. It starts at `# Writing and design standards` and ends at `  (commit, run id, ticket), then what was not done.` plus one newline. `sed 1d docs/standards.md | LC_ALL=C shasum -a 256` prints `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`, which is the hash the spec requires.
- **B.** `README.md`: in "Where things live", I replaced the `docs/writing.md` row (line 1027) with the spec's suggested one-line row, which names both `docs/writing.md` and `docs/standards.md`. README is still 1,106 lines. The status header already said "as of 2026-10-13", today's date, so I left it alone.
- **C.** `docs/north-star.md` line 21 now reads exactly `The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).` No other line changed.
- **D.** `docs/changelog.md`: I added entry 73, which starts `73. After issue #110 (2026-10-13), `. It sits after entry 72 and before the closing "Declined:" paragraph, with a blank line on each side. It says:
  - the standards were spread over four places;
  - `docs/standards.md` now holds them in one self-contained file;
  - no prompt, `docs/prompts/` file or `docs/writing.md` names the new file, so no role's behaviour changes;
  - README's `docs/writing.md` row now names it;
  - the north-star sentence calls the target a port of the Nanobot chat bot;
  - two options were rejected: editing `docs/writing.md` (that would be a prompt change) and adding a new README row (it would not fit the line budget).

  `git diff | grep '^+' | grep -i lionbot` matches nothing, so no added line names the private product.

## Acceptance results

I ran every command from the worktree through the running-code wrapper. "Before" is base `525d73f`; "after" is commit `21f90c4`.

| Scenario | Kind | Before | After | What "after" shows |
|---|---|---|---|---|
| The standards file holds the approved text | NEW | `title=0 body=e3b0c442…b855` | `title=1 body=010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e` | The file has a `# ` title, and the text after it matches the approved hash. |
| Where things live names the standards file | NEW | `row=0` | `row=1` | Exactly one row in the table names the file. |
| Nothing a role reads names the standards file | REGRESSION | `readers=0` | `readers=0` | No prompt, `docs/writing.md`, `factory/` or `agents/` file names it. |
| The north-star sentence names a port of the Nanobot chat bot | NEW | `line=0 serves=1` | `line=1 serves=1` | The sentence now has the new wording, and it is still the only "serves" sentence. |
| The changelog records issue 110 in one entry without a numbering gap | NEW | `entries=0 terms=0`, `CONTIGUOUS` | `entries=1 terms=3`, `CONTIGUOUS` | One entry names all three files, and the numbering still has no gap. |
| README is at most 1,110 lines (current truth) | re-run | `readme=within` (per the spec) | `readme=within` | README is still 1,106 lines. |
| The maintained documents pass git's whitespace check in full (current truth) | re-run | `exit=0` (per the spec) | `exit=0` | This covers the new file, because the check reads all of `docs/`. |

All four NEW scenarios printed the spec's "today" output before the change, so the spec matched the code.

Gate commands, each run exactly as written:
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `584 passed in 141.51s (0:02:21)`, exit 0.

## Tests added/changed

None. This is a documentation-only change, and the spec's acceptance checks are shell scenarios. The spec lists no tests to change, and `grep -rn 'north-star\|Where things live\|standards.md' tests/factory` finds nothing there.

## Known gaps and uncertainties

- The changelog wording is mine, not the operator's. It makes three claims about the rest of the repo, and I checked only the first:
  - The golden set (the fixed tickets in `docs/golden.md` that every prompt change is replayed on) has no baseline yet. I took this from the spec's Problem section. README's `docs/golden.md` row describes the file that way, but I did not open `docs/golden.md` to confirm the baseline table is empty.
  - Every role prompt names `docs/writing.md`. I took this from the spec. The preamble of my own system prompt does name it.
  - Rule 4 ("stating" for "that states") and the other small differences between the appendix's section 2 and `docs/writing.md` are kept as the operator wrote them. The spec puts this out of scope.
- Part D's order rule: if T-0052 or issue #109 merges into `main` before this branch and takes number 73, this entry must become 74 when the branch is merged with `main`. The numbering scenario would catch a duplicate 73.

## Out-of-scope observations

The private product's name still appears in other tracked public files. The spec lists them: `docs/golden.md`, `tests/factory/test_decision_log.py`, and the frozen `dev/build-harness.spec.md` and `dev/build-harness.plan.md`. Issue #111 owns that cleanup. I did not touch them.

## Protected paths

None touched. The diff changes only `README.md`, `docs/standards.md` (new), `docs/north-star.md` and `docs/changelog.md`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every scenario and both gates ran on commit `21f90c4` and gave the spec's expected output, and the standards text matches the approved SHA-256.
ESCALATIONS: none

## Diff `525d73fdd4d3a2d70f66961195f9f9e19ac44c7d...21f90c4e2d6ef5d8180c954ff3c2ff02711744aa`

diff --git a/README.md b/README.md
index e6dc6ba..026a206 100644
--- a/README.md
+++ b/README.md
@@ -1024,7 +1024,7 @@ has not been tried, is in `docs/design.md`, "Running on another agent host".
 | `docs/principles.md` | The fourteen learned principles, each with its incident, citation and implementing mechanism |
 | `docs/decided-against.md` | Approaches tried or offered and dropped, with the evidence and what would reopen each |
 | `docs/golden.md` | The fixed golden set every prompt-change replay runs, with each entry's base and known catch, the baseline table, and the rule for changing the set |
-| `docs/writing.md` | The writing standard for every section a person reads; the preamble names the runtime's copy |
+| `docs/writing.md`, `docs/standards.md` | The writing standard for every section a person reads; the preamble names the runtime's copy. `docs/standards.md` collects it with the operator's other writing and design standards in one file that can be copied out of the repo; no prompt reads it |
 | `docs/coding.md` | The coding standard for the implementer and code reviewer; their prompts name the runtime's copy |
 | `dev/` | The issue index (`dev/issues.md`), kept live; and the build spec, its plan and the P0 walking skeleton, frozen as history from building the factory |
 | `factory/` | The harness package: the store CLI, its role prompts and its two workflow scripts (`factory/workflows/`) |
diff --git a/docs/changelog.md b/docs/changelog.md
index e686eb2..4e0d323 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -76,4 +76,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 
 72. After issue #101 (2026-10-11), where the operator read two long maintained documents at every spec gate and parts of README were false: README explained several mechanisms two or three times, said six features had not yet run on a real ticket when the stores' logs showed they had, and kept project history; and the briefing asked every design change to keep `dev/build-harness.spec.md` in step though it describes a design the code never had. The three `dev/` build documents, `dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md`, are frozen as history: each gains a header at line 3 and is otherwise as it was at `7231670`, and no change updates them; `.factory/context.md` and README's `dev/` row say so, and the briefing no longer names them in a design change's conventions. `dev/issues.md` stays the live issue index. README's claims now match the logs: the one-sub-ticket path has run on real tickets on both targets (16 tickets from T-0031 to T-0051 here, five on the Nanobot store); the driver took T-0035 and T-0036 through intake and the build on the Nanobot target; a gate command's path skip is recorded for T-0036.1; the re-plan after a re-spec fired for T-0031; the protected-path refusal at merge fired for T-0044.1, which the operator accepted with `--accept-paths`; every run has its scratch directory; and a run with no output is run once more, not recorded as killed. The tripwire, the sibling-tests check and the drift check's sibling-merge exception still say they have not yet fired or run, and the effort entry that neither target sets it. README's rule for its Built list now admits a thing once it is built and tested and asks its entry to say whether it has yet run on a real ticket, and `docs/design.md` line 3 drops its own date and points here. Each mechanism has one home in README: the live-store fence under "Where a human decides", the driver and its same-ticket guard under its how-to, the final check's skip under "The build workflow, step by step", the store branch under "How the factory uses git", and other agent hosts only in `docs/design.md`; the Built entries become short pointers, "Not built" one paragraph that repeats nothing under "Where this can go", and the glossary points to "Where it runs" and defines a protected path in its own row. History moved out of README: the overlap of 41 and 11 runs of different tickets in the two stores on 2026-10-04, the double count `factory/cost.py` once made (entry 70), the two stores' moves onto their store branch with `factory store migrate`, the page's origin story and the regeneration pass's two past catches, a target described as cut over that was not and a bound stated on the wrong case; "Related work and history" keeps every issue reference beside what it names. `docs/design.md`'s model-per-role paragraph points to principle 4 and entry 70 for the first `factory stats` figures, which it no longer repeats; they were, up to 2026-10-07 12:00 UTC over both stores, the code reviewer (Fable) changing an outcome in 4 of 94 runs with 3 BLOCKING findings for 94,860,442 context tokens over 99 runs, the critic (Fable) in 19 of 84 for 66,027,675, the verifier in 8 of 108 on Opus for 232,945,610 and in 1 of 5 on Fable for 5,189,563, and the implementer (Opus) in 18 of 111 for 372,507,821 over 114 runs. README is held to at most 1,110 lines; a later change that needs more raises the bound in its own spec. The `harness-docs` current truth is rewritten so each check keeps passing after later changes: a check finds a changelog entry by its opening words, `<n>. After issue #<k> `, and never by the last line or an entry count; no check measures what one change left untouched against `main` or a fixed commit, and the two requirements made only of such checks are removed; whitespace is checked once over the maintained documents in full, while the instance's gate command still checks each change; the frozen build spec's checks, and principle 2's retired status clause, are dropped. Rejected: moving the build documents to `dev/archive/`, which breaks the `Parent:` links and every path cited to them; moving the built but unfired features under "Where this can go", which is for intended work; bumping `docs/design.md`'s date, which every later change would also have to do; padding the cuts to the requested 150 lines, against about 90 that one home per mechanism gives; and splitting the work into four sub-tickets, which would all edit README.
 
+73. After issue #110 (2026-10-13), where the operator had no single written copy of their own standards for specs, design pages, reports and records: the rules sat in four places, `docs/writing.md`, the spec writer's prompt, a target repository's `AGENTS.md`, and corrections the operator gave in conversation, which survived only in one session's memory notes. A new file, `docs/standards.md`, holds the operator's text of them in one place, self-contained so that a copy taken out of the repo still makes sense. No role prompt, no `docs/prompts/` file and not `docs/writing.md` names it, so no role's behaviour changes; pointing a prompt at it is a later prompt change, which waits until the golden set, the fixed tickets in `docs/golden.md` that every prompt change is replayed on, has a baseline. README's `docs/writing.md` row in "Where things live" now names `docs/standards.md` too, so README gains no line. `docs/north-star.md` now names the factory's current target as a port of the Nanobot chat bot, since this public repo names no private product. Rejected: editing `docs/writing.md`, which every role prompt names, so that edit would be a prompt change; and a new README row, which would not fit README's 1,110-line bound once other queued changes use their lines.
+
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/north-star.md b/docs/north-star.md
index e64cfd8..0b1d85e 100644
--- a/docs/north-star.md
+++ b/docs/north-star.md
@@ -18,7 +18,7 @@ Success is measured as:
 - tokens and wall time per change;
 - defects that escape to the target, and reverts.
 
-The factory serves its own development (spec-factory) and its targets (today, the Lionbot v3.5 port).
+The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).
 
 ## What it will not trade away
 
diff --git a/docs/standards.md b/docs/standards.md
new file mode 100644
index 0000000..09732d9
--- /dev/null
+++ b/docs/standards.md
@@ -0,0 +1,146 @@
+# Writing and design standards
+
+What this is: every standing instruction for how specs, design pages, reports and records are
+written across the spec factory and the repositories it builds, collected into one file so the
+standards can be recreated without the repos, the harness or any one session's memory. Who it is for:
+the operator, and any agent asked to write for the operator.
+
+Sources, in order of authority: `docs/writing.md` (the twelve rules), the factory's
+spec-writer prompt (the reader and the spec format), each target repository's `.factory/context.md`
+(that repo's reader), the target repository's `AGENTS.md` (report style), and the operator's own
+corrections given in conversation 2026-09-16 to 2026-09-29, which until now lived only in a
+session's memory notes. Where a rule's origin matters it is dated.
+
+## 1. The reader
+
+Deeply technical: knows databases, tables, locks, RPCs, agents and context windows. New to this
+system: has not read its design document and does not know its function, command, file or state
+names, or why a particular line of code exists. A reader who stops after the first paragraph can
+say what is wrong and for whom.
+
+A target repository's `.factory/context.md` can narrow the reader: for example, the operator, who
+knows that codebase well but not the pipeline's vocabulary. Gloss harness terms (pinned, parked, parent-close, archive,
+exit codes) on first use. File-and-function detail goes under Evidence and Root cause, never in
+the Problem section.
+
+## 2. The twelve rules (from `docs/writing.md`)
+
+Each rule has a check you can run on your own text before handing it in.
+
+| # | Rule | Check |
+|---|---|---|
+| 1 | The first paragraph says what is wrong, or what this is, and for whom. | Stop after paragraph one; can you name the problem and who has it? |
+| 2 | A term specific to this system is glossed at first use with what it does or why it exists. General technical concepts are not glossed. | Underline every made-up name; its first use says what it does. |
+| 3 | One idea per sentence; no parenthetical holds a second idea. | Delete each parenthetical; if a claim is lost, it needs its own sentence. |
+| 4 | A diagram comes after the words needed to read it, with a caption stating its one claim. | Every box and arrow is named in the text above it. |
+| 5 | A command is shown with what its output shows. | Every quoted output is followed by what it means for the claim. |
+| 6 | Project-internal references are introduced, or moved to a closing note. | Each ticket id, issue number, decision id, session or person is introduced by what it is, or sits in a closing note. |
+| 7 | Lead with the problem; the mechanism comes second. | First sentence: what is broken or what the reader must do. |
+| 8 | State a choice and the alternative rejected; do not write an essay defending it. | One sentence for the choice, one per rejected alternative and why. |
+| 9 | One name per concept: no synonyms, no name shared by two concepts. | Each term keeps the name it got at first use. |
+| 10 | One mode per section: explanation, how-to and reference do not share a heading. | Label each section; a section with two labels is split. |
+| 11 | A heading states what is under it. | Read only the headings; each predicts its section. |
+| 12 | Parallel facts go in a table. | Three or more items with the same kinds of fact become rows, one column per kind. |
+
+Two worked examples, kept because they are the ones most often violated:
+
+- Rule 2, before: `--accept-harness` appeared in a diagram with no statement of what requires it.
+  After: "Each target repository runs only the harness commit it has accepted, recorded in its
+  `harness.lock`. When the harness is upgraded, the operator accepts the new commit with
+  `--accept-harness <commit>`; until then the harness refuses to run there."
+- Rule 7, before: "Stale branch base, which is a harness/process issue. The verifier was given base
+  `20849b6`, but the head forks at `cdb1c67`…" After: "The test gate cannot pass on this branch: it
+  was cut from `main` before the change it depends on merged. Decide: update the branch and
+  re-verify, or accept the trial-merge evidence."
+
+## 3. Operator corrections given in conversation
+
+These are rules the operator stated directly. They apply to replies, specs, pages, commit messages,
+ledgers and comments alike.
+
+| Date | Rule | The operator's words, and why |
+|---|---|---|
+| 2026-09-16 | Direct and compact. Lead with the answer. Facts as short declaratives or a table. Keep the caveat, tradeoff or number that changes a decision; drop wrapping and narration. | "make your response style more direct, less mannered prose, less verbose but not dropping nuance." |
+| 2026-09-17 | The same for everything written. State the fact and its source (command, SHA, file:line); reasoning goes in the commit message once; a code comment states the invariant, not the history. | "[a spec] at 561 lines is crazy work … an entire essay for PATH composition is a place we should not be." Everything written is read back many times into large contexts; a verbose doc is paid for at reads × later calls. |
+| 2026-09-17 | Length budgets: a spec's normative half ≤150 lines; a profile ≤100; a cold-read record ≤60; a notes cell ≤3 sentences; a Done entry is the fixed fields, one line each. Do not rewrite closed specs for style; trim when opened for another reason. | The budgets were in an earlier maintenance-workflow document that no longer has them, so this table is now their record. |
+| 2026-09-24 | Every decision id or obligation id carries a short parenthetical reminder of what it decides, on every mention. | "A bare id makes the message unreadable without the register open." |
+| 2026-09-24 | Scope one unit per message: one spec, one ticket, one section. No batch-wide sweeps. | |
+| 2026-09-29 | Report findings as what they mean first, mechanism second. A decision row that carries a recommendation is taken by default, recorded and reported; ask only when there is no lean or the choice is irreversible. Never re-ask after a go. | |
+| ongoing | Pressure-test a proposal before presenting it: the root why, the failure modes, and an independent counter-proposal. State a concern in a sentence or two, then deliver. | |
+
+The trap that catches a writer: copying the shape of the neighbouring record. Older entries were
+written before the budgets and are long; patterning a new one on them breaks the rule even when the
+rule was read the same session. Write to the rule, not to the file's median entry.
+
+## 4. Reports and records (from the target repo's `AGENTS.md`)
+
+- A report leads with what changed for the operator and what it cost; paths and mechanisms go
+  below.
+- Before any message that claims done or verified, ground it: state from commands, every quoted
+  identifier read back, every figure from the command that produced it. Before saying a check
+  passed, prove it ran on the claimed tree in a fresh environment.
+- Ledgers and command logs are written for the cold reader: explicit why, not just what.
+- No ledgers where the store is the record: the factory's store log replaces TASKS.md and Done
+  entries.
+
+## 5. The spec format (from the spec-writer prompt)
+
+A spec is a change folder: `proposal.md`, `design.md`, `specs/<capability>/spec.md`, `tasks.md`.
+
+| Section | Contents |
+|---|---|
+| Problem | What is wrong or missing, for whom, in plain words for the operator at the spec gate; each term of art glossed on first use; detail goes below. |
+| Evidence | Actual output, logs, metrics, repro steps; each quoted output followed by what it means. |
+| Root cause | Files and functions if known; "unknown" is allowed. |
+| Out of scope | What must not change. |
+| Open questions | none, or a list. |
+| Decisions | none, or one line per design call, including each answered open question, with the alternative rejected. |
+| Risk | Blast radius; protected paths declared on one line the merge gate reads. |
+| Operator steps | Optional: actions on live or protected state only the operator can perform, after merge. |
+| Proposed change (design) | Lettered parts A, B, C, specific enough to follow. |
+| Tests to change | none, or the existing tests the change breaks, and why. |
+| ADDED / MODIFIED / REMOVED Requirements | The delta on the capability spec, one part per capability changed; reuse a current-truth capability where the behaviour already lives. |
+
+Anti-Goodharting: the critic scores against a rubric; satisfy each item's intent, not its wording.
+A spec padded with generic criteria to look thorough is a failed spec. On revision, answer each
+critic finding with FIXED and what changed.
+
+## 6. Design pages and reports delivered as pages
+
+Used for two earlier pages, a feature design and a cleanup report. These conventions were applied
+but never written down before this file.
+
+- **Open with what changes for the reader and what it cost.** First paragraph: the outcome in the
+  reader's terms, the date, and what was not lost. A one-line meta row under it: where it was
+  applied, how it was rehearsed and reviewed, how it is reverted.
+- **Figures block next.** Three or four numbers that justify the page, each with a one-line label;
+  a "live check" line under them quoting the command or log line that proves the headline number.
+- **"One step left for you" callout** when the page asks the operator to do something: the exact
+  edit, the exact command, and why the writer could not do it (for example, a safety check
+  blocked the edit).
+- **What changed, as numbered steps**, each with its commit id as a tag, each step revertible on
+  its own.
+- **What the review caught**: a short register of findings an independent critic raised before the
+  change went live, each with its category and what was done.
+- **Not done, and why**: deferred items with their reason, stale content left in place, and the
+  decisions still open, each named by its id and a reminder of what it decides.
+- **Decision register** for a design page: one row per decision, id, the question, the
+  recommendation, the alternative rejected; a decision with a recommendation is taken by default.
+- **How to undo**: the exact commands, the tag or backup that marks the state before, and whether
+  a restart is needed.
+- **A full table at the end** for anything with many rows (every skill, every job), with filters
+  and a search box, and a key paragraph defining each category used in the table.
+- **Privacy**: no chat contents, phone numbers, messaging-platform user ids or private people's
+  names on a page, in a spec, a test, a commit or a public post. Neutral roles ("the requester",
+  "a group member") where a role is needed. Nothing public references a private repository.
+- Pages follow the twelve rules above; a page is not a place to escape them.
+
+## 7. Comments, issues and messages to peers
+
+- A comment answering a question on a page answers the question in the first sentence, then
+  grounds it (file, command, log line), then says what was changed because of it, if anything.
+- An issue filed from an agent's run record states: asked, did (with evidence), should have, impact,
+  and an optional one-line possible fix marked as a guess. Primary evidence only; a summary stream
+  is never a citation.
+- A message to a peer session leads with the one fact the peer must act on, then the identifiers
+  (commit, run id, ticket), then what was not done.
