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

_DESCRIPTION = "CIT is a Capital Income Tax calculator for cryptocurrencies."

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
        print(format_DF(df, title="YOU'VE BOUGHT & SOLD:", index=True))
    elif args.mode == "bought":
        df_buy: DataFrame = df.query(f"{config._AMOUNT} > 0")
        print(
            format_DF(
                df_buy,
                title="YOU'VE BOUGHT:",
                index=True,
            )
        )
    elif args.mode == "sold":
        df_sell: DataFrame = df.query(f"{config._AMOUNT} < 0")
        print(
            format_DF(
                df_sell,
                title="YOU'VE SOLD:",
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
        df = df[df.index.year <= args.year]
    else:
        args.year = df.index[-1].year
        df = df

    df: DataFrame = df.pipe(calculate_statistics, c=config)

    if args.ccy:
        currency = read_json_with_config(c=config)[config._CURRENCY]
        fx_rate: R = (
            download(
                ticker=f"{currency}USD=X",
                start_date=datetime(year=args.year, month=1, day=1),
                end_date=datetime(year=args.year, month=12, day=31),
            )
            .apply(lambda x: 1/x)
            .tail(1)
            .squeeze()
        )
        column_infix = f" ({currency})"
    else:
        fx_rate = 1.0
        column_infix = ""

    df = (
        df
        .apply(lambda x: fx_rate * x if x.name == "Average buying price" else x)
        .rename(
            columns={
                "Average buying price": f"Average price{column_infix} / coin"
            }
        )
    )

    print(
        format_DF(
            df,
            title="SUMMARY:",
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
        help="available subcommands",
    )

    list_parser = subparsers.add_parser("transactions", help="lists transactions")
    list_parser.add_argument(
        "mode",
        nargs="?",
        const="all",
        default="all",
        choices=["all", "bought", "sold"],
        help="choose transaction",
    )
    list_parser.add_argument(
        "-f", "--file",
        default=config._INPUT_FILE,
        type=str,
        help="select input file",
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
        help="show market price in domestic CCY",
    )
    list_parser.add_argument(
        "-m",
        "--mute",
        action="store_false",
        help="suppress program's warranty",
    )
    list_parser.set_defaults(func=list_transactions)

    summary_parser = subparsers.add_parser("summary", help="shows current position")
    summary_parser.add_argument(
        "-f", "--file",
        default=config._INPUT_FILE,
        type=str,
        help="select input file",
        dest="infile",
    )
    summary_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="select year",
    )
    summary_parser.add_argument(
        "-c",
        "--ccy",
        action="store_true",
        help="show price in domestic CCY",
    )
    summary_parser.add_argument(
        "-m",
        "--mute",
        action="store_false",
        help="suppress program's warranty",
    )
    summary_parser.set_defaults(func=summary)

    args = parser.parse_args()

    print()

    args.func(args)

    print()


    #parser.add_argument("year", type=int, default=datetime.now().year, help="select a financial year")
    #parser.add_argument("-i", "--file", type=str, dest="file", default=config._INPUT_FILE, help="select an input file")
    #parser.add_argument("-s", "--statistics", action="store_true", help="show basic statistics")
    #parser.add_argument("-d", "--details", action="store_true", help="show P&L of transactions instead of tax liability")
    #parser.add_argument("-m", "--mute", action="store_false", help="suppress showing the disclaimer")
    #args = parser.parse_args()

    #config._INPUT_FILE = args.file

    #df = read_in_transactions(config)

    #print()
    #
    #if not args.details:
    #    print(
    #        format_DF(
    #            calculate_skatteverket(
    #                financial_year=args.year,
    #                df=df,
    #                c=config,
    #            ),
    #            title="TAXATION:",
    #        )
    #    )
    #else:
    #    print(
    #        format_DF(
    #            calculate_PNL_per_year(
    #                financial_year=args.year,
    #                df=df,
    #                c=config,
    #            ),
    #            title="DETAILED TRANSACTIONS:",
    #            index=True,
    #        )
    #    )
    #
    #if args.statistics:
    #    print()
    #    print(
    #        format_DF(
    #            calculate_statistics(
    #                financial_year=args.year,
    #                df=df,
    #                c=config,
    #            ),
    #            title="STATISTICS:",
    #        )
    #    )
    #else:
    #    pass

    #print()

