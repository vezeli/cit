# CIT

CIT is a command-line interface designed to calculate the tax liability
associated with capital income tax on the buying, selling, and spending of
cryptocurrencies, following to the rules and regulations set forth by the
Swedish Tax Agency (Swe., Skatteverket).

CIT is a double-nested recursive acronym that stands for **CIT's Income Tax**
with the first CIT represents *Crypto Income Tax* and is also an acronym from
the term capital income tax.

## Installation and Documentation

### Installation

To set up CIT, the user clones the project locally by running the command `git
clone https://github.com/vezeli/cit.git`. The program does not require
installation since the command-line interface (CLI) can be executed directly
from a script.

CIT is tested with Python 3.10 or later versions and has dependencies on
third-party packages. To install the necessary dependencies, navigate to the
project's root directory within a terminal and execute the command `python -m
pip install -r requirements.txt`.

### Usage

Script `cit.py` starts the CLI

``$ python cit.py --help``

which provides three subcommands with their positional and optional arguments:

* ``$ python cit.py transactions --help`` - list transactions (alias `ls`)

* ``$ python cit.py summary --help`` - aggregate transactions (alias `agg`)

* ``$ python cit.py report --help`` - process transactions and creates a report
  (alias `get`)

The program, by default, reads JSON files from the `./data` directory that
contain transaction data. If no CLI argument is provided to specify the input
file name, the program will read from `./data/skatteverket-example-1.json`. An
optional argument `-i` or `--in` is available for the user to specify the input
file name within the `./data` directory.

### Modes

CIT operates in two modes:

1. When the user provides market prices and exchange rates in a JSON file, CIT
   processes the transaction data with the provided information.

2. If the market prices are not included in the JSON file, CIT automatically
   retrieves the prices from Yahoo Finance. It then proceeds to process the
   transaction data using the fetched market prices, just as it would if the
   prices were provided in the JSON file.

### Input Files

To read transaction data from a JSON file, the file needs to comply with the
configuration format specified in `_config.py`. By default, the following
information needs to be provided in the JSON file:

- `Asset`: A string representing the ticker symbol for the currency pair from
  Yahoo Finance (e.g., BTC-USD, DOGE-USD).

- `AssetPriceCurrency`: A string with the currency symbol used for pricing the
  Asset (e.g., USD).

- `Currency`: A string representing the domestic currency symbol in which the
  taxes are paid (e.g., SEK). Note that it can be the same as
  `AssetPriceCurrency`.

- `Transactions`: A nested container that stores a list of dictionaries with
  details about the transactions.

Each dictionary within `Transactions` should include the following information:

- `date`: A string indicating the transaction date.

- `amount`: A numeric value representing the quantity of crypto units that were
  bought, sold, or spent. Positive values indicate buying, and negative values
  indicate selling or spending.

- `market price`: A positive numeric value representing the price *per crypto
  unit* in `AssetPriceCurrency` at the time of the transaction.

- `exchange rate`: A positive numeric value representing the exchange rate
  between `AssetPriceCurrency` and `Currency` at the time of the transaction.
  `AssetPriceCurrency` is considered the base currency, and `Currency` is the
  price currency.

When the `market price` and `exchange rate` keys are omitted in the
`Transactions` dictionary, CIT operates in the download mode. In this mode, it
fetches the so-called mid prices from Yahoo Finance, which are calculated as
the average of the opening and closing prices for that day.

## Skatteverket's Examples

Skatteverket offers hypothetical examples of transaction histories, accompanied
by a step-by-step guide that demonstrates how to utilize transaction data for
calculating tax liabilities.

The following examples are found on [Skatteverket's
website](https://skatteverket.se/privat/skatter/vardepapper/andratillgangar/kryptovalutor.4.15532c7b1442f256bae11b60.html):

1. Köp och försäljning av kryptovaluta
2. Köp, försäljning, köp av varor

To replicate these examples, two JSON files,
`./data/skatteverket-example-1.json` and `./data/skatteverket-example-2.json`,
have been created using the provided data which are included as part of the
project.

### Hands On Examples

In this subsection we provide guidance on processing transaction data using the
file `./data/skatteverket-example-1.json` as an illustrative example. However,
the same approach can be applied to process other input files as well.

* For listing all transactions, use the `transactions` subcommand with
  positional argument `all` and optional argument `--in`:

``$ python cit.py transactions --in "skatteverket-example-1.json" all``

* For listing only the buy transactions made in 2021:

``$ python cit.py transactions --year 2021 buy``

  Note that it is possible to omit the name of the files because
  `skatteverket-example-1.json` is default input file in `_config.py`:

* To aggregate the transaction data and summarize trade statistics for the year
  2022, use the `summary` subcommand:

``$ python cit.py summary --in "skatteverket-example-1.json" --year 2022``

* When making a sell transaction, you can calculate the profit and loss (P&L)
  using the `report` subcommand with the `pnl` positional argument:

``$ python cit.py report --in "skatteverket-example-1.json" --year 2022 pnl``

* For calculating the tax liability from the P&L, use the `report` subcommand
  with the `taxes` positional argument:

``$ python cit.py report --in "skatteverket-example-1.json" --year 2022 taxes``

Additionally, you can use the `--ccy` optional flag to control the currency in
which CIT provides results. However, for the current examples, this flag is not
relevant because the market prices are provided in the same currency in which
the tax is declared.

To make the commands less verbose use subcommand aliases `ls`, `agg` and `get`.

Finally, it is recommend to go through examples step by step and compare CIT's
outputs with the calculations from Skatteverket. This will greatly improve your
understanding of how CIT operates behind the scenes and how you can efficiently
utilize it.

## Disclaimer

This program is not a substitute for professional accounting advice and should
not be used as such. You should always seek the guidance of a tax accountant
and/or professional for comprehensive and correct tax advice and calculation.

## Warranty

Because the program is licensed free of charge, there is no warranty for the
program, to the extent permitted by applicable law. Except when otherwise
stated in writing the copyright holders and/or other parties provide the
program "as is" without warranty of any kind, either expressed or implied,
including, but not limited to, the implied warranties of merchantability and
fitness for a particular purpose. The entire risk as to the quality and
performance of the program is with you. Should the program prove defective, you
assume the cost of all necessary servicing, repair or correction.
