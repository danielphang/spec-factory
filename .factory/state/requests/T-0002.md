---
title: Clerk-via-schema re-encodes the CLI's JSON; the clerk should relay raw stdout and the script should parse
labels: harness, design-doc
---
**Where:** design doc §Harness piece 2, v0 limit (1) ("store writes go through a clerk agent calling the CLI"); `specs/build-harness.md` part H: *every read and write of the store is an `agent()` call on `factory-clerk` … whose schema is the command's JSON output.*

**What happened (P0 run, 2026-10-01):** with the clerk's `schema` set to the command's JSON shape, a Haiku clerk returned `{"ok": true, "status": "success", "state": "{\"ok\": true, \"id\": \"T-0001\", \"state\": \"ready-for-triage\", …}"}` for `factory ticket show --json`: it invented a `status: success` field and stringified the nested object into the `state` slot. The script then read `state === '{"ok": true, …}'` and routed "nothing to dispatch". A second shape error later surfaced as `tr.round.spec` undefined.

**Why it matters:** a schema on the clerk asks the model to *re-type* structured data it has already received verbatim. Every clerk call becomes a chance to corrupt the store's answer, and the corruption is silent (the schema validates).

**Proposed fix (design doc piece 2 and spec H):** the clerk's schema is `{stdout, exit, stderr}` with stdout verbatim; the *script* parses the last JSON line of stdout. The guards stay in the CLI (unchanged). State the rule once: "the clerk never restates a command's output; it relays bytes".

**Fix as implemented on the Nanobot side:** `factory/workflows/intake.js` `clerk()` at `0f2e29136`. Design-doc text not yet changed; awaiting review.
