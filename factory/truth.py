"""`factory truth check`: replay every current-truth scenario against the git checkout that holds the
caller's directory, and compare each WHEN's output with its THEN by the exact-print rule (design,
"Replaying current truth"). Like `stats`, it only reads: main() runs it before the instance refusal,
the live-store fence and the harness lock.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from factory import instance, specstore
from factory.store import Refused

WORDS = {w: i for i, w in enumerate(("two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"), 2)}
ITEM_RE = re.compile(r"`([^`]*)`(?:,? (twice|three times))?(?: \([^`()]*\))?")
SEP_RE = re.compile(r", then |, and |, | and ")
COUNT = {None: 1, "twice": 2, "three times": 3}


def _items(s: str) -> list[str] | None:
    """LIST := ITEM (SEP ITEM)*, read in full, or None."""
    out, pos = [], 0
    while m := ITEM_RE.match(s, pos):
        out += [m.group(1)] * COUNT[m.group(2)]
        pos = m.end()
        if pos == len(s):
            return out
        if not (sep := SEP_RE.match(s, pos)):
            return None
        pos = sep.end()
    return None


def expected(then: str, block: list[str] | None) -> tuple[list[str], bool] | None:
    """The exact-print rule: (expected lines, whether the exit status must be 0) for the THEN text
    after `- THEN `, `block` being the fenced block after it; None when the rule cannot read it in full."""
    m = re.match(r"it prints (?:exactly |only )?(.*)$", then)
    if not m:
        return None
    body = m.group(1).removesuffix(".")
    exits = body.endswith((" and exits 0", ", and exits 0"))
    body = re.sub(r",? and exits 0$", "", body).removesuffix(", one per line")
    if re.fullmatch(r"these (?:\d+|[A-Za-z]+) lines:", body):
        return (block, exits) if block is not None else None
    if m := re.fullmatch(r"([a-z]+) lines, each (?:exactly )?(`.*)", body):
        first = ITEM_RE.match(m.group(2))
        if m.group(1) not in WORDS or not first:
            return None
        rest = m.group(2)[first.end():]
        tail = _items(rest.removeprefix(", then ")) if rest.startswith(", then ") else ([] if not rest else None)
        lines = [first.group(1)] * COUNT[first.group(2)] * WORDS[m.group(1)]
        return (lines + tail, exits) if tail is not None else None
    body = re.sub(r"^(?:these )?(?:\d+|[A-Za-z]+) lines(?:, one per line)?: ", "", body)
    lines = _items(body)
    return (lines, exits) if lines is not None else None


class Scenario:
    """One `#### Scenario:` block, read outside fences: its WHEN and THEN lines, its GIVEN blocks
    (the fenced blocks before the WHEN line), the fenced block after its THEN, and its quoted strings."""

    def __init__(self, cap: str, name: str, block: str):
        self.cap, self.name = cap, name
        self.whens, self.thens, self.given, self.quotes, self.given_quotes = [], [], [], [], []
        self.then_block: list[str] | None = None
        fenced = None
        for line in block.splitlines()[1:]:
            if line.lstrip().startswith("```"):
                if fenced is None:
                    fenced = []
                    continue
                if not self.whens:
                    self.given.append("\n".join(fenced) + "\n")
                elif self.thens and self.then_block is None and self.thens[0].endswith("lines:"):
                    self.then_block = fenced
                fenced = None
            elif fenced is not None:
                fenced.append(line)
            elif line.startswith("- WHEN "):
                self.whens.append(line)
            elif line.startswith("- THEN "):
                self.thens.append(line[len("- THEN "):].rstrip())
            else:
                q = re.findall(r'"([^"]+)"', line)
                self.quotes += q
                self.given_quotes += q if "GIVEN block" in line else []

    def command(self) -> str:
        """The WHEN line's text between its first and last backtick."""
        w = self.whens[0]
        return w[w.find("`") + 1:w.rfind("`")]


def _ticket(root: Path, tid: str) -> dict:
    p = root / "tickets" / f"{tid}.yaml"
    return (yaml.safe_load(p.read_text(encoding="utf-8")) or {}) if p.is_file() else {}


def _ticket_under_test(root: Path, checkout: Path) -> str | None:
    """The ticket whose checkout this is, by the store's own layout: `worktrees/<id>` (the
    implementer's worktree) or `runs/<run>/wt` (a checker's checkout, ticket in the run's meta.yaml)."""
    if checkout.parent == root / "worktrees":
        return checkout.name
    meta = checkout.parent / "meta.yaml"
    if checkout.name == "wt" and checkout.parent.parent == root / "runs" and meta.is_file():
        return (yaml.safe_load(meta.read_text(encoding="utf-8")) or {}).get("ticket")
    return None


def folded_ids(root: Path, tid: str | None) -> list[str]:
    """The ticket under test's change (its parent's, or its own), plus every unarchived change whose
    ticket is not closed and has a merged sub-ticket: that code is on the integration branch before
    its scenarios reach current truth."""
    changes = specstore.root_dir(root) / "changes"
    tickets = [yaml.safe_load(p.read_text(encoding="utf-8")) or {} for p in sorted((root / "tickets").glob("*.yaml"))]
    merged = {t.get("parent") for t in tickets if t.get("status") == "merged"}
    ids = {d.name for d in (changes.iterdir() if changes.is_dir() else ())
           if d.is_dir() and d.name != "archive" and d.name in merged and _ticket(root, d.name).get("status") != "closed"}
    if tid:
        cid = _ticket(root, tid).get("parent") or tid
        ids |= {cid} if (changes / cid).is_dir() else set()
    return sorted(ids)


def fold(root: Path, ids: list[str]) -> tuple[dict[str, str], dict[tuple[str, str], str]]:
    """Current truth with each change's delta applied, in order, as archive applies it; and, per
    (capability, scenario) in an ADDED or MODIFIED requirement of a folded delta, that change's id."""
    truth = {p.parent.name: p.read_text(encoding="utf-8")
             for p in sorted((specstore.root_dir(root) / "specs").glob("*/spec.md"))}
    owner: dict[tuple[str, str], str] = {}
    for cid in ids:
        errors = []
        for part in sorted((specstore.change_dir(root, cid) / "specs").glob("*/spec.md")):
            cap = part.parent.name
            ops, errs = specstore.parse_delta(part.read_text(encoding="utf-8"))
            # specstore.applies' check, against the text folded so far rather than the store's files
            have = specstore.requirement_blocks(truth.get(cap, ""))
            errs += [f"ADDED {n!r} is already in current truth ({cap})" for n in ops.get("ADDED", {}) if n in have]
            errs += [f"{op} {n!r} is not in current truth ({cap})"
                     for op in ("MODIFIED", "REMOVED") for n in ops.get(op, {}) if n not in have]
            if errs or not any(ops.values()):
                errors += errs
                continue
            truth[cap] = specstore.apply_delta(truth.get(cap, ""), cap, ops)
            for op in ("ADDED", "MODIFIED"):
                for b in ops.get(op, {}).values():
                    owner.update({(cap, n): cid for n in specstore.scenario_names(b)})
        if errors:
            raise Refused(f"truth check: the approved delta of {cid} does not apply to current truth: {'; '.join(errors)}")
    return truth, owner


def skip_reason(sc: Scenario, owner: dict, names: set[str], skip_texts: list[str]) -> str | None:
    if (sc.cap, sc.name) in owner:
        return f"in the approved delta of {owner[(sc.cap, sc.name)]}, which that ticket's verifier checks"
    if len(sc.whens) != 1:
        return "has no WHEN line" if not sc.whens else "has more than one WHEN line"
    cmd = sc.command()
    if sc.whens[0].count("`") < 2 or not cmd.strip():
        return "its WHEN is not one backticked command"
    for t in skip_texts:
        if t in cmd:
            return f'its WHEN contains "{t}", which this run skips'
    for q in sc.given_quotes:
        if q not in names:
            return f'needs the GIVEN block of "{q}", which current truth does not hold'
    if not sc.thens:
        return "has no THEN line"
    if len(sc.thens) > 1:
        return "has more than one THEN line"
    if expected(sc.thens[0], sc.then_block) is None:
        return f"THEN is not an exact print: {sc.thens[0]}"
    return None


def _bash(text: str, cwd: Path, env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", "-c", text], cwd=cwd, env=env, stdin=subprocess.DEVNULL, capture_output=True)


def _run_capability(todo: list[Scenario], refs, checkout: Path) -> dict[int, subprocess.CompletedProcess]:
    """Runs one capability's scenarios in file order, in a fresh HOME and TMPDIR, each after the
    GIVEN blocks it needs (each reference's needs first, then its own); a block runs at most once."""
    d = Path(tempfile.mkdtemp(prefix="factory-truth-"))
    (d / "home").mkdir()
    (d / "tmp").mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_")}
    env.update(HOME=str(d / "home"), TMPDIR=str(d / "tmp"))

    def needs(sc: Scenario, path: tuple[int, ...]) -> list[tuple[tuple[int, int], str]]:
        out = [k for r in refs(sc) if id(r) not in path for k in needs(r, (*path, id(r)))]
        return out + [((id(sc), i), b) for i, b in enumerate(sc.given)]

    ran, results = set(), {}
    try:
        for sc in todo:
            for key, block in needs(sc, (id(sc),)):
                if key not in ran:
                    ran.add(key)
                    _bash(block, checkout, env)  # a GIVEN block's exit status is not compared
            results[id(sc)] = _bash(sc.command(), checkout, env)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return results


def _lines(b: bytes) -> list[str]:
    s = b.decode("utf-8", errors="replace").removesuffix("\n")
    return s.split("\n") if s else []


def _store(a) -> Path:
    cwd = instance.caller_cwd()
    if a.store:
        return (cwd / Path(a.store).expanduser()).resolve()
    inst = instance.find()
    root = instance.env_path("FACTORY_STATE") or (
        instance.state_root(inst, instance.load_config(inst)) if inst is not None else None)
    if root is None:
        raise Refused(f"truth check: no store found: give --store PATH, set FACTORY_STATE, or run from "
                      f"inside an instance ({instance.not_found_message()})")
    return root.resolve()


def check(a) -> int:
    """Replays current truth; prints one line per scenario and the counts. 1 when any failed."""
    root = _store(a)
    if not (specstore.root_dir(root) / "specs").is_dir():
        raise Refused(f"truth check: {root} has no current truth (openspec/specs)")
    for c in a.capability:
        if not specstore.truth_path(root, c).is_file():
            raise Refused(f"truth check: no capability {c} in current truth")
    cwd = instance.caller_cwd()
    top = subprocess.run(["git", "-C", str(cwd), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0:
        raise Refused(f"truth check: {cwd} is not inside a git checkout")
    checkout = Path(top.stdout.strip()).resolve()
    ids = folded_ids(root, _ticket_under_test(root, checkout))
    start = time.monotonic()
    truth, owner = fold(root, ids)
    caps = {c: [Scenario(c, n, b) for n, b in specstore.scenario_blocks(f"=== specs/x/spec.md\n{t}").items()]
            for c, t in sorted(truth.items())}  # scenario_blocks reads delta parts: give the text one
    flat = [s for scs in caps.values() for s in scs]
    names = {s.name for s in flat}

    def refs(sc: Scenario) -> list[Scenario]:
        order = caps[sc.cap] + flat  # the same capability first, then capability order
        return [next(s for s in order if s.name == q) for q in sc.quotes if q in names]

    shown = sorted(set(a.capability) or caps)
    skips = {id(s): skip_reason(s, owner, names, a.skip_when_contains) for c in shown for s in caps.get(c, [])}
    with ThreadPoolExecutor(max_workers=max(len(shown), 1)) as ex:
        runs = [ex.submit(_run_capability, [s for s in caps.get(c, []) if not skips[id(s)]], refs, checkout)
                for c in shown]
        results = {k: v for f in runs for k, v in f.result().items()}
    wall = int(time.monotonic() - start)
    print(f"truth check: {checkout} against {root}; folded: {', '.join(ids) or 'none'}")
    n = {"PASS": 0, "FAIL": 0, "SKIPPED": 0}
    for c in shown:
        for s in caps.get(c, []):
            if skips[id(s)]:
                n["SKIPPED"] += 1
                print(f"SKIPPED {c}: {s.name}: {skips[id(s)]}")
                continue
            cp, (want, exits) = results[id(s)], expected(s.thens[0], s.then_block)
            got = _lines(cp.stdout)
            verdict = "PASS" if got == want and (cp.returncode == 0 or not exits) else "FAIL"
            n[verdict] += 1
            print(f"{verdict} {c}: {s.name}")
            if verdict == "FAIL":
                print("\n".join(["  expected:", *(f"    {x}" for x in want), "  got:", *(f"    {x}" for x in got[:40]),
                                 *([f"    … {len(got) - 40} more lines"] if len(got) > 40 else []),
                                 f"  exit {cp.returncode}",
                                 *(["  stderr:", *(f"    {x}" for x in _lines(cp.stderr)[-5:])] if cp.stderr else [])]))
    print(f"{sum(n.values())} scenarios: {n['PASS']} passed, {n['FAIL']} failed, {n['SKIPPED']} skipped; "
          f"wall time {wall} s")
    return 1 if n["FAIL"] else 0


def add_parser(sp) -> None:
    """`factory truth check`, built here so factory/cli.py stays under its line limit."""
    p = sp.add_parser("truth", help="replay current truth's scenarios against this checkout; reads, writes nothing")
    p = p.add_subparsers(dest="sub", required=True).add_parser(
        "check", help="run each current-truth scenario's WHEN under bash and compare its output with the THEN")
    p.add_argument("--store", metavar="PATH", help="the store to read; default: FACTORY_STATE, else the instance's own store")
    p.add_argument("--capability", action="append", default=[], metavar="NAME",
                   help="report and run only this capability (repeatable)")
    p.add_argument("--skip-when-contains", action="append", default=[], metavar="TEXT",
                   help="skip, and list, each scenario whose WHEN contains TEXT (repeatable)")
    p.set_defaults(fn=check)
