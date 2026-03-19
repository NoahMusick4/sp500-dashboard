import sys
import os
sys.path.append(os.path.dirname(__file__))

from fetch_data import fetch_prices, save_raw
from calculate_returns import build_summary, save_processed
from visualize import plot_static, plot_interactive
from datetime import date

if __name__ == "__main__":
    print("\n🚀 Starting S&P 500 Sector Dashboard\n" + "="*40)

    prices = fetch_prices()
    save_raw(prices)

    summary = build_summary(prices)
    save_processed(summary)

    print("\n📊 Sector Performance Summary:")
    print(summary.to_string(index=False))

    ytd_start = date(date.today().year, 1, 1)
    plot_static(summary)
    plot_interactive(summary, prices, ytd_start)

    print("\n✅ Done! Check outputs/ for your charts and dashboard.")
