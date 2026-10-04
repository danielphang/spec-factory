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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0160-triage/output.md`

## Request (raw, with any answers appended)

---
title: "P0: role test runs can write live state outside the worktree; planner field bullets silently drop dependencies"
labels: "harness, p0"
---
**Problem 1 (safety):** an agent's test run overwrote live production state. On 2026-10-04, during the Nanobot v3.5 build of T-0002 (SPEC-20, the policy store), T-0002.1's implementer (run-0080) ran its new tests before they were isolated. The new store module defaulted to the real `~/.nanobot/policies.json`, so the tests overwrote the live bot's `policies.json` and its `.bak`. The live per-chat permissions were lost until the operator restored them. Two causes:
- **Only the gate isolates HOME.** Gate commands run under a throwaway `HOME`, but the roles' own test runs use the instance's plain test command, so a test that resolves a path from `HOME` before a fixture redirects it writes the real home.
- **Protected paths are not enforced.** `credentials: ~/.nanobot/**` is declared, but nothing enforces it while a role runs. Claude Code's `permissions.deny` cannot catch this either: it does not apply to "arbitrary subprocesses that read or write files indirectly, like a Python or Node script" (code.claude.com/docs/en/permissions.md).

**Problem 2 (planner parse):** a planner that writes its fields as Markdown bullets loses them silently. The T-0002 plan wrote `- Depends on: T-0002.1` and `- Parallel-safe: …`. `subtickets.FIELD_RE` does not match a line starting with `- `, so all eight sub-tickets came out with `depends_on: []` and `parallel_safe: false`. They were dispatched without their order, and 2 to 8 BLOCKED, about 3M tokens. Reproduced with the runtime's parser on `plans/T-0002.md`. The same class of fault as #13 and spec-factory T-0014 (`ID / Title:` head line).

**Proposed change:**
- A. **Preamble, a hard rule:** every test, script or prototype a role runs, runs with `HOME` set to a fresh temporary directory, and with the target's state paths (the instance's `credentials` class) unreachable. Never run anything that may write outside your worktree or run scratch directory without it.
- B. **Compose:** the role's input names the instance's test command already wrapped with a throwaway `HOME`, taken from the gate's environment, so the easiest command to copy is the safe one. A target whose test command cannot run under a throwaway `HOME` declares so in `instance.yaml`, and the role is told.
- C. **Parser:** field lines may start with a list bullet (`- `, `* `). Every sub-ticket must carry a `Depends on:` line, `none` included. A plan with a sub-ticket that has no `Depends on:` line is refused with the sub-ticket named, never defaulted to "no dependencies".
- D. **Planner prompt:** the OUTPUT example shows the field lines exactly as the parser reads them.

**Outside this ticket, the operator's decision:** OS-enforced write denial through Claude Code's sandbox (`sandbox.enabled`, `sandbox.filesystem.denyWrite: ["~/.nanobot"]`, code.claude.com/docs/en/sandboxing.md) in each runner session's project settings. Whether agents launched by a workflow inherit the session's sandbox is undocumented and must be tested with a canary write before relying on it.
