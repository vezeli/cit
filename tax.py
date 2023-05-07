from datetime import datetime

import pandas as pd

FINANCIAL_YEAR = 2021
DATA = pd.DataFrame(
    [
        {"transaction_date": datetime(2020,2,1), "amount": 1, "price": 1, "fxrate": 100},
        {"transaction_date": datetime(2020,6,1), "amount": 2, "price": 1, "fxrate": 100},
        {"transaction_date": datetime(2020,8,1), "amount": -1, "price": 8, "fxrate": 100},
        {"transaction_date": datetime(2021,6,1), "amount": -1, "price": 1, "fxrate": 100},
        {"transaction_date": datetime(2021,7,1), "amount": -1, "price": 3, "fxrate": 100},
    ]
).set_index("transaction_date")


def calculate_cost(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(cost=lambda df: -1 * df.amount * df.price * df.fxrate)


df = calculate_cost(DATA)

df_buy = df.query("amount > 0")
df_sell = df .loc[df.index.year == FINANCIAL_YEAR] .query("amount < 0")

bought = df_buy.amount.abs().sum()
payed = df_buy.cost.abs().sum()

sold = df_sell.amount.abs().sum()
recieved = df_sell.cost.abs().sum()

aquisition_price = (avg_buy_price := payed / bought) * sold

profit_and_loss = recieved - aquisition_price


def format_table(recieved, aquisition_price, profit_and_loss) -> None:
    out = f"| RECIEVED: {recieved} | AQUISITION PRICE: {aquisition_price} | P&L: {profit_and_loss} |"
    print(len(out) * "-")
    print(out)
    print(len(out) * "-")


format_table(recieved, aquisition_price, profit_and_loss)
