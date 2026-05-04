import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def intent_gold() -> list[dict]:
    p = ROOT / "fixtures" / "test_queries" / "intent_classification.json"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def safety_gold() -> list[dict]:
    p = ROOT / "fixtures" / "test_queries" / "safety_pairs.json"
    return json.loads(p.read_text(encoding="utf-8"))


@pytest.fixture()
def user_empty():
    p = ROOT / "fixtures" / "users" / "user_004_empty.json"
    return json.loads(p.read_text(encoding="utf-8"))
