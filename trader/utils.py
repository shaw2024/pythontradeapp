import os
import csv
from pathlib import Path
from datetime import datetime
import yfinance as yf


def load_series(symbol: str, repo_root: Path):
    """Return (dates, closes) for a symbol.

    Prefers yfinance if no API key is required; otherwise falls back to CSVs in sample_data.
    """
    # Try yfinance (no API key required for basic history)
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="max")
        if not hist.empty:
            dates = [d.strftime("%Y-%m-%d") for d in hist.index]
            closes = [float(x) for x in hist["Close"].tolist()]
            return dates, closes
    except Exception:
        pass

    # Fallback to sample CSV under repo_root/sample_data/{symbol}.csv
    sample = repo_root / "sample_data" / f"{symbol}.csv"
    if sample.exists():
        dates = []
        closes = []
        with open(sample, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                # expect Date and Close
                dates.append(row.get("Date"))
                closes.append(float(row.get("Close", 0)))
        return dates, closes

    # Last resort: empty lists
    return [], []
