class SolanaTokens:
    with open('../../../scripts/solana_tokens.txt', 'r') as txt:
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
    EXTENDED = {
        'SOL', 'SRM', 'MSOL', 'RAY', 'MNGO', 'ATLAS', 'FIDA', 'AURY', 'IN', 'OXY', 'KIN', 'SAMO', 'SLIM',
        'JET', 'ORCA', 'STEP', 'TULIP', 'SLRS', 'LIKE', 'DXL', 'MAPS', 'RIN', 'PRISM', 'SNY', 'PORT', 'COPE', 'MER',
        'CYS', 'MEDIA', 'LIQ', 'FAB', 'IVN', 'CRP', 'SUNNY', 'SWARM', 'MOLA', 'SAIL', 'HOLY', 'KURO', 'CATO', 'GST',
        'GSAIL', 'ROPE', 'SLX', 'SOLAB', 'SOLA', 'NAXAR', 'ASH', 'FRIES', 'DATE', 'SOLAPE', 'STR', 'APEX', 'SOLUM',
        'SWOLE', 'GOFX', 'SOLPAD', 'INU', 'UPS', 'UXP', 'KITTY', 'NEKI', 'BASIS', 'SECO', 'RACEFI', 'BOP', 'ISOLA',
        'FTR', 'GRAPE', 'SHILL', 'WOOF', 'OXS', 'NINJA', 'PRT', 'SCNSOL', 'POLIS', 'DFL'
    }
    TOP_20 = {
        'SOL', 'LINK', 'GRT', 'REN',
        'RAY', 'INJ', 'MNGO', 'BAND',
        'FIDA', 'DFL', 'DIA', 'RAMP',
        'PRQ', 'FRONT', 'OOE', 'SLRS',
        'SNY', 'SLND', 'UPS', 'CYS',
    }
