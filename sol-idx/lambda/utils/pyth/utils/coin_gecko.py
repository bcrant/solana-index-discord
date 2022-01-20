import pandas as pd
from utils.helpers import get_unix_timestamps, get_date_from_unix_timestamp
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()


def get_token_historical_data(token: str, token_list: list):
    start_ts, end_ts = get_unix_timestamps()

    token_historical_dict = dict()
    for coin_dict in token_list:
        if coin_dict.get('symbol') == token.lower():
            cg_id = coin_dict.get('id')
            historical_data = cg.get_coin_market_chart_range_by_id(
                id=cg_id,
                vs_currency='usd',
                from_timestamp=start_ts,
                to_timestamp=end_ts,
            )

            dt_idx: list = []
            for price in historical_data.get('prices'):
                dt_idx.append(get_date_from_unix_timestamp(price[0]))

            tmp_dict: dict = {}
            for col in historical_data.keys():
                rows = historical_data.get(col)
                tmp_dict[col] = list(row[1] for row in rows)

            historical_data_df = pd.DataFrame(
                data=tmp_dict,
                index=dt_idx,
                columns=['prices', 'market_caps', 'total_volumes']
            )
            print(historical_data_df.head())

            token_historical_dict.update(historical_data)

    return token_historical_dict


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
    token_list = cg.get_coins_list()

    idx = dict()
    for tok in df['symbol'].tolist():
        idx.update(get_token_market_cap(tok, token_list))
        # idx.update(get_token_historical_data(tok, token_list))

    # pprint.pprint(idx)

    return idx
