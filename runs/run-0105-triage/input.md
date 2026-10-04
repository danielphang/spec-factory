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
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0105-triage/output.md`

## Request (raw, with any answers appended)

---
title: Define and implement technical documentation standards for the factory's agents (reader: technical, new to the system)
labels: p1, design-doc, harness
---
**Priority:** P1 (next after the P0 layout work). **Related:** #11 (closed: the spec's Problem section in plain language, critic rubric 6, changelog 41), which fixed one section of one role's output; this issue generalises it to every document and every human-facing section the factory's agents produce. #21 (README overview, current truth) is the first consumer.

**Where:** `docs/design.md` §Shared preamble (OUTPUT), §2 Spec writer FORMAT and RULES, §3 Spec critic rubric 6, §5 Implementer PR DESCRIPTION, §6 Code reviewer, the Appendix reviewer prompt (`docs/prompts/99-doc-reviewer.md`); `factory/context.template.md` (the per-repo briefing); a new `docs/writing.md`; `README.md` and the overview page as the first documents held to it.

**Problem, for the gate:** the factory has no documentation standard, so every document an agent writes is written for the agent that wrote it. The reader the factory actually has is a technical person seeing the project, or the ticket, for the first time: the operator at a gate, a new adopter reading the README, a reviewer reading a PR description, a future session reading a run's output. Those readers get system-internal names with no gloss, parentheticals stacked three deep, issue numbers and ticket ids used as nouns, and diagrams before the vocabulary to read them. #11 fixed this for one section (the spec's Problem paragraph) and showed the fix works: a rubric item the critic can apply. Nothing applies it anywhere else.

**What happened (2026-10-03):** the operator reviewed the draft overview of the system (the page #21 part B will land) and left three findings within five minutes, each a standard the agents were never given:
1. A flag (`--accept-harness`) appeared in a diagram with no statement of what requires it; the explanation sat two sections later, in the passive.
2. A section listed what is built as a parenthetical pile-up ("the build half in local-commit mode (no remote, no PR, no CI service: the verifier runs the instance's `gate_commands` and its result is the `ci` row; …)"), which the operator called incomprehensible, and asked for "at least the plain outline".
3. The page as a whole assumed its reader knew the project: "consider audience and what they know and don't know; this doc will be read by a technical audience that will probably see this project for the first time."

The same three failures recur in the factory's own outputs: spec Evidence sections quoting commands with no statement of what they show; PR descriptions whose "What changed" is a file list; escalations that name a state (`checks-in-flight`) without saying what is stuck. The ponytail review (#20's source) found the same thing from the other side: an instruction that moves behaviour is operational ("grep every caller"), not a principle ("trace the flow"), and that applies to writing rules as much as coding rules.

**Why it matters:** the gate is the factory's one real safety check, and it is only as good as what the operator can read there. A standard the critic and reviewer can apply makes readability a checked property instead of a hope; without it every document costs a review round, and documents nobody reviews (run outputs, escalations) stay unreadable.

**Proposed change:**

A. **`docs/writing.md`, the standard.** Short, operational, one page. The reader model: technical, new to this system, has not read the design doc. Rules in the form the critic can check: the first paragraph says what is wrong (or what this is) and for whom; a term specific to this system is glossed on first use with what it does or why it exists, general technical concepts are not; one idea per sentence, no parenthetical holding a second idea; a diagram comes after the words needed to read it, with a caption that states its one claim; commands are shown with what they produce; project-internal references (ticket ids, issue numbers, session names, people) are introduced or moved to a closing note; lead with the problem, mechanism second; no essays defending a choice, state it and the alternative rejected. Each rule carries a before/after pair taken from the factory's own outputs (the three findings above are the first three).

B. **Preamble OUTPUT rule.** One line: every section a human will read (a spec's Problem and Evidence, a PR description's What changed and Known gaps, an ESCALATIONS line, a NEEDS-HUMAN question, a retro proposal) follows `docs/writing.md`; the standard is a declared input of every role, carried in the role-context block like the protected paths.

C. **Checkers apply it.** Critic rubric 6 is generalised from "the Problem section" to every human-facing section of the spec, with the same BLOCKING rule for an unglossed term of art in a first paragraph. The code reviewer gets one check: the PR description's What changed and Known gaps are readable by the gate operator (SHOULD-FIX, since the code, not the prose, is what merges). The doc-reviewer prompt in the Appendix becomes the checker for documentation tickets (README, overview, design-doc text), run as the critic is run.

D. **The briefing template** (`factory/context.template.md`) gains a line naming the reader of this repo's documents, filled per instance, so a target whose gate operator is a product manager and one whose operator is a kernel engineer get different glossing thresholds without changing the standard.

E. **First application.** `README.md` and the overview page are rewritten to the standard as part of this ticket or #21, whichever lands first, and become the worked examples the standard cites.

**Decisions:**
- The standard is one page with examples, not a style guide. Rules an agent cannot check in its own output are left out.
- Readability of prose is SHOULD-FIX for code PRs and BLOCKING for specs and documentation tickets: the spec is the contract the gate signs; the PR description is evidence for a merge the checkers already judged on the code.
- Terms of art are glossed, not avoided. The factory's names (gate, parked, round, instance) are the vocabulary; the rule is that the reader learns them where they first appear.

**Out of scope:** changing what roles decide; the routing table; the design doc's prompt blocks beyond the OUTPUT line and rubric 6 (prompt borrowings are #20); translating documents.

**Risk, protected and guardrail paths:** the role prompts (guardrail: agent prompts) and `docs/prompts/**` (`generated` on this instance) change by one preamble line and one rubric item; `factory/context.template.md` is harness code (`harness` class). Declared.

**Sequencing:** after #19's post-close step (the layout is settling); can run in parallel with #21, which it feeds. Enters as a ticket on this repo's instance.

**Acceptance the spec writer can make runnable:** `docs/writing.md` exists and is under 120 lines; `grep -c` of its rule headings equals the count of before/after pairs; the preamble contains the OUTPUT line; rubric 6 no longer names "the Problem section" alone; a critic run on a seeded spec whose Evidence section uses an unglossed system term in its first paragraph returns a rubric-6 finding; `README.md`'s first paragraph names what the project is and for whom with no project-internal reference.

**Fix as implemented elsewhere:** none. The overview draft (claude.ai artifact, operator-reviewed 2026-10-03) was rewritten to this standard by hand and is the first before/after example.



## Answer 1

Operator (2026-10-03): option (a). Standard and existing checkers only.

In scope: `docs/writing.md`; the preamble OUTPUT line; critic rubric 6 generalised to every human-facing section; one code-reviewer SHOULD-FIX check on PR-description readability (the out-of-scope line is read as allowing this one §6 check); the reader line in `factory/context.template.md`. Each prompt change lands in both copies, `docs/prompts/` and `factory/prompts/`, and the spec's Risk section declares `factory/prompts/**` (harness class).

Out of scope, to a follow-up issue: the Appendix doc-reviewer as a checker role for documentation tickets (a workflow and routing change). The README rewrite is not part of this ticket: README.md is already the overview (752ce40), and #21 part B keeps it current.

Open for the spec writer to decide and list under Decisions: how the standard reaches a target that has no `docs/writing.md` of its own (inlined into the preamble, a path into the harness checkout, or a per-instance copy). An acceptance item that needs an LLM run must be made deterministic (a stub or fixture through the harness) or say how it is judged.

## Your previous Triage output (the question you asked is answered above)

Type: feature

Title: A writing standard for every human-facing section the factory's agents produce, applied by the checkers

Summary: The factory's agents write for each other, not for the person who reads the result: the operator at a gate, a first-time reader of the README, a reviewer reading a PR description. That reader is technical but new to this system. Issue #11 (spec writer and critic rubric 6, changelog 41) fixed this for one section: the spec's Problem paragraph. The requester wants that fix generalised. Part A is a one-page standard, `docs/writing.md`, with checkable rules and before/after pairs. Part B is a preamble OUTPUT line that makes every human-read section follow it. Part C has the critic, the code reviewer and a documentation checker apply it. Part D adds a per-instance "reader" line to the briefing template. Part E holds the README to it as the first worked example.

Evidence:
- Operator review of the draft overview on 2026-10-03, three findings quoted in the request: (1) "`--accept-harness` appeared in a diagram with no statement of what requires it"; (2) a parenthetical pile-up the operator called "incomprehensible", asking for "at least the plain outline"; (3) "consider audience and what they know and don't know; this doc will be read by a technical audience that will probably see this project for the first time."
- The same failures recur in factory outputs, according to the request: Evidence sections quote commands without saying what they show; "What changed" is a file list; escalations name a state (`checks-in-flight`) without saying what is stuck.
- Verified on this checkout (`~/dev/spec-factory`, HEAD `2efc165`):
  - `docs/writing.md` does not exist (`ls docs/writing.md`: No such file or directory).
  - Rubric 6 is limited to the Problem section today: `docs/design.md:381-382` reads "the operator at the gate could read the Problem section". The same text is at `docs/prompts/03-spec-critic.md:19` and `factory/prompts/critic.md:19`.
  - The preamble OUTPUT block (`docs/design.md:217-221`) has no readability rule.
  - The PR DESCRIPTION format is at `docs/design.md:510-520`. The code reviewer's CHECK list is at `docs/design.md:528-547` and has no prose check.
  - The Appendix reviewer prompt (`docs/design.md:680-713`, `docs/prompts/99-doc-reviewer.md`) is a reviewer "of an agent-prompt document". The harness never runs it: `grep -n "doc-reviewer\|doc_reviewer\|99-doc" factory/*.py factory/workflows/*` returns nothing, and `factory/prompts/` has no file for it.
  - `factory/context.template.md` exists and has no "reader" line.
- No duplicate. The issue index (`dev/issues.md`) lists this request as #23, "not in intake". Store ticket T-0013 is this request itself (`status: ready-for-triage`). #11 is closed and covered only the Problem section. #21 is the README and current-truth ticket, which this request feeds. It does not duplicate #21.
- The requester gives no harness fix elsewhere ("Fix as implemented elsewhere: none"). Green has no writing-standard file (`find ~/dev/nanobot-upstream -maxdepth 4 -name "writing*.md"` finds nothing).

Assumptions (inferences, not stated by the requester):
- The prompts agents actually receive are the harness copies in `factory/prompts/*.md`, not `docs/prompts/`. `factory/cli.py:26,195-196` reads `PROMPTS / "preamble.md"` and `PROMPTS / f"{prompt_name}.md"`. The preamble copy is byte-identical to `docs/prompts/00-preamble.md` (diff run, no output). So parts B and C reach agents only if `factory/prompts/preamble.md`, `critic.md` and `reviewer.md` change as well. Those files are under the `harness` protected class (`factory/**`). The request's Risk section names `docs/prompts/**`, `factory/context.template.md` and "the role prompts", but not `factory/prompts/**` explicitly. The spec's Risk section must declare it.
- "Carried in the role-context block like the protected paths": protected paths reach agents because `fill_preamble` (`factory/instance.py:160-170`) fills them into the preamble from `instance.yaml`. Doing the same for the standard means a harness code change in compose or cli. A target repo other than this one (for example, green's Nanobot fork) has no `docs/writing.md` of its own. The request does not say how the standard reaches agents there: inlined text, a path into the harness checkout, or a per-instance copy. That is a design choice the spec writer should list as an Open question if the human does not settle it here.
- Part E is partly done already. Commit `752ce40` (2026-10-03, "README: the system as it runs today, inlined (overview, …)") folded the overview into `README.md`. README lines 3-12 already carry a "Reader" row and a separate internal-references note. "README.md and the overview page" are now one document, and the requester's README acceptance criterion may already pass on this checkout. A NEW criterion that already passes proves nothing, so the spec writer needs a criterion that would fail without this ticket's change.
- One proposed acceptance item is "a critic run on a seeded spec ... returns a rubric-6 finding". That is an LLM run, not a deterministic command. The spec writer will have to make it runnable through the harness stub or fixture path, or mark how it is judged.
- Suggested priority: P1, as the requester labels it. Priority is a human call.

Question for human: Part C turns the Appendix doc-reviewer prompt into a checker "run as the critic is run" for documentation tickets. The same request lists "the routing table" and "the design doc's prompt blocks beyond the OUTPUT line and rubric 6" as out of scope. Part C also changes the code-reviewer block (§6), which is a prompt block beyond those two. Running a new checker on a class of tickets needs a new role in the workflow (`factory/workflows/intake.js` runs only triage, spec writer, critic and planner). It also needs a rule for which tickets count as documentation tickets, which is routing. Which scope should the spec carry?
  - (a) Standard and existing checkers only. This ticket ships `docs/writing.md`, the preamble OUTPUT line, generalised rubric 6, the one code-reviewer SHOULD-FIX check and the briefing reader line, in both prompt copies. The out-of-scope line is read as allowing the §6 check. The doc-reviewer-as-checker work and the README rewrite go to a follow-up issue (README to #21).
  - (b) Everything in the request, including the doc-reviewer as a new checker role. The out-of-scope line is narrowed to allow the workflow change, the routing rule for "documentation ticket" and the rewrite of the Appendix prompt's job from prompt-set review to documentation review.
  - (c) The standard only, in two tickets. First `docs/writing.md`, the OUTPUT line and rubric 6 (the critic is the only checker). The code-reviewer check, the doc-reviewer and the briefing line follow after the standard has been used on one real spec.

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. The intent and evidence are clear and checked against the files, but the request's own out-of-scope line contradicts part C, and that needs a scope call before a spec can be written.
ESCALATIONS:
- Scope contradiction inside the request: part C (a new documentation checker and a §6 code-reviewer change) against "Out of scope: the routing table; the design doc's prompt blocks beyond the OUTPUT line and rubric 6". This is the question above.
- Protected path not explicitly declared: the running prompts are `factory/prompts/*.md` (`factory/cli.py:26,195-196`), which are in the `harness` class. The request's Risk section declares `docs/prompts/**` and `factory/context.template.md` but does not name `factory/prompts/**`. The spec's Risk section must declare it.
