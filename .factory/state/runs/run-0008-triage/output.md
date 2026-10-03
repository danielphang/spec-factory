Type: bug (a defect in the plan document `plans/P0-intake-skeleton.md`: following it as written breaks the run)

Title: P0 plan does not warn that a session started before `.claude/agents/` existed cannot address the factory-* role agents, and does not check for them before P0-2

Summary:
The P0 plan's Part A has the operator write `.claude/agents/factory-*.md` for six roles (Triage, Spec writer, Spec critic, Planner, clerk, stub). The plan does not say that Claude Code only registers agent files from directories that existed when the session started. On 2026-10-01 the files were written in the same session that then ran P0-2..P0-5, so `Agent(subagent_type: "factory-clerk")` failed with "Agent type 'factory-clerk' not found". Workflow `agentType` uses the same registry. The run fell back to `inlineRoles`: general-purpose agents that read `runs/<id>/system-prompt.txt`. That fallback keeps the model for each role but drops the per-role `tools:` limits that spec R6 relies on. The requester wants the P0 plan to (a) state this as a Risk with the step that avoids it, and (b) add an acceptance check that a fresh session can see the six factory-* agents before P0-2 runs.

Evidence:
- Request: "`Agent(subagent_type: "factory-clerk")` returned *Agent type 'factory-clerk' not found*, and the Workflow `agentType` resolves from the same registry."
- I checked the Claude Code docs (https://code.claude.com/docs/en/sub-agents, fetched in this run). They confirm the cause: "The watcher covers only directories that existed when the session started, so after creating a scope's first agent file in a new `agents` directory, restart to load it." The same page says `.claude/agents/` inside directories added with `--add-dir` / `/add-dir` is not watched at all, so changes there also need a restart.
- The plan text matches the request. `plans/P0-intake-skeleton.md:27` is Part A and lists the six agent files. The Risk section (lines 63-68) says nothing about agent registration or session start. Line 66 is "Workflow under `claude -p` unverified; fallback is an interactive session (same script)." The plan's acceptance items P0-1..P0-8 contain no check that the agents are registered.
- What the reference harness does today (read only, `~/dev/nanobot-upstream`):
  - `factory/workflows/intake.js` lines 24-27 contain this comment: "inlineRoles: the .claude/agents/factory-* definitions are not registered in this session (the directory did not exist at session start), so every role runs as general-purpose ... Model per role is unchanged; tool fences are not."
  - Lines 49, 83 and 89 switch `agentType` to `'general-purpose'` when `INLINE` is set.
  - `git log -S inlineRoles -- factory/workflows/intake.js` returns only `0f2e29136`, the P0 skeleton commit, so the fallback shipped with P0.
  - `.claude/agents/` there holds exactly six files: factory-clerk, factory-planner, factory-spec-critic, factory-spec-writer, factory-stub, factory-triage.
  - The harness has a workaround (the fallback) but no fix. Nothing in it makes the agents register.
- Spec R6 (`specs/build-harness.md:118`, also line 296 item 4) makes the role definition's `tools:` the tool fence. The `inlineRoles` fallback bypasses it, which is why this matters.
- This run shows the same thing. `~/dev/spec-factory/.claude` does not exist (`ls` → "No such file or directory"). The intake here runs with `inlineRoles: true` (`intake/README.md:47`), and this Triage agent is a general-purpose agent reading `system-prompt.txt`.
- Duplicate search: I read requests T-0001..T-0007 (`intake/state/requests/`), the ticket files `intake/state/tickets/T-0001..T-0007.yaml`, and the titles in `issues/01..07`. No other ticket covers agent registration or `.claude/agents/`. This request is T-0004 (`issues/04_p0_agents_dir.md`; `diff` against `requests/T-0004.md` shows the two are identical).

Assumptions:
- (inference) The change is limited to `plans/P0-intake-skeleton.md`: its Risk section and its Acceptance list. The request does not ask to change `docs/spec-factory.md`, `specs/build-harness.md` or `prompts/`. The full BH-4 build in the spec creates the same `.claude/agents/` directory and has the same exposure, but extending the fix there is not asked for.
- (inference) The requester's wording ("create `.claude/agents/` (even empty) before starting the session") is a suggestion. The requirement is the evidence: the session that runs P0 must be able to address the six factory-* agents, and the operator must be able to check that before P0-2. One caveat from the docs: creating the directory early is not enough if the checkout is attached with `--add-dir`, because `.claude/agents/` there is never watched. A spec writer may want the Risk text to say "start the session in the checkout, or restart after writing the agent files", but that is my inference and not something the requester stated.
- (inference) "Six" means the six files listed in Part A (Triage, Spec writer, Spec critic, Planner, clerk, stub). That matches the six files in the reference harness.
- (inference) The new acceptance check is an operator-observable behaviour in a fresh session on the green checkout, matching how the plan's existing P0-1..P0-8 are phrased. It is not a shell command runnable from `~/dev/spec-factory`. A spec for this ticket can still give grep-able acceptance against the plan text itself, such as the Risk line and the new P0 item.
- Suggested priority (suggestion only; priority is a human call): medium. P0 has already run using the fallback. But the next session that follows the plan, including the Nanobot rerun or the full build, hits the same failure or silently runs without R6's tool limits.

Reason: n/a (ACCEPT)

Out-of-scope observations:
- The reference agent definitions give Triage, Spec writer, Spec critic and Planner `Write` (`.claude/agents/factory-{triage,spec-writer,spec-critic,planner}.md`, line 5: `tools: Read, Grep, Glob, Bash, Write`). Spec R6 says "checkers and read-only authors Read/Grep/Glob/Bash, no Edit/Write", and spec item 54 expects `factory-critic.md` (the spec's name) to contain no `Write`. This may be deliberate (roles write their output file), but the plan and the spec disagree here. I did not change anything.
- `specs/build-harness.md` (layout lines 136-139, BH-4) creates `.claude/agents/` with no warning about registration at session start. This is the same trap, outside the P0 plan.

STATUS: ACCEPT
CONFIDENCE: high. The failure mechanism is confirmed in the Claude Code docs, the fallback and its comment are in the reference harness at the cited lines, the plan's Risk and Acceptance sections lack the item, and no duplicate exists among T-0001..T-0007.
ESCALATIONS: none
