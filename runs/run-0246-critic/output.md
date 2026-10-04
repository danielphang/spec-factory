## Spec critic review: T-0026 workflow view, round 1

Spot checks (all run from `~/dev/spec-factory` on `main` at `0b1abad`, under a throwaway HOME, fixtures under this run's scratch directory via `TMPDIR`):

- Cited paths and lines: `factory/workflows/intake.js` lines 54, 72, 91, 97, 112, 113, 117, 126, 128, 166 and `factory/workflows/build.js` lines 45, 63, 82, 88, 111, 112, 116, 126-128, 172, 176, 198, 200, 232, 240, 243, 260 all hold what the spec says they hold (clerk label `clerk: ${label}`, role labels, every `log()` call, the two `ticket show --json` calls that keep only `state`). `factory/cli.py:88` returns `"title"` in `ticket show --json`. `tests/factory/test_shepherd.py:9-11` says the workflow script cannot run under pytest. `tests/factory/fixtures/stubs/accept-approve` exists. `grep -c '^issue:'` over the 28 request files found none.
- Acceptance: I ran the GIVEN block and all eight NEW scenarios plus the REGRESSION scenario on this checkout. Every NEW scenario printed exactly the "fails today" text verification.md states (`triage run-0009-x: ACCEPT`; `roles=0 clerk=0 untitled=18`; `start=0 roles=0 sub_clerk=0 parent_clerk=0 untitled=31`; `transitions=0 bare=4`; `changes=0 bare=6`; and so on). The REGRESSION scenario printed the five checksums as written (`intake 1072986007 1493` … `build 3636463416 2810`).
- Short-title rule: I applied the Decisions rule as design.md A states it (`lastIndexOf(' ', 60)`, strip `[\s,;:·—-]+`, append `…`) to the five fixture titles. It produces the exact strings the THEN clauses expect, including the dropped trailing comma in "park reasons…".
- Counts: the expected `clerk=13 untitled=2` (intake) and `sub_clerk=19 parent_clerk=6 untitled=3` (build) agree with a hand count of the clerk calls on each path given design.md C's rule for which calls stay bare.

The scenarios would fail against a stub or a wrong fix: they pin exact label text, exact narrator lines, the order of the start line, per-ticket attribution on the build path, and byte-identical commands. The spec makes no hidden product choice: the GitHub-issue cut and the uniform clerk label are stated under Decisions with the alternative rejected. The protected path is declared under Risk and matches the request. Nothing conflicts with the open-ticket decisions in the log.

### Findings

[BLOCKING] 6 proposal.md, Evidence first paragraph; Decisions last bullet; Operator steps step 1
Problem: Two terms specific to this system reach the operator unglossed in a first paragraph: "current-truth `build-dispatch` scenarios" (Evidence) and "stub mode" / "stub-mode run" (Decisions and Operator steps), and no human-facing section glosses either earlier.
Evidence: Read Problem, Evidence, Open questions, Decisions and Operator steps as the gate reader; "current truth" and "stub" appear nowhere in Problem. The rubric names this case as blocking even when a careful reader could work it out.
Suggested fix: In Evidence write "the acceptance scenarios already in force for the build script, which drive it the same way" in place of the bare term, and at the first "stub mode" (Decisions) add "a run in which each role returns a fixture file instead of calling a model".

[SHOULD-FIX] 6 proposal.md, Operator steps step 1
Problem: The step says "run the intake workflow in stub mode on a throwaway store" but gives no way to do it; README's "Running one ticket" shows the Workflow call with `{ticket, repo, instance}` only, and `stubs` does not appear anywhere in README.md.
Evidence: `grep -n stubs README.md` prints nothing; the arg is documented only in the comment at `factory/workflows/intake.js:16`.
Suggested fix: Give the call form, e.g. "call the Workflow tool with the intake script and args `{ticket, repo: <runtime>, instance: <.factory>, state: <throwaway store>, stubs: tests/factory/fixtures/stubs/accept-approve, inlineRoles: true}`".

[SHOULD-FIX] 4 design.md, part E against part D
Problem: E says "Add no `await`", but D requires `transition()` to await the clerk reply before printing, so the two parts contradict each other as written.
Evidence: `transition()` today returns the clerk promise without awaiting (intake.js:119, build.js:118); D's print-on-`res.ok` needs that await, which changes no command order.
Suggested fix: Reword E to "Add no new clerk call, branch or reordering of calls, so the command order stays the same".

[NIT] 1 proposal.md, Decisions second bullet
Problem: "the last space at or before character 60" reads as 1-based (index 59), while design.md A and the expected THEN strings use index 60 (the 61st character).
Evidence: The "Isolate the store…" fixture cuts to 60 characters plus `…`; with a 1-based reading of "character 60" the rule would still land on the same space here, but it would not in general.
Suggested fix: Write "at or before the 61st character (index 60)" or restate the rule as "the first 60 characters, then back to the last space".

### Out-of-scope observations

- The "Only the two workflow scripts change" scenario passes trivially on `main`; the spec says so. It is a fence for the PR, not evidence of the change, and that is acceptable here.
- Operator step 2 (mobile-app narrator lines) cannot be checked from a shell; its placement under Operator steps is right.

STATUS: REVISE
CONFIDENCE: high, every cited line, every "fails today" output and the five REGRESSION checksums reproduced on this checkout; the one blocking item is a gloss, not a design defect
ESCALATIONS: none
