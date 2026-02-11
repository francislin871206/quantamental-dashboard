"""
Scoring Model — computes weighted composite scores and ranks candidates.
"""

import pandas as pd
from config import DEFAULT_WEIGHTS


def compute_composite_score(analysis: dict, weights: dict = None) -> float:
    """
    Compute weighted composite score for a single ticker analysis.

    Args:
        analysis: dict from data_engine.analyze_ticker()
        weights: dict with keys: sentiment, catalyst, insider, options, technical

    Returns:
        Composite score (0–10)
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    score = (
        analysis["sentiment_score"] * weights["sentiment"]
        + analysis["catalyst_score"] * weights["catalyst"]
        + analysis["insider_score"] * weights["insider"]
        + analysis["options_score"] * weights["options"]
        + analysis["technical_score"] * weights["technical"]
    )
    return round(score, 2)


def rank_candidates(analyses: list, weights: dict = None) -> pd.DataFrame:
    """
    Score and rank all analyzed tickers.

    Args:
        analyses: list of dicts from data_engine.analyze_ticker()
        weights: scoring weights

    Returns:
        DataFrame sorted by composite score descending
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    rows = []
    for a in analyses:
        composite = compute_composite_score(a, weights)
        rows.append({
            "Ticker": a["ticker"],
            "Company": a["name"],
            "Sector": a["sector"],
            "Price": a["price"],
            "Market Cap": a["market_cap"],
            "P/E": a["pe_ratio"],
            "Earnings": a["earnings_date"],
            "Sentiment": a["sentiment_score"],
            "Catalyst": a["catalyst_score"],
            "Insider": a["insider_score"],
            "Options": a["options_score"],
            "Technical": a["technical_score"],
            "Composite": composite,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("Composite", ascending=False).reset_index(drop=True)
        df.index = df.index + 1  # 1-based ranking
        df.index.name = "Rank"

    return df


def get_top_picks(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    """Return the top N picks from ranked DataFrame."""
    return df.head(n)


def format_market_cap(value):
    """Format market cap for display."""
    if value is None or value == 0:
        return "N/A"
    if value >= 1e12:
        return f"${value / 1e12:.1f}T"
    elif value >= 1e9:
        return f"${value / 1e9:.1f}B"
    elif value >= 1e6:
        return f"${value / 1e6:.1f}M"
    else:
        return f"${value:,.0f}"
