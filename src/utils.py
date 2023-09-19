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
	
	for format in [".gif",".png",".jpg",".jpeg",".webp", ".mp3",".ogg",".wav",".flac", ".mp4",".webm",".mov"]:
		if format in link:
			try:
				async with aiohttp.ClientSession() as cs:
					async with cs.get(link) as resp:
						file = discord.File(io.BytesIO(await resp.content.read()), filename=f"file{format}")
						msg = await LogPic.send(file=file)
						return msg.attachments[0].url
			except:
				break
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
				data = data[int(opt)]
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

def is_summer_time() -> bool:
	"""Checks if it's summer time."""
	now = dt.datetime.now()
	debut_heure_dete = dt.datetime(now.year, 3, 31) - dt.timedelta(days=dt.datetime(now.year, 3, 31).weekday() + 1)
	fin_heure_dete = dt.datetime(now.year, 10, 31) - dt.timedelta(days=dt.datetime(now.year, 10, 31).weekday() + 1)

	return debut_heure_dete <= now <= fin_heure_dete


def sort_bdays(data : dict) -> list[tuple[str, dt.datetime]]:
	"""Trie les anniversaires par dates."""
	year = dt.datetime.now().year
	birthdays = {}

	for user in data.keys():

		date = dt.datetime(year, data[user]["month"], data[user]["day"])
		if date < dt.datetime.now():
			date = dt.datetime(year+1, data[user]["month"], data[user]["day"])


		def is_heure_dete():
			# Récupérer la date actuelle
			now = dt.datetime.now()

			# Récupérer le dernier dimanche de mars de cette année
			debut_heure_dete = dt.datetime(now.year, 3, 31) - dt.timedelta(days=dt.datetime(now.year, 3, 31).weekday() + 1)

			# Récupérer le dernier dimanche d'octobre de cette année
			fin_heure_dete = dt.datetime(now.year, 10, 31) - dt.timedelta(days=dt.datetime(now.year, 10, 31).weekday() + 1)

			# Vérifier si nous sommes actuellement entre les deux dates
			return debut_heure_dete <= now < fin_heure_dete

		#diff horaire
		diff = 1
		if is_heure_dete():
			diff = 2

		birthdays[user] = date - dt.timedelta(hours=diff)

	return sorted(birthdays.items(), key=lambda x: birthdays[x[0]])

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
	view: 'SelectView'

	def __init__(self, options: list[Any]) -> None:
		options = [discord.SelectOption(label=label, value=value) for label, value in options]
		super().__init__(options=options, placeholder="Choose an option", min_values=1, max_values=1)

	async def callback(self, inter:discord.Interaction):
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
def new_user():
	return {
		"level"   : 0,
		"timely"  : int(dt.datetime.now().timestamp()),
		"roses"   : 0,
		"candies" : 0,
		"ideas"   : 0,
		"bank"    : {
			"roses"   : 0,
			"candies" : 0,
			"ideas"   : 0
		},
		"achievements" : []
	}

def get_amount(cash: int, txt: str) -> Optional[int]:
	txt = txt.lower().replace(" ", "")
	# Check if txt is a valid number
	try: 
		return int(float(txt))
	except ValueError:
		pass

	if txt == "all":
		return cash

	# Check if txt is a valid percentage
	elif re.match(r'^([1-9]|[1-9]\d|100)%$', txt):
		percentage = int(txt[:-1]) / 100
		return int(cash * percentage)

	return None

def get_value(user_data:dict) -> int:
	"""Calculates the value of the timely reward. \n
	Level 0 starts with 150. Each level grants 40% of that each time \n
	Each achievement adds 1% bonus, 2% if all achievements are unlocked"""
	level:int = user_data["level"]
	achievements:list = user_data["achievements"]
	return int((150 * (1 + (level/4)))*(1 + (len(achievements)/100)))

def translate(txt: str) -> str:
	"""Translates choice emojis to their names"""
	return {"🌹": "roses","🍬": "candies","💡": "ideas"}[txt]
