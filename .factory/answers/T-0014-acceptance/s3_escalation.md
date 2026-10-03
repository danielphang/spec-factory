## Escalations

1. **C.2 contradicts an existing test that this sub-ticket may not change.**
   - The test is `tests/factory/test_instance.py::test_repo_root_is_the_instance_parent_and_factory_repo_overrides`, at line 240, added in T-0012.3.
   - It builds an instance directory `alt` from only `instance.yaml` and `context.md`, with no `harness.lock`. Then it runs `config` twice on that instance's own store: first with `FACTORY_INSTANCE=alt`, then with `FACTORY_REPO=target`.
   - C.2 says every command except `init` and `paths` exits 2 when "the lock is missing". So the first call now fails: `harness fe6303c56536389c668e37ccba0e73b98077d44e is not the revision this instance accepted (none); rerun with --accept-harness fe6303c… to accept it` / `assert 2 == 0` (line 247).
   - The sub-ticket says "Tests to change: none" and requires harness-suite-passes-after-uv-sync to report no `failed`.
   - Proposed resolution, for a human: add this test to "Tests to change" with one added line after `(alt / "context.md").write_text("x\n")`: `(alt / "harness.lock").write_bytes((target / ".factory" / "harness.lock").read_bytes())`. I applied that line temporarily: the test passed (`1 passed, 21 deselected`). I then reverted it with `git checkout tests/factory/test_instance.py`, so the branch does not carry it.
   - Alternative: exempt `config` from the lock. That contradicts C.2's "every command except `init` and `paths`", so I did not do it.
2. **Informational.** Four NEW criteria passed vacuously at base (see Known gaps). They are not a spec defect, but by the process rule they are reported here.
