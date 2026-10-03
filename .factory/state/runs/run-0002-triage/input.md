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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0002-triage/output.md`

## Request (raw, with any answers appended)

---
title: Clerk-via-schema re-encodes the CLI's JSON; the clerk should relay raw stdout and the script should parse
labels: harness, design-doc
---
**Where:** design doc §Harness piece 2, v0 limit (1) ("store writes go through a clerk agent calling the CLI"); `specs/build-harness.md` part H: *every read and write of the store is an `agent()` call on `factory-clerk` … whose schema is the command's JSON output.*

**What happened (P0 run, 2026-10-01):** with the clerk's `schema` set to the command's JSON shape, a Haiku clerk returned `{"ok": true, "status": "success", "state": "{\"ok\": true, \"id\": \"T-0001\", \"state\": \"ready-for-triage\", …}"}` for `factory ticket show --json`: it invented a `status: success` field and stringified the nested object into the `state` slot. The script then read `state === '{"ok": true, …}'` and routed "nothing to dispatch". A second shape error later surfaced as `tr.round.spec` undefined.

**Why it matters:** a schema on the clerk asks the model to *re-type* structured data it has already received verbatim. Every clerk call becomes a chance to corrupt the store's answer, and the corruption is silent (the schema validates).

**Proposed fix (design doc piece 2 and spec H):** the clerk's schema is `{stdout, exit, stderr}` with stdout verbatim; the *script* parses the last JSON line of stdout. The guards stay in the CLI (unchanged). State the rule once: "the clerk never restates a command's output; it relays bytes".

**Fix as implemented on the Nanobot side:** `factory/workflows/intake.js` `clerk()` at `0f2e29136`. Design-doc text not yet changed; awaiting review.
