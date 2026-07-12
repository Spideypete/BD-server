import nextcord
from nextcord.ext import commands
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    log_filename = f"evrima_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    log_path = os.path.join('logs', log_filename)

    log_handler = RotatingFileHandler(
        filename=log_path, 
        maxBytes=10**7,
        backupCount=6,
        encoding='utf-8'
    )
    log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    log_handler.setFormatter(log_formatter)

    logging.basicConfig(level=logging.INFO, handlers=[log_handler])

    clean_logs('logs', 10)

def clean_logs(directory, max_logs):
    log_files = sorted(
        [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith("evrima_") and f.endswith(".log")],
        key=os.path.getctime,
        reverse=True
    )

    while len(log_files) > max_logs:
        os.remove(log_files.pop())
        
async def handle_errors(interaction, error):
    try:
        if isinstance(error, nextcord.NotFound):
            message = "Interaction expired or not found."
        elif isinstance(error, nextcord.HTTPException):
            message = "HTTP error occurred."
        elif isinstance(error, nextcord.Forbidden):
            message = "You do not have permission to perform this action."
        elif isinstance(error, commands.CommandOnCooldown):
            message = f"Command is on cooldown. Please wait {error.retry_after:.2f} seconds."
        elif isinstance(error, commands.MissingPermissions):
            message = "You are missing required permissions."
        elif isinstance(error, commands.MissingRequiredArgument):
            message = "Missing a required argument."
        else:
            logging.error(f"Unhandled command error: {error}")
            message = "An unexpected error occurred."

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
    except nextcord.errors.NotFound:
        logging.error("Failed to send error message, interaction not found or expired.")
    except Exception as e:
        logging.error(f"Unexpected error when handling command error: {e}")