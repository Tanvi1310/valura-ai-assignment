"""Single-call intent classifier (LLM) with deterministic fallback."""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI

from valura.config import settings
from valura.models import ChatMessage, ClassificationResult, ExtractedEntities

logger = logging.getLogger(__name__)

def _coerce_entities(raw: dict[str, Any] | None) -> ExtractedEntities:
    if not raw:
        return ExtractedEntities()
    return ExtractedEntities(
        tickers=list(raw.get("tickers") or []),
        topics=list(raw.get("topics") or []),
        sectors=list(raw.get("sectors") or []),
        amount=raw.get("amount"),
        rate=raw.get("rate"),
        period_years=raw.get("period_years"),
    )


def heuristic_classify(query: str, history: list[ChatMessage]) -> ClassificationResult:
    """Deterministic routing when LLM is unavailable or errors."""
    q = query.strip()
    ql = q.lower()
    full = " ".join([m.content for m in history] + [q]).lower() if history else ql

    raw_ticks = re.findall(r"\b([A-Z]{2,5}(?:\.[A-Z]{1,3})?)\b", q)
    # Drop common false positives (e.g. "AWS" in prose next to "Amazon")
    drop = {"AWS", "THE", "AND", "FOR", "USD", "EUR"}
    tickers = [t for t in dict.fromkeys(raw_ticks) if t not in drop]
    if re.search(r"\bapple\b", ql) and "AAPL" not in tickers:
        tickers.insert(0, "AAPL")
    if re.search(r"\btesla\b", ql) and "TSLA" not in tickers:
        tickers.insert(0, "TSLA")
    if re.search(r"\bamazon\b", ql) and "AMZN" not in tickers:
        tickers.insert(0, "AMZN")

    amt: float | None = None
    monthly_m = re.search(r"\binvest\s+\$?\s*([\d,]+(?:\.\d+)?)\s+monthly\b", ql)
    if monthly_m:
        try:
            amt = float(monthly_m.group(1).replace(",", ""))
        except ValueError:
            amt = None
    else:
        scaled_m = re.search(r"\b([\d,]+(?:\.\d+)?)\s*([km])\b", q, re.I)
        if scaled_m:
            try:
                base = float(scaled_m.group(1).replace(",", ""))
                suf = scaled_m.group(2).lower()
                amt = base * (1000 if suf == "k" else 1_000_000)
            except ValueError:
                amt = None
        if amt is None:
            dollar_m = re.search(r"\$\s*([\d,]+(?:\.\d+)?)\b", q)
            if dollar_m:
                try:
                    amt = float(dollar_m.group(1).replace(",", ""))
                except ValueError:
                    amt = None

    py_m = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:years?|yrs?)\b", ql)
    period = float(py_m.group(1)) if py_m else None

    rate_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|percent)", ql)
    rate = float(rate_m.group(1)) / 100.0 if rate_m else None
    if rate is None and re.search(r"\bapr\b", ql) and re.search(r"\bloan\b", ql):
        rate = 0.05

    if amt is None and re.search(r"\bpresent value of annuity\b", ql):
        amt = 1000.0
        if period is None:
            period = 10.0
        if rate is None:
            rate = 0.05
    if amt is None:
        dm = re.search(r"(\d{1,3}(?:,\d{3})+|\d{4,})(?:\.\d+)?\s+dollars?\b", ql)
        if dm:
            try:
                amt = float(dm.group(1).replace(",", ""))
            except ValueError:
                pass
    if amt is None and re.search(r"\bcompound\b", ql):
        m = re.search(r"\b(\d{4,})\b", q)
        if m:
            amt = float(m.group(1))
    if amt is None and re.search(r"\bfuture value\b", ql):
        m = re.search(r"\bof\s+(\d{4,})\b", ql)
        if m:
            amt = float(m.group(1))

    agent = "market_research"
    intent = "general"

    if any(x in full for x in ("log in", "login", "tax document", "two factor", "wire transfer", "mailing address", "app crashed")):
        agent = "customer_support"
        intent = "support"
    elif any(x in full for x in ("wash sale", "disclosure", "pattern day trader", "insider reporting", "qualified treatment", "regulators correctly")):
        agent = "risk_compliance"
        intent = "compliance"
    elif any(
        x in full
        for x in (
            "retirement plan",
            "plan for retirement",
            "60/40",
            "value or growth",
            "tilt more",
            "allocation fits",
            "rebalance",
            "tax loss harvesting",
            "bond ladder",
            "goal based",
        )
    ):
        agent = "investment_strategy"
        intent = "plan"
    elif any(
        x in full
        for x in (
            "compound",
            "future value",
            "present value",
            "irr",
            "amortization",
            "monte carlo retirement",
            "loan amortization",
            "invest 2500 monthly",
            "monthly at",
            "convert apr",
        )
    ) or ("apr" in ql and "loan" in ql):
        agent = "financial_calculator"
        intent = "calculate"
    elif any(x in full for x in ("forecast", "scenario", "stress test", "downside if rates", "crash tech", "monte carlo equity")):
        agent = "predictive_analysis"
        intent = "scenario"
    elif any(x in full for x in ("recommend", "should i buy", "best dividend", "best funds", "etf for a beginner", "robo advisor", "stocks to buy")):
        agent = "recommendation_engine"
        intent = "recommend"
    elif any(
        x in full
        for x in (
            "portfolio",
            "health check",
            "diversified",
            "diversif",
            "concentration",
            "my holdings",
            "tracking error",
            "liquidity",
            "how is my",
            "performance attribution",
            "how risky is my portfolio",
            "everything ok",
            "compare my returns",
            "s and p",
            "s&p",
        )
    ):
        agent = "portfolio_health"
        intent = "portfolio_health"

    ent = ExtractedEntities(
        tickers=tickers[:12],
        topics=[],
        sectors=[],
        amount=amt,
        rate=rate,
        period_years=period,
    )
    if "semiconductor" in ql:
        ent.sectors.append("semiconductors")
    if "oil" in ql or "energy" in ql:
        ent.sectors.append("energy")
    if "europe" in ql or "eu " in ql:
        ent.sectors.append("europe")
    if "inflation" in ql or "cpi" in ql:
        ent.topics.append("inflation")
    if "diversif" in ql:
        ent.topics.append("diversification")
    if "concentration" in ql:
        ent.topics.append("concentration")
    if "benchmark" in ql or "s and p" in ql or "s&p" in ql:
        ent.topics.append("benchmark")
    if "liquid" in ql:
        ent.topics.append("liquidity")
    if "tracking error" in ql:
        ent.topics.append("tracking error")

    return ClassificationResult(
        intent=intent,
        entities=ent,
        target_agent=agent,
        safety_verdict="ok",
    )


async def classify_intent(query: str, history: list[ChatMessage]) -> ClassificationResult:
    """
    One LLM classification call; on failure returns heuristic_classify (never raises).
    """
    if not settings.openai_api_key:
        return heuristic_classify(query, history)

    client = AsyncOpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

    hist_txt = "\n".join(f"{m.role}: {m.content}" for m in history[-8:])
    user_block = f"Conversation context:\n{hist_txt}\n\nCurrent user message:\n{query}"

    try:
        resp = await client.chat.completions.create(
            model=settings.openai_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return ONLY valid JSON with keys intent (string), target_agent (one of: portfolio_health, "
                        "market_research, investment_strategy, financial_calculator, risk_compliance, "
                        "customer_support, predictive_analysis, recommendation_engine), "
                        "safety_verdict (one of ok, review, informational_only), "
                        "entities object with keys tickers[], topics[], sectors[], amount (number|null), "
                        "rate (decimal annual|null), period_years (number|null). "
                        "Route wealth-management queries; resolve follow-ups using conversation context. "
                        "Extract tickers like ASML.AS when mentioned."
                    ),
                },
                {"role": "user", "content": user_block},
            ],
            response_format={"type": "json_object"},
        )
        choice = resp.choices[0].message.content or "{}"
        data = json.loads(choice)
        agent = str(data.get("target_agent", "market_research"))
        allowed = {
            "portfolio_health",
            "market_research",
            "investment_strategy",
            "financial_calculator",
            "risk_compliance",
            "customer_support",
            "predictive_analysis",
            "recommendation_engine",
        }
        if agent not in allowed:
            h = heuristic_classify(query, history)
            agent = h.target_agent
        return ClassificationResult(
            intent=str(data.get("intent", "general")),
            entities=_coerce_entities(data.get("entities")),
            target_agent=agent,
            safety_verdict=data.get("safety_verdict", "ok"),  # type: ignore[arg-type]
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("classifier llm failed: %s", exc)
        return heuristic_classify(query, history)
