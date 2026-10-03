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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0114-spec_writer/output.md`

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
