import discord
from discord import app_commands
from discord.ext import commands

import aiohttp
import requests
from typing import Optional, Literal

from utils import UnexpectedValue, app_guild_cooldown, is_cutie

activities = Literal["playing", "watching", "listening", "stop"]
statuses = Literal["online", "idle", "dnd", "offline"]


class Control(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Changes the bot's name")
	@app_commands.describe(name="Write new name")
	@app_commands.check(is_cutie)
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 3600, key=app_guild_cooldown)
	async def rename(self, inter:discord.Interaction, *, name:str):

		if not 2 <= len(name) <= 32:
			await inter.response.send_message("The name'length must be between 2 and 32 characters", delete_after=5)
			return
		try:
			if not isinstance(self.bot.user, discord.ClientUser):
				raise Exception("self.bot.user is not a ClientUser")

			await self.bot.user.edit(username=name)
			await inter.response.send_message(f"Name successfully changed to **{name}**")
		except: 
			await inter.response.send_message("Invalid name", delete_after=5)


	@app_commands.command(description="Changes the bot's avatar")
	@app_commands.check(is_cutie)
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 3600, key=app_guild_cooldown)
	async def avatar(self, inter: discord.Interaction, link:Optional[str], file:Optional[discord.Attachment]):
		if isinstance(file, discord.Attachment):
			link = file.url
		else:
			link = link or ""

		try :
			requests.get(link)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(link) as resp:
					File = await resp.content.read()

					if not isinstance(self.bot.user, discord.ClientUser):
						raise UnexpectedValue("self.bot.user is not a ClientUser")
					await self.bot.user.edit(avatar=File)
		except :
			await inter.response.send_message(f"**{inter.user},** Invalid link",delete_after=5)
			return
		
		await inter.response.send_message("Avatar successfully changed")


	@app_commands.command(description="Changes the bot's status")
	@app_commands.describe(state="Chose the new status of the bot")
	@app_commands.check(is_cutie)
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 60, key=app_guild_cooldown)
	async def status(self, inter:discord.Interaction, state:statuses):
		if not isinstance(inter.guild, discord.Guild):
			raise UnexpectedValue("inter.guild.me is not a Member")
		if not isinstance(inter.guild.me.activity, discord.Activity):
			raise UnexpectedValue("inter.guild.me.activity is not an Activity")
	
		await self.bot.change_presence(status=discord.Status(f'{state}'),activity=inter.guild.me.activity)
		await inter.response.send_message(f"Status successfully changed to **{state}**")


	@app_commands.command(description="Changes the bot's activity")
	@app_commands.describe(
		typ="Choose the activity type",
		text = "Enter any text"
	)
	@app_commands.check(is_cutie)
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 60, key=app_guild_cooldown)
	async def activity(self, inter:discord.Interaction, typ:activities, text:Optional[str]):
		if not isinstance(inter.guild, discord.Guild):
			raise UnexpectedValue("inter.guild.me is not a Member")

		match typ:
			case "playing":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Game(name=text or " "))
			case "watching":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Activity(type=discord.ActivityType.watching, name=text or ""))
			case "listening":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Activity(type=discord.ActivityType.listening, name=text or ""))
			case "stop":
				await self.bot.change_presence(status=inter.guild.me.status,activity=discord.Game(name=""))
				await inter.response.send_message(f"Activity successfully removed")
				return

		await inter.response.send_message(f"Activity successfully changed to **{typ} {text or ''}**")


	@app_commands.command(description="Talk using the bot")
	@app_commands.describe(text="Enter any text", file="Enter any file")
	@app_commands.check(is_cutie)
	@app_commands.guild_only()
	@app_commands.checks.cooldown(1, 1, key=app_guild_cooldown)
	async def say(self, inter:discord.Interaction, text:str, file:Optional[discord.Attachment]):
		if not isinstance(inter.channel, discord.TextChannel):
			return await inter.response.send_message("This command can only be used in a textchannel", ephemeral=True)
	
		if isinstance(file, discord.Attachment):
			f = await file.to_file()
			await inter.channel.send(text, file=f)
		else:
			await inter.channel.send(text)

		await inter.response.send_message("✅** **", ephemeral=True)


async def setup(bot:commands.Bot):
	await bot.add_cog(Control(bot))