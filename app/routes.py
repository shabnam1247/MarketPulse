from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file
)

from scraper.stock_scraper import (
    scrape_stock,
    fetch_history
)

from utils.data_utils import (
    watchlist_dataframe,
    save_snapshot,
    build_analytics,
    dataframe_to_excel
)

from config import Config

import io


main = Blueprint(
    "main",
    __name__
)


DEFAULT_SYMBOLS = (
    Config.DEFAULT_SYMBOLS
)


# =====================================
# DASHBOARD
# =====================================

@main.route("/")
def dashboard():

    stocks = watchlist_dataframe(
        DEFAULT_SYMBOLS
    )

    analytics = build_analytics(
        stocks
    )

    gainers = (

        stocks[
            stocks[
                "change_percent"
            ] > 0
        ]

        .sort_values(
            "change_percent",
            ascending=False
        )

        .head(5)

        .to_dict(
            "records"
        )

    )

    losers = (

        stocks[
            stocks[
                "change_percent"
            ] < 0
        ]

        .sort_values(
            "change_percent"
        )

        .head(5)

        .to_dict(
            "records"
        )

    )

    return render_template(

        "dashboard.html",

        stocks=
            stocks.to_dict(
                "records"
            ),

        gainers=gainers,

        losers=losers,

        analytics=analytics

    )


# =====================================
# MARKET WATCH
# =====================================

@main.route("/stocks")
def stocks_page():

    symbol = request.args.get(
        "symbol",
        ""
    ).strip().upper()

    if symbol:

        try:

            result = scrape_stock(
                symbol
            )

            stocks = [result]

        except Exception as exc:

            return render_template(

                "stocks.html",

                stocks=[],

                error=(
                    f"Could not load "
                    f"{symbol}: {exc}"
                ),

                search=symbol

            )

    else:

        stocks = (
            watchlist_dataframe(
                DEFAULT_SYMBOLS
            )
            .to_dict("records")
        )

    return render_template(

        "stocks.html",

        stocks=stocks,

        search=symbol

    )


# =====================================
# STOCK DETAILS
# =====================================

@main.route(
    "/stock/<symbol>"
)
def stock_detail(symbol):

    symbol = symbol.upper()

    try:

        stock = scrape_stock(
            symbol
        )

        history = fetch_history(
            symbol,
            period="1mo"
        )

    except Exception as exc:

        return render_template(

            "stock_detail.html",

            stock={
                "symbol": symbol
            },

            history=[],

            error=str(exc)

        )

    return render_template(

        "stock_detail.html",

        stock=stock,

        history=history,

        error=None

    )


# =====================================
# ANALYTICS
# =====================================

@main.route("/analytics")
def analytics():

    stocks = watchlist_dataframe(
        DEFAULT_SYMBOLS
    )

    stats = build_analytics(
        stocks
    )

    chart_labels = (
        stocks["symbol"]
        .tolist()
    )

    chart_values = [

        round(
            float(value),
            2
        )

        for value in
        stocks[
            "change_percent"
        ].fillna(0)

    ]

    return render_template(

        "analytics.html",

        stats=stats,

        chart_labels=
            chart_labels,

        chart_values=
            chart_values,

        stocks=
            stocks.to_dict(
                "records"
            )

    )


# =====================================
# API
# =====================================

@main.route(
    "/api/stock/<symbol>"
)
def stock_api(symbol):

    try:

        result = scrape_stock(
            symbol.upper()
        )

        save_snapshot(
            result
        )

        return jsonify(
            result
        )

    except Exception as exc:

        return jsonify({

            "error": str(exc)

        }), 500


@main.route(
    "/api/history/<symbol>"
)
def history_api(symbol):

    try:

        return jsonify(

            fetch_history(
                symbol.upper(),
                period="3mo"
            )

        )

    except Exception as exc:

        return jsonify({

            "error": str(exc)

        }), 500


# =====================================
# CSV EXPORT
# =====================================

@main.route(
    "/export/csv"
)
def export_csv():

    stocks = (
        watchlist_dataframe(
            DEFAULT_SYMBOLS
        )
    )

    csv_data = stocks.to_csv(
        index=False
    )

    return (

        csv_data,

        200,

        {

            "Content-Type":
                "text/csv",

            "Content-Disposition":
                "attachment; "
                "filename="
                "marketpulse_stocks.csv"

        }

    )


# =====================================
# EXCEL EXPORT
# =====================================

@main.route(
    "/export/excel"
)
def export_excel():

    stocks = (
        watchlist_dataframe(
            DEFAULT_SYMBOLS
        )
    )

    output = io.BytesIO()

    dataframe_to_excel(
        stocks,
        output
    )

    output.seek(0)

    return send_file(

        output,

        as_attachment=True,

        download_name=
            "marketpulse_stocks.xlsx",

        mimetype=
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )


# =====================================
# 404
# =====================================

@main.errorhandler(404)
def page_not_found(error):

    return (
        render_template(
            "404.html"
        ),
        404
    )