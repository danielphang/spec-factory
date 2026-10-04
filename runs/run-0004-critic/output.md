Spec critic, round 1, spec v1 (ticket T-0002, clerk relays bytes instead of re-typing the store's answer).

## What I checked

All from `~/dev/spec-factory` at `aa122ee` (`main`), working tree dirty only under `intake/state/` (the harness's own files).

- Cited paths and symbols. `specs/build-harness.md:195` is the CLI header line, `:199` the `factory ticket show ID` bullet with no output format, `:268` part H's opening paragraph with "whose schema is the command's JSON output", `:272` runRole with "The clerk returns `{run_id, status, escalations}`", `:276` phase 2 with "are read from `config.yaml` by the clerk at the start of each script", `:495` the Risk bullet with "Mitigation: each clerk call has a schema and the command is given verbatim;". `grep -cF` of each of the four OLD strings in A, D, F, G prints `1` (each matches exactly once). Design doc piece-2 row: the `sed` extraction prints the limit (1) sentence as quoted; `awk -F'|' '{print NF}'` prints `7`. Changelog: `grep -cE '^[0-9]+\. '` prints `33`; item 33 is the last numbered line, one blank line, then `Declined:`, so "append after item 33" is unambiguous. `docs/spec-factory.md:64` reads "Clerk, parsing, routing | Haiku, or no model" as the spec says. `grep -n -i clerk prompts/*` prints nothing; `grep -c 'Event dispatcher' prompts/* | grep -v ':0$'` prints nothing.
- Reference harness (`~/dev/nanobot-upstream`, `feat/lionbot-v3`, read only). `factory/workflows/intake.js:31-39`: `CLERK_SCHEMA` is `{stdout, exit, stderr}`, all three `required`, descriptions "verbatim, unmodified" / "verbatim". `:45-60` `clerk()`: prompt says "Report its stdout verbatim (do not reformat, summarize or re-encode it)"; `null` → `ok: false`; walks stdout lines from the last, `JSON.parse` each, none → `error: 'no JSON on stdout'`; non-zero exit forces `ok: false`. `:106-108`: start-of-run `factory config` then `factory ticket show <id> --json`. `factory/cli.py:4` docstring "Every command prints one JSON object on stdout; refusals also print {"ok": false, "error"}"; `:59-65` `ticket_show` prints YAML by default, a JSON object with `--json`; `:383-384` `config_cmd` prints `{"ok", "models", "max_rounds", "state_dir"}`; `:501-508` `Refused` → reason on stderr, JSON `ok: false` on stdout, exit 2; other exceptions exit 1 the same way. The scratch copy `intake/harness/factory/workflows/intake.js` has a byte-identical `clerk()` body (`diff` printed nothing). The spec's Evidence section matches what the reference does.
- Acceptance commands, all 13 run as written on this checkout. NEW items: item 1 prints `ok: the guards live in the CLI, not the clerk` and six `MISSING:` lines; item 2 prints `1`, `1`, `1`; item 3 prints six `MISSING:` lines; item 4 prints `0`; item 5 prints `0`, `1`; items 6 and 7 print nothing and exit 1; item 8 prints `33`, `0`. Each fails today for the reason the spec gives. REGRESSION items: `1`, `7`, `unchanged` with no other output, no output, no output with exit 0. I also read each NEW text block against its grep: every fixed string in items 1, 3, 4, 5, 6, 7 occurs in the corresponding NEW block, and the `grep -o` items 6 and 7 each find their three patterns exactly once in the order listed, so the items pass after a mechanical application and only after it.
- Consistency with open tickets. `intake/state/tickets/`: T-0001 (STATUS parser, parked) touches a different paragraph of part H; T-0003 touches §Routing table; T-0004 and T-0006 touch `plans/P0-intake-skeleton.md`; T-0005 the writer's FORMAT; T-0007 part D8 and `factory render`. None edits the four passages this spec changes. Spec B's items 1 and 9 keep grepping YAML, which part C preserves by making `--json` a flag; item 21's merge refusal text on stdout is carried by part D's named exception.

The spec is grounded, the edits are verbatim and unique, the acceptance items fail today and pass only on the stated text, and the stated design (relay bytes, script parses, refusal and no-JSON park) is what the reference already runs. An implementer can start without a question. Nothing below blocks.

## Findings

[SHOULD-FIX] 6 Part F (phase 2, `:276`) and part D's `factory config` read
Problem: the first clerk call (`factory config`) has to run before `MODELS.clerk` is known, and the spec names no model for it; the writer parks this under Out-of-scope observation 3 instead of in the text, so an implementer building from H has to pick one.
Evidence: NEW F says MODELS "come from clerk `factory config` (B) at the start of each script" and H says "clerk calls themselves use `model: MODELS.clerk`"; the reference hard-codes `let MODELS = { clerk: 'haiku' }` at `intake.js:41` before that call; `docs/spec-factory.md:64` already gives Haiku as the clerk's model, so no new decision is needed. The same gap exists in the OLD text (a clerk that "reads `config.yaml`" also needs a model), so this is not a regression.
Suggested fix: extend NEW F by one clause, e.g. "…at the start of each script (that first call runs on the doc's clerk default, Haiku; later calls on `MODELS.clerk`)".

[NIT] 5 Part D, "a non-zero `exit` is a refusal whatever `stdout` holds"
Problem: part B and the reference reserve "refusal" for exit 2 (store unchanged, nothing logged) and use exit 1 for errors (item 7 at `:345`: exit 1, `results/ may only be written by harness`; `cli.py:507-508`), so calling every non-zero exit a refusal blurs a term B defines; the handling D gives (park) is the same for both, so nothing routes wrongly.
Evidence: `specs/build-harness.md:345`, `~/dev/nanobot-upstream/factory/cli.py:501-508`.
Suggested fix: "a non-zero `exit` (a refusal, or an error) is never an answer" or equivalent; do not block on it.

[NIT] 6 Part D, "`factory merge`'s `head does not contain main`, matched in the relayed text"
Problem: "the relayed text" could mean `stdout`, `stderr`, or the parsed JSON's `error`; any of the three works with the reference's refusal path (reason on stderr and in the JSON `error`, item 21 puts merge's reason on stdout), so an implementer cannot go wrong, but the sentence leaves the choice open.
Evidence: `cli.py:504-506`; `specs/build-harness.md:367` (item 21); the writer's Out-of-scope observation 4 names the stdout/stderr split.
Suggested fix: "matched in `stdout` or `stderr`" (two words), or leave as is.

## Out-of-scope observations

- The writer's observation 1 (`run finish --output-file -` with `out` asks the clerk to re-type the role's whole output on the input side) is real and bigger than this ticket: the reference has each role write `runs/<id>/output.md` itself and `run finish RUN` reads the file. It should become its own ticket; the spec is right not to fold it in.
- The writer's observation 2 (`plans/build-harness.md` BH-1 and BH-5 do not list `ticket show --json` or `factory config`) is confirmed by `grep -n -i clerk plans/*.md`: neither plan names either command. A plan amendment belongs to the planner after this lands.

STATUS: APPROVE
CONFIDENCE: high — every cited line, OLD string, reference symbol and all 13 acceptance commands were checked on this checkout and in the reference harness; the one open item (clerk model for the first call) has an answer in the design doc's model table and is a SHOULD-FIX, not a blocker.
ESCALATIONS: none
