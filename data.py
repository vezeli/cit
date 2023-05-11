from datetime import datetime
import json

from pandas import DataFrame
from pandas.errors import ParserError
import yfinance as yf

from _config import Config


def read_json(filename: str) -> dict:
    with open(filename, "r") as fhandle:
        d = json.load(fhandle)
    return d


def check_transaction_data_type(transactions: list[dict], c: Config) -> str:
    df = DataFrame(transactions)

    if {c._DATE, c._AMOUNT}.issuperset(df):
        rv = c._BASIC
    elif {c._DATE, c._AMOUNT, c._PRICE, c._FX_RATE}.issuperset(df):
        rv = c._COMPLETE
    else:
        raise ValueError("Unable to import transaction data.")

    return rv


def read_in_transactions(c: Config) -> DataFrame:
    d = read_json(c._DATA_PATH)

    asset = d[c._ASSET]
    currency = d[c._CURRENCY]
    transactions = d[c._TRANSACTIONS]

    transaction_data_type = check_transaction_data_type(transactions, c)

    df = (
        DataFrame(data=transactions)
        .astype({c._DATE: "datetime64[ns]"})
        .set_index(c._DATE)
        .sort_index()
    )

    if transaction_data_type == c._BASIC:
        df = complement_basic_data(d[c._ASSET], d[c._CURRENCY], df, c)
    elif transaction_data_type == c._COMPLETE:
        df = df
    else:
        raise ValueError

    return df


def download(
    ticker: str,
    start_date: datetime,
    end_date: datetime) -> DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date)

    df =  (
        df
        .asfreq("D", method="ffill")
        .assign(Mid=lambda df: (df.Open+df.Close)/2)
        .Mid
        .to_frame()
    )

    return df


def complement_basic_data(
    asset: str,
    currency: str,
    df_a: DataFrame,
    c: Config) -> DataFrame:
    start, end = df_a.index.year.min(), df_a.index.year.max()

    df_b = download(
        ticker=asset,
        start_date=datetime(year=start, month=1, day=1),
        end_date = datetime(year=end, month=12, day=31)
    ).rename(columns={"Mid": c._PRICE})

    df_c = download(
        ticker=f"{currency}=X", # NOTE: Yahoo Finance FX tickers are SEK=X -> USD/SEK
        start_date=datetime(year=start, month=1, day=1),
        end_date = datetime(year=end, month=12, day=31)
    ).rename(columns={"Mid": c._FX_RATE})

    df_r = (
        df_a.merge(
            df_b.merge(df_c, left_index=True, right_index=True),
            left_index=True,
            right_index=True,
            how="left"
        )
    )

    return df_r
