from datetime import datetime
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


def calculate_acquisition_costs(df_: DataFrame, c: Config) -> DataFrame:
    _COST = "_cost"


    def _calculate_cost(df_: DataFrame, c: Config) -> DataFrame:
        nonlocal _COST
        df = (
            df_
            .copy()
            .assign(Cost = lambda x: (-1 * np.sign(x[c._AMOUNT])) * x[c._PRICE])
            .rename(columns={"Cost": _COST})
        )
        return df


    def _calculate_acquisition_costs(df_: DataFrame, c: Config) -> list[R]:
        nonlocal _COST

        def _is_sell(cost: R) -> bool:
            return True if cost > 0 else False

        def _is_first_transaction(row: Series, df: DataFrame) -> bool:
            first_row = 0
            return row.equals(df.iloc[first_row, :])

        df_transactions = df_.pipe(_calculate_cost, c=c)

        acquisition_costs: list[R] = []
        for _, transaction in df_transactions.iterrows():
            cost, amount = transaction[_COST], transaction[c._AMOUNT]

            if _is_first_transaction(transaction, df_transactions):
                acquisition_cost = cost
                acquisition_amount = 0 + amount
            else:
                acquisition_amount = (previous_acquisition_amount := acquisition_amount) + amount
                # When selling `acquisition_cost` doesn't change but the amount
                # held (i.e., `acquisition_amount`) changes:
                if _is_sell(cost):
                    acquisition_cost: R = acquisition_cost
                # When buying both `acquisition_cost` and `acquisition_amount` are affected:
                else: 
                    acquisition_cost: R = np.average(
                        [acquisition_cost, cost],
                        weights=[previous_acquisition_amount, amount]
                    )

            acquisition_costs.append(acquisition_cost)

        return acquisition_costs

    acquisition_costs: list[R] = _calculate_acquisition_costs(df_, c)
    return concat(
        [df_, Series(acquisition_costs, index=df_.index, name=c._ACQUISITION_COST)]
        , axis=1
    )


def calculate_statistics(df: DataFrame, financial_year: int, c: Config) -> DataFrame:
    df = calculate_cost(df, c)

    df_buy = df.query(f"{c._AMOUNT} > 0")
    df_sell = df .loc[df.index.year == financial_year] .query(f"{c._AMOUNT} < 0")

    bought = df_buy.loc[:, c._AMOUNT].abs().sum()
    payed = df_buy._cost.abs().sum()

    sold = df_sell.loc[:, c._AMOUNT].abs().sum()
    recieved = df_sell._cost.abs().sum()

    acquisition_price = (avg_buy_price := payed / bought) * sold

    profit_and_loss = recieved - acquisition_price

    print(f"{bought=}, {payed=}")
    print(f"{sold=}, {recieved=}")
    print(f"{avg_buy_price=}")

    return recieved, acquisition_price, profit_and_loss
