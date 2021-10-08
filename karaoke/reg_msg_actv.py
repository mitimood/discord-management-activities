from datetime import datetime, timedelta
from tinydb import table

from functions.a_functions import db_temp_users
from main import configData
from discord.ext import commands


class Karaoke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        if message.channel == message.guild.get_channel(configData["channels"]["karaoke_chat"]) \
                and message.author.voice \
                and message.author.voice.channel == message.guild.get_channel(configData["channels"]["karaoke_voice"]) \
                and message.guild.get_role(configData["roles"]["equipe_karaoke"]) in message.author.roles:
            try:
                doc_id = message.author.id
                if db_temp_users.contains(doc_id=doc_id):
                    doc = db_temp_users.get(doc_id=doc_id)
                    if not doc["lastMsg"]:
                        comp_date = datetime.utcnow()
                    else:
                        comp_date = datetime.fromtimestamp(doc["lastMsg"])
                        comp_date = comp_date + timedelta(seconds=20)
                    if datetime.utcnow() >= comp_date:
                        doc["chat"] = doc["chat"] + 1
                        doc["lastMsg"] = datetime.utcnow().timestamp()
                        db_temp_users.update(doc, doc_ids=[doc_id])
                else:
                    try:
                        insert = {"_id": message.author.id, "voice": 0, "chat": 1,
                                  "lastMsg": datetime.utcnow().timestamp()}
                        db_temp_users.insert(table.Document(insert, doc_id=doc_id))
                    except:
                        print("Erro ao inserir atividade de mensagem na db interna")
            except:
                print("Erro ao inserir atividade de mensagem na db")


def setup(bot):
    bot.add_cog(Karaoke(bot))
