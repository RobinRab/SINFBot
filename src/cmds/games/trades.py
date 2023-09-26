import discord 
from discord import app_commands
from discord.ext import commands

import datetime as dt
from typing import Literal, Optional
currencies = Literal["🌹", "🍬", "💡"]

from utils import get_data, upd_data, GetLogLink, new_user, translate

class Trades(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Sell one of your items")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(
		amount="The amount to sell",       sell_item="The item to sell",
		price="Price to pay for the item", buy_item="The currency to pay with", 
		user="The user to sell to")
	async def trade(self, inter:discord.Interaction, amount:int, sell_item:currencies, price:int, buy_item:currencies, user:Optional[discord.Member]):
		await inter.response.defer()

		try:
			data = get_data(f"games/users/{inter.user.id}")
		except KeyError:
			return await inter.followup.send("You don't have an account yet")

		if inter.user == user:
			return await inter.followup.send("You can't sell to yourself")

		if amount < 0 or price < 0:
			return await inter.followup.send("You can't sell or buy negative amounts")

		if sell_item == buy_item:
			return await inter.followup.send("Sell item and buy item can't be the same")

		if amount > data[translate(sell_item)]:
			return await inter.followup.send(f"You don't have enough {sell_item} to sell")

		E = discord.Embed(title=f"Trade order by {inter.user.name}", color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.add_field(name="Selling", value=f"{amount}{sell_item}", inline=False)
		E.add_field(name="For", value=f"{price}{buy_item}", inline=False)

		class Button(discord.ui.View):
			def __init__(self, timeout=60):
				super().__init__(timeout=timeout)
				self.message : Optional[discord.Message]

			async def interaction_check(self, inter2: discord.Interaction):
				if inter.user == inter2.user:
					await inter2.response.send_message("You can't interact with your own message", ephemeral=True)
					return False
				if user is not None and user != inter2.user:
					await inter2.response.send_message("You can't interact with this message", ephemeral=True)
					return False
				return True

			async def close(self, reason):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True

				if isinstance(self.message, discord.Message):
					content = self.message.content
					content = content.split("\n")
					content[1] = f"({reason})"
					await self.message.edit(content='\n'.join(content), view=self)
				self.stop()

			@discord.ui.button(label=f"Buy for {price} {buy_item}",style=discord.ButtonStyle.success)
			async def buy(self, inter2: discord.Interaction, _: discord.ui.Button):
				try: 
					buyer = get_data(f"games/users/{inter2.user.id}")
				except KeyError:
					return await inter2.response.send_message("You don't have an account yet", ephemeral=True)
				
				if buyer[translate(buy_item)] < price:
					return await inter2.response.send_message(f"You don't have enough {buy_item} to buy this", ephemeral=True)

				# update buyer and seller
				buyer[translate(buy_item)] -= price
				buyer[translate(sell_item)] += amount
				upd_data(buyer, f"games/users/{inter2.user.id}")

				seller = get_data(f"games/users/{inter.user.id}")
				seller[translate(buy_item)] += price
				upd_data(seller, f"games/users/{inter.user.id}")

				await inter2.response.send_message(f"{inter.user.mention}, {inter2.user.mention} bought {amount} {sell_item} for {price} {buy_item}")
				await self.close("bought")

			if user is not None:
				@discord.ui.button(label=f"Refuse",style=discord.ButtonStyle.danger)
				async def sell(self, inter2: discord.Interaction, _: discord.ui.Button):
					# refund the item from the seller
					seller = get_data(f"games/users/{inter.user.id}")
					seller[translate(sell_item)] += amount
					upd_data(seller, f"games/users/{inter.user.id}")

					await inter2.response.send_message(f"{inter.user.mention}, {inter2.user.mention} refused to buy {amount} {sell_item} for {price} {buy_item}")
					await self.close("refused")

			async def on_timeout(self):
				# refund the item from the seller
				seller = get_data(f"games/users/{inter.user.id}")
				seller[translate(sell_item)] += amount
				upd_data(seller, f"games/users/{inter.user.id}")

				await self.close("timed out")

		txt = f"**{inter.user.name}** want to sell {amount} {sell_item} for {price} {buy_item}"
		if user is not None:
			E.set_footer(text=f"Trade offer for {user.name}", icon_url=await GetLogLink(self.bot, user.display_avatar.url))
			txt = f"{user.mention}, **{inter.user.name}** is selling {amount} {sell_item} for {price} {buy_item}"

		txt += f"\nend <t:{int(dt.datetime.now().timestamp()) + 60}:R>"

		# remove the item from the seller
		seller = get_data(f"games/users/{inter.user.id}")
		seller[translate(sell_item)] -= amount
		upd_data(seller, f"games/users/{inter.user.id}")

		button = Button()
		button.message = await inter.followup.send(txt, embed=E, view=button)

async def setup(bot:commands.Bot):
	await bot.add_cog(Trades(bot))