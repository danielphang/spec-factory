# role-inputs

## Requirements

### Requirement: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest
When a ticket's latest finished triage output has a `Capabilities:` line, the spec writer and critic inputs SHALL hold in full only the current-truth capabilities that line names or the spec they work from cites by its `specs/<name>/spec.md` path. They MUST hold, for every other capability, one index line with its absolute spec path and its requirement names, under an instruction that citing a capability's path sends it in full to the critic. The planner SHALL receive no current truth.

#### Scenario: A ticket naming one capability composes inputs with only that capability in full and an index line for each other one
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0036-store.sh <<'EOF'
# Sourced from the repo root, with $1 the Capabilities line that T-0001's triage output carries
# (empty for none). Builds a throwaway store holding three capabilities, alpha, beta and gamma,
# each with one requirement whose text carries a marker (ALPHA-BODY, BETA-BODY, GAMMA-BODY), and a
# decision log of four lines: OWN-LINE logged against T-0001, BETA-LINE and GAMMA-LINE naming those
# capabilities, OTHER-LINE logged against T-0009 and naming none. T-0001's triage run ends ACCEPT
# with that line. Its spec writer run is composed; the spec it returns changes beta and cites
# `openspec/specs/gamma/spec.md` under Evidence. A critic run is composed on that spec; the spec is
# approved and a planner run is composed. Leaves $S (the store) and the input.md of each run:
# $I (triage), $W (spec writer), $C (critic), $P (planner).
T=$(cd "$(mktemp -d)" && pwd -P); S=$T/store
export FACTORY_INSTANCE=$PWD/tests/factory/fixtures/instance FACTORY_STATE=$S FACTORY_REPO=$PWD
start() { bin/factory run start --role $1 --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/'; }
finish() { printf '%s\nSTATUS: %s\nCONFIDENCE: high, fixture\nESCALATIONS: none\n' "$2" "$3" > $T/out.md; bin/factory run finish $1 --output-file $T/out.md >/dev/null; }
printf '# Fixture\n\nMake beta stricter.\n' > $T/req.md
bin/factory ticket new --file $T/req.md >/dev/null && bin/factory init >/dev/null
for c in alpha beta gamma; do U=$(echo $c | tr a-z A-Z); mkdir -p $S/openspec/specs/$c
  printf '# %s\n\n## Requirements\n\n### Requirement: The %s part works\n%s-BODY The %s part SHALL work.\n' $c $c $U $c > $S/openspec/specs/$c/spec.md; done
printf '%s\n' "2026-10-01 T-0001 OWN-LINE decided for this ticket." "2026-10-02 T-0007 BETA-LINE beta keeps its default." \
  "2026-10-03 T-0008 GAMMA-LINE gamma stays read-only." "2026-10-04 T-0009 OTHER-LINE logs rotate weekly." > $S/decisions.md
R=$(start triage); bin/factory run compose $R >/dev/null; I=$S/runs/$R/input.md
finish $R "$(printf 'Type: feature\nTitle: Fixture\nSummary: Make beta stricter.\n%s' "$1")" ACCEPT
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
R=$(start spec_writer); bin/factory run compose $R >/dev/null; W=$S/runs/$R/input.md
finish $R "$(printf '%s\n' '=== proposal.md' '## Problem' 'Beta is lax.' '## Evidence' 'Read `openspec/specs/gamma/spec.md`.' \
  '## Decisions' 'none' '## Risk' 'none' '=== design.md' '## Proposed change' 'A. Tighten beta.' '=== specs/beta/spec.md' \
  '## MODIFIED Requirements' '### Requirement: The beta part works' 'The beta part SHALL work strictly.' '#### Scenario: strict' \
  '- WHEN `true`' '- THEN it exits 0' '=== verification.md' '## Acceptance' '- strict → NEW; today lax')" READY-FOR-CRITIC
bin/factory spec add T-0001 --from-run $R >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
R=$(start critic); bin/factory run compose $R >/dev/null; C=$S/runs/$R/input.md
finish $R "Findings: none." APPROVE
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null && bin/factory approve-spec T-0001 >/dev/null
R=$(start planner); bin/factory run compose $R >/dev/null; P=$S/runs/$R/input.md
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; for v in W C P; do eval f=\$$v; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) alpha-index=$(y alpha) gamma-index=$(y gamma) cites=$(grep -cF 'sends that capability in full to the critic' $f)"; done)`
- THEN it prints exactly `W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1`, then `C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0`. The writer gets beta, which triage named. The critic also gets gamma, whose path the spec cites. A capability's index line holds both its spec's absolute path and its requirement name. The writer's and critic's capability index carries its instruction paragraph once; the planner has no capability index.

### Requirement: A ticket whose triage output names no capabilities receives today's inputs
When a ticket's latest finished triage output has no `Capabilities:` line, the spec writer and critic SHALL receive every current-truth capability in full, and all three roles SHALL receive the whole decision log, as before this change.

#### Scenario: Without a Capabilities line every capability and every decision reach the writer, critic and planner
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh ''; for v in W C P; do eval f=\$$v; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) own=$(grep -c OWN-LINE $f) beta-line=$(grep -c BETA-LINE $f) gamma-line=$(grep -c GAMMA-LINE $f) other=$(grep -c OTHER-LINE $f)"; done)`
- THEN it prints exactly `W: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1`, then `C: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1`, then `P: alpha=0 beta=0 gamma=0 own=1 beta-line=1 gamma-line=1 other=1`

#### Scenario: The harness suite passes with the new inputs
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory >/dev/null 2>&1; echo "suite=$?")`
- THEN it prints exactly `suite=0`

### Requirement: Triage receives the capability index and is asked to name the capabilities a request touches
A triage run's input SHALL hold one capability index line per current-truth capability, with its absolute spec path and its requirement names, and no capability body or decision. Its system prompt MUST ask for a `Capabilities:` output line.

#### Scenario: A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; f=$I; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; echo "triage: alpha-index=$(y alpha) beta-index=$(y beta) gamma-index=$(y gamma) bodies=$(grep -c -- '-BODY' $f) decisions=$(grep -c -- '-LINE' $f) asks=$(grep -c '^Capabilities:' $(dirname $f)/system-prompt.txt)")`
- THEN it prints exactly `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0 asks=1`

### Requirement: The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names
Whenever `decisions.md` holds any text, the spec writer, critic and planner inputs SHALL hold it whole, under the heading `## Decision log (decisions.md): standing decisions, read-only`, and SHALL list it in `input_sources`, whether or not the ticket's latest finished triage output has a `Capabilities:` line; they MUST hold no decision index. Triage MUST still receive no decision line, and the capabilities each role receives in full, with the capability index, MUST stay as they are.

#### Scenario: With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; for v in W C P; do eval f=\$$v; echo "$v: own=$(grep -c OWN-LINE $f) beta-line=$(grep -c BETA-LINE $f) gamma-line=$(grep -c GAMMA-LINE $f) other=$(grep -c OTHER-LINE $f) whole=$(grep -cxF '## Decision log (decisions.md): standing decisions, read-only' $f) index=$(grep -c '^## Decision index' $f) grep-cmd=$(grep -cF "grep ' <ticket id> '" $f) note-decisions=$(grep -cF 'and the decisions that name it' $f) source=$(grep -cx -- '- decisions.md' $(dirname $f)/meta.yaml)"; done)`
- THEN it prints exactly `W: own=1 beta-line=1 gamma-line=1 other=1 whole=1 index=0 grep-cmd=0 note-decisions=0 source=1`, then the same with `C:`, then the same with `P:`. OTHER-LINE, logged against another ticket and naming no capability, reaches all three roles. No role gets a decision index or its `grep` instruction, and the capability index note no longer speaks of decisions.

#### Scenario: The capabilities each role receives and triage's input are unchanged by the whole log
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; y() { grep -F -- "$S/openspec/specs/$1/spec.md" $f | grep -qF -- "The $1 part works" && echo y || echo n; }; for v in W C P; do eval f=\$$v; echo "$v: alpha=$(grep -c ALPHA-BODY $f) beta=$(grep -c BETA-BODY $f) gamma=$(grep -c GAMMA-BODY $f) alpha-index=$(y alpha) gamma-index=$(y gamma) cites=$(grep -cF 'sends that capability in full to the critic' $f)"; done; f=$I; echo "triage: alpha-index=$(y alpha) beta-index=$(y beta) gamma-index=$(y gamma) bodies=$(grep -c -- '-BODY' $f) decisions=$(grep -c -- '-LINE' $f)")`
- THEN it prints exactly `W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1`, then `C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0`, then `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0`

#### Scenario: The harness suite passes with the whole decision log
Run with TMPDIR unset or outside any `.factory/` instance: some suite tests need a directory outside every instance.
- WHEN `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory >/dev/null 2>&1; echo "suite=$?")`
- THEN it prints exactly `suite=0`

### Requirement: The critic sees approved changes not yet archived
A critic run's composed input on a store with a spec store MUST contain a section `## Approved changes not yet archived` that lists every other ticket's change folder whose ticket is neither closed nor back in the spec loop, each with its decisions and the requirements its deltas change, and SHALL drop a change once it is archived or sent back to the spec writer.

#### Scenario: The critic's input lists approved changes not yet archived, other than its own
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && spec 'Wave at night.' 'echo wave' 'wave' > $T27/w.md && printf '# Second\n\nWave.\n' > $T27/req2.md && bin/factory ticket new --file $T27/req2.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-spec-writer --by t >/dev/null && bin/factory spec add T-0002 --file $T27/w.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-critic --by t --round spec:init >/dev/null; R=$(bin/factory run start --role critic --ticket T-0002 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); sec() { bin/factory run compose ${R:-none} >/dev/null 2>&1; awk '/^## Approved changes not yet archived$/{on=1; print; next} /^## /{on=0} on' $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null; }; X=$(sec); echo "listed=$(echo "$X" | grep -c '^### T-0001: ') self=$(echo "$X" | grep -c '^### T-0002') decision=$(echo "$X" | grep -cxF -- '- Greet by default.') requirement=$(echo "$X" | grep -c 'Greets')"; bin/factory archive T-0001 >/dev/null 2>&1; X=$(sec); echo "after_archive: heading=$(echo "$X" | grep -c '^## Approved changes not yet archived$') listed=$(echo "$X" | grep -c '^### T-0001: ')")`
- THEN it prints exactly `listed=1 self=0 decision=1 requirement=1`, then `after_archive: heading=1 listed=0`

#### Scenario: A change sent back to the spec writer leaves the critic's list
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && spec 'Wave at night.' 'echo wave' 'wave' > $T27/w.md && printf '# Second\n\nWave.\n' > $T27/req2.md && bin/factory ticket new --file $T27/req2.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-spec-writer --by t >/dev/null && bin/factory spec add T-0002 --file $T27/w.md >/dev/null && bin/factory ticket transition T-0002 --to ready-for-critic --by t --round spec:init >/dev/null; R=$(bin/factory run start --role critic --ticket T-0002 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); sec() { bin/factory run compose ${R:-none} >/dev/null 2>&1; awk '/^## Approved changes not yet archived$/{on=1; print; next} /^## /{on=0} on' $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null; }; X=$(sec); echo "listed=$(echo "$X" | grep -c '^### T-0001: ') self=$(echo "$X" | grep -c '^### T-0002') decision=$(echo "$X" | grep -cxF -- '- Greet by default.') requirement=$(echo "$X" | grep -c 'Greets')"; bin/factory ticket park T-0001 --reason x >/dev/null && bin/factory resolve T-0001 --to spec-gate >/dev/null && printf 'redo\n' > $T27/n.md && bin/factory request-changes T-0001 --notes $T27/n.md >/dev/null; X=$(sec); echo "respec: heading=$(echo "$X" | grep -c '^## Approved changes not yet archived$') listed=$(echo "$X" | grep -c '^### T-0001: ')")`
- THEN it prints exactly `listed=1 self=0 decision=1 requirement=1`, then `respec: heading=1 listed=0`
