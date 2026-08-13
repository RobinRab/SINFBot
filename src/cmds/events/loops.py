
from discord.ext import commands, tasks

import random
import asyncio
import datetime as dt
import discord

from cmds.games.wordle import get_words
from utils import get_data, upd_data, get_belgian_time, get_acnh_data, UserAccount
from settings import BOT_CHANNEL_ID


def reset_wordle_choice() -> None:
	#user_data = await self.get_data_wordle(inter)

	languages = ["en", "fr", "sp", "ge"]
	w_data = get_words()
	
	#Chooses new daily wordle word
	for l in languages:
		upd_data(random.choice(w_data[f"wordle_list_{l}"]), f"games/todays_word_{l}")

	for user_id in get_data("games/users").keys():
		user_data = get_data(f"games/users/{user_id}")
		
		for l in languages:
			#Resets/increases user's streak + updates best streak
			if user_data[f"wordle_stats_{l}"]["todays_w_results_shown"] == 0:
				user_data[f"wordle_stats_{l}"]["streak"] = 0
			
			#Resets wordle guesses for every user
			user_data[f"wordle_{l}"] = {}
			user_data[f"wordle_stats_{l}"]["todays_w_results_shown"] = 0


		upd_data(user_data, f"games/users/{user_id}")

def reset_daily_villagers() -> None:
	# empty the list of the people who have stopped the meeting today
	data : dict[str, UserAccount]= get_data('games/users')

	for user_id, user_data in data.items():
		user_villagers = user_data.get('villagers', [])

		acnh = get_acnh_data()

		# select one random villager from villagers.json not in user_villagers
		choices = [name for name in acnh.keys() if name not in user_villagers]

		data[user_id]['villager_of_the_day'] = random.choice(choices)

	upd_data(data, 'games/users')

def reset_daily_traveler() -> None:
	data = get_data('games/users')

	for user_id, _ in data.items():
		data[user_id]['has_got_daily_traveler'] = False

	upd_data(data, 'games/users')


def free_sunday_roll() -> None:
    # Current day and time
    now = get_belgian_time()

    # Puts the right value in free_sunday_roll depending on the day (Sunday/Other day that Sunday)
    if now.weekday() != 6:
        for user_id in get_data("games/users").keys():
            upd_data(0, f"games/users/{user_id}/free_sunday_roll")
    else:
        for user_id in get_data("games/users").keys():
            upd_data(1, f"games/users/{user_id}/free_sunday_roll")

class Loops(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot
		self.midnight_events.start()

	@tasks.loop()
	async def midnight_events(self) -> None:
		now = get_belgian_time()
		tomorrow = now + dt.timedelta(days=1)

		date = dt.datetime(tomorrow.year, tomorrow.month, tomorrow.day)

		sleep = (date - now).total_seconds()
		await asyncio.sleep(sleep)
		print(f"{get_belgian_time()} --- Midnight event triggered")

		# select today's wordle words
		reset_wordle_choice()

		# animal crossing villagers
		reset_daily_villagers()

		# new day, new traveler
		reset_daily_traveler()

		#if sunday, free sunday roll for everyone
		free_sunday_roll()

		#Lotto results
		if now.weekday() == 6:
			await self.lotto_results()

	async def lotto_results(self) -> None:
		channel = self.bot.get_channel(BOT_CHANNEL_ID)
		# Chooses the correct guess for the lotto
		correct_guess : int = random.randint(1, 15)
		users = get_data("games/users")
		winner : str = ""
		E = discord.Embed()
		E.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1219558860516364302/1497938622018486373/lotto-2.png?ex=69ef578d&is=69ee060d&hm=950c4d2bf75c0b50ce7073fbf5f7bd7ddc5181abf4b1bfb7af56ebc09e414310&")
		E.title = "Lotto day! :sparkles:"
		# Check if there is a winner 
		for user in users:
			if get_data(f"games/users/{user}/lotto_guess") == correct_guess:
				winner = user
		
		# No winner
		if len(winner) == 0:
			E.color = discord.Color.red()
			E.description = f"Nobody won this week! The correct answer was {correct_guess}\n\nA new lotto will be held next sunday, don't forget to guess! The robber total is currently {get_data('games/robber_total')} roses!"

		# The winner wins the robber's money
		else:
			E.color = discord.Color.gold()
			E.description = f"The winner is <@!{winner}>! They won {get_data('games/robber_total')} roses. Congrats! The correct answer was {correct_guess}\n\nA new lotto will be held next sunday, don't forget to guess! The robber total is now 0"
			roses = get_data(f"games/users/{winner}/roses") + get_data("games/robber_total")
			upd_data(roses, f"games/users/{winner}/roses")
			upd_data(0, "games/robber_total")

		for user_id in get_data("games/users").keys():
			upd_data(-1, f"games/users/{user_id}/lotto_guess")
		await channel.send(embed=E)

async def setup(bot:commands.Bot):
	print("started midnight events loop")
	await bot.add_cog(Loops(bot))