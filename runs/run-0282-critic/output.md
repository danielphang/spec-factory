Round 1 review of the v1 spec (role agents, checker fence, trimmed inputs, per-role effort).

What I checked myself, on `main` at `c2750bf` from `~/dev/spec-factory`, with a throwaway HOME and the fixtures written to this run's scratch directory:
- Cited paths and lines: `ls agents/` lists the six files the spec names and no implementer, reviewer or verifier; `AGENT_NAME` is used at `factory/workflows/build.js:88` and `intake.js:97`, and the catch below each records the run KILLED and parks with `agent call failed: <role>: <error>`; `init_cmd` copies only missing `agents/factory-*.md` at `factory/cli.py:983-987`; `compose.py` adds the whole pinned spec at lines 160 (planner), 188 (implementer), 203 and 206 (verifier, parent-close) and the previous version whole at 153; `tests/factory/test_instance.py:89` asserts `len(agents) == 6`; `factory/instance.template.yaml` has `models:` (reviewer `fable`, implementer and verifier `opus`) and no effort map; `run_start` writes `model` to `meta.yaml` (cli.py:216) and no effort; README line 371 carries the "Add `inlineRoles: true` on every target for now" passage and line 487 the "Per-role effort settings" bullet; `.factory/README.md:65-66` says "this repo adds no `.claude/agents/`". All as the spec says.
- The four existing definitions carry a prompt copy after the `system-prompt.txt` line; `diff -q` against `factory/prompts/{triage,spec_writer,critic}.md` reports each differs, and the planner diff shows `parent criterion` against `parent scenario`.
- Acceptance commands run today: the agent-types scenario prints the three `missing` lines; points/copy prints `copy=1` four times and `points= copy=` three times; the fence script prints `missing` three times; both REGRESSION park scenarios print the stated lines; the compose-marks scenario prints `evidence=1 responses=1 kept=9 full=0` five times; the round-2 small case prints `removed=0 added=0 keep100=2 prior_findings=1` and the rewrite case its REGRESSION line; the e2e effort scenario prints `role effort=none clerk effort=low meta_effort=absent inline=absent` twice; the effort-refusal scenario prints `exit=0 named=0 runs=1` twice; the build-effort, docs and README scenarios print the stated "today" values; the init scenario prints the six-file list, an empty line and `local`. Every NEW item fails today for the reason the spec gives, and the fixtures run as written.
- Claude Code docs (code.claude.com/docs/en/sub-agents.md, fetched today): subagent frontmatter supports `hooks` scoped to the subagent, `tools`, `model` and `effort`; a `disallowedTools` entry with a specifier removes the whole tool; the watcher covers only directories that existed at session start. The spec's reading is correct.
- Existing tests that read composed inputs (`test_p0_cli.py:170`, `test_shepherd.py:124,202-231,454-459`) assert strings outside the Evidence and Responses sections of their fixture specs, or that a diff would still carry as a `-` line, so "Tests to change" naming only `test_instance.py` is right.
- The four downstream prompts mention "Responses" only for the implementer's own PR-description responses, not the spec's section, so Problem item 2 holds.

Findings

[SHOULD-FIX] 1 Evidence, "Token overhead" paragraph
Problem: The paragraph counts "149 role runs" and then "21 of 118 role runs ran with a registered definition" without saying why the base changed, and Problem item 1's "both repositories run every role inline" sits beside those 21 registered runs and the four intake definitions the Nanobot fork has installed in its `.claude/agents/`.
Evidence: Read the paragraph; `ls ~/dev/nanobot-upstream/.claude/agents/` shows the four intake definitions plus clerk and stub.
Suggested fix: Say what the 118 are (for example, the runs whose transcript names an agent type) and make Problem item 1 say that both repositories dispatch with `inlineRoles: true` today, which is what README tells them to do.

[SHOULD-FIX] 4 Decisions, the `effort:` map bullet, and Risk
Problem: `run start` accepts any of the five levels for any role, but the docs say the levels available "depend on the model", so a level the role's model lacks passes validation and fails only at the agent call, and the spec does not say what happens then.
Evidence: sub-agents.md frontmatter table, `effort` row: "Options: low, medium, high, xhigh, max; available levels depend on the model". I did not verify how a Workflow `agent()` call reports an unavailable level.
Suggested fix: Add a Risk line that a level the model does not offer is caught at the call, with the `agent call failed` park as the expected result and the operator probe as the way to confirm, and have README's `effort:` paragraph say so.

[NIT] 6 Operator steps, step 3
Problem: The probe calls `factory-reviewer` with no run directory, but the new body tells the agent to read `system-prompt.txt` in the run directory that holds its input file, so the agent's first report may be that it found no run, not a blocked write.
Evidence: Design A.3 body text against step 3's prompt.
Suggested fix: Say the pass condition is the file's absence after the agent returns, whatever the agent says about its missing run.

[NIT] 4 Design A.1
Problem: The implementer's `tools` drops MultiEdit and NotebookEdit without a Decision, while the fence scenario asserts `edit_tools=Edit` for it.
Evidence: Design A.1 tool list; fence scenario's third THEN line.
Suggested fix: One sentence under Decisions saying the implementer keeps only Write and Edit and why, or add the two tools to its list and the scenario's expected line.

[NIT] 5 Risk
Problem: Open ticket T-0022's plan changes `run_start` in `factory/cli.py` and `runRole` in `factory/workflows/build.js`, the same functions parts A and B change, so whichever lands second rebases onto the other; not a design conflict.
Evidence: `.factory/state/plans/T-0022.md` lines 25-26, 44-45.
Suggested fix: Note it under Risk so the planner orders the parts with that in mind.

Prior findings: none (round 1).

Out-of-scope observations
- The docs name `permissions.deny` with `Bash(<pattern>)` as the way to block specific shell commands while keeping Bash. That is per-instance settings, not the agent definition, and belongs with issue #37's question.

STATUS: APPROVE
CONFIDENCE: high, every cited path and twelve acceptance commands checked on this checkout and the docs claims re-read today; the one unverified point (hooks under a Workflow agent call) is declared under Risk with an operator probe.
ESCALATIONS: none
