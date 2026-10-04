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

STATUS: READY-FOR-CRITIC
CONFIDENCE: high. Every acceptance command was re-run on `967ee77` for this revision. The
no-re-acceptance claim was checked against the lock and both checkouts' harness revisions. Parts
A–C, which the critic reproduced, did not change.
ESCALATIONS: none
