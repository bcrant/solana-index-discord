import json
import os
import pprint
from dotenv import load_dotenv
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from utils.environment import init_env
load_dotenv('../../.env', verbose=True)


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    logger.info(f'[EVENT]: {event}')
    logger.info(f'[CONTEXT]: {context}')

    # return {
    #     'statusCode': 200,
    #     'body': json.dumps({'type': 1})
    # }

    PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = event.get('signature')
    timestamp = event.get('timestamp')
    body = event.get('jsonBody')

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        body_json = json.loads(body)
        if body_json.get('type') == 1:
            return {
                'statusCode': 200,
                'body': json.dumps({'type': 1})
            }
    except BadSignatureError as e:
        return {
            'statusCode': 401,
            'body': json.dumps("Bad Signature")
        }


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
