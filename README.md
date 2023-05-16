# CIT

CIT is a command-line interface designed to calculate the tax liability
associated with capital income tax on the buying, selling, and spending of
cryptocurrencies, adhering to the rules and regulations set forth by the
Swedish Tax Agency (Swe., Skatteverket).

CIT is a double-nested recursive acronym that stands for **CIT's Income Tax**
where the first CIT represents *Crypto Income Tax* and is also an acronym from
the term capital income tax.

## Installation and documentation

### Installation

To set up CIT, the user clones the project locally by running the command `git
clone https://github.com/vezeli/cit.git`. The program does not require
installation since the command-line interface (CLI) can be executed directly
from a script.

CIT is tested with Python 3.10 and newer versions and has dependencies on
third-party packages. To install the necessary dependencies, navigate to the
project's root directory in a terminal and run the command `python -m pip
install -r requirements.txt`.

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

CIT operates in two mode:

1. When the user provides both transaction details and market prices in a JSON
   file, CIT processes the transaction data based on the provided information.

2. If the market prices are not included in the JSON file, CIT automatically
   retrieves the prices from Yahoo Finance. It then proceeds to process the
   transaction data using the fetched market prices, just as it would if the
   prices were provided in the file.

#### Input files

To use CIT with a JSON file, the file must adhere to the configuration format
specified in `_config.py`. By default, the following information needs to be
provided in the JSON file:

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

- `market price`: A numeric value representing the price *per crypto unit* in
  `AssetPriceCurrency` at the time of the transaction.

- `exchange rate`: A numeric value representing the exchange rate between
  `AssetPriceCurrency` and `Currency` at the time of the transaction.
  `AssetPriceCurrency` is considered the base currency, and `Currency` is the
  price currency.

When the `market price` and `exchange rate` keys are omitted in the
`Transactions` dictionary, CIT operates in the download mode. In this mode, it
fetches the so-called mid prices from Yahoo Finance, which are calculated as
the average of the open and close prices for that day.

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
