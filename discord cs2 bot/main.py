import discord
import aiohttp
import asyncio
import os
from dotenv import load_dotenv


TOKEN = os.getenv('DISCORD_TOKEN')

CHANNEL_ID = os.getenv('Discord_CHANNELID')
CHECK_INTERVAL = 3600  

class HLTVBot(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_sent_news_ids = set()

    async def setup_hook(self):
        self.bg_task = self.loop.create_task(self.send_news_periodically())

    async def fetch_hltv_news(self):
        url = 'https://hltv-api.vercel.app/api/news.json'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"Failed to fetch news: {resp.status}")
                    return []

    async def send_news_periodically(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        if not channel:
            print(f"Channel with ID {CHANNEL_ID} not found.")
            return

        while not self.is_closed():
            try:
                news = await self.fetch_hltv_news()
                for article in reversed(news):
                    if article['link'] not in self.last_sent_news_ids:
                        message = f"**{article['title']}**\n{article['link']}"
                        await channel.send(message)
                        self.last_sent_news_ids.add(article['link'])
            except Exception as e:
                print(f"Error in news task: {e}")

            await asyncio.sleep(CHECK_INTERVAL)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')


intents = discord.Intents.default()
bot = HLTVBot(intents=intents)
bot.run(TOKEN)       