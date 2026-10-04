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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0113-triage/output.md`

## Request (raw, with any answers appended)

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
