import os
import pprint
import requests
from dotenv import load_dotenv
load_dotenv("../../.env", verbose=True)


def register_discord_slash_command():
    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = f"https://discord.com/api/v8/applications/{os.getenv('DISCORD_APP_ID')}/commands"

    json = {
        "name": "sol",
        "type": 1,
        "description": "Get Solana ecosystem DeFi token updates",
        "options": []
    }

    # For authorization, you can use either your bot token
    headers = {
        "Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"
    }

    r = requests.post(url, headers=headers, json=json)

    pprint.pprint(vars(r))


if __name__ == '__main__':
    register_discord_slash_command()
