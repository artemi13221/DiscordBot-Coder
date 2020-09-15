import discord

class MyClient(discord.Client):
  async def on_ready(self):
    print(f'접속되었습니다! {self.user}')

  async def on_message(self, message):
    print(f'이 메세지는 {message.author} : {message.context}')

client = MyClient()
client.run()