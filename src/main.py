"""
S&P 500 Sector Performance Dashboard
=====================================
Built with: yfinance, pandas, matplotlib, plotly
Run: python sp500_dashboard.py

This script:
1. Pulls real stock data for each S&P 500 sector ETF
2. Calculates 1M, 3M, and YTD returns
3. Shows a ranked bar chart of sector performance
4. Exports an interactive HTML dashboard you can share with anyone
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, date
import warnings
warnings.filterwarnings("ignore")


# ── 1. SECTOR ETF MAP ────────────────────────────────────────────────────────
# These are the standard SPDR sector ETFs that track each S&P 500 sector

SECTORS = {
    "Technology":        "XLK",
    "Healthcare":        "XLV",
    "Financials":        "XLF",
    "Consumer Discret.": "XLY",
    "Consumer Staples":  "XLP",
    "Industrials":       "XLI",
    "Energy":            "XLE",
    "Utilities":         "XLU",
    "Real Estate":       "XLRE",
    "Materials":         "XLB",
    "Communication":     "XLC",
}

# ── 2. DATE SETUP ────────────────────────────────────────────────────────────

today      = date.today()
ytd_start  = date(today.year, 1, 1)          # Jan 1 of this year
three_m    = pd.Timestamp.today() - pd.DateOffset(months=3)
one_m      = pd.Timestamp.today() - pd.DateOffset(months=1)
pull_start = date(today.year - 1, 1, 1)      # Pull extra history for safety


# ── 3. PULL DATA ─────────────────────────────────────────────────────────────

print("📡 Pulling sector data from Yahoo Finance...")

tickers = list(SECTORS.values())
raw = yf.download(tickers, start=pull_start, end=today, auto_adjust=True, progress=False)

# Use adjusted close prices
prices = raw["Close"]

print(f"✅ Got {len(prices)} trading days of data\n")


# ── 4. CALCULATE RETURNS ─────────────────────────────────────────────────────

def period_return(df, start):
    """Calculate % return from a given start date to today."""
    start_ts = pd.Timestamp(start)
    # Find the closest available trading day at or after start
    valid = df.index[df.index >= start_ts]
    if len(valid) == 0:
        return pd.Series([None] * len(df.columns), index=df.columns)
    start_price = df.loc[valid[0]]
    end_price   = df.iloc[-1]
    return ((end_price - start_price) / start_price * 100).round(2)


returns_1m  = period_return(prices, one_m)
returns_3m  = period_return(prices, three_m)
returns_ytd = period_return(prices, ytd_start)

# Build summary DataFrame
summary = pd.DataFrame({
    "Sector":   list(SECTORS.keys()),
    "Ticker":   list(SECTORS.values()),
    "1M (%)":   [returns_1m[t]  for t in tickers],
    "3M (%)":   [returns_3m[t]  for t in tickers],
    "YTD (%)":  [returns_ytd[t] for t in tickers],
}).sort_values("YTD (%)", ascending=False).reset_index(drop=True)

# Add rank
summary.insert(0, "Rank", range(1, len(summary) + 1))

print("📊 Sector Performance Summary (sorted by YTD return):")
print(summary.to_string(index=False))
print()


# ── 5. MATPLOTLIB CHART (Quick View) ─────────────────────────────────────────

fig, axes = plt.subplots(1, 3, figsize=(18, 7))
fig.patch.set_facecolor("#0f0f1a")

periods = ["1M (%)", "3M (%)", "YTD (%)"]
titles  = ["1 Month Return", "3 Month Return", "Year-to-Date Return"]

for ax, period, title in zip(axes, periods, titles):
    df_sorted = summary.sort_values(period, ascending=True)
    colors = ["#00e676" if v >= 0 else "#ff5252" for v in df_sorted[period]]

    bars = ax.barh(df_sorted["Sector"], df_sorted[period], color=colors, edgecolor="none", height=0.65)

    # Add value labels
    for bar, val in zip(bars, df_sorted[period]):
        x_pos = val + 0.2 if val >= 0 else val - 0.2
        ha = "left" if val >= 0 else "right"
        ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.1f}%", va="center", ha=ha,
                color="white", fontsize=8.5, fontweight="bold")

    ax.axvline(0, color="white", linewidth=0.8, alpha=0.4)
    ax.set_title(title, color="white", fontsize=13, fontweight="bold", pad=12)
    ax.set_facecolor("#0f0f1a")
    ax.tick_params(colors="white", labelsize=9)
    ax.spines[:].set_visible(False)
    ax.xaxis.label.set_color("white")

fig.suptitle("S&P 500 Sector Performance Dashboard",
             color="white", fontsize=16, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig("sector_performance.png", dpi=150, bbox_inches="tight",
            facecolor="#0f0f1a")
print("💾 Saved: sector_performance.png")
plt.show()


# ── 6. INTERACTIVE PLOTLY DASHBOARD (Shareable HTML) ─────────────────────────

fig2 = make_subplots(
    rows=2, cols=2,
    subplot_titles=("YTD Returns by Sector", "1M vs 3M Scatter",
                    "Sector Price Trends (Normalized)", "Performance Heatmap"),
    specs=[[{"type": "bar"}, {"type": "scatter"}],
           [{"type": "scatter"}, {"type": "heatmap"}]],
    vertical_spacing=0.14,
    horizontal_spacing=0.1,
)

DARK_BG    = "#0f0f1a"
CARD_BG    = "#1a1a2e"
GREEN      = "#00e676"
RED        = "#ff5252"
ACCENT     = "#7c6af7"

# ── Panel 1: YTD Bar Chart ────────────────────────────────────────────────────
ytd_sorted = summary.sort_values("YTD (%)", ascending=True)
bar_colors = [GREEN if v >= 0 else RED for v in ytd_sorted["YTD (%)"]]

fig2.add_trace(go.Bar(
    x=ytd_sorted["YTD (%)"],
    y=ytd_sorted["Sector"],
    orientation="h",
    marker_color=bar_colors,
    text=[f"{v:+.1f}%" for v in ytd_sorted["YTD (%)"]],
    textposition="outside",
    name="YTD Return",
), row=1, col=1)

# ── Panel 2: 1M vs 3M Scatter ─────────────────────────────────────────────────
fig2.add_trace(go.Scatter(
    x=summary["1M (%)"],
    y=summary["3M (%)"],
    mode="markers+text",
    text=summary["Sector"],
    textposition="top center",
    marker=dict(
        size=12,
        color=summary["YTD (%)"],
        colorscale="RdYlGn",
        showscale=True,
        colorbar=dict(title="YTD %", x=1.02, len=0.45, y=0.78),
        line=dict(width=1, color="white"),
    ),
    name="Sectors",
), row=1, col=2)

# Add quadrant lines
fig2.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3, row=1, col=2)
fig2.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.3, row=1, col=2)

# ── Panel 3: Normalized Price Trends ─────────────────────────────────────────
# Normalize from YTD start so all sectors start at 100
ytd_prices = prices[prices.index >= pd.Timestamp(ytd_start)]
normalized = (ytd_prices / ytd_prices.iloc[0] * 100)

# Plot top 5 and bottom 2 YTD performers to keep it clean
top_sectors    = summary.head(5)["Ticker"].tolist()
bottom_sectors = summary.tail(2)["Ticker"].tolist()
plot_tickers   = top_sectors + bottom_sectors

color_scale = px.colors.qualitative.Plotly

for i, ticker in enumerate(plot_tickers):
    sector_name = {v: k for k, v in SECTORS.items()}[ticker]
    is_bottom   = ticker in bottom_sectors
    fig2.add_trace(go.Scatter(
        x=normalized.index,
        y=normalized[ticker],
        name=sector_name,
        line=dict(
            width=2 if not is_bottom else 1.5,
            color=color_scale[i % len(color_scale)],
            dash="solid" if not is_bottom else "dot",
        ),
    ), row=2, col=1)

# ── Panel 4: Heatmap ──────────────────────────────────────────────────────────
heat_data   = summary[["1M (%)", "3M (%)", "YTD (%)"]].values.T
heat_labels = summary["Sector"].tolist()

fig2.add_trace(go.Heatmap(
    z=heat_data,
    x=heat_labels,
    y=["1M", "3M", "YTD"],
    colorscale="RdYlGn",
    text=[[f"{v:+.1f}%" for v in row] for row in heat_data],
    texttemplate="%{text}",
    showscale=False,
    name="Heatmap",
), row=2, col=2)

# ── Layout ────────────────────────────────────────────────────────────────────
fig2.update_layout(
    title=dict(
        text=f"S&P 500 Sector Dashboard  |  As of {today.strftime('%B %d, %Y')}",
        font=dict(size=20, color="white"),
        x=0.5,
    ),
    paper_bgcolor=DARK_BG,
    plot_bgcolor=CARD_BG,
    font=dict(color="white", family="monospace"),
    height=900,
    showlegend=True,
    legend=dict(
        bgcolor="rgba(255,255,255,0.05)",
        bordercolor="rgba(255,255,255,0.1)",
        x=1.05, y=0.35,
    ),
)

# Style all subplots
fig2.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.2)")
fig2.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.2)")

# Save interactive HTML
output_file = "sp500_sector_dashboard.html"
fig2.write_html(output_file)
print(f"🌐 Saved interactive dashboard: {output_file}")
print("   → Open this file in any browser and share it with anyone!")

fig2.show()


# ── 7. EXPORT CLEAN CSV ───────────────────────────────────────────────────────

summary.to_csv("sector_returns.csv", index=False)
print("📄 Saved: sector_returns.csv")

print("\n✅ Done! Files created:")
print("   • sector_performance.png   — static chart (post to LinkedIn)")
print("   • sp500_sector_dashboard.html — interactive dashboard (share with clients)")
print("   • sector_returns.csv       — raw data")
