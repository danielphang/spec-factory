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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0600-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0600-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0600-reviewer/wt` (branch `factory/T-0059.1`, base `db28eb1451e35171b6de62f09d5e378c46a715fa`, head `2588b553013712729323c916c8e9063633b47e29`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

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

## PR description (the implementer's output)

Sub-ticket: T-0059.1, `factory truth check` replays every current-truth scenario, and the gate runs it (parent T-0059, issue #120, approved spec v4). Branch `factory/T-0059.1`, head `2588b55`, base `db28eb1`.

## What changed

The new command `factory truth check` replays the scenarios in current truth. Current truth is the store's record of required behaviour: one spec per area, called a capability. Each scenario is a shell command, its WHEN, and the output it must print, its THEN. Until now nothing ran these scenarios again after their own ticket closed. With this change, this repo's merge gate runs the replay as its last command.

**A. `factory/truth.py` (new, 297 lines): the replay.**
- **Inputs.** The store comes from `--store`, else `FACTORY_STATE`, else the instance's own store. The checkout under test is `git rev-parse --show-toplevel` of the caller's directory.
- **Folding.** The command finds the ticket under test from the store's layout: `worktrees/<id>`, or `runs/<run>/wt` plus that run's `meta.yaml`. It folds in the approved delta of that ticket's parent, or of the ticket itself if it has no parent. It also folds the delta of every unarchived change whose ticket is not closed and has a merged sub-ticket. Deltas are folded in id order, each checked against the text folded so far and applied with `specstore.apply_delta`. A delta that does not apply refuses the check with exit 2 and names its ticket.
- **Reading a scenario.** It reads each scenario's single WHEN, its THEN, its GIVEN blocks and its double-quoted references to other scenarios.
- **The exact-print rule** is `expected()`, following the grammar in design part A.
- **Skips.** The five skip reasons are checked in the spec's order.
- **Running.** Capabilities run at the same time, one thread each. Each capability gets a fresh `HOME` and `TMPDIR`, and every `FACTORY_*` variable is removed from its environment. Scenarios run in file order under `bash -c`, after the GIVEN blocks they need, and each block runs once per capability.
- **Output.** One line per scenario, and under each failure the expected lines, the printed lines (at most 40), the exit status and the last five stderr lines. The last line gives the counts and the wall time. The exit code is 1 when any scenario failed.
- **Parser.** `add_parser()` builds the `truth check` parser, so `cli.py` stays small.

**B. `factory/cli.py` (899 lines, unchanged count).**
- One import, and one `truth.add_parser(sp)` call in `build_parser()`.
- `("truth", "check")` is added to `READ_ONLY`, and its comment is updated.
- `"truth"` is added to both tuples in `main()`, so the command refuses `--accept-harness` with the same message and runs before the instance refusal, the fence and the lock. The message names `factory truth check`.
- That branch now returns `a.fn(a) or 0`, so the command's exit code reaches the shell. `init_cmd`, `paths_cmd` and `stats_cmd` return `None` (no `return` statement), so they still exit 0.
- Callers of `main()`, found by grep: `factory/__main__.py`, `factory/drive.py:63`, `tests/factory/clean_harness_cli.py:28` and `tests/factory/test_store_migrate.py:164`. None of them runs `truth`, and the return value only changed for that command.

**C. `.factory/instance.yaml`.** After the suite command, the comment line and the last gate entry are added verbatim from design part C.

**D. Documents.**
- README, "Where a human decides": the read-only list now ends `log tail`, `truth check`, `paths` and `stats`.
- README: a new subsection, "Replaying current truth with `factory truth check`", six lines with no figures, placed before "What is built and what is not".
- README: a two-line Built entry.
- README, "Accepting a harness revision": the one sentence there now reads "`paths`, `stats` and `truth check` only read, so they skip both checks on any store and refuse `--accept-harness`, as `init` does". It is reworded, not just extended; see Known gaps.
- README: the status date is now 2026-10-26.
- README grows by exactly 11 lines, to 1,224.
- `docs/design.md`: a new paragraph, `**Replaying current truth.**`, placed immediately before `**Routing table.**`. `truth check` is added to the fence paragraph's read-only list and to the lock clause in `**Role-context block.**`.
- `docs/changelog.md`: entry 79, which names #120. The numbering is contiguous.

**E. Restated scenarios.** E changes only the spec store, at archive. This branch has no code for it; the restated scenarios' results are below.

## Acceptance results

I ran every WHEN from the worktree at the head commit, through the HOME wrapper with `TMPDIR` in my scratch directory. A small runner, `scratch/runwhen.sh`, ran each GIVEN block once and then each WHEN. The WHENs were extracted verbatim from `openspec/changes/T-0059/specs/*/spec.md`, which I diffed against v4 and found identical. Every "after" output below matches its THEN exactly. The 14-line transitions block was compared with `diff` against the THEN's fenced block and printed `SAME 14`. All 34 "after" runs were made at `eb6d383`. The only later commit, `2588b55`, renames one helper inside `tests/factory/test_truth.py`, and the suite and ruff were re-run after it.

| Scenario | Label | Before (db28eb1) | After |
|---|---|---|---|
| Each scenario of a fixture truth gets one result line… | NEW | `exit=2` only | the 16 expected lines, ending `16 scenarios: 11 passed, 2 failed, 3 skipped; wall time N s` |
| The first line names the checkout, the store and the folded deltas… | NEW | nothing | `truth check: G against S; folded: T-0002`, `  expected:`, `    hello`, `  got:`, `    hullo`, `  exit 0` |
| --capability limits the run… | NEW | `one: exit=2 0 0`, `unknown: exit=2 named=0`, `no-truth: exit=2`, … | `one: exit=0 2 2`, `unknown: exit=2 named=1`, `no-truth: exit=2`, `no-git: exit=2` |
| Capabilities run at the same time | NEW | nothing | `together` |
| Prose THENs, missing GIVEN blocks and WHENs the caller skips… | NEW | nothing | the 5 expected lines, ending `16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s` |
| On a checker's checkout of a sub-ticket… | NEW | nothing | the 5 expected lines (`folded: T-0001, T-0002`, …) |
| The implementer's worktree folds the same deltas | NEW | nothing | `truth check: W against S; folded: T-0001, T-0002`, then the SKIPPED alpha line |
| From the integration branch only an open ticket's delta… | NEW | nothing | `PASS alpha: The greeting is printed exactly`, the SKIPPED gamma line, `PASS gamma: Gamma prints two` |
| A folded delta that no longer applies is refused… | NEW | `exit=2 named=0 results=0` | `exit=2 named=1 results=0` |
| truth check reads a live store with a run in flight… | NEW | `here=2 inside=2 store=unchanged total=factory: error: argument cmd: invalid choice: 'truth' …` | `here=0 inside=0 store=unchanged total=0 scenarios: 0 passed, 0 failed, 0 skipped locked=2` |
| truth check refuses --accept-harness and names config | NEW | `exit=2 hint=0 json=0` | `exit=2 hint=1 json=1` |
| The instance's last gate command is the truth check… | NEW | `  - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"` | `  - "{integration}/bin/factory truth check --store {integration}/.factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'"` |
| The truth check on this checkout reports no failure in the capabilities this change restates | NEW | `exit=2 ` | `exit=0 failed=0` |
| README, the design doc and the changelog describe the truth check | NEW | `readonly=no section=no built=no accepting=no design=no design-fence=no changelog=0` | `readonly=yes section=yes built=yes accepting=yes design=yes design-fence=yes changelog=1` |
| README, the design doc and the changelog describe the refusal route | REGRESSION (restated form) | — | `formed=yes truth=yes round=yes edge=yes row=yes design=yes growth=ok`, `CONTIGUOUS`, `entries=1 terms=3` |
| Implementer and verifier run prompts carry the declared-path rule | REGRESSION | — | `implementer declared=1 notunder=1 undeclared=1`, `verifier declared=1 notunder=1 undeclared=1` |
| Status transitions write the same events and history entries | REGRESSION | — | the 14 expected lines (`diff` empty) |
| Spec pinning and planner-run refusals keep their text | REGRESSION (restated form) | — | the 4 expected `{"ok": false, …}` lines |
| The dispatcher parks a refused store command with the same reason | REGRESSION | — | the 3 expected lines |
| The spec parser gives the same result as the base on every spec in the store | REGRESSION | — | `files=394 checks=6134 differ=0` |
| The refactored harness has no unused imports or variables | REGRESSION | — | `All checks passed!`, exit 0 (re-run at `2588b55`: same) |
| The harness suite passes and no existing test file changes | REGRESSION | — | `658 passed in 111.08s (0:01:51)`, nothing after it (`git diff --name-only --diff-filter=DMR main...HEAD -- tests` is empty at `2588b55`) |
| The drift checks live in factory/drift.py | REGRESSION | — | `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` |
| The shared helpers and the live-store fence live in factory/common.py | REGRESSION | — | `_add_spec_version _in_flight _integration_head _rel fence out` |
| Instance and store setup live in factory/setup.py | REGRESSION | — | the expected 14 names |
| The gates live in factory/gates.py | REGRESSION | — | the expected 18 names |
| The human decisions live in factory/human.py | REGRESSION | — | the expected 15 names |
| factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines | REGRESSION | — | `899 3` |
| Unmarked writes from inside the target are refused while a run is in flight, init included | REGRESSION | — | `init=2 new=2 transition=2 decision=2 store=unchanged agents=none` |
| The refusal names the throwaway store and not the marker | REGRESSION | — | `rule=1 state=1 marker=0 json=1 inside=1` |
| A harness acceptance is refused while a run is in flight | REGRESSION | — | `accept=2 store=unchanged` |
| A launch copy is written unmarked while a run is in flight… | REGRESSION | — | `launch=0 new=2 copies=1 store=unchanged` |
| The flag with init, paths or stats is refused… | REGRESSION | — | `init:`/`paths:`/`stats: exit=2 named=1 hint=1 json=1`, `target=unchanged`, `fresh: exit=2 files=0` |
| Without the flag paths and stats still run under another lock… | REGRESSION | — | `paths=0 stats=0 config=2 accept=0 lock=accepted` |

"Before" outputs come from `scratch/before/new-out.txt`. One note on the before column: my first "after" attempt at the live-store scenario printed `here=1 inside=1 … locked=1`. The cause was in my runner, not the code. The runner had not run that scenario's live-store-guard fixture, and the fixture's `run start` was also refused while the harness edits were uncommitted. Re-run after commit with its fixture, the scenario printed the line in the table.

Gate commands, each run exactly as written, at `2588b55`:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` exited 0: `658 passed in 112.90s (0:01:52)`.

**The full gate replay, as operator step 1 will run it.** I ran `bin/factory truth check --store <live store> --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'` from this worktree against the live store at `2588b55`. It exited 0:
- `339 scenarios: 276 passed, 0 failed, 63 skipped; wall time 128 s`;
- `folded: T-0059`, because this worktree is the store's `worktrees/T-0059.1`;
- the 63 skips are 34 scenarios in T-0059's delta, 13 WHENs that run the suite (the 14th is inside the delta) and 16 prose THENs.

The live store's `git status --porcelain` held 10 entries before and after the run: the operator's own uncommitted edits, unchanged.

On `eb6d383`, the same replay printed 1 failure: harness-suite's "The shared constants and wrappers are defined once" printed `ticket=2`. My new test file defined its own `ticket()` helper, which repeats a name the shared test helpers already define. Commit `2588b55` renames it to `write_ticket`. After that, the harness-suite capability alone prints `16 scenarios: 4 passed, 0 failed, 12 skipped`, and the full replay above is clean.

## Tests added/changed

- Added `tests/factory/test_truth.py`, 6 tests, about 13 s under xdist. I wrote the tests after the code. To check that they test the change, I ran them on an export of base `db28eb1`, where all 6 fail.
  - The exact-print rule: 14 forms that read and 9 that must not. These run in one Python subprocess from the repo root, because `tests/factory` is itself a package named `factory`.
  - Every skip reason, plus a GIVEN block reused through a quoted reference.
  - The failure detail: the 40-line cap, the `… 5 more lines` line, the exit status, stderr, and a THEN that says "exits 0".
  - The fold, from the integration checkout, an implementer worktree, and a checker checkout whose ticket has no parent. It also checks that the later delta's id wins, and that a scenario of another capability with the same name still runs.
  - A refused delta, where nothing runs.
  - The refusals: unknown capability, no current truth, caller outside git, and `--accept-harness`.
- No existing test changed.

## Known gaps and uncertainties

1. **Size.** The change is larger than the spec estimated. `factory/truth.py` is 297 lines against about 200, and its tests are 203 lines against about 150; the whole diff is 535 lines added and 18 deleted, against about 370. I did not compress the code to meet the estimate.
2. **A repeated check.** `specstore.applies` reads current truth from files, but the fold must check against text folded in memory, and `factory/specstore.py` is out of scope. So `fold()` repeats its ADDED/MODIFIED/REMOVED check in three lines, with the same error texts, and a comment says so. I also count `parse_delta`'s own errors as reasons to refuse, under the spec's "on any error, refuse".
3. **Folded scenarios are keyed by capability and name.** The spec says to record each scenario name of a folded delta with its id. I key it by capability and scenario name instead, so a same-named scenario in another capability still runs; a test covers this. With no duplicate names across capabilities today, the two readings give the same result on the live store.
4. **One skip reason the spec does not list.** A scenario with more than one THEN line is skipped as `has more than one THEN line`, mirroring the WHEN reason. The spec defines "the THEN" as "the one line", but lists no reason for two. An awk count over all 16 current-truth files found no such scenario, so this changes nothing today.
5. **Scenario splitting is reused indirectly.** `specstore.scenario_blocks` only reads delta parts of a spec version, so I prefix each capability's text with a dummy `=== specs/x/spec.md` line to reuse it. A comment says so. Duplicate scenario names within one capability would collapse to one, as they do elsewhere in the harness.
6. **README wording beyond the spec's letter.** In "Accepting a harness revision", adding `truth check` to the existing sentence as written would have grown README to 12 lines, one over the 11-line limit. I reworded the sentence instead. It stays one sentence, and the existing check that counts such sentences still passes: harness-docs' "README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy" is a PASS line in the full replay. To stay within the same limit, "Related work and history" gains no `#120` entry.
7. **A stale comment.** The comment above `gate_commands` in `.factory/instance.yaml` still says "whitespace errors…, then the harness's own suite". The new entry has its own comment line, as design C specifies, but the header comment does not mention the third command.
8. **Not tested on macOS's own shell.** The command runs the `bash` on `PATH`, which was Homebrew bash 5.3.9 here. Nothing was run under macOS's `/bin/bash` 3.2.
9. `factory:` markers added: none.

## Out-of-scope observations

- Running `bin/factory` leaves `factory/__pycache__/` in a checkout, because the launcher does not set `PYTHONDONTWRITEBYTECODE`. It is git-ignored, so nothing shows in `git status`.
- Two current-truth scenarios that measure a change against `main` (harness-code's "Every definition keeps its exact text…" and harness-suite's "The only existing test file changed is the stats test") are skipped as prose today. The spec's Risk section names them. An exact-print scenario of that kind added later would fail every gate.

## Responses to findings

None: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION command printed its THEN on this branch, both gate commands pass, and the full live replay reports 0 failed.
ESCALATIONS: none

## Diff `db28eb1451e35171b6de62f09d5e378c46a715fa...2588b553013712729323c916c8e9063633b47e29`

diff --git a/.factory/instance.yaml b/.factory/instance.yaml
index 568fca3..3595a9b 100644
--- a/.factory/instance.yaml
+++ b/.factory/instance.yaml
@@ -24,6 +24,8 @@ protected_paths:
 gate_commands:
   - "git diff --check main...HEAD"
   - "uv run --frozen pytest -q -p no:cacheprovider tests/factory"
+  # then current truth, replayed by the integration checkout's harness; WHENs that run the suite are skipped, since the line above runs it
+  - "{integration}/bin/factory truth check --store {integration}/.factory/store --skip-when-contains 'pytest -q -p no:cacheprovider tests/factory'"
 placeholders: {rounds: 2, spec_lines: 400, audit_n: 5, retro_min: 3}
 max_rounds: {spec: 2, pr: 2}
 # Build half, local-commit stand-in (operator, 2026-10-02): no remote, no CI. The merge gate is the
diff --git a/README.md b/README.md
index 50fdf61..6daf137 100644
--- a/README.md
+++ b/README.md
@@ -10,7 +10,7 @@ attention, with no rise in escaped defects. See `docs/north-star.md`, `STATUS.md
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-25. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-26. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -614,8 +614,8 @@ can accept a revision while another stays on the old one.
 The flag cannot clear the other refusal. A runtime with uncommitted edits to the harness code is
 refused outright; commit or discard them first. Both checks apply only when a command uses the
 instance's own store. A throwaway store (`FACTORY_STATE` pointing elsewhere, as every test does)
-skips them. `paths` and `stats` skip both checks on any store because they write nothing, and
-`init`, `paths` and `stats` refuse `--accept-harness`; every other command accepts it.
+skips them. `paths`, `stats` and `truth check` only read, so they skip both checks on any store
+and refuse `--accept-harness`, as `init` does; every other command accepts it.
 
 ### Upgrading the runtime
 
@@ -904,7 +904,7 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 A run is in flight from `run start` until `run finish` records its result. While any run on a
 target is in flight, the harness refuses every write to that target's store that lacks this
 marker. A write is any command except `ticket show`, `ticket join`, `results show`, `config`,
-`launch-script`, `status parse`, `log tail`, `paths` and `stats`; a command given
+`launch-script`, `status parse`, `log tail`, `truth check`, `paths` and `stats`; a command given
 `--accept-harness` is always a write. `factory drive` is exempt from this check and needs no
 marker, because it is the dispatcher; it guards its own ticket instead ("Driving a ticket from a shell with `factory drive`"). The
 workflow scripts already put the marker on their own commands. Put it in front of one command at
@@ -1021,6 +1021,15 @@ changes. A change is a ticket closed in the window after at least one of its sub
 | Tokens and wall time per change | the median of each change's summed run time, in hours; then the median tokens of the changes whose every run has tokens, how many runs took tokens from a record, a transcript (with `--transcripts`) or neither, and the dollars on the records that carry them |
 | Lead time | from the ticket's creation to its last merge, in hours: median and range |
 
+### Replaying current truth with `factory truth check`
+
+`factory truth check` runs each current-truth scenario's WHEN under `bash` in the git checkout of the
+current directory. A scenario passes only if its WHEN prints exactly the lines its THEN quotes
+(`docs/design.md`, "Replaying current truth"); one it cannot check is listed SKIPPED with its reason.
+`--capability NAME` limits the run, and `--skip-when-contains TEXT` skips each WHEN holding TEXT. It
+folds in approved changes that are merged or under test, so their intended edits are not failures.
+This repo's gate runs it last. A scenario must not replay its own capability, or it replays itself.
+
 ## What is built and what is not
 
 **Built**
@@ -1082,6 +1091,8 @@ changes. A change is a ticket closed in the window after at least one of its sub
 - **The scorecard, escapes and workflow token records.** `factory stats --scorecard`,
   `factory escape add`, `factory intervention add` and `run finish --transcripts` ("Counting what
   each role catches and costs"). Not yet run on a real store.
+- **Replaying current truth, `factory truth check`.** The gate replays every current-truth scenario
+  ("Replaying current truth with `factory truth check`"). Not yet run in a real gate.
 
 **Not built**
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 0b18178..b85d516 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -88,4 +88,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 
 78. After issue #105 (2026-10-12), where `approve-spec` refused a spec the critic had approved, over three acceptance labels in `verification.md` that had wrapped onto the next line, and the operator had to fix the spec by hand and approve it again. The format check ran only at the spec gate, so neither the spec writer nor the critic saw its verdict. `spec add` now runs the same check as `approve-spec` on a store with current truth: a spec that is malformed, or whose changes do not apply to current truth, is refused with exit 2 and `spec not added: ` followed by the errors, and nothing is written. A spec writer's NEEDS-HUMAN draft is still stored unchecked, so the operator can read it. Both the driver and the intake workflow script send a refused spec back to the spec writer as a new round, counted against the round limit; the writer's next input holds the refusal and the refused output. When no round is left, the ticket parks as `max rounds: ` followed by the refusal, with each backtick, `$` and `\` replaced by `'`. This overturns, for a refused spec, the 2026-10-07 decision that a format refusal re-dispatches the role once and then parks. Rejected: a routing edge from the spec writer's ready state to itself, which every instance's `instance.yaml` would need; a new round command; and a record of the refusal, which would break the rule that a refusal writes nothing.
 
+79. After issue #120 (2026-10-20), where a change merged here could break a current-truth scenario an earlier change was required to keep and nothing would notice: each verifier ran only its own ticket's scenarios once, and the gate ran only a whitespace check and the harness suite. Replayed on `main` at `7bfbe8f`, five scenarios failed. `factory truth check` now replays current truth against the checkout that holds the caller's directory: each WHEN runs under `bash` after the GIVEN blocks it needs, and its stdout is compared with the THEN by the exact-print rule ("Replaying current truth"). A THEN the rule cannot read, a missing GIVEN block or a WHEN the caller skips is listed SKIPPED with its reason. It folds in the approved delta of the ticket whose checkout it runs in, and that of every open ticket with a merged sub-ticket, and skips those deltas' scenarios. It only reads, so it skips the fence and the harness lock and refuses `--accept-harness`. This repo's last gate command now runs it, with the integration checkout's `bin/factory` on the integration checkout's store, skipping the scenarios whose WHEN runs the harness suite, which the gate already runs. Wall time: one capability after another took 687 s at `3e4705a`, over the ten-minute limit on one shell command; all at once took 482 s; all at once without the suite-running scenarios took 157 s there and 127 s at `7bfbe8f`, with this change's delta folded 127 s, and 129 s with the new gate-commands scenario run, on top of the suite's 119 s. The five failing scenarios are restated. Four broke when T-0050 made `run start` refuse a `--model` the instance does not name, and their fixtures still passed one; the restated fixtures pass none. The fifth is T-0057's README check, which measured README growth against `main` and so could pass only on T-0057's own branch; it now measures across each `Merge factory/T-0057.<n>` commit against its first parent. The two live-store-guard lists gain `truth check`, and `factory/cli.py`'s limit rises from under 900 to under 910 lines. Rejected: the runtime's `bin/factory` in the gate, which would leave the gate broken between a merge and the next upgrade; a `{ticket}` placeholder in the gate command, which only an upgraded runtime would fill in; running a folded delta's new scenarios, which would fail a sub-ticket on scenarios a sibling has yet to build; and a contains match, which no passing scenario needs and which would hide extra output.
+
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 879121a..21170eb 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -61,11 +61,11 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Spec drift.** Between the writing of a spec and the build of one of its sub-tickets, other tickets merge, and a sibling that the sub-ticket's checks rely on may not have merged yet. The harness checks for this before the implementer spends a run on it. Every spec version the store keeps, from `spec add`, a gate edit or `spec amend`, records the integration branch's head when it was stored, as `integration_head` in `specs/<ticket id>/v<n>.yaml`; the value is null when the target repo or branch does not resolve. Before a sub-ticket's implementer run, `run start` checks for drift, ahead of the sibling-tests check. It checks only while the sub-ticket has no finished implementer run and no ruling on file. Two rules find drift. The sibling rule: the sub-ticket's Acceptance field names, by id or by plan label as a whole token, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. The test rule counts from the head recorded with the parent's approved version. It is skipped when that version has no record, because it was stored before the record existed, or when the head is null or not a commit in the target repo. For each first-parent commit on the integration branch since that head that changed a file the version's design part names, each test file the commit changed is a finding, unless the design's `## Tests to change` or the sub-ticket's "Tests to change" lists it. A first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans, is not counted, because the plan expects its siblings' changes. Every other commit and merge still counts. Named files are the design part's backticked paths that exist at the integration branch's head, other than test files and `.md` documents, which nearly every ticket edits. A test file's name starts with `test_`, ends `_test.<ext>`, or contains `.test.`. The test rule approximates "a test pins behaviour the spec changes". Measured on two stores' history, it would have caught 9 of 10 known breaks, and it parks about half of all sub-tickets. On drift, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build parks the sub-ticket with that error as the reason. The human amends the spec (`factory spec amend`, Spec store below), rules, or both; `resolve --ruling` returns the sub-ticket to its implementer, and the ruling on file stops the check from repeating.
 
-**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `launch-script`, `status parse`, `log tail`, `paths` and `stats`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
+**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `launch-script`, `status parse`, `log tail`, `truth check`, `paths` and `stats`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance; `paths` and `stats`, which only read, run under any revision; `init`, `paths` and `stats` never check the lock, so they refuse `--accept-harness` and name `config` as the command that accepts a revision) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance; `paths`, `stats` and `truth check`, which only read, run under any revision; `init`, `paths`, `stats` and `truth check` never check the lock, so they refuse `--accept-harness` and name `config` as the command that accepts a revision) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception. `factory stats` prints the evidence a change to this table needs; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog entry 70.
 
@@ -95,6 +95,8 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 `decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. After the gate, only `factory spec amend <ticket id> --file F --reason "<line>" --intent unchanged` changes the pinned version. A human runs it on a parent ticket whose spec is approved and not yet archived, when another ticket's merge or a checker's finding shows the approved spec is wrong; no workflow script or role prompt names it. It refuses while any run is in flight on the ticket or its sub-tickets. `--intent unchanged` keeps the Problem section, every Decisions line, and each requirement's name, operation and statement, whitespace aside. Scenarios, their setup, Evidence, design text and Tests to change may change. The harness checks that claim against the approved version. It refuses a change of intent, and always refuses `--intent changed`, with a restart note: the merged sub-tickets, which a restart keeps; the unmerged ones, which it discards; and the two ways to restart, re-spec and re-plan through the spec gate, or close and re-file. It also refuses a version that fails the gate's own checks. The amended version becomes the approved one, so every later role run receives it. The re-pin rewrites the change folder as the gate does, but keeps the planner's `tasks.md`, and archive writes the amended scenarios. Each sub-ticket not merged or closed moves to the new version and keeps the version its plan was made from, so an amendment supersedes no plan. The amendment is recorded in `approvals/<ticket id>/amendment-<n>.md`, with the reason, each scenario changed, added or removed, each sub-ticket merged before it, and the diff, and logged as `spec.amended`. It changes no ticket state; the human resumes the ticket by the usual routes. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. Triage receives the capability index: one line per current-truth capability, with its size, the absolute path of its spec and its requirement names. Triage names the capabilities the request touches on its `Capabilities:` line. The spec writer and the critic receive those capabilities in full, plus each one whose `specs/<name>/spec.md` path the spec they work from cites, and the capability index for the rest (routing table). They and the planner receive the whole decision log, `decisions.md`, when it holds any text, whatever capabilities the ticket names: a standing decision often names no capability, yet every ticket must follow it. A ticket whose latest triage output has no `Capabilities:` line gets every current-truth spec in full.
 
+**Replaying current truth.** `factory truth check` replays current truth against a checkout, so a change that breaks a scenario an earlier change was required to keep is caught. It runs every scenario's WHEN under `bash -c`, from the top of the git checkout that holds the caller's directory, with stdin closed, after the GIVEN blocks the scenario needs: the fenced blocks before its WHEN line, and those of each scenario named in double quotes on its other lines, run first. Each block runs once per capability, and a GIVEN block's exit status is ignored. It compares the WHEN's stdout with the THEN by the exact-print rule. A THEN of the form "it prints [exactly|only] …" lists the expected lines in backticks, joined by ", then", ", and", ", " or " and"; the list may open with "[these] N lines:" or read "N lines, each `X`"; an item may be followed by "twice" or "three times", or by a parenthetical note; the THEN may end ", one per line" or "and exits 0"; and a THEN ending "these N lines:" takes them from the fenced block after it. The stdout, less one trailing newline, must equal those lines exactly; stderr is never compared, and the exit status only when the THEN says "and exits 0". A scenario is listed SKIPPED, with its reason, and counted, when it is in a folded delta, has no single backticked WHEN command, has a WHEN that contains a `--skip-when-contains` text, needs a GIVEN block current truth does not hold, or has a THEN the rule cannot read in full. Before it runs, the check folds into current truth, as archive would, the approved delta of the ticket whose checkout it runs in (the parent's, for a sub-ticket; recognised by the store's `worktrees/<id>` and `runs/<run>/wt` layout), and the delta of every unarchived change whose ticket is not closed and has a merged sub-ticket, because that code is on the integration branch before its scenarios reach current truth. The scenarios in those deltas' ADDED and MODIFIED requirements are skipped, since their tickets' verifiers check them; a folded delta that no longer applies refuses the check with exit 2, naming its ticket. Capabilities run at the same time, each in its own fresh `HOME` and `TMPDIR`, with every `FACTORY_` variable removed; within one, scenarios run in file order. It prints one PASS, FAIL or SKIPPED line per scenario, the expected and printed lines under each failure, and a last line with the counts and the wall time, and exits 1 when any scenario failed. It only reads, so like `stats` it skips the instance refusal, the live-store fence and the harness lock, and refuses `--accept-harness`. This repo's last gate command runs it with the integration checkout's `bin/factory` on the integration checkout's store, skipping each scenario whose WHEN runs the harness suite, which the gate's previous command runs; the runtime's `bin/factory` would leave the gate broken between a merge and the next upgrade. A scenario must not run the check over a capability that holds that scenario, or the check replays itself.
+
 **Routing table.** The dispatcher (piece 2) is this table and nothing else. Each row: a STATUS a role emits, what runs next, and what it receives. "Receives" adds to the INPUT the role prompt already declares. Both follow the role-context block (above).
 
 Rules the table relies on:
diff --git a/factory/cli.py b/factory/cli.py
index 7724f8c..b68a202 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -15,7 +15,7 @@ from pathlib import Path
 
 import yaml
 
-from factory import compose, cost, gitops, instance, launch, specstore, status, store, subtickets, tripwire
+from factory import compose, cost, gitops, instance, launch, specstore, status, store, subtickets, tripwire, truth
 from factory.common import _add_spec_version, _rel, fence, out
 from factory.drift import _check_drift, _check_sibling_tests
 from factory.gates import (_parent_close_verified, archive_cmd, merge_cmd, results_record, results_show,
@@ -785,6 +785,7 @@ def build_parser() -> argparse.ArgumentParser:
                         "cost record, and for implementer gate failures (repeatable)")
     p.add_argument("--scorecard", action="store_true", help="print only the north star's scorecard; needs --since")
     p.set_defaults(fn=stats_cmd)
+    truth.add_parser(sp)
     p = sp.add_parser("archive")
     p.add_argument("id")
     p.set_defaults(fn=archive_cmd)
@@ -858,23 +859,22 @@ def build_parser() -> argparse.ArgumentParser:
 
 # ----- live-store fence: only the dispatcher writes a live store during a run ------------------
 
-# `paths` and `stats` never reach the fence (main() runs them before it); they are listed so this set
-# matches the documents' read-only list.
+# `truth check`, `paths` and `stats` never reach the fence (main() runs them before it); they are listed
+# so this set matches the documents' read-only list.
 READ_ONLY = {("ticket", "show"), ("ticket", "join"), ("results", "show"), ("config", None),
-             ("launch-script", None), ("status", "parse"), ("log", "tail"), ("paths", None), ("stats", None)}
+             ("launch-script", None), ("status", "parse"), ("log", "tail"), ("truth", "check"), ("paths", None), ("stats", None)}
 
 
 def main(argv: list[str] | None = None) -> int:
     a = build_parser().parse_args(argv)
     try:
-        if a.cmd in ("init", "paths", "stats") and a.accept_harness:
-            raise Refused(f"factory {a.cmd} never checks the harness lock, so it cannot accept a revision; "
-                          f"run factory --accept-harness {a.accept_harness} config")
-        # exempt from the instance refusal (design B.1); `paths` and `stats` only read, so they also
-        # skip the fence and the harness lock; all three refuse --accept-harness (above, T-0058)
-        if a.cmd in ("init", "paths", "stats"):
-            a.fn(a)
-            return 0
+        if a.cmd in ("init", "paths", "stats", "truth") and a.accept_harness:
+            raise Refused(f"factory {a.cmd}{' ' + a.sub if a.cmd == 'truth' else ''} never checks the harness lock, so it "
+                          f"cannot accept a revision; run factory --accept-harness {a.accept_harness} config")
+        # exempt from the instance refusal (design B.1); `paths`, `stats` and `truth check` only read, so
+        # they also skip the fence and the harness lock; all four refuse --accept-harness (above, T-0058)
+        if a.cmd in ("init", "paths", "stats", "truth"):
+            return a.fn(a) or 0
         inst = instance.require()  # refused when no instance is found: nothing is written
         cfg = instance.load_config(inst)
         root = store.state_root(cfg)
diff --git a/factory/truth.py b/factory/truth.py
new file mode 100644
index 0000000..e405fe1
--- /dev/null
+++ b/factory/truth.py
@@ -0,0 +1,297 @@
+"""`factory truth check`: replay every current-truth scenario against the git checkout that holds the
+caller's directory, and compare each WHEN's output with its THEN by the exact-print rule (design,
+"Replaying current truth"). Like `stats`, it only reads: main() runs it before the instance refusal,
+the live-store fence and the harness lock.
+"""
+from __future__ import annotations
+
+import os
+import re
+import shutil
+import subprocess
+import tempfile
+import time
+from concurrent.futures import ThreadPoolExecutor
+from pathlib import Path
+
+import yaml
+
+from factory import instance, specstore
+from factory.store import Refused
+
+WORDS = {w: i for i, w in enumerate(("two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"), 2)}
+ITEM_RE = re.compile(r"`([^`]*)`(?:,? (twice|three times))?(?: \([^`()]*\))?")
+SEP_RE = re.compile(r", then |, and |, | and ")
+COUNT = {None: 1, "twice": 2, "three times": 3}
+
+
+def _items(s: str) -> list[str] | None:
+    """LIST := ITEM (SEP ITEM)*, read in full, or None."""
+    out, pos = [], 0
+    while m := ITEM_RE.match(s, pos):
+        out += [m.group(1)] * COUNT[m.group(2)]
+        pos = m.end()
+        if pos == len(s):
+            return out
+        if not (sep := SEP_RE.match(s, pos)):
+            return None
+        pos = sep.end()
+    return None
+
+
+def expected(then: str, block: list[str] | None) -> tuple[list[str], bool] | None:
+    """The exact-print rule: (expected lines, whether the exit status must be 0) for the THEN text
+    after `- THEN `, `block` being the fenced block after it; None when the rule cannot read it in full."""
+    m = re.match(r"it prints (?:exactly |only )?(.*)$", then)
+    if not m:
+        return None
+    body = m.group(1).removesuffix(".")
+    exits = body.endswith((" and exits 0", ", and exits 0"))
+    body = re.sub(r",? and exits 0$", "", body).removesuffix(", one per line")
+    if re.fullmatch(r"these (?:\d+|[A-Za-z]+) lines:", body):
+        return (block, exits) if block is not None else None
+    if m := re.fullmatch(r"([a-z]+) lines, each (?:exactly )?(`.*)", body):
+        first = ITEM_RE.match(m.group(2))
+        if m.group(1) not in WORDS or not first:
+            return None
+        rest = m.group(2)[first.end():]
+        tail = _items(rest.removeprefix(", then ")) if rest.startswith(", then ") else ([] if not rest else None)
+        lines = [first.group(1)] * COUNT[first.group(2)] * WORDS[m.group(1)]
+        return (lines + tail, exits) if tail is not None else None
+    body = re.sub(r"^(?:these )?(?:\d+|[A-Za-z]+) lines(?:, one per line)?: ", "", body)
+    lines = _items(body)
+    return (lines, exits) if lines is not None else None
+
+
+class Scenario:
+    """One `#### Scenario:` block, read outside fences: its WHEN and THEN lines, its GIVEN blocks
+    (the fenced blocks before the WHEN line), the fenced block after its THEN, and its quoted strings."""
+
+    def __init__(self, cap: str, name: str, block: str):
+        self.cap, self.name = cap, name
+        self.whens, self.thens, self.given, self.quotes, self.given_quotes = [], [], [], [], []
+        self.then_block: list[str] | None = None
+        fenced = None
+        for line in block.splitlines()[1:]:
+            if line.lstrip().startswith("```"):
+                if fenced is None:
+                    fenced = []
+                    continue
+                if not self.whens:
+                    self.given.append("\n".join(fenced) + "\n")
+                elif self.thens and self.then_block is None and self.thens[0].endswith("lines:"):
+                    self.then_block = fenced
+                fenced = None
+            elif fenced is not None:
+                fenced.append(line)
+            elif line.startswith("- WHEN "):
+                self.whens.append(line)
+            elif line.startswith("- THEN "):
+                self.thens.append(line[len("- THEN "):].rstrip())
+            else:
+                q = re.findall(r'"([^"]+)"', line)
+                self.quotes += q
+                self.given_quotes += q if "GIVEN block" in line else []
+
+    def command(self) -> str:
+        """The WHEN line's text between its first and last backtick."""
+        w = self.whens[0]
+        return w[w.find("`") + 1:w.rfind("`")]
+
+
+def _ticket(root: Path, tid: str) -> dict:
+    p = root / "tickets" / f"{tid}.yaml"
+    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.is_file() else {}
+
+
+def _ticket_under_test(root: Path, checkout: Path) -> str | None:
+    """The ticket whose checkout this is, by the store's own layout: `worktrees/<id>` (the
+    implementer's worktree) or `runs/<run>/wt` (a checker's checkout, ticket in the run's meta.yaml)."""
+    if checkout.parent == root / "worktrees":
+        return checkout.name
+    meta = checkout.parent / "meta.yaml"
+    if checkout.name == "wt" and checkout.parent.parent == root / "runs" and meta.is_file():
+        return (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("ticket")
+    return None
+
+
+def folded_ids(root: Path, tid: str | None) -> list[str]:
+    """The ticket under test's change (its parent's, or its own), plus every unarchived change whose
+    ticket is not closed and has a merged sub-ticket: that code is on the integration branch before
+    its scenarios reach current truth."""
+    changes = specstore.root_dir(root) / "changes"
+    tickets = [yaml.safe_load(p.read_text(encoding="utf-8")) or {} for p in sorted((root / "tickets").glob("*.yaml"))]
+    merged = {t.get("parent") for t in tickets if t.get("status") == "merged"}
+    ids = {d.name for d in (changes.iterdir() if changes.is_dir() else ())
+           if d.is_dir() and d.name != "archive" and d.name in merged and _ticket(root, d.name).get("status") != "closed"}
+    if tid:
+        cid = _ticket(root, tid).get("parent") or tid
+        ids |= {cid} if (changes / cid).is_dir() else set()
+    return sorted(ids)
+
+
+def fold(root: Path, ids: list[str]) -> tuple[dict[str, str], dict[tuple[str, str], str]]:
+    """Current truth with each change's delta applied, in order, as archive applies it; and, per
+    (capability, scenario) in an ADDED or MODIFIED requirement of a folded delta, that change's id."""
+    truth = {p.parent.name: p.read_text(encoding="utf-8")
+             for p in sorted((specstore.root_dir(root) / "specs").glob("*/spec.md"))}
+    owner: dict[tuple[str, str], str] = {}
+    for cid in ids:
+        errors = []
+        for part in sorted((specstore.change_dir(root, cid) / "specs").glob("*/spec.md")):
+            cap = part.parent.name
+            ops, errs = specstore.parse_delta(part.read_text(encoding="utf-8"))
+            # specstore.applies' check, against the text folded so far rather than the store's files
+            have = specstore.requirement_blocks(truth.get(cap, ""))
+            errs += [f"ADDED {n!r} is already in current truth ({cap})" for n in ops.get("ADDED", {}) if n in have]
+            errs += [f"{op} {n!r} is not in current truth ({cap})"
+                     for op in ("MODIFIED", "REMOVED") for n in ops.get(op, {}) if n not in have]
+            if errs or not any(ops.values()):
+                errors += errs
+                continue
+            truth[cap] = specstore.apply_delta(truth.get(cap, ""), cap, ops)
+            for op in ("ADDED", "MODIFIED"):
+                for b in ops.get(op, {}).values():
+                    owner.update({(cap, n): cid for n in specstore.scenario_names(b)})
+        if errors:
+            raise Refused(f"truth check: the approved delta of {cid} does not apply to current truth: {'; '.join(errors)}")
+    return truth, owner
+
+
+def skip_reason(sc: Scenario, owner: dict, names: set[str], skip_texts: list[str]) -> str | None:
+    if (sc.cap, sc.name) in owner:
+        return f"in the approved delta of {owner[(sc.cap, sc.name)]}, which that ticket's verifier checks"
+    if len(sc.whens) != 1:
+        return "has no WHEN line" if not sc.whens else "has more than one WHEN line"
+    cmd = sc.command()
+    if sc.whens[0].count("`") < 2 or not cmd.strip():
+        return "its WHEN is not one backticked command"
+    for t in skip_texts:
+        if t in cmd:
+            return f'its WHEN contains "{t}", which this run skips'
+    for q in sc.given_quotes:
+        if q not in names:
+            return f'needs the GIVEN block of "{q}", which current truth does not hold'
+    if not sc.thens:
+        return "has no THEN line"
+    if len(sc.thens) > 1:
+        return "has more than one THEN line"
+    if expected(sc.thens[0], sc.then_block) is None:
+        return f"THEN is not an exact print: {sc.thens[0]}"
+    return None
+
+
+def _bash(text: str, cwd: Path, env: dict) -> subprocess.CompletedProcess:
+    return subprocess.run(["bash", "-c", text], cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True)
+
+
+def _run_capability(todo: list[Scenario], refs, checkout: Path) -> dict[int, subprocess.CompletedProcess]:
+    """Runs one capability's scenarios in file order, in a fresh HOME and TMPDIR, each after the
+    GIVEN blocks it needs (each reference's needs first, then its own); a block runs at most once."""
+    d = Path(tempfile.mkdtemp(prefix="factory-truth-"))
+    (d / "home").mkdir()
+    (d / "tmp").mkdir()
+    env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
+    env.update(HOME=str(d / "home"), TMPDIR=str(d / "tmp"))
+
+    def needs(sc: Scenario, path: tuple[int, ...]) -> list[tuple[tuple[int, int], str]]:
+        out = [k for r in refs(sc) if id(r) not in path for k in needs(r, (*path, id(r)))]
+        return out + [((id(sc), i), b) for i, b in enumerate(sc.given)]
+
+    ran, results = set(), {}
+    try:
+        for sc in todo:
+            for key, block in needs(sc, (id(sc),)):
+                if key not in ran:
+                    ran.add(key)
+                    _bash(block, checkout, env)  # a GIVEN block's exit status is not compared
+            results[id(sc)] = _bash(sc.command(), checkout, env)
+    finally:
+        shutil.rmtree(d, ignore_errors=True)
+    return results
+
+
+def _lines(b: bytes) -> list[str]:
+    s = b.decode("utf-8", errors="replace").removesuffix("\n")
+    return s.split("\n") if s else []
+
+
+def _store(a) -> Path:
+    cwd = instance.caller_cwd()
+    if a.store:
+        return (cwd / Path(a.store).expanduser()).resolve()
+    inst = instance.find()
+    root = instance.env_path("FACTORY_STATE") or (
+        instance.state_root(inst, instance.load_config(inst)) if inst is not None else None)
+    if root is None:
+        raise Refused(f"truth check: no store found: give --store PATH, set FACTORY_STATE, or run from "
+                      f"inside an instance ({instance.not_found_message()})")
+    return root.resolve()
+
+
+def check(a) -> int:
+    """Replays current truth; prints one line per scenario and the counts. 1 when any failed."""
+    root = _store(a)
+    if not (specstore.root_dir(root) / "specs").is_dir():
+        raise Refused(f"truth check: {root} has no current truth (openspec/specs)")
+    for c in a.capability:
+        if not specstore.truth_path(root, c).is_file():
+            raise Refused(f"truth check: no capability {c} in current truth")
+    cwd = instance.caller_cwd()
+    top = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
+    if top.returncode != 0:
+        raise Refused(f"truth check: {cwd} is not inside a git checkout")
+    checkout = Path(top.stdout.strip()).resolve()
+    ids = folded_ids(root, _ticket_under_test(root, checkout))
+    start = time.monotonic()
+    truth, owner = fold(root, ids)
+    caps = {c: [Scenario(c, n, b) for n, b in specstore.scenario_blocks(f"=== specs/x/spec.md\n{t}").items()]
+            for c, t in sorted(truth.items())}  # scenario_blocks reads delta parts: give the text one
+    flat = [s for scs in caps.values() for s in scs]
+    names = {s.name for s in flat}
+
+    def refs(sc: Scenario) -> list[Scenario]:
+        order = caps[sc.cap] + flat  # the same capability first, then capability order
+        return [next(s for s in order if s.name == q) for q in sc.quotes if q in names]
+
+    shown = sorted(set(a.capability) or caps)
+    skips = {id(s): skip_reason(s, owner, names, a.skip_when_contains) for c in shown for s in caps.get(c, [])}
+    with ThreadPoolExecutor(max_workers=max(len(shown), 1)) as ex:
+        runs = [ex.submit(_run_capability, [s for s in caps.get(c, []) if not skips[id(s)]], refs, checkout)
+                for c in shown]
+        results = {k: v for f in runs for k, v in f.result().items()}
+    wall = int(time.monotonic() - start)
+    print(f"truth check: {checkout} against {root}; folded: {', '.join(ids) or 'none'}")
+    n = {"PASS": 0, "FAIL": 0, "SKIPPED": 0}
+    for c in shown:
+        for s in caps.get(c, []):
+            if skips[id(s)]:
+                n["SKIPPED"] += 1
+                print(f"SKIPPED {c}: {s.name}: {skips[id(s)]}")
+                continue
+            cp, (want, exits) = results[id(s)], expected(s.thens[0], s.then_block)
+            got = _lines(cp.stdout)
+            verdict = "PASS" if got == want and (cp.returncode == 0 or not exits) else "FAIL"
+            n[verdict] += 1
+            print(f"{verdict} {c}: {s.name}")
+            if verdict == "FAIL":
+                print("\n".join(["  expected:", *(f"    {x}" for x in want), "  got:", *(f"    {x}" for x in got[:40]),
+                                 *([f"    … {len(got) - 40} more lines"] if len(got) > 40 else []),
+                                 f"  exit {cp.returncode}",
+                                 *(["  stderr:", *(f"    {x}" for x in _lines(cp.stderr)[-5:])] if cp.stderr else [])]))
+    print(f"{sum(n.values())} scenarios: {n['PASS']} passed, {n['FAIL']} failed, {n['SKIPPED']} skipped; "
+          f"wall time {wall} s")
+    return 1 if n["FAIL"] else 0
+
+
+def add_parser(sp) -> None:
+    """`factory truth check`, built here so factory/cli.py stays under its line limit."""
+    p = sp.add_parser("truth", help="replay current truth's scenarios against this checkout; reads, writes nothing")
+    p = p.add_subparsers(dest="sub", required=True).add_parser(
+        "check", help="run each current-truth scenario's WHEN under bash and compare its output with the THEN")
+    p.add_argument("--store", metavar="PATH", help="the store to read; default: FACTORY_STATE, else the instance's own store")
+    p.add_argument("--capability", action="append", default=[], metavar="NAME",
+                   help="report and run only this capability (repeatable)")
+    p.add_argument("--skip-when-contains", action="append", default=[], metavar="TEXT",
+                   help="skip, and list, each scenario whose WHEN contains TEXT (repeatable)")
+    p.set_defaults(fn=check)
diff --git a/tests/factory/test_truth.py b/tests/factory/test_truth.py
new file mode 100644
index 0000000..e80e4bc
--- /dev/null
+++ b/tests/factory/test_truth.py
@@ -0,0 +1,203 @@
+"""T-0059 (issue #120): `factory truth check` replays every current-truth scenario under bash in the
+checkout under test, compares each WHEN's stdout with its THEN by the exact-print rule, lists what it
+cannot check as skipped with a reason, and folds the approved deltas whose code is under test or
+merged before it runs.
+
+The rule is tested on `factory.truth.expected`, in one Python process run from the repository root
+(tests/factory is itself a package named `factory`); the command black-box through the CLI on
+throwaway stores built from files, each with a scratch git checkout as the caller's directory.
+"""
+from __future__ import annotations
+
+import json
+import subprocess
+import sys
+from pathlib import Path
+
+import pytest
+
+from ._cli import REPO, cli, git_repo, js
+
+F = "```"
+
+
+def read(cases: list) -> list:
+    """`factory.truth.expected(then, block)` for each (then, block), as JSON: a tuple reads as a list."""
+    code = "import json, sys\nfrom factory import truth\nprint(json.dumps([truth.expected(*c) for c in json.load(sys.stdin)]))"
+    cp = subprocess.run([sys.executable, "-c", code], input=json.dumps(cases), cwd=REPO, capture_output=True, text=True)
+    assert cp.returncode == 0, cp.stderr
+    return json.loads(cp.stdout)
+
+
+READ = [
+    ("it prints `hello`", None, (["hello"], False)),
+    ("it prints exactly `hello`.", None, (["hello"], False)),
+    ("it prints only `a  b`, then `c`", None, (["a  b", "c"], False)),
+    ("it prints `a`, and `b`, `c` and `d`", None, (["a", "b", "c", "d"], False)),
+    ("it prints `ok` and exits 0", None, (["ok"], True)),
+    ("it prints `ok`, and exits 0", None, (["ok"], True)),
+    ("it prints exactly `x`, `y`, one per line", None, (["x", "y"], False)),
+    ("it prints exactly `x` twice, then `y`, three times, one per line", None, (["x", "x", "y", "y", "y"], False)),
+    ("it prints `hello`, then `bye` (the farewell second)", None, (["hello", "bye"], False)),
+    ("it prints exactly two lines: `one`, then `two`", None, (["one", "two"], False)),
+    ("it prints exactly these 2 lines, one per line: `one`, then `two`", None, (["one", "two"], False)),
+    ("it prints exactly three lines, each `same`", None, (["same"] * 3, False)),
+    ("it prints exactly two lines, each exactly `s`, then `t`", None, (["s", "s", "t"], False)),
+    ("it prints exactly these 2 lines:", ["a", "b"], (["a", "b"], False)),
+]
+UNREAD = [
+    ("it prints a friendly greeting", None),
+    ("it exits 0", None),
+    ("it prints `x`. The rest is ignored.", None),
+    ("it prints two numbers: the first below 910, the second `3`", None),
+    ("it prints one line, `files=<n>`, with n above 0", None),
+    ("it prints exactly these 2 lines:", None),
+    ("it prints exactly eleven lines, each `x`", None),
+    ("it prints `x` (a note with `ticks`)", None),
+    ("it prints `x` or `y`", None),
+]
+
+
+def test_exact_print_rule_reads_each_form_and_refuses_what_it_cannot_read_in_full():
+    got = read([[t, b] for t, b, _ in READ] + [list(c) for c in UNREAD])
+    assert got[:len(READ)] == [[w[0], w[1]] for _, _, w in READ]
+    assert got[len(READ):] == [None] * len(UNREAD)
+
+
+def scenario(name: str, when: str | None, then: str | None, extra: str = "") -> str:
+    lines = [f"#### Scenario: {name}", *([extra] if extra else []),
+             *([f"- WHEN `{when}`"] if when is not None else []), *([f"- THEN {then}"] if then is not None else [])]
+    return "\n".join(lines) + "\n"
+
+
+def capability(store: Path, cap: str, *scenarios: str, req: str = "It works") -> None:
+    p = store / "openspec" / "specs" / cap / "spec.md"
+    p.parent.mkdir(parents=True, exist_ok=True)
+    p.write_text(f"# {cap}\n\n## Requirements\n\n### Requirement: {req}\nIt SHALL work.\n\n" + "\n".join(scenarios))
+
+
+def write_ticket(store: Path, tid: str, status: str, parent: str | None = None) -> None:
+    (store / "tickets").mkdir(parents=True, exist_ok=True)
+    (store / "tickets" / f"{tid}.yaml").write_text(f"id: {tid}\nstatus: {status}\nparent: {parent or 'null'}\n")
+
+
+def delta(store: Path, cid: str, cap: str, text: str) -> None:
+    p = store / "openspec" / "changes" / cid / "specs" / cap / "spec.md"
+    p.parent.mkdir(parents=True, exist_ok=True)
+    p.write_text(text)
+
+
+def results(cp) -> list[str]:
+    return [ln for ln in cp.stdout.splitlines() if ln.split(" ", 1)[0] in ("PASS", "FAIL", "SKIPPED")]
+
+
+@pytest.fixture
+def repo(tmp_path):
+    return git_repo(tmp_path / "repo")
+
+
+def test_each_skip_reason_is_listed_and_counted_and_never_passed(tmp_path, repo):
+    s = tmp_path / "s"
+    given = f"- GIVEN the block below\n\n{F}sh\necho given > $TMPDIR/g\n{F}\n"
+    capability(s, "a",
+               scenario("No WHEN", None, "it prints `x`"),
+               scenario("Two WHENs", "echo x", "it prints `x`", extra="- WHEN `echo y`"),
+               scenario("A bare WHEN", None, "it prints `x`", extra="- WHEN echo x"),
+               scenario("A slow one", "echo slow-marker", "it prints `slow-marker`"),
+               scenario("A missing fixture", "echo x", "it prints `x`", extra='Needs the GIVEN block of "Nowhere" run once.'),
+               scenario("No THEN", "echo x", None),
+               scenario("Prose", "echo x", "it prints an x"),
+               scenario("A fixture", "cat $TMPDIR/g", "it prints exactly `given`", extra=given),
+               scenario("A reuse", "cat $TMPDIR/g", "it prints exactly `given`",
+                        extra='Needs the GIVEN block of "A fixture" run once.'))
+    cp = cli(repo, "truth", "check", "--store", str(s), "--skip-when-contains", "slow-marker")
+    assert cp.returncode == 0, cp.stderr
+    assert results(cp) == [
+        "SKIPPED a: No WHEN: has no WHEN line",
+        "SKIPPED a: Two WHENs: has more than one WHEN line",
+        "SKIPPED a: A bare WHEN: its WHEN is not one backticked command",
+        'SKIPPED a: A slow one: its WHEN contains "slow-marker", which this run skips',
+        'SKIPPED a: A missing fixture: needs the GIVEN block of "Nowhere", which current truth does not hold',
+        "SKIPPED a: No THEN: has no THEN line",
+        "SKIPPED a: Prose: THEN is not an exact print: it prints an x",
+        "PASS a: A fixture",
+        "PASS a: A reuse",
+    ]
+    assert cp.stdout.splitlines()[-1].startswith("9 scenarios: 2 passed, 0 failed, 7 skipped; wall time ")
+
+
+def test_a_failure_shows_expected_got_exit_and_stderr_and_exits_1(tmp_path, repo):
+    s = tmp_path / "s"
+    capability(s, "a", scenario("Long", "seq 45; echo oops >&2; exit 4", "it prints `1`"),
+               scenario("Status", "echo ok; exit 3", "it prints `ok` and exits 0"))
+    cp = cli(repo, "truth", "check", "--store", str(s))
+    assert cp.returncode == 1, cp.stderr
+    out = cp.stdout.splitlines()
+    assert out[0] == f"truth check: {repo.resolve()} against {s.resolve()}; folded: none"
+    i = out.index("FAIL a: Long")
+    assert out[i + 1:i + 4] == ["  expected:", "    1", "  got:"]
+    assert out[i + 4:i + 44] == [f"    {n}" for n in range(1, 41)]
+    assert out[i + 44:i + 48] == ["    … 5 more lines", "  exit 4", "  stderr:", "    oops"]
+    assert out[i + 48:i + 54] == ["FAIL a: Status", "  expected:", "    ok", "  got:", "    ok", "  exit 3"]
+    assert out[-1].startswith("2 scenarios: 0 passed, 2 failed, 0 skipped;")
+
+
+def test_the_ticket_under_test_and_open_tickets_with_merged_code_are_folded(tmp_path, repo):
+    s = tmp_path / "s"
+    capability(s, "a", scenario("Old greeting", "echo hello", "it prints `hello`"), req="Greets")
+    capability(s, "b", scenario("Same name", "echo b", "it prints `b`"))
+    new = "## MODIFIED Requirements\n\n### Requirement: Greets\nIt SHALL greet anew.\n\n" + scenario(
+        "Same name", "echo new", "it prints `nope`")
+    for cid, status in (("T-0001", "planned"), ("T-0002", "planned"), ("T-0003", "closed"), ("T-0004", "planned")):
+        write_ticket(s, cid, status)
+        delta(s, cid, "a", new)
+    write_ticket(s, "T-0001.1", "checks-in-flight", "T-0001")
+    write_ticket(s, "T-0002.1", "merged", "T-0002")
+    write_ticket(s, "T-0003.1", "merged", "T-0003")
+    wt, k = s / "worktrees" / "T-0001.1", s / "runs" / "run-0002-verifier" / "wt"
+    for co in (wt, k):
+        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "--detach", str(co)], check=True)
+    (k.parent / "meta.yaml").write_text("role: verifier\nticket: T-0004\n")  # a ticket with no parent folds its own
+
+    cp = cli(repo, "truth", "check", "--store", str(s))
+    assert cp.returncode == 0, cp.stderr
+    assert cp.stdout.splitlines()[0] == f"truth check: {repo.resolve()} against {s.resolve()}; folded: T-0002"
+    # a scenario of another capability with the same name still runs
+    assert results(cp) == ["SKIPPED a: Same name: in the approved delta of T-0002, which that ticket's verifier checks",
+                           "PASS b: Same name"]
+    for co, folded in ((wt, "T-0001, T-0002"), (k, "T-0002, T-0004")):
+        cp = cli(co, "truth", "check", "--store", str(s))
+        assert cp.stdout.splitlines()[0] == f"truth check: {co.resolve()} against {s.resolve()}; folded: {folded}"
+        last = folded.split(", ")[-1]  # the later delta's id wins
+        assert results(cp)[0] == f"SKIPPED a: Same name: in the approved delta of {last}, which that ticket's verifier checks"
+
+
+def test_a_delta_that_does_not_apply_is_refused_naming_its_ticket_and_nothing_runs(tmp_path, repo):
+    s = tmp_path / "s"
+    capability(s, "a", scenario("Writes", f"touch {tmp_path}/ran; echo x", "it prints `x`"))
+    write_ticket(s, "T-0005", "planned")
+    write_ticket(s, "T-0005.1", "merged", "T-0005")
+    delta(s, "T-0005", "a", "## ADDED Requirements\n\n### Requirement: It works\nAgain.\n")
+    cp = cli(repo, "truth", "check", "--store", str(s))
+    assert cp.returncode == 2
+    assert cp.stderr.strip() == ("truth check: the approved delta of T-0005 does not apply to current truth: "
+                                 "ADDED 'It works' is already in current truth (a)")
+    assert js(cp)["ok"] is False and not results(cp) and not (tmp_path / "ran").exists()
+
+
+def test_refusals(tmp_path, repo):
+    s = tmp_path / "s"
+    capability(s, "a", scenario("One", "echo 1", "it prints `1`"))
+    (tmp_path / "bare").mkdir()
+    cases = [
+        (repo, ["--store", str(s), "--capability", "nope"], "truth check: no capability nope in current truth"),
+        (repo, ["--store", str(tmp_path / "bare")], f"truth check: {(tmp_path / 'bare').resolve()} has no current truth (openspec/specs)"),
+        (tmp_path / "bare", ["--store", str(s)], f"truth check: {(tmp_path / 'bare').resolve()} is not inside a git checkout"),
+    ]
+    for cwd, argv, err in cases:
+        cp = cli(cwd, "truth", "check", *argv)
+        assert (cp.returncode, cp.stderr.strip(), js(cp)["ok"]) == (2, err, False)
+    z = "0123456789abcdef0123456789abcdef01234567"
+    cp = cli(repo, "--accept-harness", z, "truth", "check", "--store", str(s))
+    assert cp.returncode == 2 and "factory truth check never checks the harness lock" in cp.stderr
+    assert f"factory --accept-harness {z} config" in cp.stderr
