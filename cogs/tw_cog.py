from discord.ext import commands,tasks
import os
import tweepy
import time
import datetime
import pymongo
from dotenv import load_dotenv
import logging
FORMAT = '[%(asctime)s] [%(levelname)s]: %(message)s'
logging.basicConfig(level=logging.DEBUG,format=FORMAT)
load_dotenv()


#twitter API
client_id = os.environ.get('client_id')
access_token_secret = os.environ.get('access_token_secret')
access_token = os.environ.get('access_token')
consumer_secret = os.environ.get('consumer_secret')
consumer_key = os.environ.get('consumer_key')
client_secret = os.environ.get('client_secret')
bearer_token = os.environ.get('bearer_token')

#datbase setup
client = pymongo.MongoClient(os.getenv("database"))

db = client["twitter"]
trackings = db["trackings"]
user_data = db["user_data"]
#API setup

#api v2

api2 = tweepy.Client(bearer_token,consumer_key,consumer_secret,access_token,access_token_secret,return_type=dict)


class Twitter(commands.Cog):
  """
  Modules for using twitter API
  #posting and direct message is not included
  """
  def __init__(self,bot):
    self.bot = bot
    self.tw_trace.start()
  
  @commands.group(invoke_without_command=True)
  async def twitter(self,ctx):
    """
    `**add**`
    `Usage:`
    `$twitter add <username>`
    adding `username` into tracking list
    
    `**delete**`
    `Usage:`
    `$twitter delete <username>`
    delete `username` from tracking list
    
    `**list**`
    `Usage:`
    `$twitter list`
    sending users that are tracking

    `**update**`
    `Usage:`
    `$twitter update`
    force updating
    """

    pass
  
  @twitter.command()
  async def add(self,ctx,userid:str):
    names = [x for x in trackings.find({},{"_id":0,"last_update":0}) if bool(x)]
    data = {"userid":userid,"channel":[ctx.message.channel.mention]}
    if len(names) == 0:
      trackings.insert_one(data)
      await ctx.send(f"{userid} is added to the tracking list")
    for i in range(len(names)):
        if (names[i]["userid"] == userid) and (names[i]["channel"] == ctx.message.channel.mention):
            await ctx.send(f"{userid} is already in the tracking list") 
            break
        elif (names[i]["userid"] == userid) and not(ctx.message.channel.mention in names[i]["channel"]):
            trackings.update_one({"userid":userid},{"$push":{"channel":ctx.message.channel.mention}})
            await ctx.send(f"{userid} is added to the tracking list (channel)") 
            break
        
        if i == len(names) - 1:
            trackings.insert_one(data)
            await ctx.send(f"{userid} is added to the tracking list")

  @twitter.command()
  async def list(self,ctx):
    data = [x for x in trackings.find({},{"_id":0,"last_update":0}) if bool(x)]
    if len(data) > 0:
      userids = [x["userid"] for x in data if ctx.message.channel.mention in x["channel"]]
      lists = ",".join(userids)
      try:
        await ctx.send(f"{lists}")
      except:
        await ctx.send("No twitter account is tracing")
    else:
      await ctx.send("No twitter account is tracing")

  @twitter.command()
  async def delete(self,ctx,userid:str):
    userids = [x for x in trackings.find({},{"_id":0,"last_update":0}) if bool(x)]
    tweets_count = [x for x in user_data.find({},{f"{userid}_data":1,"_id":0}) if bool(x)]
    if len(userids) > 0:
        for id in range(len(userids)):
            if (userids[id]["userid"] == userid) and (ctx.message.channel.mention in userids[id]["channel"]):
                if len(userids[id]["channel"]) == 1:
                    trackings.delete_one({"userid":userid})
                    try:
                      user_data.delete_one({f"{userid}_data":{"tweets_count":tweets_count[0][f"{userid}_data"]["tweets_count"]}})
                    except Exception as e:
                      logging.error(e)
                    await ctx.send(f"{userid} has removed from tracking list")
                else:
                    trackings.update_one({"userid":userid},{"$pull":{"channel":{"$gte":ctx.message.channel.mention}}})
                    await ctx.send(f"{userid} has removed from tracking list (channel)")
                break
            if id == len(userids) - 1:
                await ctx.send(f"{userid} is not in the tracking list")
    else:
        print("No twitter account is tracing")

  @twitter.command()
  async def update(self,ctx):
    try:
      self.tw_trace.cancel()
      self.tw_trace.start()
      await ctx.send("Forced updated tracking")
    except RuntimeError:
      await ctx.send("Updating, please try later")
  
  @tasks.loop(seconds=20)
  async def tw_trace(self):
    data = [x for x in trackings.find({},{"_id":1,"last_update":0}) if bool(x)][1:]
    time_trac = [x for x in trackings.find({},{"_id":1,"last_update":1}) if bool(x)]
    time_user = [x for x in user_data.find({},{"_id":1,"last_update":1}) if bool(x)]
    if len(data) > 0:
      #retrievng data from API
      namelist = [x["userid"] for x in data]
      
      user_data.update_one({"_id":time_user[0]["_id"]},{"$set":{"last_update" : time.mktime(datetime.datetime.now().timetuple())}})
      trackings.update_one({"_id":time_trac[0]["_id"]},{"$set":{"last_update" : time.mktime(datetime.datetime.now().timetuple())}})
      id = api2.get_users(usernames=namelist,user_fields=["public_metrics"])
      
      i2 = 0
      for username in id["data"]:
        tweets_count = username['public_metrics']['tweet_count']
        name = username["username"]
        #try:
        #  p_tw_count = [x for x in user_data.find({},{f"{name}_data":1})][0]["tweets_count"]
        #  print(p_tw_count)
        #except Exception:
        #  p_tw_count = tweets_count
        logging.debug("username:%s tweets_count:%s"%(name,tweets_count))
        try:
          p_tw_count = [x for x in user_data.find({},{f"{name}_data":1,"_id":0}) if bool(x)][0][f"{name}_data"]["tweets_count"]
          logging.debug("loading tweets count from database successfully")
          logging.debug("database data:%s"%(p_tw_count))
        except IndexError as e:
          p_tw_count = tweets_count
          logging.debug("loading tweets count from database unsuccessfully")    
          logging.error(e)
        if tweets_count > p_tw_count:
          logging.info("Detected %s has new tweet, loading..."%(name))
          tw_id = api2.get_users_tweets(id=username["id"],max_results=5)["data"][0]["id"]
          for i in data:
            if i["userid"] == name:
              for x in i["channel"]:
                channel = self.bot.get_channel(int(x[2:-1]))
                await channel.send(f"https://twitter.com/{name}/status/{tw_id}")  
        
        
        logging.info("searching for update...")
        if len([x for x in user_data.find({f"{name}_data":{"tweets_count":p_tw_count}})]) == 0:
          user_data.insert_one({f"{name}_data":{
          "tweets_count":tweets_count
        }})
          logging.debug("inserted data for %s"%(name))
        result = user_data.update_one({f"{name}_data":{"tweets_count":p_tw_count}},{"$set":{f"{name}_data":{
          "tweets_count":tweets_count
        }}})     
        logging.debug("modifed count: %s"%(result.modified_count))
        logging.debug("matched count: %s"%(result.matched_count))

        
        i2 += 1



def setup(bot):
  bot.add_cog(Twitter(bot))


