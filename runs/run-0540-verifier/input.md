## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
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
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0540-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0540-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0540-verifier/wt` (branch `factory/T-0054.1`, base `308d03857bced6dc4f33e62812d83c52fd73e4b2`, head `e12ca713eb3b8594445773d44e87790fd480faa1`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0054.1

T-0054.1 / Workflow builds stop parking on the clerk's relays: the harness writes each role's model into a launch copy of the script, the scripts parse a reformatted reply, and `resolve` has a route back from a park after a finished implementer (#109, #112)
Depends on: none
Parallel-safe: yes

Parent: T-0054, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks
- An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy
- A launch copy launched for another instance returns an error naming its own and runs nothing
- A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies
- A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it
- The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked
- Unmarked writes from inside the target are refused while a run is in flight, init included
- The refusal names the throwaway store and not the marker
- A harness acceptance is refused while a run is in flight
- A launch copy is written unmarked while a run is in flight, and the target is unchanged
- The README, the design doc and the changelog describe the launch copy and the route back to checks
- The suite passes, no existing test changes, and every test file this change adds fails on the base
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0054/v3.md`

=== proposal.md
## Problem

The clerk, a small agent that copies the factory's command output back to the workflow scripts, sometimes miscopies it. Each slip stops a build partway through, and the operator, who launches the factory's runs and answers its stops, has to find the cause and restart the build by hand. This store holds four such stops from one kind of slip, all on 2026-10-13, three of them on one piece of work.

How the clerk comes into it. The factory moves a ticket through its roles in one of two ways. The older way is a pair of workflow scripts, `factory/workflows/intake.js` and `build.js`. They are JavaScript programs that Claude Code's Workflow tool runs, and each starts the roles (triage, spec writer, implementer, reviewer, verifier and so on) as separate agents. A workflow script cannot read a file or run a command. Each time it needs the factory's records, which the factory calls its store (tickets, runs and results), it asks the clerk to run one command of the harness, the factory's own command-line program `factory`, and to copy that command's output back word for word. The script parses the copied text as JSON and decides the next step.

Two of the clerk's slips stop a build:

- **It changes a value.** At the start of a run the script asks the harness for the factory's configuration, which names the model each role runs on. The clerk has reported the wrong model for a role, for example the verifier as `fable` where the instance says `opus`. An instance is a repository's `.factory/` directory; among other settings it names each role's model. The harness refuses to start a role on a model the instance does not name, which is the right call. The sub-ticket, one PR-sized piece of a ticket, still stops, or "parks", until a human resumes it.
- **It reformats.** Once, on the other repository this factory runs on, the clerk returned a one-line JSON reply spread over many lines. The script reads JSON only one line at a time, found none, and parked a sub-ticket whose implementer had already finished its work. The operator answers a park with one of the `factory resolve` commands, and none of them covers this one. The operator resumed it with raw state edits.

This change makes three fixes. First, the operator launches a **launch copy** instead of the script itself. A launch copy is the workflow script with the instance's models, round limits and store written into one line by a harness command, so no agent relays them. Second, a reply spread over several lines still parses. Third, the park after a finished implementer gets its own `resolve` command. The harness's refusal of a wrong model stays as a backstop. The clerk keeps relaying every other command. `factory drive`, the newer runner that needs no clerk, does not change.

## Root cause

- #109: `build.js:225-226` and `intake.js:146-147` take each role's model from a model's copy of `factory config`'s output, so the model a role runs on is only as reliable as that copy.
- #112: `clerk()` (`build.js:41-58`, `intake.js:50-66`) parses the relayed stdout only line by line, so one JSON value spread over lines never parses.
- No resume command: `resolve` in `factory/human.py` has no route from a `ready-for-implementer` park to `checks-in-flight`.

## Out of scope

- `run start`'s refusal of a model the instance does not name (T-0050) stays as it is.
- `factory drive` and `factory/drive.py` do not change.
- The clerk keeps relaying every command except `factory config` in a launch copy. Retiring it is #89.
- The scripts launched as they are keep reading the configuration through the clerk (Decision 6).
- No change to `agents/`, `docs/prompts/`, any `instance.yaml` or `dev/issues.md`. The operator updates the issue index after merge, as usual.
- `MAX_PR` in `build.js` is set at line 226 and never read. It stays; it is noted here only.
- README's line budget does not change (Decision 13).
- Cut as speculative: the copy defaulting `repo` to its harness; the copy checking its recorded harness revision at run time; a resume route for tripwire or conflict-limit parks.

## Open questions

none

## Decisions

1. The command is `factory launch-script intake|build`, and what it writes is a launch copy. Each call writes `<name>.js` into a new directory `factory-launch-<random>` under the temporary directory and prints `{"ok": true, "script": <path>, "source", "harness_revision", "instance"}`. Rejected: a fixed path under the instance's `.factory/`. A later launch would rewrite a script a running workflow came from. A run against a throwaway store would also write into the live instance's directory, which here is a protected path: one the instance lists as needing the operator's acceptance before any ticket may change it.
2. A launch copy differs from its script in one line. The scripts gain the line `const LAUNCH = null`. The copy holds `const LAUNCH = {...}` instead: one JSON object with `written_by: "factory launch-script"`, the source path, the harness revision, the instance, and `models`, `max_rounds` and `state_dir` as `factory config` prints them. The file is read-only. This answers the request's Risk. A launch copy is told apart from an edited script because the harness command alone writes it, into a directory the command creates. It is a one-line change to the reviewed script, and that line names the command, the source and the revision.
3. A launch copy asks no clerk for the configuration. It uses `LAUNCH` as the reply `factory config` would give, so the clerk's own model comes from the instance too.
4. `launch-script` refuses exactly where `config` refuses: with no instance, with uncommitted harness edits, or when the instance has not accepted the running harness revision. To get that, it joins the read-only list of the live-store fence, the harness's refusal of store writes that lack the dispatcher's marker while a role run is in flight. It writes no store file. This modifies live-store-guard's first requirement. Rejected: fencing it as a write, which would refuse a launch while another ticket's run is in flight, where `config` stays open.
5. A launch copy sends every store command to the instance it records. Given an `instance` argument that names another instance, it returns an error naming its own before any store command runs. The copy's models and store path belong to its instance. Mixed with another, agents would read one store's runs while the clerk writes another's.
6. The scripts launched as they are keep their clerk path, and README tells the operator to launch the copy. This keeps every scenario and suite test that runs the scripts directly, and T-0050's park as the backstop. Rejected: a script that refuses to run without a copy, which breaks those checks and would need a test-only switch.
7. `clerk()` in both scripts first parses the whole trimmed stdout, then falls back to the last-line scan. Every rule after the parse is unchanged.
8. The resume command is `factory resolve <id> --to checks`. It accepts a sub-ticket that meets four conditions: it is parked; it was parked from `ready-for-implementer`; its reason starts `harness-bug:`; and its newest implementer run started after it last entered `ready-for-implementer` and finished `READY-FOR-REVIEW`. The event log's order decides "after", because the store's timestamps are whole seconds.
9. The route reads the branch tip as `ticket head` does, through one shared definition. It applies the round step the build applies on this move (`pr:init`): a first round's 0 becomes 1, and a later round is unchanged. That is "round unchanged, as the script would have", and it is what the operator ran by hand for #112. It records a `resolve-<n>.yaml` and a `human.resolved` event of kind `to-checks`.
10. Only `harness-bug:` parks qualify, the class #112 belongs to: a store command failed after the implementer finished. A tripwire park and the conflict-limit park keep their documented routes.
11. A head from a conflict run that did not merge the integration branch still moves to checks. The join then sends it back to its implementer as a conflict (`factory/gates.py:203-206`), as it does after the script's own move.
12. The new tests run the scripts under node inside the suite, as `tests/factory/_fixtures.py`'s `BUILD_DRIVER` already does. T-0023's "the suite does not need node" no longer holds.
13. README keeps its 1,110-line budget. Part F names the lines each edit replaces, and its edits together add at most one line, so README ends at 1,109 lines or fewer. Rejected: raising the budget, which nothing here needs.
14. The changelog entry takes the next free number and opens `<n>. After issue #109 `.
15. Each `launch-script` call first removes earlier launch copies: every `factory-launch-*` directory under the temporary directory that is more than one hour old (by its modification time) and holds exactly one file, `intake.js` or `build.js`, containing `"written_by": "factory launch-script"`. It removes nothing else. The Workflow tool keeps its own copy of a script once launched, so an old launch copy is no longer read (operator, at the gate). Rejected: removing every earlier copy, because another session sharing the temporary directory may have written one seconds before its own Workflow call; and leaving them for the system to clear.

## Risk

- Blast radius: every Workflow-tool run (both scripts change), `factory resolve`, the CLI's parser and fence list, and the store helpers that `ticket head` and `ticket transition` use.
- I could not run Claude Code's Workflow tool here. It may not load a script from the temporary directory. Claude Code's auto-mode classifier, its check on what a session running without per-step approval may do, may refuse to launch the copy as it once refused a hand-edited `build.js`. The scripts launched as they are still work, so a refusal costs only the fix (Operator step 1).
- The scripts launched as they are can still receive a wrong model. T-0050's run-start refusal then parks the ticket, as today.
- harness-code's current truth pins the definitions of `common.py`, `drift.py`, `gates.py`, `human.py` and `setup.py`, `factory/cli.py` under 900 lines, 12 `gitops.repo_root()` sites and one `"ticket.transition"` literal in the CLI modules and one in `store.py`. `design.md` places the new code so all of them hold.
- harness-code's current truth also holds "Splitting the command-line code changes no definition". Its scenario (`t0047-moved.py`) compares `git merge-base HEAD main` with HEAD and expects `added=0 removed=0`. That scenario measures T-0047's own split, so on this ticket's branch it reports this change's new and moved definitions, as it has for every `factory/` change since T-0047. A verifier running current truth should not read that count as a regression.
- Protected paths: `factory/**`

## Operator steps

1. After the merge, move the runtime checkout to the new revision and accept it. The runtime checkout, `$RUNTIME` (`~/dev/spec-factory-harness`), is the separate copy of this repository the factory runs from; it moves only when you upgrade it. To accept it, give the first `factory` command you run against this instance `--accept-harness <revision>`, the flag that lets an instance run on a harness revision it has not used before. Then launch the next build from a copy: run `$RUNTIME/bin/factory launch-script build`, and call the Workflow tool with `scriptPath` set to the `script` it prints. Check that the Workflow tool loads the copy and that Claude Code's auto-mode classifier lets it run. If either refuses, report it; launching `build.js` itself still works as before, with its models relayed by the clerk.
2. Tell the runner session of the other target, the Nanobot chat-bot repository this runtime also serves, to launch copies too: the same command, run from that repository.

=== design.md
## Proposed change

Four parts in one PR. The prototype of A to D, with no tests or docs, changed 75 lines of `factory/` (67 added, 8 removed); with E and F the change should stay under 400 lines.

**A. `factory launch-script intake|build` writes a launch copy.**
- New module `factory/launch.py` holds the command, and the one definition of the values `factory config` prints (`models`, `max_rounds`, `state_dir`). `config` in `factory/cli.py` uses that definition too. A new module keeps harness-code's pinned definition lists of `setup.py` and `common.py` unchanged; it must not import `factory.cli`.
- `factory/cli.py`: a `launch-script` subparser with one positional argument, choices `intake` and `build`. Add `("launch-script", None)` to `READ_ONLY`, so the command takes `config`'s path through `main()`: the instance is required, and the harness lock is checked on the instance's own store.
- The command reads `factory/workflows/<name>.js` from the running harness checkout (`instance.HARNESS`). If the line `const LAUNCH = null` does not occur exactly once, it refuses with exit 2 and writes nothing. Otherwise it creates a directory with `tempfile.mkdtemp(prefix="factory-launch-")` and writes `<name>.js` there. The copy is the script with that one line replaced by `const LAUNCH = <json>`. The JSON object, written with `json.dumps(..., ensure_ascii=False)`, holds `written_by` (`"factory launch-script"`), `source` (the script's absolute path), `harness_revision`, `instance` (the instance's path as `factory paths` prints it), `models`, `max_rounds` and `state_dir`. The file is made read-only (0444). The command prints `{"ok": true, "script", "source", "harness_revision", "instance"}`.
- Before writing, it removes earlier launch copies as Decision 15 says: under `tempfile.gettempdir()`, each `factory-launch-*` directory whose modification time is more than 3,600 seconds old and which holds exactly one file, `intake.js` or `build.js`, whose text contains `"written_by": "factory launch-script"`. Any other directory, and any error while checking or removing one, is skipped silently; cleanup never changes the command's exit or output.

**B. Both workflow scripts honour a launch copy.**
- Add, above `INSTANCE`, a comment saying that `factory launch-script` writes a copy of the script with the next line set to the instance's values, and the line `const LAUNCH = null`.
- `const INSTANCE = LAUNCH ? LAUNCH.instance : args.instance`, so `ENV` carries the recorded instance.
- Just before the config step: when `LAUNCH` is set and `args.instance` is given and differs from `LAUNCH.instance`, return `{ ticket, error }`, where the error reads `launch copy written for instance <LAUNCH.instance>, launched with <args.instance>`.
- The config step becomes `const cfg = LAUNCH ? { ok: true, ...LAUNCH } : <today's clerk call of factory config>`. The lines after it stay as they are.
- Update the `// args:` header comments to say a launch copy takes its instance from the copy.

**C. `clerk()` parses a reply spread over lines (both scripts).** Trim the stdout once, try `JSON.parse` on the whole text, and only when that fails run today's last-line scan over its lines. Everything after the parse is unchanged.

**D. `factory resolve <id> --to checks`.**
- In `resolve` (`factory/human.py`), a `--to checks` branch, written inside `resolve` so `human.py`'s top-level definitions stay as harness-code pins them. Before any write it requires: status `parked`; `parked.from == "ready-for-implementer"`; a reason starting `harness-bug:`; and the newest implementer run of the ticket started after the ticket last entered `ready-for-implementer` and finished `READY-FOR-REVIEW`. Otherwise it refuses with exit 2, writing nothing, with `--to checks applies to a sub-ticket parked by a harness-bug from ready-for-implementer after its implementer run finished READY-FOR-REVIEW; <id> is <status> (<reason or 'no park'>)`. Any other `--to` value is refused with `--to accepts only spec-gate or checks`.
- The "newest implementer run since it last entered ready-for-implementer" test reads the event log through `store.log_lines` in file and line order. A move into that state is an event of the ticket whose `to`, or for `ticket.created` whose `status`, is `ready-for-implementer`. The newest implementer `run.started` must come after the last such move, and that run's `run.finished` must carry `READY-FOR-REVIEW`. Match moves by their field, not by event name: harness-code pins the `"ticket.transition"` literal to one place in `store.py`.
- On acceptance: read the branch tip into the ticket exactly as `ticket head` does, conflict bookkeeping included. Apply the `pr:init` round step. Then `move("checks-in-flight", "to-checks", {"head": head})`, which writes the history entry, `resolve-<n>.yaml` and the `human.resolved` event.
- Shared definitions, placed so harness-code's pins hold:
  - `ticket head`'s body (`factory/gates.py:12-33`) becomes one function in `factory/store.py`, used by `ticket head` and the route. It keeps its single `gitops.repo_root()` call, imported lazily inside the function, as `store.py` already imports `instance`. The site count stays 12, and `gates.py` keeps its definitions; `ticket_head` only prints the function's result.
  - `_apply_round` moves from `factory/cli.py` to `factory/store.py` as one definition, used by `ticket transition` and the route. `human.py` may not import `factory.cli`.
  - The log query lives in `factory/store.py` beside `log_lines`.
- The parser's `--to` gets help text naming `spec-gate` and `checks`.

**E. Tests: new files only, under `tests/factory/`.** Name them for what they test, for example `test_launch_copy.py`. Use the suite's helpers through relative imports (`._cli`, `._fixtures`) and edit no existing file. Each test keeps to its own `tmp_path`, with `TMPDIR` pointed inside it, because the suite runs in parallel. Cover:
- a launch copy of each script is a one-line change naming the revision and instance; `launch-script` is refused where `config` is, writing no copy; and it runs unmarked while a run is in flight;
- `launch-script` removes a launch copy over an hour old and keeps a recent copy and a `factory-launch-*` directory that holds no launch copy;
- `build.js`, run from a launch copy under node with a stand-in clerk that retypes a model in the config reply, launches every role on the instance's model;
- both scripts proceed when every clerk reply is pretty-printed;
- `resolve --to checks` on #112's park returns the sub-ticket to its checks at the branch tip, and is refused, writing nothing, on each other park the scenarios list.

**F. Documents.** README has 2 lines of room under its 1,110-line budget (1,108 lines on 308d038). Each README edit below names the lines it replaces; together they add at most one line.
- `README.md`:
  - "Starting a run": replace `README.md:699-711`, the `paths` block and the paragraph that launches the scripts (13 lines), with at most 13 lines that say: the session runs `$RUNTIME/bin/factory launch-script intake` (or `build`) and passes the printed `script` as `scriptPath`; a launch copy is the script with the instance's models, round limits and store written into one line, so no agent relays them, and it names the harness revision and instance it was written for; it has not yet run on a real ticket; args are `{ticket, repo: <runtime>}`, since the copy carries the instance; and, kept from today's text, the `inlineRoles: true` advice and that the intake script has nothing to do past the spec gate. `factory paths` stays documented in "Where things live" (`README.md:1096`). A draft that fits in 13 lines:

    ~~~
    A Claude Code session in the target repo has the runtime write a launch copy of the script:

    ```
    $RUNTIME/bin/factory launch-script intake   # or build; prints the copy's path as "script"
    ```

    A launch copy is the script with the instance's models, round limits and store written into one
    line, so no agent relays them; it names the harness revision and instance it was written for. It
    has not yet run on a real ticket. The session calls the Workflow tool with `scriptPath` set to the
    printed `script` and args `{ticket, repo: <runtime>}`; after the spec gate, the same with `build`.
    Add `inlineRoles: true` on every target for now: `agents/` ships agent definitions only for the
    intake roles and the planner, so a build without it fails at the first implementer call. "What
    depends on Claude Code" says what it changes. The intake script has nothing to do past the gate.
    ~~~

  - "Where a human decides": add `launch-script` to the sentence "A write is any command except ...;" at `README.md:831-832`, keeping that sentence's form, rewrapped within its paragraph with no added line. Add `--to checks` to the **Unstick** row (`README.md:859`, one table line), with what it is for (a `harness-bug:` park from ready-for-implementer after the implementer finished READY-FOR-REVIEW: the sub-ticket returns to its checks at its branch tip) and that it has not yet run on a real ticket, as README's "Maintaining this page" rule asks of every entry.
  - The run-start sentence at `README.md:251-252`, about a model the clerk misreported, also says that a launch copy carries the models itself. Its paragraph (`README.md:249-254`) may grow by one line at most; this is the one added line.
  - Bump the status date at `README.md:9` in place.
  - If the text cannot fit these bounds, stop and report it rather than cutting other README content or exceeding 1,110 lines.
- `docs/design.md`:
  - line 44, limit (1): one sentence on the launch copy and on parsing a reply spread over lines;
  - line 64: add `launch-script` to the read-only list;
  - line 109: the `--to checks` route beside the harness-bug ruling rule.
  - None of these lines is a prompt block, so `docs/prompts/` does not change.
- `docs/changelog.md`: one entry with the next free number, opening `<n>. After issue #109 ` and naming #112, `launch-script` and `--to checks`.

## Tests to change

none. On the prototype of parts A to D, the suite printed `594 passed` with no existing test changed. No existing test pins `--to accepts only spec-gate`, the read-only list or the clerk's parse.

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: A Workflow run launched from its launch copy runs each role on the instance's model, whatever the clerk relays
A copy of `factory/workflows/build.js` or `factory/workflows/intake.js` written by `factory launch-script` SHALL launch each role, and send `run start` its `--model`, on the model the instance names, and SHALL ask no clerk for the configuration. The scripts launched as they are SHALL still park at a role's run start when the relayed configuration names another model.

#### Scenario: A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. The models printed are the ones this repository's `.factory/instance.yaml` names (reviewer `fable`, verifier `opus`, implementer `opus`, triage `opus`). Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" (current truth, build-dispatch) run once. T-0001.1 waits at its checks, and the clerk relays `factory config` with the verifier's model retyped to `fable`, as in #109.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0054-wf.mjs <<'EOF'
// node t0054-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script, a launch copy or the script itself, on <ticket> of the store $FACTORY_STATE with the target
// $FACTORY_REPO. Each clerk command runs for real (sh -c, from this checkout). Two knobs change what
// the clerk relays, as the clerk did on real runs: T54_SWAP=<role>=<model> names <model> for <role>
// in any reply that lists `models`; T54_PRETTY=1 relays every JSON reply pretty-printed over several
// lines. T54_INSTANCE, when set, is passed to the script as its `instance` argument. Each role call
// prints `agent <role> <ticket> model=<the model it was launched on>`. An implementer commits one file
// in its worktree. Each role writes an output with the STATUS T54_PLAYS ({"<role>": "<STATUS>"}) gives
// it (a checker with the run's head as its Commit: line, the verifier with "Gate suite: PASS") and
// returns the same text. Prints each park as `park <id>: <reason>`, then `result <the script's
// return value as JSON>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const plays = JSON.parse(process.env.T54_PLAYS || '{}')
const [swapRole, swapModel] = (process.env.T54_SWAP || '=').split('=')
const sh = (cmd, cwd) => spawnSync('sh', ['-c', cmd], { cwd, encoding: 'utf8' })
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt, opts) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = sh(m[1], process.cwd())
    let stdout = cp.stdout, j = null
    try { j = JSON.parse(stdout.trim().split('\n').pop()) } catch (e) { j = null }
    if (j && swapRole && j.models) { j.models[swapRole] = swapModel; stdout = JSON.stringify(j) + '\n' }
    if (j && process.env.T54_PRETTY) stdout = JSON.stringify(j, null, 2) + '\n'
    return { stdout, exit: cp.status, stderr: cp.stderr }
  }
  console.log(`agent ${opts.label} model=${opts.model}`)
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const meta = readFileSync(`${r[1]}/meta.yaml`, 'utf8')
  const wt = (meta.match(/^worktree: '?([^'\n]+)/m) || [])[1]
  if (r[2] === 'implementer' && wt) sh('echo work > work.txt && git add work.txt && git -c user.email=f@x -c user.name=f commit -qm work', wt)
  const head = (meta.match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = (head && r[2] !== 'implementer' ? `Commit: ${head}\n` : '') + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${plays[r[2]] || 'NONE'}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true, ...(process.env.T54_INSTANCE ? { instance: process.env.T54_INSTANCE } : {}) },
  agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`result ${JSON.stringify(res)}`)
EOF
cat > ${TMPDIR:-/tmp}/t0054-impl.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# ready for its implementer with no branch yet. `implement <STATUS>` runs one implementer run on it
# by hand, as the build does: run start, one commit on the sub-ticket's branch, an output with that
# STATUS, run finish. It sets $H to the branch tip.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
implement() {
  R=$(bin/factory run start --role implementer --ticket T-0001.1 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
  W=$(sed -n "s/^worktree: '\{0,1\}\([^']*\)'\{0,1\}$/\1/p" $FACTORY_STATE/runs/$R/meta.yaml)
  (cd $W && echo $R > work.txt && git add work.txt && git -c user.email=f@x -c user.name=f commit -qm work)
  printf 'STATUS: %s\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' "$1" > $FACTORY_STATE/runs/$R/output.md
  bin/factory run finish $R >/dev/null
  H=$(git -C $T23/t rev-parse factory/T-0001.1)
}
EOF
```

- WHEN `(for side in copy script; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && export T54_SWAP=verifier=fable T54_PLAYS='{"reviewer": "APPROVE", "verifier": "VERIFIED"}' && if [ $side = copy ]; then C=$(bin/factory launch-script build 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'); else C=factory/workflows/build.js; fi; node ${TMPDIR:-/tmp}/t0054-wf.mjs "${C:-no launch copy}" T-0001 2>&1 | grep -e 'T-0001\.1' -e '^Error' | sort; echo "$side: $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') runs=$(grep -l '^ticket: T-0001.1$' $FACTORY_STATE/runs/*/meta.yaml 2>/dev/null | xargs sed -n 's/^role: //p;s/^model: //p' | paste -sd' ' -)"); done)`
- THEN it prints exactly `agent reviewer T-0001.1 model=fable`, `agent verifier T-0001.1 model=opus`, `copy: merged runs=reviewer fable verifier opus`, `agent reviewer T-0001.1 model=fable`, `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus`, `script: parked runs=reviewer fable`, one per line

#### Scenario: An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it
Needs the GIVEN block of "A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks" run once.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store T54_SWAP=triage=fable T54_PLAYS='{"triage": "REJECT"}'; printf '# Fixture\n\nThe bot should do the thing.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && C=$(bin/factory launch-script intake 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'); node ${TMPDIR:-/tmp}/t0054-wf.mjs "${C:-no launch copy}" T-0001 2>&1 | grep -e '^agent' -e '^park' -e '^Error'; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') runs=$(for d in $(ls $FACTORY_STATE/runs 2>/dev/null); do echo "${d#run-????-}=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/$d/meta.yaml)"; done | paste -sd' ' -)")`
- THEN it prints exactly `agent triage T-0001 model=opus`, then `closed runs=triage=opus`

### Requirement: factory launch-script writes a launch copy that differs from its script in one line, wherever factory config would run
`factory launch-script intake|build` MUST write, in a new directory named `factory-launch-*` under the temporary directory, a read-only copy of that workflow script. The copy SHALL differ from the script in one line, which holds the instance's models, round limits and store as `factory config` reports them, the running harness revision and the instance. The command SHALL write nothing to the checkout or the store. Before writing, it SHALL remove each earlier `factory-launch-*` directory under the temporary directory that is more than one hour old and holds only a launch copy, and SHALL remove no other directory. Wherever `factory config` refuses, it MUST refuse with exit 2 and the same error, writing no copy.

#### Scenario: Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; mkdir $T/tmp; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; G0=$(git status --porcelain | cksum); S0=$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum); P=$(bin/factory paths); R=$(echo "$P" | sed -n 's/.*"harness_revision": "\([0-9a-f]*\)".*/\1/p'); I=$(echo "$P" | sed -n 's/.*"instance": "\([^"]*\)".*/\1/p'); for s in intake build; do C=$(TMPDIR=$T/tmp bin/factory launch-script $s 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'); L=$(diff factory/workflows/$s.js "${C:-/dev/null}" | grep '^>'); echo "$s: where=$(case "$C" in $T/tmp/factory-launch-*/$s.js) echo own-dir;; *) echo none;; esac) changed=$(diff factory/workflows/$s.js "${C:-/dev/null}" | grep -c '^[<>]') revision=$(echo "$L" | grep -cF "\"harness_revision\": \"$R\"") instance=$(echo "$L" | grep -cF "\"instance\": \"$I\"") writable=$([ -n "$C" ] && [ -w "$C" ] && echo yes || echo no)"; done; echo "checkout=$([ "$(git status --porcelain | cksum)" = "$G0" ] && echo unchanged || echo changed) store=$([ "$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed) dirs=$(ls $T/tmp | grep -c '^factory-launch-')")`
- THEN it prints exactly `intake: where=own-dir changed=2 revision=1 instance=1 writable=no`, `build: where=own-dir changed=2 revision=1 instance=1 writable=no`, `checkout=unchanged store=unchanged dirs=2`, one per line

#### Scenario: launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
The target's own store is used, so the harness lock applies. Its lock names a revision that is not running.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && mkdir $T/tmp && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && echo 0000000000000000000000000000000000000000 > .factory/harness.lock; $B config >/dev/null 2>$T/c; c=$?; TMPDIR=$T/tmp $B launch-script build >/dev/null 2>$T/l; l=$?; echo "config=$c launch=$l same=$(cmp -s $T/c $T/l && echo yes || echo no) lock=$(grep -c 'is not the revision this instance accepted' $T/l) copies=$(ls $T/tmp | grep -c .)")`
- THEN it prints exactly `config=2 launch=2 same=yes lock=1 copies=0`

#### Scenario: launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; mkdir $T/tmp; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; c() { TMPDIR=$T/tmp bin/factory launch-script build 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'; }; O=$(c); O=${O%/*}; F=$(c); F=${F%/*}; X=$T/tmp/factory-launch-other; mkdir $X && echo x > $X/build.js; touch -t 202001010000 $X; [ -n "$O" ] && touch -t 202001010000 "$O"; N=$(c); N=${N%/*}; k() { [ -n "$1" ] && [ -e "$1" ] && echo kept || echo gone; }; echo "old=$(k "$O") other=$(k $X) fresh=$(k "$F") new=$([ -n "$N" ] && [ -e "$N" ] && echo written || echo none) dirs=$(ls $T/tmp | grep -c '^factory-launch-')")`
- THEN it prints exactly `old=gone other=kept fresh=kept new=written dirs=3`

### Requirement: A launch copy runs only for the instance it was written for
A launch copy SHALL send every store command to the instance it records. Given an `instance` argument that names another instance, it MUST return an error that names the recorded instance before any store command or role runs.

#### Scenario: A launch copy launched for another instance returns an error naming its own and runs nothing
Needs the GIVEN blocks named in "A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && C=$(bin/factory launch-script build 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'); I=$(bin/factory paths | sed -n 's/.*"instance": "\([^"]*\)".*/\1/p'); export T54_INSTANCE=$T23/other T54_PLAYS='{"reviewer": "APPROVE", "verifier": "VERIFIED"}'; node ${TMPDIR:-/tmp}/t0054-wf.mjs "${C:-no launch copy}" T-0001 >$T23/o 2>&1; echo "refused=$(grep '^result ' $T23/o | grep -cF "launch copy written for instance $I") agents=$(grep -c '^agent' $T23/o) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .)")`
- THEN it prints exactly `refused=1 agents=0 checks-in-flight runs=0`

### Requirement: A store reply the clerk relays over several lines still parses
Both workflow scripts SHALL read a relayed stdout that is one JSON value spread over several lines as that value, before they try each line from the last. A ticket whose replies are relayed pretty-printed SHALL take the route it takes with one-line replies.

#### Scenario: A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies
Needs the GIVEN blocks named in "A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks" run once. T-0001.1 starts ready for its implementer; T-0002 starts ready for triage.
- WHEN `(for s in build intake; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && export T54_PRETTY=1; if [ $s = build ]; then . ${TMPDIR:-/tmp}/t0054-impl.sh && export T54_PLAYS='{"implementer": "READY-FOR-REVIEW", "reviewer": "APPROVE", "verifier": "VERIFIED"}' && t=T-0001.1; else printf '# G\n\nDo y.\n' > $T23/req2.md && bin/factory ticket new --file $T23/req2.md >/dev/null && export T54_PLAYS='{"triage": "REJECT"}' && t=T-0002; fi; node ${TMPDIR:-/tmp}/t0054-wf.mjs factory/workflows/$s.js ${t%.1} | grep -e "^agent [a-z_]* $t " -e "^park $t:" -e '^result .*no JSON' | sed 's/^result .*/result: no JSON on stdout/' | sort; echo "$s: $t $(bin/factory ticket show $t | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `agent implementer T-0001.1 model=opus`, `agent reviewer T-0001.1 model=fable`, `agent verifier T-0001.1 model=opus`, `build: T-0001.1 merged`, `agent triage T-0002 model=opus`, `intake: T-0002 closed`, one per line

=== specs/human-resolution/spec.md
## ADDED Requirements

### Requirement: A sub-ticket parked by a harness-bug after its implementer finished returns to its checks
`factory resolve <id> --to checks` MUST accept a sub-ticket that meets four conditions. It is parked. It was parked from `ready-for-implementer`. Its park reason starts `harness-bug:`. Its newest implementer run started after it last entered `ready-for-implementer` and finished `READY-FOR-REVIEW`. On such a sub-ticket the command SHALL set its head to its branch tip, apply the round step the build applies on that move, and move it to `checks-in-flight`. On any other ticket it MUST refuse with exit 2, writing nothing, with an error containing `--to checks applies to`.

#### Scenario: A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. Needs the GIVEN blocks named in "A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks" (build-dispatch, this change) run once. The park is #112's: the implementer run finished `READY-FOR-REVIEW`, then the sub-ticket was parked from `ready-for-implementer` with the reason the build gives when it cannot parse `run finish`'s reply.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0054-impl.sh && implement READY-FOR-REVIEW && bin/factory ticket park T-0001.1 --reason "harness-bug: run finish implementer: exit 0, no JSON on stdout" >/dev/null && bin/factory resolve T-0001.1 --to checks >/dev/null 2>&1; echo "resolve=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') head=$([ "$(bin/factory ticket show T-0001.1 | sed -n "s/^head: '\{0,1\}\([0-9a-f]*\).*/\1/p")" = "$H" ] && echo tip || echo other) pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; T54_PLAYS='{"reviewer": "APPROVE", "verifier": "VERIFIED"}' node ${TMPDIR:-/tmp}/t0054-wf.mjs factory/workflows/build.js T-0001 | grep 'T-0001\.1' | sort; echo "$(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') implementer_runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `resolve=0 checks-in-flight head=tip pr=1`, `agent reviewer T-0001.1 model=fable`, `agent verifier T-0001.1 model=opus`, `merged implementer_runs=1`, one per line

#### Scenario: The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked
Needs the GIVEN blocks named in "A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it" run once. `revised` is a sub-ticket whose READY-FOR-REVIEW run was checked and sent back, and whose next implementer run then failed to start: its newest implementer run predates its return.
- WHEN `(for c in blocked revised checks tripwire unparked; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0054-impl.sh && case $c in blocked) implement BLOCKED && bin/factory ticket park T-0001.1 --reason "harness-bug: run finish implementer: exit 0, no JSON on stdout" >/dev/null;; revised) implement READY-FOR-REVIEW && bin/factory ticket transition T-0001.1 --to checks-in-flight --by t --round pr:init >/dev/null && bin/factory ticket transition T-0001.1 --to ready-for-implementer --by t --round pr:+1 >/dev/null && bin/factory ticket park T-0001.1 --reason "harness-bug: run start implementer: x" >/dev/null;; checks) implement READY-FOR-REVIEW && bin/factory ticket transition T-0001.1 --to checks-in-flight --by t --round pr:init >/dev/null && bin/factory ticket park T-0001.1 --reason "harness-bug: results record reviewer: x" >/dev/null;; tripwire) implement READY-FOR-REVIEW && bin/factory ticket park T-0001.1 --reason "tripwire: /x changed during $R" >/dev/null;; unparked) implement READY-FOR-REVIEW;; esac; K=$(cat $FACTORY_STATE/tickets/T-0001.1.yaml $FACTORY_STATE/log/*.jsonl | cksum); bin/factory resolve T-0001.1 --to checks >/dev/null 2>$T23/e; echo "$c: exit=$? refused=$(grep -c -- '--to checks applies to' $T23/e) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') store=$([ "$(cat $FACTORY_STATE/tickets/T-0001.1.yaml $FACTORY_STATE/log/*.jsonl | cksum)" = "$K" ] && echo unchanged || echo changed)"); done)`
- THEN it prints exactly `blocked: exit=2 refused=1 parked store=unchanged`, `revised: exit=2 refused=1 parked store=unchanged`, `checks: exit=2 refused=1 parked store=unchanged`, `tripwire: exit=2 refused=1 parked store=unchanged`, `unparked: exit=2 refused=1 ready-for-implementer store=unchanged`, one per line

=== specs/live-store-guard/spec.md
## MODIFIED Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `launch-script`, `status parse`, `log tail`, `paths`, `drive` and `stats`, none of them given `--accept-harness`, MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

#### Scenario: A launch copy is written unmarked while a run is in flight, and the target is unchanged
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The unmarked `ticket new` beside it shows the fence is up.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && mkdir $T/tmp && S0=$(snap); TMPDIR=$T/tmp $B launch-script build >/dev/null 2>&1; l=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "launch=$l new=$n copies=$(ls $T/tmp | grep -c '^factory-launch-') store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `launch=0 new=2 copies=1 store=unchanged`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the launch copy and the route back to checks
`README.md`'s "Starting a run" SHALL tell the operator to launch the copy `factory launch-script` writes. Its "Where a human decides" SHALL list `launch-script` among the commands that are not writes, and its **Unstick** row SHALL name `resolve --to checks`. `docs/design.md` SHALL list `launch-script` in the live-store fence's read-only list and describe the `--to checks` route. `docs/changelog.md` SHALL hold one entry opening `After issue #109`, naming #112, `launch-script` and `--to checks`, numbered without a gap. README SHALL stay within its 1,110-line budget, and the maintained documents SHALL carry no whitespace error.

#### Scenario: The README, the design doc and the changelog describe the launch copy and the route back to checks
Run from the repository root of the checkout under test.
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "start=$(y $(sed -n '/^## Starting a run/,/^### Driving a ticket/p' README.md | grep -c 'factory launch-script')) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--to checks')) writes=$(y $(printf '%s' "$R" | grep -o 'A write is any command except [^;]*;' | grep -c 'launch-script')) list=$(printf '%s' "$R" | grep -o 'A write is any command except [^;]*;' | grep -c .) fence=$(y $(grep '^\*\*Only the dispatcher writes a live store' docs/design.md | grep -c 'launch-script')) route=$(y $(grep -c -- '--to checks' docs/design.md)) readme=$(wc -l < README.md | awk '{print ($1 <= 1110 ? "within" : "over")}')"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #109 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e '#112' -e 'launch-script' -e '--to checks' | sort -u | grep -c .)"; E0=$(git hash-object -t tree /dev/null); git diff --check $E0 HEAD -- README.md docs dev .factory/context.md; echo "exit=$?")`
- THEN it prints exactly `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within`, `CONTIGUOUS`, `entries=1 terms=3`, `exit=0`, one per line

=== specs/harness-suite/spec.md
## ADDED Requirements

### Requirement: The suite tests the launch copy, a reformatted reply and the route back to checks, and changes no existing test
The harness suite SHALL pass with no existing test file changed or deleted. The test files this change adds SHALL each fail, with at least one failed test, when run against the harness code of the change's base.

#### Scenario: The suite passes, no existing test changes, and every test file this change adds fails on the base
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends. The base is `git merge-base HEAD main`; its tree is unpacked into that directory, and the added files are copied in beside its tests.
- WHEN `(P=$(mktemp -d /tmp/t0054-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; B=$(git merge-base HEAD main); echo "changed=$(git diff --name-only --diff-filter=DMR $B HEAD -- tests | grep -c .) added=$(git diff --name-only --diff-filter=A $B HEAD -- tests | grep -c '/test_[^/]*\.py$')"; mkdir $P/base && git archive $B | tar -x -C $P/base && for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests); do mkdir -p $P/base/${f%/*} && cp $f $P/base/$f; done; for f in $(git diff --name-only --diff-filter=A $B HEAD -- tests | grep '/test_[^/]*\.py$'); do echo "$f on the base: $(cd $P/base && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider $f 2>&1 | tail -1 | sed 's/ in [0-9.]*s.*//')"; done; rm -rf "$P")`
- THEN the first line reports a number of passed tests and no `failed` or `error`; the second is `changed=0 added=<n>` with n at least 1; then n lines follow, each `<added test file> on the base: <pytest summary>`, where every summary includes `failed`

=== verification.md
## Acceptance

Each NEW item's failure below is what that WHEN printed on `main` at 308d038. Each PR-side THEN was checked on a scratch prototype of parts A to D, except the docs and suite items, which the prototype does not cover.

- A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks → NEW. Today `launch-script` is an invalid choice, so node gets no script: it prints `Error: ENOENT: no such file or directory, open 'no launch copy'` and `copy: checks-in-flight runs=`. The script half already prints its three lines; that half guards the backstop.
- An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it → NEW. Today it prints the same `Error: ENOENT ...` line, then `ready-for-triage runs=`.
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance → NEW. Today it prints `intake: where=none changed=206 revision=0 instance=0 writable=no`, `build: where=none changed=310 revision=0 instance=0 writable=no` and `checkout=unchanged store=unchanged dirs=0`.
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy → NEW. Today it prints `old=gone other=kept fresh=gone new=none dirs=1`: `launch-script` is an invalid choice, so no copy is written. Added at the gate (operator, 2026-10-18); not run on the prototype.
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy → NEW. Today it prints `config=2 launch=2 same=no lock=0 copies=0`: the exit 2 is argparse's usage error, not the lock's refusal.
- A launch copy launched for another instance returns an error naming its own and runs nothing → NEW. Today it prints `refused=0 agents=0 checks-in-flight runs=0`, because no copy exists.
- A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies → NEW. Today it prints `result: no JSON on stdout`, `build: T-0001.1 ready-for-implementer`, `result: no JSON on stdout`, `intake: T-0002 ready-for-triage`: each script stops at its first reply, `factory config`.
- A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it → NEW. Today it prints `resolve=2 parked head=other pr=0`, then `parked implementer_runs=1`. The refusal text is `--to accepts only spec-gate`.
- The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked → NEW. Today every line reads `exit=2 refused=0 ...`: the command is refused, but by `--to accepts only spec-gate`, not by this route's rule.
- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION. Restated unchanged from current truth; it prints its THEN today.
- The refusal names the throwaway store and not the marker → REGRESSION. Restated unchanged; it prints its THEN today.
- A harness acceptance is refused while a run is in flight → REGRESSION. Restated unchanged; it prints its THEN today.
- A launch copy is written unmarked while a run is in flight, and the target is unchanged → NEW. Today it prints `launch=2 new=2 copies=0 store=unchanged`.
- The README, the design doc and the changelog describe the launch copy and the route back to checks → NEW. Today it prints `start=no unstick=no writes=no list=1 fence=no route=no readme=within`, `CONTIGUOUS`, `entries=0 terms=0`, `exit=0`.
- The suite passes, no existing test changes, and every test file this change adds fails on the base → NEW. On `main` the base is `main` itself, so the second line is `changed=0 added=0` and no file line follows. I ran this command's base-tree mechanics on the prototype with one stand-in test file, which printed `<file> on the base: 1 failed`. The full suite on the prototype printed `594 passed`.

## PR description (the implementer's output)

Sub-ticket: T-0054.1, `/Users/dphang/dev/spec-factory/.factory/store/tickets/T-0054.1.yaml`. Parent spec v3: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0054/v3.md`.
Branch: `factory/T-0054.1`, one commit, `e12ca71`, on base `308d038`. Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0054.1`.

## What changed

Workflow builds no longer stop because the clerk miscopied a reply. The clerk is the small agent that runs one store command for a workflow script and copies its output back. On real runs it retyped a role's model (#109) and spread a one-line JSON reply over several lines (#112). Each slip parked a sub-ticket. For #112, no `resolve` command could return the sub-ticket.

**A. `factory launch-script intake|build`** (new `factory/launch.py`, 57 lines; `factory/cli.py`).
- The command reads `factory/workflows/<name>.js` from the running harness checkout. It requires the line `const LAUNCH = null` exactly once and otherwise refuses with exit 2. It then writes `<name>.js` read-only (0444) into a new `tempfile.mkdtemp(prefix="factory-launch-")` directory. In the copy, that one line becomes `const LAUNCH = {...}`. The object holds `written_by`, `source`, `harness_revision`, `instance` (as `factory paths` prints it), `models`, `max_rounds` and `state_dir`. The command prints `{"ok": true, "script", "source", "harness_revision", "instance"}`.
- Before writing, it removes each `factory-launch-*` directory under the temporary directory that meets three conditions: it is more than 3,600 seconds old; it holds exactly one file, named `intake.js` or `build.js`; and that file contains `"written_by": "factory launch-script"`. It skips every other directory, and any `OSError` or `ValueError` while checking one.
- `config_values()` in `launch.py` is now the one definition of what `factory config` prints. `config_cmd` uses it too.
- `cli.py` gains the `launch-script` subparser, with one positional `name` (`intake` or `build`). It also adds `("launch-script", None)` to `READ_ONLY`, so the command takes `config`'s path through `main()`: the instance is required, the fence is skipped, and the harness lock is checked.

**B. Both workflow scripts honour a launch copy** (`build.js`, `intake.js`).
- Each script gains a comment and the line `const LAUNCH = null` above `INSTANCE`.
- `const INSTANCE = LAUNCH ? LAUNCH.instance : args.instance`.
- Before the config step: a copy given another `args.instance` returns `{ticket, error: "launch copy written for instance <recorded>, launched with <given>"}`.
- The config step is `const cfg = LAUNCH ? { ok: true, ...LAUNCH } : <the clerk call as before>`. The lines after it are unchanged.
- The `// args:` header comments now say a launch copy takes its instance from the copy.

**C. `clerk()` parses a reply spread over several lines** (both scripts). It trims stdout once and tries `JSON.parse` on the whole text. Only when that fails does it run the old scan from the last line up. Every rule after the parse is unchanged.

**D. `factory resolve <id> --to checks`** (`factory/human.py`, `factory/store.py`, `factory/gates.py`).
- A new branch inside `resolve` accepts a ticket that meets four conditions: status `parked`, `parked.from == "ready-for-implementer"`, a reason starting `harness-bug:`, and `store.implemented_since_ready()`.
- Accepted: `store.set_head()` reads the branch tip, then `store._apply_round(t, "pr:init", cfg)` applies the round step, then `move("checks-in-flight", "to-checks", {"head": ...})` writes the history entry, `resolve-<n>.yaml` and the `human.resolved` event.
- Refused: exit 2, nothing written, and the error `--to checks applies to a sub-ticket parked by a harness-bug from ready-for-implementer after its implementer run finished READY-FOR-REVIEW; <id> is <status> (<reason or 'no park'>)`.
- Any other `--to` value is refused with `--to accepts only spec-gate or checks`.
- New in `store.py`:
  - `implemented_since_ready(root, tid)`, beside `log_lines`. It reads the event log in file and line order. A move into ready-for-implementer is any event of the ticket whose `to` is that state, or a `ticket.created` whose `status` is. The newest implementer `run.started` must come after the last such move, and that run's `run.finished` must carry `READY-FOR-REVIEW`.
  - `set_head(root, cfg, t)`, the body of `ticket head` moved from `gates.py` with the conflict bookkeeping. It keeps its one `gitops.repo_root()` call, with `gitops` imported inside the function. `gates.ticket_head` now loads the ticket, calls it and prints the result.
  - `_apply_round`, moved from `cli.py` with its exact text. `ticket transition` calls `store._apply_round`.
- The parser's `--to` has help text naming `spec-gate` and `checks`. The "resolve needs one of …" message now lists `--to spec-gate|checks`. That message change is beyond the design's text.
- Callers, found by grep (coding rule 2):
  - `_apply_round`: `cli.ticket_transition` only, before this change.
  - `ticket head`'s body: `gates.ticket_head`, reached only through the parser.
  - `config` values: `config_cmd`.
  - `clerk()`: every store call in each script. Its behaviour changes only for a stdout whose whole text is one JSON value.

**E. Tests**: three new files under `tests/factory/`, listed below. No existing file changed.

**F. Documents.**
- `README.md`, 1,108 → 1,109 lines (budget 1,110):
  - "Starting a run": `README.md:699-711` is replaced by the spec's 13-line draft, word for word.
  - The run-start paragraph gains one line: a launch copy carries the models itself.
  - "Where a human decides": `launch-script` is added to "A write is any command except …;", rewrapped with no added line.
  - The **Unstick** row gains `--to checks`, with what it is for and "not yet run on a real ticket".
  - The status date is now 2026-10-19.
- `docs/design.md`:
  - line 44, limit (1): one sentence on the launch copy and on parsing a reply spread over several lines;
  - line 64: `launch-script` added to the read-only list;
  - line 109: the `--to checks` route, after the harness-bug ruling rule.
  - None of these is a prompt block, so `docs/prompts/` does not change.
- `docs/changelog.md`: entry 75, opening `75. After issue #109 `, naming #112, `launch-script` and `--to checks`.

Protected paths touched: `factory/**` (`launch.py`, `cli.py`, `gates.py`, `human.py`, `store.py`, `workflows/*.js`). The spec's Risk section declares them.

## Acceptance results

I copied every WHEN command verbatim out of spec v3 with a script (`scratch/extract.py`). The GIVEN blocks came from v3, `openspec/specs/human-resolution/spec.md` (`t0023-parent.sh`) and `openspec/specs/build-dispatch/spec.md` (`t0032-checks.sh`). I ran each one from the worktree inside the HOME wrapper, with `TMPDIR` set to my scratch directory, under GNU bash 5.3 (`/opt/homebrew/bin/bash`). "Before" was run on `308d038` before any edit. "After" was run on `e12ca71`. Logs: `scratch/base-new.log`, `scratch/base-15.log`, `scratch/pr-accept.log`, `scratch/pr-15.log`.

| # | Scenario | Kind | Before (308d038) | After (e12ca71) |
|---|---|---|---|---|
| 1 | A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks | NEW | `Error: ENOENT: no such file or directory, open 'no launch copy'`, `copy: checks-in-flight runs=`, then the script's 3 lines | `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001.1 model=opus` / `copy: merged runs=reviewer fable verifier opus` / `agent reviewer T-0001.1 model=fable` / `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus` / `script: parked runs=reviewer fable`: matches THEN |
| 2 | An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it | NEW | `Error: ENOENT …`, `ready-for-triage runs=` | `agent triage T-0001 model=opus` / `closed runs=triage=opus`: matches |
| 3 | Each launch copy is a one-line change to its script, … | NEW | `intake: where=none changed=206 revision=0 instance=0 writable=no` / `build: where=none changed=310 revision=0 instance=0 writable=no` / `checkout=unchanged store=unchanged dirs=0` | `intake: where=own-dir changed=2 revision=1 instance=1 writable=no` / `build: where=own-dir changed=2 revision=1 instance=1 writable=no` / `checkout=unchanged store=unchanged dirs=2`: matches |
| 4 | launch-script is refused with config's error where the instance has not accepted the running harness, … | NEW | `config=2 launch=2 same=no lock=0 copies=0` | `config=2 launch=2 same=yes lock=1 copies=0`: matches |
| 5 | launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy | NEW | `old=gone other=kept fresh=gone new=none dirs=1` | `old=gone other=kept fresh=kept new=written dirs=3`: matches |
| 6 | A launch copy launched for another instance returns an error naming its own and runs nothing | NEW | `refused=0 agents=0 checks-in-flight runs=0` | `refused=1 agents=0 checks-in-flight runs=0`: matches |
| 7 | A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies | NEW | `result: no JSON on stdout` / `build: T-0001.1 ready-for-implementer` / `result: no JSON on stdout` / `intake: T-0002 ready-for-triage` | `agent implementer T-0001.1 model=opus` / `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001.1 model=opus` / `build: T-0001.1 merged` / `agent triage T-0002 model=opus` / `intake: T-0002 closed`: matches |
| 8 | A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it | NEW | `resolve=2 parked head=other pr=0` / `parked implementer_runs=1` | `resolve=0 checks-in-flight head=tip pr=1` / `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001.1 model=opus` / `merged implementer_runs=1`: matches |
| 9 | The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked | NEW | each line `exit=2 refused=0 …` | `blocked: exit=2 refused=1 parked store=unchanged` / `revised: …` / `checks: …` (same form) / `tripwire: …` / `unparked: exit=2 refused=1 ready-for-implementer store=unchanged`: matches |
| 10 | Unmarked writes from inside the target are refused while a run is in flight, init included | REGRESSION | not run (it passed on main when the spec was written) | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`: matches |
| 11 | The refusal names the throwaway store and not the marker | REGRESSION | not run | `rule=1 state=1 marker=0 json=1 inside=1`: matches |
| 12 | A harness acceptance is refused while a run is in flight | REGRESSION | not run | `accept=2 store=unchanged`: matches |
| 13 | A launch copy is written unmarked while a run is in flight, and the target is unchanged | NEW | `launch=2 new=2 copies=0 store=unchanged` | `launch=0 new=2 copies=1 store=unchanged`: matches |
| 14 | The README, the design doc and the changelog describe the launch copy and the route back to checks | NEW | `start=no unstick=no writes=no list=1 fence=no route=no readme=within` / `CONTIGUOUS` / `entries=0 terms=0` / `exit=0` | `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within` / `CONTIGUOUS` / `entries=1 terms=3` / `exit=0`, run after the commit, because its `git diff --check` reads HEAD: matches |
| 15 | The suite passes, no existing test changes, and every test file this change adds fails on the base | NEW | `594 passed in 105.71s` / `changed=0 added=0` | `615 passed in 117.20s` / `changed=0 added=3` / `tests/factory/test_launch_script.py on the base: 4 failed, 1 error` / `tests/factory/test_resolve_to_checks.py on the base: 8 failed` / `tests/factory/test_workflow_launch_copy.py on the base: 7 failed, 1 passed`: matches THEN; every summary includes `failed` |

Gate commands, each run exactly as written from the worktree on `e12ca71`:
- `git diff --check main...HEAD`, wrapped: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, wrapped: `615 passed in 115.16s (0:01:55)`, exit 0. Afterwards the system temporary directory held no `factory-launch-*` directory.

Current-truth pins from harness-code that the spec's Risk section names, run on `e12ca71`:

| Check | Output | Expected |
|---|---|---|
| repo-root helper: `repo_root(cfg` callers, `gitops.repo_root()` sites, its definition | `0 12 1` | `0 12 1` |
| `"ticket.transition"` literals in the CLI modules and in `store.py` | `1 1` | `1 1` |
| `"*.jsonl"` in the CLI modules and in `store.py` | `0 1` | `0 1` |
| run listing outside `store.py` | `0` | `0` |
| integration-tip reads and `integration_tip` definitions | `1 1` | `1 1` |
| `factory/cli.py` line count and pinned definitions | `877 3` | under 900, and `3` |
| modules that import `factory.cli` | `factory/__main__.py factory/drive.py factory/stats.py` | the same three |
| `uvx ruff check --select F factory` | `All checks passed!` | the same |
| `uvx ruff check --select F401,F841 factory tests` | `All checks passed!` | the same |

The pinned definition lists of `drift.py`, `common.py`, `setup.py`, `gates.py` and `human.py` print exactly their current-truth strings. `t0047-moved.py` prints `pairs=5 added=13 removed=6 lines=157`. The spec's Risk section predicts this: that scenario measures T-0047's split, so it counts this change's new and moved definitions. `_apply_round` moved with its exact text and is not counted.

## Tests added/changed

No existing test file changed. Three new files:

- **`tests/factory/test_launch_script.py`** (5 tests): the CLI half of `launch-script`.
  - For each script: the copy differs from it in one line, and that line's JSON holds exactly `written_by`, `source`, the revision and instance `paths` prints, and the `models`, `max_rounds` and `state_dir` `config` prints. The copy is mode 0444, alone in its own `factory-launch-*` directory. The printed JSON is as designed. The store is unchanged.
  - Under a lock that names another revision, it is refused with `config`'s stderr byte for byte, and writes no copy.
  - It runs unmarked while a run is in flight, beside a refused `ticket new`, and the target is unchanged.
  - Cleanup removes an hour-old copy. It keeps three directories: a fresh copy, an old directory with a non-copy `build.js`, and an old copy with a second file beside it.
  - An autouse fixture points `TMPDIR` inside the test's `tmp_path`. `launch()` fails a test whose copy lands outside it. This is coding rule 6's guard for the new outside path.
- **`tests/factory/test_workflow_launch_copy.py`** (8 tests): the scripts under node, with a stand-in clerk that runs each command for real and miscopies on request, as decision 12 allows.
  - A build from a launch copy runs implementer, reviewer, verifier and every clerk call on the instance's models, while the stand-in clerk names `sonnet` for all four. It then merges.
  - `build.js` launched as it is still parks at the verifier's run start, as T-0050's backstop does. This test also passes on the base, as intended.
  - An intake from a launch copy runs triage on `opus` while the clerk names `fable`.
  - A copy of either script given another instance returns the error and makes no agent call.
  - A build and an intake whose every reply is pretty-printed merge and close.
  - A sub-ticket returned by `resolve --to checks` merges with one implementer run.
- **`tests/factory/test_resolve_to_checks.py`** (8 tests): the route.
  - #112's park returns to `checks-in-flight` at the branch tip with `round.pr` 1. The history entry, `resolve-1.yaml` and the `human.resolved` event all carry `to-checks`.
  - A later round (2) is unchanged.
  - The blocked, revised, checks, tripwire and unparked cases are refused, naming the status, with the store byte-identical (worktrees excluded).
  - Another `--to` value names both routes.

On a git checkout of the base, all 21 new tests failed before I edited any code. One of them, the as-launched backstop test, failed only because of my own assertion bug: stderr's trailing newline. I fixed the assertion, not the code. In the spec's base-tree mechanics (scenario 15) one test errors instead of failing; see Known gaps.

## Known gaps and uncertainties

- **Scenario 3 does not parse under macOS `/bin/sh`.** That shell is bash 3.2, and it reports `syntax error near unexpected token 'newline'` on the `$(case … esac)` inside the command. I ran every WHEN under bash 5.3. On the base, bash 5.3 and zsh both print the "today" output verification.md records, so the spec's author used a newer shell. A verifier using `sh` on this machine will see the syntax error whatever the code does.
- **Not run in Claude Code's Workflow tool.** I could not run it here. Whether it loads a script from the temporary directory, and whether the auto-mode classifier lets it run, is Operator step 1, as the Risk section says.
- **Instance comparison is exact string equality.** A copy given the same instance path with a trailing slash or through a symlink returns the "launched with" error. This follows the design's text.
- **A copy launched without `args.state` gets no `FACTORY_STATE` in its clerk commands.** It takes `STATE` from `LAUNCH.state_dir`, as the clerk path takes it from `config`. If the session that ran `launch-script` had `FACTORY_STATE` set and the Workflow clerk's shell does not, two things diverge: the role agents read run files under the recorded store, and the clerk's commands go to the instance's own store. The design does not set `STATE` from `LAUNCH` before `ENV` is built, so I did not either. Setting `let STATE = args.state || (LAUNCH && LAUNCH.state_dir) || null` would close it, but that is a design decision for the spec.
- **The refusal when `const LAUNCH = null` does not occur exactly once is untested.** Testing it needs a harness checkout with an edited script. I read the code path; I did not run it.
- **The "resolve needs one of …" usage message** now says `--to spec-gate|checks`. The design names only the `--to` refusal and the help text. No test pins this message.
- **On the base tree in scenario 15**, `test_launch_script.py` reports `4 failed, 1 error`. The error is the `target` fixture: `factory init` cannot read the harness revision of a `git archive` tree, which is not a git checkout. On a git checkout of the base, all five tests fail with `invalid choice: 'launch-script'`.
- **Size.** The change is 690 lines added and 74 removed. `factory/` accounts for 177 added and 54 removed; the new tests for 490. The design estimated under 400 lines with tests and docs. The node driver and the fixture classes are most of the test lines.
- **One ruff finding in the new tests.** `ruff --select F` on them reports F811 for the `target` fixture parameter. `test_live_store_guard.py` uses the same idiom, and the pinned ruff commands pass.
- **No `AGENTS.md`.** This repository has none, so step 1 of the process read none.
- `factory:` markers added: none.

## Out-of-scope observations

- `MAX_PR` in `build.js` is still set and never read, as the spec notes.
- The `STATE` gap above may deserve its own small ticket if the operator ever launches copies with a throwaway `FACTORY_STATE`.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high: every acceptance command prints its THEN on `e12ca71`, both gates pass and the harness-code pins hold; the Workflow tool itself is unverified, as the spec's Risk section says.
ESCALATIONS: none

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Diff `308d03857bced6dc4f33e62812d83c52fd73e4b2...e12ca713eb3b8594445773d44e87790fd480faa1`

diff --git a/README.md b/README.md
index 777784b..65ec168 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-13. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-19. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -249,9 +249,10 @@ in (`parked.from`).
 Every role call, in either workflow, is the same three store commands around one agent. `run start`
 creates the run directory and its prompt, and refuses unless the ticket is in that role's ready
 state. It takes the role's model from `instance.yaml` and records it. It refuses a `--model` that
-names another model, so a model the clerk misreported parks the ticket before the agent starts.
-`run compose` writes `input.md`. The role agent runs. `run finish` reads the `STATUS:` line
-and records it. Each command goes through the clerk.
+names another model, so a model the clerk misreported parks the ticket before the agent starts. A
+launch copy of a script, written by `factory launch-script` ("Starting a run"), carries the models
+itself, so no clerk relays them. `run compose` writes `input.md`. The role agent runs. `run finish`
+reads the `STATUS:` line and records it. Each command goes through the clerk.
 
 ```mermaid
 sequenceDiagram
@@ -696,19 +697,19 @@ To roll back, with no run in flight and the store committed:
 
 ## Starting a run
 
-A Claude Code session in the target repo asks the runtime where things are:
+A Claude Code session in the target repo has the runtime write a launch copy of the script:
 
 ```
-$RUNTIME/bin/factory paths      # the harness, its entry point, both workflow scripts,
-                                # the running revision, the instance and its store
+$RUNTIME/bin/factory launch-script intake   # or build; prints the copy's path as "script"
 ```
 
-It then calls the Workflow tool with `scriptPath` set to the intake script and args
-`{ticket, repo: <runtime>, instance: <.factory>}`. After the spec gate, the same call with the build
-script. Add `inlineRoles: true` on every target for now: `agents/` ships agent definitions only for
-the intake roles and the planner, so a build without it fails at the first implementer call. "What
-depends on Claude Code" says what it changes. Start the build script after the spec gate; the
-intake script has nothing to do past it.
+A launch copy is the script with the instance's models, round limits and store written into one
+line, so no agent relays them; it names the harness revision and instance it was written for. It
+has not yet run on a real ticket. The session calls the Workflow tool with `scriptPath` set to the
+printed `script` and args `{ticket, repo: <runtime>}`; after the spec gate, the same with `build`.
+Add `inlineRoles: true` on every target for now: `agents/` ships agent definitions only for the
+intake roles and the planner, so a build without it fails at the first implementer call. "What
+depends on Claude Code" says what it changes. The intake script has nothing to do past the gate.
 
 In practice you ask the runner session in plain words, for example "run the intake workflow for
 T-0032 with inlineRoles". The Workflow tool runs in the background; Claude Code's `/workflows` view
@@ -829,9 +830,9 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 A run is in flight from `run start` until `run finish` records its result. While any run on a
 target is in flight, the harness refuses every write to that target's store that lacks this
 marker. A write is any command except `ticket show`, `ticket join`, `results show`, `config`,
-`status parse`, `log tail`, `paths` and `stats`; a command given `--accept-harness` is always a
-write. `factory drive` is exempt from this check and needs no marker, because it is the
-dispatcher; it guards its own ticket instead ("Driving a ticket from a shell with `factory drive`"). The
+`launch-script`, `status parse`, `log tail`, `paths` and `stats`; a command given
+`--accept-harness` is always a write. `factory drive` is exempt from this check and needs no
+marker, because it is the dispatcher; it guards its own ticket instead ("Driving a ticket from a shell with `factory drive`"). The
 workflow scripts already put the marker on their own commands. Put it in front of one command at
 a time:
 
@@ -856,7 +857,7 @@ FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLE
 | **File** | `factory ticket new --file <abs path>` | that this request is worth a ticket |
 | **Gate** | `factory approve-spec T-n [--edit F]` · `factory request-changes T-n F` · close | the spec's intent, risk declarations, operator steps, "tests to change"; a gate edit becomes a new spec version and is what gets pinned |
 | **Amend** | `factory spec amend T-n --file F --reason "<line>" --intent unchanged`, on an approved spec before archive, while no run is in flight on the ticket or its sub-tickets | that the approved spec must change after the gate, because another ticket merged first, a checker found a scenario that cannot pass as written, or you changed your mind. Amend only when the Problem, the Decisions and every requirement's statement stay as approved; otherwise restart, by re-spec and re-plan or by close and re-file. `--intent changed` prints what a restart keeps and discards. Later runs receive the amended version, but the amendment moves no ticket: resume it as usual, for example with `--ruling F` |
-| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, the harness blocked an implementer whose sub-ticket lists a test no merged sibling added, the harness parked a sub-ticket for spec drift, or the harness failed to start an implementer run, a `harness-bug: run start implementer:` park; a ruling on the code reviewer's escalation re-runs the checks, with the ruling in their input) · `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design, and the sub-ticket returns to its checks; `--ruling F` sends the sub-ticket back to its implementer instead) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, an accepted protected path, a re-check, a re-plan, a re-scope, or closing |
+| **Unstick** | `factory resolve T-n --answer F` (a role asked a question) · `--ruling F` (a role escalated, an implementer reported itself blocked, the harness blocked an implementer whose sub-ticket lists a test no merged sibling added, the harness parked a sub-ticket for spec drift, or the harness failed to start an implementer run, a `harness-bug: run start implementer:` park; a ruling on the code reviewer's escalation re-runs the checks, with the ruling in their input) · `--accept-paths F` (the merge gate refused a protected path the approved spec does not declare: accept it under the approved design, and the sub-ticket returns to its checks; `--ruling F` sends the sub-ticket back to its implementer instead) · `--redispatch` (re-run the checks on the same commit after an outside fix, or after a checker ended without output twice) · `--replan F` (the final check failed after every sub-ticket merged: back to the planner with a note; new sub-tickets take the next free ids) · `--to spec-gate` · `--to checks` (a store command failed after the implementer finished, a `harness-bug:` park from ready-for-implementer after an implementer run that finished READY-FOR-REVIEW: the sub-ticket returns to its checks at its branch tip; not yet run on a real ticket) · `--close`; with `--answer` or `--close`, add `--decision "<line>"` to also record the answer as a standing decision | an answer, a ruling, an accepted protected path, a re-check, a re-plan, a re-scope, or closing |
 | **Record** | `factory decision add T-n "<line>"`, at any ticket state, closed included: one dated line in the decision log | that a decision binds later tickets |
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 28a3fa7..5e9e185 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -80,4 +80,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 
 74. After issue #108 (2026-10-13), where Claude Code could not load four of the six role agent templates in `agents/` (planner, spec critic, spec writer and triage): each one's frontmatter, the YAML header that names the agent, held an unquoted description containing a colon and a space, which YAML reads as a second key, so the header did not parse. No run failed, because every workflow run passes `inlineRoles: true` and `factory drive` starts each role with its prompt inline. The four descriptions are now quoted, with their words unchanged. The harness suite now parses every template's frontmatter, one case per template, and requires `name`, `description`, `model` and `tools`; no test read these headers before. `factory init` still never overwrites an existing copy in a target's `.claude/agents/`; it now lists each copy that differs from its template under `stale_agents` in its JSON output and names it on stderr, and still exits 0. Nanobot's copies, byte-identical to the old templates, are refreshed by its Driver after the merge and the runtime upgrade. Rejected: rephrasing the descriptions without the colon, which changes their words; overwriting a differing copy, which would discard an operator's deliberate edit; and refusing with exit 2, because a stale copy does not stop a run that uses `inlineRoles`.
 
+75. After issue #109 (2026-10-19), where the clerk, the agent that relays the store's command output to a workflow script, retyped a role's model in `factory config`'s reply, and the harness refused that role's run start and parked the sub-ticket; and issue #112, where the clerk relayed `run finish`'s one-line JSON reply over several lines, the script found no JSON, and it parked a sub-ticket whose implementer had finished, a park no `resolve` command covered. A new command, `factory launch-script intake|build`, writes a launch copy: the workflow script with its line `const LAUNCH = null` replaced by the instance's models, round limits and store as `config` prints them, the harness revision and the instance. The copy is read-only, in a new `factory-launch-*` directory under the temporary directory, and asks no clerk for the configuration. It refuses with config's error wherever config refuses, joins the live-store fence's read-only list, and first removes launch copies more than an hour old. A copy given another `instance` argument returns an error naming its own and runs nothing. Both scripts now parse a reply as one JSON value before trying its lines one at a time. `factory resolve <id> --to checks` returns a sub-ticket parked with a `harness-bug:` reason from ready-for-implementer, after its newest implementer run finished READY-FOR-REVIEW, to its checks at its branch tip, with the build's `pr:init` round step. `ticket head`'s body and the round step moved to `factory/store.py`, each one definition used by both callers. The scripts launched as they are keep their clerk path, so `run start`'s refusal of a model the instance does not name stays the backstop. Rejected: a fixed launch-copy path under the instance's `.factory/`, which a later launch would rewrite under a running workflow; a script that refuses to run without a copy, which breaks every check that runs the scripts directly; and removing every earlier copy, which could remove one another session is about to launch.
+
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 9b394bf..e10ecb4 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -41,7 +41,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | # | Piece | What it must do | GitHub gives you | Minimum portable substitute |
 |---|---|---|---|---|
 | 1 | Ticket store | One record per ticket and sub-ticket: status, type, spec text and version, PR link, round counter, history. The spec gate pins the version the human approved, including any edits made at the gate. This is the state machine's memory. A store CLI (read, transition, record) fronts it: the dispatcher chooses the transition, the CLI rejects any not in the routing table and any round past the cutoff, and the clerk goes through it too | Issues + labels | Any tracker (Jira, Linear) or a table in a DB. A `factory-store` branch of YAML works to start: the pre-receive hook restricts it to harness and human identities and exempts it from the merge gate |
-| 2 | Event dispatcher | Notice a state change and start the right role with the right inputs. Routes on the `STATUS:` line of the last output, per the routing table | Webhooks + Actions `on:` events | A loop (cron, every 1–5 min) that queries the store for tickets in a "ready for X" state and launches X. Polling is fine; nothing here is latency-sensitive. For a v0 inside one Claude Code session, a Workflow script: each agent() call is a fresh context, the fan-out, join, and round counters are plain code, and the same routing table lifts into the loop later. Three v0 limits. (1) The script has no filesystem or clock, so store reads and writes go through a clerk agent calling the CLI; the guards live in the CLI, not the clerk. The clerk never restates a command's output: it returns stdout verbatim with the exit code and stderr, and the script parses the JSON itself, since a schema shaped like the command's output lets the clerk re-type the answer and still validate. A non-zero exit is a refusal and no JSON on stdout is a failed store call; neither is ever read as an answer. (2) A hung agent blocks the join until a human skips it, so the piece-3 kill is post-hoc. (3) v0 gives fresh context, not isolation: every agent() call shares the session's checkout, credentials, and git identity. Use a worktree per call, run the clerk's CLI under a harness identity that has no verb for approval rows (humans write those directly), and treat v0 as exercising the routing table, not as producing trusted merges. `factory drive TICKET` is the external dispatcher, outside the Workflow tool: an ordinary Python process that routes as the two scripts do and calls the store CLI's own entry point in its own process, one call at a time. It has no clerk, so limit (1) does not apply to it. It starts each role as one headless `claude -p` process from the run's directory, with the role's prompt, model, effort and tool limits, and stops at the spec gate. Limits (2) and (3) still hold: no role process has a time limit, and every role process runs under the operator's own login and settings |
+| 2 | Event dispatcher | Notice a state change and start the right role with the right inputs. Routes on the `STATUS:` line of the last output, per the routing table | Webhooks + Actions `on:` events | A loop (cron, every 1–5 min) that queries the store for tickets in a "ready for X" state and launches X. Polling is fine; nothing here is latency-sensitive. For a v0 inside one Claude Code session, a Workflow script: each agent() call is a fresh context, the fan-out, join, and round counters are plain code, and the same routing table lifts into the loop later. Three v0 limits. (1) The script has no filesystem or clock, so store reads and writes go through a clerk agent calling the CLI; the guards live in the CLI, not the clerk. The clerk never restates a command's output: it returns stdout verbatim with the exit code and stderr, and the script parses the JSON itself, since a schema shaped like the command's output lets the clerk re-type the answer and still validate. A non-zero exit is a refusal and no JSON on stdout is a failed store call; neither is ever read as an answer. A launch copy of a script, which `factory launch-script` writes with the instance's models, round limits and store in one line, takes its configuration from that line instead of a clerk, and both scripts read a reply as one JSON value before they try its lines one at a time, so a reply the clerk spread over several lines still parses. (2) A hung agent blocks the join until a human skips it, so the piece-3 kill is post-hoc. (3) v0 gives fresh context, not isolation: every agent() call shares the session's checkout, credentials, and git identity. Use a worktree per call, run the clerk's CLI under a harness identity that has no verb for approval rows (humans write those directly), and treat v0 as exercising the routing table, not as producing trusted merges. `factory drive TICKET` is the external dispatcher, outside the Workflow tool: an ordinary Python process that routes as the two scripts do and calls the store CLI's own entry point in its own process, one call at a time. It has no clerk, so limit (1) does not apply to it. It starts each role as one headless `claude -p` process from the run's directory, with the role's prompt, model, effort and tool limits, and stops at the spec gate. Limits (2) and (3) still hold: no role process has a time limit, and every role process runs under the operator's own login and settings |
 | 3 | Isolated run per role | Every role invocation starts in a clean checkout with no memory of earlier runs and only its declared inputs. This is what "fresh context per checker" means in practice | Actions job on a fresh runner | A container or VM per run (Docker, Firecracker, K8s Job). Run `claude -p` with the preamble + role prompt as the system prompt and the inputs on stdin. Destroy the environment after. A run that exceeds {time budget, token budget} is killed, recorded as a result row for that head and role so no join waits on it, and its ticket parked |
 | 4 | Scoped credentials | Each role gets only the access its rules allow. Implementer: push to its own branch. Triage, spec writer, critic, planner, reviewer, verifier, and gate runner: read-only clone plus a shell, with no secrets in the environment, since they run PR code before any security check has passed (model access through a proxy sidecar that holds the key, so the container has none to leak; no git write token; restricted egress). Retro: push a branch and open a PR, nothing else. No role can push to main. Only the harness identity and humans write the ticket store; role outputs enter it through the dispatcher, and the merge gate accepts an approval row only if a human identity pushed it, judged by the server's pusher identity, not the commit author | Job-level `permissions:` on a per-job `GITHUB_TOKEN` | One git user or deploy key per role, with server-side rights set on the git host. Secrets injected per job from a vault or env, never baked into the image |
 | 5 | Change proposal | A unit of review: a branch, its base, its head commit, and a place for the PR description and findings. Approvals attach to the head commit. Fix rounds push to the same branch, which is the ticket's identity | Pull requests | A branch naming convention (`ticket/<id>`) plus a record in the ticket store holding base, head SHA, and the description. GitLab MRs or Gerrit changes are direct equivalents |
@@ -61,7 +61,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Spec drift.** Between the writing of a spec and the build of one of its sub-tickets, other tickets merge, and a sibling that the sub-ticket's checks rely on may not have merged yet. The harness checks for this before the implementer spends a run on it. Every spec version the store keeps, from `spec add`, a gate edit or `spec amend`, records the integration branch's head when it was stored, as `integration_head` in `specs/<ticket id>/v<n>.yaml`; the value is null when the target repo or branch does not resolve. Before a sub-ticket's implementer run, `run start` checks for drift, ahead of the sibling-tests check. It checks only while the sub-ticket has no finished implementer run and no ruling on file. Two rules find drift. The sibling rule: the sub-ticket's Acceptance field names, by id or by plan label as a whole token, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. The test rule counts from the head recorded with the parent's approved version. It is skipped when that version has no record, because it was stored before the record existed, or when the head is null or not a commit in the target repo. For each first-parent commit on the integration branch since that head that changed a file the version's design part names, each test file the commit changed is a finding, unless the design's `## Tests to change` or the sub-ticket's "Tests to change" lists it. A first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans, is not counted, because the plan expects its siblings' changes. Every other commit and merge still counts. Named files are the design part's backticked paths that exist at the integration branch's head, other than test files and `.md` documents, which nearly every ticket edits. A test file's name starts with `test_`, ends `_test.<ext>`, or contains `.test.`. The test rule approximates "a test pins behaviour the spec changes". Measured on two stores' history, it would have caught 9 of 10 known breaks, and it parks about half of all sub-tickets. On drift, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build parks the sub-ticket with that error as the reason. The human amends the spec (`factory spec amend`, Spec store below), rules, or both; `resolve --ruling` returns the sub-ticket to its implementer, and the ruling on file stops the check from repeating.
 
-**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths` and `stats`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
+**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `launch-script`, `status parse`, `log tail`, `paths` and `stats`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
@@ -106,7 +106,7 @@ Rules the table relies on:
 - A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs. When either run's last message says it is still waiting on a command it started, the park reason adds `ended its turn waiting on a background command`, because a plain re-dispatch is likely to end the same way.
 - When a human resolves a parked ticket:
   - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
-  - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes. A sub-ticket parked `harness-bug: run start implementer:` from `ready-for-implementer`, because the harness failed to start its implementer run, also returns to its implementer with the ruling, same round. A ruling on any other harness-bug park is refused.
+  - BLOCKED, a critic ESCALATE, and a planner ESCALATE return to the role that emitted them with the ruling, same round, or the human re-scopes (spec gate or writer round reset) or closes. A sub-ticket parked `harness-bug: run start implementer:` from `ready-for-implementer`, because the harness failed to start its implementer run, also returns to its implementer with the ruling, same round. A ruling on any other harness-bug park is refused. A sub-ticket parked with a `harness-bug:` reason from `ready-for-implementer` after its newest implementer run finished READY-FOR-REVIEW, as when that run's `run finish` reply did not parse, returns to its checks with `resolve --to checks`: its head becomes its branch tip, and its PR round takes the step the build applies on that move: a first round's 0 becomes 1, and a later round is unchanged.
   - A merge the gate refused for an undeclared protected path parks as BLOCKED. A ruling returns the sub-ticket to its implementer, same round. `resolve --accept-paths` instead adds the named paths to what that sub-ticket may change and returns it to its checks, whose passing results stand; every other merge condition still applies.
   - A spec loop at max rounds goes to the spec gate.
   - A parent-close FAILED or SPEC-DEFECT, an archive that does not apply, or a sub-ticket closed by the human, parks the parent: the human amends the spec and re-plans (new sub-tickets under the same parent) or closes the parent. A new plan made from a later approved version supersedes the earlier plan's sub-tickets that have not merged: they keep their records and ids, are no longer dispatched, and neither park the parent nor hold back its close. Merged ones stay merged and count toward the close.
diff --git a/factory/cli.py b/factory/cli.py
index 1b88875..ebf9200 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -15,7 +15,7 @@ from pathlib import Path
 
 import yaml
 
-from factory import compose, gitops, instance, specstore, status, store, subtickets, tripwire
+from factory import compose, gitops, instance, launch, specstore, status, store, subtickets, tripwire
 from factory.common import _add_spec_version, _rel, fence, out
 from factory.drift import _check_drift, _check_sibling_tests
 from factory.gates import (_parent_close_verified, archive_cmd, merge_cmd, results_record, results_show,
@@ -123,26 +123,6 @@ def ticket_set(a, root, cfg):
     out(res)
 
 
-def _apply_round(t: dict, op: str | None, cfg: dict) -> None:
-    if not op:
-        return
-    m = re.fullmatch(r"(spec|pr):(init|\+1|reset)", op)
-    if not m:
-        raise Refused(f"bad --round {op}; expected spec|pr:init|+1|reset")
-    loop, act = m.groups()
-    cur = t["round"][loop]
-    mx = cfg["max_rounds"][loop]
-    if act == "init":
-        if cur == 0:
-            t["round"][loop] = 1
-    elif act == "+1":
-        if cur + 1 > mx:
-            raise Refused(f"round.{loop} {cur} is at max_rounds {mx}")
-        t["round"][loop] = cur + 1
-    else:
-        t["round"][loop] = 0
-
-
 def _check_edge(cfg: dict, frm: str, to: str) -> None:
     if to not in cfg["routing"].get(frm, []):
         raise Refused(f"no route {frm} → {to}: not a routing edge")
@@ -161,7 +141,7 @@ def ticket_transition(a, root, cfg):
             raise Refused(f"{t['id']} has sub-tickets: it closes after a VERIFIED parent-close run (or `resolve {t['id']} --close`)")
         if specstore.is_active(root) and specstore.change_dir(root, t["id"]).exists():
             raise Refused(f"{t['id']} is verified but not archived: run `archive {t['id']}` first")
-    _apply_round(t, a.round, cfg)
+    store._apply_round(t, a.round, cfg)
     if a.to != "parked":
         t["parked"] = None
     store.record_transition(root, t, a.to, a.by,
@@ -642,7 +622,7 @@ def spec_tasks(a, root, cfg):
 # ----- misc ---------------------------------------------------------------------
 
 def config_cmd(a, root, cfg):
-    out({"ok": True, "models": cfg["models"], "max_rounds": cfg["max_rounds"], "state_dir": str(root)})
+    out({"ok": True, **launch.config_values(root, cfg)})
 
 
 def status_parse(a, root, cfg):
@@ -816,7 +796,9 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("--answer")
     p.add_argument("--ruling")
     p.add_argument("--accept-paths", metavar="F", help="a sub-ticket the merge gate refused for undeclared protected paths: accept them under the approved design and return it to its reviewer and verifier")
-    p.add_argument("--to")
+    p.add_argument("--to", metavar="spec-gate|checks",
+                   help="spec-gate: a parked ticket with a spec back to the spec gate; checks: a sub-ticket parked "
+                        "by a harness-bug after its implementer finished READY-FOR-REVIEW back to its checks")
     p.add_argument("--redispatch", action="store_true")
     p.add_argument("--replan", metavar="F", help="a parked parent whose sub-tickets all merged: back to the planner with F as a ruling")
     p.add_argument("--close", action="store_true")
@@ -838,6 +820,10 @@ def build_parser() -> argparse.ArgumentParser:
     p.set_defaults(fn=drive_cmd)
     p = sp.add_parser("config")
     p.set_defaults(fn=config_cmd)
+    p = sp.add_parser("launch-script", help="write a launch copy of a workflow script, the instance's models, "
+                                            "round limits and store in one line; prints its path as `script`")
+    p.add_argument("name", choices=("intake", "build"))
+    p.set_defaults(fn=launch.launch_script)
     st = sp.add_parser("status").add_subparsers(dest="sub", required=True)
     p = st.add_parser("parse")
     p.add_argument("file")
@@ -856,7 +842,7 @@ def build_parser() -> argparse.ArgumentParser:
 # `paths` and `stats` never reach the fence (main() runs them before it); they are listed so this set
 # matches the documents' read-only list.
 READ_ONLY = {("ticket", "show"), ("ticket", "join"), ("results", "show"), ("config", None),
-             ("status", "parse"), ("log", "tail"), ("paths", None), ("stats", None)}
+             ("launch-script", None), ("status", "parse"), ("log", "tail"), ("paths", None), ("stats", None)}
 
 
 def main(argv: list[str] | None = None) -> int:
diff --git a/factory/gates.py b/factory/gates.py
index ab9fd3a..ad5ddf2 100644
--- a/factory/gates.py
+++ b/factory/gates.py
@@ -11,25 +11,8 @@ from factory.store import Refused
 
 def ticket_head(a, root, cfg):
     t = store.load_ticket(root, a.id)
-    if not t.get("branch"):
-        raise Refused(f"{t['id']} has no branch yet")
-    repo = gitops.repo_root()
-    head = gitops.rev(repo, t["branch"])
-    changed = head != t.get("head")
-    t["head"] = head
-    if t.get("merge_refused"):
-        if gitops.head_contains(repo, head, gitops.integration_branch(cfg, repo)):
-            t["merge_refused"] = None
-            t["conflict_runs"] = 0
-        else:
-            # A conflict run that did not merge the integration branch in. Counted once per
-            # implementer run (this command may be called more than once), so the loop is bounded.
-            last = [r for r, _ in store.ticket_runs(root, t["id"], "implementer", finished=True)]
-            if last and last[-1] != t.get("conflict_counted_run"):
-                t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
-                t["conflict_counted_run"] = last[-1]
-    store.save_ticket(root, t)
-    out({"ok": True, "id": t["id"], "head": head, "branch": t["branch"], "changed": changed,
+    changed = store.set_head(root, cfg, t)
+    out({"ok": True, "id": t["id"], "head": t["head"], "branch": t["branch"], "changed": changed,
          "merge_refused": t.get("merge_refused"), "conflict_runs": int(t.get("conflict_runs") or 0)})
 
 
diff --git a/factory/human.py b/factory/human.py
index f282e5b..f0151b3 100644
--- a/factory/human.py
+++ b/factory/human.py
@@ -252,9 +252,19 @@ def resolve(a, root, cfg):
         dest = _copy_record(d, "ruling", a.accept_paths)
         t["accepted_paths"] = sorted(set(t.get("accepted_paths") or []) | set(paths))
         move("checks-in-flight", "accept-paths", {"ruling": _rel(root, dest), "head": head, "accepted": paths})
+    elif a.to == "checks":
+        # A store command failed after the implementer finished (issue #112: its `run finish` reply
+        # did not parse): back to its checks at the branch tip, with the round step the build applies.
+        if not (st == "parked" and parked.get("from") == "ready-for-implementer" and reason.startswith("harness-bug:")
+                and store.implemented_since_ready(root, t["id"])):
+            raise Refused("--to checks applies to a sub-ticket parked by a harness-bug from ready-for-implementer after "
+                          f"its implementer run finished READY-FOR-REVIEW; {t['id']} is {st} ({reason or 'no park'})")
+        store.set_head(root, cfg, t)
+        store._apply_round(t, "pr:init", cfg)
+        move("checks-in-flight", "to-checks", {"head": t["head"]})
     elif a.to:
         if a.to != "spec-gate":
-            raise Refused("--to accepts only spec-gate")
+            raise Refused("--to accepts only spec-gate or checks")
         if st != "parked" or t["spec"]["version"] < 1:
             raise Refused(f"--to spec-gate needs a parked ticket with a spec version; {t['id']} is {st}")
         move("awaiting-spec-gate", "to-spec-gate", {})
@@ -283,7 +293,7 @@ def resolve(a, root, cfg):
             raise Refused(f"{t['id']} is already closed")
         move("closed", "close", decided("resolve --close"))
     else:
-        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate | --redispatch | "
+        raise Refused("resolve needs one of --answer F | --ruling F | --accept-paths F | --to spec-gate|checks | --redispatch | "
                       "--replan F | --close")
 
 
diff --git a/factory/launch.py b/factory/launch.py
new file mode 100644
index 0000000..bc1c03b
--- /dev/null
+++ b/factory/launch.py
@@ -0,0 +1,57 @@
+"""`factory launch-script intake|build`: a launch copy of a workflow script, with the instance's
+values written into one line so no clerk relays them, and the values `factory config` prints."""
+from __future__ import annotations
+
+import json
+import shutil
+import tempfile
+import time
+from pathlib import Path
+
+from factory import instance
+from factory.common import out
+from factory.store import Refused
+
+LAUNCH_LINE = "const LAUNCH = null"
+WRITTEN_BY = "factory launch-script"
+
+
+def config_values(root: Path, cfg: dict) -> dict:
+    """What `factory config` prints besides `ok`; a launch copy carries the same values."""
+    return {"models": cfg["models"], "max_rounds": cfg["max_rounds"], "state_dir": str(root)}
+
+
+def launch_script(a, root, cfg):
+    """Write `<name>.js` read-only into a new `factory-launch-*` directory under the temporary
+    directory: the workflow script with its one `const LAUNCH = null` line set to the instance's
+    values, the running harness revision and the instance. Writes nothing to the checkout or store."""
+    src = instance.HARNESS / "factory" / "workflows" / f"{a.name}.js"
+    lines = src.read_text(encoding="utf-8").split("\n")
+    if lines.count(LAUNCH_LINE) != 1:
+        raise Refused(f"{src} holds the line `{LAUNCH_LINE}` {lines.count(LAUNCH_LINE)} times, not once; "
+                      "no launch copy written")
+    rev, inst = instance.harness_revision(), str(instance.require())
+    launch = {"written_by": WRITTEN_BY, "source": str(src), "harness_revision": rev, "instance": inst,
+              **config_values(root, cfg)}
+    lines[lines.index(LAUNCH_LINE)] = f"const LAUNCH = {json.dumps(launch, ensure_ascii=False)}"
+    _remove_old_copies()
+    dest = Path(tempfile.mkdtemp(prefix="factory-launch-")) / src.name
+    dest.write_text("\n".join(lines), encoding="utf-8")
+    dest.chmod(0o444)
+    out({"ok": True, "script": str(dest), "source": str(src), "harness_revision": rev, "instance": inst})
+
+
+def _remove_old_copies() -> None:
+    """Remove each `factory-launch-*` directory under the temporary directory that is more than an
+    hour old and holds only a launch copy. The Workflow tool keeps its own copy of a script once
+    launched, so such a copy is no longer read; a newer one may be about to be launched by another
+    session sharing the directory. Any other directory, and any error, is skipped."""
+    cutoff = time.time() - 3600
+    for d in Path(tempfile.gettempdir()).glob("factory-launch-*"):
+        try:
+            files = list(d.iterdir())
+            if (d.stat().st_mtime < cutoff and len(files) == 1 and files[0].name in ("intake.js", "build.js")
+                    and f'"written_by": "{WRITTEN_BY}"' in files[0].read_text(encoding="utf-8")):
+                shutil.rmtree(d)
+        except (OSError, ValueError):
+            continue
diff --git a/factory/store.py b/factory/store.py
index 7ef578b..02b14f8 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -4,6 +4,7 @@ from __future__ import annotations
 import datetime as dt
 import hashlib
 import json
+import re
 import shutil
 from pathlib import Path
 
@@ -99,6 +100,26 @@ def log_lines(root: Path):
         yield from p.read_text(encoding="utf-8").splitlines()
 
 
+def implemented_since_ready(root: Path, tid: str) -> bool:
+    """Whether ticket `tid`'s newest implementer run started after the ticket last entered
+    ready-for-implementer, and finished READY-FOR-REVIEW. Read in the event log's order: its
+    timestamps are whole seconds. A move into the state is any event of the ticket whose `to`, or
+    for `ticket.created` whose `status`, is ready-for-implementer."""
+    entered = started = -1
+    run = status = None
+    for i, ln in enumerate(log_lines(root)):
+        e = json.loads(ln)
+        if e.get("ticket") != tid:
+            continue
+        if e.get("to") == "ready-for-implementer" or (e["event"] == "ticket.created" and e.get("status") == "ready-for-implementer"):
+            entered = i
+        elif e["event"] == "run.started" and e.get("role") == "implementer":
+            started, run, status = i, e.get("run"), None
+        elif e["event"] == "run.finished" and e.get("run") == run:
+            status = e.get("status")
+    return started > entered and status == "READY-FOR-REVIEW"
+
+
 def ticket_path(root: Path, tid: str) -> Path:
     return root / "tickets" / f"{tid}.yaml"
 
@@ -163,6 +184,52 @@ def record_transition(root: Path, t: dict, to: str, by: str, history: dict | Non
     return frm
 
 
+def _apply_round(t: dict, op: str | None, cfg: dict) -> None:
+    if not op:
+        return
+    m = re.fullmatch(r"(spec|pr):(init|\+1|reset)", op)
+    if not m:
+        raise Refused(f"bad --round {op}; expected spec|pr:init|+1|reset")
+    loop, act = m.groups()
+    cur = t["round"][loop]
+    mx = cfg["max_rounds"][loop]
+    if act == "init":
+        if cur == 0:
+            t["round"][loop] = 1
+    elif act == "+1":
+        if cur + 1 > mx:
+            raise Refused(f"round.{loop} {cur} is at max_rounds {mx}")
+        t["round"][loop] = cur + 1
+    else:
+        t["round"][loop] = 0
+
+
+def set_head(root: Path, cfg: dict, t: dict) -> bool:
+    """Set ticket `t`'s head to the tip of its branch and save it, as `ticket head` does; returns
+    whether the head changed. A merge-refused ticket whose new head contains the integration branch
+    is cleared of the refusal; one whose head does not is a conflict run that did not merge it in."""
+    from factory import gitops  # local: gitops imports this module
+    if not t.get("branch"):
+        raise Refused(f"{t['id']} has no branch yet")
+    repo = gitops.repo_root()
+    head = gitops.rev(repo, t["branch"])
+    changed = head != t.get("head")
+    t["head"] = head
+    if t.get("merge_refused"):
+        if gitops.head_contains(repo, head, gitops.integration_branch(cfg, repo)):
+            t["merge_refused"] = None
+            t["conflict_runs"] = 0
+        else:
+            # A conflict run that did not merge the integration branch in. Counted once per
+            # implementer run (this command may be called more than once), so the loop is bounded.
+            last = [r for r, _ in ticket_runs(root, t["id"], "implementer", finished=True)]
+            if last and last[-1] != t.get("conflict_counted_run"):
+                t["conflict_runs"] = int(t.get("conflict_runs") or 0) + 1
+                t["conflict_counted_run"] = last[-1]
+    save_ticket(root, t)
+    return changed
+
+
 def park_ticket(root: Path, t: dict, reason: str, outputs: list[str], question: str | None = None,
                 by: str = "park") -> None:
     """Park ticket `t` (the caller has checked it is not parked or closed): record where it came
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 2f7d097..52f908c 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -7,14 +7,18 @@ export const meta = {
     { title: 'Close', detail: 'one verifier run on the integration branch against the parent spec; VERIFIED archives, then closes' },
   ],
 }
-// args: { ticket, repo, instance?, state?, target?, integration?, stubs?, inlineRoles? }  — repo/instance/state/stubs/inlineRoles as in intake.js.
+// args: { ticket, repo, instance?, state?, target?, integration?, stubs?, inlineRoles? }  — repo/instance/state/stubs/inlineRoles as in intake.js;
+//   a launch copy takes its instance from the copy.
 // Local-commit stand-in (operator, 2026-10-02): no remote, no CI. The gate suite is run by the
 // verifier and recorded as the ci row; the merge is a local --no-ff merge into the integration
 // branch. The routing is build spec part H, build.js; the join itself is `factory ticket join`.
 
 const TICKET = args.ticket
 const REPO = args.repo
-const INSTANCE = args.instance
+// `factory launch-script build` writes a launch copy of this script with the next line set to the
+// instance's models, round limits and store, the harness revision and the instance: no clerk relays them.
+const LAUNCH = null
+const INSTANCE = LAUNCH ? LAUNCH.instance : args.instance
 let STATE = args.state || null  // set from `factory config` below when not given
 // target = the repo the implementer works in (default: the instance's repo, the parent of its `.factory/`);
 // integration = the branch merged into (default: config integration_branch, else the target's current branch).
@@ -44,8 +48,11 @@ async function clerk(cmd, phase, label) {
     `Report its stdout verbatim (do not reformat, summarize or re-encode it), its exit code, and its stderr verbatim.`,
     { agentType: INLINE ? 'general-purpose' : `${PREFIX}clerk`, model: MODELS.clerk, effort: 'low', phase, label: `clerk: ${label}`, schema: CLERK_SCHEMA })
   if (res === null) return { ok: false, exit: -1, stderr: 'clerk returned nothing' }
-  const lines = String(res.stdout || '').trim().split('\n').filter(l => l.trim())
+  // The whole reply first: a clerk has relayed one JSON value spread over several lines.
+  const text = String(res.stdout || '').trim()
   let parsed = null
+  try { parsed = JSON.parse(text) } catch (e) { parsed = null }
+  const lines = text.split('\n').filter(l => l.trim())
   for (let i = lines.length - 1; i >= 0 && parsed === null; i--) {
     try { parsed = JSON.parse(lines[i]) } catch (e) { parsed = null }
   }
@@ -222,7 +229,10 @@ async function buildOne(st) {
 }
 
 // --- start
-const cfg = await clerk(`${BIN} config`, 'Plan', 'config')
+if (LAUNCH && args.instance && args.instance !== LAUNCH.instance) {
+  return { ticket: TICKET, error: `launch copy written for instance ${LAUNCH.instance}, launched with ${args.instance}` }
+}
+const cfg = LAUNCH ? { ok: true, ...LAUNCH } : await clerk(`${BIN} config`, 'Plan', 'config')
 if (cfg.ok) { MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr; if (!STATE) STATE = cfg.state_dir }
 if (!STATE) return { ticket: TICKET, error: `no store: factory config failed: ${cfg.stderr || cfg.error || ''}` }
 const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Plan', 'ticket show')
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index 87635f6..3b045ba 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -10,7 +10,8 @@ export const meta = {
 //   repo     = absolute path of the harness checkout (bin/factory lives under it); the clerk runs from it
 //   instance = absolute path of the target repo's `.factory/` (`factory paths` prints it); when given,
 //              every store command runs with FACTORY_INSTANCE=<instance>. Without it the harness walks
-//              up from `repo`, which finds only the harness repo's own instance
+//              up from `repo`, which finds only the harness repo's own instance. A launch copy takes its
+//              instance from the copy, and returns an error when given another
 //   state    = absolute path of the store (FACTORY_STATE); optional: by default the instance's own
 //              store, as `factory config` reports it
 //   stubs = directory of <role>-<n>.md fixture outputs; when set, every role is the factory-stub agent
@@ -21,7 +22,10 @@ export const meta = {
 
 const TICKET = args.ticket
 const REPO = args.repo
-const INSTANCE = args.instance
+// `factory launch-script intake` writes a launch copy of this script with the next line set to the
+// instance's models, round limits and store, the harness revision and the instance: no clerk relays them.
+const LAUNCH = null
+const INSTANCE = LAUNCH ? LAUNCH.instance : args.instance
 let STATE = args.state || null  // set from `factory config` below when not given
 const ENV = ['FACTORY_DISPATCH=1', INSTANCE ? `FACTORY_INSTANCE=${INSTANCE}` : '', STATE ? `FACTORY_STATE=${STATE}` : ''].filter(Boolean).join(' ')
 const BIN = `${ENV ? ENV + ' ' : ''}${REPO}/bin/factory`
@@ -53,8 +57,11 @@ async function clerk(cmd, phase, label) {
     `Report its stdout verbatim (do not reformat, summarize or re-encode it), its exit code, and its stderr verbatim.`,
     { agentType: INLINE ? 'general-purpose' : `${PREFIX}clerk`, model: MODELS.clerk, effort: 'low', phase, label: `clerk: ${label}`, schema: CLERK_SCHEMA })
   if (res === null) return { ok: false, exit: -1, stderr: 'clerk returned nothing' }
-  const lines = String(res.stdout || '').trim().split('\n').filter(l => l.trim())
+  // The whole reply first: a clerk has relayed one JSON value spread over several lines.
+  const text = String(res.stdout || '').trim()
   let parsed = null
+  try { parsed = JSON.parse(text) } catch (e) { parsed = null }
+  const lines = text.split('\n').filter(l => l.trim())
   for (let i = lines.length - 1; i >= 0 && parsed === null; i--) {
     try { parsed = JSON.parse(lines[i]) } catch (e) { parsed = null }
   }
@@ -143,7 +150,10 @@ async function transition(to, roundOp, phase) {
 }
 
 // --- start: read config and the ticket's stored state (resumption starts from what the store holds)
-const cfg = await clerk(`${BIN} config`, 'Triage', 'config')
+if (LAUNCH && args.instance && args.instance !== LAUNCH.instance) {
+  return { ticket: TICKET, error: `launch copy written for instance ${LAUNCH.instance}, launched with ${args.instance}` }
+}
+const cfg = LAUNCH ? { ok: true, ...LAUNCH } : await clerk(`${BIN} config`, 'Triage', 'config')
 if (cfg.ok) { MODELS = cfg.models; MAX = cfg.max_rounds.spec; if (!STATE) STATE = cfg.state_dir }
 if (!STATE) return { ticket: TICKET, error: `no store: factory config failed: ${cfg.stderr || cfg.error || ''}` }
 const show = await clerk(`${BIN} ticket show ${TICKET} --json`, 'Triage', 'ticket show')
diff --git a/tests/factory/test_launch_script.py b/tests/factory/test_launch_script.py
new file mode 100644
index 0000000..855bf26
--- /dev/null
+++ b/tests/factory/test_launch_script.py
@@ -0,0 +1,115 @@
+"""`factory launch-script intake|build` (T-0054, issue #109): a launch copy of a workflow script.
+
+A launch copy is the script with its line `const LAUNCH = null` replaced by one JSON object: the
+instance's models, round limits and store as `factory config` prints them, the harness revision and
+the instance. The command writes it read-only into a new `factory-launch-*` directory under the
+temporary directory, and nothing to the checkout or the store. It is refused wherever `config` is,
+runs unmarked while a run is in flight, as `config` does, and first removes launch copies more than
+an hour old.
+
+Every test points TMPDIR inside its own tmp_path (the autouse fixture below), and `launch` fails a
+test whose copy lands anywhere else, so no test leaves a copy in the real temporary directory.
+"""
+from __future__ import annotations
+
+import difflib
+import json
+import os
+import stat
+import time
+from pathlib import Path
+
+import pytest
+
+from ._cli import REPO, cli, git_repo, js, run, tree
+from ._fixtures import assert_refused, snapshot, start_triage, target  # noqa: F401  (target is a fixture)
+from ._fixtures import other_request as request
+
+PREFIX = "const LAUNCH = "
+
+
+@pytest.fixture(autouse=True)
+def launch_tmp(tmp_path: Path, monkeypatch) -> Path:
+    d = tmp_path / "tmp"
+    d.mkdir()
+    monkeypatch.setenv("TMPDIR", str(d))
+    return d
+
+
+def launch(cp, launch_tmp: Path) -> Path:
+    assert cp.returncode == 0, cp.stderr
+    script = Path(js(cp)["script"])
+    assert script.is_relative_to(launch_tmp), script
+    return script
+
+
+def copies(launch_tmp: Path) -> list[str]:
+    return sorted(p.name for p in launch_tmp.glob("factory-launch-*"))
+
+
+def store_with_a_ticket(tmp_path: Path) -> Path:
+    store = tmp_path / "store"
+    (tmp_path / "r.md").write_text("# F\n\nDo x.\n")
+    assert run(store, "ticket", "new", "--file", str(tmp_path / "r.md")).returncode == 0
+    return store
+
+
+@pytest.mark.parametrize("name", ["intake", "build"])
+def test_a_launch_copy_is_its_script_with_one_line_set_to_the_instances_values(tmp_path, launch_tmp, name):
+    store = store_with_a_ticket(tmp_path)
+    before, checkout = tree(store), run(store, "paths")
+    cp = run(store, "launch-script", name)
+    script = launch(cp, launch_tmp)
+    src = REPO / "factory" / "workflows" / f"{name}.js"
+    paths, config = js(checkout), js(run(store, "config"))
+    assert script.name == f"{name}.js" and script.parent.parent == launch_tmp and script.parent.name.startswith("factory-launch-")
+    assert os.listdir(script.parent) == [f"{name}.js"]
+    diff = [ln for ln in difflib.unified_diff(src.read_text().splitlines(), script.read_text().splitlines(), lineterm="", n=0)
+            if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
+    assert diff[0] == "-const LAUNCH = null" and len(diff) == 2 and diff[1].startswith("+" + PREFIX)
+    assert json.loads(diff[1][1 + len(PREFIX):]) == {
+        "written_by": "factory launch-script", "source": str(src), "harness_revision": paths["harness_revision"],
+        "instance": paths["instance"], "models": config["models"], "max_rounds": config["max_rounds"],
+        "state_dir": config["state_dir"]}
+    assert stat.S_IMODE(script.stat().st_mode) == 0o444
+    assert js(cp) == {"ok": True, "script": str(script), "source": str(src),
+                      "harness_revision": paths["harness_revision"], "instance": paths["instance"]}
+    assert tree(store) == before
+
+
+def test_launch_script_is_refused_with_configs_error_where_the_lock_does_not_name_the_running_harness(tmp_path, launch_tmp):
+    t = git_repo(tmp_path / "tgt")
+    assert cli(t, "init", "--repo-name", "demo").returncode == 0
+    (t / ".factory" / "harness.lock").write_text("0" * 40 + "\n")
+    config, cp = cli(t, "config"), cli(t, "launch-script", "build")
+    assert config.returncode == 2 and cp.returncode == 2
+    assert cp.stderr == config.stderr and "is not the revision this instance accepted" in cp.stderr
+    assert copies(launch_tmp) == []
+
+
+def test_launch_script_runs_unmarked_while_a_run_is_in_flight_and_changes_nothing_in_the_target(target, tmp_path, launch_tmp):
+    rid = start_triage(target)
+    before = snapshot(target)
+    launch(cli(target, "launch-script", "build"), launch_tmp)
+    assert_refused(cli(target, "ticket", "new", "--file", request(tmp_path)), f"in flight: {rid}")
+    assert snapshot(target) == before and len(copies(launch_tmp)) == 1
+
+
+def test_launch_script_removes_only_launch_copies_over_an_hour_old(tmp_path, launch_tmp):
+    store = store_with_a_ticket(tmp_path)
+    old = launch(run(store, "launch-script", "build"), launch_tmp).parent
+    fresh = launch(run(store, "launch-script", "intake"), launch_tmp).parent
+    other = launch_tmp / "factory-launch-other"  # an old directory that holds no launch copy
+    other.mkdir()
+    (other / "build.js").write_text("x\n")
+    extra = launch_tmp / "factory-launch-extra"  # an old launch copy with a second file beside it
+    extra.mkdir()
+    (extra / "build.js").write_bytes((old / "build.js").read_bytes())
+    (extra / "notes.txt").write_text("x\n")
+    hour_ago = time.time() - 3700
+    for d in (old, other, extra):
+        os.utime(d, (hour_ago, hour_ago))
+    new = launch(run(store, "launch-script", "build"), launch_tmp).parent
+    assert not old.exists()
+    assert fresh.exists() and other.exists() and extra.exists() and new.exists()
+    assert copies(launch_tmp) == sorted(d.name for d in (fresh, other, extra, new))
diff --git a/tests/factory/test_resolve_to_checks.py b/tests/factory/test_resolve_to_checks.py
new file mode 100644
index 0000000..ac8f82c
--- /dev/null
+++ b/tests/factory/test_resolve_to_checks.py
@@ -0,0 +1,145 @@
+"""`factory resolve <id> --to checks` (T-0054, issue #112): the route back to its checks for a
+sub-ticket parked by a harness-bug after its implementer finished.
+
+On the real run the clerk relayed `run finish`'s one-line JSON over several lines, the build found
+no JSON, and it parked the sub-ticket from ready-for-implementer although its implementer run had
+finished READY-FOR-REVIEW. The route reads the branch tip into the ticket as `ticket head` does,
+applies the build's `pr:init` round step and moves it to checks-in-flight. Every other park, and a
+ticket that is not parked, is refused with nothing written.
+
+Black-box through `bin/factory` on a throwaway store whose sub-ticket T-0001.1 builds in a scratch
+target repository.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+from ._cli import CliStore, approved_parent, git_repo
+
+PARK = "harness-bug: run finish implementer: exit 0, no JSON on stdout"
+REFUSAL = "--to checks applies to"
+
+
+class SubTicket(CliStore):
+    """T-0001 past the spec gate and planned as one sub-ticket, T-0001.1, ready for its implementer
+    with no branch yet."""
+
+    def __init__(self, tmp_path: Path):
+        self.root = tmp_path / "store"
+        self.target = git_repo(tmp_path / "t")
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(self.target),
+                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
+        (tmp_path / "req.md").write_text("# Fixture\n\nThe bot should do the thing.\n")
+        (tmp_path / "spec.md").write_text("## Problem\nx\n")
+        (tmp_path / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+        self.ok("ticket", "new", "--file", str(tmp_path / "req.md"))
+        approved_parent(self.ok, "T-0001", tmp_path / "spec.md")
+        self.ok("subticket", "add", "T-0001", "--file", str(tmp_path / "plan.md"))
+        self.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+
+    def implement(self, status: str) -> str:
+        """One implementer run on T-0001.1, as the build runs it: one commit on its branch and an
+        output with `status`. Returns the run id."""
+        rid = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
+        wt = yaml.safe_load((self.root / "runs" / rid / "meta.yaml").read_text())["worktree"]
+        (Path(wt) / "work.txt").write_text(rid)
+        for argv in (["add", "work.txt"], ["-c", "user.email=f@x", "-c", "user.name=f", "commit", "-qm", "work"]):
+            subprocess.run(["git", "-C", wt, *argv], check=True, capture_output=True)
+        (self.root / "runs" / rid / "output.md").write_text(f"STATUS: {status}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+        self.ok("run", "finish", rid)
+        return rid
+
+    def tip(self) -> str:
+        return subprocess.run(["git", "-C", str(self.target), "rev-parse", "factory/T-0001.1"],
+                              check=True, capture_output=True, text=True).stdout.strip()
+
+    def ticket(self) -> dict:
+        return yaml.safe_load((self.root / "tickets" / "T-0001.1.yaml").read_text())
+
+    def events(self) -> list[dict]:
+        return [json.loads(ln) for p in sorted((self.root / "log").glob("*.jsonl")) for ln in p.read_text().splitlines()]
+
+    def snapshot(self) -> dict[str, bytes]:
+        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted(self.root.rglob("*"))
+                if p.is_file() and "worktrees" not in p.relative_to(self.root).parts}
+
+
+def test_a_harness_bug_park_after_a_finished_implementer_returns_to_its_checks_at_the_branch_tip(tmp_path):
+    s = SubTicket(tmp_path)
+    s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "park", "T-0001.1", "--reason", PARK)
+    out = s.ok("resolve", "T-0001.1", "--to", "checks")
+    t = s.ticket()
+    assert out["state"] == "checks-in-flight" and out["kind"] == "to-checks" and out["head"] == s.tip()
+    assert t["status"] == "checks-in-flight" and t["parked"] is None
+    assert t["head"] == s.tip() and t["round"]["pr"] == 1
+    assert t["history"][-1]["from"] == "parked" and t["history"][-1]["resolve"] == "to-checks"
+    rec = yaml.safe_load((s.root / "approvals" / "T-0001.1" / "resolve-1.yaml").read_text())
+    assert (rec["kind"], rec["from"], rec["to"], rec["head"]) == ("to-checks", "parked", "checks-in-flight", s.tip())
+    last = s.events()[-1]
+    assert (last["event"], last["kind"], last["to"]) == ("human.resolved", "to-checks", "checks-in-flight")
+
+
+def test_a_later_round_is_unchanged_by_the_route(tmp_path):
+    s = SubTicket(tmp_path)
+    s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
+    s.ok("ticket", "transition", "T-0001.1", "--to", "ready-for-implementer", "--by", "t", "--round", "pr:+1")
+    s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "park", "T-0001.1", "--reason", PARK)
+    s.ok("resolve", "T-0001.1", "--to", "checks")
+    t = s.ticket()
+    assert t["status"] == "checks-in-flight" and t["round"]["pr"] == 2 and t["head"] == s.tip()
+
+
+def _blocked(s: SubTicket) -> None:
+    s.implement("BLOCKED")
+    s.ok("ticket", "park", "T-0001.1", "--reason", PARK)
+
+
+def _revised(s: SubTicket) -> None:
+    # checked and sent back; the next implementer run then failed to start, so the newest
+    # implementer run predates the sub-ticket's return to ready-for-implementer
+    s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
+    s.ok("ticket", "transition", "T-0001.1", "--to", "ready-for-implementer", "--by", "t", "--round", "pr:+1")
+    s.ok("ticket", "park", "T-0001.1", "--reason", "harness-bug: run start implementer: x")
+
+
+def _from_checks(s: SubTicket) -> None:
+    s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "transition", "T-0001.1", "--to", "checks-in-flight", "--by", "t", "--round", "pr:init")
+    s.ok("ticket", "park", "T-0001.1", "--reason", "harness-bug: results record reviewer: x")
+
+
+def _tripwire(s: SubTicket) -> None:
+    rid = s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "park", "T-0001.1", "--reason", f"tripwire: /x changed during {rid}")
+
+
+def _unparked(s: SubTicket) -> None:
+    s.implement("READY-FOR-REVIEW")
+
+
+@pytest.mark.parametrize("setup", [_blocked, _revised, _from_checks, _tripwire, _unparked],
+                         ids=["blocked", "revised", "checks", "tripwire", "unparked"])
+def test_every_other_ticket_is_refused_and_nothing_is_written(tmp_path, setup):
+    s = SubTicket(tmp_path)
+    setup(s)
+    status, before = s.ticket()["status"], s.snapshot()
+    cp = s.cli("resolve", "T-0001.1", "--to", "checks")
+    assert cp.returncode == 2, (cp.stdout, cp.stderr)
+    assert REFUSAL in cp.stderr and f"T-0001.1 is {status}" in cp.stderr
+    assert s.snapshot() == before
+
+
+def test_any_other_to_value_names_both_routes(tmp_path):
+    s = SubTicket(tmp_path)
+    cp = s.cli("resolve", "T-0001.1", "--to", "planner")
+    assert cp.returncode == 2 and "--to accepts only spec-gate or checks" in cp.stderr
diff --git a/tests/factory/test_workflow_launch_copy.py b/tests/factory/test_workflow_launch_copy.py
new file mode 100644
index 0000000..daec3cb
--- /dev/null
+++ b/tests/factory/test_workflow_launch_copy.py
@@ -0,0 +1,230 @@
+"""The workflow scripts under node with a stand-in clerk that miscopies, as the clerk did on real
+runs (T-0054, issues #109 and #112).
+
+- #109: the clerk relayed `factory config` with a role's model retyped. A launch copy (written by
+  `factory launch-script`) asks no clerk for the configuration, so every role, and the clerk itself,
+  runs on the instance's model; the script launched as it is still parks at the role's run start.
+- #112: the clerk relayed a one-line JSON reply pretty-printed over several lines. Both scripts
+  read it as that one value.
+- A sub-ticket parked by #112 and returned with `resolve --to checks` is merged by the next build
+  without another implementer run.
+
+Each clerk command runs for real (sh -c, from this checkout) on a throwaway store; each role is a
+stub that writes the STATUS its test gives it. Every test points TMPDIR inside its own tmp_path.
+"""
+from __future__ import annotations
+
+import json
+import os
+import shutil
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+from ._cli import REPO, CliStore, approved_parent, git_repo
+
+# node driver.mjs <script> <ticket>: runs that workflow script on <ticket> of $FACTORY_STATE.
+# T_SWAP ({"<role>": "<model>"}) names those models in any clerk reply that lists `models`;
+# T_PRETTY=1 relays every JSON reply pretty-printed; T_INSTANCE is passed as the `instance` argument;
+# T_PLAYS ({"<role>": "<STATUS>"}) is the STATUS each role's run writes. An implementer commits one
+# file in its worktree; a checker's output carries the run's head, the verifier's "Gate suite: PASS".
+# Prints one JSON line: every agent call's label and model, each park, and the script's result.
+DRIVER = r"""
+import { readFileSync, writeFileSync } from 'node:fs'
+import { spawnSync } from 'node:child_process'
+const [script, ticket] = process.argv.slice(2)
+const swap = JSON.parse(process.env.T_SWAP || '{}')
+const plays = JSON.parse(process.env.T_PLAYS || '{}')
+const sh = (cmd, cwd) => spawnSync('sh', ['-c', cmd], { cwd, encoding: 'utf8' })
+const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
+const calls = [], parks = []
+const agent = async (prompt, opts) => {
+  calls.push({ label: opts.label, model: opts.model })
+  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
+  if (m) {
+    const cp = sh(m[1], process.cwd())
+    let stdout = cp.stdout, j = null
+    try { j = JSON.parse(stdout.trim().split('\n').pop()) } catch (e) { j = null }
+    if (j && j.models) { Object.assign(j.models, swap); stdout = JSON.stringify(j) + '\n' }
+    if (j && process.env.T_PRETTY) stdout = JSON.stringify(j, null, 2) + '\n'
+    return { stdout, exit: cp.status, stderr: cp.stderr }
+  }
+  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
+  const meta = readFileSync(`${r[1]}/meta.yaml`, 'utf8')
+  const wt = (meta.match(/^worktree: '?([^'\n]+)/m) || [])[1]
+  if (r[2] === 'implementer' && wt) sh('echo work > work.txt && git add work.txt && git -c user.email=f@x -c user.name=f commit -qm work', wt)
+  const head = (meta.match(/^head: '?([0-9a-f]{40})/m) || [])[1]
+  const text = (head && r[2] !== 'implementer' ? `Commit: ${head}\n` : '') + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') +
+    `STATUS: ${plays[r[2]] || 'NONE'}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
+  writeFileSync(`${r[1]}/output.md`, text)
+  return text
+}
+const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) parks.push(`${q[1]}: ${q[2]}`) }
+const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
+const result = await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
+  integration: 'main', inlineRoles: true, ...(process.env.T_INSTANCE ? { instance: process.env.T_INSTANCE } : {}) },
+  agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
+console.log(JSON.stringify({ calls, parks, result }))
+"""
+
+CHECKS = {"reviewer": "APPROVE", "verifier": "VERIFIED"}
+BUILD = {"implementer": "READY-FOR-REVIEW", **CHECKS}
+
+
+@pytest.fixture(autouse=True)
+def launch_tmp(tmp_path: Path, monkeypatch) -> Path:
+    d = tmp_path / "tmp"
+    d.mkdir()
+    monkeypatch.setenv("TMPDIR", str(d))
+    return d
+
+
+class Store(CliStore):
+    """A throwaway store whose tickets build in a scratch target repository."""
+
+    def __init__(self, tmp_path: Path):
+        self.tmp = tmp_path
+        self.root = tmp_path / "store"
+        self.target = git_repo(tmp_path / "t")
+        self.env = {**os.environ, "FACTORY_STATE": str(self.root), "FACTORY_REPO": str(self.target),
+                    "FACTORY_INTEGRATION_BRANCH": "main", "PYTHONDONTWRITEBYTECODE": "1"}
+
+    def new_ticket(self) -> str:
+        req = self.tmp / "req.md"
+        req.write_text("# Fixture\n\nThe bot should do the thing.\n")
+        return self.ok("ticket", "new", "--file", str(req))["id"]
+
+    def planned(self) -> None:
+        """T-0001 past the spec gate and planned as one sub-ticket, T-0001.1, ready for its implementer."""
+        tid = self.new_ticket()
+        (self.tmp / "spec.md").write_text("## Problem\nx\n")
+        (self.tmp / "plan.md").write_text("ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n")
+        approved_parent(self.ok, tid, self.tmp / "spec.md")
+        self.ok("subticket", "add", tid, "--file", str(self.tmp / "plan.md"))
+        self.ok("ticket", "transition", tid, "--to", "planned", "--by", "t")
+
+    def at_checks(self) -> None:
+        """T-0001.1 at checks-in-flight on a branch holding one commit, with no result rows."""
+        self.planned()
+        for argv in (["checkout", "-qb", "factory/T-0001.1"], ["commit", "-q", "--allow-empty", "-m", "work"],
+                     ["checkout", "-q", "main"]):
+            self.git(str(self.target), *argv)
+        head = self.git(str(self.target), "rev-parse", "factory/T-0001.1")
+        self.ok("ticket", "set", "T-0001.1", "status=checks-in-flight", "branch=factory/T-0001.1", f"head={head}")
+
+    def implement(self, status: str) -> None:
+        """One implementer run on T-0001.1, as the build runs it, ending with `status`."""
+        rid = self.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
+        wt = yaml.safe_load((self.root / "runs" / rid / "meta.yaml").read_text())["worktree"]
+        (Path(wt) / "work.txt").write_text(rid)
+        self.git(wt, "add", "work.txt")
+        self.git(wt, "commit", "-qm", "work")
+        (self.root / "runs" / rid / "output.md").write_text(f"STATUS: {status}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+        self.ok("run", "finish", rid)
+
+    def git(self, cwd: str, *argv: str) -> str:
+        return subprocess.run(["git", "-C", cwd, "-c", "user.email=f@x", "-c", "user.name=f", *argv],
+                              check=True, capture_output=True, text=True).stdout.strip()
+
+    def launch_copy(self, name: str) -> str:
+        script = self.ok("launch-script", name)["script"]
+        assert Path(script).is_relative_to(self.tmp), script
+        return script
+
+    def drive(self, script: str, ticket: str, plays: dict, **env: str) -> dict:
+        node = shutil.which("node")
+        assert node, "node must be on PATH: this case runs a workflow script"
+        driver = self.tmp / "driver.mjs"
+        driver.write_text(DRIVER)
+        cp = subprocess.run([node, str(driver), script, ticket], capture_output=True, text=True, cwd=REPO,
+                            env={**self.env, "T_PLAYS": json.dumps(plays), **env})
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def status(self, tid: str) -> str:
+        return yaml.safe_load((self.root / "tickets" / f"{tid}.yaml").read_text())["status"]
+
+    def run_models(self, tid: str) -> list[tuple[str, str]]:
+        """(role, model) of each run of ticket `tid`, in run order."""
+        runs = self.root / "runs"
+        metas = [yaml.safe_load((d / "meta.yaml").read_text()) for d in sorted(runs.iterdir())] if runs.exists() else []
+        return [(m["role"], m["model"]) for m in metas if m["ticket"] == tid]
+
+
+def sub_parks(res: dict) -> list[str]:
+    """The parks of T-0001.1. After it merges the build goes on to close T-0001 and parks it at
+    `archive`: this throwaway store has no spec store."""
+    return [p for p in res["parks"] if p.startswith("T-0001.1:")]
+
+
+def role_of(label: str) -> str:
+    return "clerk" if label.startswith("clerk:") else label.split()[0]
+
+
+def test_a_build_from_its_launch_copy_runs_every_role_and_the_clerk_on_the_instances_model(tmp_path):
+    s = Store(tmp_path)
+    s.planned()
+    models = s.ok("config")["models"]
+    swap = {role: "sonnet" for role in ("implementer", "reviewer", "verifier", "clerk")}
+    res = s.drive(s.launch_copy("build"), "T-0001", BUILD, T_SWAP=json.dumps(swap))
+    assert sub_parks(res) == []
+    assert {c["label"] for c in res["calls"] if not c["label"].startswith("clerk:") and c["label"].endswith(" T-0001.1")} == {
+        "implementer T-0001.1", "reviewer T-0001.1", "verifier T-0001.1"}
+    assert [c for c in res["calls"] if c["model"] != models[role_of(c["label"])]] == []
+    assert s.status("T-0001.1") == "merged"
+    assert s.run_models("T-0001.1") == [("implementer", "opus"), ("reviewer", "fable"), ("verifier", "opus")]
+
+
+def test_the_build_script_launched_as_it_is_still_parks_on_a_retyped_model(tmp_path):
+    s = Store(tmp_path)
+    s.at_checks()
+    res = s.drive(str(REPO / "factory" / "workflows" / "build.js"), "T-0001", CHECKS, T_SWAP='{"verifier": "fable"}')
+    assert [p.rstrip("\n") for p in res["parks"]] == ["T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus"]
+    assert s.status("T-0001.1") == "parked" and s.run_models("T-0001.1") == [("reviewer", "fable")]
+
+
+def test_an_intake_from_its_launch_copy_runs_triage_on_the_instances_model(tmp_path):
+    s = Store(tmp_path)
+    tid = s.new_ticket()
+    res = s.drive(s.launch_copy("intake"), tid, {"triage": "REJECT"}, T_SWAP='{"triage": "fable"}')
+    assert [c for c in res["calls"] if not c["label"].startswith("clerk:")] == [{"label": f"triage {tid}", "model": "opus"}]
+    assert s.status(tid) == "closed" and s.run_models(tid) == [("triage", "opus")]
+
+
+@pytest.mark.parametrize("name", ["intake", "build"])
+def test_a_launch_copy_launched_for_another_instance_runs_nothing(tmp_path, name):
+    s = Store(tmp_path)
+    s.at_checks()
+    instance = s.ok("paths")["instance"]
+    res = s.drive(s.launch_copy(name), "T-0001", CHECKS, T_INSTANCE=str(tmp_path / "other"))
+    assert res["result"]["error"] == f"launch copy written for instance {instance}, launched with {tmp_path / 'other'}"
+    assert res["calls"] == [] and s.status("T-0001.1") == "checks-in-flight" and s.run_models("T-0001.1") == []
+
+
+def test_a_build_whose_every_reply_is_pretty_printed_merges(tmp_path):
+    s = Store(tmp_path)
+    s.planned()
+    res = s.drive(str(REPO / "factory" / "workflows" / "build.js"), "T-0001", BUILD, T_PRETTY="1")
+    assert sub_parks(res) == [] and s.status("T-0001.1") == "merged"
+    assert s.run_models("T-0001.1") == [("implementer", "opus"), ("reviewer", "fable"), ("verifier", "opus")]
+
+
+def test_an_intake_whose_every_reply_is_pretty_printed_closes(tmp_path):
+    s = Store(tmp_path)
+    tid = s.new_ticket()
+    res = s.drive(str(REPO / "factory" / "workflows" / "intake.js"), tid, {"triage": "REJECT"}, T_PRETTY="1")
+    assert res["result"]["state"] == "closed" and s.status(tid) == "closed"
+    assert s.run_models(tid) == [("triage", "opus")]
+
+
+def test_a_sub_ticket_returned_to_its_checks_is_merged_without_another_implementer_run(tmp_path):
+    s = Store(tmp_path)
+    s.planned()
+    s.implement("READY-FOR-REVIEW")
+    s.ok("ticket", "park", "T-0001.1", "--reason", "harness-bug: run finish implementer: exit 0, no JSON on stdout")
+    s.ok("resolve", "T-0001.1", "--to", "checks")
+    res = s.drive(str(REPO / "factory" / "workflows" / "build.js"), "T-0001", CHECKS)
+    assert sub_parks(res) == [] and s.status("T-0001.1") == "merged"
+    assert s.run_models("T-0001.1") == [("implementer", "opus"), ("reviewer", "fable"), ("verifier", "opus")]
