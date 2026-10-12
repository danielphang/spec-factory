"""Spec-drift checks: refuse a sub-ticket's implementer run when the code has moved from its spec."""
from __future__ import annotations

import re
from pathlib import Path

from factory import gitops, specstore, store, subtickets
from factory.store import Refused


def _check_sibling_tests(root: Path, cfg: dict, t: dict) -> None:
    """Doc §Harness, "Tests a sibling added": each file the sub-ticket's "Tests to change" lists as
    added by a sibling must be absent at the parent's base, and first added on the integration
    branch by a commit inside one merged sibling's recorded merge (reachable from its main_after,
    not from its base_before). Else refused, so the build parks the sub-ticket as BLOCKED."""
    sub = root / "specs" / t["id"] / "subticket.md"
    paths = subtickets.sibling_tests(sub.read_text(encoding="utf-8")) if sub.exists() else []
    if not paths:
        return
    parent = store.load_ticket(root, t["parent"])
    base = parent.get("parent_base")
    repo = gitops.repo_root()
    tip = gitops.integration_tip(cfg, repo)
    merges = [s["merge"] for s in store.subtickets_of(root, parent["id"])
              if s["id"] != t["id"] and s["status"] == "merged"
              and (s.get("merge") or {}).get("main_after") and s["merge"].get("base_before")]
    for path in paths:
        added = gitops.first_added(repo, base, tip, path) if base else None
        if added and any(gitops.head_contains(repo, m["main_after"], added)
                         and not gitops.head_contains(repo, m["base_before"], added) for m in merges):
            continue
        since = f"since {base[:9]}" if base else "(no sibling has merged)"
        raise Refused(f"BLOCKED from harness: Tests to change lists {path} as added by a sibling, but no merged "
                      f"sibling of {parent['id']} added it {since}; list it in the parent spec's Tests to change, "
                      f"or remove it")


TEST_FILE_RE = re.compile(r"(^|/)test_[^/]*$|_test\.[A-Za-z0-9]+$|\.test\.[A-Za-z0-9]+$")
TICK_RE = re.compile(r"`([^`\n]+)`")


def _check_drift(root: Path, cfg: dict, t: dict) -> None:
    """Doc §Harness, "Spec drift": before a sub-ticket's first implementer run (none finished, no
    ruling on file), refuse when its Acceptance names an unmerged sibling of the current plan that it
    does not depend on, or when a test file changed on the integration branch since the parent's
    approved version was written, by a first-parent commit that also changed a file the version's
    design names, and no Tests to change list names it. A merged sibling's recorded merge is not
    drift: the plan expects its changes. The build parks the refusal as BLOCKED."""
    tid = t["id"]
    if any(store.ticket_runs(root, tid, "implementer", finished=True)) or list((root / "approvals" / tid).glob("ruling-*")):
        return
    sub = root / "specs" / tid / "subticket.md"
    sub_text = sub.read_text(encoding="utf-8") if sub.exists() else ""
    parent = store.load_ticket(root, t["parent"])
    findings = _sibling_drift(root, t, parent, sub_text) + _test_drift(root, cfg, parent, sub_text)
    if findings:
        raise Refused(f"BLOCKED from harness: spec drift: {'; '.join(findings)}. Amend the spec "
                      f"(`spec amend {parent['id']}`) or rule (`resolve {tid} --ruling F`)")


def _sibling_drift(root: Path, t: dict, parent: dict, sub_text: str) -> list[str]:
    """The sibling rule: each current sibling, not merged and outside the sub-ticket's dependency
    closure, whose id or plan label is a whole token of its Acceptance field."""
    current = {s["id"]: s for s in subtickets.split_plan(store.subtickets_of(root, parent["id"]))[0]}
    closure, todo = set(), list(t.get("depends_on") or [])
    while todo:
        dep = todo.pop()
        if dep not in closure:
            closure.add(dep)
            todo += (current.get(dep) or {}).get("depends_on") or []
    acceptance = subtickets.field_text(sub_text, "acceptance")
    findings = []
    for s in current.values():
        if s["id"] == t["id"] or s["status"] == "merged" or s["id"] in closure:
            continue
        if any(re.search(rf"(?<![\w.-]){re.escape(tok)}(?![\w-]|\.\d)", acceptance)
               for tok in (s["id"], s.get("label")) if tok):
            findings.append(f"its Acceptance names {s['id']} ({s['status']}), which has not merged and is not "
                            "one of its dependencies")
    return findings


def _test_drift(root: Path, cfg: dict, parent: dict, sub_text: str) -> list[str]:
    """The test rule, counted from the integration head recorded with the parent's approved version.
    No record (a version stored before the record existed), a null head or one that is not a commit
    in the target repo: no findings. A first-parent commit that is the recorded merge (`main_after`)
    of a merged sub-ticket of this parent, from any of its plans, is skipped: it is the parent's own
    planned work. Other merges still count."""
    n = parent["spec"]["approved_version"]
    rec = root / "specs" / parent["id"] / f"v{n}.yaml"
    base = (store.read_yaml(rec) or {}).get("integration_head") if rec.exists() else None
    if not base:
        return []
    repo = gitops.repo_root()
    if not gitops.git(repo, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", check=False):
        return []
    tip = gitops.integration_tip(cfg, repo)
    design = dict(specstore.split_parts((root / "specs" / parent["id"] / f"v{n}.md").read_text(encoding="utf-8")))
    design_text = design.get("design.md", "")
    at_tip = set(gitops.git(repo, "ls-tree", "-r", "--name-only", tip).splitlines())
    named = {p for p in TICK_RE.findall(design_text)
             if p in at_tip and not TEST_FILE_RE.search(p) and not p.endswith(".md")}
    if not named:
        return []
    listed_text = subtickets.field_text(sub_text, "tests to change") + "\n" + _tests_to_change_section(design_text)
    listed = {p.split("::", 1)[0] for p in TICK_RE.findall(listed_text)}
    siblings = {s["merge"]["main_after"] for s in store.subtickets_of(root, parent["id"])
                if s["status"] == "merged" and (s.get("merge") or {}).get("main_after")}
    last: dict[str, str] = {}
    # factory: one git diff per first-parent commit since the spec was written; fold into one
    # `git log --diff-merges=first-parent --name-only` call if that range grows to hundreds of commits
    for c in gitops.git(repo, "rev-list", "--first-parent", "--reverse", f"{base}..{tip}").split():
        if c in siblings:
            continue
        files = gitops.git(repo, "diff", "--name-only", "--no-renames", f"{c}^1", c, check=False).splitlines()
        if named.intersection(files):
            for f in files:
                if TEST_FILE_RE.search(f) and f not in listed:
                    last[f] = c
    return [f"{f} changed by {c[:9]} since spec v{n} was written at {base[:9]}" for f, c in last.items()]


def _tests_to_change_section(design_text: str) -> str:
    """The design part's `## Tests to change` section, up to the next heading outside a fence."""
    lines, inside = [], False
    for line, in_fence in specstore.lines_outside_fences(design_text):
        if specstore._heading(line, in_fence):
            inside = line.strip() == "## Tests to change"
            continue
        if inside:
            lines.append(line)
    return "\n".join(lines)
