import os

import pathlib
import logging
import logging.handlers
from dotenv import load_dotenv

load_dotenv()
BOT_PREFIX = os.getenv("BOT_PREFIX")
DISCORD_API_TOKEN = os.getenv("DISCORD_API_TOKEN")
BOT_ID = os.getenv("BOT_ID") 
GUILD_ID = os.getenv("GUILD_ID")
ERROR_CHANNEL_ID = os.getenv("ERROR_CHANNEL_ID")
ANON_SAYS_ID = os.getenv("ANON_SAYS_ID")
GENERAL_ID = os.getenv("GENERAL_ID")
CONFESSION_ID = os.getenv("CONFESSION_ID")
CUTIE_ID = os.getenv("CUTIE_ID")

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