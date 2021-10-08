import asyncio

from functions.a_functions import db, guilds
from main import client, configData
from discord.ext import commands
from discord_slash import cog_ext


async def exclude_activity(id_reg):
    db.activitykaraoke.update_one({"_id": id_reg}, {"$set": {"available": {"state": False, "since": None}}})


class Karaoke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="eligos",
                       description="Chama a equipe que ajuda a organizar o karaoke",
                       guild_ids=guilds)
    async def _eligos(self, ctx):
        regs_in_karaoke = []
        regs_avl = []
        regs_avlID = []
        caps_p = []
        for mem in ctx.guild.get_channel(configData["channels"]["karaoke_voice"]).members:
            for role in mem.roles:
                if role.id == configData["roles"]["equipe_karaoke"]:
                    regs_in_karaoke.append(mem.mention)
        query = {"available.state": True}
        docs = db.activitykaraoke.find(query)
        for doc in docs:
            if ctx.guild.get_member(doc["_id"]):
                regs_avlID.append(doc["_id"])
                regs_avl.append(ctx.guild.get_member(doc["_id"]).mention)
        if regs_avl:
            if regs_in_karaoke:
                caps = ctx.guild.get_role(configData["roles"]["capitaes_karaoke"]).members
                for cap in caps:
                    await cap.send(
                        f"Pediram ajuda no karaoke, porém já tem alguns organizadores no karaoke {regs_in_karaoke}\n<#{configData['channels']['karaoke_voice']}>")
            call_reg_msg = await ctx.guild.get_channel(configData["channels"]["equipe_karaoke"]).send(
                f"<#{configData['channels']['karaoke_voice']}> Karaoke precisando de ajuda {set(regs_avl)}")
            await ctx.send("Já já vai vir alguem para ajudar")
            await call_reg_msg.add_reaction('✅')
            regs_reacted = []

            def check(reaction, user):

                if reaction.message == call_reg_msg:
                    for avl_id in regs_avlID:
                        if avl_id == user.id:
                            regs_reacted.append(user.id)
                return len(regs_avl) == len(regs_reacted)

            try:
                await client.wait_for("reaction_add", timeout=300, check=check)
                await call_reg_msg.delete()
            except asyncio.TimeoutError:
                for id in regs_avlID:
                    if id not in regs_reacted:
                        await exclude_activity(id)
                await call_reg_msg.delete()
        elif regs_in_karaoke:
            caps = ctx.guild.get_role(configData["roles"]["capitaes_karaoke"]).members
            for cap in caps:
                await cap.send(
                    f"Pediram ajuda no karaoke, mas não tem ninguém disponivel e tem alguns organizadores no karaoke {regs_in_karaoke}\n<#{configData['channels']['karaoke_voice']}>")
                caps_p.append(cap.mention)
                await ctx.send("Já já vai vir alguem para ajudar")
        else:
            caps = ctx.guild.get_role(configData["roles"]["capitaes_karaoke"]).members
            for cap in caps:
                await cap.send(
                    f"Pediram ajuda no karaoke, mas não tem ninguém disponivel\n<#{configData['channels']['karaoke_voice']}>")
            await ctx.send("Já já vai vir alguem para ajudar")


def setup(bot):
    bot.add_cog(Karaoke(bot))
