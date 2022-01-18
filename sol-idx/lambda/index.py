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

    headers = event.get('headers')
    logger.info(f'Headers: {type(headers)} {headers}')

    signature = event.get('signature')
    logger.info(f'Signature: {type(signature)} {signature}')

    timestamp = event.get('timestamp')
    logger.info(f'Timestamp: {type(timestamp)} {timestamp}')

    jsonBody = event.get('jsonBody')
    logger.info(f'jsonBody: {type(jsonBody)} {jsonBody}')

    rawBody = event.get('rawBody')
    logger.info(f'rawBody: {type(rawBody)} {rawBody}')

    verify_payload_a = f'{timestamp}{rawBody}'.encode()
    verify_payload_b = bytes.fromhex(signature)
    logger.info(f'Verify Payload A: {type(verify_payload_a)} {verify_payload_a}')
    logger.info(f'Verify Payload B: {type(verify_payload_b)} {verify_payload_b}')

    try:
        verify_result = verify_key.verify(verify_payload_a, verify_payload_b)
        logger.info(f'Verify Result: {verify_result}')

        if jsonBody.get('type') == 1:
            v = validate_response(jsonBody)
            logger.info(f'Ping Pong Validation Response: {v}')
            return logger.info('READY FOR ACTION')

    except BadSignatureError as e:
        logger.error(f'Bad Signature Error: {e}')
        return {
            'statusCode': 401,
            'body': json.dumps({'err': 'Bad Signature Error'})
        }


def validate_response(req_body):

    interaction_id = req_body.get('id')
    interaction_token = req_body.get('token')

    ping_pong_url = f'https://discord.com/api/v8/interactions' \
        f'/{interaction_id}' \
        f'/{interaction_token}' \
        f'/callback'

    ping_pong_payload = {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }

    ping_pong_req = requests.post(ping_pong_url, json=ping_pong_payload)

    return ping_pong_req


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({}, {})
