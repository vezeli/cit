import sys

from _config import Config
from calculation import calculate_statistics, format_table
from data import read_in_transactions

config = Config()

if __name__ == "__main__":
    try:
        financial_year = int(sys.argv[1])
    except TypeError as e:
        raise e("Argument `financial_year` must be integer.")

    format_table(
        *calculate_statistics(
            df=read_in_transactions(config),
            financial_year=financial_year,
            c=config
        )
    )
