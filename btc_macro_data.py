import pandas as pd
import requests
from fredapi import Fred

# ── CONFIGURATION ───────────────────────────────────────────
FRED_API_KEY = "7e8e9330a6e37403fd4127a417c2f562"
START_DATE = "2015-01-01"
END_DATE = "2025-01-01"
# ────────────────────────────────────────────────────────────

fred = Fred(api_key=FRED_API_KEY)

# ── PULL FRED DATA ───────────────────────────────────────────
print("Pulling Fed Funds Rate...")
fed_funds = fred.get_series("FEDFUNDS", start=START_DATE, end=END_DATE)
fed_funds = fed_funds.reset_index()
fed_funds.columns = ["date", "fed_funds_rate"]

print("Pulling CPI...")
cpi = fred.get_series("CPIAUCSL", start=START_DATE, end=END_DATE)
cpi = cpi.reset_index()
cpi.columns = ["date", "cpi"]

print("Pulling M2 Money Supply...")
m2 = fred.get_series("M2SL", start=START_DATE, end=END_DATE)
m2 = m2.reset_index()
m2.columns = ["date", "m2"]

# ── PULL BITCOIN DATA FROM YAHOO FINANCE ────────────────────
print("Pulling Bitcoin price from Yahoo Finance...")
import yfinance as yf

btc = yf.download("BTC-USD", start=START_DATE, end=END_DATE, interval="1mo")
btc = btc[["Close"]].reset_index()
btc.columns = ["date", "btc_price"]
btc["date"] = pd.to_datetime(btc["date"]).dt.to_period("M").dt.to_timestamp()
btc_prices = btc
# ── MERGE EVERYTHING ─────────────────────────────────────────
print("Merging datasets...")

# Normalize all dates to monthly
fed_funds["date"] = pd.to_datetime(fed_funds["date"]).dt.to_period("M").dt.to_timestamp()
cpi["date"] = pd.to_datetime(cpi["date"]).dt.to_period("M").dt.to_timestamp()
m2["date"] = pd.to_datetime(m2["date"]).dt.to_period("M").dt.to_timestamp()
btc_prices["date"] = pd.to_datetime(btc_prices["date"]).dt.to_period("M").dt.to_timestamp()

# Filter to date range
btc_prices = btc_prices[(btc_prices["date"] >= START_DATE) & (btc_prices["date"] <= END_DATE)]

# Merge all on date
df = btc_prices.merge(fed_funds, on="date", how="left")
df = df.merge(cpi, on="date", how="left")
df = df.merge(m2, on="date", how="left")

# ── ADD CALCULATED COLUMNS ───────────────────────────────────
df["btc_pct_change"] = df["btc_price"].pct_change() * 100
df["cpi_yoy"] = df["cpi"].pct_change(12) * 100  # Year-over-year inflation
df["m2_yoy"] = df["m2"].pct_change(12) * 100    # Year-over-year M2 growth

# ── EXPORT TO CSV ────────────────────────────────────────────
df.to_csv("btc_macro_data.csv", index=False)
print("Done! File saved as btc_macro_data.csv")
print(df.tail())