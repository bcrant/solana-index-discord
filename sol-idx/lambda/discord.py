import json
import os
import pprint
import requests
from dotenv import load_dotenv
load_dotenv("../../.env", verbose=True)


def register_discord_slash_command():
    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = f"https://discord.com/api/v8" \
          f"/applications/{os.getenv('DISCORD_APP_ID')}" \
          f"/guilds/{os.getenv('DISCORD_GUILD_ID')}" \
          f"/commands"
    print(url)

    req_json = {
        "name": "sol_train",
        "type": 1,
        "description": "Get Solana ecosystem DeFi token updates",
        "guild_id": os.getenv('DISCORD_GUILD_ID'),
    }

    # For authorization, you can use either your bot token
    headers = {
        "Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"
    }

    r = requests.post(url, headers=headers, json=req_json)
    print(r)
    pprint.pprint(r.text)


if __name__ == '__main__':
    register_discord_slash_command()
