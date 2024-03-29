import os
from utils.discord.interactions import respond_to_discord_interaction
from utils.environment import init_env


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info("RUNNING LAMBDA FUNCTION... inputs: ")
    logger.debug(f"[EVENT]: {event}")
    logger.debug(f"[CONTEXT]: {context}")

    response = respond_to_discord_interaction(event, logger)
    return response


if os.getenv("AWS_EXECUTION_ENV") is None:
    handler({}, {})
