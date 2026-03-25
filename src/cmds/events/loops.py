
from discord.ext import commands, tasks

import random
import asyncio
import datetime as dt

from utils import get_data, upd_data, get_belgian_time, get_acnh_data, UserAccount

def reset_wordle_choice() -> None:
	return None

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

class Loops(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot

	@tasks.loop()
	async def midnight_events() -> None:
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

async def setup(bot:commands.Bot):
	print("started midnight events loop")
	Loops.midnight_events.start()