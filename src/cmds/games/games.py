import discord 
from discord import app_commands
from discord.ext import commands, tasks

import html
import random
import asyncio
import requests
from typing import Optional

from settings import BOT_CHANNEL_ID
from utils import log, get_data, upd_data, get_value, new_user

class Games(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

		traveler.start(bot=self.bot)

	#! jsp quoi faire de ça
	# @app_commands.command(description="memorize the squares")
	# @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	# @app_commands.guild_only()
	# async def memory(self, inter:discord.Interaction):
	# 	matrix = [[0]*5 for _ in range(5)]

	# 	num_ones = 5
	# 	for i in range(num_ones):
	# 		while True:
	# 			x = random.randint(0, 4)
	# 			y = random.randint(0, 4)
	# 			if matrix[y][x] == 0:
	# 				matrix[y][x] = 1
	# 				break

	# 	class Memory(discord.ui.View):
	# 		def __init__(self, matrix:list[list], timeout:int):
	# 			super().__init__(timeout=timeout)

	# 			self.matrix = matrix
	# 			self.message : Optional[discord.Message]

	# 			for iy, y in enumerate(matrix):
	# 				for ix, x in enumerate(y):
	# 					color = random.choice([discord.ButtonStyle.red, discord.ButtonStyle.blurple])
	# 					if x == 1:
	# 						self.add_item(discord.ui.Button(label=f"({ix},{iy})", style=discord.ButtonStyle.green))
	# 					else:
	# 						self.add_item(discord.ui.Button(label=f"({ix},{iy})"))

	# 	memoryview = Memory(matrix, 10)
	# 	memoryview.message = await inter.response.send_message("Memorize the squares", view=memoryview)

	# 	await memoryview.wait()

	# 	class CallbackButton(discord.ui.Button):
	# 		def __init__(self, parent_view:'HiddenView', *args, **kwargs):
	# 			super().__init__(*args, **kwargs)

	# 			self.parent_view = parent_view

	# 		async def callback(self, inter2: discord.Interaction):
	# 			assert isinstance(self.label, str)
	# 			assert isinstance(self.parent_view.message, discord.Message)

	# 			if matrix[int(self.label[3])][int(self.label[1])] == 1:
	# 				self.style = discord.ButtonStyle.green
	# 				self.parent_view.children[int(self.label[3])*5 + int(self.label[1])] = self

	# 				await self.parent_view.message.edit(view=self.parent_view)
	# 				await inter2.response.send_message("correct", ephemeral=True)
	# 			else:
	# 				self.style = discord.ButtonStyle.red
	# 				self.parent_view.children[int(self.label[3])*5 + int(self.label[1])] = self

	# 				await self.parent_view.message.edit(view=self.parent_view, content="You lost")
	# 				await inter2.response.send_message("incorrect", ephemeral=True)
	# 				self.parent_view.stop()

	# 	class HiddenView(discord.ui.View):
	# 		def __init__(self, message, timeout:int):
	# 			super().__init__(timeout=timeout)
	# 			self.message : discord.Message = message

	# 	hiddenview = HiddenView(memoryview.message, 30)

	# 	for iy in range(5):
	# 		for ix in range(5):
	# 			hiddenview.add_item(CallbackButton(hiddenview, label=f"({ix},{iy})", style=discord.ButtonStyle.grey))

	# 	await hiddenview.message.edit(content="click the green squares", view=hiddenview)


@tasks.loop()
async def traveler(*, bot: commands.Bot):
	# spawn every 2 to 10 hours
	random_time = random.randint(7200, 36000)

	await asyncio.sleep(random_time)

	# get the bot channel and make sure it is not none
	bot_channel = await bot.fetch_channel(BOT_CHANNEL_ID)
	assert isinstance(bot_channel, discord.TextChannel)

	# make the request and check it is valid
	r = random.choice([18,19])
	url = f"https://opentdb.com/api.php?amount=1&category={r}"

	response = requests.get(url)
	data = response.json()

	if data["response_code"] != 0:
		return log('WARNING', "opentdb api returned 0 response code")
	
	# extract the data
	category:str = data["results"][0]["category"]
	difficulty:str = data["results"][0]["difficulty"]

	question_type:str = data["results"][0]["type"]
	# convert html entities to normal unicode text
	question:str = html.unescape(data["results"][0]["question"])
	correct_answer:str = html.unescape(data["results"][0]["correct_answer"])
	incorrect_answers:list = list(map(html.unescape, data["results"][0]["incorrect_answers"]))

	# create a list of answers and randomize them
	answers = []
	answers.append(correct_answer)
	answers.extend(incorrect_answers)
	random.shuffle(answers)

	correct_answer_index = answers.index(correct_answer)

	# create embed
	E = discord.Embed(title='Traveler', description=f"**{question}**")
	E.description = f"## **{question}**\n\n"
	E.set_footer(text=f"Category: {category} | Difficulty: {difficulty} | Type: {question_type}")
	E.set_thumbnail(url="https://media.discordapp.net/attachments/709313685226782751/1127893104402386966/traveler.png")

	if difficulty == "easy":
		E.color = discord.Color.green()
	elif difficulty == "medium":
		E.color = discord.Color.gold()
	elif difficulty == "hard":
		E.color = discord.Color.red()

	# handle the correct and incorrect cases
	async def correct(inter:discord.Interaction):
		E = discord.Embed(title="Correct!", color=discord.Color.green())
		E.set_thumbnail(url="https://media.discordapp.net/attachments/709313685226782751/1127893104402386966/traveler.png")

		# user_id : {user data}
		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			user_data = new_user()
		
		value = get_value(user_data)

		user_data["roses"] += value
		user_data["ideas"] += 10

		upd_data(user_data, f"games/users/{inter.user.id}")
		E.description = f"You earned **{value}🌹** and **10💡**"
	
		await inter.followup.send(inter.user.mention, embed=E)

	async def incorrect(inter:discord.Interaction):
		E = discord.Embed(title="Incorrect!", color=discord.Color.red())
		E.set_thumbnail(url="https://media.discordapp.net/attachments/709313685226782751/1127893104402386966/traveler.png")

		# user_id : {user data}
		try: 
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			user_data = new_user()

		user_data["roses"] += 50
		upd_data(user_data, f"games/users/{inter.user.id}")

		E.description = f"The correct answer was **{correct_answer}**\n"
		E.description += f"The traveler left **50🌹** by accident on the ground"

		await inter.followup.send(inter.user.mention, embed=E)

	# subclass of discord.ui.Button, all buttons will have the same callback (no need for functions)
	class CallbackButton(discord.ui.Button):
		def __init__(self, parent_view:'B_choices', *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.parent_view = parent_view

		async def callback(self, inter: discord.Interaction):
			await inter.response.defer()
			if question_type == "boolean":
				if correct_answer.upper() == self.label:
					await correct(inter)
				else:
					await incorrect(inter)

			else:
				if str(correct_answer_index+1) == self.label:
					await correct(inter)
				else:
					await incorrect(inter)

			if isinstance(self.parent_view.message, discord.Message):
				await self.parent_view.message.delete()
			self.parent_view.stop()

	class B_choices(discord.ui.View):
		def __init__(self, timeout=3600):
			super().__init__(timeout=timeout)
			self.message : Optional[discord.Message]

		# traveler leaves: removes message after timeout
		async def on_timeout(self):
			try:
				if isinstance(self.message, discord.Message):
					await self.message.delete()
			except discord.NotFound:
				pass

	# add the necessary buttons
	b_choices = B_choices()
	if question_type == "boolean":
		b_choices.add_item(CallbackButton(parent_view=b_choices, label="TRUE", style=discord.ButtonStyle.green))
		b_choices.add_item(CallbackButton(parent_view=b_choices, label="FALSE", style=discord.ButtonStyle.red))
	else:
		for i in range(4):
			E.description += f"{i+1}. {answers[i]}\n"
			b_choices.add_item(CallbackButton(parent_view=b_choices, label=str(i+1), style=discord.ButtonStyle.blurple))

	b_choices.message = await bot_channel.send(embed=E, view=b_choices)

	await b_choices.wait()

async def setup(bot:commands.Bot):
	await bot.add_cog(Games(bot))