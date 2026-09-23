from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:

    SECRET_KEY = "marketpulse-development-key"

    DATA_DIR = BASE_DIR / "data"

    DEFAULT_SYMBOLS = [
        "AAPL",
        "MSFT",
        "GOOGL",
        "AMZN",
        "NVDA",
        "TSLA",
        "META",
        "NFLX"
    ]