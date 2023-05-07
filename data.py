from datetime import datetime
import json

from pandas import DataFrame
import yfinance as yf


def read_json(filename: str) -> dict:
    with open(filename, "r") as fhandle:
        d = json.load(fhandle)
    return d


# data_types
_BASIC = "basic"
_COMPLETE = "complete"
# root keys
_ASSET = "asset"
_CURRENCY = "currency"
_TRANSACTIONS = "transactions"
# columns in _TRANSACTION values
_DATE = "date"
_AMOUNT = "amount"
_PRICE = "price"
_FX_RATE = "fxrate"


# TODO: add `config` object as input
# TODO: `check_transaction_data_type` should be a object that returns either `_BASIC` or _COMPELTE`
def check_transaction_data_type(transactions: list[dict]) -> str:
    df = DataFrame(transactions)

    if {_DATE, _AMOUNT}.issuperset(df):
        rv = _BASIC
    elif {_DATE, _AMOUNT, _PRICE, _FX_RATE}.issuperset(df):
        rv = _COMPLETE
    else:
        raise ValueError

    return rv


# TODO: add a try/except when reading in the data
# TODO: add a try/except when constructing a DataFrame
def read_in_transactions(filename: str) -> DataFrame:
    d = read_json(filename)

    asset, currency, transactions = d[_ASSET], d[_CURRENCY], d[_TRANSACTIONS]

    transaction_data_type = check_transaction_data_type(transactions)

    df = (
        DataFrame(data=transactions)
        .astype({_DATE: "datetime64[D]"})
        .set_index(_DATE)
        .sort_index()
    )

    if transaction_data_type == _BASIC:
        df = complement_basic_data(d[_ASSET], d[_CURRENCY], df)
    elif transaction_data_type == _COMPLETE:
        df = df
    else:
        raise ValueError

    return df.apply(lambda x: x.round(2) if x.name in [_PRICE, _FX_RATE] else x)


def download(ticker: str, start_date: datetime, end_date: datetime) -> DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date)
    return (
        df
        .asfreq("D", method="ffill")
        .assign(Mid=lambda x: (x.Open+x.Close)/2)
        .Mid
        .to_frame()
    )


def complement_basic_data(asset: str, currency: str, df_a: DataFrame) -> DataFrame:
    start, end = df_a.index.year.min(), df_a.index.year.max()

    df_b = download(
        ticker=asset,
        start_date=datetime(year=start, month=1, day=1),
        end_date = datetime(year=end, month=12, day=31)
    ).rename(columns={"Mid": _PRICE})

    df_c = download(
        ticker=f"{currency}=X", # NOTE: Yahoo Finance FX tickers are SEK=X -> USD/SEK
        start_date=datetime(year=start, month=1, day=1),
        end_date = datetime(year=end, month=12, day=31)
    ).rename(columns={"Mid": _FX_RATE})

    df_r = (
        df_a.merge(
            df_b.merge(df_c, left_index=True, right_index=True),
            left_index=True,
            right_index=True,
            how="left"
        )
    )

    return df_r
