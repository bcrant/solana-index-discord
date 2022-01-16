import json
import os
from utils.environment import init_env
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PING_PONG = {"type": 1}
RESPONSE_TYPES = {
    "PONG": 1,
    "ACK_NO_SOURCE": 2,
    "MESSAGE_NO_SOURCE": 3,
    "MESSAGE_WITH_SOURCE": 4,
    "ACK_WITH_SOURCE": 5
}


def handler(event, context):
    """
    Query the Pyth price feed
    """
    logger = init_env()
    logger.info('RUNNING LAMBDA FUNCTION... inputs: ')
    # verify the signature
    try:
        verify_signature(event)
    except BadSignatureError as e:
        raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")

    # check if message is a ping
    body = event.get('body-json')
    if ping_pong(body):
        return PING_PONG

    # dummy return
    return {
        "type": RESPONSE_TYPES['MESSAGE_NO_SOURCE'],
        "data": {
            "tts": False,
            "content": "BEEP BOOP",
            "embeds": [],
            "allowed_mentions": []
        }
    }

    # return {
    #     "isBase64Encoded": "false",
    #     "statusCode": "200",
    #     "body": json.dumps({"data": "bleep boop"})
    # }


def verify_signature(event):
    raw_body = event.get("rawBody")
    auth_sig = event['params']['header'].get('x-signature-ed25519')
    auth_ts = event['params']['header'].get('x-signature-timestamp')

    message = auth_ts.encode() + raw_body.encode()
    verify_key = VerifyKey(bytes.fromhex(os.getenv('DISCORD_PUBLIC_KEY')))
    verify_key.verify(message, bytes.fromhex(auth_sig))  # raises an error if unequal


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


if os.getenv('AWS_EXECUTION_ENV') is None:
    handler({'params': {'header': {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}}}, {})
