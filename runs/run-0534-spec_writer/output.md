=== proposal.md
## Problem

The factory moves a ticket through its roles in one of two ways. The older way is a pair of workflow scripts, `factory/workflows/intake.js` and `build.js`: JavaScript programs that Claude Code's Workflow tool runs, and that start each role (triage, spec writer, implementer, reviewer, verifier and so on) as a separate agent. A workflow script cannot read a file or run a command. Each time it needs the factory's records (the store: tickets, runs and results), it asks the **clerk**, a small and cheap model agent, to run one harness command and copy that command's output back word for word. The script then parses the copied output as JSON and decides the next step.

The clerk does not always copy faithfully. Two of its slips stop a build and need the operator to restart it by hand:

- **It changes a value.** At the start of a run the script asks for the factory's configuration, which names the model each role runs on. The clerk has reported the wrong model for a role, for example the verifier as `fable` where the instance (a repository's `.factory/` directory, which names each role's model) says `opus`. The harness refuses to start a role on a model the instance does not name, which is the right call. The sub-ticket (one PR-sized piece of a ticket) still stops, or "parks", until a human resumes it. This store alone holds four such parks, three of them on one sub-ticket.
- **It reformats.** Once, on the other repository this factory runs on, the clerk returned a one-line JSON reply spread over many lines. The script reads JSON only one line at a time, found none, and parked a sub-ticket whose implementer had already finished its work. None of the operator's `factory resolve` commands, which answer a park, covers that case. The operator resumed it with raw state edits.

The operator, who launches workflows and answers parks, pays for each slip with a stopped build and a manual restart. This change makes three fixes. Each role's model reaches the script without any model relaying it. A reformatted reply still parses. The second kind of park gets its own resume command. The harness's refusal of a wrong model stays as a backstop. The clerk keeps relaying every other command. `factory drive`, the newer runner that needs no clerk, does not change.

## Evidence

- The request quotes #109 and #112. In 5 of 8 builds on 2026-10-12 and 2026-10-13 the clerk relayed `"verifier": "fable"` where the command printed `"opus"`. On 2026-10-14 it relayed `factory run finish`'s one-line JSON pretty-printed, and the build parked a sub-ticket whose implementer had finished `READY-FOR-REVIEW`. The operator resumed that park with `ticket head`, then `ticket transition --to checks-in-flight --round pr:init`, then a relaunch.
- This store's log, `grep '"ticket.parked"' .factory/store/log/*.jsonl | grep -c 'model fable refused'`, prints `4`. The parks are T-0048.1 at 2026-10-13T18:26 and T-0052.1 at 19:42, 19:46 and 19:49.
- The scripts take their models from the clerk's relay. `factory/workflows/build.js:225-226` runs `${BIN} config` through `clerk()` and sets `MODELS = cfg.models; MAX_PR = cfg.max_rounds.pr`, and `STATE = cfg.state_dir` when no `state` argument was given. `build.js:84` sends `--model ${MODELS[role]}` to `run start`, and `build.js:110` launches the agent on `MODELS[role]`. `intake.js:146-147` does the same with `max_rounds.spec`.
- `clerk()` parses one line at a time. `build.js:47-51` splits the trimmed stdout into lines and tries `JSON.parse` on each, from the last. `build.js:52` returns `no JSON on stdout` when none parses. `intake.js:56-61` is the same code.
- The harness prints one line. `factory/common.py:12-13` `out()` prints `json.dumps(obj, ensure_ascii=False)` with no indent, so a reply spread over lines is the clerk's doing.
- No resolve route covers #112's park. In `factory/human.py` `resolve`, `--to` accepts only `spec-gate` (`human.py:255-257`). `--redispatch` needs a park from `checks-in-flight` or `ready-for-merge` (`human.py:261-265`). `--ruling` takes a `ready-for-implementer` park only when its reason starts `harness-bug: run start implementer:` (`human.py:223-224`).
- Both runners read the branch tip again when they enter a sub-ticket at `checks-in-flight`: `build.js:178` and `factory/drive.py:469` run `ticket head` before any checker starts.
- Current truth this change touches: `openspec/specs/live-store-guard/spec.md` (its first requirement lists the commands the live-store fence leaves open) and `openspec/specs/harness-code/spec.md` (it pins each command-line module's definitions, `factory/cli.py` under 900 lines, 12 `gitops.repo_root()` call sites and one `"ticket.transition"` literal per place; this change keeps all of them).
- Prototype. I built parts A to D in a scratch clone and ran every scenario of this change on it and on `main` (308d038). Each NEW scenario except the documents and suite ones printed its THEN on the prototype, and each NEW scenario printed the failure listed in `verification.md` on `main`. The harness suite on the prototype printed `594 passed`, with no existing test file changed.
- One run of my scenario runner wrote its output file to the dev checkout's root for a few seconds. I moved it into my scratch directory, and `git -C ~/dev/spec-factory status --porcelain` printed nothing afterwards.
- Reference harness: triage found no as-built fix on the Nanobot fork's `feat/lionbot-v3.5`. I did not search it again.

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
- Cut as speculative: the copy defaulting `repo` to its harness; the copy checking its recorded harness revision at run time; a resume route for tripwire or conflict-limit parks.

## Open questions

none

## Decisions

1. The command is `factory launch-script intake|build`. Each call writes `<name>.js` into a new directory `factory-launch-<random>` under the temporary directory and prints `{"ok": true, "script": <path>, "source", "harness_revision", "instance"}`. Rejected: a fixed path under the instance's `.factory/`. A later launch would rewrite a script a running workflow came from, and a run against a throwaway store would write into the live instance's directory, a protected path here.
2. A launch copy differs from its script in one line. The scripts gain the line `const LAUNCH = null`. The copy holds `const LAUNCH = {...}` instead: one JSON object with `written_by: "factory launch-script"`, the source path, the harness revision, the instance, and `models`, `max_rounds` and `state_dir` as `factory config` prints them. The file is read-only. This answers the request's Risk. A launch copy is told apart from an edited script because the harness command alone writes it, into a directory the command creates, as a one-line change to the reviewed script that names the command, the source and the revision.
3. A launch copy asks no clerk for the configuration. It uses `LAUNCH` as the reply `factory config` would give, so the clerk's own model comes from the instance too.
4. `launch-script` joins the live-store fence's read-only list, so it refuses exactly where `config` refuses: no instance, uncommitted harness edits, or an unaccepted harness revision. It writes no store file. This modifies live-store-guard's first requirement. Rejected: fencing it as a write, which would refuse a launch while another ticket's run is in flight, where `config` stays open.
5. A launch copy sends every store command to the instance it records. Given an `instance` argument that names another instance, it returns an error naming its own before any store command runs. The copy's models and store path belong to its instance; mixed with another, agents would read one store's runs while the clerk writes another's.
6. The scripts launched as they are keep their clerk path, and README tells the operator to launch the copy. This keeps every scenario and suite test that runs the scripts directly, and T-0050's park as the backstop. Rejected: a script that refuses to run without a copy, which breaks those checks and would need a test-only switch.
7. `clerk()` in both scripts first parses the whole trimmed stdout, then falls back to the last-line scan. Every rule after the parse is unchanged.
8. The resume command is `factory resolve <id> --to checks`. It accepts a sub-ticket that meets four conditions: it is parked; it was parked from `ready-for-implementer`; its reason starts `harness-bug:`; and its newest implementer run started after it last entered `ready-for-implementer` and finished `READY-FOR-REVIEW`. The event log's order decides "after", because the store's timestamps are whole seconds.
9. The route reads the branch tip as `ticket head` does, through one shared definition. It applies the round step the build applies on this move (`pr:init`): a first round's 0 becomes 1, and a later round is unchanged. That is "round unchanged, as the script would have", and it is what the operator ran by hand for #112. It records a `resolve-<n>.yaml` and a `human.resolved` event of kind `to-checks`.
10. Only `harness-bug:` parks qualify, the class #112 belongs to: a store command failed after the implementer finished. A tripwire park and the conflict-limit park keep their documented routes.
11. A head from a conflict run that did not merge the integration branch still moves to checks. The join then sends it back to its implementer as a conflict (`factory/gates.py:203-206`), as it does after the script's own move.
12. The new tests run the scripts under node inside the suite, as `tests/factory/_fixtures.py`'s `BUILD_DRIVER` already does. T-0023's "the suite does not need node" no longer holds.
13. README keeps its 1,110-line budget.
14. The changelog entry takes the next free number and opens `<n>. After issue #109 `.

## Risk

- Blast radius: every Workflow-tool run (both scripts change), `factory resolve`, the CLI's parser and fence list, and the store helpers that `ticket head` and `ticket transition` use.
- I could not run Claude Code's Workflow tool here. It may not load a script from the temporary directory, or the auto-mode classifier may refuse to launch it. The scripts launched as they are still work, so a refusal costs only the fix (Operator step 1).
- The scripts launched as they are can still receive a wrong model. T-0050's run-start refusal then parks the ticket, as today.
- harness-code's current truth pins the definitions of `common.py`, `drift.py`, `gates.py`, `human.py` and `setup.py`, `factory/cli.py` under 900 lines, 12 `gitops.repo_root()` sites and one `"ticket.transition"` literal in the CLI modules and one in `store.py`. `design.md` places the new code so all of them hold.
- Protected paths: `factory/**`

## Operator steps

1. After the merge, the runtime upgrade and `--accept-harness`, launch the next build from a copy: `$RUNTIME/bin/factory launch-script build`, then the Workflow tool with `scriptPath` set to the printed `script`. Check that the Workflow tool loads it and that the auto-mode classifier lets it run. If either refuses, report it; launching `build.js` itself still works as before.
2. Tell the other target's runner session (instance A) to launch copies too: the same command, run from that target.

=== design.md
## Proposed change

Four parts in one PR. The prototype of A to D, with no tests or docs, changed 75 lines of `factory/` (67 added, 8 removed); with E and F the change should stay under 400 lines.

**A. `factory launch-script intake|build` writes a launch copy.**
- New module `factory/launch.py` holds the command, and the one definition of the values `factory config` prints (`models`, `max_rounds`, `state_dir`). `config` in `factory/cli.py` uses that definition too. A new module keeps harness-code's pinned definition lists of `setup.py` and `common.py` unchanged; it must not import `factory.cli`.
- `factory/cli.py`: a `launch-script` subparser with one positional argument, choices `intake` and `build`. Add `("launch-script", None)` to `READ_ONLY`, so the command takes `config`'s path through `main()`: the instance is required, and the harness lock is checked on the instance's own store.
- The command reads `factory/workflows/<name>.js` from the running harness checkout (`instance.HARNESS`). If the line `const LAUNCH = null` does not occur exactly once, it refuses with exit 2 and writes nothing. Otherwise it creates a directory with `tempfile.mkdtemp(prefix="factory-launch-")` and writes `<name>.js` there. The copy is the script with that one line replaced by `const LAUNCH = <json>`. The JSON object, written with `json.dumps(..., ensure_ascii=False)`, holds `written_by` (`"factory launch-script"`), `source` (the script's absolute path), `harness_revision`, `instance` (the instance's path as `factory paths` prints it), `models`, `max_rounds` and `state_dir`. The file is made read-only (0444). The command prints `{"ok": true, "script", "source", "harness_revision", "instance"}`.

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
- `build.js`, run from a launch copy under node with a stand-in clerk that retypes a model in the config reply, launches every role on the instance's model;
- both scripts proceed when every clerk reply is pretty-printed;
- `resolve --to checks` on #112's park returns the sub-ticket to its checks at the branch tip, and is refused, writing nothing, on each other park the scenarios list.

**F. Documents.**
- `README.md`:
  - "Starting a run": the session runs `$RUNTIME/bin/factory launch-script intake` (or `build`) and passes the printed `script` as `scriptPath`. Say in one sentence what a launch copy is and why: the script with the instance's models, round limits and store written in, so no model relays them. Say it has not yet run on a real ticket. The copy records its instance, so `instance` in args becomes optional.
  - "Where a human decides": add `launch-script` to the sentence "A write is any command except ...;", keeping that sentence's form; add `--to checks` to the **Unstick** row.
  - The run-start sentence at `README.md:252`, about a model the clerk misreported, says that a launch copy carries the models itself.
  - Bump the status date. Stay within 1,110 lines.
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
`factory launch-script intake|build` MUST write, in a new directory named `factory-launch-*` under the temporary directory, a read-only copy of that workflow script. The copy SHALL differ from the script in one line, which holds the instance's models, round limits and store as `factory config` reports them, the running harness revision and the instance. The command SHALL write nothing to the checkout or the store. Wherever `factory config` refuses, it MUST refuse with exit 2 and the same error, writing no copy.

#### Scenario: Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; mkdir $T/tmp; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; G0=$(git status --porcelain | cksum); S0=$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum); P=$(bin/factory paths); R=$(echo "$P" | sed -n 's/.*"harness_revision": "\([0-9a-f]*\)".*/\1/p'); I=$(echo "$P" | sed -n 's/.*"instance": "\([^"]*\)".*/\1/p'); for s in intake build; do C=$(TMPDIR=$T/tmp bin/factory launch-script $s 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'); L=$(diff factory/workflows/$s.js "${C:-/dev/null}" | grep '^>'); echo "$s: where=$(case "$C" in $T/tmp/factory-launch-*/$s.js) echo own-dir;; *) echo none;; esac) changed=$(diff factory/workflows/$s.js "${C:-/dev/null}" | grep -c '^[<>]') revision=$(echo "$L" | grep -cF "\"harness_revision\": \"$R\"") instance=$(echo "$L" | grep -cF "\"instance\": \"$I\"") writable=$([ -n "$C" ] && [ -w "$C" ] && echo yes || echo no)"; done; echo "checkout=$([ "$(git status --porcelain | cksum)" = "$G0" ] && echo unchanged || echo changed) store=$([ "$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed) dirs=$(ls $T/tmp | grep -c '^factory-launch-')")`
- THEN it prints exactly `intake: where=own-dir changed=2 revision=1 instance=1 writable=no`, `build: where=own-dir changed=2 revision=1 instance=1 writable=no`, `checkout=unchanged store=unchanged dirs=2`, one per line

#### Scenario: launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
The target's own store is used, so the harness lock applies. Its lock names a revision that is not running.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && mkdir $T/tmp && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && echo 0000000000000000000000000000000000000000 > .factory/harness.lock; $B config >/dev/null 2>$T/c; c=$?; TMPDIR=$T/tmp $B launch-script build >/dev/null 2>$T/l; l=$?; echo "config=$c launch=$l same=$(cmp -s $T/c $T/l && echo yes || echo no) lock=$(grep -c 'is not the revision this instance accepted' $T/l) copies=$(ls $T/tmp | grep -c .)")`
- THEN it prints exactly `config=2 launch=2 same=yes lock=1 copies=0`

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
`README.md`'s "Starting a run" SHALL tell the operator to launch the copy `factory launch-script` writes. Its "Where a human decides" SHALL list `launch-script` among the commands that are not writes, and its **Unstick** row SHALL name `resolve --to checks`. `docs/design.md` SHALL list `launch-script` in the live-store fence's read-only list and describe the `--to checks` route. `docs/changelog.md` SHALL hold one entry opening `After issue #109`, naming #112, `launch-script` and `--to checks`, numbered without a gap. README SHALL stay within 1,110 lines, and the maintained documents SHALL carry no whitespace error.

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

STATUS: READY-FOR-CRITIC
CONFIDENCE: medium. Every scenario was run on a prototype and on `main` with the outputs given. Two things are unverified: whether Claude Code's Workflow tool and its auto-mode classifier accept a script from the temporary directory (Operator step 1), and the docs and suite items, which the prototype did not implement.
ESCALATIONS: none
