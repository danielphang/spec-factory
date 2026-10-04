Type: feature

Title: Coding standard: add `docs/coding.md`, the coding twin of `docs/writing.md`, and point the implementer and code reviewer prompts to it

Summary:
The factory's coding roles have no rule against over-building. The implementer (the role that writes the code for one sub-ticket) is told to make "the smallest change that makes them pass for the right reason" and nothing about how to find that change. The code reviewer's maintainability check names no kind of finding to look for. The requester wants one new page, `docs/coding.md`, written in the same format as the writing standard `docs/writing.md`: each rule checkable in your own output, each with a before/after, and each naming its code-design principle. Its rules are:
- reuse before writing, with a check order (DRY);
- grep every caller and fix the shared function once (single responsibility, root cause over symptom);
- a `factory:` marker comment on every deliberate shortcut, naming its limit and when to upgrade it (technical-debt bookkeeping);
- the reviewer's finding tags `reuse:`, `stdlib:`, `native:`, `yagni:` and `delete:`;
- one name per concept, from spec to code (ubiquitous language), the same principle as writing rule 9.
The page opens with a precedence rule: a target repo's own instructions win where they disagree. The implementer and code reviewer prompts each get one line pointing to the page.

Evidence:
- The governing text is the operator's rescope comment on #20 (`gh issue view 20 --comments`), 2026-10-03. It says "the newest comment on #20 below governs where it differs from the original body". Its quotes: "the deliverable is `docs/coding.md`, the coding twin of `docs/writing.md`, not five edits scattered through the role prompts"; "the implementer and reviewer prompts get one pointer line to `docs/coding.md`, as the writing standard did"; "The retro's marker ledger (E) is unchanged."
- `docs/coding.md` does not exist (`ls docs/coding.md`: No such file or directory). `docs/writing.md` has 131 lines (`wc -l`) and rules 1–12. Each rule carries a check, a before/after and, where one fits, a `Code counterpart:` line. That format is the model the request names.
- The sequencing is met. The request lands "after #26", and #26's change is on `main`: `c64183a docs(writing): add rules 9-12 and code counterpart lines (T-0014.1)`, merged in `fcc8756`. Intake ticket T-0014 is closed. GitHub still shows #26 as OPEN. #19 is CLOSED (`gh issue view 19`).
- Writing rule 9 ("One name per concept", `docs/writing.md`) already cites "ubiquitous language (Evans, Domain-Driven Design)". So the request's new "one name per concept, spec to code" rule can cite that same principle.
- The text the old proposal would have replaced is still there:
  - implementer step 4, "Make the smallest change that makes them pass for the right reason" (`docs/design.md:493`, `docs/prompts/05-implementer.md:10`);
  - reviewer check 7, "Maintainability, only where it will cause real problems. Not style." (`docs/design.md:555`, `docs/prompts/06-code-reviewer.md:21`).
- "As the writing standard did" works like this. The preamble, the text that opens every role's prompt, names the writing standard through a `{writing standard}` placeholder (`docs/prompts/00-preamble.md:53`). The harness fills it with the absolute path of `docs/writing.md` in the runtime checkout (`factory/instance.py:163-166`). The build spec (`dev/build-harness.spec.md:158`) lists that placeholder. A pointer line in the implementer and reviewer prompts must also resolve to a path the role can open from the target repo.
- The precedence example is real. `~/dev/nanobot/.agent/design.md:15` is the heading "Prefer duplication over premature abstraction".
- No retro is built in this harness. The retro is the role that proposes prompt changes from pipeline outcomes. `factory/workflows/` holds only `build.js` and `intake.js`, `factory/prompts/` has no retro prompt, and `grep -rli retro factory/ tests/factory` finds only config templates and the preamble. The design and build spec describe it (`docs/design.md:635`; `dev/build-harness.spec.md:290`, `retro.js`).
- The request says no harness fix exists on the Nanobot side ("none"). Confirmed: green's `factory/` contains no `coding.md`, `grep every caller` or `reuse:` text.

Assumptions (the triage agent's inferences; the request does not state them):
- The pointer line takes the same form as the writing standard's. That means a new placeholder, filled by the harness with the runtime checkout's `docs/coding.md`. It needs a small change under `factory/**`, a protected harness path, so the spec's Risk section must declare it. The edited prompt blocks must also be re-copied into `docs/prompts/`, a protected generated path.
- Part C's reviewer output becomes a rule in `docs/coding.md`, together with its severities (`reuse:` blocks the merge; the other tags ride with an approval as should-fix) and its closing `net: -N lines possible` or `Lean already.` line. The reviewer prompt gets only the pointer line. The rescope's "not five edits scattered through the role prompts" implies this; it does not say it outright. The spec writer should list it under Decisions.
- Part D (cut any part a ticket doesn't need, at spec time) stays a rule in the spec writer's prompt, as the rescope says. Its probe in the spec critic's rubric 3 ("a part no acceptance item needs is a finding") is not mentioned. Under the rescope's governance rule it therefore stands.
- The Nanobot v3.5 driver is the session running the Nanobot re-port. "Both land before the nanobot v3.5 driver proceeds with intake" reads as urgency. It sets no requirement on this ticket.
- Suggested priority (a suggestion; priority is the human's call): p1. The operator ties it to the start of v3.5 intake.

Question for human:
What does this ticket do with part E, the retro's marker ledger? The ledger would be a harness-made list of every `factory:` comment for the retro, so it can see deliberate shortcuts. The rescope says E "is unchanged". Read literally, the original E stands: the retro INPUT, the routing table's Retro row, and the harness producing the ledger. But this harness has no retro yet, so a ledger producer would have nothing to feed.
- (a) Leave E out. This ticket ships `docs/coding.md`, the two pointer lines and D. The retro prompt, routing table and harness code are untouched. The `factory:` rule in `docs/coding.md` keeps markers greppable for later.
- (b) Ship E's text and defer its code. The design doc's retro INPUT and Retro row, and the build spec, name the ledger. Building the producer waits for the ticket that builds the retro. (Triage's reading of "unchanged": recommended.)
- (c) Ship E whole. Add the design text, and build the ledger producer under `factory/**` now, ahead of the retro it feeds.

Reason: n/a (NEEDS-HUMAN). No duplicate exists. The request is #20 as rescoped, imported as intake ticket T-0015, and no earlier intake ticket covers #20 (`dev/issues.md`: "not in intake yet"). #15 (closed, the simplifier role) is superseded by #20. #26 (T-0014, closed) added the writing rules this page will mirror. #25 (a documentation checker) is different work.

Out-of-scope observations:
- #26 shows as OPEN on GitHub, but T-0014 is closed as applied and its change is on `main` (`fcc8756`). `dev/issues.md` still lists T-0014 as "intake started 2026-10-03", with no merge.
- The original body's file paths are stale. It names `docs/spec-factory.md` and `prompts/0N-…`; after #19 these are `docs/design.md` and `docs/prompts/0N-….md`.

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. The deliverable and the wiring are clear and checked against the tree. Part E's sentence supports two readings, and they differ in whether this is a documentation-only ticket or also touches harness code.
ESCALATIONS: none
