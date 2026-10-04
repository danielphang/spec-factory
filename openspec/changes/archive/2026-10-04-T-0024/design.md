## Proposed change
**A. The fence, in `factory/cli.py`.**
1. Add the read-only set as `(command, subcommand)` pairs: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths`.
2. "Runs in flight" are the union of the `in_flight` lists over `tickets/*.yaml` in the store in use. Sub-tickets are ticket files too. A store with no `tickets/` directory yet (an instance whose store is not created) has no runs in flight.
3. Add one fence function `fence(inst, cfg, root)`. It does nothing unless the store in use is the instance's own (`instance.is_own_store`). Then, in this order:
   - **Location.** Let `own = instance.own_state_root(inst, cfg)` and `cwd = instance.caller_cwd()`. If `cwd` lies under `own / "runs"` or `own / "worktrees"` (`Path.is_relative_to`; both paths are already resolved), raise `Refused`. This holds whatever `FACTORY_DISPATCH` says and whether or not a run is in flight.
   - **Marker.** If `os.environ.get("FACTORY_DISPATCH") == "1"`, return.
   - **In flight.** If at least one run is in flight, raise `Refused`.

   Both refusals use `role runs may not write the live store (<detail>); use a throwaway FACTORY_STATE`. The detail is `<own store>; called from inside its runs/` (or `worktrees/`) for the location rule, and `<store>; in flight: <comma-separated run ids>` for the in-flight rule. Neither names the marker. `main()`'s existing `Refused` handler gives exit 2, stderr and `{"ok": false, "error": ...}`.
4. In `main()`, after `root = store.state_root(cfg)` (`factory/cli.py:1201`) and before `instance.guard(...)`, call `fence(inst, cfg, root)` when the command is not in the read-only set or `--accept-harness` was given. Calling it before the guard means a fenced `--accept-harness` rewrites no lock.
5. In `init_cmd`, call `fence(inst, cfg, root)` on the line right after `root = instance.state_root(inst, cfg)` (`factory/cli.py:870`). For an existing instance this comes before any write: `context.md`, `harness.lock`, agent files, `.gitignore`, `.gitattributes`, the spec store. A brand-new instance has no tickets, so `init` on a new repository is not fenced by the in-flight rule. Keep it to these two call sites, so the store-branch change (#46) can rebase on them.
6. Add the new behaviour's tests in a new file, such as `tests/factory/test_live_store_guard.py`. Cover both rules: an unmarked write with a run in flight, a marked write from a run's scratch directory and from under `worktrees/`, and a write from a finished run's scratch directory with nothing in flight. Its subprocess helper drops `FACTORY_DISPATCH` from the inherited environment, so a runner that exported it cannot change the result.

**B. The marker, in the workflow scripts.** In `factory/workflows/intake.js:26` and `factory/workflows/build.js:21`, start `ENV` with `'FACTORY_DISPATCH=1'`. Then `BIN`, and with it every clerk command, carries it unconditionally. The clerk needs no change; it already runs from the harness checkout.

**C. Documents.**
- `docs/design.md`: a new paragraph after "**Tripwire on live files.**", titled "**Only the dispatcher writes a live store during a run.**". Like its neighbours it is one line. It states:
  - the location rule: a write run from inside the own store's `runs/` or `worktrees/` is refused, marker or not, run in flight or not;
  - the in-flight rule: live store only, in flight only, the read-only list, `--accept-harness`;
  - the `FACTORY_DISPATCH=1` marker, set by both workflow scripts, and the operator's per-command use of it;
  - the refusal: exit 2, writes nothing, names a throwaway `FACTORY_STATE`, never names the marker;
  - that it guards against accidents and is not isolation;
  - that the fence is checked before the harness lock, so a fenced command never reaches the lock or its `--accept-harness`, and a marked command still meets the lock unchanged.
- `docs/changelog.md`: one new entry, numbered after the current last entry (52 if nothing else lands first). It names `FACTORY_DISPATCH`, "in flight", `runs/` and `worktrees/`, the throwaway store and exit 2. It says that parts B and C of the request were declined, and why.
- `README.md`:
  - In "Where a human decides", the first paragraph under the heading, before the table, opens with this bold sentence on its own line: "**While a run is in flight, put `FACTORY_DISPATCH=1` in front of every store write you make.**" The paragraph then:
    - shows the exact command form in a code block, for example `FACTORY_DISPATCH=1 $RUNTIME/bin/factory decision add T-n "<line>"`;
    - says that without it the write is refused with exit 2, and that the refusal text deliberately does not name the marker, so that a role reading it is not told how to get past it; its "use a throwaway FACTORY_STATE" advice is for roles, not for the operator;
    - says to never export the marker, because every role run started from that shell would inherit it;
    - says to run store writes from the repository root: from inside the store's `runs/` or `worktrees/` every write is refused and the marker does not help;
    - says that a run left in flight by a stopped workflow is cleared with `FACTORY_DISPATCH=1 $RUNTIME/bin/factory run finish <run> --status-override KILLED`.
  - A "Built" bullet for the fence, saying it is tested and has not yet fired on a real ticket.
  - In "How a ticket moves", replace the sentence at `README.md:102-103` ("While that final run is in progress the ticket's record does not list it as in flight, so a ticket at this step can look idle for a few minutes.") with one saying that while that final run is in progress, the ticket's record lists it as in flight, like any other run.
  - In "Not built", rewrite the "Current truth for the factory itself" bullet: the spec store holds only the capabilities that tickets have changed since it was created, not the whole factory. Remove "never entered it" and quote no count, since each archive changes it.
  - Bump the status date, per "Maintaining this page".
- `docs/prompts/` and `factory/prompts/` do not change.

## Tests to change
- `tests/factory/test_instance.py::test_composed_input_opens_with_the_instance_context` (line 271; the call is at line 274). Its `run compose` call stands for the dispatcher's own command. It runs on a scratch instance's live store, from the target's root, while the triage run that `_start_triage` just started is in flight, so the in-flight rule refuses it. Change: pass `FACTORY_DISPATCH="1"` to that one `cli(...)` call. Verified on the prototype: with the marker exported and this change reverted, the file gave `1 failed, 21 passed`; with it, the suite gave `254 passed`.
- The same file's `STRIP` tuple (`tests/factory/test_instance.py:21`), the variables its `cli()` helper drops from the inherited environment. Add `"FACTORY_DISPATCH"` to it. Without this, a runner shell that exported the marker would make the test above pass with or without its change, and every own-store case in the file would skip the in-flight rule. An explicit `FACTORY_DISPATCH="1"` argument still wins, because `cli()` applies its arguments after the strip. Verified on the prototype: `254 passed` with the marker exported.
- No other existing test changes. No existing test runs a write on its own store from inside that store's `runs/` or `worktrees/`; the suite passed in full on the prototype.

