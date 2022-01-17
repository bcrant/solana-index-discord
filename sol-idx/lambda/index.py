import json
import os
import pprint
import requests
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
    logger.info(f'Verify Key: {verify_key}')
    #
    # headers = event.get('headers')
    # logger.info(f'Headers: {headers}')

    signature = event.get('signature')
    logger.info(f'Signature: {signature}')
    timestamp = event.get('timestamp')
    logger.info(f'Timestamp: {timestamp}')
    body = event.get('jsonBody')
    logger.info(f'Body: {type(body)} {body}')

    verify_payload = f'{timestamp}{body}'.encode()
    logger.info(f'Verify Payload: {type(verify_payload)} {verify_payload}')

    try:
        verify_result = verify_key.verify(verify_payload, bytes.fromhex(signature))
        logger.info(f'Verify Result: {verify_result}')

        if body.get('type') == 1:
            v = validate_response(body)
            return logger.info(f'Validation Response: {v.content}')

    except BadSignatureError as e:
        logger.error(f'Bad Signature Error: {e}')
        return {
            'statusCode': 401,
            'body': json.dumps({'err': 'Bad Signature Error'})
        }


def validate_response(req_body):

    interaction_id = req_body.get('id')
    interaction_token = req_body.get('token')

    url = f'https://discord.com/api/v8/interactions' \
          f'/{interaction_id}' \
          f'/{interaction_token}' \
          f'/callback'
    # response = json.dumps({
    #     'statusCode': 200,
    #     'type': 1,
    # })
    response = {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
    r = requests.post(url, json=response)

    return r


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
