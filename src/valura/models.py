from typing import Any, Literal

from pydantic import BaseModel, Field

SafetyCategory = Literal[
    "insider_trading",
    "market_manipulation",
    "money_laundering",
    "guaranteed_returns",
    "reckless_advice",
]

AgentName = Literal[
    "portfolio_health",
    "market_research",
    "investment_strategy",
    "financial_calculator",
    "risk_compliance",
    "customer_support",
    "predictive_analysis",
    "recommendation_engine",
]


class ExtractedEntities(BaseModel):
    tickers: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    sectors: list[str] = Field(default_factory=list)
    amount: float | None = None
    rate: float | None = None
    period_years: float | None = None


class ClassificationResult(BaseModel):
    intent: str
    entities: ExtractedEntities
    target_agent: str
    safety_verdict: Literal["ok", "review", "informational_only"] = "ok"

    model_config = {"extra": "ignore"}


class SafetyBlock(BaseModel):
    blocked: Literal[True] = True
    category: SafetyCategory
    message: str


class SafetyPass(BaseModel):
    blocked: Literal[False] = False


SafetyOutcome = SafetyBlock | SafetyPass


class UserProfile(BaseModel):
    user_id: str
    kyc_status: str | None = None
    risk_profile: str | None = None
    base_currency: str = "USD"
    holdings: list[dict[str, Any]] = Field(default_factory=list)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class QueryRequest(BaseModel):
    query: str
    session_id: str
    user: UserProfile


class StubAgentPayload(BaseModel):
    intent: str
    entities: ExtractedEntities
    target_agent: str
    message: str
