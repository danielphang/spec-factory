"""T-0059 (issue #120): `factory truth check` replays every current-truth scenario under bash in the
checkout under test, compares each WHEN's stdout with its THEN by the exact-print rule, lists what it
cannot check as skipped with a reason, and folds the approved deltas whose code is under test or
merged before it runs.

The rule is tested on `factory.truth.expected`, in one Python process run from the repository root
(tests/factory is itself a package named `factory`); the command black-box through the CLI on
throwaway stores built from files, each with a scratch git checkout as the caller's directory.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from ._cli import REPO, cli, git_repo, js

F = "```"


def read(cases: list) -> list:
    """`factory.truth.expected(then, block)` for each (then, block), as JSON: a tuple reads as a list."""
    code = "import json, sys\nfrom factory import truth\nprint(json.dumps([truth.expected(*c) for c in json.load(sys.stdin)]))"
    cp = subprocess.run([sys.executable, "-c", code], input=json.dumps(cases), cwd=REPO, capture_output=True, text=True)
    assert cp.returncode == 0, cp.stderr
    return json.loads(cp.stdout)


READ = [
    ("it prints `hello`", None, (["hello"], False)),
    ("it prints exactly `hello`.", None, (["hello"], False)),
    ("it prints only `a  b`, then `c`", None, (["a  b", "c"], False)),
    ("it prints `a`, and `b`, `c` and `d`", None, (["a", "b", "c", "d"], False)),
    ("it prints `ok` and exits 0", None, (["ok"], True)),
    ("it prints `ok`, and exits 0", None, (["ok"], True)),
    ("it prints exactly `x`, `y`, one per line", None, (["x", "y"], False)),
    ("it prints exactly `x` twice, then `y`, three times, one per line", None, (["x", "x", "y", "y", "y"], False)),
    ("it prints `hello`, then `bye` (the farewell second)", None, (["hello", "bye"], False)),
    ("it prints exactly two lines: `one`, then `two`", None, (["one", "two"], False)),
    ("it prints exactly these 2 lines, one per line: `one`, then `two`", None, (["one", "two"], False)),
    ("it prints exactly three lines, each `same`", None, (["same"] * 3, False)),
    ("it prints exactly two lines, each exactly `s`, then `t`", None, (["s", "s", "t"], False)),
    ("it prints exactly these 2 lines:", ["a", "b"], (["a", "b"], False)),
]
UNREAD = [
    ("it prints a friendly greeting", None),
    ("it exits 0", None),
    ("it prints `x`. The rest is ignored.", None),
    ("it prints two numbers: the first below 910, the second `3`", None),
    ("it prints one line, `files=<n>`, with n above 0", None),
    ("it prints exactly these 2 lines:", None),
    ("it prints exactly eleven lines, each `x`", None),
    ("it prints `x` (a note with `ticks`)", None),
    ("it prints `x` or `y`", None),
]


def test_exact_print_rule_reads_each_form_and_refuses_what_it_cannot_read_in_full():
    got = read([[t, b] for t, b, _ in READ] + [list(c) for c in UNREAD])
    assert got[:len(READ)] == [[w[0], w[1]] for _, _, w in READ]
    assert got[len(READ):] == [None] * len(UNREAD)


def scenario(name: str, when: str | None, then: str | None, extra: str = "") -> str:
    lines = [f"#### Scenario: {name}", *([extra] if extra else []),
             *([f"- WHEN `{when}`"] if when is not None else []), *([f"- THEN {then}"] if then is not None else [])]
    return "\n".join(lines) + "\n"


def capability(store: Path, cap: str, *scenarios: str, req: str = "It works") -> None:
    p = store / "openspec" / "specs" / cap / "spec.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"# {cap}\n\n## Requirements\n\n### Requirement: {req}\nIt SHALL work.\n\n" + "\n".join(scenarios))


def write_ticket(store: Path, tid: str, status: str, parent: str | None = None) -> None:
    (store / "tickets").mkdir(parents=True, exist_ok=True)
    (store / "tickets" / f"{tid}.yaml").write_text(f"id: {tid}\nstatus: {status}\nparent: {parent or 'null'}\n")


def delta(store: Path, cid: str, cap: str, text: str) -> None:
    p = store / "openspec" / "changes" / cid / "specs" / cap / "spec.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def results(cp) -> list[str]:
    return [ln for ln in cp.stdout.splitlines() if ln.split(" ", 1)[0] in ("PASS", "FAIL", "SKIPPED")]


@pytest.fixture
def repo(tmp_path):
    return git_repo(tmp_path / "repo")


def test_each_skip_reason_is_listed_and_counted_and_never_passed(tmp_path, repo):
    s = tmp_path / "s"
    given = f"- GIVEN the block below\n\n{F}sh\necho given > $TMPDIR/g\n{F}\n"
    capability(s, "a",
               scenario("No WHEN", None, "it prints `x`"),
               scenario("Two WHENs", "echo x", "it prints `x`", extra="- WHEN `echo y`"),
               scenario("A bare WHEN", None, "it prints `x`", extra="- WHEN echo x"),
               scenario("A slow one", "echo slow-marker", "it prints `slow-marker`"),
               scenario("A missing fixture", "echo x", "it prints `x`", extra='Needs the GIVEN block of "Nowhere" run once.'),
               scenario("No THEN", "echo x", None),
               scenario("Prose", "echo x", "it prints an x"),
               scenario("A fixture", "cat $TMPDIR/g", "it prints exactly `given`", extra=given),
               scenario("A reuse", "cat $TMPDIR/g", "it prints exactly `given`",
                        extra='Needs the GIVEN block of "A fixture" run once.'))
    cp = cli(repo, "truth", "check", "--store", str(s), "--skip-when-contains", "slow-marker")
    assert cp.returncode == 0, cp.stderr
    assert results(cp) == [
        "SKIPPED a: No WHEN: has no WHEN line",
        "SKIPPED a: Two WHENs: has more than one WHEN line",
        "SKIPPED a: A bare WHEN: its WHEN is not one backticked command",
        'SKIPPED a: A slow one: its WHEN contains "slow-marker", which this run skips',
        'SKIPPED a: A missing fixture: needs the GIVEN block of "Nowhere", which current truth does not hold',
        "SKIPPED a: No THEN: has no THEN line",
        "SKIPPED a: Prose: THEN is not an exact print: it prints an x",
        "PASS a: A fixture",
        "PASS a: A reuse",
    ]
    assert cp.stdout.splitlines()[-1].startswith("9 scenarios: 2 passed, 0 failed, 7 skipped; wall time ")


def test_a_failure_shows_expected_got_exit_and_stderr_and_exits_1(tmp_path, repo):
    s = tmp_path / "s"
    capability(s, "a", scenario("Long", "seq 45; echo oops >&2; exit 4", "it prints `1`"),
               scenario("Status", "echo ok; exit 3", "it prints `ok` and exits 0"))
    cp = cli(repo, "truth", "check", "--store", str(s))
    assert cp.returncode == 1, cp.stderr
    out = cp.stdout.splitlines()
    assert out[0] == f"truth check: {repo.resolve()} against {s.resolve()}; folded: none"
    i = out.index("FAIL a: Long")
    assert out[i + 1:i + 4] == ["  expected:", "    1", "  got:"]
    assert out[i + 4:i + 44] == [f"    {n}" for n in range(1, 41)]
    assert out[i + 44:i + 48] == ["    … 5 more lines", "  exit 4", "  stderr:", "    oops"]
    assert out[i + 48:i + 54] == ["FAIL a: Status", "  expected:", "    ok", "  got:", "    ok", "  exit 3"]
    assert out[-1].startswith("2 scenarios: 0 passed, 2 failed, 0 skipped;")


def test_the_ticket_under_test_and_open_tickets_with_merged_code_are_folded(tmp_path, repo):
    s = tmp_path / "s"
    capability(s, "a", scenario("Old greeting", "echo hello", "it prints `hello`"), req="Greets")
    capability(s, "b", scenario("Same name", "echo b", "it prints `b`"))
    new = "## MODIFIED Requirements\n\n### Requirement: Greets\nIt SHALL greet anew.\n\n" + scenario(
        "Same name", "echo new", "it prints `nope`")
    for cid, status in (("T-0001", "planned"), ("T-0002", "planned"), ("T-0003", "closed"), ("T-0004", "planned")):
        write_ticket(s, cid, status)
        delta(s, cid, "a", new)
    write_ticket(s, "T-0001.1", "checks-in-flight", "T-0001")
    write_ticket(s, "T-0002.1", "merged", "T-0002")
    write_ticket(s, "T-0003.1", "merged", "T-0003")
    wt, k = s / "worktrees" / "T-0001.1", s / "runs" / "run-0002-verifier" / "wt"
    for co in (wt, k):
        subprocess.run(["git", "-C", str(repo), "worktree", "add", "-q", "--detach", str(co)], check=True)
    (k.parent / "meta.yaml").write_text("role: verifier\nticket: T-0004\n")  # a ticket with no parent folds its own

    cp = cli(repo, "truth", "check", "--store", str(s))
    assert cp.returncode == 0, cp.stderr
    assert cp.stdout.splitlines()[0] == f"truth check: {repo.resolve()} against {s.resolve()}; folded: T-0002"
    # a scenario of another capability with the same name still runs
    assert results(cp) == ["SKIPPED a: Same name: in the approved delta of T-0002, which that ticket's verifier checks",
                           "PASS b: Same name"]
    for co, folded in ((wt, "T-0001, T-0002"), (k, "T-0002, T-0004")):
        cp = cli(co, "truth", "check", "--store", str(s))
        assert cp.stdout.splitlines()[0] == f"truth check: {co.resolve()} against {s.resolve()}; folded: {folded}"
        last = folded.split(", ")[-1]  # the later delta's id wins
        assert results(cp)[0] == f"SKIPPED a: Same name: in the approved delta of {last}, which that ticket's verifier checks"


def test_a_delta_that_does_not_apply_is_refused_naming_its_ticket_and_nothing_runs(tmp_path, repo):
    s = tmp_path / "s"
    capability(s, "a", scenario("Writes", f"touch {tmp_path}/ran; echo x", "it prints `x`"))
    write_ticket(s, "T-0005", "planned")
    write_ticket(s, "T-0005.1", "merged", "T-0005")
    delta(s, "T-0005", "a", "## ADDED Requirements\n\n### Requirement: It works\nAgain.\n")
    cp = cli(repo, "truth", "check", "--store", str(s))
    assert cp.returncode == 2
    assert cp.stderr.strip() == ("truth check: the approved delta of T-0005 does not apply to current truth: "
                                 "ADDED 'It works' is already in current truth (a)")
    assert js(cp)["ok"] is False and not results(cp) and not (tmp_path / "ran").exists()


def test_refusals(tmp_path, repo):
    s = tmp_path / "s"
    capability(s, "a", scenario("One", "echo 1", "it prints `1`"))
    (tmp_path / "bare").mkdir()
    cases = [
        (repo, ["--store", str(s), "--capability", "nope"], "truth check: no capability nope in current truth"),
        (repo, ["--store", str(tmp_path / "bare")], f"truth check: {(tmp_path / 'bare').resolve()} has no current truth (openspec/specs)"),
        (tmp_path / "bare", ["--store", str(s)], f"truth check: {(tmp_path / 'bare').resolve()} is not inside a git checkout"),
    ]
    for cwd, argv, err in cases:
        cp = cli(cwd, "truth", "check", *argv)
        assert (cp.returncode, cp.stderr.strip(), js(cp)["ok"]) == (2, err, False)
    z = "0123456789abcdef0123456789abcdef01234567"
    cp = cli(repo, "--accept-harness", z, "truth", "check", "--store", str(s))
    assert cp.returncode == 2 and "factory truth check never checks the harness lock" in cp.stderr
    assert f"factory --accept-harness {z} config" in cp.stderr
