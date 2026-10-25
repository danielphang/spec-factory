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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0583-implementer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0583-implementer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0056.2` (branch `factory/T-0056.2`, base `b863e4ec2b2c147e6133e73fc9ba5d50f2b6f494`, head `b863e4ec2b2c147e6133e73fc9ba5d50f2b6f494`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`; `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`

## Sub-ticket T-0056.2

## T-0056.2 / The scorecard and its records: `factory stats --scorecard`, `factory escape add`, `factory intervention add`
Depends on: T-0056.1
Parallel-safe: no (edits `factory/cli.py` and `README.md`, which T-0056.1 also edits)

Parent: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0056/v3.md` (T-0056, approved v3). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope:
- B1: `escape_add` in `factory/human.py` and its parser in `cli.py`: `factory escape add TICKET --issue TEXT [--note TEXT]`, its five refusals (exit 2, nothing written), one `escape.recorded` event holding `issue_sha256` and never the `--issue` text, and the printed `{"ok": true, "id": …, "issue_sha256": …}`.
- B2: `intervention_add` in `factory/human.py` and its parser: `factory intervention add --kind WORD [--ticket TICKET] [--note TEXT]`, its two refusals, and one `intervention.recorded` event.
- Neither command joins the live-store fence's read-only list. `human.py` gains no top-level name other than these two.
- C1 to C4: the scorecard in `factory/stats.py` and `--scorecard` on the `stats` parser. Sections A to D and `report()` do not change.
- D, the rest, in a new test file (for example `tests/factory/test_scorecard.py`): the fixture's figures in both windows and both kinds, with and without transcripts; both C1 refusals; that `--scorecard` writes nothing; B1's five refusals, its event, and that the `--issue` text appears nowhere under the store; B2's event and its two refusals; and the fence refusing an unmarked `escape add` while a run is in flight on an instance's own store, reusing the existing live-store-guard test helpers.
- E2: the **Escape** and **Intervene** rows in "Where a human decides", after the **Record** row.
- E4: **The scorecard.** paragraph and its table, after the paragraph that ends `the column can undercount.`
- E5: the Built entry "The scorecard, escapes and workflow token records.", after the entry that begins "- **Counting catch and cost, `factory stats`.**". It names `run finish --transcripts`, which T-0056.1 built.
- E6: bump the status header's date to the merge date, and add the `target_is_factory` comment block to `factory/instance.template.yaml` after `# effort: {critic: high}`.

Acceptance (base: the integration branch with T-0056.1 merged). Same setup as the parent: repository root, after `uv sync --frozen`, `git` and `node` on `PATH`, each WHEN in a subshell through the briefing's wrapper.
- NEW: The scorecard gives each instance's measures for the window and the window before, and writes nothing (factory-stats). GIVEN: the `t0056-fixture.sh` block of this scenario in the parent spec, run once at column 0. The next two scenarios reuse it.
  - WHEN `(. ${TMPDIR:-/tmp}/t0056-fixture.sh && O=$(mktemp) && S0=$(find $F -type f -exec cksum {} + | sort | cksum); bin/factory stats --scorecard --store $F/fw/.factory/store --store $F/tg/.factory/store --since 2026-10-08 --until 2026-10-15 > $O 2>&1; echo "exit=$? store=$([ "$(find $F -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)"; grep -E '^(## |\| )' $O | grep -vE '^\|(---\|)+$')`
  - THEN it prints exactly these 25 lines, one per line: `exit=0 store=unchanged`, `## fw: factory work`, `| measure | 2026-10-01 to 2026-10-08 | 2026-10-08 to 2026-10-15 |`, `| Factory work merged | 0 | 1 |`, `| Escapes | 0 | 0 |`, `| Operator decisions and interventions per change | - | 0.0 |`, `| … CLI decisions | 0 | 0 |`, `| … interventions | 0 | 0 |`, `| Tokens and wall time per change: wall time, median (range) | - | 0.5 h (0.5 to 0.5 h) |`, `| … tokens, median (changes whose every run has tokens) | - (0 of 0) | - (0 of 1) |`, `| … runs with tokens from a record, a transcript or neither | record 0, transcript 0, none 0 | record 0, transcript 0, none 1 |`, `| … USD on the records that carry dollars | 0.00 (0 runs) | 0.00 (0 runs) |`, `| Lead time, median (range) | - | 12.0 h (12.0 to 12.0 h) |`, `## tg: target changes`, `| measure | 2026-10-01 to 2026-10-08 | 2026-10-08 to 2026-10-15 |`, `| Target changes merged | 1 | 2 |`, `| Escapes | 0 | 1 (T-0002) |`, `| Operator decisions and interventions per change | 2.0 | 3.0 |`, `| … CLI decisions | 2 | 3 |`, `| … interventions | 0 | 3 |`, `| Tokens and wall time per change: wall time, median (range) | 1.0 h (1.0 to 1.0 h) | 2.2 h (0.9 to 3.5 h) |`, `| … tokens, median (changes whose every run has tokens) | 450 (1 of 1) | 1200 (1 of 2) |`, `| … runs with tokens from a record, a transcript or neither | record 2, transcript 0, none 0 | record 4, transcript 0, none 2 |`, `| … USD on the records that carry dollars | 3.00 (2 runs) | 0.75 (2 runs) |`, `| Lead time, median (range) | 36.0 h (36.0 to 36.0 h) | 30.0 h (6.0 to 54.0 h) |`
- NEW: The scorecard takes a run's tokens from its transcript when the run has no cost record (factory-stats).
  - WHEN `(. ${TMPDIR:-/tmp}/t0056-fixture.sh && bin/factory stats --scorecard --store $F/fw/.factory/store --store $F/tg/.factory/store --since 2026-10-08 --until 2026-10-15 --transcripts $F/tx 2>&1 | sed -n '/^## tg:/,$p' | grep -E '^\| … (tokens|runs)[ ,]')`
  - THEN it prints exactly these two lines, one per line: `| … tokens, median (changes whose every run has tokens) | 450 (1 of 1) | 3890 (2 of 2) |`, `| … runs with tokens from a record, a transcript or neither | record 2, transcript 0, none 0 | record 4, transcript 2, none 0 |`
- NEW: The scorecard refuses a missing --since and a malformed target_is_factory (factory-stats).
  - WHEN `(. ${TMPDIR:-/tmp}/t0056-fixture.sh && bin/factory stats --scorecard --store $F/tg/.factory/store > /dev/null 2> $F/e1; a=$?; echo 'target_is_factory: maybe' >> $F/tg/.factory/instance.yaml; bin/factory stats --scorecard --store $F/tg/.factory/store --since 2026-10-08 > /dev/null 2> $F/e2; b=$?; bin/factory stats --scorecard --store $F/fw/.factory/store --since 2026-10-08 > /dev/null 2>&1; c=$?; echo "no-since=$a $(grep -c -- '--since' $F/e1) bad-setting=$b $(grep -c 'target_is_factory' $F/e2) good=$c")`
  - THEN it prints exactly `no-since=2 1 bad-setting=2 1 good=0`
- REGRESSION: Without --scorecard, stats prints sections A to D and no scorecard (factory-stats). GIVEN: the `t0043-fixture.sh` block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" in `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/factory-stats/spec.md`, run once.
  - WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 | grep '^## ')`
  - THEN it prints exactly these four lines, one per line: `## A. Runs and verdicts by role and model`, `## B. Where tickets stop`, `## C. Where spec defects were caught and where they came from`, `## D. What each role costs`
- NEW: An escape is recorded against a merged change, its link kept only as a hash, and counted by the scorecard (factory-stats).
  - WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; L=https://tracker.example/9; H=$(.venv/bin/python -c 'import hashlib, sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest())' $L); printf '# F\n\nDo x.\n' > $T/r1.md && printf '# G\n\nDo y.\n' > $T/r2.md && bin/factory ticket new --file $T/r1.md >/dev/null && bin/factory ticket new --file $T/r2.md >/dev/null && printf '%s\n' '{"ts": "2026-10-02T00:00:00+00:00", "event": "merge.done", "ticket": "T-0001.1"}' '{"ts": "2026-10-02T00:00:02+00:00", "event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}' > $FACTORY_STATE/log/fixture.jsonl; n() { cat $FACTORY_STATE/log/*.jsonl | grep -c .; }; S0=$(n); bin/factory escape add T-0002 --issue $L >/dev/null 2>&1; a=$?; bin/factory escape add T-0001.1 --issue $L >/dev/null 2>&1; b=$?; bin/factory escape add T-0009 --issue $L >/dev/null 2>&1; c=$?; bin/factory escape add T-0001 --issue '' >/dev/null 2>&1; e=$?; bin/factory escape add T-0001 --issue $L --note "see $L" >/dev/null 2>&1; f=$?; S1=$(n); bin/factory escape add T-0001 --issue $L --note 'needed a fix' > $T/out 2>&1; d=$?; echo "no-merge=$a sub-ticket=$b unknown=$c empty=$e link-note=$f refused-wrote=$((S1 - S0)) recorded=$d printed=$(grep -c $H $T/out)/$(grep -c tracker.example $T/out) link-in-store=$(grep -rl tracker.example $FACTORY_STATE | grep -c .)"; .venv/bin/python -c 'import glob, json, sys; es = [e for f in sorted(glob.glob(sys.argv[1] + "/log/*.jsonl")) for e in map(json.loads, filter(str.strip, open(f))) if e["event"] == "escape.recorded"]; print("events=%d" % len(es), "fields=" + ",".join(sorted(k for e in es for k in e if k not in ("ts", "event"))), "hash=" + ("match" if [e.get("issue_sha256") for e in es] == [sys.argv[2]] else "differ"))' $FACTORY_STATE $H; bin/factory stats --scorecard --store $FACTORY_STATE --since 2026-10-01 2>&1 | grep '^| Escapes |')`
  - THEN it prints exactly three lines: `no-merge=2 sub-ticket=2 unknown=2 empty=2 link-note=2 refused-wrote=0 recorded=0 printed=1/0 link-in-store=0`, then `events=1 fields=by,issue_sha256,note,ticket hash=match`, then `| Escapes | 0 | 1 (T-0001) |`
- NEW: An intervention recorded outside the CLI is counted by the scorecard (factory-stats).
  - WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && printf '%s\n' '{"ts": "2026-10-02T00:00:00+00:00", "event": "merge.done", "ticket": "T-0001.1"}' '{"ts": "2026-10-02T00:00:02+00:00", "event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}' > $FACTORY_STATE/log/fixture.jsonl; bin/factory intervention add --kind commit --ticket T-0009 >/dev/null 2>&1; a=$?; bin/factory intervention add --kind commit --ticket T-0001 --note 'hand commit to the gate config' >/dev/null 2>&1; b=$?; echo "unknown=$a recorded=$b"; bin/factory stats --scorecard --store $FACTORY_STATE --since 2026-10-01 2>&1 | grep '^| … interventions |')`
  - THEN it prints exactly two lines: `unknown=2 recorded=0`, then `| … interventions | 0 | 1 |`
- NEW: README and the instance template describe the scorecard, the two records and the token record (harness-docs, ADDED). After the sibling's merge, `record`, `old`, `depends` and `pieces` already print as wanted, but `scorecard`, `setting`, `escape`, `hash`, `intervene`, `template` and `built` do not, so the scenario fails on this base.
  - WHEN `(r=README.md; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; C=$(sed -n '/^### Counting what each role catches and costs/,/^## /p' $r); H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' $r); D=$(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r); echo "scorecard=$(y $(printf '%s\n' "$C" | grep -c -- '--scorecard')) setting=$(y $(printf '%s\n' "$C" | grep -c 'target_is_factory')) escape=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'factory escape add')) hash=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'SHA-256')) intervene=$(y $(printf '%s\n' "$H" | grep '^| \*\*Intervene\*\* |' | grep -c 'factory intervention add')) record=$(y $(printf '%s\n' "$C" | tr '\n' ' ' | grep -c 'run finish --transcripts')) old=$(y $(grep -c 'Any other run has its tokens only in the transcript' $r)) depends=$(y $(printf '%s\n' "$D" | grep '^| ' | grep -c 'run finish --transcripts')) pieces=$(y $(printf '%s\n' "$D" | grep -c 'Six pieces assume Claude Code')) template=$(y $(grep -c 'target_is_factory' factory/instance.template.yaml))"; awk -v h='- **The scorecard, escapes and workflow token records.**' 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' $r | awk '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=3 && index(t,"Counting what each role catches") && index(t,"Not yet run on a real store")) ? "built=pointer" : "built=long")}')`
  - THEN it prints exactly `scorecard=yes setting=yes escape=yes hash=yes intervene=yes record=yes old=no depends=yes pieces=yes template=yes`, then `built=pointer`
- REGRESSION: The drift checks live in factory/drift.py (harness-code).
  - WHEN `uv run --frozen python -B -c 'import factory.drift' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/drift.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  - THEN it prints exactly `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`
- REGRESSION: The shared helpers and the live-store fence live in factory/common.py (harness-code).
  - WHEN `uv run --frozen python -B -c 'import factory.common' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/common.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  - THEN it prints exactly `_add_spec_version _in_flight _integration_head _rel fence out`
- REGRESSION: Instance and store setup live in factory/setup.py (harness-code).
  - WHEN `uv run --frozen python -B -c 'import factory.setup' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/setup.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  - THEN it prints exactly `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`
- REGRESSION: The gates live in factory/gates.py (harness-code).
  - WHEN `uv run --frozen python -B -c 'import factory.gates' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/gates.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  - THEN it prints exactly `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`
- NEW: The human decisions live in factory/human.py (harness-code).
  - WHEN `uv run --frozen python -B -c 'import factory.human' && grep -oE '^(def [A-Za-z_]+|[A-Z_]+ =)' factory/human.py | sed 's/^def //; s/ =$//' | LC_ALL=C sort | paste -sd' ' -`
  - THEN it prints exactly `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add escape_add intervention_add request_changes resolve spec_amend`
- REGRESSION: factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines (harness-code).
  - WHEN `echo "$(wc -l < factory/cli.py | tr -d ' ') $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"`
  - THEN it prints two numbers: the first below 900, the second `3`
- Intermediate, REGRESSION: README is at most 1,225 lines, and its whitespace check passes (harness-docs, MODIFIED; this sub-ticket adds most of the change's README lines).
  - WHEN `(E=$(git hash-object -t tree /dev/null); echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')"; git diff --check $E HEAD -- README.md docs/changelog.md >/dev/null; echo "check=$?")`
  - THEN it prints exactly `readme=within`, then `check=0`
- Intermediate, REGRESSION: the change as a whole adds at most 30 lines net to README, from 1,184 (design part E).
  - WHEN `(echo "net=$(wc -l < README.md | awk '{print ($1 <= 1214 ? "within" : "over")}')")`
  - THEN it prints exactly `net=within`
- Intermediate, REGRESSION: run finish records the transcript's tokens for a run with no reply, and keeps a reply's record (build-dispatch; this sub-ticket edits the `cli.py` parser that `run finish` shares).
  - WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; X=$T/cc/projects; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; st() { bin/factory run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'; }; u() { printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "[Workflow harness — computed task] Your entire input is the file %s/runs/%s/input.md"}}\n' $1 $FACTORY_STATE $2; }; a() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": %s, "output_tokens": %s}}}\n' "$@"; }; now() { date -u +%Y-%m-%dT%H:%M:%SZ; }; out() { printf 'Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\nSTATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n' > $FACTORY_STATE/runs/$1/output.md; }; show() { .venv/bin/python -c 'import sys, yaml; c = yaml.safe_load(open(sys.argv[1])).get("claude"); u = (c or {}).get("usage") or {}; print("none" if c is None else " ".join(str(v) for v in [c.get("source"), c.get("session_id"), c.get("total_cost_usd")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")] + [str(c.get("transcript") or "-").rsplit("/", 1)[-1]]))' $FACTORY_STATE/runs/$1/meta.yaml; }; R1=$(st); mkdir -p $X/p/s/subagents/workflows/wf; t=$(now); { u $t $R1; a $t m1 5 100 0 3; a $t m1 5 100 0 3; a $t m2 1 200 4 10; } > $X/p/s/subagents/workflows/wf/agent-1.jsonl; { u $t run-9999-triage; a $t m3 1000 0 0 1000; } > $X/p/s/agent-2.jsonl; { u 2026-01-01T00:00:00Z $R1; a 2026-01-01T00:00:00Z m4 1000 0 0 1000; } > $X/p/old.jsonl; out $R1; bin/factory run finish $R1 --transcripts $X >/dev/null 2>&1; f1=$?; R2=$(st); t=$(now); { u $t $R2; a $t m5 1000 0 0 1000; } > $X/p/s/agent-3.jsonl; printf '{"session_id": "s2", "total_cost_usd": 0.5, "num_turns": 2, "usage": {"input_tokens": 1, "output_tokens": 2}}\n' > $T/reply.json; out $R2; bin/factory run finish $R2 --reply $T/reply.json --transcripts $X >/dev/null 2>&1; f2=$?; echo "finish=$f1 $f2"; show $R1; show $R2; bin/factory stats --store $FACTORY_STATE | grep '^| triage |' | grep -o 'record [0-9]*, transcript [0-9]*, none [0-9]*')`
  - THEN it prints exactly four lines: `finish=0 0`, then `transcript None None 6 300 4 13 agent-1.jsonl`, then `None s2 0.5 1 None None 2 -`, then `record 2, transcript 0, none 0`
- Intermediate, REGRESSION: the harness suite passes and one run finishes in under three minutes (current truth, harness-suite): `uv run --frozen pytest -q -p no:cacheprovider tests/factory` through the wrapper exits 0.

Interim tests: none
Tests to change: none
Protected paths: `factory/**` (`factory/human.py`, `factory/cli.py`, `factory/stats.py`, `factory/instance.template.yaml`)
Out of scope: part A (the transcript record, `run finish --transcripts`, the scripts and the driver), which the dependency already merged; README E1 and E3; the live-store fence's read-only list; sections A to D of `factory stats`; the operator steps (adding `target_is_factory: true` to this repository's `.factory/instance.yaml` is the operator's, after the merge).

## Shared plan context (from the plan; applies to every sub-ticket)

The approved spec (v3) already names its split: design.md, heading "Size and seams", gives S1 (the token record) and S2 (the scorecard and its records), with S2 depending on S1. This plan follows those seams exactly and adds no third sub-ticket. Both edit `factory/cli.py` and `README.md`, so they run one after the other.

Two shared budgets cross the seam, and the spec sets each only for the whole change:
- `factory/cli.py` may grow by at most 19 lines across parts A, B and C (880 lines today; it must stay under 900). T-0056.1 uses part of that for A2's flag; T-0056.2 gets the rest.
- `README.md` may grow by at most 30 lines net across the change, from 1,184 (so at most 1,214 lines after both). E1 and E3 add about 5; E2, E4, E5 and E6 add the rest.

## Parent spec (v3, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0056/v3.md`

=== proposal.md
## Problem

The operator cannot read from the factory's own records whether the factory is doing its job. The factory is an AI pipeline: a written request becomes a ticket, AI roles (triage, a spec writer, an implementer, reviewers) each do one job on it in a "run", and the result is merged code. The factory keeps every ticket, run and decision in its store, a folder of files on a git branch of its own. The north star, `docs/north-star.md`, is the page that says what the factory is for, and it names five numbers to watch at a review every two weeks: changes merged into the product, escapes (merged changes that later needed a fix or a revert), operator decisions and interventions per change, tokens and wall time per change, and lead time from request to merge. `factory stats`, the factory's read-only report on its store, counts what each role catches and costs, but none of those five numbers. The operator counted them once by hand, for 2026-10-03 to 2026-10-19 (`docs/reviews/2026-10-19.md`), and that count cannot be repeated cheaply or checked. The review template, `docs/reviews/TEMPLATE.md`, tells each later review to paste the scorecard from `factory stats` as printed, and `factory stats` prints none.

Three things are missing from the store, so no report can compute the numbers:
- **Escapes are not recorded anywhere.** Whether a merged change later needed a fix lives only in the operator's memory and in issue trackers, some of them private. This repository and its store are public, so a record of an escape must not carry a link to a private tracker.
- **Most runs carry no cost record.** A run started by the newer driver, `factory drive`, records the tokens and dollars its AI process used. A run started by the Workflow scripts, the original way of running the factory inside a Claude Code session, records nothing, and those are most runs: from 2026-10-08 to 2026-10-14, 23 of 26 triage runs and 64 of 66 implementer runs had no cost record.
- **Nothing says whose merges count as product work.** The factory runs on two repositories, each with its own configuration and store (together an "instance"): a port of the Nanobot chat bot, which is product work, and the factory's own code. The operator decided that the factory's changes to itself are "factory work", reported on a line of their own and never counted as product changes.

Until these exist, no later factory ticket can say which number it moves, and the review every two weeks has to be counted by hand.

## Root cause

- Escapes: unrecorded; no command or event exists.
- Cost: `run finish` takes a cost record only from a process reply (`factory/cli.py:340-341`), which only `factory/drive.py` has. The Workflow scripts' runs (`factory/workflows/intake.js:131`, `build.js:134`, and both scripts' KILLED path) and drive's stopped runs (`factory/drive.py:577`) finish with no reply, so their tokens stay only in Claude Code's transcript, which `factory stats` reads only when given `--transcripts`.
- Scorecard: `factory/stats.py` has sections A to D only, and no instance declares what its merges count as.

## Out of scope

- `factory stats` sections A to D, with or without `--transcripts`: their code, columns and current-truth scenarios stay as they are.
- Back-filling cost records for runs that already ended. The scorecard and section D still read their transcripts when given `--transcripts`.
- Dollars for a run whose record comes from a transcript. Transcripts carry none, and no estimate is recorded.
- What the baseline counted and the store cannot: merges made outside the factory, operator hours, decisions made only in chat, commands typed outside Claude Code, and the Workflow scripts' own clerk cost.
- `docs/north-star.md`, `docs/design.md`, `docs/changelog.md`, `docs/prompts/`, `agents/` and every role prompt.
- The live-store fence's read-only list (the fence is the guard that refuses a write to a store while a role run is working in it, unless the command carries the harness's own marker): the two new commands are writes and stay fenced.
- The Nanobot instance's `instance.yaml`: it needs no change, because a missing setting means target changes.
- Whether an escape has been repaired or is still open, and the baseline review's "record only" escapes. The scorecard counts changes with at least one escape record; splitting them needs a further record and a later ticket.
- Merging the four README budget checks into one requirement. This change raises the bound in each of the four that state it.

## Open questions

none. Both questions of the last round are answered (Answer 2), and the Decisions below record the answers.

## Decisions

- Interventions made outside the CLI are recorded with `factory intervention add --kind <word> [--ticket T-n] [--note "<line>"]`, which writes one `intervention.recorded` line in the store's event log, and the scorecard counts it. The operator, or a runner session (a Claude Code session that runs the factory for the operator) acting for the operator, runs it after each such action (Answer 2, question 1, option (a); standing, which means later tickets must follow it).
- The store keeps no issue link (Answer 2, question 2, option (b); standing for every later record that carries a link). `factory escape add` requires `--issue` and keeps only `issue_sha256`: the SHA-256 of the `--issue` text exactly as given, encoded as UTF-8, written as 64 lowercase hex characters. The operator matches a record to its issue by hashing the link the same way. A hash cannot be turned back into the link, but anyone who already knows or guesses the exact link can confirm a match; README says so. The command prints the hash, never the link. A `--note` on `escape add` or `intervention add` that contains `://` is refused, so the free-text note cannot carry a link either; this is the one check added beyond the answer, and it rejects only text that looks like a URL.
- The scorecard is opt-in: `factory stats --scorecard --since WHEN [--until WHEN] [--transcripts DIR]…` prints only the scorecard, so a review pastes the whole output. Without `--scorecard`, the output is byte for byte today's.
- The windows are `[--since, --until)` and the window of the same length just before it. `--until` defaults to now. `--scorecard` without `--since` is refused with exit 2.
- Each instance declares its kind with an optional `target_is_factory: true|false` in its `instance.yaml` (Answer 1, standing). Missing or false: its merges are target changes. Any other value: `stats --scorecard` refuses with exit 2. `factory stats` finds a store's instance as the nearest directory above the store that holds `.factory/instance.yaml` whose `state_dir` resolves to that store, and names its table after that directory. A store with no such instance is named by its path, its heading says "no instance found", and its merges count as target changes.
- A change is a parent ticket (an id with no `.N`) whose last `ticket.transition` to `closed` is in the window and which has at least one `merge.done` for itself or a sub-ticket. Same as the baseline.
- An escape counts against the window in which its change closed, when recorded before the report's end. A change with several escape records counts once. The row prints ticket ids, never links or notes (request part B).
- CLI decisions are `approval.recorded` and `human.resolved` events in the window. Interventions are, in the window: a `ticket.transition` whose `by` is not `workflow`, `merge`, `parent-check` or `ready-implementers` and that has no `approval.recorded` or `human.resolved` event for the same ticket within 2 seconds; a `spec.added` whose source is not a run id; a `decision.recorded` with `via: decision add`; and an `intervention.recorded` (Answer 2). Decisions and interventions per change is their sum divided by the window's changes. This stands in for hours of operator attention (T-0055's standing decision). Standing: later tickets that add a human command say which of the two it counts as.
- The row name stays T-0055's "Tokens and wall time per change", which settles triage's wording gap. Its first line is the median of each change's summed run wall time, in hours. Its sub-rows are the median tokens (context plus output) over the changes whose every run has tokens, the runs by token source, and the dollars on the records that carry them. Dollars are reported but never estimated.
- A change's runs are every finished run of the parent or its sub-tickets, killed ones included, because they took time and tokens. The baseline summed `run.finished` events only, so killed runs make this figure slightly higher than a baseline-style count.
- A run's tokens come from its cost record, else (with `--transcripts`) from the transcript section D's rule places, as section D does today.
- Lead time runs from the parent's `ticket.created` event to its last `merge.done`. The baseline started from the earliest of the request's date, the issue's creation and the ticket's creation. The store holds only the last, so this figure can be shorter than the baseline's for a request filed late.
- Root cause C is fixed where the record is written: `run finish --transcripts DIR` (repeatable) records the tokens of the run's transcript when the run has no reply usage. Both Workflow scripts pass it on every `run finish`; `factory drive` passes it on all three of its `run finish` calls. The directory is `$CLAUDE_CONFIG_DIR/projects`, else `$HOME/.claude/projects`. It is passed explicitly, never defaulted inside `run finish`, so a test with a throwaway HOME never reads the operator's transcripts.
- A transcript record is kept under the run's existing `claude:` key as `{source: transcript, transcript: <path>, usage: {input_tokens, cache_read_input_tokens, cache_creation_input_tokens, output_tokens}, total_cost_usd: null}`. Section D therefore counts it as a record with no change to its code, and its "USD from records" column covers only the records that carry dollars; README says so. A reply record keeps its exact current shape (`tests/factory/test_drive.py:167`).
- `run finish` matches a transcript by the rule section D already uses (`factory/cost.py` `match_transcripts`) for that one store and run, with no upper time bound because the run is finishing. It opens only files modified at or after the run's `started`.
- `factory escape add <ticket> --issue <link> [--note "<line>"]` writes one `escape.recorded` event, holding the hash above and no link, and nothing else. It is refused with exit 2, writing nothing, for an unknown ticket, a sub-ticket id (the message names the parent), a ticket with no `merge.done` for itself or a sub-ticket, an empty `--issue`, or a `--note` containing `://`. The ticket need not be closed yet.
- Both new commands are writes. The live-store fence refuses them unmarked while a run is in flight, as its first requirement already says for every command outside its read-only list, so live-store-guard does not change.
- `escape_add` and `intervention_add` live in `factory/human.py` beside `decision_add`, and the harness-code requirement that pins that module's names is modified to list them. Rejected: a new module, which the harness-code checks that read the five split modules would not cover.
- README's line budget rises from 1,185 to 1,225 lines in each of the four current-truth harness-docs requirements that state it (MODIFIED in this change), and this change adds at most 30 lines net to README (the draft adds 28, from 1,184). The operator approves the figure at this gate.
- No changelog entry: `docs/design.md` does not change (precedent: T-0049).
- The change is built as two sub-tickets (design.md, heading "Size and seams"), and this spec ends NEEDS-SPLIT, so the build sends it to the planner, which splits it on those seams. Either the status or the heading alone sends it there.

## Risk

Harness code changes in five places: the stats report (new read-only output only), `run finish` (a new optional flag), both Workflow scripts and the driver (one argument on every `run finish`), and two new commands. The riskiest piece is the scripts' `run finish` command. A mistake in it, such as an unescaped `${…}` inside the JavaScript template string, would fail every run finish and park every ticket as `harness-bug: run finish …`. The scenario "A run the intake script starts carries its transcript's tokens" runs the real intake script under node, and part D's suite test drives build.js the same way. A Workflow run whose transcript cannot be found records no cost, as today; nothing parks for it. `run finish` reads files under the operator's Claude Code directory, read-only; a scenario never reads the real one. The cost record's file path names the operator's home directory in the store, as run records already do for worktrees. An escape's link never reaches the store, only its hash; the residual exposure is that someone who guesses the exact link can confirm it.

Order: T-0055 has merged (`c42d167`), so nothing waits on it. README has one line left under its old cap, so the seam that first grows README carries the raised budget (design.md, heading "Size and seams").

Protected paths: `factory/**`

## Operator steps

1. After the merge, add `target_is_factory: true` to this repository's `.factory/instance.yaml` (protected), with a one-line comment, and commit it on `main`. Leave the Nanobot instance's `instance.yaml` unchanged.
2. Upgrade the runtime and accept the revision in both instances as usual (README "Upgrading the runtime"). Then write fresh launch copies with `factory launch-script intake|build` before the next Workflow run: a launch copy written earlier still calls `run finish` without `--transcripts`.
3. Check one real Workflow run and one real drive run after the upgrade: `grep -A2 '^claude:' <store>/runs/<run>/meta.yaml` shows `source: transcript` for the Workflow run and `total_cost_usd` for the drive run. The scenarios use stand-ins for Claude Code, so only this confirms where Claude Code writes transcripts on this machine.
4. Optional: record the escapes the baseline review lists, with `FACTORY_DISPATCH=1 $RUNTIME/bin/factory escape add T-n --issue <link>` in each instance. Which ones count is your call; the baseline marks some as "record only". The store keeps only each link's hash.

=== design.md
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

=== specs/factory-stats/spec.md
## ADDED Requirements

### Requirement: factory stats --scorecard reports the north star's measures for each instance, for a window and the window before
`factory stats --scorecard --since WHEN` MUST print, for each store given, a table headed by its instance's directory and kind (target changes, or factory work when the instance sets `target_is_factory: true`), with changes merged, escapes, operator decisions and interventions per change, tokens and wall time per change, and lead time, for the window and for the window of the same length before it, as design part C defines them; it SHALL write nothing, and SHALL print no store path or issue link for a store whose instance it finds.

#### Scenario: The scorecard gives each instance's measures for the window and the window before, and writes nothing
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0056-fixture.sh <<'EOF'
# Sourced from the repo root: builds two instances, $F/fw (whose instance.yaml sets target_is_factory:
# true) and $F/tg (which does not), each with its store at .factory/store, and a directory of
# transcripts, $F/tx, whose figures the t0056 scenarios state. Leaves F set.
F=$(cd "$(mktemp -d)" && pwd -P)
for i in fw tg; do mkdir -p $F/$i/.factory/store/log && printf 'state_dir: .factory/store\n' > $F/$i/.factory/instance.yaml; done
echo 'target_is_factory: true' >> $F/fw/.factory/instance.yaml
run() { d=$F/$1/.factory/store/runs/$2; mkdir -p $d && printf 'run_id: %s\nrole: %s\nticket: %s\nmodel: opus\nstarted: %s\nfinished: %s\nwall_s: %s\nstatus: %s\n' $2 ${2#run-????-} $3 "'$4'" "$5" $6 $7 > $d/meta.yaml; }
rec() { printf 'claude:\n  usage: {input_tokens: %s, cache_read_input_tokens: %s, cache_creation_input_tokens: 0, output_tokens: %s}\n  total_cost_usd: %s\n' $3 $4 $5 $6 >> $F/$1/.factory/store/runs/$2/meta.yaml; [ $6 = null ] && echo '  source: transcript' >> $F/$1/.factory/store/runs/$2/meta.yaml; true; }
ev() { s=$1; shift; printf '{"ts": "%s", "event": "%s", "ticket": "%s"%s}\n' "$@" >> $F/$s/.factory/store/log/2026-10.jsonl; }
run tg run-0001-triage T-0001 2026-10-02T00:10:00+00:00 "'2026-10-02T00:20:00+00:00'" 600 ACCEPT; rec tg run-0001-triage 100 0 50 1.00
run tg run-0002-implementer T-0001.1 2026-10-03T10:00:00+00:00 "'2026-10-03T10:50:00+00:00'" 3000 READY-FOR-REVIEW; rec tg run-0002-implementer 200 0 100 2.00
run tg run-0003-triage T-0002 2026-10-08T00:10:00+00:00 "'2026-10-08T00:40:00+00:00'" 1800 ACCEPT; rec tg run-0003-triage 1000 0 100 0.50
run tg run-0004-implementer T-0002.1 2026-10-08T10:00:00+00:00 "'2026-10-08T11:30:00+00:00'" 5400 READY-FOR-REVIEW; rec tg run-0004-implementer 2000 3000 300 null
run tg run-0005-implementer T-0002.2 2026-10-09T10:00:00+00:00 "'2026-10-09T11:00:00+00:00'" 3600 READY-FOR-REVIEW
run tg run-0006-reviewer T-0002.2 2026-10-09T12:00:00+00:00 "'2026-10-09T12:30:00+00:00'" 1800 KILLED
run tg run-0007-triage T-0003 2026-10-09T00:05:00+00:00 "'2026-10-09T00:20:00+00:00'" 900 ACCEPT; rec tg run-0007-triage 400 0 100 0.25
run tg run-0008-implementer T-0003.1 2026-10-09T03:00:00+00:00 "'2026-10-09T03:39:00+00:00'" 2340 READY-FOR-REVIEW; rec tg run-0008-implementer 500 0 200 null
run tg run-0009-critic T-0002 2026-10-08T05:00:00+00:00 null null running
run tg run-0010-triage T-0004 2026-10-08T00:00:00+00:00 "'2026-10-08T00:10:00+00:00'" 600 REJECT
run fw run-0001-implementer T-0010.1 2026-10-10T11:00:00+00:00 "'2026-10-10T11:30:00+00:00'" 1800 READY-FOR-REVIEW
ev tg 2026-10-02T00:00:00+00:00 ticket.created T-0001 ''
ev tg 2026-10-02T01:00:00+00:00 approval.recorded T-0001 ', "kind": "spec", "version": 1, "by": "op"'
ev tg 2026-10-02T01:00:01+00:00 ticket.transition T-0001 ', "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"'
ev tg 2026-10-03T00:00:00+00:00 human.resolved T-0001.1 ', "kind": "ruling", "by": "op"'
ev tg 2026-10-03T00:00:00+00:00 ticket.transition T-0001.1 ', "from": "parked", "to": "ready-for-implementer", "by": "op"'
ev tg 2026-10-03T12:00:00+00:00 merge.done T-0001.1 ''
ev tg 2026-10-03T12:00:00+00:00 ticket.transition T-0001.1 ', "from": "ready-for-merge", "to": "merged", "by": "merge"'
ev tg 2026-10-03T12:00:02+00:00 ticket.transition T-0001 ', "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"'
ev tg 2026-10-08T00:00:00+00:00 ticket.created T-0002 ''
ev tg 2026-10-08T00:00:00+00:00 ticket.created T-0004 ''
ev tg 2026-10-08T00:30:00+00:00 spec.added T-0002 ', "version": 1, "source": "run-0011-spec_writer"'
ev tg 2026-10-08T01:00:00+00:00 approval.recorded T-0002 ', "kind": "spec", "version": 1, "by": "op"'
ev tg 2026-10-08T01:00:01+00:00 ticket.transition T-0002 ', "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"'
ev tg 2026-10-08T12:00:00+00:00 ticket.transition T-0002.1 ', "from": "parked", "to": "ready-for-implementer", "by": "op"'
ev tg 2026-10-09T00:00:00+00:00 ticket.created T-0003 ''
ev tg 2026-10-09T00:00:00+00:00 merge.done T-0002.1 ''
ev tg 2026-10-09T01:00:00+00:00 spec.added T-0003 ', "version": 2, "source": "gate edit /x/T-0003-gate.md"'
ev tg 2026-10-09T01:00:00+00:00 approval.recorded T-0003 ', "kind": "spec", "version": 2, "by": "op"'
ev tg 2026-10-09T01:00:00+00:00 ticket.transition T-0003 ', "from": "awaiting-spec-gate", "to": "ready-for-planner", "by": "op"'
ev tg 2026-10-09T02:00:00+00:00 human.resolved T-0004 ', "kind": "close", "by": "op"'
ev tg 2026-10-09T02:00:01+00:00 ticket.transition T-0004 ', "from": "parked", "to": "closed", "by": "op"'
ev tg 2026-10-09T06:00:00+00:00 merge.done T-0003.1 ''
ev tg 2026-10-09T06:00:02+00:00 ticket.transition T-0003 ', "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"'
ev tg 2026-10-10T00:00:00+00:00 ticket.created T-0006 ''
ev tg 2026-10-10T06:00:00+00:00 merge.done T-0002.2 ''
ev tg 2026-10-10T06:00:02+00:00 ticket.transition T-0002 ', "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"'
ev tg 2026-10-11T00:00:00+00:00 decision.recorded T-0002 ', "by": "op", "line": "x", "via": "decision add"'
ev tg 2026-10-11T00:00:00+00:00 decision.recorded T-0003 ', "by": "op", "line": "y", "via": "resolve --answer"'
ev tg 2026-10-12T00:00:00+00:00 ticket.created T-0005 ''
ev tg 2026-10-12T00:00:00+00:00 escape.recorded T-0002 ', "issue_sha256": "0000000000000000000000000000000000000000000000000000000000000001", "by": "op"'
ev tg 2026-10-13T00:00:00+00:00 escape.recorded T-0002 ', "issue_sha256": "0000000000000000000000000000000000000000000000000000000000000002", "by": "op"'
ev tg 2026-10-14T00:00:00+00:00 merge.done T-0005.1 ''
ev tg 2026-10-16T00:00:00+00:00 escape.recorded T-0001 ', "issue_sha256": "0000000000000000000000000000000000000000000000000000000000000003", "by": "op"'
ev tg 2026-10-16T00:00:00+00:00 merge.done T-0006.1 ''
ev tg 2026-10-16T00:00:02+00:00 ticket.transition T-0006 ', "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"'
ev fw 2026-10-10T00:00:00+00:00 ticket.created T-0010 ''
ev fw 2026-10-10T12:00:00+00:00 merge.done T-0010.1 ''
ev fw 2026-10-10T12:00:01+00:00 ticket.transition T-0010 ', "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"'
tx() { mkdir -p $(dirname $F/tx/$1) && printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "[Workflow harness — computed task] Your entire input is the file %s/input.md"}}\n{"type": "assistant", "timestamp": "%s", "message": {"id": "m-%s", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": 0, "output_tokens": %s}}}\n' $2 $F/tg/.factory/store/runs/$3 $2 $3 $4 $5 $6 > $F/tx/$1; }
tx a/agent-1.jsonl 2026-10-09T10:00:05Z run-0005-implementer 10 90 20
tx b/agent-2.jsonl 2026-10-09T12:00:05Z run-0006-reviewer 5 45 10
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0056-fixture.sh && O=$(mktemp) && S0=$(find $F -type f -exec cksum {} + | sort | cksum); bin/factory stats --scorecard --store $F/fw/.factory/store --store $F/tg/.factory/store --since 2026-10-08 --until 2026-10-15 > $O 2>&1; echo "exit=$? store=$([ "$(find $F -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)"; grep -E '^(## |\| )' $O | grep -vE '^\|(---\|)+$')`
- THEN it prints exactly these 25 lines, one per line: `exit=0 store=unchanged`, `## fw: factory work`, `| measure | 2026-10-01 to 2026-10-08 | 2026-10-08 to 2026-10-15 |`, `| Factory work merged | 0 | 1 |`, `| Escapes | 0 | 0 |`, `| Operator decisions and interventions per change | - | 0.0 |`, `| … CLI decisions | 0 | 0 |`, `| … interventions | 0 | 0 |`, `| Tokens and wall time per change: wall time, median (range) | - | 0.5 h (0.5 to 0.5 h) |`, `| … tokens, median (changes whose every run has tokens) | - (0 of 0) | - (0 of 1) |`, `| … runs with tokens from a record, a transcript or neither | record 0, transcript 0, none 0 | record 0, transcript 0, none 1 |`, `| … USD on the records that carry dollars | 0.00 (0 runs) | 0.00 (0 runs) |`, `| Lead time, median (range) | - | 12.0 h (12.0 to 12.0 h) |`, `## tg: target changes`, `| measure | 2026-10-01 to 2026-10-08 | 2026-10-08 to 2026-10-15 |`, `| Target changes merged | 1 | 2 |`, `| Escapes | 0 | 1 (T-0002) |`, `| Operator decisions and interventions per change | 2.0 | 3.0 |`, `| … CLI decisions | 2 | 3 |`, `| … interventions | 0 | 3 |`, `| Tokens and wall time per change: wall time, median (range) | 1.0 h (1.0 to 1.0 h) | 2.2 h (0.9 to 3.5 h) |`, `| … tokens, median (changes whose every run has tokens) | 450 (1 of 1) | 1200 (1 of 2) |`, `| … runs with tokens from a record, a transcript or neither | record 2, transcript 0, none 0 | record 4, transcript 0, none 2 |`, `| … USD on the records that carry dollars | 3.00 (2 runs) | 0.75 (2 runs) |`, `| Lead time, median (range) | 36.0 h (36.0 to 36.0 h) | 30.0 h (6.0 to 54.0 h) |`

#### Scenario: The scorecard takes a run's tokens from its transcript when the run has no cost record
Needs the GIVEN block of "The scorecard gives each instance's measures for the window and the window before, and writes nothing" run once. Of change T-0002's four runs, two have no cost record, and `$F/tx` holds a transcript for each of those two.
- WHEN `(. ${TMPDIR:-/tmp}/t0056-fixture.sh && bin/factory stats --scorecard --store $F/fw/.factory/store --store $F/tg/.factory/store --since 2026-10-08 --until 2026-10-15 --transcripts $F/tx 2>&1 | sed -n '/^## tg:/,$p' | grep -E '^\| … (tokens|runs)[ ,]')`
- THEN it prints exactly these two lines, one per line: `| … tokens, median (changes whose every run has tokens) | 450 (1 of 1) | 3890 (2 of 2) |`, `| … runs with tokens from a record, a transcript or neither | record 2, transcript 0, none 0 | record 4, transcript 2, none 0 |`

#### Scenario: The scorecard refuses a missing --since and a malformed target_is_factory
Needs the GIVEN block of "The scorecard gives each instance's measures for the window and the window before, and writes nothing" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0056-fixture.sh && bin/factory stats --scorecard --store $F/tg/.factory/store > /dev/null 2> $F/e1; a=$?; echo 'target_is_factory: maybe' >> $F/tg/.factory/instance.yaml; bin/factory stats --scorecard --store $F/tg/.factory/store --since 2026-10-08 > /dev/null 2> $F/e2; b=$?; bin/factory stats --scorecard --store $F/fw/.factory/store --since 2026-10-08 > /dev/null 2>&1; c=$?; echo "no-since=$a $(grep -c -- '--since' $F/e1) bad-setting=$b $(grep -c 'target_is_factory' $F/e2) good=$c")`
- THEN it prints exactly `no-since=2 1 bad-setting=2 1 good=0`

### Requirement: factory stats without --scorecard prints sections A to D as before
`factory stats` without `--scorecard` MUST print the same four sections, A to D, as before this change.

#### Scenario: Without --scorecard, stats prints sections A to D and no scorecard
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" (current truth, factory-stats) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 | grep '^## ')`
- THEN it prints exactly these four lines, one per line: `## A. Runs and verdicts by role and model`, `## B. Where tickets stop`, `## C. Where spec defects were caught and where they came from`, `## D. What each role costs`

### Requirement: factory escape add records an escape against a merged change, and the scorecard counts it
`factory escape add TICKET --issue TEXT [--note TEXT]` MUST write one `escape.recorded` event for a ticket that has a merge, holding the SHA-256 hash of the `--issue` text and never the text itself, and MUST refuse with exit 2, writing nothing, an unknown ticket, a sub-ticket id, a ticket with no merge, an empty `--issue` or a `--note` that contains `://`; the scorecard SHALL count a change with an escape recorded before the report's end in the window the change closed in.

#### Scenario: An escape is recorded against a merged change, its link kept only as a hash, and counted by the scorecard
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; L=https://tracker.example/9; H=$(.venv/bin/python -c 'import hashlib, sys; print(hashlib.sha256(sys.argv[1].encode()).hexdigest())' $L); printf '# F\n\nDo x.\n' > $T/r1.md && printf '# G\n\nDo y.\n' > $T/r2.md && bin/factory ticket new --file $T/r1.md >/dev/null && bin/factory ticket new --file $T/r2.md >/dev/null && printf '%s\n' '{"ts": "2026-10-02T00:00:00+00:00", "event": "merge.done", "ticket": "T-0001.1"}' '{"ts": "2026-10-02T00:00:02+00:00", "event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}' > $FACTORY_STATE/log/fixture.jsonl; n() { cat $FACTORY_STATE/log/*.jsonl | grep -c .; }; S0=$(n); bin/factory escape add T-0002 --issue $L >/dev/null 2>&1; a=$?; bin/factory escape add T-0001.1 --issue $L >/dev/null 2>&1; b=$?; bin/factory escape add T-0009 --issue $L >/dev/null 2>&1; c=$?; bin/factory escape add T-0001 --issue '' >/dev/null 2>&1; e=$?; bin/factory escape add T-0001 --issue $L --note "see $L" >/dev/null 2>&1; f=$?; S1=$(n); bin/factory escape add T-0001 --issue $L --note 'needed a fix' > $T/out 2>&1; d=$?; echo "no-merge=$a sub-ticket=$b unknown=$c empty=$e link-note=$f refused-wrote=$((S1 - S0)) recorded=$d printed=$(grep -c $H $T/out)/$(grep -c tracker.example $T/out) link-in-store=$(grep -rl tracker.example $FACTORY_STATE | grep -c .)"; .venv/bin/python -c 'import glob, json, sys; es = [e for f in sorted(glob.glob(sys.argv[1] + "/log/*.jsonl")) for e in map(json.loads, filter(str.strip, open(f))) if e["event"] == "escape.recorded"]; print("events=%d" % len(es), "fields=" + ",".join(sorted(k for e in es for k in e if k not in ("ts", "event"))), "hash=" + ("match" if [e.get("issue_sha256") for e in es] == [sys.argv[2]] else "differ"))' $FACTORY_STATE $H; bin/factory stats --scorecard --store $FACTORY_STATE --since 2026-10-01 2>&1 | grep '^| Escapes |')`
- THEN it prints exactly three lines: `no-merge=2 sub-ticket=2 unknown=2 empty=2 link-note=2 refused-wrote=0 recorded=0 printed=1/0 link-in-store=0`, then `events=1 fields=by,issue_sha256,note,ticket hash=match`, then `| Escapes | 0 | 1 (T-0001) |`

### Requirement: factory intervention add records an intervention made outside the CLI, and the scorecard counts it
`factory intervention add --kind WORD [--ticket TICKET] [--note TEXT]` MUST write one `intervention.recorded` event, refusing with exit 2 a ticket that does not exist or a `--note` that contains `://`, and the scorecard SHALL count the event among the interventions of the window it is dated in.

#### Scenario: An intervention recorded outside the CLI is counted by the scorecard
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && printf '%s\n' '{"ts": "2026-10-02T00:00:00+00:00", "event": "merge.done", "ticket": "T-0001.1"}' '{"ts": "2026-10-02T00:00:02+00:00", "event": "ticket.transition", "ticket": "T-0001", "from": "ready-for-parent-verify", "to": "closed", "by": "workflow"}' > $FACTORY_STATE/log/fixture.jsonl; bin/factory intervention add --kind commit --ticket T-0009 >/dev/null 2>&1; a=$?; bin/factory intervention add --kind commit --ticket T-0001 --note 'hand commit to the gate config' >/dev/null 2>&1; b=$?; echo "unknown=$a recorded=$b"; bin/factory stats --scorecard --store $FACTORY_STATE --since 2026-10-01 2>&1 | grep '^| … interventions |')`
- THEN it prints exactly two lines: `unknown=2 recorded=0`, then `| … interventions | 0 | 1 |`

=== specs/build-dispatch/spec.md
## ADDED Requirements

### Requirement: run finish records a run's tokens from its transcript when the run has no reply usage
`run finish RUN --transcripts DIR` MUST record under the run's `claude:` key, with `source: transcript`, the path of the one transcript under DIR that names the run's directory and starts after the run started, its input, cache-read, cache-creation and output tokens with each message counted once, and no dollars, when the run gets no usage from `--reply`; a reply with usage SHALL be recorded as before, and a transcript naming another run or dated before the run started SHALL NOT be taken.

#### Scenario: run finish records the transcript's tokens for a run with no reply, and keeps a reply's record
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper. The first run's transcript repeats one message's record, as Claude Code writes them; beside it lie a transcript naming another run and one naming this run but dated 2026-01-01.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store; X=$T/cc/projects; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; st() { bin/factory run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'; }; u() { printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "[Workflow harness — computed task] Your entire input is the file %s/runs/%s/input.md"}}\n' $1 $FACTORY_STATE $2; }; a() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": %s, "output_tokens": %s}}}\n' "$@"; }; now() { date -u +%Y-%m-%dT%H:%M:%SZ; }; out() { printf 'Type: bug\nTitle: T\nSummary: s\nEvidence: e\nAssumptions: a\nSTATUS: ACCEPT\nCONFIDENCE: high, x\nESCALATIONS: none\n' > $FACTORY_STATE/runs/$1/output.md; }; show() { .venv/bin/python -c 'import sys, yaml; c = yaml.safe_load(open(sys.argv[1])).get("claude"); u = (c or {}).get("usage") or {}; print("none" if c is None else " ".join(str(v) for v in [c.get("source"), c.get("session_id"), c.get("total_cost_usd")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")] + [str(c.get("transcript") or "-").rsplit("/", 1)[-1]]))' $FACTORY_STATE/runs/$1/meta.yaml; }; R1=$(st); mkdir -p $X/p/s/subagents/workflows/wf; t=$(now); { u $t $R1; a $t m1 5 100 0 3; a $t m1 5 100 0 3; a $t m2 1 200 4 10; } > $X/p/s/subagents/workflows/wf/agent-1.jsonl; { u $t run-9999-triage; a $t m3 1000 0 0 1000; } > $X/p/s/agent-2.jsonl; { u 2026-01-01T00:00:00Z $R1; a 2026-01-01T00:00:00Z m4 1000 0 0 1000; } > $X/p/old.jsonl; out $R1; bin/factory run finish $R1 --transcripts $X >/dev/null 2>&1; f1=$?; R2=$(st); t=$(now); { u $t $R2; a $t m5 1000 0 0 1000; } > $X/p/s/agent-3.jsonl; printf '{"session_id": "s2", "total_cost_usd": 0.5, "num_turns": 2, "usage": {"input_tokens": 1, "output_tokens": 2}}\n' > $T/reply.json; out $R2; bin/factory run finish $R2 --reply $T/reply.json --transcripts $X >/dev/null 2>&1; f2=$?; echo "finish=$f1 $f2"; show $R1; show $R2; bin/factory stats --store $FACTORY_STATE | grep '^| triage |' | grep -o 'record [0-9]*, transcript [0-9]*, none [0-9]*')`
- THEN it prints exactly four lines: `finish=0 0`, then `transcript None None 6 300 4 13 agent-1.jsonl`, then `None s2 0.5 1 None None 2 -`, then `record 2, transcript 0, none 0`

### Requirement: A run a Workflow script starts carries its transcript's tokens
`factory/workflows/intake.js` and `factory/workflows/build.js` MUST pass `--transcripts` with the directory where Claude Code keeps transcripts (`$CLAUDE_CONFIG_DIR/projects`, else `$HOME/.claude/projects`) on every `run finish` they run, so that each run they finish records its agent's tokens.

#### Scenario: A run the intake script starts carries its transcript's tokens
- GIVEN the file written by the block below, run once at column 0 as shown

```sh
cat > ${TMPDIR:-/tmp}/t0056-wf.mjs <<'EOF'
// node t0056-wf.mjs, from the checkout under test: runs factory/workflows/intake.js on T-0001 of the
// store $FACTORY_STATE. Each clerk command runs for real (sh -c). Each role call stands in for a
// Workflow agent: it writes the role's output with STATUS NEEDS-HUMAN and, as Claude Code does, a
// transcript under $CLAUDE_CONFIG_DIR/projects whose first user message is the call's prompt and which
// records one model call: 7 input, 70 cache-read, 0 cache-creation and 3 output tokens.
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const run = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  const dir = `${process.env.CLAUDE_CONFIG_DIR}/projects/p/s/subagents/workflows/wf`
  mkdirSync(dir, { recursive: true })
  const ts = new Date().toISOString()
  n += 1
  writeFileSync(`${dir}/agent-${n}.jsonl`,
    JSON.stringify({ type: 'user', timestamp: ts, message: { role: 'user', content: `[Workflow harness — computed task] ${prompt}` } }) + '\n' +
    JSON.stringify({ type: 'assistant', timestamp: ts, message: { id: `m${n}`, usage: { input_tokens: 7, cache_read_input_tokens: 70, cache_creation_input_tokens: 0, output_tokens: 3 } } }) + '\n')
  const text = 'Question for human: which one?\nSTATUS: NEEDS-HUMAN\nCONFIDENCE: low, stub\nESCALATIONS: none\n'
  writeFileSync(`${run}/output.md`, text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, inlineRoles: true }, agent,
  () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store CLAUDE_CONFIG_DIR=$T/cc; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && node ${TMPDIR:-/tmp}/t0056-wf.mjs >/dev/null 2>&1; echo "state=$(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; for m in $FACTORY_STATE/runs/*/meta.yaml; do .venv/bin/python -c 'import sys, yaml; m = yaml.safe_load(open(sys.argv[1])); c = m.get("claude"); u = (c or {}).get("usage") or {}; print(m["role"], "none" if c is None else " ".join(str(v) for v in [c.get("source")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")]))' $m; done)`
- THEN it prints exactly two lines: `state=parked`, then `triage transcript 7 70 0 3`

### Requirement: A drive run whose process gave no usable reply carries its transcript's tokens
`factory drive` MUST pass the same transcript directory on each `run finish` it runs, so that a run whose `claude` process printed no JSON reply, or that the driver stopped, records its transcript's tokens.

#### Scenario: A drive run whose claude process failed records its transcript's tokens
- GIVEN the stand-in written by the block below, run once at column 0 as shown

```sh
mkdir -p ${TMPDIR:-/tmp}/t0056-bin && cat > ${TMPDIR:-/tmp}/t0056-bin/claude <<'EOF'
#!/bin/sh
# Stands in for a `claude` process that fails: run from a role run's directory, it writes a transcript
# under $CLAUDE_CONFIG_DIR/projects whose first user message names the run's input and which records one
# model call (2 input, 20 cache-read, 0 cache-creation, 1 output tokens), then prints no JSON and exits 1.
d=$CLAUDE_CONFIG_DIR/projects/p && mkdir -p $d && t=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "Read %s/input.md"}}\n{"type": "assistant", "timestamp": "%s", "message": {"id": "m1", "usage": {"input_tokens": 2, "cache_read_input_tokens": 20, "cache_creation_input_tokens": 0, "output_tokens": 1}}}\n' $t "$PWD" $t > $d/s1.jsonl
echo 'not json'; echo 'stand-in failure' >&2; exit 1
EOF
chmod +x ${TMPDIR:-/tmp}/t0056-bin/claude
```

- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store CLAUDE_CONFIG_DIR=$T/cc; printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null && PATH=${TMPDIR:-/tmp}/t0056-bin:$PATH bin/factory drive T-0001 --phase intake >/dev/null 2>&1; echo "state=$(bin/factory ticket show T-0001 | sed -n 's/^status: //p')"; for m in $FACTORY_STATE/runs/*/meta.yaml; do .venv/bin/python -c 'import sys, yaml; m = yaml.safe_load(open(sys.argv[1])); c = m.get("claude"); u = (c or {}).get("usage") or {}; print(m["role"], m["status"], "none" if c is None else " ".join(str(v) for v in [c.get("source")] + [u.get(k) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")]))' $m; done)`
- THEN it prints exactly two lines: `state=parked`, then `triage KILLED transcript 2 20 0 1`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the scorecard, escape and intervention records, and workflow token records
README SHALL describe `factory stats --scorecard` and `target_is_factory` in "Counting what each role catches and costs", with the run token record that `run finish --transcripts` writes in place of the claim that only driver runs carry a cost record; SHALL give `factory escape add` and `factory intervention add` their rows in "Where a human decides", the **Escape** row saying the store keeps only the link's SHA-256 hash; SHALL list the transcript record among the six pieces in "What depends on Claude Code"; and SHALL give the three a short Built entry that points to that subsection and says they have not yet run on a real store; `factory/instance.template.yaml` SHALL document `target_is_factory`.

#### Scenario: README and the instance template describe the scorecard, the two records and the token record
- WHEN `(r=README.md; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; C=$(sed -n '/^### Counting what each role catches and costs/,/^## /p' $r); H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' $r); D=$(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r); echo "scorecard=$(y $(printf '%s\n' "$C" | grep -c -- '--scorecard')) setting=$(y $(printf '%s\n' "$C" | grep -c 'target_is_factory')) escape=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'factory escape add')) hash=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'SHA-256')) intervene=$(y $(printf '%s\n' "$H" | grep '^| \*\*Intervene\*\* |' | grep -c 'factory intervention add')) record=$(y $(printf '%s\n' "$C" | tr '\n' ' ' | grep -c 'run finish --transcripts')) old=$(y $(grep -c 'Any other run has its tokens only in the transcript' $r)) depends=$(y $(printf '%s\n' "$D" | grep '^| ' | grep -c 'run finish --transcripts')) pieces=$(y $(printf '%s\n' "$D" | grep -c 'Six pieces assume Claude Code')) template=$(y $(grep -c 'target_is_factory' factory/instance.template.yaml))"; awk -v h='- **The scorecard, escapes and workflow token records.**' 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' $r | awk '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=3 && index(t,"Counting what each role catches") && index(t,"Not yet run on a real store")) ? "built=pointer" : "built=long")}')`
- THEN it prints exactly `scorecard=yes setting=yes escape=yes hash=yes intervene=yes record=yes old=no depends=yes pieces=yes template=yes`, then `built=pointer`

## MODIFIED Requirements

### Requirement: README stays within its line budget
`README.md` SHALL be at most 1,225 lines long; a later change that needs more room raises this bound in its own spec, where the operator approves it at the gate.

#### Scenario: README is at most 1,225 lines
- WHEN `(echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')")`
- THEN it prints exactly `readme=within`

### Requirement: The documents record the template fix and init's report of a differing agent copy
`README.md`'s `.claude/agents/factory-*.md` row SHALL say that init reports a copy that differs from its template, and step 1 of "Adopting the factory in a repo" SHALL name `stale_agents`. `docs/changelog.md` SHALL hold one entry for issue #108, numbered without a gap, that names `frontmatter`, `stale_agents` and `Nanobot`. README MUST stay within its 1,225-line budget, and both documents MUST carry no whitespace error.

#### Scenario: README describes init's report of a differing agent copy
- WHEN `(echo "row=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'differs from its template') step=$(sed -n '/^### Adopting the factory in a repo/,/^2\. /p' README.md | tr '\n' ' ' | grep -c 'stale_agents') missing=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'when they are missing')")`
- THEN it prints exactly `row=1 step=1 missing=1`

#### Scenario: The changelog records issue 108 in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #108 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e frontmatter -e stale_agents -e Nanobot | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `3`

#### Scenario: README stays within its line budget and both documents pass the whitespace check
- WHEN `(E=$(git hash-object -t tree /dev/null); echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')"; git diff --check $E HEAD -- README.md docs/changelog.md >/dev/null; echo "check=$?")`
- THEN it prints exactly `readme=within`, then `check=0`

### Requirement: The documents record the launch copy and the route back to checks
`README.md`'s "Starting a run" SHALL tell the operator to launch the copy `factory launch-script` writes. Its "Where a human decides" SHALL list `launch-script` among the commands that are not writes, and its **Unstick** row SHALL name `resolve --to checks`. `docs/design.md` SHALL list `launch-script` in the live-store fence's read-only list and describe the `--to checks` route. `docs/changelog.md` SHALL hold one entry opening `After issue #109`, naming #112, `launch-script` and `--to checks`, numbered without a gap. README SHALL stay within its 1,225-line budget, and the maintained documents SHALL carry no whitespace error.

#### Scenario: The README, the design doc and the changelog describe the launch copy and the route back to checks
Run from the repository root of the checkout under test.
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "start=$(y $(sed -n '/^## Starting a run/,/^### Driving a ticket/p' README.md | grep -c 'factory launch-script')) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--to checks')) writes=$(y $(printf '%s' "$R" | grep -o 'A write is any command except [^;]*;' | grep -c 'launch-script')) list=$(printf '%s' "$R" | grep -o 'A write is any command except [^;]*;' | grep -c .) fence=$(y $(grep '^\*\*Only the dispatcher writes a live store' docs/design.md | grep -c 'launch-script')) route=$(y $(grep -c -- '--to checks' docs/design.md)) readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #109 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e '#112' -e 'launch-script' -e '--to checks' | sort -u | grep -c .)"; E0=$(git hash-object -t tree /dev/null); git diff --check $E0 HEAD -- README.md docs dev .factory/context.md; echo "exit=$?")`
- THEN it prints exactly `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within`, `CONTIGUOUS`, `entries=1 terms=3`, `exit=0`, one per line

### Requirement: README shows the north star on its first screen
`README.md` SHALL hold one paragraph opening `**North star.**`, placed before "What problem it solves", that states the primary metric per hour of operator attention and names `docs/north-star.md`, `STATUS.md` and `docs/reviews/`. README MUST stay within its 1,225-line budget.

#### Scenario: README opens with the north-star paragraph and stays within its budget
- WHEN `(H=$(grep -n '^## What problem it solves$' README.md | cut -d: -f1); B=$(awk -v h="$H" 'NR>=h{exit} /^\*\*North star\.\*\*/{f=1} f&&/^$/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "block=$(grep -c '^\*\*North star\.\*\*' README.md) top=$(printf '%s' "$B" | grep -c '^\*\*North star\.\*\*') metric=$(printf '%s' "$B" | grep -c 'per hour of operator attention') links=$(printf '%s' "$B" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'docs/reviews/' | sort -u | grep -c .) readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')")`
- THEN it prints exactly `block=1 top=1 metric=1 links=3 readme=within`

=== specs/harness-code/spec.md
## MODIFIED Requirements

### Requirement: The command-line code has one module per job
The harness's command-line code SHALL be split by job: the spec-drift checks in
`factory/drift.py`, setup in `factory/setup.py`, the gates in `factory/gates.py`, the human
decisions in `factory/human.py`, and the helpers more than one of them uses, with the live-store
fence, in `factory/common.py`. `factory/cli.py` MUST keep the parser, the entry point and the role
list, and be under 900 lines.

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

#### Scenario: factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines
- WHEN `echo "$(wc -l < factory/cli.py | tr -d ' ') $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"`
- THEN it prints two numbers: the first below 900, the second `3`
=== verification.md
## Acceptance
- The scorecard gives each instance's measures for the window and the window before, and writes nothing → NEW; today `stats` rejects `--scorecard` (argparse usage error), so it prints `exit=2 store=unchanged` and no heading or table line.
- The scorecard takes a run's tokens from its transcript when the run has no cost record → NEW; today it prints nothing (`--scorecard` is rejected).
- The scorecard refuses a missing --since and a malformed target_is_factory → NEW; today it prints `no-since=2 0 bad-setting=2 0 good=2`: every call is refused as an unknown argument, and neither message names `--since` or `target_is_factory`.
- Without --scorecard, stats prints sections A to D and no scorecard → REGRESSION; passes today.
- An escape is recorded against a merged change, its link kept only as a hash, and counted by the scorecard → NEW; today it prints `no-merge=2 sub-ticket=2 unknown=2 empty=2 link-note=2 refused-wrote=0 recorded=2 printed=0/0 link-in-store=0`, then `events=0 fields= hash=differ`, and no `Escapes` row: there is no `escape` command, so every call is an argparse usage error.
- An intervention recorded outside the CLI is counted by the scorecard → NEW; today it prints `unknown=2 recorded=2` and no row.
- run finish records the transcript's tokens for a run with no reply, and keeps a reply's record → NEW; today `run finish` rejects `--transcripts`, so it prints `finish=2 2`, then `none`, then a Python traceback (the second run never starts, because the first stays in flight), and no section D line.
- A run the intake script starts carries its transcript's tokens → NEW; today it prints `state=parked`, then `triage none`.
- A drive run whose claude process failed records its transcript's tokens → NEW; today it prints `state=parked`, then `triage KILLED none`.
- README and the instance template describe the scorecard, the two records and the token record → NEW; today it prints `scorecard=no setting=no escape=no hash=no intervene=no record=no old=yes depends=no pieces=no template=no`, then `built=long`.
- README is at most 1,225 lines → REGRESSION; passes today (1,184 lines), and the change keeps it within 1,225.
- README describes init's report of a differing agent copy → REGRESSION; passes today, unchanged by this change.
- The changelog records issue 108 in one entry without a numbering gap → REGRESSION; passes today, unchanged by this change.
- README stays within its line budget and both documents pass the whitespace check → REGRESSION; passes today at 1,225 (`readme=within`, `check=0`), and at the old 1,185 too.
- The README, the design doc and the changelog describe the launch copy and the route back to checks → REGRESSION; passes today at 1,225.
- README opens with the north-star paragraph and stays within its budget → REGRESSION; passes today at 1,225.
- The drift checks live in factory/drift.py → REGRESSION; passes today.
- The shared helpers and the live-store fence live in factory/common.py → REGRESSION; passes today.
- Instance and store setup live in factory/setup.py → REGRESSION; passes today.
- The gates live in factory/gates.py → REGRESSION; passes today.
- The human decisions live in factory/human.py → NEW; today it prints `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend`, without `escape_add` and `intervention_add`.
- factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines → REGRESSION; passes today (880 lines).
