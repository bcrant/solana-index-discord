import os
from utils.discord.interactions import respond_to_discord_interaction
from utils.environment import init_env


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    logger.info(f'[EVENT]: {event}')
    logger.info(f'[CONTEXT]: {context}')

    respond_to_discord_interaction(event, logger)


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
