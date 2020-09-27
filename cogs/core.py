from ast import Num
import discord
import json
import urllib.request
from bs4 import BeautifulSoup
from urllib.request import HTTPError
from discord.ext import tasks, commands
from tabulate import tabulate

client = discord.Client()
url = "https://www.acmicpc.net/user/"
idList = {}
DFAULTCHANNEL = 755469632772767873
#755469632772767873 -Main
#759826483518111757 -Test
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
			idList[id]['getAnswer'] = temp_update_num[1]
			idList[id]['today'] = True
			return True
		else:
			return False

def Reset_User(id) :
	global idList
	idList[id]['today'] = False

def Update_today() :
	global idList
	notSoloveList = []
	for autoid in idList :
		if not(Update_User(autoid)) :
			notSoloveList.append('<@' + (str)(idList[autoid]['authorID']) + '>')
	FileWrite()
	mention = ", ".join(notSoloveList)
	if mention == '' :
		mention = "없음"
	embed=discord.Embed(title="업데이트", description='현재 상황을 보고합니다.', color=0x00ff56)
	embed.set_author(name="Coding bot", url="https://www.acmicpc.net/", icon_url="https://user-images.githubusercontent.com/42747200/46140125-da084900-c26d-11e8-8ea7-c45ae6306309.png")
	embed.add_field(name="풀지 않은 ID", value=f'{mention}', inline=False)

	return embed

def Reset_today() :
	global idList

	embed=discord.Embed(title="리셋", description='오늘 푼 문제를 모두 초기화합니다.', color=0x00ff56)
	embed.set_author(name="Coding bot", url="https://www.acmicpc.net/", icon_url="https://user-images.githubusercontent.com/42747200/46140125-da084900-c26d-11e8-8ea7-c45ae6306309.png")
	for autoid in idList:
		if(not(idList[autoid]['today'])) :
			idList[autoid]['warning'] += 1
		Reset_User(autoid)
	FileWrite()
	print("Reset Complete")
	return embed

class DevCommands(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.loopcount = 0
		FileRead()
		Reset_today()
		self.loop_station.start()
	
	def cog_unload(self) :
		self.loop_station.cancel()

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
		embed.add_field(name="Update User", value="```!update```", inline=True)
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
					idList[id] = {'authorID' : t, 'getAnswer' : idNum[1], 'today' : False, 'warning' : 0}
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
				table = []
				for statid in idList :
					#statid.ljust(12, ' ') + ' - 맞은문제수 : ' + idList[statid]['getAnswer'].ljust(4, ' ') + ' 오늘 상황 : ' + (str)(idList[statid]['today']).ljust(7, ' ') + '경고 수 : ' + (str)(idList[statid]['warning']) + '\n'
					table.append([statid, idList[statid]['getAnswer'], idList[statid]['today'], idList[statid]['warning']])
				headers = ["ID", 'Answer', 'Today', 'Warning']
				resultTable = '```py\n'+ tabulate(table, headers, tablefmt='presto', numalign='center', stralign='center') + '\n```'
				print(resultTable)
				await ctx.send(resultTable)
	
	@tasks.loop(hours=3) #hours=3
	async def loop_station(self):
		if (self.loopcount > 0) & (self.loopcount < 7) :
			embed = Update_today()
			self.loopcount += 1
			channel = self.bot.get_channel(DFAULTCHANNEL)
			await channel.send(embed=embed)
		elif self.loopcount >= 7 :
			channel = self.bot.get_channel(DFAULTCHANNEL)
			if self.loopcount == 7 :
				self.loopcount += 1
				print("휴식")
			else :
				self.loopcount = 1
				print('reset')
				embed = Reset_today()
				await channel.send(embed=embed)
		else :
			self.loopcount = 1
			print("Started loop")

	@loop_station.after_loop
	async def afterloop(self):
		print('오류이 발생하였습니다.')
		channel = self.bot.get_channel(DFAULTCHANNEL)
		await channel.send('오류가 발생하여 봇의 백그라운드가 종료되었습니다.')
		
	@commands.command()
	async def start(self, ctx):
		self.loop_station.start()
		await ctx.send("Start loop!")

	@commands.command()
	async def stop(self, ctx):
		self.loop_station.cancel()
		FileWrite()
		await ctx.send("도중에 종료하셨습니다. 현재 진행 상황을 저장합니다.")

	@commands.command()
	async def admin_today(self, ctx) :
		idList['dhtm1231']['today'] = True
		channel = self.bot.get_channel(DFAULTCHANNEL)
		await channel.send("관리자가 치트를 사용하였습니다. ==> dhtm1231의 오늘 문제 풀이를 True로 설정함.")

	@commands.command()
	async def update(self, ctx) :
		Update_today()
		await ctx.send("업데이트를 완료하였습니다.")

	@commands.command()
	async def reset(self, ctx) :
		embedReset = Reset_today()
		await ctx.send(embed=embedReset)

	@commands.command()
	async def site(self, ctx) :
		await ctx.send("https://www.acmicpc.net/")

	@commands.command()
	async def warning(self, ctx, stat = 'stat', id=' ', num = '1') :
		if num.isdigit() :
			if stat == 'add' :
				if id in idList :
					idList[id]['warning'] += int(num)
					FileWrite()
					await ctx.send(id + "의 경고를 " + num + "만큼 올렸습니다.")
				else :
					await ctx.send("없는 id이거나, id를 입력하지 않으셨습니다. 다시 입력하여 주세요.")
			elif stat == 'del' :
				if id in idList :
					idList[id]['warning'] -= int(num)
					FileWrite()
					await ctx.send(id + "의 경고를 " + num + "만큼 내렸습니다.")
				else :
					await ctx.send("없는 id이거나, id를 입력하지 않으셨습니다. 다시 입력하여 주세요.")
			else :
				await ctx.send("제대로 된 명령어를 입력해주세요.")
		else :
			await ctx.send("숫자를 제대로 입력해주세요.")
def setup(bot):
	print("Loaded! -Core.py")
	bot.add_cog(DevCommands(bot))