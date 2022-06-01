import json
import os
import discord
from discord_slash import SlashCommand

# make available the config file as configData object
if os.path.exists((os.getcwd() + "/config.json")):
    with open("config.json") as f:
        configData = json.load(f)

# require all needed discord intents to be cached
Intents = discord.Intents()
Intents.members = True
Intents.guilds = True
Intents.emojis = True
Intents.guild_messages = True
Intents.guild_reactions = True
Intents.voice_states = True


# declare SlashCommands through the client
client = discord.ext.commands.Bot(command_prefix="!a", intents=Intents)

slash = SlashCommand(client, delete_from_unused_guilds=True, sync_commands=True)

for filename in os.listdir('./functions'):
    if filename.endswith('.py'):
        client.load_extension(f"functions.{filename[:-3]}")

for filename in os.listdir('./karaoke'):
    if filename.endswith('.py'):
        client.load_extension(f"karaoke.{filename[:-3]}")

for filename in os.listdir('./poems'):
    if filename.endswith('.py'):
        client.load_extension(f"poems.{filename[:-3]}")

for filename in os.listdir('./painting'):
    if filename.endswith('.py'):
        client.load_extension(f"painting.{filename[:-3]}")

from functions.a_functions import db_temp_CD

# Reply when the bot is ready
@client.event
async def on_ready():
    print("Ready!")
    db_temp_CD.truncate()


client.run(configData["token"])
