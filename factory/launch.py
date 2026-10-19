"""`factory launch-script intake|build`: a launch copy of a workflow script, with the instance's
values written into one line so no clerk relays them, and the values `factory config` prints."""
from __future__ import annotations

import json
import shutil
import tempfile
import time
from pathlib import Path

from factory import instance
from factory.common import out
from factory.store import Refused

LAUNCH_LINE = "const LAUNCH = null"
WRITTEN_BY = "factory launch-script"


def config_values(root: Path, cfg: dict) -> dict:
    """What `factory config` prints besides `ok`; a launch copy carries the same values."""
    return {"models": cfg["models"], "max_rounds": cfg["max_rounds"], "state_dir": str(root)}


def launch_script(a, root, cfg):
    """Write `<name>.js` read-only into a new `factory-launch-*` directory under the temporary
    directory: the workflow script with its one `const LAUNCH = null` line set to the instance's
    values, the running harness revision and the instance. Writes nothing to the checkout or store."""
    src = instance.HARNESS / "factory" / "workflows" / f"{a.name}.js"
    lines = src.read_text(encoding="utf-8").split("\n")
    if lines.count(LAUNCH_LINE) != 1:
        raise Refused(f"{src} holds the line `{LAUNCH_LINE}` {lines.count(LAUNCH_LINE)} times, not once; "
                      "no launch copy written")
    rev, inst = instance.harness_revision(), str(instance.require())
    launch = {"written_by": WRITTEN_BY, "source": str(src), "harness_revision": rev, "instance": inst,
              **config_values(root, cfg)}
    lines[lines.index(LAUNCH_LINE)] = f"const LAUNCH = {json.dumps(launch, ensure_ascii=False)}"
    _remove_old_copies()
    dest = Path(tempfile.mkdtemp(prefix="factory-launch-")) / src.name
    dest.write_text("\n".join(lines), encoding="utf-8")
    dest.chmod(0o444)
    out({"ok": True, "script": str(dest), "source": str(src), "harness_revision": rev, "instance": inst})


def _remove_old_copies() -> None:
    """Remove each `factory-launch-*` directory under the temporary directory that is more than an
    hour old and holds only a launch copy. The Workflow tool keeps its own copy of a script once
    launched, so such a copy is no longer read; a newer one may be about to be launched by another
    session sharing the directory. Any other directory, and any error, is skipped."""
    cutoff = time.time() - 3600
    for d in Path(tempfile.gettempdir()).glob("factory-launch-*"):
        try:
            files = list(d.iterdir())
            if (d.stat().st_mtime < cutoff and len(files) == 1 and files[0].name in ("intake.js", "build.js")
                    and f'"written_by": "{WRITTEN_BY}"' in files[0].read_text(encoding="utf-8")):
                shutil.rmtree(d)
        except (OSError, ValueError):
            continue
