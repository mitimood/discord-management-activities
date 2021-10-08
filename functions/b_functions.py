from discord.ext import commands
from pymongo import MongoClient

from main import configData


cluster = MongoClient(
    configData["mongoconect"])
db = cluster["kamaibot"]
collection = db["activityarte"]


def insert_atv_db(id, stamp):
    query = {"_id": id}
    insert = {"$set": {"_id": id, "last_arte": stamp}}
    collection.update_one(query, insert, upsert=True)


def get_atv_db(id_array):
    query = {"_id": {"$in": id_array}}
    docs = collection.find(query)
    return docs


class functions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(functions(bot))
