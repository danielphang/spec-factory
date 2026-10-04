## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

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
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0183-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0183-verifier/wt` (branch `factory/T-0020.1`, base `02465fa0356b30d72ce6211ea874e230d5113236`, head `b45462df5b0c9570634b4d6d2074b3054ac296b6`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0020.1

## T-0020-S1 / Tripwire on listed live files (baseline, compare, park or escalate), workflow stop, documents and coding rule 6
Depends on: none
Parallel-safe: yes (the only sub-ticket; nothing runs beside it)

Parent: T-0020 approved spec v1 (issue #38). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: parts A (A1 to A5), B, C, D (D1 to D4), E and F of the parent's design.md. The whole parent.

Notes for the implementer, checked on `main` at `02465fa`:
- Fixtures. Most scenarios need the two fixture scripts that the GIVEN block of the parent's first scenario writes ("A changed park-listed file parks the ticket", in `specs/live-file-tripwire/spec.md`). Run that block once, verbatim, at column 0, before running any scenario. Run every command from the root of your worktree, after `uv sync --frozen`.
- Running tests. Run the suite and every probe under a throwaway `HOME`: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Never list a path under the real home that exists in a test or a probe.
- Part A1 resolves `~/` with `pwd.getpwuid(os.getuid()).pw_dir`, never `HOME`. The scenario "A file under a substitute HOME is not watched" fails if `HOME` is used.
- Part A3, `.gitignore`. `ensure_gitignore` (`factory/store.py` lines 52-60) appends the whole `STORE_GITIGNORE` block when any checked line is missing. With a third line in the list, an existing store `.gitignore` that has only the first two lines gets the two lines again, plus the new one. That is harmless. Appending only the missing lines is also within A3. Do not change what the two existing lines are.
- Part A4, the shared park helper. `ticket_park` is at `factory/cli.py` lines 173-185. Move its body into the helper and call the helper from both places, as A4 says. Keep `ticket_park`'s own refusal for a `closed` or `parked` ticket.
- Part C. The `if (!fin.ok) …` line is `factory/workflows/intake.js` line 108 and `factory/workflows/build.js` line 107. The ticket variable is `TICKET` in intake.js and `ticket` in build.js.
- Part D1. The commented `tripwire` example goes right after the `protected_paths:` block (template lines 12-13), before the `gate_commands` comment. Since T-0019, a real key, `run_env: {}`, sits at line 30. Leave it as it is.
- Part D2. The **What the harness itself owns** paragraph is still at `docs/design.md` line 52. It is prose, not a prompt block, so no `docs/prompts/` file changes.
- Part D3. The README anchors are on `main`: the "Instances and the harness lock" bullet (line 343), and the sentence ending "returns it." on lines 321-322 of the "Gap, as of today" paragraph.
- Part D4. Number the entry after the last numbered entry on `main` when you start. T-0019 added one. The entry goes before `Declined:`.
- Part E. Rule 4's sentence wraps: "A finding against" ends line 66 and "rule 2, 3 or 5 takes no tag" starts line 67. After the edit, keep `rule 2, 3, 5 or 6` on one line, or the rule-6 scenario's `grep -c 'rule 2, 3, 5 or 6'` prints `0`. `docs/coding.md` must still end with the two-line "The check order (rule 1) and …" paragraph.

Acceptance (each WHEN verbatim from the parent; run the fixture GIVEN block first):
- A changed park-listed file parks the ticket. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"token": "T20-SECRET-C"}\n' > $T20/live/policies.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; secrets)`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`, then `secrets=0`
- A park-listed file deleted or created during a run counts as changed. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && rm $T20/live/policies.json && echo '{}' > $T20/live/new.json && bin/factory run finish $R --output-file $T20/out.md >/dev/null 2>&1; show)`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage`
- A killed run is still compared. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; show)`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`
- A changed escalate-listed file is queued and the ticket still moves. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"chat": "T20-SECRET-D"}\n' > $T20/live/pairing.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; bin/factory log tail -n 1 --event escalation.queued > $T20/esc.out; python3 -c 'import json,sys; t=sys.stdin.read().strip(); print("items=%s" % (json.loads(t)["items"] if t else None))' < $T20/esc.out | sed "s|$T20|\$T20|g"; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null && echo moved=yes; secrets)`
  THEN it prints exactly `state=ready-for-triage reason=None`, then `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']`, then `moved=yes`, then `secrets=0`
- Unchanged listed files neither park nor escalate. REGRESSION.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print("status=" + json.load(sys.stdin)["status"])'; show; echo "escalations=$(bin/factory log tail -n 100 --event escalation.queued | wc -l | tr -d ' ')")`
  THEN it prints exactly `status=ACCEPT`, then `state=ready-for-triage reason=None`, then `escalations=0`
- Clearing an abandoned run compares it; an unrelated set does not. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory ticket set T-0001 title=Renamed >/dev/null 2>&1; show; bin/factory ticket set T-0001 'in_flight=[]' >/dev/null 2>&1; show)`
  THEN it prints exactly `state=ready-for-triage reason=None`, then `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`
- A file under a substitute HOME is not watched. NEW.
  WHEN `(T20=$(mktemp -d); mkdir -p $T20/home; echo a > $T20/home/.t0020-probe; echo a > $T20/live.json; TRIPWIRE="tripwire: {park: [\"~/.t0020-probe\", $T20/live.json]}"; export HOME=$T20/home; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && echo b > $T20/home/.t0020-probe && echo b > $T20/live.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; bin/factory ticket show T-0001 --json | tail -1 | python3 -c 'import json,sys; t=json.load(sys.stdin); print("state=%s reason=%s" % (t["state"], (t["parked"] or {}).get("reason")))' | sed "s|$T20|\$T20|g")`
  THEN it prints exactly `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage`
- A directory in the list refuses run start. NEW.
  WHEN `(T20=$(mktemp -d); mkdir -p $T20/live; TRIPWIRE="tripwire: {park: [$T20/live]}"; . ${TMPDIR:-/tmp}/t0020-bare.sh && bin/factory run start --role triage --ticket T-0001 > $T20/start.out 2>&1; echo "exit=$? named=$(grep -q "$T20/live" $T20/start.out && echo yes || echo no) runs=$(ls $T20/store/runs 2>/dev/null | wc -l | tr -d ' ')")`
  THEN it prints exactly `exit=2 named=yes runs=0`
- The baseline digest is kept but not committable. NEW.
  WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && H=$(printf '{"token": "T20-SECRET-A"}\n' | python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())') && echo "held=$(grep -rl $H $T20/store | wc -l | tr -d ' ')" && git -C $T20/store init -q && git -C $T20/store add -A && echo "committed=$(git -C $T20/store grep --cached -l $H | wc -l | tr -d ' ')")`
  THEN it prints exactly `held=1`, then `committed=0`
- No tripwire key, no new output or file. REGRESSION.
  WHEN `(TRIPWIRE=; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && printf 'Type: bug\nTitle: F\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' > $T20/out.md && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin)))'; ls $FACTORY_STATE/runs/$R | tr '\n' ' '; echo)`
  THEN it prints exactly `['confidence', 'escalations', 'ok', 'run_id', 'status']`, then `meta.yaml output.md system-prompt.txt ` (with the trailing space)
- The harness suite passes under a throwaway HOME. REGRESSION.
  WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
  THEN it exits 0 with no failures, including the new `tests/factory/test_tripwire.py`
- Both scripts check run finish for a park. NEW. This check is structural: the workflow scripts need the Claude Code Workflow runtime and cannot run in the verifier.
  WHEN `for f in factory/workflows/intake.js factory/workflows/build.js; do echo "$f $(awk '/^async function runRole/{f=1} f&&/^}/{f=0} f' $f | grep -c '\.parked')"; done`
  THEN each of the two lines ends in a number of 1 or more, and reading those lines shows a `return null` taken when the `run finish` answer carries `parked`
- Rule 6 is in the page's format and rule 4 names it. NEW.
  WHEN `awk '/^## 6\. /{f=1;print "heading=yes";next} /^## |^The check order/{f=0} f&&/^Check: /{c=1} f&&/^Principle: /{p=1} f&&/^Before /{b=1} f&&/^After: /{a=1} f&&/tmp_path/{t=1} f&&/store\.policy_store_path/{m=1} END{print "check="(c?"yes":"no"), "principle="(p?"yes":"no"), "before="(b?"yes":"no"), "after="(a?"yes":"no"), "tmp_path="(t?"yes":"no"), "module_attr="(m?"yes":"no")}' docs/coding.md; grep -c 'rule 2, 3, 5 or 6' docs/coding.md; tail -2 docs/coding.md | head -1 | cut -c1-28`
  THEN it prints exactly `heading=yes`, then `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes`, then `1`, then `The check order (rule 1) and`
- Design doc, template and README name the tripwire. NEW.
  WHEN `echo "design=$(grep -c '^\*\*Tripwire on live files\.\*\*' docs/design.md) template=$(grep -c 'tripwire' factory/instance.template.yaml) built=$(awk '/^\*\*Built\*\*/{f=1} /^\*\*Not built\*\*/{f=0} f' README.md | grep -ci 'tripwire') resume=$(grep -c 'A ticket the tripwire parked' README.md)"`
  THEN it prints `design=1`, `template=` a number of 1 or more, `built=` a number of 1 or more, and `resume=1`
- The changelog records the change in order. NEW.
  WHEN `awk '/^[0-9]+\. /{n++; split($0,a,"."); if (a[1]+0!=n) bad=1; last=$0} END{print "contiguous=" (bad?"no":"yes"), "last_names_tripwire=" (last ~ /tripwire/ ? "yes":"no")}' docs/changelog.md`
  THEN it prints exactly `contiguous=yes last_names_tripwire=yes`
- The change adds no whitespace errors. REGRESSION.
  WHEN `git diff --check main...HEAD`
  THEN it exits 0 with no output
- Intermediate check: only the files the parent declares change, and no existing test changes. NEW.
  WHEN `git diff --name-only main...HEAD | sort`
  THEN it prints exactly these 11 lines: `README.md`, `docs/changelog.md`, `docs/coding.md`, `docs/design.md`, `factory/cli.py`, `factory/instance.template.yaml`, `factory/store.py`, `factory/tripwire.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `tests/factory/test_tripwire.py`

Tests to change: none. New tests go in the new file `tests/factory/test_tripwire.py` (part F).

Protected paths: harness: `factory/tripwire.py` (new), `factory/cli.py`, `factory/store.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/instance.template.yaml`. That is the parent's whole Risk list. Guardrail path: `docs/coding.md` (part E asks for it).

Out of scope:
- Everything in the parent's Out of scope section. That includes watching directories, naming changed JSON keys, a new `resolve` mode, `dev/build-harness.spec.md`, the prompt blocks and `docs/prompts/**`.
- Either instance's own files: `.factory/**` here, and anything under `~/dev/nanobot-upstream`. Adding Nanobot's lists is the parent's Operator step 1, after merge.
- `~/.nanobot/**`: never read or write it, not even to test.
- A guard on leaving `parked` for every park, and documenting how to recover a run left in flight. Both are in the parent's out-of-scope observations.

## Shared plan context (from the plan; applies to every sub-ticket)

Parent: the approved spec v1 of T-0020 (issue #38), in this run's input and the T-0020 spec store.

One sub-ticket. The parent decides this itself ("One change, not split: about 300 lines, half of them the new test file"), and the parts cannot land apart without leaving `main` wrong. The workflow-script stop (part C) on its own reads a `parked` field that nothing writes. The baseline and comparison (parts A and B) on their own would park tickets that the workflow scripts then route out of `parked`, which is the silent undo the parent's Evidence describes. Rejected: a separate documents-and-rule-6 sub-ticket (parts D and E). It would describe a tripwire that does not exist yet, and splitting would make one more merge for the other in-flight work to re-verify, with no gain for review or rollback.

The parent's ordering condition holds. It asks for this to be built after T-0019 merges. T-0019 is the approved change that runs every role under a throwaway `HOME`. Both of its sub-tickets are merged on `main` (`02465fa`: T-0019.1 at `9853737`, T-0019.2 at `3d23560`). They changed `docs/design.md`, `docs/changelog.md`, `README.md` and `factory/instance.template.yaml`. I re-checked every anchor this change edits against `main` at `02465fa` (below). `factory/cli.py`, `factory/store.py` and both workflow scripts are unchanged since the spec's base `1c5f6a7`, so the parent's line numbers for them still hold.

## Parent spec (v1, pinned)

=== proposal.md
## Problem

Nothing in the spec factory notices when an AI agent it runs changes the operator's live files outside the repository. The operator learns about it only if the agent happens to say so. The factory runs each requested change through a chain of agents called roles: triage, spec writer, critic, planner, implementer, reviewer and verifier. Each agent call is a role run. The harness is the code that starts and records each run, and keeps every ticket's state in a store. The harness knows exactly when each run starts and finishes, but it never looks at anything outside the repository.

This has already cost live data. On 2026-10-04, while the factory was building a change for the Nanobot chat bot (the factory's other target repository), an implementer's tests overwrote the live bot's per-chat permission file and its backup in `~/.nanobot/`. The overwrite came to light only because one test happened to fail on an unexpected `FileExistsError`. The day before, intake roles left 13 stray session folders in the live bot's data directory, and nobody noticed for a day. A separate approved change gives roles a throwaway `HOME`, to make such writes less likely. Nothing yet tells the operator when one gets through anyway.

This change adds detection. A target's instance can list live files to watch, in two lists. The instance is its `.factory/` directory, which holds its config and its store. A run that changes a file on the "park" list stops its ticket and puts it in the human queue: the ticket is parked. A run that changes a file on the "escalate" list raises an escalation: it puts a flagged item in the operator's queue and lets the run continue. That list is for files with legitimate outside writers, such as a pairing approval or the operator's own edit. Neither list ever prints a file's contents, because these files hold live secrets. A run that is killed is checked the same way.

The leak also had a code-level cause that a coding rule would have caught. A test file imported a path function by name when the test runner loaded it. The test fixture's later replacement of that function never reached the copy the test file already held. So the coding standard, the rules page the implementer and code reviewer follow, gains a rule against that pattern.

## Evidence

Checked on `main` at `1c5f6a7`.

- **The incident is recorded by the run that caused it.** The Nanobot store's `runs/run-0080-implementer/output.md`, lines 91-93, names `/Users/dphang/.nanobot/policies.json` and `policies.json.bak` as overwritten by the first run of `uv run pytest tests/policy` "with the real `HOME`". It quotes the run's own error, `FileExistsError: [Errno 17] File exists: '/Users/dphang/.nanobot/policies.json'`. It names the cause: "the test module imported `policy_store_path` by name when pytest collected it. The conftest fixture replaces the module attribute later, so the test helpers kept calling the real function." That run's sub-ticket worktree shows the fixed form: `tests/policy/test_store.py` lines 23-30 call `store.policy_store_path()`, with a comment that "a name imported at collection time would still point at" the real function. The module is `nanobot/policy/store.py` in that worktree.
- **The 13 stray session folders** are from the request. I did not verify them, because `~/.nanobot/` is off limits to me.
- **No harness code looks outside the repository during a run.** `run start` (`factory/cli.py` lines 197-228) and `run finish` (lines 281-320) read and write only the store and, for build roles, git worktrees. The only reader of the instance's `protected_paths` is `fill_preamble` (`factory/instance.py` lines 168-179), which prints the list into the role's rules text.
- **Today an instance's `tripwire` key is silently ignored.** I appended `tripwire: {park: [<scratch>/live/policies.json, ...], escalate: [<scratch>/live/pairing.json]}` to an instance made from the template, started a triage run, changed `policies.json`, and finished the run (scenario "A changed park-listed file parks the ticket", below). `run finish` printed `{"ok": true, "run_id": "run-0001-triage", "status": "ACCEPT", "confidence": "high", "escalations": []}`. The ticket then read `state=ready-for-triage reason=None`: the change went unnoticed and the ticket stayed ready to move on. The same happened for a killed run, an escalate-listed change (no `escalation.queued` event in the log), and a run cleared from the in-flight list by hand.
- **Today a directory in that list is accepted.** With `tripwire: {park: [<scratch>/live]}`, a directory, `run start` exited 0 and created one run directory. The output was `exit=0 named=no runs=1`: the run started, nothing named the bad entry, and one run was recorded.
- **A run leaves the in-flight list in exactly three places.** The ticket record's `in_flight` list names its running runs. `grep -n in_flight factory/*.py` shows it changed only in `run_start` (append, line 225), `run_finish` (remove, lines 306-307) and the generic `ticket set` (lines 109-121). Neither store has a run left unfinished today: every `meta.yaml` under both stores' `runs/` has a `finished` time except the run writing this spec. Every killed run in the Nanobot log, for example `run-0047-implementer`, went through `run finish --status-override KILLED`.
- **A park written by `run finish` would be undone by the workflow scripts today.** The two scripts that drive roles, `factory/workflows/intake.js` and `factory/workflows/build.js`, route on the role's STATUS right after `run finish`. For example, intake line 153 moves a ticket to `ready-for-critic`. The instance's routing table allows `parked → ready-for-critic` and most other exits from `parked` (`factory/instance.template.yaml`, the `parked:` row). So a park that `run finish` writes would be silently overwritten unless the scripts check for it. In both scripts, the `runRole` function contains no reference to a parked answer from `run finish`: the count printed below is `0` for each.
- **The coding standard has no rule on patch targets.** `docs/coding.md` has rules 1 to 5 (`## 5.` at line 86). Rule 4 says "A finding against rule 2, 3 or 5 takes no tag" (line 67).
- **No reference fix exists.** `git log --all -i --grep=tripwire` in the Nanobot checkout finds no factory commit, so there is no as-built behaviour to compare against.
- **The gate passes today.** `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `171 passed in 103.25s`, and `git diff --check main...HEAD` exited 0.

## Root cause

- `factory/cli.py` `run_start` and `run_finish`: no snapshot of any file outside the store, so there is nothing to compare.
- `factory/cli.py` `ticket_set`: a run removed from `in_flight` by hand is dropped with no record of what it did.
- `factory/workflows/intake.js` and `build.js`, `runRole`: they route on the role's STATUS and never ask whether `run finish` stopped the ticket.
- `docs/coding.md`: no rule that tests reach a patched function through its module, and none that a new path outside the repository ships with a test guard.

## Out of scope

- Prevention: the throwaway `HOME` for every role (approved separately as T-0019, issue #36) and an operating-system write denial (issue #37).
- Watching directories. The 13 stray session folders were in a directory that the live bot writes all the time, and the request excludes such directories. A directory in either list is refused.
- Naming the changed top-level keys of a JSON, YAML or TOML file in an escalation, as the request proposed. Cut: a pairing file's keys can themselves be user identifiers, and the log is committed with the store (Decisions).
- Naming the other runs that overlapped a changed file in the park reason. Cut: the log's timestamps already show them.
- A new `resolve` mode for a tripwire park. The existing `ticket transition` and `resolve --redispatch` resume one.
- Either instance's own files: `.factory/**` here and everything in `~/dev/nanobot-upstream`. Adding Nanobot's lists is an Operator step.
- The design doc's prompt blocks and `docs/prompts/`: no prompt changes.
- `dev/build-harness.spec.md`. I read its lines 202 (`ticket set`), 203 (`run start`) and 205 (`run finish`). None is contradicted, because the change adds behaviour to those commands and removes none.

## Open questions

none

## Decisions

- Detection compares a SHA-256 of each listed file's bytes at run start with one at the end; a file created, deleted or modified counts as changed. Rejected: modification times, which a restore by copy or a write within the same second defeats.
- A `~/` entry resolves against the account's home from the system user database, never the `HOME` variable. A `run start` or `run finish` under a throwaway `HOME` therefore still watches the real files. Rejected: `HOME`, under which that case would hash the wrong files and never fire.
- The baseline is kept per run in the store, in a file the store's `.gitignore` excludes, so the operator's store commit never carries a digest of a live secret file.
- Each run's baseline is compared once, when the run leaves the in-flight list: at `run finish`, which every killed run in either store went through, or at a `ticket set` that removes it. Rejected: comparing at every command that names the ticket, because a run still in progress looks the same as an abandoned one there and would be compared early.
- The park reason says the files changed "during" the run, not "by" it, because runs on other tickets and the operator's own edits can overlap a run, and the tripwire cannot tell them apart.
- When a park-listed change is found on a ticket that is already parked or closed, the tripwire does not park it again; it queues the same reason as an escalation.
- Escalations and park reasons name changed files only, never contents or keys.
- A directory, or an entry that is neither absolute nor `~/`, refuses `run start`, so a bad list is loud from its first run.
- The workflow scripts stop on a `run finish` that reports a park, instead of routing on the role's STATUS, because the routing table lets a ticket leave `parked` for most states.
- The coding rule is rule 6 of `docs/coding.md`, and rule 4's list of untagged rules gains it.
- One change, not split: about 300 lines, half of them the new test file.

## Risk

Blast radius: nothing changes for an instance with no `tripwire` key, or with both lists empty. No baseline is written there, and no command's output gains a field. Under the key, every `run start` hashes a handful of files, every `run finish` hashes them again, and a bad entry refuses every `run start` on that instance. The workflows then park the ticket as `harness-bug: run start …`. A park-listed file that the live service itself rewrites will park tickets on legitimate changes; which files go on which list is the operator's call. A tripwire park stops the workflow before the role's output is recorded (for example, a spec is not added), so resuming re-runs that role.

Protected paths this change touches:
- harness: `factory/tripwire.py` (new), `factory/cli.py`, `factory/store.py`, `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/instance.template.yaml`.

Guardrail paths: `docs/coding.md` is the coding standard that the implementer and reviewer prompts name; part E of this ticket asks for its edit. The prompts themselves do not change. New tests go in a new file. No existing test changes.

Not touched: `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `docs/prompts/**`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`.

Ordering: the approved throwaway-`HOME` change (T-0019) also edits `docs/design.md`, `docs/changelog.md`, `README.md` and `factory/instance.template.yaml`, in different places. Build this after it merges. The changelog scenario checks for the next free number, not a fixed one.

Gate: the request says it is pre-approved under the queue policy. Whether that covers a change to five harness files is the operator's decision at the spec gate.

## Operator steps

These come after the merge, once the runtime has moved to a revision with this change. The runtime is the pinned checkout of the harness that runs tickets. The operator accepts that revision for the Nanobot instance with `--accept-harness <revision>`.

1. In the Nanobot instance's `.factory/instance.yaml`, add the Driver's lists:
   `tripwire: {park: ["~/.nanobot/policies.json", "~/.nanobot/policies.json.bak", "~/.nanobot/config.json"], escalate: ["~/.nanobot/pairing.json", "~/.nanobot/config-localgateway.json"]}`
2. Check it: the next role run's `run finish` JSON on that instance carries a `tripwire` field, `{"park": [], "escalate": []}` when nothing changed. If `run start` is refused instead, its message names the entry to fix.
3. This repository's own instance watches no live files, so it gets no list.

=== design.md
## Proposed change

**A. Baseline at run start, comparison at run finish** (`factory/tripwire.py`, new; `factory/cli.py`; `factory/store.py`)
- A1. Read `cfg.get("tripwire")`. Absent, null, or both lists empty: the feature is off, and A2-A5 and B do nothing for that instance. Otherwise it must be a mapping whose only keys are `park` and `escalate`, each optional and each a list of strings. Expand each entry: a leading `~/` becomes the home directory of `pwd.getpwuid(os.getuid()).pw_dir` plus `/`; an entry that then is not absolute is refused. Refuse also an entry that exists and is not a regular file (a directory, for example), and one that exists and cannot be read. Each refusal is `store.Refused` (exit 2) naming `tripwire` and the entry as written and expanded. A path in both lists counts under both.
- A2. In `run_start`, do A1 and hash every listed file before `store.next_run_id` reserves the run directory, so a refusal writes nothing. A file's state is the hex SHA-256 of its bytes, or the string `absent`.
- A3. After `meta.yaml` is written, write the baseline to `runs/<run id>/tripwire.yaml`: `{park: {<expanded path>: <state>}, escalate: {...}, compared: null}`, keys in config order. Call `store.ensure_gitignore(root)` first. Add the line `runs/*/tripwire.yaml` to `STORE_GITIGNORE` and to the list `ensure_gitignore` checks, so the baseline is never committed with the store. Write no digest anywhere else.
- A4. A comparison of one run (`tripwire.compare`, used by A5 and B): if the run has a baseline whose `compared` is null, re-hash each path in the baseline, not the current config. A file that cannot be read now counts as changed. Set `compared` to the current time. Return the changed paths per list, in baseline order. Then act:
  - Park list changed, ticket not `parked` or `closed`: park it with reason `tripwire: <path>, <path> changed during <run id>`, outputs `[<run id>]`, history `by: tripwire`. Do this through one helper shared with `ticket_park`, which today writes the park record and logs `ticket.parked` and `escalation.queued` (`factory/cli.py` lines 173-185). Move that body into the helper and call it from both.
  - Park list changed, ticket already `parked` or `closed`: log `escalation.queued` (`ticket`, `run`, `items: [<that same reason>]`); do not park again.
  - Escalate list changed: log `escalation.queued` (`ticket`, `run`, `items: ["tripwire (escalate): <path>, <path> changed during <run id>"]`). The ticket is not touched.
  - Anything changed: also log `tripwire.changed` (`ticket`, `run`, `park: [...]`, `escalate: [...]`).
  - No event, reason or output ever includes a file's bytes or any part of them.
- A5. In `run_finish`, after the run is recorded and the ticket saved as today (both normal and `--status-override KILLED`), run A4 for this run. When the run had a baseline, add `"tripwire": {"park": [...], "escalate": [...]}` (changed paths) to the printed JSON. When A4 parked the ticket, also add `"parked": "<reason>"`. Without a baseline the JSON is exactly as today.

**B. A run dropped by hand** (`factory/cli.py` `ticket_set`): note `in_flight` before the assignments. After the ticket is saved, run A4 for each run id that was in `in_flight` before and is not after. When one parked the ticket, add `"parked": "<reason>"` to the printed JSON. No other command compares.

**C. The workflow scripts stop on a tripwire park** (`factory/workflows/intake.js`, `factory/workflows/build.js`): in each `runRole`, right after the existing `if (!fin.ok) …` line, add `if (fin.parked) { log(\`<ticket> parked: ${fin.parked}\`); return null }`, using the script's own ticket variable. Every caller already returns on `null` without routing. In `build.js` the reviewer or verifier cleanup still runs first, as it does today.

**D. Template and documents**
- D1. `factory/instance.template.yaml`, after the `protected_paths` block, add this as comments. A commented example keeps `set(template) == set(instance)` true and lets fixtures append the key.
  ```
  # Live files outside the repo that no role run should change, as absolute or `~/` paths (`~` is the
  # account's home, never $HOME). `run start` hashes each; the comparison runs when the run leaves the
  # in-flight list. A changed `park` file parks the ticket; a changed `escalate` file queues an
  # escalation and the run goes on. Contents are never printed. Files only: a directory is refused.
  # tripwire: {park: [], escalate: []}
  ```
- D2. `docs/design.md`: a new paragraph after the **What the harness itself owns** paragraph (line 52), with one blank line on each side, opening exactly `**Tripwire on live files.**`. It says: an instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list; `~` is the account's home, never `HOME`; files only. `run start` records a SHA-256 of each, or that it is absent, in a baseline the store's `.gitignore` excludes. The run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A changed `park` file parks the ticket, `tripwire: <files> changed during <run>`. "During", because overlapping runs and the operator's own edits cannot be told apart. A changed `escalate` file queues an escalation and the run goes on. Nothing prints a file's contents. The workflow scripts stop on a `run finish` that parked. It detects a write after the fact; it does not prevent one.
- D3. `README.md`:
  - In "What is built and what is not", **Built**, after the "Instances and the harness lock" bullet, add: `- **Tripwire on live files.** An instance can list files outside the repo that no role run should change, such as a live bot's credentials, under \`tripwire\` in \`instance.yaml\`: a \`park\` list and an \`escalate\` list. The harness hashes each file when a run starts and compares when the run ends, killed runs included. A changed \`park\` file parks the ticket; a changed \`escalate\` file is queued for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not yet fired on a real ticket.` Wrap it at the page's width.
  - In "Where a human decides", after the "Gap, as of today" paragraph's sentence that ends "returns it.", add: `A ticket the tripwire parked returns the same way, to the state its record names as \`parked.from\`, once the operator has checked the named files; a checker park can use \`resolve --redispatch\` instead.`
  - Bump the status-header date to the merge date.
- D4. `docs/changelog.md`: after the last numbered entry and before `Declined:`, one entry with the next number, opening `<n>. After the 2026-10-04 Nanobot incident, where a role's tests overwrote the live bot's permission file and nothing in the factory noticed:`. It says what D2 says in one paragraph. It also says that the coding standard gains rule 6, as part E. It must contain the word `tripwire`.

**E. `docs/coding.md`, rule 6.** Insert before the closing "The check order (rule 1) …" paragraph, with one blank line on each side, in the page's format:

```
## 6. A test reaches a patched path through its module, and a new outside path ships with a guard.
Check: each function or constant your tests patch to redirect a path outside the repository is
called in test code as an attribute of its module (`store.policy_store_path()`), never through a
name imported when the test file loads. Each path your diff adds outside the repository (a data
directory, a config file) comes with an autouse test fixture that fails any test resolving that
path outside `tmp_path`.
Principle: patch where the name is looked up (the Python `unittest.mock` documentation, "Where to
patch"); and fail-safe defaults (Saltzer and Schroeder): a test that stops is cheaper than one that
writes live data.
Before (a Nanobot implementer run, 2026-10-04): the test module ran
`from nanobot.policy.store import policy_store_path` when pytest collected it. The conftest fixture
then replaced `nanobot.policy.store.policy_store_path`, but the test helpers still held the real
function. The tests overwrote the live bot's `~/.nanobot/policies.json` and its `.bak`, and an
unrelated `FileExistsError` was the only sign.
After: the test module runs `from nanobot.policy import store` and calls `store.policy_store_path()`,
so the fixture's patch reaches every call. An autouse fixture fails any test whose resolved policy
path is not under `tmp_path`, so the next escape stops a test instead of writing live data.
```

In rule 4, change "A finding against rule 2, 3 or 5 takes no tag" to "A finding against rule 2, 3, 5 or 6 takes no tag".

**F. New tests**, in a new file `tests/factory/test_tripwire.py`, driven through `bin/factory` on scratch instances and stores. Cover the scenarios in `specs/live-file-tripwire/spec.md`: park, create and delete, escalate, unchanged, killed, dropped by `ticket set` (and not compared while still in flight), the account home, the directory refusal, the baseline kept out of a commit, and no tripwire key. Every listed file lives under `tmp_path`; no test lists a path under the real home that exists.

## Tests to change

none. I checked each existing test against the change:
- `tests/factory/test_instance.py` line 89 and `tests/factory/test_shepherd.py` lines 200-201 check that `.gitignore` contains its two lines, as a subset, so a third line passes.
- `tests/factory/test_instance.py` lines 94-106 compare an initialised instance with the template key for key. The new template text is a comment, so neither gains a key. The test fixture instance (`tests/factory/fixtures/instance/instance.yaml`) has no `tripwire`, so every existing run is unchanged.
- The tests that read `run finish` output (`test_p0_cli.py` line 251, `test_killed_checker.py` line 27) read named fields. Without a baseline the output is unchanged.
- No test drives the workflow scripts; `test_shepherd.py` replays their routing through the CLI.

=== specs/live-file-tripwire/spec.md
## ADDED Requirements

### Requirement: A changed park-listed file parks the ticket without showing its contents
When a role run's ticket belongs to an instance whose `tripwire` lists files under `park`, and any of those files is changed, created or deleted between `run start` and the end of the run, the harness SHALL park the ticket with the reason `tripwire: <changed paths, comma-separated> changed during <run id>`, and no store file or command output SHALL contain any of the file's contents.

#### Scenario: A changed park-listed file parks the ticket
Run every command in this file from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell and may run under a throwaway `HOME`; none depends on `HOME` except where it sets it.
- GIVEN the two fixture scripts written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0020-fix.sh <<'EOF'
# Sourced from the repo root. A scratch instance (from the template) whose tripwire lists two park
# files and one escalate file under $T20/live, a scratch store, ticket T-0001, one started triage
# run $R, and a triage output $T20/out.md. `show` prints the ticket's state and park reason with
# the scratch directory written as $T20; `secrets` counts files holding the fixture's file contents.
unset FACTORY_REPO FACTORY_INTEGRATION_BRANCH
T20=$(mktemp -d); mkdir -p $T20/inst $T20/live
sed -e 's/__REPO_NAME__/demo/' -e "s|__HARNESS__|\"$PWD\"|" factory/instance.template.yaml > $T20/inst/instance.yaml
printf 'tripwire:\n  park: [%s/live/policies.json, %s/live/new.json]\n  escalate: [%s/live/pairing.json]\n' $T20 $T20 $T20 >> $T20/inst/instance.yaml
printf '{"token": "T20-SECRET-A"}\n' > $T20/live/policies.json
printf '{"chat": "T20-SECRET-B"}\n' > $T20/live/pairing.json
export FACTORY_INSTANCE=$T20/inst FACTORY_STATE=$T20/store
printf '# Fixture\n\nDo the thing.\n' > $T20/req.md && bin/factory ticket new --file $T20/req.md >/dev/null
R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
printf 'Type: bug\nTitle: Fixture\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' > $T20/out.md
show() { bin/factory ticket show T-0001 --json | tail -1 | python3 -c 'import json,sys; t=json.load(sys.stdin); print("state=%s reason=%s" % (t["state"], (t["parked"] or {}).get("reason")))' | sed "s|$T20|\$T20|g"; }
secrets() { echo "secrets=$(grep -rl T20-SECRET $T20/store $T20/*.out 2>/dev/null | wc -l | tr -d ' ')"; }
EOF
cat > ${TMPDIR:-/tmp}/t0020-bare.sh <<'EOF'
# Sourced from the repo root. A scratch instance from the template with $TRIPWIRE (if set) appended,
# a scratch store and ticket T-0001. Set T20 before sourcing to use a directory you prepared.
unset FACTORY_REPO FACTORY_INTEGRATION_BRANCH
T20=${T20:-$(mktemp -d)}; mkdir -p $T20/inst
sed -e 's/__REPO_NAME__/demo/' -e "s|__HARNESS__|\"$PWD\"|" factory/instance.template.yaml > $T20/inst/instance.yaml
[ -n "$TRIPWIRE" ] && printf '%s\n' "$TRIPWIRE" >> $T20/inst/instance.yaml
export FACTORY_INSTANCE=$T20/inst FACTORY_STATE=$T20/store
printf '# Fixture\n\nDo the thing.\n' > $T20/req.md && bin/factory ticket new --file $T20/req.md >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"token": "T20-SECRET-C"}\n' > $T20/live/policies.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; secrets)`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`, then `secrets=0`

#### Scenario: A park-listed file deleted or created during a run counts as changed
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && rm $T20/live/policies.json && echo '{}' > $T20/live/new.json && bin/factory run finish $R --output-file $T20/out.md >/dev/null 2>&1; show)`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage`

#### Scenario: A killed run is still compared
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; show)`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`

### Requirement: A changed escalate-listed file queues an escalation and the ticket goes on
When a file under `escalate` changes during a role run, the harness SHALL log an `escalation.queued` event whose item is `tripwire (escalate): <changed paths> changed during <run id>`, SHALL leave the ticket's state unchanged, and SHALL NOT write any of the file's contents to the store or a command's output.

#### Scenario: A changed escalate-listed file is queued and the ticket still moves
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && printf '{"chat": "T20-SECRET-D"}\n' > $T20/live/pairing.json && bin/factory run finish $R --output-file $T20/out.md > $T20/finish.out 2>&1; show; bin/factory log tail -n 1 --event escalation.queued > $T20/esc.out; python3 -c 'import json,sys; t=sys.stdin.read().strip(); print("items=%s" % (json.loads(t)["items"] if t else None))' < $T20/esc.out | sed "s|$T20|\$T20|g"; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null && echo moved=yes; secrets)`
- THEN it prints exactly `state=ready-for-triage reason=None`, then `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']`, then `moved=yes`, then `secrets=0`

#### Scenario: Unchanged listed files neither park nor escalate
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print("status=" + json.load(sys.stdin)["status"])'; show; echo "escalations=$(bin/factory log tail -n 100 --event escalation.queued | wc -l | tr -d ' ')")`
- THEN it prints exactly `status=ACCEPT`, then `state=ready-for-triage reason=None`, then `escalations=0`

### Requirement: A run dropped from the in-flight list without run finish is compared then, and only then
When a `ticket set` removes a run from the ticket's in-flight list without `run finish`, the harness SHALL compare that run's listed files as `run finish` would. A command that leaves the run in flight SHALL NOT compare it.

#### Scenario: Clearing an abandoned run compares it; an unrelated set does not
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && echo x > $T20/live/policies.json && bin/factory ticket set T-0001 title=Renamed >/dev/null 2>&1; show; bin/factory ticket set T-0001 'in_flight=[]' >/dev/null 2>&1; show)`
- THEN it prints exactly `state=ready-for-triage reason=None`, then `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage`

### Requirement: Home-relative entries resolve against the account's home
A tripwire entry starting `~/` SHALL resolve against the account's home directory from the system user database, not against the `HOME` variable of the process running the command.

#### Scenario: A file under a substitute HOME is not watched
- WHEN `(T20=$(mktemp -d); mkdir -p $T20/home; echo a > $T20/home/.t0020-probe; echo a > $T20/live.json; TRIPWIRE="tripwire: {park: [\"~/.t0020-probe\", $T20/live.json]}"; export HOME=$T20/home; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && echo b > $T20/home/.t0020-probe && echo b > $T20/live.json && bin/factory run finish $R --status-override KILLED >/dev/null 2>&1; bin/factory ticket show T-0001 --json | tail -1 | python3 -c 'import json,sys; t=json.load(sys.stdin); print("state=%s reason=%s" % (t["state"], (t["parked"] or {}).get("reason")))' | sed "s|$T20|\$T20|g")`
- THEN it prints exactly `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage` (the account's real `~/.t0020-probe` does not exist and is unchanged; the substitute-`HOME` file is not named)

### Requirement: A tripwire list holds files only
`run start` SHALL be refused, with exit 2, a message naming the entry, and no run recorded, when a tripwire entry is an existing directory.

#### Scenario: A directory in the list refuses run start
- WHEN `(T20=$(mktemp -d); mkdir -p $T20/live; TRIPWIRE="tripwire: {park: [$T20/live]}"; . ${TMPDIR:-/tmp}/t0020-bare.sh && bin/factory run start --role triage --ticket T-0001 > $T20/start.out 2>&1; echo "exit=$? named=$(grep -q "$T20/live" $T20/start.out && echo yes || echo no) runs=$(ls $T20/store/runs 2>/dev/null | wc -l | tr -d ' ')")`
- THEN it prints exactly `exit=2 named=yes runs=0`

### Requirement: The baseline never travels with a store commit
The harness SHALL keep each file's start-of-run SHA-256 in exactly one file in the store, and the store's `.gitignore` SHALL exclude that file.

#### Scenario: The baseline digest is kept but not committable
- WHEN `(. ${TMPDIR:-/tmp}/t0020-fix.sh && H=$(printf '{"token": "T20-SECRET-A"}\n' | python3 -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())') && echo "held=$(grep -rl $H $T20/store | wc -l | tr -d ' ')" && git -C $T20/store init -q && git -C $T20/store add -A && echo "committed=$(git -C $T20/store grep --cached -l $H | wc -l | tr -d ' ')")`
- THEN it prints exactly `held=1`, then `committed=0`

### Requirement: An instance without a tripwire behaves as before
For an instance with no `tripwire` key, `run start` and `run finish` SHALL write and print exactly what they do today.

#### Scenario: No tripwire key, no new output or file
- WHEN `(TRIPWIRE=; . ${TMPDIR:-/tmp}/t0020-bare.sh && R=$(bin/factory run start --role triage --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/') && printf 'Type: bug\nTitle: F\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n' > $T20/out.md && bin/factory run finish $R --output-file $T20/out.md | tail -1 | python3 -c 'import json,sys; print(sorted(json.load(sys.stdin)))'; ls $FACTORY_STATE/runs/$R | tr '\n' ' '; echo)`
- THEN it prints exactly `['confidence', 'escalations', 'ok', 'run_id', 'status']`, then `meta.yaml output.md system-prompt.txt ` (with the trailing space)

#### Scenario: The harness suite passes under a throwaway HOME
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`
- THEN it exits 0 with no failures

### Requirement: The workflow scripts stop on a tripwire park
Each workflow script's role-running step SHALL return without routing when `run finish` reports that it parked the ticket.

#### Scenario: Both scripts check run finish for a park
This is a structural check: the workflow scripts need the Claude Code Workflow runtime and cannot run in the verifier.
- WHEN `for f in factory/workflows/intake.js factory/workflows/build.js; do echo "$f $(awk '/^async function runRole/{f=1} f&&/^}/{f=0} f' $f | grep -c '\.parked')"; done`
- THEN each of the two lines ends in a number of 1 or more, and reading those lines shows a `return null` taken when the `run finish` answer carries `parked`

=== specs/coding-standard/spec.md
## ADDED Requirements

### Requirement: The coding standard has a rule on patch targets and outside-path guards
`docs/coding.md` SHALL hold a rule 6, in the page's format (a `Check:` line, a `Principle:` line, a `Before` example from the 2026-10-04 incident and an `After:`), saying that tests reach a patched path through its module's attribute and that a new path outside the repository ships with a test guard against resolving it outside `tmp_path`. Rule 4 SHALL list rule 6 among the rules whose findings take no tag.

#### Scenario: Rule 6 is in the page's format and rule 4 names it
- WHEN `awk '/^## 6\. /{f=1;print "heading=yes";next} /^## |^The check order/{f=0} f&&/^Check: /{c=1} f&&/^Principle: /{p=1} f&&/^Before /{b=1} f&&/^After: /{a=1} f&&/tmp_path/{t=1} f&&/store\.policy_store_path/{m=1} END{print "check="(c?"yes":"no"), "principle="(p?"yes":"no"), "before="(b?"yes":"no"), "after="(a?"yes":"no"), "tmp_path="(t?"yes":"no"), "module_attr="(m?"yes":"no")}' docs/coding.md; grep -c 'rule 2, 3, 5 or 6' docs/coding.md; tail -2 docs/coding.md | head -1 | cut -c1-28`
- THEN it prints exactly `heading=yes`, then `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes`, then `1`, then `The check order (rule 1) and`

=== specs/factory-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the tripwire
The design doc SHALL carry a paragraph opening `**Tripwire on live files.**`; the instance template SHALL show the `tripwire` key; the README's **Built** list SHALL name the tripwire, and "Where a human decides" SHALL say how a tripwire park is resumed; the changelog's last numbered entry SHALL record the change, with numbering unbroken.

#### Scenario: Design doc, template and README name the tripwire
- WHEN `echo "design=$(grep -c '^\*\*Tripwire on live files\.\*\*' docs/design.md) template=$(grep -c 'tripwire' factory/instance.template.yaml) built=$(awk '/^\*\*Built\*\*/{f=1} /^\*\*Not built\*\*/{f=0} f' README.md | grep -ci 'tripwire') resume=$(grep -c 'A ticket the tripwire parked' README.md)"`
- THEN it prints `design=1`, `template=` a number of 1 or more, `built=` a number of 1 or more, and `resume=1`

#### Scenario: The changelog records the change in order
- WHEN `awk '/^[0-9]+\. /{n++; split($0,a,"."); if (a[1]+0!=n) bad=1; last=$0} END{print "contiguous=" (bad?"no":"yes"), "last_names_tripwire=" (last ~ /tripwire/ ? "yes":"no")}' docs/changelog.md`
- THEN it prints exactly `contiguous=yes last_names_tripwire=yes`

#### Scenario: The change adds no whitespace errors
- WHEN `git diff --check main...HEAD`
- THEN it exits 0 with no output

=== verification.md
## Acceptance

- A changed park-listed file parks the ticket → NEW. Today it prints `state=ready-for-triage reason=None` then `secrets=0`: the `tripwire` key is ignored and the ticket stays ready to move.
- A park-listed file deleted or created during a run counts as changed → NEW. Today: `state=ready-for-triage reason=None`.
- A killed run is still compared → NEW. Today: `state=ready-for-triage reason=None`.
- A changed escalate-listed file is queued and the ticket still moves → NEW. Today: `state=ready-for-triage reason=None`, `items=None` (no `escalation.queued` event), `moved=yes`, `secrets=0`.
- Unchanged listed files neither park nor escalate → REGRESSION. Today: `status=ACCEPT`, `state=ready-for-triage reason=None`, `escalations=0`.
- Clearing an abandoned run compares it; an unrelated set does not → NEW. Today both lines are `state=ready-for-triage reason=None`.
- A file under a substitute HOME is not watched → NEW. Today: `state=ready-for-triage reason=None`. An implementation that expanded `~` with `HOME` would print `reason=tripwire: $T20/home/.t0020-probe, $T20/live.json changed during run-0001-triage` and fail.
- A directory in the list refuses run start → NEW. Today: `exit=0 named=no runs=1`.
- The baseline digest is kept but not committable → NEW. Today: `held=0`, `committed=0`: no baseline exists.
- No tripwire key, no new output or file → REGRESSION. Today: `['confidence', 'escalations', 'ok', 'run_id', 'status']` and `meta.yaml output.md system-prompt.txt `.
- The harness suite passes under a throwaway HOME → REGRESSION. Today: `171 passed in 103.25s`.
- Both scripts check run finish for a park → NEW. Today it prints `factory/workflows/intake.js 0` and `factory/workflows/build.js 0`. This check is structural; see its scenario.
- Rule 6 is in the page's format and rule 4 names it → NEW. Today: no `heading=yes` line, then `check=no principle=no before=no after=no tmp_path=no module_attr=no`, then `0`, then `The check order (rule 1) and`.
- Design doc, template and README name the tripwire → NEW. Today: `design=0 template=0 built=0 resume=0`.
- The changelog records the change in order → NEW. Today: `contiguous=yes last_names_tripwire=no`.
- The change adds no whitespace errors → REGRESSION. Today it exits 0.

Every "today" output above was produced on `main` at `1c5f6a7` by running the scenario's WHEN exactly as written, after writing the two fixture scripts.

## Out-of-scope observations

- The routing table lets a `ticket transition --by workflow` move a ticket out of `parked` into most states. So any park written outside the workflow script, while that script still routes the same ticket, can be silently undone. Part C closes this for the tripwire only. A store-level guard on leaving `parked` would close it for every park.
- A run left in the in-flight list with no `run finish` blocks the ticket: `run start` refuses the next run. The only recovery today is `ticket set <id> in_flight=[]` or a manual `run finish --status-override KILLED`, and no page documents either.

## PR description (the implementer's output)

Sub-ticket: T-0020.1 (parent T-0020, issue #38). Branch `factory/T-0020.1`, head `b45462df5b0c9570634b4d6d2074b3054ac296b6`, one commit on base `02465fa0356b30d72ce6211ea874e230d5113236`. 11 files, +429 / -18.

## What changed

Until now, nothing in the factory noticed when a role run changed one of the operator's live files outside the repository. A role run is one agent call that the harness starts and records. With this change, an instance can list such files under `tripwire` in its `instance.yaml` (the instance is a target repo's `.factory/` directory). A changed file on the `park` list stops the ticket and puts it in the human queue. A changed file on the `escalate` list queues a flagged item for the operator, and the ticket goes on. No event, reason or output names anything but the file's path.

**A. Baseline at run start, comparison when the run ends** (`factory/tripwire.py` new, `factory/cli.py`, `factory/store.py`)
- A1/A2: `tripwire.baseline(cfg)` reads `cfg["tripwire"]`. It returns None when the key is absent or null, or when both lists are empty. Otherwise the key must be a mapping whose only keys are `park` and `escalate`, each a list of strings. A `~/` entry expands with `pwd.getpwuid(os.getuid()).pw_dir`, never `HOME`. Some entries are refused with `store.Refused` (exit 2), and the message names the entry as written and as expanded: an entry that is not absolute, one that exists and is not a regular file, and one that exists and cannot be read. `run_start` calls it before `store.next_run_id`, so a refusal writes nothing. Each file's state is the hex SHA-256 of its bytes (`hashlib.file_digest`), or `absent`.
- A3: after `meta.yaml`, `run_start` calls `store.ensure_gitignore(root)` and writes `runs/<id>/tripwire.yaml` as `{park: {...}, escalate: {...}, compared: null}`. `STORE_GITIGNORE` gains a comment line and `runs/*/tripwire.yaml`. The tuple `ensure_gitignore` checks gains the same line. The two existing lines are unchanged.
- A4: `tripwire.compare(root, rid, tid)` re-hashes the baseline's paths, but only when `compared` is null. A file that cannot be read now counts as changed. The function sets `compared` and returns the changed paths in baseline order. Then:
  - a park-list change on a ticket that is neither parked nor closed parks it, with reason `tripwire: <paths> changed during <run>`, outputs `[<run>]` and history `by: tripwire`;
  - on a ticket already parked or closed, the same reason goes out as an `escalation.queued` event instead;
  - an escalate-list change logs `escalation.queued`, with item `tripwire (escalate): <paths> changed during <run>`;
  - any change also logs `tripwire.changed`.

  The park goes through the new helper `store.park_ticket`. That helper is `ticket_park`'s old body, moved. `ticket_park` now calls it and keeps its own refusal for a `closed` or `parked` ticket.
- A5: `run_finish` calls `compare` after the run is recorded and its events are logged, for both normal and `--status-override KILLED` finishes. When the run has a baseline, the printed JSON gains `tripwire: {park, escalate}`. When the comparison parked the ticket, it also gains `parked: <reason>`.

**B. A run dropped by hand** (`ticket_set`): `ticket_set` notes `in_flight` before applying the assignments. After saving, it compares each run that left the list. When one of them parked the ticket, the JSON gains `parked`.

**C. Workflow stop** (`intake.js`, `build.js`): `runRole` gains `if (fin.parked) { log(...); return null }`, right after the existing `if (!fin.ok) …` line. It uses `TICKET` in intake.js and `ticket` in build.js. In build.js the checker `run cleanup` still runs first. Every caller of `runRole` returns on `null` without routing. I checked this with `grep -n -A2 "await runRole"` over both scripts.

**D. Documents**
- D1: the template gets the commented `tripwire` example after `protected_paths`. `run_env: {}` is untouched.
- D2: a new `**Tripwire on live files.**` paragraph in `docs/design.md`, placed after **What the harness itself owns**. It is prose, so no `docs/prompts/` file changes.
- D3: README gets a **Built** bullet after "Instances and the harness lock", and the resume sentence after "returns it." in "Where a human decides". The status date is already 2026-10-04, today's date.
- D4: changelog entry 49, before `Declined:`, with the required opening text.

**E. `docs/coding.md`**: rule 6, in the page's format, goes before the closing "The check order…" paragraph. In rule 4, "rule 2, 3 or 5" becomes "rule 2, 3, 5 or 6", kept on one line. The two lines after it re-wrapped to stay within the page width.

**F.** `tests/factory/test_tripwire.py` (new, 13 tests).

Callers of the existing functions I changed (coding rule 2), from a grep of `factory/`:
- `ticket_park` is reached only through the CLI parser (`cli.py:1036`) and the workflow scripts' `park()`. Its output is unchanged.
- `ensure_gitignore` is called by `run_start` (new, only when a baseline exists), `_start_build_run` and `init`.
- `run_start`, `run_finish` and `ticket_set` are CLI entry points. Without a `tripwire` key their output is unchanged.

Reuse (coding rule 1): the store's own `read_yaml`, `write_yaml`, `log_event`, `now` and `Refused`, and the standard library's `hashlib.file_digest`. `store.content_hash` does not fit: it hashes text and truncates to 16 hex characters.

## Acceptance results

Every command ran exactly as written under bash, from the worktree root, after `uv sync --frozen` and the fixture GIVEN block. All of them ran under `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`. "Before" means base `02465fa` before any edit. "After" means head `b45462d`.

| Scenario | Kind | Before | After |
|---|---|---|---|
| A changed park-listed file parks the ticket | NEW | `state=ready-for-triage reason=None` / `secrets=0` | `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` / `secrets=0` |
| Deleted or created counts as changed | NEW | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live/policies.json, $T20/live/new.json changed during run-0001-triage` |
| A killed run is still compared | NEW | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` |
| Escalate-listed file queued, ticket moves | NEW | `state=ready-for-triage reason=None` / `items=None` / `moved=yes` / `secrets=0` | `state=ready-for-triage reason=None` / `items=['tripwire (escalate): $T20/live/pairing.json changed during run-0001-triage']` / `moved=yes` / `secrets=0` |
| Unchanged files neither park nor escalate | REGRESSION | (not required) `status=ACCEPT` / `state=ready-for-triage reason=None` / `escalations=0` | same three lines |
| Clearing an abandoned run compares it | NEW | `state=ready-for-triage reason=None` twice | `state=ready-for-triage reason=None` / `state=parked reason=tripwire: $T20/live/policies.json changed during run-0001-triage` |
| Substitute HOME not watched | NEW | `state=ready-for-triage reason=None` | `state=parked reason=tripwire: $T20/live.json changed during run-0001-triage` |
| Directory refuses run start | NEW | `exit=0 named=no runs=1` | `exit=2 named=yes runs=0` |
| Baseline kept but not committable | NEW | `held=0` / `committed=0` | `held=1` / `committed=0` |
| No tripwire key, no new output or file | REGRESSION | (not required) same as after | `['confidence', 'escalations', 'ok', 'run_id', 'status']` / `meta.yaml output.md system-prompt.txt ` |
| Suite under a throwaway HOME | REGRESSION | not run | `203 passed in 103.70s`, exit 0 (171 on the spec's base, plus T-0019's tests, plus 13 new) |
| Both scripts check run finish for a park | NEW | `intake.js 0` / `build.js 0` | `factory/workflows/intake.js 1` / `factory/workflows/build.js 1`; each count is the `if (fin.parked) { log(...); return null }` line inside `runRole` |
| Rule 6 format, rule 4 names it | NEW | no `heading=yes`, all `no`, `0`, `The check order (rule 1) and` | `heading=yes` / `check=yes principle=yes before=yes after=yes tmp_path=yes module_attr=yes` / `1` / `The check order (rule 1) and` |
| Docs name the tripwire | NEW | `design=0 template=0 built=0 resume=0` | `design=1 template=1 built=2 resume=1` |
| Changelog in order | NEW | `contiguous=yes last_names_tripwire=no` | `contiguous=yes last_names_tripwire=yes` |
| No whitespace errors | REGRESSION | exit 0 | no output, exit 0 |
| Only declared files change | NEW | (empty) | exactly the 11 listed paths, sorted |

What the outputs mean:
- `secrets=0`: no store file and no captured command output holds the watched files' contents.
- `named=yes runs=0`: the refusal message names the bad entry, and no run directory was created.
- `held=1 committed=0`: the digest is in exactly one store file, and `git add -A` in the store does not stage it.
- The substitute-HOME probe path `~/.t0020-probe` resolves to the account's home. I confirmed with `ls` that it does not exist there, before and after.

Gate commands, each run from the worktree on `b45462d`:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: run once, as the suite REGRESSION command above, which wraps it exactly as written. Result: `203 passed`, exit 0.

## Tests added/changed

- Added `tests/factory/test_tripwire.py`, 13 tests through `bin/factory`. Each runs on a copy of the suite's fixture instance with a `tripwire` key appended, and on a throwaway store. The tests cover:
  - park; delete and create; killed;
  - escalate, with the ticket still able to transition;
  - unchanged;
  - a park-list change on a ticket that is already parked, which queues an escalation and does not park again;
  - `ticket set`: an unrelated set does not compare, dropping the run compares it, and a later `run finish` does not compare it again;
  - the account home and not `HOME`;
  - directory refusal; bad-list refusal (relative entry, unknown key, non-mapping, non-string);
  - a baseline held once and never staged;
  - no key: output and files unchanged, and no `.gitignore` written;
  - empty lists mean off.

  Every listed file that exists lives under `tmp_path`. The home test lists `~/.tripwire-probe-<uuid>` and asserts first that it does not exist. Before the change, 11 failed and 2 passed: the two backward-compatibility tests.
- Changed: none.

## Known gaps and uncertainties

- The store `.gitignore` gets duplicate lines on existing stores. When a store's `.gitignore` already has the two old lines, the next `ensure_gitignore` appends the whole block again: two old lines plus the new one. Every build-role `run start` calls it. On this repo's tracked store and on Nanobot's, that rewrites `.gitignore` once with the duplicated lines. The plan note calls this harmless, and I kept the whole-block append. Appending only the missing lines would also have been within A3.
- A run compared by `ticket set` is not compared again. If someone later runs `run finish` on that same run, the JSON has no `tripwire` field, because nothing was compared that time. The test covers this. A5 says "when the run had a baseline, add the field"; I read it as "when a comparison happened". I did not print `{"park": [], "escalate": []}`, because that would claim nothing changed.
- An agent call that throws can leave a stale "parked" line in the workflow log. In both scripts the `catch` path runs `run finish --status-override KILLED` and then calls `park(...)` without reading `fin`. If the tripwire parked the ticket in that `run finish`, the follow-up `ticket park` is refused, because the ticket is already parked. The ticket stays parked with the tripwire reason. The script still logs `parked: agent call failed…`. Part C names only the line after `if (!fin.ok)`, so I left this path alone.
- Parallel checker runs can see each other's changes. In build.js the reviewer and verifier run in parallel on one ticket. A change made during one shows up in both comparisons. The second comparison finds the ticket already parked and queues an escalation, as the "during" wording intends.
- The README's status date is already 2026-10-04, today. If the merge lands on a later day, D3 asks for that date.
- The new README **Built** bullet uses the spec's exact text, "It is tested, and has not yet fired on a real ticket." That sits against the README's "Ground truth only above 'Where this can go'" rule, under which a thing appears only after it has run on a real ticket. I followed the approved spec text.
- The workflow scripts were checked by reading them and by `node --check` on each (both exit 0) only. They cannot run here: they need the Claude Code Workflow runtime.
- `factory:` markers added: none.

## Out-of-scope observations

- The README paragraph at lines 105-107 ("At any step a role can say it needs a human … So does running out of rounds, or a run exceeding its budget.") lists what parks a ticket and does not name the tripwire. D3 did not ask for that edit, so I left it.
- Both of the parent's out-of-scope observations still hold:
  - Nothing guards a ticket leaving `parked`. Part C closes that gap only for tripwire parks.
  - Recovery of a run left in flight is undocumented.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command and both gates were run on `b45462d` and printed the required output; the workflow-script change is checked structurally only.
ESCALATIONS: none

## Diff `02465fa0356b30d72ce6211ea874e230d5113236...b45462df5b0c9570634b4d6d2074b3054ac296b6`

diff --git a/README.md b/README.md
index e9cb379..4d5cb93 100644
--- a/README.md
+++ b/README.md
@@ -319,7 +319,9 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 | **Upgrade** | `factory --accept-harness <sha> <command>` | that this target adopts a new harness revision |
 
 Gap, as of today: an implementer that reports itself blocked has no `resolve` verb. A plain
-`ticket transition --to ready-for-implementer` returns it. Everything else is the harness's and
+`ticket transition --to ready-for-implementer` returns it. A ticket the tripwire parked returns the
+same way, to the state its record names as `parked.from`, once the operator has checked the named
+files; a checker park can use `resolve --redispatch` instead. Everything else is the harness's and
 the scripts': which role runs next, how many rounds, what the checkers receive, when a merge is
 allowed, when the ticket closes.
 
@@ -342,6 +344,12 @@ allowed, when the ticket closes.
   `archive` applies the deltas, so the description of the system is kept current by the pipeline.
 - **Instances and the harness lock.** One runtime serves any number of targets. Each adopts a new
   harness revision only when its operator accepts it. See "Where it runs".
+- **Tripwire on live files.** An instance can list files outside the repo that no role run should
+  change, such as a live bot's credentials, under `tripwire` in `instance.yaml`: a `park` list and
+  an `escalate` list. The harness hashes each file when a run starts and compares when the run ends,
+  killed runs included. A changed `park` file parks the ticket; a changed `escalate` file is queued
+  for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not
+  yet fired on a real ticket.
 
 **Not built**
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 1874795..baf1750 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -50,5 +50,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 46. After the Nanobot target's T-0003 (2026-10-04), a ticket that existed only to get a decision: the human answered its question about where the port's code lives and closed it, archive never ran, and the decision stayed in that ticket's request, so the operator copied it by hand into the two later requests that depend on it. `decisions.md` gains writers besides archive: `factory decision add <ticket id> "<line>"`, at any ticket state, closed included, and `--decision "<line>"` on `resolve --answer` or `resolve --close`, refused with any other `resolve` mode. Each appends the line in archive's format, `<YYYY-MM-DD> <ticket id> <line>`, creates the file when absent, and logs `decision.recorded`. The spec writer and the critic receive a non-empty `decisions.md` after current truth, and the planner after the approved spec; triage and the build roles do not. Triage's NEEDS-HUMAN question and the spec writer's open questions now ask whether the answer is a standing decision that later tickets must follow. Archive's own output is unchanged.
 47. After issue #33 (2026-10-04), where six approved tickets on the Nanobot target stalled with no record of why: intake ends at the spec gate, and the build owns planning. A build that finds a planned parent with no sub-tickets creates them from the planner run named by the parent's latest `plan.added` event (`subticket add PARENT` with no `--run`), or parks the parent with a reason containing `no sub-tickets`. No stop is silent any more: an `agent()` call that throws finishes its run KILLED and parks the ticket with `agent call failed: <role>: <error>`, and a refused `parent-check` parks the parent with its refusal. The verifier writes `Gate suite:` as a plain line, never a heading or bold, and the harness also reads that line in heading or bold form, so a verifier's PASS written as `## Gate suite: PASS` is no longer recorded as a missing gate line.
 48. After issue #36 (2026-10-04): a role's test run overwrote the Nanobot bot's live permission file, so every role now runs tests, scripts and prototypes through a wrapper the composer hands it, which sets a throwaway `HOME`, with gate commands already wrapped and `run_env` for tool caches; and the preamble forbids running anything that could write a protected path outside the repository. A plan's bulleted field lines lost every sub-ticket's dependencies, so the harness now reads `Depends on:` and `Parallel-safe:` lines that start with a list bullet and refuses a sub-ticket with no `Depends on:` line; and the planner prompt shows the three parsed lines at the start of a line and says `yes` means alongside every sibling.
+49. After the 2026-10-04 Nanobot incident, where a role's tests overwrote the live bot's permission file and nothing in the factory noticed: an instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list, files only, with `~` meaning the account's home and never `HOME`. `run start` records a SHA-256 of each file, or that it is absent, in a per-run baseline that the store's `.gitignore` excludes, and refuses a directory or an entry that is neither absolute nor `~/`. Each run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A changed `park` file parks the ticket with `tripwire: <files> changed during <run>`, "during" because overlapping runs and the operator's own edits cannot be told apart; on a ticket already parked or closed the reason is queued as an escalation instead. A changed `escalate` file queues an escalation and the run goes on. Nothing prints a file's contents, and the workflow scripts stop on a `run finish` that parked the ticket instead of routing on the role's STATUS. The tripwire detects a write after the fact; it does not prevent one. The incident's code-level cause, a test module that imported a path function by name before the fixture replaced it, gives the coding standard rule 6: a test reaches a patched path through its module's attribute, and a new path outside the repository ships with a test guard that fails any test resolving it outside `tmp_path`; rule 4 lists rule 6 among the rules whose findings take no tag.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/coding.md b/docs/coding.md
index cc27e2d..c83c77d 100644
--- a/docs/coding.md
+++ b/docs/coding.md
@@ -64,9 +64,9 @@ is greppable: `grep -rnE '(#|//|/\*) ?factory:'` lists every one in the code.
 Check: each over-building finding (code the change could have reused, or did not need) starts,
 after its severity, with one tag from the table (`[BLOCKING] reuse: file:line: problem →
 consequence`), names what the table says to name, and has the table's severity. A finding against
-rule 2, 3 or 5 takes no tag; it earns its severity as a correctness or scope finding. The pass ends
-with `net: -N lines possible`, where N is the lines the tagged findings would remove, or with
-`Lean already.`
+rule 2, 3, 5 or 6 takes no tag; it earns its severity as a correctness or scope finding. The pass
+ends with `net: -N lines possible`, where N is the lines the tagged findings would remove, or
+with `Lean already.`
 Principle: per tag, in the table.
 
 | Tag | Flags | Names | Severity | Principle |
@@ -94,5 +94,23 @@ state `on_hold` and a function `hold_ticket()` for the same thing.
 After: the state stays `parked` and the command stays `ticket park`, the names the store and the
 README already use.
 
+## 6. A test reaches a patched path through its module, and a new outside path ships with a guard.
+Check: each function or constant your tests patch to redirect a path outside the repository is
+called in test code as an attribute of its module (`store.policy_store_path()`), never through a
+name imported when the test file loads. Each path your diff adds outside the repository (a data
+directory, a config file) comes with an autouse test fixture that fails any test resolving that
+path outside `tmp_path`.
+Principle: patch where the name is looked up (the Python `unittest.mock` documentation, "Where to
+patch"); and fail-safe defaults (Saltzer and Schroeder): a test that stops is cheaper than one that
+writes live data.
+Before (a Nanobot implementer run, 2026-10-04): the test module ran
+`from nanobot.policy.store import policy_store_path` when pytest collected it. The conftest fixture
+then replaced `nanobot.policy.store.policy_store_path`, but the test helpers still held the real
+function. The tests overwrote the live bot's `~/.nanobot/policies.json` and its `.bak`, and an
+unrelated `FileExistsError` was the only sign.
+After: the test module runs `from nanobot.policy import store` and calls `store.policy_store_path()`,
+so the fixture's patch reaches every call. An autouse fixture fails any test whose resolved policy
+path is not under `tmp_path`, so the next escape stops a test instead of writing live data.
+
 The check order (rule 1) and the tag vocabulary (rule 4) are adapted from ponytail
 (DietrichGebert/ponytail, MIT), as the design document's changelog records.
diff --git a/docs/design.md b/docs/design.md
index 1ef552d..7a1aaa5 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -51,6 +51,8 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **What the harness itself owns** (no platform provides these): the routing table, the round counter and the max-round cutoff, composing each role's input from *only* its declared sources, choosing the model per role, and the escalation queue view for the daily human pass.
 
+**Tripwire on live files.** An instance may list files outside the repository under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list. A `~/` entry means the account's home directory, never the `HOME` variable, so a run under a throwaway `HOME` still watches the real files. The lists hold files only: a directory, or an entry that is neither absolute nor `~/`, refuses `run start`. `run start` records a SHA-256 of each listed file, or that it is absent, in a baseline in the run's directory, which the store's `.gitignore` excludes so no store commit carries a digest of a live secret. The run is compared once, when it leaves the in-flight list: at `run finish`, killed runs included, or at a `ticket set` that drops it. A file created, deleted or modified counts as changed. A changed `park` file parks the ticket with the reason `tripwire: <files> changed during <run>`. The reason says "during", not "by", because runs on other tickets and the operator's own edits can overlap a run, and the tripwire cannot tell them apart. On a ticket already parked or closed, the same reason is queued as an escalation instead. A changed `escalate` file queues an escalation and the run goes on; that list is for files with legitimate outside writers. No event, reason or output names more than a file's path: nothing prints a file's contents. The workflow scripts stop on a `run finish` that parked the ticket, instead of routing on the role's STATUS. The tripwire detects a write after the fact; it does not prevent one.
+
 **Role-context block.** Every role's input opens with a role-context block, ahead of the INPUT its role prompt declares and anything the routing table's "Receives" column adds. The block is per repo, like `{repo name}` and the protected paths: it says which repository the role works in, how to run commands and tests there, what kind of request to expect, and who reads what the roles write there. Its text is the same for every role. It is a declared input of every role, so composing from *only* declared sources includes it; it travels with the input (piece 3), not in the system prompt. A wrong block misdirects every role at once, and the checkers receive the same block, so they share the error instead of catching it. The block is kept in the repo it describes, at `.factory/context.md`. That directory, `.factory/`, is the repo's instance of the factory: `instance.yaml` (the per-repo config: `{repo name}`, protected paths, `{gate commands}`, the variables kept for code runs (`run_env`), models, routing, the store's path and the harness checkout it runs with), `context.md`, `harness.lock` (the harness revision the instance has accepted; the harness refuses to touch the instance's store under any other revision until a human accepts it, and logs the acceptance) and the store. The harness picks the instance by walking up from the working directory to the nearest `.factory/instance.yaml`, or takes it from an explicit override, and never falls back to an instance of its own; the composer prepends that instance's `context.md`, and the preamble's `{repo name}` and protected paths are filled from its `instance.yaml`, and `{writing standard}` with the path of `docs/writing.md` in the harness checkout that runs it. `{coding standard}`, in the implementer and code reviewer prompts, is filled the same way with the path of `docs/coding.md` in that checkout. The composer also gives every role a "Running code" section: a wrapper that runs one command in a subshell with `HOME` set to a fresh temporary directory, exporting any variables the instance lists in `run_env`; `{gate commands}` reach a role already wrapped. It is guidance, not a sandbox: a command can still write an absolute path, which the preamble forbids for protected paths outside the repository. Each run leaves its temporary directory behind.
 
 **Model per role, starting point.** One rule: a role's model depends on what checks its output. Default Opus. A checker is never weaker than the author it checks, except the verifier, whose check is the commands. Fable goes where a role's output is checked only by a human: the critic, the code reviewer, the retro. Sonnet only where the output is checked mechanically inside the same loop. The verifier is the one checker whose check is the commands themselves; its probe step is judgment, so it drops to Sonnet only where probes rarely matter. Tune effort before changing model; record the model on every run so the retro can compare failure rates by model; this table is the harness's model config, so a retro diff to it is the proposal path. Never let an author and its checker share a model where you can avoid it; the verifier is again the exception.
diff --git a/factory/cli.py b/factory/cli.py
index 8a96fc4..f1c1195 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -18,7 +18,7 @@ from pathlib import Path
 
 import yaml
 
-from factory import compose, gitops, instance, specstore, status, store, subtickets
+from factory import compose, gitops, instance, specstore, status, store, subtickets, tripwire
 from factory.store import Refused
 
 ROLES = ("triage", "spec_writer", "critic", "planner", "implementer", "reviewer", "verifier")
@@ -108,6 +108,7 @@ def _set_dotted(obj: dict, key: str, value) -> None:
 
 def ticket_set(a, root, cfg):
     t = store.load_ticket(root, a.id)
+    was_in_flight = list(t.get("in_flight") or [])
     changes = {}
     for kv in a.assignments:
         if "=" not in kv:
@@ -118,7 +119,13 @@ def ticket_set(a, root, cfg):
         changes[k] = val
     store.save_ticket(root, t)
     store.log_event(root, "ticket.set", ticket=t["id"], changes=changes)
-    out({"ok": True, "id": t["id"], "changes": changes})
+    res = {"ok": True, "id": t["id"], "changes": changes}
+    for rid in was_in_flight:  # a run dropped by hand is compared now, as run finish would
+        if rid not in (t.get("in_flight") or []):
+            tw = tripwire.compare(root, rid, t["id"])
+            if tw and tw["parked"]:
+                res["parked"] = tw["parked"]
+    out(res)
 
 
 def _apply_round(t: dict, op: str | None, cfg: dict) -> None:
@@ -175,13 +182,7 @@ def ticket_park(a, root, cfg):
     frm = t["status"]
     if frm in ("closed", "parked"):
         raise Refused(f"{t['id']} is {frm}; cannot park")
-    t["status"] = "parked"
-    t["parked"] = {"reason": a.reason, "since": store.now(), "from": frm,
-                   "outputs": [x for x in (a.outputs or "").split(",") if x], "question": a.question}
-    t["history"].append({"ts": store.now(), "from": frm, "to": "parked", "by": "park", "reason": a.reason})
-    store.save_ticket(root, t)
-    store.log_event(root, "ticket.parked", ticket=t["id"], **{"from": frm, "reason": a.reason})
-    store.log_event(root, "escalation.queued", ticket=t["id"], items=[a.reason])
+    store.park_ticket(root, t, a.reason, [x for x in (a.outputs or "").split(",") if x], a.question)
     out({"ok": True, "id": t["id"], "state": "parked", "reason": a.reason})
 
 
@@ -208,6 +209,7 @@ def run_start(a, root, cfg):
         raise Refused(f"{t['id']} already has a {a.role} run in flight")
     if a.role in ("triage", "spec_writer", "critic", "planner") and t["in_flight"]:
         raise Refused(f"{t['id']} already has run {t['in_flight'][0]} in flight")
+    baseline = tripwire.baseline(cfg)  # hashed before the run id is reserved: a refusal writes nothing
     rid = store.next_run_id(root, a.role)
     model = a.model or cfg["models"][a.role]
     d = root / "runs" / rid
@@ -217,6 +219,9 @@ def run_start(a, root, cfg):
     if a.role in BUILD_ROLES:
         _start_build_run(root, cfg, t, meta, d, parent_close)
     store.write_yaml(d / "meta.yaml", meta)
+    if baseline:
+        store.ensure_gitignore(root)
+        store.write_yaml(d / "tripwire.yaml", baseline)
     prompt_name = a.role
     preamble = instance.fill_preamble((PROMPTS / "preamble.md").read_text(encoding="utf-8"), cfg)
     role_prompt = instance.fill_standards((PROMPTS / f"{prompt_name}.md").read_text(encoding="utf-8"))
@@ -316,8 +321,14 @@ def run_finish(a, root, cfg):
     store.log_event(root, ev, ticket=t["id"], run=a.run, role=meta["role"], status=parsed["status"], wall_s=meta["wall_s"])
     if parsed.get("escalations"):
         store.log_event(root, "escalation.queued", ticket=t["id"], run=a.run, items=parsed["escalations"])
-    out({"ok": True, "run_id": a.run, "status": parsed["status"], "confidence": parsed.get("confidence"),
-         "escalations": parsed.get("escalations", [])})
+    res = {"ok": True, "run_id": a.run, "status": parsed["status"], "confidence": parsed.get("confidence"),
+           "escalations": parsed.get("escalations", [])}
+    tw = tripwire.compare(root, a.run, t["id"])
+    if tw:
+        res["tripwire"] = {"park": tw["park"], "escalate": tw["escalate"]}
+        if tw["parked"]:
+            res["parked"] = tw["parked"]
+    out(res)
 
 
 # ----- spec / plan ----------------------------------------------------------------
diff --git a/factory/instance.template.yaml b/factory/instance.template.yaml
index 8674d5d..ccabbdb 100644
--- a/factory/instance.template.yaml
+++ b/factory/instance.template.yaml
@@ -11,6 +11,11 @@ state_dir: .factory/state
 # Filled into the preamble's protected-path line at run start as `class (glob, glob), ...`.
 protected_paths:
   infra: [".factory/instance.yaml", ".factory/harness.lock", ".factory/context.md"]
+# Live files outside the repo that no role run should change, as absolute or `~/` paths (`~` is the
+# account's home, never $HOME). `run start` hashes each; the comparison runs when the run leaves the
+# in-flight list. A changed `park` file parks the ticket; a changed `escalate` file queues an
+# escalation and the run goes on. Contents are never printed. Files only: a directory is refused.
+# tripwire: {park: [], escalate: []}
 # Commands every implementer and verifier runs in the checkout under test, each exactly as written.
 # `{integration}` is replaced with the checkout that has the integration branch.
 gate_commands: []
diff --git a/factory/store.py b/factory/store.py
index 024f10f..295c111 100644
--- a/factory/store.py
+++ b/factory/store.py
@@ -46,15 +46,17 @@ def now() -> str:
     return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
 
 
-STORE_GITIGNORE = "# git worktrees the build half creates; they are checkouts, never store content\nworktrees/\nruns/*/wt/\n"
+STORE_GITIGNORE = ("# git worktrees the build half creates; they are checkouts, never store content\nworktrees/\nruns/*/wt/\n"
+                   "# tripwire baselines: digests of the operator's live files, never committed\nruns/*/tripwire.yaml\n")
 
 
 def ensure_gitignore(root: Path) -> None:
     """The store keeps implementer worktrees under worktrees/ and checker checkouts under runs/<id>/wt/.
-    Both are nested git checkouts: a store committed by directory must not pick them up."""
+    Both are nested git checkouts: a store committed by directory must not pick them up. Nor may it
+    pick up a run's tripwire baseline, runs/<id>/tripwire.yaml, which holds digests of live files."""
     p = root / ".gitignore"
     have = p.read_text(encoding="utf-8") if p.exists() else ""
-    missing = [ln for ln in ("worktrees/", "runs/*/wt/") if ln not in have.splitlines()]
+    missing = [ln for ln in ("worktrees/", "runs/*/wt/", "runs/*/tripwire.yaml") if ln not in have.splitlines()]
     if missing:
         root.mkdir(parents=True, exist_ok=True)
         p.write_text((have.rstrip() + "\n\n" if have.strip() else "") + STORE_GITIGNORE, encoding="utf-8")
@@ -97,6 +99,19 @@ def save_ticket(root: Path, t: dict) -> None:
     write_yaml(ticket_path(root, t["id"]), t)
 
 
+def park_ticket(root: Path, t: dict, reason: str, outputs: list[str], question: str | None = None,
+                by: str = "park") -> None:
+    """Park ticket `t` (the caller has checked it is not parked or closed): record where it came
+    from, save it, and queue the reason for the operator."""
+    frm = t["status"]
+    t["status"] = "parked"
+    t["parked"] = {"reason": reason, "since": now(), "from": frm, "outputs": outputs, "question": question}
+    t["history"].append({"ts": now(), "from": frm, "to": "parked", "by": by, "reason": reason})
+    save_ticket(root, t)
+    log_event(root, "ticket.parked", ticket=t["id"], **{"from": frm, "reason": reason})
+    log_event(root, "escalation.queued", ticket=t["id"], items=[reason])
+
+
 def next_ticket_id(root: Path, prefix: str = "T") -> str:
     tickets = root / "tickets"
     nums = []
diff --git a/factory/tripwire.py b/factory/tripwire.py
new file mode 100644
index 0000000..294910a
--- /dev/null
+++ b/factory/tripwire.py
@@ -0,0 +1,109 @@
+"""Tripwire on live files: notice when a role run changes a file outside the repo.
+
+An instance lists files under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list.
+`run start` records each file's SHA-256 (or `absent`) in `runs/<id>/tripwire.yaml`, which the store's
+`.gitignore` excludes. The run is compared once, when it leaves the in-flight list: a changed `park`
+file parks the ticket, a changed `escalate` file queues an escalation. Nothing here reads a file's
+bytes into an event, a reason or an output; only paths are named.
+"""
+from __future__ import annotations
+
+import hashlib
+import os
+import pwd
+from pathlib import Path
+
+from factory import store
+from factory.store import Refused
+
+LISTS = ("park", "escalate")
+
+
+def _expand(entry: str) -> str:
+    """`~/` is the account's home from the user database, never $HOME: a role run under a throwaway
+    HOME must still watch the real files."""
+    return pwd.getpwuid(os.getuid()).pw_dir + entry[1:] if entry.startswith("~/") else entry
+
+
+def _digest(path: str) -> str:
+    """Hex SHA-256 of the file's bytes, or `absent`. OSError when it exists but cannot be read."""
+    try:
+        with open(path, "rb") as fh:
+            return hashlib.file_digest(fh, "sha256").hexdigest()
+    except FileNotFoundError:
+        return "absent"
+
+
+def baseline(cfg: dict) -> dict | None:
+    """The instance's listed files hashed now, as `{park: {path: state}, escalate: {...}, compared:
+    None}`; None when the tripwire is off (no key, null, or both lists empty). Refused for a list
+    that is not a mapping of string lists, or an entry that is not absolute after expansion, exists
+    and is not a regular file, or exists and cannot be read."""
+    tw = cfg.get("tripwire")
+    if tw is None:
+        return None
+    if not isinstance(tw, dict) or set(tw) - set(LISTS):
+        raise Refused(f"tripwire must be a mapping with only the keys park and escalate, got {tw!r}")
+    lists = {}
+    for name in LISTS:
+        entries = tw.get(name) or []
+        if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
+            raise Refused(f"tripwire.{name} must be a list of file paths, got {entries!r}")
+        lists[name] = [(e, _expand(e)) for e in entries]
+    if not any(lists.values()):
+        return None
+    base: dict = {}
+    for name, entries in lists.items():
+        base[name] = {}
+        for written, path in entries:
+            what = f"tripwire.{name} entry {written!r} ({path})"
+            if not os.path.isabs(path):
+                raise Refused(f"{what} is not an absolute or ~/ path")
+            if os.path.exists(path) and not os.path.isfile(path):
+                raise Refused(f"{what} exists and is not a regular file; list files only")
+            try:
+                base[name][path] = _digest(path)
+            except OSError as e:
+                raise Refused(f"{what} cannot be read: {e.strerror}")
+    base["compared"] = None
+    return base
+
+
+def compare(root: Path, rid: str, tid: str) -> dict | None:
+    """Compare run `rid`'s baseline with the files now, once, and act on ticket `tid`: a changed
+    `park` file parks it (or, if it is already parked or closed, queues the reason as an
+    escalation); a changed `escalate` file queues an escalation. Returns `{park: [...], escalate:
+    [...], parked: <reason> | None}`, or None when the run has no baseline or was compared before."""
+    p = root / "runs" / rid / "tripwire.yaml"
+    if not p.exists():
+        return None
+    base = store.read_yaml(p)
+    if base.get("compared"):
+        return None
+    changed = {}
+    for name in LISTS:
+        changed[name] = []
+        for path, before in (base.get(name) or {}).items():
+            try:
+                now = _digest(path)
+            except OSError:
+                now = "unreadable"  # cannot be read now: counts as changed
+            if now != before:
+                changed[name].append(path)
+    base["compared"] = store.now()
+    store.write_yaml(p, base)
+    parked = None
+    if changed["park"]:
+        reason = f"tripwire: {', '.join(changed['park'])} changed during {rid}"
+        t = store.load_ticket(root, tid)
+        if t["status"] in ("parked", "closed"):
+            store.log_event(root, "escalation.queued", ticket=tid, run=rid, items=[reason])
+        else:
+            store.park_ticket(root, t, reason, [rid], by="tripwire")
+            parked = reason
+    if changed["escalate"]:
+        item = f"tripwire (escalate): {', '.join(changed['escalate'])} changed during {rid}"
+        store.log_event(root, "escalation.queued", ticket=tid, run=rid, items=[item])
+    if changed["park"] or changed["escalate"]:
+        store.log_event(root, "tripwire.changed", ticket=tid, run=rid, **changed)
+    return {**changed, "parked": parked}
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index 4ece3ff..9219d8b 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -105,6 +105,8 @@ async function runRole(role, ticket, phase) {
     : await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
   if (role === 'reviewer' || role === 'verifier') await clerk(`${BIN} run cleanup ${runId}`, phase, `run cleanup ${role}`)
   if (!fin.ok) { await park(ticket, `harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
+  // run finish parked the ticket (the tripwire saw a listed live file change): stop, do not route on STATUS
+  if (fin.parked) { log(`${ticket} parked: ${fin.parked}`); return null }
   log(`${role} ${runId} (${ticket}): ${fin.status}`)
   return { runId, status: fin.status, outputPath }
 }
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index b145f46..0ca3158 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -106,6 +106,8 @@ async function runRole(role, phase) {
     ? await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (killed)`)
     : await clerk(`${BIN} run finish ${runId}`, phase, `run finish ${role}`)
   if (!fin.ok) { await park(`harness-bug: run finish ${role}: ${fin.stderr || ''}`, [runId], phase); return null }
+  // run finish parked the ticket (the tripwire saw a listed live file change): stop, do not route on STATUS
+  if (fin.parked) { log(`${TICKET} parked: ${fin.parked}`); return null }
   log(`${role} ${runId}: ${fin.status}${fin.escalations && fin.escalations.length ? ` (+${fin.escalations.length} escalations)` : ''}`)
   return { runId, status: fin.status, escalations: fin.escalations || [] }
 }
diff --git a/tests/factory/test_tripwire.py b/tests/factory/test_tripwire.py
new file mode 100644
index 0000000..fd6467f
--- /dev/null
+++ b/tests/factory/test_tripwire.py
@@ -0,0 +1,238 @@
+"""The tripwire on live files (issue #38): an instance's `tripwire` lists files outside the repo;
+`run start` hashes each into a git-ignored baseline, and the run is compared once, when it leaves
+the in-flight list (`run finish`, killed runs included, or a `ticket set` that drops it). A changed
+`park` file parks the ticket; a changed `escalate` file queues an escalation. Nothing prints a
+file's contents.
+
+Black-box through `bin/factory`, each case on a throwaway store (FACTORY_STATE) and a copy of the
+suite's fixture instance (FACTORY_INSTANCE) with a `tripwire` key appended. Every listed file that
+exists lives under tmp_path.
+"""
+from __future__ import annotations
+
+import hashlib
+import json
+import os
+import pwd
+import shutil
+import subprocess
+import uuid
+from pathlib import Path
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+FIXTURE_INSTANCE = Path(__file__).resolve().parent / "fixtures" / "instance"
+SECRET = '{"token": "TRIPWIRE-SECRET-A"}\n'
+OUT = "Type: bug\nTitle: Fixture\n\nSTATUS: ACCEPT\nCONFIDENCE: high\nESCALATIONS: none\n"
+
+
+class Inst:
+    """A scratch instance and store with ticket T-0001 ready for triage. `tripwire` is the YAML
+    text appended to the instance (None: no key)."""
+
+    def __init__(self, tmp_path: Path, tripwire: str | None):
+        self.tmp = tmp_path
+        self.store = tmp_path / "store"
+        inst = tmp_path / "inst"
+        shutil.copytree(FIXTURE_INSTANCE, inst)
+        if tripwire is not None:
+            with (inst / "instance.yaml").open("a", encoding="utf-8") as f:
+                f.write(tripwire + "\n")
+        self.env = {**os.environ, "FACTORY_STATE": str(self.store), "FACTORY_INSTANCE": str(inst),
+                    "PYTHONDONTWRITEBYTECODE": "1"}
+        req = tmp_path / "req.md"
+        req.write_text("# Fixture\n\nDo the thing.\n")
+        self.ok("ticket", "new", "--file", str(req))
+        (tmp_path / "out.md").write_text(OUT)
+
+    def cli(self, *argv: str) -> subprocess.CompletedProcess:
+        return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=self.env, cwd=REPO)
+
+    def ok(self, *argv: str) -> dict:
+        cp = self.cli(*argv)
+        assert cp.returncode == 0, cp.stderr
+        return json.loads(cp.stdout.strip().splitlines()[-1])
+
+    def start(self) -> str:
+        return self.ok("run", "start", "--role", "triage", "--ticket", "T-0001")["run_id"]
+
+    def finish(self, rid: str, *extra: str) -> dict:
+        return self.ok("run", "finish", rid, *(extra or ("--output-file", str(self.tmp / "out.md"))))
+
+    def ticket(self) -> dict:
+        return self.ok("ticket", "show", "T-0001", "--json")
+
+    def events(self, name: str) -> list[dict]:
+        cp = self.cli("log", "tail", "-n", "1000", "--event", name)
+        return [json.loads(ln) for ln in cp.stdout.splitlines() if ln.strip()]
+
+    def store_text(self) -> str:
+        return "".join(p.read_text(encoding="utf-8", errors="replace") for p in self.store.rglob("*") if p.is_file())
+
+
+def live(tmp_path: Path) -> tuple[Inst, Path, Path, Path]:
+    """The fixture of the spec's scenarios: park [policies.json, new.json], escalate [pairing.json],
+    policies.json and pairing.json present, new.json absent."""
+    d = tmp_path / "live"
+    d.mkdir()
+    pol, new, pair = d / "policies.json", d / "new.json", d / "pairing.json"
+    pol.write_text(SECRET)
+    pair.write_text('{"chat": "TRIPWIRE-SECRET-B"}\n')
+    return Inst(tmp_path, f"tripwire:\n  park: [{pol}, {new}]\n  escalate: [{pair}]"), pol, new, pair
+
+
+def test_a_changed_park_file_parks_the_ticket_and_prints_no_contents(tmp_path):
+    f, pol, _, _ = live(tmp_path)
+    rid = f.start()
+    pol.write_text('{"token": "TRIPWIRE-SECRET-C"}\n')
+    cp = f.cli("run", "finish", rid, "--output-file", str(tmp_path / "out.md"))
+    assert cp.returncode == 0, cp.stderr
+    reason = f"tripwire: {pol} changed during {rid}"
+    fin = json.loads(cp.stdout.strip().splitlines()[-1])
+    assert fin["tripwire"] == {"park": [str(pol)], "escalate": []}
+    assert fin["parked"] == reason
+    t = f.ticket()
+    assert t["state"] == "parked" and t["parked"]["reason"] == reason and t["parked"]["outputs"] == [rid]
+    assert [e["items"] for e in f.events("escalation.queued")] == [[reason]]
+    changed = f.events("tripwire.changed")
+    assert [(e["run"], e["park"], e["escalate"]) for e in changed] == [(rid, [str(pol)], [])]
+    assert "TRIPWIRE-SECRET" not in cp.stdout + cp.stderr + f.store_text()
+
+
+def test_a_deleted_and_a_created_park_file_both_count_as_changed(tmp_path):
+    f, pol, new, _ = live(tmp_path)
+    rid = f.start()
+    pol.unlink()
+    new.write_text("{}\n")
+    f.finish(rid)
+    assert f.ticket()["parked"]["reason"] == f"tripwire: {pol}, {new} changed during {rid}"
+
+
+def test_a_killed_run_is_still_compared(tmp_path):
+    f, pol, _, _ = live(tmp_path)
+    rid = f.start()
+    pol.write_text("x\n")
+    fin = f.finish(rid, "--status-override", "KILLED")
+    assert fin["status"] == "KILLED" and fin["parked"] == f"tripwire: {pol} changed during {rid}"
+    assert f.ticket()["state"] == "parked"
+
+
+def test_a_changed_escalate_file_is_queued_and_the_ticket_still_moves(tmp_path):
+    f, _, _, pair = live(tmp_path)
+    rid = f.start()
+    pair.write_text('{"chat": "TRIPWIRE-SECRET-D"}\n')
+    fin = f.finish(rid)
+    assert fin["tripwire"] == {"park": [], "escalate": [str(pair)]} and "parked" not in fin
+    assert f.ticket()["state"] == "ready-for-triage"
+    queued = f.events("escalation.queued")
+    assert [(e["run"], e["items"]) for e in queued] == [(rid, [f"tripwire (escalate): {pair} changed during {rid}"])]
+    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+    assert "TRIPWIRE-SECRET" not in f.store_text()
+
+
+def test_unchanged_files_neither_park_nor_escalate(tmp_path):
+    f, _, _, _ = live(tmp_path)
+    fin = f.finish(f.start())
+    assert fin["status"] == "ACCEPT" and fin["tripwire"] == {"park": [], "escalate": []} and "parked" not in fin
+    assert f.ticket()["state"] == "ready-for-triage"
+    assert f.events("escalation.queued") == [] and f.events("tripwire.changed") == []
+
+
+def test_a_park_change_on_a_ticket_already_parked_is_queued_not_parked_again(tmp_path):
+    f, pol, _, _ = live(tmp_path)
+    rid = f.start()
+    f.ok("ticket", "park", "T-0001", "--reason", "operator hold")
+    pol.write_text("x\n")
+    fin = f.finish(rid)
+    assert "parked" not in fin and fin["tripwire"]["park"] == [str(pol)]
+    assert f.ticket()["parked"]["reason"] == "operator hold"
+    reason = f"tripwire: {pol} changed during {rid}"
+    assert [e["items"] for e in f.events("escalation.queued")] == [["operator hold"], [reason]]
+    assert len(f.events("ticket.parked")) == 1
+
+
+def test_ticket_set_compares_a_dropped_run_and_not_one_still_in_flight(tmp_path):
+    f, pol, _, _ = live(tmp_path)
+    rid = f.start()
+    pol.write_text("x\n")
+    f.ok("ticket", "set", "T-0001", "title=Renamed")
+    assert f.ticket()["state"] == "ready-for-triage" and f.events("tripwire.changed") == []
+    out = f.ok("ticket", "set", "T-0001", "in_flight=[]")
+    reason = f"tripwire: {pol} changed during {rid}"
+    assert out["parked"] == reason
+    assert f.ticket()["parked"]["reason"] == reason
+    # compared once: a later run finish of the same run does not compare it again
+    f.ok("ticket", "transition", "T-0001", "--to", "ready-for-triage", "--by", "t")
+    pol.write_text("y\n")
+    assert "parked" not in f.finish(rid)
+    assert f.ticket()["state"] == "ready-for-triage" and len(f.events("tripwire.changed")) == 1
+
+
+def test_a_home_entry_resolves_against_the_account_home_not_HOME(tmp_path):
+    name = f".tripwire-probe-{uuid.uuid4().hex}"
+    account = Path(pwd.getpwuid(os.getuid()).pw_dir) / name
+    assert not account.exists()  # never list a real file under the account's home
+    home = tmp_path / "home"
+    home.mkdir()
+    (home / name).write_text("a\n")
+    other = tmp_path / "live.json"
+    other.write_text("a\n")
+    f = Inst(tmp_path, f'tripwire: {{park: ["~/{name}", {other}]}}')
+    f.env["HOME"] = str(home)
+    rid = f.start()
+    base = (f.store / "runs" / rid / "tripwire.yaml").read_text()
+    assert str(account) in base and str(home) not in base
+    (home / name).write_text("b\n")
+    other.write_text("b\n")
+    f.finish(rid, "--status-override", "KILLED")
+    assert f.ticket()["parked"]["reason"] == f"tripwire: {other} changed during {rid}"
+    assert not account.exists()
+
+
+def test_a_directory_refuses_run_start_and_records_no_run(tmp_path):
+    d = tmp_path / "live"
+    d.mkdir()
+    f = Inst(tmp_path, f"tripwire: {{park: [{d}]}}")
+    cp = f.cli("run", "start", "--role", "triage", "--ticket", "T-0001")
+    assert cp.returncode == 2 and str(d) in cp.stderr and "tripwire" in cp.stderr
+    assert not (f.store / "runs").exists() or not any((f.store / "runs").iterdir())
+    assert f.ticket()["in_flight"] == []
+
+
+def test_a_bad_list_refuses_run_start(tmp_path):
+    for i, bad in enumerate(["tripwire: {park: [relative/file.json]}", "tripwire: {watch: []}",
+                             "tripwire: [a]", "tripwire: {park: [1]}"]):
+        (tmp_path / str(i)).mkdir()
+        f = Inst(tmp_path / str(i), bad)
+        cp = f.cli("run", "start", "--role", "triage", "--ticket", "T-0001")
+        assert cp.returncode == 2 and "tripwire" in cp.stderr, (bad, cp.stderr)
+        assert not (f.store / "runs").exists() or not any((f.store / "runs").iterdir())
+
+
+def test_the_baseline_is_kept_once_and_never_committed(tmp_path):
+    f, _, _, _ = live(tmp_path)
+    f.start()
+    digest = hashlib.sha256(SECRET.encode()).hexdigest()
+    holders = [p for p in f.store.rglob("*") if p.is_file() and digest in p.read_text(errors="replace")]
+    assert [p.name for p in holders] == ["tripwire.yaml"]
+    subprocess.run(["git", "-C", str(f.store), "init", "-q"], check=True)
+    subprocess.run(["git", "-C", str(f.store), "add", "-A"], check=True)
+    staged = subprocess.run(["git", "-C", str(f.store), "grep", "--cached", "-l", digest],
+                            capture_output=True, text=True)
+    assert staged.stdout == ""
+
+
+def test_no_tripwire_key_writes_and_prints_what_it_did_before(tmp_path):
+    f = Inst(tmp_path, None)
+    rid = f.start()
+    fin = f.finish(rid)
+    assert sorted(fin) == ["confidence", "escalations", "ok", "run_id", "status"]
+    assert sorted(p.name for p in (f.store / "runs" / rid).iterdir()) == ["meta.yaml", "output.md", "system-prompt.txt"]
+    assert not (f.store / ".gitignore").exists()
+
+
+def test_empty_lists_are_off(tmp_path):
+    f = Inst(tmp_path, "tripwire: {park: [], escalate: []}")
+    rid = f.start()
+    assert "tripwire" not in f.finish(rid)
+    assert not (f.store / "runs" / rid / "tripwire.yaml").exists()
