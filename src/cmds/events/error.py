import discord
from discord import app_commands
from discord.ext import commands

import traceback
import datetime as dt

from src.utils import log
from cmds.src.settings import ERROR_CHANNEL_ID

class Error(commands.Cog):
	def __init__(self, bot):
		self.bot : commands.Bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx:commands.Context, error:commands.CommandError):

		if isinstance(error, commands.CommandNotFound) :
			return

		elif isinstance(error, commands.NoPrivateMessage):
			await ctx.send("Cette commande n'est pas utilisable en messages privés",delete_after=5)

		elif isinstance(error, commands.MaxConcurrencyReached):
			if str(error.per) == "BucketType.guild" : 
				await ctx.send("Cette commande est déjà utilisée sur le serveur",delete_after=5)
			elif str(error.per) == "BucketType.user" : 
				await ctx.send("Vous êtes déjà entrain d'utiliser cette commande",delete_after=5)
			elif str(error.per) == "BucketType.channel" : 
				await ctx.send("Cette commande est déjà en cours d'utilisation dans ce salon",delete_after=5)
			else :
				await ctx.send(error)

		elif isinstance(error, commands.CommandOnCooldown):
			await ctx.send(f"Vous ne pouvez pas encore utiliser cette commande, attendez : **{round(error.retry_after,1)}** secondes",delete_after=error.retry_after)

		elif isinstance(error, commands.MissingPermissions):
			L = error.missing_perms
			if len(L) == 1 : 
				await ctx.send(f"Vous ne pouvez pas executer cette commande, vous avez besoin de la permission : **{L[0]} **!",delete_after=5)
			elif len(L) > 1 :
				await ctx.send(f"Vous ne pouvez pas executer cette commande, vous avez besoin des permissions : **{', '.join(L)}** ! ",delete_after=5)

		elif isinstance(error, commands.CheckFailure):
			await ctx.send(f"**{ctx.author},** Vous n'êtes pas autorisé à utiliser la commande **{ctx.command}**",delete_after=5)

		else :
			await ctx.send(error)

			error_chan = await self.bot.fetch_channel(ERROR_CHANNEL_ID)

			E = discord.Embed(title=str(error),colour=0xFF0000,timestamp=dt.datetime.now())
			E.url = ctx.message.jump_url
			E.description = "\n".join(traceback.format_exception(type(error),error,error.__traceback__))

			log("ERROR", f"{error} \n {E.url} \n {E.description}")

			await error_chan.send(embed=E)


	def cog_load(self):
		tree = self.bot.tree
		self._old_tree_error = tree.on_error
		tree.on_error = self.on_app_command_error

	def cog_unload(self):
		tree = self.bot.tree
		tree.on_error = self._old_tree_error


	async def on_app_command_error(self,inter: discord.Interaction,error: app_commands.AppCommandError):
		if isinstance(error, app_commands.errors.CommandNotFound) :
			await inter.response.send_message("Cette commande n'existe pas",ephemeral=True)
	
		elif isinstance(error, app_commands.errors.CommandOnCooldown):
			await inter.response.send_message(f"Vous ne pouvez pas encore utiliser cette commande, attendez : **{round(error.retry_after,1)}** secondes",ephemeral=True)

		elif isinstance(error, app_commands.errors.MissingPermissions):
			L = error.missing_perms
			if len(L) == 1 : 
				await inter.response.send_message(f"Vous ne pouvez pas executer cette commande, vous avez besoin de la permission : **{L[0]} **!",ephemeral=True)
			elif len(L) > 1 :
				await inter.response.send_message(f"Vous ne pouvez pas executer cette commande, vous avez besoin des permissions : **{', '.join(L)}** ! ",ephemeral=True)

		elif isinstance(error, app_commands.errors.CheckFailure):
			await inter.response.send_message("Vous n'êtes pas autorisé à utiliser cette commande",ephemeral=True)

		else :
			try:
				await inter.response.send_message(error)
			except:
				await inter.followup.send(error)

			error_chan = await self.bot.fetch_channel(ERROR_CHANNEL_ID)

			E = discord.Embed(title=str(error),colour=0xFF0000,timestamp=dt.datetime.now())
			E.description = "\n".join(traceback.format_exception(type(error),error,error.__traceback__))

			log("ERROR", f"{error} \n {E.description}")

			await error_chan.send(embed=E)



async def setup(bot:commands.Bot):
	await bot.add_cog(Error(bot))