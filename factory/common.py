"""Helpers more than one command module calls, and the live-store fence."""
from __future__ import annotations

import json
import os
from pathlib import Path

from factory import gitops, instance, store
from factory.store import Refused


def out(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False))


def _rel(root: Path, p: Path) -> str:
    return str(p.relative_to(root))


def _integration_head(cfg: dict) -> str | None:
    """The integration branch's head in the target repo, or None when the repo or branch does not resolve."""
    try:
        repo = gitops.repo_root()
        return gitops.integration_tip(cfg, repo)
    except (Refused, OSError):
        return None


def _add_spec_version(root: Path, t: dict, text: str, source: str, cfg: dict) -> int:
    """Write the next spec version, and beside it `v<n>.yaml` with the integration head it was written
    against, which the spec drift check counts from (doc §Harness, Spec drift)."""
    n = t["spec"]["version"] + 1
    store.write_text(root / "specs" / t["id"] / f"v{n}.md", text)
    store.write_yaml(root / "specs" / t["id"] / f"v{n}.yaml", {"integration_head": _integration_head(cfg)})
    store.write_text(root / "specs" / f"{t['id']}.md", text)
    t["spec"]["version"] = n
    store.save_ticket(root, t)
    store.log_event(root, "spec.added", ticket=t["id"], version=n, source=source)
    return n


def _in_flight(root: Path) -> list[str]:
    """Every run in flight on the store: the union of its tickets' in_flight lists."""
    return [rid for p in sorted((root / "tickets").glob("*.yaml"))
            for rid in store.read_yaml(p).get("in_flight") or []]


def fence(inst: Path, cfg: dict, root: Path, *, in_flight: bool = True) -> None:
    """Refuse a write to the instance's own store from inside its runs/ or worktrees/ (marker or
    not), or while a run is in flight there unless FACTORY_DISPATCH=1. Accidents, not isolation.
    With in_flight=False only the location rule applies: `factory drive` is the dispatcher, exempt
    from the in-flight rule, and guards its own ticket instead (drive._same_ticket_guard). Commands in
    READ_ONLY skip it; `paths` and `stats` never reach it, and `init` calls it itself."""
    if not instance.is_own_store(inst, cfg, root):
        return
    own, cwd = instance.own_state_root(inst, cfg), instance.caller_cwd()
    for sub in ("runs", "worktrees"):
        if cwd.is_relative_to(own / sub):
            raise Refused(f"role runs may not write the live store ({own}; called from inside its {sub}/); "
                          "use a throwaway FACTORY_STATE")
    if not in_flight or os.environ.get("FACTORY_DISPATCH") == "1":
        return
    runs = _in_flight(root)
    if runs:
        raise Refused(f"role runs may not write the live store ({root}; in flight: {', '.join(runs)}); "
                      "use a throwaway FACTORY_STATE")
