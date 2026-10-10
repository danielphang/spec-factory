## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0411-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0411-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0411-reviewer/wt` (branch `factory/T-0040.2`, base `2ad4d8c5288474b823d4571ba03de82a706eabdf`, head `4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0040.2

### T-0040.B / The build phase
Depends on: T-0040.A
Parallel-safe: no (it edits `factory/drive.py`, which A creates, and C depends on it)

Parent: T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B, items 1 to 4 of design.md:
- `build.js` ported from `// --- start` to its end, with `buildOne`, branch for branch;
- the two checkers run with `asyncio.gather`;
- ready sub-tickets run under a semaphore of `--parallel N`;
- progress lines and status-file `running` entries for sub-tickets;
- the build-route suite cases.

This sub-ticket also replaces A's interim build-phase refusal.

Put the new suite cases in a new file, `tests/factory/test_drive_build.py`. The file may import A's stand-in `claude` helper from `tests/factory/test_drive.py`, or copy it. The spec says these cases go in `test_drive.py`, but the guardrail allows new tests only in new files, and A's file is not on the parent's Tests to change list. This changes where the tests live, not what they check.

Acceptance:
- NEW. "The driver takes the build fixtures through the same routes as the build script".
  - WHEN `(for P in '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "REQUEST-CHANGES"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]}' '{"implementer": [{"write": "BLOCKED"}]}'; do (PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
  - THEN it prints exactly these four lines: `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`.
- NEW. "Each role runs as one claude process with its prompt, model and tool limits", in full. The intake half already passes after A; the build half does not.
  - WHEN the parent's command for that scenario is run (an intake parity run, then a build parity run, each followed by `t0040-calls.py`).
  - THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`, one per line.
- NEW. "The checkers run at once, and sub-tickets up to the parallel limit".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `parallel=1: calls=4 max=2 parked parked`, then `parallel=default: calls=4 max=4 parked parked`.
- NEW. "Build step lines name the sub-ticket they concern".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `untagged=0 sub=yes last=1`.
- REGRESSION. These parent scenarios already pass after A, and each must print exactly what A's Acceptance lists:
  - "The driver takes the intake fixtures through the same routes as the intake script";
  - "Each role run records its process's reply";
  - "Every intake step line names its ticket and title, and the status file shows the end";
  - "A stopped driver ends its role process, records the run as killed and resumes from the stored state";
  - "The driver marks its own store calls, never its roles', and passes a configured effort".
- REGRESSION. "The Workflow scripts still take both fixtures to the end of their routes".
  - THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`.
- Intermediate check: the harness suite passes, including `tests/factory/test_drive_build.py`.
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the running-code wrapper.
  - THEN it exits 0.

Before these scenarios, run the same GIVEN blocks as A.

Interim tests: none

Tests to change: none

Protected paths: `factory/**` (`factory/drive.py`)

Out of scope:
- part A's core, except where the build phase plugs into it. Do not change A's intake routing, `call()`, the argv, `run finish --reply` or the stop sequence, beyond what is needed to run them for build roles and sub-tickets;
- part C's documents;
- the parent's Out of scope, including any change to `factory/workflows/build.js`.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v3) already divides the change into three lettered parts, A, B and C, and states their order: B depends on A, and C depends on A and B (design.md, "Size and seams"). It also maps each scenario to a part. This plan keeps that split. Nothing smaller is worth splitting: A and B both edit `factory/drive.py`, and C documents what A and B build. Each of the three runs alone, one after another.

What I checked on `main` at `37848db`: `factory/drive.py` and `tests/factory/test_drive.py` do not exist, and `factory/cli.py` has no `drive`. So the change is not already applied. These things the spec names do exist:
- `STORE_GITIGNORE` at `factory/store.py:49`;
- the three tests to change, at `tests/factory/test_run_scratch.py:121`, `:132` and `:142`;
- the `// --- start` markers at `factory/workflows/intake.js:138` and `factory/workflows/build.js:217`;
- `run_finish` at `factory/cli.py:446`;
- the README anchors the documents scenario reads: "What depends on Claude Code" (line 97), "Terms used on this page" (117), "Starting a run" (690), "Filing a request from an issue tracker" (712), **Built** (828), **Not built** (904), and the "Per-role effort settings" bullet (913);
- R6's "nor `dontAsk`" at `dev/build-harness.spec.md:118`;
- `docs/changelog.md` entries up to 66, then "Declined:" at line 72.

---

## Parent spec (v4, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md`

=== proposal.md
## Problem

The operator who runs the spec factory pays a relay cost on every step of every ticket. The programs that decide which AI agent runs next cannot run a command or read a file. So each time they need the pipeline's records, they start one more agent, the clerk, whose only job is to run one command and copy its output back. Over 97 runs, the requester counted 2,236 clerk agents, 17% of all context tokens those runs used. The clerk was also most of the wait between steps. And it fails in its own way: on 2026-10-09 it re-formatted a correct reply, so a ticket was parked, that is, stopped for a human, although its step had succeeded.

The spec factory takes a feature request through a fixed sequence of AI agent jobs, called roles: triage, spec writer, spec critic, planner, implementer, code reviewer and verifier. Each role is a separate Claude run with its own prompt. The reviewer and the verifier are the checkers: both judge the implementer's commit, side by side. A Python program, the harness (`bin/factory`), keeps the pipeline's records, called the store, and enforces its rules, such as which state a ticket may move to next and how many revision rounds are allowed. Two scripts decide which role runs next. Intake takes a request to an approved spec. Build takes an approved spec to merged code: a planner splits the spec into sub-tickets, and each sub-ticket is implemented, checked and merged on its own. Both scripts are written for the Workflow tool, which runs JavaScript inside the operator's Claude Code session and gives a script no access to files or commands.

The scripts have two further limits. They cannot give a role its own tool limits or effort level. And every role agent the Workflow tool starts receives the operator's latest chat message, marked as overriding its task.

This change adds `factory drive TICKET`, an ordinary Python command that does the scripts' job. It routes exactly as the scripts do, with the same round limits, refusals and park reasons. It calls the harness directly, with no clerk. It starts each role as its own non-interactive Claude Code process (`claude -p`), with that role's prompt, model, effort and tool limits, and records each process's cost and session id with the run. It prints one line per step and keeps a status file. Like the intake script, it stops at the spec gate, where the operator approves a spec before any code is written. The Workflow scripts stay as they are until the operator has taken one real ticket through each half with the driver. Retiring them is a later ticket.

## Root cause

Design piece 2 builds the dispatcher (the program that decides which role runs next) as a Workflow-tool script, and that script has no filesystem or process access (`docs/design.md:44`, limit 1). Every store call therefore goes through `clerk()` in `factory/workflows/intake.js` (lines 50–67) and `factory/workflows/build.js` (lines 41–58). Role agents are started with `agent()`, whose options carry a model but, in the `inlineRoles` mode every target uses, no per-role tool list (README, "What depends on Claude Code").

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
- Each role runs as `claude -p <prompt> --model <models[role]> --output-format json --permission-mode auto --append-system-prompt-file <run>/system-prompt.txt --tools <list> --allowedTools <list>`, plus `--add-dir <worktree>` for the implementer and `--effort <level>` when the instance sets one. The process runs from the run directory with stdin closed. The `-p` prompt is the fixed text that names the run's input and output files and nothing else. That also removes the operator's chat message from every role's task (#28, absorbed).
- `--permission-mode auto` with explicit allowlists: the classifier keeps checking each call that no rule allows, as it does for role agents today. Rejected: `dontAsk`. It is strict (Evidence), but it removes the classifier while roles run with no operating-system isolation (#37); operator ruling, 2026-10-09, to revisit once #37 lands. Build spec row R6's "nor `dontAsk`" therefore stays. Rejected: `bypassPermissions`, which R6 rightly forbids.
- Tool limits. `--tools` is `Read,Grep,Glob,Bash,Write,WebFetch,WebSearch` for every role, and the implementer's list adds `Edit`. `--allowedTools` is `Read,Grep,Glob,Bash,WebFetch,WebSearch` plus three `Edit` rules on absolute real paths: `Edit(/<run>/output.md)`, `Edit(/<run>/scratch/**)` and `Edit(/<temporary directory>/**)`. The implementer's list adds `Edit(/<worktree>/**)`. The checkers therefore cannot use a file tool on the checkout under their run directory, which is the limit #24 part A wanted, absorbed. Bash stays unrestricted, so these limits cover the file tools only (Risk). Web tools are kept because role agents have them today. Every other tool the session offers today, such as sub-agents, task lists and notebook edits, is withheld: no role prompt in `factory/prompts/` asks for one. Rejected: withholding `Write` from the checkers, who must write `output.md`.
- `--append-system-prompt-file` is the default. `--prompt-mode replace` passes `--system-prompt-file` instead, so the operator can measure the difference on a real ticket (Operator step 3). Rejected: deciding by measurement in this spec, which needs real model runs.
- No `--bare`: it needs an API key and does not use the operator's subscription.
- Effort per role comes from an optional `effort:` map in `instance.yaml`, keyed by role. An absent role gets no `--effort` flag. Values are passed through unchecked: Claude Code rejects a bad value before the run starts, which the driver records as a failed call. Neither instance sets `effort` in this change (Operator step 4). Per-role effort (#22) is absorbed.
- A role process's reply is kept whole, as printed, in `runs/<id>/reply.json`. `run finish` gains `--reply FILE`, which records `session_id`, `total_cost_usd`, `num_turns` and `usage` under a `claude:` key in the run's `meta.yaml`. The reply's `result` text is not copied into `meta.yaml`, because it repeats `output.md`. This departs from the request's wording, which listed `result` too.
- A failed call is a role process that exits non-zero or prints no JSON object on stdout. It is treated as a thrown `agent()` call is today: `run finish --status-override KILLED`, then a cleanup of a checker's checkout, then a park with `agent call failed: <role>: <message>`, and no retry. The message is the reply's `result` when there is one, else the last non-blank line of stderr, else `exit <code>`. A process that exits 0 with `is_error` set is routed on its output file like any other.
- The two checkers run as concurrent processes, and both finish and record their results before the join, as `parallel()` does today. Ready sub-tickets build concurrently up to `--parallel N`, default 2. Rejected: unbounded, as `build.js` runs today, while concurrent `claude -p` processes are untested (Operator step 2).
- On SIGINT or SIGTERM the driver sends SIGTERM to each role process it started. It sends SIGKILL to any still running 10 seconds later. It finishes each of its in-flight runs with `--status-override KILLED`, and runs a checker's cleanup. It parks nothing. It writes the stop to its status file, prints `{"ok": false, "ticket": "<id>", "stopped": "SIGINT"|"SIGTERM"}` as its last line and exits with 128 plus the signal number. Running `factory drive` again resumes from the stored state, as re-running a script does today. Rejected: parking on a stop, because a human stop is not a pipeline failure.
- Without `--phase`, the phase follows the stored state. `ready-for-triage`, `ready-for-spec-writer` and `ready-for-critic` are intake. `ready-for-planner`, `planned` and `ready-for-parent-verify` are build. Any other state ends at once with "nothing to dispatch", as the scripts do. The driver never crosses the spec gate.
- Progress output: one stdout line per step, `<ticket id> "<ticket title>": <step>`, where the ticket is the one the step concerns. A build step on a sub-ticket names the sub-ticket and its title (#47, absorbed). The last stdout line is one JSON object, the result the matching script returns, with `"ok": true` added. The status file is `drive/<parent id>.yaml` in the store, with keys `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running` (a list of `{run, role, ticket, pid}`), `last` (the last step line) and `ended` (null while running, then the result object). Rejected: changing `ticket show`, which `factory report` (#17) is meant to cover.
- The status file is never committed. Part A appends `drive/` to the store's `.gitignore` block, under its own comment line, as `runs/*/tripwire.yaml` is. The file is a live view of one driver process: its `pid`, `updated` time and `running` list change at every step, and what lasts (each run's status, reply and cost, the ticket's state) is already in the run and ticket records. Rejected: committing it, which adds a churning file to every store commit. Rejected: a `drive/.gitignore` that ignores its own directory, which would put a second list of never-committed paths beside the store's block.
- The driver has no stub mode. Tests put a stand-in `claude` first on `PATH`. Rejected: porting the scripts' `stubs` argument, whose stub agent needs Claude Code.
- Park reasons and log events are the same as the scripts produce, so the parity scenarios compare records byte for byte, apart from ids, times and the order of the two checkers.
- Retiring the scripts (the request's part F) is a separate ticket. A sub-ticket of this spec cannot wait for the operator's real runs, so the build would retire the scripts before the driver had run a real ticket.
- The suite tests use a Python stand-in `claude`, so the suite needs nothing new. The acceptance scenarios also run the scripts under node, side by side with the driver, as earlier tickets' scenarios do.
- The change is NEEDS-SPLIT, in three lettered parts (design.md).

## Risk

Blast radius: a new command and module. `run finish` gains one optional flag, and the store's `.gitignore` block gains `drive/`, which every store gets at its next `run start`. The existing commands, the two Workflow scripts and the fence are unchanged, so a runner that keeps using the scripts sees no difference. The driver writes the same records the scripts write, through the same entry point, plus `reply.json`, a `claude:` key in `meta.yaml` and `drive/<ticket>.yaml`.

- Role processes run under the operator's own login and settings, not a sandbox. The tool limits do not cover Bash, so a role can still write anywhere a shell command can. This is no weaker than today, where role agents run with the session's permissions. Isolation at the operating-system level is issue #37.
- Under `auto`, the classifier may refuse a role's command that no rule allows, as it refused T-0030.1's twice. A refused call ends the run with output that says so, or with EMPTY-OUTPUT, and the operator answers case by case. Operator step 1 checks the first real runs.
- Concurrent `claude -p` processes are untested. `--parallel 1` limits the driver to the two checkers at once.
- Claude Code's auto-mode permission check may refuse commands that run `factory drive` in the implementer's or verifier's session. It refused one such command in this run, while the same command with a stand-in `claude` on `PATH` went through (Evidence). T-0030.1 was refused twice in a similar way ("Code from External"). If the build parks on such a refusal, the operator must allow the command.
- Suite fixtures generate and run a stand-in `claude` script, so the same classifier may flag them.

Protected paths: `factory/**`

## Operator steps

1. After merge, move the runtime, the separate checkout the factory runs from, to the merged revision. Then accept that revision for this repository's instance with `--accept-harness <commit>`: each target repository refuses to run a harness revision it has not accepted. Drive one real ticket through intake with `factory drive <T> --phase intake`, and one through build after its spec gate. Check that each role finished its work under `auto`: read each run's `reply.json` for permission denials. Record the per-ticket totals (the sum of `total_cost_usd` and of `usage` over the ticket's runs) beside the 2026-10-05 figures in `dev/issues.md` row 65.
2. On the same ticket or a second one, confirm that two checker processes and two drivers on different tickets run at once without errors. If they conflict, use `--parallel 1` and file an issue.
3. Drive one ticket with `--prompt-mode replace` and compare its start-up context with step 1's, against the 44k baseline. Keep `append` unless `replace` is smaller and the roles still finish.
4. To set per-role effort, add an `effort:` map to `.factory/instance.yaml` (protected `infra`), for example `effort: {critic: high}`.
5. When steps 1 and 2 have passed, file the retirement ticket: remove the Workflow scripts, the clerk and its agent definition, the `inlineRoles` documentation and the workflow entries of `factory paths`, and update the README.

=== design.md
## Proposed change

Size and seams: the change is about 800 lines in total, with the module, the tests and the documents together, so it is split into three parts. B depends on A. C depends on A and B.

**A. The driver core and the intake phase** (`factory/drive.py`, new; `factory/cli.py`; `factory/store.py`; `factory/instance.template.yaml`; `tests/factory/test_drive.py`, new; `tests/factory/test_run_scratch.py`).

1. Command. Add the `drive` subparser to `build_parser()`: `TICKET`, `--phase {intake,build}`, `--parallel N` (int ≥ 1, default 2; used by B), `--prompt-mode {append,replace}` (default `append`). It dispatches through `main()` like every other write command. The instance refusal, the fence and the harness lock therefore apply at start, and a refusal exits 2 having written nothing. After those checks the driver sets `FACTORY_DISPATCH=1` in its own environment (`os.environ`).
2. Store calls. `call(*argv) -> dict` runs `factory.cli.main(list(argv))` with `sys.stdout` and `sys.stderr` redirected to buffers. It returns the last stdout line that parses as a JSON object, with `exit` (the return code) and `stderr` (the captured text). It applies the same normalisation as the scripts' `clerk()`: a non-zero exit sets `ok` to false, and a refusal with empty stderr takes its JSON `error`, else `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Calls run one at a time on the main thread. Role processes run concurrently as asyncio subprocesses.
3. Role runner, `run_role(role, ticket)`, mirrors the scripts' `runRole`/`runOnce`. It runs `run start --role R --ticket T --model models[R]` and parks on a refusal exactly as the scripts do (in build, a refusal whose `error` starts `BLOCKED ` parks with it verbatim). It runs `run compose`. It then starts `claude` (found on `PATH`) from the run directory, with stdin `/dev/null` and an environment equal to the driver's minus `FACTORY_DISPATCH`. The argv, in this order:
   `-p "Your entire input is the file <run>/input.md; read it first and follow it. Write your complete output to <run>/output.md and return the same text."`, `--model <models[role]>`, `--output-format json`, `--permission-mode auto`, `--append-system-prompt-file <run>/system-prompt.txt` (or `--system-prompt-file` under `--prompt-mode replace`), `--tools <list>`, `--allowedTools <list>`, then `--add-dir <worktree>` for the implementer only, then `--effort <level>` when `effort[role]` is set. Each option and its value are separate arguments. `--tools` and `--allowedTools` each take one comma-separated value, as listed in proposal.md Decisions. `<run>`, `<worktree>` and the temporary directory (`tempfile.gettempdir()`) are written as real absolute paths. An `Edit` rule's path therefore starts with `//`.
   The driver writes the process's stdout, as printed, to `<run>/reply.json`. A failed call (exit ≠ 0, or stdout not a JSON object) goes to `run finish R --status-override KILLED --reply <run>/reply.json`, then `run cleanup R` for a reviewer or verifier, then a park with `agent call failed: <role>: <message>`. Otherwise the driver runs `run finish R --reply <run>/reply.json` and `run cleanup` for a checker, and then does exactly what the scripts do. A refused finish parks `harness-bug: run finish <role>: …`. A `parked` result stops the route. On `EMPTY-OUTPUT`, a non-blank reply `result` is kept with `run last-message R --text=<last 4000 characters>`, and the role is re-dispatched once. A second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both runs.
4. `run finish --reply FILE` (`factory/cli.py` `run_finish`). When FILE parses as a JSON object, it records `claude: {session_id, total_cost_usd, num_turns, usage}` in `meta.yaml`, each null when absent. Otherwise it records `claude: null`. Nothing else in `run finish` changes.
5. Intake routing: port `factory/workflows/intake.js` from `// --- start` to its end, branch for branch, with the same transitions, `--round` operations, `spec add` calls and park reasons: triage ACCEPT, REJECT, NEEDS-HUMAN, CLARIFY and unknown; the writer/critic loop with `max_rounds.spec` read from `factory config`. The config call also gives `models`.
6. Phase. `--phase` selects intake or build. Without it the stored state selects it (proposal.md Decisions). A state outside the selected phase returns `{"ticket", "state", "note": "nothing to dispatch from this state"}`.
7. Progress. Print one line per step on stdout and flush it: a role run started (`start <role> <run id>`), a role run finished (`<role> <run id>: <STATUS>`), a transition (`-> <state>`), a park (`parked: <reason>`) and the end. Each line has the form `<ticket id> "<title>": <step>`. The title is the ticket's `title` from `ticket show --json`, read again after triage ACCEPT. Write `drive/<parent id>.yaml` in the store (`store.write_yaml`) at start, at each step and at the end, with the keys listed in proposal.md Decisions. Append to `STORE_GITIGNORE` (`factory/store.py`), after `runs/*/scratch/`, one comment line saying the driver's status files are a live view never committed, then `drive/`. The last stdout line is the result JSON with `"ok": true`. Exit 0.
8. Stop. Install SIGINT and SIGTERM handlers that run the stop sequence in proposal.md Decisions. An unexpected exception inside the driver runs the same sequence and then exits 1.
9. `factory/instance.template.yaml`: add a commented `# effort: {critic: high}` example with one comment line on what it does.
10. Suite: `tests/factory/test_drive.py` with a Python stand-in `claude` written into `tmp_path` and put first on `PATH`. It covers each intake route of the parity table, the argv, the `claude:` record, the dropped marker, and a stop and resume. Update the three tests listed under Tests to change.

**B. The build phase** (`factory/drive.py`; `tests/factory/test_drive.py`).

1. Port `factory/workflows/build.js` from `// --- start` to its end, and its `buildOne`, branch for branch, with the same commands, transitions and park reasons. That covers `plan whole-spec`, the planner and its `spec tasks` / `plan add` / `subticket add`, `ticket ready-implementers` with the one-time `subticket add` for a parent planned with none, the closed-sub-ticket park, `ticket parent-check` and its `reuse`, the parent's final verifier run, `archive` and `closed`. In `buildOne` it covers the implementer and `ticket head` with `merge_refused`, the move to `checks-in-flight`, which checkers run (both after an implementer run, otherwise those `results show` lists as missing), `results record` with the head, `ticket join` and its five decisions, `merge`, a `BLOCKED ` merge refusal parked verbatim, and the second join after a refused merge.
2. Concurrency. Run the two checkers of one head with `asyncio.gather`. Both finish and record their results before the join, and a failure of either ends that sub-ticket's pass after both have returned, as `parallel()` does. Run the sub-tickets of one `ready-implementers` answer as tasks, gated by a semaphore of `--parallel N`. Wait for all of them, then ask `ready-implementers` again, as the script's loop does.
3. Progress lines for a sub-ticket's steps carry the sub-ticket's id and title. The status file's `running` list holds every role process in flight.
4. Suite: add the build routes of the parity table, the implementer's `--add-dir` and `Edit` rule, the checkers' rules, and the `--parallel` bound.

**C. Documents** (`README.md`, `docs/design.md`, `dev/build-harness.spec.md`, `docs/changelog.md`).

1. README. "Starting a run" gains a how-to for `factory drive`: what to run, `FACTORY_DISPATCH=1` when another run is in flight, `--parallel`, what it prints, and the status file. It says the Workflow tool remains the tested route until the driver has run a real ticket. "What depends on Claude Code" gains a row for the driver's role processes (`claude -p`, the flags, `auto`). "Built" gains a bullet for the driver, ending "It is tested, and has not yet run a real ticket". The "Not built" bullet "Per-role effort settings" is removed. Its replacement in "Built" says that effort is set per role for driver runs only. The store's file table gains a row for `drive/<ticket>.yaml`: on no branch, git ignores it, written by `factory drive`, never committed, rewritten at each step and kept until the next drive of that ticket. The table's "Store records" row says the records are written through the workflows' clerk or `factory drive`. Follow "Maintaining this page": bump the status date, and re-derive any figure quoted.
2. `docs/design.md`. Piece 2 (`docs/design.md:44`) says that `factory drive` is the external dispatcher, with no clerk. The fence paragraph (line 64) says that the driver marks its own store calls and that its role processes are never marked. "Running on another agent host" names the driver as the Claude Code form of the adapter it describes.
3. `dev/build-harness.spec.md`. R3 names the driver beside the Workflow scripts. R6 keeps "Never `bypassPermissions` (nor `dontAsk`)" and adds that the driver runs roles under `auto` plus allowlists. Part H gains one paragraph pointing to `factory drive` for the same routing. I.4 says that under the driver the tool restriction is `--tools`/`--allowedTools`.
4. `docs/changelog.md`: one entry at the next free number, before the closing "Declined:" line, in the existing form "After issue #65 (2026-10-05), where …". It cites the clerk figures and the T-0027.2 failure, and notes #22, #28 and #47 as absorbed.

Scenario to part: A covers "The driver takes the intake fixtures through the same routes as the intake script", "Each role run records its process's reply", "Every intake step line names its ticket and title, and the status file shows the end", "A stopped driver ends its role process, records the run as killed and resumes from the stored state" and "The driver marks its own store calls, never its roles', and passes a configured effort". B covers "The driver takes the build fixtures through the same routes as the build script", "Each role runs as one claude process with its prompt, model and tool limits", "The checkers run at once, and sub-tickets up to the parallel limit" and "Build step lines name the sub-ticket they concern". C covers "The documents describe the driver". "The Workflow scripts still take both fixtures to the end of their routes" is a regression check for every part.

## Tests to change

Part A, following the Decision that the status file is never committed (`drive/` joins the store's `.gitignore` block). Each test pins the block's exact text, so each must take the new comment line and `drive/` as the block's last two lines:

- `tests/factory/test_run_scratch.py`, `test_a_new_store_gitignore_is_the_full_commented_block_once`: asserts exactly 3 comment lines; the block now has 4. Its loop over entries should also count `drive/` once.
- `tests/factory/test_run_scratch.py`, `test_an_existing_store_gitignore_gains_only_the_missing_lines`: asserts the exact line list ending `"runs/*/scratch/"`; it now ends `"runs/*/scratch/", "drive/"`.
- `tests/factory/test_run_scratch.py`, `test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line`: same, its list now ends with `"drive/"`.

No other decision overturns behaviour an existing test pins. The scripts, the clerk, the fence, the routing and `run finish` without `--reply` are unchanged. Tests that read the store's `.gitignore` by membership (`test_instance.py:96`, `test_shepherd.py:200`, `test_tripwire.py:231`) keep passing. `tests/factory/test_sibling_tests.py`, `test_spec_drift.py` and `test_merge_protected_paths.py` drive `factory/workflows/build.js` and keep passing, because the script is untouched.

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
# json, --permission-mode auto, --append-system-prompt-file <run>/system-prompt.txt, --tools and
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
    want = {"--model": m["model"], "--output-format": "json", "--permission-mode": "auto"}
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

### Requirement: Each role run is one headless claude process with its role's prompt, model and tool limits
For every role run, the driver MUST start exactly one `claude` process from the run's directory, without `FACTORY_DISPATCH` in its environment, with argv `-p` and a prompt naming only the run's input and output files, then `--model` with the run's model, `--output-format json`, `--permission-mode auto`, `--append-system-prompt-file <run>/system-prompt.txt`, `--tools` and `--allowedTools`, and no `--bare`. Its `Edit` allow rules SHALL cover only the run's `output.md`, its `scratch/`, the temporary directory and, for the implementer alone, its worktree, and only the implementer SHALL have the `Edit` tool.

#### Scenario: Each role runs as one claude process with its prompt, model and tool limits
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
Every line the driver prints on stdout before its last MUST have the form `<ticket id> "<title>": <step>`, naming the ticket the step concerns, a sub-ticket included. The last line SHALL be the result as one JSON object, and the store's `drive/<ticket>.yaml` SHALL hold the ticket, its title, the role processes still running and, once the driver ends, its result under `ended`; the store's `.gitignore` SHALL exclude `drive/`.

#### Scenario: Every intake step line names its ticket and title, and the status file shows the end
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "steps=$([ $(sed '$d' $O | grep -c .) -ge 10 ] && echo yes || echo no) untagged=$(sed '$d' $O | grep -vcE '^T-0001 "Fixture": ') last=$(tail -1 $O | grep -c '"state": "awaiting-spec-gate"') status=$(.venv/bin/python -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); print(d["ticket"], d["title"], d["ended"]["state"], len(d["running"]))' $(cat $D/drive.state)/drive/T-0001.yaml 2>/dev/null) ignored=$(cat $(cat $D/drive.state)/.gitignore 2>/dev/null | grep -cx 'drive/')")`
- THEN it prints exactly `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`

#### Scenario: Build step lines name the sub-ticket they concern
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "untagged=$(sed '$d' $O | grep -vcE '^T-0001(\.1)? "[^"]+": ') sub=$([ $(grep -cE '^T-0001\.1 "[^"]+": ' $O) -ge 6 ] && echo yes || echo no) last=$(tail -1 $O | grep -c '"state": "parked"')")`
- THEN it prints exactly `untagged=0 sub=yes last=1`

### Requirement: A stopped driver ends its role processes and resumes from the stored state
On SIGTERM or SIGINT the driver MUST end every role process it started, record each of its in-flight runs as `KILLED`, leave the ticket in its stored state unparked with nothing in flight, print a last line with `"stopped"` and exit with 128 plus the signal number; `factory drive TICKET` run again SHALL continue from the stored state, choosing the phase from that state when `--phase` is not given.

#### Scenario: A stopped driver ends its role process, records the run as killed and resumes from the stored state
Needs the GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(T40=$(mktemp -d); export FACTORY_STATE=$T40/store T40_LOG=$T40/claude.log PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH; printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null; T40_PLAYS='{"triage": [{"sleep": 60, "write": "ACCEPT"}]}' bin/factory drive T-0001 > $T40/out 2>/dev/null & p=$!; for i in $(seq 50); do [ -s $T40_LOG ] && break; sleep 0.2; done; sleep 1; r=$(grep -c '^- run: run-0001-triage' $FACTORY_STATE/drive/T-0001.yaml 2>/dev/null); kill -TERM $p 2>/dev/null; wait $p; x=$?; c=$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' $T40_LOG 2>/dev/null); echo "stop: exit=$x running=${r:-0} run=$(sed -n 's/^status: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml 2>/dev/null) $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) $(grep '^in_flight' $FACTORY_STATE/tickets/T-0001.yaml) child=$(kill -0 ${c:-999999} 2>/dev/null && echo alive || echo gone) last=$(tail -1 $T40/out | grep -c '"stopped": "SIGTERM"')"; T40_PLAYS='{"triage": [{"write": "REJECT"}]}' bin/factory drive T-0001 >/dev/null 2>&1; echo "resumed: exit=$? $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) calls=$(grep -c . $T40_LOG 2>/dev/null)")`
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
`README.md` MUST describe `factory drive` under "Starting a run", its `claude -p` role processes under "What depends on Claude Code", the driver among the built pieces and its status file in the store's file table, and SHALL no longer list per-role effort as not built; `docs/design.md` and `dev/build-harness.spec.md` SHALL name the driver, the build spec SHALL still forbid `dontAsk`, `docs/changelog.md` SHALL gain an entry for issue #65, and the changed documents SHALL carry no whitespace errors.

#### Scenario: The documents describe the driver
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) drive-row=$(y $(grep -cE '^\| `drive/' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md)) buildspec=$(y $(grep -c 'factory drive' dev/build-harness.spec.md)) dontask-ban=$(y $(grep -c 'nor `dontAsk`' dev/build-harness.spec.md)) whitespace=$(git diff --check main -- README.md docs dev >/dev/null && echo clean || echo dirty)")`
- THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`

=== verification.md
## Acceptance

- The driver takes the intake fixtures through the same routes as the intake script → NEW. Today `bin/factory drive` exits 2 with argparse's usage line (`{ticket,run,spec,…,log}`, no `drive`). The four lines print `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ` and `ready-for-triage script=1/1 drive=0/0 differ` (run in this spec's investigation).
- The driver takes the build fixtures through the same routes as the build script → NEW. Today it prints `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=6/6 drive=0/0 differ`, `ready-for-planner script=4/4 drive=0/0 differ` and `ready-for-planner script=1/1 drive=0/0 differ` (observed).
- Each role runs as one claude process with its prompt, model and tool limits → NEW. Today the drive side starts no process, its log is empty, and the check prints two empty lines (observed). The check itself was validated on synthetic argv built to this design against real run directories: it printed `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`. It prints `bad: prompt, --model=None, …` for the scripts' own calls.
- Each role run records its process's reply → NEW. Today the drive store has no runs, so the check prints `none` (observed).
- The checkers run at once, and sub-tickets up to the parallel limit → NEW. Today it prints `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, then the same for `default` (observed). Under `build.js` the same fixture starts 4 calls and parks both sub-tickets `SPEC-DEFECT from verifier` (observed), so the fixture reaches the checkers.
- Every intake step line names its ticket and title, and the status file shows the end → NEW. Today it prints `steps=no untagged=0 last=0 status= ignored=0`: stdout is empty, there is no status file, and the store's `.gitignore` has no `drive/` line (observed, round 2).
- Build step lines name the sub-ticket they concern → NEW. Today stdout is empty, and it prints `untagged=0 sub=no last=0` (observed).
- A stopped driver ends its role process, records the run as killed and resumes from the stored state → NEW. Today it prints `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0`, then `resumed: exit=2 ready-for-triage calls=` (observed).
- The driver marks its own store calls, never its roles', and passes a configured effort → NEW. Today it prints `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` (observed). `marked=2` is argparse's refusal.
- The Workflow scripts still take both fixtures to the end of their routes → REGRESSION. It prints `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` today (observed), and must after each part.
- The documents describe the driver → NEW. Today it prints `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean` (observed).

## PR description (the implementer's output)

Sub-ticket: T-0040.2 (T-0040.B, the build phase). Parent spec: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md`
Branch: `factory/T-0040.2`, head `4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8`, base `2ad4d8c5288474b823d4571ba03de82a706eabdf`
Commit: 4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8

## What changed

`factory drive TICKET` can now take an approved ticket through the build, so the operator no longer needs the build Workflow script and its clerk for that half. The build is the half of the pipeline that splits an approved spec into sub-tickets and implements, checks and merges each one. Before this change the driver refused any ticket in a build state. Part A's interim refusal is gone, and so is its `factory:` marker.

All changes are in `factory/drive.py`, plus one new test file. They follow part B, items 1 to 4 of design.md.

1. **Build routing** (`Driver.build` and `Driver.build_one`). This is a branch-for-branch port of `factory/workflows/build.js` from `// --- start`, with its `buildOne`. It issues the same store commands with the same arguments, and makes the same transitions with `--by workflow`. Its park reasons are the same.
   - Plan phase: `plan whole-spec`, either the planner-skipped step or the planner run, then `spec tasks`, `plan add` and `subticket add`, then `-> planned`.
   - Build phase: the `ready-implementers` loop. That includes the one-time `subticket add` for a parent planned with no sub-tickets, the park when a human closed a sub-ticket, `resumable` sub-tickets, the `remaining` result, then `parent-check`.
   - Close phase: `parent-check` again with its `reuse`, the parent-close verifier, `archive`, then `-> closed`.
   - `build_one`: the implementer, then `ticket head` with `merge_refused`, then `-> checks-in-flight` with `pr:init`. It then picks which checkers run: both after an implementer run, otherwise those `results show` lists as missing, with `ci` meaning the verifier. Next come `results record` with the head (and `--killed` for a KILLED run), then `ticket join` and its five decisions: merge, revise, conflict, wait and park. After a merge decision it runs `merge`. A `BLOCKED ` merge refusal is parked verbatim. Any other refusal asks the join a second time.
   - `run_once` now also returns the run's `outputPath`, which `results record --output` needs.
2. **Concurrency.** A head's two checkers, the reviewer and the verifier, run through `asyncio.gather` inside a small helper, `_all`. Both finish and record their results before the join. If either checker ends with no result, the sub-ticket's pass ends only after both have returned, as `parallel()` does in the script. The sub-tickets of one `ready-implementers` answer run as tasks behind an `asyncio.Semaphore(--parallel)`, which defaults to 2. The driver waits for all of them, then asks `ready-implementers` again.
   - Why `_all` and not a bare `gather`: if one awaitable raises, `_all` cancels the others and waits for them before re-raising. Without that, a sibling task could still be routing while the stop sequence finishes its run as KILLED, and its later `run finish` would be refused and would park the ticket. That would break the rule that a stop parks nothing. Rejected: `asyncio.TaskGroup`. It cancels the same way, but it wraps the error in an `ExceptionGroup`, which hides the real message in the driver's `error` result.
3. **Progress.** `step()` now names each sub-ticket with that sub-ticket's own title, which `build_one` reads from `ticket show --json`. `transition()` gains an optional `ticket` argument, so a sub-ticket's transitions print under the sub-ticket. Before this change it always moved the parent. `step()` also joins a multi-line step text onto one line. A park reason built from stderr ends in a newline, and in the build route this printed a blank, untagged stdout line, so "Build step lines name the sub-ticket they concern" printed `untagged=1` before this fix. The reason stored with the ticket is unchanged, so the records still match the script's. The status file's `running` list already held every role run in flight with its ticket. It now holds both checkers of each sub-ticket in flight.
4. **Phase.** The driver now picks build for `--phase build`, or, without `--phase`, for a stored state of `ready-for-planner`, `planned` or `ready-for-parent-verify`. The phase it picks is written to the status file.

Callers (coding standard rule 2): `step`, `transition` and `run_once` are called only inside `factory/drive.py`. `factory/cli.py` calls only `drive.drive`. A's intake calls keep working unchanged: `transition(to, round_op)` still defaults to the parent.

## Acceptance results

I extracted the GIVEN blocks verbatim and ran them once, with `TMPDIR` set to this run's scratch directory:
- `t0023-*` from `openspec/specs/human-resolution/spec.md`;
- `t0024-*` from `openspec/specs/live-store-guard/spec.md`;
- the six `t0040-*` files from `openspec/changes/T-0040/specs/build-dispatch/spec.md`, whose block matches v4's exactly by `diff`.

Every WHEN command below was copied from that change spec and ran unchanged, from the worktree, under bash, through the running-code wrapper, with the same `TMPDIR`. The full "after" log is `scratch/acceptance-after.txt`.

| Scenario | Kind | Before (2ad4d8c) | After (4bfedc7) |
|---|---|---|---|
| The driver takes the build fixtures through the same routes as the build script | NEW | `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=6/6 drive=0/0 differ`, `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=1/1 drive=0/0 differ` | `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same` |
| Each role runs as one claude process with its prompt, model and tool limits | NEW | `critic ok`, `spec_writer ok`, `triage ok`, then a blank line | `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok` |
| The checkers run at once, and sub-tickets up to the parallel limit | NEW | `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, `parallel=default: calls=0 max=0 checks-in-flight checks-in-flight` | `parallel=1: calls=4 max=2 parked parked`, `parallel=default: calls=4 max=4 parked parked` |
| Build step lines name the sub-ticket they concern | NEW | `untagged=0 sub=no last=0` | `untagged=0 sub=yes last=1` |
| The driver takes the intake fixtures through the same routes as the intake script | REGRESSION | not run | `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` |
| Each role run records its process's reply | REGRESSION | not run | `triage=ok spec_writer=ok critic=ok` |
| Every intake step line names its ticket and title, and the status file shows the end | REGRESSION | not run | `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` |
| A stopped driver ends its role process, records the run as killed and resumes from the stored state | REGRESSION | not run | `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, `resumed: exit=0 closed calls=2` |
| The driver marks its own store calls, never its roles', and passes a configured effort | REGRESSION | not run | `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` |
| The Workflow scripts still take both fixtures to the end of their routes | REGRESSION | not run | `T-0001.1 merged T-0001 parked`, `T-0001 awaiting-spec-gate` |

Every "after" line is exactly what the sub-ticket's Acceptance and the parent's scenarios expect. The "before" lines match the "today" figures in verification.md. The one exception is the claude-process check, whose intake half A had already made pass.

Gates. I ran each one exactly as written, from the worktree, on 4bfedc7:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `520 passed in 453.62s (0:07:33)` and exited 0. That is A's 511 plus the 9 new tests. This run is also the intermediate check that the suite passes with `tests/factory/test_drive_build.py`.

`ruff check` with default rules found nothing in the two changed files. `ruff` is not in this repo's environment, so I ran a copy already installed on the machine. It is not a gate command here.

## Tests added and changed

Added: `tests/factory/test_drive_build.py`, 9 tests. Each test drives `bin/factory` as a black box on part A's `Store`, which the file imports from `test_drive.py` as the sub-ticket allows. The store is taken past the spec gate, and a scratch git repository serves as the target. The file has its own Python stand-in `claude`, which extends A's in two ways:
- a written output carries a `Commit:` line with the run's head, and a verifier's output also carries `Gate suite: PASS`, so that `results record` accepts the checkers' outputs;
- each call logs its start and end time, so a test can count the role processes that ran at once.

The tests:
- the four build routes of the parity table: merge then the parent-close verifier, review rounds to the limit, two empty reviews, and a BLOCKED implementer reached with no `--phase`;
- a failed reviewer, after which the verifier still finishes and records its result before the sub-ticket parks (the gather semantics);
- the implementer's `Edit` tool, its worktree `Edit` rule and `--add-dir` in a real build, and the checkers' rules: no `Edit` tool, and `Edit` rules on their own run only;
- the `--parallel` bound: at most 2 role processes at once under `--parallel 1`, and 4 at the default;
- step lines that name `T-0001.1 "One"` and `T-0001.2 "Two"`, and a status file whose `running` list shows all four checker runs with their sub-tickets;
- a SIGTERM while both checkers run: both runs are recorded KILLED, the sub-ticket stays `checks-in-flight` and unparked, and a re-run with no `--phase` re-runs both checkers and merges.

I wrote the driver code before these tests, not after, so the order of process step 3 was not kept. To check the tests still discriminate, I swapped base `factory/drive.py` back in. The first 8 tests all failed (`8 failed`), and with the new code they all pass. I added the stop test after that check and did not re-run it against base. On base, the driver refuses every build state, so it cannot pass there.

Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- `factory:` markers added: none. One was removed: A's interim build refusal at the old `factory/drive.py:390`.
- No test reaches `_all`'s path for a raised exception, where it cancels the sibling tasks. Only outer cancellation (the stop test) and normal completion are exercised.
- These branches of the port are untested in the suite and were not reached by the acceptance fixtures: the planner route (`ESCALATE`, unknown status, `spec tasks`, `plan add` and `subticket add` refusals), the one-time recorded-plan `subticket add`, the closed-sub-ticket park, `merge_refused` and conflict runs, a `BLOCKED ` merge refusal, a merge refusal that asks the join again, `reuse` at parent close, and `archive` success leading to `closed`. Each is a line-for-line port of the script, and I read each against `build.js`, but none has run.
- Two small departures from the script, where the script would misbehave:
  - When `ticket join` succeeds with no `reason`, the driver parks with an empty reason. In the script, `park()` would throw on `undefined.replace`.
  - The `join:` step line prints an empty reason in place of `undefined`.
  Neither path is reachable with the current `ticket join`, which always returns a reason with each decision.
- `step()` now joins a multi-line step text onto one line. This also changes part A's intake step lines when a park reason carries stderr's trailing newline. No intake scenario or test depends on the old blank line.
- A store call captures `sys.stdout` and `sys.stderr` only. `gitops.head_contains` runs `git merge-base --is-ancestor` without capturing, so a git error there would reach the driver's stderr, not its stdout. Stdout's line format is not at risk. I saw no such output in any run.
- The stand-in role processes return almost at once, so the bound under `--parallel` is tested only with role processes that sleep. Real concurrent `claude -p` processes are untested, as the spec's Risk section says (Operator step 2).

## Out-of-scope observations

- The README is unchanged. The parent assigns the documents, including the README's "Starting a run" and "Built" entries, to part C.
- The fixture files the scenarios write live under this run's scratch directory (`TMPDIR=<scratch>/tmp`), so they cannot collide with another run's copies in the shared `$TMPDIR`.

Protected paths touched: `factory/drive.py`, under `factory/**`. The sub-ticket declares it.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION scenario printed exactly its expected lines on 4bfedc7, and both gates passed. Several rare build branches are ported but have never run (Known gaps).
ESCALATIONS: none

## Diff `2ad4d8c5288474b823d4571ba03de82a706eabdf...4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8`

diff --git a/factory/drive.py b/factory/drive.py
index d8168f8..cd08f8d 100644
--- a/factory/drive.py
+++ b/factory/drive.py
@@ -6,16 +6,17 @@ fence and the harness lock run as they do for `bin/factory`. Every role runs as
 `claude -p` process from its run directory, with its role's prompt, model, effort and tool limits;
 its reply is kept as `runs/<id>/reply.json` and its cost recorded by `run finish --reply`.
 
-The routing is a port of factory/workflows/intake.js from `// --- start`, branch for branch: the
-same commands, transitions, round operations and park reasons, so a ticket driven here leaves the
-same records the script leaves. Like the script, the driver stops at the spec gate.
-
-One stdout line per step, `<ticket id> "<title>": <step>`, then the result as one JSON object. The
-store's `drive/<ticket>.yaml` is a live view of this process (git ignores it). SIGINT or SIGTERM
-ends the role processes, records their runs KILLED and parks nothing: running `factory drive`
-again resumes from the stored state.
-
-Part A of T-0040 builds the intake phase only: the build phase (build.js) is refused.
+The routing is a port of factory/workflows/intake.js and factory/workflows/build.js from
+`// --- start` (build.js with its buildOne), branch for branch: the same commands, transitions,
+round operations and park reasons, so a ticket driven here leaves the same records the script
+leaves. Like the intake script, the driver stops at the spec gate. A head's two checkers run at
+once, and ready sub-tickets build at once up to `--parallel N`.
+
+One stdout line per step, `<ticket id> "<title>": <step>`, naming the ticket the step concerns (a
+sub-ticket's steps name the sub-ticket), then the result as one JSON object. The store's
+`drive/<ticket>.yaml` is a live view of this process (git ignores it). SIGINT or SIGTERM ends the
+role processes, records their runs KILLED and parks nothing: running `factory drive` again
+resumes from the stored state.
 """
 from __future__ import annotations
 
@@ -24,12 +25,12 @@ import contextlib
 import io
 import json
 import os
+import re
 import signal
 import tempfile
 from pathlib import Path
 
 from factory import cli, store
-from factory.store import Refused
 
 INTAKE_STATES = ("ready-for-triage", "ready-for-spec-writer", "ready-for-critic")
 BUILD_STATES = ("ready-for-planner", "planned", "ready-for-parent-verify")
@@ -116,12 +117,14 @@ class Driver:
     def __init__(self, a, root: Path, cfg: dict):
         self.ticket = a.ticket
         self.phase = a.phase
+        self.parallel = a.parallel
         self.prompt_mode = a.prompt_mode
         self.root = root
         self.effort = cfg.get("effort") or {}
         self.models: dict = {}
         self.max_spec = 2
         self.title = ""
+        self.titles: dict[str, str] = {}  # sub-ticket id -> title, read by build_one
         self.running: dict[str, dict] = {}  # run id -> {run, role, ticket, pid}: this driver's runs in flight
         self.procs: dict[str, asyncio.subprocess.Process] = {}
         self.stopped: signal.Signals | None = None
@@ -136,7 +139,9 @@ class Driver:
         store.write_yaml(self.status_path, self.status)
 
     def step(self, text: str, ticket: str | None = None) -> None:
-        line = f'{ticket or self.ticket} "{self.title}": {text}'
+        ticket = ticket or self.ticket
+        text = " ".join(ln.strip() for ln in text.strip().splitlines())  # a park reason may end in stderr's newline
+        line = f'{ticket} "{self.titles.get(ticket, self.title)}": {text}'
         print(line, flush=True)
         self.write_status(last=line)
 
@@ -149,10 +154,11 @@ class Driver:
         call(*argv)
         self.step(f"parked: {reason}", ticket)
 
-    def transition(self, to: str, round_op: str | None = None) -> dict:
-        argv = ["ticket", "transition", self.ticket, "--to", to, "--by", "workflow"]
+    def transition(self, to: str, round_op: str | None = None, ticket: str | None = None) -> dict:
+        ticket = ticket or self.ticket
+        argv = ["ticket", "transition", ticket, "--to", to, "--by", "workflow"]
         res = call(*argv, *(["--round", round_op] if round_op else []))
-        self.step(f"-> {to}" if res["ok"] else f"-> {to} refused: {res.get('stderr', '').strip()}")
+        self.step(f"-> {to}" if res["ok"] else f"-> {to} refused: {res.get('stderr', '').strip()}", ticket)
         return res
 
     # ----- role runs ----------------------------------------------------------------------
@@ -232,7 +238,7 @@ class Driver:
             call("run", "last-message", rid, "--text=" + said[-4000:])
         esc = fin.get("escalations") or []
         self.step(f"{role} {rid}: {fin['status']}" + (f" (+{len(esc)} escalations)" if esc else ""), ticket)
-        return {"runId": rid, "status": fin["status"], "escalations": esc}
+        return {"runId": rid, "status": fin["status"], "escalations": esc, "outputPath": os.path.join(run, "output.md")}
 
     # ----- intake: factory/workflows/intake.js from `// --- start` ---------------------------
 
@@ -310,11 +316,218 @@ class Driver:
             self.park(T, "max rounds", [c["runId"]])
             return {**parked, "rounds": rnd, "reason": "max rounds"}
 
+    # ----- build: factory/workflows/build.js from `// --- start` ----------------------------
+
+    async def build(self, state: str) -> dict:
+        T = self.ticket
+        parked = {"ticket": T, "state": "parked"}
+        if state == "ready-for-planner":  # phase 1: Plan
+            # A spec that needs one sub-ticket becomes it without a planner run; the harness decides which.
+            whole = call("plan", "whole-spec", T)
+            if not whole["ok"]:
+                self.park(T, f"harness-bug: plan whole-spec: {whole.get('stderr') or ''}", [])
+                return parked
+            if whole.get("planner") == "skipped":
+                self.step(f"planner skipped ({whole.get('reason')}); one sub-ticket from the whole spec")
+            else:
+                p = await self.run_role("planner", T)
+                if not p:
+                    return parked
+                if p["status"] == "ESCALATE":
+                    self.park(T, "ESCALATE from planner", [p["runId"]])
+                    return parked
+                if p["status"] != "PLANNED":
+                    self.park(T, f"harness-bug: unknown STATUS {p['status']} from planner", [p["runId"]])
+                    return parked
+                for what, argv in (("spec tasks", ("spec", "tasks", T, "--run", p["runId"])),
+                                   ("plan add", ("plan", "add", T, "--from-run", p["runId"])),
+                                   ("subticket add", ("subticket", "add", T, "--run", p["runId"]))):
+                    res = call(*argv)
+                    if not res["ok"]:
+                        self.park(T, f"harness-bug: {what}: {res.get('stderr') or ''}", [p["runId"]])
+                        return parked
+            self.transition("planned")
+            state = "planned"
+        if state == "planned":  # phase 2: Build, while any sub-ticket is not merged, parked or closed
+            sem = asyncio.Semaphore(self.parallel)
+
+            async def bounded(st: str) -> None:
+                async with sem:
+                    await self.build_one(st)
+
+            first = True
+            while True:
+                ready = call("ticket", "ready-implementers", T)
+                if not ready["ok"]:
+                    self.park(T, f"harness-bug: ready-implementers: {ready.get('stderr') or ''}", [])
+                    return parked
+                # A parent planned with no sub-tickets (e.g. by an older intake): create them once from
+                # the planner run its recorded plan names, or park the parent saying why.
+                if first and ready.get("subtickets") == []:
+                    first = False
+                    made = call("subticket", "add", T)
+                    if not made["ok"]:
+                        self.park(T, "no sub-tickets, and none could be created from the recorded plan: "
+                                     f"{made.get('stderr') or ''}", [])
+                        return parked
+                    self.step(f"created {len(made.get('subtickets') or [])} sub-ticket(s) from the recorded plan")
+                    continue
+                first = False
+                # A sub-ticket the human closed parks the parent: amend the spec and re-plan, or close.
+                if ready.get("closed"):
+                    self.park(T, f"sub-ticket closed by a human: {', '.join(ready['closed'])}", [])
+                    return parked
+                todo = ready["ready"] + (ready.get("resumable") or [])
+                if not todo:
+                    if ready["remaining"]:
+                        self.step(f"{len(ready['remaining'])} sub-ticket(s) parked or waiting on a human")
+                        return {"ticket": T, "state": "planned", "remaining": ready["remaining"]}
+                    break
+                if ready.get("resumable"):
+                    self.step(f"resuming {', '.join(ready['resumable'])} from its stored state")
+                await _all(bounded(st) for st in todo)
+            pc = call("ticket", "parent-check", T)
+            if not pc["ok"]:
+                self.park(T, f"parent-check refused: {pc.get('stderr') or ''}", [])
+                return parked
+            if pc.get("state") != "ready-for-parent-verify":
+                return {"ticket": T, "state": pc.get("state") or "planned"}
+            state = "ready-for-parent-verify"
+        if state == "ready-for-parent-verify":  # phase 3: Close
+            # Asked again here: a resumed build may arrive already in ready-for-parent-verify. `reuse`
+            # names a single sub-ticket's VERIFIED run that stands for the parent-close run.
+            pc = call("ticket", "parent-check", T)
+            rid = pc.get("reuse") if pc["ok"] else None
+            if rid:
+                self.step(f"sub-ticket verifier run {rid} stands for the parent-close run; no new verifier run")
+            else:
+                v = await self.run_role("verifier", T)
+                if not v:
+                    return parked
+                if v["status"] != "VERIFIED":
+                    self.park(T, f"{v['status']} from parent-close verifier", [v["runId"]])
+                    return parked
+                rid = v["runId"]
+            arch = call("archive", T)
+            if not arch["ok"]:
+                self.park(T, f"archive: {arch.get('stderr') or ''}", [rid])
+                return parked
+            self.transition("closed")
+            return {"ticket": T, "state": "closed", "archived_to": arch.get("archived_to")}
+        return {"ticket": T, "state": state, "note": "nothing to dispatch from this state"}
+
+    async def build_one(self, st: str) -> None:
+        """buildOne: one sub-ticket through the PR loop. The routing after the checkers is `ticket
+        join`'s decision: merge, revise, conflict, wait or park; this only carries it out."""
+        while True:
+            show = call("ticket", "show", st, "--json")
+            if not show["ok"]:
+                return
+            self.titles[st] = show["title"]
+            implemented = show["state"] == "ready-for-implementer"
+            if implemented:
+                impl = await self.run_role("implementer", st)
+                if not impl:
+                    return
+                if impl["status"] == "BLOCKED":
+                    self.park(st, "BLOCKED from implementer", [impl["runId"]])
+                    return
+                if impl["status"] != "READY-FOR-REVIEW":
+                    self.park(st, f"harness-bug: unknown STATUS {impl['status']} from implementer", [impl["runId"]])
+                    return
+                moved = call("ticket", "head", st)
+                if not moved["ok"]:
+                    self.park(st, f"harness-bug: ticket head: {moved.get('stderr') or ''}", [impl["runId"]])
+                    return
+                if moved.get("merge_refused"):
+                    # A conflict run that did not merge the integration branch in: no point checking that head.
+                    j = call("ticket", "join", st)
+                    if j["ok"] and j.get("decision") == "conflict":
+                        continue
+                    self.park(st, (j.get("reason") or "") if j["ok"] else f"harness-bug: join: {j.get('stderr') or ''}",
+                              [impl["runId"]])
+                    return
+                tr = self.transition("checks-in-flight", "pr:init", st)
+                if not tr["ok"]:
+                    self.park(st, f"harness-bug: transition to checks: {tr.get('stderr') or ''}", [impl["runId"]])
+                    return
+            elif show["state"] != "checks-in-flight":
+                return  # parked, merged, closed or waiting: nothing for this loop to do
+            # The checkers on the same head, at once; each result recorded against that head. After an
+            # implementer run both run. Entered at checks-in-flight (a redispatch or a resumed
+            # sub-ticket), only the checkers with no row on this head run; the verifier writes the ci row too.
+            head_now = call("ticket", "head", st)
+            sha = head_now.get("head") if head_now["ok"] else None
+            if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
+                self.park(st, f"harness-bug: no head for the checkers: {head_now.get('stderr') or ''}", [])
+                return
+            roles = list(CHECKERS)
+            if not implemented:
+                rows = call("results", "show", st)
+                if not rows["ok"]:
+                    self.park(st, f"harness-bug: results show: {rows.get('stderr') or ''}", [])
+                    return
+                missing = rows.get("missing") or []
+                roles = [r for r in roles if r in missing or (r == "verifier" and "ci" in missing)]
+
+            async def check(role: str) -> dict | None:
+                r = await self.run_role(role, st)
+                if not r:
+                    return None
+                rec = call("results", "record", st, "--head", sha, "--role", role, "--output", r["outputPath"],
+                           "--run", r["runId"], *(["--killed"] if r["status"] == "KILLED" else []))
+                if not rec["ok"]:
+                    self.park(st, f"harness-bug: results record {role}: {rec.get('stderr') or ''}", [r["runId"]])
+                    return None
+                return r
+
+            checked = await _all(check(role) for role in roles)
+            if any(r is None for r in checked):
+                return
+            outs = [r["runId"] for r in checked]
+            join = call("ticket", "join", st)
+            if not join["ok"]:
+                self.park(st, f"harness-bug: join: {join.get('stderr') or ''}", outs)
+                return
+            decision, reason = join.get("decision"), join.get("reason") or ""
+            self.step(f"join: {decision} ({reason})", st)
+            if decision == "merge":
+                self.transition("ready-for-merge", None, st)
+                m = call("merge", st)
+                if m["ok"]:
+                    self.step(f"merged: {m.get('main_after')}", st)
+                    return
+                # A refusal that starts `BLOCKED ` is the merge gate blocking the merge (an undeclared
+                # protected path): parked verbatim, for `resolve --accept-paths` or `resolve --ruling`.
+                if isinstance(m.get("error"), str) and m["error"].startswith("BLOCKED "):
+                    self.park(st, m["error"], outs)
+                    return
+                # The gate refused. Ask the join again: a moved integration branch is a conflict run.
+                again = call("ticket", "join", st)
+                if again["ok"] and again.get("decision") == "conflict":
+                    self.transition("ready-for-implementer", None, st)
+                    continue
+                self.park(st, (again.get("reason") or "") if again["ok"] and again.get("decision") == "park"
+                          else f"harness-bug: merge: {m.get('stderr') or ''}", outs)
+                return
+            if decision == "revise":
+                tr = self.transition("ready-for-implementer", join.get("round_op"), st)
+                if not tr["ok"]:
+                    self.park(st, f"harness-bug: round increment refused: {tr.get('stderr') or ''}", outs)
+                    return
+                continue
+            if decision == "conflict":
+                self.transition("ready-for-implementer", None, st)
+                continue
+            # 'park', or 'wait' (a row is missing after both checkers reported: a harness bug, not a red round)
+            self.park(st, f"harness-bug: {reason}" if decision == "wait" else reason, outs)
+            return
+
     # ----- start, stop, end ------------------------------------------------------------------
 
     async def run(self, state: str, rnd: int) -> int:
         loop = asyncio.get_running_loop()
-        route = asyncio.ensure_future(self.intake(state, rnd))
+        route = asyncio.ensure_future(self.build(state) if self.phase == "build" else self.intake(state, rnd))
         for sig in (signal.SIGINT, signal.SIGTERM):
             loop.add_signal_handler(sig, self._on_signal, sig, route)
         try:
@@ -366,6 +579,20 @@ class Driver:
         print(json.dumps(result, ensure_ascii=False), flush=True)
 
 
+async def _all(aws) -> list:
+    """asyncio.gather, as the scripts' parallel(): every awaitable finishes before it returns. If
+    one raises, the rest are cancelled and waited for before the error goes on, so no role run is
+    still being routed while the stop sequence runs."""
+    tasks = [asyncio.ensure_future(a) for a in aws]
+    try:
+        return await asyncio.gather(*tasks)
+    except BaseException:
+        for t in tasks:
+            t.cancel()
+        await asyncio.gather(*tasks, return_exceptions=True)
+        raise
+
+
 def _spec_round(tr: dict, rnd: int) -> int:
     spec = (tr.get("round") or {}).get("spec")
     return spec if isinstance(spec, int) and not isinstance(spec, bool) else rnd
@@ -385,13 +612,9 @@ def drive(a, root: Path, cfg: dict) -> None:
     if not show["ok"]:
         _fail({"ticket": d.ticket, "error": f"no such ticket: {show.get('stderr') or ''}"})
     state = show["state"]
-    phase = d.phase or ("intake" if state in INTAKE_STATES else "build" if state in BUILD_STATES else None)
-    if phase == "build":
-        # factory: interim until T-0040 part B ports build.js; refused before anything is written.
-        raise Refused(f"{d.ticket} is {state}: the build phase of factory drive is not built yet; "
-                      "run the build Workflow script")
+    d.phase = d.phase or ("intake" if state in INTAKE_STATES else "build" if state in BUILD_STATES else None)
     d.title = show["title"]
-    d.status = {"ticket": d.ticket, "title": d.title, "phase": phase, "pid": os.getpid(), "started": store.now(),
+    d.status = {"ticket": d.ticket, "title": d.title, "phase": d.phase, "pid": os.getpid(), "started": store.now(),
                 "updated": None, "running": [], "last": None, "ended": None}
     d.write_status()
     code = asyncio.run(d.run(state, (show.get("round") or {}).get("spec") or 0))
diff --git a/tests/factory/test_drive_build.py b/tests/factory/test_drive_build.py
new file mode 100644
index 0000000..240c6f0
--- /dev/null
+++ b/tests/factory/test_drive_build.py
@@ -0,0 +1,244 @@
+"""`factory drive`, part B (T-0040): the build phase, a port of factory/workflows/build.js.
+
+Black-box through `bin/factory`, on part A's throwaway store (test_drive.Store) taken past the spec
+gate, with a scratch git repository as the target. The stand-in `claude` here extends part A's: a
+written output carries a `Commit:` line naming the run's head, and a verifier's a passing gate
+suite, so the checkers' results can be recorded; each call also appends "<start> <end>" to
+<log>.times, so a test can count the role processes that ran at once.
+"""
+from __future__ import annotations
+
+import json
+import os
+import signal
+import subprocess
+import sys
+import tempfile
+import time
+
+import yaml
+
+from .test_drive import BIN, REPO, Store
+
+STANDIN = '''#!{python}
+import json, os, pathlib, re, sys, time
+t0 = time.time()
+cwd = pathlib.Path.cwd(); log = pathlib.Path(os.environ["STANDIN_LOG"])
+with log.open("a") as f:
+    f.write(json.dumps({{"argv": sys.argv[1:], "cwd": str(cwd), "pid": os.getpid(),
+                        "dispatch": os.environ.get("FACTORY_DISPATCH")}}) + "\\n")
+role = cwd.name.split("-", 2)[2]
+plays = json.loads(os.environ.get("STANDIN_PLAYS") or "{{}}").get(role) or [{{"say": ""}}]
+nf = log.with_name(log.name + ".n-" + role); n = int(nf.read_text()) + 1 if nf.exists() else 1
+nf.write_text(str(n)); p = plays[min(n, len(plays)) - 1]
+time.sleep(p.get("sleep", 0))
+text, err = p.get("say", ""), "fail" in p
+if "write" in p:
+    head = re.search(r"^head: '?([0-9a-f]{{40}})", (cwd / "meta.yaml").read_text(), re.M)
+    text = (("Commit: %s\\n" % head[1]) if head else "") + ("Gate suite: PASS\\n" if role == "verifier" else "")
+    text += "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
+    (cwd / "output.md").write_text(text)
+elif err:
+    text = p["fail"]
+with log.with_name(log.name + ".times").open("a") as f:
+    f.write("%f %f\\n" % (t0, time.time()))
+print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
+                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
+sys.exit(1 if err else 0)
+'''
+
+OK_PLAYS = {"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}],
+            "verifier": [{"write": "VERIFIED"}]}
+
+
+class BuildStore(Store):
+    """Part A's store, with T-0001 approved at the spec gate (ready for its planner; a one-section
+    spec, so the planner is skipped), a scratch git repository as the target, and this file's
+    stand-in `claude`."""
+
+    def __init__(self, tmp_path):
+        super().__init__(tmp_path)
+        (tmp_path / "bin" / "claude").write_text(STANDIN.format(python=sys.executable))
+        spec = tmp_path / "spec.md"
+        spec.write_text("## Problem\nx\n")
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+        self.ok("spec", "add", "T-0001", "--file", str(spec))
+        self.ok("ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+        self.ok("ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+        self.ok("approve-spec", "T-0001")
+        self.target = tmp_path / "target"
+        self.git("init", "-q", "-b", "main", str(self.target), cwd=tmp_path)
+        self.git("commit", "-q", "--allow-empty", "-m", "init")
+        self.env.update(FACTORY_REPO=str(self.target), FACTORY_INTEGRATION_BRANCH="main")
+
+    def git(self, *argv: str, cwd=None) -> str:
+        cp = subprocess.run(["git", "-c", "user.email=f@x", "-c", "user.name=f", *argv], cwd=cwd or self.target,
+                            capture_output=True, text=True, check=True)
+        return cp.stdout.strip()
+
+    def two_subtickets_at_checks(self) -> None:
+        """T-0001 planned into T-0001.1 and T-0001.2, independent, each at checks-in-flight on its own commit."""
+        plan = self.tmp / "plan.md"
+        plan.write_text("ST-1 / One\nDepends on: none\nParallel-safe: yes\n\n"
+                        "ST-2 / Two\nDepends on: none\nParallel-safe: yes\n")
+        self.ok("subticket", "add", "T-0001", "--file", str(plan))
+        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+        for i in (1, 2):
+            self.git("checkout", "-qb", f"factory/T-0001.{i}", "main")
+            (self.target / f"f{i}.txt").write_text(f"{i}\n")
+            self.git("add", f"f{i}.txt")
+            self.git("commit", "-qm", f"w{i}")
+            self.git("checkout", "-q", "main")
+            head = self.git("rev-parse", f"factory/T-0001.{i}")
+            self.ok("ticket", "set", f"T-0001.{i}", "status=checks-in-flight", f"branch=factory/T-0001.{i}",
+                    f"head={head}")
+
+    def most_at_once(self) -> int:
+        spans = [tuple(map(float, ln.split())) for ln in (self.log.parent / (self.log.name + ".times"))
+                 .read_text().splitlines()]
+        return max([sum(a <= s < b for a, b in spans) for s, _ in spans] or [0])
+
+
+def roles_and_statuses(s: Store) -> list[tuple[str, str, str]]:
+    return [(m["role"], m["ticket"], m["status"]) for m in s.runs()]
+
+
+def test_an_approved_head_merges_then_the_parent_close_verifier_runs(tmp_path):
+    s = BuildStore(tmp_path)
+    cp, res = s.drive(OK_PLAYS, "--phase", "build")
+    assert cp.returncode == 0, cp.stderr
+    assert s.ticket("T-0001.1")["status"] == "merged"
+    assert roles_and_statuses(s) == [("implementer", "T-0001.1", "READY-FOR-REVIEW"),
+                                     ("reviewer", "T-0001.1", "APPROVE"), ("verifier", "T-0001.1", "VERIFIED"),
+                                     ("verifier", "T-0001", "VERIFIED")]
+    # The fixture has no spec store, so the archive is refused and the parent parks, as under build.js.
+    assert res == {"ticket": "T-0001", "state": "parked", "ok": True}
+    assert s.ticket()["parked"]["reason"].startswith("archive: ")
+
+
+def test_a_reviewer_still_asking_for_changes_at_the_round_limit_parks_the_subticket(tmp_path):
+    s = BuildStore(tmp_path)
+    cp, res = s.drive({**OK_PLAYS, "reviewer": [{"write": "REQUEST-CHANGES"}]}, "--phase", "build")
+    assert cp.returncode == 0, cp.stderr
+    assert res == {"ticket": "T-0001", "state": "planned", "ok": True}
+    assert s.ticket("T-0001.1")["status"] == "parked"
+    assert [r for r, _, _ in roles_and_statuses(s)] == ["implementer", "reviewer", "verifier"] * 2
+    assert s.ticket("T-0001.1")["round"]["pr"] == 2
+
+
+def test_two_empty_reviews_park_the_subticket_after_the_verifier_has_recorded(tmp_path):
+    s = BuildStore(tmp_path)
+    cp, res = s.drive({**OK_PLAYS, "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]},
+                      "--phase", "build")
+    assert cp.returncode == 0, cp.stderr
+    assert res["state"] == "planned"
+    assert s.ticket("T-0001.1")["parked"]["reason"] == "EMPTY-OUTPUT from reviewer"
+    assert sorted(roles_and_statuses(s)) == sorted([
+        ("implementer", "T-0001.1", "READY-FOR-REVIEW"), ("reviewer", "T-0001.1", "EMPTY-OUTPUT"),
+        ("reviewer", "T-0001.1", "EMPTY-OUTPUT"), ("verifier", "T-0001.1", "SPEC-DEFECT")])
+
+
+def test_a_blocked_implementer_parks_its_subticket(tmp_path):
+    s = BuildStore(tmp_path)
+    cp, res = s.drive({"implementer": [{"write": "BLOCKED"}]})  # no --phase: ready-for-planner selects build
+    assert cp.returncode == 0, cp.stderr
+    assert res == {"ticket": "T-0001", "state": "planned", "ok": True}
+    assert s.ticket("T-0001.1")["parked"]["reason"] == "BLOCKED from implementer"
+    assert len(s.calls()) == 1
+
+
+def test_a_failed_checker_ends_the_pass_only_after_the_other_has_recorded(tmp_path):
+    s = BuildStore(tmp_path)
+    cp, res = s.drive({**OK_PLAYS, "reviewer": [{"fail": "usage limit reached"}],
+                       "verifier": [{"sleep": 1, "write": "VERIFIED"}]}, "--phase", "build")
+    assert cp.returncode == 0, cp.stderr
+    assert s.ticket("T-0001.1")["parked"]["reason"] == "agent call failed: reviewer: usage limit reached"
+    assert sorted(roles_and_statuses(s)) == sorted([
+        ("implementer", "T-0001.1", "READY-FOR-REVIEW"), ("reviewer", "T-0001.1", "KILLED"),
+        ("verifier", "T-0001.1", "VERIFIED")])
+    rows = [yaml.safe_load(p.read_text()) for p in s.root.glob("results/*/*.yaml")]
+    assert ("verifier", "VERIFIED") in [(r.get("role"), r.get("status")) for r in rows]
+    assert s.ticket("T-0001.1")["in_flight"] == []
+
+
+def test_the_implementer_gets_edit_and_its_worktree_and_the_checkers_only_their_run(tmp_path):
+    s = BuildStore(tmp_path)
+    cp, _ = s.drive(OK_PLAYS, "--phase", "build")
+    assert cp.returncode == 0, cp.stderr
+    tmp = os.path.realpath(tempfile.gettempdir())
+    metas = {m["run_id"]: m for m in s.runs()}
+    assert len(s.calls()) == 4
+    for c in s.calls():
+        run = os.path.realpath(c["cwd"])
+        m = metas[os.path.basename(run)]
+        opts = dict(zip(c["argv"][2::2], c["argv"][3::2]))
+        assert c["dispatch"] is None and opts["--model"] == m["model"] and opts["--permission-mode"] == "auto"
+        rules = [f"Edit(/{run}/output.md)", f"Edit(/{run}/scratch/**)", f"Edit(/{tmp}/**)"]
+        if m["role"] == "implementer":
+            wt = os.path.realpath(m["worktree"])
+            assert opts["--tools"].split(",")[-1] == "Edit" and opts["--add-dir"] == wt
+            rules.append(f"Edit(/{wt}/**)")
+        else:
+            assert "Edit" not in opts["--tools"].split(",") and "--add-dir" not in opts
+        assert [r for r in opts["--allowedTools"].split(",") if r.startswith("Edit")] == rules
+
+
+def test_the_checkers_run_at_once_and_subtickets_up_to_the_parallel_limit(tmp_path):
+    plays = {"reviewer": [{"sleep": 1.5, "write": "APPROVE"}], "verifier": [{"sleep": 1.5, "write": "SPEC-DEFECT"}]}
+    for name, extra, most in (("one", ("--parallel", "1"), 2), ("default", (), 4)):
+        (tmp_path / name).mkdir()
+        s = BuildStore(tmp_path / name)
+        s.two_subtickets_at_checks()
+        cp, res = s.drive(plays, "--phase", "build", *extra)
+        assert cp.returncode == 0, cp.stderr
+        assert len(s.calls()) == 4 and s.most_at_once() == most, name
+        assert [s.ticket(f"T-0001.{i}")["parked"]["reason"] for i in (1, 2)] == ["SPEC-DEFECT from verifier"] * 2
+
+
+def test_build_step_lines_and_the_status_file_name_the_subticket_in_flight(tmp_path):
+    s = BuildStore(tmp_path)
+    s.two_subtickets_at_checks()
+    env = {**s.env, "STANDIN_PLAYS": json.dumps({"reviewer": [{"sleep": 2, "write": "APPROVE"}],
+                                                 "verifier": [{"sleep": 2, "write": "SPEC-DEFECT"}]})}
+    p = subprocess.Popen([str(BIN), "drive", "T-0001"], stdout=subprocess.PIPE,
+                         stderr=subprocess.PIPE, text=True, env=env, cwd=REPO)
+    status = s.root / "drive" / "T-0001.yaml"
+    seen: list[tuple[str, str]] = []
+    deadline = time.monotonic() + 30
+    while p.poll() is None and time.monotonic() < deadline:
+        if status.exists():
+            running = (yaml.safe_load(status.read_text()) or {}).get("running") or []
+            if len(running) > len(seen):
+                seen = sorted((r["ticket"], r["role"]) for r in running)
+        time.sleep(0.05)
+    out, _ = p.communicate(timeout=30)
+    assert p.returncode == 0
+    assert seen == [("T-0001.1", "reviewer"), ("T-0001.1", "verifier"),
+                    ("T-0001.2", "reviewer"), ("T-0001.2", "verifier")]
+    lines = out.strip().splitlines()
+    assert all(ln.startswith(('T-0001 "Fixture": ', 'T-0001.1 "One": ', 'T-0001.2 "Two": ')) for ln in lines[:-1])
+    assert 'T-0001.2 "Two": parked: SPEC-DEFECT from verifier' in lines
+    assert json.loads(lines[-1])["state"] == "planned"
+    assert yaml.safe_load(status.read_text())["running"] == []
+
+
+def test_a_stop_during_the_checkers_kills_both_and_a_rerun_resumes_the_subticket(tmp_path):
+    s = BuildStore(tmp_path)
+    env = {**s.env, "STANDIN_PLAYS": json.dumps({**OK_PLAYS, "reviewer": [{"sleep": 60, "write": "APPROVE"}],
+                                                 "verifier": [{"sleep": 60, "write": "VERIFIED"}]})}
+    p = subprocess.Popen([str(BIN), "drive", "T-0001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
+                         text=True, env=env, cwd=REPO)
+    deadline = time.monotonic() + 30
+    while time.monotonic() < deadline and len(s.calls()) < 3:
+        time.sleep(0.05)
+    time.sleep(0.5)
+    p.send_signal(signal.SIGTERM)
+    out, _ = p.communicate(timeout=30)
+    assert p.returncode == 128 + signal.SIGTERM
+    assert json.loads(out.strip().splitlines()[-1]) == {"ok": False, "ticket": "T-0001", "stopped": "SIGTERM"}
+    assert sorted(roles_and_statuses(s))[1:] == [("reviewer", "T-0001.1", "KILLED"), ("verifier", "T-0001.1", "KILLED")]
+    sub = s.ticket("T-0001.1")
+    assert (sub["status"], sub["in_flight"], sub["parked"]) == ("checks-in-flight", [], None)
+    cp, res = s.drive(OK_PLAYS)  # no --phase: planned selects build; both checkers re-run on the same head
+    assert cp.returncode == 0, cp.stderr
+    assert s.ticket("T-0001.1")["status"] == "merged" and len(s.calls()) == 6

## Human ruling

Ruling (Green, harness owner), 2026-10-10, on the harness's spec-drift park.

Not drift. `tests/factory/test_drive.py` was created by your own sibling's merge (T-0040.1, merge 2ad4d8c52), as the plan intends: part A creates it, and your sub-ticket already says you may import its stand-in `claude` helper. No spec change is needed. Build part B as the sub-ticket says. The drift check's false positive on a sibling's merge is filed as a harness bug.
