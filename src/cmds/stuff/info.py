import discord
from discord import app_commands
from discord.ext import commands

import io
import aiohttp
import requests
import datetime as dt

from settings import CONFESSION_ID
from utils import UnexpectedValue, is_member, GetLogLink, get_emoji


class General(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot = bot

	@app_commands.command(description="Converts a link into a file")
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	@app_commands.describe(link="The link to convert")
	async def link_to_file(self, inter:discord.Interaction, link:str):
		await inter.response.defer()

		formats = [".gif",".png",".jpg",".jpeg",".webp", ".mp3",".ogg",".wav",".flac", ".mp4",".webm",".mov"]
		if not any(x in link for x in formats):
			await inter.followup.send(f"**{inter.user.name},** link invalid",ephemeral=True)
			return

		Format = link.split(".")[-1]

		try :
			requests.get(link)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(link) as resp:
					File = discord.File(io.BytesIO(await resp.content.read()),filename=f"file.{Format}") #,filename="image.png") pour préciser le format
					await inter.followup.send(f"**{inter.user.name},** here's your file!",file=File)
		except :
			await inter.followup.send(f"**{inter.user.name},** link invalid",ephemeral=True)


	@app_commands.command(description="Converts a file into a link")
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	@app_commands.describe(file="The file to convert")
	async def file_to_link(self, inter:discord.Interaction, file:discord.Attachment):
		await inter.response.defer()
		formats = [".gif",".png",".jpg",".jpeg",".webp", ".mp3",".ogg",".wav",".flac", ".mp4",".webm",".mov"]
		if not any(x in file.filename for x in formats):
			await inter.followup.send(f"**{inter.user},** file invalid",ephemeral=True)
			return
		
		link = await GetLogLink(self.bot, file.url)
		await inter.followup.send(f"**{inter.user.name}**, here's your permanent link : {link}")

	@app_commands.command(description="Gets informations about an emoji")
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	@app_commands.describe(content="The emoji to get informations from")
	async def emoji(self, inter:discord.Interaction[commands.Bot], content:str):
		await inter.response.defer()

		emoji = await get_emoji(inter,content)

		if emoji is None:
			await inter.followup.send(f"**{inter.user.name}**, Emoji not found",ephemeral=True)
			return
	
		a = str(emoji.created_at)
		b = a.split()
		b[1] = b[1].split(".")[0]
		c = b[0].split("-")
		creator = emoji.user if emoji.user is not None else "Unknown"
		date =  str(c[2]+"/"+c[1]+"/"+ c[0] +" à " + b[1])
		link = await GetLogLink(self.bot, emoji.url)
		icon = await GetLogLink(self.bot, str(inter.user.display_avatar))
		embed = discord.Embed(
			title = "Here's your emoji",
			description = f"**Name : **`{emoji.name}`\n**Preview : **{emoji}\n**ID : **{emoji.id}\n**ID : **`{emoji}`\n**Server : **`{emoji.guild}`{creator}\n**Date added : **{date}",
			colour = discord.Colour.random()
			)
		embed.url=link
		embed.set_image(url=link)
		embed.set_footer(text=f"Requested by : {inter.user.name}",icon_url=icon)
		await inter.followup.send(embed=embed)


	@app_commands.command(description="Sends a confession anonymously")
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	@app_commands.describe(confess="The confession to send")
	async def confession(self, inter: discord.Interaction, confess:str):
		E = discord.Embed(
			title="New confession",
			description=confess,
			color=discord.Colour.from_rgb(88, 101, 242),
			timestamp=dt.datetime.now()
		)
		E.set_footer(text="Anon",icon_url="https://cdn.discordapp.com/attachments/709313685226782751/1049237441053208676/anon.png")
		chan = await self.bot.fetch_channel(CONFESSION_ID)
		if not isinstance(chan, discord.TextChannel):
			raise UnexpectedValue("Channel not found")

		await chan.send(embed=E)
		await inter.response.send_message("Confession sent !", ephemeral=True)


async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(General(bot))