import asyncio

from datetime import datetime, timedelta
from tinydb import Query

from functions.a_functions import db_temp_CD, db
from main import client, configData
from discord.ext import commands


class Karaoke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def exclude_activity(self, id):
        stamp_time = datetime.utcnow().timestamp()
        insert = {"$set": {"_id": id, "available": {"state": False, "since": None}},
                  "$push": {"time_available": {"When": stamp_time, "Total": -1000}}}
        await db.activitykaraoke.update_many({"_id": id}, insert)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, oldstate, newstate):
        if newstate.channel and newstate.channel.id == configData["channels"]["karaoke_voice"] \
                and len(newstate.channel.members) >= configData["max_call"] and newstate.channel != oldstate.channel:
            regs_k = []
            regs_av = []
            caps_p = []
            regs_avId = []
            if db_temp_CD.contains(Query()["karaoke_alert_size"].exists()):
                cd_doc = db_temp_CD.search(Query()["karaoke_alert_size"].exists())
                cd_time = timedelta(minutes=30) + datetime.fromtimestamp(cd_doc[0]["karaoke_alert_size"])
                if datetime.utcnow() < cd_time:
                    return
                else:
                    db_temp_CD.update({"karaoke_alert_size": datetime.utcnow().timestamp()},
                                      Query()["karaoke_alert_size"].exists())
            else:
                db_temp_CD.insert({"karaoke_alert_size": datetime.utcnow().timestamp()})
            for mem in newstate.channel.members:
                for role in mem.roles:
                    if role.id == configData["roles"]["equipe_karaoke"]:
                        regs_k.append(mem)
            if not regs_k:
                x = {"available.state": True}
                doc = db.activitykaraoke.find(x)
                for x in doc:
                    regs_av.append(member.guild.get_member(x["_id"]).mention)
                    regs_avId.append(x["_id"])
                if regs_av:
                    call_reg_msg = await member.guild.get_channel(configData["channels"]["equipe_karaoke"]).send(
                        f"<#{configData['channels']['karaoke_voice']}> Karaoke precisando de ajuda {set(regs_av)}")
                    await call_reg_msg.add_reaction('✅')
                    regs_reacted = []

                    def check(reaction, user):

                        if reaction.message == call_reg_msg:
                            for avl_id in regs_avId:
                                if avl_id == user.id:
                                    regs_reacted.append(user.id)
                        return len(regs_avId) == len(regs_reacted)

                    try:
                        await client.wait_for("reaction_add", timeout=300, check=check)
                        await call_reg_msg.delete()
                    except asyncio.TimeoutError:
                        for id in regs_avId:
                            if id not in regs_reacted:
                                await self.exclude_activity(id)
                        await call_reg_msg.delete()
                else:
                    caps = member.guild.get_role(configData["roles"]["capitaes_karaoke"]).members
                    for cap in caps:
                        caps_p.append(cap.mention)
                    await member.guild.get_channel(configData["channels"]["equipe_karaoke"]).send(
                        f"{set(caps_p)} karaoke enchendo, nenhum responsavel na sala, e ninguem disponivel, <#{configData['channels']['karaoke_voice']}>")


def setup(bot):
    bot.add_cog(Karaoke(bot))


