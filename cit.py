import argparse
from datetime import datetime
from numbers import Real as R

from _config import Config
from calculation import (
    calculate_acquisition_prices,
    calculate_PNL_per_year,
    calculate_skatteverket,
    calculate_statistics,
)
from data import read_in_transactions
from formatting import df_select_year, format_DF

_PROGRAM_NAME = "cit"

_DESCRIPTION = "CIT is a Capital Income Tax calculator for cryptocurrencies."

_DISCLAIMER = (
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
    global _DISCLAIMER, config
    
    config._INPUT_FILE = args.infile

    df = (
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

    if args.ccy:
        df = (
            df
            .assign(price=lambda x: x[config._AMOUNT] * x[config._FX_RATE])
            .round({"price": 2})
        )
    else:
        pass

    if args.mode == "all":
        print(format_DF(df, title="YOU'VE BOUGHT & SOLD:"))
    elif args.mode == "bought":
        df_buy: DataFrame = df.query(f"{config._AMOUNT} > 0")
        print(
            format_DF(
                df_buy,
                title="YOU'VE BOUGHT:",
            )
        )
    elif args.mode == "sold":
        df_sell: DataFrame = df.query(f"{config._AMOUNT} < 0")
        print(
            format_DF(
                df_sell,
                title="YOU'VE SOLD:",
            )
        )

    if args.mute:
        print(_DISCLAIMER)
    else:
        pass


if __name__ == "__main__":

    config = Config()

    parser = argparse.ArgumentParser(
        prog=_PROGRAM_NAME,
        description=_DESCRIPTION,
        epilog=_DISCLAIMER,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(
        title="subcommands",
        dest="subcommand",
        help="available subcommands",
    )

    list_parser = subparsers.add_parser("list", help="lists transactions")
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
        help="select year",
    )
    list_parser.add_argument(
        "-c",
        "--ccy",
        action="store_true",
        help="show price in domestic CCY",
    )
    list_parser.add_argument(
        "-m",
        "--mute",
        action="store_false",
        help="suppress program's warranty",
    )
    list_parser.set_defaults(func=list_transactions)

    args = parser.parse_args()

    print()

    args.func(args)


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

