Type: bug

Title: Build spec: `factory run start` must reserve its run id atomically so concurrent starts on one store get distinct run directories

Summary:
`specs/build-harness.md` part B says what `factory run start` writes (`runs/<run_id>/{meta.yaml,system-prompt.txt}`) and which guards refuse it, but not how `<run_id>` is chosen or that choosing it is safe when another start runs at the same moment on the same store. The P0 reference harness chose ids by listing `runs/` and taking max+1, so two starts on different tickets (where the `in_flight` guard does not apply) could get the same id and write into one `runs/<id>/`; their `meta.yaml`, `input.md` and `output.md` would then mix, and the retro would read one run's output as another's. The requester wants the spec to say that `run start` reserves `runs/<id>/` atomically (create-exclusive, taking the next id on collision) and that the id is fixed before `meta.yaml` is written. They also want an acceptance item that starts N runs at once on N tickets and checks for N distinct run directories, each with its own `meta.yaml`.

Evidence:
- Request (`intake/state/requests/T-0009.md`, also `issues/09_run_id_allocation.md`): "the P0 harness allocated an id by listing `runs/` and taking max+1, then creating the directory. Two workflows dispatching on one store at the same moment (different tickets, so the `in_flight` guard does not apply) could both compute the same number and write into one `runs/<id>/` directory."
- Spec gap confirmed: `specs/build-harness.md:201` (part B, `factory run start`) covers outputs and guards only. Running `grep -n -i "concurren\|run-[0-9N]\|run id" specs/build-harness.md docs/spec-factory.md` finds no rule for allocating ids and no concurrency requirement for the store. Part I (`specs/build-harness.md:292-299`) covers isolation, input, budget and cleanup, not id allocation.
- Concurrent `run start` calls are already part of the spec, even inside one workflow. Part H, build workflow step 2 (`specs/build-harness.md:283`), runs `await parallel(ready.map(st => () => buildOne(st)))`. Acceptance item 79 (`specs/build-harness.md:450`) says "two `parallel_safe: true` siblings both ready, nothing in flight → both listed". The design doc's Planner routing row (`docs/spec-factory.md:101`) says "parallel-safe ones run concurrently". So two clerks can run `run start` at the same moment on different tickets.
- Reference fix verified in `~/dev/nanobot-upstream` (read only). Commit `3dc4d6149` ("factory(store): run ids reserved by mkdir so concurrent workflows on one store never collide") changes `factory/store.py` `next_run_id`: it picks a candidate from max+1, then loops `(runs / rid).mkdir()` and adds 1 to n on `FileExistsError`. The diff shows the old code returned `f"run-{...}-{role}"` without creating anything. In `factory/cli.py` `run_start`, the ready-state and `in_flight` guards run before `store.next_run_id(...)`, so a refused start still creates no directory, which item 70 (`specs/build-harness.md:438`) requires.
- Workaround in this repo: `intake/README.md:57`: "One ticket at a time: the store allocates run ids without a lock."

Assumptions (triage inferences, not stated by the requester):
- A1. Only the build spec is in scope (parts B and I, plus a new acceptance item). Whether `docs/spec-factory.md` §Harness piece 2 also gets a sentence is left to the spec writer, because the requester marks it optional ("No design-doc text change needed unless §Harness wants one sentence under piece 2"). If the doc does change, its own rules apply: a Changelog entry, and a re-copy of any `prompts/` file whose block changed. Piece 2's text is a table row, not a prompt block, so no `prompts/` re-copy is expected.
- A2. The new reservation must keep the existing guard behaviour: a refused `run start` still writes no directory (item 70). In other words, the guards run before the reservation. The reference already does this. The requester did not say it.
- A3. "Distinct run directories" means distinct `runs/<id>/` paths. The reference id format `run-NNNN-<role>` lets two different roles share a number in different directories. The request does not require numbers to be unique across roles, so this ticket does not add that requirement.
- A4. The requester's phrase "parallel across tickets, serial inside a ticket" does not appear word for word in `docs/spec-factory.md`. The concurrency it describes is supported by the piece 2 row (line 38) and the Planner routing row (line 101), cited above.
- Suggested priority (a suggestion; priority is a human call): low-medium. The reference harness is already fixed and pinned, so this closes a gap in the spec rather than a live defect in that harness.

Question for human / Missing info / Reason: n/a (ACCEPT)

Out-of-scope observations:
- The request says "This repo's pinned copy (`intake/HARNESS_PIN`) predates it." That is out of date. `intake/HARNESS_PIN` now reads `3dc4d61491798af161add6471d2491653653912e`, re-pinned in `4cd8d12` ("intake: re-pin harness to 3dc4d6149 (run ids reserved by mkdir ...)"). The one-ticket-at-a-time note at `intake/README.md:57` probably no longer applies. `intake/**` is protected infra, so I did not touch it.
- `run_start` in the reference loads the ticket, checks `in_flight`, then saves. Two concurrent starts on the same ticket could both pass the `in_flight` guard. The request is about different tickets, so this ticket does not cover it; it may deserve its own request.

Duplicate search: there is no duplicate among `intake/state/tickets/T-0001..T-0008.yaml` (all closed except T-0008, which is OpenSpec storage and lifecycle). T-0009 is this request's own ticket. `issues/09_run_id_allocation.md` is the source draft of the same text.

STATUS: ACCEPT
CONFIDENCE: high, because the spec gap, the concurrent-dispatch paths in part H and item 79, and the reference fix were each checked by grep or `git show` on the cited files.
ESCALATIONS: none
