"""Entity normalization for subset matching against gold fixtures."""

from __future__ import annotations

import re
from typing import Any

_TICKER_SUFFIXES = (".US", ".AS", ".L", ".PA", ".DE", ".TO", ".T", ".HK")


def normalize_ticker(raw: str) -> str:
    s = raw.strip().casefold()
    for suf in _TICKER_SUFFIXES:
        if s.endswith(suf.casefold()):
            s = s[: -len(suf)].strip(".")
            break
    return re.sub(r"[^a-z0-9]", "", s)


def normalize_topic(raw: str) -> str:
    return " ".join(raw.strip().casefold().split())


def normalize_sector(raw: str) -> str:
    return normalize_topic(raw)


def entities_subset(actual: dict[str, Any], expected: dict[str, Any]) -> tuple[bool, str]:
    """
    True if `actual` covers `expected` under normalization rules:
    - string lists: every expected item matches some actual item
    - numerics: within 5% when expected value is not null
    """
    for k, ev in expected.items():
        if ev in (None, [], ""):
            continue
        av = actual.get(k)
        if k in ("tickers", "topics", "sectors") and isinstance(ev, list):
            if not isinstance(av, list):
                return False, f"{k}: not a list in actual"
            if k == "tickers":
                an = {normalize_ticker(str(x)) for x in av}
                for t in ev:
                    tn = normalize_ticker(str(t))
                    if tn in an:
                        continue
                    if not any(_compatible_ticker(tn, x) for x in an):
                        return False, f"ticker {t!r} not found in {av!r}"
            else:
                fn = normalize_topic if k == "topics" else normalize_sector
                anorm = {fn(x) for x in av}
                for item in ev:
                    if fn(str(item)) not in anorm:
                        return False, f"{k}: missing {item!r}"
        elif k in ("amount", "rate", "period_years") and isinstance(ev, (int, float)):
            if av is None:
                return False, f"{k}: expected numeric {ev}, got None"
            try:
                fv = float(av)
                evf = float(ev)
                if evf == 0:
                    if abs(fv) > 1e-6:
                        return False, f"{k}: expected ~0"
                elif abs(fv - evf) / max(abs(evf), 1e-9) > 0.05:
                    return False, f"{k}: {fv} not within 5% of {evf}"
            except (TypeError, ValueError):
                return False, f"{k}: not coercible to float"
    return True, "ok"


def _compatible_ticker(a: str, b: str) -> bool:
    return a == b or a.startswith(b) or b.startswith(a)
