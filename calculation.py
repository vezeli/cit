from datetime import datetime
from numbers import Real as R

import numpy as np
from pandas import concat, DataFrame, Series

from _config import Config


def format_table(recieved, acquisition_price, profit_and_loss) -> None:
    out = f"| RECIEVED: {recieved:.2f} | AQUISITION PRICE: {acquisition_price:.2f} | P&L: {profit_and_loss:.2f} |"

    print(len(out) * "-")
    print(out)
    print(len(out) * "-")

    return None


def calculate_acquisition_cost(df_: DataFrame, c: Config) -> DataFrame:
    _COST = "_cost"


    def calculate_cost(df_: DataFrame, c: Config) -> DataFrame:
        nonlocal _COST
        df = (
            df_
            .copy()
            .assign(Cost = lambda x: -1*np.sign(x[c._AMOUNT])*x[c._PRICE])
            .rename(columns={"Cost": _COST})
        )
        return df


    def _calculate_acquisition_cost(df_: DataFrame, c: Config) -> DataFrame:
        nonlocal _COST

        def sell(transaction_cost: R) -> bool:
            return True if transaction_cost > 0 else False

        acquisition_costs = []
        for _, s in (df := df_.pipe(calculate_cost, c=c)).iterrows():
            transaction_cost, transaction_amount = s[_COST], s[c._AMOUNT]

            if s.equals(df.iloc[0, :]):
                acquisition_cost = transaction_cost
                storage = 0 + transaction_amount
            else:
                storage = (previous_storage := storage) + transaction_amount
                # When selling `acquisition_cost` doesn't change but the amount
                # held (i.e., `storage) changes:
                if sell(transaction_cost):
                    acquisition_cost = acquisition_cost
                # When buying both `acquisition_cost` and `storage` are affected:
                else: # when buying
                    acquisition_cost = np.average(
                        [acquisition_cost, transaction_cost],
                        weights=[previous_storage, transaction_amount]
                    )

            acquisition_costs.append(acquisition_cost)

        return -1*Series(acquisition_costs, index=df.index, name=c._AQUISITION_COST)

    acquisition_series = _calculate_acquisition_cost(df_, c)

    return concat([df_, acquisition_series], axis=1)


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
