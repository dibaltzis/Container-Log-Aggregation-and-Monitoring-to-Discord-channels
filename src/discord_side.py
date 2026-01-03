# discord_side.py
import discord
from discord.ext import commands
import asyncio
from datetime import datetime

class DiscordLogBot:
    def __init__(self, token, guild_id, category_name="discord-logs", container_names=None):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.messages = True

        self.token = token
        self.guild_id = guild_id
        self.category_name = category_name
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        self.channels = {}  
        self.category = None

        # Event: on_ready
        @self.bot.event
        async def on_ready():
            guild = self.bot.get_guild(self.guild_id)
            print(f"[INFO] [{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}] Logged in as [{self.bot.user}] at server: [{guild.name}]")
            if guild is None:
                print("[ERROR] Guild not found")
                return
            await self.ensure_category(guild)
            await self.ensure_channels(container_names, guild)

        # Run the bot in the background loop
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.bot.start(self.token))

    async def ensure_category(self,guild):
        # Fetch all channels from Discord to avoid cache issues
        all_channels = await guild.fetch_channels()

        # Check if category exists
        for c in all_channels:
            if isinstance(c, discord.CategoryChannel) and c.name == self.category_name:
                self.category = c
                return
        # Create category if not found
        self.category = await guild.create_category(self.category_name)
    
    async def ensure_channels(self, container_names, guild):
        if self.category is None:
            await self.ensure_category(guild)

        # Fetch all channels under this category (API call for freshness)
        all_channels = [c for c in await guild.fetch_channels() if isinstance(c, discord.TextChannel) and c.category_id == self.category.id]

        # Map lowercased names for safe comparison
        existing_names = {c.name.lower(): c for c in all_channels}

        for name in container_names:
            # Case-insensitive check to avoid duplicates
            channel = existing_names.get(name.lower())

            # Create channel if not found
            if channel is None:
                channel = await guild.create_text_channel(name, category=self.category)

            # Store reference in self.channels (use exact name)
            self.channels[name] = channel



    async def send_log(self, container_name, log_entry):
        """
        Send a log entry to the container's channel.
        If the channel does not exist yet, create it on the fly.
        """
        channel = self.channels.get(container_name)
        if channel is None:
            guild = self.bot.get_guild(self.guild_id)
            category = discord.utils.get(guild.categories, name=self.category_name)
            await self.add_container_channel(container_name, guild, category)
            channel = self.channels.get(container_name)

        await channel.send(f"```{log_entry}```")
