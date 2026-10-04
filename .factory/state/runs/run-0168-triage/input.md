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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0168-triage/output.md`

## Request (raw, with any answers appended)

---
title: "Tripwire on a target's live files during role runs, and a coding rule against import-time fixture escape (split from #36)"
labels: "harness"
---
**Split from #36** (P0, 2026-10-04): these two parts were added in comments on #36 after its intake had begun. #36 ships the prevention (a throwaway HOME for every role, the wrapped test command, and the planner field-line parse). This ticket adds detection, and the coding rule that would have caught the leak's mechanism.

**Problem:** nothing notices when a role run changes a target's live files. In the 2026-10-04 Nanobot incident, an implementer's tests overwrote the live `~/.nanobot/policies.json` and its `.bak`. It was caught only because that implementer happened to see a `FileExistsError`. On 2026-10-03, intake roles left 13 stray session folders in the live `~/.nanobot/sessions/`, and nobody noticed until the next day. The leak's mechanism: the conftest patched `nanobot.policy.store.policy_store_path`, but the test module had done `from nanobot.policy.store import policy_store_path` at collection, so its helpers kept the real function.

**Proposed change:**
- A. **Tripwire.** `instance.yaml` takes an optional `tripwire: {park: [paths], escalate: [paths]}` of live files, never whole directories that a running service writes. `run start` records each file's content hash, or that it is absent. `run finish` compares.
  - A changed `park` path parks the ticket. The reason names the run and the paths.
  - A changed `escalate` path queues an escalation and does not stop the run, because these files can change legitimately (a pairing approval, the operator's own edit).
  - Neither ever prints file contents. For an `escalate` path that parses as JSON, YAML or TOML, the escalation names the changed top-level key paths only, never values: these files hold live secrets.
  - A run killed before `run finish` is compared at the next store command for that ticket.
- B. **`docs/coding.md`, a new rule** in the page's format (check, principle, before/after from this incident): tests reach a patched path through the module attribute (`store.policy_store_path`), never through a name imported at collection. Code that adds a new data-directory path ships with an autouse test guard that fails any test resolving that path outside `tmp_path`.

**Nanobot's list** (the Driver's; adding it to Nanobot's `instance.yaml` is the operator's call, as a protected path):
- park: `~/.nanobot/policies.json`, `~/.nanobot/policies.json.bak`, `~/.nanobot/config.json`
- escalate: `~/.nanobot/pairing.json`, `~/.nanobot/config-localgateway.json`

**Out of scope:** OS-enforced denial (#37), and the throwaway HOME (#36).

**Gate:** pre-approved under the queue policy. The blast radius is additive: one optional instance key, a hash at run start and finish, and one new park reason. Nothing changes for an instance that declares no `tripwire:`.
