## ADDED Requirements
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

### Requirement: The spec writer, critic and planner receive in full only the decisions of their ticket and its capabilities, and a decision index for the rest
When a ticket's latest finished triage output has a `Capabilities:` line, the spec writer, critic and planner inputs SHALL hold in full only the decision-log lines logged against that ticket or naming a capability that role receives in full. They MUST hold one index line per ticket whose lines were left out, and the absolute path of `decisions.md` in an instruction to read a ticket's decisions with `grep`.

#### Scenario: Decisions of other tickets and capabilities reach each role as one index line per ticket
Needs the GIVEN block of "A ticket naming one capability composes inputs with only that capability in full and an index line for each other one" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0036-store.sh 'Capabilities: beta'; for v in W C P; do eval f=\$$v; echo "$v: own=$(grep -c OWN-LINE $f) beta-line=$(grep -c BETA-LINE $f) gamma-line=$(grep -c GAMMA-LINE $f) other=$(grep -c OTHER-LINE $f) indexed=$(grep -v -- '-LINE' $f | grep -o 'T-000[789]' | sort -u | paste -sd, -) log-path=$(grep -qF "$S/decisions.md" $f && echo y || echo n) grep-cmd=$(grep -cF "grep ' <ticket id> ' $S/decisions.md" $f)"; done)`
- THEN it prints exactly `W: own=1 beta-line=1 gamma-line=0 other=0 indexed=T-0008,T-0009 log-path=y grep-cmd=1`, then `C: own=1 beta-line=1 gamma-line=1 other=0 indexed=T-0009 log-path=y grep-cmd=1`, then `P: own=1 beta-line=1 gamma-line=1 other=0 indexed=T-0009 log-path=y grep-cmd=1`. Each role's decision index carries its `grep` instruction once, with the log's absolute path.

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

