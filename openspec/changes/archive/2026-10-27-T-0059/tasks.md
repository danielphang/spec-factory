T-0059.1 / `factory truth check` replays every current-truth scenario, and the gate runs it
Depends on: none
Parallel-safe: yes

Parent: T-0059, approved spec v4. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time
- The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed
- --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused
- Capabilities run at the same time
- Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped
- On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped
- The implementer's worktree folds the same deltas
- From the integration branch only an open ticket's delta with a merged sub-ticket is folded
- A folded delta that no longer applies is refused, naming its ticket, and nothing runs
- truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing
- truth check refuses --accept-harness and names config
- The instance's last gate command is the truth check on the integration checkout's store
- The truth check on this checkout reports no failure in the capabilities this change restates
- README, the design doc and the changelog describe the truth check
- README, the design doc and the changelog describe the refusal route
- Implementer and verifier run prompts carry the declared-path rule
- Status transitions write the same events and history entries
- Spec pinning and planner-run refusals keep their text
- The dispatcher parks a refused store command with the same reason
- The spec parser gives the same result as the base on every spec in the store
- The refactored harness has no unused imports or variables
- The harness suite passes and no existing test file changes
- The drift checks live in factory/drift.py
- The shared helpers and the live-store fence live in factory/common.py
- Instance and store setup live in factory/setup.py
- The gates live in factory/gates.py
- The human decisions live in factory/human.py
- factory/cli.py keeps the parser, the entry point and the role list, in under 910 lines
- Unmarked writes from inside the target are refused while a run is in flight, init included
- The refusal names the throwaway store and not the marker
- A harness acceptance is refused while a run is in flight
- A launch copy is written unmarked while a run is in flight, and the target is unchanged
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance
- Without the flag paths and stats still run under another lock, and config still accepts a revision
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
