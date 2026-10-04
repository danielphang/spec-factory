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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0003-spec_writer/output.md`

## Ticket (Triage output)

Type: bug

Title: Clerk calls re-type the store CLI's JSON through a schema, so a store answer can be silently corrupted; the clerk should relay raw output and the script should parse it

Summary: The design doc (§Harness table piece 2, v0 limit (1)) and `specs/build-harness.md` part H have every store read and write go through a clerk agent. Spec H gives that agent a schema equal to the command's JSON output. In the P0 run a Haiku clerk invented a field and stringified a nested object into the `state` slot. The answer still passed the schema, and the script misrouted to "nothing to dispatch". The requester wants the documents to say that the clerk never restates a command's output. It returns stdout verbatim with the exit code and stderr, and the script parses the JSON itself. The CLI guards stay as they are. The as-built harness already works this way. Only the design documents still have the old rule.

Duplicate search:
- No duplicate in the local store. `intake/state/requests/index.yaml` maps T-0002 (this ticket) to `issues/02_clerk_schema.md`, and `diff` of the two files printed nothing. I read the `title:`/`Where:` head of every other request. T-0001 (STATUS parser), T-0003 (re-ask input), T-0004 (agents dir), T-0005 (protected live state), T-0006 (P0-5 grep) and T-0007 (single-target harness) cover other problems. T-0001 also concerns parsing, but of role output, not clerk output.
- I did not search GitHub issues. Filing is on hold until `gh auth` is restored (`issues/README.md`).

Evidence:
- Design doc, `docs/spec-factory.md:38` (piece 2): "(1) The script has no filesystem or clock, so store writes go through a clerk agent calling the CLI; the guards live in the CLI, not the clerk." It says nothing about the shape of what the clerk returns.
- Spec rule, `specs/build-harness.md:268`: "every read and write of the store is an `agent()` call on `factory-clerk` (`effort: 'low'`) whose prompt is a fixed `factory …` command line and whose schema is the command's JSON output."
- The same assumption appears elsewhere in spec H. `specs/build-harness.md:272` (runRole) says "The clerk returns `{run_id, status, escalations}`". `specs/build-harness.md:495` (Risk) says "each clerk call has a schema and the command is given verbatim".
- Failure quoted in the request (P0 run, 2026-10-01): for `factory ticket show --json` the clerk returned `{"ok": true, "status": "success", "state": "{\"ok\": true, \"id\": \"T-0001\", \"state\": \"ready-for-triage\", …}"}`. The script read `state` as that string and routed "nothing to dispatch". A second shape error then surfaced as `tr.round.spec` undefined. I could not find the transcript itself in the reference store. I did confirm the code path exists: `~/dev/nanobot-upstream/factory/workflows/intake.js:108` calls `ticket show … --json` through the clerk, and `:181` returns `note: 'nothing to dispatch from this state'`.
- I checked the as-built fix in the reference harness (`~/dev/nanobot-upstream`, `feat/lionbot-v3`, read only):
  - `0f2e29136` exists. It is the P0 skeleton commit, and its message says "every store write is a clerk call returning raw stdout that the script parses."
  - `factory/workflows/intake.js:31-39` defines `CLERK_SCHEMA` = `{stdout, exit, stderr}`, all required, with stdout described as "verbatim, unmodified".
  - `clerk()` at `:45-60` takes the last line of stdout that parses as JSON. When there is none it returns `ok: false` with `error: 'no JSON on stdout'`. A non-zero exit forces `ok: false`.
  - The only later commit touching the file is `f3294b239`, and the `clerk()` body there is unchanged. `intake/harness/factory/workflows/intake.js` in this repo has a `clerk()` byte-identical to the reference copy (`diff` printed nothing).
- Store CLI contract: the reference `factory/cli.py:4` says "Every command prints one JSON object on stdout; refusals also print {"ok": false, "error"}."

Assumptions (my inferences, not stated by the requester):
- A1: The requester's evidence fixes one requirement: the clerk must not be asked to re-type structured store data. The script must get the CLI's own bytes, so a mis-typed answer cannot pass validation. The rest is the requester's proposal, which the as-built harness implements: the `{stdout, exit, stderr}` shape, "parse the last JSON line", and the exact wording of the rule. The Spec writer may adopt it but should not treat it as binding.
- A2: Spec H must be brought into line wherever it assumes the clerk returns parsed fields, not only at line 268. That includes line 272 ("The clerk returns `{run_id, status, escalations}`") and the Risk mitigation at line 495. This follows from the input's convention that `specs/build-harness.md` stays consistent with the design doc.
- A3: The design-doc edit falls within piece 2's v0 limit (1). It needs a Changelog entry (`docs/spec-factory.md:605`). `grep -n -i clerk prompts/*` matched nothing, so no `prompts/` file is expected to need re-copying.
- A4: A clerk that cannot produce a JSON line (no JSON, or a non-zero exit) should count as a failed store call that the script handles, for example by parking as a harness bug. It must not be read as a valid answer. The requester implies this ("the corruption is silent"), and the as-built `ok: false` path does it.
- Priority (suggestion only): high. Every clerk call in both workflows depends on this rule, and the failure mode misroutes tickets without any error.

Reason: The intent is clear, the evidence is concrete, and no product decision is needed. The fix runs in the reference harness and is a single rule. A Spec writer can take this as is.

Out-of-scope observations:
- Spec acceptance items 1 and 9 (`specs/build-harness.md:339`, `:347`) grep `factory ticket show` output as YAML lines (`^status:`). The reference CLI adds a `--json` flag (`factory/cli.py:415`) for the workflow's use. The spec does not say which output format `ticket show` uses by default, and the clerk rule should not leave this ambiguous. Whoever writes the spec should check it.

STATUS: ACCEPT
CONFIDENCE: high — I read the document text and the as-built clerk with file reads, grep, `git log`/`git show` and `diff`; only the failure transcript itself could not be found, and GitHub was not searched
ESCALATIONS: none

## Request (raw)

---
title: Clerk-via-schema re-encodes the CLI's JSON; the clerk should relay raw stdout and the script should parse
labels: harness, design-doc
---
**Where:** design doc §Harness piece 2, v0 limit (1) ("store writes go through a clerk agent calling the CLI"); `specs/build-harness.md` part H: *every read and write of the store is an `agent()` call on `factory-clerk` … whose schema is the command's JSON output.*

**What happened (P0 run, 2026-10-01):** with the clerk's `schema` set to the command's JSON shape, a Haiku clerk returned `{"ok": true, "status": "success", "state": "{\"ok\": true, \"id\": \"T-0001\", \"state\": \"ready-for-triage\", …}"}` for `factory ticket show --json`: it invented a `status: success` field and stringified the nested object into the `state` slot. The script then read `state === '{"ok": true, …}'` and routed "nothing to dispatch". A second shape error later surfaced as `tr.round.spec` undefined.

**Why it matters:** a schema on the clerk asks the model to *re-type* structured data it has already received verbatim. Every clerk call becomes a chance to corrupt the store's answer, and the corruption is silent (the schema validates).

**Proposed fix (design doc piece 2 and spec H):** the clerk's schema is `{stdout, exit, stderr}` with stdout verbatim; the *script* parses the last JSON line of stdout. The guards stay in the CLI (unchanged). State the rule once: "the clerk never restates a command's output; it relays bytes".

**Fix as implemented on the Nanobot side:** `factory/workflows/intake.js` `clerk()` at `0f2e29136`. Design-doc text not yet changed; awaiting review.
