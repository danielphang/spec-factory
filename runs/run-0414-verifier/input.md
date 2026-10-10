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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0414-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0414-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0414-verifier/wt` (branch `factory/T-0040.3`, base `18fbe88ba88be7f2ae2dbebca09586bd25caf50d`, head `0e99ddad7eb10387369fac62286f8520fd6a1a67`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0040.3

### T-0040.C / Documents
Depends on: T-0040.A, T-0040.B
Parallel-safe: no (it documents what A and B build, so it runs after both)

Parent: T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part C, items 1 to 4 of design.md:
- README:
  - a how-to for `factory drive` under "Starting a run";
  - a row for the role processes under "What depends on Claude Code";
  - a bullet for the driver under **Built**, ending "It is tested, and has not yet run a real ticket";
  - the **Not built** "Per-role effort settings" bullet removed, with its replacement under **Built**;
  - a `drive/<ticket>.yaml` row in the store's file table;
  - the "Store records" row updated;
  - the status date bumped, and any quoted figure re-derived, as "Maintaining this page" requires.
- `docs/design.md`: piece 2, the fence paragraph, and "Running on another agent host".
- `dev/build-harness.spec.md`: R3, R6 (keep "nor `dontAsk`"), part H and I.4.
- `docs/changelog.md`: one entry at the next free number, which is 67 today, placed before "Declined:".

Do not change any prompt block in `docs/design.md`. Its `docs/prompts/` copy is protected and the parent does not declare it. If a needed edit falls inside a prompt block, escalate.

Acceptance:
- NEW. "The documents describe the driver".
  - WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) drive-row=$(y $(grep -cE '^\| `drive/' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md)) buildspec=$(y $(grep -c 'factory drive' dev/build-harness.spec.md)) dontask-ban=$(y $(grep -c 'nor `dontAsk`' dev/build-harness.spec.md)) whitespace=$(git diff --check main -- README.md docs dev >/dev/null && echo clean || echo dirty)")`
  - THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`.
- REGRESSION. All nine driver and script scenarios of `specs/build-dispatch/spec.md` must print exactly what A's and B's Acceptance list. That covers intake parity, build parity, role argv, the reply record, concurrency, intake step lines, build step lines, stop and resume, marker and effort, and the Workflow scripts.
- Intermediate check: the harness suite passes.
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the running-code wrapper.
  - THEN it exits 0.

Interim tests: none

Tests to change: none

Protected paths: none

Out of scope:
- any code under `factory/`, `bin/` or `tests/`;
- `docs/prompts/`, `agents/` and `.factory/`;
- the retirement of the Workflow scripts, which is Operator step 5's later ticket.

---

Notes:
- README lags the code from A's merge until C's merge. The briefing expects a new command to update README in the same ticket, but the approved spec puts all the documents in part C. This plan follows the spec. If the operator wants each part to update README, that is a gate edit, not something the planner should decide.
- B's suite cases go in a new test file rather than the `test_drive.py` the spec names (see B's Scope). This keeps the guardrail without listing a sibling's file under Tests to change. The behaviour checked is unchanged.

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

Sub-ticket: T-0040.3 (T-0040.C / Documents), parent T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md`)
Branch: `factory/T-0040.3`, base `18fbe88ba88be7f2ae2dbebca09586bd25caf50d`
Commit: 0e99ddad7eb10387369fac62286f8520fd6a1a67

## What changed

This change brings the documents up to date with `factory drive`. Parts A and B of this ticket built `factory drive`, a command that does the job of the Workflow-tool scripts. It decides which AI agent role runs next, and it starts each role as its own `claude -p` process. Until this commit the documents did not mention it, and the README still listed per-role effort as not built. Only documents change here. Nothing under `factory/`, `bin/`, `tests/`, `agents/`, `docs/prompts/` or `.factory/` is touched.

Part C, item 1, `README.md`:
- **"Starting a run"** has a new how-to subsection, "Driving a ticket from a shell with `factory drive`". It covers what to run and how the phase follows the stored state. It covers `FACTORY_DISPATCH=1` when another run is in flight, `--parallel`, what the driver prints, the status file `drive/<ticket>.yaml`, and stopping and resuming. It ends with `reply.json`, the `effort:` map and `--prompt-mode`. It also says the Workflow tool remains the tested route until the driver has run a real ticket.
- **"What depends on Claude Code"** gains a row for the driver's role processes: `claude -p`, `--output-format json`, `--permission-mode auto`, the prompt file, the model, an optional `--effort`, `--tools` and `--allowedTools`. The intro count went from "Four pieces" to "Five pieces" because that table now has five "yes" rows.
- **Built** gains two bullets. The driver bullet ends "It is tested, and has not yet run a real ticket." The second bullet, "Per-role effort, for driver runs only", replaces the removed Not built bullet "Per-role effort settings". The Built bullet on the live-store fence now says that the driver also marks its own commands, and that its role processes are never marked.
- **The store's file table** gains a `drive/<ticket>.yaml` row. Its columns say: on no branch because git ignores it, written by `factory drive`, never committed, rewritten at each step and kept until the next drive of that ticket. The "Store records" row now reads "through the workflows' clerk or `factory drive`, and the operator's commands".
- **The status date** went from 2026-10-09 to 2026-10-10.

Part C, item 2, `docs/design.md`. No prompt block changed: the three edits are at lines 44, 64 and 874, and all three are outside every ```` ```text ```` block.
- In the harness table, piece 2 (the event dispatcher) now names `factory drive` as the external dispatcher. It has no clerk, so v0 limit (1) does not apply to it. Limits (2) and (3) still hold. "Clerk" is the agent the scripts start only to run one store command.
- The fence paragraph says the driver goes through the fence and the lock when it starts, then marks its own store calls. It also says the driver removes the marker from every role process's environment.
- "Running on another agent host" names `factory drive` as the Claude Code form of the adapter that section describes.

Part C, item 3, `dev/build-harness.spec.md`:
- R3 names the driver beside the Workflow scripts.
- R6 keeps "Never `bypassPermissions` (nor `dontAsk`)". It adds that under the driver, roles run under `auto` with the `--tools` and `--allowedTools` lists and the four `Edit` rule scopes, and that Bash is not restricted.
- Part H gains one paragraph pointing to `factory drive` for the same routing.
- I.4 says that under the driver, the tool restriction is `--tools` and `--allowedTools`.

Part C, item 4, `docs/changelog.md`: entry 67, "After issue #65 (2026-10-05), where …", placed before "Declined:". It cites the clerk figures and the T-0027.2 failure, and lists #22, #28, #47 and #24 part A as absorbed.

## Acceptance results

The fixtures ran under the running-code wrapper with `TMPDIR` set to this run's scratch directory (`…/run-0412-implementer/scratch/tmp`). The GIVEN blocks were taken verbatim from current truth (`human-resolution`, `live-store-guard`) and from the parent spec (`build-dispatch`). The WHEN commands were taken verbatim from the sub-ticket's input. Full log: `scratch/regress.log`.

- **NEW, "The documents describe the driver."**
  - Before (on base `18fbe88`): `starting=no depends=no built=no effort-gap=yes drive-row=no design=no changelog=no buildspec=no dontask-ban=yes whitespace=clean`. This matches the spec's "today" line.
  - After (on `0e99dda`): `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes buildspec=yes dontask-ban=yes whitespace=clean`. That is exactly the expected line. It means every required section names the driver, no "none has an effort level" text remains, the build spec still forbids `dontAsk`, and there are no whitespace errors.
- **REGRESSION, the ten driver and script scenarios of `specs/build-dispatch/spec.md`, run after the change.** All ten printed exactly their THEN lines:
  - intake parity: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`
  - build parity: `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`
  - role argv: `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`
  - reply record: `triage=ok spec_writer=ok critic=ok`
  - concurrency: `parallel=1: calls=4 max=2 parked parked`, `parallel=default: calls=4 max=4 parked parked`
  - intake step lines: `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`
  - build step lines: `untagged=0 sub=yes last=1`
  - stop and resume: `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, `resumed: exit=0 closed calls=2`
  - marker and effort: `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`
  - Workflow scripts: `T-0001.1 merged T-0001 parked`, `T-0001 awaiting-spec-gate`

  The sub-ticket says "nine" scenarios, but the ten it names are the ten WHENs in the spec, so all ten ran.
- **Gate `git diff --check main...HEAD`**, wrapped exactly as given: no output, exit 0. The change adds no whitespace errors.
- **Gate `uv run --frozen pytest -q -p no:cacheprovider tests/factory`**, wrapped exactly as given: `520 passed in 348.70s`, exit 0. This also covers the sub-ticket's intermediate check.

## Tests added/changed

None. The sub-ticket lists no tests to change and no interim tests. The change is documents only.

## Known gaps and uncertainties

- **README edits beyond the sub-ticket's list.** I made four small README edits that the sub-ticket does not list. Without them, sentences this change made stale would have stayed wrong, and "Maintaining this page" counts a stale sentence as a reviewer finding. A reviewer may judge any of them out of scope:
  1. The directory tree in "What the factory keeps in a target" gains a `drive/<T>.yaml` line, and the `runs/` line now mentions `reply.json`.
  2. The Built "Live-store fence" bullet now names the driver as marking its own commands.
  3. The README's "Running on another agent host" gains one sentence pointing to `factory drive`. That section mirrors the design doc, and the design doc's matching section changed here.
  4. "Related work and history" no longer lists per-role effort (#22) as open work, and gains one sentence on #65 and the issues it absorbs.
- **Re-derived figures.** In "Related work and history", the store counts went from "32 tickets and 26 sub-tickets" to 40 tickets and 47 sub-tickets. I counted `^T-[0-9]*\.yaml$` and `^T-[0-9]*\.[0-9]*\.yaml$` in `/Users/dphang/dev/spec-factory/.factory/store/tickets`. The runtime commit (`639fcb5`, from `git -C ~/dev/spec-factory-harness rev-parse --short HEAD`) and the harness revision (`da50576…`, from `.factory/harness.lock`) still match what the page quotes, so they are unchanged. The ticket counts will go stale as soon as more tickets are filed.
- **"Ground truth only" rule.** "Maintaining this page" says a thing appears above "Where this can go" only after it has run on a real ticket. The approved spec puts the driver under "Starting a run" and Built anyway. I followed the spec: both places say plainly that the driver is tested and has not yet run a real ticket, as several existing Built bullets already do.
- **Changelog figures are the requester's, not re-derived.** The figures are 2,236 clerk agents, 4,476 calls and 143M of 866M tokens. The parent spec's Evidence also marks them "Not re-derived here".
- **Claims about the driver.** I checked the driver behaviour these documents describe against `factory/drive.py` and the `drive` subparser in `factory/cli.py`. That covers the argv, the `Edit` rule scopes, the dropped marker, the states for each phase, the stop sequence, the status file keys and the absence of any time limit. I did not run the driver with a real `claude`. The Operator steps cover that.

## Out-of-scope observations

- **The sub-ticket says "nine" scenarios, but the spec has ten.** It names ten, and the parent spec holds ten WHENs. This is a counting slip in the plan, and it changes nothing.
- **The README's "Running on another agent host" table** still shows only the Workflow tool in the "Claude Code (today)" column. So does the design doc's. The new sentence below each covers this. Changing the table cells was more than C.2 asked for.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command, all ten regression scenarios and both gates were run on this head and printed exactly what the spec expects; the remaining risk is reviewer judgement on the four unlisted README edits
ESCALATIONS: none

## Diff `18fbe88ba88be7f2ae2dbebca09586bd25caf50d...0e99ddad7eb10387369fac62286f8520fd6a1a67`

diff --git a/README.md b/README.md
index dcfcc58..b52dbc4 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-09. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-10. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -96,7 +96,7 @@ entry but no prompt and no way to run yet.
 
 ### What depends on Claude Code
 
-Most of the factory is plain files and a Python program. Four pieces assume Claude Code.
+Most of the factory is plain files and a Python program. Five pieces assume Claude Code.
 
 | Piece | Claude Code only? | Why |
 |---|---|---|
@@ -104,6 +104,7 @@ Most of the factory is plain files and a Python program. Four pieces assume Clau
 | Role prompts, the spec format, the store's files | no | Markdown, YAML and JSONL |
 | The workflow scripts (`factory/workflows/*.js`) | yes | written for Claude Code's Workflow tool: `agent()` with a JSON schema for each clerk reply, `parallel()` for the two checkers, `phase()` for the progress view |
 | Role agents (`agents/`, copied into a target's `.claude/agents/`) | yes | Claude Code agent definitions, with a tool list per role; Claude Code registers them only when a session starts |
+| Role processes of `factory drive` (`factory/drive.py`) | yes | each role runs as one headless `claude -p` process with `--output-format json` and `--permission-mode auto`, its role's prompt file, model and optional `--effort`, and its tool limits given by `--tools` and `--allowedTools` |
 | Model names (`models` in `instance.yaml`) | yes | Claude model aliases |
 | Token cost per role (`factory/cost.py`) | yes | reads the Workflow tool's transcript files |
 
@@ -433,7 +434,8 @@ git ignores them.
 │       │                          written against; specs/<T>.<k>/subticket.md for each sub-ticket
 │       ├── plans/<T>.md           the planner's plan
 │       ├── runs/run-NNNN-<role>/  one per role run: system-prompt.txt, input.md, output.md,
-│       │   │                      meta.yaml (status, model, base, head), diff.patch for checkers
+│       │   │                      meta.yaml (status, model, base, head), diff.patch for checkers,
+│       │   │                      reply.json for a role `factory drive` ran
 │       │   ├── scratch/           ignored: the run's temporary files
 │       │   └── wt/                ignored: a checker's detached checkout of the judged commit
 │       ├── results/<commit>/      reviewer.yaml, verifier.yaml, ci.yaml: the verdicts on that commit;
@@ -446,6 +448,7 @@ git ignores them.
 │       │                          moved to openspec/changes/archive/<date>-<T>/ when it closes
 │       ├── decisions.md           standing decisions; the spec writer, critic and planner read it
 │       ├── log/<YYYY-MM>.jsonl    one event per state change, run and decision, appended
+│       ├── drive/<T>.yaml         ignored: the live status of `factory drive` on that ticket
 │       └── worktrees/<T>.<k>/     ignored: the implementer's checkout, on branch factory/<T>.<k>
 └── .claude/agents/factory-*.md    role agent definitions, where the target registers them
 ```
@@ -460,8 +463,9 @@ The store's path is `state_dir` in `instance.yaml`. `factory init` creates a new
 | `instance.yaml`, `context.md` | integration | `factory init`, then edited by the operator | the operator | durable |
 | `harness.lock` | integration | `factory init`; `--accept-harness` rewrites it | the operator | durable |
 | `.claude/agents/factory-*.md` | integration | `factory init`, when they are missing | the operator, if the target keeps them | durable |
-| Store records: requests, tickets, specs, plans, runs, results, approvals, current truth, changes, decisions, log | `factory-store` | the harness, through the workflows' clerk and the operator's commands | the operator, with `git -C <store> commit`; the harness commits the store once, the first commit `store migrate` makes | durable |
+| Store records: requests, tickets, specs, plans, runs, results, approvals, current truth, changes, decisions, log | `factory-store` | the harness, through the workflows' clerk or `factory drive`, and the operator's commands | the operator, with `git -C <store> commit`; the harness commits the store once, the first commit `store migrate` makes | durable |
 | `runs/*/scratch/`, `runs/*/wt/`, `worktrees/` | none; git ignores them | `run start` | never | scratch until the ticket moves on (kept while parked); checker checkouts until `run cleanup`; implementer checkouts until the merge |
+| `drive/<ticket>.yaml` | none; git ignores it | `factory drive` | never | a live view of one driver process, rewritten at each step; kept until the next drive of that ticket |
 | Sub-ticket branches, `factory/<T>.<k>` | their own | the implementer's commits | the implementer | kept after the merge |
 | Merges of sub-tickets | integration | `merge` | the harness | durable |
 
@@ -709,6 +713,50 @@ shows each agent as it runs. When the workflow ends, the session receives its re
 `{"ticket": "T-0032", "state": "awaiting-spec-gate", "rounds": 1}`, and the ticket's record shows the
 same state.
 
+### Driving a ticket from a shell with `factory drive`
+
+`factory drive` does the workflow scripts' job as an ordinary command, without the Workflow tool.
+It takes a ticket through the same routes as the scripts, with the same round limits and park
+reasons, and writes the same records. It calls the harness in its own process, so no clerk agent
+relays store commands. Each role runs as its own headless `claude -p` process, with that role's
+prompt, model and tool limits. The driver is tested, and has not yet run a real ticket. Until it
+has, the Workflow tool remains the tested route.
+
+1. From the target repo, start it on one ticket:
+
+   ```
+   $RUNTIME/bin/factory drive T-0032                  # the phase follows the stored state
+   $RUNTIME/bin/factory drive T-0032 --phase build --parallel 1
+   ```
+
+   Without `--phase`, a ticket in `ready-for-triage`, `ready-for-spec-writer` or `ready-for-critic`
+   goes through intake. A ticket in `ready-for-planner`, `planned` or `ready-for-parent-verify` goes
+   through the build. From any other state it prints "nothing to dispatch from this state" and ends.
+   Like the intake script, it stops at the spec gate: after you approve the spec, run it again.
+2. If any run is in flight on the target, put `FACTORY_DISPATCH=1` in front of the command, as for
+   any store write during a run ("Where a human decides"). Without it the live-store fence refuses
+   the command with exit 2. Once started, the driver marks its own store calls. Its role processes
+   never carry the marker.
+3. `--parallel N` sets how many sub-tickets build at once; the default is 2. A commit's reviewer
+   and verifier always run at the same time. Use `--parallel 1` if role processes running at once
+   conflict.
+4. Read the progress. It prints one line per step, such as
+   `T-0032.1 "Add the flag": start implementer run-0120-implementer`. Each line names the ticket or
+   sub-ticket the step concerns, with its title. The last line is the result as one JSON object:
+   what the matching script returns, with `"ok": true` added. The store's `drive/<ticket>.yaml`
+   shows the same while it runs: the role processes still running, the last step line, and the
+   result under `ended` once it stops. Git ignores that file.
+5. To stop it, press Ctrl-C or send SIGTERM. It ends its role processes, records their runs as
+   `KILLED`, parks nothing, and exits with 128 plus the signal number. Run the same command again to
+   resume from the stored state.
+
+Each role process's reply is kept as `reply.json` in its run directory. Its session id, cost in
+dollars, turn count and token usage are recorded under `claude:` in the run's `meta.yaml`. To give a
+role an effort level, add an `effort:` map to `.factory/instance.yaml`, such as
+`effort: {critic: high}`. The workflow scripts ignore it. `--prompt-mode replace` passes the role
+prompt as Claude Code's whole system prompt instead of appending it to Claude Code's own; it exists
+to measure which starts a role with less context.
+
 ### Filing a request from an issue tracker
 
 The harness has no tracker integration. A request is a Markdown file, and the link to an issue is
@@ -855,7 +903,8 @@ path above is relative to the store.
   for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not
   yet fired on a real ticket.
 - **Live-store fence.** While a run is in flight on a target, a write to its store without the
-  `FACTORY_DISPATCH=1` marker is refused. The workflow scripts mark their own commands, and the
+  `FACTORY_DISPATCH=1` marker is refused. The workflow scripts and `factory drive` mark their own
+  commands, the driver's role processes are never marked, and the
   operator marks one command at a time ("Where a human decides"). A write run from inside the
   store's `runs/` or `worktrees/` is refused even with the marker. The fence stops a role's tools,
   such as its test suite, from changing the live records by accident; it is not isolation. It has
@@ -900,6 +949,20 @@ path above is relative to the store.
   `resolve --accept-paths F`, which accepts the paths for that sub-ticket and returns it to its
   checks, whose passing results stand, or with `resolve --ruling F`, which sends it back to its
   implementer. It is tested, and has not yet fired on a real ticket.
+- **The driver, `factory drive`.** An ordinary command that takes a ticket through intake, or
+  through the build after the spec gate, on the same routes as the workflow scripts: the same round
+  limits, refusals and park reasons, and the same records. It calls the harness in its own process,
+  so no clerk agent relays store commands. Each role runs as one `claude -p` process with its
+  role's prompt and model, under Claude Code's `auto` permission mode. Its file tools may edit only
+  the run's output file, its scratch directory and the temporary directory; the implementer may
+  also edit its own worktree. Shell commands are not limited. Each process's reply and cost are
+  recorded with its run. A commit's two checkers run at once, and ready sub-tickets build at once
+  up to `--parallel N`. The workflow scripts are unchanged beside it. It is tested, and has not yet
+  run a real ticket.
+- **Per-role effort, for driver runs only.** An optional `effort:` map in `instance.yaml` gives a
+  role an effort level, which `factory drive` passes to that role's process. A role not listed gets
+  Claude Code's default. The workflow scripts ignore the map, so a role they run has a model and no
+  effort level. Neither target sets it yet.
 
 **Not built**
 
@@ -910,7 +973,6 @@ path above is relative to the store.
   for one operator and not for a team.
 - **The retro role.** Reads the log and proposes changes to the prompts and rules from what went
   wrong. No run has produced one yet.
-- **Per-role effort settings.** Each role has a model; none has an effort level.
 - **A status page.** `factory report TICKET` would render where a ticket is from the store alone.
   Today you read the store's YAML or ask the session running it.
 - **Current truth for the factory itself.** The spec store holds only the capabilities that
@@ -943,7 +1005,8 @@ format and the store carry over unchanged. Only the pieces in "What depends on C
 counterpart. Neither OpenAI Codex nor Google Antigravity has a scripted orchestrator inside the
 agent session like Claude Code's Workflow tool. On either host, the workflow logic would move into
 an ordinary script that starts one headless agent run per role and reads its JSON reply. That
-script can call `bin/factory` itself, so the clerk role goes away.
+script can call `bin/factory` itself, so the clerk role goes away. On Claude Code that script
+exists: `factory drive`, described under "Starting a run".
 
 | Need | Claude Code (today) | OpenAI Codex | Google Antigravity |
 |---|---|---|---|
@@ -990,13 +1053,15 @@ their store branch on 2026-10-04. The architecture subsections (what each role r
 ticket states, both workflows step by step, what the factory keeps in a target, how it uses git,
 filing from an issue tracker, what you read at each stop, other agent hosts) were added on
 2026-10-04 at the operator's request; the target layout answers issue #55. Open work named above:
-`factory report` (#17); current-truth seeding (#21); per-role effort (#22); registered agents for
+`factory report` (#17); current-truth seeding (#21); registered agents for
 the build roles, which `inlineRoles` works around today (#24); a stopped run that stays in flight
-(#53). Earlier sources: prompt changes borrowed from the ponytail project (#20); the documentation
+(#53). The driver, `factory drive`, answers #65 and absorbs per-role effort (#22), the operator's
+latest chat message reaching every role agent (#28), titles beside ticket ids in progress output
+(#47) and the checkers' tool limits (#24 part A); retiring the workflow scripts is a later ticket. Earlier sources: prompt changes borrowed from the ponytail project (#20); the documentation
 standard this page follows (#23); each run's scratch directory (#35); the store branch (#46). The
 design document is `docs/design.md`, its changelog `docs/changelog.md`; the working documents from
-building the harness are under `dev/`; the issue index is `dev/issues.md`. The store holds 32
-tickets and 26 sub-tickets at `.factory/store/`; the runtime is at `~/dev/spec-factory-harness`,
+building the harness are under `dev/`; the issue index is `dev/issues.md`. The store holds 40
+tickets and 47 sub-tickets at `.factory/store/`; the runtime is at `~/dev/spec-factory-harness`,
 commit `639fcb5`, and its harness revision `da50576` equals this repo's `harness.lock`.
 
 ## Maintaining this page
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index 814042c..d7988d4 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -112,10 +112,10 @@ Rows marked "ruling" are decided; rows marked "default" are mine and repeat unde
 |---|---|---|---|
 | R1 | Target and shape | `~/dev/nanobot-upstream`, branch `feat/lionbot-v3`; skills/agent definitions under `.claude/` + `factory/` package + `/factory` entry skill | ruling + addendum 2 |
 | R2 | Git server | Bare repo `~/factory-remote/nanobot.git`, pre-receive hook, one deploy key per role; GitHub remote untouched | ruling + addendum 1 |
-| R3 | **Dispatcher** | Claude Code **Workflow tool**: `factory/workflows/intake.js` and `factory/workflows/build.js`; fresh context per `agent()`; join, round counters and routing are plain code in the script. The three v0 limits of doc §Harness table piece 2 apply: (1) no filesystem or clock, so the clerk calls the store CLI and the guards live in the CLI (B); (2) the piece-3 kill is post-hoc (I.5); (3) fresh context, not isolation: every `agent()` call shares the session's checkout, credentials and git identity (Risk R1, R6). The cron/`factory loop` dispatcher of v1 is **deferred to a later ticket** | addendum 1 |
+| R3 | **Dispatcher** | Claude Code **Workflow tool**: `factory/workflows/intake.js` and `factory/workflows/build.js`; fresh context per `agent()`; join, round counters and routing are plain code in the script. The three v0 limits of doc §Harness table piece 2 apply: (1) no filesystem or clock, so the clerk calls the store CLI and the guards live in the CLI (B); (2) the piece-3 kill is post-hoc (I.5); (3) fresh context, not isolation: every `agent()` call shares the session's checkout, credentials and git identity (Risk R1, R6). The cron/`factory loop` dispatcher of v1 is **deferred to a later ticket**. Beside the scripts, `factory drive TICKET` (`factory/drive.py`) does the same routing as an ordinary Python process: it calls the store CLI in its own process, so it has no clerk and limit (1) does not apply, and it starts each role as one `claude -p` process (part H) | addendum 1; driver: issue #65 |
 | R4 | Isolated run | Implementer and retro: `agent(..., {isolation: 'worktree'})` on `~/factory/clone`; checkers: fresh context, read + shell, checkout of the head made by the clerk in `~/factory/runs/<run_id>/wt`; Docker deferred | ruling + E7 |
 | R5 | Tracker / human surface | `tickets/` YAML + `queue.md` on branch `factory-store` of the bare repo (v3 called it `factory/state`; same checkout `~/factory/state`); approved specs also exported to `knowledge_vault/sanitized_specs/<ID>.md` | ruling + addendum 2 (location: default) |
-| R6 | Permissions | Never `bypassPermissions` (nor `dontAsk`). Role agent definitions carry `tools:` allowlists: checkers and read-only authors Read/Grep/Glob/Bash, no Edit/Write; implementer and retro add Edit/Write; clerk Bash only, allowed `Bash(factory *)`, `Bash(git *)`. Real runs: the operator's session runs `/factory` with `--permission-mode acceptEdits` and `--allowedTools "Bash(factory *)" "Bash(git *)" "Bash(pytest *)" "Bash(ruff *)" "Bash(mypy *)" Read Grep Glob Edit Write Skill Workflow`; anything outside that list prompts the operator (the session is attended in v0). With the per-role keys (E) this is the fence for v0 limit (3), shared identity and credentials. See Risk R6 | ruling; mode/allowlist: default (critic S3) |
+| R6 | Permissions | Never `bypassPermissions` (nor `dontAsk`). Under `factory drive`, roles run under `--permission-mode auto` plus allowlists instead: `--tools` is Read, Grep, Glob, Bash, Write, WebFetch and WebSearch, with Edit added for the implementer, and `--allowedTools` allows Read, Grep, Glob, Bash, WebFetch and WebSearch, plus `Edit` rules, which also cover Write, for only the run's `output.md`, its `scratch/`, the temporary directory and, for the implementer, its worktree; Bash is not restricted. Role agent definitions carry `tools:` allowlists: checkers and read-only authors Read/Grep/Glob/Bash, no Edit/Write; implementer and retro add Edit/Write; clerk Bash only, allowed `Bash(factory *)`, `Bash(git *)`. Real runs: the operator's session runs `/factory` with `--permission-mode acceptEdits` and `--allowedTools "Bash(factory *)" "Bash(git *)" "Bash(pytest *)" "Bash(ruff *)" "Bash(mypy *)" Read Grep Glob Edit Write Skill Workflow`; anything outside that list prompts the operator (the session is attended in v0). With the per-role keys (E) this is the fence for v0 limit (3), shared identity and credentials. See Risk R6 | ruling; mode/allowlist: default (critic S3) |
 | R7 | Faux-SPEC input / sanitized output | `knowledge_vault/specs/*.md` → `knowledge_vault/sanitized_specs/` | addendum 2 |
 | D1 | Trunk | The bare repo's `main`, seeded once from `feat/lionbot-v3` by `factory init` | default |
 | D2 | Language, deps, gates | Python 3.11+, `pyyaml`; factory gates `ruff check factory tests/factory && mypy factory && pytest -q tests/factory`; repo `{gate commands}` default `pytest -q` | default; Nanobot's own commands unknown |
@@ -292,13 +292,15 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 
 Resumption after a human decision: the `/factory` skill re-runs `build.js` for the parent; the clerk's `ready-implementers` returns the sub-ticket the human moved to `ready-for-implementer` (`resolve --ruling`, `--redispatch`), and `buildOne` starts from the state the store holds (round from the store; for `--redispatch` after a checker kill, only the missing checker runs: `ready-checkers ST` lists roles without a row on the current head; a `--ruling` on BLOCKED re-runs the implementer at the same round with the ruling in its input, K).
 
+**`factory drive`** (`factory/drive.py`) does the same routing outside the Workflow tool. It ports both scripts from `// --- start`, `build.js` with its `buildOne`, branch for branch, with the same commands, transitions, round limits and park reasons, so a ticket it drives leaves the records the scripts leave. In place of the clerk it calls `factory.cli.main` in its own process, one call at a time, so every guard, the fence and the harness lock run as for `bin/factory`. Each role runs as one `claude -p` process from the run's directory; its reply is kept as `runs/<run_id>/reply.json` and recorded by `run finish --reply`. A head's two checkers run at once, ready sub-tickets build at once up to `--parallel N`, and the driver stops at the spec gate. Its permissions are in R6 and I.4.
+
 ### I. Isolated run per role (piece 3) — worktree v0
 
 1. System prompt = the agent definition (`factory/prompts/preamble.md` is read by its first instruction); the clerk records it in `runs/<run_id>/system-prompt.txt`.
 2. Input composed by `factory run compose RUN` (B): the role-context block (doc §Harness), then exactly the declared sources (H), written as `runs/<run_id>/input.md` with `input_sources:` in `meta.yaml` **before** the role runs; the role's prompt is a pointer to that file, so what the role saw is auditable and no second composition path exists.
 3. Mutating roles get `isolation: 'worktree'` (E7), which the Workflow tool creates and removes; the implementer's `git push` uses the implementer key via `GIT_SSH_COMMAND` set in its agent definition's `env:` (not verified: whether agent-definition frontmatter supports `env:`; fallback: a `factory git-push ticket/<ID>` wrapper the implementer is allowed to run, which supplies the key). Checkers run read+shell in a checkout the clerk made; they have no key, so a push fails at authentication.
    - Environment sync: when the instance sets `environment_sync`, `run start` runs that command in each build checkout (the implementer's worktree at every dispatch, and each checker's checkout) through the running-code wrapper, after the environment files are copied and before the role starts. A failure refuses the run, with the command and its output in `runs/<id>/environment-sync.log`.
-4. Tool restriction is the agent definition's `tools:` (R6); no `bypassPermissions` anywhere; `--restricted` applies to `claude -p` test drivers (E6).
+4. Tool restriction is the agent definition's `tools:` (R6); no `bypassPermissions` anywhere; `--restricted` applies to `claude -p` test drivers (E6). Under `factory drive`, the tool restriction is the role process's `--tools` and `--allowedTools` instead (R6).
 5. Empty output (doc §Routing rules): no time or token budget is enforced, and `agent()` reports no reason a run stopped, so no empty output is a budget kill. A run that ends without its output file, or with a blank one, is `EMPTY-OUTPUT` in `run finish`, whether `agent()` returned text, blank text or `null` (a user skip or a terminal error). When the returned text is non-blank, the script keeps its last 4000 characters with `run last-message`. The same role is re-dispatched once, on the same inputs and in the same round; a second `EMPTY-OUTPUT` in a row parks `EMPTY-OUTPUT from <role>` with both runs as outputs and records no result row for it, so `resolve --redispatch` re-runs only that role. A thrown `agent()` stays `KILLED`, parked `agent call failed: <role>: <error>`, with no re-dispatch. Until a run returns, a hung agent blocks `parallel()` and every sibling in that join; the user skipping the agent is the one manual stop (E7; Open question 4).
 6. After each run: `meta.yaml` complete, the checker worktree removed by the clerk (`factory run cleanup RUN`). The run's `runs/<run_id>/scratch/` stays until its ticket's next state change other than `parked`, which removes it (`store.save_ticket`).
 
diff --git a/docs/changelog.md b/docs/changelog.md
index d90de0a..6d55447 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -68,5 +68,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 64. After issue #76 (2026-10-09), where five of the seven role prompts, triage, planner, implementer, code reviewer and verifier, lacked the reading rules that #73 gave the spec writer and critic, though the implementer and verifier run test suites and other long commands, and every later turn re-sends what a run has read. Each of the five prompts gains the critic's Turn economy bullet, word for word: put independent reads and commands in one turn, read a line range once grep has found it, and send long output to a file in the run's scratch directory and grep or tail it. The spec writer's sentence on writing the spec in as few writes as possible stays out. The bullet goes directly before the declared-path rule in the implementer's and verifier's RULES, last in the code reviewer's WHAT YOU RUN, and last in the planner's and triage's RULES. #74's replay (entry 59) found that these rules cut the spec writer's tokens by about 37% at the same quality, but it tested the critic's reading rules only together with a cap on checking, and that pair saved nothing and made the critic check less. Nothing else in the five prompts changes, and the hook that would refuse whole-file reads and uncapped searches stays with #65. The runtime moves to these prompts only after the operator's replay of past implementer and verifier runs, with the old and the new prompts, holds quality. Rejected: a shared preamble line, which would also reach the spec writer and critic, which already carry the rules.
 65. After issues #44 and #50 (2026-10-04), where scenarios approved at the spec gate could not pass once another ticket merged first, and nothing could correct the pinned spec: on the Nanobot target, two scenarios of its ticket T-0008 created no policy file after a merged ticket made one mandatory, rulings let the build go on, and archive would still have written the unamended scenarios into current truth; here, T-0012's pinned spec was edited in place by hand, and a test that merged after T-0032's spec was written blocked T-0032.1's implementer. A human now amends a pinned spec with `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged`. It writes F as the next version and makes it the approved one, which every later role run receives. It re-pins the change folder but keeps the planner's `tasks.md`, so archive writes the amended scenarios. `--intent` is required: the harness checks that the Problem, every Decisions line, and each requirement's name, operation and statement are unchanged. It refuses `--intent changed`, or any such difference, with a restart note that names the merged sub-tickets a restart keeps, the unmerged ones it discards, and the commands to re-spec and re-plan or to close and re-file. It also refuses, writing nothing, while any run is in flight on the ticket or its sub-tickets, on a sub-ticket, at the gate, on a closed or archived ticket, and for a version that fails the gate's checks. Each amendment is recorded in `approvals/<ticket id>/amendment-<n>.md`, logged as `spec.amended`, and changes no ticket state. Every stored spec version now records the integration branch's head in `specs/<ticket id>/v<n>.yaml`. Before a sub-ticket's first implementer run, `run start` checks for spec drift: its Acceptance names an unmerged sibling it does not depend on, or a test file changed since its parent's approved version was written, in a commit that also changed a file the design names, and no Tests to change list names it. Drift refuses the run with an error that starts `BLOCKED from harness: spec drift:`, and the build parks the sub-ticket; the human amends, rules, or both, and a ruling on file stops the check. Measured on both stores' history, the test rule would have caught 9 of 10 known breaks and parks about half of all sub-tickets. The critic now receives every other approved change not yet archived, with the requirements it changes and its decisions, and its rubric item 5 makes a scenario BLOCKING when its setup would not hold whichever of the two tickets merges first. Rejected: the build spec's unbuilt `resolve --amend-spec`, because an amendment may be needed while the ticket is not stopped; a critic run on every amendment, which needs a new route; running each scenario at build start, whose expected failure is prose a program cannot compare; and a new park status for drift, which needs a new `resolve` route.
 66. After issue #51 (2026-10-04), where every build role lost its first attempt to a broken Python environment: a role's shell inherited the virtual environment activated in the session that launched the factory, which on this machine belongs to another repository's checkout, and each fresh build checkout had no `.venv`, so a `uv run --no-sync` check failed on its first import until the implementer, then the reviewer, then the verifier each installed the environment themselves. The running-code wrapper, around every role command and every gate command, now first removes the exact `$VIRTUAL_ENV/bin` entry from `PATH` and unsets `VIRTUAL_ENV` and `PYTHONHOME`, then sets the fresh HOME and the `run_env` exports as before. An instance may name one shell command, `environment_sync`, in `instance.yaml`. `run start` runs it through that wrapper in the run's checkout, the implementer's worktree at every dispatch and each checker's checkout, including the parent-close verifier's, after the environment files are copied and before the role starts. On success the run's `meta.yaml` records the command and the role's input ends its "Where you work" section with a line saying the environment is already synced and should not be synced again unless the change alters the files it is built from. A failed sync refuses the run start with exit 2 and one line naming the exit code and the run's `environment-sync.log`, which holds the command and its full output; no run is recorded or put in flight, and a checker's checkout is removed while the implementer's worktree is kept. Without the key nothing runs and the input is as before. Rejected: unsetting only the two variables, which leaves the environment's `python` first on `PATH`; an opt-in way to unset variables through `run_env`, which would leave the deactivation off by default; syncing only when the implementer's worktree is first created, because the environment files and a conflict run's merge can change the lock file at a later dispatch; and quoting the command or its output in the refusal, because the build workflow expands backticks and `$` in a park reason.
+67. After issue #65 (2026-10-05), where the dispatcher, a Workflow-tool script that can run no command and read no file, sent every store read and write through a clerk agent: the requester counted 2,236 clerk agents and 4,476 calls over 97 runs, 143M of 866M workflow context tokens (17%), and the clerk was most of the wait between steps. On 2026-10-09 the clerk also returned a correct `run finish` reply pretty-printed across lines, so T-0027.2's build parked as `harness-bug: run finish reviewer:` although the reviewer's run had succeeded. `factory drive TICKET [--phase intake|build] [--parallel N] [--prompt-mode append|replace]` (`factory/drive.py`) now does the scripts' job as an ordinary Python process. It ports both scripts branch for branch, with the same routes, round limits, refusals and park reasons, and stops at the spec gate. It calls the store CLI's entry point in its own process, one call at a time, so it has no clerk and every guard, the fence and the lock run as for `bin/factory`. It marks its own store calls with `FACTORY_DISPATCH=1` once started and never its role processes. Each role runs as one `claude -p` process from its run directory, with `--output-format json`, `--permission-mode auto`, the role's prompt file, model and an optional `--effort` from a new `effort:` map in `instance.yaml`, and `--tools`/`--allowedTools` lists whose `Edit` rules cover only the run's output file, its scratch directory and the temporary directory, plus the implementer's worktree. The reply is kept as `reply.json`, and `run finish --reply` records its session id, cost, turns and usage under `claude:` in `meta.yaml`. Progress is one line per step naming the ticket or sub-ticket and its title, and a status file, `drive/<ticket>.yaml`, which the store's `.gitignore` excludes. SIGINT or SIGTERM ends the role processes, records their runs `KILLED`, parks nothing, and a second run resumes. Absorbed: #22 (per-role effort), #28 (the operator's latest chat message reaching every role agent as overriding its task), #47 (a title beside every ticket id in progress output) and #24 part A (the checkers' tool limits). The workflow scripts stay unchanged until the driver has taken a real ticket through each half; retiring them and the clerk is a later ticket. Rejected: `dontAsk`, which removes the permission classifier while roles have no operating-system isolation (#37); the build spec's "nor `dontAsk`" stays. Rejected: a `bin/factory` subprocess per store call, and calling store functions below the CLI's entry point, which would skip the fence and the lock.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 4c1fdb0..5844e4f 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -41,7 +41,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | # | Piece | What it must do | GitHub gives you | Minimum portable substitute |
 |---|---|---|---|---|
 | 1 | Ticket store | One record per ticket and sub-ticket: status, type, spec text and version, PR link, round counter, history. The spec gate pins the version the human approved, including any edits made at the gate. This is the state machine's memory. A store CLI (read, transition, record) fronts it: the dispatcher chooses the transition, the CLI rejects any not in the routing table and any round past the cutoff, and the clerk goes through it too | Issues + labels | Any tracker (Jira, Linear) or a table in a DB. A `factory-store` branch of YAML works to start: the pre-receive hook restricts it to harness and human identities and exempts it from the merge gate |
-| 2 | Event dispatcher | Notice a state change and start the right role with the right inputs. Routes on the `STATUS:` line of the last output, per the routing table | Webhooks + Actions `on:` events | A loop (cron, every 1–5 min) that queries the store for tickets in a "ready for X" state and launches X. Polling is fine; nothing here is latency-sensitive. For a v0 inside one Claude Code session, a Workflow script: each agent() call is a fresh context, the fan-out, join, and round counters are plain code, and the same routing table lifts into the loop later. Three v0 limits. (1) The script has no filesystem or clock, so store reads and writes go through a clerk agent calling the CLI; the guards live in the CLI, not the clerk. The clerk never restates a command's output: it returns stdout verbatim with the exit code and stderr, and the script parses the JSON itself, since a schema shaped like the command's output lets the clerk re-type the answer and still validate. A non-zero exit is a refusal and no JSON on stdout is a failed store call; neither is ever read as an answer. (2) A hung agent blocks the join until a human skips it, so the piece-3 kill is post-hoc. (3) v0 gives fresh context, not isolation: every agent() call shares the session's checkout, credentials, and git identity. Use a worktree per call, run the clerk's CLI under a harness identity that has no verb for approval rows (humans write those directly), and treat v0 as exercising the routing table, not as producing trusted merges |
+| 2 | Event dispatcher | Notice a state change and start the right role with the right inputs. Routes on the `STATUS:` line of the last output, per the routing table | Webhooks + Actions `on:` events | A loop (cron, every 1–5 min) that queries the store for tickets in a "ready for X" state and launches X. Polling is fine; nothing here is latency-sensitive. For a v0 inside one Claude Code session, a Workflow script: each agent() call is a fresh context, the fan-out, join, and round counters are plain code, and the same routing table lifts into the loop later. Three v0 limits. (1) The script has no filesystem or clock, so store reads and writes go through a clerk agent calling the CLI; the guards live in the CLI, not the clerk. The clerk never restates a command's output: it returns stdout verbatim with the exit code and stderr, and the script parses the JSON itself, since a schema shaped like the command's output lets the clerk re-type the answer and still validate. A non-zero exit is a refusal and no JSON on stdout is a failed store call; neither is ever read as an answer. (2) A hung agent blocks the join until a human skips it, so the piece-3 kill is post-hoc. (3) v0 gives fresh context, not isolation: every agent() call shares the session's checkout, credentials, and git identity. Use a worktree per call, run the clerk's CLI under a harness identity that has no verb for approval rows (humans write those directly), and treat v0 as exercising the routing table, not as producing trusted merges. `factory drive TICKET` is the external dispatcher, outside the Workflow tool: an ordinary Python process that routes as the two scripts do and calls the store CLI's own entry point in its own process, one call at a time. It has no clerk, so limit (1) does not apply to it. It starts each role as one headless `claude -p` process from the run's directory, with the role's prompt, model, effort and tool limits, and stops at the spec gate. Limits (2) and (3) still hold: no role process has a time limit, and every role process runs under the operator's own login and settings |
 | 3 | Isolated run per role | Every role invocation starts in a clean checkout with no memory of earlier runs and only its declared inputs. This is what "fresh context per checker" means in practice | Actions job on a fresh runner | A container or VM per run (Docker, Firecracker, K8s Job). Run `claude -p` with the preamble + role prompt as the system prompt and the inputs on stdin. Destroy the environment after. A run that exceeds {time budget, token budget} is killed, recorded as a result row for that head and role so no join waits on it, and its ticket parked |
 | 4 | Scoped credentials | Each role gets only the access its rules allow. Implementer: push to its own branch. Triage, spec writer, critic, planner, reviewer, verifier, and gate runner: read-only clone plus a shell, with no secrets in the environment, since they run PR code before any security check has passed (model access through a proxy sidecar that holds the key, so the container has none to leak; no git write token; restricted egress). Retro: push a branch and open a PR, nothing else. No role can push to main. Only the harness identity and humans write the ticket store; role outputs enter it through the dispatcher, and the merge gate accepts an approval row only if a human identity pushed it, judged by the server's pusher identity, not the commit author | Job-level `permissions:` on a per-job `GITHUB_TOKEN` | One git user or deploy key per role, with server-side rights set on the git host. Secrets injected per job from a vault or env, never baked into the image |
 | 5 | Change proposal | A unit of review: a branch, its base, its head commit, and a place for the PR description and findings. Approvals attach to the head commit. Fix rounds push to the same branch, which is the ticket's identity | Pull requests | A branch naming convention (`ticket/<id>`) plus a record in the ticket store holding base, head SHA, and the description. GitLab MRs or Gerrit changes are direct equivalents |
@@ -61,7 +61,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Spec drift.** Between the writing of a spec and the build of one of its sub-tickets, other tickets merge, and a sibling that the sub-ticket's checks rely on may not have merged yet. The harness checks for this before the implementer spends a run on it. Every spec version the store keeps, from `spec add`, a gate edit or `spec amend`, records the integration branch's head when it was stored, as `integration_head` in `specs/<ticket id>/v<n>.yaml`; the value is null when the target repo or branch does not resolve. Before a sub-ticket's implementer run, `run start` checks for drift, ahead of the sibling-tests check. It checks only while the sub-ticket has no finished implementer run and no ruling on file. Two rules find drift. The sibling rule: the sub-ticket's Acceptance field names, by id or by plan label as a whole token, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. The test rule counts from the head recorded with the parent's approved version. It is skipped when that version has no record, because it was stored before the record existed, or when the head is null or not a commit in the target repo. For each first-parent commit on the integration branch since that head that changed a file the version's design part names, each test file the commit changed is a finding, unless the design's `## Tests to change` or the sub-ticket's "Tests to change" lists it. Named files are the design part's backticked paths that exist at the integration branch's head, other than test files and `.md` documents, which nearly every ticket edits. A test file's name starts with `test_`, ends `_test.<ext>`, or contains `.test.`. The test rule approximates "a test pins behaviour the spec changes". Measured on two stores' history, it would have caught 9 of 10 known breaks, and it parks about half of all sub-tickets. On drift, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build parks the sub-ticket with that error as the reason. The human amends the spec (`factory spec amend`, Spec store below), rules, or both; `resolve --ruling` returns the sub-ticket to its implementer, and the ruling on file stops the check from repeating.
 
-**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
+**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` meets the fence and the lock like any write when it starts; once past them, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
@@ -871,7 +871,7 @@ Intended, not built. The factory should run on any agent host that can start a r
 
 Most of the factory is already host-neutral: the store CLI and its guards (a Python program run from a shell), the role prompts (plain text), the spec format, and the store's files (YAML, Markdown, JSONL on a git branch). The pieces written for Claude Code are the two workflow scripts, which use its Workflow tool, and the role agent definitions in `.claude/agents/`; the model names and the token-cost report also assume it (README, "What depends on Claude Code").
 
-A port replaces those two pieces with one adapter whose only primitive is "run role R in directory D, with model M and reply schema S, and return the reply". The workflow logic moves into an ordinary script, in Node or Python, that calls that primitive and calls `bin/factory` directly. The clerk role then goes away: it exists only because a Workflow script cannot run a command itself. Each host's role files are generated from the one prompt source, as `docs/prompts/` will be by `factory render`.
+A port replaces those two pieces with one adapter whose only primitive is "run role R in directory D, with model M and reply schema S, and return the reply". The workflow logic moves into an ordinary script, in Node or Python, that calls that primitive and calls `bin/factory` directly. The clerk role then goes away: it exists only because a Workflow script cannot run a command itself. On Claude Code, `factory drive` is that adapter's form: it routes as the workflow scripts do, calls the store CLI in its own process, and runs each role as one `claude -p --output-format json` process whose JSON reply it reads. The workflow scripts stay beside it until it has taken a real ticket through each half. Each host's role files are generated from the one prompt source, as `docs/prompts/` will be by `factory render`.
 
 | Need | Claude Code (today) | OpenAI Codex | Google Antigravity |
 |---|---|---|---|

## Human ruling

Ruling (Green, harness owner), 2026-10-10, on the harness's spec-drift park.

Not drift. `tests/factory/test_drive.py` and `tests/factory/test_drive_build.py` were created by your own siblings' merges (T-0040.1 at 2ad4d8c52, T-0040.2 at 18fbe88ba), as the plan intends. No spec change is needed. Build part C as the sub-ticket says. This is the false positive filed as spec-factory #85.
