import yfinance as yf
import pandas as pd
from datetime import date

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

def fetch_prices(start_date=None):
    if start_date is None:
        start_date = date(date.today().year - 1, 1, 1)
    tickers = list(SECTORS.values())
    print("📡 Pulling sector data from Yahoo Finance...")
    raw = yf.download(tickers, start=start_date, end=date.today(), auto_adjust=True, progress=False)
    prices = raw["Close"]
    print(f"✅ Got {len(prices)} trading days of data")
    return prices

def save_raw(prices, path="../data/raw/prices_raw.csv"):
    prices.to_csv(path)
    print(f"💾 Raw data saved to {path}")