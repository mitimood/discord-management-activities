from main import configData
from discord.ext import commands
from datetime import datetime

from functions.c_functions import insert_atv_db


class poems(commands.Cog):
    @commands.Cog.listener()
    async def on_message(self, message):
        if configData["channels"]["poems_post"] == message.channel.id:
            for role in message.author.roles:
                if role.id == configData["roles"]["equipe_poem"]:
                    now = datetime.utcnow().timestamp()
                    insert_atv_db(message.author.id, now)


def setup(bot):
    bot.add_cog(poems(bot))
