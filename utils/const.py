class SolanaTokens:
    with open('./solana_tokens.txt', 'r') as txt:
        tokens = list()
        for token in txt.read().splitlines():
            tokens.append(token.replace('\"', '').rstrip(','))
    BASE = tokens
    TOP = {
        'SOL',
        'RAY',
        'SRM',
        'MNGO',
        'ATLAS',
        'AURY',
        'FIDA',
        'SAMO',
        'OXY',
        'SLRS',
        'STEP',
    }
