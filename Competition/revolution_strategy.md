# Revolution Stock Selection Strategy
## Sentiment + Catalyst Convergence Method

**Objective:** Select 3 US stocks with explosive short-term growth potential (3-week horizon) for the asset allocation competition.

---

## 1. Philosophy

"Revolution" stocks are **undervalued companies approaching an inflection point**. Unlike "Evolution" stocks (stable compounders), these are contrarian picks where positive sentiment momentum is building around a near-term catalyst — creating a compressed growth window.

---

## 2. Screening Criteria

| Criterion | Target | Rationale |
|-----------|--------|-----------|
| Market Cap | $1B – $30B | Large enough to be liquid, small enough to move fast |
| P/E or P/S | Below sector median | Undervalued relative to peers |
| Catalyst | Within 1–3 weeks | Earnings, FDA approval, product launch, partnership |
| Sentiment Trend | Rising positive | Social + news buzz accelerating |
| Insider Activity | Net buying | Smart money conviction |

---

## 3. Five-Factor Scoring Model

Each candidate is scored 0–10 on five factors, then weighted:

| # | Factor | Weight | Signal Description |
|---|--------|--------|--------------------|
| 1 | **News Sentiment** | 30% | Average polarity of recent news headlines (TextBlob). Higher = more positive coverage |
| 2 | **Catalyst Proximity** | 25% | Days until next earnings/event. Closer = higher score |
| 3 | **Insider Buying** | 15% | Net insider purchases in last 3 months. More buying = higher score |
| 4 | **Options Flow** | 15% | Put/call ratio and unusual volume. Heavy call buying = higher score |
| 5 | **Technical Setup** | 15% | Price vs. 50/200-day SMA, RSI position, breakout pattern |

**Composite Score** = Σ (Factor Score × Weight)

---

## 4. Data Sources

| Data | Source | Cost |
|------|--------|------|
| Price & Volume | Yahoo Finance (yfinance) | Free |
| News Headlines | FinViz news scraping | Free |
| Insider Trading | FinViz insider table | Free |
| Sentiment Scoring | TextBlob NLP | Free |
| Technical Indicators | Calculated from price data | Free |

---

## 5. Selection Workflow

```
Step 1: Define Universe
  → Input 10–20 candidate tickers (from sector scans, watchlists, or screener results)

Step 2: Fetch Data
  → Pull price history, news headlines, insider transactions for each ticker

Step 3: Score Each Factor
  → Sentiment: average TextBlob polarity of last 20 headlines → normalize 0–10
  → Catalyst: days to next earnings → inverse normalize 0–10
  → Insider: net shares bought → normalize 0–10
  → Technical: SMA crossover + RSI → normalize 0–10

Step 4: Compute Composite Score
  → Apply weights → rank candidates

Step 5: Select Top 3
  → Review top-ranked stocks
  → Verify no overlapping risks (same sector, correlated catalysts)
  → Final selection
```

---

## 6. Scientific Risk Management (Short-Term Focus)

Instead of generic annual volatility, we use short-term metrics tailored for a 3-week competition.

### A. ATR Method (Primary System)
Uses **Average True Range (14-day)** to capture daily price noise.
*   **Stop Loss:** $2.0 \times ATR$ (Allows for normal daily fluctuations)
*   **Take Profit:** $4.0 \times ATR$ (Targets significant trend extension)
*   **Risk/Reward Ratio:** 1:2

### B. Statistical Method ($\sigma_{15}$)
Projects past 60-day volatility into a 15-day (3-week) expected range.
*   $\sigma_{daily}$ = Standard Deviation of daily returns (last 60 days)
*   $\sigma_{15}$ = $\sigma_{daily} \times \sqrt{15}$
*   **Stop Limit:** $-1.0 \times \sigma_{15}$ (Statistical breakdown level)
*   **Profit Target:** $+1.5 \times \sigma_{15}$ (Upper band of expected move)

### C. Portfolio Constraints
- **Diversification:** Max 2 stocks per sector
- **Liquidity:** Avg Volume > 500K shares
- **Correlation:** Portfolio average correlation $\rho < 0.6$

---

## 7. Timeline (3-Week Competition)

| Week | Action |
|------|--------|
| Week 1 | Screen, score, and select 3 revolution stocks |
| Week 2 | Monitor sentiment shifts, adjust if catalyst disappoints |
| Week 3 | Hold or exit based on momentum continuation |

---

*Strategy designed for the Quantamental Investment Competition, February 2026.*
