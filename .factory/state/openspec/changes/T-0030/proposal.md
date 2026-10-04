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

## Gate edit (Green session, operator-delegated, 2026-10-04)

The spec store's part splitter is not fence-aware, so the fixture's own `=== ` lines inside the fenced GIVEN block were read as duplicate spec parts and the pin was refused. The fixture heredoc now pipes through `sed 's/^|//'` and its four `=== ` lines carry a `|` prefix: the generated `spec.md` is byte-identical. The splitter bug is filed separately.

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

