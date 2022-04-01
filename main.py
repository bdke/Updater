import os
from discord.ext import commands
from keep_alive import keep_alive
import pymongo
from dotenv import load_dotenv
import datetime
import time
import logging
FORMAT = '[%(asctime)s] [%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
load_dotenv()

#discord API
discord_key = os.getenv("discord_key")
bot = commands.Bot(command_prefix='$')

#mongo API
#*database setup
client = pymongo.MongoClient(os.getenv("database"))
db = client["twitter"]

#*user_data
user_data = db["user_data"]
if not(user_data.find_one()):
    user_data.insert_one({"last_update":time.mktime(datetime.datetime.now().timetuple())})
    
#*tracking
trackings = db["trackings"]
if not(trackings.find_one()):
    trackings.insert_one({"last_update":time.mktime(datetime.datetime.now().timetuple())})

#cogs

bot.load_extension("cogs.dev_cog")
bot.load_extension("cogs.tw_cog")
bot.load_extension("cogs.error_cog")
bot.remove_command('help')
bot.load_extension("cogs.help_cog")


#loading data from database


#discord setup
@bot.event
async def on_ready():
  print(">> Bot is online <<")



#keep_alive()
bot.run(discord_key)