import json

import pandas as pd


def read_json(filename: str) -> dict:
    with open(filename, "r") as fhandle:
        d = json.load(fhandle)
    return d


# root keys
_SYMBOL = "symbol"
_TRANSACTIONS = "transactions"
_TRANSACTIONS_DATA_TYPE = "data_type"
_TRANSACTIONS_DATA = "data"
# columns in _TRANSACTION values
_DATE = "date"


def read_in_transactions(filename: str) -> pd.DataFrame:
    d = read_json(filename)
    symbol = d[_SYMBOL]
    transactions = d[_TRANSACTIONS]
    data_type = transactions[_TRANSACTIONS_DATA_TYPE],

    df = pd.DataFrame(data=transactions[_TRANSACTIONS_DATA]).set_index(_DATE)

    match data_type:
        case "basic":
            pass
        case "complete":
            df = df

    return df


def complement_basic_data(df):
   pass
