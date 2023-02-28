import discord
from discord import app_commands
from discord.ext import commands, tasks

import asyncio
import datetime as dt
from settings import GENERAL_ID
from utils import get_data, upd_data, sort_bdays, months

class Birthday(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Ajoute ton anniversaire")
	@app_commands.describe(day="Ton jour de naissance", month="Ton mois de naissance", year="Ton année de naissance")
	async def set_birthday(self, inter:discord.Interaction, day:int, month:months, year:int):
		months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]
		name = str(inter.user.id)

		data : dict = get_data("birthday")

		if name in data.keys():
			await inter.response.send_message(f"Vous avez déjà ajouté votre anniversaire", ephemeral=True)
			return
		
		MIN = dt.datetime.now().year - 100
		MAX = dt.datetime.now().year - 13

		if not (MIN < year < MAX):
			await inter.response.send_message("Cette date n'existe pas", ephemeral=True)
			return
		
		try:
			month = months.index(month) + 1
			birthday = dt.datetime(year, month, day)
		except ValueError:
			await inter.response.send_message("Cette date n'existe pas")
			return

		data[name] = {"year": year, "month": month, "day": day}
		upd_data(data, "birthday")
		self.birthdays.restart()

		await inter.response.send_message(f"L'anniversaire de {inter.user.mention} a été ajouté le {birthday.strftime('%d/%m/%Y')}")

	@app_commands.command(description="Affiche les anniversaires")
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	async def birthdays(self, inter:discord.Interaction, user:discord.Member=None):

		data : dict = get_data("birthday")
		year = dt.datetime.now().year

		if user is None:
			birthdays = sort_bdays(data)

			embed = discord.Embed(title="Anniversaires", color=discord.Color.blurple())
			embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1074650207796609115/file.png")

			txt = ""
			for user, date in birthdays:
				user = inter.guild.get_member(int(user))

				if user is None:
					continue
			
				left = date - dt.datetime.now()

				txt += f"{user.mention} - {date.strftime('%d/%m/%Y')} dans **{left.days+1}j**\n"

			embed.description = txt
			await inter.response.send_message(embed=embed)

		else:
			if str(user.id) not in data.keys():
				await inter.response.send_message(f"**{user}** n'a pas ajouté son anniversaire")
				return

			date = dt.datetime(year, data[str(user.id)]["month"], data[str(user.id)]["day"])
			if date < dt.datetime.now():
				date = dt.datetime(year+1, data[str(user.id)]["month"], data[str(user.id)]["day"])

			left = date - dt.datetime.now()

			await inter.response.send_message(f"**{user}** a son anniversaire le {date.strftime('%d/%m/%Y')} dans **{left.days+1}j**")

	@tasks.loop()
	async def _birthdays(bot:commands.Bot):
		channel = bot.get_channel(GENERAL_ID)
		while 1:
			data : dict = get_data("birthday")

			birthdays = sort_bdays(data)

			for user, date in birthdays:
				user = bot.get_user(int(user))

				if user is None:
					continue

				left = (date - dt.datetime.now()).total_seconds()
				left -= 3600 # 1h, -2h for summer time (7200)
				left += 1 # somehow it is 1 second early

				await asyncio.sleep(left)

				year = dt.datetime.now().year
				age = year - data[str(user.id)]["year"]

				await channel.send(f"Joyeux anniversaire {user.mention}, tu fêtes aujourd'hui tes {age} ans! :tada:")

				await asyncio.sleep(43200) #sleep 12h by safety (2h at least to skip timezone issues)

async def setup(bot:commands.Bot):
	await bot.add_cog(Birthday(bot))
