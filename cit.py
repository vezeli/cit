import argparse
from datetime import datetime
from numbers import Real as R

from pandas import DataFrame

from _config import Config
from calculation import (
    calculate_acquisition_prices,
    calculate_PNL_per_year,
    calculate_skatteverket,
    calculate_statistics,
)
from data import read_json_with_config, read_in_transactions
from formatting import format_DF

_PROGRAM_NAME = "cit"

_DESCRIPTION = "CIT is a minimalistic Capital Income Tax calculator for cryptocurrencies."

_WARRANTY = (
"""
+--------------------------------------------------+
| NOTE:                                            |
| The program is not a substitute for professional |
| accounting advice. You should always seek the    |
| guidance of a qualified accountant or tax        |
| professional for accurate and comprehensive tax  |
| advice.                                          |
+--------------------------------------------------+"""
)

def list_transactions(args):
    global _WARRANTY, config
    
    config._INPUT_FILE = args.infile

    df: DataFrame = (
        read_in_transactions(config)
        .round(
            {
                config._AMOUNT: 6,
                config._PRICE: 2,
                config._FX_RATE: 2
            }
        )
    )

    if args.ccy:
        df = (
            df
            .assign(DomesticMV=lambda x: x[config._PRICE] * x[config._FX_RATE])
            .round({"DomesticMV": 2})
        )
    else:
        pass

    if args.year:
        df = df.loc[df.index.year == args.year]
    else:
        pass
    df.index = df.index.date

    if args.mode == "all":
        df = df
        title = "ALL TRANSACTIONS"
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

    if args.mute:
        print(_WARRANTY)
    else:
        pass


def summary(args):
    global _WARRANTY, config

    config._INPUT_FILE = args.infile

    df: DataFrame = (
        read_in_transactions(config)
        .round(
            {
                config._AMOUNT: 6,
                config._PRICE: 2,
                config._FX_RATE: 2
            }
        )
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
            title="AGGREGATED TRADE STATISTICS",
            m=column_map,
            index=False,
        )
    )

    if args.mute:
        print(_WARRANTY)
    else:
        pass


def calculate(args):
    global _WARRANTY, config

    config._INPUT_FILE = args.infile
    config._DEDUCTIBLE = args.deductible

    df: DataFrame = (
        read_in_transactions(config)
        .round(
            {
                config._AMOUNT: 6,
                config._PRICE: 2,
                config._FX_RATE: 2
            }
        )
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

    if args.mute:
        print(_WARRANTY)
    else:
        pass


if __name__ == "__main__":

    config = Config()

    parser = argparse.ArgumentParser(
        prog=_PROGRAM_NAME,
        description=_DESCRIPTION,
        epilog=_WARRANTY,
        formatter_class=argparse.RawDescriptionHelpFormatter
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
        "-f", "--file",
        default=config._INPUT_FILE,
        type=str,
        help="select a file for processing",
        dest="infile",
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
    list_parser.add_argument(
        "-m",
        "--mute",
        action="store_false",
        help="suppress warranty message",
    )
    list_parser.set_defaults(func=list_transactions)

    summary_parser = subparsers.add_parser(
        "summary",
        aliases=["agg"],
        help="aggregate transactions into current holding",
    )
    summary_parser.add_argument(
        "-f", "--file",
        default=config._INPUT_FILE,
        type=str,
        help="select a file for processing",
        dest="infile",
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
    summary_parser.add_argument(
        "-m",
        "--mute",
        action="store_false",
        help="suppress warranty message",
    )
    summary_parser.set_defaults(func=summary)

    calculate_parser = subparsers.add_parser(
        "calculate",
        aliases=["get"],
        help="make tax-related calculations",
    )
    calculate_parser.add_argument(
        "mode",
        choices=["pnl", "taxes"],
        help="choose calculation",
    )
    calculate_parser.add_argument(
        "-f",
        "--file",
        default=config._INPUT_FILE,
        type=str,
        help="select a file for processing",
        dest="infile",
    )
    calculate_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="calculate tax liability for the provided year",
    )
    calculate_parser.add_argument(
        "-c",
        "--ccy",
        action="store_false",
        help="show price in the asset-priced currency",
    )
    calculate_parser.add_argument(
        "-d",
        "--deductible",
        default=config._DEDUCTIBLE,
        type=float,
        help="select a percentage of deductible amount of loss",
    )
    calculate_parser.add_argument(
        "-m",
        "--mute",
        action="store_false",
        help="suppress warranty message",
    )
    calculate_parser.set_defaults(func=calculate)

    args = parser.parse_args()

    print()

    args.func(args)

    print()
