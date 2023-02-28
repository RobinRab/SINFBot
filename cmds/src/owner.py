import discord
from discord import app_commands
from discord.ext import commands

import os
from utils import log
import settings

class Owner(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot : commands.Bot = bot

	@commands.command()
	@commands.is_owner()
	async def sync(self, ctx:commands.Context):
		if self.bot.tree.synced:
			await ctx.send("Bot already synced")
			return
		try : 
			self.bot.tree.clear_commands(guild=discord.Object(id=settings.GUILD_ID))
			self.bot.tree.copy_global_to(guild=discord.Object(id=settings.GUILD_ID))
			
			await self.bot.tree.sync(guild=discord.Object(id=settings.GUILD_ID))
			self.bot.tree.synced = True

			await ctx.send("Bot synced")
			log("INFO", "Bot synced")
		except:
			await ctx.send("Sync failed")
			log("ERROR", "Sync failed")

	@commands.command()
	@commands.is_owner()
	async def reload(self, _:commands.Context):
		for ext in settings.extensions:
			try: 
				await self.bot.load_extension(ext)
			except:
				await self.bot.reload_extension(ext)
			log("INFO", f"{ext} reloaded")


	@app_commands.command(description="Enables a file or folder")
	@commands.is_owner()
	async def enable(self, inter:discord.Interaction, directory:str, file:str=None):
		txt = ""
		try:
			# enable all files in a folder
			if file is None :
				for file in os.listdir("cmds/"+directory):
					if file.endswith(".py"):

						try:
							await self.bot.load_extension("cmds."+directory+"."+file[:-3])
						except:
							await self.bot.reload_extension("cmds."+directory+"."+file[:-3])

						log("INFO", f"cmds.{directory}.{file[:-3]} loaded")
						txt += f"cmds/{directory}/{file[:-3]} loaded\n"
			elif file is not None:

				try:
					await self.bot.load_extension(file)
				except:
					await self.bot.reload_extension(file)

				log("INFO", f"{file} loaded")
				txt += f"{file} loaded"
			else:
				await inter.response.send_message("You must specify a file")
				return
		except FileNotFoundError:
			await inter.response.send_message("File not found")
			return
		
		await inter.response.send_message(txt)


	@app_commands.command(description="Disables a file or folder")
	@commands.is_owner()
	async def disable(self, inter:discord.Interaction, directory:str, file:str=None):
		txt = ""
		try:
			# enable all files in a folder
			if file is None :
				for file in os.listdir("cmds/"+directory):
					if file.endswith(".py"):
				
						try:
							await self.bot.unload_extension("cmds."+directory+"."+file[:-3])
						except:
							pass

						log("INFO", f"cmds.{directory}.{file[:-3]} unloaded")
						txt += f"cmds/{directory}/{file[:-3]} unloaded\n"
			elif file is not None:

				try:
					await self.bot.unload_extension(file)
				except:
					pass

				log("INFO", f"{file} unloaded")
				txt += f"{file} unloaded"
			else:
				await inter.response.send_message("You must specify a file")
				return
		except FileNotFoundError:
			await inter.response.send_message("File not found")
			return
		
		await inter.response.send_message(txt)


	@enable.autocomplete("directory")
	@disable.autocomplete("directory")
	async def dir_autocomplete(inter: discord.Interaction, _:str, __:str):
		return [app_commands.Choice(name=dir, value=dir) for dir in settings.directories]
	
	@enable.autocomplete("file")
	@disable.autocomplete("file")
	async def ext_autocomplete(inter: discord.Interaction, _:str, __:str):
		return [app_commands.Choice(name=dir, value=dir) for dir in settings.extensions]



async def setup(bot:commands.Bot):
	await bot.add_cog(Owner(bot))

