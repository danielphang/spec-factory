## Spot checks (round 2; base `3a3f58c`, clean clone under this run's scratch, fresh HOME)

Changed text only, per the convergence rule.

Paths and symbols: `tests/factory/test_instance.py:21` is `STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")`, and `cli()` at `:25-27` builds the environment from `os.environ` minus `STRIP` and then applies `**extra`, so an explicit `FACTORY_DISPATCH="1"` argument wins over the strip, as Tests to change says. `:271-274` is `test_composed_input_opens_with_the_instance_context` with its `cli(target, "run", "compose", run.name)` call. `factory/instance.py:141-166` `guard()`: uncommitted edits refused first, then `--accept-harness` rewrites the lock and logs `harness.accepted` inside the function, then the lock check; so the new Decisions bullet (fence before the lock, else a fenced `--accept-harness` would write before it was refused) matches the code. `factory/cli.py:1202` is the `instance.guard(...)` call in `main()`. `docs/changelog.md` still ends at entry 51.

Acceptance command run on base: the new scenario "A marked write from a harness checkout with an uncommitted edit is still refused" printed `exit=2 lock=1 store=unchanged`; stderr's first line was `harness <clone> has uncommitted changes:`, as the REGRESSION line in Acceptance states. (My exported `TMPDIR` was not honoured by `mktemp` in the sandbox, so the scenario's scratch target landed under the system temp directory; it is a fresh git repository either way and no protected path was touched.)

The prototype-side results (fence refusal from a dirty checkout, `1 failed, 253 passed` with the marker exported before the one test is marked) are the writer's. Round 1 accepted the prototype's shape from the code; the v3 additions follow from the same code, so I accept them again.

## Prior findings (round 1)

- [BLOCKING] 6 Decisions, first bullet: RESOLVED. Problem now glosses instance, instance B, current truth and `decisions.md` before Decisions uses them; Evidence glosses "closed as applied"; Decisions no longer cites "Answer 1" or a bare "#37", and names the Driver session as the one that runs instance A. Read in order as the gate operator, every term of art in Decisions now has an earlier gloss.
- [NIT] 2 Tests to change (`STRIP`): RESOLVED. `FACTORY_DISPATCH` is added to `STRIP` in the same file, with a reason and a prototype result for each direction; Risk lists the tuple under guardrail paths.
- [NIT] 5 design.md A.4 / Risk (fence before the lock): RESOLVED. Design part C adds the sentence; Decisions gains the bullet with the rejected ordering and why; a new REGRESSION scenario checks that a marked write still meets the lock, and it prints the stated result on base.

## Findings

No blocking issues. No new findings on the changed text.

## Out-of-scope observations

- Carried from round 1, unchanged and accepted by the writer: `t0024-e2e.mjs` runs clerk commands with the environment unchanged, so an exported marker would let it pass without part B; the first scenario fails in that case, so the set still catches it.

STATUS: APPROVE
CONFIDENCE: high, all three round-1 findings resolved as described, the new lock scenario and the `STRIP`/`cli()` claims checked on a clean clone of base; only the prototype-side numbers are taken from the writer.
ESCALATIONS: none
