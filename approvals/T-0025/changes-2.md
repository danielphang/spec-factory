Changes requested, round 2 (operator delegated; Fable design review round 2: `.factory/answers/design-review-45-46/round-2.md`). Every round-1 finding is RESOLVED. Remaining:

1. N1 (SHOULD-FIX), settled on #45's side: #45 was approved as v5 with its throwaway-store scenario now running `init` from the target root (`(cd $T/tgt && FACTORY_STATE=$T/s $B init ...)`), so it stays true under this spec's layout. Confirm in Tests to change / Risk that no #45 scenario runs `init` from inside a run's scratch directory any more, and keep "Tests to change: none" only if that holds after reading #45 v5 (`.factory/state/specs/T-0024/v5.md`).
2. N2: A.1 keys on `symbolic-ref -q HEAD`. A detached store HEAD skips it. Add the branch-agnostic second condition: also refuse when `instance.find()` from the caller's cwd returns an instance whose own store root equals or contains the toplevel.
3. N3: #45 v5 now says a store with no `tickets/` has no runs in flight. Rely on that, and don't restate it.
4. N4: write #45's fence call as unconditional (a no-op on a new instance), not "for an existing instance".
5. N5: A.3.1's refusal puts the path on one line, or the scenario uses `grep -q`.
