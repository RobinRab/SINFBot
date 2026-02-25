import discord 
from discord import app_commands
from discord.ext import commands

import random
import csv
import json

import datetime as dt
from typing import Literal, Optional
currencies = Literal["🌹", "🍬", "💡"]

from settings import DATA_DIR
from utils import get_data, upd_data, new_user, get_acnh_data, get_acnh_musics

# all data from : https://docs.google.com/spreadsheets/d/13d_LAJPlxMa_DubPTuirkIV4DERBMXbrWQsmSh8ReK4/edit?gid=1289224346#gid=1289224346
#todo: do something on their birthday? (no abuse)
"""
- aide traveller (10%)
- trouver bonbon/trucs ?
- rembourser un gamble perdu (1%)
- te donne un mot match mes règles du worlde (50%)
"""


class AnimalCrossing(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Get the profile of an Animal Crossing villager")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(name="The name of the villager")
	async def stalk(self, inter:discord.Interaction, name:str):
		embed = self.build_embed_from_name(name)
		await inter.response.send_message(embed=embed)

	@stalk.autocomplete("name")
	async def user_autocomplete(self, _: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
		acnh = get_acnh_data()

		# list of tuple (display_name, value)
		choices = []
		for villager in get_acnh_data().keys():
			specie =  self.animals.get(acnh[villager]['Species'], '❔')
			personnality = self.personnalities.get(acnh[villager]['Personality'], '❔')
			entry = f"{specie} {villager} {personnality}"
			if current.lower() in entry.lower():
				choices.append((f"{specie} {villager} {personnality}", villager))

		# only keep the first 25 and convert them to choices
		final_choices = []
		for name, value in choices[:25]:
			final_choices.append(app_commands.Choice(name=name, value=value))

		return final_choices

	@app_commands.command(description="Meet once a day a random Animal Crossing villager")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	async def meet(self, inter:discord.Interaction):
		await inter.response.defer()

		try :
			user_data : dict = get_data(f"games/users/{inter.user.id}")
		except :
			user_data = new_user()
			#

		acnh = get_acnh_data()

		if user_data["villager_of_the_day"] == "":
			while True:
				villager_name = random.choice(list(acnh.keys()))
				if villager_name not in user_data['villagers']:
					break
		elif user_data["villager_of_the_day"] == "[STOP]":
			await inter.followup.send("You have already met your villager today", ephemeral=True)
			return
		else:
			villager_name = user_data["villager_of_the_day"]
		
		# save the villager as met today
		user_data["villager_of_the_day"] = villager_name
		upd_data(user_data, f"games/users/{inter.user.id}")

		embed = self.build_embed_from_name(villager_name)

		class Button(discord.ui.View):
			def __init__(self, timeout:int):
				super().__init__(timeout=timeout)
				self.message : Optional[discord.Message]

				self.end = f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>"

			async def interaction_check(self, inter2: discord.Interaction):
				if inter2.user.id != inter.user.id:
					await inter2.response.send_message("❌ This is not your villager ❌", ephemeral=True)
					return False
				return True

			@discord.ui.button(label="yes",style=discord.ButtonStyle.green, custom_id="yes")
			async def yes(self, inter2: discord.Interaction, _: discord.ui.Button):
				user_data : dict = get_data(f"games/users/{inter.user.id}")

				villagers = user_data['villagers']

				user_level = user_data.get('level', 0)
				# start with 1 villager at level 0, then gain 1 more villager every 5 levels, up to 5 villagers max
				allowed_number_of_villagers = min(1 + (user_level // 5), 5)

				if len(villagers) >= allowed_number_of_villagers:
					#! chooose one villager to kick
					# remove the current buttons:
					for item in self.children:
						if isinstance(item, discord.ui.Button):
							self.remove_item(item)

					kickView = AnimalCrossing.VillagersView(viewUserID=inter.user.id, villagers=villagers, timeout=180)
					#setup view kick button
					if 1: 
						confirm_kick = 0
						confirm_villager = ""
						label = f"Kick ({confirm_kick}/3)"
						# add a close button (row 3 will always be empty, so bottom)
						close_btn = discord.ui.Button(label=label, style=discord.ButtonStyle.danger, custom_id="Kick", row=3)
						async def _kick(inter: discord.Interaction, button: discord.ui.Button = close_btn):
							nonlocal confirm_kick
							nonlocal confirm_villager
							if confirm_villager == kickView.current:
								confirm_kick += 1
							else:
								confirm_villager = kickView.current
								confirm_kick = 1
					
							if confirm_kick < 3:
								button.label = f"Kick ({confirm_kick}/3)"
								return await inter.response.edit_message(view=kickView)
							
							#! 3 confirms, kick the current villager
							else  :
								# disable all buttons and remove the view
								for child in kickView.children:
									if isinstance(child, discord.ui.Button):
										child.disabled = True
								# remove the close button
								kickView.remove_item(button)
							
								# change the data
								user_data['villagers'].remove(kickView.current)
								user_data['villagers'].append(villager_name)
								user_data['villager_of_the_day'] = "[STOP]"
								upd_data(user_data, f"games/users/{inter.user.id}")
							
								await inter.response.edit_message(view=None, embed=embed, content=f"You have kicked {kickView.current} from your villagers.\nBut {villager_name} has joined your villagers! 🎉")
								kickView.stop()
						
						close_btn.callback = _kick #type:ignore
						kickView.add_item(close_btn)

					embeds = kickView.embeds
					first_name = villagers[0]
					kickView.message = self.message
					await inter2.response.edit_message(content=f"You cannot have more than 5 villagers! Please free up some space before adding {villager_name}.",embed=embeds[first_name],  view=kickView)
					return
				

				await inter2.response.edit_message(content=f"{villager_name} has been added to your villagers! 🎉", view=None)
				# The user can no longer use the command today
				upd_data("[STOP]", f"games/users/{inter.user.id}/villager_of_the_day")

				# add the villager to the user's villagers
				
				user_data['villagers'].append(villager_name)
				upd_data(user_data, f"games/users/{inter.user.id}")
				await self.close()

			@discord.ui.button(label="no",style=discord.ButtonStyle.danger, custom_id="no")
			async def no(self, inter2: discord.Interaction, _: discord.ui.Button):
				await inter2.response.edit_message(content=f"{villager_name} will not join your villagers", view=None)
				# The user can no longer use the command today
				upd_data("[STOP]", f"games/users/{inter.user.id}/villager_of_the_day")
				await self.close()

			@discord.ui.button(label="I need more time",style=discord.ButtonStyle.blurple, custom_id="I need more time")
			async def considering(self, inter2: discord.Interaction, _: discord.ui.Button):
				await inter2.response.edit_message(content=f"Take your Time!", view=None)
				await self.close()

			async def on_timeout(self):
				await self.close()

			async def close(self):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True
				self.stop()

		button = Button(timeout=180)
		button.message = await inter.followup.send(view=button, embed=embed, content=f"{villager_name} wants to join your villagers! Do you accept?")


	@app_commands.command(description="Visit your Animal Crossing village")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe()
	async def village(self, inter:discord.Interaction, user:Optional[discord.User]=None):

		user_id = inter.user.id
		if user is not None:
			user_id = user.id

		await inter.response.defer()
		try:
			user_data : dict = get_data(f"games/users/{user_id}")
		except:
			user_data = new_user()
			upd_data(user_data, f"games/users/{inter.user.id}")
			if user_id == inter.user.id:
				return await inter.followup.send("You have no villagers yet! Use `/meet` to meet one!", ephemeral=True)
			else:
				return await inter.followup.send(f"{user} has no villagers yet!", ephemeral=True)

		villagers = user_data['villagers']
		if len(villagers) == 0:
			if user_id == inter.user.id:
				return await inter.followup.send("You have no villagers yet! Use `/meet` to meet one!", ephemeral=True)
			else:
				return await inter.followup.send(f"{user} has no villagers yet!", ephemeral=True)
		
		
		view = AnimalCrossing.VillagersView(viewUserID=inter.user.id, villagers=villagers, timeout=180)
		#setup view close button
		if 1: 
			# add a close button (row 3 will always be empty, so bottom)
			close_btn = discord.ui.Button(label="Close", style=discord.ButtonStyle.danger, custom_id="close", row=3)
			async def _close_cb(inter: discord.Interaction, button: discord.ui.Button = close_btn):
				# disable all buttons and remove the view
				for child in view.children:
					if isinstance(child, discord.ui.Button):
						child.disabled = True
				# remove the close button
				view.remove_item(button)
				await inter.response.edit_message(view=view)
				view.stop()
		
			close_btn.callback = _close_cb #type:ignore
			view.add_item(close_btn)

		embeds = view.embeds
		first_name = villagers[0]

		txt = f"Village of {inter.user.display_name}"
		if user_id != inter.user.id:
			user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
			txt = f"Village of {user.display_name}"
		view.message = await inter.followup.send(embed=embeds[first_name], view=view, content=txt)


	animals = {
		"Alligator": "🐊",
		"Anteater": "🐜",
		"Bear": "🐻",
		"Bird": "🐦",
		"Bull": "🐂",
		"Cat": "🐈",
		"Chicken": "🐔",
		"Cow": "🐮",
		"Cub": "🐻",
		"Deer": "🦌",
		"Dog": "🐶",
		"Duck": "🦆",
		"Eagle": "🦅",
		"Elephant": "🐘",
		"Frog": "🐸",
		"Goat": "🐐",
		"Gorilla": "🦍",
		"Hamster": "🐹",
		"Hippo": "🦛",
		"Horse": "🐴",
		"Kangaroo": "🦘",
		"Koala": "🐨",
		"Lion": "🦁",
		"Monkey": "🐒",
		"Mouse": "🐭",
		"Octopus": "🐙",
		"Ostrich": "🦃",
		"Penguin": "🐧",
		"Pig": "🐷",
		"Rabbit": "🐰",
		"Rhinoceros":"🦏",
		"Sheep": "🐑",
		"Squirrel": "🐿️",
		"Tiger": "🐯",
		"Wolf": "🐺",
	}

	personnalities = {
		"Big Sister": "😜", 
		"Snooty": "💄",
		"Smug": "😎",
		"Jock": "💪",
		"Cranky": "😒",
		"Peppy": "🤩",
		"Normal": "☺️",
		"Lazy": "🥺",
	}

	genders = {
		"Male": "♂️",
		"Female": "♀️",
	}

	@staticmethod
	def build_embed_from_name(name:str) -> discord.Embed:
		acnh = get_acnh_data()
		villager_info = acnh[name]

		name = villager_info['Name']
		species = villager_info['Species']
		parsed_species = f"{AnimalCrossing.animals.get(species, '❔')} {species}"

		gender = villager_info['Gender']
		parsed_gender = f"{AnimalCrossing.genders.get(gender, '❔')} {gender}"

		personality = villager_info['Personality']
		parsed_personality = f"{AnimalCrossing.personnalities.get(personality, '❔')} {personality}"

		birthday = villager_info['Birthday']
		catchphrase = villager_info['Catchphrase']
		hobby = villager_info['Hobby']
		favorite_song = villager_info['Favorite Song']
		favorite_saying = villager_info['Favorite Saying']
		bubble_color = villager_info['Bubble Color']
		filename = villager_info['Filename']

		url = get_acnh_musics().get(favorite_song, "")

		embed = discord.Embed(
			title=f"{AnimalCrossing.animals.get(species, '❔')} {name} {AnimalCrossing.personnalities.get(personality, '❔')}",
			color=discord.Color.from_str(bubble_color)
		)

		icon = f"https://nh-cdn.catalogue.ac/NpcIcon/{filename}.png"
		photo = f"https://nh-cdn.catalogue.ac/NpcBromide/NpcNml{filename.capitalize()}.png"

		# image from Unique Entry ID
		embed.description = f'"{favorite_saying}"'
		embed.set_image(url=photo)
		embed.set_thumbnail(url=icon)
		embed.add_field(name="Species", value=parsed_species, inline=True)
		embed.add_field(name="Gender", value=parsed_gender, inline=True)
		embed.add_field(name="Personality", value=parsed_personality, inline=True)
		embed.add_field(name="Birthday", value=birthday, inline=True)
		embed.add_field(name="Hobby", value=hobby, inline=True)
		embed.add_field(name="Favorite song", value=f"[{favorite_song}]({url})", inline=True)
		embed.set_footer(text=catchphrase)

		return embed


	class VillagersView(discord.ui.View):
		def __init__(self, viewUserID:int, villagers:list[str], timeout:int=180):
			super().__init__(timeout=timeout)

			self.embeds: dict[str, discord.Embed] = {}
			for villager_name in villagers:
				embed = AnimalCrossing.build_embed_from_name(villager_name)
				if not embed.title :
					embed.title = "???"
				self.embeds[villager_name] = embed
			
			self.names = list(self.embeds.keys())
			self.current = self.names[0]

			self.viewUserID = viewUserID
			self.message: Optional[discord.Message] = None

			# create one button per villager and attach a callback
			for name in self.names:
				# disable current button, enable all others
				btn = discord.ui.Button(label=name, style=discord.ButtonStyle.blurple, custom_id=name, disabled=(name == self.current))
				async def _callback(inter: discord.Interaction, button: discord.ui.Button = btn, name: str = name):
					self.current = name

					for child in self.children:
						if isinstance(child, discord.ui.Button):
							child.disabled = (child.custom_id == name)
					await inter.response.edit_message(embed=self.embeds[self.current], view=self)
				btn.callback = _callback #type:ignore
				self.add_item(btn)

		async def interaction_check(self, inter: discord.Interaction):
			if inter.user.id != self.viewUserID:
				await inter.response.send_message("❌ This is not your command ❌", ephemeral=True)
				return False
			return True

		async def on_timeout(self):
			for item in self.children:
				if isinstance(item, discord.ui.Button):
					item.disabled = True
				
			# remove the close button
			# self.remove_item(self.children[-1])

			if self.message:
				await self.message.edit(view=self)
			self.stop()


async def setup(bot:commands.Bot):
	await bot.add_cog(AnimalCrossing(bot))