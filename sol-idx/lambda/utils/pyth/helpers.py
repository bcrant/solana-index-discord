import datetime
import dateutil
import dateutil.parser
import pandas as pd
import time
from const import SolanaTokens
from pythclient.pythaccounts import PythPriceAccount, PythPriceStatus
from pytrends.request import TrendReq
from pycoingecko import CoinGeckoAPI
pytrends = TrendReq(hl='en-US')
cg = CoinGeckoAPI()


def get_unix_timestamps():
    utc_12M_ago_ts = int(datetime.datetime.timestamp(datetime.datetime.utcfromtimestamp(
        int(time.time())) - dateutil.relativedelta.relativedelta(months=12)
    ))
    utc_now_ts = int(time.time())
    return utc_12M_ago_ts, utc_now_ts


def get_date_from_unix_timestamp(ts: int):
    return datetime.datetime.fromtimestamp(ts/1000).isoformat()


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


def get_trends_df(tokens: list):
    url_fmt = [
        token + ' crypto'
        for token in tokens
    ]
    pytrends.build_payload(kw_list=url_fmt, timeframe='today 12-m')
    trends_df = pytrends.interest_over_time()
    trends_df.columns = [col.rstrip(' crypto') for col in trends_df.columns]
    return trends_df


def derive_index(data: list[tuple]):
    df = pd.DataFrame(data, columns=['datetime', 'symbol', 'price'])
    df['percent_total'] = df['price']/df['price'].sum()
    token_list = cg.get_coins_list()

    idx = dict()
    for tok in df['symbol'].tolist():
        # idx.update(get_token_market_cap(tok, token_list))
        idx.update(get_token_historical_data(tok, token_list))

    # pprint.pprint(idx)

    return idx


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
