import os
import sys
from utils.discord.interactions import validate_discord_interaction
from utils.environment import init_env
print('os.getcwd: ', os.getcwd())
print('sys.path: ', sys.path)
print('os.path.join(os.path.dirname(__file__)): ', os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append('./utils/')
print('sys.path: ', sys.path)


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    logger.info(f'[EVENT]: {event}')
    logger.info(f'[CONTEXT]: {context}')

    validate_discord_interaction(event, logger)


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
