# Decided against

Approaches the factory tried, considered, or was offered, and dropped. Each entry says what it was, why
it was dropped, the evidence, and what would reopen it. Read this before proposing something that
sounds new: it may have been measured already. The current position is `docs/north-star.md`.

| Date | What | Why it was dropped | Evidence | Reopen if |
|---|---|---|---|---|
| 2026-10-04 | Take recommended defaults instead of parking for the human | Removes the stops the operator relies on to steer | Operator ruling on the retro trial | Never by a role; only an operator's standing delegation |
| 2026-10-04 | Store records committed on the integration branch | Every store commit moved main and forced catch-up runs | 6+ catch-up runs, about 1M tokens each (#46) | — (replaced by the store branch) |
| 2026-10-04 | An implementer editing an existing test on its own judgement | A test the spec does not list is the spec's guardrail | #40's design | A test an earlier sibling added is allowed, checked by the harness |
| 2026-10-04 | Labelling every empty role output a "budget kill" | No budget is enforced; the label hid the real cause | Three stalls from roles waiting on background work (#41) | A real time or token budget is built |
| 2026-10-04 | The code reviewer running the test suite | The verifier runs it on the same commit; the reviewer stalled waiting on it | #41; reviewer changed 4 of 94 outcomes (Discussion 71) | — |
| 2026-10-05 | Letting `--accept-harness` past the store-write fence | It guesses that a run is dead; a wrong guess moves the runtime under a live run | Operator, on #53 | Run ownership is recorded (#53 B) |
| 2026-10-05 | Batching clerk calls inside the Workflow tool | The operator chose removing the clerk with an external driver | #24 B → #65 | #65 proves unworkable |
| 2026-10-05 | Headless `claude -p --bare` for roles | Needs a separate API key; does not use the subscription | Claude Code docs, 2026-10-05 | Billing model changes |
| 2026-10-07 | A per-commit human approval for every protected-path change | 19 of the last 20 merges touched a protected path; nearly every merge would wait | #57 triage; operator chose the approved Risk list as authorization | Self-modification needs a stricter class (option 3, left open) |
| 2026-10-07 | Reading every backticked path in Risk as a declaration | Risk sections also list paths they promise not to touch | #57 spec | — |
| 2026-10-07 | A long-running critic or reviewer session | Judges favour familiar text; a checker that has formed a view misses more | Discussion 71 (self-preference and confirmation-bias research) | — |
| 2026-10-08 | Limiting the critic: at most 2 paths and 1 command per claim, no builds | No token saving (its cost is mostly fixed start-up context) and it missed real findings | #73 replay: critic 0.71→0.72M, 1.0→0.93M, 1.67→1.63M; two of three verdicts weaker; reverted by #74 | — |
| 2026-10-09 | Scoping the decision log by capability | No decision names a capability; a cross-cutting standing decision was filtered out and a writer broke it | #75 replay (Nanobot T-0032 missed T-0003); #78 | Decisions are tagged (#54) in a way that cannot drop a cross-cutting rule |
| 2026-10-09 | Never block on the human; proceed, then present (pstack) | The spec gate is where the operator's decision and the record live | Discussion 82 | — |
| 2026-10-09 | Independence from model diversity rather than context separation (pstack) | Self-preference is about familiarity of text, which fresh context addresses; one model family here | Discussions 71, 82 | Several model families are available and a pair trial (#64 note) shows a gain |
| 2026-10-09 | The author judging its own reviewers' findings (pstack) | The self-preference setup the research warns about | Discussion 82 | — |
| 2026-10-09 | Ambitious restructuring in the per-ticket review (thermonuclear) | Builds beyond the ticket; the coding standard keeps changes to the sub-ticket | Discussion 82 | As a periodic sweep that files tickets, never per ticket |
| 2026-10-09 | Deleting nearly all code comments (pstack) | Comments that say why are kept by the coding standard | Discussion 82 | — |
| 2026-10-09 | Reading the principles in full on every role turn (pstack) | A measured per-turn context cost the factory is cutting | Discussion 82; #24, #75 | — |
| 2026-10-08 | A learned test selector | Not worth it at this volume; hand-scoped gate commands (#48) do the job | Discussion 71 (Machalica et al.) | Gate time dominates again at much higher volume |
