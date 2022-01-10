import datetime
import pandas as pd
from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from utils.const import SolanaTokens


def derive_index(data: list[tuple]):
    df = pd.DataFrame(data, columns=['datetime', 'symbol', 'price'])
    print(df.info())
    print(df.sort_values(by='price', ascending=False))


def limit_to_solana_tokens(products_list):
    return list(
        cp
        for cp in products_list
        if cp.attrs.get('asset_type') == 'Crypto'
        and cp.attrs.get('base') in SolanaTokens.TOP
    )


def validate_price_status(prices: PythPriceAccount):
    for _, pr in prices.items():
        valid_count = 0
        invalid_count = 0
        for pc in pr.price_components:
            if pc.latest_price_info.price_status == PythPriceStatus.TRADING:
                valid_count += 1
            else:
                invalid_count += 1

        if valid_count >= 3:
            # Columns: UTC DateTime, Symbol, Price
            return tuple((
                datetime.datetime.utcnow().isoformat(),
                pr.product.symbol.lstrip('Crypto.').rstrip('/USD'),
                pr.aggregate_price_info.price
            ))
