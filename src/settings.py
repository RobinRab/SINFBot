import os

import pathlib
import logging
import logging.handlers
from dotenv import load_dotenv

load_dotenv()
# bot setup variables
BOT_PREFIX = os.getenv("BOT_PREFIX") or "!"
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN") or ""

# id of the guild the bot is in
GUILD_ID = int(os.getenv("GUILD_ID") or 0)
# id of the channel the bot will send errors to
ERROR_CHANNEL_ID = int(os.getenv("ERROR_CHANNEL_ID") or 0)
# id of the log channel for GetLogLink
LOG_PIC_CHANNEL_ID = int(os.getenv("LOG_PIC_CHANNEL_ID") or 0)

# used to display birthdays
GENERAL_ID = int(os.getenv("GENERAL_ID") or 0)
# used to send confessions
CONFESSION_ID = int(os.getenv("CONFESSION_ID") or 0)
# only channel to allow bot commands
BOT_CHANNEL_ID = int(os.getenv("BOT_CHANNEL_ID") or 0)

# the 3 status roles a member can have
MEMBER_ID = int(os.getenv("MEMBER_ID") or 0)
CUTIE_ID = int(os.getenv("CUTIE_ID") or 0)
OWNER_ID = int(os.getenv("OWNER_ID") or 0)

BASE_DIR = pathlib.Path(__file__).parent
CMDS_DIR = BASE_DIR / "cmds"
DATA_DIR = BASE_DIR / "data"

directories = []
extensions = []
for _, folders, _ in os.walk(CMDS_DIR):
    for folder in folders:
        if folder.startswith('_'):
            continue

        directories.append(folder)

        dir = CMDS_DIR / folder
        for file in dir.iterdir():
            if file.name.endswith(".py"):
                extensions.append(f"cmds.{folder}.{file.name[:-3]}")


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='src/data/bot.log',
    encoding='utf-8',
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)