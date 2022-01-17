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

    PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    signature = event['headers']["x-signature-ed25519"]
    timestamp = event['headers']["x-signature-timestamp"]
    body = event['body']

    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        body = json.loads(event['body'])
        if body["type"] == 1:
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
