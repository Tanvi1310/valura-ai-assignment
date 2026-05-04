"""Synchronous safety guard — local pattern checks only, no network."""

from __future__ import annotations

import re
from functools import lru_cache

from valura.models import SafetyBlock, SafetyCategory, SafetyOutcome, SafetyPass


_MESSAGES: dict[SafetyCategory, str] = {
    "insider_trading": (
        "We cannot assist with trading on material nonpublic information or circumventing "
        "insider-trading rules. If you have MNPI, avoid trading affected securities and consult "
        "compliance counsel."
    ),
    "market_manipulation": (
        "We cannot help execute or plan market manipulation (including spoofing, wash trading, "
        "pumps, corners, or deceptive volumes). Market integrity rules prohibit these behaviors."
    ),
    "money_laundering": (
        "We cannot assist with concealing proceeds of crime, structuring transactions to evade "
        "reporting, or bypassing AML/KYC controls. Brokers must follow applicable AML obligations."
    ),
    "guaranteed_returns": (
        "We cannot promise or imply guaranteed investment returns or risk-free outsized gains. "
        "Investments involve risk of loss; seek regulated disclosures and suitability guidance."
    ),
    "reckless_advice": (
        "We cannot recommend extreme leverage, gambling savings on concentrated speculative bets, "
        "or strategies likely inconsistent with prudent retail investing. Consider diversification "
        "and your risk tolerance."
    ),
}

# Always block: clear instructions to do harm.
_HARD_BLOCK: list[tuple[re.Pattern[str], SafetyCategory]] = [
    (
        re.compile(
            r"non-?public.*(leak|leaked|before (they are )?released)|"
            r"share tomorrow earnings|"
            r"how can i trade on material nonpublic|"
            r"front run my employer|"
            r"tell me which insider tips to buy|"
            r"ignore compliance.*insider stuff",
            re.I | re.S,
        ),
        "insider_trading",
    ),
    (
        re.compile(
            r"help me run a pump|"
            r"how do i spoof|"
            r"pump and dump on a small cap|"
            r"corner the float|"
            r"layering bids|"
            r"create fake volume",
            re.I,
        ),
        "market_manipulation",
    ),
    (
        re.compile(
            r"move illegal proceeds|"
            r"crypto mixer.*brokerage|"
            r"structuring deposits to avoid|"
            r"smurf transactions|"
            r"use nominee accounts to hide|"
            r"bypass aml checks",
            re.I | re.S,
        ),
        "money_laundering",
    ),
    (
        re.compile(
            r"guarantee me .*returns|"
            r"promise this etf will never lose|"
            r"generate guaranteed passive income with no risk|"
            r"triple my account every month risk free|"
            r"guaranteed dividend forever",
            re.I,
        ),
        "guaranteed_returns",
    ),
    (
        re.compile(
            r"tell me to borrow maximum margin|"
            r"i want to put 100 percent of my savings into .*0dte|"
            r"borrow payday loans to day trade|"
            r"invest rent money in leveraged",
            re.I | re.S,
        ),
        "reckless_advice",
    ),
]

_EDU_PARTS: list[re.Pattern[str]] = [
    re.compile(
        r"(?is)^(what is|what are|why do|why does|explain|define|describe|"
        r"teach me what constitutes|how does|how do(?!\s+i\b)|"
        r"what does|what was|overview of|basics of|introduction to|"
        r"examples of|history of|under (us|u\.s\.)\s+law|regulatory perspective|"
        r"sec rules on|enforcement examples|"
        r"margin trading risks explained|"
        r"educational overview|book recommendation|podcast about|course outline|"
        r"anti money laundering compliance)\b",
    ),
    re.compile(r"(?is)^learn how (?!to (move|launder|spoof|pump)\b)", re.I),
    re.compile(r"\bfor academic purposes\b", re.I),
    re.compile(r"\bfrom a regulatory perspective\b", re.I),
    re.compile(r"\bfinancial crime enforcement\b", re.I),
]


def _edu_whitelist(q: str) -> bool:
    s = q.strip()
    if any(p.search(s) for p in _EDU_PARTS):
        return True
    if re.search(r"\b(pump and dump prosecutions|market manipulation cases)\b", s, re.I):
        return True
    if re.search(r"^\s*what are aml\b", s, re.I):
        return True
    if re.search(r"why regulators prohibit", s, re.I):
        return True
    return False


_SOFT_BUCKETS: list[tuple[re.Pattern[str], SafetyCategory]] = [
    (re.compile(r"\b(material nonpublic|mnpi|insider tips? to buy|insider stuff)\b", re.I), "insider_trading"),
    (re.compile(r"\b(pump and dump(?! prosecutions)|spoof(ing)? orders|wash trad)\b", re.I), "market_manipulation"),
    (re.compile(r"\b(money laundering|crypto mixer|structuring deposits|smurf)\b", re.I), "money_laundering"),
    (re.compile(r"\b(guarantee(d)? returns|promised?.*guaranteed|no risk.*income)\b", re.I), "guaranteed_returns"),
    (re.compile(r"\b100%\s*of my savings|all in on one ticker|maximum margin|meme stocks\b", re.I), "reckless_advice"),
]


@lru_cache(maxsize=1)
def _warm() -> None:
    for rx, _ in _HARD_BLOCK + _SOFT_BUCKETS:
        rx.pattern  # noqa: B018
    for rx in _EDU_PARTS:
        rx.pattern  # noqa: B018


def evaluate_safety(user_query: str) -> SafetyOutcome:
    """Pure local guard; completes in milliseconds."""
    _warm()
    q = user_query.strip()

    for rx, cat in _HARD_BLOCK:
        if rx.search(q):
            return SafetyBlock(category=cat, message=_MESSAGES[cat])

    if _edu_whitelist(q):
        return SafetyPass()

    for rx, cat in _SOFT_BUCKETS:
        if rx.search(q):
            return SafetyBlock(category=cat, message=_MESSAGES[cat])
    return SafetyPass()
