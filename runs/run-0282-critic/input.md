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
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0282-critic/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0282-critic/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Spec under review (v1)

=== proposal.md
## Problem
The factory does each step of a ticket with an AI agent playing one role: triage, spec writer, critic, planner, implementer, reviewer or verifier. The operator pays for every model call these agents make. Today much of that cost is fixed overhead, not work. The reviewer and verifier, the two roles that check an implementer's code, can also edit the code they are checking.

Three gaps cause this:

1. **Most roles run without their own agent definition.** Claude Code can start an agent from a registered agent definition: a file in the repository's `.claude/agents/` that gives the agent a short system prompt and a fixed list of tools. Without one, the factory starts the role as Claude Code's general-purpose agent. The workflow script (the code that moves a ticket through its roles) calls this "inline" mode and switches it on with the argument `inlineRoles: true`. A general-purpose agent re-sends about 44k tokens of fixed context on every call. A registered agent re-sends about 30k. The harness, the factory's own code, ships definitions for only four of the seven roles. The build half (implementer, reviewer, verifier) therefore cannot run any other way, and both repositories run every role inline. Inline agents have every tool, including the file-editing ones, so nothing enforces the rule that a reviewer or verifier must not change what it checks.
2. **Roles receive spec text they never use.** Each role reads one input file that the harness composes for it. For the planner, implementer, reviewer and verifier, that file holds the whole approved spec. This includes its Evidence section (captured command output, often the largest section) and the writer's Responses to the critic. None of these four roles' instructions use either section. A critic's second round receives the previous spec version in full, even when only a few lines changed.
3. **There is no per-role effort setting.** Effort is how much reasoning the model does before it answers. Each role has a configured model but no configured effort, so the operator cannot tune it per role.

This change adds the missing agent definitions and limits the checkers' file-editing tools to their own run's output and scratch files. It cuts each role's input down to the spec sections that role uses, and it adds an optional effort setting per role. Inline mode stays available as a fallback. It is still needed by any Claude Code session that started before the new definitions were installed: such a session does not know them.

## Evidence
**Token overhead (the request's measurement, 2026-10-03).** The store is the set of files where the factory records tickets and runs. Each workflow reads and writes it through a small agent that runs one store command per call. The request measured 149 role runs and 741 such store-command calls from both repositories' workflow transcripts. Fixed start-up context is 47% of the role agents' 247M context tokens. It is 44.4k tokens per call for an inline role and 30.2k for a registered one. 21 of 118 role runs ran with a registered definition. The composed input is 11.5% of role tokens: 4% of a triage run and 23% of a reviewer run.

**Missing definitions, checked on `main` at `c2750bf`.** `ls agents/` lists `factory-clerk.md factory-planner.md factory-spec-critic.md factory-spec-writer.md factory-stub.md factory-triage.md`, so there are no implementer, reviewer or verifier definitions. The Nanobot runner reported that `build.js` without `inlineRoles` failed at the first implementer call with "agent type 'factory-implementer' not found" (workflow wf_345169c6-fca). The first acceptance scenario below runs both workflow scripts with a recording stub and checks each agent type they ask for against `agents/`. Today it prints `factory-implementer=missing`, `factory-reviewer=missing` and `factory-verifier=missing`.

**What happens today when a definition is missing.** These runs use a stub agent that throws Claude Code's "not found" error:
- **A build role is missing.** The build script records that run as killed and parks the sub-ticket. It prints `run finish run-0009-x --status-override KILLED`, then `ticket park T-0001.1 --reason "agent call failed: implementer: agent type 'factory-implementer' not found" --outputs run-0009-x`. No run is left in flight, and the ticket waits for a human.
- **No factory agent is registered at all.** This is this repository's situation: it has no `.claude/agents/`. Both scripts stop at their first store command, which is itself an agent call: `stopped: agent type 'factory-clerk' not found after 1 agent call(s)`. Nothing has been written to the store.

**The four existing role definitions carry stale copies of their prompts.** Each existing role definition's body repeats its role prompt after a line telling the agent to read the run's `system-prompt.txt`. That file holds the current prompt, `factory/prompts/<role>.md`. `diff <(sed -n '/^ROLE:/,$p' agents/factory-planner.md) factory/prompts/planner.md` shows the copy's OUTPUT section is an older format. For example, the copy says `Coverage map: parent criterion → sub-ticket ID` where the current prompt says `parent scenario`. The triage, spec writer and critic copies also differ from their prompts (`diff -q` reports each). The spec writer copy still gives the old one-document FORMAT. Inline runs never see these copies. Registered runs would get the copy as their system prompt, then read the current prompt beside it.

**Input sizes per role, this repository's store, 2026-10-04 (all 278 runs with an `input.md`).** The column "Evidence + Responses" counts the bytes of the spec's `## Evidence` and `## Responses` sections inside each input.

| Role | Runs | Mean input | Mean Evidence + Responses | Share of input |
|---|--:|--:|--:|--:|
| triage | 40 | 8.6 KB | 0.0 KB | 0% |
| spec_writer | 51 | 41.2 KB | 1.3 KB | 3% |
| critic | 46 | 64.2 KB | 7.2 KB | 11% |
| planner | 17 | 44.7 KB | 6.4 KB | 14% |
| implementer | 36 | 75.0 KB | 8.9 KB | 12% |
| reviewer | 39 | 127.0 KB | 8.9 KB | 7% |
| verifier | 49 | 111.8 KB | 8.7 KB | 8% |

The planner, implementer, reviewer and verifier would lose those shares. The critic and spec writer keep them: the critic's rubric checks that Evidence is real output.

**Round-2 critic: the previous version against a diff.** The store has 14 round-2 critic runs. Their previous spec versions total 497.7 KB. Unified diffs (`diff -u`) from each previous version to the next total 382.5 KB. In 4 of the 14, the diff was larger than the previous version, because the writer had rewritten most of the spec: T-0008 (68.6 KB diff against a 40.4 KB version), T-0010, T-0019 and T-0021. If each run gets whichever is smaller, those inputs carry 340.9 KB in place of 497.7 KB. That is about 11 KB less per run, on inputs averaging 101.7 KB.

**Claude Code's documented behaviour, read on 2026-10-04 (code.claude.com/docs/en/sub-agents.md and /hooks.md):**
- `tools` lists tool names. A `disallowedTools` entry with a path or command pattern "still removes the whole tool". A tool list alone therefore cannot let a role write one file and not another.
- An agent definition may declare `hooks`. A `PreToolUse` hook runs only while that agent is active. It receives the tool call as JSON on stdin, with the Write tool's absolute path in `tool_input.file_path`. Exit code 2 blocks the call. Any other non-zero exit is reported as a non-blocking error, and the call proceeds.
- Hooks in a project's `.claude/agents/` run only after the workspace trust dialog for that folder has been accepted.
- "The watcher covers only directories that existed when the session started." A session that already had `.claude/agents/` picks up new files in it within seconds. A session that started before the directory existed must restart.

**Documents that describe inline running today.** `README.md` "Starting a run" says "Add `inlineRoles: true` on every target for now". `.factory/README.md` "Running" says "this repo adds no `.claude/agents/`, so roles run inline". Both stop being true with this change.

## Root cause
- `agents/` has no `factory-implementer.md`, `factory-reviewer.md` or `factory-verifier.md`. `factory/workflows/build.js` already asks for those agent types (`AGENT_NAME`, line 88).
- `init_cmd` in `factory/cli.py` copies each `agents/factory-*.md` that the target's `.claude/agents/` lacks (lines 983–990). It never overwrites an existing file, so a stale copy stays.
- `compose` in `factory/compose.py` adds the whole pinned spec file through `add()` for the planner (line 160), the implementer (line 188) and the checkers (lines 203, 206). A round-2 critic gets the whole previous version (line 153).
- `runRole` in both workflow scripts (`intake.js:97`, `build.js:88`) passes `agentType` and `model` to a role's agent call but no `effort`. Only the store-command agent and the test stub pass `effort: 'low'`. `run_start` in `factory/cli.py` records `model` in the run's `meta.yaml` but has no effort. `factory/instance.template.yaml` has a `models:` map and no effort map.

## Out of scope
- Removing or batching the store-command agent: the low-cost agent each workflow starts only to run one `bin/factory` command and relay its output. This is part B of the request, deferred by the operator. That agent's definition, model and fixed `'low'` effort do not change.
- The test-stub definition `agents/factory-stub.md`.
- Which model each role uses. Claude Code's own system prompt. `omitClaudeMd` on the role definitions.
- A recovery command for an `agent call failed` park. README documents the existing route.
- Stopping a checker from writing through its shell. That needs operating-system isolation (issue #37).
- `factory/cost.py --breakdown`, and any change to how `factory/cost.py` counts.
- What spec writers put in Evidence (issue #23). Reusing a sub-ticket's verifier run for its parent's close.
- The role prompts: no file under `docs/prompts/` or `factory/prompts/` changes.

## Open questions
none

## Decisions
- Every role definition's body is one paragraph telling the agent to read its run's `system-prompt.txt`, as inline runs already do. The four existing role definitions lose their copied prompts. Rejected: copying the prompt into the body, as the four existing definitions do. A copy goes stale (Evidence) and is re-sent on every call. Once roles run registered, every stale copy becomes live.
- The reviewer and verifier fence covers the file-editing tools only:
  - their tool list is `Read, Grep, Glob, Bash, Write`, with no Edit, MultiEdit or NotebookEdit;
  - a `PreToolUse` hook lets a file-editing call through only for the agent's own role's run `output.md` or a file under that run's `scratch/`, and blocks everything else with exit 2.

  The fence does not cover the shell. A checker can still write anywhere through Bash, and its gate commands legitimately write build files into the checkout. Rejected: dropping Write, which the role needs for its output file. Rejected: a Bash pattern in the tool list, which Claude Code does not support. A stronger fence is issue #37's question.
- The hook matches any run directory of the agent's own role, not only the current run. A hook receives no run id.
- The hook fails closed: any failure to decide, including a missing `python3`, blocks the call. Rejected: an exit code other than 2 on failure, which Claude Code treats as non-blocking.
- A role call to an agent type the session has not registered keeps today's handling: the run is recorded killed, the ticket parks with `agent call failed: <role>: <error>`, and no run stays in flight. With no factory agent registered at all, the workflow stops at its first store command and writes nothing. Rejected: retrying the call as a general-purpose agent. That would silently run a checker with no fence.
- To recover from such a park, the operator restarts the runner session, or dispatches with `inlineRoles: true`, then sends the ticket back with the existing commands: `ticket transition <id> --to <the state it parked from> --by <name>`, or `resolve --redispatch` for a checker. No new command is added.
- Each run's `meta.yaml` records `inline: true|false` and `effort`. `run start` gains `--inline`, which the workflows pass in inline mode.
- `instance.yaml` may hold an optional `effort:` map, from role to level. Keys are the seven roles. Values are `low`, `medium`, `high`, `xhigh` or `max`. `run start` checks the whole map and refuses an unknown role or level with exit 2, writing nothing. It returns the role's effort in its JSON, and the workflow passes that value to the role's agent call. A role with no entry gets no effort argument. Rejected: an entry for the store-command agent, which the operator keeps unchanged. Rejected: `effort` in the agent definitions, because one set of definitions serves every instance.
- The planner, implementer, reviewer and verifier (including the parent-close verifier) receive the pinned spec without its `## Evidence` and `## Responses` sections. Each input names the full spec's absolute path. Rejected: the requester's keep-list (Problem, Proposed change, Acceptance, Risk, Tests to change, Out of scope). It would also drop Root cause, Decisions, Operator steps and the requirement scenarios, and the implementer and verifier run those scenarios.
- A round-2 critic receives the unified diff from the previous spec version when the diff is smaller than that version, and the version whole otherwise. Rejected: always the diff, which was larger in 4 of 14 real cases.
- No `--breakdown` option is added to `factory/cost.py`. The per-role input size is measured from the store with a one-line command (Operator steps). The start-up context per call is already available as context tokens divided by calls in `factory/cost.py`'s table.
- The work is split into four parts: A agents, B effort, C inputs, D documents. They share one changelog entry. Rejected: one PR. Together the parts exceed the size limit.

## Risk
- Blast radius: every role run. Each one composes its input through the changed composer, and from now on starts as a registered agent. A defect in the section cut would hide spec text from the implementer and checkers. A defect in the hook would stop a checker writing its output, and that run would end killed.
- Unverified: whether a Workflow-tool `agent()` call applies an agent definition's frontmatter hooks. The docs describe hooks for subagents and say nothing either way for workflow agents. The hook logic itself is tested here. The operator probe under Operator steps checks it live. If the probe shows the write going through, the checkers have no file-tool fence in workflow runs, only the narrowed tool list.
- The hook needs `python3` on the runner's `PATH`, and the runner folder's workspace trust accepted. Without `python3`, a checker's writes are all blocked and its run ends killed. Without trust, the hook does not run.
- Protected paths this change touches:
  - **harness**: `agents/factory-implementer.md`, `agents/factory-reviewer.md` and `agents/factory-verifier.md` (new); `agents/factory-triage.md`, `agents/factory-spec-writer.md`, `agents/factory-spec-critic.md` and `agents/factory-planner.md` (bodies replaced; these are agent prompts, a guardrail path, changed under this approval); `factory/cli.py`; `factory/compose.py`; `factory/instance.template.yaml`; `factory/workflows/intake.js`; `factory/workflows/build.js`.
  - **infra**: `.factory/README.md`.
  - Existing test `tests/factory/test_instance.py` (see Tests to change). New tests go in new files.
- Not touched: `docs/prompts/**`, `factory/prompts/**`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

## Operator steps
1. **Install the definitions in this repository.** After merge, upgrade the runtime (the pinned harness checkout that runs tickets) and accept its revision. Then, with no run in flight, run `~/dev/spec-factory-harness/bin/factory init` from `~/dev/spec-factory`. It writes the nine files to `.claude/agents/`. Commit them on `main`, as the Nanobot fork tracks its own. Then restart this repository's runner session, the Claude Code session that starts workflows. This directory did not exist when that session started, so it will not see the files otherwise.
2. **Refresh the Nanobot fork's definitions.** In the Nanobot Driver session, delete `.claude/agents/factory-triage.md`, `factory-spec-writer.md`, `factory-spec-critic.md` and `factory-planner.md`; `init` never overwrites a file, so this is how the stale copies go. Then run the runtime's `bin/factory init` there. It installs those four and the three new ones. Commit under that repository's own rules, then restart its runner session.
3. **Probe the fence in each runner session.** Ask Claude to run a one-call Workflow script whose only call is `agent('Use the Write tool to write the word probe to <repo>/fence-probe.txt, then say what happened.', {agentType: 'factory-reviewer'})`. Expected: the agent reports the write was blocked, and `<repo>/fence-probe.txt` does not exist. If the file exists, the hook did not run: say so in an issue before relying on the fence.
4. **Stop passing inline mode.** Drop `inlineRoles: true` from both repositories' dispatch arguments. Keep it only in a session that started before its `.claude/agents/` existed.
5. **Optionally set effort.** Add `effort:` entries to an instance's `instance.yaml`, for example `effort: {verifier: high}`.
6. **Measure the first ticket that runs entirely on the new harness.** Let `N` be its first run number:
   - Input size per role, from the store directory that `factory paths` reports: `for r in triage spec_writer critic planner implementer reviewer verifier; do ls runs | awk -F- -v r=$r -v n=N '$3 == r && $2 + 0 >= n {print "runs/" $0 "/input.md"}' | xargs wc -c 2>/dev/null | awk -v r=$r '$2 != "total" {k++; s += $1} END {if (k) printf "%s runs=%d mean_kb=%.1f\n", r, k, s / k / 1024}'; done`. Compare it with the table under Evidence.
   - Start-up context per call: `uv run --frozen python -m factory.cost <the run's transcript dir>`, context tokens divided by calls for each role. Compare with 44.4k inline and 30.2k registered.
   - Record `/usage` (the session and weekly bars, with the subagent breakdown) before and after that run.

=== design.md
## Proposed change
NEEDS-SPLIT. The four parts below are the seams. A, B and C are independent of each other. D depends on all three and lands last. One changelog entry covers all four.

**A. A registered definition for every role, and a fence on the checkers** (`agents/`, `factory/workflows/*.js`, `factory/cli.py`).
1. Add `agents/factory-implementer.md`, `agents/factory-reviewer.md` and `agents/factory-verifier.md`. Their frontmatter follows the existing files: `name` equal to the file name without `.md`, a one-line `description`, and `model` taken from the template's `models:` (implementer `opus`, reviewer `fable`, verifier `opus`). The implementer's `tools` is `Read, Grep, Glob, Bash, Write, Edit`. The reviewer's and verifier's `tools` is `Read, Grep, Glob, Bash, Write`.
2. The reviewer and verifier frontmatter also declares `hooks.PreToolUse`, with one entry whose `matcher` is `Write|Edit|MultiEdit|NotebookEdit` and one `type: command` hook. The command:
   - runs under `sh`, using `python3` from `PATH`;
   - reads the hook JSON from stdin and takes `tool_input.file_path`, or `tool_input.notebook_path`;
   - resolves the path with `os.path.realpath`;
   - exits 0 only when the resolved path matches `/runs/run-<digits>-<role>/output.md` or `/runs/run-<digits>-<role>/scratch/<one or more characters>`, where `<role>` is that file's own role;
   - otherwise exits 2, with a one-line stderr message naming the two allowed places.

   Any failure to decide must also exit 2, for example a shell form like `python3 -c '…' || exit 2`.
3. Replace the body of `agents/factory-triage.md`, `factory-spec-writer.md`, `factory-spec-critic.md` and `factory-planner.md` with the same single paragraph the three new files use. It says to read `system-prompt.txt` in the run directory that holds the input file before anything else, because it holds the role and rules for the run, preamble first. No body may contain a `ROLE:` line. Their frontmatter is unchanged.
4. `run start` gains `--inline` (a flag). It records `inline: true` with the flag and `inline: false` without it in `meta.yaml`. Both workflow scripts add `--inline` to their `run start` command when `INLINE` is set. Update the scripts' `inlineRoles` comments: inline mode is the fallback for a session that has not registered the definitions, and it runs with no tool fence.
5. `init` keeps its rule of copying only missing files. Its log line and its "restart the session so the agents register" message do not change.

**B. Effort per role** (`factory/cli.py`, `factory/instance.template.yaml`, `factory/workflows/*.js`).
1. `run_start` reads `cfg.get("effort")`. Absent or null means an empty map. It refuses with exit 2 before reserving a run id, so nothing is written, when the value is not a mapping, when a key is not one of `ROLES`, or when a value is not one of `low`, `medium`, `high`, `xhigh`, `max`. The refusal names the bad key or value.
2. `run_start` records `effort: <the role's level or null>` in `meta.yaml` and adds `"effort"` (the same value) to its JSON output.
3. In `runRole` in both workflow scripts, the real role call (not the stub call) passes `effort: start.effort` when that is set, and passes no `effort` key otherwise. The store-command agent and stub calls keep `effort: 'low'`.
4. `factory/instance.template.yaml`: add a commented example `# effort: {verifier: high}` after `models:`. Explain in a comment that an absent role gets the session default, and list the allowed levels. Add no live key, so a new instance's keys are unchanged.

**C. Each role's input cut to the sections it uses** (`factory/compose.py`).
1. Add a helper that returns a spec text without its `## Evidence` and `## Responses` sections. A section starts at a line `## Evidence` or `## Responses`, ignoring trailing spaces. It runs up to, but not including, the next line that starts with `## ` or `=== `. Lines inside a fenced code block do not count as that next line.
2. Use the cut text for the planner's "Approved spec", for the implementer's, reviewer's and verifier's "Parent spec", and for the parent-close verifier's spec. Each heading keeps its current words, so the parent-close heading still contains "verify every scenario on main". Each heading adds that the Evidence and Responses sections are left out, and gives the absolute path of the full spec file. `input_sources` keeps listing the same `specs/<id>/v<n>.md` paths. The sub-ticket text, `specs/<id>/subticket.md`, is not cut.
3. Round-2 critic: in place of the whole previous version, build `difflib.unified_diff` from `v<n-1>` to `v<n>` with 3 lines of context, labelled with the two store paths. Use it when its byte length is less than `v<n-1>`'s. Otherwise add the previous version whole, as today. Name in the heading which one the input holds. `input_sources` is unchanged.
4. The triage and spec writer inputs, the critic's current spec, and every other input are unchanged.

**D. Documents** (`docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md`, `README.md`, `.factory/README.md`).
1. `docs/design.md` routing table, "Receives" column:
   - The Spec writer → Critic row's round 2+ input says the previous spec version arrives as a diff when that is smaller, and whole otherwise.
   - The "Human spec gate | Approved", "Planner | PLANNED", "Implementer | READY-FOR-REVIEW" and "Merge gate | CI green" rows each say the spec arrives without its Evidence and Responses sections.
2. `dev/build-harness.spec.md`: make the critic's round-2 input in H's intake step (the sentence with "round ≥ 2: prior findings") match the design doc, naming the diff.
3. `docs/changelog.md`: one entry, the next number with no gap, after any entry already on `main`. It names the seven definitions (`factory-implementer` among them), the reviewer and verifier fence and its limit, the `agent call failed` park, `inlineRoles` as the fallback, the `effort` map, and the inputs without Evidence and with a diff for a round-2 critic.
4. `README.md`, following "Maintaining this page":
   - "Starting a run": replace the "Add `inlineRoles: true` on every target for now" passage. Say that roles run as their registered agents, and when inline mode is still needed. Say what happens without the definitions: the `agent call failed` park, or a stop at the first store command. Give how to recover (Decisions).
   - Describe the checker fence and its limit, with the `python3` and workspace-trust requirement.
   - Describe the `effort:` map (with that literal key in backticks) and remove the "Per-role effort settings" bullet from the list of what is not built.
   - Re-derive figures; add this ticket and issues #24 and #22 under "Related work and history"; bump the status date.
5. `.factory/README.md` "Running": dispatch without `inlineRoles`, and drop "this repo adds no `.claude/agents/`". Keep `inlineRoles: true` only for a session started before `.claude/agents/` was installed.

## Tests to change
- `tests/factory/test_instance.py::test_init_creates_the_instance_at_the_git_top_level` asserts `len(agents) == 6` for `agents/factory-*.md`. Part A makes it nine, so the assertion becomes `== 9`. The rest of that test, that every template is copied byte for byte and the restart message is printed once, is unchanged.

=== specs/role-agents/spec.md
## ADDED Requirements
### Requirement: Every role has a registered agent definition that reads the run's prompt
`agents/` SHALL hold a definition for every agent type either workflow script asks for, each named as its file, and every role definition's body MUST point the agent at its run's `system-prompt.txt` and carry no copy of a role prompt.

#### Scenario: Every agent type the workflows ask for has a definition
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the eight fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0030-wf.mjs <<'EOF'
// node t0030-wf.mjs <workflow.js> '<replies JSON>' [inline]: runs one workflow script with a stub clerk, as
// t0023-wf.mjs does (same reply rules), with inlineRoles set when a third argument is given. Prints one
// line per role agent call, `<agentType> effort=<effort or none>`, in call order, then
// `clerk effort=<the distinct efforts of the clerk calls>`.
import { readFileSync } from 'node:fs'
const [file, replies, inline] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = [], clerkEffort = new Set()
const agent = async (prompt, opts = {}) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) { lines.push(`${opts.agentType} effort=${opts.effort ?? 'none'}`); return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n' }
  clerkEffort.add(opts.effort ?? 'none')
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s', inlineRoles: !!inline }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
console.log(`clerk effort=${[...clerkEffort].sort().join(',')}`)
EOF
cat > ${TMPDIR:-/tmp}/t0030-intake.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": [{"out": {"ok": true, "status": "ACCEPT"}}, {"out": {"ok": true, "status": "READY-FOR-CRITIC"}}, {"out": {"ok": true, "status": "APPROVE"}}], "ticket transition": {"out": {"ok": true, "round": {"spec": 1}}}}
EOF
cat > ${TMPDIR:-/tmp}/t0030-build.json <<'EOF'
{"ticket show T-0001 ": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": [{"out": {"ok": true, "status": "PLANNED"}}, {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, {"out": {"ok": true, "status": "APPROVE"}}], "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": [], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}, "ticket parent-check": {"out": {"ok": true, "state": "planned"}}}
EOF
cat > ${TMPDIR:-/tmp}/t0030-throw.mjs <<'EOF'
// node t0030-throw.mjs <workflow.js> '<replies JSON>' [all]: as t0030-wf.mjs, but every role agent call throws
// the error Claude Code gives for an agent type this session has not registered; with `all`, clerk calls
// throw it too. Prints each `run finish` and `ticket park` command the workflow sends, in order, or, if
// the workflow itself stops, `stopped: <error> after <n> agent call(s)`.
import { readFileSync } from 'node:fs'
const [file, replies, all] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
let calls = 0
const agent = async (prompt, opts = {}) => {
  calls++
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m || all) throw new Error(`agent type '${opts.agentType}' not found`)
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  if (/^(run finish|ticket park)/.test(cmd)) lines.push(cmd)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
try {
  await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
  console.log(lines.join('\n'))
} catch (e) { console.log(`stopped: ${e.message} after ${calls} agent call(s)`) }
EOF
cat > ${TMPDIR:-/tmp}/t0030-e2e.mjs <<'EOF'
// node t0030-e2e.mjs <instance dir> [inline], from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store, as t0024-e2e.mjs does: every clerk command runs for
// real, and the triage role writes the stub output "STATUS: REJECT". Prints `role effort=<the effort
// the role's agent call received, or none>` and `clerk effort=<the clerk calls' efforts>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [inst, inline] = process.argv.slice(2)
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const seen = [], clerk = new Set()
const agent = async (prompt, opts = {}) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    clerk.add(opts.effort ?? 'none')
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  seen.push(`role effort=${opts.effort ?? 'none'}`)
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), instance: inst, inlineRoles: !!inline }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${seen.join(' ')} clerk effort=${[...clerk].sort().join(',')}`)
EOF
cat > ${TMPDIR:-/tmp}/t0030-spec.sh <<'EOF'
# Sourced from the repo root: a scratch store (FACTORY_STATE) whose T-0001 has an approved spec v1 with every
# section, one of them a Responses section, and one sub-ticket T-0001.1; a scratch target repo with a
# commit H30 on its branch side. Defines comp ROLE TICKET: starts a run, composes it, finishes it as KILLED
# and prints the path of its input.md; and marks ROLE FILE: prints which marked spec sections FILE holds.
T30=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T30/store
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
printf '# Fixture\n\nThe bot should do the thing.\n' > $T30/req.md
cat > $T30/spec.md <<'SPEC'
=== proposal.md
## Problem
PROBLEM-MARK the thing is missing.
## Evidence
EVIDENCE-MARK long captured output.
## Root cause
ROOTCAUSE-MARK in one function.
## Out of scope
OUTOFSCOPE-MARK nothing else.
## Decisions
DECISIONS-MARK one call.
## Risk
RISK-MARK small.
=== design.md
## Proposed change
CHANGE-MARK do the thing.
## Tests to change
TESTS-MARK none
=== specs/demo/spec.md
## ADDED Requirements
### Requirement: The thing
SCENARIO-MARK the thing SHALL happen.
=== verification.md
## Acceptance
ACCEPTANCE-MARK the thing → NEW
## Responses
RESPONSES-MARK FIXED earlier finding.
STATUS: READY-FOR-CRITIC
SPEC
bin/factory ticket new --file $T30/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T30/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T30/plan.md
bin/factory subticket add T-0001 --file $T30/plan.md >/dev/null
git init -q -b main $T30/t && git -C $T30/t commit -q --allow-empty -m init
git -C $T30/t checkout -q -b side && echo x > $T30/t/x.txt && git -C $T30/t add x.txt && git -C $T30/t commit -q -m work
H30=$(git -C $T30/t rev-parse HEAD) && git -C $T30/t checkout -q main
export FACTORY_REPO=$T30/t FACTORY_INTEGRATION_BRANCH=main
comp() { R=$(bin/factory run start --role $1 --ticket $2 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null 2>&1 && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; echo $FACTORY_STATE/runs/${R:-none}/input.md; }
marks() { echo "$1: evidence=$(grep -c EVIDENCE-MARK $2) responses=$(grep -c RESPONSES-MARK $2) kept=$(grep -o -e PROBLEM-MARK -e ROOTCAUSE-MARK -e OUTOFSCOPE-MARK -e DECISIONS-MARK -e RISK-MARK -e CHANGE-MARK -e TESTS-MARK -e SCENARIO-MARK -e ACCEPTANCE-MARK $2 | sort -u | grep -c .) full=$(grep -cF "$FACTORY_STATE/specs/T-0001/v1.md" $2)"; }
EOF
cat > ${TMPDIR:-/tmp}/t0030-critic.sh <<'EOF'
# Sourced from the repo root, with $1 = small or rewrite: a scratch store whose T-0001 is at round 2
# with the critic next, holding spec v1 and v2 and one finished round-1 critic run. v1 is 200 lines
# "keep line N" and the line OLD-ONLY. For small, v2 is v1 with OLD-ONLY replaced by NEW-ONLY; for
# rewrite, every line of v2 differs from v1 ("other line N"). Prints the path of the composed
# input.md of a round-2 critic run.
T31=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T31/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T31/req.md
{ echo '## Problem'; seq 1 200 | sed 's/^/keep line /'; echo OLD-ONLY; echo 'STATUS: READY-FOR-CRITIC'; } > $T31/v1.md
if [ "$1" = small ]; then sed 's/^OLD-ONLY$/NEW-ONLY/' $T31/v1.md > $T31/v2.md; else sed 's/^keep line /other line /; s/^OLD-ONLY$/NEW-ONLY/; s/^## Problem$/## Problem (rewritten)/; s/^STATUS: READY-FOR-CRITIC$/STATUS:  READY-FOR-CRITIC/' $T31/v1.md > $T31/v2.md; fi
printf 'Findings: one.\nSTATUS: REVISE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' > $T31/c1.md
bin/factory ticket new --file $T31/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T31/v1.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
R1=$(bin/factory run start --role critic --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
bin/factory run finish $R1 --output-file $T31/c1.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t --round spec:+1 >/dev/null
bin/factory spec add T-0001 --file $T31/v2.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
R2=$(bin/factory run start --role critic --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
bin/factory run compose $R2 >/dev/null && echo $FACTORY_STATE/runs/$R2/input.md
EOF
cat > ${TMPDIR:-/tmp}/t0030-fence.py <<'EOF'
# .venv/bin/python t0030-fence.py, from the repo root: for the reviewer, verifier and implementer agent
# definitions under agents/, reads the frontmatter's tool list and runs every PreToolUse hook whose
# matcher covers the Write tool against a Write of each test path, the way Claude Code would (JSON on
# stdin; exit 2 blocks). A run directory of each role is made under a scratch store. Prints one line per
# role: the file-editing tools it has, then for each path `allowed` or `blocked`.
import json, os, re, subprocess, tempfile, yaml
base = os.path.realpath(tempfile.mkdtemp())
for role, n, other in (("reviewer", "0042", "verifier"), ("verifier", "0043", "reviewer"), ("implementer", "0045", "reviewer")):
    f = f"agents/factory-{role}.md"
    if not os.path.exists(f):
        print(f"{role}: missing"); continue
    fm = yaml.safe_load(open(f, encoding="utf-8").read().split("---")[1]) or {}
    tools = fm.get("tools") or []
    tools = [t.strip() for t in tools.split(",")] if isinstance(tools, str) else tools
    hooks = [h["command"] for m in (fm.get("hooks") or {}).get("PreToolUse", [])
             if re.fullmatch(m.get("matcher") or ".*", "Write") for h in m.get("hooks", []) if h.get("type") == "command"]
    run = os.path.join(base, "store", "runs", f"run-{n}-{role}")
    os.makedirs(os.path.join(run, "scratch"), exist_ok=True); os.makedirs(os.path.join(run, "wt", "pkg"), exist_ok=True)
    paths = {"output": f"{run}/output.md", "scratch": f"{run}/scratch/notes.txt", "worktree": f"{run}/wt/pkg/code.py",
             "escape": f"{run}/scratch/../wt/pkg/code.py", "other_run": f"{base}/store/runs/run-0044-{other}/output.md",
             "repo": f"{base}/repo/pkg/code.py"}
    res = []
    for name, p in paths.items():
        inp = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Write", "cwd": run,
                          "tool_input": {"file_path": p, "content": "x"}})
        blocked = any(subprocess.run(["sh", "-c", c], input=inp, text=True, capture_output=True).returncode == 2 for c in hooks)
        res.append(f"{name}={'blocked' if blocked else 'allowed'}")
    edit = ",".join(t for t in ("Edit", "MultiEdit", "NotebookEdit") if t in tools) or "none"
    print(f"{role}: bash={'Bash' in tools} write={'Write' in tools} edit_tools={edit} " + " ".join(res))
EOF
```

- WHEN `(for w in intake build; do node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/$w.js "$(cat ${TMPDIR:-/tmp}/t0030-$w.json)"; done | grep -v '^clerk ' | sed 's/ .*//' | sort -u | while read a; do echo "$a=$(sed -n 's/^name: *//p' agents/$a.md 2>/dev/null | grep -cx "$a" | sed 's/^1$/defined/;s/^0$/missing/')"; done)`
- THEN it prints exactly `factory-implementer=defined`, `factory-planner=defined`, `factory-reviewer=defined`, `factory-spec-critic=defined`, `factory-spec-writer=defined`, `factory-triage=defined`, `factory-verifier=defined`, one per line

#### Scenario: Every role definition points at the run's prompt and copies none
- WHEN `(for a in triage spec-writer spec-critic planner implementer reviewer verifier; do echo "$a: points=$(grep -c 'system-prompt.txt' agents/factory-$a.md 2>/dev/null | awk '{print ($1 > 0)}') copy=$(grep -c '^ROLE:' agents/factory-$a.md 2>/dev/null)"; done)`
- THEN it prints exactly `triage: points=1 copy=0`, `spec-writer: points=1 copy=0`, `spec-critic: points=1 copy=0`, `planner: points=1 copy=0`, `implementer: points=1 copy=0`, `reviewer: points=1 copy=0`, `verifier: points=1 copy=0`, one per line

#### Scenario: init installs every definition and adds only missing ones
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; ls .claude/agents | tr '\n' ' '; echo; rm -f .claude/agents/factory-implementer.md .claude/agents/factory-reviewer.md .claude/agents/factory-verifier.md; echo local >> .claude/agents/factory-planner.md; $B init 2>/dev/null | tail -1 | grep -o '"agents": \[[^]]*\]' | grep -o 'factory-[a-z-]*\.md' | tr '\n' ' '; echo; tail -1 .claude/agents/factory-planner.md)`
- THEN it prints `factory-clerk.md factory-implementer.md factory-planner.md factory-reviewer.md factory-spec-critic.md factory-spec-writer.md factory-stub.md factory-triage.md factory-verifier.md `, then `factory-implementer.md factory-reviewer.md factory-verifier.md `, then `local`

### Requirement: The reviewer and verifier may write only their run's output and scratch files with the file tools
The reviewer and verifier definitions MUST omit Edit, MultiEdit and NotebookEdit and keep Bash and Write, and their hooks MUST block a Write to any path other than their own role's run `output.md` or a file under that run's `scratch/`, after resolving `..`; the implementer definition SHALL keep Edit and Write with no such limit.

#### Scenario: A checker's Write is limited to its run's output file and scratch directory
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(.venv/bin/python ${TMPDIR:-/tmp}/t0030-fence.py)`
- THEN it prints exactly these three lines:
  `reviewer: bash=True write=True edit_tools=none output=allowed scratch=allowed worktree=blocked escape=blocked other_run=blocked repo=blocked`
  `verifier: bash=True write=True edit_tools=none output=allowed scratch=allowed worktree=blocked escape=blocked other_run=blocked repo=blocked`
  `implementer: bash=True write=True edit_tools=Edit output=allowed scratch=allowed worktree=allowed escape=allowed other_run=allowed repo=allowed`

=== specs/build-dispatch/spec.md
## ADDED Requirements
### Requirement: A role whose agent type is not registered parks its ticket with no run in flight
When a role's agent call fails because the session has not registered its agent type, the workflow MUST record that run killed and park the ticket with `agent call failed: <role>: <error>`; when no factory agent is registered at all, the workflow SHALL stop at its first store command, having written nothing.

#### Scenario: A build run before the build-role agents register parks the sub-ticket
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0030-throw.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}}')`
- THEN it prints exactly `run finish run-0009-x --status-override KILLED`, then `ticket park T-0001.1 --reason "agent call failed: implementer: agent type 'factory-implementer' not found" --outputs run-0009-x`

#### Scenario: A workflow in a session with no factory agents stops at its first store command
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(for w in intake build; do node ${TMPDIR:-/tmp}/t0030-throw.mjs factory/workflows/$w.js '{}' all; done)`
- THEN it prints exactly `stopped: agent type 'factory-clerk' not found after 1 agent call(s)` twice, one per line

=== specs/role-inputs/spec.md
## ADDED Requirements
### Requirement: Downstream roles receive the pinned spec without Evidence and Responses
The composed input of the planner, implementer, reviewer and verifier, the parent-close verifier included, SHALL hold every section of the pinned spec except `## Evidence` and `## Responses`, and MUST name the full spec file's absolute path.

#### Scenario: Downstream roles get every spec section but Evidence and Responses, and the full spec's path
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0030-spec.sh && marks planner $(comp planner T-0001) && marks implementer $(comp implementer T-0001.1) && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H30 >/dev/null && marks reviewer $(comp reviewer T-0001.1) && marks verifier $(comp verifier T-0001.1) && bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null && marks parent-close $(comp verifier T-0001))`
- THEN it prints exactly `planner: evidence=0 responses=0 kept=9 full=1`, `implementer: evidence=0 responses=0 kept=9 full=1`, `reviewer: evidence=0 responses=0 kept=9 full=1`, `verifier: evidence=0 responses=0 kept=9 full=1`, `parent-close: evidence=0 responses=0 kept=9 full=1`, one per line

### Requirement: A round-2 critic receives the smaller of the diff and the previous version
A round-2 critic's input MUST hold the unified diff from the previous spec version to the current one when that diff is smaller than the previous version, and SHALL hold the previous version whole otherwise, with its prior findings in both cases.

#### Scenario: A round-2 critic receives a small revision as a diff
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh small) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) added=$(grep -cx -- '+NEW-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
- THEN it prints exactly `removed=1 added=1 keep100=1 prior_findings=1`

#### Scenario: A round-2 critic receives a rewritten spec's previous version whole
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh rewrite) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) other100=$(grep -cx 'other line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
- THEN it prints exactly `removed=0 keep100=1 other100=1 prior_findings=1`

=== specs/role-effort/spec.md
## ADDED Requirements
### Requirement: An instance's effort map reaches each role's agent call and run record
A role listed in the instance's `effort:` map SHALL have that level passed to its agent call and recorded as `effort` in its run's `meta.yaml`; a role with no entry MUST get no effort argument and `effort: null`; the store-command agent SHALL stay at `low`; and `meta.yaml` SHALL record whether the run was inline.

#### Scenario: The intake workflow gives triage the effort the instance sets and records it
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once. The store commands run for real on a scratch instance's own store.
- WHEN `(B=$PWD/bin/factory; for c in high:inline none:typed; do e=${c%%:*}; m=${c##*:}; T=$(cd "$(mktemp -d)" && pwd -P); git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && { [ $e = none ] || printf 'effort:\n  triage: %s\n' $e >> .factory/instance.yaml; } && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && M=$T/tgt/.factory/state/runs/run-0001-triage/meta.yaml && echo "$(node ${TMPDIR:-/tmp}/t0030-e2e.mjs $T/tgt/.factory $([ $m = inline ] && echo 1)) meta_effort=$(sed -n 's/^effort: *//p' $M | grep . || echo absent) inline=$(sed -n 's/^inline: *//p' $M | grep . || echo absent)"; done)`
- THEN it prints exactly `role effort=high clerk effort=low meta_effort=high inline=true`, then `role effort=none clerk effort=low meta_effort=null inline=false`

#### Scenario: The build workflow passes the run's effort to each build role's agent call
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/build.js "$(sed 's/"run finish"/"run start": {"out": {"ok": true, "run_id": "run-0009-x", "worktree": "\/w", "effort": "max"}}, "run finish"/' ${TMPDIR:-/tmp}/t0030-build.json)")`
- THEN it prints exactly `factory-planner effort=max`, `factory-implementer effort=max`, `factory-reviewer effort=max`, `factory-verifier effort=max`, `clerk effort=low`, one per line

### Requirement: run start refuses an effort map with an unknown role or level
`factory run start` MUST refuse with exit 2, naming the bad entry and starting no run, when the instance's `effort:` map has a level other than `low`, `medium`, `high`, `xhigh` or `max`, or a key that is not one of the seven roles.

#### Scenario: An effort map with an unknown level or role is refused
- WHEN `(for e in 'triage: extreme' 'triag: high'; do T=$(cd "$(mktemp -d)" && pwd -P); cp -R tests/factory/fixtures/instance $T/inst && printf 'effort:\n  %s\n' "$e" >> $T/inst/instance.yaml && printf '# F\n\nDo x.\n' > $T/req.md && FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/s bin/factory ticket new --file $T/req.md >/dev/null && FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/s bin/factory run start --role triage --ticket T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -cw -e extreme -e triag $T/err) runs=$(ls $T/s/runs 2>/dev/null | grep -c .)"; done)`
- THEN it prints exactly `exit=2 named=1 runs=0`, twice, one per line

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents describe registered role agents, trimmed inputs and effort
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; the design doc's routing table and the build spec SHALL describe the trimmed spec and the round-2 diff; README SHALL describe registered roles, the `agent call failed` park and the `effort:` map and SHALL no longer tell every target to run inline or list per-role effort as not built; `.factory/README.md` SHALL no longer say this repo adds no `.claude/agents/`; no prompt copy SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records registered agents, trimmed inputs and effort as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e factory-implementer -e Evidence -e effort -e diff -e inlineRoles | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The routing table and build spec describe the trimmed spec and the diff, and no prompt changes
- WHEN `(echo "critic_diff=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c diff) trimmed_rows=$(grep -e '^| Human spec gate | Approved' -e '^| Planner | PLANNED' -e '^| Implementer | READY-FOR-REVIEW' -e '^| Merge gate | CI green' docs/design.md | grep -c Evidence) build_spec=$(grep 'round ≥ 2: prior findings' dev/build-harness.spec.md | grep -c diff) prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `critic_diff=1 trimmed_rows=4 build_spec=1 prompts=0`

#### Scenario: README and the instance page describe registered roles, the park and effort
- WHEN `(Q=$(printf '\140'); R=$(tr '\n' ' ' < README.md | tr -s ' '); I=$(tr '\n' ' ' < .factory/README.md | tr -s ' '); echo "inline_everywhere=$(echo "$R" | grep -o 'inlineRoles: true. on every target' | grep -c .) parks=$(echo "$R" | grep -o 'agent call failed' | grep -c . | awk '{print ($1 > 0)}') effort_map=$(grep -c "${Q}effort:${Q}" README.md | awk '{print ($1 > 0)}') effort_not_built=$(grep -c 'Per-role effort settings' README.md) instance_inline=$(echo "$I" | grep -o 'adds no .\.claude/agents/.' | grep -c .)")`
- THEN it prints exactly `inline_everywhere=0 parks=1 effort_map=1 effort_not_built=0 instance_inline=0`

#### Scenario: The role-agents change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

=== verification.md
## Acceptance
- Every agent type the workflows ask for has a definition → NEW. Today it prints `factory-implementer=missing`, `factory-reviewer=missing` and `factory-verifier=missing`.
- Every role definition points at the run's prompt and copies none → NEW. Today the first four lines end `copy=1`, and the implementer, reviewer and verifier lines print `points= copy=` because their files do not exist.
- init installs every definition and adds only missing ones → NEW. Today the first line lists six files, with no implementer, reviewer or verifier, and the second line is empty.
- A checker's Write is limited to its run's output file and scratch directory → NEW. Today it prints `reviewer: missing`, `verifier: missing` and `implementer: missing`.
- A build run before the build-role agents register parks the sub-ticket → REGRESSION.
- A workflow in a session with no factory agents stops at its first store command → REGRESSION.
- Downstream roles get every spec section but Evidence and Responses, and the full spec's path → NEW. Today all five lines print `evidence=1 responses=1 kept=9 full=0`.
- A round-2 critic receives a small revision as a diff → NEW. Today it prints `removed=0 added=0 keep100=2 prior_findings=1`: the previous version whole, no diff.
- A round-2 critic receives a rewritten spec's previous version whole → REGRESSION.
- The intake workflow gives triage the effort the instance sets and records it → NEW. Today both lines print `role effort=none clerk effort=low meta_effort=absent inline=absent`.
- The build workflow passes the run's effort to each build role's agent call → NEW. Today all four role lines print `effort=none`.
- An effort map with an unknown level or role is refused → NEW. Today both lines print `exit=0 named=0 runs=1`: the run starts, and the map is ignored.
- The changelog records registered agents, trimmed inputs and effort as its last entry → NEW. Today it prints `CONTIGUOUS`, then `0`.
- The routing table and build spec describe the trimmed spec and the diff, and no prompt changes → NEW. Today it prints `critic_diff=0 trimmed_rows=0 build_spec=0 prompts=0`.
- README and the instance page describe registered roles, the park and effort → NEW. Today it prints `inline_everywhere=1 parks=0 effort_map=0 effort_not_built=1 instance_inline=1`.
- The role-agents change adds no whitespace errors → REGRESSION.

## Current truth: build-dispatch

# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

## Current truth: harness-docs

# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL gain entry 51 covering every part, numbered without a gap, `README.md` SHALL describe the new `resolve` behaviour and relative environment paths, and the change MUST add no whitespace errors.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print n, (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `51 CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

#### Scenario: The change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL gain one entry for this change as its last numbered entry, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store; no prompt copy under `docs/prompts/` or `factory/prompts/` SHALL change; and the change MUST add no whitespace errors.

#### Scenario: The changelog records the guard as its last entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule, and no prompt copy changes
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 dirs=1 prompts=0`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

#### Scenario: The guard change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule, and the build spec SHALL call the store branch only `factory-store`. `docs/changelog.md` SHALL gain one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location. The change MUST add no whitespace errors.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The build spec calls the store branch factory-store
- WHEN `(Q=$(printf '\140'); echo "old_name=$(grep -c "${Q}tickets${Q}\|refs/heads/tickets\|HEAD:tickets" dev/build-harness.spec.md) new_name=$(grep -c 'factory-store' dev/build-harness.spec.md | awk '{print ($1 > 0)}')")`
- THEN it prints `old_name=0 new_name=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

#### Scenario: The store-branch change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

## Current truth: harness-suite

# harness-suite

## Requirements

### Requirement: The harness suite runs mid-edit without loosening the lock
The harness's own test suite SHALL pass in a checkout that has an uncommitted edit under a harness path, and a store command on an instance's own store run from such a checkout MUST still be refused.

#### Scenario: The harness suite passes with an uncommitted harness edit
The command gives pytest its own temporary directory under `/tmp`, because four existing tests need one outside every repository and instance. Run it as written, whatever `TMPDIR` the caller has set; it removes that directory when it ends.
- WHEN `(T=$(mktemp -d) && P=$(mktemp -d /tmp/t0023-suite.XXXXXX) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && cd $T/c && TMPDIR=$P .venv/bin/python -m pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P")`
- THEN it prints one line reporting a number of passed tests and no `failed` or `error`

#### Scenario: The uncommitted-edit refusal still holds on an instance's own store
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && echo '# uncommitted edit' >> $T/c/factory/status.py && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && $T/c/bin/factory config >/dev/null 2>$T/err; echo "exit=$?"; head -1 $T/err | grep -o 'has uncommitted changes:$')`
- THEN it prints `exit=2`, then `has uncommitted changes:`

## Current truth: human-resolution

# human-resolution

## Requirements

### Requirement: A ruling returns a BLOCKED sub-ticket to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts with `BLOCKED` MUST write F as the ticket's next ruling, return it to `ready-for-implementer` at the same round, and the next implementer input SHALL contain the ruling.

#### Scenario: A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0023-parent.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate (no spec store).
T23=$(mktemp -d); export FACTORY_STATE=$T23/store
printf '# Fixture\n\nThe bot should do the thing.\n' > $T23/req.md && printf '## Problem\nx\n' > $T23/spec.md
bin/factory ticket new --file $T23/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T23/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T23/t && git -C $T23/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
export FACTORY_REPO=$T23/t FACTORY_INTEGRATION_BRANCH=main
EOF
cat > ${TMPDIR:-/tmp}/t0023-closed.sh <<'EOF'
# Sourced after t0023-parent.sh: T-0001 split into T-0001.1 and T-0001.2, both merged, then parked
# by a FAILED parent-close run.
printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n' > $T23/plan1.md
bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null
bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket transition T-0001 --to ready-for-parent-verify --by t >/dev/null
bin/factory ticket park T-0001 --reason "FAILED from parent-close verifier" >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0023-wf.mjs <<'EOF'
// node t0023-wf.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk that
// reports an empty stderr. A clerk command gets the reply of the longest key its `bin/factory`
// arguments start with: {"out": <object printed as JSON on stdout> | "raw": <stdout text>, "exit": n},
// or a list of such replies, used in turn (the last one repeats).
// Defaults: `config` and `run start` succeed; anything else prints {"ok": true}. Role agents return
// a bare trailer. Prints `park: <reason>` per ticket park and `start: <role>` per run start, in order.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  const p = cmd.match(/^ticket park \S+ --reason "([^"]*)"/)
  if (p) lines.push(`park: ${p[1]}`)
  const s = cmd.match(/^run start --role (\S+)/)
  if (s) lines.push(`start: ${s[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket park T-0001.1 --reason "BLOCKED from implementer" >/dev/null && printf 'Ruling: take the second approach.\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') pr=$(bin/factory ticket show T-0001.1 | sed -n 's/^  pr: //p')"; cmp -s $T23/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo ruling=kept || echo ruling=missing; R=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take the second approach.')")`
- THEN it prints `exit=0 ready-for-implementer pr=0`, then `ruling=kept`, then `in_input=1`

### Requirement: Existing ruling routes are unchanged
A ruling on a critic ESCALATE park SHALL still return the ticket to `ready-for-critic`.

#### Scenario: A ruling on a critic ESCALATE still returns the ticket to the critic
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; bin/factory ticket park T-0001 --reason "ESCALATE from critic" >/dev/null; echo r > $T/r.md; bin/factory resolve T-0001 --ruling $T/r.md >/dev/null; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 ready-for-critic`

### Requirement: A re-plan returns a fully merged parent to its planner
`factory resolve <parent> --replan F` on a parked parent whose sub-tickets have all merged MUST move it to `ready-for-planner` with F as its next ruling, and the next planner input SHALL contain F and list each existing sub-ticket with its title and state; with any sub-ticket not merged it MUST refuse, naming that sub-ticket, and write nothing.

#### Scenario: A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'Re-plan: add one fix for the case-insensitive path.\n' > $T23/note.md; bin/factory resolve T-0001 --replan $T23/note.md >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; R=$(bin/factory run start --role planner --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && bin/factory run compose $R >/dev/null; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "in_input=$(cat $I 2>/dev/null | grep -c 'Re-plan: add one fix') listed=$(cat $I 2>/dev/null | grep -cxF -e '- T-0001.1 / First: merged' -e '- T-0001.2 / Second: merged')")`
- THEN it prints `exit=0 ready-for-planner`, then `in_input=1 listed=2`

#### Scenario: A re-plan is refused while a sub-ticket is not merged
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && bin/factory ticket set T-0001.2 status=closed >/dev/null && echo n > $T23/note.md; echo "names=$(bin/factory resolve T-0001 --replan $T23/note.md 2>&1 >/dev/null | grep -c 'T-0001.2')"; echo "$(bin/factory ticket show T-0001 | sed -n 's/^status: //p') $(ls $FACTORY_STATE/approvals/T-0001 | tr '\n' ' ')")`
- THEN it prints `names=1`, then `parked spec-v1.yaml ` (still parked, and no ruling file written)

### Requirement: A redispatch sets aside only rows that did not pass
`factory resolve <id> --redispatch` MUST keep a reviewer row that is `APPROVE`, and the verifier and gate rows together when they are `VERIFIED` and `PASS`, and SHALL move every other row of that commit to `superseded-<n>/`.

#### Scenario: A redispatch after a killed reviewer keeps the verifier's passing rows
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --killed --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "budget kill: reviewer" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: ci.yaml verifier.yaml `, then `set aside: reviewer.yaml `

#### Scenario: A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && H=abababababababababababababababababababab && bin/factory ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && printf "Commit: $H\nGate suite: FAIL\nSTATUS: SPEC-DEFECT\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/v.md && printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T23/r.md && bin/factory results record T-0001.1 --head $H --role verifier --output $T23/v.md --run run-0002-verifier >/dev/null && bin/factory results record T-0001.1 --head $H --role reviewer --output $T23/r.md --run run-0003-reviewer >/dev/null && bin/factory ticket park T-0001.1 --reason "SPEC-DEFECT from verifier" >/dev/null && bin/factory resolve T-0001.1 --redispatch >/dev/null && echo "kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')" && echo "set aside: $(ls $FACTORY_STATE/results/$H/superseded-1 | tr '\n' ' ')")`
- THEN it prints `kept: reviewer.yaml `, then `set aside: ci.yaml verifier.yaml `

## Current truth: live-store-guard

# live-store-guard

## Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths` (and any command given `--accept-harness`) MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

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

### Requirement: Writes from inside a store's run directories or code checkouts are refused, marked or not
Every `factory` command on an instance's own store except the read-only list above MUST be refused with exit 2, writing nothing, when the caller's directory lies under that store's `runs/` or `worktrees/`, whether or not its environment has `FACTORY_DISPATCH=1` and whether or not any run is in flight.

#### Scenario: Marked writes from a run's scratch directory or a worktree directory are refused, init included
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && mkdir -p $S/worktrees/T-0001/sub && S0=$(snap); cd $W && FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B init --repo-name x >/dev/null 2>&1; i=$?; cd $S/worktrees/T-0001/sub && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "scratch_decision=$d scratch_init=$i worktree_new=$n store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `scratch_decision=2 scratch_init=2 worktree_new=2 store=unchanged agents=none`

#### Scenario: Writes from a finished run's scratch directory are refused with no run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1) && S0=$(snap); cd $W && $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; FACTORY_DISPATCH=1 $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "idle=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]') new=$n decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `idle=1 new=2 decision=2 store=unchanged`

### Requirement: Reads, marked commands from outside the store, throwaway stores and idle stores stay open
While a run is in flight on the live store, the read-only commands SHALL succeed from anywhere, a command with `FACTORY_DISPATCH=1` run from outside the store's `runs/` and `worktrees/` SHALL succeed as before, and a command on a throwaway store (`FACTORY_STATE` naming another store) SHALL NOT be fenced from any directory; with no run in flight, unmarked writes from outside those directories SHALL succeed as before.

#### Scenario: Read commands still answer while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && $B ticket show T-0001 >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B log tail >/dev/null 2>&1; l=$?; $B results show T-0001 >/dev/null 2>&1; r=$?; cd $W && $B ticket show T-0001 >/dev/null 2>&1; w=$?; echo "show=$s config=$c log=$l results=$r inside=$w")`
- THEN it prints exactly `show=0 config=0 log=0 results=0 inside=0`

#### Scenario: A marked write from the repository root still writes while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && cd $T/tgt && FACTORY_DISPATCH=1 $B decision add T-0001 "marked line" >/dev/null 2>&1; d=$?; FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; f=$?; echo "decision=$d finish=$f cleared=$($B ticket show T-0001 --json | tail -1 | grep -c '"in_flight": \[\]')")`
- THEN it prints exactly `decision=0 finish=0 cleared=1`

#### Scenario: A throwaway store is not fenced, even from a run's scratch directory
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && (cd $T/tgt && FACTORY_STATE=$T/s $B init >/dev/null 2>&1); i=$?; cd $W && FACTORY_STATE=$T/s $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "init=$i new=$n")`
- THEN it prints exactly `init=0 new=0`

#### Scenario: With no run in flight, unmarked commands write as before
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B run finish $R --status-override KILLED >/dev/null 2>&1; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B decision add T-0001 "after the run" >/dev/null 2>&1; d=$?; echo "new=$n decision=$d")`
- THEN it prints exactly `new=0 decision=0`

### Requirement: The marker does not lift the harness lock
A command with `FACTORY_DISPATCH=1` on an instance's own store MUST still be refused by the harness lock's uncommitted-edit check, with exit 2 and nothing written, whether or not a run is in flight.

#### Scenario: A marked write from a harness checkout with an uncommitted edit is still refused
- WHEN `(T=$(mktemp -d) && git clone -q --no-checkout . $T/c && git -C $T/c checkout -q $(git rev-parse HEAD) && ln -s "$PWD/.venv" $T/c/.venv && git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $T/c/bin/factory init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $T/c/bin/factory ticket new --file $T/req.md >/dev/null && $T/c/bin/factory run start --role triage --ticket T-0001 >/dev/null && echo '# uncommitted edit' >> $T/c/factory/status.py && S0=$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum) && FACTORY_DISPATCH=1 $T/c/bin/factory decision add T-0001 x >/dev/null 2>$T/err; echo "exit=$? lock=$(head -1 $T/err | grep -c 'has uncommitted changes:$') store=$([ "$(find $T/tgt/.factory -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 lock=1 store=unchanged`

## Current truth: merge-gate

# merge-gate

## Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`

## Current truth: store-setup

# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on exactly one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses when more than one remote carries the store branch
`factory init` MUST refuse with exit 2, creating no store and no local branch, when the own store is missing, no local `factory-store` exists and more than one remote carries it; the refusal MUST name each `<remote>/factory-store`.

#### Scenario: init on a clone with two remotes carrying the store branch refuses and names both
- GIVEN the three fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

```sh
cat > ${TMPDIR:-/tmp}/t0025-old.sh <<'EOF'
# Sourced from the repo root: a target whose store is a plain directory tracked on main, as both
# instances keep it today. Leaves the shell in the target; PRE is the commit that last tracked it.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
mkdir -p .factory/state && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
git add -A && git commit -q -m "instance, with its store on main" && PRE=$(git rev-parse HEAD)
EOF
cat > ${TMPDIR:-/tmp}/t0025-b1.sh <<'EOF'
# Sourced from the repo root: a target whose store at .factory/state is already a git worktree of
# an unborn factory-store branch, built with git alone (so it is the same layout whatever the
# harness does), then given an instance by init. Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
git worktree add -q --orphan -b factory-store .factory/state && echo /.factory/state/ >> "$(git rev-parse --git-path info/exclude)"
$B init --repo-name demo >/dev/null 2>&1
EOF
cat > ${TMPDIR:-/tmp}/t0025-gate.sh <<'EOF'
# Sourced from the repo root: a target made by init, its instance committed on main, and T-0001 on
# branch factory/T-0001 with reviewer APPROVE, verifier VERIFIED and gate PASS on its head H.
# Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance
git checkout -q -b factory/T-0001 && echo x > x.txt && git add x.txt && git commit -q -m work
H=$(git rev-parse HEAD) && git checkout -q main
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
$B ticket set T-0001 status=checks-in-flight branch=factory/T-0001 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/rv.md
$B results record T-0001 --head $H --role verifier --output $T25/v.md --run run-0001-verifier >/dev/null
$B results record T-0001 --head $H --role reviewer --output $T25/rv.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
- THEN it prints `exit=2 store=none local_branch=0 names=1,1`

### Requirement: init refuses to run from inside the store checkout
`factory init`, run with `FACTORY_INSTANCE` unset from a directory whose git top level is a checkout of `factory-store`, or is the store of the instance found from that directory or a checkout of the same repository inside that store, MUST refuse with exit 2 and write nothing, whichever commit the store has checked out, so that it never creates an instance inside the live store; other commands run from there SHALL still find the live instance, and `init` in a separate repository under the store SHALL still create that repository's instance.

#### Scenario: init from a scratch directory inside the store checkout refuses and leaves the store unchanged
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init from the store checkout on a detached HEAD refuses
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init in a separate repository under a run's scratch directory still creates its instance
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 instance=written live=ready-for-triage`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH, and verify the copy before removing anything;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`

## Current truth: sub-ticket-planning

# sub-ticket-planning

## Requirements

### Requirement: A later plan's sub-tickets continue the parent's numbering
`factory subticket add` on a parent that already has sub-tickets MUST number the new ones from the next free index, SHALL accept a `Depends on:` line naming an existing sub-ticket, and MUST refuse a plan whose head line reuses an existing sub-ticket's id, writing nothing.

#### Scenario: A later plan's sub-tickets take the next free ids and may depend on a merged sibling
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'ST-1 / Fix the bypass\nDepends on: T-0001.2\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md 2>/dev/null | tail -1 | grep -o '"id": "[^"]*"\|"depends_on": \[[^]]*\]'; bin/factory ticket ready-implementers T-0001 | tail -1 | grep -o '"ready": \[[^]]*\]')`
- THEN it prints `"id": "T-0001.3"`, then `"depends_on": ["T-0001.2"]`, then `"ready": ["T-0001.3"]`

#### Scenario: A plan that reuses an existing sub-ticket id is refused and writes nothing
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0023-closed.sh && printf 'T-0001.1 / Again\nDepends on: none\nParallel-safe: yes\n' > $T23/plan3.md; bin/factory subticket add T-0001 --file $T23/plan3.md >/dev/null 2>&1; echo "exit=$? $(ls $FACTORY_STATE/tickets | tr '\n' ' ')")`
- THEN it prints `exit=2 T-0001.1.yaml T-0001.2.yaml T-0001.yaml `

## Decision log (decisions.md): standing decisions, read-only

2026-10-04 T-0023 `resolve --ruling F` also accepts a park whose reason starts with `BLOCKED`. It writes F as the next `approvals/<id>/ruling-<n>.md` and returns the sub-ticket to `ready-for-implementer` at the same round.
2026-10-04 T-0023 `resolve PARENT --replan F` moves a parked parent whose sub-tickets have all merged to `ready-for-planner`, with F as its next ruling. The planner receives F and plans the fix. Rejected: the requester's `--replan --file <plan>` straight to `planned`. It needs a new routing edge, which the queue policy does not count as small. It would also skip the planner. `dev/build-harness.spec.md` already sends a re-plan through the planner.
2026-10-04 T-0023 On a re-plan, the planner's input lists the parent's existing sub-tickets, each with its title and state. The human's note F therefore needs to say only what to fix. Rejected: asking the human to restate in F what has merged, which the store already knows.
2026-10-04 T-0023 Sub-tickets that a later plan adds take the next free ids under the parent, and their `Depends on:` lines may name the parent's existing sub-tickets. A plan head line that reuses an existing sub-ticket's id is refused. Rejected: honouring explicit non-colliding ids, a second numbering rule that the planner's free-form ids would make ambiguous.
2026-10-04 T-0023 A park reason is never blank. When the clerk relays an empty stderr, the workflows use the refusal's JSON `error`, and failing that `exit <n>, no JSON on stdout` or `exit <n>, no error text`. Rejected: editing each of the 26 reason sites.
2026-10-04 T-0023 A redispatch sets aside a checker's rows only when they did not pass. The reviewer's row is kept when it is `APPROVE`. The verifier and gate rows are kept together when they are `VERIFIED` and `PASS`, because one verifier run writes both. The build then runs only the checkers with no row on that commit. After an implementer run it still runs both. Rejected: a `--roles` flag on redispatch, which no reported case needs.
2026-10-04 T-0023 The store gets a `.gitattributes` holding `runs/** -whitespace`. `init` and every `run start` write it the way they already write `.gitignore`. Rejected: rewriting committed records, and excluding the store path inside each gate command.
2026-10-04 T-0023 `init` refuses, with exit 2 and nothing written, to create an instance while `FACTORY_STATE` names another store. A compose with no `context.md` refuses with exit 2. Rejected: writing every instance piece from a throwaway-store `init`. That contradicts the rule that such a run initialises only that store.
2026-10-04 T-0023 A relative `FACTORY_INSTANCE`, `FACTORY_STATE` or `FACTORY_REPO` resolves against the caller's directory: `FACTORY_CWD`, else the working directory.
2026-10-04 T-0023 The suite's own-store cases that are not about the uncommitted-edit refusal run the CLI through a test-only launcher that stubs that one check. The refusal itself keeps its tests on a clone's real `bin/factory`. Rejected: a switch the production CLI honours, which would loosen the check. Also rejected: running every case from a committed snapshot of the working tree, which changes every assertion that names this checkout's revision or paths.
2026-10-04 T-0023 The suite scenario gives pytest a fresh temporary directory under `/tmp` and removes it afterwards. Four existing tests need a temporary directory outside every repository, and an agent's scratch directory lies inside this one. The scenario states this in its command, so no role has to choose between its scratch rule and a valid run. Rejected: fixing those four tests in this ticket, which is beyond H8 and needs its own design (Out-of-scope observations).
2026-10-04 T-0023 The workflow-script fixes are checked by acceptance scenarios that run the scripts under node with a stub clerk. They get no suite test, because the suite does not need node today and adding that would change what the gate needs.
2026-10-04 T-0023 The change is built as four seams (design.md, "Size and seams"). They share one changelog entry, 51.
2026-10-04 T-0024 T-0024: instance B keeps the spec store created 2026-10-04 by run-0196; its tickets close by archive into current truth (operator)
2026-10-04 T-0024 While a role run is in flight on a live store, a human or runner writes it by prefixing that one command with FACTORY_DISPATCH=1; README documents it and the refusal text never names it (operator)
2026-10-04 T-0024 Instance B keeps the spec store that run-0196 created. Its tickets close by archive into current truth, and `decisions.md` keeps reaching the spec writer, critic and planner. The operator decided this in the first answer to this ticket, and it is already recorded in `decisions.md`. This is a standing decision. This ticket touches README, so it also corrects README's stale "never entered it" line, as that answer directs.
2026-10-04 T-0024 While a role run is in flight on a live store, the operator or a runner session writes it by putting `FACTORY_DISPATCH=1` in front of that one command. README documents this. The refusal text never names the marker. The operator decided this in the same answer, and it is already recorded in `decisions.md`. This is a standing decision for every runner session, including the Driver session that runs the Nanobot fork's instance (instance A).
2026-10-04 T-0024 A write is refused, marker or not and run in flight or not, when the caller's directory lies under the own store's `runs/` or `worktrees/`. The operator's gate review asked for this rule. Rejected: applying it only while a run is in flight, because a process a role left running in its run directory would then write freely once the store went idle. Rejected: letting the marker lift it, because the rule exists so that a copied or exported marker does not help from there. This is a standing decision: the operator and runner sessions run store writes from outside the store.
2026-10-04 T-0024 The location rule is checked first, then the marker, then the in-flight list.
2026-10-04 T-0024 The in-flight rule acts only on an instance's own store, and only while at least one run is in flight on any ticket of that store. Rejected: refusing every unmarked write at all times, as the requester proposed. The operator would then need the marker on every command and would export it in the shell, and every role run started from that shell would inherit it. The operator's decision on the marker assumes unmarked writes when nothing is in flight.
2026-10-04 T-0024 The in-flight rule checks every ticket's in-flight list, not only the calling ticket's. The tool cannot tell which run, if any, is calling.
2026-10-04 T-0024 The marker is the environment variable `FACTORY_DISPATCH=1`. Both workflow scripts put it in front of every clerk command. Rejected: the requester's exemption for "a human's `--by`". Human commands have no `--by`, and `ticket transition` requires one from everyone.
2026-10-04 T-0024 A write is every command except a fixed read-only list: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. Any command given `--accept-harness` is a write, because it rewrites the lock and logs. A new command is fenced until someone adds it to the list. Rejected: the requester's list of ten write commands. It misses writes such as `ticket set`, `ticket park`, `ticket head`, `ticket ready-implementers`, `ticket parent-check`, `run compose` and `spec add`.
2026-10-04 T-0024 The refusal exits 2 and writes nothing. Its text is `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<store>; in flight: <run ids>` for the in-flight rule and `<store>; called from inside its runs/` (or `worktrees/`) for the location rule. The advice is meant for a role. The operator learns the marker from README.
2026-10-04 T-0024 A run left in flight by a dead workflow keeps the in-flight rule up. The operator clears it with a marked `run finish <run> --status-override KILLED`, run from the repository root, and README says so. Rejected: a timeout that drops the fence by itself. A long run that is still working would lose the fence.
2026-10-04 T-0024 The fence guards against accidents, not against a determined agent. It is not a security boundary. A role working from outside the store that copies the marker from the workflow scripts or README still gets through. That is recorded under Risk rather than designed around. Isolating role runs at the operating-system level is issue #37.
2026-10-04 T-0024 The fence is checked before the harness lock, the check that each instance runs only the harness revision it has accepted. A fenced command is refused before it reaches the lock, so a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged, so the marker cannot be used to get past the lock. Rejected: checking the fence after the lock, because `--accept-harness` rewrites the lock inside that check, so a fenced acceptance would write before it was refused.
2026-10-04 T-0024 Part B (a preamble line) is cut. The incident came from the test suite, not from a command the role typed, so a preamble line would not have stopped it. The refusal text gives the same advice at the moment it matters.
2026-10-04 T-0024 Part C (the tripwire on the store root) is cut. Role runs legitimately write their own run directory in the store (`output.md`, `scratch/`). Clerk commands for other tickets' runs also write the store during a run. A comparison of the store root therefore cannot tell whose write it saw. The fence refuses the write before it happens.
2026-10-04 T-0022 Removing clearly redundant work (a step, run or check that cannot change any outcome) is pre-approved, provided every refusal the pipeline gives today still fires (operator, 2026-10-04: 'slashing clearly redundant work is always going to be OK, if we trust our process')
2026-10-04 T-0022 Under a sub-ticket's Tests to change, the planner may list tests an earlier sibling of the same parent added, with a harness check that each first appeared in a sibling's merge; pre-existing tests still need the approved spec (operator, #40)
2026-10-04 T-0025 The store lives on its own branch, `factory-store`, checked out as a git worktree at the store's path (B1). This is for the operator to confirm at the spec gate. Rejected: B2, the branch written through git plumbing with no working copy. It needs new harness commands to snapshot, show and restore the store, and `git clean -fdx` in the integration checkout deletes the store (Evidence). Rejected: A, a gate exception (operator, 2026-10-04).
2026-10-04 T-0025 A store path must be one the integration branch has never tracked. Both existing stores move from `.factory/state` to `.factory/store`. Rejected: keeping `.factory/state`, where checking out an older commit overwrote an uncommitted record and checking `main` out again deleted it (Evidence).
2026-10-04 T-0025 The branch is named `factory-store`, and the design doc and build spec drop the name `tickets` for it. Rejected: `tickets`, a generic name in a target repo whose branches serve other work, such as the Nanobot repo, which shares its objects with another checkout.
2026-10-04 T-0025 `init` creates a new store as a worktree on an unborn `factory-store` branch, and the operator makes the first commit. On a clone where the branch already exists, `init` checks it out, which restores the store. Rejected: `init` committing, which needs a git identity, and the suite runs under a throwaway HOME that has none.
2026-10-04 T-0025 When no local `factory-store` exists and more than one remote carries it, `init` refuses and names each `<remote>/factory-store`. The operator picks one with `git branch factory-store <remote>/factory-store` and runs `init` again. Rejected: creating a new empty branch, which would silently start a second store history beside the pushed one. Also rejected: preferring `origin`, a guess about which remote is canonical.
2026-10-04 T-0025 With `FACTORY_INSTANCE` unset, `init` refuses, writing nothing, when the caller's git top level is a checkout of `factory-store`. It also refuses when the instance found by walking up from the caller's directory has a store that is that top level, or that contains it in the same repository (the same git common directory). These are the cases where it would build a phantom instance inside the live store. The second condition does not depend on which branch or commit the store has checked out, so a detached store HEAD does not open the route again (operator, round 2 change request N2). The same-repository qualifier keeps `init` working in a separate throwaway repository under a run's scratch directory (Evidence). Rejected: "contains" without that qualifier, which would refuse every suite `init` run with pytest's temporary directory inside a store. Rejected: taking the repository from the parent of `--git-common-dir`. That is the main worktree, which for the Nanobot instance is `~/dev/nanobot`, another checkout on another branch, and for the runtime checkout is `~/dev/spec-factory` (Evidence).
2026-10-04 T-0025 In `init`, every refusal and the store-worktree step come before any instance file is written, so a failed worktree step (for example, git's "already used by worktree" when `init` runs in a code checkout of a repo whose store branch is checked out elsewhere) leaves nothing behind.
2026-10-04 T-0025 The integration checkout ignores the store through the repo's git exclude file, which `init` and `store migrate` write. Rejected: a line in the target's tracked `.gitignore`. That would change the target's code to record a fact about one clone.
2026-10-04 T-0025 A new command, `factory store migrate --to PATH`, moves an existing store. It refuses unless the store is idle and committed, and it leaves the integration-branch side uncommitted for the operator to review. Rejected: a hand procedure, untested, run once on each repo by a different session.
2026-10-04 T-0025 `store migrate` deletes the old store directory only after it has checked that every ignored file (run scratch directories, tripwire baselines) was copied byte for byte. If the check fails, it undoes its own worktree and branch and leaves the old store as it was. Rejected: relying on `git status` in the new checkout, which cannot see ignored files.
2026-10-04 T-0025 The store branch starts with one commit whose tree is the store as last committed on the integration branch, and whose message names that commit. Earlier history stays readable with `git log <that commit> -- .factory/state`. Rejected: rewriting history with a subtree split. It would follow only part of the store's past, which began at `intake/state`, and it adds nothing that `main`'s history does not already keep.
2026-10-04 T-0025 An instance whose store is still a plain directory keeps working unchanged. `init` leaves such a store alone and points to `store migrate`. The harness reads and writes the store only through `state_dir`, so it runs with either layout.
