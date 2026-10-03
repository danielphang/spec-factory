## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0008-triage/output.md`

## Request (raw, with any answers appended)

---
title: P0 plan: .claude/agents/ created mid-session is not visible to that session (Agent tool and Workflow agentType)
labels: p0, operational
---
**Where:** `plans/P0-intake-skeleton.md` Part A ("`.claude/agents/factory-*.md` for Triage, Spec writer, Spec critic, Planner, clerk, stub") and its Risk list ("Workflow under `claude -p` unverified").

**What happened (2026-10-01):** the agent files were written in the session that then ran P0-2..P0-5. `Agent(subagent_type: "factory-clerk")` returned *Agent type 'factory-clerk' not found*, and the Workflow `agentType` resolves from the same registry. Claude Code docs: the agents watcher covers only directories that existed at session start. The run proceeded with an `inlineRoles` fallback (general-purpose agents reading `runs/<id>/system-prompt.txt`), which keeps model-per-role but drops the per-role `tools:` fences the spec's R6 relies on.

**Proposed fix:** add to P0 §Risk: "create `.claude/agents/` (even empty) before starting the session that will run P0; a session started before the directory existed cannot address the role agents." Add P0 acceptance: a fresh session lists the six `factory-*` agents before P0-2 runs.
