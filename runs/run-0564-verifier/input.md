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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0564-verifier/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0564-verifier/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0564-verifier/wt` (branch `factory/T-0058.1`, base `788a201a34fb3a416b394a14fba65583989c24c9`, head `6f4d8658252556ed62bd19e130b09634f119f454`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0058.1

T-0058.1 / Four small harness defects: the escalation parser counts Claude Code's attribution footer as escalations, a build-dispatch scenario fails under macOS /bin/sh, `factory init` exits 1 on an unreadable agent copy, and `--accept-harness` is silently ignored by `init`, `paths` and `stats` (#88, #113, #114, #115)
Depends on: none
Parallel-safe: yes

Parent: T-0058, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A none trailer followed by the attribution footer finishes with no escalation and queues nothing
- A real item above the attribution footer stays, and the footer is dropped
- Real item lines, and a line that only mentions Claude Code, are still read by rule (b)
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy
- init reports an edited agent copy and leaves it as it is
- init still creates a missing agent copy and lists no matching copy
- init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance
- Without the flag paths and stats still run under another lock, and config still accepts a revision
- README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy
- The design doc states the footer rule and the refusal in the lock clause
- The changelog records the four issues in one entry without a numbering gap
- The harness suite passes
- The only existing test file changed is the stats test
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0058/v3.md`

=== proposal.md
## Problem

This ticket fixes four small defects in the harness. The harness is the code that runs the factory's AI roles and keeps their records. None of the defects changes where a ticket goes next. Each one leaves a record that is wrong, or a command that fails or silently does nothing, and a person has to notice it and work around it.

1. **A false escalation in the run record.** Every role ends its output with a three-line trailer: STATUS (its verdict), CONFIDENCE and ESCALATIONS (the items it wants a human to see). The harness reads that trailer when the run finishes. If the ESCALATIONS line says `none` and further lines follow it, the harness treats the whole block as a real list of items. The operator chose that rule on 2026-10-01 (the code calls it rule (b)). Claude Code sometimes appends its own attribution line, `🤖 Generated with [Claude Code](…)`, after the trailer. When it does, the harness records two escalations the role never raised, `none` and the footer, and logs a false "escalation queued" event. This has happened once on each of the two repositories the factory runs on.
2. **A scenario that fails under macOS's `/bin/sh`.** Current truth is the store's record of each capability's accepted behaviour. Each requirement in it carries scenarios, which are shell commands with the output they must print. One scenario puts a `case` statement inside `$( )` without a leading parenthesis on its patterns. The bash 3.2 that macOS ships as `/bin/sh` cannot parse that, so the scenario fails whatever the code does. A check that runs current truth under that shell would report a regression the code did not cause. Such a check is queued as the next ticket (#120).
3. **`factory init` fails on an agent copy it cannot read.** `factory init` sets a repository up for the factory. Since the fix for #108, it also compares each copy of an agent definition in the repository (`.claude/agents/factory-*.md`) with the harness's template. It lists a copy that differs under `stale_agents` in its JSON output, and leaves it alone. If a copy exists but cannot be read, init crashes with exit 1 instead. Before #108 it exited 0.
4. **`--accept-harness` is silently ignored by three commands.** Each repository records which harness revision it has agreed to run, in a lock file, and the harness refuses to touch that repository's store under any other revision. The operator agrees to a new revision by adding `--accept-harness <sha>` to a command. Three commands, `init`, `paths` and `stats`, never check the lock, so they drop the flag without a word. On 2026-10-19 the operator ran `--accept-harness … paths` on the Nanobot target. The command looked as if it had worked, and the lock was left unchanged.

## Root cause

- **#88.** `factory/status.py` `parse()`, lines 37-49. Every non-blank line below the ESCALATIONS line goes into `tail`. A non-empty `tail` makes `[esc_head, *tail]` the item list, as the 2026-10-01 rule (b) says. Nothing tells the attribution footer apart from an item line. `run finish` uses this parser for both the drive and the Workflow-script path (`factory/workflows/intake.js:143` logs `fin.escalations` from `run finish`).
- **#113.** The scenario text in current truth. Bash before 4.0 ends a command substitution at the first `)`, and an unparenthesised case pattern has one. This is not a code defect.
- **#114.** `factory/setup.py:187`: `(dest / src.name).read_bytes()` raises `PermissionError`. The generic handler in `factory/cli.py` `main()` turns that into exit 1.
- **#115.** `factory/cli.py:851-855`: `main()` runs `init`, `paths` and `stats` and returns before `instance.guard(…, a.accept_harness)` at line 863, so nothing reads the flag for those three. The comment at line 852 says "ignore --accept-harness".

## Out of scope

- Setting `attribution.pr` (or any `--settings`) on the role processes `factory drive` starts. See Decisions.
- Any other footer or trailer form, such as `Co-Authored-By:` lines. None appears in either store's escalation records.
- A check that no current-truth scenario has an unparenthesised `case` inside `$( )`, which #113 suggests as optional.
- Every other scenario in current truth, and any code change for #113.
- What the harness lock and the live-store fence do for every command other than `init`, `paths` and `stats`. The live-store fence is the guard that keeps writes out of a store while a role run is in flight.
- The shape of `stale_agents` (a list of paths), and creating missing copies. Init never overwrites, repairs or changes the permissions of an existing copy.
- Rule (b) for real item lines below a `none` head.
- Past run records. The false items in run-0418 and run-0538 stay as they are.

## Open questions

none

## Decisions

- #88 is fixed in the parser. Before rule (b) is applied, the trailer parser, `parse()` in `factory/status.py`, drops each line below the ESCALATIONS line that, after its list marker is stripped, is exactly `🤖 Generated with [Claude Code](<link>)`, with any link and nothing else on the line. Rule (b) applies unchanged to the lines that are left.
- Rejected for #88: passing `attribution.pr` through `--settings` to the role processes that `factory drive` (the command that runs each role as a headless `claude -p` process) starts. The key exists, but its effect on a `claude -p` reply is unverified. The footer appeared in 2 of 990 runs, so no acceptance check could show the setting works. It would also not cover the Workflow-script path (the older way of running the roles, beside the drive), which goes through the same parser.
- Rejected for #88: ignoring everything after a blank line below the trailer. That would break rule (b) for real items separated by blank lines.
- Standing decision for later tickets: the trailer parser drops only the exact Claude Code attribution footer. Any other text below the ESCALATIONS line stays an item under rule (b). Recognising a new footer form needs its own ticket.
- #113 changes only the two patterns of that one `case`, to `($T/tmp/factory-launch-*/$s.js)` and `(*)`. The rest of the requirement is restated word for word. This is a spec delta, so current truth changes when the ticket is archived.
- #114: an existing copy whose read raises any `OSError` is listed under `stale_agents` by its path, as a differing copy is. Stderr gets one line that names the copy and says it `could not be read`, with the error. Init exits 0 and leaves the copy as it is. The JSON shape does not change, which keeps T-0052's decision that `stale_agents` is a list of paths.
- #115: `factory --accept-harness <sha>` with `init`, `paths` or `stats` is refused with exit 2 before anything else runs, on any store, whether or not a run is in flight, and writes nothing. The message names the command and gives `factory --accept-harness <sha> config`, with the sha the operator passed, as the command to run instead. `config` reads nothing it could break and reaches the lock.
- That overturns the 2026-10-12 T-0043 decision that `stats` ignores `--accept-harness`, and the same behaviour in `init` and `paths`. Standing decision for later tickets: a command that skips the harness lock refuses `--accept-harness` and never ignores it.
- README's "Upgrading the runtime" step 2 names `factory --accept-harness <sha> config` as the command to run. It no longer says "any store command", which would now include three that refuse the flag.

## Risk

Blast radius:
- The parser change touches every `run finish`, for every role, on both instances, once the runtime moves to the merge. The match is one exact line form, so the only result that changes is a trailer followed by that footer.
- The `init` change affects only a copy that cannot be read, which today crashes.
- The `--accept-harness` refusal turns a silent no-op into exit 2 for three commands. A script that passes the flag to them would now stop. None does in the harness, in either workflow script or in the tests, apart from the one test listed under "Tests to change".
- The #113 edit reaches current truth only at archive. Until then current truth keeps the scenario that breaks under `/bin/sh`.

Protected paths: `factory/status.py`, `factory/setup.py`, `factory/cli.py`

=== design.md
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

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: Claude Code's attribution footer below the trailer is not an escalation
When a role's output has, below its ESCALATIONS line, a line that is exactly Claude Code's attribution footer `🤖 Generated with [Claude Code](<link>)`, `run finish` and `status parse` SHALL drop that line before applying the escalation rule, and MUST apply the rule unchanged to every other line below the ESCALATIONS line.

#### Scenario: A none trailer followed by the attribution footer finishes with no escalation and queues nothing
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p') && bin/factory run compose $R >/dev/null && printf 'Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\nSTATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n\n\360\237\244\226 Generated with [Claude Code](https://claude.com/claude-code)\n' > $FACTORY_STATE/runs/$R/output.md && bin/factory run finish $R | tail -1 | python3 -c 'import json, sys; print("finish=" + json.dumps(json.load(sys.stdin)["escalations"], ensure_ascii=False))'; echo "queued=$(cat $FACTORY_STATE/log/*.jsonl | grep -c '"escalation.queued"') meta=$(grep -c 'Generated with' $FACTORY_STATE/runs/$R/meta.yaml)")`
- THEN it prints exactly `finish=[]`, then `queued=0 meta=0`

#### Scenario: A real item above the attribution footer stays, and the footer is dropped
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; printf 'body\nSTATUS: APPROVE\nCONFIDENCE: high, ok\nESCALATIONS: none\n- the auth path needs review\n\n\360\237\244\226 Generated with [Claude Code](https://claude.ai/code)\n' > $T/o.md && bin/factory status parse $T/o.md | tail -1 | python3 -c 'import json, sys; print(json.dumps(json.load(sys.stdin)["escalations"], ensure_ascii=False))')`
- THEN it prints exactly `["none", "the auth path needs review"]`

#### Scenario: Real item lines, and a line that only mentions Claude Code, are still read by rule (b)
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; for t in 'ESCALATIONS: none. x\n- extra line\n' 'ESCALATIONS:\n- one\n- two\n' 'ESCALATIONS: none\n- Generated with Claude Code, says the footer\n' 'ESCALATIONS: none\n'; do printf "body\nSTATUS: APPROVE\nCONFIDENCE: high, ok\n$t" > $T/o.md && bin/factory status parse $T/o.md | tail -1 | python3 -c 'import json, sys; print(json.dumps(json.load(sys.stdin)["escalations"]))'; done)`
- THEN it prints exactly `["none. x", "extra line"]`, `["one", "two"]`, `["none", "Generated with Claude Code, says the footer"]`, `[]`, one per line

## MODIFIED Requirements

### Requirement: factory launch-script writes a launch copy that differs from its script in one line, wherever factory config would run
`factory launch-script intake|build` MUST write, in a new directory named `factory-launch-*` under the temporary directory, a read-only copy of that workflow script. The copy SHALL differ from the script in one line, which holds the instance's models, round limits and store as `factory config` reports them, the running harness revision and the instance. The command SHALL write nothing to the checkout or the store. Before writing, it SHALL remove each earlier `factory-launch-*` directory under the temporary directory that is more than one hour old and holds only a launch copy, and SHALL remove no other directory. Wherever `factory config` refuses, it MUST refuse with exit 2 and the same error, writing no copy.

#### Scenario: Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; mkdir $T/tmp; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; G0=$(git status --porcelain | cksum); S0=$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum); P=$(bin/factory paths); R=$(echo "$P" | sed -n 's/.*"harness_revision": "\([0-9a-f]*\)".*/\1/p'); I=$(echo "$P" | sed -n 's/.*"instance": "\([^"]*\)".*/\1/p'); for s in intake build; do C=$(TMPDIR=$T/tmp bin/factory launch-script $s 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'); L=$(diff factory/workflows/$s.js "${C:-/dev/null}" | grep '^>'); echo "$s: where=$(case "$C" in ($T/tmp/factory-launch-*/$s.js) echo own-dir;; (*) echo none;; esac) changed=$(diff factory/workflows/$s.js "${C:-/dev/null}" | grep -c '^[<>]') revision=$(echo "$L" | grep -cF "\"harness_revision\": \"$R\"") instance=$(echo "$L" | grep -cF "\"instance\": \"$I\"") writable=$([ -n "$C" ] && [ -w "$C" ] && echo yes || echo no)"; done; echo "checkout=$([ "$(git status --porcelain | cksum)" = "$G0" ] && echo unchanged || echo changed) store=$([ "$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed) dirs=$(ls $T/tmp | grep -c '^factory-launch-')")`
- THEN it prints exactly `intake: where=own-dir changed=2 revision=1 instance=1 writable=no`, `build: where=own-dir changed=2 revision=1 instance=1 writable=no`, `checkout=unchanged store=unchanged dirs=2`, one per line

#### Scenario: launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
The target's own store is used, so the harness lock applies. Its lock names a revision that is not running.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && mkdir $T/tmp && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && echo 0000000000000000000000000000000000000000 > .factory/harness.lock; $B config >/dev/null 2>$T/c; c=$?; TMPDIR=$T/tmp $B launch-script build >/dev/null 2>$T/l; l=$?; echo "config=$c launch=$l same=$(cmp -s $T/c $T/l && echo yes || echo no) lock=$(grep -c 'is not the revision this instance accepted' $T/l) copies=$(ls $T/tmp | grep -c .)")`
- THEN it prints exactly `config=2 launch=2 same=yes lock=1 copies=0`

#### Scenario: launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; mkdir $T/tmp; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; c() { TMPDIR=$T/tmp bin/factory launch-script build 2>/dev/null | tail -1 | sed -n 's/.*"script": "\([^"]*\)".*/\1/p'; }; O=$(c); O=${O%/*}; F=$(c); F=${F%/*}; X=$T/tmp/factory-launch-other; mkdir $X && echo x > $X/build.js; touch -t 202001010000 $X; [ -n "$O" ] && touch -t 202001010000 "$O"; N=$(c); N=${N%/*}; k() { [ -n "$1" ] && [ -e "$1" ] && echo kept || echo gone; }; echo "old=$(k "$O") other=$(k $X) fresh=$(k "$F") new=$([ -n "$N" ] && [ -e "$N" ] && echo written || echo none) dirs=$(ls $T/tmp | grep -c '^factory-launch-')")`
- THEN it prints exactly `old=gone other=kept fresh=kept new=written dirs=3`

=== specs/store-setup/spec.md
## MODIFIED Requirements

### Requirement: init reports an agent copy that differs from its template and never overwrites it
When `factory init` runs for an instance's own store, it SHALL list each existing `.claude/agents/factory-*.md` copy whose bytes differ from its template, or that it cannot read, under `stale_agents` in its JSON output and name it on stderr, saying of a copy it cannot read that it could not be read. It MUST leave that copy unchanged and exit 0, and SHALL still create a missing copy without listing any matching copy.

#### Scenario: init reports an edited agent copy and leaves it as it is
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf 'local edit\n' >> .claude/agents/factory-planner.md && cp .claude/agents/factory-planner.md $T/kept && $B init >$T/out 2>$T/err; rc=$?; echo "exit=$rc stale=$(python3 -c 'import json, sys; o = json.load(sys.stdin); print(",".join(p.rsplit("/", 1)[-1] for p in o["stale_agents"]) if "stale_agents" in o else "absent")' < $T/out) kept=$(cmp -s $T/kept .claude/agents/factory-planner.md && echo yes || echo no) named=$(grep -c 'factory-planner\.md' $T/err) others=$(grep -v 'factory-planner\.md' $T/err | grep -c .)")`
- THEN it prints exactly `exit=0 stale=factory-planner.md kept=yes named=1 others=0`

#### Scenario: init still creates a missing agent copy and lists no matching copy
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; A=$PWD/agents; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .claude/agents/factory-triage.md && $B init >$T/out 2>$T/err; rc=$?; echo "exit=$rc $(python3 -c 'import json, sys; o = json.load(sys.stdin); print("created=" + ",".join(p.rsplit("/", 1)[-1] for p in o["agents"]) + " stale=" + str(len(o.get("stale_agents", []))))' < $T/out) same=$(for f in $A/factory-*.md; do cmp -s $f .claude/agents/$(basename $f) && echo x; done | grep -c .) differs=$(grep -c 'differs' $T/err)")`
- THEN it prints exactly `exit=0 created=factory-triage.md stale=0 same=6 differs=0`

#### Scenario: init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is
- GIVEN the shell runs as a user other than root, since root reads a file at mode `000`
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && cp .claude/agents/factory-planner.md $T/kept && chmod 000 .claude/agents/factory-planner.md && $B init >$T/out 2>$T/err; rc=$?; chmod 644 .claude/agents/factory-planner.md; echo "exit=$rc stale=$(python3 -c 'import json, sys; o = json.load(sys.stdin); print(",".join(p.rsplit("/", 1)[-1] for p in o["stale_agents"]) if "stale_agents" in o else "absent")' < $T/out) kept=$(cmp -s $T/kept .claude/agents/factory-planner.md && echo yes || echo no) named=$(grep -c 'factory-planner\.md' $T/err) unread=$(grep 'factory-planner\.md' $T/err | grep -c 'could not be read') others=$(grep -v 'factory-planner\.md' $T/err | grep -c .)")`
- THEN it prints exactly `exit=0 stale=factory-planner.md kept=yes named=1 unread=1 others=0`

=== specs/live-store-guard/spec.md
## ADDED Requirements

### Requirement: init, paths and stats refuse --accept-harness and name a command that accepts it
`factory --accept-harness <sha>` given with `init`, `paths` or `stats` MUST be refused with exit 2 and `{"ok": false, …}` on stdout, writing nothing. The refusal SHALL name the command and give `factory --accept-harness <sha> config` with the same sha. Without the flag, `paths` and `stats` SHALL still run under a lock that names another revision, and every other command SHALL keep its lock behaviour.

#### Scenario: The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; Z=0123456789abcdef0123456789abcdef01234567; snap() { find . -path ./.git -prune -o -type f -exec cksum {} + | sort | cksum; }; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && git init -q -b main $T/fresh && git -C $T/fresh -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && S0=$(snap) && for c in init paths stats; do $B --accept-harness $Z $c >$T/o 2>$T/e; echo "$c: exit=$? named=$(grep -cw "$c" $T/e) hint=$(grep -cF -- "factory --accept-harness $Z config" $T/e) json=$(grep -c '"ok": false' $T/o)"; done; echo "target=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)"; cd $T/fresh && $B --accept-harness $Z init --repo-name demo >/dev/null 2>&1; echo "fresh: exit=$? files=$(find . -path ./.git -prune -o -type f -print | grep -c .)")`
- THEN it prints exactly `init: exit=2 named=1 hint=1 json=1`, `paths: exit=2 named=1 hint=1 json=1`, `stats: exit=2 named=1 hint=1 json=1`, `target=unchanged`, `fresh: exit=2 files=0`, one per line

#### Scenario: Without the flag paths and stats still run under another lock, and config still accepts a revision
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && R=$($B paths | sed -n 's/.*"harness_revision": "\([0-9a-f]*\)".*/\1/p') && echo 0000000000000000000000000000000000000000 > .factory/harness.lock && $B paths >/dev/null 2>&1; p=$?; $B stats >/dev/null 2>&1; s=$?; $B config >/dev/null 2>&1; c=$?; $B --accept-harness $R config >/dev/null 2>&1; a=$?; echo "paths=$p stats=$s config=$c accept=$a lock=$([ "$(cat .factory/harness.lock)" = "$R" ] && echo accepted || echo other)")`
- THEN it prints exactly `paths=0 stats=0 config=2 accept=0 lock=accepted`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the footer rule, the unreadable agent copy and the --accept-harness refusal
README's "Accepting a harness revision" SHALL say, in one sentence, that `init`, `paths` and `stats` refuse `--accept-harness`. Step 2 of "Upgrading the runtime" SHALL name `--accept-harness <sha> config`. "Counting what each role catches and costs" SHALL say that `stats` refuses `--accept-harness`. The `.claude/agents/factory-*.md` row SHALL say that init reports a copy it cannot read. `docs/design.md`'s ESCALATIONS bullet SHALL name the dropped `Generated with [Claude Code]` footer, and its `harness.lock` clause SHALL say, in one sentence, that `init`, `paths` and `stats` refuse `--accept-harness`. `docs/changelog.md` SHALL hold one entry naming #88, #113, #114 and #115, numbered without a gap.

#### Scenario: README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy
- WHEN `(S=$(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' README.md); U=$(sed -n '/^### Upgrading the runtime/,/^### Installing the harness/p' README.md | grep '^2\. '); C=$(sed -n '/^### Counting what each role catches and costs/,/^```/p' README.md); echo "accepting=$(printf '%s' "$S" | python3 -c 'import re, sys; print(sum(1 for s in re.split(r"\.\s", sys.stdin.read()) if all(w in s for w in ("init", "paths", "stats", "--accept-harness")) and "refuse" in s))') upgrade=$(printf '%s' "$U" | grep -c -- '--accept-harness <sha> config') stats=$(printf '%s' "$C" | tr '\n' ' ' | grep -c 'refuses .--accept-harness.') row=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'cannot read')")`
- THEN it prints exactly `accepting=1 upgrade=1 stats=1 row=1`

#### Scenario: The design doc states the footer rule and the refusal in the lock clause
- WHEN `(echo "footer=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -cF 'Generated with [Claude Code]') lock=$(grep '^\*\*Role-context block\.\*\*' docs/design.md | python3 -c 'import re, sys; print(sum(1 for s in re.split(r"\.\s", sys.stdin.read()) if all(w in s for w in ("init", "paths", "stats", "--accept-harness")) and "refuse" in s))')")`
- THEN it prints exactly `footer=1 lock=1`

#### Scenario: The changelog records the four issues in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#88' | grep -F '#113' | grep -F '#114' | grep -F '#115'); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e 'Generated with' -e stale_agents -e '--accept-harness' -e '/bin/sh' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `4`

=== specs/harness-suite/spec.md
## ADDED Requirements

### Requirement: The suite passes with this change, which changes only the stats test the --accept-harness refusal overturns
The harness suite SHALL pass with this change, and among existing test files this change MUST modify or delete only `tests/factory/test_stats.py`.

#### Scenario: The harness suite passes
- WHEN `(uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1)`
- THEN its last line reports tests passed and no `failed` or `error`

#### Scenario: The only existing test file changed is the stats test
- WHEN `(git diff --name-only --diff-filter=MD $(git merge-base main HEAD) HEAD -- tests/factory)`
- THEN it prints nothing, or only `tests/factory/test_stats.py`

=== verification.md
## Acceptance

Every command was run on `main` at `788a201` from `~/dev/spec-factory`, under the running-code wrapper, with both `/bin/sh` (bash 3.2.57) and zsh. Both shells gave the same output.

- A none trailer followed by the attribution footer finishes with no escalation and queues nothing → NEW. Today it prints `finish=["none", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]` and `queued=1 meta=1`.
- A real item above the attribution footer stays, and the footer is dropped → NEW. Today it prints `["none", "the auth path needs review", "🤖 Generated with [Claude Code](https://claude.ai/code)"]`.
- Real item lines, and a line that only mentions Claude Code, are still read by rule (b) → REGRESSION. Today it prints the THEN exactly.
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance → REGRESSION.
  - Under zsh and bash 5, the old text and the restated text both print the THEN. Under `/bin/sh` only the restated text does.
  - #113 is an edit to scenario text, applied at archive, so no item can fail on the base code and pass on the PR. To check the restated text under the shell #113 concerns, run `(F=.factory/store/openspec/changes/T-0058/specs/build-dispatch/spec.md; T=$(mktemp -d); B=$(printf '\140'); sed -n '/^#### Scenario: Each launch copy is a one-line change/,/^- WHEN/p' $F | sed -n "s/^- WHEN $B\(.*\)$B\$/\1/p" > $T/w.sh; /bin/sh $T/w.sh)`. It must print the THEN.
  - With `F` set to current truth, `.factory/store/openspec/specs/build-dispatch/spec.md`, the same command prints `syntax error near unexpected token 'newline'` and `intake: where= echo own-dir;; *) echo none;; esac) …`. I ran both forms, with my restated text standing in for the change file.
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy → REGRESSION. It is restated word for word.
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy → REGRESSION. It is restated word for word.
- init reports an edited agent copy and leaves it as it is → REGRESSION. It is restated word for word.
- init still creates a missing agent copy and lists no matching copy → REGRESSION. It is restated word for word.
- init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is → NEW. Today it prints `exit=1 stale=absent kept=yes named=1 unread=0 others=0`. The `named=1` comes from the PermissionError line, which names the copy.
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance → NEW. Today it prints `init: exit=0 named=0 hint=0 json=0`, `paths: exit=0 named=0 hint=0 json=0`, `stats: exit=0 named=0 hint=0 json=0`, `target=unchanged`, `fresh: exit=0 files=16`.
- Without the flag paths and stats still run under another lock, and config still accepts a revision → REGRESSION. Today it prints `paths=0 stats=0 config=2 accept=0 lock=accepted`.
- README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy → NEW. Today it prints `accepting=0 upgrade=0 stats=0 row=0`.
- The design doc states the footer rule and the refusal in the lock clause → NEW. Today it prints `footer=0 lock=0`.
- The changelog records the four issues in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, `0`, `0`.
- The harness suite passes → REGRESSION. On `main` at `788a201`, under the wrapper, it printed `615 passed in 79.30s`.
- The only existing test file changed is the stats test → REGRESSION. On the base it prints nothing.
- Current truth also checked, not part of this delta: the harness-docs scenarios "README is at most 1,185 lines" and "The maintained documents pass git's whitespace check in full". "The documents record factory stats" also still passes, because the README "Accepting" section and design line 68 still name `stats`; I ran it today and it printed its THEN. So does "The design doc states the EMPTY-OUTPUT rule, its rows and its park".

## PR description (the implementer's output)

Sub-ticket: T-0058.1 (parent T-0058, spec v3: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0058/v3.md`). Branch `factory/T-0058.1`, commit `6f4d865` on base `788a201`.

## What changed

This change fixes four small defects in the harness (the code that runs the factory's AI roles and keeps their records). Each defect left a wrong record, or a command that failed or silently did nothing. None of them changed where a ticket goes next.

**A. Claude Code's attribution footer is no longer read as an escalation (#88). File: `factory/status.py`.** Every role ends its output with a STATUS / CONFIDENCE / ESCALATIONS trailer. Sometimes Claude Code adds a line after it: `🤖 Generated with [Claude Code](<link>)`. The trailer parser used to read `ESCALATIONS: none` with that line below it as two real escalations. The fix:
- New constant `ATTRIBUTION_RE`.
- `parse()` now drops every line below the ESCALATIONS line that matches that pattern exactly, after any list marker is stripped. It does this before the `none` rule. (That rule, "rule (b)", is the operator's 2026-10-01 decision: a `none` line with anything below it counts as a real list.)
- Rule (b) itself is unchanged, and so is `strip_trailer()`.
- I updated the module docstring and the rule (b) comment.

I checked who calls `status.parse` (grep): `cli.py:331` (`run finish`), `cli.py:629` (`status parse`), `gates.py:30` and `specstore.py:271`. They all go through this one function, so the fix sits there once.

**B. `factory init` handles an agent copy it cannot read (#114). File: `factory/setup.py`, the agent-copy loop in `init_cmd`.** Before, if a copy in `.claude/agents/` could not be read, init crashed with exit 1. Now:
- The comparison runs inside `try … except OSError`.
- If the copy cannot be read, it is added to `stale_agents` (the JSON list of copies init reports and leaves alone).
- Init prints one stderr line: `factory init: <copy> could not be read (<strerror>); left as it is`. It then moves on to the next template and exits 0.
- The copy is never written, chmod-ed or deleted.

The only caller is `cli.py:763`, through `set_defaults(fn=init_cmd)`.

**C. `init`, `paths` and `stats` refuse `--accept-harness` (#115). File: `factory/cli.py` `main()`.** Background: each repository records the harness revision it has agreed to run in a lock file, `harness.lock`. The operator agrees to a new revision by adding `--accept-harness <sha>` to a command. These three commands never check the lock, so before this change they dropped the flag without a word.
- The new first statement in the `try` refuses the flag for these three commands. It raises `Refused`, which ends with exit 2 and `{"ok": false, …}`.
- The message is one line. It names the command, says it never checks the harness lock, and ends `run factory --accept-harness <sha> config`, using the sha the operator passed.
- I rewrote the comment above the `init`/`paths`/`stats` branch.

`main()` is the module's only entry point.

**D. Tests.** The new file `tests/factory/test_small_defects.py` has 12 cases, listed under "Tests added/changed". The one existing test listed under "Tests to change" was updated.

**E. Docs.**
- `README.md`:
  - "Accepting a harness revision" now says `init`, `paths` and `stats` refuse `--accept-harness`, and every other command accepts it.
  - "Upgrading the runtime" step 2 names `factory --accept-harness <sha> config`.
  - "Counting what each role catches and costs" says `stats` never checks the harness lock and refuses `--accept-harness`.
  - The `.claude/agents/factory-*.md` row says init also reports a copy it cannot read.
  - The status date is now 2026-10-22. The README is still 1,174 lines, within its 1,185-line budget.
- `docs/design.md`:
  - The ESCALATIONS bullet says the exact footer line is dropped before the `none` rule.
  - The `harness.lock` clause in the Role-context block paragraph says `init`, `paths` and `stats` refuse `--accept-harness` and name `config`.
  - No prompt block changed, so nothing under `docs/prompts/` was touched.
- `docs/changelog.md`: new entry 76 names #88, #113, #114 and #115. It covers the footer, the `stale_agents` listing, the `--accept-harness` refusal and the `/bin/sh` scenario fix.

**F. Current truth (#113).** Current truth is the store's record of each capability's accepted behaviour. #113 is a fix to one scenario's text in it, and the spec delta applies that fix when the ticket is archived. I touched no store file and no code for it.

## Acceptance results

All commands ran from the worktree under the running-code wrapper with `/bin/sh` (bash 3.2.57). Each WHEN was taken from the pinned spec by `sed` into scratch scripts, not retyped. Every run needed `uv sync --frozen` first: before it, `bin/factory` fell back to a system `python3` that has no `yaml`. That was setup, not a result.

NEW, run before the change (base `788a201`) and after (`6f4d865`):

| Scenario | Before | After |
|---|---|---|
| A none trailer followed by the attribution footer finishes with no escalation and queues nothing | `finish=["none", "🤖 Generated with [Claude Code](https://claude.com/claude-code)"]`, `queued=1 meta=1` | `finish=[]`, `queued=0 meta=0` |
| A real item above the attribution footer stays, and the footer is dropped | `["none", "the auth path needs review", "🤖 Generated with [Claude Code](https://claude.ai/code)"]` | `["none", "the auth path needs review"]` |
| init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is | `exit=1 stale=absent kept=yes named=1 unread=0 others=0` | `exit=0 stale=factory-planner.md kept=yes named=1 unread=1 others=0` |
| The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance | `init: exit=0 named=0 hint=0 json=0`, `paths: exit=0 named=0 hint=0 json=0`, `stats: exit=0 named=0 hint=0 json=0`, `target=unchanged`, `fresh: exit=0 files=16` | `init: exit=2 named=1 hint=1 json=1`, `paths: exit=2 named=1 hint=1 json=1`, `stats: exit=2 named=1 hint=1 json=1`, `target=unchanged`, `fresh: exit=2 files=0` |
| README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy | `accepting=0 upgrade=0 stats=0 row=0` | `accepting=1 upgrade=1 stats=1 row=1` |
| The design doc states the footer rule and the refusal in the lock clause | `footer=0 lock=0` | `footer=1 lock=1` |
| The changelog records the four issues in one entry without a numbering gap | `CONTIGUOUS`, `0`, `0` | `CONTIGUOUS`, `1`, `4` |

Each "before" matches what the spec's verification.md predicted, so the spec matched reality. Each "after" is the scenario's THEN exactly.

REGRESSION, run after the change only:
- Real item lines, and a line that only mentions Claude Code, are still read by rule (b): `["none. x", "extra line"]`, `["one", "two"]`, `["none", "Generated with Claude Code, says the footer"]`, `[]`. This is the THEN.
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance: `intake: where=own-dir changed=2 revision=1 instance=1 writable=no`, `build: where=own-dir changed=2 revision=1 instance=1 writable=no`, `checkout=unchanged store=unchanged dirs=2`. This is the THEN. It ran the restated text, with the parenthesised `case` patterns, under `/bin/sh`, so the #113 text parses under the shell the issue is about.
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy: `config=2 launch=2 same=yes lock=1 copies=0`. THEN.
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy: `old=gone other=kept fresh=kept new=written dirs=3`. THEN.
- init reports an edited agent copy and leaves it as it is: `exit=0 stale=factory-planner.md kept=yes named=1 others=0`. THEN.
- init still creates a missing agent copy and lists no matching copy: `exit=0 created=factory-triage.md stale=0 same=6 differs=0`. THEN.
- Without the flag paths and stats still run under another lock, and config still accepts a revision: `paths=0 stats=0 config=2 accept=0 lock=accepted`. THEN.
- The harness suite passes: this is gate 2, run exactly as written. It printed `627 passed in 104.99s (0:01:44)` and exited 0. That is 615 on the base plus 12 new cases.
- The only existing test file changed is the stats test: it printed `tests/factory/test_stats.py`, which the THEN allows.

Gates, each run exactly as written from the worktree on `6f4d865`:
- `git diff --check main...HEAD` printed nothing and exited 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `627 passed` and exited 0.

I also ran the current-truth harness-docs scenarios that verification.md names, from `.factory/store/openspec/specs/harness-docs/spec.md`, on `6f4d865`. Each printed its THEN:
- "README is at most 1,185 lines": `readme=within`.
- "The maintained documents pass git's whitespace check in full": `exit=0`.
- "The documents record factory stats": `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no`, `CONTIGUOUS`, `1`, `4`.
- "The design doc states the EMPTY-OUTPUT rule, its rows and its park": `rule=1 rows=2 parks=1 kill=1`.

A grep of current truth for the README phrases I replaced found no scenario that depends on them.

## Tests added/changed

- New file `tests/factory/test_small_defects.py`, 12 cases. 9 of them failed on the base code before the fix. The rest pass on both base and fix, and guard against the fix over-matching:
  - `test_run_finish_drops_the_footer_below_a_none_trailer_and_queues_nothing`: run-0418's tail (none trailer, blank line, footer). Expects escalations `[]`, no footer in `meta.yaml` and no `escalation.queued`. Failed before.
  - `test_status_parse_drops_only_the_exact_footer`, 5 cases:
    - item above the footer: failed before.
    - footer behind a `- ` marker, dropped: failed before.
    - a line that only mentions Claude Code: kept.
    - the footer with text after it: kept.
    - the footer with an empty link `()`: kept.
  - `test_init_lists_an_unreadable_copy_exits_0_and_leaves_it`: the copy at mode `000`. Expects exit 0, the copy in `stale_agents`, exactly one stderr line in the new form, and the bytes unchanged. The mode is restored in a `finally` so the temporary directory can be removed. Failed before.
  - `test_accept_harness_with_a_lock_free_command_is_refused_and_writes_nothing`, for each of `init`, `paths` and `stats`: expects exit 2, `"ok": false`, a one-line message ending in the `config` hint, and the lock and the `.factory`/`.claude` trees unchanged. All 3 failed before.
  - `test_accept_harness_with_init_creates_no_instance`: a fresh repository gets no files. Failed before.
  - `test_paths_and_stats_without_the_flag_still_run_under_another_lock`: guards the existing behaviour.
  - No case uses skip or xfail.
- Changed `tests/factory/test_stats.py`, `test_reads_an_own_store_with_a_run_in_flight_from_its_runs_under_another_lock`. This test is listed under the spec's "Tests to change". The `--accept-harness … stats` call now asserts `returncode == 2` and the `factory --accept-harness 000…0 config` hint on stderr, and its comment is updated. The surrounding `snapshot(target) == before` assertion is kept, and it still passes because a refusal writes nothing.

## Known gaps and uncertainties

- `factory: markers added: none`.
- Part B differs slightly from design step B.1. B.1 says to handle "a copy that is not a file … as today" in a separate branch. I put the `is_file()` test and the read in the same `try`, so the "differs" message is not written twice. The behaviour is the same: a directory in place of a copy is still listed with the "differs" message, and `test_init_lists_a_directory_in_place_of_a_copy_and_leaves_it` passes. An `OSError` raised by `is_file()` itself would now get the "could not be read" line. On this Python, `Path.is_file()` returns False on such errors rather than raising.
- The mode-`000` test assumes the suite does not run as root, because root can read a file at mode `000`. The spec's own scenario states this as its GIVEN. The spec forbids skip, so a root run would fail this test.
- README's "Where a human decides" table still has the row **Upgrade**: `factory --accept-harness <sha> <command>`. Part E does not list it, so I left it. Taken literally, `<command>` could now be one of the three that refuse. Making it `config` would be a one-word follow-up.
- In changelog entry 76, I wrote the "Rejected" list from the spec's Decisions. One item, "keeping the flag a silent no-op on the three commands", is my wording for the overturned 2026-10-12 decision. It is not a rejection the spec names in those words.
- The marked-footer case (`- 🤖 Generated with …`, dropped) follows design step A.2, which says the entries are "already stripped of `-`/`*` markers". The spec's requirement text says "exactly" the footer, and it does not mention markers.

## Out-of-scope observations

- `docs/changelog.md` entry 70 (T-0043) still says `stats` ignores `--accept-harness`. It is a dated history entry, so I left it. Entry 76 records the change.
- The worktree had no `.venv`, so `bin/factory` fell back to a system `python3` without `yaml`, and every acceptance command failed until `uv sync --frozen` ran. A future implementer run will hit the same thing unless the harness syncs the worktree first or the briefing says to.
- Running `bin/factory` leaves `factory/__pycache__/` in the worktree, because `bin/factory` does not set `PYTHONDONTWRITEBYTECODE`. It is gitignored, so it does not dirty `git status`.

## Responses to findings

Round 1: none.

Protected paths changed, each declared in the spec's Risk section: `factory/status.py`, `factory/setup.py`, `factory/cli.py`.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every NEW command failed as the spec predicted and now prints its THEN, and every REGRESSION command, both gates and the named current-truth doc checks pass on 6f4d865
ESCALATIONS: none

## Diff `788a201a34fb3a416b394a14fba65583989c24c9...6f4d8658252556ed62bd19e130b09634f119f454`

diff --git a/README.md b/README.md
index e9bc1e7..cb0ab0b 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-19. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-22. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -526,7 +526,7 @@ The store's path is `state_dir` in `instance.yaml`. `factory init` creates a new
 |---|---|---|---|---|
 | `instance.yaml`, `context.md` | integration | `factory init`, then edited by the operator | the operator | durable |
 | `harness.lock` | integration | `factory init`; `--accept-harness` rewrites it | the operator | durable |
-| `.claude/agents/factory-*.md` | integration | `factory init`, when they are missing; it reports a copy that differs from its template and leaves it as it is | the operator, if the target keeps them | durable |
+| `.claude/agents/factory-*.md` | integration | `factory init`, when they are missing; it reports a copy that differs from its template, or that it cannot read, and leaves it as it is | the operator, if the target keeps them | durable |
 | Store records: requests, tickets, specs, plans, runs, results, approvals, current truth, changes, decisions, log | `factory-store` | the harness, through the workflows' clerk or `factory drive`, and the operator's commands | the operator, with `git -C <store> commit`; the harness commits the store once, the first commit `store migrate` makes | durable |
 | `runs/*/scratch/`, `runs/*/wt/`, `worktrees/` | none; git ignores them | `run start` | never | scratch until the ticket moves on (kept while parked); checker checkouts until `run cleanup`; implementer checkouts until the merge |
 | `drive/<ticket>.yaml` | none; git ignores it | `factory drive` | never | a live view of one driver process, rewritten at each step; read by the next drive of that ticket, which refuses to start while it shows a live driver; kept until that next drive |
@@ -608,7 +608,8 @@ can accept a revision while another stays on the old one.
 The flag cannot clear the other refusal. A runtime with uncommitted edits to the harness code is
 refused outright; commit or discard them first. Both checks apply only when a command uses the
 instance's own store. A throwaway store (`FACTORY_STATE` pointing elsewhere, as every test does)
-skips them. `paths` and `stats` skip both checks on any store, because they write nothing.
+skips them. `paths` and `stats` skip both checks on any store because they write nothing, and
+`init`, `paths` and `stats` refuse `--accept-harness`; every other command accepts it.
 
 ### Upgrading the runtime
 
@@ -616,7 +617,7 @@ Between tickets, never during one:
 
 1. Move the runtime: `git -C ~/dev/spec-factory-harness checkout --detach <sha>`, then
    `uv sync --frozen` there.
-2. In each target that should adopt it, run any store command once with `--accept-harness <sha>`.
+2. In each target that should adopt it, run `factory --accept-harness <sha> config` once.
 
 Targets you do not touch keep running the revision they accepted.
 
@@ -949,7 +950,8 @@ path above is relative to the store.
 `factory stats` counts, from the store's records, how often each role's verdict changed what
 happened next and what each role cost. Use it before deciding which model a role runs, or whether
 a check is worth its cost. It reads one or more stores and writes nothing. It needs no marker and
-no `--accept-harness`, so it runs while a build is in flight and from any checkout.
+never checks the harness lock, so it runs while a build is in flight and from any checkout. It
+refuses `--accept-harness`.
 
 ```
 $RUNTIME/bin/factory stats [--store PATH]... [--since WHEN] [--until WHEN] [--transcripts DIR]...
diff --git a/docs/changelog.md b/docs/changelog.md
index 5e9e185..61ccec7 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -82,4 +82,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 
 75. After issue #109 (2026-10-19), where the clerk, the agent that relays the store's command output to a workflow script, retyped a role's model in `factory config`'s reply, and the harness refused that role's run start and parked the sub-ticket; and issue #112, where the clerk relayed `run finish`'s one-line JSON reply over several lines, the script found no JSON, and it parked a sub-ticket whose implementer had finished, a park no `resolve` command covered. A new command, `factory launch-script intake|build`, writes a launch copy: the workflow script with its line `const LAUNCH = null` replaced by the instance's models, round limits and store as `config` prints them, the harness revision and the instance. The copy is read-only, in a new `factory-launch-*` directory under the temporary directory, and asks no clerk for the configuration. It refuses with config's error wherever config refuses, joins the live-store fence's read-only list, and first removes launch copies more than an hour old. A copy given another `instance` argument returns an error naming its own and runs nothing. Both scripts now parse a reply as one JSON value before trying its lines one at a time. `factory resolve <id> --to checks` returns a sub-ticket parked with a `harness-bug:` reason from ready-for-implementer, after its newest implementer run finished READY-FOR-REVIEW, to its checks at its branch tip, with the build's `pr:init` round step. `ticket head`'s body and the round step moved to `factory/store.py`, each one definition used by both callers. The scripts launched as they are keep their clerk path, so `run start`'s refusal of a model the instance does not name stays the backstop. Rejected: a fixed launch-copy path under the instance's `.factory/`, which a later launch would rewrite under a running workflow; a script that refuses to run without a copy, which breaks every check that runs the scripts directly; and removing every earlier copy, which could remove one another session is about to launch.
 
+76. After four small harness defects, each found in a real run and none of which changed where a ticket went next. Issue #88: Claude Code sometimes appends its attribution footer, `🤖 Generated with [Claude Code](<link>)`, below a role's STATUS/CONFIDENCE/ESCALATIONS trailer, and the trailer parser read an `ESCALATIONS: none` line with the footer below it as a real list of two items, so `run finish` recorded two escalations the role never raised and logged a false `escalation.queued`. The parser now drops a line below the ESCALATIONS line that is exactly that footer, with any link and after its list marker is stripped, before it applies the `none` rule; every other line below the ESCALATIONS line is still an item. Issue #113: one build-dispatch scenario in current truth put a `case` statement inside `$( )` with unparenthesised patterns, which the bash 3.2 that macOS ships as `/bin/sh` cannot parse; the spec delta parenthesises the two patterns, and current truth changes when the ticket is archived. Issue #114: `factory init` exited 1 on an agent copy in `.claude/agents/` it could not read; it now lists that copy under `stale_agents`, says on stderr that it could not be read, leaves it as it is and exits 0. Issue #115: `init`, `paths` and `stats` never check the harness lock, so they silently ignored `--accept-harness`; given the flag, each now refuses with exit 2 before anything runs, writes nothing, and names `factory --accept-harness <sha> config` as the command to run instead. README's upgrade step names that command. Rejected: setting Claude Code's attribution off for the role processes `factory drive` starts, whose effect on a headless reply is unverified and which would not cover the workflow scripts; ignoring every line after a blank line below the trailer, which would drop real items separated by blank lines; and keeping the flag a silent no-op on the three commands.
+
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index e10ecb4..4e66f97 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -65,7 +65,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
-**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance; `paths` and `stats`, which only read, run under any revision) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
+**Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), the command that installs each build checkout's environment (`environment_sync`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance; `paths` and `stats`, which only read, run under any revision; `init`, `paths` and `stats` never check the lock, so they refuse `--accept-harness` and name `config` as the command that accepts a revision) and the store: a git worktree of the repo's `factory-store` branch, at a path the integration branch has never tracked, because a checkout of an older commit would otherwise overwrite live records. That branch is never merged into the integration branch, so a store commit never moves it. A command run from inside a code checkout finds that checkout's own instance, whose store does not exist there, so it reports no such ticket rather than reaching the live store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell that first drops a Python virtual environment inherited from the launching shell (its `bin/` off `PATH`, `VIRTUAL_ENV` and `PYTHONHOME` unset), then sets `HOME` to a fresh temporary directory and exports any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. When the instance names an `environment_sync` command, `run start` runs it through that wrapper in each build checkout before the role starts, refuses the run if it fails (keeping the command and its output in the run's `environment-sync.log`), and the role's input says the environment is already synced. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception. `factory stats` prints the evidence a change to this table needs; its first figures, from 2026-10-11, are in `docs/principles.md`, principle 4, and changelog entry 70.
 
@@ -102,7 +102,7 @@ Rules the table relies on:
 - A round is one checker pass; the first check is round 1. Two loops carry a counter: the spec loop (writer ↔ critic) and the PR loop (implementer ↔ reviewer + verifier). The counter increments when the author re-enters after REVISE, REQUEST-CHANGES, or FAILED. A gate failure, whether CI reports it or the verifier's gate step does, counts: the implementer ran the gates locally before pushing. Rebases and merge-main rounds do not count.
 - The PR loop routes only after CI and both checker results for the current head are recorded. One implementer run then receives all three outputs. Never launch a second implementer run on a branch that already has one in flight.
 - The dispatcher reads a role's trailer by its labels, not by line position. The last `STATUS:` line wins; CONFIDENCE is the next line labelled `CONFIDENCE:` after it, and ESCALATIONS the next line labelled `ESCALATIONS:` after that. Lines between labelled lines are continuation (a wrapped reason, a remark), so a verbose but well-formed verdict routes on its STATUS. A trailer with no CONFIDENCE or no ESCALATIONS line after its last STATUS is a parse failure, which routes as a STATUS not in this table.
-- A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. Only NEEDS-HUMAN, CLARIFY, BLOCKED, ESCALATE, SPEC-DEFECT, a max-round cutoff, a budget kill (piece 3), a second EMPTY-OUTPUT in a row, a parent-close FAILED, and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) park the ticket. A parking STATUS from one checker wins over the other's REQUEST-CHANGES or FAILED; both outputs go to the queue.
+- A non-empty ESCALATIONS line is copied to the human queue without blocking the STATUS route. An ESCALATIONS line that starts with the word `none` followed by end of line or punctuation (so not `None of …`), with prose after it on that line and nothing below it, is empty for routing, and the prose is kept with the run for audit. A `none` line with further lines below it is a real list, copied verbatim from that line on. A line below the ESCALATIONS line that is exactly Claude Code's attribution footer, `🤖 Generated with [Claude Code](<link>)`, is dropped before the `none` rule is applied, because Claude Code appends it and the role never raised it. Only NEEDS-HUMAN, CLARIFY, BLOCKED, ESCALATE, SPEC-DEFECT, a max-round cutoff, a budget kill (piece 3), a second EMPTY-OUTPUT in a row, a parent-close FAILED, and an archive refusal (Spec store: a delta that does not apply, no change folder, or no spec store) park the ticket. A parking STATUS from one checker wins over the other's REQUEST-CHANGES or FAILED; both outputs go to the queue.
 - A role run that ends without writing its output is EMPTY-OUTPUT, whatever stopped it. The agent call reports no reason, so an empty output is never recorded as a budget kill; the harness keeps the agent's last message with the run. The same role is re-dispatched once, on the same inputs and in the same round. A second EMPTY-OUTPUT in a row parks the ticket with both runs. When either run's last message says it is still waiting on a command it started, the park reason adds `ended its turn waiting on a background command`, because a plain re-dispatch is likely to end the same way.
 - When a human resolves a parked ticket:
   - A question returns to the role that asked, with the answer and that role's previous output (the output that asked it); a requester's CLARIFY answer returns to Triage the same way. When the answer is a standing decision, the human passes `--decision "<line>"` with the answer, or with the close, so that it lands in `decisions.md`.
diff --git a/factory/cli.py b/factory/cli.py
index ebf9200..964ba97 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -848,8 +848,11 @@ READ_ONLY = {("ticket", "show"), ("ticket", "join"), ("results", "show"), ("conf
 def main(argv: list[str] | None = None) -> int:
     a = build_parser().parse_args(argv)
     try:
+        if a.cmd in ("init", "paths", "stats") and a.accept_harness:
+            raise Refused(f"factory {a.cmd} never checks the harness lock, so it cannot accept a revision; "
+                          f"run factory --accept-harness {a.accept_harness} config")
         # exempt from the instance refusal (design B.1); `paths` and `stats` only read, so they also
-        # skip the fence and the harness lock and ignore --accept-harness
+        # skip the fence and the harness lock; all three refuse --accept-harness (above, T-0058)
         if a.cmd in ("init", "paths", "stats"):
             a.fn(a)
             return 0
diff --git a/factory/setup.py b/factory/setup.py
index ce69419..d46d032 100644
--- a/factory/setup.py
+++ b/factory/setup.py
@@ -184,11 +184,19 @@ def init_cmd(a):
                 (dest / src.name).parent.mkdir(parents=True, exist_ok=True)
                 shutil.copyfile(src, dest / src.name)
                 agents.append(str(dest / src.name))
-            elif not (dest / src.name).is_file() or (dest / src.name).read_bytes() != src.read_bytes():
-                # reported, never overwritten
-                stale.append(str(dest / src.name))
-                print(f"factory init: {dest / src.name} differs from its template {src}; left as it is",
-                      file=sys.stderr)
+            else:
+                # reported, never overwritten; a copy that cannot be read is listed too (T-0058, #114)
+                try:
+                    differs = not (dest / src.name).is_file() or (dest / src.name).read_bytes() != src.read_bytes()
+                except OSError as e:
+                    stale.append(str(dest / src.name))
+                    print(f"factory init: {dest / src.name} could not be read ({e.strerror or e}); left as it is",
+                          file=sys.stderr)
+                    continue
+                if differs:
+                    stale.append(str(dest / src.name))
+                    print(f"factory init: {dest / src.name} differs from its template {src}; left as it is",
+                          file=sys.stderr)
         checkout = gitops.checkout_of(repo, gitops.STORE_BRANCH)
         if checkout is not None and checkout.resolve() == root:
             store_branch = gitops.STORE_BRANCH
diff --git a/factory/status.py b/factory/status.py
index 85331f4..abc7cfb 100644
--- a/factory/status.py
+++ b/factory/status.py
@@ -5,7 +5,10 @@ ESCALATIONS: the next labelled line after that (models wrap and interleave comme
 between are continuation). A `none` head (`none` in any case, then end of line or punctuation) with
 nothing below it is no escalation; prose after it on that line is returned as `escalations_note`
 and kept with the run. A `none` head with further lines is a real list, every line from the head
-on an item verbatim; so is anything else (operator decision 2026-10-01, option (b)).
+on an item verbatim; so is anything else (operator decision 2026-10-01, option (b)). Claude Code's
+attribution footer, a line below the ESCALATIONS line that is exactly `🤖 Generated with [Claude
+Code](<link>)`, is dropped first: Claude Code appends it after the trailer, and the role never
+raised it (T-0058, #88).
 """
 from __future__ import annotations
 
@@ -13,6 +16,7 @@ import re
 
 STATUS_RE = re.compile(r"^STATUS:\s*(\S+)\s*$")
 NONE_HEAD_RE = re.compile(r"^none\s*($|[.,;:—–-])", re.I)
+ATTRIBUTION_RE = re.compile(r"^🤖 Generated with \[Claude Code\]\(\S+\)$")
 
 
 def parse(text: str) -> dict:
@@ -36,10 +40,13 @@ def parse(text: str) -> dict:
     confidence = " ".join([nonblank[conf_i].split(":", 1)[1].strip()] + nonblank[conf_i + 1:esc_i]).strip()
     esc_head = nonblank[esc_i].split(":", 1)[1].strip()
     tail = [ln.lstrip("-* ").strip() for ln in nonblank[esc_i + 1:]]
+    tail = [ln for ln in tail if not ATTRIBUTION_RE.fullmatch(ln)]
     # Operator decision 2026-10-01, option (b): a `none` head is `none` in any case followed by end
     # of line or punctuation (never a space and a word). A none head with prose and nothing below
     # routes as no escalation and the prose is kept with the run (escalations_note). A none head
     # with further lines is a real list; anything else is an item. Unsure text goes to the queue.
+    # Claude Code's attribution footer was dropped from the tail first: Claude Code appends it after
+    # the trailer and the role never raised it, so it never turns a none head into a list (#88).
     note = None
     if not tail and (not esc_head or NONE_HEAD_RE.match(esc_head)):
         items = []
diff --git a/tests/factory/test_small_defects.py b/tests/factory/test_small_defects.py
new file mode 100644
index 0000000..fafc0ae
--- /dev/null
+++ b/tests/factory/test_small_defects.py
@@ -0,0 +1,125 @@
+"""T-0058 (#88, #114, #115), black-box through `bin/factory`.
+
+- #88: Claude Code's attribution footer below the ESCALATIONS line is dropped before rule (b), in
+  `run finish` and `status parse`; a real item line and a line that only mentions Claude Code stay.
+- #114: `factory init` lists an agent copy it cannot read under `stale_agents`, says so on stderr,
+  exits 0 and leaves the copy as it is.
+- #115: `--accept-harness` with `init`, `paths` or `stats` is refused with exit 2 and the `config`
+  hint, and writes nothing, on an instance and where init would create one.
+"""
+from __future__ import annotations
+
+import os
+import stat
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+from ._cli import BIN, STRIP, cli, git_repo, js, run, tree
+from ._fixtures import snapshot, target  # noqa: F401  (target is a fixture)
+
+FOOTER = "\U0001f916 Generated with [Claude Code](https://claude.com/claude-code)"
+SHA = "0123456789abcdef0123456789abcdef01234567"
+
+
+# ----- #88: the attribution footer -----------------------------------------------------------------
+
+def test_run_finish_drops_the_footer_below_a_none_trailer_and_queues_nothing(tmp_path):
+    store = tmp_path / "state"
+    req = tmp_path / "r.md"
+    req.write_text("# F\n\nDo x.\n")
+    run(store, "ticket", "new", "--file", str(req))
+    rid = js(run(store, "run", "start", "--role", "triage", "--ticket", "T-0001"))["run_id"]
+    run(store, "run", "compose", rid)
+    # run-0418's tail: a none trailer, a blank line, the footer
+    (store / "runs" / rid / "output.md").write_text(
+        "Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\n"
+        f"STATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n\n{FOOTER}\n", encoding="utf-8")
+    cp = run(store, "run", "finish", rid)
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["escalations"] == []
+    meta = (store / "runs" / rid / "meta.yaml").read_text(encoding="utf-8")
+    assert "Generated with" not in meta and yaml.safe_load(meta)["escalations"] == []
+    log = "".join(p.read_text(encoding="utf-8") for p in (store / "log").glob("*.jsonl"))
+    assert "escalation.queued" not in log
+
+
+@pytest.mark.parametrize("tail, want", [
+    (f"- the auth path needs review\n\n{FOOTER}\n", ["none", "the auth path needs review"]),
+    (f"- {FOOTER}\n", []),  # a list marker before the footer is stripped first
+    ("- Generated with Claude Code, says the footer\n", ["none", "Generated with Claude Code, says the footer"]),
+    (f"{FOOTER} and more\n", ["none", f"{FOOTER} and more"]),
+    ("\U0001f916 Generated with [Claude Code]()\n", ["none", "\U0001f916 Generated with [Claude Code]()"]),
+], ids=["item-above-footer", "marked-footer", "mention-only", "footer-plus-text", "footer-no-link"])
+def test_status_parse_drops_only_the_exact_footer(tmp_path, tail, want):
+    p = tmp_path / "o.md"
+    p.write_text(f"body\nSTATUS: APPROVE\nCONFIDENCE: high, ok\nESCALATIONS: none\n{tail}", encoding="utf-8")
+    cp = run(tmp_path / "state", "status", "parse", str(p))
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["escalations"] == want
+
+
+# ----- #114: an agent copy init cannot read --------------------------------------------------------
+
+def test_init_lists_an_unreadable_copy_exits_0_and_leaves_it(tmp_path):
+    # assumes the suite runs as a user other than root, since root reads a file at mode 000
+    t = git_repo(tmp_path / "target")
+    assert cli(t, "init", "--repo-name", "demo").returncode == 0
+    copy = t / ".claude" / "agents" / "factory-planner.md"
+    kept = copy.read_bytes()
+    copy.chmod(0)
+    try:
+        cp = cli(t, "init")
+    finally:
+        copy.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
+    assert cp.returncode == 0, cp.stderr
+    out = js(cp)
+    assert out["ok"] is True
+    assert [Path(p).name for p in out["stale_agents"]] == ["factory-planner.md"]
+    assert out["agents"] == []
+    assert copy.read_bytes() == kept
+    lines = [ln for ln in cp.stderr.splitlines() if ln.strip()]
+    assert len(lines) == 1, cp.stderr
+    assert lines[0].startswith(f"factory init: {copy} could not be read (")
+    assert lines[0].endswith("; left as it is")
+
+
+# ----- #115: --accept-harness with the lock-free commands ------------------------------------------
+
+def bare(cwd: Path, *argv: str) -> subprocess.CompletedProcess:
+    """`bin/factory` itself: `stats` is not in `cli`'s list of commands that skip the lock stub."""
+    env = {k: v for k, v in os.environ.items() if k not in STRIP}
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, cwd=cwd,
+                          env={**env, "PYTHONDONTWRITEBYTECODE": "1"})
+
+
+@pytest.mark.parametrize("cmd", ["init", "paths", "stats"])
+def test_accept_harness_with_a_lock_free_command_is_refused_and_writes_nothing(target, cmd):  # noqa: F811
+    lock = (target / ".factory" / "harness.lock").read_text()
+    before = snapshot(target)
+    cp = bare(target, "--accept-harness", SHA, cmd)
+    assert cp.returncode == 2, cp.stderr
+    assert js(cp)["ok"] is False
+    err = cp.stderr.strip()
+    assert len(err.splitlines()) == 1, cp.stderr
+    assert f"factory {cmd}" in err and "harness lock" in err
+    assert err.endswith(f"factory --accept-harness {SHA} config")
+    assert (target / ".factory" / "harness.lock").read_text() == lock
+    assert snapshot(target) == before
+
+
+def test_accept_harness_with_init_creates_no_instance(tmp_path):
+    t = git_repo(tmp_path / "fresh")
+    cp = bare(t, "--accept-harness", SHA, "init", "--repo-name", "demo")
+    assert cp.returncode == 2, cp.stderr
+    assert f"factory --accept-harness {SHA} config" in cp.stderr
+    assert {k for k in tree(t) if not k.startswith(".git/")} == set()
+
+
+def test_paths_and_stats_without_the_flag_still_run_under_another_lock(target):  # noqa: F811
+    (target / ".factory" / "harness.lock").write_text("0" * 40 + "\n")
+    for cmd in ("paths", "stats"):
+        cp = bare(target, cmd)
+        assert cp.returncode == 0, f"{cmd}: {cp.stderr}"
diff --git a/tests/factory/test_stats.py b/tests/factory/test_stats.py
index 46b664d..42c5ca3 100644
--- a/tests/factory/test_stats.py
+++ b/tests/factory/test_stats.py
@@ -416,11 +416,13 @@ def test_reads_an_own_store_with_a_run_in_flight_from_its_runs_under_another_loc
         assert cp.returncode == 0, cp.stderr
         assert f"Stores: {own}" in cp.stdout.splitlines()
         assert "1 runs in flight left out" in cp.stdout
-        # --accept-harness is ignored, as for `paths`: no lock rewrite, no refusal
+        # --accept-harness is refused, as for `init` and `paths` (T-0058): stats never checks the lock,
+        # so the refusal names `config` as the command that accepts a revision, and rewrites nothing
         env = {k: v for k, v in os.environ.items() if k not in STRIP}
         cp = subprocess.run([str(BIN), "--accept-harness", "0" * 40, "stats"], capture_output=True, text=True,
                             cwd=cwd, env={**env, "PYTHONDONTWRITEBYTECODE": "1"})
-        assert cp.returncode == 0, cp.stderr
+        assert cp.returncode == 2, cp.stderr
+        assert f"factory --accept-harness {'0' * 40} config" in cp.stderr
     assert snapshot(target) == before
     # the lock is in force: an ordinary read is refused
     assert factory_cli(target, "ticket", "show", "T-0001").returncode == 2
