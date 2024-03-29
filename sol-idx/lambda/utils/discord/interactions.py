import json
import os
import requests
import traceback
from utils.pyth.pyth import get_pyth_discord_response
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from dotenv import load_dotenv

load_dotenv("../../../../.env", verbose=True)


def respond_to_discord_interaction(lambda_event, logger):
    logger.info("Validating Discord Interaction....")
    validate_discord_interaction(lambda_event, logger)

    logger.info("Responding to Discord Interaction...")
    req_body = json.loads(lambda_event.get("jsonBody"))
    logger.debug(f"Request body: {type(req_body)} {req_body}")

    interaction_type = req_body.get("type")
    if interaction_type == 1:
        return respond_to_type_one(logger)
    if interaction_type == 2:
        return respond_to_type_two_deferred(req_body, logger)


def validate_discord_interaction(lambda_event, logger):
    headers = lambda_event.get("headers")
    logger.debug(f"Headers: {type(headers)} {headers}")

    signature = headers.get("x-signature-ed25519")
    logger.debug(f"Signature: {type(signature)} {signature}")

    timestamp = headers.get("x-signature-timestamp")
    logger.debug(f"Timestamp: {type(timestamp)} {timestamp}")

    raw_body = lambda_event.get("rawBody")
    logger.debug(f"Raw Body BEFORE: {type(raw_body)} {raw_body}")
    logger.debug(f"Raw Body BEFORE repr: {repr(raw_body)}")

    logger.debug("Verifying that payloads match signature...")
    PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY")
    logger.debug(f"PUBLIC KEY: {PUBLIC_KEY}")

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    logger.debug(f"Verify Key: {type(verify_key)}")

    # verify_payload_a = timestamp.encode() + decoded_raw_body
    verify_payload_a = f"{timestamp}{raw_body}".encode()
    logger.debug(f"Verify Payload A: {type(verify_payload_a)}")

    verify_payload_b = bytes.fromhex(signature)
    logger.debug(f"Verify Payload B: {type(verify_payload_b)}")

    try:
        verify_key.verify(verify_payload_a, verify_payload_b)

    except BadSignatureError as e:
        logger.error(f"Bad Signature Error: {e}")
        return {
            "isBase64Encoded": False,
            "statusCode": 401,
            "body": json.dumps({"error": "Bad Signature Error"}),
        }

    except BaseException as err:
        logger.error(f"Base Exception: {traceback.format_exc()} {err}")
        raise err

    finally:
        logger.debug("Completed Request Validation.")


def respond_to_type_one(logger):
    logger.info('Response "type" == 1. Returning Ping Pong....')
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": json.dumps({"type": 1}),
    }


def respond_to_type_two_deferred(req_body, logger):
    #
    # Reuse same Session
    #
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})

    #
    # POST | DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE
    #
    logger.info('Response "type" == 2. Deferring Channel Message...')
    defer_url = get_interaction_response_url(req_body, logger)
    defer_json = {
        "statusCode": 200,
        "type": 5,
    }
    defer_response = s.post(
        defer_url,
        json=defer_json,
    )
    logger.info(
        f"Interaction Response (Defer): {defer_response} {defer_response.content}"
    )

    #
    # PATCH | Edit Initial Response to Interaction
    #
    logger.info("Sending Deferred Channel Message...")
    hook_url = get_interaction_webhook_url(req_body, logger)
    hook_msg = get_interaction_response_msg_pyth(logger)
    hook_json = {"type": 3, "content": hook_msg}
    hook_response = s.patch(
        hook_url,
        json=hook_json,
    )
    logger.info(
        f"Interaction Response (Edit Initial Response): {hook_response} {hook_response.content}"
    )

    logger.debug(f"Finished responding to Discord Interaction...")
    logger.debug(f"Returning 200 to API Gateway...")
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
    }


def respond_to_type_two_sync(req_body, logger):
    logger.info('Response "type" == 2. Returning message...')
    url = get_interaction_response_url(req_body, logger)
    msg_content = get_interaction_response_msg_pyth(logger)

    resp_json = {
        "statusCode": 200,
        "type": 4,
        "data": {
            "content": json.dumps(msg_content),
        },
    }
    interaction_response = requests.post(
        url, json=resp_json, headers={"Content-Type": "application/json"}
    )
    logger.info(
        f"Interaction Response:  {interaction_response} {interaction_response.content}"
    )

    logger.debug(f"Finished responding to Discord Interaction...")
    logger.debug(f"Returning to 200 Api Gateway...")
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
    }


def get_interaction_response_url(req_body, logger):
    logger.debug("Building URL for Discord Interaction Response...")
    interaction_id = req_body.get("id")
    interaction_token = req_body.get("token")
    resp_url = (
        f"https://discord.com/api/v8/interactions"
        f"/{interaction_id}"
        f"/{interaction_token}"
        f"/callback"
    )
    logger.debug(f"Response URL: {resp_url}")
    return resp_url


def get_interaction_response_msg_pyth(logger):
    logger.info("Responding to Discord Interaction with Pyth price feed...")
    resp_msg = get_pyth_discord_response(logger)
    logger.debug(f"Response Message: {resp_msg}")
    return resp_msg


def get_interaction_webhook_url(req_body, logger):
    logger.debug("Building URL for Discord Interaction Response...")
    interaction_token = req_body.get("token")
    resp_url = (
        f"https://discord.com/api/v8/webhooks"
        f'/{os.getenv("DISCORD_APP_ID")}'
        f"/{interaction_token}"
        f"/messages"
        f"/@original"
    )

    logger.debug(f"Response URL: {resp_url}")
    return resp_url
