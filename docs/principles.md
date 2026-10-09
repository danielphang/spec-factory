# Principles

Fourteen rules the spec factory has learned about where effort pays, each from an incident in its own
record. This page is for the operator and for anyone writing a ticket that changes the factory. It is
not for role prompts: no role reads it. Read it before proposing a change, and name any principle the
change weakens under the spec's Decisions.

Each principle states the rule, the incident that taught it, the outside research that tested it, and
the mechanism that implements it today. Issue numbers refer to this repository's GitHub issues; their
changelog entries are in `docs/changelog.md`. Counts are from both factory stores on 2026-10-07 and
10-08. The research notes are Discussions 71 and 82 (github.com/danielphang/spec-factory/discussions).

## Where checking pays

### 1. The implementer is the test of the spec.

Implementation is the first step where a spec meets something that can fail. Across both stores,
implementers stopped as BLOCKED 18 times and verifiers returned SPEC-DEFECT 5 times, nearly all for
defects in the spec, the plan or a dependency. The critic sent a spec back for a purely mechanical
reason once in 19 revisions. So the way to find what a spec got wrong is to put it in front of an
implementer sooner, not to add rounds before one.
External test: Olausson et al., ICLR 2024, found that self-repair is limited by the model's own
feedback, and that an external signal such as execution gives far larger gains
(https://proceedings.iclr.cc/paper_files/paper/2024/file/9ddc141bdbf9d1db510cefff56c586ad-Paper-Conference.pdf).
Implemented by: the implementer's BLOCKED status, which parks the piece for a ruling
(`factory/prompts/implementer.md`); the one-piece path that skips the planner (#48,
`factory/workflows/build.js`). Planned: intake sized to the change (#64).

### 2. A check runs only where it can change the verdict.

A check that cannot change the outcome is cost. Two of six suite runs per build could change
anything (#31). Gate commands ran on changes outside their paths (#48). The code reviewer ran the
suite the verifier also ran, and three times in one day it ended its turn waiting for that run and
returned nothing (#41). The rule: a role that only reads does not run suites, and the suite runs once
per commit, in the role whose verdict depends on it.
External test: predictive test selection at Facebook caught 99.9% of faulty changes with a third of
the dependent tests, halving test cost (Machalica et al., 2018,
https://engineering.fb.com/2018/11/21/developer-tools/predictive-test-selection/).
Implemented by: regression checks and gates once per change (#31); `paths:` on a gate command, and
the gate skips it when the diff touches none of them (#48, `gate_commands` in `instance.yaml`); the
reviewer's WHAT YOU RUN section and its input, which says the verifier runs the gate commands (#41,
`factory/prompts/reviewer.md`, `factory/compose.py`); the critic's PROCESS section, which runs no test
suite (#73, kept by #74, `factory/prompts/critic.md`).

### 3. Deterministic before judgment.

If two runs on the same input could disagree, the check is for a model. Otherwise it is a script, and
it runs first. STATUS lines are parsed by their labels, not judged (#1). The clerk relays a command's
raw output and its exit code (#2).
External test: Google's Tricorder found that analysers above about 10% effective false positives get
dismissed by developers (https://research.google.com/pubs/archive/43322.pdf). LLM judges show position
bias (https://aclanthology.org/2025.ijcnlp-long.18/). So a lint must stay under that false-positive
rate, and a model never re-judges what a script settled.
Implemented by: `factory/status.py`; the store CLI's refusals with exit 2. Planned: a role-output
contract module (#68) and a spec lint run before the critic (#67).

### 4. Measure catch beside cost.

A checker that never disagrees with the author is cost, and it stays invisible until counted. The
code reviewer changed the outcome in 4 of 94 runs, with 1 BLOCKING finding in total.
External test: 14% of human code-review comments address defects (Bacchelli and Bird, ICSE 2013,
https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/ICSE202013-codereview.pdf).
Automated reviewers recall 20 to 57% of defects (https://arxiv.org/html/2603.23448v2).
A field every run fills the same way is not a signal: every recorded CONFIDENCE is `high` or null. Its
replacement must vary in practice: the evidence ladder (#79 C) says whether a finding was stated,
pointed at, shown, run or reproduced. An unenforced claim, like the retro's "mandatory" status with zero
runs (#83 B), is a documentation defect, not a rule.
Implemented by: nothing yet beyond `factory/cost.py`, which reports cost only and double-counts.
Planned: `factory stats`, catch rate and cost by role (#70); the evidence ladder (#79).

## Separation and record

### 5. Fresh context per role, enforced by process.

The critic never sees the spec writer's reasoning because it runs as a different process, not because
a prompt asks it to forget. Sharing has a price: when parallel runs shared one scratchpad, a verifier
mixed two checkouts into one result (#35).
External test: model judges score familiar, low-perplexity text higher, and stronger models more so
(Wataoka et al., 2024, https://arxiv.org/pdf/2410.21819). Models do not self-correct reasoning without
external feedback. So a writer or implementer may keep its conversation across rounds; a critic or
reviewer may not.
Implemented by: each run is a fresh agent that sees only the inputs `factory/compose.py` declares for
its role; each run has its own scratch directory (#35). The external driver (#65) must keep checkers
fresh per round if it adds a resume option.

### 6. A role's test run is untrusted code.

A role's tests overwrote the live chat bot's permission file (#36). A spec writer's test run
initialised the factory's own store from inside its scratch directory (#45).
External test: nine production-data deletions by coding agents in 14 months, about half with
permission prompts on; the root cause was credential scope, not model judgment
(https://adversa.ai/blog/ai-coding-agent-incidents/). So scope what a run's credentials can reach
before scoping its filesystem.
Implemented by: every command wrapped with a fresh temporary HOME (`run_env`, `factory/compose.py`);
the tripwire on live files (#38, `factory/tripwire.py`); the store-write fence (#45); the store on
its own branch (#46). Planned: a sandbox or a separate user per run (#37), credentials first.

### 7. Routing and refusals live in the CLI.

An agent can talk past a rule in a prompt. It cannot talk past an exit 2. So which state a ticket may
move to, how many rounds it gets, and when a merge is allowed are decided by the store CLI, never by a
prompt or by the clerk.
External test: reasoning-based guardrails fall to simple attacks (https://arxiv.org/pdf/2510.11570).
Enforcement belongs between the decision to call a tool and the call
(https://arxiv.org/pdf/2607.08028).
Implemented by: the routing table (`routing` in `instance.yaml`) and the guards in `factory/cli.py`:
`ticket transition`, `run start`, `merge`; the merge gate refuses a changed protected path the approved
spec does not declare (#57, merged, live at the next runtime move).

### 8. Every stop is a logged state with a reason.

A build that exits silently leaves no one to act. Six approved tickets stalled with no record of why
(#33). A checker's park was labelled a harness bug (#18). A park is a state with a reason and the
state it stopped in, not a failure.
External test: production agent frameworks keep the event log as the one source of truth (the
OpenHands SDK; Discussion 69).
Implemented by: the `parked` state with `parked.reason` and `parked.from` (`factory/store.py`); the
append-only log, `log/<month>.jsonl`; park reasons that always end with the failing command's error
(#39).

## Scaffold and prose

### 9. Size the scaffold to the change.

Nine of thirteen specs planned so far got exactly one sub-ticket, after a planner run of about 72
seconds (#48). A 17-line change spent 27 minutes in intake (#64).
External test: a minimal harness reaches 74% or more on SWE-Bench Verified (mini-swe-agent). Imposed
plan phases hurt when they do not match the model's own strategy
(https://arxiv.org/html/2604.12147v1). Tool overhead slowed experienced developers by 19% on familiar
tasks (METR 2025). The limit: add scaffold only where the model cannot gather the context itself.
Implemented by: the one-piece path that skips the planner (#48). Planned: intake sized to the change,
bounded or architectural (#64).

### 10. The human-facing sections are for the gate reader.

An approved spec's Problem section needed a translation before the operator could read it (#11).
Most of the critic's BLOCKING findings are now about readability: 14 of 16 on this repository. The
writing standard is the fix, not more rounds.
External test: most human review comments are about readability and knowledge transfer, not defects
(Bacchelli and Bird, above). Open question: does a readability pass earn its cost on the most
expensive model, beside a lint and the implementer's BLOCKED?
Implemented by: `docs/writing.md`; critic rubric item 6 (`factory/prompts/critic.md`). Planned: a
readability-pass experiment on the bounded path, measured by #70 (#72 part B.4).

### 11. Round 2 reads only what changed.

A critic's second round reviews whether its earlier findings were resolved, and what changed, rather
than the whole spec again. A role asked a second time receives its own earlier output (#3).
External test: reviewers' detection collapses past 400 lines and 90 minutes (SmartBear and Cisco,
https://static1.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf). But
framing a change as bug-free cuts detection by 16 to 93%, almost all through missed defects
(https://arxiv.org/html/2603.18740v1). So keep the rule and keep the escape clause for a new BLOCKING
finding on unchanged text. Do not strengthen the framing.
Implemented by: the critic's CONVERGENCE section (`factory/prompts/critic.md`); a round-2 critic
receives a diff from the previous version when it is smaller (#24 part C, `factory/compose.py`).

### 12. A role never waits on background work, and an empty run parks.

A role that ends its turn while its own command still runs returns nothing (#41). A run's empty
output used to be recorded as a budget kill, wrongly (#18, #41): the harness enforces no time or token
budget, so "budget kill" now means only a run a person recorded as killed.
Implemented by: the preamble's rule to run every command in the foreground and wait for it
(`factory/prompts/preamble.md`); `run finish` records an empty output as EMPTY-OUTPUT, retried once,
then parked, with the agent's last message kept (#41, `factory/cli.py`, both workflow scripts).

### 13. Bounded, on-demand context beats complete context.

A role gets what the ticket touches and an index of the rest, and opens more by path. The writer's
input averaged 102 KB on Nanobot (max 416 KB), re-sent on a median 45 calls; it read 111 whole files.
External test: SWE-agent (Yang et al., NeurIPS 2024): a 100-line window scored 18.0% against 12.7% for
the whole file; a search capped at 50 results, 18.0% against 12.0%. The refusal is part of the
interface. The limit: a cross-cutting rule must never be filtered out (#78).
Implemented by: trimmed downstream inputs (#24 C); reading rules (#73); capability-scoped inputs with
the whole decision log (#75, #78, live at the next runtime move). Planned: an enforcing hook (#76, #65).

### 14. One source per artifact; a copy is generated and checked, or deleted.

Each role prompt lives in three hand-synced places (`factory/prompts/`, `docs/prompts/`, the design
doc's role blocks), and two already differ (`round 2` against `round {2}`). pstack's design red flags
name it: keep one and derive the others, or fail the build when they disagree (principle 3).
Implemented by: the harness lock, for the runtime checkout. Planned: one prompt source (#83 C).

## Spiking: who vets an approach

Grounding a claim the spec makes (a path exists, an acceptance command fails on the base) is the
critic's job, with a floor of two cited paths and one acceptance command and no ceiling. It may run a
small scratch check to confirm a finding, never a test suite (principle 2). Vetting whether a whole
approach works is implementation: a critic's trial is self-repair's weak signal, an implementer's is
execution feedback (principle 1). So vetting a whole approach belongs to the spec writer during investigation, with
its output in Evidence, or to a spike ticket on #64's spike path, run by an implementer and recorded
as a decision. A cap of two paths and one command per claim with no builds (#73) saved the critic no
tokens on a three-ticket replay and missed real findings, so #74 removed it.

## Candidates

**A question a run can answer by running something is not the human's to answer.** From pstack's
router: 30 of 82 parks were NEEDS-HUMAN from triage, but how many were observable facts is not yet
measured. #79 A applies it and records each question's kind; when `factory stats` (#70) shows the
NEEDS-HUMAN share before and after, it becomes principle 15 or is dropped.
