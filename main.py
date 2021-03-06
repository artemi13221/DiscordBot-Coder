import discord
import os
import schedule
import time
import dotenv
from discord.ext import tasks, commands

dotenv.load_dotenv(verbose=True)
ifloop = True

def core():
  global ifloop, bot
  print("loading core...")
  ifloop = False
  extensions = [
	'cogs.core'
  ]
  for extension in extensions:
    bot.load_extension(extension)

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

schedule.every().day.at("21:00").do(core)
while ifloop :
    schedule.run_pending()
    time.sleep(1)


token = os.getenv("DISCORD_BOT_SECRET")
bot.run(token)