## Proposed change

The change is one PR of about 370 lines: `factory/truth.py` about 200, its tests about 150, and the rest small edits. Parts A and B are the command, C the gate entry, D the documents, and E the restated scenarios, which change only the spec store.

**A. `factory/truth.py`: the replay.** A new module. It imports `factory.specstore`, `factory.store` and `factory.instance`, never `factory.cli`. It reuses `specstore.lines_outside_fences`, `requirement_blocks`, `parse_delta` and `apply_delta` rather than redefining them. It must leave no unused import or name.

- **Inputs.** The store is `--store PATH` (relative paths from the caller's directory, as `stats` does), else `FACTORY_STATE`, else the store of the instance found from the caller's directory. Refuse with exit 2 when `<store>/openspec/specs` is not a directory: `truth check: <store> has no current truth (openspec/specs)`. The checkout under test is `git -C <caller's directory> rev-parse --show-toplevel`, resolved. Refuse when that fails: `truth check: <dir> is not inside a git checkout`. The caller's directory is `instance.caller_cwd()`.
- **Folding.** Find the ticket under test:
  - if the checkout's parent is `<store>/worktrees`, it is the checkout's name;
  - if the checkout is named `wt` and its grandparent is `<store>/runs`, it is the `ticket` in `<checkout>/../meta.yaml`;
  - otherwise there is none.

  Its change id is the `parent` in `<store>/tickets/<ticket>.yaml`, or the ticket itself when the file is missing or `parent` is null. Read only the `status` and `parent` keys of ticket files, so a file holding `id`, `status` and `parent` is enough.

  The folded set holds that change id if `openspec/changes/<id>/` exists. It also holds every directory directly under `openspec/changes/`, `archive` aside, whose own ticket's `status` is not `closed` and which has a ticket with `parent: <id>` and `status: merged`. Fold the set in id order. For each delta part `specs/<cap>/spec.md`, check it against the text folded so far, as `specstore.applies` checks a delta against files: an ADDED name must be absent, a MODIFIED or REMOVED name present. Then apply it with `apply_delta`. On any error, refuse: `truth check: the approved delta of <id> does not apply to current truth: <errors joined by "; ">`. Record every scenario name in an ADDED or MODIFIED block of a folded delta, with that delta's id; a later delta's id wins. A store with no `openspec/changes` folds nothing, a missing `tickets` directory reads as no ticket files, and a capability current truth lacks starts from empty text, as `apply_delta` does (`factory/specstore.py:386-387`).
- **Parsing.** For each capability, in name order, split the folded text into scenario blocks. A block runs from a `#### Scenario: <name>` line to the next `##`, `###` or `####` heading outside fences. Within a block, outside fences:
  - the WHEN is the one line starting `- WHEN `, and its command is the text between the line's first and last backtick;
  - the THEN is the one line starting `- THEN `, with the first fenced block after it when the line ends `lines:`;
  - the GIVEN blocks are the bodies of the fenced blocks that open before the WHEN line;
  - the references are the double-quoted strings on lines other than the WHEN and THEN lines that equal a scenario name anywhere in folded truth, looked up in the same capability first, then in capability order.
- **The exact-print rule** reads the THEN text after `- THEN `:
  ```text
  THEN  := "it prints " ["exactly " | "only "] BODY [", one per line"] [" and exits 0" | ", and exits 0"] ["."]
  BODY  := "these " N " lines:"                     expected = the lines of the fenced block after the THEN
         | [["these "] N " lines" [", one per line"] ": "] LIST
         | WORD " lines, each " ["exactly "] ITEM [", then " LIST]    WORD is two..ten; ITEM repeats WORD times
  LIST  := ITEM ((", then " | ", and " | ", " | " and ") ITEM)*
  ITEM  := "`" text with no backtick "`" [[","] " twice" | [","] " three times"] [" (" note with no backtick or parenthesis ")"]
  ```
  N is digits or a word, and its value is not checked. Expected lines are the ITEM texts in order, verbatim, spaces included. The WHEN passes when its stdout, decoded as UTF-8 with errors replaced, with one trailing newline removed and split at `\n` (empty output is no lines), equals the expected lines. With "and exits 0", its exit status must also be 0; otherwise the status is not compared. Stderr is never compared.
- **Skips**, checked in this order; the first that applies gives the reason:
  1. In a folded delta: `in the approved delta of <id>, which that ticket's verifier checks`.
  2. No WHEN line: `has no WHEN line`. More than one: `has more than one WHEN line`. Fewer than two backticks, or an empty command: `its WHEN is not one backticked command`.
  3. A `--skip-when-contains` text in the command: `its WHEN contains "<text>", which this run skips`.
  4. On a line outside fences containing `GIVEN block`, a double-quoted string that names no scenario: `needs the GIVEN block of "<name>", which current truth does not hold`.
  5. No THEN line, or one the rule cannot read in full: `THEN is not an exact print: <THEN text after "- THEN ">`, or `has no THEN line`.
- **Running.** Each capability gets a fresh directory from `tempfile.mkdtemp`, holding `home/` and `tmp/`, removed at the end. Its scenarios that are not skipped run in file order. Before each one's WHEN, the GIVEN blocks it needs run, in order: each reference's needs first, recursively and never twice on one path, then its own. A block that already ran in this capability is not run again. Every block and WHEN runs as `subprocess.run(["bash", "-c", text], cwd=<checkout>, stdin=DEVNULL, capture_output=True)`. The environment is `os.environ` less every `FACTORY_*` name, with `HOME=<dir>/home` and `TMPDIR=<dir>/tmp`. GIVEN exit statuses are ignored. Capabilities run at the same time, one thread each, through `concurrent.futures.ThreadPoolExecutor`. There is no time limit.
- **Output** goes to stdout, in capability name order and file order, after everything has run:
  - first line: `truth check: <checkout> against <store>; folded: <ids joined by ", ">`, or `folded: none`;
  - one line per reported scenario: `PASS <cap>: <name>`, `FAIL <cap>: <name>` or `SKIPPED <cap>: <name>: <reason>`;
  - under each FAIL, lines that start with two spaces: `  expected:`, then each expected line indented four spaces; `  got:`, then each stdout line indented four spaces, at most 40, then `    … <k> more lines`; `  exit <status>`; and, when stderr is not empty, `  stderr:` and its last five lines indented four spaces;
  - last line: `<n> scenarios: <p> passed, <f> failed, <s> skipped; wall time <t> s`, where t is the whole seconds from the start of parsing to the end of the last run, rounded down.

  The command returns 1 when f > 0, else 0.
- **`--capability NAME`**, repeatable, reports and runs only those capabilities. Their GIVEN references into other capabilities still resolve and run. A name with no `openspec/specs/<name>/spec.md` is refused: `truth check: no capability <name> in current truth`. `--skip-when-contains TEXT` is repeatable.

**B. `factory/cli.py`: the command.** Add the parser `truth` with the required subcommand `check`, its options `--store`, `--capability` and `--skip-when-contains`, and its function from `factory/truth.py`. Put the parser's construction in `factory/truth.py` behind one call from `build_parser()` if that keeps `cli.py` under 910 lines. In `main()`, add `"truth"` to both `("init", "paths", "stats")` tuples, so it refuses `--accept-harness` with the same message and runs before the instance refusal, fence and lock. Return the function's exit code. Add `("truth", "check")` to `READ_ONLY` and update its comment. `cli.py` must stay under 910 lines; the expected count is about 903, from 899.

**C. `.factory/instance.yaml`: the gate entry.** After the suite command, add a comment line and this last entry:
```text
  # then current truth, replayed by the integration checkout's harness; WHENs that run the suite are skipped, since the line above runs it
  - "{integration}/bin/factory truth check --store {integration}/.factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'"
```
`gate_commands()` already replaces `{integration}` with the checkout that has `main` (`factory/compose.py:92-99`). The gate-commands scenario that reads the suite entry matches only a line that starts `  - "uv run` and ends `tests/factory"`, so it still finds one line.

**D. Documents.** The new lines and headings are these, verbatim:
```text
### Replaying current truth with `factory truth check`
- **Replaying current truth, `factory truth check`.**
**Replaying current truth.**
```
- README, "Where a human decides": the read-only list ends `log tail`, `truth check`, `paths` and `stats`. Keep `paths` and `stats` adjacent, which a current-truth scenario greps.
- README: the subsection headed by the first line above, after "Counting what each role catches and costs" and before "## What is built and what is not". In at most six lines of text it says:
  - what the command replays and against which checkout;
  - how a THEN is read (the exact-print rule, with a pointer to `docs/design.md`), and that skipped scenarios are listed with reasons and counted;
  - `--capability` and `--skip-when-contains`;
  - which deltas it folds, and why;
  - that this instance's gate runs it as its last command;
  - that a scenario must not replay a capability that holds it.

  It quotes no figure.
- README "Built": one entry of at most two lines, opening with the second line above and naming "Replaying current truth with".
- README "Accepting a harness revision": add `truth check` to the one sentence that says `init`, `paths` and `stats` refuse `--accept-harness`. Keep it one sentence, so the current-truth count of such sentences stays 1.
- README grows by at most 11 lines.
- `docs/design.md`: a paragraph opening with the third line above, immediately before the paragraph opening `**Routing table.**`. It states the command, the exact-print rule, the skip reasons, the fold, the per-capability environment and the gate entry.
- `docs/design.md`, the paragraph opening `**Only the dispatcher writes a live store during a run.**`: its read-only list ends `log tail`, `truth check`, `paths` and `stats`.
- `docs/design.md`, the paragraph opening `**Role-context block.**`: in its `harness.lock` clause, the sentence on commands that refuse `--accept-harness` names `truth check` too.
- `docs/changelog.md`: one entry, numbered next with no gap, naming #120. It records:
  - the command and the gate entry;
  - the wall-time figures from this spec's Evidence;
  - the five scenarios restated and why, and T-0057's README check restated to measure T-0057's own merge;
  - what was rejected: the runtime's binary, a `{ticket}` placeholder, running a delta's new scenarios, and a contains match.

**E. Restated scenarios, spec store only.** The MODIFIED requirements below change current truth at archive and need no code: the two whose fixtures drop `--model`, the two live-store-guard lists, the `cli.py` limit, and T-0057's README check, which now measures README growth across each `Merge factory/T-0057.<n>` commit against its first parent. The verifier runs each of their scenarios.

**Tests.** A new file, `tests/factory/test_truth.py`, covers the exact-print rule's forms, the skip reasons, the fold and the refusals. It must not change any existing test, and it must keep the suite under three minutes. A test may build a store from files, as the acceptance fixture does.

## Tests to change

none. No test pins `READ_ONLY` or the lock-exempt commands as a whole. `tests/factory/test_small_defects.py:99` and `:121` test the `--accept-harness` refusal for `init`, `paths` and `stats` by name, and still pass. The `cli.py` limit and T-0057's README growth check are current-truth scenarios, not tests, and are restated under E. No test reads this repo's `.factory/instance.yaml`.

