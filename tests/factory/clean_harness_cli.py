"""Test-only launcher: runs this checkout's CLI as `bin/factory` does, with one check stubbed.

It stubs only the refusal of uncommitted harness edits (design item C.4), by replacing
`factory.instance.harness_changes` with a function that reports none. The lock comparison (design
items C.2 and C.3) still runs. The suite uses it for own-store cases that are not about C.4, so the
suite passes in a checkout with an uncommitted edit; the C.4 refusal keeps its tests on a clone's
real `bin/factory`. The production CLI honours no such switch. Not named `test_*`, so pytest does
not collect it.

Usage: `python tests/factory/clean_harness_cli.py <factory arguments>`.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[2]

# As bin/factory: hand the caller's directory over, then run from the harness checkout.
os.environ["FACTORY_CWD"] = os.getcwd()
os.chdir(HARNESS)
sys.path.insert(0, str(HARNESS))

from factory import cli, instance  # noqa: E402  (needs the harness on sys.path first)

instance.harness_changes = lambda *args, **kwargs: []
raise SystemExit(cli.main(sys.argv[1:]))
