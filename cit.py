import argparse
from numbers import Real as R

from pandas import DataFrame

from src.cit.accounting import (
    calculate_forex_transactions,
    calculate_PNL_per_year,
    calculate_skatteverket,
    calculate_statistics,
)
from src.cit.config import Config
from src.cit.formatting import format_DF
from src.cit.io import export_json, read_json_with_config, read_input_files

_PROGRAM_NAME = "cit"

_DESCRIPTION = (
    "CIT is a minimalistic Capital Income Tax calculator for cryptocurrencies."
)


def list_transactions(args):
    global config

    df = read_input_files(args.FILES, config)

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
    domestic_currency = config._DOMESTIC_CURRENCY
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


def forex_transactions(args):
    global config

    df = read_input_files(args.FILES, config)

    df = calculate_forex_transactions(df, config)

    if args.out:
        filename = args.out
        export_json(filename, df, config)

    print(df)
    


def calculate(args):
    global config

    config._DEDUCTIBLE = args.deductible

    df = read_input_files(args.FILES, config)

    if args.year:
        year = args.year
    else:
        year = df.index[-1].year

    d = read_json_with_config(config)
    asset_currency = d[config._ASSET_CURRENCY]
    domestic_currency = config._DOMESTIC_CURRENCY
    if not args.ccy:
        currency = domestic_currency
        fx_ticker = f"{asset_currency}{domestic_currency}"
    else:
        currency = asset_currency
        fx_ticker = f"{asset_currency}{asset_currency}"

    if args.mode == "position-summary":
        df: DataFrame = calculate_statistics(
            financial_year=year,
            df=df,
            c=config,
            ccy=args.ccy,
        )
        title = f"POSITION SUMMARY FOR {year}"
        column_map = {
            "Average buying price": f"Average buying price ({currency})",
        }
        index = False
    elif args.mode == "profit-and-loss":
        df: DataFrame = calculate_PNL_per_year(
            financial_year=year,
            df=df,
            c=config,
            ccy=args.ccy,
        )
        title = f"PROFIT AND LOSS IN {year}"
        column_map = {
            config._AMOUNT: config._AMOUNT.capitalize(),
            config._PRICE: f"{config._PRICE.capitalize()} ({asset_currency})",
            config._FX_RATE: f"{fx_ticker}",
            config._ACQUISITION_PRICE: f"{config._ACQUISITION_PRICE.capitalize()} ({asset_currency})",
            "P&L": f"P&L ({currency})",
        }
        index = True
    elif args.mode == "tax-liability":
        df: DataFrame = calculate_skatteverket(
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
        nargs="*",
        default=[config._INPUT_FILE],
        type=str,
        help=f"select input files from {config._DATA_PATH} dir",
        dest="FILES",
    )
    list_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="filter transactions by year",
    )
    list_parser.add_argument(
        "-d",
        "--domestic-ccy",
        action="store_true",
        help="convert to domestic currency",
        dest="ccy",
    )
    list_parser.set_defaults(func=list_transactions)

    forex_parser = subparsers.add_parser(
        "forex-transactions",
        help="construct forex transactions",
    )
    forex_parser.add_argument(
        "-i",
        "--in",
        nargs="*",
        default=[config._INPUT_FILE],
        type=str,
        help=f"select input files from {config._DATA_PATH} dir",
        dest="FILES",
    )
    forex_parser.add_argument(
        "-o",
        "--out",
        nargs="?",
        default=config._OUTPUT_FILE,
        type=str,
        help=f"write data to a JSON file (default: {config._OUTPUT_FILE})",
    )
    forex_parser.set_defaults(func=forex_transactions)

    calculate_parser = subparsers.add_parser(
        "calculate",
        aliases=["get"],
        help="process transaction data",
    )
    calculate_parser.add_argument(
        "mode",
        choices=["position-summary", "profit-and-loss", "tax-liability"],
        help="choose report type",
    )
    calculate_parser.add_argument(
        "-i",
        "--in",
        nargs="*",
        default=[config._INPUT_FILE],
        type=str,
        help=f"select a file from {config._DATA_PATH} dir",
        dest="FILES",
    )
    calculate_parser.add_argument(
        "-y",
        "--year",
        default=None,
        type=int,
        help="select a year from input file",
    )
    calculate_parser.add_argument(
        "-t",
        "--tax-deductible",
        default=config._DEDUCTIBLE,
        type=float,
        help=f"set tax-deductible percentage (default: {config._DEDUCTIBLE})",
        dest="deductible",
    )
    calculate_parser.add_argument(
        "-d",
        "--domestic-ccy",
        action="store_false",
        help="convert to domestic currency",
        dest="ccy",
    )
    calculate_parser.set_defaults(func=calculate)

    args = parser.parse_args()

    if args.subcommand:
        print()

        args.func(args)
    else:
        parser.print_help()

    print()
