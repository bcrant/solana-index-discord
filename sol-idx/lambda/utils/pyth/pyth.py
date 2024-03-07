import asyncio
from pythclient.exceptions import SolanaException
from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pythclient.pythclient import PythClient
from pythclient.ratelimit import RateLimit
from pythclient.utils import get_key
from utils.pyth.lib.constants import SolanaTokens, IpBanned
from utils.pyth.lib.helpers import fmt_pyth_output, get_iso_utc_timestamp_now

RateLimit.configure_default_ratelimit(overall_cps=2, method_cps=2, connection_cps=2)


async def get_pyth_price_feed():
    v2_first_mapping_account_key = get_key("devnet", "mapping")
    v2_program_key = get_key("devnet", "program")
    async with PythClient(
        first_mapping_account_key=v2_first_mapping_account_key,
        program_key=v2_program_key or None,
    ) as c:
        await c.refresh_all_prices()
        solana_products = limit_to_solana_tokens(await c.get_products())
        solana_products_prices = dict()
        for sp in solana_products:
            valid_prices = validate_price_status(await sp.get_prices())
            if valid_prices is not None:
                solana_products_prices[valid_prices[0]] = valid_prices[1]

        return solana_products_prices


def limit_to_solana_tokens(products_list):
    return list(
        cp
        for cp in products_list
        if cp.attrs.get("asset_type") == "Crypto"
        and cp.attrs.get("base") in SolanaTokens.TOP_20
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

        if valid_count >= 2:
            # Columns: UTC DateTime, Symbol, Price
            return tuple(
                (
                    pr.product.symbol.lstrip("Crypto.").rstrip("/USD"),
                    pr.aggregate_price_info.price,
                )
            )


def format_price_records(prices: PythPriceAccount):
    for _, pr in {**prices}.items():
        # Columns: UTC DateTime, Symbol, Price
        return tuple(
            (
                get_iso_utc_timestamp_now(),
                pr.product.symbol.lstrip("Crypto.").rstrip("/USD"),
                pr.aggregate_price_info.price,
            )
        )


def get_pyth_discord_response(logger):
    try:
        msg = asyncio.run(get_pyth_price_feed())
        logger.info(f"Pyth Price Feed Message: {type(msg)} {msg}")
        return fmt_pyth_output(msg, logger)

    except SolanaException as s_err:
        logger.error(f"Solana Exception: {s_err}")
        # Provide a fallback value when API Gateway IP gets banned
        # I might try to port the PythHttpClient from pyth-client-js to pyth-client-py
        # to facilitate trivial requests that do not require a websocket
        return fmt_pyth_output(IpBanned.FALLBACK_MSG, logger)


if __name__ == "__main__":
    asyncio.run(get_pyth_price_feed())
