import discord
from discord.ext import commands

from utils import get_data, simplify
from settings import ANON_SAYS_ID, GENERAL_ID

import re

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


async def setup(bot:commands.Bot):
	await bot.add_cog(Message(bot))