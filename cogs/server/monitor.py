import nextcord
from nextcord.ext import commands, tasks
from util.config import RCON_HOST, RCON_PORT, RCON_PASS
import util.constants as c
from gamercon_async import EvrimaRCON
from util.functions import saveserverinfo, loadserverinfo
import pytz
import datetime
import re
import logging

class EvrimaMonitorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rcon_host = RCON_HOST
        self.rcon_port = RCON_PORT
        self.rcon_password = RCON_PASS
        self.update_server_info.start()
        self.update_bot_activity.start()

    def create_embed(self, server_info):
        embed_timestamp = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone('US/Central')).strftime('%m/%d/%Y %H:%M %Z')
        embed = nextcord.Embed(title=server_info.get("ServerDetailsServerName", "N/A"), color=nextcord.Color.blurple())
        embed.add_field(name="Players", value=f"{server_info.get('ServerCurrentPlayers', 0)}/{server_info.get('ServerMaxPlayers', 0)}", inline=False)
        embed.add_field(name="Map", value=server_info.get("ServerMap", "N/A"), inline=False)
        embed.add_field(name="Day Length", value=f"{server_info.get('ServerDayLengthMinutes', 0)} minutes", inline=False)
        embed.add_field(name="Night Length", value=f"{server_info.get('ServerNightLengthMinutes', 0)} minutes", inline=False)
        embed.set_thumbnail(url=c.BOT_ICON)
        embed.set_footer(text=f"{c.BOT_TEXT} {c.BOT_VERSION} • Updated: {embed_timestamp}", icon_url=c.BOT_ICON)
        
        return embed

    def _extract_field(self, response, key):
        # Match "Key: value" where value runs until the next ", Key2:" or the end
        # of the response. This tolerates added/removed/reordered fields so a
        # game-server update can't break the whole parse.
        match = re.search(rf"{re.escape(key)}:\s*(.*?)(?=,\s*\w+:|\Z)", response, re.DOTALL)
        if not match:
            return None
        return match.group(1).strip()

    def _parse_server_info(self, response):
        def as_int(key, default=0):
            raw = self._extract_field(response, key)
            try:
                return int(raw)
            except (TypeError, ValueError):
                return default

        def as_bool(key, default=False):
            raw = self._extract_field(response, key)
            if raw is None:
                return default
            return raw.lower() == "true"

        return {
            "ServerDetailsServerName": self._extract_field(response, "ServerDetailsServerName") or "N/A",
            "ServerPassword": self._extract_field(response, "ServerPassword") or "",
            "ServerMap": self._extract_field(response, "ServerMap") or "N/A",
            "ServerMaxPlayers": as_int("ServerMaxPlayers"),
            "ServerCurrentPlayers": as_int("ServerCurrentPlayers"),
            "bEnableMutations": as_bool("bEnableMutations"),
            "bEnableHumans": as_bool("bEnableHumans"),
            "bServerPassword": as_bool("bServerPassword"),
            "bQueueEnabled": as_bool("bQueueEnabled"),
            "bServerWhitelist": as_bool("bServerWhitelist"),
            "bSpawnAI": as_bool("bSpawnAI"),
            "bAllowRecordingReplay": as_bool("bAllowRecordingReplay"),
            "bUseRegionSpawning": as_bool("bUseRegionSpawning"),
            "bUseRegionSpawnCooldown": as_bool("bUseRegionSpawnCooldown"),
            "RegionSpawnCooldownTimeSeconds": as_int("RegionSpawnCooldownTimeSeconds"),
            "ServerDayLengthMinutes": as_int("ServerDayLengthMinutes"),
            "ServerNightLengthMinutes": as_int("ServerNightLengthMinutes"),
            "bEnableGlobalChat": as_bool("bEnableGlobalChat"),
        }

    async def get_server_info(self):
        try:
            rcon = EvrimaRCON(self.rcon_host, self.rcon_port, self.rcon_password)
            await rcon.connect()
            command = b'\x02' + b'\x12' + b'\x00'
            response = await rcon.send_command(command)

            server_info = self._parse_server_info(response)

            if server_info and server_info.get("ServerMaxPlayers"):
                return server_info
            else:
                # Only log the raw response for debugging; do not spam the loop.
                logging.warning(
                    "Could not parse server info from RCON response. "
                    f"Response was: {response!r}"
                )
                return None
        except Exception as e:
            logging.error(f"Error retrieving server info: {e}")
            return None

    @tasks.loop(seconds=30)
    async def update_bot_activity(self):
        try:
            server_info = await self.get_server_info()
            if server_info:
                player_count = server_info["ServerCurrentPlayers"]
                max_players = server_info["ServerMaxPlayers"]
                activity_text = f"Players {player_count}/{max_players}"
                activity = nextcord.Activity(type=nextcord.ActivityType.watching, name=activity_text)
                await self.bot.change_presence(activity=activity)
        except Exception as e:
            logging.error(f"Error updating bot activity: {e}")

    @update_bot_activity.before_loop
    async def before_update_bot_activity(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=5)
    async def update_server_info(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            guild_info_list = loadserverinfo(guild.id)
            if guild_info_list:
                for guild_info in guild_info_list:
                    channel = self.bot.get_channel(int(guild_info['channel_id']))
                    if channel:
                        try:
                            message = await channel.fetch_message(int(guild_info['message_id']))
                            server_info = await self.get_server_info()
                            if server_info:
                                embed = self.create_embed(server_info)
                                await message.edit(embed=embed)
                        except Exception as e:
                            logging.error(f"Error updating server info for guild {guild.id}: {e}")

    @update_server_info.before_loop
    async def before_update_server_info(self):
        await self.bot.wait_until_ready()

    @nextcord.slash_command(
        description='Post a live tracker of your game server.',
        default_member_permissions=nextcord.Permissions(administrator=True)
    )
    async def postserver(self, interaction: nextcord.Interaction, channel: nextcord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        server_info = await self.get_server_info()
        if server_info:
            embed = self.create_embed(server_info)
            message = await channel.send(embed=embed)
            saveserverinfo(interaction.guild_id, channel.id, message.id)
            await interaction.followup.send(f"Server info message created in {channel.mention}", ephemeral=True)
        else:
            await interaction.followup.send("Error retrieving server info. Check the RCON connection.", ephemeral=True)

    def cog_unload(self):
        self.update_server_info.cancel()
        self.update_bot_activity.cancel()

def setup(bot):
    cog = EvrimaMonitorCog(bot)
    bot.add_cog(cog)
    if not hasattr(bot, 'all_slash_commands'):
        bot.all_slash_commands = []
    bot.all_slash_commands.extend([
        cog.postserver
    ])
