## Escalations

1. **An existing test now fails, and this sub-ticket is not allowed to change it. A human must decide the fix.**
   Decide: allow the one-line test change proposed below, or exempt `config` from the lock check. I recommend the test change.
   - What breaks. Part C.2 of this sub-ticket says every command except `init` and `paths` exits 2 when "the lock is missing". The lock is the instance's `harness.lock`, which records the harness revision that instance accepted.
   - The failing test is `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides`, at line 240. It was added by an earlier sub-ticket, T-0012.3.
   - The test builds an instance directory `alt` from only `instance.yaml` and `context.md`. It writes no `harness.lock`. It then runs `config` twice on that instance's own store: first with `FACTORY_INSTANCE=alt`, then with `FACTORY_REPO=target`.
   - Under C.2 the first call now exits 2. It prints `harness fe6303c56536389c668e37ccba0e73b98077d44e is not the revision this instance accepted (none); rerun with --accept-harness fe6303c… to accept it`. The `(none)` means `alt` has no accepted revision, because it has no lock file. The test then fails with `assert 2 == 0` (line 247): it expected exit 0 and got exit 2.
   - Why this needs a human. The sub-ticket says "Tests to change: none". It also requires the check harness-suite-passes-after-uv-sync to report no `failed`. Both cannot hold while C.2 stands.
   - Proposed resolution: add this test to "Tests to change", with one line added after `(alt / "context.md").write_text("x\n")`:
     `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`
     The line copies the target's lock file into `alt`. I applied it temporarily, and the test passed: `1 passed, 21 deselected` means the one selected test passed. I then reverted it with `git checkout tests/factory/test_instance.py`. The branch does not carry it.
   - Rejected: exempting `config` from the lock. It contradicts C.2's "every command except `init` and `paths`", so I did not do it.
2. **Informational: four NEW criteria passed vacuously at base.** They passed on the base commit, before this change. Known gaps has the details. They are not a spec defect. The process rule requires reporting them here.
