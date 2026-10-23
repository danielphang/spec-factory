## Proposed change

**A. Drop the attribution footer before rule (b)** (`factory/status.py`).
1. Add a module constant `ATTRIBUTION_RE = re.compile(r"^🤖 Generated with \[Claude Code\]\(\S+\)$")`.
2. In `parse()`, after `tail` is built (line 38), remove each entry that `ATTRIBUTION_RE.fullmatch`es. The entries are already stripped of `-`/`*` markers.
3. Lines 43-49 then run unchanged on the filtered `tail`. A `none` head with only the footer below it therefore becomes "no escalation", and a `none` head with a real line and the footer gives `["none", "<real line>"]`.
4. Add one sentence to the module docstring and to the comment above line 43, saying that the footer is dropped first and why.
5. Change nothing else in the parser. `strip_trailer()` is not touched.

**B. List an unreadable agent copy** (`factory/setup.py`, the loop at lines 182-191).
1. Split the comparison in the `elif`. A copy that is not a file is handled as today.
2. For a file, read it in `try: … except OSError as e:`. On error, append its path to `stale` and print `factory init: <copy> could not be read (<e.strerror or e>); left as it is` to stderr.
3. Otherwise compare the bytes as today.
4. Never write, chmod or delete the copy. The loop goes on to the remaining templates, and `out(...)` reports `ok: true` with exit 0.

**C. Refuse `--accept-harness` with the lock-free commands** (`factory/cli.py` `main()`).
1. As the first statement inside the `try`, before the `init`/`paths`/`stats` branch, add: `if a.cmd in ("init", "paths", "stats") and a.accept_harness: raise Refused(...)`.
2. Give the error one line that names `a.cmd`, says the command never checks the harness lock, and ends `factory --accept-harness <a.accept_harness> config`. The existing `except Refused` prints it, emits `{"ok": false, ...}` and returns 2.
3. Rewrite the comment at lines 851-852 to say these three commands skip the fence and the lock and refuse the flag. The comment above `READ_ONLY` (line 837) stays true.

**D. Suite cases** (new test file(s) under `tests/factory/`, using the existing helper modules):
- `run finish` on an output ending with run-0418's tail (`ESCALATIONS: none`, blank line, footer). Expect escalations `[]`, no `escalation.queued` event, and no footer in `meta.yaml`.
- `status parse` with a real item line above the footer. Expect the footer dropped and the real items kept per rule (b).
- `status parse` with a line that only mentions Claude Code. Expect it kept as an item.
- `init` with one copy at mode `000`. Expect exit 0, the copy in `stale_agents`, a stderr line saying it `could not be read`, and the copy unchanged once readable again. Restore the mode in the test's teardown so the temporary directory can be removed.
- `--accept-harness` with each of `init`, `paths` and `stats`. Expect exit 2, the `config` hint on stderr, the lock unchanged and nothing written.
- No case uses skip or xfail.

**E. Docs.**
- `README.md`:
  - In "Accepting a harness revision", replace the last sentence (line 611) with: `paths` and `stats` skip both checks on any store because they write nothing, and `init`, `paths` and `stats` refuse `--accept-harness`; every other command accepts it.
  - In "Upgrading the runtime", step 2 (line 619) names `factory --accept-harness <sha> config`.
  - In "Counting what each role catches and costs" (line 952), "needs … no `--accept-harness`" becomes "refuses `--accept-harness`".
  - The `.claude/agents/factory-*.md` row (line 529) adds that init also reports a copy it cannot read.
  - Bump the status date. README stays within its 1,185-line budget.
- `docs/design.md`:
  - The ESCALATIONS bullet (line 105) gains one sentence saying that a line below the ESCALATIONS line that is Claude Code's attribution footer, `🤖 Generated with [Claude Code](<link>)`, is dropped before the `none` rule is applied.
  - The `harness.lock` clause in the Role-context block paragraph (line 68) says that `init`, `paths` and `stats` refuse `--accept-harness`.
  - No prompt block changes, so `docs/prompts/` is not touched.
- `docs/changelog.md`: one new entry with the next free number, naming #88, #113, #114 and #115 and covering the footer (`Generated with`), the `stale_agents` listing of an unreadable copy, the `--accept-harness` refusal and the `/bin/sh` scenario fix.

**F. Current truth.** The build-dispatch delta below restates the launch-script requirement with the two patterns parenthesised. It is applied at archive, and the implementer touches no store file.

## Tests to change

- `tests/factory/test_stats.py`, in `test_reads_an_own_store_with_a_run_in_flight_from_its_runs_under_another_lock`, lines 419-423. The test runs `--accept-harness 0…0 stats` and asserts `returncode == 0`, with the comment "--accept-harness is ignored, as for `paths`". The Decision on #115 makes that exit 2.
  - Change the assertion to `returncode == 2`, add a check that stderr holds the `config` hint, and update the comment.
  - Keep the surrounding `snapshot(target) == before` assertion. A refusal writes nothing, so it still holds.

