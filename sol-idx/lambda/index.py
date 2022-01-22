import os
from utils.discord.interactions import validate_discord_interaction, respond_to_discord_interaction
from utils.environment import init_env


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    logger.info(f'[EVENT]: {event}')
    logger.info(f'[CONTEXT]: {context}')

    is_verified, json_body = validate_discord_interaction(event, logger)
    if bool(is_verified):
        respond_to_discord_interaction(json_body, logger)


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
