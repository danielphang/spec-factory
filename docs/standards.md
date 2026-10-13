# Writing and design standards

What this is: every standing instruction for how specs, design pages, reports and records are
written across the spec factory and the repositories it builds, collected into one file so the
standards can be recreated without the repos, the harness or any one session's memory. Who it is for:
the operator, and any agent asked to write for the operator.

Sources, in order of authority: `docs/writing.md` (the twelve rules), the factory's
spec-writer prompt (the reader and the spec format), each target repository's `.factory/context.md`
(that repo's reader), the target repository's `AGENTS.md` (report style), and the operator's own
corrections given in conversation 2026-09-16 to 2026-09-29, which until now lived only in a
session's memory notes. Where a rule's origin matters it is dated.

## 1. The reader

Deeply technical: knows databases, tables, locks, RPCs, agents and context windows. New to this
system: has not read its design document and does not know its function, command, file or state
names, or why a particular line of code exists. A reader who stops after the first paragraph can
say what is wrong and for whom.

A target repository's `.factory/context.md` can narrow the reader: for example, the operator, who
knows that codebase well but not the pipeline's vocabulary. Gloss harness terms (pinned, parked, parent-close, archive,
exit codes) on first use. File-and-function detail goes under Evidence and Root cause, never in
the Problem section.

## 2. The twelve rules (from `docs/writing.md`)

Each rule has a check you can run on your own text before handing it in.

| # | Rule | Check |
|---|---|---|
| 1 | The first paragraph says what is wrong, or what this is, and for whom. | Stop after paragraph one; can you name the problem and who has it? |
| 2 | A term specific to this system is glossed at first use with what it does or why it exists. General technical concepts are not glossed. | Underline every made-up name; its first use says what it does. |
| 3 | One idea per sentence; no parenthetical holds a second idea. | Delete each parenthetical; if a claim is lost, it needs its own sentence. |
| 4 | A diagram comes after the words needed to read it, with a caption stating its one claim. | Every box and arrow is named in the text above it. |
| 5 | A command is shown with what its output shows. | Every quoted output is followed by what it means for the claim. |
| 6 | Project-internal references are introduced, or moved to a closing note. | Each ticket id, issue number, decision id, session or person is introduced by what it is, or sits in a closing note. |
| 7 | Lead with the problem; the mechanism comes second. | First sentence: what is broken or what the reader must do. |
| 8 | State a choice and the alternative rejected; do not write an essay defending it. | One sentence for the choice, one per rejected alternative and why. |
| 9 | One name per concept: no synonyms, no name shared by two concepts. | Each term keeps the name it got at first use. |
| 10 | One mode per section: explanation, how-to and reference do not share a heading. | Label each section; a section with two labels is split. |
| 11 | A heading states what is under it. | Read only the headings; each predicts its section. |
| 12 | Parallel facts go in a table. | Three or more items with the same kinds of fact become rows, one column per kind. |

Two worked examples, kept because they are the ones most often violated:

- Rule 2, before: `--accept-harness` appeared in a diagram with no statement of what requires it.
  After: "Each target repository runs only the harness commit it has accepted, recorded in its
  `harness.lock`. When the harness is upgraded, the operator accepts the new commit with
  `--accept-harness <commit>`; until then the harness refuses to run there."
- Rule 7, before: "Stale branch base, which is a harness/process issue. The verifier was given base
  `20849b6`, but the head forks at `cdb1c67`…" After: "The test gate cannot pass on this branch: it
  was cut from `main` before the change it depends on merged. Decide: update the branch and
  re-verify, or accept the trial-merge evidence."

## 3. Operator corrections given in conversation

These are rules the operator stated directly. They apply to replies, specs, pages, commit messages,
ledgers and comments alike.

| Date | Rule | The operator's words, and why |
|---|---|---|
| 2026-09-16 | Direct and compact. Lead with the answer. Facts as short declaratives or a table. Keep the caveat, tradeoff or number that changes a decision; drop wrapping and narration. | "make your response style more direct, less mannered prose, less verbose but not dropping nuance." |
| 2026-09-17 | The same for everything written. State the fact and its source (command, SHA, file:line); reasoning goes in the commit message once; a code comment states the invariant, not the history. | "[a spec] at 561 lines is crazy work … an entire essay for PATH composition is a place we should not be." Everything written is read back many times into large contexts; a verbose doc is paid for at reads × later calls. |
| 2026-09-17 | Length budgets: a spec's normative half ≤150 lines; a profile ≤100; a cold-read record ≤60; a notes cell ≤3 sentences; a Done entry is the fixed fields, one line each. Do not rewrite closed specs for style; trim when opened for another reason. | The budgets were in an earlier maintenance-workflow document that no longer has them, so this table is now their record. |
| 2026-09-24 | Every decision id or obligation id carries a short parenthetical reminder of what it decides, on every mention. | "A bare id makes the message unreadable without the register open." |
| 2026-09-24 | Scope one unit per message: one spec, one ticket, one section. No batch-wide sweeps. | |
| 2026-09-29 | Report findings as what they mean first, mechanism second. A decision row that carries a recommendation is taken by default, recorded and reported; ask only when there is no lean or the choice is irreversible. Never re-ask after a go. | |
| ongoing | Pressure-test a proposal before presenting it: the root why, the failure modes, and an independent counter-proposal. State a concern in a sentence or two, then deliver. | |

The trap that catches a writer: copying the shape of the neighbouring record. Older entries were
written before the budgets and are long; patterning a new one on them breaks the rule even when the
rule was read the same session. Write to the rule, not to the file's median entry.

## 4. Reports and records (from the target repo's `AGENTS.md`)

- A report leads with what changed for the operator and what it cost; paths and mechanisms go
  below.
- Before any message that claims done or verified, ground it: state from commands, every quoted
  identifier read back, every figure from the command that produced it. Before saying a check
  passed, prove it ran on the claimed tree in a fresh environment.
- Ledgers and command logs are written for the cold reader: explicit why, not just what.
- No ledgers where the store is the record: the factory's store log replaces TASKS.md and Done
  entries.

## 5. The spec format (from the spec-writer prompt)

A spec is a change folder: `proposal.md`, `design.md`, `specs/<capability>/spec.md`, `tasks.md`.

| Section | Contents |
|---|---|
| Problem | What is wrong or missing, for whom, in plain words for the operator at the spec gate; each term of art glossed on first use; detail goes below. |
| Evidence | Actual output, logs, metrics, repro steps; each quoted output followed by what it means. |
| Root cause | Files and functions if known; "unknown" is allowed. |
| Out of scope | What must not change. |
| Open questions | none, or a list. |
| Decisions | none, or one line per design call, including each answered open question, with the alternative rejected. |
| Risk | Blast radius; protected paths declared on one line the merge gate reads. |
| Operator steps | Optional: actions on live or protected state only the operator can perform, after merge. |
| Proposed change (design) | Lettered parts A, B, C, specific enough to follow. |
| Tests to change | none, or the existing tests the change breaks, and why. |
| ADDED / MODIFIED / REMOVED Requirements | The delta on the capability spec, one part per capability changed; reuse a current-truth capability where the behaviour already lives. |

Anti-Goodharting: the critic scores against a rubric; satisfy each item's intent, not its wording.
A spec padded with generic criteria to look thorough is a failed spec. On revision, answer each
critic finding with FIXED and what changed.

## 6. Design pages and reports delivered as pages

Used for two earlier pages, a feature design and a cleanup report. These conventions were applied
but never written down before this file.

- **Open with what changes for the reader and what it cost.** First paragraph: the outcome in the
  reader's terms, the date, and what was not lost. A one-line meta row under it: where it was
  applied, how it was rehearsed and reviewed, how it is reverted.
- **Figures block next.** Three or four numbers that justify the page, each with a one-line label;
  a "live check" line under them quoting the command or log line that proves the headline number.
- **"One step left for you" callout** when the page asks the operator to do something: the exact
  edit, the exact command, and why the writer could not do it (for example, a safety check
  blocked the edit).
- **What changed, as numbered steps**, each with its commit id as a tag, each step revertible on
  its own.
- **What the review caught**: a short register of findings an independent critic raised before the
  change went live, each with its category and what was done.
- **Not done, and why**: deferred items with their reason, stale content left in place, and the
  decisions still open, each named by its id and a reminder of what it decides.
- **Decision register** for a design page: one row per decision, id, the question, the
  recommendation, the alternative rejected; a decision with a recommendation is taken by default.
- **How to undo**: the exact commands, the tag or backup that marks the state before, and whether
  a restart is needed.
- **A full table at the end** for anything with many rows (every skill, every job), with filters
  and a search box, and a key paragraph defining each category used in the table.
- **Privacy**: no chat contents, phone numbers, messaging-platform user ids or private people's
  names on a page, in a spec, a test, a commit or a public post. Neutral roles ("the requester",
  "a group member") where a role is needed. Nothing public references a private repository.
- Pages follow the twelve rules above; a page is not a place to escape them.

## 7. Comments, issues and messages to peers

- A comment answering a question on a page answers the question in the first sentence, then
  grounds it (file, command, log line), then says what was changed because of it, if anything.
- An issue filed from an agent's run record states: asked, did (with evidence), should have, impact,
  and an optional one-line possible fix marked as a guess. Primary evidence only; a summary stream
  is never a citation.
- A message to a peer session leads with the one fact the peer must act on, then the identifiers
  (commit, run id, ticket), then what was not done.
