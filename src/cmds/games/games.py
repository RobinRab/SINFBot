import discord 
from discord import app_commands
from discord.ext import commands, tasks

import html
import random
import asyncio
import requests
from typing import Optional

import numpy as np
import datetime as dt
from settings import BOT_CHANNEL_ID
from utils import log, get_data, upd_data, get_value, new_user, get_user_data, simplify, GetLogLink
#from wordle import get_words, color_function, space

class Games(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

		traveler_loop.start(bot=self.bot)
		#wordle_traveler.start(bot=self.bot)

	@app_commands.command(description="Play Amazons!")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(user = "Choose an opponent")
	async def amazons(self, inter: discord.Interaction, user:Optional[discord.Member]):
		await inter.response.defer()
		E = discord.Embed(title=f"Play offer by {inter.user.name}", color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url = await GetLogLink(self.bot, inter.user.display_avatar.url))
		class Button(discord.ui.View):
			def __init__(self, timeout_date:dt.datetime):
				self.timeout_date = timeout_date
				super().__init__(timeout=60)
				self.message : Optional[discord.Message]

			async def interaction_check(self, inter2: discord.Interaction):
				self.upd_timeout()

				if inter.user == inter2.user:
					await inter2.response.send_message("You can't interact with your own message", ephemeral=True)
					return False
				if user is not None and user != inter2.user:
					await inter2.response.send_message("You can't interact with this message", ephemeral=True)
					return False
				return True
			

			
			def upd_timeout(self):
				timeout = (self.timeout_date - dt.datetime.now()).total_seconds()
				self.timeout = timeout

			async def close(self, reason):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True

				if isinstance(self.message, discord.Message):
					content = self.message.content
					content = content.split("\n")
					content[1] = f"({reason})"
					await self.message.edit(content='\n'.join(content), view=self)
				self.stop()

			@discord.ui.button(label=f"Play",style=discord.ButtonStyle.success)
			async def play(self, inter2: discord.Interaction, _: discord.ui.Button):
				try: 
					player = get_data(f"games/users/{inter2.user.id}")
				except KeyError:
					return await inter2.response.send_message("You don't have an account yet", ephemeral=True)

				class Amazons:
					def __init__(self,bot):
						self.bot : commands.Bot = bot
					board = [["__" for i in range(10)] for i in range(10)]
					board = np.array(board)

					white_queen = "W"
					black_queen = "B"

					board[0][3] = black_queen + "0"
					board[0][6] = black_queen + "1"
					board[3][0] = black_queen + "2"
					board[3][9] = black_queen + "3"
					board[6][0] = white_queen + "0"
					board[9][3] = white_queen + "1"
					board[9][6] = white_queen + "2"
					board[6][9] = white_queen + "3"

					def get_elem_where(self, elem):
						return([np.where(Amazons.board == elem)[0][0], np.where(Amazons.board == elem)[1][0]])

					def set_board_at_index(self, index, value):
						Amazons.board[index[0], index[1]] = value
						
					def can_move(self, queen):
						possible_placements = []
						row, column = self.get_elem_where(queen)
						i = column-1
						while i!=-1 and Amazons.board[row][i]=='__':
							possible_placements.append(f"{row}{i}")
							i-=1
							
						i = column+1
						while i!=10 and Amazons.board[row][i]=='__':
							possible_placements.append(f"{row}{i}")
							i+=1
							
						i = row+1
						while i!=10 and Amazons.board[i][column]=='__':
							possible_placements.append(f"{i}{column}")
							i+=1
							
						i = row-1
						while i!=-1 and Amazons.board[i][column]=='__':
							possible_placements.append(f"{i}{column}")
							i-=1
							
						i = row-1
						j = column-1
						while i!=-1 and j!=-1 and Amazons.board[i][j]=='__':
							possible_placements.append(f"{i}{j}")
							i-=1
							j-=1
							
						i = row-1
						j = column+1
						while i!=-1 and j!=10 and Amazons.board[i][j]=='__':
							possible_placements.append(f"{i}{j}")
							i-=1
							j+=1
							
						i = row+1
						j = column-1
						while i!=10 and j!=-1 and Amazons.board[i][j]=='__':
							possible_placements.append(f"{i}{j}")
							i+=1
							j-=1
							
						i = row+1
						j = column+1
						while i!=10 and j!=10 and Amazons.board[i][j]=='__':
							possible_placements.append(f"{i}{j}")
							i+=1
							j+=1
						return possible_placements
					def move_queen(self, queen, coord):
						self.set_board_at_index(self.get_elem_where(queen), "__")
						self.set_board_at_index(coord, queen)
						
					async def play(self):
						possible_queens_white = ["W0", "W1", "W2", "W3"]
						possible_queens_black = ["B0", "B1", "B2", "B3"]
						cnt = 0
						while True:
							queen = 0
							coord = 0
							coord_dot = 0

							print(self.board)
							if cnt % 2 == 0:
								possible_queens = possible_queens_white
								winner = "Black"
								player = "White"
								player_data = get_data(f"games/users/{inter2.user.id}")
								i = inter
							else:
								possible_queens = possible_queens_black
								winner = "White"
								player = "Black"
								player_data = get_data(f"games/users/{inter.user.id}")
								i = inter2
							lose = True
							for element in possible_queens:
								if self.can_move(element)!=[]:
									lose = False
							if lose:
								return winner
							
							await i.response.send_message("Which queen would you like to move?", ephemeral=True)
							#Waiting for the user's response
							def check(message: discord.Message):
								return message.author == i.user and message.channel == i.channel
							try:
								message = await self.bot.wait_for("message", timeout = 180, check = check)
							except asyncio.TimeoutError:
								await inter.followup.send(f"The winner is {winner}!\n{Amazons.board}")
								return 
							queen = simplify(message.content.lower())
							await message.delete()
							while queen not in possible_queens or self.can_move(queen)==[]:
								#Waiting for the user's response
								await i.response.send_message("This is not a possible queen tomove, please choose another queen", ephemeral=True)
								try:
									message = await self.bot.wait_for("message", timeout = 180, check = check)
								except asyncio.TimeoutError:
									await inter.followup.send(f"The winner is {winner}!\n{Amazons.board}")
									return 
								queen = simplify(message.content.lower())
								await message.delete()


							await i.response.send_message("Where would you like to move the queen", ephemeral=True)
							try:
								message = await self.bot.wait_for("message", timeout = 180, check = check)
							except asyncio.TimeoutError:
								await inter.followup.send(f"The winner is {winner}!\n{Amazons.board}")
								return 
							coord = simplify(message.content.upper())
							await message.delete()
							while coord not in self.can_move(queen):
								await i.response.send_message("This is not a vaid position for this queen, choose another position", ephemeral=True)
								try:
									message = await self.bot.wait_for("message", timeout = 180, check = check)
								except asyncio.TimeoutError:
									await inter.followup.send(f"The winner is {winner}!\n{Amazons.board}")
									return 
								coord = simplify(message.content.lower())
								await message.delete()
							new_coord = (int(coord[0]), int(coord[1]))
							self.move_queen(queen, new_coord)

							await i.response.send_message("Where would you like to shoot an arrow", ephemeral=True)
							try:
								coord_dot = await self.bot.wait_for("message", timeout = 180, check = check)
							except asyncio.TimeoutError:
								await inter.followup.send(f"The winner is {winner}!\n{Amazons.board}")
								return 
							coord_dot = simplify(message.content.lower())
							await message.delete()
							while coord_dot not in self.can_move(queen):
								await i.response.send_message("This is not a vaid position for an arrow, choose another position", ephemeral=True)
								try:
									coord_dot = await self.bot.wait_for("message", timeout = 180, check = check)
								except asyncio.TimeoutError:
									await inter.followup.send(f"The winner is {winner}!\n{Amazons.board}")
									return 
								coord_dot = simplify(message.content.lower())
								await message.delete()
							new_coord = (int(coord_dot[0]), int(coord_dot[1]))
							self.set_board_at_index(new_coord, "O") 
							cnt += 1
				

			if user is not None:
				@discord.ui.button(label=f"Refuse",style=discord.ButtonStyle.danger)
				async def sell(self, inter2: discord.Interaction, _: discord.ui.Button):
					

					await inter2.response.send_message(f"{inter.user.mention}, {inter2.user.mention} refused to play", ephemeral = True)
					await self.close("refused")


		txt = f"**{inter.user.name}** wants to play Amazons"
		if user is not None:
			E.set_footer(text=f"Play offer for {user.name}", icon_url=await GetLogLink(self.bot, user.display_avatar.url))

		txt += f"\nends <t:{int(dt.datetime.now().timestamp()) + 60}:R>"

		timeout_date = dt.datetime.now() + dt.timedelta(seconds=60)
		button = Button(timeout_date)

		button.message = await inter.followup.send(txt, embed=E, view=button)



async def traveler(*, bot: commands.Bot):
	# get the bot channel and make sure it is not none
	bot_channel = await bot.fetch_channel(BOT_CHANNEL_ID)
	assert isinstance(bot_channel, discord.TextChannel)

	# 17 science&nature, 18 computer, 19 maths, 22 geography, 24 politics, 27 animals
	r = random.choice([17, 18, 19, 22, 24, 27])
	url = f"https://opentdb.com/api.php?amount=1&category={r}"

	response = requests.get(url)
	data = response.json()

	if data["response_code"] != 0:

		return log('WARNING', "opentdb api returned 0 response code")
	
	# extract the data
	category:str = data["results"][0]["category"]
	difficulty:str = data["results"][0]["difficulty"]
	new_traveler:list[str] = get_data(f"games/created_traveler")
	creator:str = ""
	if len(new_traveler)!=0:
		if len(new_traveler)==6:
			question_type:str = "multiple"
		else:
			question_type:str = "boolean"
		creator = new_traveler[-1]
	else:
		question_type:str = data["results"][0]["type"]
	# convert html entities to normal unicode text
	question:str = html.unescape(data["results"][0]["question"])
	correct_answer:str = html.unescape(data["results"][0]["correct_answer"])
	incorrect_answers:list = list(map(html.unescape, data["results"][0]["incorrect_answers"]))
	if len(get_data(f"games/created_traveler"))!=0:
		question = new_traveler[0]
		correct_answer = new_traveler[1]
		incorrect_answers = new_traveler[2:-1]
		upd_data([], "games/created_traveler")
		difficulty = "Random"
	# create a list of answers and randomize them
	answers = []
	answers.append(correct_answer)
	answers.extend(incorrect_answers)
	random.shuffle(answers)

	correct_answer_index = answers.index(correct_answer)

	# create embed
	E = discord.Embed(title='Traveler', description=f"**{question}**")
	E.description = f"## **{question}**\n\n"
	E.set_footer(text=f"{f'Created by {creator} | 'if len(new_traveler)!=0 else f'Category: {category} | Difficulty: {difficulty} |' }Type: {question_type}")
	E.set_thumbnail(url="https://media.discordapp.net/attachments/709313685226782751/1127893104402386966/traveler.png")

	if difficulty == "easy":
		E.color = discord.Color.green()
	elif difficulty == "medium":
		E.color = discord.Color.gold()
	elif difficulty == "hard":
		E.color = discord.Color.red()
	else:
		E.color = discord.Color.purple()
	
	# check if it will be a traveler or a robber : traveler = 1 and robber = 0
	traveler = random.getrandbits(1)
	if traveler:
		photo = "https://media.discordapp.net/attachments/709313685226782751/1127893104402386966/traveler.png"
	else:
		photo = "https://cdn.discordapp.com/attachments/709313685226782751/1205143937052839946/bandit.png"

	# handle the correct and incorrect cases
	async def correct(inter:discord.Interaction):
		# check if the creator of the traveler is trying to answer the traveler
		if inter.user.name == creator:
			assert inter.guild
			await inter.followup.send("You can't answer your own traveler", ephemeral=True)
			user_data = get_user_data(inter.user.id)
			user_data["ideas"] -= 10
			try :
				member = inter.guild.get_member(inter.user.id)
				assert member
				await member.timeout(dt.timedelta(minutes=0.1), reason="haha mskn")
			except : 
				user_data["ideas"] -= 10
			upd_data(user_data, f"games/users/{inter.user.id}")
			return False
		
		E = discord.Embed(title="Correct!", color=discord.Color.green())
		E.set_thumbnail(url=photo)

		# user_id : {user data}
		user_data = get_user_data(inter.user.id)
		if traveler:
			value = get_value(user_data) 
		else:
			value = int(get_value(user_data)*1.5)

		user_data["roses"] += value
		user_data["ideas"] += 7

		upd_data(user_data, f"games/users/{inter.user.id}")

		if traveler:
			E.description = f"You earned **{value}🌹** and **7💡**"
		else:
			E.description = f"The robber is impressed by your knowledge! You earned **{value}🌹** and **7💡**"

		await inter.followup.send(inter.user.mention, embed=E)

	async def incorrect(inter:discord.Interaction):
		if inter.user.name == creator:
			assert inter.guild
			await inter.followup.send("You can't answer your own traveler", ephemeral=True)
			user_data = get_user_data(inter.user.id)
			user_data["ideas"] -= 10
			try :
				member = inter.guild.get_member(inter.user.id)
				assert member
				await member.timeout(dt.timedelta(minutes=0.1), reason="haha mskn")
			except : 
				user_data["ideas"] -= 10
			upd_data(user_data, f"games/users/{inter.user.id}")
			print(2)
			return False
		E = discord.Embed(title="Incorrect!", color=discord.Color.red())
		E.set_thumbnail(url=photo)

		# user_id : {user data}
		user_data = get_user_data(inter.user.id)
		robber_money=0
		E.description = f"The correct answer was **{correct_answer}**\n"
		if traveler:
			value = 50
			E.description += "The traveler left **50🌹** by accident on the ground" 
		else:

			double_collect_value = get_value(user_data)*2
			value = get_value(user_data)*(-2)
		
		if user_data["roses"]<0 and not traveler:
			E.description += f"You're already in debt so the robber didn't take you anything"
		else:
			robber_money=(-1)*value
			if user_data["roses"]+value<=0:
				robber_money=user_data["roses"]
			user_data["roses"] += value
			if not traveler:
				if user_data["roses"]<0:
					user_data["roses"]=-1
					E.description += f"The robber took you all of your roses 🌹"
				else:
					E.description += f"The robber took you **{double_collect_value}** 🌹"
				robber_money += get_data(f"games/robber_total")
				upd_data(robber_money, "games/robber_total")
			upd_data(user_data, f"games/users/{inter.user.id}")
		await inter.followup.send(inter.user.mention, embed=E)

	# subclass of discord.ui.Button, all buttons will have the same callback (no need for functions)
	class CallbackButton(discord.ui.Button):
		def __init__(self, parent_view:'B_choices', *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.parent_view = parent_view

		async def callback(self, inter: discord.Interaction):
			await inter.response.defer()

			user_data = get_user_data(inter.user.id)
			fail_next = False
			if "fail_next_traveler" in user_data["effects"]:
				user_data["effects"].remove("fail_next_traveler")
				upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
				await incorrect(inter)
				fail_next = True
			else:
				if question_type == "boolean":
					if correct_answer.upper() == self.label:
						await correct(inter) 
					else:
						await incorrect(inter)

				else:
					print(self.label)
					if str(correct_answer_index+1) == self.label:
						await correct(inter)
					else:
						await incorrect(inter)
			if fail_next:
				await inter.followup.send("You had 100% chances of losing today... ", ephemeral=True)
			if difficulty != "Random" or inter.user.name != creator:
				if isinstance(self.parent_view.message, discord.Message):
					await self.parent_view.message.delete()
			print("stopping")
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



@tasks.loop()
async def traveler_loop(*, bot: commands.Bot):
	await traveler(bot=bot)

	# come back in 2 to 10 hours
	random_time = random.randint(7200, 36000)

	await asyncio.sleep(random_time)
"""
@tasks.loop()
async def wordle_traveler(*, bot: commands.Bot):
	word = random.choice(get_words()[2])
	guessed_words = ["STARE", color_function(word, "stare"), "CLOUD", color_function(word, "cloud"), "PINKY", color_function(word, "pinky")]
	already_guessed = ""
	
	for element, index in enumerate(guessed_words):
		if index%2==0:
			already_guessed += f"#{element:^4}"
		else:
			already_guessed += f"{element:^3}"

	E = discord.Embed(title='Wordle', description=f"**{already_guessed}**")
	E.description = f"## **{already_guessed}**\n\n"

	#Et là on fait un petit modal pour la réponse mdr
"""


async def setup(bot:commands.Bot):
	await bot.add_cog(Games(bot))
