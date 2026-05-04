import pytest

from valura.safety import evaluate_safety


def test_safety_pairs_match_gold(safety_gold):
    ok = 0
    for row in safety_gold:
        out = evaluate_safety(row["query"])
        got = bool(getattr(out, "blocked", False))
        assert got == row["expect_block"], (row["id"], row["query"], got, row["expect_block"])
        ok += 1
    assert ok >= 45
