from pathlib import Path

from datetime import datetime

import pandas as pd

from scraper.stock_scraper import (
    scrape_stock
)

from config import Config


def watchlist_dataframe(symbols):

    rows = []

    for symbol in symbols:

        try:

            rows.append(
                scrape_stock(symbol)
            )

        except Exception as exc:

            rows.append({

                "symbol": symbol,

                "price": None,

                "previous_close": None,

                "change": None,

                "change_percent": None,

                "day_range":
                    "Unavailable",

                "volume":
                    "Unavailable",

                "market_cap":
                    "Unavailable",

                "scraped_at":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "error": str(exc)

            })

    return pd.DataFrame(rows)


def save_snapshot(row):

    data_dir = Path(
        Config.DATA_DIR
    )

    data_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        data_dir /
        "stock_snapshots.csv"
    )

    df = pd.DataFrame([row])

    if file_path.exists():

        df.to_csv(

            file_path,

            mode="a",

            header=False,

            index=False

        )

    else:

        df.to_csv(

            file_path,

            index=False

        )


def build_analytics(df):

    valid = df.dropna(
        subset=[
            "change_percent"
        ]
    ).copy()

    if valid.empty:

        return {

            "average_change": 0,

            "best_stock": "N/A",

            "worst_stock": "N/A",

            "gainers": 0,

            "losers": 0

        }

    best = valid.loc[
        valid[
            "change_percent"
        ].idxmax()
    ]

    worst = valid.loc[
        valid[
            "change_percent"
        ].idxmin()
    ]

    return {

        "average_change":
            round(
                float(
                    valid[
                        "change_percent"
                    ].mean()
                ),
                2
            ),

        "best_stock":
            best["symbol"],

        "worst_stock":
            worst["symbol"],

        "gainers":
            int(
                (
                    valid[
                        "change_percent"
                    ] > 0
                ).sum()
            ),

        "losers":
            int(
                (
                    valid[
                        "change_percent"
                    ] < 0
                ).sum()
            )

    }


def dataframe_to_excel(
    df,
    output
):

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(

            writer,

            index=False,

            sheet_name="Market Watch"

        )