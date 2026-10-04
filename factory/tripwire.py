"""Tripwire on live files: notice when a role run changes a file outside the repo.

An instance lists files under `tripwire` in `instance.yaml`, as a `park` list and an `escalate` list.
`run start` records each file's SHA-256 (or `absent`) in `runs/<id>/tripwire.yaml`, which the store's
`.gitignore` excludes. The run is compared once, when it leaves the in-flight list: a changed `park`
file parks the ticket, a changed `escalate` file queues an escalation. Nothing here reads a file's
bytes into an event, a reason or an output; only paths are named.
"""
from __future__ import annotations

import hashlib
import os
import pwd
from pathlib import Path

from factory import store
from factory.store import Refused

LISTS = ("park", "escalate")


def _expand(entry: str) -> str:
    """`~/` is the account's home from the user database, never $HOME: a role run under a throwaway
    HOME must still watch the real files."""
    return pwd.getpwuid(os.getuid()).pw_dir + entry[1:] if entry.startswith("~/") else entry


def _digest(path: str) -> str:
    """Hex SHA-256 of the file's bytes, or `absent`. OSError when it exists but cannot be read."""
    try:
        with open(path, "rb") as fh:
            return hashlib.file_digest(fh, "sha256").hexdigest()
    except FileNotFoundError:
        return "absent"


def baseline(cfg: dict) -> dict | None:
    """The instance's listed files hashed now, as `{park: {path: state}, escalate: {...}, compared:
    None}`; None when the tripwire is off (no key, null, or both lists empty). Refused for a list
    that is not a mapping of string lists, or an entry that is not absolute after expansion, exists
    and is not a regular file, or exists and cannot be read."""
    tw = cfg.get("tripwire")
    if tw is None:
        return None
    if not isinstance(tw, dict) or set(tw) - set(LISTS):
        raise Refused(f"tripwire must be a mapping with only the keys park and escalate, got {tw!r}")
    lists = {}
    for name in LISTS:
        entries = tw.get(name) or []
        if not isinstance(entries, list) or not all(isinstance(e, str) for e in entries):
            raise Refused(f"tripwire.{name} must be a list of file paths, got {entries!r}")
        lists[name] = [(e, _expand(e)) for e in entries]
    if not any(lists.values()):
        return None
    base: dict = {}
    for name, entries in lists.items():
        base[name] = {}
        for written, path in entries:
            what = f"tripwire.{name} entry {written!r} ({path})"
            if not os.path.isabs(path):
                raise Refused(f"{what} is not an absolute or ~/ path")
            if os.path.exists(path) and not os.path.isfile(path):
                raise Refused(f"{what} exists and is not a regular file; list files only")
            try:
                base[name][path] = _digest(path)
            except OSError as e:
                raise Refused(f"{what} cannot be read: {e.strerror}")
    base["compared"] = None
    return base


def compare(root: Path, rid: str, tid: str) -> dict | None:
    """Compare run `rid`'s baseline with the files now, once, and act on ticket `tid`: a changed
    `park` file parks it (or, if it is already parked or closed, queues the reason as an
    escalation); a changed `escalate` file queues an escalation. Returns `{park: [...], escalate:
    [...], parked: <reason> | None}`, or None when the run has no baseline or was compared before."""
    p = root / "runs" / rid / "tripwire.yaml"
    if not p.exists():
        return None
    base = store.read_yaml(p)
    if base.get("compared"):
        return None
    changed = {}
    for name in LISTS:
        changed[name] = []
        for path, before in (base.get(name) or {}).items():
            try:
                now = _digest(path)
            except OSError:
                now = "unreadable"  # cannot be read now: counts as changed
            if now != before:
                changed[name].append(path)
    base["compared"] = store.now()
    store.write_yaml(p, base)
    parked = None
    if changed["park"]:
        reason = f"tripwire: {', '.join(changed['park'])} changed during {rid}"
        t = store.load_ticket(root, tid)
        if t["status"] in ("parked", "closed"):
            store.log_event(root, "escalation.queued", ticket=tid, run=rid, items=[reason])
        else:
            store.park_ticket(root, t, reason, [rid], by="tripwire")
            parked = reason
    if changed["escalate"]:
        item = f"tripwire (escalate): {', '.join(changed['escalate'])} changed during {rid}"
        store.log_event(root, "escalation.queued", ticket=tid, run=rid, items=[item])
    if changed["park"] or changed["escalate"]:
        store.log_event(root, "tripwire.changed", ticket=tid, run=rid, **changed)
    return {**changed, "parked": parked}
