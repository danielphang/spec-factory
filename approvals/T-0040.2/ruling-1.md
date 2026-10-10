Ruling (Green, harness owner), 2026-10-10, on the harness's spec-drift park.

Not drift. `tests/factory/test_drive.py` was created by your own sibling's merge (T-0040.1, merge 2ad4d8c52), as the plan intends: part A creates it, and your sub-ticket already says you may import its stand-in `claude` helper. No spec change is needed. Build part B as the sub-ticket says. The drift check's false positive on a sibling's merge is filed as a harness bug.
