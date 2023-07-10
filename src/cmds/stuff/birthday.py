import discord
from discord import app_commands
from discord.ext import commands, tasks

import asyncio
import datetime as dt
from typing import Optional, Literal
from settings import GENERAL_ID
from utils import UnexpectedValue, is_summer_time, is_member, get_data, upd_data, sort_bdays

months = Literal["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


class Birthday(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

		birthdays_loop.start(bot=self.bot)

	@app_commands.command(description="Adds your birthday!")
	@app_commands.describe(day="Day of birth", month="Month of birth", year="Year of birth")
	@app_commands.check(is_member)
	@app_commands.guild_only()
	async def set_birthday(self, inter:discord.Interaction, day:int, month:months, year:int):
		months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
		name = str(inter.user.id)

		data : dict = get_data("birthday")

		if name in data.keys():
			await inter.response.send_message(f"You already set your birthday", ephemeral=True)
			return
		
		MIN = dt.datetime.now().year - 100
		MAX = dt.datetime.now().year - 13

		if not (MIN < year < MAX):
			await inter.response.send_message("This date does not exist", ephemeral=True)
			return
		
		try:
			month_index = months.index(month) + 1
			birthday = dt.datetime(year, month_index, day)
		except ValueError:
			await inter.response.send_message("This date does not exist")
			return

		data[name] = {"year": year, "month": month, "day": day}
		upd_data(data, "birthday")

		birthdays_loop.restart(self.bot)

		await inter.response.send_message(f"{inter.user.mention}'s birthday has been set on the {birthday.strftime('%d/%m/%Y')}")

	@app_commands.command(description="Displays everyone's birthday")
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	async def birthdays(self, inter:discord.Interaction, user:Optional[discord.Member]):
		if not isinstance(inter.guild, discord.Guild):
			raise UnexpectedValue("inter.guild is not a discord.Guild")


		data : dict = get_data("birthday")
		year = dt.datetime.now().year

		if isinstance(user, discord.Member):
			if str(user.id) not in data.keys():
				await inter.response.send_message(f"**{user.name}** has not set their birthday yet")
				return

			date = dt.datetime(year, data[str(user.id)]["month"], data[str(user.id)]["day"])
			if date < dt.datetime.now():
				date = dt.datetime(year+1, data[str(user.id)]["month"], data[str(user.id)]["day"])

			left = date - dt.datetime.now()

			await inter.response.send_message(f"**{user.name}** has their birthday on the {date.strftime('%d/%m/%Y')} in **{left.days+1}d**")
		else:
			birthdays = sort_bdays(data)

			embed = discord.Embed(title="Birthdays list", color=discord.Color.blurple())
			embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1074650207796609115/file.png")

			txt = ""
			for Bduser, date in birthdays:

				user = inter.guild.get_member(int(Bduser))

				if user is None:
					continue
			
				left = date - dt.datetime.now()

				txt += f"{user.mention} - {date.strftime('%d/%m/%Y')} dans **{left.days+1}d**\n"

			embed.description = txt
			await inter.response.send_message(embed=embed)

@tasks.loop()
async def birthdays_loop(*, bot:commands.Bot):
	channel = bot.get_channel(GENERAL_ID)
	if not isinstance(channel, discord.TextChannel):
		raise UnexpectedValue("channel is not a discord.TextChannel")

	while 1:
		data : dict = get_data("birthday")

		birthdays = sort_bdays(data)

		for user, date in birthdays:
			user = bot.get_user(int(user))

			if user is None:
				continue

			left = (date - dt.datetime.now()).total_seconds()
			left -= 3600 # -1h, winter time
			if is_summer_time():
				left -= 3600 # -2h for summer time (7200)
			left += 1 # somehow it is 1 second early

			await asyncio.sleep(left)

			year = dt.datetime.now().year
			age = year - data[str(user.id)]["year"]

			await channel.send(f"Happy birthday {user.mention}, You are {age} years old today! :tada:")

			await asyncio.sleep(43200) #sleep 12h to skip timezones issudes

async def setup(bot:commands.Bot):
	await bot.add_cog(Birthday(bot))
