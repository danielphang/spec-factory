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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0318-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0318-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0030.1` (branch `factory/T-0030.1`, base `5426ff2ef0e376f6962725bbe08a85eadff40060`, head `d226a4d03ca94bab45bd4221972285a4d16ee0bb`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0030.1

### ST-1 / A registered agent definition for every role, a file-tool fence on the reviewer and verifier, and `run start --inline`
Depends on: none
Parallel-safe: no (ST-2 edits the same `run_start` in `factory/cli.py` and the same `runRole` in both workflow scripts)

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part A, items A1 to A5 (design.md "Proposed change").
- A1: add `agents/factory-implementer.md`, `agents/factory-reviewer.md` and `agents/factory-verifier.md`, with the frontmatter and tool lists given.
- A2: the reviewer's and verifier's `hooks.PreToolUse` fence. It fails closed, exiting 2 on any failure to decide.
- A3: replace the bodies of the four existing role definitions with the single paragraph. Their frontmatter stays as it is.
- A4: add `run start --inline`, which records `inline: true|false` in `meta.yaml`. Both workflow scripts pass the flag in inline mode, and their `inlineRoles` comments are updated.
- A5: `init` stays unchanged.

Acceptance:
- NEW. "Every agent type the workflows ask for has a definition".
  WHEN `(for w in intake build; do node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/$w.js "$(cat ${TMPDIR:-/tmp}/t0030-$w.json)"; done | grep -v '^clerk ' | sed 's/ .*//' | sort -u | while read a; do echo "$a=$(sed -n 's/^name: *//p' agents/$a.md 2>/dev/null | grep -cx "$a" | sed 's/^1$/defined/;s/^0$/missing/')"; done)`
  THEN it prints exactly `factory-implementer=defined`, `factory-planner=defined`, `factory-reviewer=defined`, `factory-spec-critic=defined`, `factory-spec-writer=defined`, `factory-triage=defined`, `factory-verifier=defined`, one per line.
- NEW. "Every role definition points at the run's prompt and copies none".
  WHEN `(for a in triage spec-writer spec-critic planner implementer reviewer verifier; do echo "$a: points=$(grep -c 'system-prompt.txt' agents/factory-$a.md 2>/dev/null | awk '{print ($1 > 0)}') copy=$(grep -c '^ROLE:' agents/factory-$a.md 2>/dev/null)"; done)`
  THEN it prints exactly `triage: points=1 copy=0`, `spec-writer: points=1 copy=0`, `spec-critic: points=1 copy=0`, `planner: points=1 copy=0`, `implementer: points=1 copy=0`, `reviewer: points=1 copy=0`, `verifier: points=1 copy=0`, one per line.
- NEW. "init installs every definition and adds only missing ones".
  WHEN the scenario's command as written in the parent (`$B init --repo-name demo` in a scratch target, then the three build definitions removed, `local` appended to the planner copy, and `$B init` run again).
  THEN it prints `factory-clerk.md factory-implementer.md factory-planner.md factory-reviewer.md factory-spec-critic.md factory-spec-writer.md factory-stub.md factory-triage.md factory-verifier.md `, then `factory-implementer.md factory-reviewer.md factory-verifier.md `, then `local`.
- NEW. "A checker's Write is limited to its run's output file and scratch directory".
  WHEN `(.venv/bin/python ${TMPDIR:-/tmp}/t0030-fence.py)`
  THEN it prints exactly these three lines:
  - `reviewer: bash=True write=True edit_tools=none output=allowed scratch=allowed worktree=blocked escape=blocked other_run=blocked repo=blocked`
  - `verifier: bash=True write=True edit_tools=none output=allowed scratch=allowed worktree=blocked escape=blocked other_run=blocked repo=blocked`
  - `implementer: bash=True write=True edit_tools=Edit output=allowed scratch=allowed worktree=allowed escape=allowed other_run=allowed repo=allowed`
- REGRESSION. "A build run before the build-role agents register parks the sub-ticket".
  WHEN the parent's `t0030-throw.mjs` command on `factory/workflows/build.js`, with the replies JSON as written there.
  THEN it prints exactly `run finish run-0009-x --status-override KILLED`, then `ticket park T-0001.1 --reason "agent call failed: implementer: agent type 'factory-implementer' not found" --outputs run-0009-x`.
- REGRESSION. "A workflow in a session with no factory agents stops at its first store command".
  WHEN `(for w in intake build; do node ${TMPDIR:-/tmp}/t0030-throw.mjs factory/workflows/$w.js '{}' all; done)`
  THEN it prints exactly `stopped: agent type 'factory-clerk' not found after 1 agent call(s)` twice, one per line.
- NEW, intermediate check for A4: run start records whether the run was inline.
  WHEN the parent's command for "The intake workflow gives triage the effort the instance sets and records it", run unchanged.
  THEN it prints exactly `role effort=none clerk effort=low meta_effort=absent inline=true`, then `role effort=none clerk effort=low meta_effort=absent inline=false`. Effort is ST-2's job, so it is still absent at this point. Today both lines end `inline=absent`.
- REGRESSION. The gate suite passes, with the one test change below.

Interim tests: none
Tests to change:
- `tests/factory/test_instance.py::test_init_creates_the_instance_at_the_git_top_level`: `len(agents) == 6` becomes `== 9`, because A adds three `agents/factory-*.md`. The rest of the test stays unchanged (the parent's Tests to change).

Protected paths:
- harness: `agents/factory-implementer.md`, `agents/factory-reviewer.md` and `agents/factory-verifier.md` (new); `agents/factory-triage.md`, `agents/factory-spec-writer.md`, `agents/factory-spec-critic.md` and `agents/factory-planner.md` (bodies replaced, agent prompts changed under this approval); `factory/cli.py`; `factory/workflows/intake.js`; `factory/workflows/build.js`.
- The existing test `tests/factory/test_instance.py`.

Out of scope:
- The `effort` map, its validation and the `effort` argument (ST-2).
- `factory/compose.py` (ST-3).
- Every document: `docs/`, `dev/`, `README.md` and `.factory/README.md` (ST-4). README stays stale about inline mode and `--inline` until ST-4, as the parent's seams intend.
- `agents/factory-stub.md` and `agents/factory-clerk.md`.
- `factory/prompts/**` and `docs/prompts/**`.

---

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v2) names four parts, A to D, and says D lands last. I keep those seams. One change from the spec's "A, B and C are independent": A and B both edit `run_start` in `factory/cli.py` and `runRole` in both workflow scripts (`factory/workflows/intake.js`, `factory/workflows/build.js`). Run in parallel, they would collide, so B waits for A. C edits only `factory/compose.py` and runs alongside them.

Grounding (checked on `main` at `d226a4d`, with the spec's GIVEN block written to this run's scratch directory and every command run under a throwaway HOME):
- `ls agents/` gives six files, with no implementer, reviewer or verifier.
- The four REGRESSION scenarios already print what they expect on `main`: the build park (`run finish run-0009-x --status-override KILLED`, then the `agent call failed: implementer` park), `stopped: agent type 'factory-clerk' not found after 1 agent call(s)` twice, and the rewritten-spec critic (`removed=0 keep100=1 other100=1 prior_findings=1`).
- Three NEW scenarios print the "today" lines in `verification.md`: the agent-type scenario (`factory-implementer=missing`, and the same for reviewer and verifier), the small-diff critic (`removed=0 added=0 keep100=2 prior_findings=1`), and the intake effort scenario (`... meta_effort=absent inline=absent`, twice).
- The only existing test the spec changes is `tests/factory/test_instance.py:89` (`assert len(agents) == 6`). Two existing round-2 critic tests check the input text: `tests/factory/test_p0_cli.py:170` asserts `"v1 body" in cinp`, and `tests/factory/test_shepherd.py:123-124` asserts the sources and `## Responses`. Neither should break under C. In the first test, v1 is 22 bytes, so the diff is larger and v1 stays whole. In both, the sources stay unchanged and `## Responses` comes from the current version.

All commands below run from `~/dev/spec-factory`, inside the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Every scenario that names a `t0030-*` file needs the spec's GIVEN block (scenario "Every agent type the workflows ask for has a definition") run once first. "Gate suite" means the instance's two gate commands, `git diff --check main...HEAD` and `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, the second after `uv sync --frozen`.

---

## Parent spec (v2, pinned)

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
sed 's/^|//' > $T30/spec.md <<'SPEC'
|=== proposal.md
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
|=== design.md
## Proposed change
CHANGE-MARK do the thing.
## Tests to change
TESTS-MARK none
|=== specs/demo/spec.md
## ADDED Requirements
### Requirement: The thing
SCENARIO-MARK the thing SHALL happen.
|=== verification.md
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

## Human ruling

# Ruling on T-0030.1 (BLOCKED from implementer), operator, 2026-10-07

Operator's choice in the Green session: "Retry once as is".

The previous run (run-0312) was refused by Claude Code's auto-mode permission check ("Code from External") before it changed anything, and stopped correctly. Nothing about the spec, base or branch is wrong.

Build the sub-ticket as specified, from the start of the process. If the permission check refuses a command again, do not try to reach the same result through another tool or another form of the command. Stop, change nothing further, and report BLOCKED with the refused command and the reason it gave. The operator will then add a permission rule.
