import os
import asyncio
import logging
import aiohttp
import nextcord
from nextcord.ext import commands
import util.config as config
import util.errorhandling as e
import util.coghandler as c
from keep_alive import keep_alive

keep_alive()
e.setup_logging()
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=config.BOT_PREFIX, intents=intents, help_command=None, default_guild_ids=config.DEFAULT_GUILDS)

# Self-ping loop: on Autoscale deployments the platform spins the process down
# after a period with no inbound HTTP traffic. Hitting our own public URL
# periodically keeps that traffic flowing so the bot (and its Discord gateway
# connection) stays warm. Configure SELF_PING_URL to override the target;
# defaults to this project's published .replit.app URL. This is a workaround,
# not a guarantee -- an always-on "vm" deployment is the real fix.
SELF_PING_URL = os.environ.get("SELF_PING_URL", "https://bd-serverzip--spideypete.replit.app/")
SELF_PING_INTERVAL_SECONDS = 240

async def self_ping_loop():
    async with aiohttp.ClientSession() as session:
        while True:
            await asyncio.sleep(SELF_PING_INTERVAL_SECONDS)
            try:
                async with session.get(SELF_PING_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    logging.info(f"Self-ping to {SELF_PING_URL} returned {resp.status}")
            except Exception as ex:
                logging.warning(f"Self-ping to {SELF_PING_URL} failed: {ex}")

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}, created by KoZ")
    print(f"Servers: {len(bot.guilds)} | Users: {len(bot.users)}")
    print(f"Invite: {nextcord.utils.oauth_url(bot.user.id)}")
    if not getattr(bot, "_self_ping_started", False):
        bot._self_ping_started = True
        bot.loop.create_task(self_ping_loop())

@bot.event
async def on_guild_join(guild):
    print(f"Joined guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_guild_remove(guild):
    print(f"Left guild: {guild.name} (ID: {guild.id})")

@bot.event
async def on_application_command_error(interaction, error):
    await e.handle_errors(interaction, error)

c.load_cogs(bot)

if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)