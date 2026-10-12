"""The spec drift check (T-0027 part D). Every spec version records the integration branch's head it
was written against, in specs/<id>/v<n>.yaml. Before a sub-ticket's first implementer run (none
finished, no ruling on file), `run start` refuses with an error that starts
`BLOCKED from harness: spec drift: ` and writes nothing when:
- the sibling rule: its Acceptance field names a current sibling that has not merged and that it does
  not depend on, directly or through other siblings; or
- the test rule: a test file changed on the integration branch since the recorded head, by a
  first-parent commit that also changed a file the approved version's design names, and neither the
  spec's nor the sub-ticket's Tests to change lists it.

Each case builds the spec's t0027-amend.sh fixture (test_spec_amend's `f`): a throwaway store with a
spec store and a scratch target whose main holds src/greet.py and src/other.py. T-0001's v1, whose
design names `src/greet.py`, is approved.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest
import yaml

from ._cli import REPO
from ._fixtures import (  # noqa: F401  (f is the t0027-amend.sh store fixture)
    BUILD_DRIVER,
    V1,
    V2,
    drifted,
    f,
    head,
    implementer_runs,
    land,
    start,
    started,
)

TWO = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: {deps}\nParallel-safe: yes\n{extra}"


# ----- the record -----------------------------------------------------------------------------

def test_spec_add_records_the_integration_head(f):
    rec = yaml.safe_load((f.store / "specs" / "T-0001" / "v1.yaml").read_text())
    assert rec == {"integration_head": head(f)}


def test_gate_edit_and_amendment_each_record_the_head_at_their_time(f):
    f.ok("ticket", "new", "--file", f.file("req2.md", "# Second\n\nWave.\n"))
    f.ok("ticket", "transition", "T-0002", "--to", "ready-for-spec-writer", "--by", "t")
    f.ok("spec", "add", "T-0002", "--file", f.file("w1.md", V1))
    f.ok("ticket", "transition", "T-0002", "--to", "ready-for-critic", "--by", "t", "--round", "spec:init")
    f.ok("ticket", "transition", "T-0002", "--to", "awaiting-spec-gate", "--by", "t")
    edited_at = land(f, "src/other.py")
    f.ok("approve-spec", "T-0002", "--edit", f.file("w2.md", V2))
    amended_at = land(f, "src/other.py")
    assert f.amend(V2).returncode == 0
    assert yaml.safe_load((f.store / "specs" / "T-0002" / "v2.yaml").read_text())["integration_head"] == edited_at
    assert yaml.safe_load((f.store / "specs" / "T-0001" / "v2.yaml").read_text())["integration_head"] == amended_at


@pytest.mark.parametrize("repo", ["missing", "not-a-repo"])
def test_head_is_null_when_the_target_repo_does_not_resolve(f, repo):
    target = f.tmp / repo
    if repo == "not-a-repo":
        target.mkdir()
    f.env["FACTORY_REPO"] = str(target)
    f.ok("ticket", "new", "--file", f.file("req2.md", "# Second\n\nWave.\n"))
    f.ok("ticket", "transition", "T-0002", "--to", "ready-for-spec-writer", "--by", "t")
    f.ok("spec", "add", "T-0002", "--file", f.file("w1.md", V1))
    assert yaml.safe_load((f.store / "specs" / "T-0002" / "v1.yaml").read_text()) == {"integration_head": None}


def test_head_is_null_when_the_integration_branch_does_not_resolve(f):
    f.env["FACTORY_INTEGRATION_BRANCH"] = "no-such-branch"
    f.ok("ticket", "new", "--file", f.file("req2.md", "# Second\n\nWave.\n"))
    f.ok("ticket", "transition", "T-0002", "--to", "ready-for-spec-writer", "--by", "t")
    f.ok("spec", "add", "T-0002", "--file", f.file("w1.md", V1))
    assert yaml.safe_load((f.store / "specs" / "T-0002" / "v1.yaml").read_text()) == {"integration_head": None}


# ----- the sibling rule -----------------------------------------------------------------------

ACCEPT_ST1 = "Acceptance:\n- REGRESSION: ST-1 scenarios still pass\n"


def test_acceptance_naming_an_unmerged_sibling_is_refused_until_it_merges(f):
    f.plan(TWO.format(deps="none", extra=ACCEPT_ST1))
    error = drifted(f, start(f, "T-0001.2"), "T-0001.2")
    assert "its Acceptance names T-0001.1 (ready-for-implementer), which has not merged and is not one of " \
           "its dependencies" in error
    f.ok("ticket", "set", "T-0001.1", "status=merged")
    started(start(f, "T-0001.2"))


def test_acceptance_naming_a_sibling_by_its_id_is_refused(f):
    f.plan(TWO.format(deps="none", extra="Acceptance: T-0001.1's scenarios still pass\n"))
    assert "names T-0001.1 " in drifted(f, start(f, "T-0001.2"), "T-0001.2")


def test_a_sibling_it_depends_on_directly_or_through_another_is_no_finding(f):
    plan = ("ST-1 / First\nDepends on: none\nParallel-safe: yes\n\n"
            "ST-2 / Second\nDepends on: ST-1\nParallel-safe: yes\n\n"
            "ST-3 / Third\nDepends on: ST-2\nParallel-safe: yes\nAcceptance: ST-1 and ST-2 still pass\n")
    f.plan(plan)
    f.ok("ticket", "set", "T-0001.3", "status=ready-for-implementer")
    started(start(f, "T-0001.3"))


@pytest.mark.parametrize("text", ["ST-10 still passes", "T-0001.1.2 still passes", "XST-1 is unrelated",
                                  "ST-1-old is unrelated"])
def test_a_longer_token_containing_the_label_is_no_finding(f, text):
    f.plan(TWO.format(deps="none", extra=f"Acceptance: {text}\n"))
    started(start(f, "T-0001.2"))


def test_a_sibling_named_outside_the_acceptance_field_is_no_finding(f):
    f.plan(TWO.format(deps="none", extra="Scope: like ST-1\nAcceptance: its own scenario\nOut of scope: ST-1\n"))
    started(start(f, "T-0001.2"))


# ----- the test rule --------------------------------------------------------------------------

ONE = "ST-1 / First\nDepends on: none\nParallel-safe: yes\n{extra}"


def test_a_test_changed_beside_a_named_file_is_refused_naming_file_and_commits(f):
    base = head(f)
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", "tests/test_greet.py")
    last = land(f, "src/greet.py", "tests/test_greet.py")
    land(f, "src/other.py", "tests/test_other.py")
    error = drifted(f, start(f))
    assert f"tests/test_greet.py changed by {last[:9]} since spec v1 was written at {base[:9]}" in error
    assert "test_other.py" not in error and error.count("changed by") == 1


@pytest.mark.parametrize("test", ["src/greet_test.py", "web/greet.test.ts", "tests/test_greet.py"])
def test_each_test_file_form_is_counted(f, test):
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", test)
    assert test in drifted(f, start(f))


def test_a_commit_changing_only_tests_or_unnamed_files_is_no_finding(f):
    f.plan(ONE.format(extra=""))
    land(f, "tests/test_greet.py")
    land(f, "src/other.py", "tests/test_other.py")
    land(f, "src/greet.py", "src/helper.py")
    started(start(f))


def test_a_test_the_subticket_lists_is_no_finding(f):
    f.plan(ONE.format(extra="Tests to change:\n- `tests/test_greet.py::test_hi`: pins the old greeting\n"))
    land(f, "src/greet.py", "tests/test_greet.py")
    started(start(f))


def test_a_test_the_spec_lists_is_no_finding(f):
    v = V2.replace("## Tests to change\nnone\n", "## Tests to change\n- `tests/test_greet.py`: pins hi\n")
    assert f.amend(v).returncode == 0
    f.plan(ONE.format(extra=""))
    rec = f.store / "specs" / "T-0001" / "v2.yaml"
    rec.write_text(yaml.safe_dump({"integration_head": land(f, "src/other.py")}))  # count from before the change
    land(f, "src/greet.py", "tests/test_greet.py")
    started(start(f))


def test_an_amendment_written_after_the_change_clears_drift(f):
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", "tests/test_greet.py")
    drifted(f, start(f))
    assert f.amend(V2).returncode == 0
    started(start(f))


def test_a_version_with_no_record_gets_only_the_sibling_rule(f):
    (f.store / "specs" / "T-0001" / "v1.yaml").unlink()
    f.plan(TWO.format(deps="none", extra=ACCEPT_ST1))
    land(f, "src/greet.py", "tests/test_greet.py")
    error = drifted(f, start(f, "T-0001.2"), "T-0001.2")
    assert "names T-0001.1" in error and "test_greet.py" not in error
    started(start(f))


@pytest.mark.parametrize("recorded", [None, "0" * 40])
def test_a_null_or_unknown_recorded_head_skips_the_test_rule(f, recorded):
    (f.store / "specs" / "T-0001" / "v1.yaml").write_text(yaml.safe_dump({"integration_head": recorded}))
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", "tests/test_greet.py")
    started(start(f))


# ----- when the check runs --------------------------------------------------------------------

def test_a_ruling_on_file_skips_the_check(f):
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", "tests/test_greet.py")
    drifted(f, start(f))
    (f.store / "approvals" / "T-0001.1").mkdir(parents=True)
    (f.store / "approvals" / "T-0001.1" / "ruling-1.md").write_text("Ruling: the new test may change.\n")
    started(start(f))


def test_a_finished_implementer_run_skips_the_check(f):
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", "tests/test_greet.py")
    d = f.store / "runs" / "run-0001-implementer"
    d.mkdir(parents=True)
    (d / "meta.yaml").write_text(yaml.safe_dump({"run_id": d.name, "role": "implementer", "ticket": "T-0001.1",
                                                 "finished": "2026-10-09T00:00:00Z"}))
    started(start(f))


def test_the_build_parks_a_drifted_subticket_and_a_ruling_lets_it_start(f):
    node = shutil.which("node")
    assert node, "node must be on PATH: this case runs factory/workflows/build.js"
    f.plan(ONE.format(extra=""))
    land(f, "src/greet.py", "tests/test_greet.py")
    driver = f.tmp / "t0022-build.mjs"
    driver.write_text(BUILD_DRIVER)
    cp = subprocess.run([node, str(driver)], capture_output=True, text=True, env=f.env, cwd=REPO)
    parks = [ln for ln in cp.stdout.splitlines() if ln.startswith("park ")]
    assert len(parks) == 1 and parks[0].startswith("park T-0001.1: BLOCKED from harness: spec drift: "), \
        cp.stdout + cp.stderr
    parked = f.ticket("T-0001.1")
    assert parked["status"] == "parked" and "tests/test_greet.py" in parked["parked"]["reason"]
    assert implementer_runs(f) == []
    f.ok("resolve", "T-0001.1", "--ruling", f.file("r.md", "Ruling: the new test may change.\n"))
    started(start(f))
