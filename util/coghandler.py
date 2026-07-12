import os
import logging

def load_cogs(bot):
    for entry in os.listdir("cogs"):
        if entry.endswith(".py"):
            _try_load(bot, f"cogs.{entry[:-3]}")
        elif os.path.isdir(f"cogs/{entry}"):
            for filename in os.listdir(f"cogs/{entry}"):
                if filename.endswith(".py"):
                    _try_load(bot, f"cogs.{entry}.{filename[:-3]}")

def _try_load(bot, module_name):
    try:
        bot.load_extension(module_name)
        logging.info(f"Loaded cog: {module_name}")
    except Exception as e:
        logging.error(f"Failed to load cog {module_name}: {e}")