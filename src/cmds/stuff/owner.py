import discord
from discord import app_commands
from discord.ext import commands

import os
import settings
from utils import log, SelectView, is_owner

class Owner(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot : commands.Bot = bot

	@app_commands.command(description="Synchronise le bot")
	@app_commands.check(is_owner)
	async def sync(self, inter:discord.Interaction):
		if self.bot.description == "Synced":
			await inter.response.send_message("Bot already synced")
			return
		try : 
			self.bot.tree.clear_commands(guild=discord.Object(id=settings.GUILD_ID))
			self.bot.tree.copy_global_to(guild=discord.Object(id=settings.GUILD_ID))
			
			await self.bot.tree.sync(guild=discord.Object(id=settings.GUILD_ID))
			self.bot.description = "Synced"

			await inter.response.send_message("Bot synced")
			log("INFO", "Bot synced")
		except:
			await inter.response.send_message("Sync failed")
			log("ERROR", "Sync failed")

	@app_commands.command(description="Reload all extensions")
	@app_commands.check(is_owner)
	async def reload(self, inter:discord.Interaction):
		for ext in settings.extensions:
			try: 
				await self.bot.load_extension(ext)
			except:
				await self.bot.reload_extension(ext)
			log("INFO", f"{ext} reloaded")
		await inter.response.send_message("Bot reloaded")


	@app_commands.command(description="Enables a file or folder")
	@app_commands.check(is_owner)
	async def enable(self, inter:discord.Interaction):
		folders =  [(file,file) for file in os.listdir("src/cmds/") if file[0] not in [".", "_"]]

		view, folder = await SelectView.get_app_choice(inter, folders, previous=None)

		if folder is None:
			return await inter.followup.send("You must select a folder", ephemeral=True)
		

		files = [(file, file) for file in os.listdir("src/cmds/"+folder) if file.endswith(".py")]
		files.insert(0, ("All", "All"))
		txt = ""

		_ , file = await SelectView.get_app_choice(inter, files, previous=view)

		if file is None or file == "All":
			for file in os.listdir("src/cmds/"+folder):
				if file.endswith(".py"):
					try:
						await self.bot.load_extension("cmds."+folder+"."+file[:-3])
						txt += f"\ncmds/{folder}/{file[:-3]} loaded"
						log("INFO", f"\ncmds/{folder}/{file[:-3]} loaded")
					except:
						await self.bot.reload_extension("cmds."+folder+"."+file[:-3])
						txt += f"\ncmds/{folder}/{file[:-3]} reloaded"
						log("INFO", f"\ncmds/{folder}/{file[:-3]} reloaded")

		else:
			try:
				await self.bot.load_extension("cmds."+folder+"."+file[:-3])
				txt += f"\ncmds/{folder}/{file[:-3]} loaded"
				log("INFO", f"\ncmds/{folder}/{file[:-3]} loaded")
			except:
				await self.bot.reload_extension("cmds."+folder+"."+file[:-3])
				txt += f"\ncmds/{folder}/{file[:-3]} reloaded"
				log("INFO", f"\ncmds/{folder}/{file[:-3]} reloaded")

		await inter.followup.send(txt)


	@app_commands.command(description="Disables a file or folder")
	@app_commands.check(is_owner)
	async def disable(self, inter:discord.Interaction):
		folders =  [(file,file) for file in os.listdir("src/cmds/") if file[0] not in [".", "_"]]

		view, folder = await SelectView.get_app_choice(inter, folders, previous=None)

		if folder is None:
			return await inter.followup.send("Your must select a folder", ephemeral=True)
		

		files = [(file, file) for file in os.listdir("src/cmds/"+folder) if file.endswith(".py")]
		files.insert(0, ('All', 'All'))
		txt = ""

		_ , file = await SelectView.get_app_choice(inter, files, previous=view)

		if file is None or file == "All":
			for file in os.listdir("src/cmds/"+folder):
				if file.endswith(".py"):
					await self.bot.unload_extension("cmds."+folder+"."+file[:-3])
					txt += f"\ncmds/{folder}/{file[:-3]} unloaded"
					log("INFO", f"\ncmds/{folder}/{file[:-3]} unloaded")

		else:
			await self.bot.unload_extension("cmds."+folder+"."+file[:-3])
			txt += f"\ncmds/{folder}/{file[:-3]} unloaded"
			log("INFO", f"\ncmds/{folder}/{file[:-3]} unloaded")

		log("INFO", txt)
		await inter.followup.send(txt)


	@app_commands.command(description="Debugs the state of the bot")
	@app_commands.check(is_owner)
	async def debug(self, inter:discord.Interaction):
		txt = "```\n"
		for ext in settings.extensions:
			if ext in self.bot.extensions:
				txt += f"\n ✅ {ext} loaded"
			else :
				txt += f"\n ❌ {ext} not loaded"

		txt += "```"

		E = discord.Embed(title="Debug", description=txt)
		E.add_field(name="Synced", value=self.bot.description == "Synced")
		E.add_field(name="Ping", value=f"{self.bot.latency*1000:.2f}ms")

		await inter.response.send_message(embed=E)


async def setup(bot:commands.Bot):
	await bot.add_cog(Owner(bot))

