import discord
from discord.ext import commands

from utils import is_cutie, GetLogLink

class Help(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot = bot


	@commands.group()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def help(self, ctx:commands.Context) -> None:
		if ctx.invoked_subcommand is None:
			E = discord.Embed(title="Help")
			E.description = "To display the help page of a command, type `!help <command>`"

			if is_cutie(ctx):
				E.add_field(name="**Cuties**", value=
				"""```/rename \
					!avatar   \
					/status   \
					/activity \
					/resp     \
				```"""
				)

			E.add_field(name="**Tetrio**", value=
			"""```/register  \
				/profile     \
				/leaderboard \
			```"""
			)

			E.add_field(name="**Infos**", value=
			"""```!help \
				!file   \
				!link   \
				!emoji  \
			```"""
			)
			
			E.add_field(name="**Birthdays**", value=
			"""```/set birthday ~ set \
				/birthdays ~ bdays    \
			```"""
			)

			E.add_field(name="**Fun**", value=
			"""```!embed    \
				!confession \
			```"""
			)

			await ctx.reply(embed=E)

	# cutie section
	@help.command(aliases=["/rename"])
	@commands.check(is_cutie)
	async def rename(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/rename")
		E.description = "**Changes the name of the bot**"
		E.add_field(name="**Example**", value="```/rename <name>```")
		E.add_field(name="**Cooldown**", value="```1h / guild```")
		E.add_field(name="**Requirement**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!avatar"])
	@commands.check(is_cutie)
	async def avatar(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="!avatar")
		E.description = "**Changes the avatar of the bot**\nlink = link to an image\nattachment = image file"
		E.add_field(name="**Example**", value="```!avatar <link> \n!avatar <attachment>```")
		E.add_field(name="**Cooldown**", value="```1h / guild```")
		E.add_field(name="**Requirement**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/status"])
	@commands.check(is_cutie)
	async def status(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/status")
		E.description = "**Changes the status of the bot**\nstatus = online/idle/dnd/invisible"
		E.add_field(name="**Example**", value="```/status <status>```")
		E.add_field(name="**Cooldown**", value="```60s / guild```")
		E.add_field(name="**Requirement**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/activity"])
	@commands.check(is_cutie)
	async def activity(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/activity")
		E.description = "**Changes the activity of the bot**\nact = playing/listening/watching/stop"
		E.add_field(name="**Example**", value="```/activity <act> <txt>```")
		E.add_field(name="**Cooldown**", value="```60s / guild```")
		E.add_field(name="**Requirement**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/resp"])
	@commands.check(is_cutie)
	async def resp(self, ctx:commands.Context) -> None:
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

			async def interaction_check(self, inter: discord.Interaction):
				return inter.user.id == ctx.author.id

			@discord.ui.button(label="/resp add",style=discord.ButtonStyle.success)
			async def add(self, inter: discord.Interaction, _: discord.ui.Button):
				await inter.response.edit_message(embed=E_add)

			@discord.ui.button(label="/resp list",style=discord.ButtonStyle.primary)
			async def list(self, inter: discord.Interaction, _: discord.ui.Button):
				await inter.response.edit_message(embed=E_list)

			@discord.ui.button(label="/resp del",style=discord.ButtonStyle.danger)
			async def delete(self, inter: discord.Interaction, _: discord.ui.Button):
				await inter.response.edit_message(embed=E_del)

			async def on_timeout(self):
				for item in self.children:
					item.disabled = True

				await self.message.edit(view=self)

		B_resp.message = await ctx.reply(view=B_resp())


	# Tetrio section
	@help.command(aliases=["/register"])
	async def register(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/register")
		E.description = "**Registers a Tetrio account to your discord**\nusername = Tetrio username"
		E.add_field(name="**Example**", value="```/register <username>```")
		E.add_field(name="**Cooldown**", value="```once / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/profile"])
	async def profile(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/profile")
		E.description = "**Displays the Tetrio profile of a user**\n(username) = Tetrio username (optionnal) -> If none, displays your profile"
		E.add_field(name="**Example**", value="```/profile (username)```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/leaderboard"])
	async def leaderboard(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/leaderboard")
		E.description = "**Displays the Tetrio leaderboard**"
		E.add_field(name="**Example**", value="```/leaderboard```")
		E.add_field(name="**Cooldown**", value="```60s / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	# Birthday section
	@help.command(aliases=["/set", "set"])
	async def set_birthday(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/set")
		E.description = "**Registers your birthday**\nyear = year of birth\nmonth = month of birth\nday = day of birth"
		E.add_field(name="**Example**", value="```/set <year> <month> <day>```")
		E.add_field(name="**Cooldown**", value="```once / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/birthdays", "bdays", "/bdays"])
	async def birthdays(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/birthdays")
		E.description = "**Displays the birthdays list**\n(user) = user (optionnal) -> if specified, displays the birthday of the user"
		E.add_field(name="**Example**", value="```/birthdays (user)```")
		E.add_field(name="**Cooldown**", value="```10s / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	# General section
	@help.command(aliases=["!file"])
	async def file(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/file")
		E.description = "**Converts your link to a file**\nlink = link of file\n"
		E.description += "**WARNING :** The link must be direct.\n"
		E.description += "**WARNONG :** Only discord formats are supported:\n"
		E.description += "IMAGE : png, jpg, jpeg, webp, gif\n"
		E.description += "AUDIO : mp3, ogg, wav, flac\n"
		E.description += "VIDEO : mp4, webm, mov"
		E.add_field(name="**Example**", value="```!file <link>```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!link"])
	async def link(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/link")
		E.description = "**Converts your link to a file**\nattachment = file"
		E.add_field(name="**Example**", value="```!link <attachment>```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!emoji"])
	async def emoji(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/emoji")
		E.description = "**Displays all information about an emoji**\nemoji = emoji (name or anything)"
		E.add_field(name="**Example**", value="```!emoji <emoji>```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requirement**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!confession"])
	async def confession(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/confession")
		E.description = "**Send an anonymous confession**\nmessage = message to confess"
		E.add_field(name="**Example**", value="```!confession <message>```")
		E.add_field(name="**Cooldown**", value="```60s / user```")
		E.add_field(name="**Requirement**", value="```DM```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!embed"])
	async def embed(self, ctx:commands.Context) -> None:
		E = discord.Embed(colour=discord.Colour.random())
		E.set_author(name=ctx.author,icon_url=await GetLogLink(self.bot, ctx.author.avatar))
		E.title = "Page d'aide de la commande `embed`"
		E.description = """Vous trouverez ci-dessous une liste de toutes les options que vous pouvez appliquer à votre embed pour le personnaliser autant que possible en le commancant via `m!embed new`
			Vous aurez **un delay de 10m** à chaque fois avant que l'embed s'anulle.
			Certaines commandes ont également des sous commandes, comme pour field et émoji afin de supprimer ce que vous ne désirez plus, pour les autres, utilisez `///` pour vider le contenu.
			Vous pouvez voir à quoi ressemble un embed entièrement remplis via `m!embed view`"""
		E.description += "\n\n**cooldown** : `60`s\n**alias** : 'e', 'embed'"
		E.add_field(name="**Forme globale**",value="```md\n[titre](texte, url possible)\n[url](url du titre)\n[description](url possible via [nom](url) )\n[image](png, jpg, jpeg, webp, gif)\n[thumbnail](png, jpg, jpeg, webp, gif)\n[color](code couleur en hex/'random')```",inline=False)
		E.add_field(name="**Author**",value="```md\n[author](texte, url possible)\n[author_url](lien de l'author)\n[author_icon](png, jpg, jpeg, webp, gif)```",inline=False)
		E.add_field(name="**Footer**",value="```md\n[footer](texte simple)\n[footer_icon](png, jpg, jpeg, webp, gif)```",inline=False)
		E.add_field(name="**Fields**",value="```md\n[field](texte,,suite)\n[field del](valeur du field à delete)```",inline=False)
		E.add_field(name="**Autres**",value="```md\n[timestamp](on/off)\n[text](ajouter du texte hors embed)\n[file](ajoutr un fichier)\n[émoji](ajoute des émojis à l'embed)\n[émoji del](émoji à supprimer)\n[embed](ID de l'embed pour y retourner)\n[ctrl z](annuler une action)```",inline=False)
		E.add_field(name="**Pour finir**",value="```md\n[done](finir l'embed)\n[stop](anulle l'embed)```")
		await ctx.send(embed=E)



async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(Help(bot))
