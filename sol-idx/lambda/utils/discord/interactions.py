import json
import os
import requests
import traceback
from utils.pyth.pyth import get_pyth_discord_response
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from dotenv import load_dotenv
load_dotenv('../../../../.env', verbose=True)


def validate_discord_interaction(lambda_event, logger):
    headers = lambda_event.get('headers')
    # logger.info(f'Headers: {type(headers)} {headers}')

    signature = headers.get('x-signature-ed25519')
    # logger.info(f'Signature: {type(signature)} {signature}')

    timestamp = headers.get('x-signature-timestamp')
    # logger.info(f'Timestamp: {type(timestamp)} {timestamp}')

    raw_body = lambda_event.get('body')
    # logger.info(f'Raw Body: {type(raw_body)} {raw_body}')

    json_body = json.loads(raw_body)
    # logger.info(f'JSON Body: {type(json_body)} {json_body}')

    try:
        logger.info("Verifying that payloads match signature...")
        PUBLIC_KEY = os.getenv('DISCORD_PUBLIC_KEY')
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        # logger.info(f'Verify Key: {verify_key}')

        verify_payload_a = f'{timestamp}{raw_body}'.encode()
        # logger.info(f'Verify Payload A: {type(verify_payload_a)} {verify_payload_a}')

        verify_payload_b = bytes.fromhex(signature)
        # logger.info(f'Verify Payload B: {type(verify_payload_b)} {verify_payload_b}')

        is_verified = verify_key.verify(verify_payload_a, verify_payload_b)
        # logger.info(f'Verification Result: {bool(is_verified)} {type(is_verified)} {is_verified}')

        return is_verified, json_body

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
        respond_to_type_one(logger)

    if req_body.get('type') == 2:
        respond_to_type_two(req_body, logger)


def respond_to_type_one(logger):
    logger.info('Response "type" == 1. Returning Ping with Pong...')
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': json.dumps({'type': 1})
    }


def respond_to_type_two(req_body, logger):
    logger.info('Response "type" == 2. Returning message...')
    url = get_interaction_response_url(req_body, logger)
    msg_content = get_interaction_response_msg_pyth(logger)
    # msg_content = get_interaction_response_msg_markdown(logger)

    interaction_response = requests.post(url, json=resp_json)
    logger.info(f'Interaction Response: {interaction_response}')
    logger.info(f'Interaction Response: {interaction_response.content}')
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
        'body': json.dumps({
            'type': 4,
            'data': {
                'tts': False,
                'content': msg_content,
            }
        })
    }


def get_interaction_response_url(req_body, logger):
    logger.info('Building URL for Discord Interaction Response...')
    interaction_id = req_body.get('id')
    interaction_token = req_body.get('token')
    resp_url = f'https://discord.com/api/v8/interactions' \
               f'/{interaction_id}' \
               f'/{interaction_token}' \
               f'/callback'
    logger.info(f'Response URL: {resp_url}')
    return resp_url


def get_interaction_response_msg_pyth(logger):
    logger.info('Responding to Discord Interaction with Pyth price feed...')
    resp_msg = get_pyth_discord_response(logger)
    logger.info(f'Response Message: {resp_msg}')
    return resp_msg


def get_interaction_response_msg_markdown(logger):
    logger.info('Responding to Discord Interaction with a simple message...')
    resp_msg = ':fire: Im a little teapot'
    # resp_json = {
    #     "statusCode": 200,
    #     "type": 4,
    #     "data": {
    #         "tts": False,
    #         "content": msg,
    #     }
    # }
    logger.info(f'Response Message: {resp_msg}')
    return resp_msg
