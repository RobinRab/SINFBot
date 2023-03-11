import discord
from discord import app_commands
from discord.ext import commands

import datetime as dt
from src.utils import GetLogLink, log, get_data

#!! all functions added in this class will be added as context menu
#!! all functions added in this class will be added as context menu


class GeneralCM(commands.Cog):
	#! there is one more app in tetrio.py
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		#adds all functions in this class to the context menu
		for attribute_name in GeneralCM.__dict__:
			if not attribute_name.startswith("_"):
				attr = getattr(self, attribute_name)
				if '__call__' in dir(attr):
					name = attribute_name.replace("_", " ").title()
					log("INFO", f"adding {name} to context menu")

					self.bot.tree.add_command(app_commands.ContextMenu( 
						name=name,
						callback=attr
					))

	async def avatar(self, inter:discord.Interaction, user:discord.Member):
		P = "**Here's your avatar :**\n"
		D = ""

		for i in ["png","jpg","jpeg","webp"] :
			#Format = user.display_avatar(format=i)
			Format = str(user.display_avatar.with_format(i))
			D = f"{D}[{i}]({Format}), "

		if inter.user != user :
			P = f"**Here is {user}`s avatar **\n"

		if user.display_avatar.is_animated():
			D = "[gif]({})--".format(user.display_avatar.with_format("gif"))

		link = await GetLogLink(self.bot, user.display_avatar)
		embed = discord.Embed(colour=discord.Colour.from_rgb(0,0,0) ,title=P,description=f"**{D[:-2]}**")
		embed.url=link
		embed.set_image(url=link)
		embed.set_footer(text=f"Requested by : {inter.user}")
		
		await inter.response.send_message(embed=embed)

	async def birthday(self, inter:discord.Interaction, user:discord.Member):
		data : dict = get_data("birthday")
		year = dt.datetime.now().year

		if str(user.id) not in data.keys():
			await inter.response.send_message(f"**{user}** has not added their birthday")
			return

		date = dt.datetime(year, data[str(user.id)]["month"], data[str(user.id)]["day"])
		if date < dt.datetime.now():
			date = dt.datetime(year+1, data[str(user.id)]["month"], data[str(user.id)]["day"])

		left = date - dt.datetime.now()

		await inter.response.send_message(f"**{user}** has his birthday the {date.strftime('%d/%m/%Y')} in **{left.days+1}d**")


async def setup(bot:commands.Bot):
	await bot.add_cog(GeneralCM(bot))