## Escalations

1. **An existing test fails under rule C.2, and this sub-ticket is not allowed to change that test. Decide: allow a one-line change to the test, or exempt `config` from the rule.**

   Rule C.2 says every command except `init` and `paths` exits 2 when the instance's `harness.lock` is missing. The failing test is `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides`, at line 240. It builds an instance directory `alt` from only `instance.yaml` and `context.md`. It does not create a `harness.lock`. It then runs `config` twice on that instance's own store: first with `FACTORY_INSTANCE=alt`, then with `FACTORY_REPO=target`.

   Under C.2 the first call now exits 2. The test prints `harness fe6303c56536389c668e37ccba0e73b98077d44e is not the revision this instance accepted (none); rerun with --accept-harness fe6303c… to accept it` / `assert 2 == 0` (line 247). This means `alt` has no accepted harness revision, so `config` refuses to run, and the test's expected exit code 0 is not met.

   The sub-ticket says "Tests to change: none". It also requires the check harness-suite-passes-after-uv-sync to report no `failed`. Both cannot hold while this test fails.

   - Proposed: add this test to "Tests to change", with one line added after `(alt / "context.md").write_text("x\n")`:
     `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`
     The line copies the target's `harness.lock` into `alt`. I applied it temporarily and the test passed: `1 passed, 21 deselected` means the one selected test passed. I then reverted the line with `git checkout tests/factory/test_instance.py`. The branch does not carry it.
   - Rejected: exempt `config` from the lock. That contradicts C.2's "every command except `init` and `paths`", so I did not do it.

2. **For information only: four NEW criteria passed vacuously at base.** Known gaps has the details. This is not a spec defect. The process rule requires reporting it here.

Note: the failing test was added in T-0012.3.
