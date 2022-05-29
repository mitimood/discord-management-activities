import json
import os
import threading
from datetime import datetime

from pymongo import MongoClient
from tinydb import TinyDB
from main import configData
from discord.ext import commands

db_temp_users = TinyDB('./temporary db/ActivityKaraoke.json')
db_temp_CD = TinyDB('./temporary db/CommandsCoolDown.json')

# make available the config file as configData object
if os.path.exists((os.getcwd() + "/config.json")):
    with open("config.json") as f:
        configData = json.load(f)

cluster = MongoClient(
    configData["mongoconect"])
db = cluster[configData["database_name"]]
collection = db["activitykaraoke"]["tempdb"]


class Karaoke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


guilds = [configData["channels"]["guild"]]


def save_mongo_karaoke():
    threading.Timer(300.0, save_mongo_karaoke).start()
    stamp_time = datetime.utcnow().timestamp()
    try:
        if db_temp_users.all():
            for dic in db_temp_users:
                del dic["lastMsg"]
                insert = {"$push": {"Activities": {"time": stamp_time, "voice": dic["voice"], "chat": dic["chat"]}},
                          "$inc": {"Total_Atv": 1}, "$set": {"last": stamp_time}}
                db.activitykaraoke.update_many({"_id": dic["_id"]}, insert, upsert=True)
            db_temp_users.truncate()
    except:
        print("Erro ao salvar dbMongo")


save_mongo_karaoke()


def setup(bot):
    bot.add_cog(Karaoke(bot))


def _add_field(name, emb, value="Nenhuma atividade"):
    emb.add_field(name=name, value=value, inline=False)
    return emb
