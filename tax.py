from _config import Config
from calculation import calculate_statistics, format_table
from data import read_in_transactions

config = Config()

if __name__ == "__main__":
    format_table(
        *calculate_statistics(
            df=read_in_transactions(config),
            financial_year=2021,
            c=config
        )
    )
