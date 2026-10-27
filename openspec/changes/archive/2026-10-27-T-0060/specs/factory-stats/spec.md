## ADDED Requirements

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

