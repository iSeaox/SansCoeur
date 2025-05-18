import threading

import private_token
import discord
from discord.ext import commands

import logging
logger = logging.getLogger(f"app.{__name__}")

COMMAND_PREFIX = '!'

class BotDiscord:
    def __init__(self):
        self._intents = discord.Intents.default()
        self._intents.message_content = True
        self._intents.guilds = True
        self.bot = bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=self._intents)
        self.bot_channels = []
        for chan in private_token.CHANNEL_ID:
            channel = self.bot.get_channel(chan)
            if channel is not None:
                self.bot_channels.append(channel)
            else:
                logger.info(f"Channel with ID {chan} not found.")

    def start(self):
        threading.Thread(target=self.bot.run, args=(private_token.DISCORD_TOKEN,), daemon=True).start()

        @self.bot.event
        async def on_ready():
            logger.info(f"Bot is ready. Logged in as {self.bot.user.name} ({self.bot.user.id})")

            for channel in self.bot_channels:
                logger.info(f"Connected to channel: {channel.name} (ID: {channel.id})")
                await channel.send("SansCoeur a été mis à jour !")
