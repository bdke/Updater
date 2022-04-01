from discord.ext import commands
from discord.errors import Forbidden
import discord

async def send_embed(ctx, embed):
    """
    Function that handles the sending of embeds
    -> Takes context and embed to send
    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue?", embed=embed)

class ErrorHandler(commands.Cog):
  """
  Modules for handling errors
  ATTENTION: this module has no command
  """
  def __init__(self,bot):
    self.bot = bot

  @commands.Cog.listener()
  async def on_command_error(self,ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
      message = f"Missing argument(s): {error.param}"
    elif isinstance(error, commands.MissingPermissions):
      message = f"Missing permission(s): {error.param}"
    else:
      message = f"Unhandled error: {error}"
    
    embed=discord.Embed(title="Whoops", description="what just happened?", color=0xff0000)
    embed.add_field(name="Error Message", value=message, inline=False)
    await send_embed(ctx,embed)

def setup(bot):
  bot.add_cog(ErrorHandler(bot))