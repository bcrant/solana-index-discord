import pandas as pd


def get_pyth_df(price_data):
    df = pd.DataFrame(price_data, columns=['datetime', 'symbol', 'price'])
    df['percent_total'] = df['price'] / df['price'].sum()
    return df
