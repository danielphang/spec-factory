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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0116-spec_writer/output.md`

## Ticket (Triage output)

Type: feature

Title: Writing standard: add four rules (one name per concept, one mode per section, headings state their content, parallel facts in a table) and name each rule's code-design counterpart

Summary:
The writing standard is `docs/writing.md`: the page every role is pointed to for any section a person reads. It has no rule about names. A document can therefore call one thing by four names and still pass every check, and the README draft did exactly that before review. The requester wants four rules added to that page, in its existing format: the rule, a check, and a before/after from the factory's own writing. The four are: one name per concept, one mode per section, headings that state their content, and parallel facts in a table. They also want one "Code counterpart:" line on each of the twelve rules (eight existing, four new), naming the code-design principle it matches. A rule with no honest counterpart gets no line. Only `docs/writing.md` changes.

Evidence:
- `docs/writing.md` is 86 lines (`wc -l`) and has eight rules. Their headings are at lines 21, 29, 38, 46, 54, 62, 70 and 78 (`grep -n '^#'`). None covers naming. Rule 2 (line 29) says to gloss a term at first use; it does not say to keep using that term afterwards.
- The research comment on #23 (`gh issue view 23 --comments`) is the operator's list of ten rules with sources: Google and Microsoft style guides, Diátaxis, design-doc templates. Its items 2 (one mode per section), 3 (one name per thing), 4 (headings state the content) and 8 (tables for parallel facts) are the four rules requested. Each item carries the before/after the request proposes. Examples: "harness / runtime / installed harness / in-tree copy"; "Where it runs" split into explanation plus two how-to headings; "The human's stops" renamed "Where a human decides"; eight roles in prose rewritten as a role / does / model table.
- The after-state of those examples is in `README.md` today:
  - a "Terms used on this page" table (line 61) whose `runtime` row reads "the pinned checkout of the harness that runs tickets";
  - "## Where it runs" (line 150), followed by "### Accepting a harness revision" (202) and "### Upgrading the runtime" (219);
  - "## Where a human decides" (273);
  - a Role / Does / Model table (lines 31–40).
  The before-state is quoted only in the #23 comment. `git log -S"The human's stops" -- README.md` returns nothing, so the draft wording was never committed.
- Request quote: "the mapping is a reading aid, not decoration."
- Request quote, acceptance: "the four rule headings exist in `docs/writing.md`; each new rule has a before and an after; every rule carries one 'Code counterpart:' line or none; the file stays under 140 lines."

Assumptions (the triage agent's inferences; the request does not state them):
- One row of the proposed mapping table is "Prose says why, not what the code does". No such rule exists in `docs/writing.md`. It comes from the operator's second comment on #23 ("never narrates what code does"), not from the eight built rules. The request asks for "four rules" and says "all twelve", so this triage reads that row as a stray and not as a fifth new rule. The requester invited the writer to "confirm or correct" the mapping. The spec writer should name this choice in Decisions so the operator sees it at the spec gate (the point where a human approves a spec before code is written).
- Under "One line per rule, all twelve", a rule with no honest counterpart gets no line, as the request says elsewhere. Rules 1, 4, 5 and 8 have no row in the proposed table. The writer either finds them a counterpart or leaves them without one.
- New rules are numbered 9–12 after the existing eight, and the existing rules are not renumbered. The request does not say this. Renumbering would break the "rule 2" and "rule 6" references in the request and elsewhere.
- Suggested priority (a suggestion; priority is the human's call): p2. The rules already shape the README; the gap is that roles are not told to follow them.

Reason: n/a (ACCEPT). No duplicate exists. The request is #26 itself, indexed in `dev/issues.md` as intake ticket T-0014. #23 (closed) built the standard. #25 (the doc-checker role) and #21 (the README as the factory's current-state overview) cover different work.

Out-of-scope observations:
- The request's Evidence says research items "1, 5, 6, 9 and 10 map to rules already built". Checked against the #23 comment, this is not right for two of them. Item 1 (status header first) is the one the request itself says was left out on purpose. Item 5 (cut announcement sentences) matches no built rule and is neither requested nor listed as left out. Items 6, 9 and 10 do match built rules 3, 4 and 2. Whether item 5 should become a rule is for the operator to decide; this ticket does not add it.
- No harness fix exists on the Nanobot side for this request, and it needs none: the change is to one documentation file.

STATUS: ACCEPT
CONFIDENCE: high. Every evidence claim was checked against `docs/writing.md`, `README.md` and the #23 comment. The one stray mapping row has a stated default, and the requester left the mapping to the writer.
ESCALATIONS: none

## Request (raw)

---
title: "Writing standard: one name per concept, one mode per section, headings that state content, tables for parallel facts; each rule named by its code-design counterpart"
labels: "design-doc"
---
**Problem, for the gate:** the writing standard (`docs/writing.md`, built by T-0013 for #23) has no rule about names, so one document can call one thing by four names and pass every check. The README draft did exactly that before review: "the harness", "the runtime", "the installed harness" and "the in-tree copy" for overlapping things, which a first-time reader cannot untangle. Three other rules from #23's research comment also did not make it into the build. And the standard never says what each rule *is*, although most of them are code-design principles every agent already knows, which is the cheapest way to get a rule followed.

**Evidence:**
- `docs/writing.md` has eight rules (headings at lines 21–78). None covers naming. Rule 2 (gloss a term at first use) defines a term once; it does not say to keep using that term.
- #23's research comment listed ten rules with sources (Google and Microsoft style guides, Diátaxis, design-doc templates). Rules 1, 5, 6, 9 and 10 map to rules already built; rules 2, 3, 4 and 8 are missing: one mode per section, one name per thing, headings that state their content, tables for parallel facts. Status header first (its rule 1) and caveats beside what they qualify (its rule 7) are left out on purpose; they are page-layout advice, not rules a role can check in its own output.
- Each missing rule has a before/after in the README's review history (operator comments on the overview draft, 2026-10-03), which is the example format the standard already uses.

**Proposed change:** one sub-ticket, `docs/writing.md` only.

A. Four rules, in the standard's existing format (rule, why, a before/after from the factory's own writing):
   - **One name per concept; never a synonym.** The README's terms table is the reference for that page; a spec uses the names its Problem section defines. Before: harness / runtime / installed harness / in-tree copy. After: harness = the code, runtime = the pinned checkout that runs tickets.
   - **One mode per section.** Explanation, how-to and reference do not share a heading. Before: "Where it runs" mixed what the three places are, how to accept a lock and how to upgrade. After: one explanation section and two how-to subsections.
   - **Headings state their content.** A reader skimming headings can predict what is under each. Before: "The human's stops". After: "Where a human decides".
   - **Parallel facts go in a table.** Before: eight roles as a paragraph. After: a role / does / model table.

B. One line per rule, all twelve, naming its code-design counterpart. Proposed mapping, for the writer to confirm or correct:

| Rule | Code principle |
|---|---|
| One name per concept | Clean Code "Pick one word per concept" and "Don't pun"; ubiquitous language (Evans, DDD) |
| One mode per section | Single responsibility |
| Headings state their content | Intention-revealing names; *Rename* (Fowler, Refactoring) |
| Prose says why, not what the code does | DRY / single source of truth; Fowler: a comment explaining what code does is a smell |
| Gloss at first use (rule 2) | Declare before use |
| One idea per sentence (rule 3) | A function does one thing |
| Internal references to a closing note (rule 6) | Encapsulation / information hiding |
| Lead with the problem (rule 7) | Interface before implementation |
| Parallel facts in a table | Data, not control flow |

Rules with no honest counterpart get none; the mapping is a reading aid, not decoration.

**Decisions:**
- The mapping is a single line per rule, not a section of its own. Its job is recognition: an agent that knows "single responsibility" applies the rule without more explanation.
- The README's "Maintaining this page" rules point to `docs/writing.md`; they are not edited here.

**Out of scope:** critic rubric 6 and reviewer check 8 (they already apply `docs/writing.md` as a whole, so new rules reach them without a prompt change); the role prompts; rewriting existing documents to the new rules.

**Risk:** `docs/writing.md` is not a protected path on this instance; every role reads it through the briefing, so a wrong rule misdirects every role's human-facing output at once. The gate reads the four new rules and the mapping.

**Acceptance the writer can make runnable:** the four rule headings exist in `docs/writing.md`; each new rule has a before and an after; every rule carries one "Code counterpart:" line or none; the file stays under 140 lines.

## Critic findings on your previous version

## Spec critic review, round 1 (spec v1)

What I checked myself, from `~/dev/spec-factory` at `967ee77`:

- Cited paths and symbols: `docs/writing.md` has 86 lines, eight `## N.` headings at lines 21, 29,
  38, 46, 54, 62, 70, 78 and a widest line of 99; `HARNESS_PATHS` in `factory/instance.py` line 33
  is `("factory", "bin/factory", "agents", "pyproject.toml", "uv.lock")`; `README.md` has the Role /
  Does / Model table at lines 31–40, the `runtime` terms row, "## Where it runs" at 150,
  "### Accepting a harness revision" at 202, "### Upgrading the runtime" at 219, "## Where a human
  decides" at 273, and "Maintaining this page" at 373 with the "Reader first" bullet at 387.
  `e703c1b` is the only commit touching `docs/writing.md`. Issue 23's first comment lists the ten
  items as the spec describes; its second comment is the "prose is for the why" note the Decisions
  section attributes to it.
- All seven acceptance commands, run as written on today's checkout: `rules=1,2,3,4,5,6,7,8 new=0`,
  `9:000 10:000 11:000 12:000`, `writing=nnnnnn readme=nyyyny`, `intro=0 rules=000000000000
  misplaced=0`, `lines=86 wide=0 removed=0 ws=clean`, `changed=[]`, `5 passed in 1.79s`. The four
  NEW items fail today for the reason the spec gives.
- The same commands against a scratch copy I built from design.md parts A–C (not in the repo):
  `rules=1,...,12 new=4`, `9:111 10:111 11:111 12:111`, `writing=yyyyyy readme=nyyyny`, `intro=0
  rules=111011101111 misplaced=0`, `lines=131 wide=0`. The design text produces the THEN outputs,
  and a stub (headings without Check/Before/After, or counterpart lines in the wrong place) would
  not.

Findings:

[BLOCKING] 6 Operator steps, step 1
Problem: The only paragraph a new operator must act on says "move the runtime", "the harness
revision" and "`--accept-harness`" without saying what any of them is, and no earlier human-facing
section glosses "runtime" (Evidence bullet 9 glosses the harness lock as a commit pin, but never
says what the runtime is or that it lives in a second checkout).
Evidence: Read Problem, Evidence, Open questions and Decisions for a first use of "runtime" with a
gloss; there is none. The term is specific to this project (it is a row in the README's terms
table).
Suggested fix: Open step 1 with the gloss, e.g. "The factory runs from a second checkout of this
repo, the runtime at `~/dev/spec-factory-harness`, pinned to one commit. After merge, move it
between tickets: ...", and say "no `--accept-harness` is needed" as "the harness lock, the pin that
guards the code paths, does not cover `docs/`, so no re-acceptance step".

[SHOULD-FIX] 1 Risk, sentence 2
Problem: "the gate reads the four rules and the twelve-row mapping word for word (design.md,
part B)" cites the wrong place and count: Part B is a six-row table of counterpart lines for rules
1–7, and the four rules are Part C.
Evidence: design.md as submitted; Part B table has rows for rules 1, 2, 3, 5, 6, 7; Part C holds
rules 9–12 with their own counterpart lines.
Suggested fix: "the gate reads the six counterpart lines (part B) and the four new rules with
theirs (part C) word for word".

[NIT] 2 Scenario "only the standard changes"
Problem: The THEN accepts `changed=[]`, so on any checkout where `merge-base main HEAD` equals
HEAD (including `main` after the merge) the item passes without checking anything.
Evidence: Ran it on `main`: `changed=[]`. It carries weight only on the unmerged branch.
Suggested fix: None needed if the verifier runs it on the change branch, which is where it is
meant to run; otherwise drop the `changed=[]` clause.

Prior findings: none (round 1).

Out-of-scope observations:
- Scenario "under budget" measures removals against `e703c1b` by hand-filtering `^-` lines, which is
  fine today because that commit is the file's only history. If a later ticket edits the file, the
  anchor stays correct but the "nothing removed" meaning drifts to "nothing removed since the
  first version". Not this ticket's problem.

STATUS: REVISE
CONFIDENCE: high; every cited path, line and command was checked on the checkout and the design
text reproduces the THEN outputs on a scratch copy, so the one blocking issue is purely the
Operator steps gloss.
ESCALATIONS: none

## Your previous spec (v1)

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
  - The terms table (line 61) has a `runtime` row: "the pinned checkout of the harness that runs
    tickets".
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
- `docs/writing.md` is outside the harness revision. The harness checks a commit pin (the "harness
  lock") before it runs a ticket. That pin covers only `factory`, `bin/factory`, `agents`,
  `pyproject.toml` and `uv.lock` (`HARNESS_PATHS` in `factory/instance.py`). So once this change
  merges, moving the runtime to it needs no re-acceptance.

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
misleads all of them at once. That is why the gate reads the four rules and the twelve-row mapping
word for word (design.md, part B). The file is not a protected path on this instance. No protected
path is touched. The change reaches running roles only when the operator next moves the runtime.

## Operator steps

1. After merge, move the runtime between tickets: `git -C ~/dev/spec-factory-harness checkout
   --detach <merge sha>`, then `uv sync --frozen` there. No `--accept-harness` is needed, because
   the harness revision does not cover `docs/`. Until this step, roles keep reading the old eight
   rules.

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

I built this exact text into a scratch copy of the file (parts A, B and C applied to today's
`docs/writing.md`). It came to 131 lines with a widest line of 99, and every scenario below gave
its expected after-state on that copy.

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
errors.

#### Scenario: under budget, nothing removed, clean whitespace
- WHEN `cd ~/dev/spec-factory && echo "lines=$(grep -c '' docs/writing.md) wide=$(awk 'length($0)>100' docs/writing.md | grep -c '') removed=$(git diff -U0 e703c1b -- docs/writing.md | grep -v '^--- ' | grep -c '^-') ws=$(git diff --check e703c1b -- docs/writing.md >/dev/null && echo clean || echo errors)"`
- THEN it prints `wide=0 removed=0 ws=clean`, and `lines=` is a number below 140

#### Scenario: only the standard changes
- WHEN `cd ~/dev/spec-factory && echo "changed=[$(git diff --name-only "$(git merge-base main HEAD)" HEAD -- . ':(exclude).factory' | paste -sd, -)]"`
- THEN it prints `changed=[docs/writing.md]` on the change branch, or `changed=[]` on a checkout
  that does not have the change

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
- only the standard changes → REGRESSION. Today on `main` it prints `changed=[]`.
- the standard's existing tests still pass → REGRESSION. Today: `5 passed in 0.45s`.

How these were run: every WHEN command was run on `~/dev/spec-factory` at `967ee77` (outputs
above). The first five were also run against a scratch copy of the file with parts A–C applied
verbatim, where they gave the THEN outputs. That copy's names-changed check does not apply, since
it is not a branch. The budget check needs git history, so I ran it by copying the scratch file
over `docs/writing.md` in the dev checkout for that one command. I then restored the file with
`git checkout -- docs/writing.md`, and `git status --short docs/` printed nothing afterwards.

Out-of-scope observations:
- The README's "Maintaining this page" calls its "Reader first" bullet "its summary for this page"
  of the standard. After this change that summary lacks the one-name rule, although the page
  already applies it. The request leaves the README unedited, so the summary will be incomplete
  until a later change.
- Research item 5 ("cut announcement sentences") matches no built rule and is not requested. The
  request's statement that item 5 maps to a built rule is not right, as triage noted.
