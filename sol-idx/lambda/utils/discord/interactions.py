import json
import os
import requests
import traceback
from utils.pyth.pyth import get_pyth_discord_response
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from dotenv import load_dotenv
load_dotenv('../../../../.env', verbose=True)


def respond_to_discord_interaction(lambda_event, logger):
    logger.info('Responding to Discord Interaction...')

    req_body = json.loads(lambda_event.get('body'))
    logger.info(f'Request body: {type(req_body)} {req_body}')

    if req_body is not None:
        interaction_type = req_body.get('type')
        if interaction_type == 1:
            respond_to_type_one(lambda_event, logger)
        if interaction_type == 2:
            respond_to_type_two(req_body, logger)
    else:
        logger.error(f'Lambda Event has no body or dot get did not work: {lambda_event}')


def validate_discord_interaction(lambda_event, logger):
    headers = lambda_event.get('headers')
    # logger.info(f'Headers: {type(headers)} {headers}')

    signature = headers.get('x-signature-ed25519')
    # logger.info(f'Signature: {type(signature)} {signature}')

    timestamp = headers.get('x-signature-timestamp')
    # logger.info(f'Timestamp: {type(timestamp)} {timestamp}')

    raw_body = lambda_event.get('body')
    # logger.info(f'Raw Body: {type(raw_body)} {raw_body}')

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
        logger.info(f'Verification Result: {bool(is_verified)}')

        if bool(is_verified):
            return {
                'isBase64Encoded': False,
                'statusCode': 200,
                'body': json.dumps({'type': 1})
            }
        else:
            logger.error(f'Problem validating Discord Interaction.')

    except BadSignatureError as e:
        logger.error(f'Bad Signature Error: {e}')
        return {
            'statusCode': 401,
            'body': json.dumps({'err': 'Bad Signature Error'})
        }

    except BaseException as err:
        logger.error(f'{traceback.format_exc()} {err}')


def respond_to_type_one(lambda_event, logger):
    logger.info('Response "type" == 1. Validating Discord Interaction....')
    validate_discord_interaction(lambda_event, logger)


def respond_to_type_two(req_body, logger):
    logger.info('Response "type" == 2. Returning message...')
    url = get_interaction_response_url(req_body, logger)
    # msg_content = get_interaction_response_msg_pyth(logger)
    # msg_content = get_interaction_response_msg_markdown(logger)
    # url = get_webhook_post_interaction_url(req_body, logger)

    # resp_json = {
    #     'statusCode': 200,
    #     'type': 4,
    #     'data': {
    #         'content': json.dumps(msg_content),
    #     }
    # }

    resp_json = {
        'statusCode': 200,
        'type': 5,
    }

    #
    # POST
    #
    interaction_response = requests.post(url, json=resp_json)
    logger.info(f'Interaction Response: {interaction_response}')
    logger.info(f'Interaction Response: {interaction_response.content}')

    #
    # PATCH
    #
    hook_url = get_interaction_webhook_url(req_body, logger)
    hook_msg = get_interaction_response_msg_pyth(logger)
    hook_json = {
        'type': 3,
        'content': json.dumps(hook_msg)
    }
    webhook_interaction_response = requests.patch(
        hook_url,
        headers={'content-type': 'application/json'},
        json=hook_json
    )
    logger.info(f'Webhook Interaction Response: {webhook_interaction_response}')
    logger.info(f'Webhook Interaction Response: {webhook_interaction_response.content}')

    logger.info(f'Finished responding to Discord Interaction...')
    logger.info(f'Returning to 200 Api Gateway...')
    return {
        'isBase64Encoded': False,
        'statusCode': 200,
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
    logger.info(f'Response Message: {resp_msg}')
    return resp_msg


def get_interaction_webhook_url(req_body, logger):
    logger.info('Building URL for Discord Interaction Response...')
    interaction_token = req_body.get('token')
    resp_url = f'https://discord.com/api/v8/webhooks' \
               f'/{os.getenv("DISCORD_APP_ID")}' \
               f'/{interaction_token}' \
               f'/messages' \
               f'/@original'

    logger.info(f'Response URL: {resp_url}')
    return resp_url

