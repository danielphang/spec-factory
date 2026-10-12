# factory-stats

## Requirements

### Requirement: factory stats counts runs and verdicts per role and model
`factory stats` MUST print, for each role and model over every store given, the runs with a verdict other than `KILLED`, the `KILLED` runs, the runs whose verdict changed an outcome, the verdicts by status, the BLOCKING findings of reviewer and critic runs, and for implementer runs the gate commands that failed and then passed before hand-off. It SHALL count only runs that started inside the `--since`/`--until` window, SHALL leave out runs in flight, and SHALL write nothing.

#### Scenario: Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0043-fixture.sh <<'EOF'
# Sourced from the repo root: builds two fixture stores, $F/s1 and $F/s2, and a directory of
# transcripts, $F/tx, whose counts the t0043 scenarios state. Leaves F set.
F=$(cd "$(mktemp -d)" && pwd -P); mkdir -p $F/s1/log $F/s2/log $F/tx/a $F/tx/b $F/tx/c $F/tx/d
run() { f="'$7'"; [ $7 = null ] && f=null; mkdir -p $F/$1/runs/$2 && printf 'run_id: %s\nrole: %s\nticket: %s\nmodel: %s\nround: 0\nspec_version: %s\nstarted: %s\nfinished: %s\nwall_s: %s\nstatus: %s\n' $2 ${2#run-????-} $3 $4 $5 "'$6'" "$f" $8 $9 > $F/$1/runs/$2/meta.yaml; }
run s1 run-0001-triage T-0001 opus 0 2026-10-01T10:00:00+00:00 2026-10-01T10:05:00+00:00 100 NEEDS-HUMAN
run s1 run-0002-triage T-0001 opus 0 2026-10-01T11:00:00+00:00 2026-10-01T11:05:00+00:00 50 ACCEPT
run s1 run-0003-spec_writer T-0001 opus 0 2026-10-01T12:00:00+00:00 2026-10-01T12:30:00+00:00 300 READY-FOR-CRITIC
run s1 run-0004-critic T-0001 fable 1 2026-10-01T13:00:00+00:00 2026-10-01T13:10:00+00:00 60 REVISE
run s1 run-0005-spec_writer T-0001 opus 1 2026-10-01T14:00:00+00:00 2026-10-01T14:20:00+00:00 200 READY-FOR-CRITIC
run s1 run-0006-critic T-0001 fable 2 2026-10-01T15:00:00+00:00 2026-10-01T15:10:00+00:00 70 APPROVE
run s1 run-0007-implementer T-0001.1 opus 2 2026-10-02T10:00:00+00:00 2026-10-02T10:30:00+00:00 600 BLOCKED
run s1 run-0008-implementer T-0001.1 opus 3 2026-10-03T10:00:00+00:00 2026-10-03T10:30:00+00:00 400 READY-FOR-REVIEW
run s1 run-0009-reviewer T-0001.1 fable 3 2026-10-03T11:00:00+00:00 2026-10-03T11:05:00+00:00 90 REQUEST-CHANGES
run s1 run-0010-reviewer T-0001.1 fable 3 2026-10-03T12:00:00+00:00 2026-10-03T12:05:00+00:00 116 KILLED
run s1 run-0011-verifier T-0001.1 opus 3 2026-10-03T11:00:00+00:00 2026-10-03T11:10:00+00:00 120 SPEC-DEFECT
run s1 run-0012-verifier T-0001.1 fable 3 2026-10-03T13:00:00+00:00 2026-10-03T13:10:00+00:00 80 VERIFIED
run s1 run-0013-triage T-0002 opus 0 2026-10-04T10:00:00+00:00 null null running
run s1 run-0014-reviewer T-0001.1 fable 3 2026-10-09T10:00:00+00:00 2026-10-09T10:05:00+00:00 95 APPROVE
run s2 run-0001-triage T-0005 opus 0 2026-10-01T10:00:00+00:00 2026-10-01T10:05:00+00:00 40 ACCEPT
run s2 run-0002-critic T-0005 fable 1 2026-10-01T11:00:00+00:00 2026-10-01T11:05:00+00:00 30 APPROVE
printf 'claude:\n  session_id: s-0003\n  total_cost_usd: 1.5\n  num_turns: 10\n  usage: {input_tokens: 10, cache_read_input_tokens: 1000, cache_creation_input_tokens: 90, output_tokens: 50}\n' >> $F/s1/runs/run-0003-spec_writer/meta.yaml
printf '%s\n' '[BLOCKING] 6 proposal.md, Problem' '- [SHOULD-FIX] 1 design.md' 'STATUS: REVISE' > $F/s1/runs/run-0004-critic/output.md
printf '%s\n' '- [BLOCKING] 6 proposal.md, Problem: RESOLVED.' 'STATUS: APPROVE' > $F/s1/runs/run-0006-critic/output.md
printf '%s\n' '- [BLOCKING] reuse: a.py:1: copies b.py:2' 'No BLOCKING or SHOULD-FIX findings beyond that one.' 'STATUS: REQUEST-CHANGES' > $F/s1/runs/run-0009-reviewer/output.md
printf '%s\n' '## Where you work' 'Worktree: `/w`. Gate commands (run each from your worktree, exactly as written; each is already wrapped): `(export HOME=/tmp/h; git diff --check main...HEAD)`, `(export HOME=/tmp/h; pytest -q tests)`' > $F/s1/runs/run-0008-implementer/input.md
ev() { s=$1; shift; printf '{"ts": "%s", "event": "%s", "ticket": "%s"%s}\n' "$@" >> $F/$s/log/2026-10.jsonl; }
ev s1 2026-10-01T10:06:00+00:00 ticket.parked T-0001 ', "reason": "NEEDS-HUMAN from triage"'
ev s1 2026-10-01T12:31:00+00:00 spec.added T-0001 ', "version": 1, "source": "run-0003-spec_writer"'
ev s1 2026-10-01T14:21:00+00:00 spec.added T-0001 ', "version": 2, "source": "run-0005-spec_writer"'
ev s1 2026-10-01T16:00:00+00:00 approval.recorded T-0001 ', "kind": "spec", "version": 2'
ev s1 2026-10-02T10:31:00+00:00 ticket.parked T-0001.1 ', "reason": "BLOCKED from implementer"'
ev s1 2026-10-02T12:00:00+00:00 human.resolved T-0001.1 ', "kind": "ruling"'
ev s1 2026-10-02T13:00:00+00:00 spec.added T-0001 ', "version": 3, "source": "gate edit /x/answers/T-0001-gate-edit.md"'
ev s1 2026-10-02T14:00:00+00:00 ticket.parked T-0001.1 ', "reason": "harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0"'
ev s1 2026-10-02T15:00:00+00:00 park.corrected T-0001.1 ', "previous": "harness-bug: run start implementer: BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0", "reason": "BLOCKED from harness: spec drift: tests/test_a.py changed by 2ad4d8c52 since spec v3 was written at 37848dbb0"'
ev s1 2026-10-03T11:11:00+00:00 human.resolved T-0001.1 ', "kind": "request-changes"'
ev s1 2026-10-03T12:06:00+00:00 ticket.parked T-0001.1 ', "reason": "budget kill: reviewer"'
ev s1 2026-10-03T14:00:00+00:00 merge.refused T-0001.1 ', "reason": "head does not contain main"'
ev s1 2026-10-03T14:10:00+00:00 merge.refused T-0001.1 ', "reason": "head does not contain main"'
ev s1 2026-10-03T14:20:00+00:00 merge.refused T-0001.1 ', "reason": "protected paths not declared"'
ev s1 2026-10-03T15:00:00+00:00 ticket.parked T-0001 ', "reason": "archive: no spec store (factory init not run)\n{'"'"'ok'"'"': false}"'
ev s1 2026-10-03T15:10:00+00:00 ticket.parked T-0001 ', "reason": "archive: "'
ev s1 2026-10-03T15:20:00+00:00 ticket.parked T-0001.1 ', "reason": "sub-ticket closed by a human: T-0001.1"'
ev s1 2026-10-03T15:30:00+00:00 ticket.parked T-0002 ', "reason": "operator hold: T-0002 waits on run-0009-reviewer"'
ev s1 2026-10-03T15:40:00+00:00 human.resolved T-0002 ', "kind": "answer"'
ev s1 2026-10-09T11:00:00+00:00 ticket.parked T-0003 ', "reason": "NEEDS-HUMAN from triage"'
ev s1 2026-10-09T12:00:00+00:00 park.corrected T-0001.1 ', "previous": "budget kill: reviewer", "reason": "budget kill of reviewer after 900 s"'
ev s2 2026-10-01T10:06:00+00:00 ticket.parked T-0005 ', "reason": "NEEDS-HUMAN from triage"'
ev s2 2026-10-01T12:00:00+00:00 approval.recorded T-0005 ', "kind": "spec", "version": 1'
msg() { printf '{"type": "user", "timestamp": "%s", "message": {"role": "user", "content": "%s"}}\n' "$2" "$3" >> $1; }
use() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "model": "claude-fable-5", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": %s, "output_tokens": %s}}}\n' $2 $3 $4 $5 $6 $7 >> $1; }
A=$F/tx/a/agent-a1.jsonl; echo '{}' > $F/tx/a/agent-a1.meta.json
msg $A 2026-10-01T13:00:05Z "[Workflow harness — user request] see $F/s1/runs/run-0001-triage/output.md"
msg $A 2026-10-01T13:00:06Z "[Workflow harness — computed task] First read $F/s1/runs/run-0004-critic/system-prompt.txt"
use $A 2026-10-01T13:01:00Z m1 5 100 0 3; use $A 2026-10-01T13:01:00Z m1 5 100 0 3; use $A 2026-10-01T13:01:01Z m1 5 100 0 7
use $A 2026-10-01T13:02:00Z m2 1 200 4 10; use $A 2026-10-01T13:02:01Z m2 1 200 4 10
B=$F/tx/b/agent-b1.jsonl
msg $B 2026-10-03T10:00:05Z "[Workflow harness — computed task] Your input is $F/s1/runs/run-0008-implementer/input.md"
tool() { printf '{"type": "assistant", "timestamp": "2026-10-03T10:0%s:00Z", "message": {"id": "t%s", "content": [{"type": "tool_use", "id": "u%s", "name": "Bash", "input": {"command": "%s"}}]}}\n{"type": "user", "timestamp": "2026-10-03T10:0%s:30Z", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "u%s", "is_error": %s, "content": "%s"}]}}\n' $1 $1 $1 "$2" $1 $1 $3 "$4" >> $B; }
tool 1 '(export HOME=/tmp/h; pytest -q tests) 2>&1 | tail -3' true 'Exit code 1\n1 failed'
tool 2 '(export HOME=/tmp/h; pytest -q tests) 2>&1 | tail -3' false '3 passed'
tool 3 'git diff --check main...HEAD' false ''
use $B 2026-10-03T10:09:00Z m9 2 50 8 4
C=$F/tx/c/agent-c1.jsonl
msg $C 2026-10-01T10:00:05Z "[Workflow harness — computed task] First read $F/s2/runs/run-0001-triage/system-prompt.txt"
use $C 2026-10-01T10:01:00Z m5 1 9 0 2
D=$F/tx/d/s-0003.jsonl
msg $D 2026-10-01T12:00:05Z "Read $F/s1/runs/run-0003-spec_writer/input.md and write $F/s1/runs/run-0003-spec_writer/output.md"
use $D 2026-10-01T12:01:00Z m7 100 100000 0 500
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## A\./,/^## B\./p' $F/out | grep '^| [a-z]' | grep -v '^| role |')`
- THEN it prints exactly these eight lines, one per line: `exit=0`, `| triage | opus | 3 | 0 | 0 | ACCEPT 2, NEEDS-HUMAN 1 | - | - |`, `| spec_writer | opus | 2 | 0 | 0 | READY-FOR-CRITIC 2 | - | - |`, `| critic | fable | 3 | 0 | 1 | APPROVE 2, REVISE 1 | 1 | - |`, `| implementer | opus | 2 | 0 | 1 | BLOCKED 1, READY-FOR-REVIEW 1 | - | 1 in 1 read, 1 not recorded |`, `| reviewer | fable | 1 | 1 | 1 | REQUEST-CHANGES 1 | 1 | - |`, `| verifier | fable | 1 | 0 | 0 | VERIFIED 1 | - | - |`, `| verifier | opus | 1 | 0 | 1 | SPEC-DEFECT 1 | - | - |`

#### Scenario: A window bounds the count and the command writes nothing
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. From 2026-10-03 on, with no end, store s1 holds two reviewer runs with verdicts (one REQUEST-CHANGES, one APPROVE on 2026-10-09) and one killed.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && S0=$(find $F -type f -exec cksum {} + | sort | cksum); bin/factory stats --store $F/s1 --since 2026-10-03 --transcripts $F/tx > ${TMPDIR:-/tmp}/t0043-since.txt 2>&1; x=$?; echo "exit=$x store=$([ "$(find $F -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed) since=$(sed -n '/^## A\./,/^## B\./p' ${TMPDIR:-/tmp}/t0043-since.txt | grep -c '^| reviewer | fable | 2 | 1 | 1 | APPROVE 1, REQUEST-CHANGES 1 | 1 | - |$')")`
- THEN it prints exactly `exit=0 store=unchanged since=1`

### Requirement: factory stats groups parks by normalised reason and counts gate and merge decisions
`factory stats` MUST group the parks in its window by reason, taking a park's reason from the latest correction of it dated before `--until` when there is one, after replacing run ids with `<run>`, ticket ids with `<ticket>` and commit hashes with `<sha>`, and keeping the reason's first line up to its first two `: `-separated fields, and SHALL print the total, the spec approvals, the requests for spec changes, each other kind of human resolution, each merge-refusal reason and the archive refusals.

#### Scenario: Parks are grouped by normalised reason, with gate and merge decisions
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. Store s1's `harness-bug: ...` park was corrected on 2026-10-02 to `BLOCKED from harness: spec drift: ...`, and its `budget kill: reviewer` park was corrected on 2026-10-09, after the `--until` below.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## B\./,/^## C\./p' $F/out | grep '^| ' | grep -vE '^\| (park reason|gate or merge decision) \|')`
- THEN it prints exactly these seventeen lines, one per line: `exit=0`, `| NEEDS-HUMAN from triage | 2 |`, `| BLOCKED from harness: spec drift | 1 |`, `| BLOCKED from implementer | 1 |`, `| archive | 1 |`, `| archive: no spec store (factory init not run) | 1 |`, `| budget kill: reviewer | 1 |`, `| operator hold: <ticket> waits on <run> | 1 |`, `| sub-ticket closed by a human: <ticket> | 1 |`, `| all parks | 9 |`, `| spec approved | 2 |`, `| spec changes requested | 1 |`, `| resolved: answer | 1 |`, `| resolved: ruling | 1 |`, `| merge refused: head does not contain main | 2 |`, `| merge refused: protected paths not declared | 1 |`, `| archive refused | 2 |`

### Requirement: factory stats ties each spec defect caught downstream to the runs that wrote and critiqued the spec
For each verifier run with `SPEC-DEFECT` and each implementer run with `BLOCKED` in its window, `factory stats` MUST print the spec version the run worked from, the run that wrote it (or `human` for a human's version, or `unknown`), the latest critic run of that version (or `none`) and the number of critic REVISE runs on the ticket, and SHALL print how many approved tickets with and without a REVISE later had such a catch.

#### Scenario: Each downstream spec catch names the runs that wrote and critiqued its spec
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## C\./,/^## D\./p' $F/out | grep '^| ' | grep -vE '^\| (caught by|critic REVISE on the ticket) \|')`
- THEN it prints exactly these five lines, one per line: `exit=0`, `| run-0007-implementer | BLOCKED | T-0001.1 | 2 | run-0005-spec_writer | run-0006-critic | 1 |`, `| run-0011-verifier | SPEC-DEFECT | T-0001.1 | 3 | human | none | 1 |`, `| yes | 1 | 1 |`, `| no | 1 | 0 |`

### Requirement: factory stats reports each role's cost from run records first and transcripts second
`factory stats` MUST report, per role and model, the runs including killed ones, their wall time, and their context and output tokens, taking each run's tokens from its cost record when it has one and otherwise from the one transcript under `--transcripts` that the matching rule assigns to it, counting each message id once, and SHALL say per row how many runs used each source.

#### Scenario: Cost comes from the run record, else the transcript of that store's run, counted once per call
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. Store s1's spec writer run 3 has a cost record and also a transcript; the transcript that names s2's `run-0001-triage` overlaps s1's run of the same id; the critic transcript's first message relays a user request naming another run.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && bin/factory stats --store $F/s1 --store $F/s2 --transcripts $F/tx --until 2026-10-08 > $F/out 2>&1; echo "exit=$?"; sed -n '/^## D\./,$p' $F/out | grep '^| [a-z]' | grep -v '^| role |')`
- THEN it prints exactly these eight lines, one per line: `exit=0`, `| triage | opus | 3 | 190 | 10 | 2 | 0.00 | record 0, transcript 1, none 2 |`, `| spec_writer | opus | 2 | 500 | 1100 | 50 | 1.50 | record 1, transcript 0, none 1 |`, `| critic | fable | 3 | 160 | 310 | 17 | 0.00 | record 0, transcript 1, none 2 |`, `| implementer | opus | 2 | 1000 | 60 | 4 | 0.00 | record 0, transcript 1, none 1 |`, `| reviewer | fable | 2 | 206 | 0 | 0 | 0.00 | record 0, transcript 0, none 2 |`, `| verifier | fable | 1 | 80 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |`, `| verifier | opus | 1 | 120 | 0 | 0 | 0.00 | record 0, transcript 0, none 1 |`

### Requirement: The transcript cost report counts each message once
`python -m factory.cost DIR` MUST count each transcript message id once, using its last record's usage, so that its calls, context tokens and output tokens SHALL equal those of one record per model call.

#### Scenario: The transcript cost report counts each message once
Needs the GIVEN block of "Runs and verdicts are counted per role and model, with kills, outcome changes, BLOCKING findings and fixed gate failures" run once. The critic transcript holds two model calls, written as five records.
- WHEN `(. ${TMPDIR:-/tmp}/t0043-fixture.sh && .venv/bin/python -m factory.cost $F/tx/a | grep '^| critic |')`
- THEN it prints exactly `| critic | fable-5 | 1 | 2 | 310 | 17 |`

### Requirement: factory stats reproduces the hand count on the two live stores
Over this repository's store and the Nanobot target's store, up to 2026-10-07 12:00 UTC, `factory stats` MUST print the request's figures for the code reviewer, spec critic, implementer and parks, and SHALL keep the verifier's two models in separate rows.

#### Scenario: Stats reproduces the hand count on the two live stores
Reads both live stores; writes only its output file under the temporary directory. The expected lines are the two stores' records as they stood on 2026-10-11, when the prototype printed them. The stores live outside the checkout under test, so a mismatch is first checked against them before it is called a defect: a `park.corrected` event dated after the cut does not move these lines (the correction rule), but a hand edit to a run record or log line dated before the cut, or a store moved away from these paths, would, and the verifier names which in its report.
- WHEN `(bin/factory stats --store /Users/dphang/dev/spec-factory/.factory/store --store /Users/dphang/dev/nanobot-upstream/.factory/store --until 2026-10-07T12:00 > ${TMPDIR:-/tmp}/t0043-live.txt 2>&1; echo "exit=$?"; sed -n '/^## A\./,/^## B\./p' ${TMPDIR:-/tmp}/t0043-live.txt | grep -E '^\| (critic|implementer|reviewer|verifier) \| '; sed -n '/^## B\./,/^## C\./p' ${TMPDIR:-/tmp}/t0043-live.txt | grep -E '^\| (NEEDS-HUMAN from triage|all parks) \|')`
- THEN it prints exactly these eight lines, one per line: `exit=0`, `| critic | fable | 84 | 0 | 19 | APPROVE 65, REVISE 19 | 19 | - |`, `| implementer | opus | 111 | 3 | 18 | BLOCKED 18, READY-FOR-REVIEW 92, UNKNOWN 1 | - | 0 in 0 read, 111 not recorded |`, `| reviewer | fable | 94 | 5 | 4 | APPROVE 90, ESCALATE 1, REQUEST-CHANGES 3 | 3 | - |`, `| verifier | fable | 5 | 0 | 1 | SPEC-DEFECT 1, VERIFIED 4 | - | - |`, `| verifier | opus | 108 | 0 | 8 | FAILED 4, SPEC-DEFECT 4, VERIFIED 100 | - | - |`, `| NEEDS-HUMAN from triage | 30 |`, `| all parks | 82 |`
