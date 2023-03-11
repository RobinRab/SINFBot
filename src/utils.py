from __future__ import annotations

import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter, EmojiConverter

import io
import re
import json
import aiohttp
import unicodedata
import datetime as dt
from src.settings import DATA_DIR, CUTIE_ID
from typing import Any, Optional, Literal

#!!WARNING!! Any edits in this file can break commands

async def GetLogLink(bot:commands.Bot, link:str) -> str:
	"""Returns a permanant link of the file"""
	LogPic = bot.get_channel(709313685226782751)
	link = str(link)
	Fim = [".png",".jpg",".jpeg",".webp"]
	Fau = [".mp3",".ogg",".wav",".flac"]
	Fvi = [".mp4",".webm",".mov"]
	LL = [Fim,Fau,Fvi,".gif"]
	for n in LL :
		for i in n :
			if i in link :
				Format = i
				if i in Fim :
					Format = ".png"
				elif i in Fau : 
					Format = ".mp3"
				elif i in Fvi :
					Format = ".mp4"
				else : 
					Format = ".gif"
				try : 
					async with aiohttp.ClientSession() as cs:
						async with cs.get(link) as resp:
							File = discord.File(io.BytesIO(await resp.content.read()),filename=f"file{Format}")
							M = await LogPic.send(file=File)
							return M.attachments[0].url
				except :
					return "https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png"
	return "https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png"

async def get_member(ctx:commands.Context | discord.Interaction, text:str) -> discord.Member:
	"""Converts to a :class:`~discord.Member`."""
	try : #search by conv
		conv = MemberConverter()
		mem = await conv.convert(ctx, text)
		return mem
	except commands.errors.BadArgument : # search by name
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

async def get_emoji(ctx:commands.Context, text:str) -> discord.Emoji :
	"""Converts to a :class:`~discord.Emoji`."""
	try : #search by conv
		conv = EmojiConverter()
		emoji = await conv.convert(ctx, text)
		return emoji
	except commands.errors.BadArgument : # search by name
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
		text = unicode(text, 'utf-8') #type: ignore
	except NameError:
		pass
	text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
	return str(text)

def nospecial(text:str) -> str:
	"""Remove every character that is non-letter."""
	text = re.sub("[^a-zA-Z0-9_]+", "",simplify(text))
	return text

def get_data(*opts:Optional[str]) -> Any:
	"""Retrieve data from a JSON file."""

	with open(f"{DATA_DIR}/datasinf.json", 'r') as f:
		data = json.load(f)

	for opt in opts:
		data = data[opt]

	return data

def upd_data(new_data:Any, *keys:Optional[str]) -> None:
	"""Update data in a JSON file."""

	with open(f"{DATA_DIR}/datasinf.json", 'r') as f:
		data = json.load(f)

	if not keys:
		data = new_data
	else:
		current_level = data
		for key in keys[:-1]:
			current_level = current_level[key]
		current_level[keys[-1]] = new_data

	with open(f"{DATA_DIR}/datasinf.json", 'w') as f:
		json.dump(data, f, indent=4)

def is_cutie(inter: discord.Interaction | commands.Context) -> bool:
	"""Check if the user is a cutie."""
	if isinstance(inter, commands.Context):
		ctx = inter
		return ctx.guild.get_role(CUTIE_ID) in ctx.author.roles or ctx.author.id == 346945067975704577
	else:
		return inter.guild.get_role(CUTIE_ID) in inter.user.roles or inter.user.id == 346945067975704577

def sort_bdays(data : dict) -> dict:
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

months = Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
activities = Literal["playing", "watching", "listening", "stop"]
statuses = Literal["online", "idle", "dnd", "offline"]

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

#only use through SelectView.get_app_choice
class ChoiceSelect(discord.ui.Select):
	view: SelectView

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
	async def get_app_choice(cls, inter: discord.Interaction, choices: list[tuple[Any,Any]], *, timeout: float = 15.0, previous: Optional[SelectView]) -> tuple[SelectView, Optional[str]]:
		#create instance of SelectView
		view = cls(inter.user.id, timeout=timeout)
		if previous:
			view.message = previous.message
			for child in previous.children:
				view.add_item(child)

			view.add_item(ChoiceSelect(choices))
			await view.message.edit(view=view)

		else:
			view.add_item(ChoiceSelect(choices))
			time = f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>"
			await inter.response.send_message(f"Select a choice, timeout ({time})", view=view)
			view.message = await inter.original_response()

		await view.wait()
		return view, view.chosen

