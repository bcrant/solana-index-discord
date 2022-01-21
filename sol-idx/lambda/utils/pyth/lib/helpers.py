import time
import datetime
import dateutil
from dateutil import relativedelta
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US')


def get_unix_timestamps():
    utc_12M_ago_ts = int(datetime.datetime.timestamp(datetime.datetime.utcfromtimestamp(
        int(time.time())) - dateutil.relativedelta.relativedelta(months=12)
    ))
    utc_now_ts = int(time.time())
    return utc_12M_ago_ts, utc_now_ts


def get_date_from_unix_timestamp(ts: int):
    return datetime.datetime.fromtimestamp(ts/1000).isoformat()


def get_iso_utc_timestamp_now():
    return datetime.datetime.utcnow().isoformat()


def get_trends_df(tokens: list):
    url_fmt = [
        token + ' crypto'
        for token in tokens
    ]
    pytrends.build_payload(kw_list=url_fmt, timeframe='today 12-m')
    trends_df = pytrends.interest_over_time()
    trends_df.columns = [col.rstrip(' crypto') for col in trends_df.columns]
    return trends_df
