from numbers import Real as R

import numpy as np
from pandas import concat, DataFrame, Series

from _config import Config


def format_table(recieved, acquisition_price, profit_and_loss) -> None:
    out = f"| RECIEVED: {recieved:.2f} | ACQUISITION PRICE: {acquisition_price:.2f} | P&L: {profit_and_loss:.2f} |"

    print(len(out) * "-")
    print(out)
    print(len(out) * "-")

    return None


def calculate_acquisition_prices(df: DataFrame, c: Config) -> DataFrame:
    _COST = "_cost_per_unit"

    def _calculate_cost(df: DataFrame, c: Config) -> DataFrame:
        nonlocal _COST
        df = (
            df
            .copy()
            .assign(Cost = lambda x: (-1 * np.sign(x[c._AMOUNT])) * x[c._PRICE])
            .rename(columns={"Cost": _COST})
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
        [df, Series(acquisition_prices, index=df.index, name=c._ACQUISITION_PRICE)]
        , axis=1
    )


def calculate_PNL(df: DataFrame, c: Config) -> DataFrame:
    df = (
        df
        .copy()
        .assign(PNL = lambda x:
            np.minimum(x[c._AMOUNT], 0) * x[c._FX_RATE] * (x[c._ACQUISITION_PRICE] - x[c._PRICE])
        ).rename(columns={"PNL": c._PNL})
    )
    return df


def process_transactions(df: DataFrame, c: Config) -> DataFrame:
    df = (
        df
        .copy()
        .pipe(calculate_acquisition_prices, c=c)
        .pipe(calculate_PNL, c=c)
    )
    return df
