"""Ticket store on disk: tickets/, requests/, specs/, plans/, runs/, log/ under the state dir.

Every write goes through here so a later sub-ticket can add commit-and-push in one place.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"

STATES = [
    "ready-for-triage", "waiting-requester", "ready-for-spec-writer", "ready-for-critic",
    "awaiting-spec-gate", "ready-for-planner", "planned", "parked", "closed",
]


class Refused(Exception):  # noqa: N818
    """A guard refused the operation: exit 2, store unchanged, nothing logged."""


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def state_root(cfg: dict | None = None) -> Path:
    env = os.environ.get("FACTORY_STATE")
    if env:
        return Path(env).expanduser().resolve()
    cfg = cfg or load_config()
    return (REPO_ROOT / cfg["state_dir"]).resolve()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_yaml(path: Path, obj) -> None:
    write_text(path, yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=100))


def read_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def log_event(root: Path, event: str, **fields) -> dict:
    line = {"ts": now(), "event": event, **fields}
    p = root / "log" / f"{line['ts'][:7]}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(line, ensure_ascii=False) + "\n")
    return line


def ticket_path(root: Path, tid: str) -> Path:
    return root / "tickets" / f"{tid}.yaml"


def load_ticket(root: Path, tid: str) -> dict:
    p = ticket_path(root, tid)
    if not p.exists():
        raise Refused(f"no ticket {tid}")
    return read_yaml(p)


def save_ticket(root: Path, t: dict) -> None:
    write_yaml(ticket_path(root, t["id"]), t)


def next_ticket_id(root: Path, prefix: str = "T") -> str:
    tickets = root / "tickets"
    nums = []
    if tickets.exists():
        for p in tickets.glob(f"{prefix}-*.yaml"):
            try:
                nums.append(int(p.stem.split("-", 1)[1]))
            except ValueError:
                pass
    return f"{prefix}-{(max(nums) + 1 if nums else 1):04d}"


def next_run_id(root: Path, role: str) -> str:
    runs = root / "runs"
    nums = []
    if runs.exists():
        for p in runs.iterdir():
            try:
                nums.append(int(p.name.split("-")[1]))
            except (IndexError, ValueError):
                pass
    return f"run-{(max(nums) + 1 if nums else 1):04d}-{role}"


def new_ticket(root: Path, tid: str, title: str, request_rel: str, source: str) -> dict:
    return {
        "id": tid,
        "type": None,
        "title": title,
        "request": request_rel,
        "source": source,
        "status": "ready-for-triage",
        "round": {"spec": 0, "pr": 0},
        "spec": {"version": 0, "approved_version": None},
        "plan": None,
        "in_flight": [],
        "parked": None,
        "created": now(),
        "history": [],
    }


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def index_path(root: Path) -> Path:
    return root / "requests" / "index.yaml"


def load_index(root: Path) -> dict:
    p = index_path(root)
    return read_yaml(p) or {} if p.exists() else {}
