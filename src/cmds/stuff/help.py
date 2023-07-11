import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional, Callable

from settings import GUILD_ID
from utils import is_member, is_cutie, is_owner, GetLogLink

class MissingCommand(Exception):pass

bot_commands = {
	"Owner"      : [is_owner, "/sync", "/reload", "/enable", "/disable", "/debug"],
	"Cuties"     : [is_cutie, "/say", "/resp", "/rename", "/avatar", "/status", "/activity"],
	"Tetrio"     : [is_member, "/register", "/profile", "/leaderboard"],
	"Infos"      : [is_member, "/help", "/file_to_link", "/link_to_file", "/emoji"],
	"Birthdays"  : [is_member, "/set_birthday", "/birthdays"],
	"Member Fun" : [is_member, "/confession", "/apoll"],
	"Fun"        : [None, "/poll"],
	"Games"      : [None],
}

class Help(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot : commands.Bot = bot

	@app_commands.command(description="Anon bot's help page")
	@app_commands.describe(query="The command or category you want to get help on")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(query="The command or category you want to get help on")
	async def help(self, inter:discord.Interaction, query:Optional[str]):
		async def get_app_commands(names:list[str]) -> list[app_commands.AppCommand]:
			guild = await self.bot.fetch_guild(GUILD_ID)
			guild_commands = await self.bot.tree.fetch_commands(guild=guild)
			found_commands = []

			for name in names:
				for command in guild_commands:
					if command.name == name.lower():
						found_commands.append(command)
						break

			return found_commands

		await inter.response.defer()
		E = discord.Embed()
		E.colour = discord.Colour.blurple()
		E.description = ""

		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))

		# generates the general help page
		def general_page() -> None:
			E.title = "/help"
			E.description = "To display the help page of a command or category, type `/help query:<query>`"

			for key in bot_commands.keys():
				perms = bot_commands[key][0]
				if (isinstance(perms, Callable) and perms(inter)) or (perms is None):
					txt = "\n".join(bot_commands[key][1:]) 
					E.add_field(name=f"**{key}**", value=f"```{txt}```")

		all_commands = []
		for value in bot_commands.values():
			for val in value:
				if isinstance(val, str):
					all_commands.append(val)

		if query is None:
			general_page()
		# if the query is one of the categories
		elif query in bot_commands.keys():
			perms : Optional[Callable] = bot_commands[query][0]
			remove_first_char = lambda s: s[1:]
			commands_names = list(map(remove_first_char, bot_commands[query][1:]))
			commands = await get_app_commands(commands_names)

			if (isinstance(perms, Callable) and perms(inter)) or (perms is None):
				E.title = f"**{query} commands**"

				for command in commands:
					E.description += f"{command.mention} - {command.description}\n"
			else:
				general_page()
		# if the query is one of the commands
		elif query in all_commands:
			#check permissions
			perms : Optional[Callable] = None
			for value in bot_commands.values():
				if query in value:
					perms = value[0]
					break
			
			# if the user has the perms or the command doesn't need perms
			if (isinstance(perms, Callable) and perms(inter)) or (perms is None):
				E.title = (await get_app_commands([query[1:]]))[0].mention

				# owner commands
				if query == "/sync":
					E.description = "Syncs the bot's commands with the guild"
				elif query == "/reload":
					E.description = "Reloads the bot's extensions"
				elif query == "/enable":
					E.description = "Enables a command"
				elif query == "/disable":
					E.description = "Disables a command"
				elif query == "/debug":
					E.description = "Displays the debug page"
				# cutie commands
				elif query == "/say":
					E.description = "**Sends a message as the bot**\nmessage = message to send\nfile = file to send"
					E.add_field(name="**Example**", value="```/say <message> (file)```")
					E.add_field(name="**Cooldown**", value="```1s / user```")
					E.add_field(name="**Requirement**", value="```CUTIE```")
				elif query == "/rename":
					E.description = "**Changes the name of the bot**"
					E.add_field(name="**Example**", value="```/rename <name>```")
					E.add_field(name="**Cooldown**", value="```1h / guild```")
					E.add_field(name="**Requirement**", value="```CUTIE```")
				elif query == "/avatar":
					E.description = "**Changes the avatar of the bot**\nlink = link to an image\nattachment = image file"
					E.add_field(name="**Example**", value="```/avatar link:<link> \n/avatar file:<attachment>```")
					E.add_field(name="**Cooldown**", value="```1h / guild```")
					E.add_field(name="**Requirement**", value="```CUTIE```")
				elif query == "/status":
					E.description = "**Changes the status of the bot**\nstatus = online/idle/dnd/invisible"
					E.add_field(name="**Example**", value="```/status <status>```")
					E.add_field(name="**Cooldown**", value="```60s / guild```")
					E.add_field(name="**Requirement**", value="```CUTIE```")
				elif query == "/activity":
					E.description = "**Changes the activity of the bot**"
					E.add_field(name="**Example**", value="```/activity <typ> <txt>```")
					E.add_field(name="**Cooldown**", value="```60s / guild```")
					E.add_field(name="**Requirement**", value="```CUTIE```")
				elif query == "/resp":
					E_add = discord.Embed(title="/resp add")
					E_add.description = "**Adds an automatic response**\nkey = trigger keyword\nresp = response\n(time) = time before deletion (optionnal)"
					E_add.add_field(name="**Example**", value="```/resp <key> <resp> (time)```")
					E_add.add_field(name="**Cooldown**", value="```5s / user```")
					E_add.add_field(name="**Requirement**", value="```CUTIE```")

					E_del = discord.Embed(title="/resp del")
					E_del.description = "**Deletes an automatic response**\nid = id of the response"
					E_del.add_field(name="**Example**", value="```/resp del <id>```")
					E_del.add_field(name="**Cooldown**", value="```5s / user```")
					E_del.add_field(name="**Requirement**", value="```CUTIE```")

					E_list = discord.Embed(title="/resp list")
					E_list.description = "**Displays the list of automatic responses**\n(page) = page of the list (optionnal)"
					E_list.add_field(name="**Example**", value="```/resp list (page)```")
					E_list.add_field(name="**Cooldown**", value="```5s / user```")
					E_list.add_field(name="**Requirement**", value="```CUTIE```")

					class B_resp(discord.ui.View):
						def __init__(self, timeout=15):
							super().__init__(timeout=timeout)
							self.message : Optional[discord.Message]

						async def interaction_check(self, inter2: discord.Interaction):
							return inter2.user.id == inter.user.id

						@discord.ui.button(label="/resp add",style=discord.ButtonStyle.success)
						async def add(self, inter2: discord.Interaction, _: discord.ui.Button):
							await inter2.response.edit_message(embed=E_add)

						@discord.ui.button(label="/resp list",style=discord.ButtonStyle.primary)
						async def list(self, inter2: discord.Interaction, _: discord.ui.Button):
							await inter2.response.edit_message(embed=E_list)

						@discord.ui.button(label="/resp del",style=discord.ButtonStyle.danger)
						async def delete(self, inter2: discord.Interaction, _: discord.ui.Button):
							await inter2.response.edit_message(embed=E_del)

						async def on_timeout(self):
							for item in self.children:
								if isinstance(item, discord.ui.Button):
									item.disabled = True

							if isinstance(self.message, discord.Message):
								await self.message.edit(view=self)

					b_resp = B_resp()
					b_resp.message = await inter.followup.send(embed=E_add, view=b_resp)
					return
				# tetrio commands
				elif query == "/register":
					E.description = "**Registers a Tetrio account to your discord**\nusername = Tetrio username"
					E.add_field(name="**Example**", value="```/register <username>```")
					E.add_field(name="**Cooldown**", value="```once / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				elif query == "/profile":
					E.description = "**Displays the Tetrio profile of a user**\n(username) = Tetrio username (optionnal) -> If none, displays your profile"
					E.add_field(name="**Example**", value="```/profile (username)```")
					E.add_field(name="**Cooldown**", value="```5s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				elif query == "/leaderboard":
					E.description = "**Displays the Tetrio leaderboard**"
					E.add_field(name="**Example**", value="```/leaderboard```")
					E.add_field(name="**Cooldown**", value="```60s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				# infos commands
				elif query == "/file_to_link":
					E.description = "**Converts your link to a file**\n"
					E.add_field(name="**Example**", value="```/link_to_file <file>```")
					E.add_field(name="**Cooldown**", value="```5s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				elif query == "/link_to_file":
					E.description = "**Converts your link to a file**\n"
					E.description += "**WARNING :** The link must be direct.\n"
					E.description += "**WARNONG :** Only discord formats are supported:\n"
					E.description += "IMAGE : png, jpg, jpeg, webp, gif\n"
					E.description += "AUDIO : mp3, ogg, wav, flac\n"
					E.description += "VIDEO : mp4, webm, mov"
					E.add_field(name="**Example**", value="```/file_to_link <link>```")
					E.add_field(name="**Cooldown**", value="```5s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				elif query == "/emoji":
					E.description = "**Displays all information about an emoji**\nemoji name or anything"
					E.add_field(name="**Example**", value="```/emoji <emoji>```")
					E.add_field(name="**Cooldown**", value="```5s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				# birthday commands
				elif query == "/set_birthday":
					E.description = "**Registers your birthday**\nyear = year of birth\nmonth = month of birth\nday = day of birth"
					E.add_field(name="**Example**", value="```/set <year> <month> <day>```")
					E.add_field(name="**Cooldown**", value="```once / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				elif query == "/birthdays":
					E.description = "**Displays the birthdays list**\n(user) = user (optionnal) -> if specified, displays the birthday of the user"
					E.add_field(name="**Example**", value="```/birthdays (user)```")
					E.add_field(name="**Cooldown**", value="```10s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				# member fun commands
				elif query == "/confession":
					E.description = "**Send an anonymous confession**\nmessage = message to confess"
					E.add_field(name="**Example**", value="```/confession <message>```")
					E.add_field(name="**Cooldown**", value="```60s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				elif query == "/apoll":
					E.description = "**Sends an anonymous poll**\nquestion = question to ask\ntime = time before the poll ends"
					E.add_field(name="**Example**", value="```/poll <question> <time>```")
					E.add_field(name="**Cooldown**", value="```60s / user```")
					E.add_field(name="**Requirement**", value="```MEMBER```")
				# fun commands
				elif query == "/poll":
					E.description = "**Sends a polll**\nquestion = question to ask"
					E.add_field(name="**Example**", value="```/poll <question>```")
					E.add_field(name="**Cooldown**", value="```60s / user```")
					E.add_field(name="**Requirement**", value="```None```")
				# game commands

				else:
					raise MissingCommand(f"Help page for command {query} not found")
			# if the user doesn't have the perms
			else:
				general_page()
		# if the query is not valid
		else:
			general_page()

		await inter.followup.send(embed=E)

	@help.autocomplete("query")
	async def user_autocomplete(self, inter: discord.Interaction, current:str) -> list[app_commands.Choice[str]]:
		choices = []

		# add all the commands the user can use 
		for key in bot_commands.keys():
			perms = bot_commands[key][0]
			if (isinstance(perms, Callable) and perms(inter)) or (perms is None):
				choices.extend([key, *bot_commands[key][1:]])

		# lower everything
		choices = list(map(str.lower, choices))
		current = current.lower()

		# only keep the lookalikes
		new_choices = []
		for choice in choices:
			if current == "" or (current != "" and current in choice):
				if choice.startswith('/'):
					new_choices.append(choice)
				else : 
					new_choices.append(choice.title())

		# only keep the first 25 and convert them to choices
		final_choices = []
		for choice in new_choices[:25]:
			final_choices.append(app_commands.Choice(name=choice, value=choice))


		return final_choices

async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(Help(bot))