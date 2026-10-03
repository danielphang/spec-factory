---
title: P0 plan: .claude/agents/ created mid-session is not visible to that session (Agent tool and Workflow agentType)
labels: p0, operational
---
**Where:** `plans/P0-intake-skeleton.md` Part A ("`.claude/agents/factory-*.md` for Triage, Spec writer, Spec critic, Planner, clerk, stub") and its Risk list ("Workflow under `claude -p` unverified").

**What happened (2026-10-01):** the agent files were written in the session that then ran P0-2..P0-5. `Agent(subagent_type: "factory-clerk")` returned *Agent type 'factory-clerk' not found*, and the Workflow `agentType` resolves from the same registry. Claude Code docs: the agents watcher covers only directories that existed at session start. The run proceeded with an `inlineRoles` fallback (general-purpose agents reading `runs/<id>/system-prompt.txt`), which keeps model-per-role but drops the per-role `tools:` fences the spec's R6 relies on.

**Proposed fix:** add to P0 §Risk: "create `.claude/agents/` (even empty) before starting the session that will run P0; a session started before the directory existed cannot address the role agents." Add P0 acceptance: a fresh session lists the six `factory-*` agents before P0-2 runs.
