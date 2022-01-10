import asyncio
from pythclient.pythclient import PythClient
from pythclient.utils import get_key
from utils.helpers import \
    derive_index, \
    limit_to_solana_tokens, \
    validate_price_status


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

        derive_index(solana_products_prices)

if __name__ == '__main__':
    asyncio.run(main())
