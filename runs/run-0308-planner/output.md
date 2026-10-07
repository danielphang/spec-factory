# Plan for T-0030: registered role agents, trimmed role inputs, per-role effort

The approved spec (v2) names four parts, A to D, and says D lands last. I keep those seams. One change from the spec's "A, B and C are independent": A and B both edit `run_start` in `factory/cli.py` and `runRole` in both workflow scripts (`factory/workflows/intake.js`, `factory/workflows/build.js`). Run in parallel, they would collide, so B waits for A. C edits only `factory/compose.py` and runs alongside them.

Grounding (checked on `main` at `d226a4d`, with the spec's GIVEN block written to this run's scratch directory and every command run under a throwaway HOME):
- `ls agents/` gives six files, with no implementer, reviewer or verifier.
- The four REGRESSION scenarios already print what they expect on `main`: the build park (`run finish run-0009-x --status-override KILLED`, then the `agent call failed: implementer` park), `stopped: agent type 'factory-clerk' not found after 1 agent call(s)` twice, and the rewritten-spec critic (`removed=0 keep100=1 other100=1 prior_findings=1`).
- Three NEW scenarios print the "today" lines in `verification.md`: the agent-type scenario (`factory-implementer=missing`, and the same for reviewer and verifier), the small-diff critic (`removed=0 added=0 keep100=2 prior_findings=1`), and the intake effort scenario (`... meta_effort=absent inline=absent`, twice).
- The only existing test the spec changes is `tests/factory/test_instance.py:89` (`assert len(agents) == 6`). Two existing round-2 critic tests check the input text: `tests/factory/test_p0_cli.py:170` asserts `"v1 body" in cinp`, and `tests/factory/test_shepherd.py:123-124` asserts the sources and `## Responses`. Neither should break under C. In the first test, v1 is 22 bytes, so the diff is larger and v1 stays whole. In both, the sources stay unchanged and `## Responses` comes from the current version.

All commands below run from `~/dev/spec-factory`, inside the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Every scenario that names a `t0030-*` file needs the spec's GIVEN block (scenario "Every agent type the workflows ask for has a definition") run once first. "Gate suite" means the instance's two gate commands, `git diff --check main...HEAD` and `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, the second after `uv sync --frozen`.

---

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

### ST-2 / Effort per role: the instance's `effort:` map reaches the agent call and the run record
Depends on: ST-1
Parallel-safe: no (it edits the same `run_start` in `factory/cli.py` and the same `runRole` in both workflow scripts as ST-1, so it runs after it)

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part B, items B1 to B4.
- B1: `run_start` validates `cfg.get("effort")`. It refuses with exit 2 before reserving a run id, and the refusal names the bad entry.
- B2: `effort` is written to `meta.yaml` and to the JSON output.
- B3: the real role call in `runRole` in both workflow scripts passes `effort: start.effort` only when that is set. The store-command agent (the clerk) and the stub calls keep `'low'`.
- B4: a commented example in `factory/instance.template.yaml`. No live key is added.

Acceptance:
- NEW. "The intake workflow gives triage the effort the instance sets and records it".
  WHEN the parent's command as written (a scratch instance per case, `effort: {triage: high}` with inline mode, then no map with registered mode, then `t0030-e2e.mjs`, then a read of `meta.yaml`).
  THEN it prints exactly `role effort=high clerk effort=low meta_effort=high inline=true`, then `role effort=none clerk effort=low meta_effort=null inline=false`.
- NEW. "The build workflow passes the run's effort to each build role's agent call".
  WHEN `(node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/build.js "$(sed 's/"run finish"/"run start": {"out": {"ok": true, "run_id": "run-0009-x", "worktree": "\/w", "effort": "max"}}, "run finish"/' ${TMPDIR:-/tmp}/t0030-build.json)")`
  THEN it prints exactly `factory-planner effort=max`, `factory-implementer effort=max`, `factory-reviewer effort=max`, `factory-verifier effort=max`, `clerk effort=low`, one per line.
- NEW. "An effort map with an unknown level or role is refused".
  WHEN the parent's command as written (`triage: extreme`, then `triag: high`, each in a copy of `tests/factory/fixtures/instance`).
  THEN it prints exactly `exit=2 named=1 runs=0`, twice, one per line.
- REGRESSION, because ST-1 made each of these true:
  - "Every agent type the workflows ask for has a definition": the seven `=defined` lines.
  - "A build run before the build-role agents register parks the sub-ticket": the two lines given in ST-1.
  - "A workflow in a session with no factory agents stops at its first store command": the `stopped: ...` line twice.
- REGRESSION. The gate suite passes.

Interim tests: none
Tests to change: none
Protected paths:
- harness: `factory/cli.py`, `factory/instance.template.yaml`, `factory/workflows/intake.js`, `factory/workflows/build.js`.

Out of scope:
- Agent definitions and the fence (ST-1).
- `factory/compose.py` (ST-3).
- Documents, including README's "Per-role effort settings" bullet (ST-4).
- The clerk's model and its fixed `'low'` effort.
- An `effort` key in any agent definition.
- Any live `effort:` key in a shipped `instance.yaml`.

---

### ST-3 / Each role's input cut to the spec sections it uses, and a round-2 critic diff
Depends on: none
Parallel-safe: yes

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part C, items C1 to C4, all in `factory/compose.py`.
- C1: a helper that removes the `## Evidence` and `## Responses` sections. Lines inside a fenced code block do not end a section.
- C2: the helper is used for the planner's "Approved spec" (`factory/compose.py:199` on `main`), the implementer's and checkers' "Parent spec" (lines 238 and 256), and the parent-close verifier's spec (line 253). Each heading keeps its current words, including "verify every scenario on main". Each heading adds that Evidence and Responses are left out, and gives the full spec's absolute path. `input_sources` stays unchanged, and `subticket.md` is not cut.
- C3: a round-2 critic gets a `difflib.unified_diff` with 3 lines of context, in place of the previous version (line 192), when the diff is smaller in bytes. Otherwise it gets the version whole. The heading names which one the input holds.
- C4: every other input stays unchanged.

Line numbers are from `main` at `d226a4d`. The spec's Root cause cites lines on `c2750bf`, which have since moved.

Acceptance:
- NEW. "Downstream roles get every spec section but Evidence and Responses, and the full spec's path".
  WHEN the parent's command as written (`. ${TMPDIR:-/tmp}/t0030-spec.sh`, then `marks` on composed planner, implementer, reviewer, verifier and parent-close inputs).
  THEN it prints exactly `planner: evidence=0 responses=0 kept=9 full=1`, `implementer: evidence=0 responses=0 kept=9 full=1`, `reviewer: evidence=0 responses=0 kept=9 full=1`, `verifier: evidence=0 responses=0 kept=9 full=1`, `parent-close: evidence=0 responses=0 kept=9 full=1`, one per line.
- NEW. "A round-2 critic receives a small revision as a diff".
  WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh small) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) added=$(grep -cx -- '+NEW-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
  THEN it prints exactly `removed=1 added=1 keep100=1 prior_findings=1`.
- REGRESSION. "A round-2 critic receives a rewritten spec's previous version whole".
  WHEN `(I=$(. ${TMPDIR:-/tmp}/t0030-critic.sh rewrite) && echo "removed=$(grep -cx -- '-OLD-ONLY' $I) keep100=$(grep -cx 'keep line 100' $I) other100=$(grep -cx 'other line 100' $I) prior_findings=$(grep -c 'Findings: one.' $I)")`
  THEN it prints exactly `removed=0 keep100=1 other100=1 prior_findings=1`. This passes on `main` today.
- REGRESSION. The gate suite passes, including `tests/factory/test_p0_cli.py` and `tests/factory/test_shepherd.py`, which check round-2 critic inputs and `input_sources`.

Interim tests: none
Tests to change: none
Protected paths:
- harness: `factory/compose.py`.

Out of scope:
- The triage and spec writer inputs, and the critic's current spec.
- What spec writers put in Evidence (issue #23).
- Agent definitions, effort and documents (ST-1, ST-2, ST-4).
- `factory/cost.py`.

---

### ST-4 / Documents: design doc, build spec, changelog, README and the instance page
Depends on: ST-1, ST-2, ST-3
Parallel-safe: yes

Parent: /Users/dphang/dev/spec-factory/.factory/store/specs/T-0030/v2.md (T-0030). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: part D, items D1 to D5.
- D1: the "Receives" column of the routing table in `docs/design.md`, in five rows. The round-2 critic row says the previous version arrives as a diff when that is smaller. Four rows say the spec arrives without Evidence and Responses.
- D2: the critic's round-2 input in `dev/build-harness.spec.md`, in the sentence that contains "round ≥ 2: prior findings".
- D3: one entry in `docs/changelog.md`, numbered next with no gap. The last entry on `main` today is 57; re-derive the number at build time. The entry names the seven definitions with `factory-implementer` among them, the fence and its limit, the `agent call failed` park, `inlineRoles` as the fallback, the `effort` map, and the trimmed inputs with the round-2 diff.
- D4: `README.md`, following its "Maintaining this page" section:
  - "Starting a run": roles run as their registered agents, inline mode is the fallback, what happens when the definitions are missing, and how to recover.
  - The checker fence and its limit, including the `python3` and workspace-trust requirements.
  - The `effort:` map, and removal of the "Per-role effort settings" bullet.
  - `run start --inline`.
  - Re-derived figures, this ticket and issues #24 and #22 under "Related work and history", and a new status date.
- D5: `.factory/README.md` "Running": dispatch without `inlineRoles`, and drop "this repo adds no `.claude/agents/`".

Acceptance:
- NEW. "The changelog records registered agents, trimmed inputs and effort as its last entry".
  WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e factory-implementer -e Evidence -e effort -e diff -e inlineRoles | sort -u | grep -c .)`
  THEN it prints `CONTIGUOUS`, then `5`.
- NEW. "The routing table and build spec describe the trimmed spec and the diff, and no prompt changes".
  WHEN the parent's command as written (`critic_diff`, `trimmed_rows`, `build_spec`, `prompts` from `git diff --name-only main...HEAD -- docs/prompts factory/prompts`).
  THEN it prints exactly `critic_diff=1 trimmed_rows=4 build_spec=1 prompts=0`.
- NEW. "README and the instance page describe registered roles, the park and effort".
  WHEN the parent's command as written.
  THEN it prints exactly `inline_everywhere=0 parks=1 effort_map=1 effort_not_built=0 instance_inline=0`.
- REGRESSION. "The role-agents change adds no whitespace errors".
  WHEN `(git diff --check main...HEAD; echo "exit=$?")`
  THEN it prints only `exit=0`.
- REGRESSION. Every scenario of ST-1, ST-2 and ST-3 still prints its THEN, and the gate suite passes. This sub-ticket changes no code, so these are a check that the documents' branch carries the merged code unchanged.

Interim tests: none
Tests to change: none
Protected paths:
- infra: `.factory/README.md`.

Out of scope:
- Every code, agent definition and test file.
- `docs/prompts/**` and `factory/prompts/**`, which must not change.
- The operator steps in the parent: installing the definitions, the fence probe, dropping `inlineRoles`, and measurement. These are for the operator after merge, not for this sub-ticket.

---

Coverage map: parent scenario → sub-ticket ID
- Every agent type the workflows ask for has a definition → ST-1 (REGRESSION in ST-2 and ST-4)
- Every role definition points at the run's prompt and copies none → ST-1
- init installs every definition and adds only missing ones → ST-1
- A checker's Write is limited to its run's output file and scratch directory → ST-1
- A build run before the build-role agents register parks the sub-ticket → ST-1 (REGRESSION in ST-2)
- A workflow in a session with no factory agents stops at its first store command → ST-1 (REGRESSION in ST-2)
- Downstream roles get every spec section but Evidence and Responses, and the full spec's path → ST-3
- A round-2 critic receives a small revision as a diff → ST-3
- A round-2 critic receives a rewritten spec's previous version whole → ST-3
- The intake workflow gives triage the effort the instance sets and records it → ST-2. Its `inline=` half becomes true in ST-1, through ST-1's intermediate check.
- The build workflow passes the run's effort to each build role's agent call → ST-2
- An effort map with an unknown level or role is refused → ST-2
- The changelog records registered agents, trimmed inputs and effort as its last entry → ST-4
- The routing table and build spec describe the trimmed spec and the diff, and no prompt changes → ST-4
- README and the instance page describe registered roles, the park and effort → ST-4
- The role-agents change adds no whitespace errors → ST-4. Every sub-ticket also runs it as part of its gate suite.

Out-of-scope observations:
- The spec's Root cause cites `factory/compose.py` lines 153, 160, 188, 203 and 206, read on `c2750bf`. On `main` at `d226a4d`, the same `add()` calls are at lines 192, 199, 238, 253 and 256. This does not change what is asked.

STATUS: PLANNED
CONFIDENCE: high. The seams come from the approved spec, and the only change to its ordering (ST-2 after ST-1) follows from shared files I read. The REGRESSION labels and three of the "today" outputs were run on `main` (`d226a4d`) under a throwaway HOME.
ESCALATIONS: none
