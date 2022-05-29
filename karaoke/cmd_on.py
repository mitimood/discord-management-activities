from datetime import datetime

from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission


from functions.a_functions import db, guilds
from main import configData
from discord.ext import commands
from discord_slash import cog_ext


class available(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="on",
                       description="Poe em estado de disponivel",
                       guild_ids=guilds,
                       )
    async def _disponivel(self, ctx):  # Defines a new "context" (ctx) command called "ping."
        id_author = ctx.author.id
        query = {"_id": id_author}
        stamp_time = datetime.utcnow().timestamp()

        def days_hours_minutes(td):
            return td.days, td.seconds // 3600, (td.seconds // 60) % 60

        doc = db.activitykaraoke.find_one(query)
        if doc and "available" in doc and doc["available"]["state"]:
            date_started = datetime.utcnow() - datetime.fromtimestamp(doc["available"]["since"])
            date_days, date_hours, date_minutes = days_hours_minutes(date_started)
            await ctx.send(f"Você já esta disponivel, a {date_days}d {date_hours}h {date_minutes}m")
        else:
            insert = {"$set": {"_id": id_author, "available": {"state": True, "since": stamp_time}}}
            db.activitykaraoke.update_many(query, insert, upsert=True)
            await ctx.send("Você agora esta disponivel")



def setup(bot):
    bot.add_cog(available(bot))