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
			E.description = "Pour afficher une page d'aide, vous devez préciser le nom d'une commande"

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
		E.description = "**Change le nom du bot**"
		E.add_field(name="**Example**", value="```/rename <name>```")
		E.add_field(name="**Cooldown**", value="```1h / guild```")
		E.add_field(name="**Requis**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!avatar"])
	@commands.check(is_cutie)
	async def avatar(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="!avatar")
		E.description = "**Change l'avatar du bot**\nlink = lien vers une image\nattachment = fichier image"
		E.add_field(name="**Example**", value="```!avatar <link> \n!avatar <attachment>```")
		E.add_field(name="**Cooldown**", value="```1h / guild```")
		E.add_field(name="**Requis**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/status"])
	@commands.check(is_cutie)
	async def status(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/status")
		E.description = "**Change le status du bot**\nstatus = online/idle/dnd/invisible"
		E.add_field(name="**Example**", value="```/status <status>```")
		E.add_field(name="**Cooldown**", value="```60s / guild```")
		E.add_field(name="**Requis**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/activity"])
	@commands.check(is_cutie)
	async def activity(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/activity")
		E.description = "**Change l'activitée du bot**\nact = playing/listening/watching/stop"
		E.add_field(name="**Example**", value="```/activity <act> <txt>```")
		E.add_field(name="**Cooldown**", value="```60s / guild```")
		E.add_field(name="**Requis**", value="```CUTIE```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/resp"])
	@commands.check(is_cutie)
	async def resp(self, ctx:commands.Context) -> None:
		E_add = discord.Embed(title="/resp add")
		E_add.description = "**Ajoute une réponse automatique**\nkey = mot clé\nresp = réponse\n(time) = temps avant suppression (optionnel)"
		E_add.add_field(name="**Example**", value="```/resp <key> <resp> (time)```")
		E_add.add_field(name="**Cooldown**", value="```5s / user```")
		E_add.add_field(name="**Requis**", value="```CUTIE```")

		E_del = discord.Embed(title="/resp del")
		E_del.description = "**Supprime une réponse automatique**\nid = id de la réponse"
		E_del.add_field(name="**Example**", value="```/resp del <id>```")
		E_del.add_field(name="**Cooldown**", value="```5s / user```")
		E_del.add_field(name="**Requis**", value="```CUTIE```")

		E_list = discord.Embed(title="/resp list")
		E_list.description = "**Affiche la liste des réponses automatiques**\n(page) = page de la liste (optionnel)"
		E_list.add_field(name="**Example**", value="```/resp list (page)```")
		E_list.add_field(name="**Cooldown**", value="```5s / user```")
		E_list.add_field(name="**Requis**", value="```CUTIE```")

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
		E.description = "**Enregistre un compte Tetrio**\nusername = nom d'utilisateur Tetrio"
		E.add_field(name="**Example**", value="```/register <username>```")
		E.add_field(name="**Cooldown**", value="```once / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/profile"])
	async def profile(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/profile")
		E.description = "**Affiche le profil d'un utilisateur Tetrio**\n(username) = nom d'utilisateur Tetrio (optionnel) -> si non spécifié, affiche le profil personnel"
		E.add_field(name="**Example**", value="```/profile (username)```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/leaderboard"])
	async def leaderboard(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/leaderboard")
		E.description = "**Affiche le classement Tetrio**"
		E.add_field(name="**Example**", value="```/leaderboard```")
		E.add_field(name="**Cooldown**", value="```60s / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	# Birthday section
	@help.command(aliases=["/set", "set"])
	async def set_birthday(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/set")
		E.description = "**Enregistre votre date de naissance**\nyear = année\nmonth = mois\nday = jour"
		E.add_field(name="**Example**", value="```/set <year> <month> <day>```")
		E.add_field(name="**Cooldown**", value="```once / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["/birthdays", "bdays", "/bdays"])
	async def birthdays(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/birthdays")
		E.description = "**Affiche la liste des anniversaires**\n(user) = utilisateur (optionnel) -> si spécifié, affiche l'anniversaire de la personne"
		E.add_field(name="**Example**", value="```/birthdays (user)```")
		E.add_field(name="**Cooldown**", value="```10s / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	# General section
	@help.command(aliases=["!file"])
	async def file(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/file")
		E.description = "**transforme votre lien en fichier**\nlink = lien du fichier\n"
		E.description += "**Attention :** le lien doit être un lien direct vers le fichier.\n"
		E.description += "**Attention :** seuls les formats discord sont supportés:\n"
		E.description += "IMAGE : png, jpg, jpeg, webp, gif\n"
		E.description += "AUDIO : mp3, ogg, wav, flac\n"
		E.description += "VIDEO : mp4, webm, mov"
		E.add_field(name="**Example**", value="```!file <link>```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!link"])
	async def link(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/link")
		E.description = "**transforme votre fichier en lien**\nattachment = fichier"
		E.add_field(name="**Example**", value="```!link <attachment>```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!emoji"])
	async def emoji(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/emoji")
		E.description = "**Affiche les infos d'un emoji**\nemoji = emoji (nom accepté)"
		E.add_field(name="**Example**", value="```!emoji <emoji>```")
		E.add_field(name="**Cooldown**", value="```5s / user```")
		E.add_field(name="**Requis**", value="```None```")

		await ctx.reply(embed=E)


	@help.command(aliases=["!confession"])
	async def confession(self, ctx:commands.Context) -> None:
		E = discord.Embed(title="/confession")
		E.description = "**Envoie une confession**\nmessage = message de la confession"
		E.add_field(name="**Example**", value="```!confession <message>```")
		E.add_field(name="**Cooldown**", value="```60s / user```")
		E.add_field(name="**Requis**", value="```DM```")

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
