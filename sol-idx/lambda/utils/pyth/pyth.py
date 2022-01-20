import asyncio
from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pythclient.pythclient import PythClient
from pythclient.utils import get_key
from utils.constants import SolanaTokens
from utils.coin_gecko import derive_index
from utils.helpers import get_iso_utc_timestamp_now, get_trends_df


async def main():
    v2_first_mapping_account_key = get_key('devnet', 'mapping')
    v2_program_key = get_key('devnet', 'program')
    async with PythClient(
        first_mapping_account_key=v2_first_mapping_account_key,
        program_key=v2_program_key or None,
    ) as c:
        await c.refresh_all_prices()
        solana_products = limit_to_solana_tokens(await c.get_products())
        solana_products_prices = list()
        for sp in solana_products:
            valid_prices = validate_price_status(await sp.get_prices())
            if valid_prices is not None:
                solana_products_prices.append(valid_prices)

        idx = derive_index(solana_products_prices)

        token_names: list = list(idx.keys())
        trends_df = get_trends_df(token_names)
        print(trends_df)


def limit_to_solana_tokens(products_list):
    return list(
        cp
        for cp in products_list
        if cp.attrs.get('asset_type') == 'Crypto'
        and cp.attrs.get('base') in SolanaTokens.TOP_20
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
                get_iso_utc_timestamp_now(),
                pr.product.symbol.lstrip('Crypto.').rstrip('/USD'),
                pr.aggregate_price_info.price
            ))


if __name__ == '__main__':
    asyncio.run(main())
