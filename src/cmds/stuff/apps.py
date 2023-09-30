import discord
from discord import app_commands
from discord.ext import commands

import datetime as dt
from utils import GetLogLink, log, get_data, get_belgian_time, is_summer_time

#!! all functions added in this class will be added as context menu
#!! all functions added in this class will be added as context menu
class GeneralCM(commands.Cog):
	#! there's one more CM in tetrio.py
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

		for i in ("png","jpg","jpeg","webp") :
			Format = str(user.display_avatar.with_format(i))
			D = f"{D}[{i}]({Format}), "

		if inter.user != user :
			P = f"**Here is {user}`s avatar **\n"

		if user.display_avatar.is_animated():
			D = "[gif]({})--".format(user.display_avatar.with_format("gif"))

		link = await GetLogLink(self.bot, str(user.display_avatar))
		embed = discord.Embed(colour=discord.Colour.from_rgb(0,0,0) ,title=P,description=f"**{D[:-2]}**")
		embed.url=link
		embed.set_image(url=link)
		embed.set_footer(text=f"Requested by : {inter.user.name}")
		
		await inter.response.send_message(embed=embed, ephemeral=True)

	async def birthday(self, inter:discord.Interaction, user:discord.Member):
		try:
			data : dict = get_data(f"birthday/{user.id}")
		except KeyError:
			return await inter.response.send_message(f"**{user.name}** has not set their birthday yet", ephemeral=True)

		year = get_belgian_time().year
		month = int(data["month"])
		day = int(data["day"])

		diff = dt.timedelta(hours=2 if is_summer_time() else 1)

		date = dt.datetime(year, month, day, tzinfo=dt.timezone.utc) - diff
		if date < dt.datetime.now(tz=dt.timezone.utc) - diff:
			year += 1
			date = dt.datetime(year+1, month, day, tzinfo=dt.timezone.utc) - diff

		await inter.response.send_message(f"**{user.name}** has his birthday the {day}/{month}/{year} <t:{int(date.timestamp())}:R>", ephemeral=True)


async def setup(bot:commands.Bot):
	await bot.add_cog(GeneralCM(bot))