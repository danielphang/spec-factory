## Problem
Three of the factory's agent roles get the whole spec store with every run, whatever their ticket touches. The factory is a pipeline of AI agents that turns a request into a merged change. Each agent, called a role, works from one input file that the harness composes for it. The spec writer turns an accepted ticket into a spec. The critic reviews that spec, and the planner splits an approved spec into sub-tickets. The spec store holds two things. Current truth is one document per capability saying what that part of the system does now. The decision log, `decisions.md`, holds the standing decisions that later tickets must follow.

Today the writer and the critic receive every capability's document and the whole decision log. The planner receives the whole log. A ticket usually touches one or two capabilities. An agent re-sends its whole input on every model call of a run, and a writer run makes a median of 45 calls. So the unused part is paid for many times over, and it crowds out the part the agent needs. The cost grows with every closed ticket, because closing a ticket folds its spec into current truth. A writer input composed on the Nanobot store today would carry about 480 kB of store content before the ticket itself.

The change works in three steps:
- Triage, the role that accepts a request, names the capabilities the request touches.
- The writer and critic receive those capabilities in full. Every other capability gets one line in an index, with the path of its document.
- The decision log is cut the same way for all three roles.

Nothing is hidden. The index is complete, and a role opens anything in it by its path.

This change alone does not meet the request's targets, a mean writer input below 40 kB and a maximum below 100 kB on the Nanobot store. The rest of a writer input can be up to 152 kB by itself: the request, triage's output, and on later rounds the writer's own previous output and the critic's findings. Decisions below records this.

## Evidence
Units: kB is 1,000 bytes. Checked on `~/dev/spec-factory`, `main` at `9a25809`. The Nanobot store (`~/dev/nanobot-upstream/.factory/store`) was read only.

What each role receives today, from `factory/compose.py`:
- `current_truth` (`:33-37`) returns every `openspec/specs/*/spec.md`.
- `add_truth` (`:168-170`) adds each of them in full. `add_decisions` (`:172-176`) adds the whole `decisions.md`.
- The `spec_writer` branch (`:182`, calls at `:187-188`) and the `critic` branch (`:203`, calls at `:205-206`) call both.
- The `planner` branch (`:224`, call at `:229`) calls only `add_decisions`. The planner gets no current truth today. The request says it does, and the triage ticket corrected this.
- The `triage` branch (`:177`) adds only the request.

README already describes the writer's input as "current truth for the capabilities it touches" (`README.md:85`). That is not what runs.

This run's own input (`run-0337-spec_writer/input.md`) is 171.6 kB:
- 123.9 kB is current truth for all 10 capabilities on this store.
- 32.4 kB is the decision log.
- 15.3 kB is the briefing, the ticket and the request.

Store contents measured today:

| Store | Capabilities | Current truth | `decisions.md` | Decision lines | Tickets with decisions |
|---|---|---|---|---|---|
| spec-factory | 10 | 123 kB | 32.4 kB, 97 lines | 97 | 10 |
| Nanobot | 22 | 410 kB | 71.4 kB, 240 lines | 240 | 26 |

Every capability spec on both stores opens with `# <name>` and then `## Requirements`, with no purpose paragraph. The `### Requirement:` heading lines add up to 4.4 kB on this store and 7.2 kB on Nanobot. Each decision is one line, `<date> <ticket id> <text>`.

Projected effect. A prototype in this run's scratch directory (`measure.py`) did the following for every spec writer run on each store:
- It cut the current-truth and decision-log sections out of the run's recorded `input.md`. What remains is "the rest".
- It added back what this spec sends, using today's store. The capabilities sent in full stand in for triage's list: the existing capabilities that the ticket's spec versions cite as `specs/<name>/spec.md`, less any the ticket itself created. The decision lines sent in full are those logged against the ticket or naming one of those capabilities. Both indexes are added.
- "Today" is the rest plus today's whole store, which is what the same run would receive now.

| Store, runs | Today: mean / max | This change: mean / max | Capability index | Decision index |
|---|---|---|---|---|
| Nanobot, all 38 writer runs | 516 / 635 kB | 74 / 167 kB | 8.1 kB | 4.1 kB |
| Nanobot, 18 runs of the last ten tickets (T-0016 to T-0032) | 521 / 635 kB | 101 / 167 kB | | |
| spec-factory, all 61 writer runs | 184 / 248 kB | 59 / 161 kB | 4.6 kB | 1.8 kB |
| spec-factory, 16 runs of the last ten tickets (T-0027 to T-0036) | 186 / 235 kB | 81 / 161 kB | | |

The inputs as they were recorded at the time were smaller, because the stores were smaller then: Nanobot mean 104.6 kB and max 425.6 kB; spec-factory mean 61.6 kB and max 221.7 kB. The triage ticket's figures, 102 KiB and 416 KiB, match the Nanobot figures in kibibytes.

Why the targets are missed:
- Nanobot `run-0121-spec_writer` has 152.1 kB of rest with no current truth in it. That is a 74-line request, two answers, and the writer's own previous output re-sent after a NEEDS-HUMAN answer.
- One capability, `cron-agent-runs`, is 72.9 kB by itself. It is sent in full to every ticket that touches it, for example `run-0291-spec_writer` (T-0032): 63.5 kB of rest plus 72.9 kB.

Current behaviour, from the fixture in the first scenario of `specs/role-inputs/spec.md`, run on `main`. The fixture's T-0001 has three capabilities, alpha, beta and gamma. Its triage output says `Capabilities: beta`, and its spec cites gamma's path.
- Writer and critic each receive all three capability bodies and all four decision lines. No input contains the absolute path of a capability's spec or of `decisions.md`: `W: alpha=1 beta=1 gamma=1 alpha-index=n gamma-index=n cites=0` and `W: own=1 beta-line=1 gamma-line=1 other=1 indexed= log-path=n grep-cmd=0`. No input carries either index's instruction sentence.
- Triage's input lists no capability: `triage: alpha-index=n beta-index=n gamma-index=n bodies=0 decisions=0 asks=0`.

`(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` on `main`: `364 passed in 158.37s`.

The tests that pin today's inputs compose without a triage run, so no triage output exists. They are `tests/factory/test_spec_store.py:54-71` and `:281-293`, `tests/factory/test_decision_log.py:200-237`, and `tests/factory/test_shepherd.py:40-48`. No test or prompt contains a line starting `Capabilities:` (`grep -rn Capabilities tests/ factory/ docs/design.md README.md` prints nothing).

The live-store fence is the guard that refuses store commands while a role run is in flight. It exempts only a fixed read-only list (`factory/cli.py:1563`). A new `factory spec show` would have to join that list. It would also have to find the instance from the role's working directory (`factory/instance.py:56-64`).

The harness already points roles at a full file by its path. Each planner, implementer and checker input names the full spec's absolute path in the heading of its cut copy (`factory/compose.py:160-163`).

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

