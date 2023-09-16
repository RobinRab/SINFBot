import discord 
from discord import app_commands
from discord.ext import commands

import random
import datetime as dt
from typing import Literal, Optional

from utils import get_data, upd_data, GetLogLink, get_amount, is_cutie

class Gambling(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	async def is_allowed_to_bet(self, inter:discord.Interaction, bet:str) -> tuple[int, discord.Embed, dict]:
		E = discord.Embed()
		E.color = discord.Color.green()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		try :
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You don't have any 🌹"
			E.color = discord.Color.red()
			return 0, E, {}
		
		# translate the user request into a number
		amount = get_amount(user_data["roses"], bet)

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

	@app_commands.command(description="Rolls a dice")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet")
	async def roll(self, inter:discord.Interaction, bet:str):
		await inter.response.defer()

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)
		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)

		r = random.randint(1,100)
		if r == 100:
			cash = amount*10
			E.description = f"{inter.user.mention}, You rolled a 100 and won **{cash}🌹!** 👑"
			E.color = discord.Color.gold()
		elif r >= 90:
			cash = amount*4
			E.description = f"{inter.user.mention}, You rolled a {r} and won **{cash}🌹!** 🎯"
		elif r >= 75:
			cash = amount*2
			E.description = f"{inter.user.mention}, You rolled a {r} and won **{cash}🌹!** 🎉"
		else: 
			cash = 0
			E.color = discord.Color.red()
			E.description = f"{inter.user.mention}, You rolled a {r} and won nothing..."

		user_data["roses"] += - amount + cash
		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)

	@app_commands.command(description="Flips a coin")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet", guess="Your guess")
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
			cash = int(amount*1.6)
			E.description = f"You guessed it right and won **{cash}🌹!** 🎉"
		else:
			cash = 0
			E.color = discord.Color.red()
			E.description = f"You guessed it wrong..."

		user_data["roses"] += - amount + cash
		upd_data(user_data, f"games/users/{inter.user.id}")

		await inter.followup.send(embed=E)

	@app_commands.command(description="Lucky Ladder, each step has equal chances of occuring")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet")
	async def ladder(self, inter:discord.Interaction, bet:str):
		await inter.response.defer()

		amount, E, user_data = await self.is_allowed_to_bet(inter, bet)
		# if the already has a description, an issue was found
		if E.description is not None:
			return await inter.followup.send(embed=E)
		
		r = random.randint(1,8)
		if r <= 5:
			E.color = discord.Color.red()
		if r == 8:
			E.color = discord.Color.gold()

		equivalents = {
			1: 0.1,
			2: 0.2,
			3: 0.3,
			4: 0.4,
			5: 0.5,
			6: 1.2,
			7: 1.5,
			8: 2.2
		}
		display = [
			"╠══╣||x2.2||",
			"╠══╣||x1.5||",
			"╠══╣||x1.2||",
			"╠══╣||x0.5||",
			"╠══╣||x0.4||", 
			"╠══╣||x0.3||", 
			"╠══╣||x0.2||",
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

	@app_commands.command(description="betpoll, bet on a poll")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.describe(question="Ask everyone a question", time="The time the poll will last")
	async def bpoll(self, inter:discord.Interaction, question:str, time:Literal["1m", "15m", "1h", "12h", "24h"]):
		await inter.response.defer()

		E = discord.Embed(title=question, color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot,str(inter.user.display_avatar)))
		E.set_thumbnail(url="https://media.discordapp.net/attachments/709313685226782751/1128082089397465218/thonking.gif")

		E.add_field(name="yes", value="0", inline=True)
		E.add_field(name="no", value="0", inline=True)
		E.add_field(name="\u200b", value="\u200b") # invisible field to align
		E.add_field(name="total yes", value="0", inline=True)
		E.add_field(name="total no", value="0", inline=True)

		# id : amount
		greens = {}
		reds = {}

		# create modal that asks the amount to bet
		class GetBet(discord.ui.Modal):
			def __init__(self, message:discord.Message, bet_type:Literal["green", "red"]):
				self.message = message
				self.bet_type = bet_type
				super().__init__(title="How much 🌹 do you want to bet?")

			bet = discord.ui.TextInput(label="Bet amount?", default='0', min_length=1, max_length=5)

			async def on_submit(self, inter: discord.Interaction):
				# check if the user can bet 
				if inter.user.id in greens or inter.user.id in reds:
					return await inter.response.send_message(f'You already bet', ephemeral=True)

				# get the amount 
				bet_amount = self.bet.value

				try:
					bet_amount = int(float(bet_amount.replace(",", ".")))
					if bet_amount < 0:
						raise ValueError
				except: 
					return await inter.response.send_message(f'Invalid amount', ephemeral=True)
				
				# check if the user has enough roses
				try: 
					user_data : dict = get_data(f"games/users/{inter.user.id}")
					if user_data["roses"] < bet_amount:
						raise ValueError
				except:
					return await inter.response.send_message(f'You don\'t have enough 🌹', ephemeral=True)
				user_data["roses"] -= bet_amount
				upd_data(user_data, f"games/users/{inter.user.id}")

				# update data
				txt = ""
				if self.bet_type == "red":
					reds[inter.user.id] = bet_amount

					for user_id, amount in reds.items():
						txt += f"<@!{user_id}> : {amount:,}🌹\n"
					E.set_field_at(1, name="no", value=txt)
					E.set_field_at(4, name="total no", value=f"{sum(reds.values()):,}🌹")

				else:
					greens[inter.user.id] = bet_amount

					for user_id, amount in greens.items():
						txt += f"<@!{user_id}> : {amount:,}🌹\n"
					E.set_field_at(0, name="yes", value=txt)
					E.set_field_at(3, name="total yes", value=f"{sum(greens.values()):,}🌹")

				await self.message.edit(embed=E)

				await inter.response.send_message(f'bet set!', ephemeral=True)

		# create the view that asks users to bet
		class FirstView(discord.ui.View):
			def __init__(self, timeout:int):
				super().__init__(timeout=timeout)
				self.message : Optional[discord.Message]

			@discord.ui.button(label="bet yes",style=discord.ButtonStyle.success)
			async def bet_yes(self, inter2: discord.Interaction, _: discord.ui.Button):
				if isinstance(self.message, discord.Message):
					await inter2.response.send_modal(GetBet(self.message, "green"))
			
			@discord.ui.button(label="bet no",style=discord.ButtonStyle.danger)
			async def bet_no(self, inter2: discord.Interaction, _: discord.ui.Button):
				if isinstance(self.message, discord.Message):
					await inter2.response.send_modal(GetBet(self.message, "red"))

			@discord.ui.button(label="end poll",style=discord.ButtonStyle.blurple)
			async def end_poll(self, inter2: discord.Interaction, _: discord.ui.Button):
				if inter.user != inter2.user:
					return await inter2.response.send_message(f'This button is for the poll owner only', ephemeral=True)
				await inter2.response.send_message(f'Poll ended', ephemeral=True)

				self.stop()

		# translate timeout choice to seconds
		equivalents = {
			"1m": 10, #60
			"15m": 900,
			"1h": 3600,
			"12h": 43_200,
			"24h": 86_400
		}
		timeout = equivalents[time]

		firstView = FirstView(timeout)
		firstView.message = await inter.followup.send(
			f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>", 
			embed=E,
			view=firstView
		)

		await firstView.wait()

		# second view awaiting for the owner to choose the end result
		class SecondView(discord.ui.View):
			def __init__(self, message:discord.Message, timeout:int):
				super().__init__(timeout=timeout)
				self.add_item(discord.ui.Button(label="bet yes",style=discord.ButtonStyle.success, disabled=True))
				self.add_item(discord.ui.Button(label="bet no",style=discord.ButtonStyle.danger, disabled=True))
				self.add_item(discord.ui.Button(label="end poll",style=discord.ButtonStyle.blurple, disabled=True))
				self.message = message

				self.result : Literal["yes", "no"]

			async def close(self):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True

				if isinstance(self.message, discord.Message):
					await self.message.edit(content="The poll is over", view=self)
				self.stop()

			async def interaction_check(self, inter2: discord.Interaction) -> bool:
				return inter2.user == inter.user

			@discord.ui.button(label="yes!",style=discord.ButtonStyle.success, row=1)
			async def yes(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.result = "yes"
				await inter2.response.send_message(f"The final answer has been set to 'yes'", ephemeral=True)
				await self.close()

			@discord.ui.button(label="no!",style=discord.ButtonStyle.danger, row=1)
			async def no(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.result = "no"
				await inter2.response.send_message(f"The final answer has been set to 'no'", ephemeral=True)
				await self.close()

			async def on_timeout(self):
				for user_id, amount in {**greens, **reds}.items():
					user_data = get_data(f"games/users/{user_id}")
					user_data["roses"] += amount
					upd_data(user_data, f"games/users/{user_id}")

				await self.message.reply("all users have been refunded")
				await self.close()

		assert isinstance(firstView.message, discord.Message)
		# after 24h users are refunded
		timeout = 86400
		secondView = SecondView(message=firstView.message, timeout=timeout)

		await secondView.message.edit(content=f"Waiting for {inter.user.mention}'s answer.\nrefund in <t:{int(dt.datetime.now().timestamp() + timeout)}:R>",
				view=secondView)

		await secondView.wait()

		# get the result
		# give to the winners the amount they won proportionally to their bet
		total_greens = sum(greens.values())
		total_reds = sum(reds.values())

		E = discord.Embed(title="Congratulations!", color=discord.Color.gold())
		E.description = f"### **{secondView.result.upper()} team wins!**\n"

		if secondView.result == "yes":
			for user_id, amount in greens.items():
				user_data = get_data(f"games/users/{user_id}")
				green_prop = amount / total_greens *100
				prop_amount = green_prop * (total_reds / 100)
				user_data["roses"] += int(prop_amount) + amount
				upd_data(user_data, f"games/users/{user_id}")
				E.description += f"<@!{user_id}> : +{int(prop_amount) + amount}🌹\n"
		else: 
			for user_id, amount in reds.items():
				user_data = get_data(f"games/users/{user_id}")
				red_prop = amount / total_reds *100
				prop_amount = red_prop * (total_greens / 100)
				user_data["roses"] += int(prop_amount) + amount
				upd_data(user_data, f"games/users/{user_id}")
				E.description += f"<@!{user_id}> : +{int(prop_amount) + amount}🌹\n"

		await secondView.message.reply(embed=E)

async def setup(bot:commands.Bot):
	await bot.add_cog(Gambling(bot))