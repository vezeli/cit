from numbers import Real as R
from dataclasses import dataclass


@dataclass
class Config:
    _DATA_PATH: str = "./input_data"
    _INPUT_FILE: str = "skatteverket-example-1.json"
    _BASIC: str = "BACIS"
    _COMPLETE: str = "COMPLETE"
    _ASSET: str = "Asset"
    _ASSET_CURRENCY: str = "AssetPriceCurrency"
    _TRANSACTIONS: str = "Transactions"
    _DATE: str = "date"
    _AMOUNT: str = "amount"
    _PRICE: str = "market price"
    _FX_RATE: str = "exchange rate"
    _ACQUISITION_PRICE: str = "acquisition price"
    _PNL: str = "P&L"
    _TAXABLE: str = "taxable"
    _DEDUCTIBLE: R = 0.7
    _DOMESTIC_CURRENCY: str = "SEK"
