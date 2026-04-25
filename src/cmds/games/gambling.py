import discord 
from discord import app_commands, ui
from discord.ext import commands, tasks

import random
import datetime as dt
from typing import Literal
import asyncio

import re
from utils import get_data, upd_data, GetLogLink, get_amount, embed_roulette

class Gambling(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot
		self.GH = GamblingHelper(bot)

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
			user_data : dict = get_data(f"games/users/{inter.user.id}")
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

class GamblingHelper:
	def __init__(self, bot:commands.Bot, already_all:bool=False):
		self.bot : commands.Bot = bot
		self.already_all = already_all

	async def is_allowed_to_bet(self, inter:discord.Interaction, bet:str) -> tuple[int, discord.Embed, dict]:
		E = discord.Embed()
		E.color = discord.Color.green()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		try :
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You don't have an account yet, get one using **/collect**"
			E.color = discord.Color.red()
			return 0, E, {}
		
		# if the user sent the command too quickly
		if '🌹' not in bet:
			bet += "🌹"

        #-------------- Merge conflict --------------
		print("bet before: ", bet)
		if bet==f"all ({user_data['roses']}🌹)":
			self.already_all = True
		if "next_bet_all" in user_data["effects"] and not self.already_all:
			bet=f"all ({user_data['roses']}🌹)"



		# translate the user request into a number
		amount = get_amount(user_data["roses"], bet)
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

	async def check(self, inter:discord.Interaction) -> tuple[discord.Embed, dict]:
		E = discord.Embed()
		E.color = discord.Color.green()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		try :
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You don't have an account yet"
			E.color = discord.Color.red()
			return E, {}

		return E, user_data

	async def change_next_method(self, inter : discord.Interaction, bet : str, gambling_func):
		gambling_funcs = ["roll", "flip", "ladder"]
		gambling_funcs.remove(gambling_func.__name__)
		for i in range(10):

			choice = random.choice(gambling_funcs)
			print(choice)
		if choice=="ladder":
			await self.ladder(inter, bet)
		elif choice == "flip":
			guess : Literal["heads", "tails"] = random.choice(["heads", "tails"])
			await self.flip(inter, bet, guess)
		elif choice == "roll":
			await self.roll(inter, bet)

	async def change_next_gain(self, E : discord.Embed, inter:discord.Interaction, user_data : dict):
		if "next_gain_x3" in user_data["effects"]:
			multiplicator = 3
			user_data["effects"].remove("next_gain_x3")
			user_data["effects"].remove("next_gain")
			E.color = discord.Color.purple()
			E.description = "Wow! You tripled your gain!"
			await inter.followup.send(embed=E)

		elif "next_gain_/3" in user_data["effects"]:
			multiplicator = 1/3
			user_data["effects"].remove("next_gain_/3")
			user_data["effects"].remove("next_gain")
			E.color = discord.Color.purple()
			E.description = "Haha, your gain was divided by three!"
			await inter.followup.send(embed=E)

		elif "next_gain_x10" in user_data["effects"]:
			multiplicator = 10
			user_data["effects"].remove("next_gain_x10")
			user_data["effects"].remove("next_gain")
			E.color = discord.Color.purple()
			E.description = "Wow! Your gain has grown by a factor 10!"
			await inter.followup.send(embed=E)
			
		elif "next_gain_/10" in user_data["effects"]:
			multiplicator = 1/10
			user_data["effects"].remove("next_gain_/10")
			user_data["effects"].remove("next_gain")
			E.color = discord.Color.purple()
			E.description = "Haha, your gain was divided by ten!"
			await inter.followup.send(embed=E)

		return multiplicator

	async def roll(self, inter:discord.Interaction, bet:str):
		try:
			await inter.response.defer()
		except:
			pass

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)
		print("current_roses: ", user_data["roses"])
		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)
		
		r = random.randint(1,100)
		roulette = False
		for element in user_data["effects"]:
			if "gain" in "bet" in element or "bet" in element:
				roulette = True

		if roulette:
			E = await embed_roulette(self.bot, inter, E)

		multiplicator = 1
		double = False
		divide = False
		#Roulette effects

		#changes the bet method
		if "change_bet_method" in user_data["effects"]:
			user_data["effects"].remove("change_bet_method")
			upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
			E.colour = discord.Colour.purple()
			E.description = f"{inter.user.mention} hmmm no thanks I don't feel like rolling rn..."
			await inter.followup.send(embed=E)
			return await self.change_next_method(inter, bet, self.roll)
		
		#Changes the chances of winning
		if "chances_next_bet_x2" in user_data["effects"]:
			user_data["effects"].remove("chances_next_bet_x2")
			double=True
			E.color = discord.Color.purple()
			E.description = "Wow! You had twice the chance to win!"
			await inter.followup.send(embed=E)
		elif "chances_next_bet_/2" in user_data["effects"]:
			user_data["effects"].remove("chances_next_bet_/2")
			divide=True
			E.color = discord.Color.purple()
			E.description = "Well, you had half the chance to win this one"
			await inter.followup.send(embed=E)

		#All in effect
		if "next_bet_all" in user_data["effects"] and not self.already_all:	
			user_data["effects"].remove("next_bet_all")
			upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
			E.description = f"Oops you accidently bet all"
			E.colour = discord.Colour.purple()
			await inter.followup.send(embed=E)

		#if chances*2 : roll twice and take the best result
		if double:
			r = max(random.randint(1,100),random.randint(1,100))
		#if chances/2 : roll twice and take the worst result
		elif divide:
			r = min(random.randint(1,100),random.randint(1,100))

		# If effect include "next_gain" and it's winning, gain changed
		if r >= 70:
			multiplicator  = await self.change_next_gain(E, inter, user_data)
		E.add_field(name="Roll:", value=f"**{r}**")
		cash=amount
		if r == 100:
			#Il y a 2 int, un pour arrondir le résultat, un autre pour la division
			cash = int(int(amount*10)*multiplicator)
			E.description = f"{inter.user.mention}, You rolled a 100 and won **{cash}🌹!** 👑"
			E.color = discord.Color.gold()
		elif r >= 90:
			cash = int(int(amount*4)*multiplicator)
			E.description = f"{inter.user.mention}, You rolled 90 or above and won x4 **{cash}🌹!** 🎯"
		elif r >= 70:
			cash = int(int(amount*2)*multiplicator)
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
		try:
			await inter.response.defer()
		except:
			pass

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)

		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)
		roulette=False
		for element in user_data["effects"]:
			if "gain" in element or "bet" in element:
				roulette = True
				
		if roulette:
			E = await embed_roulette(self.bot, inter, E)
		choice = random.choice(["heads", "tails"])
		#Roulette effects

		#changes the bet method
		if "change_bet_method" in user_data["effects"]:
			user_data["effects"].remove("change_bet_method")
			upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
			E.colour = discord.Colour.purple()
			E.description = f"{inter.user.mention} hmmm no thanks I don't feel like flipping rn..."
			await inter.followup.send(embed=E)
			return await self.change_next_method(inter, bet, self.flip)
			
		multiplicator=1
		divide=False
		double=False
		
		#Changes the chances of winning
		if "chances_next_bet_x2" in user_data["effects"]:
			double=True
			user_data["effects"].remove("chances_next_bet_x2")
			E.color = discord.Color.purple()
			E.description = "Wow! You had twice the chance to win!"
		elif "chances_next_bet_/2" in user_data["effects"]:
			divide=True
			user_data["effects"].remove("chances_next_bet_/2")
			E.color = discord.Color.purple()
			E.description = "Well, you had half the chance to win this one"
			await inter.followup.send(embed=E)
		
		#All in effect
		if "next_bet_all" in user_data["effects"] and not self.already_all:	
			user_data["effects"].remove("next_bet_all")
			upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
			E.description = f"Oops you accidently bet all"
			E.colour = discord.Colour.purple()
			await inter.followup.send(embed=E)
		double_tails=0
		double_heads=0
		divide_heads=0
		divide_tails=0

		if double:
			if guess=="heads":
				double_heads=1
			else:
				double_tails=1
		elif divide:
			if guess=="heads":
				divide_tails=1
			else:
				divide_heads=1

		#if chances*2 : flip two times and take the best result, if chances/2 do the opposite
		if double or divide:
			choice = random.choices(["heads", "tails"], [1 + double_heads + divide_heads, 1 + double_tails + divide_tails])[0]
		# If effect include "next_gain" and it's winning, gain changed
		if guess == choice and "next_gain" in user_data["effects"]:
			multiplicator = await self.change_next_gain(E, inter, user_data)

		if choice == "tails":
			image = "https://media.discordapp.net/attachments/709313685226782751/1126924584973774868/ttails.png"
		else:
			image = "https://media.discordapp.net/attachments/709313685226782751/1126924585191882833/hheads.png"
		E.title = f"{choice.capitalize()}!"
		E.set_image(url=image)


		if guess == choice:
			#Il y a 2 int, un pour arrondir le résultat, un autre pour la division
			cash = int(int(amount*1.8)*multiplicator)
			E.description = f"You guessed it right and won **{cash}🌹!** 🎉"
			E.color = discord.Color.green()
		else:
			cash = 0
			E.color = discord.Color.red()
			E.description = f"You guessed it wrong..."
		if "free_flip_when_collect" in user_data["effects"]:
			amount = 0
		user_data["roses"] += - amount + cash

		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)

	async def ladder(self, inter:discord.Interaction, bet:str):
		try:
			await inter.response.defer()
		except:
			pass

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)
		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)
			
		roulette = False
		for element in user_data["effects"]:
			if "gain" in element or "bet" in element:
				roulette = True
				
		if roulette:
			E = await embed_roulette(self.bot, inter, E)

		r = random.randint(1,8)
		multiplicator=1
		double=False
		divide=False
		#Roulette effects

		#changes the bet method
		if "change_bet_method" in user_data["effects"]:
			user_data["effects"].remove("change_bet_method")
			upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
			E.colour = discord.Colour.purple()
			E.description = f"{inter.user.mention} hmmm no thanks I don't feel like laddering rn..."
			await inter.followup.send(embed=E)
			return await self.change_next_method(inter, bet, self.ladder)

		#Changes the chances of winning
		if "chances_next_bet_x2" in user_data["effects"]:
			user_data["effects"].remove("chances_next_bet_x2")
			double=True
			E.color = discord.Color.purple()
			E.description = "Wow! You had twice the chance to win!"
		elif "chances_next_bet_/2" in user_data["effects"]:
			user_data["effects"].remove("chances_next_bet_/2")
			divide=True
			E.color = discord.Color.purple()
			E.description = "Well, you had half the chance to win this one"
			await inter.followup.send(embed=E)

		#if chances*2 : ladder twice and take the best result, if chances/2 do the opposite
		if double:
			r = max(random.randint(1,8),random.randint(1,8))
		elif divide:
			r = min(random.randint(1,8),random.randint(1,8))
		elif r>=6:
			multiplicator  = await self.change_next_gain(E, inter, user_data)
		if "next_bet_all" in user_data["effects"] and not self.already_all:	
			user_data["effects"].remove("next_bet_all")
			upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
			E.description = f"Oops you accidently bet all"
			E.colour = discord.Colour.purple()
			await inter.followup.send(embed=E)

		if r <= 4:
			E.color = discord.Color.red()
		if r == 5: 
			E.color = discord.Color.blurple()
		if 8 > r > 5:
			E.color = discord.Color.green()
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

		cash = int(int(amount * equivalents[r])*multiplicator)

		E.add_field(name="Multiplier", value=f"**x{equivalents[r]}**")
		E.add_field(name="Won", value=f"**{cash}🌹 **")

		user_data["roses"] += - amount + cash
		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)

async def setup(bot:commands.Bot):
	await bot.add_cog(Gambling(bot))
