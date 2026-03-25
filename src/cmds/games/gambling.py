import discord 
from discord import app_commands
from discord.ext import commands

import random
import datetime as dt
from typing import Literal
import re

from utils import UserAccount, get_data, upd_data, GetLogLink, new_user
# new user only used to fake an account and avoid using a None type check

class Gambling(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Rolls a dice")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet")
	async def roll(self, inter:discord.Interaction, bet:str):
		GH = GamblingHelper(self.bot)
		await GH.roll(inter, bet)

	@app_commands.command(description="Flips a coin")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet", guess="Your guess")
	async def flip(self, inter:discord.Interaction, bet:str, guess:Literal["heads", "tails"]):
		GH = GamblingHelper(self.bot)
		await GH.flip(inter, bet, guess)

	@app_commands.command(description="Lucky Ladder, each step has equal chances of occuring")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet")
	async def ladder(self, inter:discord.Interaction, bet:str):
		GH = GamblingHelper(self.bot)
		await GH.ladder(inter, bet)

	@roll.autocomplete("bet")
	@flip.autocomplete("bet")
	@ladder.autocomplete("bet")
	async def gamble_autocomplete(self, inter:discord.Interaction, current:str):
		try :
			user_data : UserAccount = get_data(f"games/users/{inter.user.id}")
		except :
			if current.isdigit():
				return [app_commands.Choice(name=f"({current}🌹)", value=f"({current}🌹)")]
			return []

		roses = user_data["roses"]

		options:list[str] = []

		if current.isdigit() and int(current) <= roses:
			options.append(f"{current}🌹")

		# if user wants all
		if current.startswith("25%"):
			options.extend([
				f"25% ({roses//4}🌹)",
				f"10% ({roses//10}🌹)",
				f"50% ({roses//2}🌹)",
				f"all ({roses}🌹)", 
			])
		elif current.startswith("50%"):
			options.extend([
				f"50% ({roses//2}🌹)",
				f"10% ({roses//10}🌹)",
				f"25% ({roses//4}🌹)",
				f"all ({roses}🌹)", 
			])
		elif current.startswith("a"):
			options.extend([
				f"all ({roses}🌹)",
				f"10% ({roses//10}🌹)",
				f"25% ({roses//4}🌹)",
				f"50% ({roses//2}🌹)"
			])
		else:
			options.extend([
				f"10% ({roses//10}🌹)",
				f"25% ({roses//4}🌹)",
				f"50% ({roses//2}🌹)",
				f"all ({roses}🌹)"
			])

		return [app_commands.Choice(name=opt, value=opt) for opt in options]


class GamblingHelper():
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot

	async def is_allowed_to_bet(self, inter:discord.Interaction, bet:str) -> tuple[int, discord.Embed, UserAccount]:
		E = discord.Embed()
		E.color = discord.Color.green()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		try :
			user_data : UserAccount = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You don't have any 🌹, get some using **/collect**"
			E.color = discord.Color.red()
			return 0, E, new_user()
		
		# if the user sent the command too quickly
		if '🌹' not in bet:
			bet += "🌹"

		amount_match = re.search(r"(\d+)🌹", bet)
		if amount_match:
			amount = int(amount_match.group(1))
		else: 
			amount = None

		if amount is None or amount < 0:
			E.description = f"{inter.user.mention}, You need to bet a valid amount of 🌹"
			E.color = discord.Color.red()
			return 0, E, user_data

		if amount < 2:
			E.description = f"{inter.user.mention}, You need to bet at least 2🌹"
			E.color = discord.Color.red()

		elif user_data["roses"] < amount:
			E.description = f"{inter.user.mention}, You don't have enough 🌹"
			E.color = discord.Color.red()

		return amount, E, user_data

	async def roll(self, inter:discord.Interaction, bet:str):
		await inter.response.defer()

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)
		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)

		r = random.randint(1,100)
		E.add_field(name="Roll:", value=f"**{r}**")
		cash=amount
		if r == 100:
			cash = amount*10
			E.description = f"{inter.user.mention}, You rolled a 100 and won **{cash}🌹!** 👑"
			E.color = discord.Color.gold()
		elif r >= 90:
			cash = amount*4
			E.description = f"{inter.user.mention}, You rolled 90 or above and won x4 **{cash}🌹!** 🎯"
		elif r >= 70:
			cash = amount*2
			E.description = f"{inter.user.mention}, You rolled 70 or above and won x2 **{cash}🌹!** 🎉"
		elif r==1:
			E.description = f"{inter.user.mention}, You rolled a 1 and kept your **{cash}🌹!** ✨"
			E.color = discord.Color.dark_purple()
		else: 
			cash = 0
			E.color = discord.Color.red()
			E.description = f"{inter.user.mention}, You rolled a {r} and won nothing..."

		user_data["roses"] += - amount + cash
		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)

	async def flip(self, inter:discord.Interaction, bet:str, guess:Literal["heads", "tails"]):
		await inter.response.defer()

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)

		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)

		choice = random.choice(["heads", "tails"])
		if choice == "tails":
			image = "https://media.discordapp.net/attachments/709313685226782751/1126924584973774868/ttails.png"
		else:
			image = "https://media.discordapp.net/attachments/709313685226782751/1126924585191882833/hheads.png"

		E.title = f"{choice.capitalize()}!"
		E.set_image(url=image)

		if guess == choice:
			cash = int(amount*1.8)
			E.description = f"You guessed it right and won **{cash}🌹!** 🎉"
		else:
			cash = 0
			E.color = discord.Color.red()
			E.description = f"You guessed it wrong..."

		user_data["roses"] += - amount + cash
		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)

	async def ladder(self, inter:discord.Interaction, bet:str):
		await inter.response.defer()

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)
		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)

		r = random.randint(1,8)
		if r <= 4:
			E.color = discord.Color.red()
		if r == 5: 
			E.color = discord.Color.blurple()
		if r == 8:
			E.color = discord.Color.gold()

		equivalents = {
			1: 0.1,
			2: 0.3,
			3: 0.4,
			4: 0.5,
			5: 1.0,
			6: 1.2,
			7: 1.5,
			8: 2.2
		}
		display = [
			"╠══╣||x2.2||",
			"╠══╣||x1.5||",
			"╠══╣||x1.2||",
			"╠══╣||x1.0||",
			"╠══╣||x0.5||", 
			"╠══╣||x0.4||", 
			"╠══╣||x0.3||",
			"╠══╣||x0.1||", 
		]

		display[8-r] = display[8-r].replace("||", "**") + ' ⬅️'
		E.description = "\n".join(display)

		cash = int(amount * equivalents[r])

		E.add_field(name="Multiplier", value=f"**x{equivalents[r]}**")
		E.add_field(name="Won", value=f"**{cash}🌹 **")

		user_data["roses"] += - amount + cash
		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)



async def setup(bot:commands.Bot):
	await bot.add_cog(Gambling(bot))
