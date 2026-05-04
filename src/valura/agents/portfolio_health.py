"""Portfolio health specialist — MONITOR + PROTECT."""

from __future__ import annotations

from typing import Any, AsyncIterator

from valura.market_data import benchmark_for_currency, default_range, total_return_pct
from valura.models import ClassificationResult, UserProfile

_DISCLAIMER = (
    "This is not investment advice, a research report, or a personal recommendation. "
    "Investing involves risk, including possible loss of principal. Past performance does not "
    "guarantee future results. Consult a qualified professional for advice tailored to your situation."
)


def _flag_concentration(top_pct: float) -> str:
    if top_pct >= 50:
        return "high"
    if top_pct >= 30:
        return "elevated"
    return "moderate"


async def run_portfolio_health(
    user: UserProfile,
    classification: ClassificationResult,
    *,
    stream_narrative: bool = True,
) -> AsyncIterator[tuple[str, dict[str, Any]]]:
    """
    Yields (event_kind, payload) where kind is 'delta' (text chunk) or 'result' (structured dict).
    """
    holdings = user.holdings or []
    if not holdings:
        narrative = (
            "You do not have holdings linked yet — this is actually the easiest moment to build "
            "healthy habits. Consider defining your goal (time horizon and capacity for losses), "
            "then start with a broad, low-cost global or total-market fund and add regularly. "
            "When you are ready, even a small, diversified first investment can help you learn "
            "how markets feel without taking outsized single-stock risk."
        )
        result: dict[str, Any] = {
            "concentration_risk": {
                "top_position_pct": 0.0,
                "top_3_positions_pct": 0.0,
                "flag": "n/a",
            },
            "performance": {"total_return_pct": 0.0, "annualized_return_pct": 0.0},
            "benchmark_comparison": {
                "benchmark": "n/a",
                "portfolio_return_pct": 0.0,
                "benchmark_return_pct": 0.0,
                "alpha_pct": 0.0,
            },
            "observations": [
                {
                    "severity": "info",
                    "text": "No positions on file — focus on goal-setting and a simple starter allocation when you begin.",
                }
            ],
            "disclaimer": _DISCLAIMER,
        }
        if stream_narrative:
            for piece in _chunk_text(narrative):
                yield ("delta", {"text": piece})
        yield ("result", {"structured": result, "narrative": narrative})
        return

    weights: list[tuple[str, float]] = []
    for h in holdings:
        t = str(h.get("ticker", "")).upper()
        w = float(h.get("weight_pct", 0.0) or 0.0)
        if t and t != "CASH":
            weights.append((t, w))
    if not weights:
        user_no_invest = UserProfile(
            user_id=user.user_id,
            kyc_status=user.kyc_status,
            risk_profile=user.risk_profile,
            base_currency=user.base_currency,
            holdings=[],
        )
        async for ev in run_portfolio_health(user_no_invest, classification, stream_narrative=stream_narrative):
            yield ev
        return

    weights.sort(key=lambda x: x[1], reverse=True)
    top_sym, top_w = weights[0]
    top3 = sum(w for _, w in weights[:3])
    flag = _flag_concentration(top_w)

    start, end = default_range()
    bench = benchmark_for_currency(user.base_currency)

    port_ret = 0.0
    used = 0.0
    for sym, w in weights:
        r = total_return_pct(sym, start, end)
        if r is None:
            continue
        port_ret += (w / 100.0) * r
        used += w

    if used > 0 and used < 99.9:
        port_ret = port_ret * (100.0 / used)

    bench_ret = total_return_pct(bench, start, end) or 0.0
    alpha = port_ret - bench_ret

    observations: list[dict[str, str]] = []
    if top_w >= 40:
        observations.append(
            {
                "severity": "warning",
                "text": f"About {top_w:.1f}% of the portfolio is in {top_sym} — that is a high concentration for most retail investors.",
            }
        )
    if alpha > 1.0:
        observations.append(
            {
                "severity": "info",
                "text": f"Over the last year, the basket of listed holdings is ahead of the broad benchmark by about {alpha:.1f} percentage points (not a guarantee of future results).",
            }
        )
    elif alpha < -1.0:
        observations.append(
            {
                "severity": "info",
                "text": f"Over the last year, the listed holdings trailed the broad benchmark by about {abs(alpha):.1f} percentage points — worth reviewing whether that matches your plan.",
            }
        )
    if not observations:
        observations.append(
            {
                "severity": "info",
                "text": "No single red flag stands out from concentration and simple recent performance vs a broad index — still revisit risk and costs periodically.",
            }
        )

    narrative = _build_narrative(
        top_sym=top_sym,
        top_w=top_w,
        top3=top3,
        port_ret=port_ret,
        bench_name=bench,
        bench_ret=bench_ret,
        alpha=alpha,
    )

    result = {
        "concentration_risk": {
            "top_position_pct": round(top_w, 1),
            "top_3_positions_pct": round(top3, 1),
            "flag": flag,
        },
        "performance": {
            "total_return_pct": round(port_ret, 1),
            "annualized_return_pct": round(port_ret, 1),
        },
        "benchmark_comparison": {
            "benchmark": "S&P 500" if bench == "^GSPC" else "Broad European index (STOXX 50 proxy)",
            "portfolio_return_pct": round(port_ret, 1),
            "benchmark_return_pct": round(bench_ret, 1),
            "alpha_pct": round(alpha, 1),
        },
        "observations": observations,
        "disclaimer": _DISCLAIMER,
    }

    if stream_narrative:
        for piece in _chunk_text(narrative):
            yield ("delta", {"text": piece})
    yield ("result", {"structured": result, "narrative": narrative})


def _chunk_text(text: str, size: int = 200) -> list[str]:
    out: list[str] = []
    s = text.strip()
    i = 0
    while i < len(s):
        out.append(s[i : i + size])
        i += size
    return out or [""]


def _build_narrative(
    *,
    top_sym: str,
    top_w: float,
    top3: float,
    port_ret: float,
    bench_name: str,
    bench_ret: float,
    alpha: float,
) -> str:
    blabel = "S&P 500" if bench_name == "^GSPC" else "a broad European index"
    return (
        f"Here is a plain-language snapshot. Your largest position is {top_sym} at about {top_w:.1f}% of the "
        f"listed sleeve, and the top three names together are about {top3:.1f}%. "
        f"Over roughly the last year, a simple market-cap weighting of those tickers would have returned about "
        f"{port_ret:.1f}%, while {blabel} returned about {bench_ret:.1f}%, a gap of about {alpha:+.1f} percentage points. "
        f"Use this as a starting point, not a forecast."
    )
