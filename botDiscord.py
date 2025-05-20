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
            name = kwargs['sender'][0].upper() + kwargs['sender'][1:]
            return f"{'-' * 20}\n" \
                   f"{name} vous invite à rejoindre la partie ({kwargs['nbPlayer']} / 4)\n\n" \
                   f"Voici le lien de la partie: {kwargs['invite_link']}\n" \
                   f"Vous pouvez rejoindre la partie en cliquant sur le lien ci-dessus. (Tapez !chut pour me faire taire)"

        elif type == "test":
            return f"Ceci est un message de test.\nSi vous le voyez, ce que l'administrateur du site cherche à faire quelque chose\n" \
                   f"Je vous invite à le prévenir.\n\n" \
                   f"Merci d'avance :)"

    @staticmethod
    def send_to_player(message, player_id, bot_instance):
        async def send_to(user_id):
            await bot_instance.bot.wait_until_ready()
            try:
                user = await bot_instance.bot.fetch_user(user_id)
                if user:
                    await user.send(message)
            except discord.Forbidden:
                logger.error(f"Permission denied to send message to user {user_id}")
                return False, "Une erreur est survenue lors de l'envoi du message."
            except discord.HTTPException as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                return False, "Une erreur est survenue lors de l'envoi du message."
            except Exception as e:
                logger.error(f"Unexpected error while sending message to user {user_id}: {e}")
                return False, "Une erreur est survenue lors de l'envoi du message."
            return True, ""
        future = asyncio.run_coroutine_threadsafe(send_to(player_id), bot_instance.bot.loop)
        return future.result()

    @staticmethod
    def send_to_all_players(message, dbManager, bot_instance):

        async def send_to(user_id):
            await bot_instance.bot.wait_until_ready()
            try:
                user = await bot_instance.bot.fetch_user(user_id)
                if user:
                    await user.send(message)
            except discord.Forbidden:
                logger.error(f"Permission denied to send message to user {user_id}")
                return False, "Une erreur est survenue lors de l'envoi du message."
            except discord.HTTPException as e:
                logger.error(f"Failed to send message to user {user_id}: {e}")
                return False, "Une erreur est survenue lors de l'envoi du message."
            except Exception as e:
                logger.error(f"Unexpected error while sending message to user {user_id}: {e}")
                return False, "Une erreur est survenue lors de l'envoi du message."

        players = dbManager.getAllUsers()
        for player in players:
            if player.discord_id is not None and player.discord_mute is False:
                future = asyncio.run_coroutine_threadsafe(send_to(player.discord_id), bot_instance.bot.loop)
                ret, msg = future.result()
                if not ret:
                    logger.error(f"Failed to send message to user {player.discord_id}: {msg}")

        return True, ""

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

    def __init__(self, dbManager):
        self._intents = discord.Intents.default()
        self._intents.message_content = True
        self._intents.guilds = True
        self.bot = bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=self._intents)
        self.dbManager = dbManager

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


        @self.bot.command(name="chut")
        async def mute(ctx):
            user = self.dbManager.getUserByDiscordID(ctx.author.id)
            if user:
                ret, msg = self.dbManager.discordMute(ctx.author.id, 1)
                if ret:
                    await ctx.send(f"Quelle honte, j'ai été mis en sourdine.\n\nTape !parle pour me redonner la parole")
                else:
                    await ctx.send(f"Erreur lors de la mise en sourdine de {ctx.author}: {msg}")

        @self.bot.command(name="parle")
        async def parle(ctx):
            user = self.dbManager.getUserByDiscordID(ctx.author.id)
            if user:
                ret, msg = self.dbManager.discordMute(ctx.author.id, 0)
                if ret:
                    await ctx.send(f"Enfin, on m'a redonné la parole !\n\nTape !chut pour me faire taire.")
                else:
                    await ctx.send(f"Erreur lors de la mise en sourdine de {ctx.author}: {msg}")

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("Commande inconnue. Tape !help pour la liste des commandes.")
            else:
                raise error
