=== proposal.md
## Problem

The spec factory takes a feature request through a fixed sequence of AI agent jobs called roles: triage, spec writer, spec critic, planner, implementer, code reviewer and verifier. Each role is a separate Claude run with its own prompt. A small Python program, the harness (`bin/factory`), keeps the pipeline's records (the store) and enforces its rules, such as which state a ticket may move to next and how many revision rounds are allowed. Today two scripts decide which role runs next, one for the request-to-approved-spec half (intake) and one for the approved-spec-to-merged-code half (build). They are written for the Workflow tool, which runs JavaScript inside the operator's Claude Code session.

A Workflow-tool script cannot run a command or read a file. So every time the scripts need the store, they start one more agent, the clerk: a small model whose only job is to run one harness command and copy its output back. The operator who runs the factory pays for that relay in tokens, in time and in failures. The requester measured 2,236 clerk agents and 4,476 clerk calls over 97 workflow runs, 17% of all workflow context tokens, and most of the wait between steps. The clerk also fails in its own way: on 2026-10-09 it re-formatted a correct reply, and the script stopped a ticket whose step had succeeded. The scripts cannot give a role its own tool limits or effort level either. And every role agent the Workflow tool starts receives the operator's latest chat message, marked as overriding its task.

This change adds `factory drive TICKET`, an ordinary Python command that does the scripts' job. It routes exactly as the scripts do, with the same round limits, refusals and park reasons. It calls the harness directly, with no clerk. It starts each role as its own non-interactive Claude Code process (`claude -p`), with that role's prompt, model, effort and tool limits, and records each process's cost and session id with the run. It prints one line per step and keeps a status file. The Workflow scripts stay as they are until the operator has taken one real ticket through each half with the driver. Retiring them is a later ticket.

## Evidence

- Requester's measurement, issue #65, 2026-10-05: "the clerk was 2,236 agents and 4,476 calls, and 143M of 866M workflow context tokens (17%)". Not re-derived here.
- Clerk failure, T-0027.2, 2026-10-09 (issue comment): the reviewer's `run finish` succeeded (log `run.finished APPROVE`). The clerk returned the JSON pretty-printed across lines. The script parked the piece as `harness-bug: run finish reviewer:` with empty stderr.
- Every store access in the scripts is a clerk agent call: `grep -c 'clerk(' factory/workflows/intake.js factory/workflows/build.js` prints `factory/workflows/intake.js:12` and `factory/workflows/build.js:31`, each count including the `clerk` function's own definition (`intake.js:48`, `build.js:42`). The limit is design piece 2, limit (1): "The script has no filesystem or clock, so store reads and writes go through a clerk agent" (`docs/design.md:44`).
- Today `factory drive` does not exist. In every parity fixture below, the drive side printed `usage: factory [-h] [--accept-harness SHA] {ticket,run,spec,plan,subticket,results,merge,init,store,paths,archive,approve-spec,request-changes,resolve,decision,config,status,log}` and the store was left unchanged.
- Both scripts were run on throwaway fixtures under node, from this checkout (`bb410c0`). Clerk commands ran for real, and each role was played by a stand-in `claude` (the GIVEN block of the first scenario). Every route ended where the routing table says, and the number of role calls equalled the number of runs in the store:

  | Fixture, role plays | End state of T-0001 | Calls / runs |
  |---|---|---|
  | intake: ACCEPT, READY-FOR-CRITIC, REVISE then APPROVE | `awaiting-spec-gate`, spec round 2 | 5 / 5 |
  | intake: critic always REVISE | `parked`, `max rounds` | 5 / 5 |
  | intake: triage replies but writes no output | `parked`, `EMPTY-OUTPUT from triage` | 2 / 2 |
  | intake: triage call fails ("usage limit reached") | `parked`, `agent call failed: triage: usage limit reached`, run `KILLED` | 1 / 1 |
  | build from `ready-for-planner`: implementer, APPROVE, VERIFIED | T-0001.1 `merged`; T-0001 `parked`, `archive: no spec store (factory init not run)` | 4 / 4 |
  | build: reviewer always REQUEST-CHANGES | T-0001.1 `parked`, `max-round cutoff (reviewer REQUEST-CHANGES at round 2)` | 6 / 6 |
  | build: reviewer replies but writes nothing; verifier SPEC-DEFECT | T-0001.1 `parked`, `EMPTY-OUTPUT from reviewer` | 4 / 4 |
  | build: implementer BLOCKED | T-0001.1 `parked`, `BLOCKED from implementer` | 1 / 1 |

  The whole-spec step skipped the planner on the build fixture (log event `plan.skipped`), so the build route covers implementer, both checkers, the merge, the parent's final verifier run and archive.
- Claude Code 2.1.289, `claude --help` under a throwaway HOME: lists `--allowedTools`, `--tools`, `--effort <level>` ("low, medium, high, xhigh, max"), `--output-format` ("json (single result)"), `--add-dir`, `--model`, `--resume`, `--bare` and `--permission-mode` (choices "acceptEdits", "auto", "bypassPermissions", "manual", "dontAsk", "plan"). `--system-prompt-file` and `--append-system-prompt-file` are not listed, but both are accepted: `claude -p --append-system-prompt-file /nonexistent/sp.txt …` printed `Error: Append system prompt file not found: /nonexistent/sp.txt`, `--system-prompt-file` printed `Error: System prompt file not found: …`, and an unknown flag printed `error: unknown option '--bogus-flag-xyz'`. No model was called.
- Permission mode `dontAsk` is the strict mode, not a loose one. Claude Code's permissions page: "`dontAsk` | Auto-denies every call that would otherwise prompt; file reads in your working directories and other actions that need no approval still run, as do tools pre-approved via `/permissions` or `permissions.allow` rules." The build spec has it backwards: "Never `bypassPermissions` (nor `dontAsk`)" (`dev/build-harness.spec.md:118`, row R6).
- Rule forms (same page): "`Edit` rules apply to all built-in tools that edit files", so one `Edit(...)` rule also covers `Write`; `//path` is "Absolute path from filesystem root"; an output redirect in a Bash command is checked against `Edit` rules and the working directories.
- Headless mode (Claude Code docs, "Run Claude Code programmatically"): a run exits non-zero on failure, and "When a failure happens inside the run, such as missing authentication, Claude Code prints the failure as the result on stdout". `--bare` "doesn't use your subscription login". With `--output-format json` "the response payload includes `total_cost_usd`". "If you stop a `claude -p` run with SIGTERM … Claude Code exits with code 143 … and records no result".
- A checker's checkout lies inside its run directory: `_start_build_run` sets `wt = d / "wt"` (`factory/cli.py:390`), where `d` is `runs/<run id>`. A tool fence that allowed edits anywhere in the run directory would therefore let the reviewer or verifier edit the code it judges.
- The live-store fence (current truth `live-store-guard`, `factory/cli.py` `fence`, lines 1898–1913) refuses an unmarked write to an instance's own store while any run is in flight. A standing decision (2026-10-04, T-0024) is that a runner session puts `FACTORY_DISPATCH=1` in front of a command it runs while a run is in flight. The fixtures this change's scenarios reuse are in `openspec/specs/human-resolution/spec.md` (`t0023-parent.sh`) and in current truth `live-store-guard` (`t0024-inflight.sh`).
- In this run, Claude Code's auto-mode permission check refused one plain `bin/factory drive T-0001 --phase intake` command as "Create Unsafe Agents". The parity fixture runs, which call the same command with a stand-in `claude` first on `PATH`, were not refused.
- Not verified here, because each needs real model runs on the operator's login: whether concurrent `claude -p` processes conflict; whether the model alias `fable` is accepted by `claude --model`; which project settings and hooks load when the working directory is a run directory inside the store checkout; the start-up context with `--append-system-prompt-file` against `--system-prompt-file` (#24 part A's baseline is 44k tokens per call); and whether each role completes its work within the allowlists below. These are Operator steps.

## Root cause

Design piece 2 builds the dispatcher (the program that decides which role runs next) as a Workflow-tool script, and that script has no filesystem or process access (`docs/design.md:44`, limit 1). Every store call therefore goes through `clerk()` in `factory/workflows/intake.js` (lines 48–64) and `factory/workflows/build.js` (lines 42–58). Role agents are started with `agent()`, whose options carry a model but, in the `inlineRoles` mode every target uses, no per-role tool list (README, "What depends on Claude Code").

## Out of scope

- Retiring the Workflow scripts, `agents/factory-clerk.md`, the `agents/` definitions, the `inlineRoles` documentation, the workflow entries of `factory paths`, and `factory/cost.py`'s transcript reader. A follow-up ticket does this after Operator steps 1 and 2.
- A persistent conversation per role (`claude -p --resume`). It is to be measured once the driver exists.
- Recording a stop or a run's owner in the store (#53). A driver killed with SIGKILL leaves its runs in flight, cleared as today with a marked `run finish <run> --status-override KILLED`.
- Store integrity across concurrent writers (#60), beyond the driver serialising its own calls.
- Workflow graphs as configuration (#66), `factory report` (#17), and #76's read-limiting hook.
- `--bare`, per-run time or cost budgets, a stub mode in the driver, and a guard against two drivers on one ticket.
- No change to the routing table, round limits, ready states, park reasons, the fence, the harness lock, any role prompt, `docs/prompts/`, `agents/`, either instance's `.factory/` files, or the two Workflow scripts.

## Open questions

none

## Decisions

- The driver is a harness subcommand, `factory drive TICKET [--phase intake|build] [--parallel N] [--prompt-mode append|replace]`, in a new module `factory/drive.py`, run as its own foreground process. A runner session may start it in the background. Rejected: running it inside the Workflow tool, which is the limit this change removes.
- Store calls go through the CLI's own entry point, `factory.cli.main(argv)`, in the driver's process, with stdout and stderr captured, one call at a time on the driver's main thread. Every guard, refusal, fence check and lock check runs exactly as for `bin/factory`. Rejected: a `bin/factory` subprocess per call, which the requester ruled out. Rejected: calling store functions below `main`, which would skip the fence and the lock.
- `factory drive` is a write command like any other, so the fence and the lock apply when it starts. Under the standing 2026-10-04 T-0024 decision, a runner that starts it while any run is in flight on the target puts `FACTORY_DISPATCH=1` in front of it. Once started, the driver marks its own store calls whether or not it was started marked. Its role processes never inherit the marker. Rejected: exempting `drive` from the fence, which would change the current-truth requirement that every unmarked write is refused while a run is in flight.
- Each role runs as `claude -p <prompt> --model <models[role]> --output-format json --permission-mode dontAsk --append-system-prompt-file <run>/system-prompt.txt --tools <list> --allowedTools <list>`, plus `--add-dir <worktree>` for the implementer and `--effort <level>` when the instance sets one. The process runs from the run directory with stdin closed. The `-p` prompt is the fixed text that names the run's input and output files and nothing else. That also removes the operator's chat message from every role's task (#28, absorbed).
- `--permission-mode dontAsk` with explicit allowlists. This overturns build spec row R6's "nor `dontAsk`", which read the mode as looser than it is (Evidence). Rejected: `auto`, which needs a classifier decision on each call and was not the operator's choice. Rejected: `bypassPermissions`, which R6 rightly forbids.
- Tool fences. `--tools` is `Read,Grep,Glob,Bash,Write,WebFetch,WebSearch` for every role, and the implementer's list adds `Edit`. `--allowedTools` is `Read,Grep,Glob,Bash,WebFetch,WebSearch` plus three `Edit` rules on absolute real paths: `Edit(/<run>/output.md)`, `Edit(/<run>/scratch/**)` and `Edit(/<temporary directory>/**)`. The implementer's list adds `Edit(/<worktree>/**)`. The checkers therefore cannot use a file tool on the checkout under their run directory, which is #24 part A's fence, absorbed. Bash stays unrestricted, so this fence covers the file tools only (Risk). Web tools are kept because role agents have them today. Rejected: withholding `Write` from the checkers, who must write `output.md`.
- `--append-system-prompt-file` is the default. `--prompt-mode replace` passes `--system-prompt-file` instead, so the operator can measure the difference on a real ticket (Operator step 3). Rejected: deciding by measurement in this spec, which needs real model runs.
- No `--bare`: it needs an API key and does not use the operator's subscription.
- Effort per role comes from an optional `effort:` map in `instance.yaml`, keyed by role. An absent role gets no `--effort` flag. Values are passed through unchecked: Claude Code rejects a bad value before the run starts, which the driver records as a failed call. Neither instance sets `effort` in this change (Operator step 4). Per-role effort (#22) is absorbed.
- A role process's reply is kept whole, as printed, in `runs/<id>/reply.json`. `run finish` gains `--reply FILE`, which records `session_id`, `total_cost_usd`, `num_turns` and `usage` under a `claude:` key in the run's `meta.yaml`. The reply's `result` text is not copied into `meta.yaml`, because it repeats `output.md`. This departs from the request's wording, which listed `result` too.
- A failed call is a role process that exits non-zero or prints no JSON object on stdout. It is treated as a thrown `agent()` call is today: `run finish --status-override KILLED`, then a cleanup of a checker's checkout, then a park with `agent call failed: <role>: <message>`, and no retry. The message is the reply's `result` when there is one, else the last non-blank line of stderr, else `exit <code>`. A process that exits 0 with `is_error` set is routed on its output file like any other.
- The two checkers run as concurrent processes, and both finish and record their results before the join, as `parallel()` does today. Ready sub-tickets build concurrently up to `--parallel N`, default 2. Rejected: unbounded, as `build.js` runs today, while concurrent `claude -p` processes are untested (Operator step 2).
- On SIGINT or SIGTERM the driver sends SIGTERM to each role process it started. It sends SIGKILL to any still running 10 seconds later. It finishes each of its in-flight runs with `--status-override KILLED`, and runs a checker's cleanup. It parks nothing. It writes the stop to its status file, prints `{"ok": false, "ticket": "<id>", "stopped": "SIGINT"|"SIGTERM"}` as its last line and exits with 128 plus the signal number. Running `factory drive` again resumes from the stored state, as re-running a script does today. Rejected: parking on a stop, because a human stop is not a pipeline failure.
- Without `--phase`, the phase follows the stored state. `ready-for-triage`, `ready-for-spec-writer` and `ready-for-critic` are intake. `ready-for-planner`, `planned` and `ready-for-parent-verify` are build. Any other state ends at once with "nothing to dispatch", as the scripts do. The driver never crosses the spec gate.
- Progress output: one stdout line per step, `<ticket id> "<ticket title>": <step>`, where the ticket is the one the step concerns. A build step on a sub-ticket names the sub-ticket and its title (#47, absorbed). The last stdout line is one JSON object, the result the matching script returns, with `"ok": true` added. The status file is `drive/<parent id>.yaml` in the store, with keys `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running` (a list of `{run, role, ticket, pid}`), `last` (the last step line) and `ended` (null while running, then the result object). Rejected: changing `ticket show`, which `factory report` (#17) is meant to cover.
- The driver has no stub mode. Tests put a stand-in `claude` first on `PATH`. Rejected: porting the scripts' `stubs` argument, whose stub agent needs Claude Code.
- Park reasons and log events are the same as the scripts produce, so the parity scenarios compare records byte for byte, apart from ids, times and the order of the two checkers.
- Retiring the scripts (the request's part F) is a separate ticket. A sub-ticket of this spec cannot wait for the operator's real runs, so the build would retire the scripts before the driver had run a real ticket.
- The suite tests use a Python stand-in `claude`, so the suite needs nothing new. The acceptance scenarios also run the scripts under node, side by side with the driver, as earlier tickets' scenarios do.
- The change is NEEDS-SPLIT, in three lettered parts (design.md).

## Risk

Blast radius: a new command and module. `run finish` gains one optional flag. The existing commands, the two Workflow scripts and the fence are unchanged, so a runner that keeps using the scripts sees no difference. The driver writes the same records the scripts write, through the same entry point, plus `reply.json`, a `claude:` key in `meta.yaml` and `drive/<ticket>.yaml`.

- Role processes run under the operator's own login and settings, not a sandbox. The fence for file tools does not limit Bash, so a role can still write anywhere a shell command can. This is no weaker than today, where role agents run with the session's permissions. Isolation at the operating-system level is issue #37.
- `dontAsk` denies any tool call that no rule allows. A role whose work needs an unlisted tool, or an output redirect outside its allowed paths, will see that call denied. The run then ends with output that says so, or with EMPTY-OUTPUT. Operator step 1 checks the first real runs.
- Concurrent `claude -p` processes are untested. `--parallel 1` limits the driver to the two checkers at once.
- Claude Code's auto-mode permission check may refuse commands that run `factory drive` in the implementer's or verifier's session. It refused one such command in this run, while the same command with a stand-in `claude` on `PATH` went through (Evidence). T-0030.1 was refused twice in a similar way ("Code from External"). If the build parks on such a refusal, the operator must allow the command.
- Suite fixtures generate and run a stand-in `claude` script, so the same classifier may flag them.

Protected paths: `factory/**`

## Operator steps

1. After merge, move the runtime to the new revision and accept it (`--accept-harness`) on this instance. Drive one real ticket through intake with `factory drive <T> --phase intake`, and one through build after its spec gate. Check that each role finished its work under `dontAsk`: read each run's `reply.json` for permission denials. Record the per-ticket totals (the sum of `total_cost_usd` and of `usage` over the ticket's runs) beside the 2026-10-05 figures in `dev/issues.md` row 65.
2. On the same ticket or a second one, confirm that two checker processes and two drivers on different tickets run at once without errors. If they conflict, use `--parallel 1` and file an issue.
3. Drive one ticket with `--prompt-mode replace` and compare its start-up context with step 1's, against the 44k baseline. Keep `append` unless `replace` is smaller and the roles still finish.
4. To set per-role effort, add an `effort:` map to `.factory/instance.yaml` (protected `infra`), for example `effort: {critic: high}`.
5. When steps 1 and 2 have passed, file the retirement ticket: remove the Workflow scripts, the clerk and its agent definition, the `inlineRoles` documentation and the workflow entries of `factory paths`, and update the README.

=== design.md
## Proposed change

Size and seams: the change is about 800 lines in total, with the module, the tests and the documents together, so it is split into three parts. B depends on A. C depends on A and B.

**A. The driver core and the intake phase** (`factory/drive.py`, new; `factory/cli.py`; `factory/instance.template.yaml`; `tests/factory/test_drive.py`, new).

1. Command. Add the `drive` subparser to `build_parser()`: `TICKET`, `--phase {intake,build}`, `--parallel N` (int ≥ 1, default 2; used by B), `--prompt-mode {append,replace}` (default `append`). It dispatches through `main()` like every other write command. The instance refusal, the fence and the harness lock therefore apply at start, and a refusal exits 2 having written nothing. After those checks the driver sets `FACTORY_DISPATCH=1` in its own environment (`os.environ`).
2. Store calls. `call(*argv) -> dict` runs `factory.cli.main(list(argv))` with `sys.stdout` and `sys.stderr` redirected to buffers. It returns the last stdout line that parses as a JSON object, with `exit` (the return code) and `stderr` (the captured text). It applies the same normalisation as the scripts' `clerk()`: a non-zero exit sets `ok` to false, and a refusal with empty stderr takes its JSON `error`, else `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Calls run one at a time on the main thread. Role processes run concurrently as asyncio subprocesses.
3. Role runner, `run_role(role, ticket)`, mirrors the scripts' `runRole`/`runOnce`. It runs `run start --role R --ticket T --model models[R]` and parks on a refusal exactly as the scripts do (in build, a refusal whose `error` starts `BLOCKED ` parks with it verbatim). It runs `run compose`. It then starts `claude` (found on `PATH`) from the run directory, with stdin `/dev/null` and an environment equal to the driver's minus `FACTORY_DISPATCH`. The argv, in this order:
   `-p "Your entire input is the file <run>/input.md; read it first and follow it. Write your complete output to <run>/output.md and return the same text."`, `--model <models[role]>`, `--output-format json`, `--permission-mode dontAsk`, `--append-system-prompt-file <run>/system-prompt.txt` (or `--system-prompt-file` under `--prompt-mode replace`), `--tools <list>`, `--allowedTools <list>`, then `--add-dir <worktree>` for the implementer only, then `--effort <level>` when `effort[role]` is set. Each option and its value are separate arguments. `--tools` and `--allowedTools` each take one comma-separated value, as listed in proposal.md Decisions. `<run>`, `<worktree>` and the temporary directory (`tempfile.gettempdir()`) are written as real absolute paths. An `Edit` rule's path therefore starts with `//`.
   The driver writes the process's stdout, as printed, to `<run>/reply.json`. A failed call (exit ≠ 0, or stdout not a JSON object) goes to `run finish R --status-override KILLED --reply <run>/reply.json`, then `run cleanup R` for a reviewer or verifier, then a park with `agent call failed: <role>: <message>`. Otherwise the driver runs `run finish R --reply <run>/reply.json` and `run cleanup` for a checker, and then does exactly what the scripts do. A refused finish parks `harness-bug: run finish <role>: …`. A `parked` result stops the route. On `EMPTY-OUTPUT`, a non-blank reply `result` is kept with `run last-message R --text=<last 4000 characters>`, and the role is re-dispatched once. A second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both runs.
4. `run finish --reply FILE` (`factory/cli.py` `run_finish`). When FILE parses as a JSON object, it records `claude: {session_id, total_cost_usd, num_turns, usage}` in `meta.yaml`, each null when absent. Otherwise it records `claude: null`. Nothing else in `run finish` changes.
5. Intake routing: port `factory/workflows/intake.js` from `// --- start` to its end, branch for branch, with the same transitions, `--round` operations, `spec add` calls and park reasons: triage ACCEPT, REJECT, NEEDS-HUMAN, CLARIFY and unknown; the writer/critic loop with `max_rounds.spec` read from `factory config`. The config call also gives `models`.
6. Phase. `--phase` selects intake or build. Without it the stored state selects it (proposal.md Decisions). A state outside the selected phase returns `{"ticket", "state", "note": "nothing to dispatch from this state"}`.
7. Progress. Print one line per step on stdout and flush it: a role run started (`start <role> <run id>`), a role run finished (`<role> <run id>: <STATUS>`), a transition (`-> <state>`), a park (`parked: <reason>`) and the end. Each line has the form `<ticket id> "<title>": <step>`. The title is the ticket's `title` from `ticket show --json`, read again after triage ACCEPT. Write `drive/<parent id>.yaml` in the store (`store.write_yaml`) at start, at each step and at the end, with the keys listed in proposal.md Decisions. The last stdout line is the result JSON with `"ok": true`. Exit 0.
8. Stop. Install SIGINT and SIGTERM handlers that run the stop sequence in proposal.md Decisions. An unexpected exception inside the driver runs the same sequence and then exits 1.
9. `factory/instance.template.yaml`: add a commented `# effort: {critic: high}` example with one comment line on what it does.
10. Suite: `tests/factory/test_drive.py` with a Python stand-in `claude` written into `tmp_path` and put first on `PATH`. It covers each intake route of the parity table, the argv, the `claude:` record, the dropped marker, and a stop and resume.

**B. The build phase** (`factory/drive.py`; `tests/factory/test_drive.py`).

1. Port `factory/workflows/build.js` from `// --- start` to its end, and its `buildOne`, branch for branch, with the same commands, transitions and park reasons. That covers `plan whole-spec`, the planner and its `spec tasks` / `plan add` / `subticket add`, `ticket ready-implementers` with the one-time `subticket add` for a parent planned with none, the closed-sub-ticket park, `ticket parent-check` and its `reuse`, the parent's final verifier run, `archive` and `closed`. In `buildOne` it covers the implementer and `ticket head` with `merge_refused`, the move to `checks-in-flight`, which checkers run (both after an implementer run, otherwise those `results show` lists as missing), `results record` with the head, `ticket join` and its five decisions, `merge`, a `BLOCKED ` merge refusal parked verbatim, and the second join after a refused merge.
2. Concurrency. Run the two checkers of one head with `asyncio.gather`. Both finish and record their results before the join, and a failure of either ends that sub-ticket's pass after both have returned, as `parallel()` does. Run the sub-tickets of one `ready-implementers` answer as tasks, gated by a semaphore of `--parallel N`. Wait for all of them, then ask `ready-implementers` again, as the script's loop does.
3. Progress lines for a sub-ticket's steps carry the sub-ticket's id and title. The status file's `running` list holds every role process in flight.
4. Suite: add the build routes of the parity table, the implementer's `--add-dir` and `Edit` rule, the checkers' rules, and the `--parallel` bound.

**C. Documents** (`README.md`, `docs/design.md`, `dev/build-harness.spec.md`, `docs/changelog.md`).

1. README. "Starting a run" gains a how-to for `factory drive`: what to run, `FACTORY_DISPATCH=1` when another run is in flight, `--parallel`, what it prints, and the status file. It says the Workflow tool remains the tested route until the driver has run a real ticket. "What depends on Claude Code" gains a row for the driver's role processes (`claude -p`, the flags, `dontAsk`). "Built" gains a bullet for the driver, ending "It is tested, and has not yet run a real ticket". The "Not built" bullet "Per-role effort settings" is removed. Its replacement in "Built" says that effort is set per role for driver runs only. Follow "Maintaining this page": bump the status date, and re-derive any figure quoted.
2. `docs/design.md`. Piece 2 (`docs/design.md:44`) says that `factory drive` is the external dispatcher, with no clerk. The fence paragraph (line 64) says that the driver marks its own store calls and that its role processes are never marked. "Running on another agent host" names the driver as the Claude Code form of the adapter it describes.
3. `dev/build-harness.spec.md`. R3 names the driver beside the Workflow scripts. R6 replaces "Never `bypassPermissions` (nor `dontAsk`)" with the driver's `dontAsk` plus allowlists, keeping "Never `bypassPermissions`". Part H gains one paragraph pointing to `factory drive` for the same routing. I.4 says that under the driver the tool restriction is `--tools`/`--allowedTools`.
4. `docs/changelog.md`: one entry at the next free number, before the closing "Declined:" line, in the existing form "After issue #65 (2026-10-05), where …". It cites the clerk figures and the T-0027.2 failure, and notes #22, #28 and #47 as absorbed.

Scenario to part: A covers "The driver takes the intake fixtures through the same routes as the intake script", "Each role run records its process's reply", "Every intake step line names its ticket and title, and the status file shows the end", "A stopped driver ends its role process, records the run as killed and resumes from the stored state" and "The driver marks its own store calls, never its roles', and passes a configured effort". B covers "The driver takes the build fixtures through the same routes as the build script", "Each role runs as one claude process with its prompt, model and tool fences", "The checkers run at once, and sub-tickets up to the parallel limit" and "Build step lines name the sub-ticket they concern". C covers "The documents describe the driver". "The Workflow scripts still take both fixtures to the end of their routes" is a regression check for every part.

## Tests to change

none. No decision overturns behaviour that an existing test pins. The scripts, the clerk, the fence, the routing and `run finish` without `--reply` are unchanged. `tests/factory/test_sibling_tests.py`, `test_spec_drift.py` and `test_merge_protected_paths.py` drive `factory/workflows/build.js` and keep passing, because the script is untouched.

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: The driver takes a ticket through intake on the intake script's route
`factory drive TICKET --phase intake` MUST take a ticket from its stored intake state to the same end state, with the same ticket records, runs, result rows and log events, apart from ids and times, as `factory/workflows/intake.js` does when given the same role outputs, and it SHALL start no process other than one `claude` per role run.

#### Scenario: The driver takes the intake fixtures through the same routes as the intake script
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario also needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- GIVEN the six fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0040-claude <<'EOF'
#!/usr/bin/env node
// Stands in for `claude`. Run from a role run's directory (runs/run-NNNN-<role>). Appends one JSON line
// to $T40_LOG: its argv, its working directory, its pid and FACTORY_DISPATCH. Plays the next entry of
// its role's list in $T40_PLAYS (the last one repeats), counted in $T40_LOG.n-<role>. An entry may
// first sleep ("sleep": seconds), then:
//   {"write": "<STATUS>"}  writes output.md (a Commit: line with the run's head when meta.yaml has one;
//                          "Gate suite: PASS" for a verifier) and replies with the same text;
//   {"say": "<text>"}      writes nothing and replies with <text>;
//   {"fail": "<text>"}     writes nothing, replies with is_error and <text>, and exits 1.
// The reply is one JSON object on stdout, shaped like `claude -p --output-format json`. Each finished
// call appends "<start> <end>" (seconds) to $T40_LOG.times.
const fs = require('fs'), path = require('path')
const cwd = process.cwd(), log = process.env.T40_LOG, t0 = Date.now() / 1000
fs.appendFileSync(log, JSON.stringify({ argv: process.argv.slice(2), cwd, pid: process.pid, dispatch: process.env.FACTORY_DISPATCH || null }) + '\n')
const role = (path.basename(cwd).match(/^run-\d+-([a-z_]+)$/) || [])[1]
const list = (JSON.parse(process.env.T40_PLAYS || '{}')[role]) || [{ say: '' }]
const nf = `${log}.n-${role}`, n = (fs.existsSync(nf) ? +fs.readFileSync(nf, 'utf8') : 0) + 1
fs.writeFileSync(nf, String(n))
const p = list[Math.min(n, list.length) - 1]
if (p.sleep) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, p.sleep * 1000)
let text = '', err = false
if ('write' in p) {
  const head = (fs.readFileSync('meta.yaml', 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  text = (head ? `Commit: ${head}\n` : '') + (role === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  fs.writeFileSync('output.md', text)
} else if ('fail' in p) { text = p.fail; err = true } else { text = p.say }
fs.appendFileSync(`${log}.times`, `${t0} ${Date.now() / 1000}\n`)
process.stdout.write(JSON.stringify({ type: 'result', subtype: err ? 'error_during_execution' : 'success', is_error: err,
  result: text, session_id: `stub-${path.basename(cwd)}`, total_cost_usd: 0.25, num_turns: 1,
  usage: { input_tokens: 10, cache_creation_input_tokens: 20, cache_read_input_tokens: 30, output_tokens: 5 } }) + '\n')
process.exit(err ? 1 : 0)
EOF
chmod +x ${TMPDIR:-/tmp}/t0040-claude && mkdir -p ${TMPDIR:-/tmp}/t0040-bin && ln -sf ${TMPDIR:-/tmp}/t0040-claude ${TMPDIR:-/tmp}/t0040-bin/claude
cat > ${TMPDIR:-/tmp}/t0040-wf.mjs <<'EOF'
// node t0040-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script on <ticket> of the store $FACTORY_STATE. Each clerk command runs for real (sh -c, from this
// checkout). Each role call runs t0040-claude from the run's directory and returns its reply's
// `result`; a reply with is_error is thrown, as a failed agent call is.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const run = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  const cp = spawnSync(`${process.env.TMPDIR || '/tmp'}/t0040-claude`, ['-p', prompt], { cwd: run, encoding: 'utf8' })
  const reply = JSON.parse(cp.stdout)
  if (reply.is_error) throw new Error(reply.result)
  return reply.result
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: process.env.FACTORY_INTEGRATION_BRANCH, inlineRoles: true }, agent, () => {}, () => {},
  async (fs) => Promise.all(fs.map(f => f())))
EOF
cat > ${TMPDIR:-/tmp}/t0040-records.py <<'EOF'
# .venv/bin/python t0040-records.py <store>: prints the store's records in an order-free form, so two
# stores that took the same route print the same lines: each ticket's state, rounds and park reason;
# each run as role, ticket and status (no ids or times); each result row; log events counted by kind
# and ticket.
import collections, json, pathlib, sys, yaml
s = pathlib.Path(sys.argv[1]); y = lambda p: yaml.safe_load(p.read_text())
for p in sorted((s / "tickets").glob("*.yaml")):
    t = y(p); print("ticket", t["id"], t["status"], "spec=%s pr=%s" % (t["round"].get("spec"), t["round"].get("pr")),
                    "reason=" + str((t.get("parked") or {}).get("reason") or "").strip())
for line in sorted("run %s %s %s" % (m["role"], m["ticket"], m["status"]) for m in map(y, s.glob("runs/*/meta.yaml"))):
    print(line)
for line in sorted("result %s %s %s" % (r.get("ticket"), r.get("role"), r.get("status")) for r in map(y, s.glob("results/*/*.yaml"))):
    print(line)
ev = collections.Counter((e["event"], e.get("ticket")) for f in sorted(s.glob("log/*.jsonl")) for e in map(json.loads, f.read_text().splitlines()))
for (k, t), n in sorted(ev.items(), key=str):
    print("event", k, t, n)
EOF
cat > ${TMPDIR:-/tmp}/t0040-parity.sh <<'EOF'
# Sourced from the repo root with PHASE (intake or build) and P (plays, as for t0040-claude) set.
# Builds two identical fixtures: for intake, a throwaway store whose T-0001 is ready for triage; for
# build, t0023-parent.sh's store, whose T-0001 is ready for its planner. Runs the Workflow-tool script
# on one (under node) and `factory drive T-0001 --phase $PHASE` on the other, each role played by
# t0040-claude. Leaves in $D, per side (script, drive): <side>.records, <side>.log (t0040-claude's
# calls), <side>.out and <side>.err (stdout and stderr) and <side>.state (the store's path). Prints
# `<T-0001's state after drive> script=<calls>/<runs> drive=<calls>/<runs> same|differ`.
D=$(cd "$(mktemp -d)" && pwd -P)
for side in script drive; do (
  if [ $PHASE = intake ]; then T40=$(mktemp -d); export FACTORY_STATE=$T40/store
    printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null
  else . ${TMPDIR:-/tmp}/t0023-parent.sh; T40=$T23; fi
  export T40_LOG=$D/$side.log T40_PLAYS="$P"; : > $T40_LOG; echo $FACTORY_STATE > $D/$side.state
  if [ $side = script ]; then node ${TMPDIR:-/tmp}/t0040-wf.mjs factory/workflows/$PHASE.js T-0001 > $D/$side.out 2> $D/$side.err
  else PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH bin/factory drive T-0001 --phase $PHASE > $D/$side.out 2> $D/$side.err; fi
  .venv/bin/python ${TMPDIR:-/tmp}/t0040-records.py $FACTORY_STATE > $D/$side.records
  echo "$(grep -c . $T40_LOG)/$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .)" > $D/$side.count ); done
echo "$(sed -n 's/^ticket T-0001 \([^ ]*\) .*/\1/p' $D/drive.records) script=$(cat $D/script.count) drive=$(cat $D/drive.count) $(cmp -s $D/script.records $D/drive.records && echo same || echo differ)"
EOF
cat > ${TMPDIR:-/tmp}/t0040-calls.py <<'EOF'
# .venv/bin/python t0040-calls.py <t0040-claude log>: one line per call, sorted: `<role> ok`, or
# `<role> bad: <what>`. A call is ok when it ran from its run's directory without FACTORY_DISPATCH,
# with argv `-p <prompt>` then options given once each: --model (the run's model), --output-format
# json, --permission-mode dontAsk, --append-system-prompt-file <run>/system-prompt.txt, --tools and
# --allowedTools (one comma-separated argument each), and optionally --add-dir and --effort; no
# --bare and no --system-prompt-file. The prompt names only the run's input and output files. Every
# Edit allow rule covers only <run>/output.md, <run>/scratch/, the temporary directory, or for the
# implementer its worktree, which one rule covers; Edit is a tool only for the implementer.
import json, os, re, sys, tempfile, yaml
R = os.path.realpath; out = []
for c in map(json.loads, open(sys.argv[1]).read().splitlines()):
    run = R(c["cwd"]); m = yaml.safe_load(open(os.path.join(run, "meta.yaml"))); role = m["role"]; bad = []
    a = c["argv"]; opts = {}
    if a[:1] != ["-p"] or len(a) < 2: bad.append("no -p prompt")
    p = re.fullmatch(r"Your entire input is the file (\S+)/input\.md; read it first and follow it\. "
                     r"Write your complete output to (\S+)/output\.md and return the same text\.", a[1] if len(a) > 1 else "")
    if not p or R(p[1]) != run or R(p[2]) != run: bad.append("prompt")
    for k, v in zip(a[2::2], a[3::2]):
        if k in opts: bad.append("twice " + k)
        opts[k] = v
    if len(a[2:]) % 2: bad.append("odd options")
    want = {"--model": m["model"], "--output-format": "json", "--permission-mode": "dontAsk"}
    bad += ["%s=%s" % (k, opts.get(k)) for k, v in want.items() if opts.get(k) != v]
    if R(opts.get("--append-system-prompt-file", "/")) != os.path.join(run, "system-prompt.txt"): bad.append("system prompt")
    bad += [k for k in opts if k not in ("--model", "--output-format", "--permission-mode", "--append-system-prompt-file",
                                         "--tools", "--allowedTools", "--add-dir", "--effort")]
    if c["dispatch"] is not None: bad.append("FACTORY_DISPATCH")
    tools = opts.get("--tools", "").split(","); allow = opts.get("--allowedTools", "").split(",")
    if ("Edit" in tools) != (role == "implementer"): bad.append("Edit tool")
    ok = [os.path.join(run, "output.md"), os.path.join(run, "scratch") + "/**", R(tempfile.gettempdir()) + "/**"]
    wt = R(m["worktree"]) + "/**" if m.get("worktree") else None
    edits = [R("/" + e[7:-1].rstrip("*").rstrip("/")) + ("/**" if e.endswith("/**)") else "") for e in allow if e.startswith("Edit(//")]
    if any(e.startswith("Edit") and not e.startswith("Edit(//") for e in allow): bad.append("Edit rule form")
    bad += ["edit " + e for e in edits if e not in ok and not (role == "implementer" and e == wt)]
    if role == "implementer" and wt not in edits: bad.append("no worktree edit")
    out.append("%s %s" % (role, "ok" if not bad else "bad: " + ", ".join(bad)))
print("\n".join(sorted(out)))
EOF
```

- WHEN `(for P in '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}' '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}]}' '{"triage": [{"say": "still waiting on my commands"}]}' '{"triage": [{"fail": "usage limit reached"}]}'; do (PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
- THEN it prints exactly `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`, one per line

### Requirement: The driver takes an approved ticket through the build on the build script's route
`factory drive TICKET --phase build` MUST take an approved parent from its stored build state to the same end state, with the same ticket records, runs, result rows and log events, apart from ids and times, as `factory/workflows/build.js` does when given the same role outputs.

#### Scenario: The driver takes the build fixtures through the same routes as the build script
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(for P in '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "REQUEST-CHANGES"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]}' '{"implementer": [{"write": "BLOCKED"}]}'; do (PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
- THEN it prints exactly `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`, one per line

### Requirement: Each role run is one headless claude process with its role's prompt, model and tool fences
For every role run, the driver MUST start exactly one `claude` process from the run's directory, without `FACTORY_DISPATCH` in its environment, with argv `-p` and a prompt naming only the run's input and output files, then `--model` with the run's model, `--output-format json`, `--permission-mode dontAsk`, `--append-system-prompt-file <run>/system-prompt.txt`, `--tools` and `--allowedTools`, and no `--bare`. Its `Edit` allow rules SHALL cover only the run's `output.md`, its `scratch/`, the temporary directory and, for the implementer alone, its worktree, and only the implementer SHALL have the `Edit` tool.

#### Scenario: Each role runs as one claude process with its prompt, model and tool fences
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log; P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log)`
- THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`, one per line

### Requirement: A role process's reply is recorded with its run
After each role process ends, the run's directory MUST hold the process's stdout as `reply.json`, and the run's `meta.yaml` SHALL record its `session_id`, `total_cost_usd`, `num_turns` and `usage` under `claude:`.

#### Scenario: Each role run records its process's reply
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python -c 'import json,pathlib,sys,yaml; s=pathlib.Path(sys.argv[1]); ms=[yaml.safe_load(p.read_text()) for p in sorted(s.glob("runs/*/meta.yaml"))]; ok=lambda m,c: c.get("session_id")=="stub-"+m["run_id"] and c.get("total_cost_usd")==0.25 and c.get("num_turns")==1 and (c.get("usage") or {}).get("output_tokens")==5 and json.loads((s/"runs"/m["run_id"]/"reply.json").read_text())["session_id"]==c["session_id"]; print(" ".join("%s=%s" % (m["role"], "ok" if ok(m, m.get("claude") or {}) else "missing") for m in ms) or "none")' $(cat $D/drive.state))`
- THEN it prints exactly `triage=ok spec_writer=ok critic=ok`

### Requirement: The checkers run at once, and sub-tickets run concurrently up to a limit
The driver MUST run a head's reviewer and verifier as two concurrent processes, and SHALL build ready sub-tickets concurrently, at most `--parallel N` at a time, 2 when the option is not given.

#### Scenario: The checkers run at once, and sub-tickets up to the parallel limit
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once. Two sub-tickets with no dependency wait at `checks-in-flight`, each on its own commit; every checker sleeps 4 seconds, and the verifier's SPEC-DEFECT parks each one.
- WHEN `(for par in 1 default; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / One\nDepends on: none\nParallel-safe: yes\n\nST-2 / Two\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && for i in 1 2; do git -C $T23/t checkout -qb factory/T-0001.$i main && echo $i > $T23/t/f$i.txt && git -C $T23/t add f$i.txt && git -C $T23/t -c user.email=f@x -c user.name=f commit -qm w$i && git -C $T23/t checkout -q main && bin/factory ticket set T-0001.$i status=checks-in-flight branch=factory/T-0001.$i head=$(git -C $T23/t rev-parse factory/T-0001.$i) >/dev/null; done; export T40_LOG=$T23/claude.log T40_PLAYS='{"reviewer": [{"sleep": 4, "write": "APPROVE"}], "verifier": [{"sleep": 4, "write": "SPEC-DEFECT"}]}'; : > $T40_LOG; : > $T40_LOG.times; A=; [ $par = 1 ] && A='--parallel 1'; PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH bin/factory drive T-0001 --phase build $A >/dev/null 2>&1; echo "parallel=$par: calls=$(grep -c . $T40_LOG) max=$(.venv/bin/python -c 'import sys; t=[tuple(map(float, l.split())) for l in open(sys.argv[1])]; print(max([sum(a <= s < b for a, b in t) for s, _ in t] or [0]))' $T40_LOG.times) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `parallel=1: calls=4 max=2 parked parked`, then `parallel=default: calls=4 max=4 parked parked`

### Requirement: The driver reports each step on one line and in a status file
Every line the driver prints on stdout before its last MUST have the form `<ticket id> "<title>": <step>`, naming the ticket the step concerns, a sub-ticket included. The last line SHALL be the result as one JSON object, and the store's `drive/<ticket>.yaml` SHALL hold the ticket, its title, the role processes still running and, once the driver ends, its result under `ended`.

#### Scenario: Every intake step line names its ticket and title, and the status file shows the end
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "steps=$([ $(sed '$d' $O | grep -c .) -ge 10 ] && echo yes || echo no) untagged=$(sed '$d' $O | grep -vcE '^T-0001 "Fixture": ') last=$(tail -1 $O | grep -c '"state": "awaiting-spec-gate"') status=$(.venv/bin/python -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); print(d["ticket"], d["title"], d["ended"]["state"], len(d["running"]))' $(cat $D/drive.state)/drive/T-0001.yaml 2>/dev/null)")`
- THEN it prints exactly `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0`

#### Scenario: Build step lines name the sub-ticket they concern
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "untagged=$(sed '$d' $O | grep -vcE '^T-0001(\.1)? "[^"]+": ') sub=$([ $(grep -cE '^T-0001\.1 "[^"]+": ' $O) -ge 6 ] && echo yes || echo no) last=$(tail -1 $O | grep -c '"state": "parked"')")`
- THEN it prints exactly `untagged=0 sub=yes last=1`

### Requirement: A stopped driver ends its role processes and resumes from the stored state
On SIGTERM or SIGINT the driver MUST end every role process it started, record each of its in-flight runs as `KILLED`, leave the ticket in its stored state unparked with nothing in flight, print a last line with `"stopped"` and exit with 128 plus the signal number; `factory drive TICKET` run again SHALL continue from the stored state, choosing the phase from that state when `--phase` is not given.

#### Scenario: A stopped driver ends its role process, records the run as killed and resumes from the stored state
Needs the GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(T40=$(mktemp -d); export FACTORY_STATE=$T40/store T40_LOG=$T40/claude.log PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH; printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null; T40_PLAYS='{"triage": [{"sleep": 60, "write": "ACCEPT"}]}' bin/factory drive T-0001 > $T40/out 2>/dev/null & p=$!; for i in $(seq 50); do [ -s $T40_LOG ] && break; sleep 0.2; done; sleep 1; r=$(grep -c 'run-0001-triage' $FACTORY_STATE/drive/T-0001.yaml 2>/dev/null); kill -TERM $p 2>/dev/null; wait $p; x=$?; c=$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' $T40_LOG 2>/dev/null); echo "stop: exit=$x running=${r:-0} run=$(sed -n 's/^status: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml 2>/dev/null) $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) $(grep '^in_flight' $FACTORY_STATE/tickets/T-0001.yaml) child=$(kill -0 ${c:-999999} 2>/dev/null && echo alive || echo gone) last=$(tail -1 $T40/out | grep -c '"stopped": "SIGTERM"')"; T40_PLAYS='{"triage": [{"write": "REJECT"}]}' bin/factory drive T-0001 >/dev/null 2>&1; echo "resumed: exit=$? $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) calls=$(grep -c . $T40_LOG 2>/dev/null)")`
- THEN it prints exactly `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, then `resumed: exit=0 closed calls=2`

### Requirement: The driver marks its own store calls, never its role processes, and passes a configured effort
`factory drive` MUST be refused by the live-store fence like any write, so that unmarked it is refused while a run is in flight on the target's own store and it is refused from inside that store's `runs/` even when marked. Once started, its store calls SHALL carry the dispatcher marker, its role processes SHALL NOT, and a role with a level under `effort:` in `instance.yaml` SHALL get `--effort <level>`.

#### Scenario: The driver marks its own store calls, never its roles', and passes a configured effort
Needs the GIVEN blocks of "Unmarked writes from inside the target are refused while a run is in flight, init included" (current truth, live-store-guard) and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001's triage run stays in flight throughout; T-0002 is driven.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null && printf 'effort:\n  triage: low\n' >> $T/tgt/.factory/instance.yaml && cd $T/tgt && export T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "REJECT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG && $B drive T-0002 --phase intake >/dev/null 2>&1; u=$?; FACTORY_DISPATCH=1 $B drive T-0002 --phase intake >/dev/null 2>&1; m=$?; cd $W && FACTORY_DISPATCH=1 $B drive T-0002 --phase intake >/dev/null 2>&1; i=$?; echo "unmarked=$u marked=$m $($B ticket show T-0002 | sed -n 's/^status: //p') calls=$(grep -c . $T40_LOG) effort=$(grep -c '"--effort","low"' $T40_LOG) dispatch=$(grep -c '"dispatch":null' $T40_LOG) inside=$i")`
- THEN it prints exactly `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`

### Requirement: The Workflow scripts keep working beside the driver
`factory/workflows/intake.js` and `factory/workflows/build.js` SHALL still take a ticket through their routes unchanged until a later ticket retires them.

#### Scenario: The Workflow scripts still take both fixtures to the end of their routes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; grep '^ticket' $D/script.records | cut -d' ' -f2,3 | paste -sd' ' -; P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; grep '^ticket' $D/script.records | cut -d' ' -f2,3 | paste -sd' ' -)`
- THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the driver
`README.md` MUST describe `factory drive` under "Starting a run", its `claude -p` role processes under "What depends on Claude Code", and the driver among the built pieces, and SHALL no longer list per-role effort as not built; `docs/design.md` and `dev/build-harness.spec.md` SHALL name the driver, the build spec SHALL no longer forbid `dontAsk`, `docs/changelog.md` SHALL gain an entry for issue #65, and the changed documents SHALL carry no whitespace errors.

#### Scenario: The documents describe the driver
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md)) buildspec=$(y $(grep -c 'factory drive' dev/build-harness.spec.md)) dontask-ban=$(y $(grep -c 'nor `dontAsk`' dev/build-harness.spec.md)) whitespace=$(git diff --check main -- README.md docs dev >/dev/null && echo clean || echo dirty)")`
- THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no design=yes changelog=yes buildspec=yes dontask-ban=no whitespace=clean`

=== verification.md
## Acceptance

- The driver takes the intake fixtures through the same routes as the intake script → NEW. Today `bin/factory drive` exits 2 with argparse's usage line (`{ticket,run,spec,…,log}`, no `drive`). The four lines print `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ` and `ready-for-triage script=1/1 drive=0/0 differ` (run in this spec's investigation).
- The driver takes the build fixtures through the same routes as the build script → NEW. Today it prints `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=6/6 drive=0/0 differ`, `ready-for-planner script=4/4 drive=0/0 differ` and `ready-for-planner script=1/1 drive=0/0 differ` (observed).
- Each role runs as one claude process with its prompt, model and tool fences → NEW. Today the drive side starts no process, its log is empty, and the check prints two empty lines (observed). The check itself was validated on synthetic argv built to this design against real run directories: it printed `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`. It prints `bad: prompt, --model=None, …` for the scripts' own calls.
- Each role run records its process's reply → NEW. Today the drive store has no runs, so the check prints `none` (observed).
- The checkers run at once, and sub-tickets up to the parallel limit → NEW. Today it prints `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, then the same for `default` (observed). Under `build.js` the same fixture starts 4 calls and parks both sub-tickets `SPEC-DEFECT from verifier` (observed), so the fixture reaches the checkers.
- Every intake step line names its ticket and title, and the status file shows the end → NEW. Today it prints `steps=no untagged=0 last=0 status=`: stdout is empty and there is no status file (observed).
- Build step lines name the sub-ticket they concern → NEW. Today stdout is empty, and it prints `untagged=0 sub=no last=0` (observed).
- A stopped driver ends its role process, records the run as killed and resumes from the stored state → NEW. Today it prints `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0`, then `resumed: exit=2 ready-for-triage calls=` (observed).
- The driver marks its own store calls, never its roles', and passes a configured effort → NEW. Today it prints `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` (observed). `marked=2` is argparse's refusal.
- The Workflow scripts still take both fixtures to the end of their routes → REGRESSION. It prints `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` today (observed), and must after each part.
- The documents describe the driver → NEW. Today it prints `starting=no depends=no built=no effort-gap=yes design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean` (observed).

STATUS: NEEDS-SPLIT
CONFIDENCE: medium. The routing is pinned by side-by-side records against the scripts, and every fixture and check was run on this checkout. How real roles behave under `dontAsk` and the allowlists, and whether concurrent `claude -p` processes conflict, can only be shown by the operator's first real runs.
ESCALATIONS:
- Claude Code's auto-mode permission check in this session refused one plain `bin/factory drive T-0001 --phase intake` command as "Create Unsafe Agents". The implementer's and verifier's sessions may meet the same refusal when they run this change's scenarios or suite tests, as T-0030.1 did ("Code from External"). If the build parks on it, the operator needs to allow the command for those runs.
- This spec overturns build spec row R6's "Never `bypassPermissions` (nor `dontAsk`)". The Decisions line gives the reason and the documentation evidence. The operator approves the change at the spec gate.
