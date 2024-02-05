import discord
from discord import app_commands
from discord.ext import commands, tasks

import csv
import random
import asyncio
import datetime as dt

from settings import DATA_DIR
from utils import get_data, upd_data, get_value, get_belgian_time, new_user, GetLogLink

#! fonction 'get_words' accepts 4 columns csv
class Wordle(commands.Cog):
	active_games = {}

	def __init__(self,bot):
		self.bot : commands.Bot = bot

		choose_todays_word.start(bot=self.bot)

	async def get_data_wordle(self, inter:discord.Interaction) -> dict:
		# check if account exists
		try :
			user_data : dict = get_data(f"games/users/{inter.user.id}")
			# create wordle if never played
			if "wordle" not in user_data:
				user_data["wordle"] = {}
		except :
			user_data = new_user()

		upd_data(user_data, f"games/users/{inter.user.id}")

		return user_data

	@app_commands.command(description="Play today's wordle!")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def wordle(self, inter: discord.Interaction):
		E = discord.Embed()
		E.set_author(name=inter.user.name, icon_url = await GetLogLink(self.bot, inter.user.display_avatar.url))
		user_data = await self.get_data_wordle(inter)

		user_id = inter.user.id

		if user_id in Wordle.active_games and Wordle.active_games[user_id]:
			await inter.response.send_message("You are already playing Wordle.", ephemeral=True)
			return
		
		Wordle.active_games[user_id] = True
		
		has_won = False
		guess_list = get_words()[0]
		wordle_word : str = get_data("games/todays_word")
		current_number_guess = len(user_data["wordle"])
		
		already_won = False
		if "🟩🟩🟩🟩🟩" in user_data["wordle"].values():
			already_won = True

		#Check if the person already played today to continue the game
		if current_number_guess>=6 or already_won:
			del Wordle.active_games[user_id]
			return await inter.response.send_message(f"You already played today, see you tomorrow ", ephemeral=True)

		if current_number_guess == 0:
			await inter.response.send_message('''Welcome to wordle!\nWrite your guess to start playing. 
			\nType *stop* to pause the game, recall the function to *restart*.''')

		else:
			already_guessed = ""

			for word in user_data["wordle"]:
				spaced_word = ""
				for letter in word[1:].upper():
					spaced_word += f"{letter:^4}"

				already_guessed += "# " + spaced_word + "\n" + space(user_data["wordle"][word])+"\n"
			await inter.response.send_message( f"Welcome back ! You're on guess {current_number_guess}, here are the words you already guessed : ", ephemeral = True)
			await inter.followup.send(f"{already_guessed}", ephemeral = True)
			await inter.followup.send("Type *stop* to pause the game.", ephemeral = True)

		#The user has 6 chances
		while current_number_guess<6:

			#Waiting for the user's response
			def check(message: discord.Message):
				return message.author == inter.user and message.channel == inter.channel

			message = await self.bot.wait_for("message", timeout = 180, check = check)
			guess_word = message.content.lower()
			await message.delete()
			
			#In case the person wants to stop playing
			if guess_word == "stop":
				Wordle.active_games[user_id] = False
				return await inter.followup.send("See you later", ephemeral=True)
				

			#Word has to be a five letter word
			if len(guess_word) != 5:
				await inter.followup.send("This is not a five letter word", ephemeral=True)
				continue
			
			#Word not int the list
			elif guess_word not in guess_list: 
				await inter.followup.send("This word is not in the list", ephemeral=True)
				continue

			#Gets the colors corresponding to the word and print them

			spaced_word = ""
			for letter in guess_word.upper():
				spaced_word += f"{letter:^4}"

			colors = color_function(wordle_word, guess_word)
			already_guessed = "# " + spaced_word + "\n" + space(colors)+"\n"

			await inter.followup.send(f"{already_guessed}", ephemeral=True)
			
			current_number_guess = len(user_data["wordle"])
			user_data["wordle"][f"{current_number_guess}{guess_word}"]=colors

			upd_data(user_data, f"games/users/{inter.user.id}")
			current_number_guess = len(user_data["wordle"])
			
			#Check if the user won 
			if wordle_word == guess_word:
				has_won=True
				todays_colors=""
				for color in user_data["wordle"].values():
					todays_colors+=color+"\n"

				#Updates the roses of the user
				user_data = await self.get_data_wordle(inter)
				value = get_value(user_data)
				user_data["roses"] += value
				upd_data(user_data, f"games/users/{inter.user.id}")

				#Sends the has_won message
				current_number_guess = len(user_data["wordle"])
				await inter.followup.send("You won!", ephemeral=True)
				E.description = f"{inter.user.mention} solved today's wordle in {current_number_guess} guesses ! \n\n ||{todays_colors}||"
				E.add_field(name="Reward", value=f"You won {value} 🌹!")
				E.color = discord.Color.green()
				await inter.followup.send(embed = E)
				break
		
		if not has_won:
			todays_colors=""
			for color in user_data["wordle"].values():
				todays_colors+=color+"\n"
			await inter.followup.send(f"You lost, the word was **{wordle_word}**", ephemeral=True)
			
			E.description = f"{inter.user.mention} lost today. \n\n ||{todays_colors}||"
			E.color = discord.Color.red()
			await inter.followup.send(embed = E)
			
		del Wordle.active_games[user_id]

#Puts spaces between letters of guessed word and colors
def space(content : str):
	spaced_word = ""
	for letter in content:
		spaced_word += f"{letter:^3}"
	return spaced_word



#Function that creates the lists from the csv
def get_words()->tuple[list[str], list[str]]:
	guess_list : list[str]=[]
	wordle_list : list[str]=[]
	with open(DATA_DIR/"wordle_words.csv", "r") as f:
		for i in csv.reader(f, delimiter=','):
			guess_list.append(i[0])
			if len(i[1]) == 6:
				wordle_list.append(i[1].strip())
	
	#guess_list are the words you can guess (all of the 5 letter words)
	#wordle_list are the words that can be the answer
	return guess_list,wordle_list

def color_function(wordle_word:str, guess_word:str) -> str:
	dico_occurences : dict[str, int] = {}
	#Dictionnary to check repeated letters
	for letter in wordle_word: 
		if letter not in dico_occurences.keys():
			dico_occurences[letter] = 1
		else:
			dico_occurences[letter] += 1
	colors = ""
	colors_list : list[str] = []

	#Iteration in the words to check the green letters
	for letter_guess, letter_wordle_word in zip(guess_word, wordle_word): 
		if letter_guess == letter_wordle_word: 
			colors_list.append("🟩")
			dico_occurences[letter_guess] -= 1
		else:
			colors_list.append("1")

	for letter_guess, letter_wordle_word, color_test in zip(guess_word, wordle_word, colors_list) : 

		#if it is "1" (not green) -> check if it is yellow or grey
		if color_test == "1": 
			index_1 = colors_list.index("1")

			#check the conditions for a letter to be yellow
			#letter in the words && occurence count check -> yellow
			if letter_guess in wordle_word and dico_occurences[letter_guess] != 0: 
				colors_list[index_1]="🟨"
				dico_occurences[letter_guess] -= 1 
			else:
				colors_list[index_1]="🟥"

	for color in colors_list:
		colors += color

	return colors

@tasks.loop()
async def choose_todays_word(bot:commands.Bot) -> None:
	wordle_list = get_words()[1]
	today = get_belgian_time().today()
	tomorrow = today + dt.timedelta(days=1)
	tomorrow_midnight = dt.datetime(year=tomorrow.year, day=tomorrow.day, month= tomorrow.month)

	sleep_time = tomorrow_midnight - today
	wordle_word = random.choice(wordle_list)

	await asyncio.sleep(sleep_time.total_seconds())

	upd_data(wordle_word, "games/todays_word")
	for user_id in get_data("games/users").keys():
		upd_data({}, f"games/users/{user_id}/wordle")
		

async def setup(bot:commands.Bot):
	await bot.add_cog(Wordle(bot))