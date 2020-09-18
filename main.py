import discord
import os
from discord.ext import tasks ,commands


bot = commands.Bot(command_prefix='!', help_command=None)
@bot.event
async def on_ready():
  print(f'Bot Login! - {bot.user}')
  await bot.change_presence(activity=discord.Game('C++'))

@bot.command()
async def load(ctx, cog=None):
  if cog == None :
    return
  else :
    bot.load_extension(f'cogs.{cog}')

@bot.command()
async def unload(ctx, cog=None):
  if cog == None :
    return
  else :
    bot.unload_extension(f'cogs.{cog}')

extensions = [
	'cogs.core'
]

if __name__ == '__main__':
  for extension in extensions:
    bot.load_extension(extension)

token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)