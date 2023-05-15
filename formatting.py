from numbers import Integral as N
from pandas import DataFrame


def _format_DF(md_table: str, title: str) -> str:
    first_row = md_table.split()[0]
    width = len(first_row)
    centered_title = title.center(width)
    return centered_title + "\n" + md_table


def format_DF(df: DataFrame, title: str, m: dict, index: bool) -> str:
    df = df.rename(columns=m)
    markdown_table = df.to_markdown(index=index, tablefmt="grid")
    titled_markedown_table = _format_DF(markdown_table, title)
    return titled_markedown_table
