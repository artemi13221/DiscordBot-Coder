import os
import json
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import HTTPError
from keep_alive import keep_alive
from discord.ext import commands

url = "https://www.acmicpc.net/user/"
idList = []

def FileRead() :
  global idList
  f = open('IDList.json', 'r')
  readJson = f.readline()
  if readJson == '' :
    print("불러오기 실패!")
  else:
    idList = json.loads(readJson)
    print('IDList 불러오기 완료!')
  f.close() 
  
def FileWrite() :
  global idList
  f = open('IDList.json', 'w')
  writeJson = json.dumps(idList)
  f.write(writeJson)
  f.close
  print('IDList 저장 완료!')

def Connect_User(id) :
  print('hello')

bot = commands.Bot(
	command_prefix="!",  # Change to desired prefix
	case_insensitive=True  # Commands aren't case-sensitive
)

bot.author_id = 281419528053981185  # Change to your discord id!!!

@bot.event 
async def on_ready():  # When the bot is ready
    print("Open!")
    print(bot.user)  # Prints the bot's username and identifier
    FileRead()

@bot.command()
async def 안녕(ctx): #'안녕'을 입력하였을 때
  await ctx.send("Hello, World!") #함수의 비동기 흐름을 멈추고 명령을 수행.

@bot.command()
async def ping(ctx):
    latancy = bot.latency #봇의 레이턴시 구하기
    await ctx.send(f'현재 핑은 {round(latancy * 1000)}ms입니다') #핑을 출력 

@bot.command()
async def adduser(ctx, *, addid: str):
  f_url = url + addid
  try :  
    req = urllib.request.urlopen(f_url)
  except HTTPError:
    resultStr = f'{addid} 등록에 실패하였습니다!'
    print("오류 발생!")
  else :
    res = req.read()
    soup = BeautifulSoup(res, 'html.parser')
    num = soup.find_all('td')
    num = [each_line.get_text().strip() for each_line in num[:10]]
    idList.append({addid:num[1]})
    FileWrite()
    resultStr = f'{addid} 등록에 성공하셨습니다!'
  await ctx.send(f'{resultStr}')

@bot.command()
async def statuser(ctx) :
  if idList == '' :
    resultStr2 = '아무 것도 등록되지 않았습니다.'
  else :
    resultStr2 = idList
  await ctx.send(resultStr2)

@bot.command()
async def deleteuser(ctx, *, deleteid: str) :
  if deleteid in idList :
    del idList[deleteid]
    resultStr = str(deleteid) + '삭제에 성공하셨습니다!'
  else :
    resultStr = str(deleteid) + '삭제에 실패하셨습니다!'
  await ctx.send(resultStr)

extensions = [
	'cogs.cog_example'  # Same name as it would be if you were importing it
]

if __name__ == '__main__':  # Ensures this is the file being ran
	for extension in extensions:
		bot.load_extension(extension)  # Loades every extension.

keep_alive()  # Starts a webserver to be pinged.
token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)  # Starts the bot