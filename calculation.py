from datetime import datetime

import pandas as DataFrame

from _config import Config


def calculate_cost(df: DataFrame, c: Config) -> DataFrame:
    return df.assign(
        _cost = lambda df: (
            -1 * df[c._AMOUNT] * df[c._PRICE] * df[c._FX_RATE]
        )
    )


def format_table(recieved, aquisition_price, profit_and_loss) -> None:
    out = f"| RECIEVED: {recieved} | AQUISITION PRICE: {aquisition_price} | P&L: {profit_and_loss} |"

    print(len(out) * "-")
    print(out)
    print(len(out) * "-")

    return None


def calculate_statistics(df: DataFrame, financial_year: int, c: Config) -> DataFrame:
    df = calculate_cost(df, c)

    df_buy = df.query(f"{c._AMOUNT} > 0")
    df_sell = df .loc[df.index.year == financial_year] .query(f"{c._AMOUNT} < 0")

    bought = df_buy.loc[:, c._AMOUNT].abs().sum()
    payed = df_buy._cost.abs().sum()

    sold = df_sell.loc[:, c._AMOUNT].abs().sum()
    recieved = df_sell._cost.abs().sum()

    aquisition_price = (avg_buy_price := payed / bought) * sold

    profit_and_loss = recieved - aquisition_price

    return recieved, aquisition_price, profit_and_loss
