import os
from utils.discord.interactions import validate_discord_interaction
from utils.environment import init_env
from utils.pyth.pyth import get_pyth_price_feed


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    logger.info(f'[EVENT]: {event}')
    logger.info(f'[CONTEXT]: {context}')

    discord_msg = get_pyth_price_feed()

    validate_discord_interaction(event, discord_msg, logger)


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
