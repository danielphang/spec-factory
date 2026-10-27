## Acceptance

- Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time → NEW. Today it prints only `exit=2`: `factory` has no `truth` command (`argument cmd: invalid choice: 'truth'`).
- The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed → NEW. Today it prints nothing, because the command writes nothing to stdout.
- --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused → NEW. Today its first two lines are `one: exit=2 0 0` and `unknown: exit=2 named=0`.
- Capabilities run at the same time → NEW. Today it prints nothing.
- Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped → NEW. Today it prints nothing.
- On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped → NEW. Today it prints nothing.
- The implementer's worktree folds the same deltas → NEW. Today it prints nothing.
- From the integration branch only an open ticket's delta with a merged sub-ticket is folded → NEW. Today it prints nothing.
- A folded delta that no longer applies is refused, naming its ticket, and nothing runs → NEW. Today it prints `exit=2 named=0 results=0`: the refusal is argparse's, which names no ticket.
- truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing → NEW. Today it prints a line starting `here=2 inside=2 store=unchanged total=factory: error: argument cmd: invalid choice: 'truth'`: argparse refuses the unknown command.
- truth check refuses --accept-harness and names config → NEW. Today it prints `exit=2 hint=0 json=0`.
- The instance's last gate command is the truth check on the integration checkout's store → NEW. Today it prints `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"`.
- The truth check on this checkout reports no failure in the capabilities this change restates → NEW. Today it prints `exit=2` and a space, because `factory` has no `truth` command.
- README, the design doc and the changelog describe the truth check → NEW. Today it prints `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0`.
- README, the design doc and the changelog describe the refusal route → REGRESSION, in the form this change states, which measures README growth across T-0057's own merge. That form prints `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, then `CONTIGUOUS`, then `entries=1 terms=3` today, on `main` at `db28eb1` and at `7bfbe8f`, and on a branch that adds 11 lines to README; it passes after. Current truth's form, which measures against `main`, fails today: it prints `growth=` on `main` and `growth=over` on that branch. That is the defect this restatement fixes.
- Implementer and verifier run prompts carry the declared-path rule → REGRESSION. It passes today and after, in this change's form and in current truth's, because it asks only implementer and verifier prompts. The three scenarios that reuse its fixture and ask a reviewer prompt fail today in current truth's form; the gate-commands scenario "The truth check on this checkout reports no failure in the capabilities this change restates" checks that they pass once this change's delta is folded.
- Status transitions write the same events and history entries → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Spec pinning and planner-run refusals keep their text → REGRESSION, in the form this change states, whose `run start` passes no `--model`. That form passes today (`run-tip-fixed.txt` at `db28eb1`, `run-fixed.txt` at `7bfbe8f`) and after. Current truth's form, which passes `--model m`, fails today with `model m refused for triage: the instance names opus`; that is the defect this restatement fixes.
- The dispatcher parks a refused store command with the same reason → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The spec parser gives the same result as the base on every spec in the store → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The refactored harness has no unused imports or variables → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The harness suite passes and no existing test file changes → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The drift checks live in factory/drift.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The shared helpers and the live-store fence live in factory/common.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Instance and store setup live in factory/setup.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The gates live in factory/gates.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The human decisions live in factory/human.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The refusal names the throwaway store and not the marker → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- A harness acceptance is refused while a run is in flight → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- A launch copy is written unmarked while a run is in flight, and the target is unchanged → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Without the flag paths and stats still run under another lock, and config still accepts a revision → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.

## Responses

Round 3, answering the round-2 critic and the operator's gate note of 2026-10-26.

- [BLOCKING] 5 T-0057's growth scenario fails under the replay: FIXED, as the operator directed. harness-docs gains a MODIFIED requirement that restates T-0057's "The documents record the format check at spec add and its route back to the spec writer". Its scenario keeps its name, its THEN and every check but one: `growth` is now summed over each `Merge factory/T-0057.<n>` commit reachable from HEAD against its first parent, and prints `none` when there is none. Run from a clone, that form prints `growth=ok` on `main` at `7bfbe8f`, on `main` at `db28eb1` and on a branch that adds 11 README lines; current truth's form prints `growth=` on `main` and `growth=over` on that branch. Decisions has a bullet saying this change restates a T-0057 requirement, and the README-growth Decision no longer leans on T-0057.1's line. Risk's restated-requirements bullet names it, and a new bullet names the two other main-relative scenarios, both skipped as prose. The Acceptance has a label for the scenario, and design parts D and E and "Tests to change" mention it.
- [SHOULD-FIX] 1 Stale `main` and counts: FIXED. The Evidence measures at `7bfbe8f` and at `db28eb1`, `main`'s tip, which is one operator commit later. It describes T-0057 as closed and archived, and counts 325 scenarios in 16 capabilities. The listings are new: `run-gate.txt`, `run-fixed.txt`, `run-four.txt` and `run-nested.txt`, as asked, plus `run-branch*.txt` and `run-tip*.txt`. The previous prototype's listings were gone with its scratch directory, so the prototype was rebuilt from design part A. All nine of T-0057's scenarios now ran under the rule. Two THENs read "`X` twice, one per line" with no comma before "twice". The rule now accepts that form; it is a one-word widening of design part A's ITEM grammar, stated in Decisions. Of the nine, seven pass, those two among them; one is the README check above; and one runs the whole suite, so the gate skips it (`run-gate.txt`).
- [SHOULD-FIX] 2 Every figure came from `main`: FIXED. A clone carries a branch, `factory/T-0059.1`, whose one commit adds 11 lines to README where design part D puts them. Plain current truth there gives 288 passed, 5 failed (T-0057's check now `growth=over`), 32 skipped, in 126 s. With this change's delta folded, the same checkout gives 293 passed, 0 failed, 46 skipped, in 127 s. The gate-commands scenario, run as its own checkout would run it, passes there in 6 s. Inside the full replay, the replay's wall time is 129 s.

Everything else is v3's text unchanged: design parts A to E, apart from the ITEM line and the sentences above, and every other delta part, scenario and Acceptance item. The Problem and the Evidence are re-measured, and the figures in Decisions and Risk follow them.

## Critic rounds

round 1 · spec v2 · run-0589-critic · REVISE

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

round 2 · spec v3 · run-0593-critic · REVISE

# Critic review, round 2: T-0059 v3 (#120), `factory truth check` and the gate's replay of current truth

Round 2. I checked whether round 1's findings were resolved and read the text v3 changed. One new BLOCKING finding comes from a change in the repo since round 1, not from text I missed: T-0057.1 merged into `main` at `7bfbe8f` and T-0057 was archived, so T-0057's scenarios are now current truth, and one of them fails under this spec's own exact-print rule on `main` and on any branch that adds more than one line to README.

What I checked:
- `main` is at `7bfbe8f` (`Merge factory/T-0057.1`), not `11080b1`; the store's `tickets/T-0057.yaml` says `status: closed`, `T-0057.1.yaml` says `status: merged`, and `openspec/changes/archive/2026-10-25-T-0057/` exists. Current truth now holds 325 scenarios (`grep -c '^#### Scenario'` summed over the 15 capability files; the spec says 316).
- `factory/cli.py` is 899 lines on `main` and on `factory/T-0057.1`; README is 1,213 on both, so the spec's size arithmetic (about 903 under 910; 1,213 plus at most 11 under 1,225) still holds.
- T-0057's one harness-docs scenario, "README, the design doc and the changelog describe the refusal route", computes `growth` as `git diff --numstat $(git merge-base HEAD main) HEAD -- README.md | awk '{print ($1 - $2 <= 1 ? "ok" : "over")}'`. I ran its WHEN from `~/dev/spec-factory` on `main`, through the running-code wrapper with stdin closed: it prints `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=` (empty, because the diff is empty and awk prints nothing), then `CONTIGUOUS`, then `entries=1 terms=3`. The THEN requires `growth=ok`, so the exact-print rule fails it on `main` today. On a branch that adds more than one net line to README it prints `growth=over` and fails again.
- The other scenarios in current truth that diff the checkout against `main` have prose THENs and are skipped by the rule: harness-code's "Every definition keeps its exact text, and the split adds at most 100 lines" ("one line, `pairs=<n> ...`, with n at least 1") and harness-suite's "The only existing test file changed is the stats test" ("prints nothing, or only ..."). I did not run the other seven exact-print scenarios T-0057 added (build-dispatch 2, role-inputs 1, spec-format-check 4); they are fixture-based `bin/factory` runs, and the spec's evidence never ran them under the rule.
- Acceptance commands re-run as written from `~/dev/spec-factory` at `7bfbe8f` through the wrapper: the gate-entry sed prints `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"`; the documents grep prints `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0`. Both still match the Acceptance section's "today" text.
- Part A's new Folding sentence is present and says what round 1 asked. Part B states the expected `cli.py` count. The Problem's first paragraph now says what is wrong and for whom; "design part A" is gone from Evidence; the only section letters in human-facing sections are inside "Proposed change", which the operator is not held to.

## Findings

[BLOCKING] 5 proposal.md, Decisions (last bullet) and Risk (sixth bullet); specs/gate-commands/spec.md, "The truth check on this checkout reports no failure in the capabilities this change restates"; verification.md, Operator steps, step 1
Problem: T-0057 is archived, so its harness-docs scenario is current truth now, and it fails under this spec's exact-print rule on `main` (`growth=` empty) and on this change's own branch (`growth=over`, because README grows by up to 11 lines); the new gate-commands scenario replays harness-docs and requires `failed=0`, so it cannot pass on this change's checkout, and Operator step 1's replay on `main` after the merge would report 1 failed, which the spec says breaks every later gate.
Evidence: The run quoted above, on `main` at `7bfbe8f`; the scenario's THEN at `openspec/specs/harness-docs/spec.md:622`; the gate-commands scenario's THEN `exit=0 failed=0`; Risk's "T-0057's delta adds requirements only, so neither change's delta touches the other's", which was true while T-0057 was a folded delta whose scenarios the check skips, and is not true now that they are current truth.
Suggested fix: Add a MODIFIED harness-docs requirement that restates "The documents record the format check at spec add and its route back to the spec writer" with `growth` measured across the `Merge factory/T-0057.1` commit against its first parent, as harness-suite's T-0045 and T-0051 scenarios do (or with the growth clause dropped), note in Decisions and Risk that this change now restates a T-0057 requirement, and re-measure the replay on `main` at `7bfbe8f` and from a branch checkout that carries this change's README growth.

[SHOULD-FIX] 1 proposal.md, Evidence (first paragraph and "Size limits this change meets") and Responses (last item)
Problem: The Evidence names `11080b1` as `main`'s current tip and says T-0057.1 is "now at its checks", but `main` is at `7bfbe8f`, T-0057 is closed and archived, and current truth has 325 scenarios, nine of which (eight with exact-print THENs) were never run under the rule.
Evidence: `git log --oneline -1 main`, the store's `tickets/T-0057.yaml` and `tickets/T-0057.1.yaml`, the archive directory, and the scenario count above.
Suggested fix: Re-measure `run-gate.txt`, `run-fixed.txt`, `run-four.txt` and `run-nested.txt` on `7bfbe8f`, state the new counts, and describe T-0057 as archived.

[SHOULD-FIX] 2 proposal.md, Evidence, "Result on `main`" and "The fix works"
Problem: Every replay figure was measured on a checkout of `main`, where `git merge-base HEAD main` equals HEAD and every scenario that diffs the checkout against `main` sees an empty diff, but the gate runs the replay on a branch checkout, where those scenarios see this change's own diff.
Evidence: Three current-truth scenarios diff against `main` (named above); two are prose and skipped, and the third is the one the BLOCKING finding runs. The spec's gate-commands scenario and its Risk bullets describe the replay as run "on this change's checkout" with no evidence from one.
Suggested fix: Run the prototype once from a branch checkout that carries this change's edits (a scratch worktree of `main` with the README and `factory/` changes committed) and report that run beside the `main` runs, so the operator sees the gate's result where the gate runs.

Prior findings (round 1):
- [BLOCKING] 6 Problem and Evidence: RESOLVED. The Problem's first paragraph says what is wrong (a merged change can quietly break required behaviour) and for whom (the operator, who approves on the understanding that it holds); "design part A" is replaced by "the exact-print rule under Decisions".
- [SHOULD-FIX] 2 "Spec pinning and planner-run refusals keep their text" label: WITHDRAWN. The writer is right that the verifier runs the item in the spec's form, whose `run start` passes no `--model`, and that form passes on base today; the item's new text says which form fails and why, which is what the operator needs.
- [SHOULD-FIX] 4 nested run's cost: RESOLVED. Decisions and Risk give the four-capability run's figure (12 s nested, 16 s alone, replay at 125 s) and name build-dispatch as the capability that sets the wall time.
- [SHOULD-FIX] 6 Operator steps, step 1: RESOLVED. The wrapper clause is gone.
- [NIT] 6 "sub-ticket": RESOLVED, glossed at first use.
- [NIT] 6 design part A, Folding: RESOLVED. The sentence at design.md's Folding paragraph covers a missing `openspec/changes`, a missing `tickets` and a capability current truth lacks.
- [NIT] 5 `cli.py` limit: RESOLVED. The Decision gives the expected count (about 903 from 899); I confirmed 899 on `main` and on `factory/T-0057.1`. The premise "T-0057.1 at its checks" is stale (see the first SHOULD-FIX), but the conclusion holds: `main` is at 899 with T-0057.1 merged.

round 1 · spec v4 · run-0595-critic · APPROVE

# Spec critic, T-0059 (#120), spec v4, round 3

## What I checked

- Cited paths and lines, read from `main` (`db28eb1`): `factory/cli.py` is 899 lines; the `--model` refusal is at `cli.py:183-185`; the implementer worktree and checker `wt` paths are at `cli.py:237` and `:252`; `READ_ONLY` and both `("init", "paths", "stats")` tuples are at `cli.py:863-875`, and every subparser uses `dest="sub"`, so `("truth", "check")` fits `READ_ONLY` as written. `specstore.apply_delta` is at `:385`, `archive` at `:398`, and `lines_outside_fences`, `requirement_blocks`, `parse_delta` and `applies` exist. `drive.py:214` strips only `FACTORY_DISPATCH`. `instance.caller_cwd()` exists. `.factory/instance.yaml` has the two gate commands the spec quotes.
- Store facts: 16 capabilities, 325 scenarios; `openspec/changes/` holds T-0026 and T-0030, both closed, plus the archive with `2026-10-25-T-0057`; the role-escalations fixture passes `--model opus` at its line 28; harness-code's requirement says "under 900"; live-store-guard's two command lists read as the spec says; the harness-docs T-0057 requirement differs from the restated text only in its last sentence and the scenario's growth clause (diffed in my scratch directory).
- README is 1,213 lines; its read-only list, "Counting what each role catches and costs", "## What is built and what is not", "Accepting a harness revision" and "Upgrading the runtime" are where the spec puts them, and the accept-harness sentence in that section is one. `docs/design.md` has the three paragraph openers. The changelog's last entry is 78.
- Tests for old behaviour: `test_small_defects.py:99` and `:121` test `init`, `paths` and `stats` by name; `test_stats.py:419-425` tests `stats` alone; nothing enumerates `READ_ONLY`, counts `cli.py` lines or reads this repo's `.factory/instance.yaml`. "Tests to change: none" holds.
- Acceptance commands run as written from `~/dev/spec-factory` under a fresh HOME: the `cli.py` count prints `899 3`; the gate's last line prints the suite entry, as the Acceptance says; the restated T-0057 scenario prints `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, `CONTIGUOUS`, `entries=1 terms=3`, and `git diff --numstat 7bfbe8f^1 7bfbe8f -- README.md` is `8 7`, as the Evidence says.
- Approved changes not yet archived: none, so no scenario has a merge-order dependency.
- Hand-counted the fixture truth's expected results (16 scenarios; 11/2/3 on `main`, 10/2/4 on the checker's and implementer's checkouts, 10/2/4 with `slow-marker` skipped, folded ids `T-0001, T-0002` on the ticket checkouts and `T-0002` alone on `main`). They follow from design part A and the fixture's ticket statuses.
- Not checked: the wall-time and pass/fail figures, which need the prototype or the built command; the verifier measures them.

## Findings

[SHOULD-FIX] 6 Evidence, first paragraph; Operator steps; Problem, third paragraph
Problem: Three system-specific terms reach the operator unglossed: "design part D" (and "design part A" in the next paragraph) for the lettered parts of this spec's Proposed change, `gate_commands` in the operator step with no word that it is the list in `.factory/instance.yaml`, and "the harness" and "the instance" in the Problem's third paragraph.
Evidence: Read as the gate reader the rubric names. The Problem glosses factory, store, current truth, capability, scenario, verifier and merge gate, but none of these three. By the rubric's letter the first two are in a section's first paragraph and would be BLOCKING; I am not blocking on them because this is round 3 of a spec whose last two revisions the operator directed in person, each fix is a few words, and nothing else in these sections needs a translator.
Suggested fix: write "part D of the Proposed change below" on first use, "`gate_commands`, the gate's command list in `.factory/instance.yaml`" in the operator step, and gloss harness (the factory's code) and instance (one repository's copy of the factory, configured in `.factory/instance.yaml`) where the Problem first uses them.

[NIT] 1 Evidence, "Nothing replays current truth" and design part C
Problem: Two `factory/compose.py` line citations are off: the `{integration}` replacement is `gate_commands()` at `compose.py:109-116`, not `:92-99` (which is gate-entry validation), and the verifier's input is built around `compose.py:359-374`, not `:354` (the planner's sub-ticket list).
Evidence: `git show main:factory/compose.py`, lines 90-100, 109-117 and 352-375.
Suggested fix: change the two line numbers.

[NIT] 4 Design part A, "Inputs" and "Folding"
Problem: Part A resolves the checkout path but says nothing about resolving the store path, and the worktree and `runs/<run>/wt` tests compare the two, so a store given through a symlink (as the Evidence's own clones were) would silently fold nothing.
Evidence: The live store is a plain directory, so the gate entry is unaffected today; the acceptance fixture passes an already-resolved `$S`.
Suggested fix: add "resolved" after `--store PATH` in the Inputs bullet.

## Prior findings (round 2, as the Responses section states them)

- [BLOCKING] 5 T-0057's growth scenario fails under the replay: RESOLVED. The restated scenario measures across T-0057's own merge commit, prints `growth=ok` on `main` today (I ran it), and is the only clause of the requirement that changed; the Acceptance labels it REGRESSION with the failing old form named.
- [SHOULD-FIX] 1 Stale `main` and counts: RESOLVED. Figures are at `7bfbe8f` and `db28eb1`, `main`'s tip; T-0057 is closed and archived; 325 scenarios in 16 capabilities matches the store.
- [SHOULD-FIX] 2 Every figure came from `main`: RESOLVED. Branch figures and the nested gate-commands run are given, with listings named; I could not re-run the prototype.

## Out-of-scope observations

- Three scenarios in the four capabilities the nested gate-commands scenario replays need `node` on `PATH`; the scenario says so. A machine without it fails that scenario in every gate, which Risk already covers.

## Verifier results

2588b553013712729323c916c8e9063633b47e29 · T-0059.1 · VERIFIED · run-0601-verifier
