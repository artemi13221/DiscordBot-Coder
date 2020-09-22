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

async def on_member_join(member):
  joinStr = '```Coding Server의 오신 것을 환영합니다!\n이 서버는 하루에 백준 사이트의 한 문제씩 푸는 서버입니다.\n사용방법은 문제만 풀어주시면 됩니다.\n\n!user add <백준 사이트 아이디>를 입력하여 등록을 꼭 해주세요.\n필수! 이 서버의 알림을 끄지 말아주세요. \n멘션을 통한 알람만 받으셔도 상관없습니다.```'
  channel = bot.get_channel(755469632772767870)
  await channel.send(joinStr)

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