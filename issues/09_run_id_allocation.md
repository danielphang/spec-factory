---
title: Build spec: `run start` must reserve the run id atomically; two workflows on one store could collide
labels: harness, design-doc
---
**Where:** `specs/build-harness.md` part B, the `factory run start` bullet, and part I (concurrency). The spec says what `run start` writes (`runs/<id>/meta.yaml`, the system prompt) and that the ticket's `in_flight` guard refuses a second run on the same ticket, but not how `<id>` is chosen or that choosing it is safe against another workflow on the same store.

**What happened (2026-10-01, Nanobot green):** the P0 harness allocated an id by listing `runs/` and taking max+1, then creating the directory. Two workflows dispatching on one store at the same moment (different tickets, so the `in_flight` guard does not apply) could both compute the same number and write into one `runs/<id>/` directory. The scratch intake in this repo worked around it by running one ticket at a time (`intake/README.md`). Fixed on green the same day: allocation is by `mkdir`, so the directory creation is the reservation and a loser retries with the next number.

**Why it matters:** the design doc's "parallel across tickets, serial inside a ticket" (§Harness, piece 2 and the parking/exclusion rules) assumes a store that two dispatchers can share. Without an atomic reservation the run directory, `meta.yaml` and later `output.md` of two runs can interleave, and the retro reads one run's output as another's.

**Proposed fix (spec B and I):** state that `run start` reserves `runs/<id>/` atomically (create-exclusive; on collision take the next id) and that the id is final before `meta.yaml` is written; add an acceptance item that starts N runs concurrently on N tickets and checks N distinct run directories, each with its own `meta.yaml`. No design-doc text change needed unless §Harness wants one sentence under piece 2.

**Fix as implemented on the Nanobot side:** green `feat/lionbot-v3`, `factory/store.py` `next_run_id` → mkdir-based allocation (commit per the Driver session, 2026-10-01). This repo's pinned copy (`intake/HARNESS_PIN`) predates it.
