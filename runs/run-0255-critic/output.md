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

STATUS: APPROVE
CONFIDENCE: high, all four round-1 findings verified fixed against the code, the changed acceptance text reproduced on this checkout, and the Operator step's commands run end to end against a throwaway store
ESCALATIONS: none
