import argparse
from numbers import Real as R

from pandas import DataFrame

from _config import Config
from calculation import (
    calculate_PNL_per_year,
    calculate_skatteverket,
    calculate_statistics,
)
from data import read_json_with_config, read_in_transactions
from formatting import format_DF

_PROGRAM_NAME = "cit"

_DESCRIPTION = (
    "CIT is a minimalistic Capital Income Tax calculator for cryptocurrencies."
)

def list_transactions(args):
    global config

    config._INPUT_FILE = args.FILE

    df: DataFrame = read_in_transactions(config).round(
        {config._AMOUNT: 6, config._PRICE: 2, config._FX_RATE: 2}
    )

    if args.ccy:
        df = df.assign(
            DomesticMV=lambda x: x[config._PRICE] * x[config._FX_RATE]
        ).round({"DomesticMV": 2})
    else:
        pass

    if args.year:
        df = df.loc[df.index.year == args.year]
    else:
        pass
    df.index = df.index.date

    if args.mode == "all":
        df = df
        title = "BUY & SELL TRANSACTIONS"
    elif args.mode == "buy":
        df = df.query(f"{config._AMOUNT} > 0")
        title = "BUY TRANSACTIONS"
    elif args.mode == "sell":
        df = df.query(f"{config._AMOUNT} < 0")
        title = "SELL TRANSACTIONS"

    d = read_json_with_config(config)
    asset_currency = d[config._ASSET_CURRENCY]
    domestic_currency = d[config._CURRENCY]
    column_map = {
        config._AMOUNT: config._AMOUNT.capitalize(),
        config._PRICE: f"{config._PRICE.capitalize()} ({asset_currency})",
        config._FX_RATE: config._FX_RATE.capitalize(),
        "DomesticMV": f"{config._PRICE.capitalize()} ({domestic_currency})",
    }

    print(
        format_DF(
            df=df,
            title=title,
            m=column_map,
            index=True,
        )
    )


def summary(args):
    global config

    config._INPUT_FILE = args.FILE

    df: DataFrame = read_in_transactions(config).round(
        {config._AMOUNT: 6, config._PRICE: 2, config._FX_RATE: 2}
    )

    if args.year:
        year = args.year
    else:
        year = df.index[-1].year

    df: DataFrame = calculate_statistics(
        financial_year=year,
        df=df,
        c=config,
        ccy=args.ccy,
    )

    d = read_json_with_config(config)
    if not args.ccy:
        currency = d[config._ASSET_CURRENCY]
    else:
        currency = d[config._CURRENCY]

    column_map = {
        "Average buying price": f"Average buying price ({currency})",
    }

    print(
        format_DF(
            df,
            title=f"TRADE SUMMARY FOR {year}",
            m=column_map,
            index=False,
        )
    )


def report(args):
    global config

    config._INPUT_FILE = args.FILE
    config._DEDUCTIBLE = args.deductible

    df: DataFrame = read_in_transactions(config).round(
        {config._AMOUNT: 6, config._PRICE: 2, config._FX_RATE: 2}
    )

    if args.year:
        year = args.year
    else:
        year = df.index[-1].year

    d = read_json_with_config(config)
    asset_currency = d[config._ASSET_CURRENCY]
    domestic_currency = d[config._CURRENCY]
    if not args.ccy:
        currency = domestic_currency
        fx_ticker = f"{asset_currency}{domestic_currency}"
    else:
        currency = asset_currency
        fx_ticker = f"{asset_currency}{asset_currency}"

    if args.mode == "pnl":
        df = calculate_PNL_per_year(
            financial_year=year,
            df=df,
            c=config,
            ccy=args.ccy,
        )
        title = f"P&L IN {year}"
        column_map = {
            config._AMOUNT: config._AMOUNT.capitalize(),
            config._PRICE: f"{config._PRICE.capitalize()} ({asset_currency})",
            config._FX_RATE: f"{fx_ticker}",
            config._ACQUISITION_PRICE: f"{config._ACQUISITION_PRICE.capitalize()} ({asset_currency})",
            "P&L": f"P&L ({currency})",
        }
        index = True
    elif args.mode == "taxes":
        df = calculate_skatteverket(
            financial_year=year,
            df=df,
            c=config,
            ccy=args.ccy,
        )
        title = f"TAX LIABILITY FOR {year}"
        column_map = {
            "Payed": f"Payed ({currency})",
            "Received": f"Received ({currency})",
            "Taxable": f"Taxable ({currency})",
        }
        index = False

    print(format_DF(df, title=title, m=column_map, index=index))


if __name__ == "__main__":
    config = Config()

    parser = argparse.ArgumentParser(
        prog=_PROGRAM_NAME,
        description=_DESCRIPTION,
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
    )

    list_parser = subparsers.add_parser(
        "transactions",
        aliases=["ls"],
        help="list transactions",
    )
    list_parser.add_argument(
        "mode",
        nargs="?",
        const="all",
        default="all",
        choices=["all", "buy", "sell"],
        help="choose transaction type",
    )
    list_parser.add_argument(
        "-i",
        "--in",
        default=config._INPUT_FILE,
        type=str,
        help=f"select input file from {config._DATA_PATH} dir",
        dest="FILE",
    )
    list_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="filter transactions by year",
    )
    list_parser.add_argument(
        "-c",
        "--ccy",
        action="store_true",
        help="show price in domestic currency",
    )
    list_parser.set_defaults(func=list_transactions)

    summary_parser = subparsers.add_parser(
        "summary",
        aliases=["agg"],
        help="aggregate transactions into a remaining position",
    )
    summary_parser.add_argument(
        "-i",
        "--in",
        default=config._INPUT_FILE,
        type=str,
        help=f"select input file from {config._DATA_PATH} dir",
        dest="FILE",
    )
    summary_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="make summary for the end of the provided year",
    )
    summary_parser.add_argument(
        "-c",
        "--ccy",
        action="store_true",
        help="show price in domestic currency",
    )
    summary_parser.set_defaults(func=summary)

    report_parser = subparsers.add_parser(
        "report",
        aliases=["get"],
        help="generate tax-related report",
    )
    report_parser.add_argument(
        "mode",
        choices=["pnl", "taxes"],
        help="choose report type",
    )
    report_parser.add_argument(
        "-i",
        "--in",
        default=config._INPUT_FILE,
        type=str,
        help=f"select a file from {config._DATA_PATH} dir",
        dest="FILE",
    )
    report_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="select a year from input file",
    )
    report_parser.add_argument(
        "-d",
        default=config._DEDUCTIBLE,
        type=float,
        help=f"set tax-deductible percentage (default: {config._DEDUCTIBLE})",
        dest="deductible",
    )
    report_parser.add_argument(
        "-c",
        "--ccy",
        action="store_false",
        help="show results in asset-priced currency",
    )
    report_parser.set_defaults(func=report)

    args = parser.parse_args()

    if args.subcommand:
        print()

        args.func(args)
    else:
        parser.print_help()

    print()
