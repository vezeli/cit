from datetime import datetime
import json
from pathlib import Path
import textwrap

from pandas import DataFrame, concat
import yfinance as yf

from src.cit.config import Config


def read_json(filename: str) -> dict:
    try:
        with open(filename, "r") as fhandle:
            d = json.load(fhandle)
        return d
    except FileNotFoundError:
        print(f'ImportError: Input file "{filename}" doesn\'t exist')
        raise SystemExit(1)


def check_transaction_data_type(transactions: list[dict], c: Config) -> str:
    df = DataFrame(transactions)

    if {c._DATE, c._AMOUNT}.issuperset(df):
        rv = c._BASIC
    elif {c._DATE, c._AMOUNT, c._PRICE, c._FX_RATE}.issuperset(df):
        rv = c._COMPLETE
    else:
        msg = textwrap.dedent(
            """
            Unknown format of transaction data

            See examples of JSON input files in ./data or reconfigure
            ./_config.py."""
        )
        print(msg)
        raise SystemExit(1)

    return rv


def read_json_with_config(c: Config) -> dict:
    dir_path, input_file = Path(c._DATA_PATH), c._INPUT_FILE
    return read_json(dir_path / input_file)


def _frame_transactions(transactions: dict, c: Config) -> DataFrame:
    return (
        DataFrame(data=transactions)
        .astype({c._DATE: "datetime64[ns]"})
        .set_index(c._DATE)
        .sort_index()
    )


def frame_transactions(d: dict, c: Config) -> DataFrame:
    currency = c._DOMESTIC_CURRENCY

    asset = d[c._ASSET]
    transactions = d[c._TRANSACTIONS]

    df = _frame_transactions(transactions, c)

    data_type = check_transaction_data_type(transactions, c)
    if data_type == c._BASIC:
        df = complement_basic_data(asset, currency, df, c)
    elif data_type == c._COMPLETE:
        pass
    else:
        raise ValueError

    return df


def compute_mid_prices(df: DataFrame) -> DataFrame:
    df = (
        df.asfreq("D", method="ffill")
        .assign(Mid=lambda df: (df.Open + df.Close) / 2)
        .Mid.to_frame()
    )
    return df


def download(ticker: str, start_date: datetime, end_date: datetime) -> DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date, progress=False)
    return compute_mid_prices(df)


def complement_basic_data(
    asset: str, currency: str, df_a: DataFrame, c: Config
) -> DataFrame:
    start, end = df_a.index.year.min(), df_a.index.year.max()

    df_b = download(
        ticker=asset,
        start_date=datetime(year=start, month=1, day=1),
        end_date=datetime(year=end, month=12, day=31),
    ).rename(columns={"Mid": c._PRICE})

    # NOTE: FX tickers in Yahoo Finance (i.e., SEKUSD=X is SEK/USD)
    df_c = (
        download(
            ticker=f"{currency}USD=X",
            start_date=datetime(year=start, month=1, day=1),
            end_date=datetime(year=end, month=12, day=31),
        )
        .apply(lambda x: 1 / x if x.name == "Mid" else x)  # i.e., SEK/USD -> USD/SEK
        .rename(columns={"Mid": c._FX_RATE})
    )

    df_r = df_a.merge(
        df_b.merge(df_c, left_index=True, right_index=True),
        left_index=True,
        right_index=True,
        how="left",
    )

    return df_r


def read_in_transactions(c: Config) -> DataFrame:
    return frame_transactions(read_json_with_config(c), c)


def read_input_files(input_files: list, c: Config) -> DataFrame:
    dfs = []
    for input_file in input_files:
        c._INPUT_FILE = input_file

        df: DataFrame = read_in_transactions(c).round(
            {c._AMOUNT: 6, c._PRICE: 2, c._FX_RATE: 2}
        )
        dfs.append(df)

    df = concat(dfs).sort_index()
    return df


def _transactions_as_records(df: DataFrame, c: Config) -> list[dict]:
    return (
        df.reset_index()
        .loc[:, [c._DATE, c._AMOUNT, c._PRICE, c._FX_RATE]]
        .astype({"date": str})
        .to_dict(orient="records")
    )


def _format_transactions_file(df: DataFrame, c: Config) -> DataFrame:
    return {
        "_comment": "Auto-generated JSON for FX transactions",
        f"{c._ASSET}": "N/A",
        f"{c._ASSET_CURRENCY}": f"{c._DOMESTIC_CURRENCY}",
        f"{c._TRANSACTIONS}": _transactions_as_records(df, c),
    }


def export_json(filename: str, df: DataFrame, c: Config) -> None:
    json_content = _format_transactions_file(df, c)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            json_content,
            f,
            ensure_ascii=False,
            indent=4,
        )
