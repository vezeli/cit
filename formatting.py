from pandas import DataFrame


def _format_DF(md_table: str, title: str) -> str:
    first_row = md_table.split()[0]
    width = len(first_row)
    centered_title = title.center(width)
    return centered_title + "\n" + md_table


def format_DF(df: DataFrame, title: str) -> str:
    df.columns = df.columns.str.capitalize()
    markdown_table = df.round(5).to_markdown(index=False, tablefmt="grid")
    titled_markedown_table = _format_DF(markdown_table, title)
    return titled_markedown_table
