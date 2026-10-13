## Problem

The operator has no single written copy of their own standards for specs, design pages, reports
and records. The rules sit in four places: `docs/writing.md` (the twelve writing rules), the
spec-writer prompt (the spec format), a target repository's `AGENTS.md` (report style), and
corrections the operator gave in conversation, which survive only in one session's memory notes.
The operator has written them up as one document and wants it in this repo, as a file that still
makes sense when copied out of it.

The document must not change what any role writes. A role is one of the factory's agents
(triage, spec writer, implementer and so on), each run from a fixed prompt. Every role's prompt
already points at `docs/writing.md`, so editing that file would be a prompt change. Prompt changes
wait until a fixed set of replayed tickets (the golden set) has a baseline to measure them
against. So the standards go in a new file, `docs/standards.md`, that no prompt names.

Two small fixes ride along. This repo is public, and `docs/north-star.md` (the operator's statement
of what the factory is for) names the private port's product; it should say "a port of the
Nanobot chat bot" instead. And README, the repo's current-state page, has a line budget of 1,110
lines that another queued ticket may use up, so the pointer to the new file must not add a line.

## Evidence

- `ls docs/` lists `changelog.md coding.md decided-against.md design.md golden.md north-star.md
  principles.md prompts writing.md`. There is no `docs/standards.md`.
- `factory/instance.py:170-175`, `fill_standards`, fills the `{writing standard}` placeholder in
  the preamble and every role prompt with the path of `docs/writing.md`. That is why an edit to
  `docs/writing.md` is a prompt change and a new file is not.
- `grep -n 'today, the ' docs/north-star.md` prints line 21, the sentence "The factory serves its
  own development (spec-factory) and its targets (today, the …)", which ends with the private
  port's product name and version. This spec does not quote it, per the standing T-0053 decision
  (no new file, spec or role output names the private port's product).
- `wc -l README.md` prints `1106`. The current-truth requirement "README stays within its line
  budget" caps it at 1,110. T-0052's approved spec (`openspec/changes/T-0052/design.md`, item 3)
  allows README up to four more lines, which would leave none.
- The appendix text was taken from `.factory/store/requests/T-0053.md` lines 29-174 and checked
  equal to the ticket input's appendix with `diff` (no output). It has no tab and no trailing
  space. Everything after its title line hashes to
  `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`
  (`sed 1d | LC_ALL=C shasum -a 256`). Without `LC_ALL=C`, `shasum` aborts under this shell's
  `LANG=C.UTF-8`, so the scenario sets it.
- A prototype of Parts A to D in this run's scratch directory gave README 1,106 lines and printed
  each NEW scenario's expected output below.

## Root cause

Not a defect. The standards were never collected; `docs/north-star.md:21` was written before the
operator ruled that this public repo names no private product.

## Out of scope

- `docs/writing.md`, every `docs/prompts/` file, every role prompt, `agents/**` and `factory/**`
  stay unchanged. Pointing a prompt at `docs/standards.md` is a later prompt change.
- The appendix wording, including where its section 2 differs slightly from `docs/writing.md`'s
  rule headings (for example rule 4, "stating" for "that states"). The operator's text is exact.
- Other public mentions of the private product (see Out-of-scope observations at the end).

## Open questions

none

## Decisions

- The README pointer replaces the `docs/writing.md` row of "Where things live" with one row naming
  both files, so README does not grow. Rejected: a new row, which fits today (1,107 lines) but not
  once T-0052 uses its four lines. Rejected: asking the operator to raise the 1,110 budget, which
  a zero-growth row makes unnecessary.
- The title line stays `# Writing and design standards`, as in the appendix.
- The new requirement fixes the text after the title by its SHA-256. A later edit to
  `docs/standards.md` modifies that requirement in its own spec, where the operator approves the
  new text. Rejected: checking only that the file exists, which would not hold the operator's
  "exactly the text".
- Standing: no role prompt, `docs/writing.md`, `agents/` or `factory/` file names
  `docs/standards.md` until a spec that changes prompts says so. Its requirement is the record.
- The north-star sentence uses the operator's example wording verbatim.
- The changelog entry takes the next free number, whichever of T-0052, #109 or this ticket merges
  first.

## Risk

Documentation only: four files, no code, no prompt. The one shared-line risk is with T-0052 and
#109, which also append to `docs/changelog.md` and edit README; the next-free-number rule and the
zero-growth row absorb either order. #109 is open and not yet in `dev/issues.md`.
Protected paths: none

