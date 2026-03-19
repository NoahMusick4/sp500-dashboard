import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import date
from fetch_data import SECTORS

DARK_BG = "#0f0f1a"
CARD_BG = "#1a1a2e"
GREEN   = "#00e676"
RED     = "#ff5252"

def plot_static(summary, output_path="../outputs/charts/sector_performance.png"):
    fig, axes = plt.subplots(1, 3, figsize=(18, 7))
    fig.patch.set_facecolor(DARK_BG)
    periods = ["1M (%)", "3M (%)", "YTD (%)"]
    titles  = ["1 Month Return", "3 Month Return", "Year-to-Date Return"]

    for ax, period, title in zip(axes, periods, titles):
        df_sorted = summary.sort_values(period, ascending=True)
        colors = [GREEN if v >= 0 else RED for v in df_sorted[period]]
        bars = ax.barh(df_sorted["Sector"], df_sorted[period], color=colors, edgecolor="none", height=0.65)

        for bar, val in zip(bars, df_sorted[period]):
            x_pos = val + 0.2 if val >= 0 else val - 0.2
            ha = "left" if val >= 0 else "right"
            ax.text(x_pos, bar.get_y() + bar.get_height() / 2,
                    f"{val:+.1f}%", va="center", ha=ha,
                    color="white", fontsize=8.5, fontweight="bold")

        ax.axvline(0, color="white", linewidth=0.8, alpha=0.4)
        ax.set_title(title, color="white", fontsize=13, fontweight="bold", pad=12)
        ax.set_facecolor(DARK_BG)
        ax.tick_params(colors="white", labelsize=9)
        ax.spines[:].set_visible(False)

    fig.suptitle("S&P 500 Sector Performance Dashboard", color="white", fontsize=16, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
    print(f"💾 Static chart saved to {output_path}")
    plt.show()

def plot_interactive(summary, prices, ytd_start, output_path="../outputs/dashboards/sp500_sector_dashboard.html"):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("YTD Returns by Sector", "1M vs 3M Scatter",
                        "Sector Price Trends (Normalized)", "Performance Heatmap"),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "heatmap"}]],
        vertical_spacing=0.14, horizontal_spacing=0.1,
    )

    ytd_sorted = summary.sort_values("YTD (%)", ascending=True)
    bar_colors = [GREEN if v >= 0 else RED for v in ytd_sorted["YTD (%)"]]
    fig.add_trace(go.Bar(
        x=ytd_sorted["YTD (%)"], y=ytd_sorted["Sector"], orientation="h",
        marker_color=bar_colors,
        text=[f"{v:+.1f}%" for v in ytd_sorted["YTD (%)"]],
        textposition="outside", name="YTD Return",
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=summary["1M (%)"], y=summary["3M (%)"],
        mode="markers+text", text=summary["Sector"],
        textposition="top center",
        marker=dict(size=12, color=summary["YTD (%)"], colorscale="RdYlGn", showscale=True,
                    colorbar=dict(title="YTD %", x=1.02, len=0.45, y=0.78),
                    line=dict(width=1, color="white")),
        name="Sectors",
    ), row=1, col=2)
    fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.3, row=1, col=2)
    fig.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.3, row=1, col=2)

    ytd_prices = prices[prices.index >= pd.Timestamp(ytd_start)]
    normalized = ytd_prices / ytd_prices.iloc[0] * 100
    ticker_to_name = {v: k for k, v in SECTORS.items()}
    top5 = summary.head(5)["Ticker"].tolist()
    bottom2 = summary.tail(2)["Ticker"].tolist()
    color_scale = px.colors.qualitative.Plotly

    for i, ticker in enumerate(top5 + bottom2):
        is_bottom = ticker in bottom2
        fig.add_trace(go.Scatter(
            x=normalized.index, y=normalized[ticker],
            name=ticker_to_name.get(ticker, ticker),
            line=dict(width=2 if not is_bottom else 1.5,
                      color=color_scale[i % len(color_scale)],
                      dash="solid" if not is_bottom else "dot"),
        ), row=2, col=1)

    heat_data = summary[["1M (%)", "3M (%)", "YTD (%)"]].values.T
    fig.add_trace(go.Heatmap(
        z=heat_data, x=summary["Sector"].tolist(), y=["1M", "3M", "YTD"],
        colorscale="RdYlGn",
        text=[[f"{v:+.1f}%" for v in row] for row in heat_data],
        texttemplate="%{text}", showscale=False, name="Heatmap",
    ), row=2, col=2)

    fig.update_layout(
        title=dict(text=f"S&P 500 Sector Dashboard  |  As of {date.today().strftime('%B %d, %Y')}",
                   font=dict(size=20, color="white"), x=0.5),
        paper_bgcolor=DARK_BG, plot_bgcolor=CARD_BG,
        font=dict(color="white", family="monospace"), height=900,
        legend=dict(bgcolor="rgba(255,255,255,0.05)", bordercolor="rgba(255,255,255,0.1)", x=1.05, y=0.35),
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.2)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.2)")
    fig.write_html(output_path)
    print(f"🌐 Interactive dashboard saved to {output_path}")
    fig.show()