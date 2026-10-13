"""`run start` takes each role's model from the instance and refuses a `--model` that names another.

The instance here is a copy of the template with triage moved to `sonnet`, a model no other role
uses, so a check that falls back to a default or to another role's entry cannot pass.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from ._cli import REPO, js, run_env, ticket


@pytest.fixture
def env(tmp_path: Path) -> dict:
    inst = tmp_path / "inst"
    inst.mkdir()
    text = (REPO / "factory" / "instance.template.yaml").read_text()
    assert "\n  triage: opus\n" in text
    (inst / "instance.yaml").write_text(text.replace("\n  triage: opus\n", "\n  triage: sonnet\n"))
    req = tmp_path / "req.md"
    req.write_text("# F\n\nDo x.\n")
    e = {"FACTORY_INSTANCE": str(inst), "FACTORY_STATE": str(tmp_path / "store")}
    assert run_env(e, "ticket", "new", "--file", str(req)).returncode == 0
    return e


def _store(env: dict) -> Path:
    return Path(env["FACTORY_STATE"])


def _started_events(env: dict) -> list[str]:
    return [ln for p in sorted((_store(env) / "log").glob("*.jsonl"))
            for ln in p.read_text().splitlines() if '"run.started"' in ln]


def _recorded(env: dict, cp) -> tuple[str, str, list[str]]:
    rid = js(cp)["run_id"]
    meta = yaml.safe_load((_store(env) / "runs" / rid / "meta.yaml").read_text())
    return js(cp)["model"], meta["model"], _started_events(env)


def test_a_differing_model_is_refused_and_writes_nothing(env):
    cp = run_env(env, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "opus")
    assert cp.returncode == 2
    assert cp.stderr.strip() == "model opus refused for triage: the instance names sonnet"
    runs = _store(env) / "runs"
    assert not runs.exists() or not any(runs.iterdir())
    assert _started_events(env) == []
    assert ticket(_store(env))["in_flight"] == []


def test_the_instances_own_model_is_accepted_and_recorded(env):
    cp = run_env(env, "run", "start", "--role", "triage", "--ticket", "T-0001", "--model", "sonnet")
    assert cp.returncode == 0, cp.stderr
    returned, recorded, events = _recorded(env, cp)
    assert (returned, recorded) == ("sonnet", "sonnet")
    assert len(events) == 1 and '"model": "sonnet"' in events[0]


def test_no_model_records_the_instances_model(env):
    cp = run_env(env, "run", "start", "--role", "triage", "--ticket", "T-0001")
    assert cp.returncode == 0, cp.stderr
    returned, recorded, events = _recorded(env, cp)
    assert (returned, recorded) == ("sonnet", "sonnet")
    assert len(events) == 1 and '"model": "sonnet"' in events[0]
    assert ticket(_store(env))["in_flight"] == [js(cp)["run_id"]]


@pytest.mark.parametrize("role, given, named", [
    ("reviewer", "opus", "fable"),
    ("verifier", "fable", "opus"),
    ("critic", "sonnet", "fable"),
])
def test_each_role_is_checked_against_its_own_entry(env, role, given, named):
    cp = run_env(env, "run", "start", "--role", role, "--ticket", "T-0001", "--model", given)
    assert cp.returncode == 2
    assert cp.stderr.strip() == f"model {given} refused for {role}: the instance names {named}"
    assert _started_events(env) == []


def test_a_non_triage_role_is_accepted_on_its_own_model(env):
    for to in ("ready-for-spec-writer", "ready-for-critic"):
        assert run_env(env, "ticket", "transition", "T-0001", "--to", to, "--by", "t").returncode == 0
    cp = run_env(env, "run", "start", "--role", "critic", "--ticket", "T-0001", "--model", "fable")
    assert cp.returncode == 0, cp.stderr
    returned, recorded, _ = _recorded(env, cp)
    assert (returned, recorded) == ("fable", "fable")
