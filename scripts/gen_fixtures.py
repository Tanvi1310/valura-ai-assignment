import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

cases = [
    ("ic_001", "How is my portfolio doing?", "portfolio_health", {}),
    ("ic_002", "Give me a quick health check on my holdings.", "portfolio_health", {}),
    ("ic_003", "Am I diversified enough?", "portfolio_health", {"topics": ["diversification"]}),
    ("ic_004", "What is my concentration risk?", "portfolio_health", {"topics": ["concentration"]}),
    ("ic_005", "Compare my returns to the S and P 500", "portfolio_health", {"topics": ["benchmark"]}),
    ("ic_006", "What was Apple revenue last quarter?", "market_research", {"tickers": ["AAPL"]}),
    ("ic_007", "Tell me about NVDA fundamentals", "market_research", {"tickers": ["NVDA"]}),
    ("ic_008", "How did semiconductors perform YTD?", "market_research", {"sectors": ["semiconductors"]}),
    ("ic_009", "What is the latest news on Tesla?", "market_research", {"tickers": ["TSLA"]}),
    ("ic_010", "Chart MSFT vs GOOGL", "market_research", {"tickers": ["MSFT", "GOOGL"]}),
    ("ic_011", "I want a long term plan for retirement in 20 years", "investment_strategy", {"period_years": 20.0}),
    ("ic_012", "Should I tilt more to value or growth?", "investment_strategy", {}),
    ("ic_013", "How do I build a 60/40 portfolio?", "investment_strategy", {}),
    ("ic_014", "What allocation fits a moderate risk profile?", "investment_strategy", {}),
    ("ic_015", "Compound 10000 at 7 percent for 10 years", "financial_calculator", {"amount": 10000, "rate": 0.07, "period_years": 10.0}),
    ("ic_016", "If I invest 2500 monthly at 6 percent how much in 15 years", "financial_calculator", {"amount": 2500, "rate": 0.06, "period_years": 15.0}),
    ("ic_017", "What is the future value of 50000 over 5 years at 4 percent", "financial_calculator", {"amount": 50000, "rate": 0.04, "period_years": 5.0}),
    ("ic_018", "Convert APR to monthly rate for this loan", "financial_calculator", {"rate": 0.05}),
    ("ic_019", "Help me understand wash sale rules", "risk_compliance", {}),
    ("ic_020", "What disclosures apply if I trade options?", "risk_compliance", {}),
    ("ic_021", "Is this dividend eligible for qualified treatment?", "risk_compliance", {}),
    ("ic_022", "I cannot log in to my account", "customer_support", {}),
    ("ic_023", "Where do I find tax documents?", "customer_support", {}),
    ("ic_024", "Reset my two factor authentication", "customer_support", {}),
    ("ic_025", "Forecast next quarter revenue for ASML", "predictive_analysis", {"tickers": ["ASML"]}),
    ("ic_026", "What scenarios could crash tech stocks?", "predictive_analysis", {}),
    ("ic_027", "Estimate downside if rates rise 100bps", "predictive_analysis", {}),
    ("ic_028", "Suggest three stocks to buy tomorrow", "recommendation_engine", {}),
    ("ic_029", "What should I buy with 10000 dollars", "recommendation_engine", {"amount": 10000}),
    ("ic_030", "Recommend ETFs for a beginner", "recommendation_engine", {}),
    ("ic_031", "Deep dive on Amazon AWS margins", "market_research", {"tickers": ["AMZN"]}),
    ("ic_032", "Explain eurozone CPI trend", "market_research", {"topics": ["inflation"]}),
    ("ic_033", "Bond ladder vs bullet for retirees", "investment_strategy", {}),
    ("ic_034", "Monte carlo retirement success rate", "financial_calculator", {}),
    ("ic_035", "Are my trades reported to regulators correctly?", "risk_compliance", {}),
    ("ic_036", "App crashed during order placement", "customer_support", {}),
    ("ic_037", "Monte carlo equity paths next year", "predictive_analysis", {}),
    ("ic_038", "Best dividend stocks for passive income", "recommendation_engine", {}),
    ("ic_039", "How liquid is my portfolio?", "portfolio_health", {"topics": ["liquidity"]}),
    ("ic_040", "Show tracking error vs benchmark", "portfolio_health", {"topics": ["tracking error"]}),
    ("ic_041", "EU stocks outlook", "market_research", {"sectors": ["europe"]}),
    ("ic_042", "Tax loss harvesting strategy basics", "investment_strategy", {}),
    ("ic_043", "IRR on my cash flows", "financial_calculator", {}),
    ("ic_044", "Pattern day trader rules", "risk_compliance", {}),
    ("ic_045", "Change my mailing address", "customer_support", {}),
    ("ic_046", "Stress test my portfolio", "predictive_analysis", {}),
    ("ic_047", "Robo advisor vs self directed", "recommendation_engine", {}),
    ("ic_048", "Is everything OK with my investments?", "portfolio_health", {}),
    ("ic_049", "Performance attribution by sector", "portfolio_health", {}),
    ("ic_050", "Oil sector macro drivers", "market_research", {"sectors": ["energy"]}),
    ("ic_051", "Rebalance quarterly or yearly?", "investment_strategy", {}),
    ("ic_052", "Loan amortization payment amount on 200k at 6.5 percent for 30 years", "financial_calculator", {"amount": 200000, "rate": 0.065, "period_years": 30.0}),
    ("ic_053", "Insider reporting obligations", "risk_compliance", {}),
    ("ic_054", "Wire transfer status", "customer_support", {}),
    ("ic_055", "Scenario analysis recession", "predictive_analysis", {}),
    ("ic_056", "Best funds for ESG", "recommendation_engine", {}),
    ("ic_057", "How risky is my portfolio overall?", "portfolio_health", {}),
    ("ic_058", "Compare ASML US vs Amsterdam listing", "market_research", {"tickers": ["ASML", "ASML.AS"]}),
    ("ic_059", "Goal based investing vs stock picking", "investment_strategy", {}),
    ("ic_060", "Present value of annuity", "financial_calculator", {"amount": 1000, "rate": 0.05, "period_years": 10.0}),
]


def main() -> None:
    out = []
    for id_, q, agent, ent in cases:
        ee = {
            "tickers": ent.get("tickers", []),
            "topics": ent.get("topics", []),
            "sectors": ent.get("sectors", []),
            "amount": ent.get("amount"),
            "rate": ent.get("rate"),
            "period_years": ent.get("period_years"),
        }
        out.append({"id": id_, "query": q, "expected_agent": agent, "expected_entities": ee})
    path = ROOT / "fixtures" / "test_queries" / "intent_classification.json"
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", path, "n=", len(out))


if __name__ == "__main__":
    main()
