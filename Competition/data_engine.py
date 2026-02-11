"""
Data Engine — fetches price data, news sentiment, insider info, and technical indicators.
All data sources are free (yfinance + FinViz scraping + TextBlob).
"""

import pandas as pd
import numpy as np
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from datetime import datetime, timedelta
import warnings
import time
import re

warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


# ─── Price Data ───────────────────────────────────────────────────────────────

def fetch_price_data(ticker: str, period: str = "6mo") -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        if df.empty:
            return pd.DataFrame()
        df.index = df.index.tz_localize(None)
        return df
    except Exception:
        return pd.DataFrame()


def fetch_stock_info(ticker: str) -> dict:
    """Fetch basic stock info (market cap, P/E, sector, etc.)."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "ticker": ticker,
            "name": info.get("shortName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", None),
            "ps_ratio": info.get("priceToSalesTrailing12Months", None),
            "price": info.get("currentPrice", info.get("regularMarketPrice", 0)),
            "avg_volume": info.get("averageVolume", 0),
            "beta": info.get("beta", 1.0),
            "earnings_date": _get_next_earnings(info),
        }
    except Exception:
        return {"ticker": ticker, "name": ticker, "sector": "N/A", "industry": "N/A",
                "market_cap": 0, "pe_ratio": None, "ps_ratio": None, "price": 0,
                "avg_volume": 0, "beta": 1.0, "earnings_date": None}


def _get_next_earnings(info: dict):
    """Extract next earnings date from yfinance info dict."""
    try:
        dates = info.get("earningsTimestamps", [])
        if dates:
            future = [d for d in dates if d > datetime.now().timestamp()]
            if future:
                return datetime.fromtimestamp(min(future)).strftime("%Y-%m-%d")
    except Exception:
        pass
    return None


# ─── News Sentiment ──────────────────────────────────────────────────────────

def fetch_news_sentiment(ticker: str) -> dict:
    """
    Scrape FinViz news headlines for a ticker and compute sentiment.
    Returns dict with headlines list and average sentiment score.
    """
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}&ty=c&p=d&b=1"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        news_table = soup.find(id="news-table")
        if not news_table:
            return {"headlines": [], "avg_sentiment": 0, "positive_pct": 0, "count": 0}

        rows = news_table.find_all("tr")
        headlines = []
        for row in rows[:30]:  # Last 30 headlines
            cells = row.find_all("td")
            if len(cells) >= 2:
                text = cells[1].get_text(strip=True)
                if text:
                    blob = TextBlob(text)
                    headlines.append({
                        "headline": text,
                        "sentiment": round(blob.sentiment.polarity, 3),
                        "subjectivity": round(blob.sentiment.subjectivity, 3),
                    })

        if not headlines:
            return {"headlines": [], "avg_sentiment": 0, "positive_pct": 0, "count": 0}

        sentiments = [h["sentiment"] for h in headlines]
        positive_count = sum(1 for s in sentiments if s > 0.05)

        return {
            "headlines": headlines,
            "avg_sentiment": round(np.mean(sentiments), 3),
            "positive_pct": round(positive_count / len(sentiments) * 100, 1),
            "count": len(headlines),
        }
    except Exception:
        return {"headlines": [], "avg_sentiment": 0, "positive_pct": 0, "count": 0}


# ─── Insider Trading ─────────────────────────────────────────────────────────

def fetch_insider_data(ticker: str) -> dict:
    """
    Scrape FinViz insider trading data.
    Returns summary of recent insider activity.
    """
    try:
        url = f"https://finviz.com/quote.ashx?t={ticker}&ty=c&p=d&b=1"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Look for insider trading table
        tables = soup.find_all("table", class_="body-table")
        insider_data = {
            "total_buys": 0,
            "total_sells": 0,
            "net_activity": "Neutral",
            "recent_transactions": [],
        }

        # Try to parse insider ownership from the snapshot table
        snapshot = soup.find_all("table", class_="snapshot-table2")
        if snapshot:
            for table in snapshot:
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td")
                    for i, cell in enumerate(cells):
                        text = cell.get_text(strip=True)
                        if "Insider Own" in text and i + 1 < len(cells):
                            insider_data["insider_ownership"] = cells[i + 1].get_text(strip=True)
                        if "Insider Trans" in text and i + 1 < len(cells):
                            trans_text = cells[i + 1].get_text(strip=True)
                            insider_data["insider_trans"] = trans_text
                            try:
                                trans_val = float(trans_text.replace("%", ""))
                                if trans_val > 0:
                                    insider_data["net_activity"] = "Buying"
                                    insider_data["total_buys"] = 1
                                elif trans_val < 0:
                                    insider_data["net_activity"] = "Selling"
                                    insider_data["total_sells"] = 1
                            except ValueError:
                                pass

        return insider_data
    except Exception:
        return {"total_buys": 0, "total_sells": 0, "net_activity": "Neutral",
                "recent_transactions": []}


# ─── Technical Analysis ──────────────────────────────────────────────────────

def compute_technical_indicators(df: pd.DataFrame) -> dict:
    """
    Compute technical indicators from price data.
    Returns dict of indicator values and an overall technical score (0-10).
    """
    if df.empty or len(df) < 50:
        return {"sma_50": 0, "sma_200": 0, "rsi": 50, "score": 5,
                "signal": "Neutral", "above_sma50": False, "golden_cross": False}

    close = df["Close"]

    # SMAs
    sma_50 = close.rolling(50).mean().iloc[-1]
    sma_200 = close.rolling(200).mean().iloc[-1] if len(df) >= 200 else close.rolling(len(df)).mean().iloc[-1]

    # RSI (14-period)
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain.iloc[-1] / max(loss.iloc[-1], 0.001)
    rsi = 100 - (100 / (1 + rs))

    # Current price
    price = close.iloc[-1]

    # Scoring
    score = 5.0  # base
    above_sma50 = price > sma_50
    golden_cross = sma_50 > sma_200 if len(df) >= 200 else False

    if above_sma50:
        score += 1.5
    if golden_cross:
        score += 1.5
    if 40 < rsi < 70:  # healthy momentum zone
        score += 1.0
    elif rsi < 30:  # oversold bounce potential
        score += 0.5
    elif rsi > 70:  # overbought risk
        score -= 1.0

    # Breakout: price near 52-week high
    high_52w = close.tail(252).max() if len(close) >= 252 else close.max()
    if price > high_52w * 0.95:
        score += 1.0

    # Volume trend
    if len(df) >= 20:
        vol_avg_20 = df["Volume"].tail(20).mean()
        vol_avg_5 = df["Volume"].tail(5).mean()
        if vol_avg_5 > vol_avg_20 * 1.5:
            score += 0.5  # volume surge

    score = max(0, min(10, score))

    signal = "Bullish" if score >= 7 else ("Bearish" if score <= 3 else "Neutral")

    return {
        "sma_50": round(sma_50, 2),
        "sma_200": round(sma_200, 2),
        "rsi": round(rsi, 1),
        "price": round(price, 2),
        "score": round(score, 1),
        "signal": signal,
        "above_sma50": above_sma50,
        "golden_cross": golden_cross,
    }


# ─── Catalyst Proximity ──────────────────────────────────────────────────────

def compute_catalyst_score(stock_info: dict) -> float:
    """
    Score based on proximity to next earnings date.
    Closer earnings = higher score (event catalyst effect).
    """
    earnings_date = stock_info.get("earnings_date")
    if not earnings_date:
        return 5.0  # neutral if unknown

    try:
        ed = datetime.strptime(earnings_date, "%Y-%m-%d")
        days_until = (ed - datetime.now()).days

        if days_until < 0:
            return 3.0  # already passed
        elif days_until <= 7:
            return 9.5  # imminent catalyst
        elif days_until <= 14:
            return 8.0
        elif days_until <= 21:
            return 7.0
        elif days_until <= 30:
            return 5.5
        else:
            return 4.0
    except Exception:
        return 5.0


# ─── Options / Put-Call Proxy ─────────────────────────────────────────────────

def compute_options_score(ticker: str) -> float:
    """
    Estimate options sentiment using yfinance options data.
    Looks at put/call open interest ratio.
    """
    try:
        stock = yf.Ticker(ticker)
        dates = stock.options
        if not dates:
            return 5.0

        # Use nearest expiration
        chain = stock.option_chain(dates[0])
        calls_oi = chain.calls["openInterest"].sum()
        puts_oi = chain.puts["openInterest"].sum()

        total = calls_oi + puts_oi
        if total == 0:
            return 5.0

        call_ratio = calls_oi / total  # higher = more bullish
        # Map 0.3-0.8 range to 0-10
        score = (call_ratio - 0.3) / 0.5 * 10
        return round(max(0, min(10, score)), 1)
    except Exception:
        return 5.0


# ─── Master Data Fetch ────────────────────────────────────────────────────────

def analyze_ticker(ticker: str) -> dict:
    """
    Run full analysis pipeline for a single ticker.
    Returns all scores and raw data.
    """
    # Fetch all data
    info = fetch_stock_info(ticker)
    price_data = fetch_price_data(ticker)
    sentiment = fetch_news_sentiment(ticker)
    insider = fetch_insider_data(ticker)
    technical = compute_technical_indicators(price_data)
    catalyst_score = compute_catalyst_score(info)
    options_score = compute_options_score(ticker)

    # Normalize sentiment to 0-10 scale (polarity is -1 to 1)
    sentiment_score = round((sentiment["avg_sentiment"] + 1) / 2 * 10, 1)

    # Insider score
    if insider["net_activity"] == "Buying":
        insider_score = 8.0
    elif insider["net_activity"] == "Selling":
        insider_score = 2.0
    else:
        insider_score = 5.0

    return {
        "ticker": ticker,
        "name": info["name"],
        "sector": info["sector"],
        "industry": info["industry"],
        "price": info["price"],
        "market_cap": info["market_cap"],
        "pe_ratio": info["pe_ratio"],
        "beta": info["beta"],
        "earnings_date": info.get("earnings_date", "N/A"),
        # Scores (0-10)
        "sentiment_score": sentiment_score,
        "catalyst_score": catalyst_score,
        "insider_score": insider_score,
        "options_score": options_score,
        "technical_score": technical["score"],
        # Raw data for detailed views
        "sentiment_data": sentiment,
        "insider_data": insider,
        "technical_data": technical,
        "price_data": price_data,
    }


def generate_market_summary(top_picks: list) -> str:
    """
    Generate a natural language summary of the top picks.
    """
    if not top_picks:
        return "No stocks selected."

    summary = "### 🌟 **Market Revolution Summary**\n\n"
    summary += f"After scanning the universe, we've identified **{len(top_picks)}** standout candidates with explosive potential.\n\n"

    for i, p in enumerate(top_picks[:3]):
        ticker = p["ticker"]
        name = p["name"]
        sector = p["sector"]
        score = p["sentiment_score"]

        adj = "bullish" if score > 7 else "mixed"
        if score > 8.5: adj = "euphoric"

        summary += f"**{i+1}. {ticker} ({name})** - _{sector}_\n"
        summary += f"> Leading the pack with a **{p['sentiment_score']}/10** sentiment score. "
        summary += f"Market chatter is **{adj}**, driven by strong technicals and catalyst alignment.\n\n"

    summary += "**Strategy Insight:** These companies are showing the rare convergence of positive social sentiment, insider conviction, and nearing catalysts that defines a 'Revolution' trade."
    return summary
