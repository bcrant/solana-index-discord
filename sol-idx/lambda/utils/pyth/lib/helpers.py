import datetime
from textwrap import dedent


def get_iso_utc_timestamp_now():
    return datetime.datetime.utcnow().isoformat()


def fmt_pyth_output(msg: dict, logger):
    logger.debug('Formatting Pyth Message...')

    # Sort all coins in descending order
    logger.debug('Sorting Token Values...')
    sorted_msg = dict(sorted(msg.items(), key=lambda item: item[1], reverse=True))

    # Justify all values off of the maximum, with one leading space and four digits after decimal showing.
    max_coin_len = len(str(sorted(list(msg.values()), reverse=True)[0]).split('.')[0])
    price_justify = 1 + max_coin_len + 4

    # Convert to SOL
    converted_msg = convert_to_solana(sorted_msg, logger)

    logger.debug('Formatting Strings as Markdown for Discord...')
    out_str = 'An index of Solana DeFi Tokens measured in units of SOL\n'
    for k, v in converted_msg.items():
        fmt_k = '{:6s}'.format(k)
        trunc_usd = str('{:.4f}'.format(v.get('USD'))).rjust(price_justify)
        fmt_v_usd = '$ {} USD'.format(trunc_usd)
        spacer = '{:2s}→{:2s}'.format('', '')
        fmt_v_sol = '{:.4f} SOL'.format(v.get('SOL'))
        coin_price = dedent(f'''```{fmt_k}{fmt_v_usd}{spacer}{fmt_v_sol}```''')
        out_str += coin_price

    out_str += '\n_Real-time on-chain prices courtesy of pyth.network_'

    logger.debug(f'Formatted Pyth Message: {dedent(out_str)}')
    return dedent(out_str)


def convert_to_solana(prices: dict, logger):
    logger.debug('Converting Token Values to Units of SOL...')
    converted_prices = dict()
    sol_price = prices.get('SOL')
    for token, price in prices.items():
        converted_price = prices.get(token) / sol_price
        converted_prices[token] = {
            'USD': price,
            'SOL': converted_price
        }

    return converted_prices
