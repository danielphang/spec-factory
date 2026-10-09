"""Spec store: OpenSpec's tree under the forked `spec-factory` schema (doc §Harness, Spec store;
build spec part B "Spec store", part K `approve-spec` / `archive`).

Current truth is `openspec/specs/<capability>/spec.md`. A ticket's change is the folder
`openspec/changes/<ID>/`, written by the harness when the human gate pins a version: the pinned
text is split on its `=== <path>` lines. Only `archive` writes current truth. `decisions.md` has
three writers, all through `record_decision`: `archive`, `decision add` and `resolve --decision`.
The store is active once `init` has created `openspec/`; a store without it keeps the P0
behaviour (specs pinned as one text), so the live pilot store is unaffected.
"""
from __future__ import annotations

import datetime as dt
import re
import shutil
from pathlib import Path

from factory import store

OPS = ("ADDED", "MODIFIED", "REMOVED")
FIXED_PARTS = ("proposal.md", "design.md", "verification.md")
DELTA_RE = re.compile(r"^specs/([a-z0-9]+(?:-[a-z0-9]+)*)/spec\.md$")
PART_RE = re.compile(r"^=== (\S+).*$", re.M)  # the path is the first token after "=== "
REQ_RE = re.compile(r"^### Requirement: (.+?)\s*$")
SCEN_RE = re.compile(r"^#### Scenario: (.+?)\s*$")
LABEL_RE = re.compile(r"^- (.+?) → (NEW|REGRESSION)(?![\w/])(?!\s*/)(?:\s*[.;:,—–(-].*)?\s*$")  # "NEW / REGRESSION" is no label

SCHEMA_YAML = """# Forked from OpenSpec's built-in `spec-driven` (doc §Harness, Spec store).
name: spec-factory
artifacts:
  - id: proposal
    generates: proposal.md
  - id: specs
    generates: specs/**/*.md
    requires: [proposal]
  - id: design
    generates: design.md
    requires: [proposal]
  - id: tasks
    generates: tasks.md
    requires: [specs, design]
  - id: verification
    generates: verification.md
    requires: [specs]
"""


def root_dir(root: Path) -> Path:
    return root / "openspec"


def is_active(root: Path) -> bool:
    return root_dir(root).is_dir()


def init(root: Path) -> list[str]:
    """Create the tree. Idempotent: existing files are kept. Returns the paths written."""
    o = root_dir(root)
    written = []
    for rel, text in (("config.yaml", "schema: spec-factory\n"),
                      ("schemas/spec-factory/schema.yaml", SCHEMA_YAML)):
        p = o / rel
        if not p.exists():
            store.write_text(p, text)
            written.append(str(p.relative_to(root)))
    (o / "specs").mkdir(parents=True, exist_ok=True)
    (o / "changes").mkdir(parents=True, exist_ok=True)
    d = root / "decisions.md"
    if not d.exists():
        store.write_text(d, "")
        written.append("decisions.md")
    return written


# ----- parsing ------------------------------------------------------------------------------

def lines_outside_fences(text: str):
    """(line, in_fence) for each line; a ``` fence at any indentation toggles. Headings and
    requirement lines inside a fence are text, not structure."""
    fence = False
    for line in text.splitlines():
        if re.match(r"^\s*```", line):
            fence = not fence
            yield line, True
            continue
        yield line, fence


def _heading(line: str, in_fence: bool) -> bool:
    return not in_fence and (line.startswith("## ") or line.startswith("### ") or line.startswith("#### "))


def split_parts(text: str) -> list[tuple[str, str]]:
    """(path, body) per `=== <path>` line, in order; text before the first line is dropped."""
    ms = list(PART_RE.finditer(text))
    parts = []
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        parts.append((m.group(1), text[m.end():end].lstrip("\n")))
    return parts


def requirement_blocks(text: str) -> dict[str, str]:
    """`### Requirement: <name>` → its block (the heading through the line before the next
    `### ` or `## ` heading), for a current-truth file or one delta section."""
    out: dict[str, str] = {}
    name, buf = None, []
    for line, in_fence in lines_outside_fences(text):
        m = REQ_RE.match(line) if not in_fence else None
        if m or (not in_fence and (line.startswith("## ") or line.startswith("### "))):
            if name is not None:
                out[name] = "\n".join(buf).rstrip() + "\n"
            name, buf = (m.group(1), [line]) if m else (None, [])
            continue
        if name is not None:
            buf.append(line)
    if name is not None:
        out[name] = "\n".join(buf).rstrip() + "\n"
    return out


def parse_delta(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    """Per op (ADDED/MODIFIED/REMOVED): name → block. Second value: errors (a requirement outside
    any op section, a duplicate name within the part, no op heading at all)."""
    ops: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    cur, sect = None, []
    sections: list[tuple[str | None, list[str]]] = []
    for line, in_fence in lines_outside_fences(text):
        m = re.match(r"^## (ADDED|MODIFIED|REMOVED) Requirements\s*$", line) if not in_fence else None
        if m or (not in_fence and line.startswith("## ")):
            sections.append((cur, sect))
            cur, sect = (m.group(1) if m else None), []
            continue
        sect.append(line)
    sections.append((cur, sect))
    seen: set[str] = set()
    for op, lines in sections:
        blocks = requirement_blocks("\n".join(lines))
        if op is None:
            for n in blocks:
                errors.append(f"requirement {n!r} is not under an ADDED, MODIFIED or REMOVED heading")
            continue
        ops.setdefault(op, {})
        for n, b in blocks.items():
            if n in seen:
                errors.append(f"requirement {n!r} appears more than once in the part")
            seen.add(n)
            ops[op][n] = b
    if not ops:
        errors.append("no `## ADDED|MODIFIED|REMOVED Requirements` heading")
    return ops, errors


def scenario_names(text: str) -> list[str]:
    return [m.group(1) for line, f in lines_outside_fences(text) if not f and (m := SCEN_RE.match(line))]


def acceptance_labels(verification: str) -> tuple[dict[str, str], list[str]]:
    """`## Acceptance` of verification.md: scenario name → NEW|REGRESSION; errors for a name
    labelled twice."""
    labels: dict[str, str] = {}
    errors: list[str] = []
    inside = False
    for line, in_fence in lines_outside_fences(verification):
        if in_fence:
            continue
        if line.startswith("## "):
            inside = line.startswith("## Acceptance")
            continue
        if inside and (m := LABEL_RE.match(line)):
            if m.group(1) in labels:
                errors.append(f"scenario {m.group(1)!r} is labelled twice")
            labels[m.group(1)] = m.group(2)
    return labels, errors


# ----- the well-formed rule and the applies check -----------------------------------------------

def validate(text: str) -> tuple[dict[str, str], dict[str, dict[str, dict[str, str]]], list[str]]:
    """Returns (parts by path, deltas by capability, errors). Empty errors = well-formed."""
    errors: list[str] = []
    parts: dict[str, str] = {}
    deltas: dict[str, dict[str, dict[str, str]]] = {}
    for path, body in split_parts(text):
        if path in parts:
            errors.append(f"part {path!r} appears twice")
            continue
        m = DELTA_RE.match(path)
        if path not in FIXED_PARTS and not m:
            errors.append(f"part {path!r} is not proposal.md, design.md, verification.md or specs/<kebab-case>/spec.md")
            continue
        parts[path] = body
        if m:
            ops, errs = parse_delta(body)
            errors.extend(f"{path}: {e}" for e in errs)
            deltas[m.group(1)] = ops
    if not parts:
        errors.append("no `=== <path>` part lines")
        return parts, deltas, errors
    if not deltas:
        errors.append("no delta part (specs/<capability>/spec.md)")
    names = [n for p, b in parts.items() if DELTA_RE.match(p) for n in scenario_names(b)]
    for n in sorted({n for n in names if names.count(n) > 1}):
        errors.append(f"scenario {n!r} is named more than once in the change")
    labels, errs = acceptance_labels(parts.get("verification.md", ""))
    errors.extend(errs)
    if "verification.md" not in parts:
        errors.append("no verification.md part")
    else:
        for n in dict.fromkeys(names):
            if n not in labels:
                errors.append(f"scenario {n!r} has no NEW/REGRESSION label in verification.md")
        for n in labels:
            if n not in names:
                errors.append(f"verification.md labels {n!r}, which is not a scenario of the delta")
    return parts, deltas, errors


def truth_path(root: Path, capability: str) -> Path:
    return root_dir(root) / "specs" / capability / "spec.md"


def applies(root: Path, deltas: dict[str, dict[str, dict[str, str]]]) -> list[str]:
    errors = []
    for cap, ops in deltas.items():
        p = truth_path(root, cap)
        have = requirement_blocks(p.read_text(encoding="utf-8")) if p.exists() else {}
        for n in ops.get("ADDED", {}):
            if n in have:
                errors.append(f"ADDED {n!r} is already in current truth ({cap})")
        for op in ("MODIFIED", "REMOVED"):
            for n in ops.get(op, {}):
                if n not in have:
                    errors.append(f"{op} {n!r} is not in current truth ({cap})")
    return errors


# ----- the decision log -------------------------------------------------------------------

def _utc_date() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")


def decision_text(text: str) -> str:
    """A decision's text, stripped. Refused unless it is one non-blank line."""
    s = text.strip()
    if not s or len(s.splitlines()) > 1:
        raise store.Refused("a decision is one non-blank line of text")
    return s


def record_decision(root: Path, tid: str, text: str, today: str | None = None) -> str:
    """Append `<UTC date> <tid> <text>` to `decisions.md`, creating it if absent; return the line.
    Needs no spec store: the log does not depend on `openspec/`."""
    line = f"{today or _utc_date()} {tid} {decision_text(text)}"
    p = root / "decisions.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return line


# ----- pin and archive ----------------------------------------------------------------------

def change_dir(root: Path, tid: str) -> Path:
    return root_dir(root) / "changes" / tid


def critic_rounds(root: Path, tid: str) -> str:
    """`## Critic rounds`: per finished critic run of the ticket, oldest first."""
    from factory import status  # local import: status has no store dependency

    runs = root / "runs"
    entries = []
    if runs.exists():
        for d in sorted(runs.iterdir()):
            mp = d / "meta.yaml"
            if not mp.exists():
                continue
            m = store.read_yaml(mp)
            if m.get("ticket") != tid or m.get("role") != "critic" or not m.get("finished"):
                continue
            body = (d / "output.md").read_text(encoding="utf-8") if (d / "output.md").exists() else ""
            entries.append(f"round {m.get('round')} · spec v{m.get('spec_version')} · {m['run_id']} · {m.get('status')}\n\n"
                           + status.strip_trailer(body).rstrip() + "\n")
    return "## Critic rounds\n\n" + ("\n".join(entries) if entries else "none\n")


def pin(root: Path, tid: str, text: str) -> list[str]:
    """Write the pinned version as the change folder (part K). Caller has validated and checked
    `applies`. Returns the relative paths written."""
    parts, _, _ = validate(text)
    d = change_dir(root, tid)
    if d.exists():
        shutil.rmtree(d)
    written = []
    for path, body in parts.items():
        if path == "verification.md":
            body = body.rstrip() + "\n\n" + critic_rounds(root, tid)
        store.write_text(d / path, body)
        written.append(str((d / path).relative_to(root)))
    return written


def decisions_of(proposal: str) -> list[str]:
    inside, out = False, []
    for line, in_fence in lines_outside_fences(proposal):
        if not in_fence and line.startswith("## "):
            inside = line.startswith("## Decisions")
            continue
        if not inside or not line.strip():
            continue
        if line[:1].isspace() and out:  # a wrapped continuation of the previous decision
            out[-1] = out[-1] + " " + line.strip()
            continue
        s = re.sub(r"^[-*]\s+", "", line.strip())
        if s.lower().rstrip(".") != "none":
            out.append(s)
    return out


# ----- what an amendment may change (`factory spec amend`) ------------------------------------

def scenario_blocks(text: str) -> dict[str, str]:
    """`#### Scenario: <name>` → its block (the heading through the line before the next `##`,
    `###` or `####` heading outside fences), over every delta part of a spec version."""
    out: dict[str, str] = {}
    for path, body in split_parts(text):
        if not DELTA_RE.match(path):
            continue
        name, buf = None, []
        for line, in_fence in lines_outside_fences(body):
            if _heading(line, in_fence):
                if name is not None:
                    out[name] = "\n".join(buf).rstrip()
                m = SCEN_RE.match(line)
                name, buf = (m.group(1), [line]) if m else (None, [])
                continue
            if name is not None:
                buf.append(line)
        if name is not None:
            out[name] = "\n".join(buf).rstrip()
    return out


def _collapsed(s: str) -> str:
    return " ".join(s.split())


def intent_of(text: str) -> tuple[str, list[str], dict[tuple[str, str, str], str]]:
    """A spec version's intent: the `## Problem` body of proposal.md; its Decisions lines; and per
    (capability, op, requirement name), the requirement block up to its first `#### Scenario:` line
    outside fences. Each with whitespace runs collapsed."""
    parts = dict(split_parts(text))
    problem, inside = [], False
    for line, in_fence in lines_outside_fences(parts.get("proposal.md", "")):
        if not in_fence and line.startswith("## "):
            inside = line.startswith("## Problem")
            continue
        if inside:
            problem.append(line)
    decisions = [_collapsed(d) for d in decisions_of(parts.get("proposal.md", ""))]
    reqs: dict[tuple[str, str, str], str] = {}
    for path, body in parts.items():
        m = DELTA_RE.match(path)
        if not m:
            continue
        for op, blocks in parse_delta(body)[0].items():
            for name, block in blocks.items():
                statement = []
                for line, in_fence in lines_outside_fences(block):
                    if not in_fence and SCEN_RE.match(line):
                        break
                    statement.append(line)
                reqs[(m.group(1), op, name)] = _collapsed("\n".join(statement))
    return _collapsed("\n".join(problem)), decisions, reqs


def intent_changes(old: str, new: str) -> list[str]:
    """Each way `new` changes `old`'s intent (`intent_of`); empty when the intent is unchanged."""
    (op_, od, orq), (np_, nd, nrq) = intent_of(old), intent_of(new)
    changes = ["the Problem section"] if op_ != np_ else []
    changes += [f"Decisions line removed: {d}" for d in od if d not in nd]
    changes += [f"Decisions line added: {d}" for d in nd if d not in od]
    changes += [f"requirement removed: {c} {o} {n}" for (c, o, n) in orq if (c, o, n) not in nrq]
    changes += [f"requirement added: {c} {o} {n}" for (c, o, n) in nrq if (c, o, n) not in orq]
    changes += [f"requirement restated: {c} {o} {n}" for (c, o, n), s in orq.items()
                if (c, o, n) in nrq and nrq[(c, o, n)] != s]
    return changes


def apply_delta(truth: str, capability: str, ops: dict[str, dict[str, str]]) -> str:
    if not truth.strip():
        truth = f"# {capability}\n\n## Requirements\n"
    have = requirement_blocks(truth)
    for n, b in ops.get("MODIFIED", {}).items():
        truth = truth.replace(have[n], b)
    for n in ops.get("REMOVED", {}):
        truth = truth.replace(have[n], "")
    for b in ops.get("ADDED", {}).values():
        truth = truth.rstrip() + "\n\n" + b
    return re.sub(r"\n{3,}", "\n\n", truth).rstrip() + "\n"


def archive(root: Path, tid: str, verifier_rows: list[str], today: str | None = None) -> dict:
    """Part K `factory archive`: verifier results, apply deltas, move the folder, append the
    decisions. Caller has checked `applies`; nothing here refuses."""
    d = change_dir(root, tid)
    date = today or _utc_date()
    ver = d / "verification.md"
    vtext = ver.read_text(encoding="utf-8") if ver.exists() else ""
    store.write_text(ver, vtext.rstrip() + "\n\n## Verifier results\n\n" + ("\n".join(verifier_rows) + "\n" if verifier_rows else "none\n"))
    applied = []
    for sub in sorted(d.glob("specs/*/spec.md")):
        cap = sub.parent.name
        ops, _ = parse_delta(sub.read_text(encoding="utf-8"))
        if not any(ops.values()):
            continue  # an op heading with nothing under it changes no current truth
        tp = truth_path(root, cap)
        cur = tp.read_text(encoding="utf-8") if tp.exists() else ""
        store.write_text(tp, apply_delta(cur, cap, ops))
        applied.append(cap)
    lines = decisions_of((d / "proposal.md").read_text(encoding="utf-8")) if (d / "proposal.md").exists() else []
    for ln in lines:
        record_decision(root, tid, ln, date)
    dest = root_dir(root) / "changes" / "archive" / f"{date}-{tid}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(d), str(dest))
    return {"archived_to": str(dest.relative_to(root)), "capabilities": applied, "decisions": len(lines)}


def delta_ops_of_change(root: Path, tid: str) -> dict[str, dict[str, dict[str, str]]]:
    d = change_dir(root, tid)
    out = {}
    for sub in sorted(d.glob("specs/*/spec.md")):
        ops, _ = parse_delta(sub.read_text(encoding="utf-8"))
        out[sub.parent.name] = ops
    return out
