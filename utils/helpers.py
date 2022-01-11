import datetime
import pandas as pd
import pprint
import requests
from pycoingecko import CoinGeckoAPI
from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from utils.const import SolanaTokens
from trends import get_trends
cg = CoinGeckoAPI()


def get_trends(tokens: list):
    url = 'https://trends.google.com/trends/explore?q='
    for token in tokens:
        url += f'{token}%20crypto'

    print('FINAL URL')
    print(url)


def get_token_market_cap(token: str, token_list: list):
    token_data = dict()
    token_keys = {'id', 'name', 'symbol', 'asset_platform_id'}
    for coin_dict in token_list:
        if coin_dict.get('symbol') == token.lower():
            cg_id = coin_dict.get('id')
            cg_data = cg.get_coin_by_id(id=cg_id)
            tmp_dict = dict()
            for k in token_keys:
                tmp_dict[k] = cg_data.get(k)
            tmp_dict['usd_market_cap'] = cg_data.get('market_data').get('market_cap').get('usd')
            tmp_dict['usd_current_price'] = cg_data.get('market_data').get('current_price').get('usd')
            token_data[tmp_dict.get('name')] = tmp_dict

    return token_data


def derive_index(data: list[tuple]):
    df = pd.DataFrame(data, columns=['datetime', 'symbol', 'price'])
    df['percent_total'] = df['price']/df['price'].sum()
    print(df.info())
    print(df.sort_values(by='price', ascending=False))

    token_list = cg.get_coins_list()

    idx = dict()
    for tok in df['symbol'].tolist():
        idx.update(get_token_market_cap(tok, token_list))

    print('INDEX')
    pprint.pprint(idx)

    get_trends(list(idx.keys()))


# Next get weighted average
    # what is difference between weighted average and percent of total


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
                datetime.datetime.utcnow().isoformat(),
                pr.product.symbol.lstrip('Crypto.').rstrip('/USD'),
                pr.aggregate_price_info.price
            ))
