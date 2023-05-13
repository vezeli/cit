from numbers import Integral as N
from numbers import Real as R

import numpy as np
from pandas import concat, DataFrame, Series

from _config import Config


def calculate_acquisition_prices(df: DataFrame, c: Config) -> DataFrame:
    _COST = "_cost_per_unit"

    def _calculate_cost(df: DataFrame, c: Config) -> DataFrame:
        nonlocal _COST
        df = (
            df
            .copy()
            .assign(Cost_per_unit = lambda x: (-1 * np.sign(x[c._AMOUNT])) * x[c._PRICE])
            .rename(columns={"Cost_per_unit": _COST})
        )
        return df

    def _calculate_acquisition_prices(df: DataFrame, c: Config) -> list[R]:
        nonlocal _COST

        def _is_sell(cost: R) -> bool:
            return True if cost < 0 else False

        def _is_first_transaction(row: Series, df: DataFrame) -> bool:
            first_row = 0
            return row.equals(df.iloc[first_row, :])

        df_transactions = df.pipe(_calculate_cost, c=c)

        acquisition_prices: list[R] = []
        for _, transaction in df_transactions.iterrows():
            cost, amount = -transaction[_COST], transaction[c._AMOUNT]

            if _is_first_transaction(transaction, df_transactions):
                acquisition_price = cost
                acquisition_amount = 0 + amount
            else:
                acquisition_amount = (previous_acquisition_amount := acquisition_amount) + amount
                # When selling `acquisition_price` doesn't change but the amount
                # held (i.e., `acquisition_amount`) changes:
                if _is_sell(cost):
                    acquisition_price: R = acquisition_price
                # When buying both `acquisition_price` and `acquisition_amount` are affected:
                else: 
                    acquisition_price: R = np.average(
                        [acquisition_price, cost],
                        weights=[previous_acquisition_amount, amount]
                    )

            acquisition_prices.append(acquisition_price)

        return acquisition_prices

    acquisition_prices: list[R] = df.pipe(_calculate_acquisition_prices, c=c)
    return concat(
        [
            df,
            Series(acquisition_prices, index=df.index, name=c._ACQUISITION_PRICE)
        ],
        axis=1
    )


def _calculate_PNL(df: DataFrame, c: Config) -> DataFrame:
    # PNL can be calculated only for sell transactions (i.e., when `amount` is
    # negative), because buy transactions do not have any profit and loss.
    df = (
        df
        .copy()
        .query(f"{c._AMOUNT} < 0")
        .assign(
            PNL = lambda x:
                (-1 * x[c._AMOUNT]) * (x[c._PRICE] - x[c._ACQUISITION_PRICE])
        )
        .rename(columns={"PNL": c._PNL})
    )
    return df


def calculate_PNL(df: DataFrame, c: Config) -> DataFrame:
    df = (
        df
        .copy()
        .pipe(calculate_acquisition_prices, c=c)
        .pipe(_calculate_PNL, c=c)
    )
    return df


def calculate_PNL_per_year(financial_year: N, df: DataFrame, c: Config) -> DataFrame:
    df =  df.pipe(calculate_PNL, c=c)
    return df.loc[df.index.year == financial_year]


def calculate_statistics(financial_year: N, df: DataFrame, c: Config) -> DataFrame:
    df = (
        df
        .pipe(calculate_acquisition_prices, c=c)
        .loc[df.index.year == financial_year]
    )

    bought: R = df.loc[df[c._AMOUNT] > 0, c._AMOUNT].sum()
    sold: R = df.loc[df[c._AMOUNT] < 0, c._AMOUNT].sum()
    remaining: R = bought + sold
    average_buying_price: R = (
            df
            .loc[:, c._ACQUISITION_PRICE]
            .tail(1)
            .squeeze()
    )

    df = DataFrame(
        {
            "Amount bought": [bought],
            "Amount sold": [sold],
            "Remaining": [remaining],
            "Average buying price": [average_buying_price],
        }
    ).round(
        {
            "Amount bought": 5,
            "Amount sold": 5,
            "Remaining": 5,
            "Average buying price": 2,
        }
    )
    return df



def calculate_skatteverket(financial_year: N, df: DataFrame, c: Config) -> DataFrame:
    df = df.loc[df.index.year == financial_year]

    bought = df.loc[df[c._AMOUNT] > 0, c._AMOUNT].sum()
    sold = df.loc[df[c._AMOUNT] < 0, c._AMOUNT].sum()

    df_ = df.pipe(calculate_PNL, c)

    recieved = (
        df_
        .assign(Recieved = lambda x:
            (-1 * x[c._AMOUNT]) * x[c._PRICE]
        )
        .Recieved
        .sum()
    )

    payed = (
        df_
        .assign(Payed = lambda x:
            (-1 * x[c._AMOUNT]) * x[c._ACQUISITION_PRICE]
        )
        .Payed
        .sum()
    )

    df_[c._TAXABLE] = df_[c._PNL].apply(
            lambda pnl: pnl if pnl > 0 else c._DEDUCTIBLE * pnl
    )
    taxable = df_[c._TAXABLE].sum()

    df = DataFrame(
        {
            "Amount bought": [bought],
            "Amount sold": [sold],
            "Recieved": [recieved],
            "Payed": [payed],
            "Taxable": [taxable],
        }
    ).round(
        {
            "Amount bought": 5,
            "Amount sold": 5,
            "Recieved": 2,
            "Payed": 2,
            "Taxable": 2,
        }
    )
    return df
