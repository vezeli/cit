import argparse
from datetime import datetime
from numbers import Real as R

from _config import Config
from calculation import (
    calculate_acquisition_prices,
    calculate_PNL_per_year,
    calculate_skatteverket,
    calculate_statistics,
)
from formatting import format_DF
from data import read_in_transactions

DISCLAIMER = (
"""BECAUSE THE PROGRAM IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY FOR THE
PROGRAM, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE
STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE
PROGRAM "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND
PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE PROGRAM PROVE DEFECTIVE, YOU
ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION."""
)


if __name__ == "__main__":

    config = Config()

    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int, default=datetime.now().year, help="financial year for calculation")
    parser.add_argument("-i", "--file", type=str, dest="file", default=config._DATA_PATH, help="path to input file")
    parser.add_argument("-p", "--pnl", action="store_true", help="show P&L instead of tax liability")
    parser.add_argument("-r", "--remaining", action="store_true", help="show remaining position")
    parser.add_argument("-m", "--mute", action="store_false", help="suppress showing the disclaimer")
    args = parser.parse_args()

    config._DATA_PATH = args.file

    df = read_in_transactions(config)

    print()
    
    if not args.pnl:
        print(
            format_DF(
                calculate_skatteverket(
                    financial_year=args.year,
                    df=df,
                    c=config,
                ),
                title="TAXATION"
            )
        )
    else:
        print(
            format_DF(
                calculate_PNL_per_year(
                    financial_year=args.year,
                    df=df,
                    c=config,
                ),
                title="PROFIT AND LOSS"
            )
        )
    
    if args.remaining:
        print()
        print(
            format_DF(
                calculate_statistics(
                    financial_year=args.year,
                    df=df,
                    c=config,
                ),
                title="STATISTICS"
            )
        )
    else:
        pass

    print()

    if args.mute:
        print(DISCLAIMER)
    else:
        pass
