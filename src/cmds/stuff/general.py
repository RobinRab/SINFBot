import discord
from discord.ext import commands

import re
import io
import aiohttp
import requests
import datetime as dt

from settings import CONFESSION_ID
from utils import GetLogLink, get_emoji


class General(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot = bot

	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def file(self, ctx:commands.Context, link=None):
		if link is None : 
			await ctx.send("You must specify a link to convert",delete_after=5)
			return
		await ctx.trigger_typing()
	
		Format = None
		Fim = [".gif",".png",".jpg",".jpeg",".webp"]
		Fau = [".mp3",".ogg",".wav",".flac"]
		Fvi = [".mp4",".webm",".mov"]
		LL = [Fim,Fau,Fvi]
		for n in LL :
			for i in n :
				if i in link :
					Format = i
					break
		
		if Format is None:
			await ctx.send(f"**{ctx.author},** link invalid",delete_after=5)
			return
		
		try :
			requests.get(link)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(link) as resp:
					File = discord.File(io.BytesIO(await resp.content.read()),filename=f"file{Format}") #,filename="image.png") pour préciser le format
					await ctx.send(f"**{ctx.author},** here's your file!",file=File)
		except :
			await ctx.send(f"**{ctx.author},** link invalid",delete_after=15)


	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def link(self, ctx:commands.Context):
		if len(ctx.message.attachments) >= 1 :
			await ctx.trigger_typing()
			link = await GetLogLink(self.bot, ctx.message.attachments[0].url)
			await ctx.send(f"**{ctx.author}**, here's your permanent link : {link}")
		else : 
			await ctx.send("You must specify a file as attachment",delete_after=5)


	@commands.command()
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def emoji(self, ctx:commands.Context, content=None):
		if content is None : 
			await ctx.send("You most specify an emoji",delete_after=5)
			return
		
		async with ctx.typing():
			emoji = await get_emoji(ctx,content)

			if emoji is None:
				await ctx.send(f"**{ctx.author}**, Emoji not found",delete_after=5)
				return
		
			a = str(emoji.created_at)
			b = a.split()
			b[1] = b[1].split(".")[0]
			c = b[0].split("-")
			creator = emoji.user if emoji.user is not None else "Unknown"
			date =  str(c[2]+"/"+c[1]+"/"+ c[0] +" à " + b[1])
			link = await GetLogLink(self.bot, emoji.url)
			icon = await GetLogLink(self.bot, ctx.author.display_avatar)
			embed = discord.Embed(
				title = "Here's your emoji",
				description = f"**Name : **`{emoji.name}`\n**Preview : **{emoji}\n**ID : **{emoji.id}\n**ID : **`{emoji}`\n**Server : **`{emoji.guild}`{creator}\n**Date added : **{date}",
				colour = discord.Colour.random()
				)
			embed.url=link
			embed.set_image(url=link)
			embed.set_footer(text=f"Requested by : {ctx.author}",icon_url=icon)
			await ctx.send(embed=embed)


	@commands.command(aliases=["confess"])
	@commands.dm_only()
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def confession(self, ctx: commands.Context, *, txt=None):
		if txt is None:
			await ctx.channel.send("You must specify a confession")
			return

		E = discord.Embed(
			title="New confession",
			description=txt,
			color=discord.Colour.from_rgb(88, 101, 242),
			timestamp=dt.datetime.now()
		)
		E.set_footer(text="Anon",icon_url="https://cdn.discordapp.com/attachments/709313685226782751/1049237441053208676/anon.png")
		chan = await self.bot.fetch_channel(CONFESSION_ID)

		await chan.send(embed=E)
		await ctx.channel.send(embed=discord.Embed(
			title = "Confession sent",
			color=discord.Colour.green()
			)
		)


async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(General(bot))