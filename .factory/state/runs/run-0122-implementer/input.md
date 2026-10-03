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
  `harness.lock`, and closed records (`answers/`, `green-pilot/`). Its live store is still
  `intake/state/` until an operator step moves it.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

Green, the Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3`), is instance A: it
still runs its own in-tree copy of the harness, from which this repo's harness was imported. Read
it only to observe what a fix does there today; never write there, and never copy its test names,
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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0122-implementer/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0014.1` (branch `factory/T-0014.1`, base `431e3492d977c01f5ac3252f94b6f40f08b6c043`, head `c64183ac7d10f6286136a0b419764d05202736fc`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## This is a conflict run
The merge gate refused your branch: head does not contain main. The integration branch moved after you branched. Merge it into your branch, resolve any conflict, re-run the gates, commit, and add one note on the resolution to the PR description. Change nothing else.

## Sub-ticket T-0014.1

ST-1 / Add rules 9–12 and code counterpart lines to the writing standard

Parent: the approved spec v3 for this change (proposal.md, design.md,
specs/writing-standard/spec.md, verification.md). Read it for context. Do NOT implement parts
outside this sub-ticket.

Depends on: none
Parallel-safe: yes (it is the only sub-ticket)

Scope: design.md parts A, B and C, all in `docs/writing.md`, additions only.
- A. The intro sentence directly after line 19, as a continuation of that paragraph.
- B. One `Code counterpart:` line directly before the `Before (` line of rules 1, 2, 3, 5, 6 and
  7, with the exact text from design.md's table. Rules 4 and 8 get none.
- C. Rules 9–12, with the exact wording from design.md, between rule 8's After paragraph and
  the closing `README.md` line, with a blank line after each rule. Rewrapping is allowed at no more
  than 100 characters; wording is fixed by the gate.

Acceptance (every WHEN runs from `~/dev/spec-factory`; commands are verbatim from the parent):
1. twelve numbered rules with the four new headings → NEW.
   WHEN `echo "rules=$(grep -o '^## [0-9]*\.' docs/writing.md | tr -dc '0-9\n' | paste -sd, -) new=$(grep -c -i -E '^## 9\. One name per concept|^## 10\. One mode per section|^## 11\. A heading states what is under it|^## 12\. Parallel facts go in a table' docs/writing.md)"`
   THEN `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4`
2. each new rule has one check, one before, one after → NEW.
   WHEN `awk '/^## [0-9]+\./{n=$2+0} n>=9 && /^Check: /{c[n]++} n>=9 && /^Before \(/{b[n]++} n>=9 && /^After: /{a[n]++} END{for(i=9;i<=12;i++) printf "%d:%d%d%d ", i, c[i], b[i], a[i]; print ""}' docs/writing.md`
   THEN `9:111 10:111 11:111 12:111` (trailing space allowed)
3. example phrases are in the standard and match the README → NEW.
   WHEN `w=; r=; for h in "installed harness" "the pinned checkout of the harness that runs tickets" "Accepting a harness revision" "Upgrading the runtime" "The human's stops" "Where a human decides"; do w="$w$(tr '\n' ' ' < docs/writing.md | grep -qF "$h" && echo y || echo n)"; r="$r$(tr '\n' ' ' < README.md | grep -qF "$h" && echo y || echo n)"; done; echo "writing=$w readme=$r"`
   THEN `writing=yyyyyy readme=nyyyny`
4. counterpart lines on the agreed rules, in place → NEW.
   WHEN `awk '/^## [0-9]+\./{n=$2+0; ck=0; bf=0} /^Check: /{ck=1} /^Before \(/{bf=1} /^Code counterpart: /{k[n]++; if (!ck || bf) bad++} END{s=""; for(i=1;i<=12;i++) s=s (k[i]+0); print "intro=" (k[0]+0) " rules=" s " misplaced=" (bad+0)}' docs/writing.md`
   THEN `intro=0 rules=111011101111 misplaced=0`
5. under budget, nothing removed, clean whitespace → REGRESSION.
   WHEN `echo "lines=$(grep -c '' docs/writing.md) wide=$(awk 'length($0)>100' docs/writing.md | grep -c '') removed=$(git diff -U0 e703c1b -- docs/writing.md | grep -v '^--- ' | grep -c '^-') ws=$(git diff --check e703c1b -- docs/writing.md >/dev/null && echo clean || echo errors)"`
   THEN `wide=0 removed=0 ws=clean`, and `lines=` below 140 (the parent's scratch build gave 131)
6. only the standard changes → NEW. Run on the change branch, before merge.
   WHEN `echo "changed=[$(git diff --name-only "$(git merge-base main HEAD)" HEAD -- . ':(exclude).factory' | paste -sd, -)]"`
   THEN exactly `changed=[docs/writing.md]`
7. the standard's existing tests still pass → REGRESSION.
   WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_writing_standard.py 2>&1 | tail -1`
   THEN the last line reports `5 passed` and no failures

Intermediate check (NEW, for the reviewer, not a parent scenario): the inserted text matches
design.md word for word. Criteria 1–4 count lines and phrases but do not compare wording, and
the gate fixed the wording. The reviewer joins each inserted block's wrapped lines and compares
it with the design.md text for parts A, B and C; any wording difference fails the ticket.

Tests to change: none
Protected paths: none
Out of scope:
- Every file other than `docs/writing.md`, including `README.md` and its "Maintaining this page"
  summary, `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, the role prompts and the
  critic and reviewer rubrics.
- Any edit, move or removal of an existing line in `docs/writing.md`, including rewording rules
  1–8.
- Rewriting any existing document to the new rules, and rules for research items 1, 5 or 7.
- Operator steps 0 (the rewrite and comprehension acceptance test) and 1 (moving the runtime
  checkout at `~/dev/spec-factory-harness` to the merge commit). They are the operator's, after
  merge; the implementer does not touch the runtime checkout.

## Shared plan context (from the plan; applies to every sub-ticket)

One sub-ticket. The whole change is additions to one file, `docs/writing.md`, about 45 lines,
and no test or protected path is touched. Rejected: splitting it into parts A+B (counterpart
lines on existing rules) and part C (four new rules). Part A's intro sentence promises counterpart
lines on new rules too, and the counterpart scenario only reaches its THEN once both parts land.
A split would leave a half-true standard on `main` between merges and buy no easier review.

Baseline checked on `~/dev/spec-factory` at `d8e1ada` (the spec was verified at `967ee77`):
`git log 967ee77..HEAD -- docs/writing.md README.md` prints nothing, so neither file has drifted.
`docs/writing.md` is 86 lines with rules 1–8 at lines 21, 29, 38, 46, 54, 62, 70, 78. Each rule
has exactly one `Before (` line (lines 23, 32, 40, 48, 56, 65, 72, 80), which is where part B
anchors. Line 19 ends "example taken from the factory's own writing, and its rewrite." and the
last line is "`README.md` is a worked example of these rules applied to a whole page.", which are
part A's and part C's anchors. The phrase scenario prints `writing=nnnnnn readme=nyyyny`, and
`tests/factory/test_writing_standard.py` prints `5 passed in 0.41s`.

---

## Parent spec (v3, pinned)

=== proposal.md
## Problem

The factory's agents (each a "role": triage, spec writer, critic and so on) are all told to follow
one page, the writing standard (`docs/writing.md`), whenever they write something a person will
read and decide on. That page has eight rules, and none of them is about names. So a document can
call one thing by four different names and still pass every check the standard offers. The
project's own overview page did exactly that in draft. It used "the harness", "the runtime", "the
installed harness" and "the in-tree copy" for overlapping things, and a first-time reader could not
tell them apart. Three other rules from the same review are also missing: keep each section to
one kind of writing, make each heading say what is under it, and put parallel facts in a table.
Each of the four was applied by hand to the overview page, but the standard never tells a role to
apply it. A role reviewing a spec or a PR description therefore has no rule to cite when those
problems appear.

This change adds the four rules to the standard. It also gives each rule, old and new, one line
naming the code-design principle it matches, such as "single responsibility". Agents already know
those principles, so naming one is the cheapest way to make a rule recognisable. A rule with no
honest match gets no line. Only `docs/writing.md` changes.

## Evidence

- The standard has eight rules and nothing about names. `grep -n '^## [0-9]' docs/writing.md`
  prints eight headings, at lines 21, 29, 38, 46, 54, 62, 70 and 78. Rule 2 (line 29) asks for a
  term to be explained at its first use. It does not ask for the same term to be used afterwards.
  `wc -l docs/writing.md` prints `86`, which leaves room under the requester's 140-line budget.
- The four rules come from the operator's research comment on issue 23 (`gh issue view 23
  --comments`, first comment). That comment lists ten writing rules with their sources (the Google
  and Microsoft style guides, Diátaxis, design-doc templates). Its items 2, 3, 4 and 8 are the
  four requested rules: one mode per section, one name per thing, headings that state their
  content, and tables for parallel facts. Each item quotes its own before and after from the
  overview page.
- The after-state of each example is in `README.md` today:
  - The terms table (line 61) has a `runtime` row (line 74): "the pinned checkout of the harness
    that runs tickets".
  - "## Where it runs" (line 150) is followed by the how-to subsections "### Accepting a harness
    revision" (line 202) and "### Upgrading the runtime" (line 219).
  - The heading "## Where a human decides" is at line 273.
  - The eight roles are a Role / Does / Model table (lines 31–40).
- The before-state exists only as quoted in the issue 23 comment. A check that joins wrapped lines
  and searches for each example phrase printed `writing=nnnnnn readme=nyyyny`. In that output, the
  standard holds none of the six example phrases. The README holds the four after-phrases and
  neither before-phrase ("installed harness", "The human's stops").
- Nothing else depends on the rule count. No document names it: `grep -rn -i 'eight rules'
  docs/design.md dev/build-harness.spec.md README.md docs/prompts factory agents` prints nothing.
  The standard's only test file, `tests/factory/test_writing_standard.py`, checks that the file
  exists and is named in every role's prompt, not what it says. It passes today: `5 passed`.
- The prompts refer to the standard by its path, not by quoting it. The preamble says "the
  writing standard at {writing standard}". The critic and reviewer prompts say "the writing
  standard the preamble names". So new rules reach every role without a prompt change.
- The roles read the standard from the runtime, not from this checkout. The runtime is a second
  checkout of this repo, at `~/dev/spec-factory-harness`, pinned to one commit; the factory runs
  every ticket from it (`README.md` line 156). The runtime's copy of `docs/writing.md` is the one
  the preamble names (`README.md` line 349). So the new rules reach the roles only once the runtime
  is moved to a commit that has them.
- Moving the runtime to this change needs no re-acceptance. Each repo that uses the factory keeps
  a harness lock (`.factory/harness.lock`): the commit of harness code it has agreed to run. The
  harness (the code that runs the roles and keeps their records) refuses to work until the lock
  matches. The commit it compares is the last one that touched `factory`, `bin/factory`, `agents`,
  `pyproject.toml` or `uv.lock` (`HARNESS_PATHS` and `harness_revision` in `factory/instance.py`,
  lines 33 and 98). Today the lock, the runtime's harness revision and this checkout's harness
  revision are all `e703c1b`, although the runtime's own HEAD is `43a01dd`. That shows a commit
  outside those paths does not move the revision. A change to `docs/writing.md` is outside them.

## Root cause

The standard was built from eight of the ten items in the research comment (`docs/writing.md`,
added in `e703c1b`), and the other four requested items were not carried over. No code is
involved.

## Out of scope

- Every other file. That includes `README.md` and its "Maintaining this page" summary of the
  standard, `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, the critic's rubric item 6 and
  the reviewer's check 8 (both already apply the whole standard), and the role prompts.
- The wording of rules 1–8, apart from adding one line to six of them. Their headings, checks and
  examples stay byte-for-byte the same.
- Rewriting any existing document to the new rules.
- A rule for research item 5 ("cut announcement sentences"), item 1 (status header first) or item
  7 (caveats beside what they qualify).

## Open questions

none

## Decisions

- The new rules are numbered 9–12, after the existing eight, in the request's order. Existing rules
  are not renumbered, because other text cites them by number ("rule 2", "rule 6"). The change only
  adds lines and removes none.
- There are four new rules, not five. The requester's mapping table includes a row "Prose says
  why, not what the code does". No rule by that name exists. It comes from the operator's second
  comment on issue 23, about how to write a spec's Evidence. It can become a rule of its own in a
  separate request.
- Rule 9 also forbids one name standing for two things, not only two names for one thing. The
  requester mapped it to Clean Code's "don't pun", which is that second half. Without it, the
  counterpart line would claim more than the rule says.
- The counterpart line starts with `Code counterpart:` and sits after the rule's Check line and
  before its Before line. One extra intro sentence says what the line is for and that a rule may
  have none.
- The mapping, as confirmed or corrected from the requester's table:
  - Rules 2, 3, 6 and 7 keep the requester's mapping: declare before use; a function does one
    thing; information hiding; interface before implementation.
  - Rules 9, 10 and 11 keep it too: pick one word per concept and don't pun, plus ubiquitous
    language (Evans); single responsibility; intention-revealing names and Fowler's Rename.
  - Corrected: rule 12 is mapped to table-driven methods (McConnell, Code Complete) instead of
    "data, not control flow". It is the same idea under a name with a source an agent will know.
  - Added: rule 1 maps to a docstring's summary line (PEP 257). Rule 5 maps to "no magic numbers":
    raw output quoted without its meaning is a bare value with no name.
  - None for rule 4 (diagrams after the words, with a caption) or rule 8 (state the choice and
    what was rejected). No code-design principle matches either without stretching.
- Rule 12's check uses a threshold of three or more parallel items. Two items read fine in a
  sentence. Every table on the overview page has at least four rows.

## Risk

Every role reads `docs/writing.md` for its human-facing sections, so a wrong or vague rule
misleads all of them at once. That is why the gate reads the six counterpart lines for existing
rules (design.md, part B) and the four new rules with their own counterpart lines (design.md, part
C) word for word. The file is not a protected path on this instance, and no protected path is
touched. The change reaches running roles only after the operator moves the runtime (see Operator
steps).

## Operator steps

1. After merge, move the runtime to the merge commit, between tickets. The runtime is the second
   checkout of this repo at `~/dev/spec-factory-harness`, pinned to one commit; the factory runs
   every ticket from it, and roles read the writing standard from it. Run
   `git -C ~/dev/spec-factory-harness checkout --detach <merge sha>`, then `uv sync --frozen` in
   that directory. Until this step, roles keep reading the old eight rules. No acceptance step
   follows: the harness lock, the pin each repo keeps on the harness code it agreed to run, covers
   only the harness code paths, not `docs/`, so this merge does not change what it pins and no
   `--accept-harness` run is needed.
0. **Before step 1: the operator's acceptance test (operator, at the gate, 2026-10-03).** The merge changes nothing until the runtime moves, so the acceptance happens here, not in the merge checks.
   - **Rewrite.** A fresh agent rewrites a fixed sample under the merged `docs/writing.md`. The sample is T-0012's spec v3 Problem, Evidence and Decisions, one PR description, and one ESCALATIONS item. A control agent rewrites the same sample under the pre-merge standard.
   - **Comprehension.** A fresh agent that sees only one version answers a fixed question set about it: what is protected, what the operator does after close, which part depends on which. Answers from the original, the control and the new rewrite must agree on every fact.
   - **Operator.** The operator reads a side-by-side page (original, control, new) with the comprehension diff, and approves. That approval is this ticket's acceptance. Only then does step 1 run. A rejection goes back as a new ticket; it does not revert the merge, which is inert until the runtime moves.

=== design.md
## Proposed change

One file, `docs/writing.md`. Additions only: no existing line is edited, moved or removed. Wrap
at no more than 100 characters, as the file does today (its widest line is 99).

**A. Intro sentence.** Directly after line 19 ("example taken from the factory's own writing, and
its rewrite."), add as a continuation of that paragraph:

```
Where a rule matches a code-design principle, a `Code counterpart:` line names it; a rule with
no honest counterpart has none.
```

**B. Counterpart lines on existing rules.** In each rule below, insert one line directly before
its `Before (` line, which puts it after the rule's Check text. Rules 4 and 8 get none.

| Rule | Line to insert |
|---|---|
| 1 | `Code counterpart: a docstring's summary line (PEP 257), which says what a thing is for first.` |
| 2 | `Code counterpart: declare before use.` |
| 3 | `Code counterpart: a function does one thing (Clean Code).` |
| 5 | `Code counterpart: no magic numbers; a bare value gets a name that says what it means.` |
| 6 | `Code counterpart: information hiding; internal detail stays behind the interface a reader uses.` |
| 7 | `Code counterpart: interface before implementation; what a module does comes before how.` |

**C. Four new rules.** Insert them after rule 8's After paragraph and before the closing line
"`README.md` is a worked example of these rules applied to a whole page.". Use the existing format
of `## N. ` heading, `Check:`, `Code counterpart:`, `Before (<source>):` and `After:`, with a blank
line after each rule. Use this text. Rewrapping it is allowed, but the wording is fixed by the
gate:

```
## 9. One name per concept: no synonyms, and no name shared by two concepts.
Check: each term specific to this system keeps the name it got at first use (in a spec, its
Problem section; in the README, its terms table), and no name stands for two things.
Code counterpart: Clean Code's "pick one word per concept" and "don't pun"; ubiquitous language
(Evans, Domain-Driven Design).
Before (operator's research comment on the overview draft, 2026-10-03, item 3): one page called
overlapping things "the harness", "the runtime", "the installed harness" and "the in-tree copy".
After: harness is the code; runtime is "the pinned checkout of the harness that runs tickets", a
row of the page's terms table. Each name is used unchanged after that.

## 10. One mode per section: explanation, how-to and reference do not share a heading.
Check: label each section explanation (what and why), how-to (steps to do one thing) or reference
(facts to look up); a section with two labels is split, each part under its own heading.
Code counterpart: single responsibility; a module has one reason to change.
Before (operator's research comment on the overview draft, 2026-10-03, item 2): "Where it runs"
said what the three places are, how to accept a new harness revision and how to upgrade, in one
block.
After: "Where it runs" explains the three places; "Accepting a harness revision" and "Upgrading the
runtime" follow it as how-to subsections, each with its own steps.

## 11. A heading states what is under it.
Check: read only the headings; each one predicts what its section says.
Code counterpart: intention-revealing names, and Fowler's Rename when a name stops saying what the
thing does.
Before (operator's research comment on the overview draft, 2026-10-03, item 4): "The human's
stops".
After: "Where a human decides".

## 12. Parallel facts go in a table.
Check: three or more items that each give the same kinds of fact are rows of a table, one column
per kind of fact.
Code counterpart: table-driven methods (McConnell, Code Complete); parallel cases as rows of data,
not a chain of branches.
Before (operator's research comment on the overview draft, 2026-10-03, item 8): the eight roles,
what each does and the model it runs on, as a paragraph.
After: a table with one row per role and the columns Role, Does and Model.
```

In round 1 I built this exact text into a scratch copy of the file (parts A, B and C applied to
today's `docs/writing.md`). It came to 131 lines with a widest line of 99, and every scenario
below gave its expected after-state on that copy. The critic rebuilt the copy independently and
got the same outputs. Parts A–C are unchanged in this revision.

## Tests to change

none. `tests/factory/test_writing_standard.py` checks that the file exists and is named in the
prompts, not its contents.

=== specs/writing-standard/spec.md
## ADDED Requirements

### Requirement: Four rules on names, section modes, headings and tables
The writing standard `docs/writing.md` SHALL keep rules 1–8 as numbered today and SHALL add rules
9–12, in this order: one name per concept, one mode per section, a heading states what is under
it, and parallel facts go in a table.

#### Scenario: twelve numbered rules with the four new headings
- WHEN `cd ~/dev/spec-factory && echo "rules=$(grep -o '^## [0-9]*\.' docs/writing.md | tr -dc '0-9\n' | paste -sd, -) new=$(grep -c -i -E '^## 9\. One name per concept|^## 10\. One mode per section|^## 11\. A heading states what is under it|^## 12\. Parallel facts go in a table' docs/writing.md)"`
- THEN it prints `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4`

### Requirement: Each new rule has a check and one example pair
Each of rules 9–12 MUST have exactly one `Check:` line, one sourced `Before (` line and one
`After:` line, in the standard's existing format.

#### Scenario: each new rule has one check, one before, one after
- WHEN `cd ~/dev/spec-factory && awk '/^## [0-9]+\./{n=$2+0} n>=9 && /^Check: /{c[n]++} n>=9 && /^Before \(/{b[n]++} n>=9 && /^After: /{a[n]++} END{for(i=9;i<=12;i++) printf "%d:%d%d%d ", i, c[i], b[i], a[i]; print ""}' docs/writing.md`
- THEN it prints `9:111 10:111 11:111 12:111` (each triple counts Check, Before and After lines;
  trailing space allowed)

### Requirement: New rules' examples are the factory's own before and after
The examples of rules 9–11 SHALL quote the overview page's earlier wording and the wording it
uses today. Each after-phrase SHALL still be present in `README.md`, and neither before-phrase
SHALL be.

#### Scenario: example phrases are in the standard and match the README
- WHEN `cd ~/dev/spec-factory && w=; r=; for h in "installed harness" "the pinned checkout of the harness that runs tickets" "Accepting a harness revision" "Upgrading the runtime" "The human's stops" "Where a human decides"; do w="$w$(tr '\n' ' ' < docs/writing.md | grep -qF "$h" && echo y || echo n)"; r="$r$(tr '\n' ' ' < README.md | grep -qF "$h" && echo y || echo n)"; done; echo "writing=$w readme=$r"`
- THEN it prints `writing=yyyyyy readme=nyyyny`

### Requirement: Code counterpart lines
A rule SHALL carry at most one line starting `Code counterpart:`, placed after its Check text and
before its Before line. Rules 1, 2, 3, 5, 6, 7, 9, 10, 11 and 12 SHALL carry one; rules 4 and 8
SHALL carry none; no such line SHALL stand outside a rule.

#### Scenario: counterpart lines on the agreed rules, in place
- WHEN `cd ~/dev/spec-factory && awk '/^## [0-9]+\./{n=$2+0; ck=0; bf=0} /^Check: /{ck=1} /^Before \(/{bf=1} /^Code counterpart: /{k[n]++; if (!ck || bf) bad++} END{s=""; for(i=1;i<=12;i++) s=s (k[i]+0); print "intro=" (k[0]+0) " rules=" s " misplaced=" (bad+0)}' docs/writing.md`
- THEN it prints `intro=0 rules=111011101111 misplaced=0` (one digit per rule, 1 to 12)

### Requirement: The change is additive and stays within budget
The standard SHALL stay under 140 lines, with no line wider than 100 characters. Every line it
holds today SHALL still be present, in the same order, and the file SHALL have no whitespace
errors. The change SHALL modify no file other than `docs/writing.md`.

#### Scenario: under budget, nothing removed, clean whitespace
- WHEN `cd ~/dev/spec-factory && echo "lines=$(grep -c '' docs/writing.md) wide=$(awk 'length($0)>100' docs/writing.md | grep -c '') removed=$(git diff -U0 e703c1b -- docs/writing.md | grep -v '^--- ' | grep -c '^-') ws=$(git diff --check e703c1b -- docs/writing.md >/dev/null && echo clean || echo errors)"`
- THEN it prints `wide=0 removed=0 ws=clean`, and `lines=` is a number below 140

#### Scenario: only the standard changes
- GIVEN the checkout is the change branch, before it merges into `main`
- WHEN `cd ~/dev/spec-factory && echo "changed=[$(git diff --name-only "$(git merge-base main HEAD)" HEAD -- . ':(exclude).factory' | paste -sd, -)]"`
- THEN it prints exactly `changed=[docs/writing.md]`

#### Scenario: the standard's existing tests still pass
- WHEN `cd ~/dev/spec-factory && uv run --frozen pytest -q -p no:cacheprovider tests/factory/test_writing_standard.py 2>&1 | tail -1`
- THEN the last line reports `5 passed` and no failures

=== verification.md
## Acceptance

- twelve numbered rules with the four new headings → NEW. Today it prints
  `rules=1,2,3,4,5,6,7,8 new=0`: rules 9–12 do not exist.
- each new rule has one check, one before, one after → NEW. Today it prints
  `9:000 10:000 11:000 12:000`: no section 9–12 exists.
- example phrases are in the standard and match the README → NEW. Today it prints
  `writing=nnnnnn readme=nyyyny`: the standard has none of the six phrases. The README part
  already matches, which shows the after-examples are real.
- counterpart lines on the agreed rules, in place → NEW. Today it prints
  `intro=0 rules=000000000000 misplaced=0`: no rule has a counterpart line.
- under budget, nothing removed, clean whitespace → REGRESSION. Today it prints `lines=86 wide=0
  removed=0 ws=clean`. On the scratch after-state built from design.md it gave `lines=131`, with
  no wide or removed lines.
- only the standard changes → NEW. Today, on `main`, it prints `changed=[]`: nothing has changed
  yet. It must be run on the change branch before merge; there it prints `changed=[docs/writing.md]`
  only if the implementer touched no other file outside `.factory/`. After merge, on `main`, it
  prints `changed=[]` again and checks nothing, so it is not a post-merge check.
- the standard's existing tests still pass → REGRESSION. Today: `5 passed in 0.41s`.

How these were run: every WHEN command was re-run for this revision on `~/dev/spec-factory` at
`967ee77`, and printed the "today" outputs above. In round 1 the first five were also run against
a scratch copy of the file with parts A–C applied verbatim, where they gave the THEN outputs; the
critic reproduced that independently. Parts A–C did not change in this revision, so those results
still apply. The Operator steps claim that no re-acceptance is needed was checked for this
revision: `.factory/harness.lock` holds `e703c1b…`, and `git log -1 --format=%H -- factory
bin/factory agents pyproject.toml uv.lock` prints `e703c1b…` both in this checkout and in the
runtime, whose HEAD is `43a01dd`.

## Responses

- [BLOCKING] Operator steps, step 1 (runtime, harness revision and `--accept-harness` not
  glossed): FIXED. Step 1 now opens by saying what the runtime is (the second checkout at
  `~/dev/spec-factory-harness`, pinned to one commit, from which every ticket runs and roles read
  the standard). It glosses the harness lock as the pin on the harness code a repo agreed to run,
  and says why no `--accept-harness` run follows. Evidence also gains a bullet that glosses the
  runtime at its first use, with `README.md` lines 156 and 349 as sources. The harness-lock bullet
  now glosses "harness" and cites the measured revisions (`e703c1b` in the lock, the runtime and
  this checkout, with the runtime's HEAD at `43a01dd`). That shows a non-harness commit does not
  move the revision.
- [SHOULD-FIX] Risk, sentence 2 (wrong part and count): FIXED. It now reads "the six counterpart
  lines for existing rules (design.md, part B) and the four new rules with their own counterpart
  lines (design.md, part C)".
- [NIT] Scenario "only the standard changes" (passes vacuously on `changed=[]`): FIXED. The THEN
  accepts only `changed=[docs/writing.md]`, a GIVEN line says it runs on the change branch before
  merge, and the item is relabelled NEW: today it prints `changed=[]`. The requirement now states
  the one-file limit, which the scenario checks.

Out-of-scope observations:
- The README's "Maintaining this page" calls its "Reader first" bullet "its summary for this page"
  of the standard. After this change that summary lacks the one-name rule, although the page
  already applies it. The request leaves the README unedited, so the summary will be incomplete
  until a later change.
- Research item 5 ("cut announcement sentences") matches no built rule and is not requested. The
  request's statement that item 5 maps to a built rule is not right, as triage noted.
- `README.md` "Accepting a harness revision" (line 204) says the harness compares "the runtime's
  commit" with the lock. The code compares the last commit that touched harness code
  (`harness_revision`, `factory/instance.py` line 98), which differs today (`e703c1b` against the
  runtime's HEAD `43a01dd`). The README's own table at line 410 states this correctly. The wording
  at line 204 could mislead an operator into running `--accept-harness` with the HEAD commit, which
  the guard refuses.

## Reviewer findings on your previous head

Commit: c64183ac7d10f6286136a0b419764d05202736fc (branch `factory/T-0014.1`, forks from `main` at `ba4618a`; `431e349` on `main` is not an ancestor, so the merge-base diff is the one that counts)

## What I checked, in the role's order

1. Test integrity. `git diff --name-only ba4618a..HEAD` prints `docs/writing.md` only. No test file, CI config, AGENTS.md, skill or prompt is touched. Nothing to block on.
2. Correctness against the spec. All seven acceptance commands re-run in the review worktree and gave the THEN outputs:
   - 1: `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4`
   - 2: `9:111 10:111 11:111 12:111 `
   - 3: `writing=yyyyyy readme=nyyyny`
   - 4: `intro=0 rules=111011101111 misplaced=0`
   - 5: `lines=131 wide=0 removed=0 ws=clean` (131 is below 140 and equals the spec's scratch build)
   - 6: `changed=[docs/writing.md]`
   - 7: covered by the full gate run below, which includes `tests/factory/test_writing_standard.py`
   Intermediate check (wording). I extracted parts A, B (the six table cells, backticks stripped) and C from the pinned design.md in my input (44 lines) and the 45 added lines from `git diff ba4618a..HEAD -- docs/writing.md`. Line by line, the only difference is one trailing blank line after rule 12 (`diff` output: `44a45 > `), which design.md requires ("a blank line after each rule"). Joined and whitespace-normalised, `diff` prints nothing (exit 0). The inserted text matches design.md word for word; the implementer did not rewrap, so even the line breaks match.
   Placement. Part A sits directly after "example taken from the factory's own writing, and its rewrite." as a continuation of that paragraph (diff hunk at old line 19). Part B lines sit after each rule's Check text and before its `Before (` line on rules 1, 2, 3, 5, 6, 7 only (criterion 4 confirms `misplaced=0`). Part C sits after rule 8's After paragraph and before the closing `README.md` line.
3. Scope. Only `docs/writing.md`; additions only (`removed=0` against `e703c1b`). Nothing outside parts A, B, C.
4. Silent behavior changes. None. The file is read by roles from the runtime checkout, which this merge does not move; the spec's Operator steps own that.
5. Security and data safety. Not applicable; a prose file.
6. Protected paths. None touched. `docs/writing.md` is not under `.factory/`, `factory/`, `bin/factory`, `agents/`, `pyproject.toml`, `uv.lock`, `docs/prompts/`, the reference harness or credentials.
7. Maintainability. Nothing to raise.
8. PR description. What changed says in words what was added and where, glosses "writing standard" and "role" at first use, and records the wording check with its method. Known gaps names the untested-first point and the main-moved point honestly and explains why each is harmless. The base it names (`ba4618a`) is the branch's real fork point; the harness header's `431e349` is `main`'s tip, and the implementer's note on this is correct. Readable at the gate as written.

Gate commands, run from the review worktree exactly as written:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `126 passed in 116.64s (0:01:56)`.

## Findings

none

## Prior findings

none (round 1)

## Out-of-scope observations

- The harness header for this run names base `431e3492…`, which is `main`'s tip, not the branch's fork point `ba4618a`. A two-dot diff from `431e349` shows a spurious one-line deletion in `dev/issues.md`; the three-dot diff the harness actually included, and criterion 6's merge-base diff, do not. Worth knowing for anyone reading the raw header; it is not a defect in this ticket.

STATUS: APPROVE
CONFIDENCE: high. Every acceptance command and both gates were re-run in the review worktree and gave the expected output, and the inserted text was compared with design.md and matched exactly.
ESCALATIONS: none

## Verifier findings on your previous head

Commit: c64183ac7d10f6286136a0b419764d05202736fc (branch `factory/T-0014.1`, worktree
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0120-verifier/wt`, `git status --short` empty
before and after every run)

The writing standard (`docs/writing.md`, the page every role follows for text a person reads) now
has rules 9–12 and the ten agreed `Code counterpart:` lines, with nothing removed. Every acceptance
command gives its expected output on the PR and its recorded "today" output on the base. Both gate
commands pass, and the inserted text matches design.md word for word.

Where each side ran. Base: `~/dev/spec-factory`, which is `main` at `431e349` (the base I was given),
and has changes only under `.factory/`. PR: the worktree at `c64183a`. The commands say "from
`~/dev/spec-factory`", but that checkout is `main` and does not hold the change before merge, so I
ran them from the change branch's worktree. Criterion 6's GIVEN line asks for exactly that. Each
command was run verbatim from a script, with no edits.

Per criterion:

| # | Kind | Command (short name) | Base `431e349` | PR `c64183a` | Result |
|---|---|---|---|---|---|
| 1 | NEW | twelve numbered rules with the four new headings | `rules=1,2,3,4,5,6,7,8 new=0` | `rules=1,2,3,4,5,6,7,8,9,10,11,12 new=4` | PASS |
| 2 | NEW | each new rule has one check, one before, one after | `9:000 10:000 11:000 12:000 ` | `9:111 10:111 11:111 12:111 ` | PASS |
| 3 | NEW | example phrases are in the standard and match the README | `writing=nnnnnn readme=nyyyny` | `writing=yyyyyy readme=nyyyny` | PASS |
| 4 | NEW | counterpart lines on the agreed rules, in place | `intro=0 rules=000000000000 misplaced=0` | `intro=0 rules=111011101111 misplaced=0` | PASS |
| 5 | REGRESSION | under budget, nothing removed, clean whitespace | `lines=86 wide=0 removed=0 ws=clean` | `lines=131 wide=0 removed=0 ws=clean` | PASS |
| 6 | NEW | only the standard changes | `changed=[]` | `changed=[docs/writing.md]` | PASS |
| 7 | REGRESSION | the standard's existing tests still pass | `5 passed in 0.36s` | `5 passed in 1.70s` | PASS |

What the outputs mean:
- The NEW criteria (1–4 and 6) fail on the base for the reason verification.md gives: rules 9–12 and
  the counterpart lines do not exist yet, and nothing has changed on `main`. Each base output
  matches verification.md's "today" output exactly, so none of them is a spec defect.
- Criterion 5 holds on both sides. The PR file has 131 lines, the same as the spec's scratch build
  and under the 140-line budget. No line is removed relative to `e703c1b`, and there are no
  whitespace errors.
- Criterion 6: `git merge-base main HEAD` is `ba4618a`, so the diff counts only the branch's own
  commit. The two-dot diff `431e349..c64183a` also lists `dev/issues.md`. That comes from `main`
  moving one commit (`431e349`, "issues: #27 indexed") after the branch was cut, not from the
  branch. The PR description names its base as `ba4618a` while my input names `431e349`. That is
  the same fact seen from two sides, and it does not change any result.

Intermediate check (wording; the plan gives it to the reviewer, and I ran it independently):
- Part A: the two lines at `docs/writing.md` lines 20–21 are identical to design.md's block (`diff`
  printed nothing). They continue the paragraph that ends at line 19.
- Part B: the six inserted lines, each with its rule number, are identical to design.md's table
  (`diff` printed nothing). Rules 4 and 8 have none. Each line directly precedes its rule's
  `Before (` line (lines 25/26, 35/36, 44/45, 61/62, 71/72, 79/80).
- Part C: rules 9–12 at lines 91–125 are identical to design.md's block both line by line and with
  lines joined (`diff` printed nothing for either). Each rule is followed by a blank line, and the
  closing `README.md` line is still the file's last line.
- Nothing existing was edited: `diff <(git show 431e349:docs/writing.md) docs/writing.md | grep -c
  '^<'` prints `0`. Every base line is still present, in order.

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0. The change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `126 passed in 115.53s`. A rerun
  that captured the exit code gave `126 passed in 101.79s`, exit 0. The whole harness suite passes.

Probes:
- Line width at the boundary. The widest line in the PR file is 99 characters, under the 100 limit,
  and the same as the file's widest line before the change. → OK
- The README anchors the new examples cite, checked by heading structure rather than by phrase.
  `## Where it runs` (README line 150) has `### Accepting a harness revision` (202) and `### Upgrading
  the runtime` (219) as its how-to subsections, which is rule 10's After. `## Where a human decides`
  is at line 273 (rule 11). The `runtime` row at line 74 holds "the pinned checkout of the harness
  that runs tickets" (rule 9). The `| Role | Does | Model |` table at line 31 has 8 data rows, which
  matches rule 12's "the eight roles". The examples describe the README as it is, not only the
  phrases criterion 3 searches for. → OK
- Is criterion 4's placement check sensitive? I took a mutated copy of the PR file, in a pipe with no
  file written, that moves rule 2's counterpart line to after its `Before (` line. The same awk
  printed `misplaced=1`. A green criterion 4 therefore means the lines really are in place; it does
  not pass vacuously. → OK
- Wrapped phrases. "Upgrading the runtime" and "The human's stops" are split across lines in the
  standard (lines 115–116 and 122–123). Criterion 3 finds them only because it joins lines, which
  is the design the spec states. Nothing is special-cased to the test inputs. → OK

STATUS: VERIFIED
CONFIDENCE: high. All seven criteria and both gates were run verbatim on the head and the base,
and the text was diffed against design.md with no difference found.
ESCALATIONS: none

## Gate suite on your previous head
PASS

