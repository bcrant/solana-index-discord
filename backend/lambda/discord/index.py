import os
from utils.environment import init_env


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    logger.info(f'Input EVENT: {event}')
    logger.info(f'Input CONTEXT: {context}')

    return


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
