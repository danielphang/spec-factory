=== proposal.md
## Problem

The factory has no rule that stops its coding agents from building more than a ticket needs. Two
agents write and judge code. The implementer writes the code for one piece of a ticket. Its prompt
says to make "the smallest change" that passes the tests, and nothing about how to find that
change. The code reviewer judges that code before it merges. Its last check says only
"Maintainability, only where it will cause real problems", which gives the reviewer no kind of
finding to look for, so a reviewer either pads its review or says nothing. Coding agents are known
to over-build. They add a new helper beside one that already exists, hand-write something the
standard library ships, or add an interface with one implementation. Nothing in the factory
catches this. The operator pays at the gate, where they approve specs and merges, in bigger diffs.
After the merge they own the duplicate code.

This change adds one page, `docs/coding.md`, the coding counterpart of the writing standard. The
writing standard is `docs/writing.md`, the page every agent follows when it writes something a
person reads. The new page has five rules. Each rule can be checked by the agent in its own
output, has an example with its rewrite, and names the code-design principle it applies:
- reuse before writing;
- find every caller before fixing a shared function, then fix it once;
- mark each deliberate shortcut with a `factory:` comment;
- tag each over-building review finding;
- use one name per concept from spec to code.

The page opens with a precedence rule: a target repository's own instructions win where they
disagree with it. The implementer and reviewer prompts each gain one line pointing to the page.

Two smaller pieces ride with it:
- The spec writer is told to cut any part the ticket does not need, and the spec critic treats
  such a part as a finding.
- The retro is the planned agent that proposes prompt changes from pipeline outcomes. Its design
  now lists, as one of its inputs, every `factory:` comment in the code. The code that builds that
  list waits for the ticket that builds the retro.

## Evidence

- The page does not exist. `ls docs/coding.md` fails with "No such file or directory". The format
  it copies is `docs/writing.md`: one numbered rule per heading, a `Check:` line saying how to
  verify the rule in your own output, a sourced `Before (` example and an `After:` rewrite.
- The text this ticket replaces is still in place, in all three copies of each prompt. The copies
  are the design document `docs/design.md`, its verbatim copy under `docs/prompts/`, and the
  copy the harness runs, under `factory/prompts/`, which has some placeholders already filled in.
  The harness is the code that starts each agent run and keeps its records.
  - Implementer step 4: `docs/design.md:493`, `docs/prompts/05-implementer.md:10`,
    `factory/prompts/implementer.md:10`: "Make the smallest change that makes them pass for the
    right reason."
  - Code reviewer check 7: `docs/design.md:555`, `docs/prompts/06-code-reviewer.md:21`,
    `factory/prompts/reviewer.md:21`: "Maintainability, only where it will cause real problems.
    Not style."
- Today an implementer or reviewer run is not pointed at any coding standard. I started one of
  each in a throwaway target repository, using a throwaway store (scenario
  implementer-and-reviewer-prompts-name-the-page below), and searched each system prompt for the
  page's path. The output was `implementer standard=[] unfilled=0`, `reviewer standard=[]
  unfilled=0`, `file=absent`. Neither prompt names the page, neither has a placeholder for it,
  and the file is absent.
- The harness fills placeholders only in the shared preamble, the text at the top of every
  agent's prompt. `fill_preamble` in `factory/instance.py` (lines 160–172) fills
  `{writing standard}` with the absolute path of `docs/writing.md` in the running checkout.
  `run_start` in `factory/cli.py` then appends the role's prompt unchanged (line 219). So a
  placeholder written into the implementer or reviewer prompt would reach the agent unfilled
  unless the harness is changed.
- The spec writer has no rule about cutting unneeded parts. Its RULES, at `docs/design.md`
  lines 286–320, cover size, runnable acceptance, open questions, the Problem section and
  revisions. Critic rubric 3 (`docs/design.md:379`) checks size, out-of-scope and "Tests to
  change", but not whether each part is needed.
- The retro's inputs do not mention markers. Its INPUT block is at `docs/design.md:640–648` and
  is copied in `docs/prompts/08-retro.md`. Its Routing table row is at `docs/design.md:127`. The
  build spec's retro input composer is at `dev/build-harness.spec.md:323`, with its acceptance
  item 66 at line 435. `grep -c 'marker ledger'` on those three files prints 0 for each. No retro
  is built: `factory/workflows/` holds only `build.js` and `intake.js`, so the list has no reader
  yet. That is why the operator deferred building it (the operator's first answer, option b).
- The rule 1 example is real code. `ensure_gitignore` in `factory/store.py` creates the store
  directory and writes `.gitignore` itself (lines 59–60). That repeats `write_text`, defined
  just after it in the same module (line 63), which does the same two steps.
- The precedence example is real. `~/dev/nanobot/.agent/design.md:15` is the heading "Prefer
  duplication over premature abstraction". Its text limits the heading to Nanobot's channel and
  provider files.
- The proposed change works as specified. I applied it to a scratch clone of this repository at
  `b33e593`, without the new test file. Every scenario below printed its expected after-state
  there. `git diff --check main...HEAD` exited 0, and the harness suite printed `126 passed`, the
  same count as on `main`. The change came to 149 added and 15 removed lines in 16 files.

## Root cause

No coding standard was ever written. The writing standard (changelog entry 43) gave every role a
page for its prose, with one pointer line in the preamble. No page covers code, and the two
coding prompts carry only the step 4 and check 7 sentences quoted above. The harness fills
`{writing standard}` only in the preamble (`fill_preamble`, `factory/instance.py`), so a role
prompt has no way to name a page by path. The spec-stage cut rule and the retro's list of
`factory:` comments were proposed in the original issue and never made.

## Out of scope

- The verifier prompt, the triage and planner prompts, and the shared preamble.
- Any new role or checker seat. That includes the simplifier from the closed issue that this one
  replaced.
- The code that builds the list of `factory:` comments, and the retro itself (`retro-input`,
  `retro.js`). Both wait for the ticket that builds the retro.
- The `agents/` role-agent templates. They are already out of date with `factory/prompts/`, as
  noted under Out-of-scope observations.
- Fixing the duplication in `ensure_gitignore` that rule 1 uses as its example.
- Rewriting existing code to the new rules.
- Checks 1–6 and 8 of the code reviewer, and its OUTPUT format.
- A behaviour benchmark of the new rules in the shape of ponytail's agentic runs. It is an
  optional Operator step, not acceptance.
- Green (`~/dev/nanobot-upstream`), which runs its own copy of the harness.

## Open questions

none

## Decisions

- **The page has five rules, in the request's order.** Each has `Check:`, `Principle:`, `Before (`
  and `After:` lines. The twin of the writing standard's "Code counterpart:" line is
  `Principle:`, because these rules are already about code. The precedence rule comes before rule
  1, as the operator asked.
- **The page's path reaches the two prompts through a placeholder, `{coding standard}`.** The
  harness fills it when a run starts, with the path of `docs/coding.md` in the running checkout,
  the same way it fills `{writing standard}`. One helper fills both placeholders. The preamble
  uses it, and so does the role prompt, which the harness does not fill today. Two alternatives
  were rejected:
  - Naming the page in the preamble. The preamble is out of scope, and the rescope asks for the
    pointer in the implementer and reviewer prompts only.
  - A repository-relative path. The implementer works in the target repository, which has no
    `docs/coding.md`.
- **Check 7's text is replaced by the pointer, not kept beside it.** Keeping "Maintainability,
  only where it will cause real problems" would leave two checks that overlap. It is also the
  vague check the request says reviewers pad or skip. The cost: the reviewer loses a general
  maintainability check that is not about over-building. Correctness (check 2) and scope (check
  3) still apply.
- **The PR description line for markers lives in rule 3, not in the implementer's PR template.**
  The rescope gives each coding prompt one line only. The implementer's rules already require
  "Disclose every shortcut … in the PR description". Rule 3 says the shortcuts go under Known
  gaps.
- **Tag severities come from the request's part C.** `reuse:` is BLOCKING; `stdlib:`, `native:`,
  `yagni:` and `delete:` are SHOULD-FIX. A finding against rules 2, 3 or 5 takes no tag, and its
  severity is that of a correctness or scope finding. The tag goes after the severity, so the
  reviewer's Findings line keeps its shape. Ponytail's sixth tag, `shrink:`, is not adopted
  (request).
- **The spec-stage cut rule ships in this ticket**, in the spec writer's RULES and as a probe in
  critic rubric 3. The rescope keeps it among the spec writer's rules, not in `docs/coding.md`.
  The probe is reworded from the request's "a part no acceptance item needs is a finding" to "a
  lettered part the ticket's intent does not need is a finding". Read literally, the original
  would push spec writers to add acceptance items for bookkeeping parts such as a changelog
  entry. That is padding, which the anti-Goodharting rules forbid.
- **The list of markers, called the marker ledger, is named as design only (the operator's first answer, option b).**
  The harness builds it from the code on the integration branch when the retro runs. It is not
  appended to the audit log (the append-only record of every run). Markers live in the code, so a
  marker removed since the last retro should drop out. The ledger reads code comments, not
  documents, so the example markers in `docs/coding.md` are not rows.
- **Three of the five examples are labelled "illustration".** The rule 1 example is live code in
  this repository. The rule 2 example comes from ponytail's benchmark, as reported in the
  request. No real factory output matched rules 3, 4 or 5, so their examples are written for the
  page and say so.
- **The `agents/` templates are not changed**, as the writing-standard ticket decided before. Runs
  that read `system-prompt.txt` get the new text.
- **`README.md` gains one row in its files table.** The retro bullet under "Where this can go" is
  unchanged, because it already describes the retro at that level.

## Risk

Blast radius:
- Every implementer and code-reviewer run gains one line and one absolute path. Every spec-writer
  and critic run gains the cut rule.
- Reviewers will raise more findings. A `reuse:` finding blocks the merge, so expect more PR
  rounds at first.
- Critics may return more specs for revision under the rubric 3 probe.
- The change touches `factory/**`, so the harness revision moves. This instance refuses its store
  until the operator accepts the new revision. Nothing reaches a running role before the runtime
  moves (Operator steps).
- Green runs its own copy of the harness and is not affected.

Protected and guardrail paths this change touches:
- **harness (`factory/**`):** `factory/instance.py` (one helper fills both standards' paths),
  `factory/cli.py` (the role prompt is filled), `factory/prompts/implementer.md`,
  `factory/prompts/reviewer.md`, `factory/prompts/spec_writer.md`, `factory/prompts/critic.md`.
- **generated (`docs/prompts/**`):** `02-spec-writer.md`, `03-spec-critic.md`,
  `05-implementer.md`, `06-code-reviewer.md`, `08-retro.md`. Each is re-copied from its changed
  design block.
- **Guardrail, agent prompts:** the spec writer, spec critic, implementer, code reviewer and retro
  blocks in `docs/design.md`, plus the copies above.

Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, existing
tests, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Also changed, unprotected: `docs/coding.md` (new), `docs/design.md` (the role-context paragraph at
line 54 and the Routing table's Retro row), `docs/changelog.md` (entry 44),
`dev/build-harness.spec.md` (three sentences), `README.md` (one row), and one new test file under
`tests/factory/`.

## Operator steps

0. **Before step 1: the operator's acceptance test (operator, pre-approved gate, 2026-10-03).** The merge changes nothing until the runtime moves, so the acceptance happens here, not in the merge checks.
   - **Sample.** Two real implementer diffs from this store (for example T-0012.3 and T-0013.1), each with its sub-ticket text.
   - **Review.** A fresh reviewer agent reviews each diff once under the pre-merge reviewer prompt, and once under the merged prompt with `docs/coding.md`. The two finding lists go side by side.
   - **Rewrite.** For one sub-ticket, a fresh implementer re-implements it in a scratch checkout with and without `docs/coding.md`. Both must pass that sub-ticket's acceptance. The diffs are compared on size and on the page's rules.
   - **Operator.** The operator reads a side-by-side page and approves. That approval is this ticket's acceptance. Only then does step 1 run. A rejection goes back as a new ticket; it does not revert the merge, which is inert until the runtime moves.
1. **Upgrade, then accept.** After merge, between tickets, move the runtime to the merge commit
   and accept it on this instance, as the README's "Upgrading the runtime" describes. The runtime
   is the pinned checkout at `~/dev/spec-factory-harness` that runs every ticket. This change
   touches harness code, so `--accept-harness` is required. Until then, no agent sees the change.
2. **Optional: judge the first review.** Read the findings of the first code-reviewer run after
   step 1. Pass: each over-building finding carries a tag after its severity and names what
   replaces the code, and the review ends with `net: -N lines possible` or `Lean already.`.
   A failure goes into a follow-up issue; it does not revert this change. A deeper check is a
   seeded repository in the shape of ponytail's benchmark: a shared `_debit()` and a ticket that
   names one caller, built with and without the page, on Opus or Sonnet. That is the operator's
   call and not part of this ticket.

=== design.md
## Proposed change

The parts are listed in dependency order. B needs A's file, C needs B's placeholder, and every
part's acceptance is listed in `verification.md`. Wrap prose at no more than 100 characters, as
the documents do now. The prompt blocks keep their narrower wrap, and table rows in
`docs/coding.md` may run past 100.

**A. `docs/coding.md` (new).** This exact text. Rewrapping is allowed; the gate fixes the wording.

```markdown
# Coding standard

A coding agent tends to build more than its ticket needs: a new helper beside one that already
exists, hand-rolled code for something the standard library ships, an interface with one
implementation. The operator pays for each at the gate, in a bigger diff, and later owns the
duplicate code. This page is how the spec factory's implementer (the role that writes the code for
one sub-ticket) and its code reviewer (the role that judges that code before it merges) keep a
change as small as the ticket allows. It is the twin of the writing standard, `docs/writing.md`:
the same format, and where both pages name a principle, they name the same one.

**Precedence.** A target repository's own instructions win where they disagree with this page.
They are in its `AGENTS.md` and the documents that file points to. Example: Nanobot's
`.agent/design.md` says "Prefer duplication over premature abstraction" for its channel and
provider files. In those files DRY (rule 1) gives way, and a repeated block is not a `reuse:`
finding (rule 4).

Each rule below is one you can check in your own output before you hand it in: the implementer
in its diff and PR description, the reviewer in its findings. Each names its code-design
principle and has an example and its rewrite. An example marked "illustration" was written for
this page; the others are sourced.

## 1. Reuse before writing: take the first rung that holds.
Check: for each function, class, type or dependency your diff adds, you can name the rung it sits
on and say why no earlier rung held.
1. A helper, util, type or pattern already in this repo.
2. The standard library.
3. A native platform feature: a database constraint over app code, an atomic file-system call
   over a lock.
4. A dependency already installed.
5. One line.
6. The minimum code that works.
Whether the thing should exist at all is the spec's question, not the implementer's: the spec
writer cuts any part the ticket does not need.
Principle: DRY, don't repeat yourself (Hunt and Thomas, The Pragmatic Programmer).
Before (`factory/store.py`, `ensure_gitignore`, as of 2026-10-03): it creates the store directory
and writes `.gitignore` with its own two lines, which repeat `write_text` in the same module.
After: it calls `write_text`, so a later change to how the store writes files, such as its
encoding or an atomic replace, reaches `.gitignore` too.

## 2. Fix the shared function once: grep every caller before you edit.
Check: for each existing function your diff changes, your PR description names its callers, found
by a grep of the repo, and says why the fix sits where it does.
Principle: single responsibility, and root cause over symptom: a ticket names a symptom, and the
fix goes where the cause is, once.
Before (ponytail's comprehension benchmark, 2026-06-22: a seeded `bank.py` where `transfer()` and
`withdraw()` share `_debit()`, and the bug report names only transfers): told to "trace the flow
end to end", Opus scored 0 of 3. Patching only `transfer()` leaves `withdraw()` broken.
After: told to "grep every caller of the function you touch; fix the shared function once",
Sonnet 4.6 and Opus 4.8 scored 6 of 6, against a baseline of 1 of 6. One guard in `_debit()` is a
smaller diff than one per caller.

## 3. A deliberate shortcut carries a `factory:` comment naming its limit and upgrade trigger.
Check: each simplification in your diff with a known limit (a global lock, an O(n²) scan, a naive
heuristic) has a comment starting `factory:` that names the limit and when to upgrade. Your PR
description's Known gaps lists each marker you added, or says "factory: markers added: none".
Principle: technical-debt bookkeeping; debt taken on purpose is recorded where it lives
(Cunningham's debt metaphor).
Before (illustration): `with ACCOUNTS_LOCK:` around every account update, with no comment, so
the next reader cannot tell a choice from an oversight.
After: `# factory: one global lock; per-account locks if transfers contend` above it. The marker
is greppable: `grep -rnE '(#|//|/\*) ?factory:'` lists every one in the code.

## 4. A reviewer's over-building finding carries one tag and names what replaces the code.
Check: each over-building finding (code the change could have reused, or did not need) starts,
after its severity, with one tag from the table (`[BLOCKING] reuse: file:line: problem →
consequence`), names what the table says to name, and has the table's severity. A finding against
rule 2, 3 or 5 takes no tag; it earns its severity as a correctness or scope finding. The pass ends
with `net: -N lines possible`, where N is the lines the tagged findings would remove, or with
`Lean already.`
Principle: per tag, in the table.

| Tag | Flags | Names | Severity | Principle |
|---|---|---|---|---|
| `reuse:` | a helper, type or pattern this repo already has | its path | BLOCKING | DRY |
| `stdlib:` | code the standard library ships | the function | SHOULD-FIX | don't reinvent |
| `native:` | code or a dependency doing the platform's job | the feature | SHOULD-FIX | don't reinvent |
| `yagni:` | an abstraction, setting or layer with one use | what it folds into | SHOULD-FIX | YAGNI |
| `delete:` | dead code, unused flexibility, a speculative feature | nothing | SHOULD-FIX | dead code |

Before (illustration): "Maintainability: some duplication in the store module; consider
refactoring."
After: "[BLOCKING] reuse: factory/store.py:59: `ensure_gitignore` repeats `write_text` → a change
to how the store writes files misses `.gitignore`; call `write_text`." Then "net: -1 lines
possible".

## 5. One name per concept, from spec to code.
Check: each term your spec defines (in its Problem section; for the factory itself, in the
README's terms table) is the identifier your code uses for that concept, and no identifier you add
is a synonym for one the repo already has.
Principle: ubiquitous language (Evans, Domain-Driven Design), the same principle as the writing
standard's rule 9.
Before (illustration): the README's terms table defines a "parked" ticket, and a change adds the
state `on_hold` and a function `hold_ticket()` for the same thing.
After: the state stays `parked` and the command stays `ticket park`, the names the store and the
README already use.

The check order (rule 1) and the tag vocabulary (rule 4) are adapted from ponytail
(DietrichGebert/ponytail, MIT), as the design document's changelog records.
```

**B. Pointer lines (implementer and code reviewer).** Make the same edit in `docs/design.md`
(§5 Implementer, §6 Code reviewer), `docs/prompts/05-implementer.md`,
`docs/prompts/06-code-reviewer.md`, `factory/prompts/implementer.md` and
`factory/prompts/reviewer.md`.
- Implementer PROCESS step 4: keep its line, and add one line under it:
  ```
  4. Make the smallest change that makes them pass for the right reason.
     Follow the coding standard at {coding standard}.
  ```
- Code reviewer CHECK 7: replace `7. Maintainability, only where it will cause real problems. Not
  style.` with:
  ```
  7. The coding standard at {coding standard}: a finding against it
     carries the tag and severity the standard gives it. Not style.
  ```

**C. The harness fills `{coding standard}`.**
- In `factory/instance.py`, add `fill_standards(text)` next to `fill_preamble`. It replaces
  `{writing standard}` with `HARNESS / "docs" / "writing.md"` and `{coding standard}` with
  `HARNESS / "docs" / "coding.md"`, both as absolute paths. `fill_preamble` calls it in place of
  its own `{writing standard}` line, and its docstring points there.
- In `factory/cli.py` `run_start`, pass the role prompt through `instance.fill_standards` before
  appending it to the preamble.
- Rejected: a second, separate `.replace` in `cli.py`. It would repeat the path logic, against
  rule 1 of the new page.

**D. Spec-stage cut.** Make the same edit in `docs/design.md`, `docs/prompts/02-spec-writer.md`
and `factory/prompts/spec_writer.md` for the writer, and in `docs/design.md`,
`docs/prompts/03-spec-critic.md` and `factory/prompts/critic.md` for the critic.
- Spec writer RULES: directly after the Size rule (the one ending "seams as lettered parts under
  Proposed change."), add:
  ```
  - Cut before you specify: for each part, ask first whether the ticket's
    intent needs it at all. A speculative part is cut, and named in one
    line under Out of scope.
  ```
- Critic rubric 3: its last line `   breaks, with a reason each.` becomes:
  ```
     breaks, with a reason each; a lettered part the ticket's intent does
     not need is a finding.
  ```

**E. The retro's input names the marker ledger.** Text only; no code.
- Retro INPUT, in `docs/design.md` §8 and re-copied to `docs/prompts/08-retro.md`. After the line
  `is how you propose a model change.`, add:
  ```
  Also the marker ledger: one row per `factory:` comment in the code on
  the integration branch (a shortcut its author marked, per the coding
  standard), with its file:line, the limit it names and its upgrade
  trigger, flagged no-trigger where it names none.
  ```
- The Routing table's Retro row (`docs/design.md:127`). Its Receives cell ends "…for the period
  and for each prior proposal's window". Append: `, and the marker ledger: one row per `factory:`
  comment in the code on the integration branch, with file:line, limit and upgrade trigger,
  flagged `no-trigger` where it names none, composed by the harness when the retro runs`.
- `dev/build-harness.spec.md:323`, the `retro-input` sentence. Replace "and run and outcome counts
  per `(role, model)` from `runs/*/meta.yaml` and `log/`;" with "run and outcome counts per
  `(role, model)` from `runs/*/meta.yaml` and `log/`, and the marker ledger (one row per
  `factory:` comment in the code on `main`: file:line, limit, upgrade trigger, and `no-trigger`
  where the comment names none);".
- `dev/build-harness.spec.md` item 66 (line 435). After "`counts per role` (one line per `(role,
  model)`, item 72)", add ", `marker ledger` (one row per `factory:` code comment on `main`; a
  comment naming no upgrade trigger carries `no-trigger`)".

**F. Records and a test.**
- `docs/design.md:54`, the role-context paragraph. After its last sentence, which ends "…and
  `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it.",
  add: "`{coding standard}`, in the implementer and code reviewer prompts, is filled the same way
  with the path of `docs/coding.md` in that checkout."
- `dev/build-harness.spec.md:158`. After "with the absolute path of its `docs/writing.md`", add ",
  and `{coding standard}`, in the implementer and code-reviewer prompts, with the absolute path of
  its `docs/coding.md`".
- `docs/changelog.md`: entry 44, after entry 43 and before the "Declined:" line. It says what
  the page holds (five rules, the precedence rule, the tags and their severities), the two
  pointer lines and the `{coding standard}` fill, that check 7's old text is replaced, the spec
  writer's cut rule and the critic's probe, and that the marker ledger is design whose producer
  waits for the retro. It credits ponytail (DietrichGebert/ponytail, MIT) for the check order
  and the tag vocabulary.
- `README.md`, "Where things live". After the `docs/writing.md` row, add:
  `| `docs/coding.md` | The coding standard for the implementer and code reviewer; their prompts
  name the runtime's copy |`.
- One new test file, `tests/factory/test_coding_standard.py`, driven through `bin/factory` as
  `tests/factory/test_writing_standard.py` is. It checks:
  - an implementer run's and a reviewer run's system prompt name the running checkout's
    `docs/coding.md`, with no `{coding standard}` left unfilled;
  - the spec writer, implementer and retro design blocks equal their `docs/prompts/` copies.

## Tests to change

none. The two existing tests that read prompt text still pass unchanged. The scratch-clone trial
ran the suite with every part except the new test file applied, and it printed `126 passed`:
- `test_design_block_equals_its_prompt_copy` covers the critic and reviewer blocks, and both
  copies change together.
- `test_system_prompt_is_the_design_preamble_filled_from_the_instance` uses the triage role,
  whose prompt has no placeholder.

=== specs/coding-standard/spec.md
## ADDED Requirements

### Requirement: coding-standard-page-of-checkable-rules
The repository SHALL have `docs/coding.md`, which states a precedence rule before its first rule
and holds five numbered rules, each with one `Check:`, one `Principle:`, one `Before (` and one
`After:` line.

#### Scenario: coding-page-has-five-checkable-rules
- WHEN (bash, from `~/dev/spec-factory`) `if [ -f docs/coding.md ]; then f=docs/coding.md; echo "rules=$(grep -o '^## [0-9]*\.' $f | tr -dc '0-9\n' | paste -sd, -) check=$(grep -c '^Check: ' $f) principle=$(grep -c '^Principle: ' $f) before=$(grep -c '^Before (' $f) after=$(grep -c '^After: ' $f) precedence=$(awk '/^\*\*Precedence\.\*\*/ {p=NR} /^## 1\./ {r=NR} END {print (p && p < r) ? "first" : "absent"}' $f)"; else echo missing; fi`
- THEN it prints `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first`

### Requirement: coding-standard-carries-the-requested-rules
`docs/coding.md` MUST contain the precedence example, the grep-every-caller rule, the `factory:`
marker, the five reviewer tags, both closing lines of a review pass, and the principles DRY,
YAGNI and ubiquitous language.

#### Scenario: coding-page-has-every-requested-phrase
- WHEN (bash, from `~/dev/spec-factory`) `b=$(printf '\140'); n=0; for h in 'Prefer duplication over premature abstraction' 'grep every caller' "${b}factory:${b}" "${b}reuse:${b}" "${b}stdlib:${b}" "${b}native:${b}" "${b}yagni:${b}" "${b}delete:${b}" 'net: -N lines possible' 'Lean already.' 'ubiquitous language' 'DRY' 'YAGNI'; do if cat docs/coding.md 2>/dev/null | tr '\n' ' ' | grep -qF "$h"; then n=$((n+1)); else echo "missing: $h"; fi; done; echo "found=$n of 13"`
- THEN it prints only `found=13 of 13`

### Requirement: reviewer-tag-severities
The tag table in `docs/coding.md` SHALL give `reuse:` the severity BLOCKING and `stdlib:`,
`native:`, `yagni:` and `delete:` the severity SHOULD-FIX.

#### Scenario: tag-table-severities
- WHEN (bash, from `~/dev/spec-factory`) `b=$(printf '\140'); for t in reuse stdlib native yagni delete; do printf '%s=%s ' "$t" "$(grep -E "^\| ${b}$t:${b} \|" docs/coding.md 2>/dev/null | grep -oE 'BLOCKING|SHOULD-FIX' | paste -sd+ -)"; done; echo`
- THEN it prints `reuse=BLOCKING stdlib=SHOULD-FIX native=SHOULD-FIX yagni=SHOULD-FIX delete=SHOULD-FIX` (a trailing space is allowed)

### Requirement: implementer-and-reviewer-point-to-the-page
The implementer's PROCESS step 4 and the code reviewer's CHECK 7 SHALL each name the coding
standard through `{coding standard}`, in all three copies of each prompt, and check 7's old
"Maintainability, only where" text MUST be gone.

#### Scenario: pointer-line-in-every-copy
- WHEN (bash, from `~/dev/spec-factory`) `grep -cF 'Follow the coding standard at {coding standard}.' docs/design.md docs/prompts/05-implementer.md factory/prompts/implementer.md; grep -cF '7. The coding standard at {coding standard}' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; grep -cF 'Maintainability, only where' docs/design.md docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md`
- THEN the first six lines each end `:1` and the last three each end `:0`

### Requirement: run-prompts-name-the-running-checkouts-page
When an implementer or code-reviewer run starts, its system prompt MUST name the absolute path of
`docs/coding.md` in the running harness checkout, with no `{coding standard}` placeholder left.

#### Scenario: implementer-and-reviewer-prompts-name-the-page
- GIVEN a scratch target repository with an instance and a throwaway store, with the ticket's status set by `ticket set` so that each role can start
- WHEN (bash, from `~/dev/spec-factory`) `H=$(pwd -P); T=$(mktemp -d); git -C "$T" init -q -b main; git -C "$T" -c user.name=t -c user.email=t@t commit -q --allow-empty -m init; printf '# demo\n\nDo the thing.\n' > "$T/r.md"; F() { (cd "$T" && env -u FACTORY_INSTANCE -u FACTORY_REPO -u FACTORY_INTEGRATION_BRANCH "$@"); }; F env -u FACTORY_STATE "$H/bin/factory" init --repo-name demo >/dev/null 2>&1; S="$T/s"; X() { F env FACTORY_STATE="$S" "$H/bin/factory" "$@" >/dev/null; }; X ticket new --file "$T/r.md"; X ticket set T-0001 status=ready-for-implementer; X run start --role implementer --ticket T-0001 --model opus; X ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git -C "$T" rev-parse HEAD); X run start --role reviewer --ticket T-0001 --model opus; for r in implementer reviewer; do P=$(ls "$S"/runs/*-$r/system-prompt.txt); echo "$r standard=[$(grep -oF "$H/docs/coding.md" "$P" | head -1)] unfilled=$(grep -c '{coding standard}' "$P")"; done; echo "file=$(test -s "$H/docs/coding.md" && echo present || echo absent)"; rm -rf "$T"`
- THEN it prints `implementer standard=[<checkout>/docs/coding.md] unfilled=0`, `reviewer standard=[<checkout>/docs/coding.md] unfilled=0` and `file=present`, where `<checkout>` is the absolute path of the checkout it ran in

=== specs/spec-writer/spec.md
## ADDED Requirements

### Requirement: spec-stage-cut
The spec writer's RULES SHALL tell it to cut any part the ticket's intent does not need, and
critic rubric 3 SHALL make such a part a finding, in all three copies of each prompt.

#### Scenario: cut-rule-and-probe-in-every-copy
- WHEN (bash, from `~/dev/spec-factory`) `grep -cF -- '- Cut before you specify: for each part' docs/design.md docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; grep -cF 'a lettered part the ticket' docs/design.md docs/prompts/03-spec-critic.md factory/prompts/critic.md`
- THEN it prints six lines, each ending `:1`

=== specs/retro/spec.md
## ADDED Requirements

### Requirement: retro-input-names-the-marker-ledger
The retro's INPUT block, its Routing table row and the build spec's retro input composer SHALL
name the marker ledger, one row per `factory:` comment in the code on the integration branch.

#### Scenario: marker-ledger-named-in-design-and-build-spec
- WHEN (bash, from `~/dev/spec-factory`) `echo "design=$(grep -c 'marker ledger' docs/design.md) retro=$(grep -c 'marker ledger' docs/prompts/08-retro.md) buildspec=$(grep -c 'marker ledger' dev/build-harness.spec.md) row=$(grep '^| Weekly audit done' docs/design.md | grep -c 'marker ledger')"`
- THEN it prints `design=2 retro=1 buildspec=2 row=1`

=== specs/design-doc/spec.md
## ADDED Requirements

### Requirement: prompt-copies-stay-verbatim
Every changed prompt block in `docs/design.md` MUST equal its `docs/prompts/` copy byte for
byte. The harness copies under `factory/prompts/` MUST differ from those copies only in the
placeholders they already fill.

#### Scenario: changed-blocks-verbatim-and-harness-copies-in-step
- WHEN (bash, from `~/dev/spec-factory`) `q=$(printf '\140\140\140'); for s in "2. Spec writer:02-spec-writer" "3. Spec critic:03-spec-critic" "5. Implementer:05-implementer" "6. Code reviewer:06-code-reviewer" "8. Retro:08-retro"; do f=${s##*:}; sed -n "/^## ${s%%:*}\$/,/^$q\$/p" docs/design.md | sed "1,/^${q}text\$/d;\$d" | cmp -s - docs/prompts/$f.md && echo "$f verbatim" || echo "$f differs"; done; for p in "02-spec-writer spec_writer" "03-spec-critic critic" "05-implementer implementer" "06-code-reviewer reviewer"; do set -- $p; printf '%s-diff=%s ' "$2" "$(diff docs/prompts/$1.md factory/prompts/$2.md | grep -c '^[<>]')"; done; echo`
- THEN it prints five `verbatim` lines, then `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2` (a trailing space is allowed)

### Requirement: design-records-follow-the-change
The changelog SHALL have an entry naming `docs/coding.md`. The design doc and the build spec
SHALL say how `{coding standard}` is filled. `README.md`'s files table SHALL list
`docs/coding.md`.

#### Scenario: records-name-the-coding-standard
- WHEN (bash, from `~/dev/spec-factory`) `echo "changelog=$(grep -E '^[0-9]+\. ' docs/changelog.md | grep -c 'docs/coding.md') design=$(grep -c '{coding standard}' docs/design.md) buildspec=$(grep -c '{coding standard}' dev/build-harness.spec.md) row=$(grep -c '^| .docs/coding.md. |' README.md)"`
- THEN it prints `changelog=1 design=3 buildspec=1 row=1`

### Requirement: harness-gates-still-pass
The instance's gate commands MUST pass on the change.

#### Scenario: gates-pass
- WHEN (bash, from `~/dev/spec-factory`) `git diff --check main...HEAD; echo "check=$?"; uv run --frozen pytest -q -p no:cacheprovider tests/factory`
- THEN it prints `check=0`, and pytest ends with `N passed` and no failures or errors

=== verification.md
## Acceptance

- coding-page-has-five-checkable-rules → NEW. Today it prints `missing`, because
  `docs/coding.md` does not exist.
- coding-page-has-every-requested-phrase → NEW. Today it prints thirteen `missing: …` lines and
  `found=0 of 13`, because the file does not exist.
- tag-table-severities → NEW. Today it prints `reuse= stdlib= native= yagni= delete=`: there is no
  tag table to read.
- pointer-line-in-every-copy → NEW. Today the first six lines end `:0`, because no prompt names a
  coding standard. The last three end `:1`, because check 7 still says "Maintainability, only
  where".
- implementer-and-reviewer-prompts-name-the-page → NEW. Today it prints `implementer
  standard=[] unfilled=0`, `reviewer standard=[] unfilled=0` and `file=absent`.
  - Both runs do start; the failure is the missing path and file, not the setup.
  - `unfilled=0` today is not a pass: there is no placeholder yet.
  - A wrong fix fails here. One that adds the placeholder without the harness fill (part C)
    prints `standard=[] unfilled=1`. One that fills the path from somewhere other than the
    running checkout prints a different path.
  - It uses a throwaway store, so the harness lock does not apply.
- cut-rule-and-probe-in-every-copy → NEW. Today all six lines end `:0`.
- marker-ledger-named-in-design-and-build-spec → NEW. Today it prints `design=0 retro=0
  buildspec=0 row=0`.
- changed-blocks-verbatim-and-harness-copies-in-step → REGRESSION. Today it prints the five
  `verbatim` lines and `spec_writer-diff=6 critic-diff=2 implementer-diff=5 reviewer-diff=2`. It
  must print the same after the change. That means every changed block is re-copied to
  `docs/prompts/`, and each `factory/prompts/` copy takes the same edit and still differs only in
  the placeholders it fills (`{400}`, `{2}`, `{gate commands}`, `{force-push allowed}`).
- records-name-the-coding-standard → NEW. Today it prints `changelog=0 design=0 buildspec=0
  row=0`.
- gates-pass → REGRESSION. Today it prints `check=0` and `126 passed`. After the change the count
  rises by the new test file's tests.

How verified:
- Base: I ran every WHEN above verbatim in `~/dev/spec-factory` at `b33e593` and copied the
  "today" results above from that output.
- After-state: I made the change in a scratch clone of the same commit. The edits were `docs/coding.md`
  as in part A and parts B–F, without the new test file. I ran every WHEN there, and each printed
  the THEN given above:
  - `rules=1,2,3,4,5 check=5 principle=5 before=5 after=5 precedence=first`;
  - `found=13 of 13`;
  - the five severities;
  - `:1` ×6 then `:0` ×3;
  - both runs naming `<clone>/docs/coding.md` with `unfilled=0`, and `file=present`;
  - `:1` ×6;
  - `design=2 retro=1 buildspec=2 row=1`;
  - five `verbatim` lines and unchanged diff counts;
  - `changelog=1 design=3 buildspec=1 row=1`;
  - `check=0`, and the suite at `126 passed`.
- The clone was outside the repository. Nothing in `~/dev/spec-factory` changed except this output
  file.

Not an acceptance item: whether a live reviewer actually tags its findings, or whether an
implementer actually guards a shared function. Both need model runs on the upgraded runtime. The
operator judges them (Operator step 2).

Out-of-scope observations:
- The `agents/` templates have drifted further from `factory/prompts/`. They lack the critic's
  rubric 2 and 6 text, and the spec writer's Problem-section and acceptance-item rules. This
  change adds two more differences: the spec writer's cut rule and the critic's probe. The fix noted after the writing
  standard still applies: regenerate the templates from `factory/prompts/`, or make each one a
  pointer only.
- `dev/build-harness.spec.md:158` describes `factory render` and `render --check` as if built.
  This harness has no `render` command (`factory/cli.py` registers none), and the README lists it
  under "Not built".
- `ensure_gitignore` in `factory/store.py` repeats `write_text` (rule 1's example). It is a
  one-line cleanup for its own ticket.
- Changelog entry 43 still says the writing standard "holds eight rules"; it has twelve since rules
  9–12 merged.
