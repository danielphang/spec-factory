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

