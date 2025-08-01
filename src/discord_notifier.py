import discord
from discord.ext import commands
import aiohttp
import logging

class DiscordNotifier:
    def __init__(self, webhook_url, channel_id, bot_token):
        self.webhook_url = webhook_url
        self.channel_id = channel_id
        self.bot_token = bot_token
        self.intents = discord.Intents.default()
        self.intents.message_content = True
        self.bot = commands.Bot(command_prefix='!', intents=self.intents)
        self.logger = logging.getLogger(__name__)

    async def send_webhook(self, message):
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(self.webhook_url, session=session)
            try:
                await webhook.send(content=message)
                self.logger.info(f"Webhook sent: {message}")
            except Exception as e:
                self.logger.error(f"Webhook error: {e}")

    async def send_message(self, message):
        try:
            channel = self.bot.get_channel(int(self.channel_id))
            if channel:
                await channel.send(message)
                self.logger.info(f"Message sent: {message}")
            else:
                await self.send_webhook(message)
        except Exception as e:
            self.logger.error(f"Message send error: {e}")
            await self.send_webhook(message)

    async def start_bot(self):
        @self.bot.event
        async def on_ready():
            self.logger.info(f"Bot logged in as {self.bot.user}")

        @self.bot.command()
        async def status(ctx):
            await ctx.send("🟢 Bot is monitoring bug egg stock!")

        await self.bot.start(self.bot_token)
