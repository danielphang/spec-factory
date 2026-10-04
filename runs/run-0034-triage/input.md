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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0034-triage/output.md`

## Request (raw, with any answers appended)

---
title: Build spec: `run start` must reserve the run id atomically; two workflows on one store could collide
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` part B, the `factory run start` bullet, and part I (concurrency). The spec says what `run start` writes (`runs/<id>/meta.yaml`, the system prompt) and that the ticket's `in_flight` guard refuses a second run on the same ticket, but not how `<id>` is chosen or that choosing it is safe against another workflow on the same store.

**What happened (2026-10-01, Nanobot green):** the P0 harness allocated an id by listing `runs/` and taking max+1, then creating the directory. Two workflows dispatching on one store at the same moment (different tickets, so the `in_flight` guard does not apply) could both compute the same number and write into one `runs/<id>/` directory. The scratch intake in this repo worked around it by running one ticket at a time (`intake/README.md`). Fixed on green the same day: allocation is by `mkdir`, so the directory creation is the reservation and a loser retries with the next number.

**Why it matters:** the design doc's "parallel across tickets, serial inside a ticket" (§Harness, piece 2 and the parking/exclusion rules) assumes a store that two dispatchers can share. Without an atomic reservation the run directory, `meta.yaml` and later `output.md` of two runs can interleave, and the retro reads one run's output as another's.

**Proposed fix (spec B and I):** state that `run start` reserves `runs/<id>/` atomically (create-exclusive; on collision take the next id) and that the id is final before `meta.yaml` is written; add an acceptance item that starts N runs concurrently on N tickets and checks N distinct run directories, each with its own `meta.yaml`. No design-doc text change needed unless §Harness wants one sentence under piece 2.

**Fix as implemented on the Nanobot side:** green `feat/lionbot-v3`, `factory/store.py` `next_run_id` → mkdir-based allocation (`3dc4d6149`, 2026-10-01; retries on `FileExistsError`). This repo's pinned copy (`intake/HARNESS_PIN`) predates it.
