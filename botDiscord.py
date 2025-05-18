import threading
import asyncio

import private_token
import discord
from discord.ext import commands

import logging
logger = logging.getLogger(f"app.{__name__}")

COMMAND_PREFIX = '!'
class BotDiscord:

    @staticmethod
    def format_message(type, **kwargs):
        if type == "invite":
            return f"{kwargs['sender']} vous invite à rejoindre la partie ({kwargs['nbPlayer']} / 4)\n\n" \
                   f"Voici le lien de la partie: {kwargs['invite_link']}\n\n" \
                   f"Vous pouvez rejoindre la partie en cliquant sur le lien ci-dessus."

    @staticmethod
    def send_on_channels(message, bot_instance):
        async def send_message():
            await bot_instance.bot.wait_until_ready()
            logger.info(f"Send message to channels {message}")
            for channel in bot_instance.bot_channels:
                try:
                    await channel.send(message)
                except discord.Forbidden:
                    logger.error(f"Permission denied to send message in channel {channel.name} (ID: {channel.id})")
                    return False, "Une erreur est survenue lors de l'envoi du message."
                except discord.HTTPException as e:
                    logger.error(f"Failed to send message in channel {channel.name} (ID: {channel.id}): {e}")
                    return False, "Une erreur est survenue lors de l'envoi du message."
                except Exception as e:
                    logger.error(f"Unexpected error while sending message in channel {channel.name} (ID: {channel.id}): {e}")
                    return False, "Une erreur est survenue lors de l'envoi du message."

        future = asyncio.run_coroutine_threadsafe(send_message(), bot_instance.bot.loop)
        try:
            future.result()
        except Exception as e:
            logger.error(f"Error while sending message: {e}")
            return False, "Une erreur est survenue lors de l'envoi du message."

        return True, ""

    def __init__(self):
        self._intents = discord.Intents.default()
        self._intents.message_content = True
        self._intents.guilds = True
        self.bot = bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=self._intents)

    def start(self):
        threading.Thread(target=self.bot.run, args=(private_token.DISCORD_TOKEN,), daemon=True).start()

        @self.bot.event
        async def on_ready():
            logger.info(f"Bot is ready. Logged in as {self.bot.user.name} ({self.bot.user.id})")
            logger.info("Fetching channels...")
            self.bot_channels = []
            for chan in private_token.CHANNEL_ID:
                channel = self.bot.get_channel(chan)
                if channel is not None:
                    self.bot_channels.append(channel)
                else:
                    logger.info(f"Channel with ID {chan} not found.")

            for channel in self.bot_channels:
                logger.info(f"Connected to channel: {channel.name} (ID: {channel.id})")
                await channel.send("SansCoeur fait peau neuve : il a été mis à jour !")
