import json
import os
import requests
import traceback
from ..pyth.pyth import get_pyth_price_feed
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from dotenv import load_dotenv
load_dotenv('../../../../.env', verbose=True)


def validate_discord_interaction(lambda_event, logger):
    headers = lambda_event.get('headers')
    logger.info(f'Headers: {type(headers)} {headers}')

    signature = headers.get('x-signature-ed25519')
    logger.info(f'Signature: {type(signature)} {signature}')

    timestamp = headers.get('x-signature-timestamp')
    logger.info(f'Timestamp: {type(timestamp)} {timestamp}')

    raw_body = lambda_event.get('body')
    logger.info(f'Raw Body: {type(raw_body)} {raw_body}')

    json_body = json.loads(raw_body)
    logger.info(f'JSON Body: {type(json_body)} {json_body}')

    try:
        logger.info("Verifying that payloads match signature...")
        PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        logger.info(f'Verify Key: {verify_key}')

        verify_payload_a = f'{timestamp}{raw_body}'.encode()
        logger.info(f'Verify Payload A: {type(verify_payload_a)} {verify_payload_a}')

        verify_payload_b = bytes.fromhex(signature)
        logger.info(f'Verify Payload B: {type(verify_payload_b)} {verify_payload_b}')

        is_verified = verify_key.verify(verify_payload_a, verify_payload_b)
        logger.info(f'Verification Result: {bool(is_verified)} {type(is_verified)} {is_verified}')

        if bool(is_verified):
            respond_to_discord_interaction(json_body, logger)

    except BadSignatureError as e:
        logger.error(f'Bad Signature Error: {e}')
        return {
            'statusCode': 401,
            'body': json.dumps({'err': 'Bad Signature Error'})
        }

    except BaseException as err:
        logger.error(f'{traceback.format_exc()} {err}')


def respond_to_discord_interaction(req_body, logger):
    logger.info('Responding to Discord Interaction...')

    if req_body.get('type') == 1:
        logger.info('Response "type" == 1. Returning Ping with Pong...')
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 1})
        }

    if req_body.get('type') == 2:
        logger.info('Response "type" == 2. Returning message...')
        return_message_to_discord_interaction(req_body, logger)


def return_message_to_discord_interaction(req_body, logger):

    logger.info('Responding to Discord Interaction with a simple message...')
    interaction_id = req_body.get('id')
    interaction_token = req_body.get('token')

    resp_url = f'https://discord.com/api/v8/interactions' \
               f'/{interaction_id}' \
               f'/{interaction_token}' \
               f'/callback'
    logger.info(f'Response URL: {resp_url}')

    msg = get_pyth_price_feed()

    resp_json = {
        "type": 4,
        "data": {
            "content": json.dumps(msg),
        }
    }
    logger.info(f'Response JSON: {resp_json}')

    interaction_response = requests.post(resp_url, json=resp_json)
    logger.info(f'Interaction Response: {interaction_response}')

    return {
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }
