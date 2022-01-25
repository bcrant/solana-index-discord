import pathlib
import os

tokens_path = os.path.join(
    pathlib.Path(__file__).parent.resolve(),
    'scripts/solana_tokens.txt'
)


class SolanaTokens:
    with open(tokens_path, 'r') as txt:
        tokens = list()
        for token in txt.read().splitlines():
            tokens.append(token.replace('\"', '').rstrip(','))
    BASE = tokens
    TOP_20 = {
        'SOL', 'LINK', 'GRT', 'REN',
        'RAY', 'INJ', 'MNGO', 'BAND',
        'FIDA', 'DFL', 'DIA', 'RAMP',
        'PRQ', 'FRONT', 'OOE', 'SLRS',
        'SNY', 'SLND', 'UPS', 'CYS',
        'SERUM', 'RIN'
    }
    EXTENDED = {
        'SOL', 'SRM', 'MSOL', 'RAY', 'MNGO', 'ATLAS', 'FIDA', 'AURY', 'IN', 'OXY', 'KIN', 'SAMO', 'SLIM',
        'JET', 'ORCA', 'STEP', 'TULIP', 'SLRS', 'LIKE', 'DXL', 'MAPS', 'RIN', 'PRISM', 'SNY', 'PORT', 'COPE', 'MER',
        'CYS', 'MEDIA', 'LIQ', 'FAB', 'IVN', 'CRP', 'SUNNY', 'SWARM', 'MOLA', 'SAIL', 'HOLY', 'KURO', 'CATO', 'GST',
        'GSAIL', 'ROPE', 'SLX', 'SOLAB', 'SOLA', 'NAXAR', 'ASH', 'FRIES', 'DATE', 'SOLAPE', 'STR', 'APEX', 'SOLUM',
        'SWOLE', 'GOFX', 'SOLPAD', 'INU', 'UPS', 'UXP', 'KITTY', 'NEKI', 'BASIS', 'SECO', 'RACEFI', 'BOP', 'ISOLA',
        'FTR', 'GRAPE', 'SHILL', 'WOOF', 'OXS', 'NINJA', 'PRT', 'SCNSOL', 'POLIS', 'DFL'
    }


class IpBanned:
    FALLBACK_MSG = {
        'SOL': 88.4050,
        'RAY': 3.3423,
        'SNY': 1.7772,
        'FIDA': 1.4817,
        'MNGO': 0.1495
    }
