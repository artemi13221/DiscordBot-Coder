import os
import json
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import HTTPError
from keep_alive import keep_alive
from discord.ext import commands

url = "https://www.acmicpc.net/user/"
idList = {}

def FileRead() : # IDList.json을 불러옴.
  global idList
  f = open('IDList.json', 'r')
  readJson = f.readline()
  if readJson == '' :
    print("불러오기 실패!")
  else:
    idList = json.loads(readJson)
    print('IDList 불러오기 완료!')
  f.close() 
  
def FileWrite() : #IDList.json을 저장함.
  global idList
  f = open('IDList.json', 'w')
  writeJson = json.dumps(idList)
  f.write(writeJson)
  f.close
  print('IDList 저장 완료!')

def Connect_User(id) : #acmicpc.net/user/의 id를 붙여 웹크롤링.
  userList = []
  f_url = url + id
  try :  
    req = urllib.request.urlopen(f_url)
  except HTTPError :
    print("오류 발생!")
  else :
    res = req.read()
    soup = BeautifulSoup(res, 'html.parser')
    userList = soup.find_all('td')
    userList = [each_line.get_text().strip() for each_line in userList[:10]]
  return userList

bot = commands.Bot(
	command_prefix="!",  # Change to desired prefix
	case_insensitive=False  # Commands aren't case-sensitive
)

bot.author_id = 281419528053981185  # Change to your discord id!!!

@bot.event 
async def on_ready():  # When the bot is ready
    print("Open!")
    print(bot.user)  # Prints the bot's username and identifier
    FileRead()

@bot.command()
async def ping(ctx):
    latancy = bot.latency #봇의 레이턴시 구하기
    await ctx.send(f'현재 핑은 {round(latancy * 1000)}ms입니다.') #핑을 출력 

@bot.command()
async def adduser(ctx, *, addid: str):
  t = ctx.author.id
  if addid in idList :
    resultStr = "오류! - 중복이 감지되었습니다. 등록되지 않았습니다."
  else :
    idNum = Connect_User(addid)
    if len(idNum) == 0 :
      print('등록 오류')
      resultStr = "오류! - 등록되지 않았습니다!"
    else :
      resultStr = "정상적으로 등록되었습니다!"
      idList[addid] = {'authorID' : t, 'getAnswer' : idNum[1], 'todayAnswer' : False}
      FileWrite()
  await ctx.send(f'{resultStr}')

@bot.command()
async def statuser(ctx) :
  if idList == '' :
    resultStr2 = '오류! - 아무 것도 등록되지 않았습니다.'
  else :
    resultStr2 = idList
  await ctx.send(resultStr2)

@bot.command()
async def deleteuser(ctx, *, deleteid: str) :
  if deleteid in idList :
    del idList[deleteid]
    resultStr = str(deleteid) + ' 삭제에 성공하셨습니다!'
  else :
    resultStr = str(deleteid) + ' 오류! - 삭제에 실패하셨습니다!'
  await ctx.send(resultStr)

@bot.command()
async def site(ctx) :
  t = ctx.author.id
  await ctx.send(f'<@!{t}>, https://www.acmicpc.net/')

@bot.command()
async def update(ctx, *, updateID: str) :
  if updateID in idList :
    updateNum = Connect_User(updateID)
    idList[updateID]['getAnswer'] = updateNum[1]
    resultStr3 = "정상적으로 업데이트되었습니다."
  else :
    resultStr3 = "오류! - 등록 되어 있지 않는 아이디입니다."
  await ctx.send(resultStr3)

@bot.command()
async def reset(ctx) :
  # 이 명령어는 자동으로 오전 12시 또는 오전 6시가 되었을 때 실행
  # 모든 idList의 담긴 todayAnswer = False로 지정
  # 그와 동시에 모든 사용자 업데이트를 통해 맞은 문제의 개수를 재조정
  # 안 푼 사람, 즉 todayAnswer = False였던 사람을 다른 List에 기록.
  await ctx.send('Reset...')

@bot.command()
async def automessage(ctx) :
  # 이 명령어는 3시간격으로 아침 9시부터 저녁 11:59분까지만 실행함.
  # 이 메세지가 나올 땐 모든 사용자 업데이트를 통해 맞은 문제의 개수 재조정
  # 만약, 맞은 문제의 개수의 조정이 생겼을 경우, todayAnswer = True로 전환
  # 메세지가 나갈 땐 todayAnswer = False인 사람들에 author id를 불러와 멘션으로 알림.
  # 그와 동시에 어제 안 푼 사람의 List를 사용해 표시하면서 공부할 의지를 다지게 해줌.
  await ctx.send('AutoMessage...')

extensions = [
	  # Same name as it would be if you were importing it
]

if __name__ == '__main__':  # Ensures this is the file being ran
	for extension in extensions:
		bot.load_extension(extension)  # Loades every extension.

keep_alive()  # Starts a webserver to be pinged.
token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)  # Starts the bot