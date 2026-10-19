## Proposed change

Four parts in one PR. The prototype of A to D, with no tests or docs, changed 75 lines of `factory/` (67 added, 8 removed); with E and F the change should stay under 400 lines.

**A. `factory launch-script intake|build` writes a launch copy.**
- New module `factory/launch.py` holds the command, and the one definition of the values `factory config` prints (`models`, `max_rounds`, `state_dir`). `config` in `factory/cli.py` uses that definition too. A new module keeps harness-code's pinned definition lists of `setup.py` and `common.py` unchanged; it must not import `factory.cli`.
- `factory/cli.py`: a `launch-script` subparser with one positional argument, choices `intake` and `build`. Add `("launch-script", None)` to `READ_ONLY`, so the command takes `config`'s path through `main()`: the instance is required, and the harness lock is checked on the instance's own store.
- The command reads `factory/workflows/<name>.js` from the running harness checkout (`instance.HARNESS`). If the line `const LAUNCH = null` does not occur exactly once, it refuses with exit 2 and writes nothing. Otherwise it creates a directory with `tempfile.mkdtemp(prefix="factory-launch-")` and writes `<name>.js` there. The copy is the script with that one line replaced by `const LAUNCH = <json>`. The JSON object, written with `json.dumps(..., ensure_ascii=False)`, holds `written_by` (`"factory launch-script"`), `source` (the script's absolute path), `harness_revision`, `instance` (the instance's path as `factory paths` prints it), `models`, `max_rounds` and `state_dir`. The file is made read-only (0444). The command prints `{"ok": true, "script", "source", "harness_revision", "instance"}`.
- Before writing, it removes earlier launch copies as Decision 15 says: under `tempfile.gettempdir()`, each `factory-launch-*` directory whose modification time is more than 3,600 seconds old and which holds exactly one file, `intake.js` or `build.js`, whose text contains `"written_by": "factory launch-script"`. Any other directory, and any error while checking or removing one, is skipped silently; cleanup never changes the command's exit or output.

**B. Both workflow scripts honour a launch copy.**
- Add, above `INSTANCE`, a comment saying that `factory launch-script` writes a copy of the script with the next line set to the instance's values, and the line `const LAUNCH = null`.
- `const INSTANCE = LAUNCH ? LAUNCH.instance : args.instance`, so `ENV` carries the recorded instance.
- Just before the config step: when `LAUNCH` is set and `args.instance` is given and differs from `LAUNCH.instance`, return `{ ticket, error }`, where the error reads `launch copy written for instance <LAUNCH.instance>, launched with <args.instance>`.
- The config step becomes `const cfg = LAUNCH ? { ok: true, ...LAUNCH } : <today's clerk call of factory config>`. The lines after it stay as they are.
- Update the `// args:` header comments to say a launch copy takes its instance from the copy.

**C. `clerk()` parses a reply spread over lines (both scripts).** Trim the stdout once, try `JSON.parse` on the whole text, and only when that fails run today's last-line scan over its lines. Everything after the parse is unchanged.

**D. `factory resolve <id> --to checks`.**
- In `resolve` (`factory/human.py`), a `--to checks` branch, written inside `resolve` so `human.py`'s top-level definitions stay as harness-code pins them. Before any write it requires: status `parked`; `parked.from == "ready-for-implementer"`; a reason starting `harness-bug:`; and the newest implementer run of the ticket started after the ticket last entered `ready-for-implementer` and finished `READY-FOR-REVIEW`. Otherwise it refuses with exit 2, writing nothing, with `--to checks applies to a sub-ticket parked by a harness-bug from ready-for-implementer after its implementer run finished READY-FOR-REVIEW; <id> is <status> (<reason or 'no park'>)`. Any other `--to` value is refused with `--to accepts only spec-gate or checks`.
- The "newest implementer run since it last entered ready-for-implementer" test reads the event log through `store.log_lines` in file and line order. A move into that state is an event of the ticket whose `to`, or for `ticket.created` whose `status`, is `ready-for-implementer`. The newest implementer `run.started` must come after the last such move, and that run's `run.finished` must carry `READY-FOR-REVIEW`. Match moves by their field, not by event name: harness-code pins the `"ticket.transition"` literal to one place in `store.py`.
- On acceptance: read the branch tip into the ticket exactly as `ticket head` does, conflict bookkeeping included. Apply the `pr:init` round step. Then `move("checks-in-flight", "to-checks", {"head": head})`, which writes the history entry, `resolve-<n>.yaml` and the `human.resolved` event.
- Shared definitions, placed so harness-code's pins hold:
  - `ticket head`'s body (`factory/gates.py:12-33`) becomes one function in `factory/store.py`, used by `ticket head` and the route. It keeps its single `gitops.repo_root()` call, imported lazily inside the function, as `store.py` already imports `instance`. The site count stays 12, and `gates.py` keeps its definitions; `ticket_head` only prints the function's result.
  - `_apply_round` moves from `factory/cli.py` to `factory/store.py` as one definition, used by `ticket transition` and the route. `human.py` may not import `factory.cli`.
  - The log query lives in `factory/store.py` beside `log_lines`.
- The parser's `--to` gets help text naming `spec-gate` and `checks`.

**E. Tests: new files only, under `tests/factory/`.** Name them for what they test, for example `test_launch_copy.py`. Use the suite's helpers through relative imports (`._cli`, `._fixtures`) and edit no existing file. Each test keeps to its own `tmp_path`, with `TMPDIR` pointed inside it, because the suite runs in parallel. Cover:
- a launch copy of each script is a one-line change naming the revision and instance; `launch-script` is refused where `config` is, writing no copy; and it runs unmarked while a run is in flight;
- `launch-script` removes a launch copy over an hour old and keeps a recent copy and a `factory-launch-*` directory that holds no launch copy;
- `build.js`, run from a launch copy under node with a stand-in clerk that retypes a model in the config reply, launches every role on the instance's model;
- both scripts proceed when every clerk reply is pretty-printed;
- `resolve --to checks` on #112's park returns the sub-ticket to its checks at the branch tip, and is refused, writing nothing, on each other park the scenarios list.

**F. Documents.** README has 2 lines of room under its 1,110-line budget (1,108 lines on 308d038). Each README edit below names the lines it replaces; together they add at most one line.
- `README.md`:
  - "Starting a run": replace `README.md:699-711`, the `paths` block and the paragraph that launches the scripts (13 lines), with at most 13 lines that say: the session runs `$RUNTIME/bin/factory launch-script intake` (or `build`) and passes the printed `script` as `scriptPath`; a launch copy is the script with the instance's models, round limits and store written into one line, so no agent relays them, and it names the harness revision and instance it was written for; it has not yet run on a real ticket; args are `{ticket, repo: <runtime>}`, since the copy carries the instance; and, kept from today's text, the `inlineRoles: true` advice and that the intake script has nothing to do past the spec gate. `factory paths` stays documented in "Where things live" (`README.md:1096`). A draft that fits in 13 lines:

    ~~~
    A Claude Code session in the target repo has the runtime write a launch copy of the script:

    ```
    $RUNTIME/bin/factory launch-script intake   # or build; prints the copy's path as "script"
    ```

    A launch copy is the script with the instance's models, round limits and store written into one
    line, so no agent relays them; it names the harness revision and instance it was written for. It
    has not yet run on a real ticket. The session calls the Workflow tool with `scriptPath` set to the
    printed `script` and args `{ticket, repo: <runtime>}`; after the spec gate, the same with `build`.
    Add `inlineRoles: true` on every target for now: `agents/` ships agent definitions only for the
    intake roles and the planner, so a build without it fails at the first implementer call. "What
    depends on Claude Code" says what it changes. The intake script has nothing to do past the gate.
    ~~~

  - "Where a human decides": add `launch-script` to the sentence "A write is any command except ...;" at `README.md:831-832`, keeping that sentence's form, rewrapped within its paragraph with no added line. Add `--to checks` to the **Unstick** row (`README.md:859`, one table line), with what it is for (a `harness-bug:` park from ready-for-implementer after the implementer finished READY-FOR-REVIEW: the sub-ticket returns to its checks at its branch tip) and that it has not yet run on a real ticket, as README's "Maintaining this page" rule asks of every entry.
  - The run-start sentence at `README.md:251-252`, about a model the clerk misreported, also says that a launch copy carries the models itself. Its paragraph (`README.md:249-254`) may grow by one line at most; this is the one added line.
  - Bump the status date at `README.md:9` in place.
  - If the text cannot fit these bounds, stop and report it rather than cutting other README content or exceeding 1,110 lines.
- `docs/design.md`:
  - line 44, limit (1): one sentence on the launch copy and on parsing a reply spread over lines;
  - line 64: add `launch-script` to the read-only list;
  - line 109: the `--to checks` route beside the harness-bug ruling rule.
  - None of these lines is a prompt block, so `docs/prompts/` does not change.
- `docs/changelog.md`: one entry with the next free number, opening `<n>. After issue #109 ` and naming #112, `launch-script` and `--to checks`.

## Tests to change

none. On the prototype of parts A to D, the suite printed `594 passed` with no existing test changed. No existing test pins `--to accepts only spec-gate`, the read-only list or the clerk's parse.

