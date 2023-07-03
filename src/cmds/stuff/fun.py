import discord
from discord import app_commands
from discord.ext import commands


class Fun(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot = bot

async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(Fun(bot))