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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0013-triage/output.md`

## Request (raw, with any answers appended)

---
title: Harness instance is single-target: running tickets against this repo needs a hand-built overlay
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` D8 (`{repo name}` and protected paths: `nanobot`, default) and `factory render` (fills `{repo name}`, protected paths and gate commands from one `config.yaml`); `README.md` ("Fill in `{braces}` per repo"). The P0 plan builds one instance, for Nanobot.

**What happened (2026-10-01):** issue drafts 01–06 are requests against this repo's documents, and the operator asked for them to go through intake. The only built harness (`~/dev/nanobot-upstream/factory/`, `feat/lionbot-v3`) hardcodes the target in three places: `factory/prompts/preamble.md` line 1 and its protected-path list, `factory/prompts/context.md` (repository, how to run tests, "the request is a legacy faux spec"), and `factory/config.yaml` (`repo_name`, `protected_paths`, `gate_commands`). `FACTORY_STATE` relocates the store but nothing relocates the target. Running the drafts needed `intake/` here: a pinned copy of the harness with those three files replaced by hand.

**Why it matters:** the design says the doc is filled in per repo, but the harness has one instance and no way to point a second store at a second target. The role context file (`context.md`) is not in the design doc at all; it carries per-repo facts (how to run things, what kind of request to expect) that every role reads first, so a wrong one silently misdirects every role.

**Proposed fix (design doc + spec):** make the target a property of the store, not the harness: the store's root carries `instance.yaml` (repo name, repo path, protected paths, gate commands) and `context.md`, `run start`/`run compose` read them from there, and `factory render` takes the instance as input. Name the role-context block in the design doc's Harness section as a per-repo input the composer prepends.

**Fix as implemented on the Nanobot side:** none. The workaround is `intake/` in this repo (scratch; `intake/README.md`).
