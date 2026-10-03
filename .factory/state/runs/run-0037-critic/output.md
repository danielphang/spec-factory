# Critic review: T-0009 v1 (`factory run start` reserves its run directory atomically)

Spot-checks performed (spec-factory `main` `b4d0f90`, clean except `intake/state/**`; reference `~/dev/nanobot-upstream` at `a65f0afd0`, `feat/lionbot-v3`, read only):

- `specs/build-harness.md:201` is the `factory run start` bullet and ends with "`ticket/T-0001 already has run <id> in flight`." as stated; it has no allocation rule. `:283` and `:286` hold the two `parallel(...)` calls; `:438` is item 70 with "no new `runs/<id>/` directory"; `:450` is item 79 with "two `parallel_safe: true` siblings both ready, nothing in flight → both listed"; `:465` is `### Gates (every seam)`; `:469` is the marker line ending `82, 85 are local-only.`; the highest item number today is 86. `docs/spec-factory.md:101` says "parallel-safe ones run concurrently"; `:46` says "keyed by run id". The E1 grep reproduces: no allocation or concurrency text.
- Reference: `git diff --stat 3dc4d6149 HEAD -- factory/` is empty. `factory/store.py` `next_run_id` pre-fix returns `f"run-{max+1:04d}-{role}"` from a listing; at `3dc4d6149` it loops `(runs / rid).mkdir()` and increments on `FileExistsError`. `factory/cli.py` `run_start` raises the ready-state and in-flight refusals before `store.next_run_id`, so a refused start creates no directory. `log tail` accepts `--event` (spec `:209` and reference argparse). `next_ticket_id` (store.py:81-90) is list-then-name, as the out-of-scope observation says. `intake/README.md:57` and `intake/HARNESS_PIN` read as quoted.
- Acceptance items 1–7 run as written from `~/dev/spec-factory`. On base: 1, 2, 4 print `0`; 3 prints nothing, exit 1; 5 prints `0`; 6 prints `untouched`; 7 exits 0. On a scratch clone with parts A–C applied exactly as written: 1, 2, 4 print `1`; 3 prints `1` then `1`; 5 prints `0`; 6 `untouched`; 7 exit 0; `git diff --stat main...HEAD` → `specs/build-harness.md | 8 ++++++--`, matching E6 and Risk. Item 2 prints `0` against a stub item with the 20 repeats removed.
- T-0008 v2 (`intake/state/specs/T-0008/v2.md`) inserts items 87 and 88 before `### Gates (every seam)` and also edits the marker line (bare-repo list). Its own Risk says it edits neither the `run start` bullet nor part I, so the only textual overlap with T-0009 is item numbering and the marker line.

The spec's core claim holds: the build spec permits concurrent `run start` calls and defines no allocation rule, so a list-then-name allocation satisfies it and collides; the proposed rule closes that gap at the place `run start` is defined, without touching the design doc, and the new item is discriminating (E4: 18/20 pre-fix failures per round; exit codes and `in_flight` alone would not catch it, which the item's design notes say).

## Findings

[SHOULD-FIX] 6 Proposed change B, item 87, "Repeated 20 times, each time on eight new tickets in a fresh working directory"
Problem: The loop hard-codes `--ticket T-000$i` and the item counts `runs/` "eight more directories than before", so a repeat needs a fresh store (ticket ids restart at `T-0001`), not merely a fresh working directory; as written, a second repeat in the same store would hit `T-0001`…`T-0008` already in flight and exit 2, or hit tickets `T-0009`+ that the loop never names.
Evidence: `specs/build-harness.md` Acceptance has no stated per-item fresh-store convention (grep for fresh/empty/new store in `:330-470` finds only "a fresh ticket" and "a fresh `run start`"); the spec's own E4 says it set `FACTORY_STATE` to "a fresh scratch store" for each round.
Suggested fix: Replace "in a fresh working directory" with "in a fresh store (and a fresh working directory for `start.*.json` and `rc.*`)".

[NIT] 3 Risk, "Merge-order risk"
Problem: T-0008 v2 part L also edits the `Items needing the bare repo: …` marker line (appends to the bare-repo list), so whichever ticket merges second gets a one-line textual conflict there in addition to renumbering; the Risk paragraph only mentions numbering.
Evidence: `intake/state/specs/T-0008/v2.md:203` ("In the line `Items needing the bare repo: …`, append the two new numbers after `84`"); T-0009 part C edits the same line.
Suggested fix: Add one clause to the merge-order paragraph: "and the marker line, which both tickets edit; resolve by keeping both additions."

[NIT] 2 Acceptance item 5
Problem: The command prints `0` but exits 1 both on base and after the change (`grep -vc` with zero selected lines exits 1), so a verifier that keys on exit status, as items 1, 3 and 7 invite, would read a pass as a failure.
Evidence: Ran item 5 on base and on the scratch clone: output `0`, `rc=1` both times.
Suggested fix: Add "(exit 1 is expected: `grep -c` exits 1 when the count is zero)" after the `→ \`0\`` so the printed value, not the exit status, is the check.

Not raised as findings, for the record: part A names the mechanism (create-exclusive mkdir) rather than only the property; this is stated openly with its scope limit (one filesystem, one checkout) and matches the as-built fix, so it is not a hidden decision. The `factory ticket show … | grep in_flight` → `in_flight: [<id>]` form in item 87 follows existing item 9 (`:348`) exactly; the reference's `yaml.safe_dump` prints the list block-style (`in_flight:\n- run-…`), which would fail that grep for item 9 and item 87 alike, but that is a pre-existing reference-vs-spec discrepancy, not something this spec introduces.

## Out-of-scope observations

- Reference `factory/cli.py` `ticket_show` writes `in_flight` as a block-style YAML list, while spec items 9 and (now) 87 expect `in_flight: [<id>]` on one line. Either the spec should say the show format or the reference should dump flow style for lists. Separate request.
- The spec's own out-of-scope notes (ticket-id race in `next_ticket_id`; lost `in_flight` update on two same-ticket starts) are real in the reference at HEAD and deserve their own requests, as the spec says.

## Prior findings

none (round 1).

STATUS: APPROVE
CONFIDENCE: high — every cited path and line was read, the fix was inspected at both commits, and all seven acceptance commands were run on base and on a scratch clone with the change applied, with the stated values in both states.
ESCALATIONS: none
