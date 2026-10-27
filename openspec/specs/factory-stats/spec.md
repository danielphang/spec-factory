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

### Requirement: python -m factory.benchmark reports an arm's operator measures from timestamps
`python -m factory.benchmark [--store PATH] [SESSION]...` MUST print, for the session transcripts and the store given, the operator messages, the store's gate and ruling events, the operator time counted in sittings, the elapsed time and the sessions' tokens, and SHALL write nothing.

#### Scenario: A plain session's transcript gives its operator messages, operator time, elapsed time and tokens
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper. Of the plain session's eleven parseable records, three are operator messages, at 10:00, 10:15 (queued) and 10:40. They form a sitting of 15 minutes plus one minute and a sitting of one minute. Its first record is at 10:00:00 and its last at 10:41:00. Message `m1` is written twice and counts once.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0060-fixture.sh <<'EOF'
# Sourced from the repo root: writes a plain session's transcript, $F/base.jsonl, a runner
# session's transcript, $F/runner.jsonl, a throwaway store's event log, $F/store/log/, and a
# directory with no log, $F/nolog. Leaves F set.
F=$(cd "$(mktemp -d)" && pwd -P); mkdir -p $F/store/log $F/nolog
u() { printf '{"type": "user", "timestamp": "%s"%s, "message": {"role": "user", "content": %s}}\n' "$@"; }
a() { printf '{"type": "assistant", "timestamp": "%s", "message": {"id": "%s", "model": "claude-opus-5-5", "usage": {"input_tokens": %s, "cache_read_input_tokens": %s, "cache_creation_input_tokens": 0, "output_tokens": %s}}}\n' "$@"; }
{ u 2026-10-01T10:00:00Z ', "promptSource": "typed"' '"Fix the cron schedule bug."'
  a 2026-10-01T10:00:30Z m1 100 1000 10; a 2026-10-01T10:00:31Z m1 100 1000 20
  u 2026-10-01T10:01:00Z '' '[{"type": "tool_result", "tool_use_id": "t1", "content": "ok"}]'
  u 2026-10-01T10:02:00Z ', "isMeta": true' '"<local-command-caveat>x</local-command-caveat>"'
  u 2026-10-01T10:03:00Z ', "promptSource": "system"' '"<task-notification>done</task-notification>"'
  u 2026-10-01T10:05:00Z ', "isSidechain": true, "promptSource": "typed"' '"a subagent prompt"'
  echo 'not json'
  u 2026-10-01T10:15:00Z ', "promptSource": "queued"' '"Also keep the old schedule."'
  a 2026-10-01T10:20:00Z m2 50 2000 40
  u 2026-10-01T10:40:00Z '' '"Looks right; done."'
  u 2026-10-01T10:41:00Z '' '"<command-name>/exit</command-name>"'; } > $F/base.jsonl
{ u 2026-10-02T09:00:10Z ', "promptSource": "typed"' '[{"type": "text", "text": "File this issue and drive it."}]'
  u 2026-10-02T09:49:30Z ', "promptSource": "typed"' '"Approve the spec."'
  a 2026-10-02T09:49:40Z m3 10 500 5
  a 2026-10-02T12:05:00Z m4 20 600 7; } > $F/runner.jsonl
ev() { printf '{"ts": "%s", "event": "%s", "ticket": "T-0001"}\n' "$1" "$2"; }
{ ev 2026-10-02T09:00:00+00:00 ticket.created; ev 2026-10-02T09:50:00+00:00 approval.recorded
  ev 2026-10-02T11:00:00+00:00 human.resolved; ev 2026-10-02T12:00:00+00:00 merge.done; } > $F/store/log/2026-10.jsonl
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0060-fixture.sh && .venv/bin/python -m factory.benchmark $F/base.jsonl; echo "exit=$?")`
- THEN it prints exactly these eight lines, one per line: `| measure | value |`, `|---|---|`, `| operator messages | 3 |`, `| gate and ruling events | 0 |`, `| operator time, minutes | 17.0 (2 sittings) |`, `| elapsed, hours | 0.68 |`, `| session tokens | 3150 context, 60 output |`, `exit=0`

#### Scenario: A factory arm's store events and runner session give one operator time
Needs the GIVEN block of "A plain session's transcript gives its operator messages, operator time, elapsed time and tokens" run once. The runner session has two operator messages, at 09:00:10 and 09:49:30. The store has an approval at 09:50:00 and a ruling at 11:00:00. So the sittings are 09:00:10 alone, 09:49:30 to 09:50:00, and 11:00:00 alone: 1, 1.5 and 1 minutes. Its `ticket.created` and `merge.done` are not interactions, but they count for elapsed time, which runs from the store's 09:00:00 to the session's 12:05:00.
- WHEN `(. ${TMPDIR:-/tmp}/t0060-fixture.sh && .venv/bin/python -m factory.benchmark --store $F/store $F/runner.jsonl; echo "exit=$?")`
- THEN it prints exactly these eight lines, one per line: `| measure | value |`, `|---|---|`, `| operator messages | 2 |`, `| gate and ruling events | 2 |`, `| operator time, minutes | 3.5 (3 sittings) |`, `| elapsed, hours | 3.08 |`, `| session tokens | 1130 context, 12 output |`, `exit=0`

### Requirement: python -m factory.benchmark refuses input it cannot read
`python -m factory.benchmark` MUST exit 2 with a message on stderr, writing nothing, when it is given neither a store nor a session, a session that is not a file, or a store with no `log/` directory.

#### Scenario: The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing
Needs the GIVEN block of "A plain session's transcript gives its operator messages, operator time, elapsed time and tokens" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0060-fixture.sh && S0=$(find $F -type f -exec cksum {} + | sort | cksum); r() { e=$(.venv/bin/python -m factory.benchmark "$@" 2>&1 >/dev/null); echo "$?$([ -n "$e" ] && echo +msg)"; }; echo "none=$(r) missing=$(r $F/missing.jsonl) nolog=$(r --store $F/nolog) store=$([ "$(find $F -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `none=2+msg missing=2+msg nolog=2+msg store=unchanged`

### Requirement: The harness suite passes with the benchmark report, and no existing test file changes
The harness suite SHALL pass with this change, and the change MUST modify or delete no existing file under `tests/`.

#### Scenario: The suite passes and no existing test file is modified or deleted
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0060-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=MD main...HEAD -- tests)`
- THEN it prints one line, which reports a number of passed tests and no `failed` or `error`, and nothing after it
