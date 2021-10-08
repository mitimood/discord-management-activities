from datetime import datetime

from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission

from functions.a_functions import guilds, db
from main import configData
from discord.ext import commands
from discord_slash import cog_ext


class cmd_off(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Display user as unavailable and saves a time stamp of the available duration in mongodb
    @cog_ext.cog_slash(name="off",
                       description="Poe em estado de ocupado",
                       guild_ids=guilds,
                       permissions={
                           configData["channels"]["guild"]: [
                               create_permission(configData["roles"]["equipe_karaoke"], SlashCommandPermissionType.ROLE,
                                                 True),
                           ]
                       },
                       default_permission=False
                       )
    async def _ocupado(self, ctx):
        id_author = ctx.author.id
        query = {"_id": id_author}
        stamp_time = datetime.utcnow().timestamp()
        try:
            doc = db.activitykaraoke.find_one(query)
            if doc and "available" in doc and doc["available"]["state"]:
                action_time = datetime.fromtimestamp(stamp_time) - datetime.fromtimestamp(doc["available"]["since"])
                insert = {"$set": {"_id": id_author, "last": stamp_time, "available": {"state": False, "since": None}},
                          "$push": {"time_available": {"When": stamp_time, "Total": action_time.total_seconds()}}}
                db.activitykaraoke.update_many(query, insert)
                await ctx.send("Você agora está no modo ocupado")
            else:
                await ctx.send("Você precisa ficar disponivel primeiro para poder ficar no ocupado")

        except():
            print("Problema ao registrar na mongodb")


def setup(bot):
    bot.add_cog(cmd_off(bot))
