import argparse
from datetime import datetime
from numbers import Real as R

from pandas import DataFrame
from yfinance import download

from _config import Config
from calculation import (
    calculate_acquisition_prices,
    calculate_PNL_per_year,
    calculate_skatteverket,
    calculate_statistics,
)
from data import download, read_json_with_config, read_in_transactions
from formatting import df_select_year, format_DF

_PROGRAM_NAME = "cit"

_DESCRIPTION = "CIT is a minimalistic Capital Income Tax calculator for cryptocurrencies."

_WARRANTY = (
"""
+--------------------------------------------------+
|                   WARRANTY                       |
+--------------------------------------------------+
| This program is provided "as is" without any     |
| warranty, expressed or implied, including but    |
| not limited to the implied warranties of         |
| merchantability and fitness for a particular     |
| purpose. The user assumes all risks associated   |
| with the quality and performance of the program. |
| If the program is defective, the user assumes    |
| the cost of all necessary servicing, repair or   |
| correction.                                      |
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

    if args.year:
        df = df.pipe(df_select_year, financial_year=args.year)
    else:
        df = df
    df.index = df.index.date

    if args.ccy:
        df = (
            df
            .assign(price=lambda x: x[config._PRICE] * x[config._FX_RATE])
            .round({"price": 2})
        )
    else:
        pass

    if args.mode == "all":
        print(format_DF(df, title="ALL TRANSACTIONS", index=True))
    elif args.mode == "buy":
        df_buy: DataFrame = df.query(f"{config._AMOUNT} > 0")
        print(
            format_DF(
                df_buy,
                title="BUY TRANSACTIONS",
                index=True,
            )
        )
    elif args.mode == "sell":
        df_sell: DataFrame = df.query(f"{config._AMOUNT} < 0")
        print(
            format_DF(
                df_sell,
                title="SELL TRANSACTIONS",
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
        df = df[df.index.year <= year]
    else:
        year = df.index[-1].year
        df = df

    df: DataFrame = df.pipe(calculate_statistics, c=config)

    df = (
        df
        .rename(
            columns={
                "Average buying price": f"Average price/coin"
            }
        )
    )

    print(
        format_DF(
            df,
            title="SUMMARY",
        )
    )

    if args.mute:
        print(_WARRANTY)
    else:
        pass


def calculate(args):
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

    if args.ccy:
        currency = read_json_with_config(c=config)[config._CURRENCY]
        currency_infix = f"({currency})"
    else:
        currency_infix = ""

    if args.mode == "pnl":
        print(
            format_DF(
                calculate_PNL_per_year(
                    financial_year=year,
                    df=df,
                    c=config,
                    transform_ccy=args.ccy,
                ),
                title=f"PROFIT AND LOSS {currency_infix}",
                index=True,
            )
        )
    elif args.mode == "taxes":
        print(
            format_DF(
                calculate_skatteverket(
                    financial_year=year,
                    df=df,
                    c=config,
                    transform_ccy=args.ccy,
                ),
                title=f"TAX LIABILITY {currency_infix}",
            )
        )

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
        help="lists transactions",
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
        help="calculate market price in domestic currency",
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
        help="shows current position",
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
        help="create summary for the provided year",
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
        help="makes tax-related calculations",
    )
    calculate_parser.add_argument(
        "mode",
        choices=["pnl", "taxes"],
        help="choose calculation",
    )
    calculate_parser.add_argument(
        "-f", "--file",
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
