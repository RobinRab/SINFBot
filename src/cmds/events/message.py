import discord
from discord.ext import commands

from utils import UnexpectedValue, get_data, simplify
from settings import ANON_SAYS_ID, GENERAL_ID

import io
import re
import aiohttp
import requests


class Message(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot
	
	@commands.Cog.listener()
	async def on_message(self, message : discord.Message):
		if message.author.bot :
			return

		#ctx = await client.get_context(message)

		#resp command
		if 1:
			data = get_data()

			for clef in data["phrases"]:
				if re.search(r'\W',clef["mot"][0]) or re.search(r"\W",clef["mot"][-1]) : #if non-aplhanumeric (start/end) : needs to be handled differently
					pat = r"(\W|^)" + re.escape(str(simplify(clef['mot'].lower()))) + r"(\W|$)"
				else :
					pat = r"\b" + re.escape(str(simplify(clef['mot'].lower()))) + r"\b"

				if re.search(pat,simplify(message.content).lower()) :
					await message.channel.send(clef["text"],delete_after=clef["time"])
					break

		#anon says
		if message.channel.id == ANON_SAYS_ID:
			if not isinstance(message.guild, discord.Guild):
				raise UnexpectedValue("message.guild is a guild")
			general = message.guild.get_channel(GENERAL_ID)
			if not isinstance(general, discord.TextChannel):
				raise UnexpectedValue("general is a text channel")

			Files= []
			try :
				for link in message.attachments:
					link = link.url
					name = link.split("/")[-1].split(".")[0]
					Format = link.split(".")[-1]
					requests.get(link)
					async with aiohttp.ClientSession() as cs:
						async with cs.get(link) as resp:
							Files.append(discord.File(io.BytesIO(await resp.content.read()),filename=f"{name}.{Format}"))

				await general.send(content=message.content, files=Files)
			except:
				await general.send("Désolé, une erreur est survenue")



async def setup(bot:commands.Bot):
	await bot.add_cog(Message(bot))