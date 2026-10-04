Type: feature

Title: Coding standard: add `docs/coding.md`, the coding twin of `docs/writing.md`, point the implementer and code reviewer prompts to it, and name the `factory:` marker ledger in the retro's input

Summary:
The factory's coding roles have no rule against over-building. The implementer (the role that writes the code for one sub-ticket) is told to make "the smallest change that makes them pass for the right reason" and nothing about how to find it. The code reviewer's last check, "Maintainability, only where it will cause real problems", names no kind of finding. The requester wants one new page, `docs/coding.md`, in the format of the writing standard `docs/writing.md`. Every rule there can be checked in your own output, has a before/after, and names its code-design principle. The page opens with a precedence rule (a target repo's own instructions win where they disagree), and its rules are:
- reuse before writing, with a check order (DRY);
- grep every caller and fix the shared function once (single responsibility, root cause over symptom);
- a `factory:` comment on every deliberate shortcut, naming its limit and when to upgrade it (technical-debt bookkeeping);
- the reviewer's finding tags `reuse:`, `stdlib:`, `native:`, `yagni:` and `delete:`;
- one name per concept, from spec to code (ubiquitous language).
The implementer and code reviewer prompts each get one line pointing to the page. The spec-stage rule (cut any part the ticket does not need) stays in the spec writer's prompt. Per the operator's answer, part E ships as text only. The retro is the role that proposes prompt changes from pipeline outcomes. The design doc's retro INPUT, its Routing table Retro row and the build spec name the `factory:` marker ledger as part of the retro's input. The ledger is a harness-made list of every `factory:` comment. The code that produces it waits for the ticket that builds the retro.

Evidence:
- The governing text is the operator's rescope comment on #20 (`gh issue view 20 --comments`), 2026-10-03: "the deliverable is `docs/coding.md`, the coding twin of `docs/writing.md`, not five edits scattered through the role prompts"; "the implementer and reviewer prompts get one pointer line to `docs/coding.md`, as the writing standard did. The retro's marker ledger (E) is unchanged."
- Answer 1 (operator default, 2026-10-03), option (b): "Ship E's text and defer its code. The design doc's retro INPUT and Retro row, and the build spec, name the `factory:` marker ledger as intended design. Building the ledger producer waits for the ticket that builds the retro." The same answer says to use the post-#19 paths, `docs/design.md` and `docs/prompts/0N-….md`.
- `docs/coding.md` does not exist (`ls docs/coding.md`: No such file or directory). `docs/writing.md` has 131 lines (`wc -l`). Its intro says each rule is checkable in your own output, with an example and its rewrite, and a `Code counterpart:` line where a principle fits. That is the format the request names.
- The text the old proposal targeted is still present:
  - implementer step 4: `docs/design.md:493` and `docs/prompts/05-implementer.md:10`, "Make the smallest change that makes them pass for the right reason."
  - reviewer check 7: `docs/design.md:555` and `docs/prompts/06-code-reviewer.md:21`, "Maintainability, only where it will cause real problems. Not style."
- Here is how the writing standard is wired, the model for "as the writing standard did". The preamble, the text that opens every role's prompt, names it through a `{writing standard}` placeholder (`docs/prompts/00-preamble.md:53`). The harness fills that placeholder with the absolute path of the runtime checkout's `docs/writing.md` (`factory/instance.py:163-166`). The build spec documents this (`dev/build-harness.spec.md:158`).
- Where E's text goes:
  - the retro prompt's INPUT block: `docs/design.md:640`, copied in `docs/prompts/08-retro.md`;
  - the Routing table's Retro row: `docs/design.md:127`, "Full outputs behind every outcome signal since the last retro (piece 10), …";
  - the build spec's retro input composer, `factory retro-input`: `dev/build-harness.spec.md:323`, and its acceptance item 66 at line 435.
- No retro is built in this harness: `factory/workflows/` holds only `build.js` and `intake.js`. So the ledger producer has nothing to feed yet, which is the reason the operator deferred it.
- Sequencing is met. #19 is closed. #26's writing rules 9–12 are on `main` (`fcc8756 Merge factory/T-0014.1: Add rules 9–12 and code counterpart lines to the writing standard`). Writing rule 9 already cites ubiquitous language (Evans, DDD), so the new name rule can cite the same principle.
- The precedence example is real: `~/dev/nanobot/.agent/design.md:15` is the heading "Prefer duplication over premature abstraction".
- No harness fix exists on the Nanobot side, as the request says ("none"). Checked in the previous pass: green's `factory/` contains no `coding.md`, `grep every caller` or `reuse:` text.
- No duplicate exists. `dev/issues.md:27` maps #20 to intake ticket T-0015 and no other ticket. #15 (the simplifier role) is closed and superseded by #20 (`dev/issues.md:22`).

Assumptions (the triage agent's inferences; the request does not state them):
- The pointer line takes the writing standard's form: a new placeholder, filled by the harness with the runtime checkout's `docs/coding.md`. That needs a small change in `factory/instance.py`, under `factory/**`, a protected harness path. The edited prompt blocks are re-copied into `docs/prompts/`, a protected generated path. The spec's Risk section must declare both, and the build spec line that lists the placeholders (`dev/build-harness.spec.md:158`) changes with them.
- Part C's reviewer rules move into `docs/coding.md`: the tags, their severities (`reuse:` blocks the merge; the others ride with an approval as should-fix) and the closing `net: -N lines possible` or `Lean already.` line. The reviewer prompt gets only the pointer line. Whether check 7's "Maintainability, only where…" wording is replaced or kept beside the pointer is a decision the spec writer should state under Decisions. The rescope's "not five edits scattered through the role prompts" suggests the pointer replaces the check's body.
- Part D's spec critic probe ("a part no acceptance item needs is a finding", rubric 3 at `docs/design.md:379`) is not mentioned in the rescope, so it stands with the spec writer rule. The spec writer may cut it, but should then say so under Decisions.
- `README.md` is the current-state page and lists `docs/writing.md` in its files table (`README.md:349`). Adding `docs/coding.md` adds a path, so by the briefing's rule the README gains a row in the same ticket.
- The design doc change carries its own changelog entry in `docs/changelog.md`, which credits ponytail (MIT) for the check order and the tag vocabulary, as the original body's "Source read" line says.
- Suggested priority (a suggestion; priority is the human's call): p1. The operator wants it landed before the Nanobot v3.5 driver, the session running the Nanobot re-port, starts intake.

Reason: n/a (ACCEPT). The one open decision, what to do with part E, is answered: option (b).

Out-of-scope observations:
- #26 still shows as OPEN on GitHub, though its change is merged (`fcc8756`). `b33e593` notes it as "merged and awaiting acceptance", which explains the open state.

STATUS: ACCEPT
CONFIDENCE: high. The deliverable, the wiring and part E's scope are all set by the operator's rescope and Answer 1, and every path cited was checked on this checkout.
ESCALATIONS: none
