Commit: 37c867e6881221552f4b86efe47fcbb04fabd929 (one commit on base 9e8f4d3, branch `factory/T-0060.1`)

## What I checked

Diff stat: `README.md` (+2 −1), `docs/benchmark.md` (new, 195 lines), `factory/benchmark.py` (new, 107 lines), `tests/factory/test_benchmark.py` (new, 174 lines). No other file changed.

1. **Test integrity.** No existing test file is modified or deleted (`git diff --stat` lists only the four files above; the one file under `tests/` is new). The new tests assert exact values that follow from the spec's rules, not values copied from output: 900 s stays in one sitting at 16.0 minutes, 901 s gives two sittings at 2.0 minutes, a store with two decisions ten minutes apart gives 11.0 minutes, and the repeated message id `m1` gives 150 context tokens. No skip, xfail or swallowed error. The spec's "Tests to change" is none and none changed.

2. **Correctness against the spec's design part A.**
   - Operator-message rule (`factory/benchmark.py:687-695`): `user` record, not `isMeta` or `isSidechain`, no `tool_result` block, `promptSource` in `typed`/`queued`/`suggestion_accepted`, or no `promptSource` and text not starting `<`, and a `timestamp` required. Matches Decisions and part A exactly. The text-block case works because `_user_text` joins the `text` fields of list content.
   - Sittings (`:698-709`): sorted interactions, new sitting when the gap exceeds 900 s, each sitting counts its span plus 60 s, sum in minutes. The boundary is `>`, so exactly 900 s stays in the sitting, as part B requires.
   - Interactions (`:716-732`): operator messages plus store events whose `event` is in `factory.stats.DECISIONS`. Events outside `DECISIONS` count only for elapsed. `gate and ruling events` counts decision events whether or not they carry `ts`, which the spec does not forbid.
   - Elapsed (`:734`): max minus min over every timestamped session record and every store event with `ts`, two decimals in hours, `-` when none.
   - Tokens (`:723-724`): sum of `transcript_usage` per session, which dedups by message id within a file, as part A words it.
   - Reuse (`:679-680`): imports `_records`, `_log_records`, `_user_text`, `_when`, `transcript_usage` and `DECISIONS`; copies none. Does not import `factory.cli` directly. The indirect load through `factory.stats` is the spec's own consequence of "take DECISIONS from factory.stats", disclosed in Known gaps; not a defect.
   - Refusals (`:748-757`): all three checked before any stdout, exit 2, one stderr line starting `factory.benchmark: `, the missing session and the store named. Nothing is written anywhere.
   - Output (`:735-740`): the five rows in the spec's order and wording.
   - I traced the spec's two fixture scenarios by hand through this code: base.jsonl gives 3 messages, 2 sittings (10:00 to 10:15 plus 1 min, 10:40 plus 1 min) = 17.0, elapsed 10:00:00 to 10:41:00 = 0.68 h, tokens 3150/60; runner plus store gives 2 messages, 2 decisions, 3 sittings = 3.5, elapsed 09:00:00 to 12:05:00 = 3.08 h, tokens 1130/12. Both match the THEN lines.

3. **Part C, `docs/benchmark.md`.** Eight `##` headings in the spec's order and no others. Every phrase the acceptance greps for sits on one line (checked lines 501, 503, 516, 539, 544, 557, 571, 596, 605, 624, 631, 637, 644, 649). Content against the spec's eight numbered items: the listing command matches the spec's Evidence verbatim with `--limit 400`; the four filters are in order with "first parent"; the five blinding measures, preface text, alternation and audit command are as specified; the factory and baseline arm procedures name `FACTORY_INSTANCE`, `FACTORY_STATE`, `--repo-name`, `factory ticket new --file` and "gives the implementer"; the scoring commands match; the measures table has a row per measure and a column per arm; the three things the sittings rule misses are listed; results go to review section 5, which `docs/reviews/TEMPLATE.md:34` does name "Experiments and side work"; spend names both approved quantities. I confirmed the referenced things exist: README `### Adopting the factory in a repo` (README.md:648), `factory init --repo-name` (factory/cli.py:768), `factory ticket new --file` (factory/cli.py:655). The three relative links resolve (`north-star.md`, `reviews/TEMPLATE.md`, `../README.md`).

4. **Part D, README.** The two rows are the spec's text verbatim (README.md:113, :1141). README is 1,225 lines, exactly the budget. The status header already reads 2026-10-26 (README.md:13), today's date; the PR notes it needs a bump only if merged later.

5. **Scope.** Nothing outside parts A to D.

6. **Silent behaviour changes.** None: no existing code calls the new module, and no existing module changed.

7. **Security and data safety.** The module opens only the paths it is given, read-only, and writes nothing. Tests write only under `tmp_path`. The subprocess runs `sys.executable -m factory.benchmark` from the checkout root with no network or home access.

8. **Protected paths.** `factory/benchmark.py`, declared in the parent's Risk ("Protected paths: `factory/benchmark.py`"). Listed under ESCALATIONS for the record.

9. **Coding standard.** Rule 1: the module takes the existing readers rather than writing its own. Rule 6: no path is patched and no path outside the repository is added. Over-building pass: Lean already.

## Findings

- [NIT] factory/benchmark.py:691: `o["message"]["content"]` indexes directly, while `_user_text` on the line above tolerates a missing `message` or `content` → a `user` record with no `content` key aborts the whole report with a `KeyError` traceback and exit 1, where every other malformed record is skipped. Claude Code always writes `content`, so this is unlikely to bite; `(o.get("message") or {}).get("content")` would make the two lines consistent.
- [NIT] PR description: What changed, part A: "a seven-row Markdown table" counts the two header lines as rows; the spec and the output have five measure rows. A reader comparing the description to the output will count five.

Prior findings: none (round 1).

## Out-of-scope observations

- The baseline's "operator decisions" needs one hand subtraction from the report's `operator messages` row, as the PR's Known gaps says. That tension is in the approved spec (design C.6 against C.7's "No number is typed or adjusted"), so it is the operator's call for a later ticket, not a defect of this change.
- Passing the same transcript twice counts its tokens twice, because the message-id dedup is per file. The spec words tokens as "the sum of `transcript_usage` over the sessions", so this follows the spec; the page could warn the operator not to list a transcript twice.

STATUS: APPROVE
CONFIDENCE: high. I read the whole diff against every lettered part and traced both fixture scenarios through the code by hand to the spec's exact THEN lines; the only findings are two nits.
ESCALATIONS: protected path `factory/benchmark.py` added, declared in the parent spec's Risk section (for the record; no action needed).
