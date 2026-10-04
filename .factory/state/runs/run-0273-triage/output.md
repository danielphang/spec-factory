Type: feature

Title: Token cost: a registered agent definition for each of the seven roles (the reviewer and verifier unable to edit what they check), each role's input cut to the spec sections it uses, and an optional per-role effort setting (#24 parts A and C, folding in #22)

Summary:
Most of a factory run's tokens go to overhead rather than work. A role run as a general-purpose agent (`inlineRoles: true`) re-sends about 44k tokens of starting context on every API call. A typed `factory-*` agent with only its declared tools re-sends about 30k. The operator wants three changes, and has approved the spec gate in advance:
(A) give every role (triage, spec writer, critic, planner, implementer, reviewer, verifier) its own `factory-*` agent definition, and have `factory init` copy them into the instance. The reviewer and verifier get tool limits: they may write only their run's scratch directory and output file, never the worktree they are checking. `inlineRoles` stays as a supported fallback.
(C) the composed `input.md` gives each role only the spec sections it uses, and the per-role input size is measured before and after from the store's `input.md` files.
(#22) an optional per-role `effort:` map beside `models:` in `instance.yaml`. Each role's agent call receives its effort value, and the run's `meta.yaml` records it.
The spec must also say what happens when a workflow runs without `inlineRoles` before the runner sessions for spec-factory and Nanobot have restarted and registered the new agents. Restarting those sessions is an operator step.

Evidence:
- The request's measurement (2026-10-03, 149 role runs and 741 clerk calls from both stores): fixed start-up context is 47% of the role agents' 247M context tokens, at 44.4k per call inline and 30.2k typed. The composed `input.md` is 11.5% overall: 4% of a triage run and 23% of a reviewer run. Spec Evidence is the largest input section (14–16 KB per spec), and a round-2 critic receives both full spec versions. 21 of 118 role runs ran typed.
- Nanobot v3.5 Driver comment (2026-10-04): `build.js` without `inlineRoles` fails at the first implementer call with "agent type 'factory-implementer' not found" (workflow wf_345169c6-fca). Both instances run the build with `inlineRoles: true`, so the reviewer and verifier run with no tool limits today.
- Checked on this checkout (`main` at `c2750bf`):
  - `agents/` holds only `factory-clerk.md`, `factory-planner.md`, `factory-spec-critic.md`, `factory-spec-writer.md`, `factory-stub.md` and `factory-triage.md`. There is no implementer, reviewer or verifier definition.
  - `factory/cli.py` lines 983–1005: `init` copies `agents/` into `<repo>/.claude/agents` and prints "restart the session so the agents register".
  - `factory/workflows/intake.js:97` and `build.js:88`: role calls pass `agentType` and `model` but no `effort`. Only the clerk and stub calls set an effort, fixed at `'low'`.
  - `factory/instance.template.yaml:37–46` has a `models:` map and no `effort:` map.
  - `factory/cost.py` takes transcript directories and has no `--breakdown` option.
  - `.factory/README.md` "Running" says this repo adds no `.claude/agents/`, so roles run inline. That page must change with part A.
- Operator scope (2026-10-04): "i really want the efficiency stuff done". Scope is parts A and C only. Part B, which would remove or batch the clerk (the low-cost agent started only to run one `bin/factory` command), stays deferred. The clerk stays on Haiku.
- Operator decisions recorded in the request's comments: the dispatcher stays the Workflow tool (no Agent SDK driver). Saving tokens never removes a check. No role loses an input its prompt names as required.

Assumptions (inferences, labelled as such):
- Duplicate search: no open or recently closed ticket covers this. #22 is "not in intake" and is folded in here at the operator's direction. #4 (T-0004, closed) explains why the restart is needed and does not duplicate this. T-0028 (a small-change lane) is a different efficiency change.
- "Seven roles" means triage, spec writer, critic, planner, implementer, reviewer and verifier. The clerk and stub definitions already exist and stay as they are. Retro has a `models:` entry but no role yet (#42), so it is not one of the seven.
- The reviewer and verifier fence can only be as strong as the agent `tools:` list allows. Both roles need Bash to run the code they judge, and they need Write for their output file. A tools list alone therefore cannot stop a write into the worktree. The spec should say exactly what the fence enforces and what it does not, and should not claim more. Whether a stronger fence is wanted is #37's question (sandbox or a separate user).
- For part C, the section lists in the request are the requester's proposal. The rule that binds is the operator's: no role loses an input its prompt names as required. The spec writer should check each role prompt in `docs/design.md` against the sections the role would stop receiving. The proposal drops Evidence and Responses for the planner, implementer, reviewer and verifier, and gives a round-2 critic a diff between spec versions.
- Effort values not set in the `effort:` map keep today's behaviour: role calls get no effort argument, and the clerk and stub stay at `'low'`.
- The `/usage` recording and the re-measurement "after each part lands" from the issue are operator steps after merge, not acceptance the build can run. The runnable measurement is the per-role `input.md` size, before and after, taken from the store, plus whatever `factory/cost.py --breakdown` adds.
- Part A changes harness-protected paths (`agents/**`, `factory/**`, including the workflow scripts that pass `effort`). The spec's Risk section must declare them. Routing must not change.
- Not in scope, though raised in the same comment thread: on an `agent()` failure, the build workflow leaves an orphan in-flight run and returns without parking. The commenter assigns this to #33's silent-exit fix. It is not part of the operator's A + C + #22 scope.
- Suggested priority (the human decides): p1, given the operator's "i really want the efficiency stuff done" and that the implementer, reviewer and verifier currently run without their tool limits.

Reason:
ACCEPT. The intent is clear, the operator has set the scope and listed the constraints, and the spec gate is approved in advance. The open points can be settled by the spec writer from the prompts and the code: how far the reviewer and verifier fence can be enforced, and which sections each role needs. Neither needs a product call.

Out-of-scope observations:
- `.factory/README.md` and the top-level `README.md` describe inline running. With part A, both must change in the same ticket, following the README's "Maintaining this page" section.

STATUS: ACCEPT
CONFIDENCE: high, with one reservation. Scope and constraints come from the operator, and the gaps they name (the missing agent files, effort passed only to the clerk and stub, no `--breakdown`) were checked against the code. How strong the reviewer and verifier fence can be with a tools list alone is still for the spec to settle.
ESCALATIONS: none
