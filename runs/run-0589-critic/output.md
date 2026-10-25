# Critic review: T-0059 v2 (#120), `factory truth check` and the gate's replay of current truth

The technical content holds up. Every cited path and line I checked exists and says what the spec says. The five restated requirements differ from current truth only where the spec says they do. "Tests to change: none" is right. The one BLOCKING finding is about the operator-facing text, and it is a small rewrite.

What I checked:
- Paths and symbols: `factory/cli.py:183-185`, `:237`, `:252`, `READ_ONLY` and the two `("init", "paths", "stats")` tuples at `:863-875`; `factory/compose.py:92-99` (`gate_commands`, which fills `{integration}` from the checkout that has `main`) and `:354`; `factory/specstore.py:76`, `:102`, `:121`, `:223`, `:385`, `:398`; `factory/drive.py:214`; `factory/instance.py:41` (`caller_cwd`); `bin/factory` (runs the package from its own checkout and hands over the caller's directory); `.factory/instance.yaml:22-24`. `factory/cli.py` is 899 lines, README 1,212, current truth 316 scenarios in 15 capabilities. All as cited.
- Document anchors: README "Accepting a harness revision" (line 601, sentence at 617), "Where a human decides" (900, read-only list at 906, before the section's first fence), "Counting what each role catches and costs" (957), "What is built and what is not" (1023), Built entries in `- **Name.**` form (1025); `docs/design.md` paragraphs at 64, 68 and 98. All exist.
- Current-truth scenarios the edits touch: harness-docs' "The documents record factory stats" greps only `` `paths` and `stats` `` in README and the design doc, so inserting `truth check` before `paths` keeps it passing. Its "README says which commands refuse the flag" scenario counts sentences containing init, paths, stats, `--accept-harness` and "refuse", so one longer sentence keeps the count at 1. gate-commands' suite-entry sed matches only a line that starts `  - "uv run` and ends `tests/factory"`, so the new last entry does not match it. The spec's claims about all three are right.
- Restated requirements: I extracted each of the five from current truth and from the delta and diffed them. The only differences are the dropped `--model opus` (role-escalations fixture), the dropped `--model m` (harness-code "Spec pinning"), `truth check` in the two live-store-guard lists, and 900 to 910 plus the `factory/truth.py` clause in harness-code. Scenario counts match (1, 6, 6, 4, 2).
- Tests: no test pins `READ_ONLY`, the lock-exempt tuples, this repo's `.factory/instance.yaml` or the README text. `tests/factory/test_small_defects.py:98-99` and `:121` parametrize `init`, `paths` and `stats` by name, and `tests/factory/test_stats.py:419-425` tests `stats` alone; none breaks.
- Unarchived changes: T-0026 and T-0030 are closed, so the fold rule leaves them out. T-0057 (planned, T-0057.1 ready for its implementer) has ADDED-only deltas, none in harness-code, role-escalations or live-store-guard. Its `spec add` check fires only on a store with an `openspec/` tree, and the t0046 fixture's store has none, so the restated harness-code scenarios hold in either merge order.
- Acceptance commands run as written from `~/dev/spec-factory` at `11080b1`, through the running-code wrapper: the gate-entry sed prints the suite line; the documents grep prints `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0`. Both match the Acceptance section's "today" text.
- I also ran current truth's "Spec pinning and planner-run refusals keep their text" (harness-code) today: it prints 2 of its 4 lines and stderr says `model m refused for triage: the instance names opus`. See the second finding.

## Findings

[BLOCKING] 6 proposal.md, Problem (first paragraph) and Evidence (first paragraph)
Problem: The Problem's first paragraph is a glossary of current truth and scenarios; what is wrong (a change can break an earlier ticket's scenario and still merge) arrives in paragraph two, and who has the problem (the operator, who relies on current truth being true) in paragraph three; the Evidence's first paragraph says "as design part A describes", a section letter nothing has glossed.
Evidence: Read as the operator at the gate against docs/writing.md rule 1 ("a reader who stops after the first paragraph can say what the problem is and who has it") and the rubric's rule on section letters.
Suggested fix: Open the Problem with one sentence that says a merged change can silently break a scenario an earlier ticket wrote and that the operator, who relies on current truth, has no way to see it, then keep the glossary; in Evidence replace "design part A" with "the replay module, part A of the Proposed change below" or just "the exact-print rule under Decisions".

[SHOULD-FIX] 2 verification.md, Acceptance, "Spec pinning and planner-run refusals keep their text"
Problem: The item is labelled REGRESSION, "It passes today and after", but it fails today for the reason the spec's own Evidence gives.
Evidence: Run from `~/dev/spec-factory` at `11080b1` with the fixture block written first: stdout has 2 lines, not 4 (`spec not pinned` and `no recorded planner run found`), and stderr ends `model m refused for triage: the instance names opus`. The role-escalations declared-path scenario asks only implementer and verifier prompts, so its label is fine.
Suggested fix: Label it as failing today because `run start --role triage --model m` is refused, and passing after the restated setup drops `--model`.

[SHOULD-FIX] 4 proposal.md, Risk (first bullet) and Decisions (last bullet)
Problem: The gate's extra wall time (121 s to 157 s) was measured before the new gate-commands scenario joins current truth, and that scenario replays four capabilities inside every later gate's replay, which the measurement does not include.
Evidence: Decisions says the four-capability scenario avoids replaying itself but gives no time for it; those four hold the run-start fixtures (role-escalations), a real `factory drive` (harness-code) and the node end-to-end runs (live-store-guard), which are among the slower capabilities. The outer replay's wall time is the slowest capability's, and gate-commands' thread now holds a nested run of four.
Suggested fix: Measure the four-capability run once (as `bin/factory truth check --store .factory/store --capability ...` from `main`) and add the figure to Risk, or bound it there, so the operator sees the gate's full cost.

[SHOULD-FIX] 6 proposal.md, Operator steps, step 1
Problem: It tells the operator to run the command "through the running-code wrapper", which is an instruction given to agent runs, not something the operator has or has seen.
Evidence: The wrapper is defined in each role's input ("Running code"); README does not define it.
Suggested fix: Say "with `HOME` pointed at a throwaway directory" or drop the clause; the command itself is fine.

[NIT] 6 proposal.md, Problem (fourth paragraph)
Problem: "sub-ticket" is used without a gloss.
Evidence: First use in the human-facing sections.
Suggested fix: "its first sub-ticket (one of the pieces a ticket is built in) merged".

[NIT] 6 design.md, part A, Folding
Problem: Two cases an implementer meets in this spec's own scenarios are left implicit: a store with no `openspec/changes` or `tickets` directory (the "Capabilities run at the same time" scenario's store has neither), and a delta part for a capability current truth lacks (this change's own `truth-check`, folded on the ticket's checkout).
Evidence: `specstore.apply_delta` at `factory/specstore.py:386-387` starts a missing capability from `# <cap>\n\n## Requirements\n`, and `applies` at `:227` treats a missing file as empty, so following the cited functions gives the right answer, but the text does not say so.
Suggested fix: Add one sentence: a missing `openspec/changes` or `tickets` folds nothing, and a capability current truth lacks starts from empty text, as `apply_delta` does.

[NIT] 5 proposal.md, Decisions, the `cli.py` limit
Problem: 910 leaves about one line of slack for T-0057, whose approved design A adds an import and a guarded call to `spec_add` in `cli.py`.
Evidence: `cli.py` is 899 lines; this change adds a parser call, a `READ_ONLY` entry, an import and a return change, about five to eight lines; T-0057's part A adds about three to five.
Suggested fix: State the expected `cli.py` line count after this change, or set the limit with explicit room for T-0057's lines.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high; every cited path, anchor and restated requirement was checked against the repo and current truth, and the one BLOCKING item is text the writer can fix in one pass.
ESCALATIONS: none
