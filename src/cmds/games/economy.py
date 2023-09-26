import discord 
from discord import app_commands
from discord.ext import commands

import datetime as dt
from typing import Optional, Literal

from utils import get_data, upd_data, is_cutie, GetLogLink, new_user, get_amount, translate, get_value, get_collect_time

class Economy(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Displays ressources of a user")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(user="The user to display, default is you")
	async def balance(self, inter:discord.Interaction, user:Optional[discord.Member]):
		await inter.response.defer()

		# if not target specified, target is the user
		target = inter.user
		if user is not None:
			target = user

		E = discord.Embed()
		E.color = discord.Color.blurple()
		E.set_author(name=target.name, icon_url=await GetLogLink(self.bot, target.display_avatar.url))

		try: 
			user_data : dict = get_data(f"games/users/{target.id}")
		except :
			E.description = f"{target.mention} has never played"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)

		level = int(user_data["level"])
		E.title = f"balance [{level} ⭐] + {user_data['tech']} :gear: "
		E.description  = f"- **{user_data['roses']}🌹**\n"
		E.description += f"- **{user_data['candies']}🍬**\n"
		E.description += f"- **{user_data['ideas']}💡**\n"
		await inter.followup.send(embed=E)

	@app_commands.command(description="Collects your ressources each 12h")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def collect(self, inter:discord.Interaction):
		await inter.response.defer()

		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		# user_id : {user data}
		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			user_data = new_user()

		next_timely:int = user_data["timely"]

		value = get_value(user_data)

		if next_timely > dt.datetime.now().timestamp():
			E.description = f"{inter.user.mention}, Come back to claim your {value}🌹 <t:{next_timely}:R>"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)

		time_to_wait = get_collect_time(is_cutie(inter), user_data["tech"])

		# add the data
		user_data["timely"] = time_to_wait
		user_data["roses"] += value

		upd_data(user_data, f"games/users/{inter.user.id}")

		E.description = f"{inter.user.mention}, You claimed your {value}🌹 roses! Come back <t:{time_to_wait}:R> to claim it again!"
		E.color = discord.Color.green()
		await inter.followup.send(embed=E)

	@app_commands.command(description="Allows you to upgrade your level")
	@app_commands.checks.cooldown(1, 3, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def levelup(self, inter:discord.Interaction):
		await inter.response.defer()

		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.color = discord.Color.green()

		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You can't level up, you have never played"
			return await inter.followup.send(embed=E)

		level = user_data["level"] + 1
		if level < 10:
			price = int((level/1.25) * 1000)
		else:
			price = int((((level**2)/25) + 4) * 1000)

		if user_data["roses"] < price:
			E.description = f"{inter.user.mention}, You need {price}🌹 to level up"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)
		
		user_data["roses"] -= price
		user_data["level"] += 1
		upd_data(user_data, f"games/users/{inter.user.id}")

		E.description = f"{inter.user.mention}, You are now level **{level}**!"

		await inter.followup.send(embed=E)

	@app_commands.command(description="Allows you to upgrade your tech level")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def tech(self, inter:discord.Interaction):
		await inter.response.defer()

		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.color = discord.Color.green()

		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You can't upgrade your tech, you have never played"
			return await inter.followup.send(embed=E)

		tech = user_data["tech"] + 1
		price = tech*10

		if tech > 10:
			E.description = f"{inter.user.mention}, You are already max tech"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)

		if user_data["ideas"] < price:
			E.description = f"{inter.user.mention}, You need {price}💡 to upgrade your tech"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)
		
		user_data["ideas"] -= price
		user_data["tech"] += 1
		upd_data(user_data, f"games/users/{inter.user.id}")

		E.description = f"{inter.user.mention}, You are now tech **{tech}**:gear:!"

		await inter.followup.send(embed=E)


class Bank(app_commands.Group):
	def __init__(self, bot:commands.Bot, *args, **kwargs):
		self.bot : commands.Bot = bot
		super().__init__(*args, **kwargs)

	@app_commands.command(description="Deposit into your bank account")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(money="The amount to deposit", currency="The currency to deposit")
	@app_commands.rename(money="amount")
	async def deposit(self, inter:discord.Interaction, money:str, currency:Literal["🌹", "🍬", "💡"]):
		await inter.response.defer()

		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.color = discord.Color.green()

		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You can't manage your bank account you have never played"
			return await inter.followup.send(embed=E)

		# translate the user request into a number
		amount = get_amount(user_data[translate(currency)], money)

		if amount is None or amount < 0:
			E.description = f"{inter.user.mention}, You need to deposit a valid amount of {currency}"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)
		elif amount == 0:
			E.description = f"{inter.user.mention}, You don't have any {currency} to deposit"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)
		
		user_data[translate(currency)] -= amount
		user_data["bank"][translate(currency)] += amount
		upd_data(user_data, f"games/users/{inter.user.id}")

		E.description = f"{inter.user.mention}, You deposited {amount}{currency} in your bank account"
		return await inter.followup.send(embed=E)

	@app_commands.command(description="Withdraw from your bank account")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(money="The amount to withdraw", currency="The currency to withdraw")
	@app_commands.rename(money="amount")
	async def withdraw(self, inter:discord.Interaction, money:str, currency:Literal["🌹", "🍬", "💡"]):
		await inter.response.defer()

		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.color = discord.Color.green()

		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You can't manage your bank account you have never played"
			return await inter.followup.send(embed=E)

		# translate the user request into a number
		amount = get_amount(user_data["bank"][translate(currency)], money)

		if amount is None or amount < 0:
			E.description = f"{inter.user.mention}, You need to withdraw a valid amount of {currency}"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)
		elif amount == 0:
			E.description = f"{inter.user.mention}, You don't have any {currency} to withdraw"
			E.color = discord.Color.red()
			return await inter.followup.send(embed=E)
		
		user_data[translate(currency)] += amount
		user_data["bank"][translate(currency)] -= amount
		upd_data(user_data, f"games/users/{inter.user.id}")

		E.description = f"{inter.user.mention}, You withdrew {amount}{currency} from your bank account"
		await inter.followup.send(embed=E)

	@app_commands.command(description="Check your bank account")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def check(self, inter:discord.Interaction):
		await inter.response.defer(ephemeral=True)

		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.color = discord.Color.green()

		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You can't manage your bank account you have never played"
			return await inter.followup.send(embed=E)

		E.title = f"bank"
		E.description  = f"- **{user_data['bank']['roses']}🌹**\n"
		E.description += f"- **{user_data['bank']['candies']}🍬**\n"
		E.description += f"- **{user_data['bank']['ideas']}💡**\n"

		await inter.followup.send(embed=E, ephemeral=True)


async def setup(bot:commands.Bot):
	await bot.add_cog(Economy(bot))
	bot.tree.add_command(Bank(bot, name="bank",description="Manage your bank account"))