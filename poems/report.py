from datetime import datetime

from discord_slash.model import SlashCommandPermissionType
from discord_slash.utils.manage_commands import create_permission


from functions.a_functions import guilds
from main import configData
from discord.ext import commands
from discord_slash import cog_ext
import pytz

from functions.c_functions import get_atv_db


class report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="reportVagantes",
                       description="Poe em estado de disponivel",
                       guild_ids=guilds,
                       default_permission=False,
                       permissions={
                           configData["channels"]["guild"]: [
                               create_permission(configData["roles"]["capitaes_poem"], SlashCommandPermissionType.ROLE, True)]
                       }
                       )
    async def _report(self, ctx):
        members_id = []
        members = ctx.guild.get_role(configData["roles"]["equipe_poem"]).members
        members_on_id = []
        all_mem = []
        for member in members:
            members_id.append(member.id)

        docs = get_atv_db(members_id)
        report_msg = "**Relatorio de atividade**"
        for doc in docs:
            all_mem.append((doc["_id"], doc["last_poem"]))

        memb = sorted(all_mem, key=lambda date: date[1])
        timezone = pytz.timezone("America/Sao_Paulo")
        for tup in memb:
            date = datetime.fromtimestamp(tup[1]).astimezone(timezone).strftime("%d/%m/%Y")
            report_msg = report_msg + "\n" + date + " --- " + f"<@{tup[0]}> {tup[0]}"
            if len(report_msg) >= 1800:
                await ctx.author.send(report_msg)
                report_msg = ""
            members_on_id.append(tup[0])

        await ctx.author.send(report_msg)
        members_off_id = set(members_on_id) ^ set(members_id)
        await ctx.author.send("Sem registro " + members_off_id.__str__())
        await ctx.send("Enviado!")


def setup(bot):
    bot.add_cog(report(bot))
