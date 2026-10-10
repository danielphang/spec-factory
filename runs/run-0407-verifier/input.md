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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0407-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0407-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0407-verifier/wt` (branch `factory/T-0040.1`, base `37848dbb04f29c63d5d684a3b4c033ed41ede13e`, head `656c179f4a4f4631b8fa61e037c7f871f36cd26d`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0040.1

### T-0040.A / The driver core and the intake phase
Depends on: none
Parallel-safe: no (B and C build on it, and B edits the same `factory/drive.py`)

Parent: T-0040 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A, items 1 to 10 of design.md:
- the `drive` subparser, with `--phase`, `--parallel` and `--prompt-mode`;
- `call()` through `factory.cli.main`;
- `run_role()` and the `claude -p` argv;
- `run finish --reply`;
- the intake routing ported from `intake.js`;
- phase selection from the stored state;
- progress lines, `drive/<parent id>.yaml`, and `drive/` added to `STORE_GITIGNORE`;
- the SIGINT/SIGTERM stop sequence;
- the commented `effort:` example in `factory/instance.template.yaml`;
- `tests/factory/test_drive.py`, plus the three tests listed under Tests to change.

Interim behaviour: until B lands, the build phase does not exist. If `--phase build` is given, or the stored state selects build, the driver must refuse with a non-zero exit and an error saying the build phase is not built yet, and it must write nothing to the store. It must not try to route those states. Do not add a suite test that pins this refusal, because B replaces it.

Acceptance:
- NEW. "The driver takes the intake fixtures through the same routes as the intake script".
  - WHEN `(for P in '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}' '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}]}' '{"triage": [{"say": "still waiting on my commands"}]}' '{"triage": [{"fail": "usage limit reached"}]}'; do (PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
  - THEN it prints exactly these four lines: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`.
- NEW. "Each role run records its process's reply".
  - WHEN the parent's command for that scenario is run (an intake parity run, then the inline Python check of `claude:` in `meta.yaml` and of `reply.json`).
  - THEN it prints exactly `triage=ok spec_writer=ok critic=ok`.
- NEW. "Every intake step line names its ticket and title, and the status file shows the end".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`.
- NEW. "A stopped driver ends its role process, records the run as killed and resumes from the stored state". It runs with no `--phase`, so it also checks that a `ready-for-triage` state selects intake.
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, then `resumed: exit=0 closed calls=2`.
- NEW. "The driver marks its own store calls, never its roles', and passes a configured effort".
  - WHEN the parent's command for that scenario is run, after the `t0024-inflight.sh` GIVEN block.
  - THEN it prints exactly `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`.
- NEW, an intermediate check: the intake half of "Each role runs as one claude process with its prompt, model and tool limits". This checks the argv, the prompt, the tool lists, the `Edit` rules and the dropped marker for the three intake roles. The full scenario needs B.
  - WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log)`
  - THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, one per line.
- REGRESSION. "The Workflow scripts still take both fixtures to the end of their routes".
  - WHEN the parent's command for that scenario is run.
  - THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`.
- Intermediate check: the harness suite passes, including the new `tests/factory/test_drive.py` and the three changed `test_run_scratch.py` tests.
  - WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run through the running-code wrapper.
  - THEN it exits 0.

Before any of these scenarios, run their GIVEN blocks once: the six fixture files written by the first scenario's block, `t0023-parent.sh` (from the human-resolution scenario of current truth), and `t0024-inflight.sh` (from live-store-guard).

Interim tests: none. A must not pin the interim build-phase refusal in a test.

Tests to change:
- `tests/factory/test_run_scratch.py::test_a_new_store_gitignore_is_the_full_commented_block_once`: the block now has 4 comment lines, not 3, and the loop over entries also counts `drive/` once.
- `tests/factory/test_run_scratch.py::test_an_existing_store_gitignore_gains_only_the_missing_lines`: the expected line list now ends `"runs/*/scratch/", "drive/"`.
- `tests/factory/test_run_scratch.py::test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line`: the same change, so its list now ends with `"drive/"`.

Protected paths: `factory/**` (`factory/drive.py`, `factory/cli.py`, `factory/store.py`, `factory/instance.template.yaml`)

Out of scope:
- part B: build routing, the checkers' concurrency, the `--parallel` semaphore, and sub-ticket progress lines;
- part C: README, `docs/design.md`, `dev/build-harness.spec.md` and `docs/changelog.md`;
- everything under the parent's Out of scope, including any change to `factory/workflows/*.js`, `agents/`, `docs/prompts/` or either instance's `.factory/` files.

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

Sub-ticket: T-0040.1 (T-0040.A, the driver core and the intake phase). Parent spec: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md` (v4, pinned)
Branch: `factory/T-0040.1`, head `656c179f4a4f4631b8fa61e037c7f871f36cd26d`, base `37848dbb04f29c63d5d684a3b4c033ed41ede13e`

Part A of `factory drive` is ready for review. `factory drive` is a new harness command that takes a ticket through the intake half of the pipeline. Intake runs triage, then the spec writer and the spec critic, and stops at the spec gate. The driver is an ordinary Python process, so it needs no clerk agent to relay its store calls. Every part A acceptance criterion and both gates pass on the head above. The build phase is part B's work.

## Since the last run: the operator's ruling

The last implementer run (run-0405) built this head and stopped with BLOCKED. One criterion counted the run id twice in the status file, which is the driver's live view of itself in the store. The run id appears once in the `running` list and once on the `last:` line, as design.md A.7 requires. The operator ruled on 2026-10-09 that the criterion was wrong, not the build. The amended criterion counts only the `running` list's entry (`grep -c '^- run: run-0001-triage'`). Design A.7 stays as built.

This run made no code change and no commit. It re-ran the amended scenario, which now prints the expected line. It also re-ran every other acceptance command and both gates on the same head, and all of them still pass.

## What changed

Part A covers items 1 to 10 of design.md. All of it is in commit 656c179.

1. **Command** (`factory/cli.py`): a new `drive` subparser takes `TICKET`, `--phase {intake,build}`, `--parallel N` and `--prompt-mode {append,replace}`. `--parallel N` must be at least 1, defaults to 2 and is unused until part B. `--prompt-mode` defaults to `append`. `drive_cmd` dispatches through `main()`, so the instance refusal, the fence and the harness lock apply at start. The fence is the check that refuses an unmarked store write while a run is in flight. The harness lock is the check that the running harness revision is the one this instance accepted. After those checks, `factory.drive.drive` sets `FACTORY_DISPATCH=1` in `os.environ`. That variable is the dispatcher marker, which the fence lets through.
2. **Store calls** (`factory/drive.py` `call`): each call runs `cli.main(argv)` with stdout and stderr captured. It returns the last stdout line that is a JSON object, plus `exit` and `stderr`. It normalises the result the same way the scripts' `clerk()` does. Calls are synchronous, so they run one at a time on the main thread.
3. **Role runner** (`run_role` and `run_once`): these follow the scripts' `runRole` and `runOnce`. The steps are `run start`, then `run compose`, then one `claude` process.
   - The process runs from the run directory, with stdin `/dev/null`. Its environment is the driver's, minus `FACTORY_DISPATCH`.
   - `role_argv` builds the argv in the design's order, with real absolute paths. Each `Edit` rule's path therefore starts with `//`. The implementer gets the `Edit` tool, its worktree rule and `--add-dir`. `--effort` comes from `effort[role]` in `instance.yaml`.
   - Stdout is written to `<run>/reply.json` as printed.
   - A failed call is a non-zero exit, or stdout that is not a JSON object. It goes to `run finish --status-override KILLED --reply`, then a checker's cleanup, then a park with `agent call failed: <role>: <message>`.
   - Otherwise the order is `run finish --reply`, then a checker's cleanup, then the script's branches. Those branches are the `harness-bug` park on a refused finish, a tripwire `parked`, `run last-message` on EMPTY-OUTPUT, and one re-dispatch. A second EMPTY-OUTPUT parks.
   - The build-only branches are ported as the scripts have them, but no part A test reaches them. They are the `BLOCKED ` run-start refusal parked verbatim, and the checker cleanup.
4. **`run finish --reply FILE`** (`factory/cli.py` `_claude_record`): when FILE is a JSON object, it records `claude: {session_id, total_cost_usd, num_turns, usage}` in `meta.yaml`. Otherwise it records `claude: null`. Without `--reply`, nothing changes.
5. **Intake routing** (`Driver.intake`): a branch-for-branch port of `intake.js` from its `// --- start` marker. It covers triage ACCEPT, REJECT, NEEDS-HUMAN, CLARIFY and unknown, then the writer/critic loop with `max_rounds.spec` and `models` from `factory config`. The transitions, `--round` operations, `spec add` calls and park reasons match the script, including `--by workflow`. Park reasons get the script's `"` to `'` replacement.
6. **Phase**: without `--phase`, the stored state selects the phase. Intake states run. A state in neither phase ends with `nothing to dispatch from this state`. **Interim behaviour**: `--phase build`, or a stored state that selects build, is refused before anything is written. The command exits 2 and prints `<T> is <state>: the build phase of factory drive is not built yet; run the build Workflow script`. As the sub-ticket asks, no suite test pins this refusal.
7. **Progress**: the driver prints one flushed line per step, of the form `<ticket id> "<title>": <step>`. The steps are start, finish, transition, park, the critic's approval note and `end: …`. The title is read again after triage ACCEPT. The status file `drive/<ticket>.yaml` is written with `store.write_yaml` at start, at each step and at the end. Its keys are `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running`, `last` and `ended`. The last stdout line is the script's result object with `"ok": true` added. `STORE_GITIGNORE` (`factory/store.py`) gains one comment line, then `drive/`.
8. **Stop** (`Driver.stop`): SIGINT and SIGTERM handlers cancel the routing. Each role process then gets SIGTERM, and SIGKILL if it is still running 10 seconds later. Each of the driver's in-flight runs is finished with `--status-override KILLED`, and a checker's run gets its cleanup. Nothing is parked. `ended` is written, the last line is `{"ok": false, "ticket": …, "stopped": "SIGTERM"}`, and the exit code is 128 plus the signal number. An unexpected exception runs the same sequence and exits 1.
9. **`factory/instance.template.yaml`**: a commented `# effort: {critic: high}` example, with one comment line on what it does.
10. **Suite**: the new `tests/factory/test_drive.py`, and the three listed changes to `test_run_scratch.py`.

## Acceptance results

I ran the GIVEN blocks once, with `TMPDIR` set to this run's scratch directory. They were extracted verbatim from the store's current-truth specs: `openspec/specs/human-resolution/spec.md` lines 13–65 (`t0023-parent.sh`) and `openspec/specs/live-store-guard/spec.md` lines 13–67 (`t0024-inflight.sh`). The six `t0040-*` files came from spec v4 lines 161–298. Each WHEN command was then extracted verbatim from this run's input. Each ran from the worktree on 656c179, through the running-code wrapper, under `bash`, with the same `TMPDIR`. The full log is `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0406-implementer/scratch/acceptance.log`.

| Scenario | Before (base 37848db, from run-0405) | After (656c179, this run) | Result |
|---|---|---|---|
| NEW: intake fixtures follow the same routes as the script | `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ`, `ready-for-triage script=1/1 drive=0/0 differ` | `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` | met |
| NEW: each role run records its reply | `none` | `triage=ok spec_writer=ok critic=ok` | met |
| NEW: step lines and status file | `steps=no untagged=0 last=0 status= ignored=0` | `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` | met |
| NEW: stop, KILLED, resume (amended count) | `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0` / `resumed: exit=2 ready-for-triage calls=` | `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1` / `resumed: exit=0 closed calls=2` | met |
| NEW: marker on the driver, never on its roles, and effort | `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` | `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` | met |
| NEW (intermediate): intake half of the argv check | one empty line | `critic ok`, `spec_writer ok`, `triage ok` | met |
| REGRESSION: the Workflow scripts still reach their ends | not run (regression check) | `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` | met |

What the results show:
- **Same route as the script.** `same` means the driver's store records match the intake script's, apart from ids and times. Each `n/n` pair says both sides started one `claude` process per run.
- **Stop.** `running=1` means the stopped run was listed as running while its role process ran. `exit=143` is 128 plus SIGTERM. `run=KILLED` means the run was recorded as killed, and `in_flight: []` means none of its runs were left in flight. `child=gone` means the role process was ended. The resume line shows that a second `factory drive` with no `--phase` picked intake from `ready-for-triage` and finished the route.
- **Marker.** `unmarked=2` and `inside=2` mean the fence refused the driver unmarked, and also refused it marked from inside a run directory. `dispatch=1` means the role process ran without the marker. `effort=1` means the configured `--effort low` reached triage.

The "before" figures were recorded by run-0405 on the base. They match verification.md's "today" figures.

Gates, each run exactly as written from the worktree on 656c179 (`main` is 37848db):
- `git diff --check main...HEAD` exited 0 with no output: the branch has no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `511 passed in 250.36s (0:04:10)` and exited 0. This run also serves as the intermediate check that the suite passes.

Run-0405 checked the interim build refusal by hand, without a test, on a `t0023-parent.sh` store whose T-0001 is `ready-for-planner`. `bin/factory drive T-0001` exited 2, and so did `--phase build`. A checksum of every store file was unchanged. The code is the same here, and I did not repeat that check.

## Tests added and changed

Added: `tests/factory/test_drive.py`, with 15 tests. They are black-box tests through `bin/factory`, with a Python stand-in `claude` first on `PATH`. They cover:
- each intake route of the parity table: approval after one revision, max rounds, two EMPTY-OUTPUTs with the last message kept, and a failed process recorded KILLED with no retry;
- triage REJECT, CLARIFY, NEEDS-HUMAN and unknown;
- stdout that is not JSON, reported by its last stderr line;
- the exact argv, with no marker even when the driver starts marked;
- `--prompt-mode replace`;
- the implementer's `Edit` tool, worktree rule and `--add-dir`. These are tested through `role_argv` in a subprocess, because the suite's own `factory` package name is `tests/factory`;
- a configured effort for one role only;
- the `claude:` record and `reply.json`, and `claude: null` for a reply that is not a JSON object;
- step lines and the status file, a state with nothing to dispatch, and a stop and resume. The stop test asserts that the `running` list is exactly `[run-0001-triage]` while the role runs, which is what the amended scenario now checks too.

Run-0405 saw these tests fail before the change: with `factory/` stashed back to base, 17 failed and 10 passed.

Changed: only the three tests listed under Tests to change, all in `tests/factory/test_run_scratch.py`. Each change follows the Decision that git ignores the status file.
- `test_a_new_store_gitignore_is_the_full_commented_block_once` now expects 4 comment lines, and counts `drive/` once.
- `test_an_existing_store_gitignore_gains_only_the_missing_lines` now expects the list to end `"runs/*/scratch/", "drive/"`.
- `test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line` now expects the list to end `"drive/"`.

## Known gaps and uncertainties

- `factory:` markers added: one, at `factory/drive.py:390`, on the interim build-phase refusal that part B replaces.
- No part A test reaches the build-only paths in `run_once`. Those are the `BLOCKED ` run-start refusal and the checker cleanup after a finish or a failure.
- Store calls capture only `sys.stdout` and `sys.stderr`. A CLI command that starts a subprocess without capturing its output would write straight to the driver's stdout and break the line format. I saw none in intake. Part B should watch for this in the build commands, which run git.
- Park reasons and `--text` go to the CLI as single arguments (`--reason=…`, `--text=…`). The scripts pass them through `sh -c` inside double quotes, so the shell expands a `$` or a backtick in a reason there. The driver keeps them verbatim.
- When `config` or `ticket show` fails, the driver prints `{"ok": false, "ticket", "error"}` and exits 1, before it writes a status file. The spec does not say what such a failure returns, so this is my choice.
- A stop does not write `reply.json` or pass `--reply` for a killed process, so that run has no `claude:` key. The spec's stop sequence names only `--status-override KILLED`.
- A second signal during the stop sequence is ignored. The 10-second SIGKILL bound still applies.
- `ruff` is not installed in the worktree's `.venv`, so I did not run it. It is not a gate command here.

## Out-of-scope observations

- The briefing says a change to a command updates the README in the same ticket. The plan assigns that to part C, so this branch leaves the README unchanged.
- The scenario fixture files were written under this run's scratch directory (`TMPDIR=<scratch>/tmp`), not the shared `$TMPDIR`. Other runs' copies of the same fixture names cannot collide with them.
- Protected paths this branch touches, all declared by the sub-ticket: `factory/drive.py`, `factory/cli.py`, `factory/store.py` and `factory/instance.template.yaml`.

## Responses to findings

None. No reviewer or verifier has reviewed this head yet. This run answers the operator's ruling on run-0405's BLOCKED report, as described above.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every part A acceptance command printed its expected output, and both gates passed, all run in this session on 656c179.
ESCALATIONS: none

## Diff `37848dbb04f29c63d5d684a3b4c033ed41ede13e...656c179f4a4f4631b8fa61e037c7f871f36cd26d`

diff --git a/factory/cli.py b/factory/cli.py
index 4e90169..898ccfe 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -468,6 +468,8 @@ def run_finish(a, root, cfg):
                  "status": parsed["status"], "confidence": parsed.get("confidence"),
                  "escalations": parsed.get("escalations", []),
                  "escalations_note": parsed.get("escalations_note")})
+    if a.reply:
+        meta["claude"] = _claude_record(a.reply)
     store.write_yaml(d / "meta.yaml", meta)
     if a.run in t["in_flight"]:
         t["in_flight"].remove(a.run)
@@ -492,6 +494,33 @@ def run_finish(a, root, cfg):
     out(res)
 
 
+def _claude_record(path: str) -> dict | None:
+    """What `run finish --reply FILE` keeps of a role process's reply (`claude -p --output-format
+    json`): its session and cost, or None when FILE is not one JSON object. The reply's `result`
+    text is left out: it repeats output.md."""
+    try:
+        reply = json.loads(Path(path).read_text(encoding="utf-8"))
+    except (OSError, ValueError):
+        return None
+    if not isinstance(reply, dict):
+        return None
+    return {k: reply.get(k) for k in ("session_id", "total_cost_usd", "num_turns", "usage")}
+
+
+# ----- driver ---------------------------------------------------------------------
+
+def drive_cmd(a, root, cfg):
+    from factory import drive  # local: the driver calls back into main() for every store call
+    drive.drive(a, root, cfg)
+
+
+def _at_least_one(v: str) -> int:
+    n = int(v)
+    if n < 1:
+        raise argparse.ArgumentTypeError(f"{v} is less than 1")
+    return n
+
+
 # ----- spec / plan ----------------------------------------------------------------
 
 def _text_from(a, root) -> str:
@@ -1767,6 +1796,8 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("run")
     p.add_argument("--output-file")
     p.add_argument("--status-override")
+    p.add_argument("--reply", help="the role process's reply (claude -p --output-format json): its session "
+                                   "id, cost, turns and usage are recorded under claude: in meta.yaml")
     p.set_defaults(fn=run_finish)
     p = rn.add_parser("last-message")
     p.add_argument("run")
@@ -1866,6 +1897,14 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("text")
     p.set_defaults(fn=decision_add)
 
+    p = sp.add_parser("drive", help="route TICKET's roles as the Workflow scripts do, each role one "
+                                    "`claude -p` process; stops at the spec gate")
+    p.add_argument("ticket")
+    p.add_argument("--phase", choices=("intake", "build"), help="default: the one the stored state is in")
+    p.add_argument("--parallel", type=_at_least_one, default=2, help="sub-tickets built at once (default 2)")
+    p.add_argument("--prompt-mode", choices=("append", "replace"), default="append",
+                   help="append the role prompt to Claude Code's system prompt, or replace it")
+    p.set_defaults(fn=drive_cmd)
     p = sp.add_parser("config")
     p.set_defaults(fn=config_cmd)
     st = sp.add_parser("status").add_subparsers(dest="sub", required=True)
diff --git a/factory/drive.py b/factory/drive.py
new file mode 100644
index 0000000..d8168f8
--- /dev/null
+++ b/factory/drive.py
@@ -0,0 +1,404 @@
+"""`factory drive TICKET`: the dispatcher as an ordinary process, with no clerk (T-0040).
+
+It does the Workflow scripts' job without the Workflow tool. Every store call goes through the
+CLI's own entry point, `factory.cli.main`, in this process, one at a time, so every guard, the
+fence and the harness lock run as they do for `bin/factory`. Every role runs as one headless
+`claude -p` process from its run directory, with its role's prompt, model, effort and tool limits;
+its reply is kept as `runs/<id>/reply.json` and its cost recorded by `run finish --reply`.
+
+The routing is a port of factory/workflows/intake.js from `// --- start`, branch for branch: the
+same commands, transitions, round operations and park reasons, so a ticket driven here leaves the
+same records the script leaves. Like the script, the driver stops at the spec gate.
+
+One stdout line per step, `<ticket id> "<title>": <step>`, then the result as one JSON object. The
+store's `drive/<ticket>.yaml` is a live view of this process (git ignores it). SIGINT or SIGTERM
+ends the role processes, records their runs KILLED and parks nothing: running `factory drive`
+again resumes from the stored state.
+
+Part A of T-0040 builds the intake phase only: the build phase (build.js) is refused.
+"""
+from __future__ import annotations
+
+import asyncio
+import contextlib
+import io
+import json
+import os
+import signal
+import tempfile
+from pathlib import Path
+
+from factory import cli, store
+from factory.store import Refused
+
+INTAKE_STATES = ("ready-for-triage", "ready-for-spec-writer", "ready-for-critic")
+BUILD_STATES = ("ready-for-planner", "planned", "ready-for-parent-verify")
+CHECKERS = ("reviewer", "verifier")
+# Every role gets these tools; the implementer also gets Edit. Anything else the session offers
+# (sub-agents, task lists, notebook edits) is withheld: no role prompt asks for one.
+TOOLS = "Read,Grep,Glob,Bash,Write,WebFetch,WebSearch"
+ALLOWED = "Read,Grep,Glob,Bash,WebFetch,WebSearch"
+PROMPT = ("Your entire input is the file {run}/input.md; read it first and follow it. "
+          "Write your complete output to {run}/output.md and return the same text.")
+KILL_AFTER_S = 10
+
+
+def call(*argv: str) -> dict:
+    """One store call: `factory.cli.main(argv)` with its output captured. Returns the last stdout
+    line that is a JSON object, plus `exit` and `stderr`, normalised as the scripts' clerk() is: a
+    non-zero exit is never ok, and a refusal always carries error text in `stderr`."""
+    so, se = io.StringIO(), io.StringIO()
+    with contextlib.redirect_stdout(so), contextlib.redirect_stderr(se):
+        try:
+            code = cli.main(list(argv))
+        except SystemExit as e:  # an argparse refusal
+            code = e.code if isinstance(e.code, int) else 2
+    err = se.getvalue()
+    res = None
+    for ln in reversed(so.getvalue().splitlines()):
+        res = _json_object(ln)
+        if res is not None:
+            break
+    if res is None:
+        return {"ok": False, "exit": code, "stderr": err or f"exit {code}, no JSON on stdout",
+                "error": "no JSON on stdout"}
+    if code != 0:
+        res["ok"] = False
+    if not res.get("stderr") and err:
+        res["stderr"] = err
+    if res.get("ok") is False and not res.get("stderr"):
+        res["stderr"] = res.get("error") or f"exit {code}, no error text"
+    res["exit"] = code
+    return res
+
+
+def _json_object(text: str) -> dict | None:
+    try:
+        v = json.loads(text)
+    except ValueError:
+        return None
+    return v if isinstance(v, dict) else None
+
+
+def role_argv(role: str, run: str, model: str, prompt_mode: str, worktree: str | None,
+              effort: str | None) -> list[str]:
+    """The `claude` argv for one role run. `run` and `worktree` are real absolute paths, so each
+    `Edit` rule's path starts with `//`, Claude Code's form for an absolute path."""
+    tmp = os.path.realpath(tempfile.gettempdir())
+    tools = TOOLS
+    allowed = f"{ALLOWED},Edit(/{run}/output.md),Edit(/{run}/scratch/**),Edit(/{tmp}/**)"
+    if role == "implementer":
+        tools += ",Edit"
+        if worktree:
+            allowed += f",Edit(/{worktree}/**)"
+    sysp = "--append-system-prompt-file" if prompt_mode == "append" else "--system-prompt-file"
+    argv = ["-p", PROMPT.format(run=run), "--model", model, "--output-format", "json",
+            "--permission-mode", "auto", sysp, f"{run}/system-prompt.txt",
+            "--tools", tools, "--allowedTools", allowed]
+    if role == "implementer" and worktree:
+        argv += ["--add-dir", worktree]
+    if effort:
+        argv += ["--effort", str(effort)]
+    return argv
+
+
+def _failure_message(reply: dict | None, stderr: str, code: int | None) -> str:
+    """Why a role process failed: its reply's `result`, else the last non-blank line of stderr,
+    else its exit code."""
+    said = (reply or {}).get("result")
+    if isinstance(said, str) and said.strip():
+        return said.strip()
+    lines = [ln for ln in stderr.splitlines() if ln.strip()]
+    return lines[-1].strip() if lines else f"exit {code}"
+
+
+class Driver:
+    def __init__(self, a, root: Path, cfg: dict):
+        self.ticket = a.ticket
+        self.phase = a.phase
+        self.prompt_mode = a.prompt_mode
+        self.root = root
+        self.effort = cfg.get("effort") or {}
+        self.models: dict = {}
+        self.max_spec = 2
+        self.title = ""
+        self.running: dict[str, dict] = {}  # run id -> {run, role, ticket, pid}: this driver's runs in flight
+        self.procs: dict[str, asyncio.subprocess.Process] = {}
+        self.stopped: signal.Signals | None = None
+        self.status: dict = {}
+        self.status_path = root / "drive" / f"{self.ticket}.yaml"
+
+    # ----- status ---------------------------------------------------------------------
+
+    def write_status(self, **changes) -> None:
+        self.status.update(changes, title=self.title, updated=store.now(),
+                           running=[dict(r) for r in self.running.values()])
+        store.write_yaml(self.status_path, self.status)
+
+    def step(self, text: str, ticket: str | None = None) -> None:
+        line = f'{ticket or self.ticket} "{self.title}": {text}'
+        print(line, flush=True)
+        self.write_status(last=line)
+
+    # ----- store calls the routing makes ------------------------------------------------
+
+    def park(self, ticket: str, reason: str, outputs: list[str]) -> None:
+        argv = ["ticket", "park", ticket, "--reason=" + reason.replace('"', "'")]
+        if outputs:
+            argv += ["--outputs", ",".join(outputs)]
+        call(*argv)
+        self.step(f"parked: {reason}", ticket)
+
+    def transition(self, to: str, round_op: str | None = None) -> dict:
+        argv = ["ticket", "transition", self.ticket, "--to", to, "--by", "workflow"]
+        res = call(*argv, *(["--round", round_op] if round_op else []))
+        self.step(f"-> {to}" if res["ok"] else f"-> {to} refused: {res.get('stderr', '').strip()}")
+        return res
+
+    # ----- role runs ----------------------------------------------------------------------
+
+    async def run_role(self, role: str, ticket: str) -> dict | None:
+        """runRole: an EMPTY-OUTPUT run is re-dispatched once; a second in a row parks the ticket.
+        None means the ticket was parked."""
+        first = await self.run_once(role, ticket)
+        if not first or first["status"] != "EMPTY-OUTPUT":
+            return first
+        self.step(f"{role} {first['runId']}: EMPTY-OUTPUT; re-dispatching {role} once", ticket)
+        second = await self.run_once(role, ticket)
+        if not second or second["status"] != "EMPTY-OUTPUT":
+            return second
+        self.park(ticket, f"EMPTY-OUTPUT from {role}", [first["runId"], second["runId"]])
+        return None
+
+    async def run_once(self, role: str, ticket: str) -> dict | None:
+        start = call("run", "start", "--role", role, "--ticket", ticket, "--model", self.models[role])
+        if not start["ok"]:
+            # A refusal that starts `BLOCKED ` is the harness blocking the run (the sibling-tests
+            # check): parked verbatim, so `resolve --ruling` treats it as an implementer's BLOCKED.
+            err = start.get("error")
+            blocked = isinstance(err, str) and err.startswith("BLOCKED ")
+            self.park(ticket, err if blocked else f"harness-bug: run start {role}: {start.get('stderr') or ''}", [])
+            return None
+        rid = start["run_id"]
+        comp = call("run", "compose", rid)
+        if not comp["ok"]:
+            self.park(ticket, f"harness-bug: run compose {role}: {comp.get('stderr') or ''}", [rid])
+            return None
+        run = os.path.realpath(self.root / "runs" / rid)
+        wt = os.path.realpath(start["worktree"]) if start.get("worktree") else None
+        argv = role_argv(role, run, start.get("model") or self.models[role], self.prompt_mode, wt,
+                         self.effort.get(role))
+        env = {k: v for k, v in os.environ.items() if k != "FACTORY_DISPATCH"}
+        self.running[rid] = {"run": rid, "role": role, "ticket": ticket, "pid": None}
+        try:
+            proc = await asyncio.create_subprocess_exec(
+                "claude", *argv, cwd=run, env=env, stdin=asyncio.subprocess.DEVNULL,
+                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
+        except OSError as e:
+            code, out, err = None, b"", f"cannot start claude: {e}"
+        else:
+            self.procs[rid] = proc
+            self.running[rid]["pid"] = proc.pid
+            self.step(f"start {role} {rid}", ticket)
+            out, errb = await proc.communicate()
+            code, err = proc.returncode, errb.decode("utf-8", "replace")
+            self.procs.pop(rid, None)
+        reply_path = os.path.join(run, "reply.json")
+        store.write_text(Path(reply_path), out.decode("utf-8", "replace"))
+        reply = _json_object(out.decode("utf-8", "replace"))
+        if code != 0 or reply is None:
+            # A failed call is treated as a thrown agent() call: the run is recorded KILLED and the
+            # ticket parked with the error, so no run is left in flight. No retry.
+            call("run", "finish", rid, "--status-override", "KILLED", "--reply", reply_path)
+            if role in CHECKERS:
+                call("run", "cleanup", rid)
+            self.running.pop(rid, None)
+            self.step(f"{role} {rid}: KILLED", ticket)
+            self.park(ticket, f"agent call failed: {role}: {_failure_message(reply, err, code)}", [rid])
+            return None
+        # run finish reads the output file for every run: a missing or blank one is EMPTY-OUTPUT.
+        fin = call("run", "finish", rid, "--reply", reply_path)
+        if role in CHECKERS:
+            call("run", "cleanup", rid)
+        self.running.pop(rid, None)
+        if not fin["ok"]:
+            self.park(ticket, f"harness-bug: run finish {role}: {fin.get('stderr') or ''}", [rid])
+            return None
+        if fin.get("parked"):  # the tripwire saw a listed live file change: do not route on STATUS
+            self.step(f"parked: {fin['parked']}", ticket)
+            return None
+        said = reply.get("result").strip() if isinstance(reply.get("result"), str) else ""
+        if fin["status"] == "EMPTY-OUTPUT" and said:
+            call("run", "last-message", rid, "--text=" + said[-4000:])
+        esc = fin.get("escalations") or []
+        self.step(f"{role} {rid}: {fin['status']}" + (f" (+{len(esc)} escalations)" if esc else ""), ticket)
+        return {"runId": rid, "status": fin["status"], "escalations": esc}
+
+    # ----- intake: factory/workflows/intake.js from `// --- start` ---------------------------
+
+    async def intake(self, state: str, rnd: int) -> dict:
+        T = self.ticket
+        parked = {"ticket": T, "state": "parked"}
+        if state == "ready-for-triage":
+            t = await self.run_role("triage", T)
+            if not t:
+                return parked
+            if t["status"] == "ACCEPT":
+                self.transition("ready-for-spec-writer")
+                state = "ready-for-spec-writer"
+                show = call("ticket", "show", T, "--json")  # triage ACCEPT may have retitled it
+                if show["ok"]:
+                    self.title = show["title"]
+            elif t["status"] == "REJECT":
+                self.transition("closed")
+                return {"ticket": T, "state": "closed", "triage": t}
+            elif t["status"] == "NEEDS-HUMAN":
+                self.park(T, "NEEDS-HUMAN from triage", [t["runId"]])
+                return {**parked, "triage": t}
+            elif t["status"] == "CLARIFY":
+                self.transition("waiting-requester")
+                return {"ticket": T, "state": "waiting-requester", "triage": t}
+            else:
+                self.park(T, f"harness-bug: unknown STATUS {t['status']} from triage", [t["runId"]])
+                return parked
+        if state not in ("ready-for-spec-writer", "ready-for-critic"):
+            return {"ticket": T, "state": state, "note": "nothing to dispatch from this state"}
+        while True:
+            if state == "ready-for-spec-writer":
+                w = await self.run_role("spec_writer", T)
+                if not w:
+                    return parked
+                if w["status"] == "NEEDS-HUMAN":
+                    call("spec", "add", T, "--from-run", w["runId"])
+                    self.park(T, "NEEDS-HUMAN from spec writer", [w["runId"]])
+                    return parked
+                if w["status"] not in ("READY-FOR-CRITIC", "NEEDS-SPLIT"):
+                    self.park(T, f"harness-bug: unknown STATUS {w['status']} from spec writer", [w["runId"]])
+                    return parked
+                added = call("spec", "add", T, "--from-run", w["runId"])
+                if not added["ok"]:
+                    self.park(T, f"harness-bug: spec add: {added.get('stderr') or ''}", [w["runId"]])
+                    return parked
+                tr = self.transition("ready-for-critic", "spec:init")
+                if not tr["ok"]:
+                    self.park(T, f"harness-bug: transition to critic: {tr.get('stderr') or ''}", [w["runId"]])
+                    return parked
+                rnd = _spec_round(tr, rnd)
+                state = "ready-for-critic"
+            c = await self.run_role("critic", T)
+            if not c:
+                return parked
+            if c["status"] == "APPROVE":
+                self.transition("awaiting-spec-gate")
+                self.step(f"spec approved by critic in round {rnd}; awaiting the human gate "
+                          f"(bin/factory approve-spec {T})")
+                return {"ticket": T, "state": "awaiting-spec-gate", "rounds": rnd}
+            if c["status"] == "ESCALATE":
+                self.park(T, "ESCALATE from critic", [c["runId"]])
+                return {**parked, "rounds": rnd}
+            if c["status"] != "REVISE":
+                self.park(T, f"harness-bug: unknown STATUS {c['status']} from critic", [c["runId"]])
+                return parked
+            if rnd < self.max_spec:
+                tr = self.transition("ready-for-spec-writer", "spec:+1")
+                if not tr["ok"]:
+                    self.park(T, f"harness-bug: round increment refused: {tr.get('stderr') or ''}", [c["runId"]])
+                    return parked
+                rnd = _spec_round(tr, rnd)
+                state = "ready-for-spec-writer"
+                continue
+            self.park(T, "max rounds", [c["runId"]])
+            return {**parked, "rounds": rnd, "reason": "max rounds"}
+
+    # ----- start, stop, end ------------------------------------------------------------------
+
+    async def run(self, state: str, rnd: int) -> int:
+        loop = asyncio.get_running_loop()
+        route = asyncio.ensure_future(self.intake(state, rnd))
+        for sig in (signal.SIGINT, signal.SIGTERM):
+            loop.add_signal_handler(sig, self._on_signal, sig, route)
+        try:
+            result, code = {**await route, "ok": True}, 0
+        except asyncio.CancelledError:
+            if self.stopped is None:
+                raise
+            await self.stop()
+            result, code = {"ok": False, "ticket": self.ticket, "stopped": self.stopped.name}, 128 + self.stopped
+        except Exception as e:  # noqa: BLE001 - a driver bug: end the role processes, park nothing
+            await self.stop()
+            result, code = {"ok": False, "ticket": self.ticket, "error": f"{type(e).__name__}: {e}"}, 1
+        self.end(result)
+        return code
+
+    def _on_signal(self, sig: signal.Signals, route: asyncio.Future) -> None:
+        if self.stopped is None:
+            self.stopped = sig
+            route.cancel()
+
+    async def stop(self) -> None:
+        """End every role process this driver started (SIGTERM, then SIGKILL after KILL_AFTER_S)
+        and record each of its runs in flight KILLED. Parks nothing: a stop is not a failure."""
+        procs = [p for p in self.procs.values() if p.returncode is None]
+        for p in procs:
+            with contextlib.suppress(ProcessLookupError):
+                p.terminate()
+        if procs:
+            waits = [asyncio.ensure_future(p.wait()) for p in procs]
+            await asyncio.wait(waits, timeout=KILL_AFTER_S)
+            for p in procs:
+                if p.returncode is None:
+                    with contextlib.suppress(ProcessLookupError):
+                        p.kill()
+            await asyncio.gather(*waits)
+        for rid, r in list(self.running.items()):
+            call("run", "finish", rid, "--status-override", "KILLED")
+            if r["role"] in CHECKERS:
+                call("run", "cleanup", rid)
+            self.running.pop(rid)
+            self.procs.pop(rid, None)
+            self.step(f"{r['role']} {rid}: KILLED", r["ticket"])
+
+    def end(self, result: dict) -> None:
+        how = (f"stopped by {result['stopped']}" if "stopped" in result
+               else f"failed: {result['error']}" if "error" in result else result.get("state"))
+        self.step(f"end: {how}")
+        self.write_status(ended=result)
+        print(json.dumps(result, ensure_ascii=False), flush=True)
+
+
+def _spec_round(tr: dict, rnd: int) -> int:
+    spec = (tr.get("round") or {}).get("spec")
+    return spec if isinstance(spec, int) and not isinstance(spec, bool) else rnd
+
+
+def drive(a, root: Path, cfg: dict) -> None:
+    """`factory drive`, after main() has run the instance refusal, the fence and the harness lock.
+    From here on the driver's own store calls carry the dispatcher marker; its role processes never
+    inherit it."""
+    os.environ["FACTORY_DISPATCH"] = "1"
+    d = Driver(a, root, cfg)
+    conf = call("config")
+    if not conf["ok"]:
+        _fail({"ticket": d.ticket, "error": f"no store: factory config failed: {conf.get('stderr') or ''}"})
+    d.models, d.max_spec = conf["models"], conf["max_rounds"]["spec"]
+    show = call("ticket", "show", d.ticket, "--json")
+    if not show["ok"]:
+        _fail({"ticket": d.ticket, "error": f"no such ticket: {show.get('stderr') or ''}"})
+    state = show["state"]
+    phase = d.phase or ("intake" if state in INTAKE_STATES else "build" if state in BUILD_STATES else None)
+    if phase == "build":
+        # factory: interim until T-0040 part B ports build.js; refused before anything is written.
+        raise Refused(f"{d.ticket} is {state}: the build phase of factory drive is not built yet; "
+                      "run the build Workflow script")
+    d.title = show["title"]
+    d.status = {"ticket": d.ticket, "title": d.title, "phase": phase, "pid": os.getpid(), "started": store.now(),
+                "updated": None, "running": [], "last": None, "ended": None}
+    d.write_status()
+    code = asyncio.run(d.run(state, (show.get("round") or {}).get("spec") or 0))
+    if code:
+        raise SystemExit(code)
+
+
+def _fail(result: dict) -> None:
+    print(json.dumps({"ok": False, **result}, ensure_ascii=False), flush=True)
+    raise SystemExit(1)
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
index ed65b60..1167da8 100644
--- a/factory/instance.template.yaml
+++ b/factory/instance.template.yaml
@@ -53,6 +53,9 @@ models:
   verifier: opus
   retro: fable
   clerk: haiku
+# Effort level per role for `factory drive`'s role processes (`claude -p --effort`); a role not listed
+# gets Claude Code's default. The Workflow scripts ignore it.
+# effort: {critic: high}
 ready_state:
   triage: ready-for-triage
   spec_writer: ready-for-spec-writer
diff --git a/factory/store.py b/factory/store.py
index de22021..bd61475 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -49,14 +49,16 @@ def now() -> str:
 STORE_GITIGNORE = ("# git worktrees the build half creates; they are checkouts, never store content\nworktrees/\nruns/*/wt/\n"
                    "# tripwire baselines: digests of the operator's live files, never committed\nruns/*/tripwire.yaml\n"
                    "# each run's scratch directory: its own temporary files, cleared when the ticket moves on\n"
-                   "runs/*/scratch/\n")
+                   "runs/*/scratch/\n"
+                   "# the driver's status files: a live view of one `factory drive` process, never committed\n"
+                   "drive/\n")
 
 
 def ensure_gitignore(root: Path) -> None:
     """The store keeps implementer worktrees under worktrees/ and checker checkouts under runs/<id>/wt/.
     Both are nested git checkouts: a store committed by directory must not pick them up. Nor may it
     pick up a run's tripwire baseline, runs/<id>/tripwire.yaml, which holds digests of live files, or
-    a run's temporary files under runs/<id>/scratch/."""
+    a run's temporary files under runs/<id>/scratch/, nor `factory drive`'s status files under drive/."""
     _ensure_block(root / ".gitignore", STORE_GITIGNORE)
 
 
diff --git a/tests/factory/test_drive.py b/tests/factory/test_drive.py
new file mode 100644
index 0000000..d8b2ddf
--- /dev/null
+++ b/tests/factory/test_drive.py
@@ -0,0 +1,303 @@
+"""`factory drive`, part A (T-0040): the intake phase run as `claude -p` processes, with no clerk.
+
+Black-box through `bin/factory` on a throwaway store (FACTORY_STATE) with the suite's fixture
+instance. A Python stand-in `claude`, written into tmp_path and put first on PATH, plays each role:
+it logs its argv, working directory and FACTORY_DISPATCH, then plays the next entry of its role's
+list in $STANDIN_PLAYS (the last one repeats): {"write": STATUS} writes output.md, {"say": text}
+writes nothing, {"fail": text} replies with is_error and exits 1; any entry may first "sleep".
+"""
+from __future__ import annotations
+
+import json
+import os
+import re
+import shutil
+import signal
+import subprocess
+import sys
+import tempfile
+import time
+from pathlib import Path
+
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
+
+STANDIN = '''#!{python}
+import json, os, pathlib, sys, time
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
+    text = "STATUS: %s\\nCONFIDENCE: high, stand-in\\nESCALATIONS: none\\n" % p["write"]
+    (cwd / "output.md").write_text(text)
+elif err:
+    text = p["fail"]
+print(json.dumps({{"type": "result", "is_error": err, "result": text, "session_id": "s-" + cwd.name,
+                  "total_cost_usd": 0.5, "num_turns": 3, "usage": {{"output_tokens": 7}}}}))
+sys.exit(1 if err else 0)
+'''
+
+TRIAGE_OK = {"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}]}
+
+
+class Store:
+    """A throwaway store with T-0001 ready for triage, and the stand-in `claude` first on PATH."""
+
+    def __init__(self, tmp_path: Path, instance: Path = FIXTURE_INSTANCE):
+        self.tmp = tmp_path
+        self.root = tmp_path / "state"
+        self.log = tmp_path / "claude.log"
+        bindir = tmp_path / "bin"
+        bindir.mkdir()
+        (bindir / "claude").write_text(STANDIN.format(python=sys.executable))
+        (bindir / "claude").chmod(0o755)
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_INSTANCE": str(instance),
+                    "PYTHONDONTWRITEBYTECODE": "1", "STANDIN_LOG": str(self.log),
+                    "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}"}
+        self.env.pop("FACTORY_DISPATCH", None)
+        req = tmp_path / "req.md"
+        req.write_text("# Fixture\n\nThe bot should do the thing.\n")
+        self.ok("ticket", "new", "--file", str(req))
+
+    def cli(self, *argv: str, plays: dict | None = None) -> subprocess.CompletedProcess:
+        env = {**self.env, "STANDIN_PLAYS": json.dumps(plays or {})}
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def drive(self, plays: dict, *extra: str) -> tuple[subprocess.CompletedProcess, dict]:
+        cp = self.cli("drive", "T-0001", *extra, plays=plays)
+        return cp, json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def ticket(self, tid: str = "T-0001") -> dict:
+        return yaml.safe_load((self.root / "tickets" / f"{tid}.yaml").read_text())
+
+    def runs(self) -> list[dict]:
+        return [yaml.safe_load(p.read_text()) for p in sorted(self.root.glob("runs/*/meta.yaml"))]
+
+    def calls(self) -> list[dict]:
+        return [json.loads(ln) for ln in self.log.read_text().splitlines()] if self.log.exists() else []
+
+    def events(self) -> list[str]:
+        return [json.loads(ln)["event"] for p in sorted((self.root / "log").glob("*.jsonl"))
+                for ln in p.read_text().splitlines() if ln.strip()]
+
+
+def test_an_approved_spec_stops_at_the_spec_gate_after_one_revision(tmp_path):
+    s = Store(tmp_path)
+    cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}, "--phase", "intake")
+    assert cp.returncode == 0, cp.stderr
+    assert res == {"ticket": "T-0001", "state": "awaiting-spec-gate", "rounds": 2, "ok": True}
+    t = s.ticket()
+    assert t["status"] == "awaiting-spec-gate" and t["round"]["spec"] == 2 and t["in_flight"] == []
+    assert [(m["role"], m["status"]) for m in s.runs()] == [
+        ("triage", "ACCEPT"), ("spec_writer", "READY-FOR-CRITIC"), ("critic", "REVISE"),
+        ("spec_writer", "READY-FOR-CRITIC"), ("critic", "APPROVE")]
+    assert len(s.calls()) == 5
+
+
+def test_a_critic_still_revising_at_the_round_limit_parks_with_max_rounds(tmp_path):
+    s = Store(tmp_path)
+    cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "REVISE"}]}, "--phase", "intake")
+    assert cp.returncode == 0, cp.stderr
+    assert res["state"] == "parked" and res["reason"] == "max rounds"
+    assert s.ticket()["status"] == "parked" and s.ticket()["parked"]["reason"] == "max rounds"
+
+
+def test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message(tmp_path):
+    s = Store(tmp_path)
+    cp, res = s.drive({"triage": [{"say": "still waiting on my commands"}]})
+    assert cp.returncode == 0, cp.stderr
+    assert res["state"] == "parked"
+    parked = s.ticket()["parked"]
+    assert parked["reason"] == "EMPTY-OUTPUT from triage"
+    assert [m["status"] for m in s.runs()] == ["EMPTY-OUTPUT", "EMPTY-OUTPUT"]
+    for m in s.runs():
+        kept = (s.root / "runs" / m["run_id"] / "last-message.md").read_text()
+        assert kept == "still waiting on my commands\n"
+
+
+def test_a_failed_role_process_is_recorded_killed_and_parks_once(tmp_path):
+    s = Store(tmp_path)
+    cp, res = s.drive({"triage": [{"fail": "usage limit reached"}]})
+    assert cp.returncode == 0, cp.stderr
+    assert res["state"] == "parked"
+    assert s.ticket()["parked"]["reason"] == "agent call failed: triage: usage limit reached"
+    assert [m["status"] for m in s.runs()] == ["KILLED"] and s.ticket()["in_flight"] == []
+    assert len(s.calls()) == 1  # no retry
+    assert "run.killed" in s.events()
+
+
+def test_a_role_that_prints_no_json_is_a_failed_call_named_by_its_stderr(tmp_path):
+    s = Store(tmp_path)
+    (tmp_path / "bin" / "claude").write_text("#!/bin/sh\necho 'not json'\necho 'bad flag --x' >&2\necho >&2\n")
+    cp, res = s.drive({})
+    assert cp.returncode == 0, cp.stderr
+    assert s.ticket()["parked"]["reason"] == "agent call failed: triage: bad flag --x"
+    meta = s.runs()[0]
+    assert meta["status"] == "KILLED" and meta["claude"] is None
+    assert (s.root / "runs" / meta["run_id"] / "reply.json").read_text() == "not json\n"
+
+
+def test_triage_reject_clarify_and_needs_human_route_as_the_script_does(tmp_path):
+    for n, (status, state, reason) in enumerate([("REJECT", "closed", None),
+                                                  ("CLARIFY", "waiting-requester", None),
+                                                  ("NEEDS-HUMAN", "parked", "NEEDS-HUMAN from triage"),
+                                                  ("MAYBE", "parked", "harness-bug: unknown STATUS MAYBE from triage")]):
+        (tmp_path / str(n)).mkdir()
+        s = Store(tmp_path / str(n))
+        cp, res = s.drive({"triage": [{"write": status}]})
+        assert cp.returncode == 0, cp.stderr
+        assert (res["state"], s.ticket()["status"]) == (state, state)
+        assert ((s.ticket()["parked"] or {}).get("reason")) == reason
+
+
+def test_each_role_process_gets_its_prompt_model_and_tool_limits_and_no_marker(tmp_path):
+    s = Store(tmp_path)
+    s.env["FACTORY_DISPATCH"] = "1"  # started marked: the role processes still never see it
+    cp, _ = s.drive({**TRIAGE_OK, "critic": [{"write": "APPROVE"}]}, "--phase", "intake")
+    assert cp.returncode == 0, cp.stderr
+    tmp = os.path.realpath(tempfile.gettempdir())
+    models = {m["run_id"]: m["model"] for m in s.runs()}
+    assert len(s.calls()) == 3
+    for c in s.calls():
+        run = os.path.realpath(c["cwd"])
+        assert c["dispatch"] is None
+        assert c["argv"] == [
+            "-p", f"Your entire input is the file {run}/input.md; read it first and follow it. "
+                  f"Write your complete output to {run}/output.md and return the same text.",
+            "--model", models[Path(run).name], "--output-format", "json", "--permission-mode", "auto",
+            "--append-system-prompt-file", f"{run}/system-prompt.txt",
+            "--tools", "Read,Grep,Glob,Bash,Write,WebFetch,WebSearch",
+            "--allowedTools", f"Read,Grep,Glob,Bash,WebFetch,WebSearch,Edit(/{run}/output.md),"
+                              f"Edit(/{run}/scratch/**),Edit(/{tmp}/**)"]
+
+
+def test_prompt_mode_replace_passes_the_role_prompt_as_the_whole_system_prompt(tmp_path):
+    s = Store(tmp_path)
+    cp, _ = s.drive({"triage": [{"write": "REJECT"}]}, "--prompt-mode", "replace")
+    assert cp.returncode == 0, cp.stderr
+    argv = s.calls()[0]["argv"]
+    run = os.path.realpath(s.calls()[0]["cwd"])
+    assert argv[argv.index("--system-prompt-file") + 1] == f"{run}/system-prompt.txt"
+    assert "--append-system-prompt-file" not in argv
+
+
+def role_argv(*args) -> list[str]:
+    """factory.drive.role_argv, run in the harness checkout (the suite's `factory` is tests/factory)."""
+    code = "import json, sys; from factory import drive; print(json.dumps(drive.role_argv(*json.loads(sys.argv[1]))))"
+    cp = subprocess.run([sys.executable, "-c", code, json.dumps(args)], capture_output=True, text=True, cwd=REPO,
+                        check=True)
+    return json.loads(cp.stdout)
+
+
+def test_the_implementer_alone_gets_edit_and_its_worktree():
+    argv = role_argv("implementer", "/s/runs/run-0001-implementer", "opus", "append", "/s/worktrees/T-1.1", None)
+    opts = dict(zip(argv[2::2], argv[3::2]))
+    assert opts["--tools"].split(",")[-1] == "Edit"
+    assert opts["--allowedTools"].endswith(",Edit(//s/worktrees/T-1.1/**)")
+    assert opts["--add-dir"] == "/s/worktrees/T-1.1"
+    checker = role_argv("reviewer", "/s/runs/run-0002-reviewer", "fable", "append", "/s/runs/x/wt", None)
+    assert "Edit" not in checker[checker.index("--tools") + 1].split(",") and "--add-dir" not in checker
+
+
+def test_a_configured_effort_is_passed_to_its_role_only(tmp_path):
+    inst = tmp_path / "instance"
+    shutil.copytree(FIXTURE_INSTANCE, inst)
+    with (inst / "instance.yaml").open("a") as f:
+        f.write("effort: {triage: low}\n")
+    (tmp_path / "s").mkdir()
+    s = Store(tmp_path / "s", instance=inst)
+    cp, _ = s.drive({**TRIAGE_OK, "critic": [{"write": "APPROVE"}]})
+    assert cp.returncode == 0, cp.stderr
+    effort = [c["argv"][c["argv"].index("--effort") + 1] if "--effort" in c["argv"] else None for c in s.calls()]
+    assert effort == ["low", None, None]
+
+
+def test_each_run_keeps_its_reply_and_records_its_cost(tmp_path):
+    s = Store(tmp_path)
+    cp, _ = s.drive({"triage": [{"write": "REJECT"}]})
+    assert cp.returncode == 0, cp.stderr
+    meta = s.runs()[0]
+    reply = json.loads((s.root / "runs" / meta["run_id"] / "reply.json").read_text())
+    assert meta["claude"] == {"session_id": "s-" + meta["run_id"], "total_cost_usd": 0.5, "num_turns": 3,
+                              "usage": {"output_tokens": 7}}
+    assert reply["session_id"] == meta["claude"]["session_id"]
+
+
+def test_run_finish_with_a_reply_that_is_not_a_json_object_records_claude_null(tmp_path):
+    s = Store(tmp_path)
+    rid = s.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]
+    (tmp_path / "reply.json").write_text("[1, 2]\n")
+    s.ok("run", "finish", rid, "--reply", str(tmp_path / "reply.json"))
+    assert "claude" in s.runs()[0] and s.runs()[0]["claude"] is None
+
+
+def test_every_step_line_names_the_ticket_and_the_status_file_shows_the_end(tmp_path):
+    s = Store(tmp_path)
+    cp, res = s.drive({**TRIAGE_OK, "critic": [{"write": "APPROVE"}]})
+    assert cp.returncode == 0, cp.stderr
+    lines = cp.stdout.strip().splitlines()
+    assert len(lines) > 9 and all(ln.startswith('T-0001 "Fixture": ') for ln in lines[:-1])
+    assert 'T-0001 "Fixture": -> awaiting-spec-gate' in lines
+    st = yaml.safe_load((s.root / "drive" / "T-0001.yaml").read_text())
+    assert (st["ticket"], st["title"], st["phase"], st["running"]) == ("T-0001", "Fixture", "intake", [])
+    assert st["ended"] == res and st["last"] == lines[-2]
+    assert "drive/" in (s.root / ".gitignore").read_text().splitlines()
+
+
+def test_a_ticket_in_no_dispatch_state_ends_at_once(tmp_path):
+    s = Store(tmp_path)
+    s.ok("ticket", "transition", "T-0001", "--to", "waiting-requester", "--by", "t")
+    cp, res = s.drive({})
+    assert cp.returncode == 0, cp.stderr
+    assert res == {"ticket": "T-0001", "state": "waiting-requester", "note": "nothing to dispatch from this state",
+                   "ok": True}
+    assert s.calls() == []
+
+
+def test_a_stopped_driver_kills_its_role_records_the_run_and_resumes(tmp_path):
+    s = Store(tmp_path)
+    env = {**s.env, "STANDIN_PLAYS": json.dumps({"triage": [{"sleep": 60, "write": "ACCEPT"}]})}
+    p = subprocess.Popen([str(BIN), "drive", "T-0001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
+                         text=True, env=env, cwd=REPO)
+    status = s.root / "drive" / "T-0001.yaml"
+    deadline = time.monotonic() + 30
+    while time.monotonic() < deadline and not (status.exists() and (yaml.safe_load(status.read_text()) or {}).get("running")
+                                               and s.calls()):
+        time.sleep(0.1)
+    running = yaml.safe_load(status.read_text())["running"]
+    assert [(r["run"], r["role"]) for r in running] == [("run-0001-triage", "triage")]
+    child = s.calls()[0]["pid"]
+    p.send_signal(signal.SIGTERM)
+    out, _ = p.communicate(timeout=30)
+    assert p.returncode == 128 + signal.SIGTERM
+    assert json.loads(out.strip().splitlines()[-1]) == {"ok": False, "ticket": "T-0001", "stopped": "SIGTERM"}
+    assert s.runs()[0]["status"] == "KILLED"
+    t = s.ticket()
+    assert (t["status"], t["in_flight"], t["parked"]) == ("ready-for-triage", [], None)
+    try:
+        os.kill(child, 0)
+        alive = True
+    except ProcessLookupError:
+        alive = False
+    assert not alive
+    st = yaml.safe_load(status.read_text())
+    assert st["running"] == [] and st["ended"]["stopped"] == "SIGTERM"
+    cp, res = s.drive({"triage": [{"write": "REJECT"}]})  # no --phase: ready-for-triage selects intake
+    assert cp.returncode == 0, cp.stderr
+    assert res["state"] == "closed" and len(s.calls()) == 2
+    assert re.search(r"^T-0001 \"Fixture\": start triage run-0002-triage$", cp.stdout, re.M)
diff --git a/tests/factory/test_run_scratch.py b/tests/factory/test_run_scratch.py
index 9cab907..c5e3667 100644
--- a/tests/factory/test_run_scratch.py
+++ b/tests/factory/test_run_scratch.py
@@ -124,9 +124,9 @@ def test_a_new_store_gitignore_is_the_full_commented_block_once(tmp_path):
     s.finish(s.start(tid))
     s.start(tid)
     lines = s.gitignore()
-    for ln in ("worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml", "runs/*/scratch/"):
+    for ln in ("worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml", "runs/*/scratch/", "drive/"):
         assert lines.count(ln) == 1, (ln, lines)
-    assert sum(ln.startswith("#") for ln in lines) == 3
+    assert sum(ln.startswith("#") for ln in lines) == 4
 
 
 def test_an_existing_store_gitignore_gains_only_the_missing_lines(tmp_path):
@@ -136,7 +136,7 @@ def test_an_existing_store_gitignore_gains_only_the_missing_lines(tmp_path):
     s.finish(s.start(tid))
     s.start(tid)
     assert s.gitignore() == ["# kept", "worktrees/", "mine/", "runs/*/wt/", "runs/*/tripwire.yaml",
-                             "runs/*/scratch/"]
+                             "runs/*/scratch/", "drive/"]
 
 
 def test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line(tmp_path):
@@ -144,7 +144,7 @@ def test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line
     tid = s.request()
     (s.root / ".gitignore").write_text("worktrees/\nruns/*/wt/\nruns/*/tripwire.yaml")
     s.start(tid)
-    assert s.gitignore() == ["worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml", "runs/*/scratch/"]
+    assert s.gitignore() == ["worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml", "runs/*/scratch/", "drive/"]
 
 
 def test_moving_a_ticket_on_clears_its_finished_runs_scratch_only(tmp_path):

## Human ruling

Operator ruling, 2026-10-09, on run-0405's BLOCKED report.

The "stopped driver" scenario's count was a defect in the spec, not in your build. Design A.7 names the run id both in the `running` list and on the `last:` line, so `grep -c 'run-0001-triage'` counts 2. The approved spec is amended (intent unchanged): the check now counts only the `running` list's entry, `grep -c '^- run: run-0001-triage'`, and still expects `running=1`. Keep design A.7 as built. Re-run that scenario as now written, confirm the rest of the acceptance results still hold on your head, and hand off as usual.
