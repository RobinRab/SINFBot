import discord 
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


@tasks.loop()
async def traveler(*, bot: commands.Bot):
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
		user_data["ideas"] += 7

		upd_data(user_data, f"games/users/{inter.user.id}")
		E.description = f"You earned **{value}🌹** and **7💡**"
	
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

	b_choices.message = await bot_channel.send(embed=E, view=b_choices, silent=True)

	await b_choices.wait()

	# come back in 2 to 10 hours
	random_time = random.randint(7200, 36000)

	await asyncio.sleep(random_time)

async def setup(bot:commands.Bot):
	await bot.add_cog(Games(bot))