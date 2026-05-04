import discord
from discord import app_commands
from discord.ext import commands

import datetime as dt
from typing import Literal, Optional
from utils import is_member, get_data, upd_data, GetLogLink, get_amount, is_cutie, UnexpectedValue


class Polls(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot = bot

	@app_commands.command(description="Creates a poll")
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(question="The question to ask")
	async def poll(self, inter:discord.Interaction, question:str):
		await inter.response.defer()

		E = discord.Embed(title=question, color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot,str(inter.user.display_avatar)))
		E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1125361175929049158/770002495614877738.png")
		
		# send the message and get it back
		await inter.followup.send(embed=E)
		msg = await inter.original_response()

		if isinstance(msg, discord.InteractionMessage):
			await msg.add_reaction("✅")
			await msg.add_reaction("❌")
			await msg.add_reaction("⬜")


	@app_commands.command(description="Creates an anonymous poll")
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	@app_commands.describe(question="The question to ask", time="The time the poll will last")
	async def apoll(self, inter:discord.Interaction, question:str, time:Literal["1m", "15m", "1h", "12h", "24h"]):
		await inter.response.defer()

		E = discord.Embed(title=question, color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot,str(inter.user.display_avatar)))
		E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1125361175929049158/770002495614877738.png")

		class B_votes(discord.ui.View):
			def __init__(self, timeout:int):
				super().__init__(timeout=timeout)
				self.message : Optional[discord.Message]

				self.greens = 0
				self.reds = 0
				self.end = f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>"

				self.voted_ids = []

			async def interaction_check(self, inter2: discord.Interaction):
				if inter2.user.id in self.voted_ids:
					await inter2.response.send_message("You already voted!", ephemeral=True)
					return False
				self.voted_ids.append(inter2.user.id)
				return True

			@discord.ui.button(label="yes",style=discord.ButtonStyle.success, custom_id="yes")
			async def add(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.greens += 1
				await inter2.response.edit_message(content=f"{self.greens+self.reds} votes. Ends in {self.end}")

			@discord.ui.button(label="no",style=discord.ButtonStyle.danger, custom_id="no")
			async def list(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.reds += 1
				await inter2.response.edit_message(content=f"{self.greens+self.reds} votes. Ends in {self.end}")

			async def on_timeout(self):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						if item.custom_id == "yes":
							item.label = f"yes ({self.greens})"
						elif item.custom_id == "no":
							item.label = f"no ({self.reds})"
						item.disabled = True

				if isinstance(self.message, discord.Message):
					txt = f"Poll ended, it lasted  {time}"
					await self.message.edit(view=self, content=txt)

		equivalents = {
			"1m": 60,
			"15m": 900,
			"1h": 3600,
			"12h": 43_200,
			"24h": 86_400
		}

		b_votes = B_votes(equivalents[time])
		b_votes.message = await inter.followup.send(view=b_votes, embed=E, content=f"0 votes. Ends in {b_votes.end}")





	@app_commands.command(description="betpoll, bet on a poll")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.describe(question="Set a bet!s", time="The time the poll will last")
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

			bet = discord.ui.TextInput(label="Bet amount?", default='2', min_length=1, max_length=5)

			async def on_submit(self, inter2: discord.Interaction):
				# get the amount 
				bet_amount = self.bet.value

				try:
					bet_amount = int(float(bet_amount.replace(",", ".")))
					if bet_amount < 0:
						raise ValueError
				except: 
					return await inter2.response.send_message(f'Invalid amount', ephemeral=True)

				if bet_amount < 2:
					return await inter2.response.send_message(f'You need to bet at least 2🌹', ephemeral=True)

				# check if the user has enough roses
				try: 
					user_data : dict = get_data(f"games/users/{inter2.user.id}")
					if user_data["roses"] < bet_amount:
						raise ValueError
				except:
					return await inter2.response.send_message(f'You don\'t have enough 🌹', ephemeral=True)

				user_data["roses"] -= bet_amount
				upd_data(user_data, f"games/users/{inter2.user.id}")

				# update data
				txt = ""
				if self.bet_type == "red":
					reds[inter2.user.id] = bet_amount

					for user_id, amount in reds.items():
						txt += f"<@!{user_id}> : {amount:,}🌹\n"
					E.set_field_at(1, name="no", value=txt)
					E.set_field_at(4, name="total no", value=f"{sum(reds.values()):,}🌹")

				else:
					greens[inter2.user.id] = bet_amount

					for user_id, amount in greens.items():
						txt += f"<@!{user_id}> : {amount:,}🌹\n"
					E.set_field_at(0, name="yes", value=txt)
					E.set_field_at(3, name="total yes", value=f"{sum(greens.values()):,}🌹")

				await self.message.edit(embed=E)

				await inter2.response.send_message(f'bet set!', ephemeral=True)

		# create the view that asks users to bet
		class FirstView(discord.ui.View):
			def __init__(self, timeout:float):
				super().__init__(timeout=timeout)
				self.message_id : int

			@discord.ui.button(label="bet yes",style=discord.ButtonStyle.success)
			async def bet_yes(self, inter2: discord.Interaction, _: discord.ui.Button):
				if inter2.user.id in greens or inter2.user.id in reds:
					return await inter2.response.send_message(f'You already bet', ephemeral=True)
				
				# fetch the message back (>15 mins)
				if not isinstance(inter2.channel, discord.TextChannel):
					raise UnexpectedValue("inter2.channel is not a discord.TextChannel")
				
				message = await inter2.channel.fetch_message(self.message_id)

				await inter2.response.send_modal(GetBet(message, "green"))

				# update timeout so it stays on time
				self.timeout = time_ends - int(dt.datetime.now().timestamp())

			@discord.ui.button(label="bet no",style=discord.ButtonStyle.danger)
			async def bet_no(self, inter2: discord.Interaction, _: discord.ui.Button):
				if inter2.user.id in greens or inter2.user.id in reds:
					return await inter2.response.send_message(f'You already bet', ephemeral=True)

				# fetch the message back (>15 mins)
				if not isinstance(inter2.channel, discord.TextChannel):
					raise UnexpectedValue("inter2.channel is not a discord.TextChannel")
				
				message = await inter2.channel.fetch_message(self.message_id)

				await inter2.response.send_modal(GetBet(message, "red"))

				# update timeout so it stays on time
				self.timeout = time_ends - int(dt.datetime.now().timestamp())

			@discord.ui.button(label="end poll",style=discord.ButtonStyle.blurple)
			async def end_poll(self, inter2: discord.Interaction, _: discord.ui.Button):
				if inter.user != inter2.user:
					return await inter2.response.send_message(f'This button is for the poll owner only', ephemeral=True)
				await inter2.response.send_message(f'Poll ended', ephemeral=True)

				self.stop()

		# translate timeout choice to seconds
		equivalents = {
			"1m": 60,
			"15m": 900,
			"1h": 3600,
			"12h": 43_200,
			"24h": 86_400
		}
		# +2 for the time it takes to send the message
		time_ends = int(dt.datetime.now().timestamp()) + equivalents[time] + 2
		left = time_ends - int(dt.datetime.now().timestamp())

		firstView = FirstView(left)

		message = await inter.followup.send(f"<t:{time_ends}:R>", embed=E,view=firstView)

		if not isinstance(message, discord.Message):
			raise UnexpectedValue("message is not a discord.Message")
		
		firstView.message_id = message.id

		await firstView.wait()

		# second view awaiting for the owner to choose the end result
		class SecondView(discord.ui.View):
			def __init__(self, message_id:int, timeout:int):
				super().__init__(timeout=timeout)
				self.add_item(discord.ui.Button(label="bet yes",style=discord.ButtonStyle.success, disabled=True))
				self.add_item(discord.ui.Button(label="bet no",style=discord.ButtonStyle.danger, disabled=True))
				self.add_item(discord.ui.Button(label="end poll",style=discord.ButtonStyle.blurple, disabled=True))
				self.message : discord.Message
				self.message_id = message_id

				self.result : Literal["yes", "no"]

			async def close(self, channel, txt):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True

				# fetch the message back (>15 mins)
				if not isinstance(channel, discord.TextChannel):
					raise UnexpectedValue("channel is not a discord.TextChannel")
				
				message = await channel.fetch_message(self.message_id)
				await message.edit(content=txt, view=self)

				self.stop()

			async def interaction_check(self, inter2: discord.Interaction) -> bool:
				return inter2.user == inter.user

			@discord.ui.button(label="yes!",style=discord.ButtonStyle.success, row=1)
			async def yes(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.result = "yes"
				await inter2.response.send_message(f"The final answer has been set to 'yes'", ephemeral=True)
				await self.close(inter2.channel, "'Yes' team wins!'")

			@discord.ui.button(label="no!",style=discord.ButtonStyle.danger, row=1)
			async def no(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.result = "no"
				await inter2.response.send_message(f"The final answer has been set to 'no'", ephemeral=True)
				await self.close(inter2.channel, "'No' team wins!")

			async def on_timeout(self):
				for user_id, amount in {**greens, **reds}.items():
					user_data = get_data(f"games/users/{user_id}")
					user_data["roses"] += amount
					upd_data(user_data, f"games/users/{user_id}")

				await self.message.reply("all users have been refunded")
				await self.close(self.message.channel, "Poll timed out\nUsers have been refunded")

		# after 24h users are refunded
		timeout = 86400
		secondView = SecondView(message_id=firstView.message_id, timeout=timeout)

		# fetch the message back (>15 mins)
		if not isinstance(inter.channel, discord.TextChannel):
			raise UnexpectedValue("channel is not a discord.TextChannel")
		
		secondView.message = await inter.channel.fetch_message(secondView.message_id)

		await secondView.message.edit(content=f"Waiting for {inter.user.mention}'s answer.\nrefund <t:{int(dt.datetime.now().timestamp() + timeout)}:R>",
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


async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(Polls(bot))