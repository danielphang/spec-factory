## Proposed change

**A. A token record for every run (build-dispatch).**

A1. `factory/cost.py`: add a function that, given transcript directories, a store path, a run id and the run's `started`, returns the run's transcript record or `None`. It walks `*.jsonl` at any depth under each directory, opens only files whose modification time is at or after `started`, and applies `match_transcripts`' rule for that one store and run (first non-relay user message naming `<P>/runs/<run>/`, first timestamp at or after `started`, own-path candidate preferred, else a single candidate). It sums the four usage fields over the transcript, each message id once with its last record's usage, as `transcript_usage` counts. The record is `{"source": "transcript", "transcript": <path>, "usage": {"input_tokens": …, "cache_read_input_tokens": …, "cache_creation_input_tokens": …, "output_tokens": …}, "total_cost_usd": None}`. `cost.py` keeps no import from the `factory` package (T-0046's decision). Reuse `match_transcripts`' helpers rather than copying them, for example with an optional modification-time floor.

A2. `factory/cli.py` `run_finish` and its parser: add `--transcripts DIR` (`action="append"`, default `[]`). After the `--reply` handling, when the recorded `claude` value has no `usage` mapping (no `--reply`, or a reply that is not a JSON object or has no `usage`) and the function in A1 finds a record, set `meta["claude"]` to it. Otherwise everything stays as today: a reply with usage is kept in its current shape, and an unusable reply with no transcript still records `claude: null`. Keep `cli.py` under 900 lines (current truth; it has 880). This part and B and C together may add at most 19 lines to it.

A3. `factory/workflows/intake.js` and `build.js`: define once per script `const TRANSCRIPTS = '"${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"'` (a plain string, so JavaScript does not interpolate it), and append ` --transcripts ${TRANSCRIPTS}` to every `run finish` clerk command: the normal one and the KILLED one after a thrown agent call. Change nothing else in either script.

A4. `factory/drive.py`: pass `--transcripts <dir>` on its three `run finish` calls (`:228`, `:235`, `:577`). `<dir>` is `os.environ["CLAUDE_CONFIG_DIR"] + "/projects"` when that is set and non-empty, else `os.path.expanduser("~/.claude/projects")`, computed from the driver's own environment, which its role processes inherit.

**B. Records the scorecard counts (factory-stats).**

B1. `factory/human.py` `escape_add`, and the parser in `cli.py`: `factory escape add TICKET --issue TEXT [--note TEXT]`. Load the ticket (unknown: exit 2). Refuse a sub-ticket id with `escape add: <id> is a sub-ticket; record the escape on its parent <parent>`. Read the log through `store.log_lines` and refuse, with `escape add: <id> has no merge`, a ticket with no `merge.done` whose ticket is the id or `<id>.N`. Refuse an empty `--issue`, and a `--note` that contains `://` (`escape add: keep links out of the note; the store keeps no link`). Every refusal exits 2 and writes nothing. Otherwise write one event, `store.log_event(root, "escape.recorded", ticket=<id>, issue_sha256=<hex>, by=_by())` plus `note=` when given, where `<hex>` is `hashlib.sha256(<the --issue text>.encode("utf-8")).hexdigest()`, and print `{"ok": true, "id": <id>, "issue_sha256": <hex>}`. The `--issue` text is written nowhere: not to the log, a ticket, stdout or stderr. Add no other top-level name to `human.py`.

B2. (Answer 2, question 1.) `factory/human.py` `intervention_add`, and its parser: `factory intervention add --kind WORD [--ticket TICKET] [--note TEXT]`. `--kind` is required and non-empty. A given ticket must exist, at any state (exit 2 otherwise). Write one `intervention.recorded` event with `kind`, `by` and, when given, `ticket` and `note`. Print `{"ok": true, "kind": …}` plus `"id"` when a ticket was given. A `--note` containing `://` is refused as in B1 (`intervention add: keep links out of the note; the store keeps no link`).

Neither command joins the fence's read-only list.

**C. The scorecard (factory-stats).** `factory/stats.py` gains a scorecard report; `cli.py`'s `stats` parser gains `--scorecard` (`store_true`), and `stats_cmd` calls the scorecard instead of `report()` when it is set. Sections A to D and `report()` do not change.

C1. Refusals, exit 2, nothing printed on stdout: `--scorecard` without `--since` (`factory stats: --scorecard needs --since`); an instance file whose `target_is_factory` is present and not a boolean (`factory stats: target_is_factory in <file> must be true or false`).

C2. Windows: `end` is `--until`, else now; the current window is `[since, end)` and the previous is `[since - (end - since), since)`. A bound is printed `YYYY-MM-DD` when it is midnight UTC, else `YYYY-MM-DD HH:MM` (UTC).

C3. For each `--store`, in the order given: find its instance (proposal, Decisions), then count from its `runs/*/meta.yaml` and its log (read with `cost._log_records`, as `report()` does), with these definitions, each per window:
- changes: as in Decisions. A sub-ticket is `<parent>.N`.
- escapes: changes with an `escape.recorded` event for the change id dated before `end`. Printed `0`, or `<n> (<ids sorted, ", "-separated>)`.
- decisions D and interventions I: as in Decisions; "within 2 seconds" is an absolute difference of at most 2 s between event timestamps. Per change: `f"{(D + I) / n:.1f}"`, or `-` when n is 0.
- a change's runs: runs whose ticket is the change or `<change>.N`, at any date, with a status other than none or `running`. A run's tokens are its `claude.usage` mapping's four fields summed; else, when `--transcripts` places a transcript for it (`match_transcripts` over all `--store`s, as `report()` does), that transcript's context plus output tokens; else none.
- wall: per change, the sum of its runs' `wall_s` (a missing value counts 0).
- lead: per change with a `ticket.created` event for its id, from that event to the change's latest `merge.done` (itself or a sub-ticket).
- hours are printed `f"{seconds / 3600:.1f}"`. A median-and-range cell is `<median> h (<min> to <max> h)`, using `statistics.median`, or `-` with no values.
- tokens cell: `<median, rounded down to a whole number> (<k> of <n>)`, where k counts the changes whose every run has tokens and the median is over those k, or `- (0 of <n>)`.
- runs cell: `record <r>, transcript <t>, none <x>` over all runs of the window's changes.
- USD cell: `f"{sum:.2f} ({m} runs)"` over those runs whose `claude.total_cost_usd` is a number.

C4. Output, exactly this shape (one blank line between blocks):

```
# factory stats: scorecard

Windows: <prev start> to <prev end>, and <start> to <end>; each from its first bound (inclusive) to its second (exclusive), in UTC. Escapes count when recorded before <end>.

## <name>: target changes            (or "factory work"; or "<store path>: target changes (no instance found)")

| measure | <prev start> to <prev end> | <start> to <end> |
|---|---|---|
| Target changes merged | … | … |      (first cell "Factory work merged" for a factory-work instance)
| Escapes | … | … |
| Operator decisions and interventions per change | … | … |
| … CLI decisions | … | … |
| … interventions | … | … |
| Tokens and wall time per change: wall time, median (range) | … | … |
| … tokens, median (changes whose every run has tokens) | … | … |
| … runs with tokens from a record, a transcript or neither | … | … |
| … USD on the records that carry dollars | … | … |
| Lead time, median (range) | … | … |
```

The `…` that opens a sub-row's name is the single character U+2026. The text in parentheses after the heading and the first row is commentary, not output.

**D. Tests (new files only).** Add `tests/factory/test_scorecard.py` and `tests/factory/test_transcript_record.py` (names are the implementer's choice). Cover: the fixture's figures in both windows and both kinds, with and without transcripts; both C1 refusals; that `--scorecard` writes nothing; B1's five refusals, its event and that the `--issue` text appears nowhere under the store; B2's event and its two refusals; the fence refusing `escape add` unmarked while a run is in flight on an instance's own store (reuse the existing live-store-guard test helpers); A2's transcript record, its two decoys (a transcript naming another run, one whose first timestamp is before the run started) and a reply winning over a transcript; and build.js passing `--transcripts` on both `run finish` commands, driven under node as `tests/factory/_fixtures.py`'s `BUILD_DRIVER` does. The suite must still finish in under three minutes (current truth, harness-suite).

**E. Documents.** `README.md`, prototyped against `1321c17`, whose passages E edits `3e4705a` leaves unchanged; wording may change, but every phrase a scenario greps for stays, and the change adds at most 30 lines net.

E1. "What depends on Claude Code": `Five pieces assume Claude Code.` becomes `Six pieces assume Claude Code.`, and after the `| Catch and cost per role …` row add:

```
| A workflow run's token record (`run finish --transcripts`) | yes | reads the token usage in the transcript Claude Code keeps for the run's agent, under `~/.claude/projects` |
```

E2. "Where a human decides", after the **Record** row:

```
| **Escape** | `factory escape add T-n --issue <link> [--note "<line>"]`, on a ticket with at least one merged sub-ticket | that a merged change later needed a fix or a revert; the scorecard counts it by ticket id. The store keeps only the link's SHA-256 hash, so you can match a record to its issue (hash the link with no trailing newline, for example with `shasum -a 256`) and a reader of the public store cannot read it; anyone who guesses the exact link can confirm it. A note may not contain a link |
| **Intervene** | `factory intervention add --kind <word> [--ticket T-n] [--note "<line>"]` | that you acted outside the CLI, for example a hand commit to the gate config or a run you stopped; the scorecard counts it |
```

E3. "Counting what each role catches and costs": replace the paragraph at `README.md:977-983`, which begins "A run started by `factory drive` carries a cost record" and ends "section A lists it as 'not recorded' in the gate column.", with:

```
Each run keeps a cost record in its `meta.yaml` when it ends. A run started by `factory drive`
records the tokens and dollars its process reported. A run a workflow script started records the
tokens in its agent's transcript, which `run finish --transcripts DIR` finds; the scripts pass the
directory where Claude Code keeps transcripts, `~/.claude/projects` unless `CLAUDE_CONFIG_DIR` moves
it. Transcripts carry no dollars, so that record has none, and "USD from records" covers only the
records that have them. A driver run whose process gave no usable reply records its transcript's
tokens the same way. Runs that ended before this record existed have none: add
`--transcripts ~/.claude/projects` to count them; reading that directory takes about 12 seconds on
this machine. Each model call is counted once. Context tokens are the input, cache-read and
cache-creation tokens together. Without `--transcripts`, a run with no record counts under `none`
in section D, and section A lists it as "not recorded" in the gate column.
```

E4. Same subsection, after the paragraph that ends `the column can undercount.`, add a blank line and:

```
**The scorecard.** `factory stats --scorecard --since WHEN [--until WHEN]` prints only the
scorecard of the north star (`docs/north-star.md`): the numbers that say whether the factory is
working, for the window and for the window of the same length just before it. It prints one table
per store, named after the instance's repository directory, and no path or issue link, so a review
pastes it as printed. An instance whose `instance.yaml` sets `target_is_factory: true` is the
factory building itself: its table counts factory work. Every other instance's merges are target
changes. A change is a ticket closed in the window after at least one of its sub-tickets merged.

| Row | What it counts |
|---|---|
| Target changes merged, or Factory work merged | the changes closed in the window |
| Escapes | those changes with an escape recorded (`factory escape add`) before the report's end, with their ticket ids |
| Operator decisions and interventions per change | the next two rows' sum, divided by the changes; the store records decisions, not time, so this stands in for hours of operator attention |
| … CLI decisions | spec approvals and `resolve` decisions in the window |
| … interventions | in the window: `ticket transition`s by a person that no approval or `resolve` made, spec versions the operator wrote (gate edits and amendments), `decision add` lines, and `factory intervention add` records |
| Tokens and wall time per change | the median of each change's summed run time, in hours; then the median tokens of the changes whose every run has tokens, how many runs took tokens from a record, a transcript (with `--transcripts`) or neither, and the dollars on the records that carry them |
| Lead time | from the ticket's creation to its last merge, in hours: median and range |
```

E5. "What is built and what is not", **Built**, after the entry that begins "- **Counting catch and cost, `factory stats`.**":

```
- **The scorecard, escapes and workflow token records.** `factory stats --scorecard`,
  `factory escape add`, `factory intervention add` and `run finish --transcripts` ("Counting what
  each role catches and costs"). Not yet run on a real store.
```

E6. Bump the status header's date to the merge date. `factory/instance.template.yaml`, after `# effort: {critic: high}`:

```
# Whether this instance's target is the factory itself. `factory stats --scorecard` counts such an
# instance's merges as factory work, in a table of their own; every other instance's are target changes.
# target_is_factory: false
```

### Size and seams (NEEDS-SPLIT, two sub-tickets)

About 520 changed lines in all, about half of them tests, which is over one reviewable PR.
- **S1, the token record:** parts A1 to A4, A's tests, README E1 and E3, and the raised README budget (harness-docs, the four MODIFIED requirements). About 175 lines. E1 and E3 add about 5 lines to a README with one line left under its old cap, so the raised budget ships here. Its scenarios: build-dispatch's three, and the six of the four MODIFIED harness-docs requirements.
- **S2, the scorecard and its records:** parts B, C, the rest of D, README E2, E4, E5, E6 and the template. About 350 lines. Depends on S1, because its Built entry names `run finish --transcripts`. Its scenarios: factory-stats's six, harness-code's, and harness-docs's ADDED one.
Both seams edit `factory/cli.py` and `README.md`, so they are not parallel-safe.

## Tests to change

none. The decisions that change existing behaviour leave every existing test passing:
- A2 keeps a reply record's shape and keeps `claude: null` for an unusable reply with no transcript, so `tests/factory/test_drive.py:82`, `:167` and `:177` hold. The suite runs with a throwaway HOME, so A4's directory holds no transcript naming a test's run.
- A3 changes the scripts' command text, which no test pins (`grep -rn "run finish" tests/factory/*.py` finds only direct CLI calls).
- B's new names in `factory/human.py` are pinned by a current-truth scenario, not a test; that requirement is modified in `specs/harness-code/spec.md`.

