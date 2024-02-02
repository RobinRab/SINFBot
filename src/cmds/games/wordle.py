import discord 
from discord.ext import commands
from discord import app_commands

import random
from typing import Optional, Literal
import csv

from settings import DATA_DIR
from utils import log, get_data, upd_data, get_value, new_user, GetLogLink

class Wordle(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	async def utils_wordle(self, inter:discord.Interaction) -> tuple[discord.Embed, dict]:
		E = discord.Embed()
		E.color = discord.Color.green()
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		try :
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			E.description = f"{inter.user.mention}, You have to collect before to play"
			E.color = discord.Color.red()
			return E, {}
		return E, user_data
	
	@app_commands.command(description="Play today's wordle!")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def wordle(self, inter: discord.Interaction): 
		win=False
		guess_wordle, wordle_list = list_of_words()
		number=random.randint(1, len(wordle_list)-1)
		wordle_word = wordle_list[number]
		print(wordle_word)
		E, user_data = await self.utils_wordle(inter)
		nombre_guess_actuel = len(user_data["wordle"])
		if nombre_guess_actuel != 0:
				print(0)
				already_guessed = ""
				for word in user_data["wordle"]:
					already_guessed+=word+"\n"+user_data["wordle"][word]+"\n\n"
				print(1)
				await inter.followup.send(f"Welcome back ! You're on guess {nombre_guess_actuel}, here are the words you alreday guessed : ", ephemeral=True)
				await inter.followup.send(f"{already_guessed}", ephemeral=True)
		else:
			print(2)
			await inter.response.send_message("Welcome to wordle!")

		while nombre_guess_actuel<5:
			is_allowed_to_wordle=True

			#on attend la réponse de l'user
			def check(message: discord.Message):
				return message.author == inter.user and message.channel == inter.channel
			
			message = await self.bot.wait_for("message", check = check)
			guess_word = message.content.lower()
			if guess_word == "stop":
				await inter.followup.send("Interaction stopped", ephemeral=True)
				break
			#mot doit contenir 5 lettres
			if len(guess_word) != 5:
				await inter.followup.send("This is not a five letter word", ephemeral=True)
				is_allowed_to_wordle=False
				continue
			
			#mot pas dans la liste
			elif guess_word not in guess_wordle: 
				await inter.followup.send("This word is not in the list", ephemeral=True)
				is_allowed_to_wordle=False
				continue
			if is_allowed_to_wordle:
				nombre_guess_actuel = len(user_data["wordle"])
				#appelle de l'autre fonction pour avoir les couleurs
				colors = color_function(wordle_word, guess_word)
				current=""
				current+=guess_word.upper()+"\n"+colors
				await inter.followup.send(f"{current}", ephemeral=True)
				user_data["wordle"][f"{nombre_guess_actuel}"]=colors
				current=""
				print(guess_word)
				print(wordle_word == guess_word)
				print("nombre guess_actuel : ",nombre_guess_actuel, user_data["wordle"])

				if wordle_word == guess_word:
					win=True
					print(1)
					today_colors=""
					for color in user_data["wordle"].values():
						today_colors+=color+"\n"
					nombre_guess_actuel = len(user_data["wordle"])
					print("wtf")
					await inter.followup.send("You won!", ephemeral=True)
					E.description = f"{inter.user.mention} solved today's wordle in {nombre_guess_actuel} guesses ! \n ||{today_colors}||"
					E.color = discord.Color.green()
					print("print")
					break
		if win==False:
			print(f"user_data: {user_data}")
			print(f"inter: {inter}")
			today_colors=""
			for color in user_data["wordle"].values():
				today_colors+=color+"\n"
			await inter.followup.send(f"You lot, the word was {wordle_word}", ephemeral=True)

			E.description = f"{inter.user.mention} lost today. \n ||{today_colors}||"
			E.color = discord.Color.red()
			
def list_of_words()->tuple[list[str], list[str]]:
	guess_wordle : list[str]=[]
	wordle_list : list[str]=[]
	with open(DATA_DIR/"wordle_words.csv", "r") as f:
		for i in csv.reader(f, delimiter=','):
			guess_wordle.append(i[0])
			if len(i[1]) == 6:
				wordle_list.append(i[1].strip())
				
	
	print(guess_wordle)
	print(wordle_list)
	return guess_wordle,wordle_list

def color_function(wordle_word:str, guess_word:str) -> str:
	dico_occurences : dict[str, int] = {}
	#petit dico pour savoir que les doubles lettres soient pas comptées deux fois
	for letter in wordle_word: 
		if letter not in dico_occurences.keys():
			dico_occurences[letter] = 1
		else:
			dico_occurences[letter] += 1
	colors = ""
	colors_list : list[str] = []

	#j'itère dans les lettres paralleles de chaque mot, si la lettre est la même que l'autre c'est vert
	for letter_guess, letter_wordle_word in zip(guess_word, wordle_word): 
		if letter_guess == letter_wordle_word: 
			colors_list.append("🟩")
			dico_occurences[letter_guess] -= 1
		else:
			colors_list.append("1")
	#j'itère dans les lettres paralleles de chaque mot
	for letter_guess, letter_wordle_word, color_test in zip(guess_word, wordle_word, colors_list) : 

		#si c'est "1" (donc pas vert) on check si c'est jaune ou gris
		if color_test == "1": 
			index_1 = colors_list.index("1")

			#vérification des conditions pour qu'une lettre soit jaune 
			#lettre dans le mot && nombre d'occurence check -> yellow
			if letter_guess in wordle_word and dico_occurences[letter_guess] != 0: 
				colors_list[index_1]="🟨"
				#colors_list = colors_list[:index_1] + ["🟨"] + colors_list[index_1 + 1:]
				dico_occurences[letter_guess] -= 1 

			else:
				colors_list[index_1]="🟥"
				#colors_list = colors_list[:index_1] + ["🟥"] + colors_list[index_1 + 1:]

	for color in colors_list:
		colors += color

	return colors

async def setup(bot:commands.Bot):
	await bot.add_cog(Wordle(bot))
		

