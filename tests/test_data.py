from datetime import datetime
from pathlib import Path
import sys

from pandas import DataFrame, Timestamp
from pandas.testing import assert_frame_equal
import pytest

root_path = Path(__file__).resolve().parent.parent
# Add the root directory to the Python module search path
sys.path.insert(0, str(root_path))

from _config import Config
from data import (
    check_transaction_data_type,
    complement_basic_data,
    ffill_mid,
    read_in_transactions,
    read_json_with_config,
)


@pytest.fixture
def configuration():
    config = Config()
    return config


def test_read_json_with_config(configuration):
    c = configuration
    c._INPUT_FILE = "test-1.json"

    d = read_json_with_config(c)
    asset = d[c._ASSET]
    asset_currency = d[c._ASSET_CURRENCY]
    currency = d[c._CURRENCY]
    transactions = d[c._TRANSACTIONS]

    ASSET = "BTC-SEK"
    ASSET_CURRENCY = "SEK"
    CURRENCY = "SEK"
    TRANSACTIONS = [
        {
            "date": "2021-10-12",
            "amount": 0.5,
            "market price": 40000.0000,
            "exchange rate": 1,
        },
        {
            "date": "2021-11-12",
            "amount": 0.2,
            "market price": 50000.0000,
            "exchange rate": 1,
        },
        {
            "date": "2022-11-16",
            "amount": -0.4,
            "market price": 100000.0000,
            "exchange rate": 1,
        },
    ]

    assert (asset, asset_currency, currency, transactions) == (
        ASSET,
        ASSET_CURRENCY,
        CURRENCY,
        TRANSACTIONS,
    )


def test_read_data_with_config_system_exit(configuration):
    c = configuration
    c._INPUT_FILE = "file-that-does-not-exist.json"

    with pytest.raises(SystemExit) as e:
        read_json_with_config(c)

    assert e.value.code == 1


@pytest.mark.parametrize(
    "filename, mode",
    [
        ("test-1.json", "_COMPLETE"),
        ("test-2.json", "_COMPLETE"),
        ("test-3.json", "_BASIC"),
    ],
)
def test_check_transaction_data_type(filename, mode, configuration):
    c = configuration
    c._INPUT_FILE = filename

    d = read_json_with_config(c)
    transactions = d[c._TRANSACTIONS]

    test_value = check_transaction_data_type(transactions, c)
    assert_value = getattr(c, mode)
    assert test_value == assert_value


@pytest.mark.parametrize(
    "filename",
    [
        "test-4.json",
        "test-5.json",
    ],
)
def test_check_transaction_data_type_system_exit(filename, configuration):
    c = configuration
    c._INPUT_FILE = filename

    d = read_json_with_config(c)
    transactions = d[c._TRANSACTIONS]

    with pytest.raises(SystemExit) as e:
        check_transaction_data_type(transactions, c)

    assert e.value.code == 1


def test_ffill_mid():
    df = (
        DataFrame(
            [
                {"date": "1997-10-15", "Open": 96.90, "Close": 96.80},
                {"date": "1997-10-16", "Open": 96.60, "Close": 96.40},
                {"date": "1997-10-17", "Open": 97.10, "Close": 97.50},
                {"date": "1997-10-20", "Open": 97.60, "Close": 97.40},
            ]
        )
        .astype({"date": "datetime64[ns]"})
        .set_index("date")
    )

    df_assert_value = DataFrame(
        {
            "Mid": {
                Timestamp("1997-10-15 00:00:00"): 96.85,
                Timestamp("1997-10-16 00:00:00"): 96.50,
                Timestamp("1997-10-17 00:00:00"): 97.30,
                Timestamp("1997-10-18 00:00:00"): 97.30,
                Timestamp("1997-10-19 00:00:00"): 97.30,
                Timestamp("1997-10-20 00:00:00"): 97.50,
            }
        }
    )
    df_assert_value.index.name = "date"
    df_assert_value.index.freq = "D"

    df_test_value = ffill_mid(df)

    assert_frame_equal(df_test_value, df_assert_value)


def test_read_in_transactions_basic(configuration):
    c = configuration
    c._INPUT_FILE = "test-3.json"

    df_test_value = read_in_transactions(c)
    df_assert_value = DataFrame(
        {
            "amount": {
                Timestamp("2021-10-12 00:00:00"): 0.5,
                Timestamp("2021-11-12 00:00:00"): 0.2,
                Timestamp("2022-11-16 00:00:00"): -0.4,
            },
            "market price": {
                Timestamp("2021-10-12 00:00:00"): 56783.9453125,
                Timestamp("2021-11-12 00:00:00"): 64509.9609375,
                Timestamp("2022-11-16 00:00:00"): 16776.890625,
            },
            "exchange rate": {
                Timestamp("2021-10-12 00:00:00"): 8.771409869525847,
                Timestamp("2021-11-12 00:00:00"): 8.70858933063606,
                Timestamp("2022-11-16 00:00:00"): 10.459399860928617,
            },
        }
    )
    df_assert_value.index.name = c._DATE

    assert_frame_equal(df_test_value, df_assert_value)


def test_read_in_transactions_complete(configuration):
    c = configuration
    c._INPUT_FILE = "test-1.json"

    df_test_value = read_in_transactions(c)
    df_assert_value = DataFrame(
        {
            "amount": {
                Timestamp("2021-10-12 00:00:00"): 0.5,
                Timestamp("2021-11-12 00:00:00"): 0.2,
                Timestamp("2022-11-16 00:00:00"): -0.4,
            },
            "market price": {
                Timestamp("2021-10-12 00:00:00"): 40000.00,
                Timestamp("2021-11-12 00:00:00"): 50000.00,
                Timestamp("2022-11-16 00:00:00"): 100000.00,
            },
            "exchange rate": {
                Timestamp("2021-10-12 00:00:00"): 1,
                Timestamp("2021-11-12 00:00:00"): 1,
                Timestamp("2022-11-16 00:00:00"): 1,
            },
        }
    )
    df_assert_value.index.name = c._DATE

    assert_frame_equal(df_test_value, df_assert_value)


def test_complement_basic_data(configuration):
    c = configuration

    asset = "BTC-USD"
    currency = "SEK"

    df = DataFrame(
        {
            "amount": {
                Timestamp("2021-10-12 00:00:00"): 0.5,
                Timestamp("2022-11-16 00:00:00"): -0.4,
                Timestamp("2021-11-12 00:00:00"): 0.2,
            }
        }
    )
    df_test_value = complement_basic_data(asset, currency, df, c)

    df_assert_value = DataFrame(
        {
            "amount": {
                Timestamp("2021-10-12 00:00:00"): 0.5,
                Timestamp("2021-11-12 00:00:00"): 0.2,
                Timestamp("2022-11-16 00:00:00"): -0.4,
            },
            "market price": {
                Timestamp("2021-10-12 00:00:00"): 56783.945312,
                Timestamp("2021-11-12 00:00:00"): 64509.960938,
                Timestamp("2022-11-16 00:00:00"): 16776.890625,
            },
            "exchange rate": {
                Timestamp("2021-10-12 00:00:00"): 8.771410,
                Timestamp("2021-11-12 00:00:00"): 8.708589,
                Timestamp("2022-11-16 00:00:00"): 10.459400,
            },
        }
    )

    assert_frame_equal(df_test_value, df_assert_value)
