import discord
from discord import app_commands
from discord.ext import commands

import datetime as dt
from typing import Literal, Optional
from utils import is_member, GetLogLink


class Fun(commands.Cog):
	def __init__(self, bot:commands.Bot) -> None:
		self.bot = bot

	@app_commands.command(description="Creates a poll")
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(question="The question to ask")
	async def poll(self, inter:discord.Interaction, question:str):
		await inter.response.defer()

		E = discord.Embed(title=question, color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot,str(inter.user.display_avatar)))
		E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1125361175929049158/770002495614877738.png")
		
		# send the message and get it back
		await inter.followup.send(embed=E)
		msg = await inter.original_response()

		if isinstance(msg, discord.InteractionMessage):
			await msg.add_reaction("✅")
			await msg.add_reaction("❌")
			await msg.add_reaction("⬜")


	@app_commands.command(description="Creates an anonymous poll")
	@app_commands.checks.cooldown(1, 60, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	@app_commands.guild_only()
	@app_commands.describe(question="The question to ask", time="The time the poll will last")
	async def apoll(self, inter:discord.Interaction, question:str, time:Literal["1m", "15m", "1h", "12h", "24h"]):
		await inter.response.defer()

		E = discord.Embed(title=question, color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot,str(inter.user.display_avatar)))
		E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/1125361175929049158/770002495614877738.png")

		class B_votes(discord.ui.View):
			def __init__(self, timeout:int):
				super().__init__(timeout=timeout)
				self.message : Optional[discord.Message]

				self.greens = 0
				self.reds = 0
				self.end = f"<t:{int(dt.datetime.now().timestamp() + timeout)}:R>"

				self.voted_ids = []

			async def interaction_check(self, inter2: discord.Interaction):
				if inter2.user.id in self.voted_ids:
					await inter2.response.send_message("You already voted!", ephemeral=True)
					return False
				self.voted_ids.append(inter2.user.id)
				return True

			@discord.ui.button(label="yes",style=discord.ButtonStyle.success, custom_id="yes")
			async def add(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.greens += 1
				await inter2.response.edit_message(content=f"{self.greens+self.reds} votes. Ends in {self.end}")

			@discord.ui.button(label="no",style=discord.ButtonStyle.danger, custom_id="no")
			async def list(self, inter2: discord.Interaction, _: discord.ui.Button):
				self.reds += 1
				await inter2.response.edit_message(content=f"{self.greens+self.reds} votes. Ends in {self.end}")

			async def on_timeout(self):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						if item.custom_id == "yes":
							item.label = f"yes ({self.greens})"
						elif item.custom_id == "no":
							item.label = f"no ({self.reds})"
						item.disabled = True

				if isinstance(self.message, discord.Message):
					txt = f"Poll ended, it lasted  {time}"
					await self.message.edit(view=self, content=txt)

		equivalents = {
			"1m": 60,
			"15m": 900,
			"1h": 3600,
			"12h": 43_200,
			"24h": 86_400
		}

		b_votes = B_votes(equivalents[time])
		b_votes.message = await inter.followup.send(view=b_votes, embed=E, content=f"0 votes. Ends in {b_votes.end}")


async def setup(bot:commands.Bot) -> None:
	await bot.add_cog(Fun(bot))