from dataclasses import dataclass


@dataclass
class Config:
    _DATA_PATH: str = "./transactions.json"
    _BASIC: str = "BACIS"
    _COMPLETE: str = "COMPLETE"
    _ASSET: str  = "Asset"
    _CURRENCY: str = "Currency"
    _TRANSACTIONS: str = "Transactions"
    _DATE: str = "date"
    _AMOUNT: str = "amount"
    _PRICE: str = "price"
    _FX_RATE: str = "exchange_rate"
    _ACQUISITION_PRICE: str = "acquisition_price"
    _PNL: str = "PNL"
