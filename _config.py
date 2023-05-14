from numbers import Real as R
from dataclasses import dataclass


@dataclass
class Config:
    _DATA_PATH: str = "./data"
    _INPUT_FILE: str = "transactions-example1.json"
    _BASIC: str = "BACIS"
    _COMPLETE: str = "COMPLETE"
    _ASSET: str  = "Asset"
    _CURRENCY: str = "Currency"
    _TRANSACTIONS: str = "Transactions"
    _DATE: str = "date"
    _AMOUNT: str = "amount"
    _PRICE: str = "market price"
    _FX_RATE: str = "exchange rate"
    _ACQUISITION_PRICE: str = "acquisition price"
    _PNL: str = "P&L"
    _TAXABLE: str = "taxable"
    _DEDUCTIBLE: R = 0.7
