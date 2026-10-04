## Acceptance

- The intake run opens with the ticket, its short title and its state → NEW; today it prints `triage run-0009-x: ACCEPT`, because the first narrator line comes after triage and carries no title.
- A ticket with no title opens with its bare id and keeps bare-id labels → NEW; today it prints `label: triage T-0001`, then `log: triage run-0009-x: REJECT`, with no start line and no `→ closed` line.
- A long title is cut at a word boundary and loses its trailing comma → NEW; today it prints `triage run-0009-x: NEEDS-HUMAN`, then `T-0001 parked: NEEDS-HUMAN from triage`.
- A short title is shown whole → NEW; today it prints only `triage run-0009-x: REJECT`.
- Every intake row after the ticket is read carries its short title → NEW; today it prints `roles=0 clerk=0 untitled=18` (re-run this round on `0b1abad`).
- Build rows carry the sub-ticket's own title, and the parent's rows the parent's → NEW; today it prints `start=0 roles=0 sub_clerk=0 parent_clerk=0 untitled=31`.
- Each intake state change gets a narrator line → NEW; today it prints `transitions=0 bare=4`.
- Build state changes and the merge are narrated under the right ticket → NEW; today it prints `changes=0 bare=6` (re-run this round on `0b1abad`).
- The clerk commands are byte-identical on five paths → REGRESSION; prints the same five lines on this checkout (re-run this round on `0b1abad`) and must after the change.
- Only the two workflow scripts change → NEW; today it prints nothing, because `main...HEAD` is empty on `main`. On the PR it fences the change to the two scripts: no CLI, test, prompt or document change.

Not restated here: the acceptance scenarios already in force for these scripts (park reasons, checker selection, the dispatcher marker) keep applying unchanged. In round 1 I ran them against a prototype of this change, and they printed the same output as on this checkout.

## Responses

- [BLOCKING] 6, unglossed terms in Evidence, Decisions and Operator steps: FIXED. Evidence now says "the acceptance scenarios already in force for the build and intake scripts", and describes the stand-in clerk as one that "returns canned store replies instead of running commands". "The GIVEN block" became "the first block of the first acceptance scenario". Decisions glosses stub mode at its first use: "a run inside the Workflow tool in which each role agent copies a prepared fixture file as its output instead of calling a model". Operator steps glosses stub mode, the throwaway store and the runtime again, since a reader may start there. The Decisions bullet on state-change lines now glosses the transition helper and "park".
- [SHOULD-FIX] 6, Operator step 1 gave no way to run it: FIXED. The step now gives the store setup commands and the full Workflow call, with `scriptPath` and args `{ticket, repo, instance, state, stubs, inlineRoles: true}`, and the exact start line and row text to look for. I ran the setup commands on this checkout with a scratch `FACTORY_STATE`: `init` exited 0, `ticket new` printed `{"ok": true, "id": "T-0001", "title": "Demo", "state": "ready-for-triage"}`, and `git status --short` was unchanged. The `stubs` and `inlineRoles` args are those documented at `factory/workflows/intake.js:9-17`.
- [SHOULD-FIX] 4, part E contradicted part D on `await`: FIXED. E now reads "Add no new clerk call, branch or reordering of calls, so the command order stays the same". D adds why the await inside `transition()` changes no order: every caller already awaits it (intake.js:136-172 and build.js:143-269, all eleven call sites).
- [NIT] 1, "character 60" read as 1-based: FIXED. Decisions and the requirement sentence now say "the last space within its first 61 characters (index 60 or earlier), so at most 60 characters are kept". design.md A keeps `lastIndexOf(' ', 60)`, which is the same rule.

## Critic rounds

round 1 · spec v1 · run-0246-critic · REVISE

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

round 2 · spec v2 · run-0255-critic · APPROVE

## Spec critic review: T-0026 workflow view, round 2

Reviewed per the convergence rule: whether the four round-1 findings were resolved, and the text that changed between v1 and v2 (`diff .factory/state/specs/T-0026/v1.md v2.md`: Evidence paragraphs 1 and 6, Decisions bullets 2, 5 and 7, Operator steps, design.md D and E, the short-title requirement sentence, verification.md's three "re-run" notes and the new Responses section).

Spot checks (from `~/dev/spec-factory` on `main` at `0b1abad`, throwaway HOME, fixtures under this run's scratch directory via `TMPDIR`):

- Changed claims: `factory/workflows/intake.js:9-17` documents `stubs` and `inlineRoles` as the Responses say. Every `transition()` caller awaits it: `grep -n 'transition('` shows `await transition(` at intake.js 136, 137, 139, 157, 165, 172 and build.js 143, 174, 179, 183, 187, 215, 269, so design.md D's "every caller already awaits its result" holds. `transition()` itself returns the clerk promise unawaited (intake.js:117-120, build.js:116-119), so D's added await is the only change in that function.
- Acceptance re-run on this checkout: the REGRESSION scenario printed `intake 1072986007 1493`, `park 536447330 571`, `short 24042256 547`, `notitle 24042256 547`, `build 3636463416 2810`; the two count scenarios printed `roles=0 clerk=0 untitled=18` and `changes=0 bare=6`; the first-line scenario printed `triage run-0009-x: ACCEPT`. All match verification.md.
- Operator step 1: I ran the store-setup commands with `FACTORY_STATE` under my scratch directory. From the repo root and from a directory with no instance, `init` exited 0 writing only the throwaway store (`"agents": []`) and `ticket new` printed `{"ok": true, "id": "T-0001", "title": "Demo of the workflow view", "state": "ready-for-triage"}`; `git status --short` was unchanged. I then sent the commands the intake script sends first (`config`, `ticket show --json`, `run start --role triage`, `run compose`) through `~/dev/spec-factory-harness/bin/factory` against that store with `FACTORY_INSTANCE` set to `$RUNTIME/.factory` as the step says, and also to this repo's `.factory`; every one exited 0 with both. The step is runnable as written.

### Findings

[NIT] 1 verification.md, Responses, third bullet
Problem: "all eleven call sites" undercounts: `transition()` has six callers in intake.js and seven in build.js, thirteen in all.
Evidence: `grep -n 'transition(' factory/workflows/intake.js factory/workflows/build.js` (the definition line excluded) lists 13 awaited calls; the line ranges 136-172 and 143-269 are right.
Suggested fix: Write "all thirteen call sites", or drop the number.

### Prior findings (round 1)

- [BLOCKING] 6, unglossed "current-truth `build-dispatch` scenarios" and "stub mode": RESOLVED. Evidence paragraph 1 now says "the acceptance scenarios already in force for the build and intake scripts" and glosses the stand-in clerk; Decisions bullet 7 glosses stub mode at its first use; Operator steps glosses runtime, stub mode and throwaway store. Read Problem, Evidence, Open questions, Decisions and Operator steps again as the gate reader: no system-specific term reaches a first paragraph unglossed.
- [SHOULD-FIX] 6, Operator step 1 gave no way to run it: RESOLVED. The step gives the setup commands and the full Workflow call, and the expected start line and row text; I reproduced the setup and the first clerk commands (above).
- [SHOULD-FIX] 4, design.md E "Add no `await`" contradicted D: RESOLVED. E now reads "Add no new clerk call, branch or reordering of calls"; D states why the await changes no order, and the code bears it out.
- [NIT] 1, "character 60" read as 1-based: RESOLVED. Decisions and the requirement sentence now say "within its first 61 characters (index 60 or earlier), so at most 60 characters are kept", matching `lastIndexOf(' ', 60)`.

### Out-of-scope observations

- The pass-side evidence for the NEW scenarios (the prototype) is from round 1 and the prototype was not kept, which the spec says plainly. The base side was re-run this round. That is enough for the gate; the implementer's PR will produce the pass side.
- Operator step 1 passes `instance: "$RUNTIME/.factory"`, the runtime worktree's own copy of the instance, where README's "Starting a run" takes the instance from `$RUNTIME/bin/factory paths` run in the target repo (here `~/dev/spec-factory/.factory`). Both work against a throwaway store (checked above), so this is a style choice, not a defect.
