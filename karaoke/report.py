from datetime import datetime, timedelta
import discord
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option, create_permission
from functions.a_functions import db, _add_field, guilds
from main import client, configData
from discord.ext import commands


class report(commands.Cog):

    @cog_ext.cog_slash(name="reporteligos",
                       description="Exibe a contagem de pontos dos eligos",
                       guild_ids=guilds,
                       default_permission=False,
                       options=[
                           create_option(
                               name="days",
                               description="Indica a quantidade de tempo para o relatorio analisar",
                               option_type=4,
                               required=True
                           )
                       ],
                       permissions={
                           configData["channels"]["guild"]: [
                               create_permission(configData["roles"]["capitaes_karaoke"], 1, True),
                           ]
                       })
    async def _report(self, ctx, days: int):
        id_array = []
        for role in ctx.guild.roles:
            if role.id == configData["roles"]["equipe_karaoke"]:
                for organizer in role.members:
                    id_array.append(organizer.id)
        com_time = datetime.utcnow() - timedelta(days=days)
        query = {"$and": [{"_id": {"$in": id_array}}, {'Activities.time': {"$gte": com_time.timestamp()}}]}
        docs_act = db.activitykaraoke.find(query)
        regs_act = {}
        for doc in docs_act:
            txt = 0
            voice = 0
            atvs = 0
            for act in doc["Activities"]:
                if act["time"] >= com_time.timestamp():
                    atvs += 1
                    voice = voice + act["voice"]
                    txt = txt + act["chat"]
            regs_act[doc["_id"]] = {"activities": atvs, "voice": voice, "Text": txt}

        query = {"$and": [{"_id": {"$in": id_array}}, {'time_available.When': {"$gte": com_time.timestamp()}}]}
        time_docs = db.activitykaraoke.find(query)
        regs_time = {}
        for doc in time_docs:
            total = 0
            for time_doc in doc["time_available"]:
                if time_doc["When"] >= com_time.timestamp():
                    total += time_doc["Total"]
            regs_time[doc["_id"]] = {"total": total}
        res = {}
        for id in regs_time:
            if id in regs_act:
                res[id] = {**regs_time[id], **regs_act[id]}
            else:
                res[id] = regs_time[id]
        for id in regs_act:
            if id in regs_time:
                res[id] = {**regs_time[id], **regs_act[id]}
            else:
                res[id] = regs_act[id]

        emb = discord.Embed().set_image(
            url="https://media.discordapp.net/attachments/750576681281912873/853674056691220530/20210612_154458_1.gif").set_thumbnail(
            url="https://media.baamboozle.com/uploads/images/291632/1619760072_114659_gif-url.gif").set_author(
            name=ctx.author.name,
            icon_url=f"https://cdn.discordapp.com/avatars/{ctx.author.id}/{ctx.author.avatar}.png")
        emb.title = f"Relatório de {days} dias"
        emb.color = 0x990f44
        emb.add_field(value="ㅤ", name="ㅤ")
        emb.timestamp = datetime.utcnow()
        inatives = set(id_array) ^ set(res.keys())
        for ind_Res in res:
            xp = 0
            if "total" in res[ind_Res]:
                xp += res[ind_Res]["total"] * configData["xp_equipe_karaoke"]["available_time"]
                duration = datetime.fromtimestamp(res[ind_Res]["total"])
                value = "{:.2f} pontos ".format(float(xp))
            if "activities" in res[ind_Res]:
                xp += configData["xp_equipe_karaoke"]["activities"] * res[ind_Res]["activities"]
                xp += configData["xp_equipe_karaoke"]["voice"] * res[ind_Res]["voice"]
                xp += configData["xp_equipe_karaoke"]["Text"] * res[ind_Res]["Text"]
                value = "{:0.2f} pontos".format(float(xp))
            user = client.get_user(ind_Res)
            if xp:
                emb = _add_field(f"{user.display_name} {user.id}", emb, value)
            else:
                inatives.add(ind_Res)
        for inative in inatives:
            inative = client.get_user(inative)
            emb = _add_field(inative.display_name, emb)
        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(report(bot))
