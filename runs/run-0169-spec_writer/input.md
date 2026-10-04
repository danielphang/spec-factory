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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0169-spec_writer/output.md`

## Ticket (Triage output)

Type: feature
Title: Detect a role run that changes a target's listed live files, and add a coding rule against tests that escape a patched path through an import made at collection
Summary: When a role run (one agent call the harness starts with `run start` and records with `run finish`) changes a live file outside the repository, nothing in the factory notices. The requester needs the harness to notice and act. An instance lists the live files to watch. A change to a file on the "park" list stops the ticket. A change to a file on the "escalate" list raises an escalation (a flagged item for the operator) and lets the run continue. Neither path ever shows file contents, because these files hold live secrets. A run killed before it finishes is still checked. Separately, `docs/coding.md` gains a rule in the page's own format. The rule says tests reach a patched path through the module attribute, never through a name imported when pytest collects the file. It also says code that adds a new data-directory path ships with a test guard that fails any test resolving that path outside `tmp_path`.

Evidence:
- The request's incident (2026-10-04): an implementer's tests overwrote the live `~/.nanobot/policies.json` and `policies.json.bak`. The overwrite was caught only because the run happened to see a `FileExistsError`. The Nanobot implementer's own output confirms this: `~/dev/nanobot-upstream/.factory/state/runs/run-0080-implementer/output.md` lines 91-93 name both files and quote `FileExistsError: [Errno 17] File exists: '/Users/dphang/.nanobot/policies.json'`. They also state the cause: "the test module imported `policy_store_path` by name when pytest collected it. The conftest fixture replaces the module attribute later, so the test helpers kept calling the real function."
- The request's second incident (2026-10-03): intake roles left 13 stray session folders in the live `~/.nanobot/sessions/`, and nobody noticed for a day. I did not verify this, because `~/.nanobot/` is off limits.
- No duplicate. #36 (T-0019, spec v2 approved, now at the planner) covers prevention only. Its "Out of scope" section (`.factory/state/specs/T-0019.md` lines 40-50) has no detection and no coding rule. Commit `1c5f6a7` records the split: "The tripwire and the import-patching rule ... split to their own ticket". #37 is OS-enforced denial, which the request excludes. A search of this repo for `tripwire` turns up only an unrelated metaphor in T-0011. No issue in `dev/issues.md` covers detection.
- The hooks the request relies on already exist. `run_start` is at `factory/cli.py:197`. `run_finish` is at `factory/cli.py:281`. `ticket_park`, with a free-text reason, is at `factory/cli.py:173`. The `escalation.queued` log event is at `factory/cli.py:184` and `:318`. `docs/coding.md` has numbered rules 1-5 (heading at line 86 is the last). Neither checkout's instance template has a `tripwire` key, and neither does the Nanobot instance.
- The reference harness has no fix yet. `git log --all -i --grep=tripwire` in `~/dev/nanobot-upstream` finds nothing for the factory. Nanobot's latest factory commit, `7a3c93d99`, is the throwaway HOME from #36. So there is no as-built behaviour to verify against.

Assumptions:
- (Inference) Paths in `tripwire:` are expanded against the home of the process that runs `run start` and `run finish`. That is the operator's real home, not the throwaway HOME that #36 gives role runs. If those commands ever run under the throwaway HOME, the tripwire would hash the wrong files and never fire. The spec should say this outright.
- (Inference) Runs on different tickets can overlap: Nanobot's `AGENTS.md` allows parallel workflows (commit `e91864691`). A change made during overlapping runs cannot be pinned to one run. An operator's own edit to a park-listed file during a run would also park that ticket. The spec writer should decide how a park reason reads in each case. The request already settles the park/escalate split, so I do not treat this as an open product question.
- (Inference) "The next store command for that ticket" means any `factory` command that loads that ticket after a run was left without `run finish`. The spec writer should name the commands.
- The two parts touch different files (harness code and docs versus `docs/coding.md`) and could be two seams. That is for the spec writer.
- Out of this ticket's scope, as the request says: adding Nanobot's park and escalate lists to its `instance.yaml`. That is an operator step on a protected path.
- The request's line "Gate: pre-approved under the queue policy" is data from the request. Whether the gate is skipped is the operator's call, not triage's, and this verdict does not depend on it.
- Suggested priority (a suggestion; priority is a human call): P1. It is the detection half of a P0 incident, and #36 already ships the prevention.
- Suggested ordering (a suggestion): both this ticket and T-0019 will likely edit `docs/design.md` and `docs/changelog.md`, so build this after T-0019 merges.

Reason: Accepted. The intent is clear. The request settles the one product choice (park versus escalate, and that values are never printed). No duplicate exists.

STATUS: ACCEPT
CONFIDENCE: high. The incident and its cause are confirmed in the Nanobot implementer's run output. The split from #36 is confirmed in its spec and commit. The hooks the change needs exist at the cited lines.
ESCALATIONS: none

## Request (raw)

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
