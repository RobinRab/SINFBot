import discord 
from discord.ext import commands
from discord.ext.commands import MemberConverter, EmojiConverter

import io
import re
import json
import random
import aiohttp
import unicodedata
import datetime as dt
from typing import Any, Optional
from settings import DATA_DIR, MEMBER_ID, CUTIE_ID, OWNER_ID, LOG_PIC_CHANNEL_ID
from typing import TypedDict
#!!WARNING!! Any edits in this file can break commands

class UnexpectedValue(Exception):
	"""Raised when an unexpected value is given"""
	pass

def app_guild_cooldown(i:discord.Interaction) -> tuple:
	"""Used as the key for app_commands cooldown on the guild"""
	assert i.guild # assets i.guild is not None
	return (i.guild_id, i.guild.id)

async def GetLogLink(bot: commands.Bot, link:str) -> str:
	LogPic = bot.get_channel(LOG_PIC_CHANNEL_ID)
	if not isinstance(LogPic, discord.TextChannel):
		raise UnexpectedValue("LogPic was not found")

	# Add a User-Agent and be more robust when fetching remote content.
	headers = {"User-Agent": "Mozilla/5.0 (compatible; SINFBot/1.0)"}
	for fmt in [".gif", ".png", ".jpg", ".jpeg", ".webp", ".mp3", ".ogg", ".wav", ".flac", ".mp4", ".webm", ".mov"]:
		if fmt in link:
			try:
				async with aiohttp.ClientSession(headers=headers) as cs:
					async with cs.get(link, timeout=10) as resp: #type: ignore
						# only accept successful responses
						if resp.status != 200:
							continue
						data = await resp.read()
						if not data:
							continue
						buf = io.BytesIO(data)
						buf.seek(0)
						filename = f"file{fmt}"
						file = discord.File(buf, filename=filename)
						msg = await LogPic.send(file=file)
						return msg.attachments[0].url
			except Exception:
				# try the next format instead of bailing out completely
				continue
	# fallback image if nothing worked
	return "https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png"


async def get_member(ctx: commands.Context | discord.Interaction[commands.Bot], text: str) -> Optional[discord.Member]:
	"""Converts to a :class:`~discord.Member`."""
	if isinstance(ctx, discord.Interaction):
		# the commands requires a discord.Interaction[commands.Bot] type
		ctx = await commands.Context.from_interaction(ctx)

	try : #search by conv
		conv = MemberConverter()
		mem = await conv.convert(ctx, text)
		return mem
	except commands.errors.BadArgument : # search by name
		if not isinstance(ctx.guild, discord.Guild):
			raise UnexpectedValue("ctx.guild is not a Guild")
		members = [i for i in ctx.guild.members if not i.bot]
		for i in members : 
			if i.name == text :
				return i
			elif i.display_name == text :
				return i
			else :
				if simplify(text.lower()) in simplify(i.name.lower()):
					return i
				elif simplify(text.lower()) in simplify(i.display_name.lower()): 
					return i
	return None

async def get_emoji(ctx:commands.Context | discord.Interaction[commands.Bot], text:str) -> Optional[discord.Emoji] :
	"""Converts to a :class:`~discord.Emoji`."""
	if isinstance(ctx, discord.Interaction):
		ctx = await commands.Context.from_interaction(ctx)

	try : #search by conv
		conv = EmojiConverter()
		emoji = await conv.convert(ctx, text)
		return emoji
	except commands.errors.BadArgument : # search by name
		if not isinstance(ctx.guild, discord.Guild):
			raise UnexpectedValue("ctx.guild is not a Guild")

		emojis = [i for i in ctx.guild.emojis]
		for e in emojis : 
			if e.name == text :
				return e
			elif simplify(text.lower()) in simplify(e.name.lower()):
				return e
	return None


def simplify(text:str) -> str:
	"""Removes special characters from a string."""
	try:
		text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
	except NameError:
		pass
	return str(text)

def nospecial(text:str) -> str:
	"""Remove every character that is non-letter."""
	text = re.sub("[^a-zA-Z0-9_]+", "",simplify(text))
	return text


def get_data(path: Optional[str]=None) -> Any:
	"""Retrieve data from a JSON file using a path."""
	with open(f"{DATA_DIR}/datasinf.json", 'r') as f:
		data = json.load(f)

	if isinstance(path, str):
		for opt in path.split('/'):
			try: 
				data = data[opt]
			except KeyError:
				try: 
					data = data[int(opt)]
				except KeyError:
					raise UnexpectedValue(f"Key {opt} not found in data")
	return data

def upd_data(new_data: Any, path: Optional[str]=None) -> None:
	"""Update data in a JSON file using a path."""
	with open(f"{DATA_DIR}/datasinf.json", 'r') as f:
		data = json.load(f)

	if isinstance(path, str):
		keys = path.split('/')
		current_level = data
		for key in keys[:-1]:
			try: 
				current_level = current_level[key]
			except:
				current_level = current_level[int(key)]
		try: 
			current_level[keys[-1]] = new_data
		except:
			current_level[int(keys[-1])] = new_data
	else:
		data = new_data

	with open(f"{DATA_DIR}/datasinf.json", 'w') as f:
		json.dump(data, f, indent=4)

# permissions check
def is_member(inter:commands.Context | discord.Interaction) -> bool:
	"""Checks if the user is allowed to use the bot."""
	if isinstance(inter, commands.Context):
		ctx = inter
		if not isinstance(ctx.guild, discord.Guild):
			raise UnexpectedValue("ctx.guild is not a Guild")
		if not isinstance(ctx.author, discord.Member):
			raise UnexpectedValue("ctx.author is not a Member")

		return ctx.guild.get_role(MEMBER_ID) in ctx.author.roles
	else:
		if not isinstance(inter.guild, discord.Guild):
			raise UnexpectedValue("inter.guild is not a Guild")
		if not isinstance(inter.user, discord.Member):
			raise UnexpectedValue("inter.user is not a Member")
	
		return inter.guild.get_role(MEMBER_ID) in inter.user.roles

def is_cutie(inter:commands.Context | discord.Interaction) -> bool:
	"""Checks if the user is a cutie."""
	if isinstance(inter, commands.Context):
		ctx = inter

		if not isinstance(ctx.guild, discord.Guild):
			raise UnexpectedValue("ctx.guild is not a Guild")
		if not isinstance(ctx.author, discord.Member):
			raise UnexpectedValue("ctx.author is not a Member")

		return ctx.guild.get_role(CUTIE_ID) in ctx.author.roles or ctx.author.id == OWNER_ID
	else:
		if not isinstance(inter.guild, discord.Guild):
			raise UnexpectedValue("inter.guild is not a Guild")
		if not isinstance(inter.user, discord.Member):
			raise UnexpectedValue("inter.user is not a Member")
	
		return inter.guild.get_role(CUTIE_ID) in inter.user.roles or inter.user.id == OWNER_ID

def is_owner(inter: commands.Context | discord.Interaction ) -> bool:
	"""Checks if the user is the owner of the bot"""
	if isinstance(inter, commands.Context):
		ctx = inter

		if not isinstance(ctx.guild, discord.Guild):
			raise UnexpectedValue("ctx.guild is not a Guild")
		if not isinstance(ctx.author, discord.Member):
			raise UnexpectedValue("ctx.author is not a Member")

		return ctx.author.id == OWNER_ID
	else:
		if not isinstance(inter.guild, discord.Guild):
			raise UnexpectedValue("inter.guild is not a Guild")
		if not isinstance(inter.user, discord.Member):
			raise UnexpectedValue("inter.user is not a Member")
	
		return inter.user.id == OWNER_ID

async def embed_roulette(bot, inter : discord.Interaction, E : discord.Embed):
	url = random_avatar()
	if inter.user.avatar:
		url = inter.user.avatar.url
    
    # On utilise le bot passé en argument
	log_link = await GetLogLink(bot, url)
	E = discord.Embed(title="Roulette")
	E.set_author(name=inter.user.display_name, url=log_link)
    
	E.title = "Roulette"
	E.color = discord.Color.purple()
	E.set_footer(text="Roulette by Scylla and Ceisal")
	E.set_thumbnail(url="https://cdn.discordapp.com/attachments/1090314687620583467/1497886878081224734/Roulette_bot.png?ex=69ef275d&is=69edd5dd&hm=f78d2ca10f3e65af9b70e8ee30f479447be5093832a024ab3e1b177f6ec21dbd&")	
	E.color = discord.Color.purple()

	return E

def is_summer_time(date:dt.datetime) -> bool:
	date = dt.datetime.fromtimestamp(date.timestamp())
	start_dst = dt.datetime(date.year, 3, 31) - dt.timedelta(days=(dt.datetime(date.year, 3, 31).weekday() + 1) % 7)
	end_dst = dt.datetime(date.year, 10, 31) - dt.timedelta(days=(dt.datetime(date.year, 10, 31).weekday() + 1) % 7)
	return start_dst <= date < end_dst

def get_belgian_time() -> dt.datetime:
	# Get the current UTC time
	utc_time = dt.datetime.utcnow()

	# Calculate the offset for Belgian time utc+1
	belgium_offset = dt.timedelta(hours=1)
	if is_summer_time(utc_time): # utc+2
		belgium_offset += dt.timedelta(hours=1)

	# Apply the offset to the UTC time to get the Belgian time
	belgium_time = utc_time + belgium_offset

	return belgium_time

def get_user_data(user_id:int) -> dict:
	try: 
		user_data : dict = get_data(f"games/users/{user_id}")
	except :
		user_data = new_user()
	return user_data


def log(type:str, txt:str) -> None:
	"""Logs a message in the console and in the bot.log file."""
	with open(f"{DATA_DIR}/bot.log", 'a') as f:
		if type == "ERROR":
			print(f"[{dt.datetime.now().strftime('20%y-%m-%d %H:%M:%S')}] [{type.upper(): <8}] {txt}", file=f)
			print(f"\033[90;1m[{dt.datetime.now().strftime('20%y-%m-%d %H:%M:%S')}] \033[1;34m[{type.upper(): <8}] \u001b[0m {txt}")
		else:
			one, *two = txt.split()
			print(f"\033[90;1m[{dt.datetime.now().strftime('20%y-%m-%d %H:%M:%S')}] \033[1;34m[{type.upper(): <8}] \u001b[0;35m{one} \u001b[1;33m{' '.join(two)}\u001b[0m")
			print(f"[{dt.datetime.now().strftime('20%y-%m-%d %H:%M:%S')}] [{type: <8}] {txt}", file=f)

def random_avatar() -> str:
	return f"https://cdn.discordapp.com/embed/avatars/{random.randint(0,5)}.png"

#only use through SelectView.get_app_choice
class ChoiceSelect(discord.ui.Select):
	view: 'SelectView' #type: ignore

	def __init__(self, options: list[Any]) -> None:
		options = [discord.SelectOption(label=label, value=value) for label, value in options]
		super().__init__(options=options, placeholder="Choose an option", min_values=1, max_values=1)

	async def callback(self, inter:discord.Interaction): #type:ignore
		self.view.chosen = self.values[0]
		for option in self.options:
			if option.value == self.values[0]:
				option.default = True
		
		self.disabled = True
		await inter.response.edit_message(view=self.view)
		self.view.stop()

class SelectView(discord.ui.View):
	message: discord.Message | discord.InteractionMessage | discord.WebhookMessage

	def __init__(self, author_id: int, *, timeout:float) -> None:
		super().__init__(timeout=timeout)
		self.author_id: int = author_id

		self.chosen: str | None = None

	async def on_timeout(self):
		for child in self.children:
			if isinstance(child, discord.ui.Select):
				child.disabled = True
				child.placeholder = "Timed out"

		await self.message.edit(content="Expired", view=self)


	async def interaction_check(self, inter: discord.Interaction, /) -> bool:
		return inter.user.id == self.author_id

	@classmethod
	async def get_app_choice(cls, inter: discord.Interaction, choices: list[tuple[Any,Any]], *, timeout: float = 15.0, previous: Optional['SelectView']) -> tuple['SelectView', Optional[str]]:
		#create instance of SelectView
		view = cls(inter.user.id, timeout=timeout)
		if previous:
			view.message = previous.message
			for child in previous.children:
				view.add_item(child)

			view.add_item(ChoiceSelect(choices))
			time = f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>"
			await view.message.edit(view=view, content=f"Select a choice, timeout ({time})")

		else:
			view.add_item(ChoiceSelect(choices))
			time = f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>"
			await inter.response.send_message(f"Select a choice, timeout ({time})", view=view)
			view.message = await inter.original_response()

		await view.wait()
		return view, view.chosen

# games
class Bank(TypedDict):
	roses: int
	candies: int
	ideas: int

# TypedDict is just dict with type hints
class UserAccount(TypedDict):
	level: int
	timely: int # timestamp
	roses: int
	candies: int
	ideas: int
	tech: int
	bank: Bank
	achievements: list[str]
	wordle_en: dict[str, str]
	wordle_fr: dict[str, str]
	wordle_ge: dict[str, str]
	wordle_sp: dict[str, str]
	wordle_stats_fr : dict[str, int]
	wordle_stats_en : dict[str, int]
	wordle_stats_ge : dict[str, int]
	wordle_stats_sp : dict[str, int]
	villager_of_the_day: str
	villagers: list[str]
	has_got_daily_traveler : bool
	free_sunday_roll : int
	effects : list[str]
	lotto_guess : int
	wordle_ban : int
	
def new_user() -> UserAccount:
	return 	{
		"level": 0,
        "timely": 0,
        "roses": 0,
        "candies": 0,
        "ideas": 0,
        "tech": 0,
        "bank" : {
            "roses": 0,
            "candies": 0,
            "ideas": 0
        },
        "achievements": [],
        "wordle_en": {},
        "wordle_fr": {},
		"wordle_ge": {},
        "wordle_stats_en": {
            "todays_w_results_shown": 0
        },
        "wordle_stats_fr": {
            "todays_w_results_shown": 0
        },
		"wordle_stats_ge": {
            "todays_w_results_shown": 0
        },
        "wordle_stats_sp": {
            "todays_w_results_shown": 0
        },
        "villager_of_the_day": "",
        "villagers" : [],
        "has_got_daily_traveler" : False, 
		"free_sunday_roll" : 0, 
		"effects" : ["never_played"],
		"lotto_guess" : -1,
		"wordle_ban" : 0
}

def get_amount(cash: int, txt: str) -> Optional[int]:
	"""Translates a user input into an amount of cash. \n
	Accepts : \n
	- A number (e.g. 100) \n
	- "all" to bet all the cash \n
	- A percentage (e.g. 50%) to bet a percentage of the cash
	only used for the bank
	"""

	txt = txt.lower().replace(" ", "")
	# Check if txt is a valid number
	try: 
		return int(float(txt))
	except ValueError:
		pass
	

	#if txt == "all":
	#	return cash

	# Check if txt is a valid percentage
	#refaire elif si besoin
	if re.match(r'^([1-9]|[1-9]\d|100)%$', txt):
		percentage = int(txt[:-1]) / 100
		return int(cash * percentage)

	return None

def get_value(user_data:UserAccount) -> int:
	"""Calculates the value of the timely reward. \n
	Level 0 starts with 120. Each level grants 40% of that each time \n
	Each achievement adds 1% bonus, 2% if all achievements are unlocked"""
	level:int = user_data["level"]
	achievements:list = user_data["achievements"]
	return int((120 * (1 + (level/7)))*(1 + (len(achievements)/100)))

def get_collect_time(tech:int) -> int:
	base = dt.timedelta(hours=10).total_seconds()

	# 1% less for each tech level
	time = base - (base*tech)/100

	return int(dt.datetime.now().timestamp() + time)

def translate(txt: str) -> str:
	"""Translates choice emojis to their names"""
	return {"🌹": "roses","🍬": "candies","💡": "ideas"}[txt]

def get_acnh_data() -> dict[str, dict[str, str]]:
	"""Retrieve data from a JSON file using a path."""
	with open(f"{DATA_DIR}/villagers.json", 'r') as f:
		acnh = json.load(f)
	return acnh

def get_acnh_musics() -> dict[str, str]:
	"""Retrieve data from a JSON file using a path."""
	with open(f"{DATA_DIR}/acnh_musics.json", 'r') as f:
		acnh_musics = json.load(f)
	return acnh_musics

### UPDATE MSG
def new_update() -> discord.Embed:
	E = discord.Embed(color=discord.Color.green())
	E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1224344157854765096/upd.png?ex=661d265a&is=660ab15a&hm=0de144c03536daff3f69408db2013ea4e9088967ce9044fd8220791516d64283")
	E.title = "New update !"
	E.set_author(name="SINF illégal family bot")
	E.description = "- Roulette ! (At last :pray:)\n"
	E.description += "- Wordle debug\n"
	E.description += "- Wordle Spanish and German\n"
	E.description += "- Sunday Lotto \n"

	E.description += "\n\nThis message will be shown to everyone the first time they interact with the bot after this update"
	E.add_field(name="Authors", value="<@!627431499960156161> and <@!411881842439094272>")

	return E