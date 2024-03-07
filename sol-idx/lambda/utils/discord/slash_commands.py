import json
import os
import pprint
import requests
from dotenv import load_dotenv

load_dotenv("../../../../.env", verbose=True)


#
# Discord > Slash Commands
# A series of helper functions for quickly Listing, Registering, and Deleting application commands.
#


def register_discord_slash_command_global():
    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = (
        f"https://discord.com/api/v8"
        f"/applications/{os.getenv('DISCORD_APP_ID')}"
        f"/commands"
    )
    print(url)

    req_json = {
        "name": "sol",
        "type": 1,
        "description": "Get Solana ecosystem DeFi token updates",
    }

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    r = requests.post(url, headers=headers, json=req_json)
    print(r)
    pprint.pprint(json.loads(r.text))


def register_discord_slash_command_guild():
    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = (
        f"https://discord.com/api/v8"
        f"/applications/{os.getenv('DISCORD_APP_ID')}"
        f"/guilds/{os.getenv('DISCORD_GUILD_ID')}"
        f"/commands"
    )
    print(url)

    req_json = {
        "name": "sol",
        "type": 1,
        "description": "Get Solana ecosystem DeFi token updates",
        "guild_id": os.getenv("DISCORD_GUILD_ID"),
    }

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    r = requests.post(url, headers=headers, json=req_json)
    print(r)
    pprint.pprint(json.loads(r.text))


def list_discord_slash_commands_global():
    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = (
        f"https://discord.com/api/v8"
        f"/applications/{os.getenv('DISCORD_APP_ID')}"
        f"/commands"
    )
    print(url)

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    r = requests.get(url, headers=headers)
    print(r)
    pprint.pprint(json.loads(r.text))


def list_discord_slash_commands_guild():
    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = (
        f"https://discord.com/api/v8"
        f"/applications/{os.getenv('DISCORD_APP_ID')}"
        f"/guilds/{os.getenv('DISCORD_GUILD_ID')}"
        f"/commands"
    )
    print(url)

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    r = requests.get(url, headers=headers)
    print(r)
    pprint.pprint(json.loads(r.text))


def delete_discord_slash_command_global(command_id):

    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = (
        f"https://discord.com/api/v8"
        f"/applications/{os.getenv('DISCORD_APP_ID')}"
        f"/commands/{command_id}"
    )
    print(url)

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    r = requests.delete(url, headers=headers)
    # Returns 204 No Content on success.
    print(r)


def delete_discord_slash_command_guild(command_id):

    # This is an example CHAT_INPUT or Slash Command, with a type of 1
    url = (
        f"https://discord.com/api/v8"
        f"/applications/{os.getenv('DISCORD_APP_ID')}"
        f"/guilds/{os.getenv('DISCORD_GUILD_ID')}"
        f"/commands/{command_id}"
    )
    print(url)

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    r = requests.delete(url, headers=headers)
    # Returns 204 No Content on success.
    print(r)


if __name__ == "__main__":
    #
    # GLOBAL
    #
    list_discord_slash_commands_global()
    # register_discord_slash_command_global()
    # delete_discord_slash_command_global('932448201674461195')

    #
    # GUILD
    #
    # list_discord_slash_commands_guild()
    # register_discord_slash_command_guild()
    # delete_discord_slash_command_guild('932448201674461195')
