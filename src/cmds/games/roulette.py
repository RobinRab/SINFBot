import discord 
from discord import app_commands, ui
from discord.ext import commands, tasks

import random
import datetime as dt
from typing import Literal
import asyncio

from settings import BOT_CHANNEL_ID
from utils import get_data, upd_data, GetLogLink, get_value, random_avatar, get_belgian_time
from cmds.games.games import traveler
from cmds.games.gambling import GamblingHelper

class Roulette:
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot
		self.GH = GamblingHelper(bot)

	# Create next traveler  
	async def create_next_traveler(self, inter:discord.Interaction):
		E = discord.Embed()
		E.color = discord.Color.purple()
		E.set_author(name = "Roulette")
		E.description = ("Create the next traveler!\nChoose the question type.")
			
		await inter.followup.send(embed=E, view = self.Create_next_traveler(), ephemeral = True)

	# When we have a create nex traveler, we choose between "True or False" or "MCQ"
	class Create_next_traveler(ui.View):
		def __init__(self):
			super().__init__(timeout=None)

		def disable_all_items(self):
			for item in self.children:
				if isinstance(item, discord.ui.Button):
					item.disabled = True
	
		@discord.ui.button(label = "True or False", style = discord.ButtonStyle.green)
		async def true_or_false(self, inter:discord.Interaction, Button = ui.Button):
			await inter.response.send_modal(Roulette.Traveler_true_or_false())
			self.disable_all_items()
			await inter.edit_original_response(view=self)

		@discord.ui.button(label = "MCQ", style = discord.ButtonStyle.red)
		async def mcq(self, inter:discord.Interaction, Button = ui.Button):
			await inter.response.send_modal(Roulette.Traveler_MCQ())
			self.disable_all_items()
			await inter.edit_original_response(view=self)

	# Create a True or False traveler
	class Traveler_true_or_false(ui.Modal, title = "True or false"):
		question = ui.TextInput(label='Question')
		
		# After clicking on the "True or False" button we choose the right answer
		async def on_submit(self, interaction: discord.Interaction):
			await interaction.response.send_message(f'Choose the right answer:', view = Roulette.Choose_correct_answer(),ephemeral=True)
			next_traveler : list[str] = []
			next_traveler.append(str(self.question))
			upd_data(next_traveler, f"games/created_traveler")

	# Create a MCQ traveler
	class Traveler_MCQ(discord.ui.Modal, title = "MCQ"):
		question = ui.TextInput(label='Question')
		correct_answer = ui.TextInput(label='Correct answer', style=discord.TextStyle.paragraph)
		wrong_answer1 = ui.TextInput(label="Wrong answer1", style=discord.TextStyle.paragraph)
		wrong_answer2 = ui.TextInput(label="Wrong answer2", style=discord.TextStyle.paragraph)
		wrong_answer3 = ui.TextInput(label="Wrong answer3", style=discord.TextStyle.paragraph)

		# After clicking on the "MCQ" button we choose the right answer and the wrong ones
		async def on_submit(self, interaction: discord.Interaction):
			await interaction.response.send_message(f'Traveler set! You are not allowed to answer it when it arrives, or there will be consequences', ephemeral=True)
			next_traveler : list[str] = []
			next_traveler.append(str(self.question))
			next_traveler.append(str(self.correct_answer))
			next_traveler.append(str(self.wrong_answer1))
			next_traveler.append(str(self.wrong_answer2))
			next_traveler.append(str(self.wrong_answer3))
			next_traveler.append(interaction.user.name)
			
			upd_data(next_traveler, f"games/created_traveler")

	class Choose_correct_answer(ui.View):
		def __init__(self):
			super().__init__(timeout=None)
			self.answer = None

		def disable_all_items(self):
			for item in self.children:
				if isinstance(item, discord.ui.Button):
					item.disabled = True

		# Choosing "True" as the right answer
		@discord.ui.button(label = "True", style = discord.ButtonStyle.green)
		async def true(self, inter:discord.Interaction, Button: ui.Button):
			self.disable_all_items()
			await inter.response.edit_message(view=self)
			self.answer = True
			await inter.followup.send(f'Traveler set! You are not allowed to answer it when it arrives, or there will be consequences', ephemeral=True)
			next_traveler : list[str] = get_data(f"games/created_traveler")
			next_traveler.append("True")
			next_traveler.append("False")
			next_traveler.append(inter.user.name)
			upd_data(next_traveler, "games/created_traveler")
			
		# Choosing "False" as the right answer
		@discord.ui.button(label = "False", style = discord.ButtonStyle.red)
		async def false(self, inter:discord.Interaction, Button: ui.Button):
			self.disable_all_items()
			await inter.response.edit_message(view=self)
			self.answer = False
			await inter.followup.send(f'Traveler set! You are not allowed to answer it when it arrives, or there will be consequences', ephemeral=True)
			next_traveler : list[str] = get_data(f"games/created_traveler")
			next_traveler.append("False")
			next_traveler.append("True")
			next_traveler.append(inter.user.name)
			upd_data(next_traveler, "games/created_traveler")
	
	async def embed(self, inter : discord.Interaction, E : discord.Embed):
		url = random_avatar()
		if inter.user.avatar:
			url = inter.user.avatar.url
		E.set_author(name=inter.user.display_name, url = await GetLogLink(self.bot, url))
		E.set_footer(text="Roulette by Scylla and Ceisal")
		E = discord.Embed(title="Roulette")
		return E
	
	async def roulette(self, inter:discord.Interaction, other_user:discord.Member):
		assert inter.guild
		
		has_been_answered = False

		E, user_data = await self.GH.check(inter)

		class FreeSpin(ui.View):
			def __init__(self):
				super().__init__(timeout=60)
				self.clicked = asyncio.Future()

			@discord.ui.button(label="🎰 Free spin!", style=discord.ButtonStyle.green)
			async def free_spin(self, inter: discord.Interaction, button: ui.Button):
				if not self.clicked.done():
					self.clicked.set_result(inter)

				button.disabled = True
				await inter.response.edit_message(view=self)

		try:
			await inter.response.defer()
			if dt.datetime.now().timestamp() - get_data(f"games/users/{inter.user.id}/last_roulette") < 60 and get_data(f"games/users/{inter.user.id}/last_roulette") != -1:
				E.description = f"Be patient, you have to wait a minute before using the roulette again :)"
				E.color = discord.Color.red()
				return await inter.followup.send(embed=E, ephemeral=True)
			if user_data["candies"]<1 and user_data["free_sunday_roll"] == 0:
				E.description = f"{inter.user.mention}, You don't have enough 🍬"
				E.color = discord.Color.red()
				return await inter.followup.send(embed=E)
			
			try :
				other_user_data : dict = get_data(f"games/users/{other_user.id}")
			except :
				return await inter.followup.send("This user doesn't have an account", ephemeral=True)
			
			if other_user_data==user_data:
				return await inter.followup.send("You can't choose yourself", ephemeral=True)

			#Are those three lines needed ? Url avatar is done previously with 
			#inter.user.display_avatar.url in self.check definition
			url = random_avatar()
			if inter.user.avatar:
				url = inter.user.avatar.url
			
			E.set_author(name=inter.user.display_name, url = await GetLogLink(self.bot, url))
			E.set_footer(text="Roulette by Scylla and Ceisal")
			E = discord.Embed(title="Roulette")
			E.color = discord.Color.purple()

			if get_data((f"games/users/{inter.user.id}/last_roulette")) == -1:
				upd_data(dt.datetime.now().timestamp(), f"games/users/{inter.user.id}/last_roulette")

				print("first time")   
				E.colour = discord.Colour.gold()
				E.description = f"Welcome to the Roulette, {inter.user.mention}! As it's your first time, you get a free spin! \nYou can consult the help command to know more about this feature.\n Enjoy!"

				view = FreeSpin()
				await inter.followup.send(embed=E, view=view)
				try:
					interaction = await asyncio.wait_for(view.clicked, timeout=60)
				except asyncio.TimeoutError:
					await inter.followup.send(
						"Are you still here? You can try again later",
						ephemeral=True
					)
					upd_data(-1, f"games/users/{inter.user.id}/last_roulette")

					return

			elif user_data["free_sunday_roll"] == 0:
				E.description = f"{inter.user.mention} used the roulette! It costs only one 🍬."
				await inter.followup.send(embed = E)
				upd_data(user_data["candies"]-1, f"games/users/{inter.user.id}/candies")
				print("updated")

			else:
				E.colour = discord.Colour.gold()
				E.description = f"{inter.user.mention} used the roulette! Free sunday roll!"

				view = FreeSpin()
				await inter.followup.send(embed=E, view=view)
				try:
					await asyncio.wait_for(view.clicked, timeout=60)
				except asyncio.TimeoutError:
					await inter.followup.send(
						"Are you still here? You can try again later",
						ephemeral=True
					)
					upd_data(-1, f"games/users/{inter.user.id}/last_roulette")

					return
				#Il faut une variable free_sunday_roll globale, qui indique si c'est dimanche.
				#et une variable free_roll individuelle, qui indique si le free roll du 
				#dimanche a déjà été utilisé ou pas.
				upd_data(0, f"games/users/{inter.user.id}/free_sunday_roll")

		except:
			pass
		upd_data(dt.datetime.now().timestamp(), f"games/users/{inter.user.id}/last_roulette")

		current_created_traveler = 1
		if get_data(f"games/created_traveler")!=[]:
			current_created_traveler = 0

		consequences = {
			"level_up" : 2,
			"level_down" : 2,
			"tech_up" : 5,
			"tech_down" : 5,
			"timeout_someone" : 5,
			"timeout_myself" : 7.5,
			"next_bet_all" : 5,
			"wordle_guess_reduced" : 5,
			"traveler_spawn" : 5.5, 
			"create_next_traveler" : 8 * current_created_traveler,
			"fail_next_traveler" : 5, 
			"chances_next_bet_x2" : 4, 
			"chances_next_bet_/2" : 4, 
			"next_gain_x3" : 4, 
			"next_gain_/3" : 4, 
			"next_bet_someone_else" : 3, 
			"steal_collect_x2" : 3, 
			"choose_name_level_up" : 3, 
			"choose_name_level_down" : 3, 
			"next_collect_x3" : 3, 
			"next_gain_x10" : 2, 
			"next_gain_/10" : 2, 
			"change_bet_method" : 5, 
			"free_flip_when_collect" : 5, 
			"bank_double": 2, 
			"bank_robbery" : 2, 
		}

		#Modify this line to make tests.
		cons = random.choices(list(consequences.keys()), list(consequences.values()))[0]
		cons = "create_next_traveler" 
		print(cons) 
		has_been_answered = False
		url = random_avatar()

		# Roulette's header
		if inter.user.avatar:
			url = inter.user.avatar.url
		E.set_author(name=inter.user.display_name, url = await GetLogLink(self.bot, url))
		E.set_footer(text="Roulette by Scylla and Ceisal")
		E = discord.Embed(title="Roulette")

		if cons == "level_up":
			has_been_answered = True
			user_data["level"]+=1
			upd_data(user_data["level"], f"games/users/{inter.user.id}/level")
			E.colour = discord.Colour.green()
			E.description = f"Congratulations you leveled-up to level **{user_data['level']}**!"
			await inter.followup.send(embed=E)
			
		elif cons=="level_down":
			has_been_answered = True
			if user_data["level"]>0:
				user_data["level"]-=1
				upd_data(user_data["level"], f"games/users/{inter.user.id}/level")
				E.colour = discord.Colour.red()
				E.description = f"Haha noob you leveled-down to level **{user_data['level']}**"
				await inter.followup.send(embed=E)
			else:
				# If the user is at level 0 they're note leveled down
				E.colour = discord.Colour.red()
				E.description = f"You didn't level down because you're already level 0..."
				await inter.followup.send(embed=E)

		elif cons=="tech_up":
			has_been_answered = True
			user_data["tech"]+=1
			upd_data(user_data["tech"], f"games/users/{inter.user.id}/tech")
			E.colour = discord.Colour.green()
			E.description = f"Congratulations you upgraded your tech to level **{user_data['tech']}**:gear:!"
			await inter.followup.send(embed=E)

		elif cons=="tech_down":
			has_been_answered = True
			if user_data["tech"]>0:
				user_data["tech"]-=1
				upd_data(user_data["tech"], f"games/users/{inter.user.id}/tech")
				E.colour = discord.Colour.red()
				E.description = f"Haha noob you downgraded your tech to level **{user_data['tech']}**:gear:!"
				await inter.followup.send(embed=E)
			else:
				# If the user is at level 0 they're note teched down
				E.colour = discord.Colour.purple()
				E.description = f"You didn't tech level down because you're already level 0..."
				await inter.followup.send(embed=E)

		elif cons=="timeout_someone": #inter user -> discord member 
			has_been_answered = True
			if not other_user.guild_permissions.administrator:
				await other_user.timeout(dt.timedelta(minutes=30), reason="haha mskn")
				E.colour = discord.Colour.green()
				E.description = f"{inter.user.mention} got {other_user.mention} timed out! I see some beef coming." 
				return await inter.followup.send(embed=E)
			elif not inter.permissions.administrator: 
				# If the user is an admin they cannot be timed out
				member = inter.guild.get_member(inter.user.id)
				assert member
				await member.timeout(dt.timedelta(minutes=30), reason="haha mskn encore plus")
				E.colour = discord.Colour.purple()
				E.description = f"{inter.user.mention} tried to timeout {other_user.mention} and got karmadd"
				await inter.followup.send(embed=E)
				return 
			else:
				await self.roulette(inter, other_user)

		elif cons == "traveler_spawn":
			has_been_answered = True
			E.colour = discord.Colour.purple()
			E.description = f"Look, there, a traveler!" 
			await inter.followup.send(embed=E)
			asyncio.create_task(traveler(bot=self.bot))
			return 
		
		elif cons=="timeout_myself":
			has_been_answered = True
			if not inter.permissions.administrator:
				member = inter.guild.get_member(inter.user.id)
				assert member 
				await member.timeout(dt.timedelta(minutes=60), reason="haha mskn encore plus")
				E.description = f"{inter.user.mention} got themselves timed out. See you later!" 
				await inter.followup.send(embed=E)
			else:
				await self.roulette(inter, other_user)

		# The robber steals the roses in the user's bank and puts it in robber_total
		elif cons == "bank_robbery":
			has_been_answered = True
			robber_money : int = get_data(f"games/users/{inter.user.id}/bank/roses")
			robber_money += get_data(f"games/robber_total")
			upd_data(0, f"games/users/{inter.user.id}/bank/roses")
			upd_data(robber_money, "games/robber_total")
			E.colour = discord.Colour.purple()
			E.description = f"{inter.user.mention} your bank got robbed.\nThe Robber got all the money you put in there."
			await inter.followup.send(embed=E)

		elif cons == "bank_double":
			has_been_answered = True
			double_money = get_data(f"games/users/{inter.user.id}/bank/roses")
			double_money+=double_money
			upd_data(double_money, f"games/users/{inter.user.id}/bank/roses")
			E.colour = discord.Colour.purple()
			E.description = f"{inter.user.mention} your bank got multiplied by two!"
			await inter.followup.send(embed=E)

		elif cons == "steal_collect_x2":
			has_been_answered = True
			value = get_value(other_user_data)*2
			user_data["roses"] += value
			other_user_data["roses"] -= value
			upd_data(other_user_data["roses"], f"games/users/{other_user.id}/roses")
			upd_data(user_data["roses"], f"games/users/{inter.user.id}/roses")

			E.colour = discord.Colour.purple()
			E.description = f"{inter.user.mention} stole two collects from {other_user.mention}!"
			await inter.followup.send(embed=E)

		elif cons=="choose_name_level_up":
			has_been_answered = True
			other_user_data["level"]+=1
			upd_data(other_user_data["level"], f"games/users/{other_user.id}/level")
			E.colour = discord.Colour.purple()
			E.description = f"Congratulations you leveled-up {other_user.mention} to level **{other_user_data['level']}**!"
			await inter.followup.send(embed=E)

		elif cons=="choose_name_level_down":
			has_been_answered = True
			other_user_data["level"]-=1
			upd_data(other_user_data["level"], f"games/users/{other_user.id}/level")
			E.colour = discord.Colour.purple()
			E.description = f"Haha, you leveled-down {other_user.mention} to level **{other_user_data['level']}**!"
			await inter.followup.send(embed=E)

		elif cons=="next_bet_all":
			user_data["effects"].append("next_bet_all")

		elif cons=="wordle_guess_reduced":
			user_data["effects"].append("wordle_guess_reduced")

		elif cons == "next_gain_x3":
			user_data["effects"].append("next_gain_x3")
			user_data["effects"].append("next_gain")

		elif cons == "next_gain_/3":
			user_data["effects"].append("next_gain_/3")
			user_data["effects"].append("next_gain")

		elif cons == "next_gain_x10":
			user_data["effects"].append("next_gain_x10")
			user_data["effects"].append("next_gain")

		elif cons == "next_gain_/10":
			user_data["effects"].append("next_gain_/10")
			user_data["effects"].append("next_gain")

		elif cons == "next_bet_someone_else":
			other_user_data["effects"].append("next_bet_all")
			upd_data(other_user_data["effects"], f"games/users/{other_user.id}/effects")

		elif cons == "chances_next_bet_x2":
			user_data["effects"].append("chances_next_bet_x2")

		elif cons == "chances_next_bet_/2":
			user_data["effects"].append("chances_next_bet_/2")

		elif cons == "fail_next_traveler":
			user_data["effects"].append("fail_next_traveler")

		elif cons == "change_bet_method":
			user_data["effects"].append("change_bet_method")

		elif cons == "free_flip_when_collect":
			user_data["effects"].append("free_flip_when_collect")

		elif cons == "next_collect_x3":
			user_data["effects"].append("next_collect_x3")
			
		elif cons == "create_next_traveler":
			has_been_answered = True
			await self.create_next_traveler(inter)
		
		if not has_been_answered:
			await inter.followup.send("A random effect has been applied to one of you, wait and see", ephemeral=True)

		upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")


# Every user has a free roll every sunday
@tasks.loop()
async def free_sunday_roll() -> None:
	# Current day and time
	now = get_belgian_time()

	# Puts the right value in free_sunday_roll depending on the day (Sunday/Other day that Sunday)
	if 6-now.weekday()!=0:
		for user_id in get_data("games/users").keys():
			upd_data(0, f"games/users/{user_id}/free_sunday_roll")
	else:
		for user_id in get_data("games/users").keys():
			upd_data(1, f"games/users/{user_id}/free_sunday_roll")

	# Next Sunday and the sleep needed between now and next_sunday_midnight
	next_sunday = now + dt.timedelta(days = 6-now.weekday())
	next_sunday_midnight = dt.datetime(next_sunday.year, next_sunday.month, next_sunday.day, 0, 0, 0)
	sleep = (next_sunday_midnight - now).total_seconds()

	await asyncio.sleep(sleep)

	for user_id in get_data("games/users").keys():
		upd_data(1, f"games/users/{user_id}/free_sunday_roll")
	
	# Sleeps for a day then puts free_sunday_roll to 0
	await asyncio.sleep(86400)

	for user_id in get_data("games/users").keys():
		upd_data(0, f"games/users/{user_id}/free_sunday_roll")

class Roulette_bis(commands.Cog):
	def __init__(self, bot):
		self.bot : commands.Bot = bot
		self.R = Roulette(bot)
		free_sunday_roll.start()

	@app_commands.command(description="Spins the wheel")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def roulette(self, inter:discord.Interaction, other_user:discord.Member):
		await self.R.roulette(inter, other_user)

async def setup(bot:commands.Bot):
	await bot.add_cog(Roulette_bis(bot))