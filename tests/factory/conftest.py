"""Point every test at a fixed instance (design B.9), never at whatever instance surrounds the
checkout the suite runs in.

The imported tests drive `bin/factory` as a subprocess with cwd set to the harness checkout and an
environment built from os.environ, each on a throwaway store (FACTORY_STATE). Without this file the
harness would resolve the instance by walking up from that checkout: the harness repo's own
`.factory/`, or none at all. FACTORY_REPO keeps the repo root the tests saw before instances existed
(the harness checkout) instead of the fixture's parent; a test that sets its own FACTORY_REPO in a
subprocess environment (the shepherd's scratch target) still overrides it.
"""
from __future__ import annotations

import os
from pathlib import Path

_HERE = Path(__file__).resolve()
os.environ["FACTORY_INSTANCE"] = str(_HERE.parent / "fixtures" / "instance")
os.environ.setdefault("FACTORY_REPO", str(_HERE.parents[2]))
