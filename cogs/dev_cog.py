from discord.ext import commands
import os
import pymongo
from keep_alive import keep_alive

#mongo API
#*database setup
client = pymongo.MongoClient(os.getenv("database"))

class Developer(commands.Cog):
  """
  Modules for the developers of the bot
  """
  def __init__(self,bot):
    self.bot = bot

  @commands.command(name="ping")
  async def ping(self,ctx):
    """
    `Description:`
    return bot latency
    `Usage:`
    `$ping`
    """
    await ctx.send(f'{round(self.bot.latency*1000)} (ms)')



  #cog command
  @commands.group(invoke_without_command=True)
  async def cog(self,ctx):
    """
    `Description:`
    Handling Cogs
    
    `**reload**`
    `Usage:`
    `$cog reload <cog>/#all`
    reload specific cog or all cogs
    
    `**unload**`
    `Usage:`
    `$cog unload <cog>`
    unload specific cog
    
    `**load**`
    `Usage:`
    `$cog load <cog>`
    load specific cog
    """
    await ctx.send("type $help")
  
  @cog.command()
  async def reload(self,ctx,name:str):
    """reloading extension"""
    if name == "#all":
      files = ["cogs."+file[:-3] for file in os.listdir("cogs") if file.endswith(".py")]
      for file in files:
        self.bot.reload_extension(file)
        await ctx.send(f"Cog {file} reloaded")
    else:
      self.bot.reload_extension(name)
      await ctx.send(f"Cog {name} reloaded")

  @cog.command()
  async def unload(self,ctx,name:str):
    """unloading extension"""
    self.bot.unload_extension(name)
    await ctx.send(f"Cog {name} unloaded")

  @cog.command()
  async def load(self,ctx,name:str):
    """loading extension"""
    self.bot.load_extension(name)
    await ctx.send(f"Cog {name} loaded")
  
    

  #database command
  @commands.group()
  async def database(self,ctx):
    """ 
    `Desciption:`
    Accesing replit database
    
    `**get**`
    `Usage:`
    `$database get`
    send all value and keys in the database

    `$database delete <target>`
    delete specific key
    """

    
    pass

  @database.command()
  async def get(self,ctx):
    for db_name in client.list_database_names():
      if db_name != "local" and db_name != "admin":
        db = client[db_name]
        for coll_name in db.list_collection_names():
          await ctx.send("db: {}, collection:{}".format(db_name, coll_name))
          for r in db[coll_name].find({},{"_id":0}):
            await ctx.send(r)

  @database.command()
  async def delete(self,ctx,db:str,col:str,target:str):
    pass
    #client[db][col].update_one({},{$unset:{}})

          
        

keep_alive()
def setup(bot):
  bot.add_cog(Developer(bot))
      
      