import requests

from bs4 import BeautifulSoup

from datetime import datetime


HEADERS = {

    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    )

}


def _number(value):

    if value is None:
        return None

    value = str(value)

    value = (
        value
        .replace(",", "")
        .replace("$", "")
        .strip()
    )

    try:

        return float(value)

    except ValueError:

        return None


def scrape_stock(symbol):

    """
    Scrape basic stock information.
    """

    symbol = symbol.upper().strip()

    if not symbol:

        raise ValueError(
            "Stock symbol is required."
        )

    url = (
        f"https://finance.yahoo.com/"
        f"quote/{symbol}/"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # --------------------------------
    # Current price
    # --------------------------------

    price_element = soup.find(
        attrs={
            "data-testid": "qsp-price"
        }
    )

    # Fallback selector
    if not price_element:

        price_element = soup.select_one(
            '[data-field="regularMarketPrice"]'
        )

    # --------------------------------
    # Previous close
    # --------------------------------

    previous_element = soup.find(
        attrs={
            "data-testid":
            "PREV_CLOSE-value"
        }
    )

    # --------------------------------
    # Convert values
    # --------------------------------

    price = _number(

        price_element.get_text(
            strip=True
        )

        if price_element

        else None

    )

    previous_close = _number(

        previous_element.get_text(
            strip=True
        )

        if previous_element

        else None

    )

    if price is None:

        raise ValueError(
            "Stock price could not be found. "
            "Yahoo Finance may have changed "
            "its HTML structure or blocked "
            "the request."
        )

    # --------------------------------
    # Change
    # --------------------------------

    change = None

    if previous_close is not None:

        change = (
            price -
            previous_close
        )

    # --------------------------------
    # Percentage change
    # --------------------------------

    change_percent = None

    if (
        previous_close
        not in (None, 0)
        and change is not None
    ):

        change_percent = (
            change /
            previous_close
        ) * 100

    # --------------------------------
    # Additional information
    # --------------------------------

    day_range = None

    volume = None

    market_cap = None

    for row in soup.select("tr"):

        text = row.get_text(
            " ",
            strip=True
        )

        if (
            "Day's Range" in text
            and day_range is None
        ):

            day_range = (
                text
                .split(
                    "Day's Range",
                    1
                )[-1]
                .strip()
            )

        if (
            "Volume" in text
            and volume is None
        ):

            volume = (
                text
                .split(
                    "Volume",
                    1
                )[-1]
                .strip()
            )

        if (
            "Market Cap" in text
            and market_cap is None
        ):

            market_cap = (
                text
                .split(
                    "Market Cap",
                    1
                )[-1]
                .strip()
            )

    # --------------------------------
    # Final result
    # --------------------------------

    return {

        "symbol": symbol,

        "price": (
            round(price, 2)
            if price is not None
            else None
        ),

        "previous_close": (
            round(previous_close, 2)
            if previous_close is not None
            else None
        ),

        "change": (
            round(change, 2)
            if change is not None
            else None
        ),

        "change_percent": (
            round(change_percent, 2)
            if change_percent is not None
            else None
        ),

        "day_range": (
            day_range
            or "N/A"
        ),

        "volume": (
            volume
            or "N/A"
        ),

        "market_cap": (
            market_cap
            or "N/A"
        ),

        "scraped_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }


def fetch_history(
    symbol,
    period="1mo"
):

    """
    Fetch historical daily
    stock prices for charts.
    """

    symbol = symbol.upper().strip()

    url = (
        "https://query1.finance.yahoo.com/"
        "v8/finance/chart/"
        f"{symbol}"
        f"?range={period}"
        "&interval=1d"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=15
    )

    response.raise_for_status()

    payload = response.json()

    result = (
        payload["chart"]
        ["result"][0]
    )

    timestamps = result.get(
        "timestamp",
        []
    )

    closes = (
        result["indicators"]
        ["quote"][0]
        .get("close", [])
    )

    history = []

    for timestamp, close in zip(
        timestamps,
        closes
    ):

        if close is None:
            continue

        date = datetime.fromtimestamp(
            timestamp
        ).strftime("%Y-%m-%d")

        history.append({

            "date": date,

            "close": round(
                float(close),
                2
            )

        })

    return history