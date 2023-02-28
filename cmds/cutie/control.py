import discord
from discord import app_commands
from discord.ext import commands

import aiohttp
import requests

from utils import is_cutie, activities, statuses


class Control(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Changes the bot's name")
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 3600, key=lambda i: (i.guild_id, i.guild.id))
	async def rename(self, inter:discord.Interaction, *, name:str):
		if not 2 <= len(name) <= 32:
			await inter.response.send_message("The name'length must be between 2 and 32 characters", delete_after=5)
			return
		try:
			await self.bot.user.edit(username=name)
			await inter.response.send_message(f"Name successfully changed to **{name}**")
		except: 
			await inter.response.send_message("Invalid name", delete_after=5)


	@commands.command(description="Changes the bot's avatar")
	@commands.check(is_cutie)
	@commands.cooldown(1, 3600, commands.BucketType.guild)
	async def avatar(self, inter: discord.Interaction, link:str=None):
		if link is None and len(inter.message.attachments) == 0:
			await inter.response.send_message("You must send a link or attach an image", delete_after=5)
			return
		elif link is None:
			link = inter.message.attachments[0].url

		try :
			requests.get(link)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(link) as resp:
					File = await resp.content.read()
					await self.bot.user.edit(avatar=File)
		except discord.DiscordException: #pense pas que c'est la bonne exception
			await inter.response.send_message(f"**{inter.user},** 404",delete_after=5)
		except ValueError:
			await inter.response.send_message(f"**{inter.user},** Invalid format",delete_after=5)
		except :
			await inter.response.send_message(f"**{inter.user},** Invalid link",delete_after=5)
		finally:
			await inter.response.send_message("Avatar successfully changed")


	@app_commands.command(description="Changes the bot's status")
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.guild.id))
	async def status(self, inter:discord.Interaction, state:statuses):
		await self.bot.change_presence(status=discord.Status(f'{state}'),activity=inter.guild.me.activity)
		await inter.response.send_message(f"Status successfully changed to **{state}**")


	@app_commands.command(description="Changes the bot's activity")
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.guild.id))
	async def activity(self, inter:discord.Interaction, typ:activities, text:str=None):
		if text is None and typ != "stop":
			await inter.response.send_message("You must specify a text", delete_after=5)
			return
	
		match typ:
			case "playing":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Game(name=text))
			case "watching":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Activity(type=discord.ActivityType.watching, name=text))
			case "listening":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Activity(type=discord.ActivityType.listening, name=text))
			case "stop":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Game(name=""))
				await inter.response.send_message(f"Activity successfully removed")
				return

		await inter.response.send_message(f"Activity successfully changed to **{typ} {text}**")


async def setup(bot:commands.Bot):
	await bot.add_cog(Control(bot))