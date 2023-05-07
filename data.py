from datetime import datetime
import json

from pandas import DataFrame
import yfinance as yf


def read_json(filename: str) -> dict:
    with open(filename, "r") as fhandle:
        d = json.load(fhandle)
    return d


# root keys
_SYMBOL = "symbol"
_PRICE_CURRENCY = "price_currency"
_TRANSACTIONS = "transactions"
_TRANSACTIONS_DATA_TYPE = "data_type"
_TRANSACTIONS_DATA = "data"
# columns in _TRANSACTION values
_DATE = "date"
_AMOUNT = "amount"
_PRICE = "price"
_FX_RATE = "FXrate"


def read_in_transactions(filename: str) -> DataFrame:
    d = read_json(filename)

    symbol, price_currency, transactions = d[_SYMBOL], d[_PRICE_CURRENCY], d[_TRANSACTIONS]
    data_type = transactions[_TRANSACTIONS_DATA_TYPE]

    # TODO: add a function that takes a config object
    # TODO: add try/except
    df = (
        DataFrame(data=transactions[_TRANSACTIONS_DATA])
        .astype({_DATE: "datetime64[ns]"})
        .set_index(_DATE)
        .sort_index()
    )

    match data_type:
        case "basic":
            df = complement_basic_data(symbol, price_currency, df)
        case "complete":
            df = df

    return df


def download(ticker: str, start_date: datetime, end_date: datetime) -> DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date)
    df = (
        df
        .asfreq("D", method="ffill")
        .assign(Mid=lambda x: (x.Open+x.Close)/2)
        .Mid
        .to_frame()
    )
    return df


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
