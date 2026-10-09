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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0342-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0342-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0342-reviewer/wt` (branch `factory/T-0036.1`, base `9a258097a5eb3feea060eca2cf3f5c7b8c65c072`, head `15c9d2f6498f40909e4a6fc270cd5639772997c8`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0036.1

T-0036.1 / Send the spec writer, critic and planner only the specs and decisions their ticket touches, with a complete index of the rest and a command to open any of it
Depends on: none
Parallel-safe: yes

Parent: T-0036, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A ticket naming one capability composes inputs with only that capability in full and an index line for each other one
- Decisions of other tickets and capabilities reach each role as one index line per ticket
- Without a Capabilities line every capability and every decision reach the writer, critic and planner
- The harness suite passes with the new inputs
- A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line
- The prompt copies, design, build spec, README and changelog name the capability index
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0036/v2.md`

=== proposal.md
## Problem
Three of the factory's agent roles get the whole spec store with every run, whatever their ticket touches. The factory is a pipeline of AI agents that turns a request into a merged change. Each agent, called a role, works from one input file that the harness composes for it. The spec writer turns an accepted ticket into a spec. The critic reviews that spec, and the planner splits an approved spec into sub-tickets. The spec store holds two things. Current truth is one document per capability saying what that part of the system does now. The decision log, `decisions.md`, holds the standing decisions that later tickets must follow.

Today the writer and the critic receive every capability's document and the whole decision log. The planner receives the whole log. A ticket usually touches one or two capabilities. An agent re-sends its whole input on every model call of a run, and a writer run makes a median of 45 calls. So the unused part is paid for many times over, and it crowds out the part the agent needs. The cost grows with every closed ticket, because closing a ticket folds its spec into current truth. A writer input composed on the Nanobot store today would carry about 480 kB of store content before the ticket itself.

The change works in three steps:
- Triage, the role that accepts a request, names the capabilities the request touches.
- The writer and critic receive those capabilities in full. Every other capability gets one line in an index, with the path of its document.
- The decision log is cut the same way for all three roles.

Nothing is hidden. The index is complete, and a role opens anything in it by its path.

This change alone does not meet the request's targets, a mean writer input below 40 kB and a maximum below 100 kB on the Nanobot store. The rest of a writer input can be up to 152 kB by itself: the request, triage's output, and on later rounds the writer's own previous output and the critic's findings. Decisions below records this.

## Root cause
`factory/compose.py` has one fixed rule for each role. `add_truth` (`:168-170`) adds every current-truth spec, and `add_decisions` (`:172-176`) adds the whole log. Nothing records which capabilities a ticket touches. Triage's output format (`docs/design.md:301-308`, `factory/prompts/triage.md`) has no field for them, and triage's input (`:177-181`) does not list them.

## Out of scope
- Reads and searches a role performs itself (#76).
- The implementer, reviewer and verifier inputs, which T-0030.3 already cut.
- Condensing the rest of an input within a run: the request, earlier outputs and findings.
- `factory spec show` and `factory decision show` commands (see Decisions).
- A `factory stats` or `factory/cost.py` report (#70). The operator steps measure with `wc` instead.
- Changes to the spec writer, critic and planner prompts, and to the instance `context.md` template. The input's own headings carry the instructions.
- Current truth for the planner, which receives none today.

## Open questions
none

## Decisions
- Triage names the capabilities on a new output line, `Capabilities:`, chosen from a capability index added to its input. A token that names no current-truth capability, such as `none` or `new`, is ignored.
- Which capabilities a role receives in full: the names on triage's line, plus each existing capability whose `specs/<name>/spec.md` path appears in the spec the role works from. For the writer that is its previous version on a revision round. For the critic it is the version under review. For the planner it is the approved version, read whole, Evidence included. A writer that opens a capability and cites its path under Evidence therefore hands it to the critic. This keeps the request's rule that the critic sees the writer's list plus whatever the writer opened.
- A ticket whose latest finished triage output has no `Capabilities:` line gets today's inputs, the whole of current truth and the whole log. This covers tickets triaged before this change, T-0036 among them. Rejected: sending only the index in that case, which would cut those tickets' inputs with no list to cut by.
- An index line for a capability gives its name, its size, the absolute path of its spec and its requirement names. Rejected: the request's "one-sentence purpose", because no capability spec on either store has a purpose paragraph (Evidence).
- A decision line goes in full when it is logged against this ticket, or when its text names a capability sent in full as a whole word. The log's other lines are indexed one line per ticket: ticket id, number of decisions, first and last date, and the ticket's title. The index heading gives the command `grep ' <ticket id> ' <absolute path of decisions.md>`. Rejected: one index line per decision, which comes to tens of kilobytes on Nanobot (240 lines, median 278 bytes).
- A role opens deferred items by path, with its own file reads or `grep`. No `factory spec show` or `factory decision show` command is added. Rejected: those commands, because a command run from inside a role must clear the live-store fence and find the instance from the role's working directory. A path needs neither, and it is how compose already points at full specs (Evidence).
- The instructions live in the index headings. They say the list is complete, that anything in it is opened by its path, and that citing a path hands the capability to the critic. Rejected: editing the writer and critic prompts, which would put the same words in two more protected copies.
- A run's `input_sources` lists only the files sent in full. An index adds no source.
- The standing 2026-10-04 T-0024 decision says that `decisions.md` "keeps reaching the spec writer, critic and planner". It still does: in full for the lines this ticket touches, and line by line for the rest through the index and its `grep` command.
- Acceptance does not hold this change to the request's 40 kB mean and 100 kB maximum. The projection gives a mean of 101 kB and a maximum of 167 kB for the Nanobot store's last ten tickets, and the remainder lies outside this change (Problem, Evidence). The operator steps measure the real figures after the change runs.
- The docs use one name for the new index, "capability index".

## Risk
Blast radius:
- Every triage, spec writer, critic and planner input composed once the runtime (the pinned checkout the factory runs from, which moves only on an upgrade) moves to a revision with this change, on both instances.
- A writer that needs a capability it was not given, and does not open it, can write a spec that conflicts with it. Two mitigations exist: the index line names every requirement, and the critic's consistency check, its rubric item 5, runs against what the spec cites. The operator steps watch for this.
- An in-flight ticket triaged before the change keeps today's input. Its triage output has no `Capabilities:` line.

Protected paths this change touches:
- harness: `factory/compose.py`, `factory/prompts/triage.md`.
- generated: `docs/prompts/01-triage.md`, re-copied from the edited `docs/design.md` §1 block.

## Operator steps
1. After the runtime (the pinned checkout the factory runs from, which moves only on an upgrade) moves to a revision with this change, and ten new spec writer runs have finished on each store, measure them. Run this from each store directory (`~/dev/nanobot-upstream/.factory/store` and `~/dev/spec-factory/.factory/store`): `ls -d runs/*-spec_writer | tail -10 | while read d; do wc -c < $d/input.md; done | awk '{s+=$1; if($1>m)m=$1} END {printf "mean=%.0f max=%d\n", s/NR, m}'`. Compare the result with the projection in Evidence: Nanobot about 101 kB mean and 167 kB max for comparable tickets, spec-factory about 81 kB and 161 kB. Record both on issue #75.
2. Over the same runs, check whether critic findings of a conflict with current truth (the critic's consistency check, its rubric item 5), or verifier runs that end SPEC-DEFECT (the verdict that the spec, not the code, is wrong), rise against the ten tickets before. Critic findings start with `[BLOCKING] <rubric item>` or `[NIT] <rubric item>`. Run `grep -l '^\[[A-Z]*\] 5 ' runs/*-critic/output.md` and `grep -l 'STATUS: SPEC-DEFECT' runs/*-verifier/output.md`. A rise means writers are missing capabilities they were not given.

=== design.md
## Proposed change
A. **Triage names the capabilities.** This part touches triage's input and its prompt.
   1. In `factory/compose.py`, the `triage` branch appends the capability index after the request. It lists every capability in current truth, built as in B2, under the heading `## Capability index: every capability in current truth`. Its first paragraph says: "Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest." With no current truth, nothing is appended.
   2. The triage prompt changes in the `docs/design.md` §1 block. `docs/prompts/01-triage.md` is re-copied from that block, and `factory/prompts/triage.md` gets the same edit:
      - INPUT reads "One raw request, the capability index (one line per current-truth capability), plus search access to open and recently closed tickets."
      - Step 4 adds a sentence: "Name the current-truth capabilities the request touches, from the capability index."
      - OUTPUT gains a line after `Evidence:` that starts at column 0, `Capabilities: (names from the capability index, comma-separated; none if the request touches none)`. The block's line width stays at 72 characters.

B. **Compose sends only the named capabilities, and an index of the rest.** All of this part is in `factory/compose.py`.
   1. `triage_capabilities(root, tid)` reads the latest finished triage run of the ticket (`_runs_for`). It returns the names on that output's first line starting `Capabilities:`. The rest of the line is split on commas and whitespace, with backticks and trailing periods stripped, and only the names of existing current-truth capabilities are kept. It returns None when there is no such run or no such line.
   2. `cited_capabilities(root, text)` returns the existing current-truth capabilities whose `specs/<name>/spec.md` appears anywhere in `text`.
   3. The capability index part is headed `## Capability index: current truth not given in full above`. Its first paragraph is one line, with these exact words:

      > This list is complete: every current-truth capability not given in full above has one line here. Open a capability at its path before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, sends that capability in full to the critic, and the decisions that name it to the critic and the planner, so cite under Evidence each capability you open.

      The third sentence states what B4 to B7 do: the critic gets a cited capability in full, and the planner gets only the decision lines that name it (B7). Acceptance counts the phrase `sends that capability in full to the critic`.

      Then comes one line per capability, in path order: `- <name>, <size in kB, rounded up> kB, `<absolute path of its spec.md>`: <requirement name>; <requirement name>; …`. Each requirement name is the text after `### Requirement: ` in that spec.
   4. The selected set S is the following:
      - writer: triage's names, plus those cited in `specs/<tid>/v<version>.md` when version ≥ 1;
      - critic: triage's names, plus those cited in the version under review;
      - planner: triage's names, plus those cited in the approved version, read whole.

      When `triage_capabilities` returns None, S is "everything" for that role. `add_truth` and `add_decisions` then behave exactly as today.
   5. With a selected S, `add_truth` adds each capability in S in full, as today, under `Current truth: <name>`. It then appends the capability index (B3) for every other capability, or nothing when none is left. Only the capabilities sent in full go into `input_sources`.
   6. With a selected S, `add_decisions` keeps a log line in full when its second field is the ticket id, or when its text contains the name of a capability in S. A match must not be bordered by a letter, digit, `-` or `_`.
      - The kept lines go under `## Decision log (decisions.md): the standing decisions logged against this ticket or naming a capability given in full, read-only. The full log is `<absolute path>``. `decisions.md` is a source only when at least one line is kept.
      - The other lines are grouped by ticket id under `## Decision index: decisions not given in full above`. Its first paragraph is one line, with these exact words, `<absolute path of decisions.md>` replaced by that path:

        > This list is complete: every ticket with a decision not given in full above has one line here. Read a ticket's decisions with `grep ' <ticket id> ' <absolute path of decisions.md>`.

        `<ticket id>` stays literal. Acceptance counts the text `grep ' <ticket id> ' <absolute path>`.
      - Then comes one line per ticket in first-appearance order: `- <ticket id> (<n> decision(s), <first date> to <last date>): <title>`. The title is the ticket's `title` from `tickets/<id>.yaml`, or empty when the store has no such ticket.
      - An empty or whitespace-only log still adds nothing, as today.
   7. The planner gets no capability index. B6 applies to the planner's log.

C. **Documents.**
   - `docs/design.md`, §Harness "Spec store" paragraph (`:94`). The last two sentences become a description of B. Triage receives the capability index and names capabilities. The spec writer and critic receive those capabilities in full, plus the ones their spec cites, and the capability index for the rest. They and the planner receive the decision log's lines for the ticket and its capabilities, and a decision index for the rest. A ticket with no `Capabilities:` line gets the whole of both.
   - `docs/design.md`, routing table. Row "New request" (`:115`) gains "the capability index". The "Triage ACCEPT" (`:116`) and "Spec writer READY-FOR-CRITIC" (`:120`) rows say "current truth and the decision log, as the Spec store paragraph describes".
   - `docs/changelog.md`: one new numbered entry, "After issue #75 (2026-10-08), where …", with the Evidence figures and the change in two or three sentences.
   - `dev/build-harness.spec.md:280`. The writer's input reads "current truth as doc §Harness, Spec store gives it (in full for the capabilities triage named or the spec cites, the capability index for the rest; all of it when triage's output has no `Capabilities:` line)". The critic's input reads "(as for the writer)". Item 90 holds as written, because its stub triage output has no `Capabilities:` line. Add one clause to item 90 saying so.
   - `README.md`:
     - the Triage row (`:84`) adds "the capability index";
     - the Spec writer row (`:85`) reads "current truth in full for the capabilities triage named, and the capability index for the rest; the decision log's lines for this ticket and those capabilities, and a decision index for the rest";
     - the Spec critic row (`:86`) follows the same pattern as the Spec writer row, with "the capability index" in it;
     - the Planner row (`:87`) gains only the decision-index clause, "the decision log's lines for this ticket and its capabilities, and a decision index for the rest", and no capability index (B7);
     - bump the status date (`:9`) under "Maintaining this page".

## Tests to change
none. Every existing test that pins a writer, critic or planner input composes without a finished triage run, or with a stub triage output that has no `Capabilities:` line. B4's fallback keeps their inputs and `input_sources` unchanged: `tests/factory/test_spec_store.py:54-71` and `:281-293`, `tests/factory/test_decision_log.py:200-237`, and `tests/factory/test_shepherd.py:40-48`. The triage input gains only an index part, which adds no source and no decision text. So `test_decision_log.py:207` and `:211` still hold. `test_decision_log.py:248-255` checks that the §1 block equals `docs/prompts/01-triage.md`, and A2 edits both. `tests/factory/test_instance.py:292-293` reads `factory/prompts/triage.md` at test time.

=== specs/role-inputs/spec.md
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

=== specs/harness-docs/spec.md
## ADDED Requirements
### Requirement: The documents record the capability index
The triage prompt's design block, its `docs/prompts/` copy and the runtime prompt SHALL each carry the `Capabilities:` output line. `docs/design.md`, `dev/build-harness.spec.md` and the README's Triage, Spec writer and Spec critic rows MUST describe the capability index. `docs/changelog.md` MUST have an entry for issue #75, with no whitespace error in the change.

#### Scenario: The prompt copies, design, build spec, README and changelog name the capability index
- WHEN `(echo "docs-copy=$(grep -c '^Capabilities:' docs/prompts/01-triage.md) runtime=$(grep -c '^Capabilities:' factory/prompts/triage.md) changelog=$(grep -c '^[0-9]*\. After issue #75 ' docs/changelog.md) design=$(grep -q 'capability index' docs/design.md && echo y || echo n) build-spec=$(grep -q 'capability index' dev/build-harness.spec.md && echo y || echo n) readme=$(grep -E '^\| (Triage|Spec writer|Spec critic) \(' README.md | grep -c 'capability index')"; git diff --check main...HEAD && echo whitespace=ok)`
- THEN it prints exactly `docs-copy=1 runtime=1 changelog=1 design=y build-spec=y readme=3`, then `whitespace=ok`

=== verification.md
## Acceptance
- A ticket naming one capability composes inputs with only that capability in full and an index line for each other one → NEW. Today it prints `W: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0`, then `C: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0`, then `P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0` (re-run on `main` at `9a25809` in this round). Every capability is sent whole, no input holds a capability's path, and there is no index instruction.
- Decisions of other tickets and capabilities reach each role as one index line per ticket → NEW. Today each of the three lines reads `own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n grep-cmd=0` (re-run on `main` in this round). The whole log is sent, there is no index or `grep` instruction, and the log's path appears nowhere.
- Without a Capabilities line every capability and every decision reach the writer, critic and planner → REGRESSION. It prints the expected three lines on `main` today (run in this spec's investigation).
- The harness suite passes with the new inputs → REGRESSION. `main` today: `364 passed`.
- A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line → NEW. Today it prints `triage: alpha-index=n beta-index=n gamma-index=n bodies=0 decisions=0 asks=0`.
- The prompt copies, design, build spec, README and changelog name the capability index → NEW. Today it prints `docs-copy=0 runtime=0 changelog=0 design=n build-spec=n readme=0`, then `whitespace=ok`.

## PR description (the implementer's output)

Sub-ticket: T-0036.1, `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0036.1/subticket.md` (parent T-0036, approved spec v2). Branch `factory/T-0036.1`, worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0036.1`, base `9a25809`, head `15c9d2f6498f40909e4a6fc270cd5639772997c8` (one commit).

## What changed

The spec writer, critic and planner now receive the whole spec store only when a ticket's triage output gives no list of capabilities. The spec store has two parts. Current truth is one document per capability saying what that part of the system does now. The decision log, `decisions.md`, holds standing decisions. Before this change, every writer and critic input carried all of current truth and the whole log. With this change, triage names the capabilities a request touches. Each of the three roles then receives those in full, plus a complete index of the rest that it can open by path.

**A. Triage names the capabilities.**
- `factory/compose.py`, triage branch: after the request, it appends `## Capability index: every capability in current truth`, with the instruction paragraph the spec gives and one index line per capability. With no current truth, nothing is appended. The index adds no `input_sources` entry.
- The triage prompt is edited identically in three places: the `docs/design.md` §1 block, its copy `docs/prompts/01-triage.md`, and the runtime prompt `factory/prompts/triage.md`.
  - INPUT names the capability index.
  - Step 4 adds "Name the current-truth capabilities the request touches, from the capability index."
  - OUTPUT gains a line after `Evidence:`, at column 0: `Capabilities: (names from the capability index, comma-separated; none` with the continuation `  if the request touches none)`. It is wrapped so that every new line fits in 72 characters; the longest is 72.

**B. Compose sends the selected capabilities in full and an index of the rest.** All of this is in `factory/compose.py`.
- New module functions:
  - `triage_capabilities(root, tid)` (B1). It reads the latest finished triage run's `output.md` and takes the first line starting `Capabilities:`. The rest of that line is split on commas and whitespace, and backticks and periods are stripped from each token. Tokens that name no current-truth capability are dropped. It returns None when there is no such run, no output file or no such line.
  - `cited_capabilities(root, text)` (B2): each capability whose `specs/<name>/spec.md` appears in `text`.
  - `capability_index(paths)` (B3): one line per capability, `- <name>, <ceil(bytes/1000)> kB, `<absolute path>`: <req>; <req>`. Requirement names come from the existing `specstore.requirement_blocks` (reuse rung 1).
  - `CAPABILITY_INDEX_NOTE`, the instruction paragraph in the spec's exact words.
- The inner `selected(spec_rel)` builds the set of capabilities a role receives in full (B4): triage's names plus the ones the role's spec cites, read whole. That spec is `specs/<tid>/v<version>.md` for the writer when version ≥ 1, the version under review for the critic, and the approved version for the planner. Without a `Capabilities:` line the set is None, and both helpers behave exactly as before.
- `add_truth(sel)` (B5) adds each selected capability in full, in path order, as before. It then appends `## Capability index: current truth not given in full above` for the rest. When every capability is selected, it appends nothing.
- `add_decisions(sel)` (B6) sorts each log line one of two ways:
  - Kept in full: the line's second field is the ticket id, or its text names a selected capability. A name only counts when no letter, digit, `-` or `_` touches either end of it. The kept lines go under the new heading, which names the absolute path of the log. `decisions.md` is a source only when at least one line is kept.
  - Indexed: every other line, grouped by ticket under `## Decision index: decisions not given in full above`. The section opens with the exact `grep ' <ticket id> ' <path>` paragraph. Each ticket gets one line, `- <id> (<n> decision(s), <first> to <last>): <title>`, with the title read from `tickets/<id>.yaml`.
  - An empty or whitespace-only log still adds nothing.
- Planner (B7): it calls `add_decisions(selected(approved version))` only, so it gets no current truth and no capability index.

**C. Documents.**
- `docs/design.md`:
  - The §Harness "Spec store" paragraph's last two sentences are replaced by a description of B. It covers the triage index and line, what the writer and critic get in full and indexed, the decision lines and decision index for all three roles, and the fallback.
  - Routing rows "New request" (adds "the capability index"), "Triage ACCEPT" and "Spec writer READY-FOR-CRITIC" now say "as the Spec store paragraph describes".
- `docs/changelog.md`: entry 60, "After issue #75 (2026-10-08), where …". It gives the Evidence figures, the change, the projection and the rejected `show` commands.
- `dev/build-harness.spec.md`: the writer's input in part H (intake step 2) reads as the spec gives it. The critic's input stays "(as for the writer)". Item 90 gains a sentence: it holds because the `accept-approve` stub triage output (`tests/factory/fixtures/stubs/accept-approve/triage-1.md`, read) has no `Capabilities:` line.
- `README.md`:
  - The Triage, Spec writer and Spec critic rows name the capability index. The Triage row glosses it at first use: one line per current-truth capability, with its spec's path and requirement names.
  - The Planner row gains only the decision-index clause.
  - The status date goes from 2026-10-06 to 2026-10-08.

Callers of what changed (coding rule 2): `add_truth` and `add_decisions` are closures inside `compose()`. `grep -rn 'add_truth\|add_decisions' factory/` finds only the calls in the writer branch (`compose.py:272-273`), the critic branch (`:291-292`) and the planner branch (`:315`). The three new module functions are called only from `compose.py`.

## Acceptance results

All were run from the worktree under the fresh-HOME wrapper, with `TMPDIR` set to this run's scratch directory. The GIVEN block and each WHEN were extracted verbatim from `specs/T-0036/v2.md` into scratch files.

**1. A ticket naming one capability composes inputs with only that capability in full and an index line for each other one → NEW**
- Before, on base `9a25809`:
  ```
  W: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0
  C: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0
  P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0
  ```
  This matches the spec's "today" output.
- After, at `15c9d2f`:
  ```
  W: alpha=0 beta=1 gamma=0 alpha-index=y gamma-index=y cites=1
  C: alpha=0 beta=1 gamma=1 alpha-index=y gamma-index=n cites=1
  P: alpha=0 beta=0 gamma=0 alpha-index=n gamma-index=n cites=0
  ```
  This is exactly the expected output. The writer gets only beta, and the critic also gets gamma, which the spec cites.

**2. Decisions of other tickets and capabilities reach each role as one index line per ticket → NEW**
- Before: each of the three lines read `own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n grep-cmd=0`, which matches the spec.
- After:
  ```
  W: own=1 beta-line=1 gamma-line=0 other=0 indexed=T-0008,T-0009 log-path=y grep-cmd=1
  C: own=1 beta-line=1 gamma-line=1 other=0 indexed=T-0009 log-path=y grep-cmd=1
  P: own=1 beta-line=1 gamma-line=1 other=0 indexed=T-0009 log-path=y grep-cmd=1
  ```
  This is exactly the expected output.

**3. Without a Capabilities line every capability and every decision reach the writer, critic and planner → REGRESSION**
- After:
  ```
  W: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1
  C: alpha=1 beta=1 gamma=1 own=1 beta-line=1 gamma-line=1 other=1
  P: alpha=0 beta=0 gamma=0 own=1 beta-line=1 gamma-line=1 other=1
  ```
  This is exactly the expected output. It printed the same before the change.

**4. The harness suite passes with the new inputs → REGRESSION**
- After: `suite=0`.

**5. A triage input lists every capability by path and requirement, and its prompt asks for the Capabilities line → NEW**
- Before: `triage: alpha-index=n beta-index=n gamma-index=n bodies=0 decisions=0 asks=0`.
- After: `triage: alpha-index=y beta-index=y gamma-index=y bodies=0 decisions=0 asks=1`, which is the expected output.

**6. The prompt copies, design, build spec, README and changelog name the capability index → NEW**
- Before: `docs-copy=0 runtime=0 changelog=0 design=n build-spec=n readme=0`, then `whitespace=ok`.
- After: `docs-copy=1 runtime=1 changelog=1 design=y build-spec=y readme=3`, then `whitespace=ok`, which is the expected output.

**Gates, run exactly as written on `15c9d2f`:**
- `(export HOME=…; git diff --check main...HEAD)`: no output, exit 0. The whitespace check passes.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `384 passed in 250.44s`. That is the 364 tests on `main` plus the 20 new ones.

## Tests added/changed

- Added `tests/factory/test_capability_index.py`, a new file with 20 tests. They run black-box through `bin/factory` on throwaway stores and cover:
  - Writer: named capability in full, index lines with exact text, `input_sources`.
  - Critic: cited capabilities added, the instruction paragraph appears once.
  - Planner: no current truth and no index.
  - kB rounding: 2001 bytes shows 3 kB, 2000 bytes shows 2 kB.
  - `Capabilities:` parsing: backticks, a trailing period, no space after a comma, unknown names, `none`, an empty line.
  - Every capability named: no index.
  - The latest finished triage run decides.
  - Decision lines kept or indexed per role, including `beta-two`, `beta_x` and `xbeta2` not matching `beta`. Index lines with pluralisation and a date range, and a ticket title.
  - A log with nothing kept: index only and no `decisions.md` source. A log with everything kept: no index.
  - A whitespace-only log.
  - Fallback without the line.
  - Triage: index text, its position after the request, no source added. No index without current truth.
  - The prompt line in both copies, after `Evidence:`, with new lines of at most 72 characters.
- No existing test was changed. The spec's "Tests to change" is none.
- I watched the new tests fail first: 15 failed and 5 passed on base. The 5 that passed pin behaviour that already held on base: planner gets no truth, all capabilities named, whitespace-only log, fallback, and no index without truth.

## Known gaps and uncertainties

- **The README rule conflicts with the spec.** The README's "Maintaining this page" says behaviour appears above "Where this can go" only after it has run on a real ticket. The spec (C) requires the role rows to describe the capability index now, but it reaches real tickets only after the runtime moves to this revision. I followed the spec. The reviewer may want the rows held until the upgrade.
- **Parentheses around the list are not stripped.** Following B1, only backticks and periods are stripped. A triage output that copies the template's parentheses, such as `Capabilities: (beta, gamma)`, yields the tokens `(beta` and `gamma)`. Both are dropped, so the writer gets no capability in full and the index for all. Nothing is hidden, since the index lists everything, but the cut is wrong for that ticket.
- **Only the first line counts.** Only the first line starting `Capabilities:` is read. Names wrapped onto a continuation line are ignored.
- **Matching is case-sensitive.** A decision line is matched to a capability case-sensitively, so `Beta` does not match `beta`. B6 does not say either way. Capability names are lower-case kebab.
- **`decision(s)` is pluralised.** I read `<n> decision(s)` as pluralisation: `1 decision`, `2 decisions`.
- **The date range uses min and max.** "First date to last date" is computed as the smallest and largest date. For the append-only log this equals first and last appearance.
- **Short lines are kept in full.** A log line with fewer than three fields cannot be indexed by ticket, so it is kept. Neither store has one: every line on both matches `<date> <T-id> <text>`, checked with grep.
- **A capability's title stays empty.** A missing or empty title leaves the index line ending at `):`, with trailing space removed.
- **A delta header counts as a citation.** `cited_capabilities` is a plain substring test. A spec's own `=== specs/<name>/spec.md` delta header therefore counts as a citation, which hands a capability the spec modifies to the critic and planner. The acceptance fixture relies on this: the critic expects beta.
- **No measured effect on real stores.** The size targets are not held by acceptance (spec Decisions). I did not measure real-store input sizes; that is operator step 1.
- factory: markers added: none.

## Out-of-scope observations

- `README.md:795` (the "Record" row) still says `decisions.md` is received by "the spec writer, critic and planner … with their input". That is now true only in part: the lines of the ticket and its capabilities, plus an index. Spec C does not list this row.
- The README terms table has no "capability index" or "decision index" row. Each is glossed at first use in the role table instead.
- `docs/prompts/01-triage.md` already had four lines of 73 characters before this change, so "line width stays at 72" was not strictly true of the block before. No new line exceeds 72.

Protected paths touched, all declared in the spec's Risk list:
- harness: `factory/compose.py`, `factory/prompts/triage.md`
- generated: `docs/prompts/01-triage.md`, re-copied identically to the edited `docs/design.md` §1 block, which `test_decision_log.py`'s block-equals-copy test checks.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command prints exactly its expected output and both gates pass on the committed head (384 passed).
ESCALATIONS: none

## Diff `9a258097a5eb3feea060eca2cf3f5c7b8c65c072...15c9d2f6498f40909e4a6fc270cd5639772997c8`

diff --git a/README.md b/README.md
index b9f8333..8518e67 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-06. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-08. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -81,10 +81,10 @@ directories and `models` entries use.
 
 | Role | Reads | Ends with `STATUS:` | What the harness keeps |
 |---|---|---|---|
-| Triage (`triage`) | the request; after a human answer, its own earlier output | ACCEPT · CLARIFY · NEEDS-HUMAN · REJECT | the title and type, copied onto the ticket |
-| Spec writer (`spec_writer`) | triage's output, the request, current truth for the capabilities it touches, the decision log; after a revision request, the critic's findings and its own previous spec; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
-| Spec critic (`critic`) | the spec version, current truth, the decision log; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
-| Planner (`planner`) | the approved spec, the decision log, rulings, any sub-tickets that already exist | PLANNED · ESCALATE | the plan, `plans/<ticket>.md`, and one sub-ticket per piece, with its dependencies |
+| Triage (`triage`) | the request; the capability index, one line per current-truth capability with its spec's path and requirement names; after a human answer, its own earlier output | ACCEPT · CLARIFY · NEEDS-HUMAN · REJECT | the title and type, copied onto the ticket |
+| Spec writer (`spec_writer`) | triage's output, the request; current truth in full for the capabilities triage named, and the capability index for the rest; the decision log's lines for this ticket and those capabilities, and a decision index for the rest, one line per other ticket; after a revision request, the critic's findings and its own previous spec; the human's change requests from the gate; any human answer or ruling | READY-FOR-CRITIC · NEEDS-SPLIT · NEEDS-HUMAN | the spec, saved as its next version, `specs/<ticket>/v<n>.md` |
+| Spec critic (`critic`) | the spec version; current truth in full for the capabilities triage named or the spec cites, and the capability index for the rest; the decision log's lines for this ticket and those capabilities, and a decision index for the rest; from round 2, its own earlier findings and the previous version; any ruling | APPROVE · REVISE · ESCALATE | the verdict; its findings are attached to the spec when it is pinned |
+| Planner (`planner`) | the approved spec; the decision log's lines for this ticket and its capabilities, and a decision index for the rest; rulings; any sub-tickets that already exist | PLANNED · ESCALATE | the plan, `plans/<ticket>.md`, and one sub-ticket per piece, with its dependencies |
 | Implementer (`implementer`) | where it works (its worktree, branch, base commit and the wrapped gate commands), the sub-ticket, the pinned spec; on a revision, both checkers' findings and the gate result | READY-FOR-REVIEW · BLOCKED | its commits on branch `factory/<sub-ticket>` and the head commit; the message itself is the PR description |
 | Code reviewer (`reviewer`) | the sub-ticket, the pinned spec, the PR description, the diff; from round 2, both checkers' findings from the previous round; any ruling | APPROVE · REQUEST-CHANGES · ESCALATE | a verdict for that commit, `results/<commit>/reviewer.yaml` |
 | Verifier (`verifier`) | the same as the code reviewer; the final run on a parent gets the spec, where it works, and any ruling | VERIFIED · FAILED · SPEC-DEFECT | a verdict for that commit, `verifier.yaml`, and the gate result, `ci.yaml` |
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index c7fc35d..000f7de 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -277,7 +277,7 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 
 `intake.js` (`args: {ticket, stubs?}`):
 1. `phase('Triage')`: `runRole('triage', …)` with input = request, answers appended (+ after an `--answer`: Triage's previous output, K); `ACCEPT` → clerk `transition --to ready-for-spec-writer` (title/type from the output); `REJECT` → `closed`; `NEEDS-HUMAN` → `park --question`; `CLARIFY` → `transition --to waiting-requester` + clerk `factory reply ID --file -` (piece 9: writes `<source dir>/<file>.reply.md` next to the request, appends to `queue.md`, event `reply.sent`); then **return**. Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'` + `harness-bug` event; always return.
-2. `phase('Spec')`: loop `while (true)`: `runRole('spec_writer')` with input = ticket + request + current truth (every `openspec/specs/<capability>/spec.md` in the store, in path order, each one of `input_sources:`) (+ on round ≥ 2: critic findings, previous spec; + after an `--answer`: the writer's previous output, K); `NEEDS-HUMAN` → park, return; `READY-FOR-CRITIC`/`NEEDS-SPLIT` → clerk `spec add`; then clerk `transition --to ready-for-critic --round spec:init` (**sets `round.spec` to 1 if 0**, doc §Routing rules "the first check is round 1"); `runRole('critic')` with input = spec vN + current truth (as for the writer) (+ round ≥ 2: prior findings, the writer's `## Responses`, spec vN−1); `APPROVE` → `transition --to ready-for-spec-gate` + clerk `factory queue` (regenerates `queue.md`, "Spec gate" section), return; `ESCALATE` → park, return; `REVISE` → `if (round < MAX) { transition --to ready-for-spec-writer --round spec:+1; continue } else { park --reason 'max-round cutoff'; return }`. `MAX` = 2 and `MODELS` (the `models:` map, D6) come from clerk `factory config` (B) at the start of each script (that first call runs on the doc's clerk default, Haiku; later calls on `MODELS.clerk`); clerk calls themselves use `model: MODELS.clerk`.
+2. `phase('Spec')`: loop `while (true)`: `runRole('spec_writer')` with input = ticket + request + current truth as doc §Harness, Spec store gives it (in full for the capabilities triage named or the spec cites, the capability index for the rest; all of it when triage's output has no `Capabilities:` line) (+ on round ≥ 2: critic findings, previous spec; + after an `--answer`: the writer's previous output, K); `NEEDS-HUMAN` → park, return; `READY-FOR-CRITIC`/`NEEDS-SPLIT` → clerk `spec add`; then clerk `transition --to ready-for-critic --round spec:init` (**sets `round.spec` to 1 if 0**, doc §Routing rules "the first check is round 1"); `runRole('critic')` with input = spec vN + current truth (as for the writer) (+ round ≥ 2: prior findings, the writer's `## Responses`, spec vN−1); `APPROVE` → `transition --to ready-for-spec-gate` + clerk `factory queue` (regenerates `queue.md`, "Spec gate" section), return; `ESCALATE` → park, return; `REVISE` → `if (round < MAX) { transition --to ready-for-spec-writer --round spec:+1; continue } else { park --reason 'max-round cutoff'; return }`. `MAX` = 2 and `MODELS` (the `models:` map, D6) come from clerk `factory config` (B) at the start of each script (that first call runs on the doc's clerk default, Haiku; later calls on `MODELS.clerk`); clerk calls themselves use `model: MODELS.clerk`.
 3. A non-`none` escalations list never changes the route; `run finish` already logged it.
 4. A re-run of `intake.js` starts from the state the store holds: `ready-for-triage` → phase 1; `ready-for-spec-writer` → phase 2 at the writer; `ready-for-critic` (a human `--ruling` on a critic ESCALATE, K) → phase 2 at the critic, same round, the ruling in its input.
 
@@ -475,7 +475,7 @@ Driver: `claude -p … "/factory run build T-0001 --stubs tests/factory/fixtures
 
 88. ⟨bare⟩ **Change folder at the gate:** `specs/T-0001/v1.md` in the four-part FORMAT of doc §2, its delta part `=== specs/status-parser/spec.md` holding `## ADDED Requirements` with `### Requirement: trailer-read` and one scenario: `AS daniel factory approve-spec T-0001 --version 1` → `openspec/changes/T-0001/` holds `proposal.md`, `design.md`, `specs/status-parser/spec.md` and `verification.md`, each equal to its part of `v1.md` except that `verification.md` also ends with `## Critic rounds`, one entry per critic run of T-0001; `change.pinned` logged; `openspec/specs/` and `decisions.md` unchanged. A `v2.md` whose delta has `## MODIFIED Requirements` with `### Requirement: no-such-req`: `AS daniel factory approve-spec T-0001 --version 2` → exit 2, stderr names `no-such-req`, `approved_version: 1`, no `approvals/T-0001/spec-v2.yaml` [NEW]
 89. ⟨wf⟩⟨bare⟩ **Archive at parent close:** case `plan-three` on item 88's T-0001, after item 77's VERIFIED: `openspec/changes/T-0001` is gone; `openspec/changes/archive/<date>-T-0001/` holds item 88's four files and `tasks.md`, equal to the planner run's `output.md` above its last `STATUS:` line; its `verification.md` ends with `## Verifier results`, one line per verifier row of `T-0001.1`–`.3` and `T-0001`; `openspec/specs/status-parser/spec.md` contains `### Requirement: trailer-read` and its scenario; `decisions.md` gained one `<date> T-0001 …` line per `## Decisions` line of the proposal; in the log `change.archived` precedes the transition to `closed`. A second parent, pinned before T-0001 archived with a delta that also ADDs `trailer-read`, reaching its parent-close VERIFIED → `status: parked`, `parked.reason` starts `archive:`, and `openspec/specs/`, `decisions.md` and its change folder are unchanged [NEW]
-90. ⟨wf⟩⟨bare⟩ **Current truth in writer and critic input:** after item 89, `factory request new --file r.md` (a new ticket `T-000k`) and case `accept-approve` run on `T-000k` → its spec writer run's and its critic run's `input.md` each contain `### Requirement: trailer-read`, and each of those runs' `meta.yaml` `input_sources` lists `openspec/specs/status-parser/spec.md` besides the sources item 42 names for that role. Item 42 holds as written because `openspec/specs/` is empty after `factory init` [NEW]
+90. ⟨wf⟩⟨bare⟩ **Current truth in writer and critic input:** after item 89, `factory request new --file r.md` (a new ticket `T-000k`) and case `accept-approve` run on `T-000k` → its spec writer run's and its critic run's `input.md` each contain `### Requirement: trailer-read`, and each of those runs' `meta.yaml` `input_sources` lists `openspec/specs/status-parser/spec.md` besides the sources item 42 names for that role. Item 42 holds as written because `openspec/specs/` is empty after `factory init`. This item holds as written after the capability index because the `accept-approve` stub triage output has no `Capabilities:` line, so both runs receive the whole of current truth [NEW]
 91. ⟨bare⟩ **Archive refusals without a change folder (K):** T-0001 pinned as in item 88's first half (`specs/T-0001/v1.md`, `AS daniel factory approve-spec T-0001 --version 1`). (a) On the `factory-store` checkout, `rm -rf openspec/changes/T-0001`; then `factory archive T-0001` → exit 2, stderr `T-0001 has no change folder to archive`. (b) Then `mv openspec ../openspec.aside` on the `factory-store` checkout; `factory archive T-0001` → exit 2, stderr `no spec store (factory init not run)`. In (a) and (b) the `factory-store` checkout's `git rev-parse HEAD` and `git status --porcelain` are the same after the command as before it, and `factory log tail --event change.archived` gained no line [NEW]
 
 ### Gates (every seam)
diff --git a/docs/changelog.md b/docs/changelog.md
index 3d1474f..6b3d210 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -61,5 +61,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 57. After issue #41 (2026-10-04), where a code reviewer started the full test suite in the background, ended its turn to wait for it, and so wrote no review, three times in one day, each time on a commit the verifier had already passed; the harness recorded each run as KILLED and parked the ticket as a budget kill, though it enforces no budget and the agent call reports no reason a run stopped. A role run that ends without writing its output is now EMPTY-OUTPUT in `run finish`, never a budget kill, and the workflow keeps the agent's last message with the run (`factory run last-message`). The same role is re-dispatched once, on the same inputs and in the same round; a second EMPTY-OUTPUT in a row parks the ticket as `EMPTY-OUTPUT from <role>` with both runs, and records no result row for that run, so `resolve --redispatch` re-runs only that checker. A thrown agent call keeps its KILLED record and its `agent call failed` park. The shared preamble gains one RUNNING CODE bullet: run every command in the foreground and never end the turn while one is still running. The code reviewer prompt gains a WHAT YOU RUN section: judge the diff by reading it and leave the test suite and the gate commands to the verifier, which runs them on the same head; a narrow command that confirms one finding is allowed. The reviewer's input no longer lists the gate commands; it says the verifier runs them. The routing table gains two EMPTY-OUTPUT rows. Rejected: keeping a budget-kill label for some empty outputs, and a retry counter in the store.
 58. After issue #73 (2026-10-07), where the spec writer took a third of all workflow context tokens (309M of 866M; a median of 29 agent calls and 5.3M tokens per run), because every call re-sends the start-up context and everything read so far, and where the critic ran the test suite and built prototype clones of the change on its own initiative, though its grounding is meant to stay within two paths and one command per claim. The spec writer prompt gains a RULES bullet, Turn economy: put independent reads and commands in one turn, read a line range once grep has found it, send long output to a file in the run's scratch directory and grep or tail it, and write the spec in as few writes as possible. The critic's PROCESS keeps its minimum spot-check and caps any one claim at two paths and one command; it runs no test suite and builds nothing, and a claim it could settle only by building becomes a finding for the writer or a question. It gains the same reading rules. No rubric item, round limit or required spec section changes, and the shared preamble does not change. Rejected: a shared preamble line, which would reach every role.
 59. After issue #74 (2026-10-08), where the operator's replay of three past intakes (#49, #51, #57), with the same inputs and bases, found that #73's spec writer rules cut its tokens by about 37% at the same quality, but that its critic rules saved nothing (0.71M to 0.72M, 1.0M to 0.93M, 1.67M to 1.63M tokens) and made the critic check less: it missed the Nanobot `UV_PYTHON_INSTALL_DIR` risk on #51 and, on #57, the brace-list declaration bug that the earlier prompt had confirmed with a scratch git test. The critic's PROCESS drops the per-claim cap (at most two paths and one command for any one claim) and the no-build rule (no clone, worktree or prototype), and says the critic may run a small experiment in its scratch directory to confirm a finding. It keeps its minimum spot-check, the rule that it runs no test suite, the rule for picking an acceptance command, the rule that a claim needing a suite run or a build of the change is a finding or a question, and the three reading rules. `docs/principles.md` principle 2 keeps the critic's no-suite rule, and its Spiking section drops the two-path bound and says that vetting a whole approach is still the spec writer's or a spike's job. The spec writer prompt is unchanged from #73.
+60. After issue #75 (2026-10-08), where every spec writer and critic input carried all of current truth and the whole decision log, whatever its ticket touched: one spec writer input on this repo's store was 171.6 kB, of which 123.9 kB was current truth and 32.4 kB the log, and the Nanobot store adds about 480 kB to each writer input. Triage now receives the capability index, one line per current-truth capability with its size, spec path and requirement names, and names the capabilities a request touches on a new `Capabilities:` output line. The spec writer and critic receive those capabilities in full, plus each one their spec cites by path, and the capability index for the rest. They and the planner receive the decision-log lines of the ticket and of those capabilities, and a decision index for the rest: one line per other ticket, with a `grep` command that reads its lines. A ticket whose triage output has no `Capabilities:` line keeps the whole of both. The projection for the Nanobot store's last ten tickets is a mean writer input of 101 kB and a maximum of 167 kB, against 521 kB and 635 kB before; that still misses the request's 40 kB and 100 kB targets, because the rest of a writer input lies outside this change. Rejected: `factory spec show` and `factory decision show` commands, because a command run from inside a role must clear the live-store fence, the guard that refuses store commands while a role runs, and find the instance; a path needs neither.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 40c079c..f0c9315 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -91,7 +91,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 | `tasks.md` | The sub-tickets and coverage map | Planner, or the harness when it skips the planner |
 | `verification.md` (the artifact the fork adds) | The NEW or REGRESSION label of each scenario and the writer's Responses; every critic round's output; at archive, every verifier result recorded per head for the parent and its sub-tickets | Spec writer (labels, Responses), critic, verifier |
 
-`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. The spec writer and the critic receive every current-truth spec with their input (routing table). They and the planner also receive `decisions.md` when it holds any text.
+`decisions.md`, one per repo beside `openspec/`, is the decision log: one line per decision, with its ticket id. Roles return text and never write the tree; the harness writes it. The spec writer returns one document in parts (§2 FORMAT), and the store keeps every version. The human spec gate pins one version: it refuses a delta that does not apply to current truth, and writes the pinned version as the change folder, so the planner, implementer and verifier work from the delta the human approved. Labels and round-to-round churn stay in `verification.md`, out of the delta. **Archive** is the parent-close step. After the parent-close run returns VERIFIED, or a sub-ticket's VERIFIED run stands in for it (routing table, Merge gate row), the harness applies each delta to current truth (ADDED appends the requirement, MODIFIED replaces the requirement of that name whole, REMOVED deletes it), moves the folder to `openspec/changes/archive/<YYYY-MM-DD>-<ticket id>/`, and appends each line of the proposal's Decisions to `decisions.md` with the date and ticket id; then the parent closes. An archive refusal writes nothing and parks the parent. There are three: a delta that no longer applies (an ADDED name already in current truth, a MODIFIED or REMOVED name missing); no change folder, because the spec was pinned before the repo had an `openspec/` tree; and no spec store at all (no `openspec/` tree). Only the archive step writes current truth. `decisions.md` has three writers: archive; `factory decision add <ticket id> "<line>"`, which a human runs at any ticket state, closed included; and `resolve --answer` or `resolve --close` with `--decision "<line>"`. Each appends `<YYYY-MM-DD> <ticket id> <line>`, with the UTC date. Triage receives the capability index: one line per current-truth capability, with its size, the absolute path of its spec and its requirement names. Triage names the capabilities the request touches on its `Capabilities:` line. The spec writer and the critic receive those capabilities in full, plus each one whose `specs/<name>/spec.md` path the spec they work from cites, and the capability index for the rest (routing table). They and the planner receive the decision log's lines logged against the ticket or naming one of those capabilities, and a decision index for the rest: one line per other ticket, with the `grep` command that reads its lines from `decisions.md`. A ticket whose latest triage output has no `Capabilities:` line gets the whole of both: every current-truth spec, and `decisions.md` when it holds any text.
 
 **Routing table.** The dispatcher (piece 2) is this table and nothing else. Each row: a STATUS a role emits, what runs next, and what it receives. "Receives" adds to the INPUT the role prompt already declares. Both follow the role-context block (above).
 
@@ -112,12 +112,12 @@ Rules the table relies on:
 
 | From | STATUS | Next | Receives |
 |---|---|---|---|
-| New request | — | Triage | The request, ticket search |
-| Triage | ACCEPT | Spec writer | The ticket; current truth (Spec store) and the decision log, read-only |
+| New request | — | Triage | The request, the capability index, ticket search |
+| Triage | ACCEPT | Spec writer | The ticket; current truth and the decision log, as the Spec store paragraph describes, read-only |
 | Triage | NEEDS-HUMAN | Human queue | The question |
 | Triage | CLARIFY | Requester, via piece 9; ticket parks until answered | The missing-info list |
 | Triage | REJECT | Closed | — |
-| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo, current truth and the decision log read-only; round 2+: prior findings, the writer's responses, previous spec version |
+| Spec writer | READY-FOR-CRITIC / NEEDS-SPLIT | Critic | Spec, repo, current truth and the decision log, as the Spec store paragraph describes, read-only; round 2+: prior findings, the writer's responses, previous spec version |
 | Spec writer | NEEDS-HUMAN | Human queue | Open questions |
 | Critic | APPROVE | Human spec gate | Spec + critic output |
 | Critic | REVISE | Spec writer (round +1) if round < {2}, else Human queue | Findings, the spec version they apply to |
@@ -273,8 +273,8 @@ ESCALATIONS: none | <list>
 ROLE: Triage. You turn raw requests (issues, Slack threads, bug reports,
 ideas) into candidate tickets, or you reject or route them.
 
-INPUT: One raw request, plus search access to open and recently closed
-tickets.
+INPUT: One raw request, the capability index (one line per current-truth
+capability), plus search access to open and recently closed tickets.
 
 FOR EACH REQUEST
 1. Search for duplicates. If one exists, link it and stop.
@@ -287,7 +287,9 @@ FOR EACH REQUEST
    - CLARIFY: key facts are missing. List exactly what's missing.
    - REJECT: duplicate, out of scope, or not actionable. One-line reason.
 4. For ACCEPT: write a title and a 2-5 sentence summary of what the
-   requester needs, in their terms, plus any evidence they gave.
+   requester needs, in their terms, plus any evidence they gave. Name
+   the current-truth capabilities the request touches, from the
+   capability index.
 
 RULES
 - Never add requirements the requester didn't state or clearly imply.
@@ -302,6 +304,8 @@ Type:
 Title:
 Summary:
 Evidence: (links, logs, quotes from the request)
+Capabilities: (names from the capability index, comma-separated; none
+  if the request touches none)
 Assumptions:
 Question for human / Missing info / Reason: (whichever applies)
 STATUS: ACCEPT | NEEDS-HUMAN | CLARIFY | REJECT
diff --git a/docs/prompts/01-triage.md b/docs/prompts/01-triage.md
index cccd415..d2256ae 100644
--- a/docs/prompts/01-triage.md
+++ b/docs/prompts/01-triage.md
@@ -1,8 +1,8 @@
 ROLE: Triage. You turn raw requests (issues, Slack threads, bug reports,
 ideas) into candidate tickets, or you reject or route them.
 
-INPUT: One raw request, plus search access to open and recently closed
-tickets.
+INPUT: One raw request, the capability index (one line per current-truth
+capability), plus search access to open and recently closed tickets.
 
 FOR EACH REQUEST
 1. Search for duplicates. If one exists, link it and stop.
@@ -15,7 +15,9 @@ FOR EACH REQUEST
    - CLARIFY: key facts are missing. List exactly what's missing.
    - REJECT: duplicate, out of scope, or not actionable. One-line reason.
 4. For ACCEPT: write a title and a 2-5 sentence summary of what the
-   requester needs, in their terms, plus any evidence they gave.
+   requester needs, in their terms, plus any evidence they gave. Name
+   the current-truth capabilities the request touches, from the
+   capability index.
 
 RULES
 - Never add requirements the requester didn't state or clearly imply.
@@ -30,6 +32,8 @@ Type:
 Title:
 Summary:
 Evidence: (links, logs, quotes from the request)
+Capabilities: (names from the capability index, comma-separated; none
+  if the request touches none)
 Assumptions:
 Question for human / Missing info / Reason: (whichever applies)
 STATUS: ACCEPT | NEEDS-HUMAN | CLARIFY | REJECT
diff --git a/factory/compose.py b/factory/compose.py
index 1c3424e..16cafe6 100644
--- a/factory/compose.py
+++ b/factory/compose.py
@@ -5,6 +5,7 @@ Per (role, round, resolution). No other code path assembles role input.
 from __future__ import annotations
 
 import difflib
+import math
 import re
 import shlex
 from pathlib import Path
@@ -37,6 +38,36 @@ def current_truth(root: Path) -> list[Path]:
     return sorted(d.glob("*/spec.md")) if d.exists() else []
 
 
+def triage_capabilities(root: Path, tid: str) -> list[str] | None:
+    """The current-truth capabilities on the first `Capabilities:` line of the ticket's latest
+    finished triage output, split on commas and whitespace, backticks and periods stripped, unknown
+    names (`none`, `new`) dropped. None when there is no such run or no such line: the ticket then
+    gets the whole of current truth and the decision log, as before the line existed."""
+    runs = _runs_for(root, tid, "triage", "")
+    p = root / "runs" / runs[-1] / "output.md" if runs else None
+    if p is None or not p.exists():
+        return None
+    for line in p.read_text(encoding="utf-8").splitlines():
+        if line.startswith("Capabilities:"):
+            have = {c.parent.name for c in current_truth(root)}
+            names = (w.strip("`.") for w in re.split(r"[,\s]+", line[len("Capabilities:"):]))
+            return list(dict.fromkeys(n for n in names if n in have))
+    return None
+
+
+def cited_capabilities(root: Path, text: str) -> list[str]:
+    """The current-truth capabilities whose `specs/<name>/spec.md` appears anywhere in `text`."""
+    return [c.parent.name for c in current_truth(root) if f"specs/{c.parent.name}/spec.md" in text]
+
+
+def capability_index(paths: list[Path]) -> str:
+    """One line per current-truth spec: its name, size in kB rounded up, absolute path and
+    requirement names."""
+    return "".join(f"- {p.parent.name}, {math.ceil(p.stat().st_size / 1000)} kB, `{p}`: "
+                   + "; ".join(specstore.requirement_blocks(p.read_text(encoding="utf-8"))) + "\n"
+                   for p in paths)
+
+
 def _last_run_meta(root: Path, ticket: str, role: str, exclude: str) -> dict | None:
     runs = _runs_for(root, ticket, role, exclude)
     return store.read_yaml(root / "runs" / runs[-1] / "meta.yaml") if runs else None
@@ -104,6 +135,12 @@ def without_evidence(text: str) -> str:
     return "\n".join(out) + ("\n" if out and text.endswith("\n") else "")
 
 
+CAPABILITY_INDEX_NOTE = (
+    "This list is complete: every current-truth capability not given in full above has one line here. Open a "
+    "capability at its path before you rely on it. A spec that cites a capability's path, as "
+    "`openspec/specs/<name>/spec.md`, sends that capability in full to the critic, and the decisions that name it "
+    "to the critic and the planner, so cite under Evidence each capability you open.")
+
 _ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
 
 
@@ -165,17 +202,64 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
     version = t["spec"]["version"]
     rnd = t["round"]["spec"]
 
-    def add_truth() -> None:
+    def selected(spec_rel: str | None) -> set[str] | None:
+        """The capabilities this role gets in full (doc §Harness, Spec store): triage's names plus
+        those the spec it works from cites. None, meaning all of them, without a `Capabilities:` line."""
+        names = triage_capabilities(root, tid)
+        if names is None:
+            return None
+        spec = root / spec_rel if spec_rel else None
+        return set(names) | set(cited_capabilities(root, spec.read_text(encoding="utf-8"))
+                                if spec and spec.exists() else [])
+
+    def add_truth(sel: set[str] | None) -> None:
+        rest = []
         for p in current_truth(root):
-            add(str(p.relative_to(root)), f"Current truth: {p.parent.name}")
+            if sel is None or p.parent.name in sel:
+                add(str(p.relative_to(root)), f"Current truth: {p.parent.name}")
+            else:
+                rest.append(p)
+        if rest:
+            parts.append("\n## Capability index: current truth not given in full above\n\n" + CAPABILITY_INDEX_NOTE
+                         + "\n\n" + capability_index(rest))
 
-    def add_decisions() -> None:
+    def add_decisions(sel: set[str] | None) -> None:
         # an empty log (the one `factory init` creates) carries nothing, so it is no input
         p = root / "decisions.md"
-        if p.exists() and p.read_text(encoding="utf-8").strip():
+        text = p.read_text(encoding="utf-8") if p.exists() else ""
+        if not text.strip():
+            return
+        if sel is None:
             add("decisions.md", "Decision log (decisions.md): standing decisions, read-only")
+            return
+        named = [re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(c)}(?![A-Za-z0-9_-])") for c in sel]
+        kept, rest = [], {}
+        for line in filter(str.strip, text.splitlines()):
+            f = line.split(maxsplit=2)
+            # a line without a date and a ticket id cannot be indexed, so it is kept
+            if len(f) < 3 or f[1] == tid or any(r.search(f[2]) for r in named):
+                kept.append(line)
+            else:
+                rest.setdefault(f[1], []).append(f[0])
+        if kept:
+            add("decisions.md", "Decision log (decisions.md): the standing decisions logged against this ticket "
+                f"or naming a capability given in full, read-only. The full log is `{p}`", lambda _: "\n".join(kept))
+        if rest:
+            def title(t_id: str) -> str:
+                tp = store.ticket_path(root, t_id)
+                return str(store.read_yaml(tp).get("title") or "") if tp.exists() else ""
+            parts.append("\n## Decision index: decisions not given in full above\n\nThis list is complete: every "
+                         "ticket with a decision not given in full above has one line here. Read a ticket's decisions "
+                         f"with `grep ' <ticket id> ' {p}`.\n\n"
+                         + "".join(f"- {k} ({len(d)} decision{'s' * (len(d) > 1)}, {min(d)} to {max(d)}): "
+                                   f"{title(k)}".rstrip() + "\n" for k, d in rest.items()))
     if role == "triage":
         add(t["request"], "Request (raw, with any answers appended)")
+        every = current_truth(root)
+        if every:
+            parts.append("\n## Capability index: every capability in current truth\n\nName the capabilities this "
+                         "request touches on your `Capabilities:` line. The spec writer receives those in full and "
+                         "this index for the rest.\n\n" + capability_index(every))
         prior = _runs_for(root, tid, "triage", run_id)
         if prior:
             add(f"runs/{prior[-1]}/output.md", "Your previous Triage output (the question you asked is answered above)")
@@ -184,8 +268,9 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         if tri:
             add(f"runs/{tri[-1]}/output.md", "Ticket (Triage output)")
         add(t["request"], "Request (raw)")
-        add_truth()
-        add_decisions()
+        sel = selected(f"specs/{tid}/v{version}.md" if version >= 1 else None)
+        add_truth(sel)
+        add_decisions(sel)
         if rnd >= 1 and version >= 1:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
@@ -202,8 +287,9 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
             add(str(p.relative_to(root)), "Human ruling")
     elif role == "critic":
         add(f"specs/{tid}/v{version}.md", f"Spec under review (v{version})")
-        add_truth()
-        add_decisions()
+        sel = selected(f"specs/{tid}/v{version}.md")
+        add_truth(sel)
+        add_decisions(sel)
         if rnd >= 2 and version >= 2:
             crit = _runs_for(root, tid, "critic", run_id)
             if crit:
@@ -226,7 +312,7 @@ def compose(root: Path, cfg: dict, meta: dict, t: dict) -> tuple[str, list[str]]
         if av is None:
             raise store.Refused(f"{tid} has no approved spec version")
         add_spec(f"specs/{tid}/v{av}.md", f"Approved spec (v{av}, pinned)")
-        add_decisions()
+        add_decisions(selected(f"specs/{tid}/v{av}.md"))  # no current truth for the planner, so no index
         for p in _approvals(root, tid, "ruling"):
             add(str(p.relative_to(root)), "Human ruling")
         subs = store.subtickets_of(root, tid)
diff --git a/factory/prompts/triage.md b/factory/prompts/triage.md
index dfe55f6..e24e947 100644
--- a/factory/prompts/triage.md
+++ b/factory/prompts/triage.md
@@ -1,8 +1,8 @@
 ROLE: Triage. You turn raw requests (issues, Slack threads, bug reports,
 ideas) into candidate tickets, or you reject or route them.
 
-INPUT: One raw request, plus search access to open and recently closed
-tickets.
+INPUT: One raw request, the capability index (one line per current-truth
+capability), plus search access to open and recently closed tickets.
 
 FOR EACH REQUEST
 1. Search for duplicates. If one exists, link it and stop.
@@ -15,7 +15,9 @@ FOR EACH REQUEST
    - CLARIFY: key facts are missing. List exactly what's missing.
    - REJECT: duplicate, out of scope, or not actionable. One-line reason.
 4. For ACCEPT: write a title and a 2-5 sentence summary of what the
-   requester needs, in their terms, plus any evidence they gave.
+   requester needs, in their terms, plus any evidence they gave. Name
+   the current-truth capabilities the request touches, from the
+   capability index.
 
 RULES
 - Never add requirements the requester didn't state or clearly imply.
@@ -34,6 +36,8 @@ Type:
 Title:
 Summary:
 Evidence: (links, logs, quotes from the request)
+Capabilities: (names from the capability index, comma-separated; none
+  if the request touches none)
 Assumptions:
 Question for human / Missing info / Reason: (whichever applies)
 STATUS: ACCEPT | NEEDS-HUMAN | CLARIFY | REJECT
diff --git a/tests/factory/test_capability_index.py b/tests/factory/test_capability_index.py
new file mode 100644
index 0000000..eb934a1
--- /dev/null
+++ b/tests/factory/test_capability_index.py
@@ -0,0 +1,295 @@
+"""The capability index and the decision index (spec-factory T-0036, issue #75).
+
+Triage names the capabilities a request touches on a `Capabilities:` line, from a capability index
+in its input. The spec writer and critic then receive those capabilities in full, plus the ones
+their spec cites by `specs/<name>/spec.md`, and one index line for every other capability. The
+writer, critic and planner receive the decision-log lines of their ticket and those capabilities,
+and one index line per other ticket. A ticket whose triage output has no `Capabilities:` line keeps
+the whole of both. Black-box through `bin/factory`.
+"""
+from __future__ import annotations
+
+import os
+import subprocess
+from pathlib import Path
+
+import pytest
+import yaml
+
+REPO = Path(__file__).resolve().parents[2]
+BIN = REPO / "bin" / "factory"
+CAPS = ("alpha", "beta", "gamma")
+CITES = "the decisions that name it to the critic and the planner"
+SPEC = "\n".join([
+    "=== proposal.md", "## Problem", "Beta is lax.", "## Evidence", "Read `openspec/specs/gamma/spec.md`.",
+    "## Decisions", "none", "## Risk", "none", "=== design.md", "## Proposed change", "A. Tighten beta.",
+    "=== specs/beta/spec.md", "## MODIFIED Requirements", "### Requirement: The beta part works",
+    "The beta part SHALL work strictly.", "#### Scenario: strict", "- WHEN `true`", "- THEN it exits 0",
+    "=== verification.md", "## Acceptance", "- strict → NEW; today lax", ""])
+
+
+def run(store: Path, *argv: str) -> subprocess.CompletedProcess:
+    env = {**os.environ, "FACTORY_STATE": str(store), "PYTHONDONTWRITEBYTECODE": "1"}
+    return subprocess.run([str(BIN), *argv], capture_output=True, text=True, env=env, cwd=REPO)
+
+
+def ok(store: Path, *argv: str) -> str:
+    cp = run(store, *argv)
+    assert cp.returncode == 0, cp.stderr
+    return cp.stdout
+
+
+def start(store: Path, role: str) -> str:
+    rid = yaml.safe_load(ok(store, "run", "start", "--role", role, "--ticket", "T-0001").strip().splitlines()[-1])["run_id"]
+    ok(store, "run", "compose", rid)
+    return rid
+
+
+def finish(store: Path, rid: str, body: str, status: str) -> None:
+    (store / "runs" / rid / "output.md").write_text(f"{body}\nSTATUS: {status}\nCONFIDENCE: high, fixture\nESCALATIONS: none\n")
+    ok(store, "run", "finish", rid)
+
+
+def text_of(store: Path, rid: str) -> str:
+    return (store / "runs" / rid / "input.md").read_text()
+
+
+def sources(store: Path, rid: str) -> list[str]:
+    return yaml.safe_load((store / "runs" / rid / "meta.yaml").read_text())["input_sources"]
+
+
+def truth(store: Path, cap: str) -> Path:
+    return store / "openspec" / "specs" / cap / "spec.md"
+
+
+DECISIONS = ["2026-10-01 T-0001 OWN-LINE decided for this ticket.",
+             "2026-10-02 T-0007 BETA-LINE beta keeps its default.",
+             "2026-10-03 T-0008 GAMMA-LINE gamma stays read-only.",
+             "2026-10-04 T-0009 OTHER-LINE logs rotate weekly.",
+             "2026-10-06 T-0009 OTHER2-LINE beta-two, beta_x and xbeta2 name other things."]
+
+
+def setup(tmp_path: Path, decisions: list[str] | None = None, others: tuple[str, ...] = ()) -> Path:
+    """A store with T-0001, one more ticket per title in `others`, alpha, beta and gamma, and a log."""
+    s = tmp_path / "state"
+    for n, title in enumerate(("Fixture", *others)):
+        req = tmp_path / f"req{n}.md"
+        req.write_text(f"# {title}\n\nMake beta stricter.\n")
+        ok(s, "ticket", "new", "--file", str(req))
+    ok(s, "init")
+    for c in CAPS:
+        truth(s, c).parent.mkdir(parents=True)
+        truth(s, c).write_text(f"# {c}\n\n## Requirements\n\n### Requirement: The {c} part works\n"
+                               f"{c.upper()}-BODY The {c} part SHALL work.\n\n### Requirement: {c} second\nMore.\n")
+    (s / "decisions.md").write_text("\n".join(DECISIONS if decisions is None else decisions) + "\n")
+    return s
+
+
+def triage(s: Path, caps_line: str | None) -> str:
+    rid = start(s, "triage")
+    finish(s, rid, "Type: feature\nTitle: Fixture\nSummary: Make beta stricter.\n" + (caps_line or ""), "ACCEPT")
+    return rid
+
+
+def build(tmp_path: Path, caps_line: str | None, decisions: list[str] | None = None, others: tuple[str, ...] = ()):
+    """T-0001 through triage (with `caps_line` on its output, or none), writer, critic, approval and
+    planner. Returns (store, {role: run id})."""
+    s = setup(tmp_path, decisions, others)
+    runs = {"triage": triage(s, caps_line)}
+    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+    runs["spec_writer"] = start(s, "spec_writer")
+    finish(s, runs["spec_writer"], SPEC, "READY-FOR-CRITIC")
+    ok(s, "spec", "add", "T-0001", "--from-run", runs["spec_writer"])
+    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
+    runs["critic"] = start(s, "critic")
+    finish(s, runs["critic"], "Findings: none.", "APPROVE")
+    ok(s, "ticket", "transition", "T-0001", "--to", "awaiting-spec-gate", "--by", "t")
+    ok(s, "approve-spec", "T-0001")
+    runs["planner"] = start(s, "planner")
+    return s, runs
+
+
+def index_line(store: Path, cap: str) -> str:
+    return (f"- {cap}, 1 kB, `{truth(store, cap)}`: The {cap} part works; {cap} second\n")
+
+
+# ----- part B: the named capabilities in full, an index line for the rest ------------------------
+
+def test_writer_gets_the_named_capability_in_full_and_an_index_line_for_each_other(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta")
+    text = text_of(s, r["spec_writer"])
+    assert "BETA-BODY" in text and "ALPHA-BODY" not in text and "GAMMA-BODY" not in text
+    head = ("\n## Capability index: current truth not given in full above\n\nThis list is complete: every "
+            "current-truth capability not given in full above has one line here. Open a capability at its path "
+            "before you rely on it. A spec that cites a capability's path, as `openspec/specs/<name>/spec.md`, "
+            "sends that capability in full to the critic, and " + CITES + ", so cite under Evidence each "
+            "capability you open.\n\n")
+    assert head + index_line(s, "alpha") + index_line(s, "gamma") in text
+    assert sources(s, r["spec_writer"]) == [f"runs/{r['triage']}/output.md", "requests/T-0001.md",
+                                            "openspec/specs/beta/spec.md", "decisions.md"]
+
+
+def test_critic_also_gets_the_capabilities_its_spec_cites(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta")
+    text = text_of(s, r["critic"])
+    assert "BETA-BODY" in text and "GAMMA-BODY" in text and "ALPHA-BODY" not in text
+    assert index_line(s, "alpha") in text and f"`{truth(s, 'gamma')}`" not in text
+    assert text.count("sends that capability in full to the critic") == 1
+    assert sources(s, r["critic"]) == ["specs/T-0001/v1.md", "openspec/specs/beta/spec.md",
+                                       "openspec/specs/gamma/spec.md", "decisions.md"]
+
+
+def test_planner_gets_no_current_truth_and_no_capability_index(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta")
+    text = text_of(s, r["planner"])
+    assert "-BODY" not in text and "Capability index" not in text and "spec.md`:" not in text
+    assert sources(s, r["planner"]) == ["specs/T-0001/v1.md", "decisions.md"]
+
+
+def test_an_index_line_rounds_the_size_up_to_whole_kilobytes(tmp_path):
+    s = setup(tmp_path)
+    head = "# {0}\n\n## Requirements\n\n### Requirement: {0} sized\n"
+    for cap, size in (("alpha", 2001), ("gamma", 2000)):
+        truth(s, cap).write_text(head.format(cap) + "x" * (size - len(head.format(cap)) - 1) + "\n")
+        assert truth(s, cap).stat().st_size == size
+    triage(s, "Capabilities: beta")
+    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+    text = text_of(s, start(s, "spec_writer"))
+    assert f"- alpha, 3 kB, `{truth(s, 'alpha')}`: alpha sized\n" in text
+    assert f"- gamma, 2 kB, `{truth(s, 'gamma')}`: gamma sized\n" in text
+
+
+@pytest.mark.parametrize("line, full", [
+    ("Capabilities: `beta`, gamma.", {"beta", "gamma"}),
+    ("Capabilities: beta,gamma", {"beta", "gamma"}),
+    ("Capabilities: beta new delta", {"beta"}),
+    ("Capabilities: none", set()),
+    ("Capabilities:", set()),
+])
+def test_the_capabilities_line_is_split_on_commas_and_spaces_and_keeps_only_existing_names(tmp_path, line, full):
+    s, r = build(tmp_path, line)
+    text = text_of(s, r["spec_writer"])
+    assert {c for c in CAPS if f"{c.upper()}-BODY" in text} == full
+    assert {c for c in CAPS if index_line(s, c) in text} == set(CAPS) - full
+
+
+def test_every_capability_named_leaves_no_capability_index(tmp_path):
+    s, r = build(tmp_path, "Capabilities: alpha, beta, gamma")
+    text = text_of(s, r["spec_writer"])
+    assert all(f"{c.upper()}-BODY" in text for c in CAPS) and "Capability index" not in text
+
+
+def test_the_latest_finished_triage_run_decides(tmp_path):
+    s = setup(tmp_path)
+    triage(s, "Capabilities: beta")
+    ok(s, "ticket", "set", "T-0001", "status=ready-for-triage", "in_flight=[]")
+    triage(s, "Capabilities: alpha")
+    ok(s, "ticket", "transition", "T-0001", "--to", "ready-for-spec-writer", "--by", "t")
+    text = text_of(s, start(s, "spec_writer"))
+    assert "ALPHA-BODY" in text and "BETA-BODY" not in text
+
+
+# ----- part B6: decision lines of this ticket and its capabilities, an index line per other ticket -
+
+def decision_block(store: Path, lines: list[str]) -> str:
+    return ("\n## Decision log (decisions.md): the standing decisions logged against this ticket or naming a "
+            f"capability given in full, read-only. The full log is `{store / 'decisions.md'}`\n\n"
+            + "\n".join(lines) + "\n")
+
+
+def decision_index(store: Path, lines: list[str]) -> str:
+    return ("\n## Decision index: decisions not given in full above\n\nThis list is complete: every ticket with "
+            "a decision not given in full above has one line here. Read a ticket's decisions with "
+            f"`grep ' <ticket id> ' {store / 'decisions.md'}`.\n\n" + "".join(f"{x}\n" for x in lines))
+
+
+def test_each_role_gets_its_ticket_s_and_its_capabilities_decisions_and_an_index_of_the_rest(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta")
+    w = text_of(s, r["spec_writer"])
+    assert decision_block(s, DECISIONS[:2]) in w
+    assert decision_index(s, ["- T-0008 (1 decision, 2026-10-03 to 2026-10-03):",
+                              "- T-0009 (2 decisions, 2026-10-04 to 2026-10-06):"]) in w
+    for role in ("critic", "planner"):
+        text = text_of(s, r[role])
+        assert decision_block(s, DECISIONS[:3]) in text, role
+        assert decision_index(s, ["- T-0009 (2 decisions, 2026-10-04 to 2026-10-06):"]) in text, role
+    for role in ("spec_writer", "critic", "planner"):
+        assert "OTHER-LINE" not in text_of(s, r[role]) and "OTHER2-LINE" not in text_of(s, r[role]), role
+
+
+def test_a_decision_index_line_carries_the_ticket_s_title(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta", ["2026-10-05 T-0002 later", "2026-10-04 T-0002 earlier"],
+                 others=("Rotate the logs",))
+    assert decision_index(s, ["- T-0002 (2 decisions, 2026-10-04 to 2026-10-05): Rotate the logs"]) \
+        in text_of(s, r["spec_writer"])
+
+
+def test_no_kept_line_leaves_only_the_index_and_no_decisions_source(tmp_path):
+    s, r = build(tmp_path, "Capabilities: none", ["2026-10-04 T-0009 OTHER-LINE logs rotate weekly."])
+    text = text_of(s, r["spec_writer"])
+    assert "## Decision log" not in text and "OTHER-LINE" not in text
+    assert decision_index(s, ["- T-0009 (1 decision, 2026-10-04 to 2026-10-04):"]) in text
+    assert "decisions.md" not in sources(s, r["spec_writer"])
+
+
+def test_every_line_kept_leaves_no_decision_index(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta", DECISIONS[:2])
+    text = text_of(s, r["spec_writer"])
+    assert decision_block(s, DECISIONS[:2]) in text and "Decision index" not in text
+
+
+def test_a_whitespace_only_log_still_adds_nothing(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta", ["  "])
+    text = text_of(s, r["spec_writer"])
+    assert "Decision log" not in text and "Decision index" not in text
+    assert "decisions.md" not in sources(s, r["spec_writer"])
+
+
+# ----- part B4: no Capabilities line keeps today's inputs -----------------------------------------
+
+def test_without_a_capabilities_line_each_role_gets_today_s_inputs(tmp_path):
+    s, r = build(tmp_path, None)
+    for role in ("spec_writer", "critic"):
+        text = text_of(s, r[role])
+        assert all(f"{c.upper()}-BODY" in text for c in CAPS) and "Capability index" not in text, role
+    for role in ("spec_writer", "critic", "planner"):
+        text = text_of(s, r[role])
+        assert "## Decision log (decisions.md): standing decisions, read-only\n\n" + "\n".join(DECISIONS) in text
+        assert "Decision index" not in text, role
+    assert sources(s, r["critic"]) == ["specs/T-0001/v1.md", *(f"openspec/specs/{c}/spec.md" for c in CAPS),
+                                       "decisions.md"]
+
+
+# ----- part A: triage gets the capability index and is asked for the line ------------------------
+
+def test_triage_input_lists_every_capability_and_adds_no_source(tmp_path):
+    s, r = build(tmp_path, "Capabilities: beta")
+    text = text_of(s, r["triage"])
+    assert ("\n## Capability index: every capability in current truth\n\nName the capabilities this request "
+            "touches on your `Capabilities:` line. The spec writer receives those in full and this index for "
+            "the rest.\n\n" + "".join(index_line(s, c) for c in CAPS)) in text
+    assert text.index("## Request") < text.index("## Capability index")
+    assert "-BODY" not in text and "-LINE" not in text
+    assert sources(s, r["triage"]) == ["requests/T-0001.md"]
+
+
+def test_triage_input_has_no_capability_index_without_current_truth(tmp_path):
+    s = tmp_path / "state"
+    req = tmp_path / "req.md"
+    req.write_text("# Fixture\n\nA thing.\n")
+    ok(s, "ticket", "new", "--file", str(req))
+    ok(s, "init")
+    assert "Capability index" not in text_of(s, start(s, "triage"))
+
+
+def test_the_triage_prompts_ask_for_the_capabilities_line():
+    ask = ["Capabilities: (names from the capability index, comma-separated; none",
+           "  if the request touches none)"]
+    for p in ("docs/prompts/01-triage.md", "factory/prompts/triage.md"):
+        lines = (REPO / p).read_text().splitlines()
+        i = lines.index(ask[0])
+        assert lines[i - 1].startswith("Evidence:") and lines[i:i + 2] == ask, p
+        assert sum(x.startswith("Capabilities:") for x in lines) == 1, p
+    # the block's own width: every line this change wrote fits in 72 characters
+    assert all(len(x) <= 72 for x in (REPO / "docs/prompts/01-triage.md").read_text().splitlines()
+               if "capabilit" in x.lower())
