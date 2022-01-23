import asyncio
from pythclient.exceptions import SolanaException
from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pythclient.pythclient import PythClient
from pythclient.ratelimit import RateLimit
from pythclient.utils import get_key
from utils.pyth.lib.constants import SolanaTokens
from utils.pyth.lib.helpers import get_iso_utc_timestamp_now

RateLimit.configure_default_ratelimit(overall_cps=9, method_cps=3, connection_cps=3)


async def get_pyth_price_feed():
    v2_first_mapping_account_key = get_key('devnet', 'mapping')
    v2_program_key = get_key('devnet', 'program')
    async with PythClient(
        first_mapping_account_key=v2_first_mapping_account_key,
        program_key=v2_program_key or None,
    ) as c:
        await c.refresh_all_prices()
        solana_products = limit_to_solana_tokens(await c.get_products())
        solana_products_prices = dict()
        for sp in solana_products:
            # valid_prices = validate_price_status(await sp.get_prices())
            # Skipping validation for now since devnet does not have as many producers...
            valid_prices = format_price_records(await sp.get_prices())
            if valid_prices is not None:
                solana_products_prices[valid_prices[0]] = valid_prices[1]

        # df = get_pyth_df(solana_products_prices)
        # print(df)

        print(solana_products_prices)
        return solana_products_prices


def limit_to_solana_tokens(products_list):
    return list(
        cp
        for cp in products_list
        if cp.attrs.get('asset_type') == 'Crypto'
        and cp.attrs.get('base') in SolanaTokens.TOP_20
    )


def validate_price_status(prices: PythPriceAccount):
    for _, pr in {**prices}.items():
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


def format_price_records(prices: PythPriceAccount):
    for _, pr in {**prices}.items():
        # Columns: UTC DateTime, Symbol, Price
        # return tuple((
        #     get_iso_utc_timestamp_now(),
        #     pr.product.symbol.lstrip('Crypto.').rstrip('/USD'),
        #     pr.aggregate_price_info.price
        # ))
        return tuple((
            pr.product.symbol.lstrip('Crypto.').rstrip('/USD'),
            pr.aggregate_price_info.price
        ))


def get_pyth_discord_response(logger):
    try:
        # msg = asyncio.run(get_pyth_price_feed())
        msg = {
            "SOL": 95.054,
            "RAY": 3.70145,
            "SNY": 1.8314000000000001,
            "MNGO": 0.1599069,
            "SLN": 2.6064000000000003,
            "FIDA": 1.4817
        }

        logger.info(f'Pyth Price Feed Message: {type(msg)} {msg}')
        return msg

    except SolanaException as s_err:
        msg = {'Solana Exception': s_err}
        logger.error(msg)
        return msg


if __name__ == '__main__':
    asyncio.run(get_pyth_price_feed())
