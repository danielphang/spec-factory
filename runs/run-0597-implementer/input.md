## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`: `dev/issues.md`, this repo's issue index, kept live; and the build spec, its plan and the
  P0 walking skeleton, frozen as history from building the harness, which no change updates;
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, and any `docs/prompts/` file whose
block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0597-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0597-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0059.1` (branch `factory/T-0059.1`, base `db28eb1451e35171b6de62f09d5e378c46a715fa`, head `db28eb1451e35171b6de62f09d5e378c46a715fa`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0059.1

T-0059.1 / `factory truth check` replays every current-truth scenario, and the gate runs it
Depends on: none
Parallel-safe: yes

Parent: T-0059, approved spec v4. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time
- The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed
- --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused
- Capabilities run at the same time
- Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped
- On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped
- The implementer's worktree folds the same deltas
- From the integration branch only an open ticket's delta with a merged sub-ticket is folded
- A folded delta that no longer applies is refused, naming its ticket, and nothing runs
- truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing
- truth check refuses --accept-harness and names config
- The instance's last gate command is the truth check on the integration checkout's store
- The truth check on this checkout reports no failure in the capabilities this change restates
- README, the design doc and the changelog describe the truth check
- README, the design doc and the changelog describe the refusal route
- Implementer and verifier run prompts carry the declared-path rule
- Status transitions write the same events and history entries
- Spec pinning and planner-run refusals keep their text
- The dispatcher parks a refused store command with the same reason
- The spec parser gives the same result as the base on every spec in the store
- The refactored harness has no unused imports or variables
- The harness suite passes and no existing test file changes
- The drift checks live in factory/drift.py
- The shared helpers and the live-store fence live in factory/common.py
- Instance and store setup live in factory/setup.py
- The gates live in factory/gates.py
- The human decisions live in factory/human.py
- factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines
- Unmarked writes from inside the target are refused while a run is in flight, init included
- The refusal names the throwaway store and not the marker
- A harness acceptance is refused while a run is in flight
- A launch copy is written unmarked while a run is in flight, and the target is unchanged
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance
- Without the flag paths and stats still run under another lock, and config still accepts a revision
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v4, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0059/v4.md`

=== proposal.md
## Problem

A change merged into this repo can quietly break behaviour that an earlier change was required to keep. The operator, who approves every spec and merge on the understanding that this required behaviour still holds, has no way to see that it no longer does.

The required behaviour is written down. The factory (the pipeline of agents that turns tickets into merged changes here) keeps a record called current truth: one spec per area of behaviour, called a capability, kept in the store (the factory's record of tickets, runs and specs). Each spec holds scenarios. A scenario is a shell command, its WHEN, and the output the command must print, its THEN. While a ticket is built, its verifier (the agent that checks a change against its spec) runs that ticket's own scenarios once. When the ticket closes, its scenarios join current truth, and nothing runs them again.

So nothing stops a later change from breaking them. The merge gate, the commands every change must pass before it merges, runs only a whitespace check and the test suite. Each verifier runs only its own spec's scenarios. A breakage stays hidden until someone happens to run the old scenario by hand. It has happened here: replayed today, five scenarios fail on `main`. Four broke when a later change made the harness refuse an agent model that the instance's configuration does not name; their setup scripts still pass a different one. The fifth, which joined current truth on 2026-10-25, checks how much its own change grew the README by comparing the checkout with `main`. On `main` that comparison is empty, and on any later branch it counts that branch's edits, so the scenario can pass only on its own change's branch. It has also happened on the Nanobot target, the other repository this factory builds.

The operator asked for two things. One is a command, `factory truth check`, that replays every scenario against a checkout and reports each result. The other is for this repo's merge gate to run that command, so that a change that breaks any scenario cannot merge. This change also rewrites the five broken scenarios, so the gate's first run is clean.

Two limits shape the command. First, current truth lags the code. A ticket is built as one or more sub-tickets, pieces that each merge on their own, and its scenarios join current truth only when the whole ticket closes, which can be days after its first sub-ticket merged. The check must not report those intended changes as regressions. Second, cost. Replaying the scenarios one after another took about eleven minutes when there were 306 of them, and an agent's single shell command is cut off at ten. Two things bring the gate's replay of today's 325 down to about two minutes on top of the suite: capabilities run at the same time, and the replay leaves out the three scenarios that themselves run the whole test suite. That second part is the operator's decision, because the same gate runs that suite anyway.

## Root cause

No component replays current truth. `factory/specstore.py` parses deltas and folds them into current truth only at archive (`apply_delta`, `factory/specstore.py:385`; `archive`, `:398`). `gate_commands` in `.factory/instance.yaml` holds no replay, and the verifier's prompt has no rule for comparing a print, so each verifier judged THENs by eye. T-0057's growth check measured README against `main` from whatever checkout ran it; its verifier ran it once, on T-0057.1's branch, where that measure was right.

## Out of scope

- Rewriting prose THENs as exact prints, and fixing scenarios that only describe their own change's diff.
- Adopting the check on another target, which is that target's owner's decision (requirement D).
- Reusing the check in `factory fast-track` (#87).
- A per-scenario time limit, a `--jobs` setting and a `--ticket` option: the gate needs none of them.
- Reading a scenario's preconditions, such as "with `node` on `PATH`": a missing tool makes its scenario fail.
- Any change to `factory/specstore.py`, `factory/compose.py`, a role prompt or `docs/prompts/`.

## Open questions

none. The first version's question, whether the gate's replay skips the three scenarios that run the whole harness suite, is answered under Decisions.

## Decisions

- The exact-print rule. A THEN of the form "it prints [exactly|only] <lines>" lists its expected lines in backticks, joined by ", then", ", and", ", " or " and". The list may open with "[these] N lines:", or read "N lines, each `X`"; an item may be followed by "twice" or "three times", with or without a comma before it, or by a parenthetical note without backticks; the THEN may end ", one per line" or " and exits 0". A THEN ending "these N lines:" takes them from the fenced block after it. The WHEN's stdout, less one trailing newline, must equal those lines exactly. Measured at `7bfbe8f`: 296 of 325 THENs read, and every one that ran and passed compared exactly.
- "twice" without a comma is new in this version: two of T-0057's THENs use it, and both pass when read so.
- "it prints `X`" reads the same as "it prints exactly `X`". Stderr is never compared. The exit status is compared only when the THEN says "and exits 0". Rejected: a contains match, which no passing scenario needs and which would hide extra output.
- A THEN the rule cannot read in full, including one that ends in further sentences, is listed SKIPPED with the THEN's text as its reason (29 at `7bfbe8f`). Rejected: reading such trailing sentences as notes, which could pass a scenario on part of its claim.
- A scenario's GIVEN blocks are its fenced blocks before its WHEN line. A double-quoted string outside fences, other than in the WHEN and THEN lines, that names a scenario anywhere in current truth makes that scenario's blocks run first. Each block runs once per capability, and a named block current truth lacks makes its scenario SKIPPED.
- Every block and WHEN runs as `bash -c`, using the `bash` on `PATH`, from the top of the checkout under test, with stdin closed. The environment is the caller's, with every `FACTORY_` variable removed and HOME and TMPDIR set to fresh directories per capability. Capabilities run at the same time; within one, scenarios run in file order. This follows the standing decision that role processes never inherit `FACTORY_DISPATCH`.
- On a ticket's checkout, recognised by the store's own layout (`worktrees/<id>`, or `runs/<run>/wt` and that run's `meta.yaml`), the check folds the approved delta of that ticket's parent, or of the ticket itself if it has no parent. Rejected: a `{ticket}` placeholder in the gate command, which only an upgraded runtime would fill in.
- The check also folds the delta of every unarchived change whose ticket is not closed and has a merged sub-ticket, because that code is on `main` before its scenarios reach current truth. A closed ticket's unarchived change is not folded, as was decided for T-0030.
- A scenario in an ADDED or MODIFIED requirement of a folded delta is listed SKIPPED, naming the ticket, because that ticket's verifier checks it. Rejected: running the new forms, which fails a sub-ticket on scenarios a sibling has yet to build.
- A folded delta that no longer applies to current truth refuses the check with exit 2, naming the ticket.
- `factory truth check` only reads. Like `stats`, it skips the instance refusal, the live-store fence and the harness lock, and it refuses `--accept-harness`, which follows the 2026-10-23 standing decision on commands that skip the lock. The two live-store-guard requirements that list those commands are restated with `truth check` added.
- This instance's gate runs the integration checkout's `bin/factory` on the integration checkout's store, as its last gate command. This follows `gate_commands`' rule that a change cannot weaken its own gate. It also needs no runtime upgrade, because it runs `main`'s code, which is outside the harness lock. Rejected: the runtime's `bin/factory`, which would leave the gate broken between merge and upgrade.
- `--skip-when-contains TEXT` skips, and lists, each scenario whose WHEN contains TEXT. The gate passes the suite command's text.
- Answer 1 (operator, 2026-10-25, standing): the gate's replay skips the three scenarios that run the whole harness suite and have exact-print THENs, because the same gate already runs that suite. Every gate run lists them as skipped, and `factory truth check` without `--skip-when-contains` runs them. The same text matches eleven suite-running scenarios whose THENs are prose, which are skipped either way; the gate lists all 14 with the WHEN reason, which is checked before the THEN. Rejected: running them in the gate (482 s at `3e4705a`, 80% of the ten-minute command limit), and leaving the gate unchanged for now.
- This change restates role-escalations' "The implementer and verifier leave declared protected paths out of ESCALATIONS" and harness-code's "Sharing an operation changes no refusal, park reason, event or parse result" with `--model` dropped from their setup, so the five scenarios T-0050 broke pass and the gate's first run is clean. The instance is the only source of a role's model, so the fixtures pass none.
- This change restates a T-0057 requirement, harness-docs' "The documents record the format check at spec add and its route back to the spec writer", as the operator directed at the gate on 2026-10-26. Its scenario measures README growth across each `Merge factory/T-0057.<n>` commit against its first parent, as harness-suite's T-0045 and T-0051 scenarios measure their own merges, and prints `growth=none` when no such commit is reachable. The rest of the requirement and its scenario are unchanged. This follows T-0048's standing rule that no scenario checks what one change left untouched against `main`. Rejected: dropping the growth clause, which would lose T-0057's limit.
- `factory/cli.py`'s limit rises from under 900 to under 910 lines, and the replay lives in `factory/truth.py`. This change adds about four lines to `cli.py` (an import, one call that builds the `truth` parser, one `READ_ONLY` entry), leaving it near 903 from 899. Rejected: compressing unrelated lines to make room.
- README grows by at most 11 lines, to at most 1,224, within its 1,225-line budget. With T-0057's check restated, that growth no longer fails a T-0057 scenario.
- The scenario that runs the check on this repo's live store names four capabilities. A standing scenario that replayed all of current truth would replay itself inside every later gate, and would double the gate's time. Measured on the branch, the four-capability run takes 6 s from this change's checkout, and leaves the replay's wall time at 129 s.

## Risk

- Every later sub-ticket's implementer and verifier runs the new gate command. On this machine that is about 126 s to 129 s more per run at `7bfbe8f`, `db28eb1` and on the branch (129 s with this change's gate-commands scenario run), and was 157 s at `3e4705a`, on top of the suite's 119 s. The slowest capability, build-dispatch, sets that figure; a slower scenario added to it raises every gate.
- Any current-truth scenario that fails now blocks every merge until a ticket fixes or restates it. That is the point of the change. It also means a scenario that depends on the machine, such as one that needs `node`, fails every gate where that tool is missing.
- The gate runs whatever is in `~/dev/spec-factory`'s working tree and `.venv`, outside the harness lock. An uncommitted edit there, or a `.venv` out of step with `uv.lock`, changes every gate's replay.
- Scenarios run with the verifier's environment, minus `FACTORY_` variables. A scenario that writes outside its temporary directories can still do so; the replay adds no isolation the verifier lacked.
- A later scenario that runs `truth check` over a capability holding itself recurses until the command limit stops it. This spec's own scenarios avoid that, as its last Decision says; README warns.
- Restated requirements: this change restates two requirements each in harness-code and live-store-guard, one in role-escalations, and one in harness-docs. The harness-docs one is T-0057's, approved and archived on 2026-10-25; this change narrows its growth measure to T-0057's own merge and changes nothing else in it. No open ticket's delta touches any of the six.
- A scenario that measures a change against `main` from whatever checkout runs it passes only on that change's branch. Two more such scenarios are in current truth, with prose THENs, so the replay skips them (harness-code's "Every definition keeps its exact text, and the split adds at most 100 lines" and harness-suite's "The only existing test file changed is the stats test"). A later exact-print one would fail the gate as T-0057's did.

Protected paths: `factory/truth.py`, `factory/cli.py`, `.factory/instance.yaml`

## Operator steps

1. After the merge, from `~/dev/spec-factory` on `main`, run the gate's replay once: `bin/factory truth check --store .factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'`. Its last line should report `0 failed`. If it does not, every later gate fails: file a ticket for the failing scenario, or take the entry out of `gate_commands` until one lands.

=== design.md
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

=== specs/truth-check/spec.md
## ADDED Requirements

### Requirement: factory truth check replays each current-truth scenario under bash in the checkout under test and fails on a wrong print
`factory truth check` SHALL run, under `bash`, from the top of the git checkout that holds the caller's directory, the WHEN of every current-truth scenario it can read, after the GIVEN blocks that scenario needs. It SHALL compare the WHEN's standard output with the THEN by the exact-print rule, and print one line per scenario: `PASS`, `FAIL` or `SKIPPED`, its capability and its name. It SHALL also print the expected and printed lines under each failure, and a last line with the counts and the wall time in seconds. It MUST exit 1 when any scenario fails, and 0 otherwise. The first line SHALL name the checkout, the store and the folded deltas. `--capability NAME`, repeatable, SHALL limit the run to those capabilities. Capabilities SHALL run at the same time, each in its own fresh HOME and TMPDIR, with no `FACTORY_` variable in its scenarios' environment. An unknown capability, a store with no `openspec/specs`, and a caller outside a git checkout MUST be refused with exit 2.

#### Scenario: Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0059-truth.sh <<'EOF'
# Sourced from the repo root of the checkout under test. Builds a scratch target $G (a git repo
# whose main prints `hello` and whose branch factory/T-0001.1 prints `hello, world`) and a scratch
# store $S holding three current-truth capabilities (alpha, beta, gamma), five tickets and four
# change folders. T-0001 (sub-ticket T-0001.1 at its checks) and T-0002 (sub-ticket T-0002.1
# merged) are open; T-0003 is closed with a merged sub-ticket; T-0004 is open with nothing merged.
# $K is a checker's checkout of T-0001.1 under $S/runs/, $W the implementer's worktree under
# $S/worktrees/. Defines `check [args]`: runs truth check on $S from the current directory with
# T59_HOME and T59_TMP set to the caller's HOME and TMPDIR, output in $T/o, exit code in $T/x.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; S=$T/s; G=$T/tgt; F=$(printf '\140\140\140')
spec() { mkdir -p "$(dirname "$1")"; sed "s/^FENCE/$F/" > "$1"; }
git init -q -b main $G && cd $G && git config user.email f@x && git config user.name f
echo 'echo hello' > greet.sh && git add -A && git commit -q -m init
git checkout -q -b factory/T-0001.1 && echo 'echo hello, world' > greet.sh && git commit -q -am world && git checkout -q main
cd - >/dev/null
mkdir -p $S/tickets $S/runs/run-0002-verifier $S/worktrees
for t in 'T-0001 planned null' 'T-0001.1 checks-in-flight T-0001' 'T-0002 planned null' 'T-0002.1 merged T-0002' \
         'T-0003 closed null' 'T-0003.1 merged T-0003' 'T-0004 planned null'; do
  set -- $t; printf 'id: %s\nstatus: %s\nparent: %s\n' $1 $2 $3 > $S/tickets/$1.yaml
done
printf 'role: verifier\nticket: T-0001.1\n' > $S/runs/run-0002-verifier/meta.yaml
git -C $G worktree add -q --detach $S/runs/run-0002-verifier/wt factory/T-0001.1 && K=$S/runs/run-0002-verifier/wt
git -C $G worktree add -q $S/worktrees/T-0001.1 factory/T-0001.1 && W=$S/worktrees/T-0001.1
spec $S/openspec/specs/alpha/spec.md <<'EOS'
# alpha

## Requirements

### Requirement: Alpha greets
The greeting SHALL be printed.

#### Scenario: The greeting is printed exactly
- WHEN `(sh greet.sh)`
- THEN it prints exactly `hello`

### Requirement: Alpha reads its THENs
The check SHALL read each THEN by the exact-print rule.

#### Scenario: Two lines are read as a list
- WHEN `(sh greet.sh | sed 's/,.*//'; echo bye)`
- THEN it prints `hello`, then `bye` (the farewell second)

#### Scenario: A wrong greeting fails
- WHEN `(echo hullo)`
- THEN it prints exactly `hello`

#### Scenario: An exit status counts only when the THEN names it
- WHEN `(echo ok; exit 3)`
- THEN it prints `ok` and exits 0

#### Scenario: An exit status the THEN does not name is not compared
- WHEN `(echo ok; exit 3)`
- THEN it prints exactly `ok`

#### Scenario: A block of lines is compared line by line
- WHEN `(printf 'a  b\nc\n')`
- THEN it prints exactly these 2 lines:

FENCE
a  b
c
FENCE

#### Scenario: A counted list of lines is read
- WHEN `(echo one; echo two)`
- THEN it prints exactly two lines: `one`, then `two`

#### Scenario: Lines that repeat one text are read
- WHEN `(echo same; echo same)`
- THEN it prints exactly two lines, each `same`

#### Scenario: A prose THEN is skipped
- WHEN `(sh greet.sh)`
- THEN it prints a friendly greeting

#### Scenario: A fixture is written once
- GIVEN the fixture file written by the block below, run once at column 0 as shown

FENCEsh
echo given >> ${TMPDIR:-/tmp}/t0059-given.txt
FENCE

- WHEN `(cat ${TMPDIR:-/tmp}/t0059-given.txt)`
- THEN it prints exactly `given`
EOS
spec $S/openspec/specs/beta/spec.md <<'EOS'
# beta

## Requirements

### Requirement: Beta reuses a fixture and checks its environment
Each scenario SHALL run in its own environment.

#### Scenario: Another capability's fixture is reused
Needs the GIVEN block of "A fixture is written once" (alpha) run once.
- WHEN `(cat ${TMPDIR:-/tmp}/t0059-given.txt)`
- THEN it prints exactly `given`

#### Scenario: A scenario runs with a fresh HOME and TMPDIR and no FACTORY_ variable
- WHEN `(echo "home=$([ "$HOME" = "$T59_HOME" ] && echo caller || echo fresh) tmp=$([ "${TMPDIR:-/tmp}" = "$T59_TMP" ] && echo caller || echo own) factory=$(env | grep -c '^FACTORY_')")`
- THEN it prints exactly `home=fresh tmp=own factory=0`

#### Scenario: A missing fixture is skipped
Needs the GIVEN block of "No such scenario" run once.
- WHEN `(echo x)`
- THEN it prints exactly `x`

#### Scenario: A scenario can be skipped by its WHEN
- WHEN `(echo slow-marker)`
- THEN it prints exactly `slow-marker`
EOS
spec $S/openspec/specs/gamma/spec.md <<'EOS'
# gamma

## Requirements

### Requirement: Gamma counts
Gamma SHALL count.

#### Scenario: Gamma prints one
- WHEN `(echo 1)`
- THEN it prints exactly `1`

### Requirement: Gamma stays
Gamma SHALL stay.

#### Scenario: Gamma prints two
- WHEN `(echo 2)`
- THEN it prints exactly `2`
EOS
spec $S/openspec/changes/T-0001/specs/alpha/spec.md <<'EOS'
## MODIFIED Requirements

### Requirement: Alpha greets
The greeting SHALL name the world.

#### Scenario: The greeting names the world
- WHEN `(sh greet.sh)`
- THEN it prints exactly `hello, world`
EOS
spec $S/openspec/changes/T-0002/specs/gamma/spec.md <<'EOS'
## MODIFIED Requirements

### Requirement: Gamma counts
Gamma SHALL count to ten.

#### Scenario: Gamma prints one, then ten
- WHEN `(echo 1; echo 10)`
- THEN it prints exactly `1`, then `10`
EOS
spec $S/openspec/changes/T-0003/specs/gamma/spec.md <<'EOS'
## REMOVED Requirements

### Requirement: Gamma stays
Closed without archive.
EOS
spec $S/openspec/changes/T-0004/specs/gamma/spec.md <<'EOS'
## REMOVED Requirements

### Requirement: Gamma counts
Nothing of T-0004 has merged.
EOS
check() { T59_HOME=$HOME T59_TMP=${TMPDIR:-/tmp} $B truth check --store $S "$@" > $T/o 2>$T/e; echo $? > $T/x; }
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check; echo "exit=$(cat $T/x)"; sed -nE 's/^(PASS|FAIL|SKIPPED) (alpha|beta): ([^:]*).*/\1 \3/p' $T/o; tail -1 $T/o | sed -E 's/wall time [0-9]+ s$/wall time N s/')`
- THEN it prints exactly these 16 lines:

```
exit=1
PASS The greeting is printed exactly
PASS Two lines are read as a list
FAIL A wrong greeting fails
FAIL An exit status counts only when the THEN names it
PASS An exit status the THEN does not name is not compared
PASS A block of lines is compared line by line
PASS A counted list of lines is read
PASS Lines that repeat one text are read
SKIPPED A prose THEN is skipped
PASS A fixture is written once
PASS Another capability's fixture is reused
PASS A scenario runs with a fresh HOME and TMPDIR and no FACTORY_ variable
SKIPPED A missing fixture is skipped
PASS A scenario can be skipped by its WHEN
16 scenarios: 11 passed, 2 failed, 3 skipped; wall time N s
```

#### Scenario: The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check; head -1 $T/o | sed "s#$G#G#; s#$S#S#"; sed -n '/^FAIL alpha: A wrong greeting fails$/,/^[A-Z]/p' $T/o | sed '1d;$d')`
- THEN it prints exactly `truth check: G against S; folded: T-0002`, then `  expected:`, then `    hello`, then `  got:`, then `    hullo`, then `  exit 0`

#### Scenario: --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && mkdir $T/empty && cd $G && check --capability gamma; echo "one: exit=$(cat $T/x) $(grep -cE '^(PASS|FAIL|SKIPPED) ' $T/o) $(grep -cE '^(PASS|FAIL|SKIPPED) gamma: ' $T/o)"; check --capability nope; echo "unknown: exit=$(cat $T/x) named=$(grep -c nope $T/e)"; $B truth check --store $T/empty >/dev/null 2>&1; echo "no-truth: exit=$?"; cd $T/empty && check; echo "no-git: exit=$(cat $T/x)")`
- THEN it prints exactly `one: exit=0 2 2`, then `unknown: exit=2 named=1`, then `no-truth: exit=2`, then `no-git: exit=2`

#### Scenario: Capabilities run at the same time
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once. Each of the two capabilities holds one scenario that sleeps three seconds.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && for c in one two; do mkdir -p $T/p/openspec/specs/$c && printf '# %s\n\n## Requirements\n\n### Requirement: %s sleeps\nIt SHALL sleep.\n\n#### Scenario: %s sleeps three seconds\n- WHEN `(sleep 3; echo slept)`\n- THEN it prints exactly `slept`\n' $c $c $c > $T/p/openspec/specs/$c/spec.md; done; cd $G && $B truth check --store $T/p | tail -1 | sed -nE 's/^2 scenarios: 2 passed, 0 failed, 0 skipped; wall time ([0-9]+) s$/\1/p' | awk '{print ($1 < 5 ? "together" : "one after another")}')`
- THEN it prints exactly `together`

### Requirement: A scenario the check cannot run mechanically is listed as skipped with its reason and counted
A scenario whose THEN the exact-print rule cannot read in full, whose named GIVEN block current truth does not hold, or whose WHEN contains a text given with `--skip-when-contains` MUST be listed as `SKIPPED` with its reason, and counted as skipped in the last line. It MUST never be counted as passed.

#### Scenario: Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check --skip-when-contains slow-marker; grep '^SKIPPED ' $T/o | sed 's/^SKIPPED //'; tail -1 $T/o | sed -E 's/wall time [0-9]+ s$/wall time N s/')`
- THEN it prints exactly these 5 lines:

```
alpha: A prose THEN is skipped: THEN is not an exact print: it prints a friendly greeting
beta: A missing fixture is skipped: needs the GIVEN block of "No such scenario", which current truth does not hold
beta: A scenario can be skipped by its WHEN: its WHEN contains "slow-marker", which this run skips
gamma: Gamma prints one, then ten: in the approved delta of T-0002, which that ticket's verifier checks
16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s
```

### Requirement: On a ticket's checkout the check folds that ticket's approved delta, and every unarchived delta with merged code, before it runs
When the checkout under test is a ticket's implementer worktree (`<store>/worktrees/<id>`) or checker checkout (`<store>/runs/<run>/wt`), `factory truth check` SHALL fold into current truth the approved delta of that ticket's parent, or of the ticket itself when it has no parent, as archive folds it. From any checkout it SHALL also fold the delta of every change not yet archived whose ticket is not closed and has a merged sub-ticket. Each scenario in an ADDED or MODIFIED requirement of a folded delta SHALL be listed SKIPPED, naming that ticket. A folded delta that does not apply to current truth MUST be refused with exit 2, naming its ticket, and no scenario run.

#### Scenario: On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once. On T-0001.1's branch the greeting is `hello, world`, which T-0001's delta expects; current truth still expects `hello`.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $K && check; head -1 $T/o | sed "s#$K#K#; s#$S#S#"; grep -E '^(PASS|FAIL|SKIPPED) (alpha: The greeting|gamma: )' $T/o; tail -1 $T/o | sed -E 's/wall time [0-9]+ s$/wall time N s/')`
- THEN it prints exactly these 5 lines:

```
truth check: K against S; folded: T-0001, T-0002
SKIPPED alpha: The greeting names the world: in the approved delta of T-0001, which that ticket's verifier checks
SKIPPED gamma: Gamma prints one, then ten: in the approved delta of T-0002, which that ticket's verifier checks
PASS gamma: Gamma prints two
16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s
```

#### Scenario: The implementer's worktree folds the same deltas
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $W && check; head -1 $T/o | sed "s#$W#W#; s#$S#S#"; grep -E '^(PASS|FAIL|SKIPPED) alpha: The greeting' $T/o)`
- THEN it prints exactly `truth check: W against S; folded: T-0001, T-0002`, then `SKIPPED alpha: The greeting names the world: in the approved delta of T-0001, which that ticket's verifier checks`

#### Scenario: From the integration branch only an open ticket's delta with a merged sub-ticket is folded
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once. T-0001 has nothing merged, T-0003 is closed and T-0004 has nothing merged; T-0004's delta would remove "Gamma counts".
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check; grep -E '^(PASS|FAIL|SKIPPED) (alpha: The greeting|gamma: )' $T/o)`
- THEN it prints exactly `PASS alpha: The greeting is printed exactly`, then `SKIPPED gamma: Gamma prints one, then ten: in the approved delta of T-0002, which that ticket's verifier checks`, then `PASS gamma: Gamma prints two`

#### Scenario: A folded delta that no longer applies is refused, naming its ticket, and nothing runs
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && printf 'id: T-0005\nstatus: planned\nparent: null\n' > $S/tickets/T-0005.yaml && printf 'id: T-0005.1\nstatus: merged\nparent: T-0005\n' > $S/tickets/T-0005.1.yaml && mkdir -p $S/openspec/changes/T-0005/specs/gamma && printf '## MODIFIED Requirements\n\n### Requirement: Gamma is gone\nGamma SHALL go.\n' > $S/openspec/changes/T-0005/specs/gamma/spec.md && cd $G && check; echo "exit=$(cat $T/x) named=$(grep -c T-0005 $T/e) results=$(grep -cE '^(PASS|FAIL|SKIPPED) ' $T/o)")`
- THEN it prints exactly `exit=2 named=1 results=0`

### Requirement: truth check only reads, so it runs during a run, from inside the store and under any harness revision, and refuses --accept-harness
`factory truth check` MUST run on an instance's own store while a run is in flight there, from inside that store's `runs/`, and when the instance's `harness.lock` names another revision, and it MUST write nothing to the store or the instance. With no `--store` it SHALL read the store of the instance found from the caller's directory. Given `--accept-harness`, it MUST be refused with exit 2 and `{"ok": false, …}` on stdout, naming `factory --accept-harness <sha> config` with the same sha.

#### Scenario: truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" (current truth, live-store-guard) run once. T-0001's triage run is in flight on the target's own store, and the lock is overwritten to name another revision, so an ordinary read is refused.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && mkdir -p $S/openspec/specs && echo 0000000000000000000000000000000000000000 > $T/tgt/.factory/harness.lock && S0=$(snap); cd $T/tgt && $B truth check > $T/o1 2>&1; a=$?; cd $W && $B truth check --store $S > $T/o2 2>&1; b=$?; cd $T/tgt && $B ticket show T-0001 >/dev/null 2>&1; c=$?; echo "here=$a inside=$b store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) total=$(tail -1 $T/o1 | sed 's/;.*//') locked=$c")`
- THEN it prints exactly `here=0 inside=0 store=unchanged total=0 scenarios: 0 passed, 0 failed, 0 skipped locked=2`

#### Scenario: truth check refuses --accept-harness and names config
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && $B --accept-harness 0123456789abcdef0123456789abcdef01234567 truth check --store $S > $T/o 2>$T/e; echo "exit=$? hint=$(grep -cF 'factory --accept-harness 0123456789abcdef0123456789abcdef01234567 config' $T/e) json=$(tail -1 $T/o | grep -c '"ok": false')")`
- THEN it prints exactly `exit=2 hint=1 json=1`

=== specs/gate-commands/spec.md
## ADDED Requirements

### Requirement: This instance's gate replays current truth with the integration checkout's harness
`.factory/instance.yaml` SHALL list, as its last gate command, `factory truth check` run by the integration checkout's `bin/factory` on the integration checkout's store, skipping each scenario whose WHEN runs the harness suite. On this change's checkout and this repo's live store, the check SHALL report no failure in the capabilities this change restates or whose scenarios reuse a restated fixture.

#### Scenario: The instance's last gate command is the truth check on the integration checkout's store
- WHEN `(sed -n '/^gate_commands:/,/^[a-z_]*:/p' .factory/instance.yaml | grep '^  - ' | tail -1)`
- THEN it prints exactly `  - "{integration}/bin/factory truth check --store {integration}/.factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'"`

#### Scenario: The truth check on this checkout reports no failure in the capabilities this change restates
Run from the checkout under test, a worktree of this repo, after `uv sync --frozen`, with `git` and `node` on `PATH`. The store is this repo's live store, found from the checkout's git common directory. It names four capabilities so that, once in current truth, it never replays itself.
- WHEN `(I=$(cd "$(git rev-parse --git-common-dir)/.." && pwd -P); bin/factory truth check --store $I/.factory/store --capability role-escalations --capability harness-code --capability harness-docs --capability live-store-guard > ${TMPDIR:-/tmp}/t0059-live.txt 2>&1; echo "exit=$? $(tail -1 ${TMPDIR:-/tmp}/t0059-live.txt | sed -n 's/.* \([0-9][0-9]*\) failed.*/failed=\1/p')")`
- THEN it prints exactly `exit=0 failed=0`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the truth check
README SHALL add `truth check` to "Where a human decides"'s read-only list, keeping `paths` and `stats` adjacent. It SHALL hold a subsection "Replaying current truth with `factory truth check`" under "Where a human decides" and a Built entry that points to it. It SHALL name `truth check` in "Accepting a harness revision". `docs/design.md` SHALL hold a paragraph opening `**Replaying current truth.**` and SHALL name `truth check` in the live-store fence's read-only list. `docs/changelog.md` SHALL hold one entry naming #120.

#### Scenario: README, the design doc and the changelog describe the truth check
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; j() { tr '\n' ' ' | tr -s ' '; }; r=README.md; H=$(sed -n '/^## Where a human decides/,/^```/p' $r | j); echo "readonly=$(y $(echo "$H" | grep -c '`log tail`, `truth check`, `paths` and `stats`')) section=$(y $(sed -n '/^### Counting what each role catches and costs/,/^## What is built and what is not/p' $r | grep -c '^### Replaying current truth with `factory truth check`$')) built=$(y $(grep -c '^- \*\*Replaying current truth, `factory truth check`\.\*\*' $r)) accepting=$(y $(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' $r | j | grep -c '`truth check`')) design=$(y $(grep -c '^\*\*Replaying current truth\.\*\*' docs/design.md)) design-fence=$(y $(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md | grep -c '`log tail`, `truth check`, `paths` and `stats`')) changelog=$(grep -c '^[0-9][0-9]*\. .*#120' docs/changelog.md)")`
- THEN it prints exactly `readonly=yes section=yes built=yes accepting=yes design=yes design-fence=yes changelog=1`

## MODIFIED Requirements

### Requirement: The documents record the format check at spec add and its route back to the spec writer
`README.md`'s "The intake workflow, step by step" SHALL say that a spec is saved only if it is well-formed and fits current truth, and that otherwise it goes back to the writer, using up a round; its flowchart SHALL draw that route back to the spec writer, and the Spec writer row of "What each role reads and writes" SHALL name the refusal. `docs/design.md`'s routing table SHALL hold the route with `spec add` and `round +1`. `docs/changelog.md` SHALL hold one entry opening `After issue #105 `, numbered without a gap, that names `spec add`, `approve-spec` and the round. T-0057's merges into `main` MUST add at most one line net to `README.md`, measured across each `Merge factory/T-0057.<n>` commit against its first parent.

#### Scenario: README, the design doc and the changelog describe the refusal route
The README growth is summed over each `Merge factory/T-0057.<n>` commit reachable from HEAD, against its first parent, as harness-suite's T-0045 and T-0051 scenarios measure their own merges, so a later change's edits to README are never counted. With no such commit it prints `growth=none`.
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; I=$(sed -n '/^### The intake workflow, step by step$/,/^### The build workflow, step by step$/p' README.md); P=$(printf '%s\n' "$I" | awk '/^Intake runs triage once/{f=1} f&&/^$/{exit} f' | tr '\n' ' '); echo "formed=$(y $(printf '%s' "$P" | grep -c 'well-formed')) truth=$(y $(printf '%s' "$P" | grep -c 'current truth')) round=$(y $(printf '%s' "$P" | grep -c 'round')) edge=$(y $(printf '%s\n' "$I" | grep -cE '^ *W -- "[^"]*refused[^"]*" --> W$')) row=$(y $(grep '^| Spec writer (`spec_writer`) |' README.md | grep -c 'refus')) design=$(y $(grep '^| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT' docs/design.md | grep 'spec add' | grep -c 'round +1')) growth=$(for m in $(git log --format=%H --grep='^Merge factory/T-0057[.]' HEAD); do git diff --numstat "$m^1" "$m" -- README.md; done | awk '{n++; s += $1 - $2} END {print (n == 0 ? "none" : (s <= 1 ? "ok" : "over"))}')"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #105 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'spec add' -e 'approve-spec' -e 'round' | sort -u | grep -c .)")`
- THEN it prints exactly `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, then `CONTIGUOUS`, then `entries=1 terms=3`, one per line

=== specs/role-escalations/spec.md
## MODIFIED Requirements

### Requirement: The implementer and verifier leave declared protected paths out of ESCALATIONS
The system prompt of every implementer and verifier run SHALL say that a protected path the sub-ticket declares is not an escalation, that the code reviewer lists declared paths once for each head it reviews, that the role may name them but not under ESCALATIONS, and that a protected path the sub-ticket does not declare still goes under ESCALATIONS.

#### Scenario: Implementer and verifier run prompts carry the declared-path rule
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0029-prompt.sh <<'EOF'
# Sourced from the repo root of the checkout under test. Defines `prompt <role>`: starts one run of
# that role (implementer, reviewer or verifier) on a scratch target with a throwaway store, and
# prints the run's system prompt on one line, runs of spaces squeezed.
T29=$(cd "$(mktemp -d)" && pwd -P); B29=$PWD/bin/factory
git init -q -b main $T29/tgt && git -C $T29/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
(cd $T29/tgt && $B29 init --repo-name demo >/dev/null 2>&1)
printf '# F\n\nDo x.\n' > $T29/req.md
(cd $T29/tgt && FACTORY_STATE=$T29/s $B29 ticket new --file $T29/req.md >/dev/null)
prompt() (
  cd $T29/tgt && export FACTORY_STATE=$T29/s
  case $1 in
    implementer) $B29 ticket set T-0001 status=ready-for-implementer 'in_flight=[]' >/dev/null ;;
    *) $B29 ticket set T-0001 status=checks-in-flight 'in_flight=[]' head=$(git rev-parse HEAD) >/dev/null ;;
  esac
  R=$($B29 run start --role $1 --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
  tr '\n' ' ' < $T29/s/runs/${R:-none}/system-prompt.txt 2>/dev/null | tr -s ' '
)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer verifier; do P=$(prompt $r); echo "$r declared=$(echo "$P" | grep -c 'A protected path the sub-ticket declares is not an escalation') notunder=$(echo "$P" | grep -c 'but not under ESCALATIONS') undeclared=$(echo "$P" | grep -c 'still goes under ESCALATIONS when the sub-ticket does not declare it')"; done)`
- THEN it prints exactly `implementer declared=1 notunder=1 undeclared=1`, then `verifier declared=1 notunder=1 undeclared=1`

=== specs/harness-code/spec.md
## MODIFIED Requirements

### Requirement: Sharing an operation changes no refusal, park reason, event or parse result
After the operations above are shared, every command MUST print the same refusals, write the same events, history entries and park reasons, and parse every spec the same way as before, and the existing harness tests SHALL pass with no existing test file changed.

#### Scenario: Status transitions write the same events and history entries
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0046-store.sh <<'EOF'
# Sourced from the repo root: a throwaway store (the suite's fixture instance) whose T-0001 is
# awaiting the spec gate with a one-line spec, and a stand-in `claude` that fails if ever called.
# Leaves T set. Every command's output is discarded.
T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance
export FACTORY_REPO=$T/none FACTORY_INTEGRATION_BRANCH=main PYTHONDONTWRITEBYTECODE=1 LOGNAME=op; unset FACTORY_DISPATCH
mkdir $T/bin && printf '#!/bin/sh\necho "{}"; exit 1\n' > $T/bin/claude && chmod +x $T/bin/claude && export PATH=$T/bin:$PATH
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && printf '## Problem\nx\n' > $T/spec.md
bin/factory ticket new --file $T/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0046-reason.py <<'EOF'
# uv run --frozen python t0046-reason.py <store> <ticket>: the ticket's park reason, as a Python
# literal, with the store's scratch directory written as <T>.
import os, sys, yaml
t = yaml.safe_load(open(os.path.join(sys.argv[1], "tickets", sys.argv[2] + ".yaml")))
print(sys.argv[2], repr((t.get("parked") or {}).get("reason")).replace(os.path.dirname(sys.argv[1]), "<T>"))
EOF
cat > ${TMPDIR:-/tmp}/t0046-specstore.py <<'EOF'
# uv run --frozen python t0046-specstore.py, from the repo root: runs the spec parser of the merge
# base of HEAD and main and the checkout's own over every spec version, change part and
# current-truth file in this repo's store, and counts the calls whose result (or raised exception
# type) differs. Prints `files=<n> checks=<m> differ=<k>`, then up to five differing calls.
import glob, importlib.util, os, subprocess, sys, tempfile
sys.path.insert(0, os.getcwd())
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout
def load(name, src):
    p = os.path.join(tempfile.mkdtemp(), name + ".py"); open(p, "w").write(src)
    s = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
old = load("t0046_old", git("show", git("merge-base", "HEAD", "main").strip() + ":factory/specstore.py"))
new = load("t0046_new", open("factory/specstore.py", encoding="utf-8").read())
S = os.path.join(os.path.dirname(git("rev-parse", "--path-format=absolute", "--git-common-dir").strip()), ".factory", "store")
files = sorted(glob.glob(S + "/specs/*/v*.md") + glob.glob(S + "/openspec/**/*.md", recursive=True))
truths = sorted(glob.glob(S + "/openspec/specs/*/spec.md"))
def res(m, fn, a):
    try: return repr(getattr(m, fn)(*a))
    except Exception as e: return "raised " + type(e).__name__
checks, differ = 0, []
for path in files:
    t = open(path, encoding="utf-8").read(); parts = dict(old.split_parts(t)); ops = old.parse_delta(t)[0]
    calls = [("validate", (t,)), ("intent_of", (t,)), ("scenario_blocks", (t,)), ("requirement_blocks", (t,)),
             ("parse_delta", (t,)), ("decisions_of", (parts.get("proposal.md", t),)),
             ("acceptance_labels", (parts.get("verification.md", t),))]
    if any(ops.values()):
        calls += [("apply_delta", (open(c, encoding="utf-8").read(), os.path.basename(os.path.dirname(c)), ops)) for c in truths]
    for fn, a in calls:
        checks += 1
        if res(old, fn, a) != res(new, fn, a):
            differ.append(f"{fn} {os.path.relpath(path, S)}")
print(f"files={len(files)} checks={checks} differ={len(differ)}")
for d in differ[:5]: print(d)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: ST-1\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.1 status=merged >/dev/null && bin/factory ticket ready-implementers T-0001 >/dev/null && bin/factory ticket set T-0001.2 status=merged >/dev/null && bin/factory ticket parent-check T-0001 >/dev/null && bin/factory log tail --event ticket.transition -n 50 | sed 's/^{"ts": "[^"]*", /{/' && uv run --frozen python -c "import glob, sys, yaml; [print(p.rsplit('/', 1)[1][:-5], {k: v for k, v in h.items() if k != 'ts'}) for p in sorted(glob.glob(sys.argv[1] + '/tickets/*.yaml')) for h in yaml.safe_load(open(p))['history']]" $FACTORY_STATE)`
- THEN it prints exactly these 14 lines:

```
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-triage", "to": "ready-for-spec-writer", "by": "t", "round": {"spec": 0, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-spec-writer", "to": "ready-for-critic", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-critic", "to": "awaiting-spec-gate", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001", "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-planner", "to": "planned", "by": "t", "round": {"spec": 1, "pr": 0}}
{"event": "ticket.transition", "ticket": "T-0001.2", "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"}
{"event": "ticket.transition", "ticket": "T-0001", "from": "planned", "to": "ready-for-parent-verify", "by": "parent-check"}
T-0001.2 {'from': 'waiting-dependencies', 'to': 'ready-for-implementer', 'by': 'ready-implementers'}
T-0001 {'from': 'ready-for-triage', 'to': 'ready-for-spec-writer', 'by': 't', 'round': {'spec': 0, 'pr': 0}}
T-0001 {'from': 'ready-for-spec-writer', 'to': 'ready-for-critic', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'ready-for-critic', 'to': 'awaiting-spec-gate', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'awaiting-spec-gate', 'to': 'ready-for-planner', 'by': 'op', 'approved_version': 1}
T-0001 {'from': 'ready-for-planner', 'to': 'planned', 'by': 't', 'round': {'spec': 1, 'pr': 0}}
T-0001 {'from': 'planned', 'to': 'ready-for-parent-verify', 'by': 'parent-check'}
```

#### Scenario: Spec pinning and planner-run refusals keep their text
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && mkdir $T/s/openspec && bin/factory approve-spec T-0001 2>/dev/null | tail -1; rmdir $T/s/openspec && bin/factory approve-spec T-0001 >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0002 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p') && bin/factory subticket add T-0001 2>/dev/null | tail -1; bin/factory subticket add T-0001 --run $R 2>/dev/null | tail -1; bin/factory spec tasks T-0001 --run $R 2>/dev/null | tail -1)`
- THEN it prints exactly these 4 lines:

```
{"ok": false, "error": "spec not pinned: no `=== <path>` part lines"}
{"ok": false, "error": "no recorded planner run found for T-0001 (latest plan.added source: none); pass --run RUN or --file F"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
{"ok": false, "error": "run-0001-triage is not a PLANNED planner run of T-0001"}
```

#### Scenario: The dispatcher parks a refused store command with the same reason
Needs the GIVEN block of "Status transitions write the same events and history entries" run once. `factory drive` runs for real on the throwaway store. T-0001.1's implementer run start is refused because the target repository does not exist. T-0001.2 sits at its checks with no branch. T-0002 is at its planner with no approved spec.
- WHEN `(. ${TMPDIR:-/tmp}/t0046-store.sh && bin/factory approve-spec T-0001 >/dev/null && printf 'ST-1 / A\nDepends on: none\nParallel-safe: yes\n\nST-2 / B\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && bin/factory subticket add T-0001 --file $T/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.2 status=checks-in-flight >/dev/null && bin/factory ticket new --file $T/req2.md >/dev/null && bin/factory ticket set T-0002 status=ready-for-planner >/dev/null && bin/factory drive T-0001 --phase build >/dev/null 2>&1; bin/factory drive T-0002 --phase build >/dev/null 2>&1; for x in T-0001.1 T-0001.2 T-0002; do uv run --frozen python ${TMPDIR:-/tmp}/t0046-reason.py $FACTORY_STATE $x; done)`
- THEN it prints exactly these 3 lines:

```
T-0001.1 "harness-bug: run start implementer: factory: FileNotFoundError: [Errno 2] No such file or directory: PosixPath('<T>/none')\n"
T-0001.2 'harness-bug: no head for the checkers: T-0001.2 has no branch yet\n'
T-0002 'harness-bug: plan whole-spec: T-0002 has no approved spec\n'
```

#### Scenario: The spec parser gives the same result as the base on every spec in the store
Needs the GIVEN block of "Status transitions write the same events and history entries" run once.
- WHEN `(uv run --frozen python ${TMPDIR:-/tmp}/t0046-specstore.py)`
- THEN it prints one line, `files=<n> checks=<m> differ=0`, with n and m above 0, and nothing after it

#### Scenario: The refactored harness has no unused imports or variables
- WHEN `uvx ruff check --select F401,F841 factory tests`
- THEN it prints `All checks passed!` and exits 0

#### Scenario: The harness suite passes and no existing test file changes
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0046-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it

### Requirement: The command-line code has one module per job
The harness's command-line code SHALL be split by job: the spec-drift checks in
`factory/drift.py`, setup in `factory/setup.py`, the gates in `factory/gates.py`, the human
decisions in `factory/human.py`, the current-truth replay in `factory/truth.py`, and the helpers more than one of them uses, with the live-store
fence, in `factory/common.py`. `factory/cli.py` MUST keep the parser, the entry point and the role
list, and be under 910 lines.

Run every command of this change from the repository root of the checkout under test, after
`uv sync --frozen`, with `git` on `PATH`.

#### Scenario: The drift checks live in factory/drift.py
- WHEN `uv run --frozen python -B -c 'import factory.drift' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/drift.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`

#### Scenario: The shared helpers and the live-store fence live in factory/common.py
- WHEN `uv run --frozen python -B -c 'import factory.common' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/common.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `_add_spec_version _in_flight _integration_head _rel fence out`

#### Scenario: Instance and store setup live in factory/setup.py
- WHEN `uv run --frozen python -B -c 'import factory.setup' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/setup.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`

#### Scenario: The gates live in factory/gates.py
- WHEN `uv run --frozen python -B -c 'import factory.gates' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/gates.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`

#### Scenario: The human decisions live in factory/human.py
- WHEN `uv run --frozen python -B -c 'import factory.human' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/human.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
- THEN it prints exactly `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add escape_add intervention_add request_changes resolve spec_amend`

#### Scenario: factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines
- WHEN `echo "$(wc -l < factory/cli.py | tr -d ' ') $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"`
- THEN it prints two numbers: the first below 910, the second `3`

=== specs/live-store-guard/spec.md
## MODIFIED Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `launch-script`, `status parse`, `log tail`, `truth check`, `paths`, `drive` and `stats`, none of them given `--accept-harness`, MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`

#### Scenario: A launch copy is written unmarked while a run is in flight, and the target is unchanged
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The unmarked `ticket new` beside it shows the fence is up.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && mkdir $T/tmp && S0=$(snap); TMPDIR=$T/tmp $B launch-script build >/dev/null 2>&1; l=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; echo "launch=$l new=$n copies=$(ls $T/tmp | grep -c '^factory-launch-') store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `launch=0 new=2 copies=1 store=unchanged`

### Requirement: init, paths and stats refuse --accept-harness and name a command that accepts it
`factory --accept-harness <sha>` given with `init`, `paths`, `stats` or `truth check` MUST be refused with exit 2 and `{"ok": false, …}` on stdout, writing nothing. The refusal SHALL name the command and give `factory --accept-harness <sha> config` with the same sha. Without the flag, `paths`, `stats` and `truth check` SHALL still run under a lock that names another revision, and every other command SHALL keep its lock behaviour.

#### Scenario: The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; Z=0123456789abcdef0123456789abcdef01234567; snap() { find . -path ./.git -prune -o -type f -exec cksum {} + | sort | cksum; }; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && git init -q -b main $T/fresh && git -C $T/fresh -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && S0=$(snap) && for c in init paths stats; do $B --accept-harness $Z $c >$T/o 2>$T/e; echo "$c: exit=$? named=$(grep -cw "$c" $T/e) hint=$(grep -cF -- "factory --accept-harness $Z config" $T/e) json=$(grep -c '"ok": false' $T/o)"; done; echo "target=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)"; cd $T/fresh && $B --accept-harness $Z init --repo-name demo >/dev/null 2>&1; echo "fresh: exit=$? files=$(find . -path ./.git -prune -o -type f -print | grep -c .)")`
- THEN it prints exactly `init: exit=2 named=1 hint=1 json=1`, `paths: exit=2 named=1 hint=1 json=1`, `stats: exit=2 named=1 hint=1 json=1`, `target=unchanged`, `fresh: exit=2 files=0`, one per line

#### Scenario: Without the flag paths and stats still run under another lock, and config still accepts a revision
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && R=$($B paths | sed -n 's/.*"harness_revision": "\([0-9a-f]*\)".*/\1/p') && echo 0000000000000000000000000000000000000000 > .factory/harness.lock && $B paths >/dev/null 2>&1; p=$?; $B stats >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B --accept-harness $R config >/dev/null 2>&1; a=$?; echo "paths=$p stats=$s config=$c accept=$a lock=$([ "$(cat .factory/harness.lock)" = "$R" ] && echo accepted || echo other)")`
- THEN it prints exactly `paths=0 stats=0 config=2 accept=0 lock=accepted`

=== verification.md
## Acceptance

- Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time → NEW. Today it prints only `exit=2`: `factory` has no `truth` command (`argument cmd: invalid choice: 'truth'`).
- The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed → NEW. Today it prints nothing, because the command writes nothing to stdout.
- --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused → NEW. Today its first two lines are `one: exit=2 0 0` and `unknown: exit=2 named=0`.
- Capabilities run at the same time → NEW. Today it prints nothing.
- Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped → NEW. Today it prints nothing.
- On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped → NEW. Today it prints nothing.
- The implementer's worktree folds the same deltas → NEW. Today it prints nothing.
- From the integration branch only an open ticket's delta with a merged sub-ticket is folded → NEW. Today it prints nothing.
- A folded delta that no longer applies is refused, naming its ticket, and nothing runs → NEW. Today it prints `exit=2 named=0 results=0`: the refusal is argparse's, which names no ticket.
- truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing → NEW. Today it prints a line starting `here=2 inside=2 store=unchanged total=factory: error: argument cmd: invalid choice: 'truth'`: argparse refuses the unknown command.
- truth check refuses --accept-harness and names config → NEW. Today it prints `exit=2 hint=0 json=0`.
- The instance's last gate command is the truth check on the integration checkout's store → NEW. Today it prints `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"`.
- The truth check on this checkout reports no failure in the capabilities this change restates → NEW. Today it prints `exit=2` and a space, because `factory` has no `truth` command.
- README, the design doc and the changelog describe the truth check → NEW. Today it prints `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0`.
- README, the design doc and the changelog describe the refusal route → REGRESSION, in the form this change states, which measures README growth across T-0057's own merge. That form prints `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, then `CONTIGUOUS`, then `entries=1 terms=3` today, on `main` at `db28eb1` and at `7bfbe8f`, and on a branch that adds 11 lines to README; it passes after. Current truth's form, which measures against `main`, fails today: it prints `growth=` on `main` and `growth=over` on that branch. That is the defect this restatement fixes.
- Implementer and verifier run prompts carry the declared-path rule → REGRESSION. It passes today and after, in this change's form and in current truth's, because it asks only implementer and verifier prompts. The three scenarios that reuse its fixture and ask a reviewer prompt fail today in current truth's form; the gate-commands scenario "The truth check on this checkout reports no failure in the capabilities this change restates" checks that they pass once this change's delta is folded.
- Status transitions write the same events and history entries → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Spec pinning and planner-run refusals keep their text → REGRESSION, in the form this change states, whose `run start` passes no `--model`. That form passes today (`run-tip-fixed.txt` at `db28eb1`, `run-fixed.txt` at `7bfbe8f`) and after. Current truth's form, which passes `--model m`, fails today with `model m refused for triage: the instance names opus`; that is the defect this restatement fixes.
- The dispatcher parks a refused store command with the same reason → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The spec parser gives the same result as the base on every spec in the store → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The refactored harness has no unused imports or variables → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The harness suite passes and no existing test file changes → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The drift checks live in factory/drift.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The shared helpers and the live-store fence live in factory/common.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Instance and store setup live in factory/setup.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The gates live in factory/gates.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The human decisions live in factory/human.py → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The refusal names the throwaway store and not the marker → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- A harness acceptance is refused while a run is in flight → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- A launch copy is written unmarked while a run is in flight, and the target is unchanged → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
- Without the flag paths and stats still run under another lock, and config still accepts a revision → REGRESSION. It passes today and after; this change restates its requirement, and the verifier runs it.
