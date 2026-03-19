import pandas as pd
from datetime import date
from fetch_data import SECTORS

def period_return(df, start):
    start_ts = pd.Timestamp(start)
    valid = df.index[df.index >= start_ts]
    if len(valid) == 0:
        return pd.Series([None] * len(df.columns), index=df.columns)
    start_price = df.loc[valid[0]]
    end_price = df.iloc[-1]
    return ((end_price - start_price) / start_price * 100).round(2)

def build_summary(prices):
    today = date.today()
    ytd_start = date(today.year, 1, 1)
    three_m = pd.Timestamp.today() - pd.DateOffset(months=3)
    one_m = pd.Timestamp.today() - pd.DateOffset(months=1)
    tickers = list(SECTORS.values())

    r1m = period_return(prices, one_m)
    r3m = period_return(prices, three_m)
    rytd = period_return(prices, ytd_start)

    summary = pd.DataFrame({
        "Sector":  list(SECTORS.keys()),
        "Ticker":  tickers,
        "1M (%)":  [r1m[t]  for t in tickers],
        "3M (%)":  [r3m[t]  for t in tickers],
        "YTD (%)": [rytd[t] for t in tickers],
    }).sort_values("YTD (%)", ascending=False).reset_index(drop=True)

    summary.insert(0, "Rank", range(1, len(summary) + 1))
    return summary

def save_processed(summary, path="../data/processed/sector_returns.csv"):
    summary.to_csv(path, index=False)
    print(f"💾 Processed data saved to {path}")