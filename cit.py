import argparse
from numbers import Real as R

from pandas import DataFrame

from src.cit.calculation import (
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

    d = read_json_with_config(config)
    asset = d[config._ASSET]
    asset_currency = d[config._ASSET_CURRENCY]
    domestic_currency = config._DOMESTIC_CURRENCY
    column_map = {
        config._AMOUNT: config._AMOUNT.capitalize(),
        config._PRICE: f"{config._PRICE.capitalize()} ({asset_currency})",
        config._FX_RATE: config._FX_RATE.capitalize(),
        "DomesticMV": f"{config._PRICE.capitalize()} ({domestic_currency})",
    }

    if args.mode == "all":
        df = df
        title = f"{asset.upper()} TRANSACTIONS"
    elif args.mode == "buy":
        df = df.query(f"{config._AMOUNT} > 0")
        title = f"{asset.upper()} BUY TRANSACTIONS"
    elif args.mode == "sell":
        df = df.query(f"{config._AMOUNT} < 0")
        title = f"{asset.upper()} SELL TRANSACTIONS"

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

    d = read_json_with_config(config)
    asset_currency = d[config._ASSET_CURRENCY]
    domestic_currency = config._DOMESTIC_CURRENCY
    title = f"{asset_currency} TRANSACTIONS"
    column_map = {
        config._AMOUNT: config._AMOUNT.capitalize(),
        config._PRICE: f"{config._PRICE.capitalize()} ({domestic_currency})",
        config._FX_RATE: f"{config._FX_RATE.capitalize()} ({domestic_currency}{domestic_currency})",
    }

    df.index = df.index.date
    print(
        format_DF(
            df=df,
            title=title,
            m=column_map,
            index=True,
        )
    )


def calculate(args):
    global config

    config._DEDUCTIBLE = args.td

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

    if args.mode == "summary":
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
            config._FX_RATE: f"{config._FX_RATE.capitalize()} ({fx_ticker})",
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
        help="show transactions",
    )
    list_parser.add_argument(
        "mode",
        nargs="?",
        const="all",
        default="all",
        choices=["all", "buy", "sell"],
        help="Which transactions do you want to show?",
    )
    list_parser.add_argument(
        "--in",
        nargs="*",
        default=[config._INPUT_FILE],
        type=str,
        help=f"specify the input files for reading (relative to {config._DATA_PATH} directory)",
        dest="FILES",
    )
    list_parser.add_argument(
        "--year",
        default=None,
        type=int,
        help="show transaction from the specified year",
    )
    list_parser.add_argument(
        "--domestic-ccy",
        action="store_true",
        help="add a column with market prices in the domestic currency",
        dest="ccy",
    )
    list_parser.set_defaults(func=list_transactions)

    forex_parser = subparsers.add_parser(
        "forex-transactions",
        help="construct FX transactions to/from asset-denominated currency",
    )
    forex_parser.add_argument(
        "--in",
        nargs="*",
        default=[config._INPUT_FILE],
        type=str,
        help=f"specify the input files for reading (relative to {config._DATA_PATH} directory)",
        dest="FILES",
    )
    forex_parser.add_argument(
        "--out",
        type=str,
        help=f"write the transactions data to the specified file",
    )
    forex_parser.set_defaults(func=forex_transactions)

    calculate_parser = subparsers.add_parser(
        "calculate",
        help="portfolio calculations",
    )
    calculate_parser.add_argument(
        "mode",
        choices=["summary", "profit-and-loss", "tax-liability"],
        help="choose report type",
    )
    calculate_parser.add_argument(
        "--in",
        nargs="*",
        default=[config._INPUT_FILE],
        type=str,
        help=f"specify the input files for reading (relative to {config._DATA_PATH} directory)",
        dest="FILES",
    )
    calculate_parser.add_argument(
        "--year",
        default=None,
        type=int,
        help="show the results for the specified year",
    )
    calculate_parser.add_argument(
        "--tax-deductible",
        default=config._DEDUCTIBLE,
        type=float,
        help=f"set the tax-deductible percentage for the calculation (default: {config._DEDUCTIBLE})",
        dest="td",
    )
    calculate_parser.add_argument(
        "--domestic-ccy",
        action="store_false",
        help="convert to domestic currency",
        dest="ccy",
    )
    calculate_parser.set_defaults(func=calculate)

    args = parser.parse_args()

    if args.subcommand:
        args.func(args)
    else:
        parser.print_help()
