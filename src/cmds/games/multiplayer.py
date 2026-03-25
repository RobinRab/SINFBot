import discord 
from discord import app_commands
from discord.ext import commands

import random
import datetime as dt
from typing import Optional, Literal
currencies = Literal["🌹", "🍬", "💡"]

from utils import get_data, upd_data, UserAccount, GetLogLink, translate

class Multiplayer(commands.Cog):
	def __init__(self,bot):
		self.bot : commands.Bot = bot

	@app_commands.command(description="Play shifumi against a friend!")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(bet="The amount to bet", currency="The currency to bet with", player="The player you want to play against")
	async def shifumi(self, inter:discord.Interaction, bet: int, currency: currencies, player: Optional[discord.Member]):
		await inter.response.defer()

		# current user check
		if not await self.user_check(inter, bet, currency):
			return

		return_player = await self.choose_player(inter, bet, currency, player, "shifumi")
		if return_player is None:
			if player is None:
				return await inter.followup.send("No player wanted to play with you")
			if player is not None:
				return  # message was already answered

		# start of actual game logic
		player1 = inter.user
		player2 = return_player

		players_data = {
			player1: {"member": player1, "color": "🟢", "score": 0, "embed_color": discord.Color.green()},
			player2: {"member": player2, "color": "🔴", "score": 0, "embed_color": discord.Color.red()}
		}

		choices = ["rock", "paper", "scissors"]
		emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
		round_history = []

		class ShifumiView(discord.ui.View):
			def __init__(self, timeout: float = 30):
				super().__init__(timeout=timeout)
				self.player_choices = {}

				self.default_choices = {}
				# default choice in case of timeout
				for player in [player1, player2]:
					self.default_choices[player.id] = random.choice(choices)

			async def interaction_check(self, inter2: discord.Interaction):
				if inter2.user.id not in [player1.id, player2.id]:
					await inter2.response.send_message("You are not part of this game!", ephemeral=True)
					return False
				return True

			@discord.ui.button(label="Rock 🪨", style=discord.ButtonStyle.primary, custom_id="rock")
			async def rock_button(self, inter2: discord.Interaction, button: discord.ui.Button):
				self.player_choices[inter2.user.id] = "rock"
				await inter2.response.send_message("You chose Rock 🪨!", ephemeral=True)

				if len(self.player_choices) == 2:
					self.stop()

			@discord.ui.button(label="Paper 📄", style=discord.ButtonStyle.success, custom_id="paper")
			async def paper_button(self, inter2: discord.Interaction, button: discord.ui.Button):
				self.player_choices[inter2.user.id] = "paper"
				await inter2.response.send_message("You chose Paper 📄!", ephemeral=True)

				if len(self.player_choices) == 2:
					self.stop()

			@discord.ui.button(label="Scissors ✂️", style=discord.ButtonStyle.danger, custom_id="scissors")
			async def scissors_button(self, inter2: discord.Interaction, button: discord.ui.Button):
				self.player_choices[inter2.user.id] = "scissors"
				await inter2.response.send_message("You chose Scissors ✂️!", ephemeral=True)

				if len(self.player_choices) == 2:
					self.stop()

			async def on_timeout(self):
				# default chosen in init
				self.stop()

		while players_data[player1]["score"] < 3 and players_data[player2]["score"] < 3:
			view = ShifumiView()
			embed_color = discord.Color.blurple()
			embed = discord.Embed(
				title="Shifumi",
				description=f"{players_data[player1]['color']} {player1.mention} vs {players_data[player2]['color']} {player2.mention}\nFirst to 3 wins!\n\n{players_data[player1]['color']} {player1.mention}: {players_data[player1]['score']}\n{players_data[player2]['color']} {player2.mention}: {players_data[player2]['score']}\n\nTimeout in: <t:{int(dt.datetime.now().timestamp()) + 30}:R>",
				color=embed_color
			)

			if round_history:
				history_text = "\n".join(
					f"{i+1}) {player1.mention} {emojis[r['p1_choice']]} vs {player2.mention} {emojis[r['p2_choice']]} - {r['result']}"
					for i, r in enumerate(round_history)
				)
				embed.add_field(name="Round History", value=history_text, inline=False)

			await inter.edit_original_response(embed=embed, view=view, content="")
			await view.wait()

			# ensure both players have a choice (in case of timeout)
			for player_fix in [player1, player2]:
				if player_fix.id not in view.player_choices:
					view.player_choices[player_fix.id] = view.default_choices[player_fix.id]

			p1_choice = view.player_choices[player1.id]
			p2_choice = view.player_choices[player2.id]

			if p1_choice == p2_choice:
				result = "⚪ draw!"
			elif (p1_choice == "rock" and p2_choice == "scissors") or \
				(p1_choice == "scissors" and p2_choice == "paper") or \
				(p1_choice == "paper" and p2_choice == "rock"):
				players_data[player1]["score"] += 1
				result = f"{players_data[player1]['color']} {player1.mention}"
				embed_color = players_data[player1]["embed_color"]
			else:
				players_data[player2]["score"] += 1
				result = f"{players_data[player2]['color']} {player2.mention}"
				embed_color = players_data[player2]["embed_color"]

			round_history.append({
				"p1_choice": p1_choice,
				"p2_choice": p2_choice,
				"result": result
			})

		winner = player1 if players_data[player1]["score"] == 3 else player2
		embed = discord.Embed(
			title="Shifumi - results",
			description=f"{players_data[winner]['color']} {winner.mention} wins {2 * bet}{currency}!\n\n{players_data[player1]['color']} {player1.mention}: {players_data[player1]['score']}\n{players_data[player2]['color']} {player2.mention}: {players_data[player2]['score']}",
			color=players_data[winner]["embed_color"]
		)

		history_text = "\n".join(
			f"{i+1}) {player1.mention} {emojis[r['p1_choice']]} vs {player2.mention} {emojis[r['p2_choice']]} - {r['result']}"
			for i, r in enumerate(round_history)
		)
		embed.add_field(name="Round History", value=history_text, inline=False)
	
		await inter.edit_original_response(embed=embed, view=None)

		# Award the winnings to the winner
		winner_data : UserAccount = get_data(f"games/users/{winner.id}")
		winner_data[translate(currency)] += 2 * bet
		
		upd_data(winner_data, f"games/users/{winner.id}")


	@app_commands.command(description="Play connect 4 against a friend!")
	@app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.guild_only()
	@app_commands.describe(
						bet="The amount to bet",
						currency="The currency to bet with",
						player="The player you want to play against",
						turn_timeout="Time per move in seconds (default 30, between 10 and 60)")
	async def connect4(self, inter:discord.Interaction, bet:int, currency:currencies, player:Optional[discord.Member], turn_timeout: Optional[int] = 30):
		await inter.response.defer()

		# fix turn_timeout if it's out of bounds or None
		if turn_timeout is None:
			turn_timeout = 30
		if turn_timeout < 10:
			turn_timeout = 10
		elif turn_timeout > 60:
			turn_timeout = 60

		# current user check
		if not await self.user_check(inter, bet, currency):
			return

		return_player = await self.choose_player(inter, bet, currency, player, "connect4")
		if return_player is None:
			if player is None:
				return await inter.followup.send("No player wanted to play with you")
			if player is not None:
				return # message was already answered

		# start of actual game logic
		player1 = inter.user
		player2 = return_player

		players_data = {
			player1: {"member": player1, "emoji": "🟢", "current_move": "❎", "embed_color":discord.Color.green(), "url":await GetLogLink(self.bot, player1.display_avatar.url)},
			player2: {"member": player2, "emoji": "🔴", "current_move": "❌", "embed_color":discord.Color.red(), "url":await GetLogLink(self.bot, player2.display_avatar.url)}
		}

		players = [player1, player2]
		current_player = 0

		board = [["⚪" for _ in range(7)] for _ in range(6)]
		def get_board_str(board, player:discord.Member | discord.User) -> str:
			txt = f"{player1.mention}🟢 vs {player2.mention}🔴\n\n"
			for row in board:
				txt += "".join(row) + "\n"
			txt += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"
			txt += "\n\n"
			txt += f"{player.mention}'s turn ({players_data[player]['emoji']})"
			return txt
		
		E = discord.Embed(title="Connect 4", color=players_data[player1]["embed_color"])
		E.set_author(name=player1.name, icon_url=players_data[player1]["url"])
		E.set_footer(text=f"Winner gets {2*bet}{currency}")

		def get_available_columns(board) -> list[int]:
			available_columns = []
			for col in range(7):
				if board[0][col] == "⚪":
					available_columns.append(col)
			return available_columns

		def someone_won(board):
			"returns 0 of no one won, 1 if player 1 won, 2 if player 2 won"
			# check horizontal
			for row in board:
				for i in range(4):
					if row[i] == row[i+1] == row[i+2] == row[i+3] != "⚪":
						return 1 if row[i] == "🟢" else 2

			# check vertical
			for col in range(7):
				for row in range(3):
					if board[row][col] == board[row+1][col] == board[row+2][col] == board[row+3][col] != "⚪":
						return 1 if board[row][col] == "🟢" else 2

			# check diagonal \
			for row in range(3):
				for col in range(4):
					if board[row][col] == board[row+1][col+1] == board[row+2][col+2] == board[row+3][col+3] != "⚪":
						return 1 if board[row][col] == "🟢" else 2

			# check diagonal /
			for row in range(3):
				for col in range(3,7):
					if board[row][col] == board[row+1][col-1] == board[row+2][col-2] == board[row+3][col-3] != "⚪":
						return 1 if board[row][col] == "🟢" else 2
					
			return 0

		def is_draw(board):
			for row in board:
				for cell in row:
					if cell == "⚪":
						return False
			return True

		while True:
			# this view has to be recreated every turn to reset the timeout and available columns
			class ColumnSelect(discord.ui.View):
				def __init__(self2, *, timeout: float = turn_timeout): #type:ignore[no-self-arg]
					super().__init__(timeout=timeout)
					# select one default choice, only applied if the user never plays
					self2.selected_column : int = random.choice(get_available_columns(board))

				async def interaction_check(self2, inter2: discord.Interaction): #type:ignore[no-self-arg]
					if inter2.user.id != players[current_player].id:
						await inter2.response.send_message("It's not your turn!", ephemeral=True)
						return False
					return True

				@discord.ui.select(placeholder="Select a column", options=[discord.SelectOption(label=str(i+1), value=str(i)) for i in get_available_columns(board)])
				async def select_callback(self2, inter2: discord.Interaction, select: discord.ui.Select):
					await inter2.response.defer() # mark the interaction as responded to avoid "This interaction failed" message
					self2.selected_column = int(select.values[0])
					self2.stop()

				async def on_timeout(self2): #type:ignore[no-self-arg]
					#await inter.followup.send(f"{players[current_player].mention} didn't select a column in time! Game over.")
					# select an available column randomly for the player that timed out
					self2.selected_column = random.choice(get_available_columns(board))
					self2.stop()

			view = ColumnSelect()
			board_text = get_board_str(board, players[current_player])
			embed = discord.Embed(title="Connect 4", description=board_text, color=players_data[players[current_player]]["embed_color"])
			embed.set_thumbnail(url="https://klipy.com/gifs/timer-1")
			embed.set_author(name=players[current_player].name, icon_url=players_data[players[current_player]]["url"])
			embed.set_footer(text=f"Winner gets {2*bet}{currency}")

			await inter.edit_original_response(embed=embed, view=view, content=f"{players[current_player].mention}, it's your turn! Select a column to drop your piece.\nTimeout in: <t:{int(dt.datetime.now().timestamp()) + turn_timeout}:R>")
			await view.wait()

			assert isinstance(view.selected_column, int)

			# clear previous play markers
			for i, row in enumerate(board):
				for ii, cell in enumerate(row):
					if cell == "❎":
						board[i][ii] = "🟢"
					elif cell == "❌":
						board[i][ii] = "🔴"

			# drop the piece in the selected column
			for row in range(5, -1, -1):
				if board[row][view.selected_column] == "⚪":
					board[row][view.selected_column] = players_data[players[current_player]]["current_move"]
					break

			winner = someone_won(board)
			if winner != 0:
				embed = discord.Embed(title="Connect 4 - Game Over", description=get_board_str(board, players[current_player]), color=players_data[players[current_player]]["embed_color"])
				embed.set_author(name=players[current_player].name, icon_url=players_data[players[current_player]]["url"])
				embed.set_footer(text=f"{players[winner-1].name} wins {2*bet}{currency}!")
				await inter.edit_original_response(embed=embed, view=None, content=f"{players[winner-1].mention} wins! 🎉")
				
				# give the winnings to the winner
				winner_data : UserAccount = get_data(f"games/users/{players[winner-1].id}")
				winner_data[translate(currency)] += 2*bet
				upd_data(winner_data, f"games/users/{players[winner-1].id}")
				return
		
			elif is_draw(board):
				embed = discord.Embed(title="Connect 4 - Game Over", description=get_board_str(board, players[current_player]), color=discord.Color.greyple())
				embed.set_author(name=players[current_player].name, icon_url=players_data[players[current_player]]["url"])
				embed.set_footer(text=f"It's a draw! Both players get their bet back.")
				await inter.edit_original_response(embed=embed, view=None, content=f"It's a draw! Both players get their bet back.")
				
				# refund both players
				for refund_player in players:
					player_data : UserAccount = get_data(f"games/users/{refund_player.id}")
					player_data[translate(currency)] += bet
					upd_data(player_data, f"games/users/{refund_player.id}")
				return

			current_player = 1 - current_player # switch player



	async def user_check(self, inter: discord.Interaction, bet:int, currency:currencies) -> bool:
		try : 
			user_data : UserAccount = get_data(f"games/users/{inter.user.id}")
		except :
			await inter.followup.send("You don't have an account yet")
			return False
		
		if bet < 1:
			await inter.followup.send(f"{inter.user.mention}, You need to bet a valid amount")
			return False
		
		amount = user_data.get(translate(currency), 0)
		if amount < bet:
			await inter.followup.send(f"{inter.user.mention}, You don't have enough {currency} to bet that amount")
			return False
		
		# subtract the bet from the user
		data : UserAccount = get_data(f"games/users/{inter.user.id}")
		data[translate(currency)] -= bet
		upd_data(data, f"games/users/{inter.user.id}")

		return True

	async def choose_player(self, inter: discord.Interaction,bet:int, currency:currencies, player:Optional[discord.Member | discord.User], game:str) -> Optional[discord.Member | discord.User]:
		if inter.user == player:
			await inter.followup.send("You can't play against yourself", ephemeral=True)
			return None

		E = discord.Embed(title=game, color=discord.Color.blurple())
		E.set_author(name=inter.user.name, icon_url=await GetLogLink(self.bot, inter.user.display_avatar.url))
		E.add_field(name="Betting", value=f"{bet}{currency}", inline=False)

		class Button(discord.ui.View):
			def __init__(self2, timeout_date:dt.datetime): #type:ignore[no-self-arg]
				self2.timeout_date = timeout_date
				super().__init__(timeout=60)
				self2.message : Optional[discord.Message]
				self2.return_player : Optional[discord.Member | discord.User] = None

			async def interaction_check(self2, inter2: discord.Interaction):#type:ignore[no-self-arg]
				self2.upd_timeout()

				if inter.user == inter2.user:
					await inter2.response.send_message("You can't interact with your own message", ephemeral=True)
					return False

				if player is not None and player != inter2.user:
					await inter2.response.send_message("You can't interact with this message", ephemeral=True)
					return False
				return True
			
			def upd_timeout(self2):#type:ignore[no-self-arg]
				timeout = (self2.timeout_date - dt.datetime.now()).total_seconds()
				self2.timeout = timeout

			async def close(self2, reason):#type:ignore[no-self-arg]
				for item in self2.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True

				if isinstance(self2.message, discord.Message):
					content = self2.message.content
					content = content.split("\n")
					content[1] = f"({reason})"
					await self2.message.edit(content='\n'.join(content), view=self2)
				self2.stop()

			@discord.ui.button(label=f"Join for {bet} {currency}",style=discord.ButtonStyle.success)
			async def join(self2, inter2: discord.Interaction, _: discord.ui.Button):
				await inter2.response.defer() # mark as answered

				try: 
					player_data : UserAccount = get_data(f"games/users/{inter2.user.id}")
				except:
					return await inter2.followup.send("You don't have an account yet, do **/collect** to create one", ephemeral=True)
				
				if player_data[translate(currency)] < bet:
					return await inter2.followup.send(f"You don't have enough {currency} to join this", ephemeral=True)

				# update buyer and seller
				player_data[translate(currency)] -= bet
				upd_data(player_data, f"games/users/{inter2.user.id}")

				self2.return_player = inter2.user

				await self2.close("joined")

			if player is not None:
				@discord.ui.button(label=f"Refuse",style=discord.ButtonStyle.danger)
				async def sell(self2, inter2: discord.Interaction, _: discord.ui.Button):
					# refund the item from the user that requested
					data : UserAccount= get_data(f"games/users/{inter.user.id}")
					data[translate(currency)] += bet
					upd_data(data, f"games/users/{inter.user.id}")

					await inter2.response.send_message(f"{inter.user.mention}, {inter2.user.mention} refused to play with you")
					await self2.close("refused")

			async def on_timeout(self2):#type:ignore[no-self-arg]
				# refund the item from the seller
				data : UserAccount = get_data(f"games/users/{inter.user.id}")
				data[translate(currency)] += bet
				upd_data(data, f"games/users/{inter.user.id}")

				await self2.close("timed out")

		view = Button(dt.datetime.now() + dt.timedelta(seconds=60))

		txt = f"{inter.user.name} wants to play **{game}**! Who wants to play?"
		if player is not None:
			txt = f"{player.mention}, {inter.user.name} wants to play connect4 with you!"
		txt += f"\nends <t:{int(dt.datetime.now().timestamp()) + 60}:R>"

		view.message = await inter.followup.send(embed=E, view=view, content=txt)
		await view.wait()

		return view.return_player


async def setup(bot:commands.Bot):
	await bot.add_cog(Multiplayer(bot))