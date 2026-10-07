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
