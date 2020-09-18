import discord
import json
import urllib.request
import asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import HTTPError
from discord.ext import tasks, commands

client = discord.Client()
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

def Update_User(id) :
	global idList
	if idList[id]['today'] :
		return True
	else:
		temp_update_num = Connect_User(id)
		if idList[id]['getAnswer'] != temp_update_num[1] :
			print(f'{id}는 문제를 풀었음.')
			idList[id]['getAnswer'] = temp_update_num[1]
			idList[id]['today'] = True
			return True
		else:
			print(f'{id}는 문제를 풀지않음.')
			return False

class DevCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.loopcount = 0
		FileRead()
	
	def cog_unload(self) :
		self.loop_station.cancle()

	@commands.command()
	async def reload(self, ctx, cog='cogs.core') :
		extensions = self.bot.extensions
		if cog in extensions:
			self.bot.reload_extension(cog)
			await ctx.send('Done!')
		else:
			await ctx.send('Fail! - Unkown Cog.')

	@commands.command()
	async def ping(self, ctx) :
		# self.loop.start()
		await ctx.send(f'Pong~ :ping_pong: {round(1000 * self.bot.latency)}ms')

	@commands.command()
	async def help(self, ctx):
		embed=discord.Embed(title="HELP", description="명령어를 확인하세요!", color=0x00ff56)
		embed.set_author(name="Coding bot", url="https://www.acmicpc.net/", icon_url="https://user-images.githubusercontent.com/42747200/46140125-da084900-c26d-11e8-8ea7-c45ae6306309.png")
		# embed.set_thumbnail(url="https://d2gd6pc034wcta.cloudfront.net/images/logo@2x.png")
		embed.add_field(name="Commands", value="```!help```", inline=True)
		embed.add_field(name="Add User", value="```!user add <id>```", inline=True)
		embed.add_field(name="Del User", value="```!user del <id>```", inline=True)
		embed.add_field(name="Stat User", value="```!user stat```", inline=True)
		embed.add_field(name="Update User", value="```!update <id>```", inline=True)
		embed.add_field(name="Site", value="```!site```", inline=True)
		await ctx.send(embed=embed)
	
	@commands.command()
	async def user(self, ctx, stat=None, id='zxcasdqwe'):

		if stat == 'add' :
			t = ctx.author.id
			if id in idList :
				await ctx.send('오류! - 중복이 감지되었습니다. 등록되지 않았습니다.')
			else :
				idNum = Connect_User(id)
				if len(idNum) == 0 :
					print('등록 오류')
					await ctx.send('오류! - 등록되지 않았습니다!')
				else :
					await ctx.send('정상적으로 등록되었습니다!')
					idList[id] = {'authorID' : t, 'getAnswer' : idNum[1], 'today' : False}
					FileWrite()
		elif stat == 'del':
			if id in idList :
				del idList[id]
				await ctx.send('삭제에 성공하셨습니다!')
			else :
				await ctx.send('오류! - 삭제에 실패하셨습니다!')
		else:
			if idList == '' :
				await ctx.send('오류! - 아무 것도 등록되지 않았습니다.')
			else :
				await ctx.send(idList)
	
	@tasks.loop(seconds=30)
	async def loop_station(self):
		if self.loopcount > 0 :
			self.loopcount += 1
			notSoloveList = []		
			for autoid in idList :
				if not(Update_User(autoid)) :
					notSoloveList.append('<@' + (str)(idList[autoid]['authorID']) + '>')

			embed=discord.Embed(title="업데이트!", description='현재 상황을 보고합니다.', color=0x00ff56)
			embed.set_author(name="Coding bot", url="https://www.acmicpc.net/", icon_url="https://user-images.githubusercontent.com/42747200/46140125-da084900-c26d-11e8-8ea7-c45ae6306309.png")
			embed.add_field(name="풀지 않은 ID", value=f'{", ".join(notSoloveList)}', inline=True)
			channel = self.bot.get_channel(755469632772767873)
			await channel.send(embed=embed)
		else :
			self.loopcount += 1
			print("Loop Start")
	
	@loop_station.after_loop
	async def reset(self):
		channel = self.bot.get_channel(755469632772767873)
		await channel.send('Hello~')
		
	@commands.command()
	async def start(self, ctx):
		self.loop_station.start()
		await ctx.send("Start loop!")

	@commands.command()
	async def stop(self, ctx):
		self.loop_station.cancle()
		await ctx.send("stop loop!")

def setup(bot):
	print("Loaded! -Core.py")
	bot.add_cog(DevCommands(bot))
