[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# CIT

CIT is a command-line interface designed to calculate the tax liability
associated with capital income tax on the buying, selling, and spending of
cryptocurrencies, following to the rules and regulations set forth by the
Swedish Tax Agency (Swe., Skatteverket).

CIT is a double-nested recursive acronym that stands for **CIT's Income Tax**
with the first CIT represents *Crypto Income Tax* and is also an acronym from
the term capital income tax.

## Installation

To set up CIT, the user clones the project locally by running the command `git
clone https://github.com/vezeli/cit.git`. The program does not require
installation since the command-line interface (CLI) can be executed directly
from a script.

CIT is tested with Python 3.10 or later versions and has dependencies on
third-party packages. To install the necessary dependencies, navigate to the
project's root directory within a terminal and execute the command `python -m
pip install -r requirements.txt`.

## Documentation

### Usage

Script `cit.py` starts the CLI

``$ python cit.py --help``

which provides three subcommands with their positional and optional arguments:

* ``$ python cit.py transactions --help`` - show asset transactions

* ``$ python cit.py forex-transactions --help`` - construct asset-denominated FX transactions

* ``$ python cit.py calculate --help`` - preform portfolio calculations

The program, by default, reads JSON files relative to the `./input_data`
directory. If no CLI argument is provided to specify the input file name, the
program will read from `./input_data/skatteverket-example-1.json`. Optional
argument `--in` is available for specifying the names of the input files.

### Input Files

To read transaction data from a JSON file, the file needs to comply with the
configuration format specified in `config.py`. By default, the following
information needs to be provided in the JSON file:

- `Asset`: A string representing the ticker symbol for the currency pair from
  Yahoo Finance (e.g., BTC-USD, DOGE-USD).

- `AssetPriceCurrency`: A string with the currency symbol used for pricing the
  Asset (e.g., USD).

- `Transactions`: A nested container that stores a list of records
  (dictionaries) with details about the transactions.

Each record within `Transactions` should include the following information:

- `date`: A string indicating the transaction date formatted as `YYYY-MM-DD`.

- `amount`: A numeric value representing the quantity of crypto units that were
  bought, sold, or spent. Positive values indicate buying, and negative values
  indicate selling or spending.

- `market price`: A positive numeric value representing the price *per crypto
  unit* in `AssetPriceCurrency` at the time of the transaction.

- `exchange rate`: A positive numeric value representing the exchange rate
  between `AssetPriceCurrency` and domestic currency (`_DOMESTIC_CURRENCY`
  specified in the `config.py`) at the time of the transaction.
  `AssetPriceCurrency` is considered the base currency, and the domestic
  currency is the price currency.

### Modes

CIT operates in two modes:

1. When the user provides `market price` and `exchange rate` data in the JSON
   input file, CIT processes the transaction data with the provided
   information.

2. If `market price` and `exchange rate` keys are omitted in the nested
   `Transactions` container, CIT automatically retrieves the market data from
   Yahoo Finance. In this mode, it fetches the so-called mid prices, which are
   calculated as the average of the opening and closing prices for a given day.
   It then processes the transaction data, with the fetched market prices, just
   as it would if the prices were provided in the JSON file.

## Skatteverket's Examples

Skatteverket offers hypothetical examples of transaction histories, accompanied
by a step-by-step guide that demonstrates how to utilize transaction data for
calculating tax liabilities.

The following examples are found on [Skatteverket's
website](https://skatteverket.se/privat/skatter/vardepapper/andratillgangar/kryptovalutor.4.15532c7b1442f256bae11b60.html):

1. Köp och försäljning av kryptovaluta
2. Köp, försäljning, köp av varor

To replicate these examples, two JSON files,
`./input_data/skatteverket-example-1.json` and
`./input_data/skatteverket-example-2.json`, have been created using the
provided data which are included as part of the project.

### Hands On Examples

In this subsection we provide guidance on processing transaction data using the
file `./input_data/skatteverket-example-1.json` as an illustrative example.
However, the same approach can be applied to process other input files as well.

* For listing all transactions, use the `transactions` subcommand with
  positional argument `all` and optional argument `--in`:

``$ python cit.py transactions all --in skatteverket-example-1.json``

* For listing only the buy transactions made during 2021:

``$ python cit.py transactions buy --in skatteverket-example-1.json --year 2021``

* To summarize and calculate position statistics for the year 2022, use the
  `calculate` subcommand:

``$ python cit.py calculate summary --in skatteverket-example-1.json --year 2022``

* When making a sell transaction, you can calculate the profit and loss (P&L)
  using the `calculate` subcommand with the `profit-and-loss` positional
  argument:

``$ python cit.py calculate profit-and-loss --in skatteverket-example-1.json --year 2022``

* For calculating the tax liability in domestic currency from the P&L, use the
  `calculate` subcommand with the `tax-liability` positional argument:

``$ python cit.py calculate tax-liability --in skatteverket-example-1.json --year 2022 --domestic-ccy``

Typically, you can use the `--domestic-ccy` optional flag to control the
currency in which CIT provides results (asset-denominated or domestic).
However, in the current examples, this flag is not relevant because the market
prices are denominated in the domestic currency.

* Skatteverket considers buying and selling of asset-denominated currency
  (e.g., USD) as separate forex trades. To construct a list of FX transaction
  from the input data, use the `forex-transactions` subcommand:

``$ python cit.py forex-transactions --in skatteverket-example-1.json``

It is recommend to go through examples step by step and compare CIT's outputs
with the calculations from Skatteverket. This will greatly improve your
understanding of how CIT operates behind the scenes and how you can efficiently
utilize it.

## Known Issues

When using the `yfinance` library to fetch market data from Yahoo Finance, you
may encounter an issue if your application is running behind a proxy. This
issue can manifest as an `SSLCertVerificationError`. To resolve this problem on
Windows, you can try installing the python-certifi-win32 library by executing
the command `pip install python-certifi-win32`.

For further details and discussions regarding this issue, you can refer to the
relevant [GitHub issue](https://github.com/ranaroussi/yfinance/issues/963).

## Disclaimer

This program is not a substitute for professional accounting advice and should
not be used as such. You should always seek the guidance of a tax accountant
and/or professional for comprehensive and correct tax advice and calculation.
