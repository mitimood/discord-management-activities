from tinydb import table

from functions.a_functions import db_temp_users
from main import configData
from discord.ext import commands


class Karaoke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, oldstate, newstate):
        if oldstate.self_mute != newstate.self_mute \
                and member.guild.get_role(configData["roles"]["equipe_karaoke"]) in member.roles \
                and newstate.channel == member.guild.get_channel(configData["channels"]["karaoke_voice"]):
            try:
                if db_temp_users.contains(doc_id=member.id):
                    doc = db_temp_users.get(doc_id=member.id)
                    doc["voice"] = doc["voice"] + 1
                    db_temp_users.update(doc, doc_ids=[member.id])
                else:
                    try:
                        insert = {"_id": member.id, "voice": 1, "chat": 0, "lastMsg": None}
                        db_temp_users.insert(table.Document(insert, doc_id=member.id))
                    except:
                        print("Um erro ocorreu ao registrar na db interna")
            except:
                print("Um erro ocorreu ao registrar atividade")


def setup(bot):
    bot.add_cog(Karaoke(bot))
