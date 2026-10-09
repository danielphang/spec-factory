# North Star

What the spec factory is for, what it will not trade away, how it decides where effort goes, and where
it is heading. This is the current position. When a ticket would change any of it, the ticket says so
under Decisions and the operator decides at the spec gate. What was tried and dropped is in
`docs/decided-against.md`.

## What it is for

Turn a written request into merged, verified code with as little of the operator's attention as the
work allows, and leave a record of what was asked, what was built, who checked it against what, and
why it was allowed through.

Success is measured as:
- correct changes delivered per batch, not per ticket: a long ticket is acceptable when independent
  tickets progress beside it;
- operator decisions and interventions per change;
- tokens and wall time per change;
- defects that escape to the target, and reverts.

The factory serves its own development (spec-factory) and its targets (today, the Lionbot v3.5 port).

## What it will not trade away

These hold for every change to the factory. A proposal that weakens one names it and is the operator's
decision.

1. **A human approves the spec before code is written.** The spec gate is enforced by the CLI, not by a
   prompt. Efficiency never comes from skipping a human decision: "keep the stops".
2. **Checkers are independent by process.** The critic, code reviewer and verifier run in fresh contexts.
   They never see the author's reasoning, and they cannot change what they judge. Only the authors (spec
   writer, implementer) may keep context across rounds.
3. **Routing and refusals live in the CLI.** Which state comes next, how many rounds, and when a merge is
   allowed are decided by code. An agent can argue past a prompt, not past an exit code.
4. **Nothing merges without verdicts on the same commit.** The gate result, the reviewer's APPROVE and the
   verifier's VERIFIED name one commit, which is the branch tip and contains the integration branch. A
   protected path merges only when the approved spec declares it.
5. **A check that can change a verdict is never cut.** Removing a check that cannot change one is
   pre-approved, provided every refusal the pipeline gives today still fires.
6. **Every stop is a recorded state with a reason.** The store, on its own branch, is the record. Nothing
   that matters lives only in a conversation.
7. **A role's run is untrusted code.** It gets a throwaway HOME, a scratch directory, the store-write fence
   and the tripwire. It never touches live state.
8. **Changes to how roles think are proven before they ship.** A prompt or standards change is replayed on
   real past tickets, comparing tokens, turns and output quality, and the operator accepts it before the
   runtime moves. A harness change passes its own red-green acceptance.

## How it decides where effort goes

The fourteen principles in `docs/principles.md`, each with the incident that taught it, in short:

| Group | Principles |
|---|---|
| Where checking pays | The implementer is the test of the spec. A check runs only where it can change the verdict. Deterministic before judgment. Measure catch beside cost. |
| Separation and record | Fresh context per role, by process. A role's test run is untrusted. Routing and refusals in the CLI. Every stop is a logged state. |
| Scaffold and prose | Size the scaffold to the change. The human-facing sections are for the gate reader. Round 2 reads only what changed. A role never waits on background work, and an empty run parks. |
| Context and sources | Bounded, on-demand context beats complete context. One source per artifact; a copy is generated and checked, or deleted. |

And three working rules that follow from them:
- **Measure before and after.** Every efficiency change states the cost it targets, from the store or the
  transcripts, and is re-measured after it ships.
- **Prefer a script to a prompt.** A rule that a script can enforce becomes a lint, a refusal or a check,
  not more prompt text.
- **A field that never varies is not a signal.** A value every run fills the same way is removed, and
  its replacement must take more than one value in practice.

## Where it is heading

In order. Each line names the issues that carry it.

1. **Correctness under parallel work.** Superseded plans stop blocking (#77). The merge gate checks
   protected paths (#57). Spec changes cannot silently overwrite each other (#58). A spec can be amended
   after planning, with intent checked (#44, #50). The store survives parallel checkers and stopped runs
   (#53, #60).
2. **Cut what each call carries.** Role inputs scoped to the capabilities a ticket touches (#75, #78).
   Bounded reads for every role, enforced (#76). An external driver with a lean system prompt and no clerk
   (#65), which also carries per-role effort, the chat-relay fix and per-step titles.
3. **Size the work to the change.** Intake sized to the change (#64). Questions classified before they
   reach the operator (#79).
4. **Measure continuously.** `factory stats` for catch beside cost (#70), and the retro on top of it
   (#42), whose status #83 settles.
5. **Make the record portable.** Reusable specs across re-ports, with decisions tagged product or
   implementation (#54).

What is parked, and why, is in the backlog review of 2026-10-09 (`dev/issues.md`).
