import discord
from discord import app_commands
from discord.ext import commands

import requests
import datetime as dt
from typing import List, Optional

from utils import is_member, get_data, upd_data, nospecial, GetLogLink
 
# Use a realistic User-Agent to avoid API blocking for default clients
DEFAULT_HEADERS = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Accept": "application/json",
}
class Tetrio(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot = bot
		#context menus can't be defined inside a cog, so we have to do it here
		self.bot.tree.add_command(app_commands.ContextMenu(
			name="Tetrio Profile",
			callback=self.tetrio_profile)
		)

	async def tprofile(self, inter:discord.Interaction, user_id:Optional[str]):
		data : dict = get_data("tetris")
	
		if user_id is None:
			user_id = str(inter.user.id)
			if user_id not in data.keys():
				return await inter.response.send_message("You are not connected to a Tetrio account", ephemeral=True)

		if user_id not in data.keys():
			return await inter.response.send_message("This user does not have a Tetrio profile", ephemeral=True)

		await inter.response.defer()

		name = data[user_id]
		
		

		try :
			rmain = requests.get(f"https://ch.tetr.io/api/users/{name}", headers=DEFAULT_HEADERS, timeout=10)
			rrecords = requests.get(f"https://ch.tetr.io/api/users/{name}/summaries", headers=DEFAULT_HEADERS, timeout=10)

			main = rmain.json()["data"]
			records = rrecords.json()["data"]
		except :
			return await inter.followup.send("An error occured while fetching data", ephemeral=True)
		
		l40 = records['40l']
		blitz = records['blitz']
		league = records['league']
		zenith = records['zenith']

		#if they have a country
		flag = ""
		if main['country'] is not None:
			flag = f" :flag_{main['country'].lower()}:"

		#get level by xp
		xp = int(main["xp"])
		level = round((xp/500)**0.6 + (xp/(5000+(max(0, xp-4*10^6)/5000))) + 1)

		# gets datetime object from string
		date = f"<t:{round(dt.datetime.strptime(main['ts'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"

		E = discord.Embed(
			title = f"__**{main['username'].upper()}**__" + flag,
			description = f"**Level**: {level}\n**Joined**: {date}",
			colour = discord.Colour.random(),
			url = f"https://ch.tetr.io/u/{main['username']}"
		)

		#! tetra league stats
		if league['gamesplayed'] >= 1:
			league_rank = league['rank']
			league_best = league['bestrank']
			league_tr = round(league['tr'])
			league_pps = league['pps']
			league_apm = league['apm']
			league_played = league['gamesplayed'] + league["past"].get("gamesplayed", 0)
			league_won = league['gameswon'] + league["past"].get("gameswon", 0)
			league_winrate = round(league_won/league_played*100, 2) if league_played != 0 else 0
			# top = league["standing"]
			# local_tol = league["standing_local"]

			E.add_field(name="**Tetra League**", value=f"{league_tr} TR \nRank: {league_rank}\nBest: {league_best}\nPPS: {league_pps}\nAPM: {league_apm}\nWins: {league_won}/{league_played}: {league_winrate}%")

		#! current zenith stats (quick play)
		if zenith['record'] != None:
			zenith_rank = zenith['rank']
			zenith_localrank = zenith['rank_local']

			# format the time from ms to min:sec.ms
			_ms_total = round(zenith['record']['results']['stats']['finaltime'])
			_secs_total = _ms_total // 1000
			_ms = _ms_total % 1000
			_mins = _secs_total // 60
			_secs = _secs_total % 60
			zenith_time = f"{_mins}:{_secs:02d}.{_ms:03d}"

			zenith_apm = round(zenith['record']['results']['aggregatestats']['apm'], 2)
			zenith_pps = round(zenith['record']['results']['aggregatestats']['pps'], 2)
			zenith_altitude = round(zenith['record']['results']['stats']['zenith']['altitude'])
			zenith_replay = f"https://tetr.io/#R:{zenith['record']['replayid']}"
			zenith_piecesgood = zenith['record']['results']['stats']['finesse']["perfectpieces"]
			zenith_piecesbad = zenith['record']['results']['stats']['finesse']["faults"]
			zenith_finesse = round(zenith_piecesgood/(zenith_piecesgood+zenith_piecesbad)*100, 2) if zenith_piecesgood+zenith_piecesbad != 0 else 0
			zenith_date = f"<t:{round(dt.datetime.strptime(zenith['record']['ts'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"

			E.add_field(name="**Zenith**", value=f"Altitude: [{zenith_altitude}]({zenith_replay})m\nRank: #{zenith_rank} (#{zenith_localrank} {flag})\nTime: {zenith_time}\nAPM: {zenith_apm}\nPPS: {zenith_pps}\nFinesse: {zenith_finesse}%\nDate: {zenith_date}")

		#! best zenith stats (quick play)
		if zenith['best'] != {}:
			zenith_rank = zenith["best"]['rank']

			# format the time from ms to min:sec.ms
			_ms_total = round(zenith["best"]['record']['results']['stats']['finaltime'])
			_secs_total = _ms_total // 1000
			_ms = _ms_total % 1000
			_mins = _secs_total // 60
			_secs = _secs_total % 60
			zenith_time = f"{_mins}:{_secs:02d}.{_ms:03d}"

			zenith_apm = round(zenith["best"]['record']['results']['aggregatestats']['apm'], 2)
			zenith_pps = round(zenith["best"]['record']['results']['aggregatestats']['pps'], 2)
			zenith_altitude = round(zenith["best"]['record']['results']['stats']['zenith']['altitude'])
			zenith_replay = f"https://tetr.io/#R:{zenith['best']['record']['replayid']}"
			zenith_piecesgood = zenith["best"]['record']['results']['stats']['finesse']["perfectpieces"]
			zenith_piecesbad = zenith["best"]['record']['results']['stats']['finesse']["faults"]
			zenith_finesse = round(zenith_piecesgood/(zenith_piecesgood+zenith_piecesbad)*100, 2) if zenith_piecesgood+zenith_piecesbad != 0 else 0
			zenith_date = f"<t:{round(dt.datetime.strptime(zenith['best']['record']['ts'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"

			E.add_field(name="**Zenith Best**", value=f"Altitude: [{zenith_altitude}]({zenith_replay})m\nRank: #{zenith_rank}\nTime: {zenith_time}\nAPM: {zenith_apm}\nPPS: {zenith_pps}\nFinesse: {zenith_finesse}%\nDate: {zenith_date}")

		#! 40L stats
		if l40['rank'] != -1:
			l40_rank = l40['rank']
			l40_localrank = l40['rank_local']
			
			# format the time from ms to min:sec.ms
			_ms_total = round(l40['record']['results']['stats']['finaltime'])
			_secs_total = _ms_total // 1000
			_ms = _ms_total % 1000
			_mins = _secs_total // 60
			_secs = _secs_total % 60
			if _mins > 0:
				l40_time = f"{_mins}:{_secs:02d}.{_ms:03d}"
			else:
				l40_time = f"{_secs}.{_ms:03d}"

			l40_pps = round(l40['record']['results']['aggregatestats']['pps'], 2)
			l40_piecesgood = l40['record']['results']['stats']['finesse']["perfectpieces"]
			l40_piecesbad = l40['record']['results']['stats']['finesse']["faults"]
			l40_finesse = round(l40_piecesgood/(l40_piecesgood+l40_piecesbad)*100, 2) if l40_piecesgood+l40_piecesbad != 0 else 0
			l40_date = f"<t:{round(dt.datetime.strptime(l40['record']['ts'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"
			l40_replay = f"https://tetr.io/#R:{l40['record']['replayid']}"

			E.add_field(name="**40L**", value=f"Time: [{l40_time}]({l40_replay})\nRank: #{l40_rank} (#{l40_localrank} {flag})\nPPS: {l40_pps}\nFinesse: {l40_finesse}%\nDate: {l40_date}")

		#! Blitz stats
		if blitz['rank'] != -1:
			blitz_rank = blitz['rank']
			blitz_localrank = blitz['rank_local']
			blitz_score = blitz['record']['results']['stats']['score']
			blitz_pieces = blitz['record']['results']['stats']['piecesplaced']
			blitz_piecesgood = blitz['record']['results']['stats']['finesse']["perfectpieces"]
			blitz_piecesbad = blitz['record']['results']['stats']['finesse']["faults"]
			blitz_finesse = round(blitz_piecesgood/(blitz_piecesgood+blitz_piecesbad)*100, 2) if blitz_piecesgood+blitz_piecesbad != 0 else 0
		
			blitz_pps = round(blitz['record']['results']['aggregatestats']['pps'], 2)
			blitz_date = f"<t:{round(dt.datetime.strptime(blitz['record']['ts'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"
			blitz_replay = f"https://tetr.io/#R:{blitz['record']['replayid']}"

			E.add_field(name="**Blitz**", value=f"Score: [{blitz_score:,}]({blitz_replay})\nRank: #{blitz_rank} (#{blitz_localrank} {flag})\nPlaced pieces: {blitz_pieces}\nPPS: {blitz_pps}\nFinesse: {blitz_finesse}%\nDate: {blitz_date}")


		# used if the user set an avatar
		if 'avatar_revision' in main.keys():
			E.set_thumbnail(url=await GetLogLink(self.bot, f"https://tetr.io/user-content/avatars/{main['_id']}.jpg?rv={main['avatar_revision']}"))
		else:
			# no avatar, I can't use SVG so error image
			E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png")


		#time format the time they have been playing for
		timeplayed = dt.timedelta(seconds=main['gametime'])
		timeplayed = f"{f'{timeplayed.days}d, ' if timeplayed.days != 0 else ''}{f'{timeplayed.seconds//3600}h' if timeplayed.seconds//3600 != 0 else ''}{f'{(timeplayed.seconds//60)%60}m' if (timeplayed.seconds//60)%60 != 0 else ''}{f'{(timeplayed.seconds//3600)%60}s' if (timeplayed.seconds//3600)%60 != 0 else ''}"

		E.set_footer(text=f"played for : {timeplayed}")

		await inter.followup.send(embed=E)

	@app_commands.command(description="Connect your discord account to your Tetrio profile")
	@app_commands.describe(name="The name of your Tetrio profile")
	@app_commands.guild_only()
	@app_commands.check(is_member)
	async def register(self, inter : discord.Interaction, name: str):
		data : dict = get_data("tetris")

		if str(inter.user.id) in data.keys():
			await inter.response.send_message(f"You are already connected to an account", ephemeral=True)
			return

		name = nospecial(name.lower())
		if name in data.values():
			await inter.response.send_message("The Tetrio profile is already registered to a discord account", ephemeral=True)
			return


		Tdata = requests.get(f"https://ch.tetr.io/api/users/{name}", headers=DEFAULT_HEADERS, timeout=10).json()
		if not Tdata['success']:
			await inter.response.send_message(f"The user {name.upper()} does not exist", ephemeral=True)
			return

		data[str(inter.user.id)] = name

		upd_data(data, "tetris")

		await inter.response.send_message(f"You have successfully been connected to {name.upper()}")

	@app_commands.command(name="profile", description="Shows the Tetrio profile of a user")
	@app_commands.guild_only()
	@app_commands.describe(user="The user's profile you want to see")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.check(is_member)
	async def profile(self, inter: discord.Interaction, user:Optional[str]):
		await self.tprofile(inter, user)

	@profile.autocomplete("user")
	async def user_autocomplete(self, inter: discord.Interaction, current:str) -> List[app_commands.Choice[str]]:
		lst = []
		for user_id in get_data("tetris").keys():
			user = self.bot.get_user(int(user_id))
			if user is not None:
				lst.append(app_commands.Choice(name=user.name, value=str(user_id)))

		return lst
	
	#tetrio profile context menu
	async def tetrio_profile(self, inter: discord.Interaction, user:discord.User):
		await self.tprofile(inter, str(user.id))

	@app_commands.command(description="Shows the rank, 40L and blitz leaderboards")
	@app_commands.guild_only()
	@commands.cooldown(1, 60, commands.BucketType.user)
	async def leaderboard(self, inter: discord.Interaction):
		await inter.response.defer()
		data = get_data("tetris")
		
		# key = username, value = (record value, replay id)
		league_scores = {}
		zenith_scores = {}
		zenith_best_scores = {}
		l40_scores = {}
		blitz_scores = {}

		for user in data.values():
			try:
				r = requests.get(f"https://ch.tetr.io/api/users/{user}/summaries", headers=DEFAULT_HEADERS, timeout=10)
				r.raise_for_status()
				data : dict = r.json().get("data", {})
			except Exception:
				continue

			# league TR (higher is better)
			league = data.get("league", {})
			if league:
				tr = league.get("tr")
				if tr != -1:
					league_scores[user] = round(tr)

			# zenith current (altitude, higher is better)
			zen = data.get("zenith", {})
			if zen and zen.get("record"):
				try:
					alt = zen["record"]["results"]["stats"]["zenith"]["altitude"]
					replay = zen["record"].get("replayid")
					zenith_scores[user] = (round(alt), f"https://tetr.io/#R:{replay}" if replay else None)
				except Exception:
					pass

			# zenith best (altitude, higher is better)
			if zen and zen.get("best"):
				try:
					alt = zen["best"]["record"]["results"]["stats"]["zenith"]["altitude"]
					replay = zen["best"]["record"].get("replayid")
					zenith_best_scores[user] = (round(alt), f"https://tetr.io/#R:{replay}" if replay else None)
				except Exception:
					pass

			# 40L (time in seconds with ms precision, lower is better)
			l40 = data.get("40l", {})
			if l40 and l40.get("record"):
				try:
					ms = l40["record"]["results"]["stats"]["finaltime"]
					seconds = round(ms / 1000, 3)
					replay = l40["record"].get("replayid")
					l40_scores[user] = (seconds, f"https://tetr.io/#R:{replay}" if replay else None)
				except Exception:
					pass

			# blitz (score, higher is better)
			bl = data.get("blitz", {})
			if bl and bl.get("record"):
				try:
					score = bl["record"]["results"]["stats"]["score"]
					replay = bl["record"].get("replayid")
					blitz_scores[user] = (score, f"https://tetr.io/#R:{replay}" if replay else None)
				except Exception:
					pass

		# sort leaderboards
		top_n = 10
		league_sorted = sorted(league_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
		zenith_sorted = sorted(zenith_scores.items(), key=lambda x: x[1][0], reverse=True)[:top_n]
		zenith_best_sorted = sorted(zenith_best_scores.items(), key=lambda x: x[1][0], reverse=True)[:top_n]
		l40_sorted = sorted(l40_scores.items(), key=lambda x: x[1][0])[:top_n]
		blitz_sorted = sorted(blitz_scores.items(), key=lambda x: x[1][0], reverse=True)[:top_n]

		def make_embed(title: str, rows: list, formatter):
			emb = discord.Embed(title=title, description="", color=discord.Colour.blurple())
			if not rows:
				emb.description = "No data."
				return emb
			desc = ""
			for i, (name, val) in enumerate(rows):
				medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else str(i + 1)
				desc += f"\n**{medal}) {name.upper()}**: {formatter(name, val)}"
			emb.description = desc
			return emb

		league_emb = make_embed("RANK LEADERBOARD", league_sorted, lambda n, v: f"[{v:,} TR](https://ch.tetr.io/u/{n})")
		zenith_emb = make_embed("ZENITH LEADERBOARD", zenith_sorted, lambda n, v: f"[{v[0]}]({v[1]})m")
		zenith_best_emb = make_embed("ZENITH BEST LEADERBOARD", zenith_best_sorted, lambda n, v: f"[{v[0]}]({v[1]})m")
		l40_emb = make_embed("40L LEADERBOARD", l40_sorted, lambda n, v: f"[{v[0]}s]({v[1]})")
		blitz_emb = make_embed("BLITZ LEADERBOARD", blitz_sorted, lambda n, v: f"[{v[0]:,}]({v[1]})")

		class LeaderBoard(discord.ui.View):
			def __init__(self, timeout=30):
				super().__init__(timeout=timeout)
				self.message: Optional[discord.Message] = None

			@discord.ui.button(label="League", style=discord.ButtonStyle.primary)
			async def league_btn(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=league_emb, view=self)

			@discord.ui.button(label="Zenith", style=discord.ButtonStyle.secondary)
			async def zenith_btn(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=zenith_emb, view=self)

			@discord.ui.button(label="Zenith Best", style=discord.ButtonStyle.secondary)
			async def zenith_best_btn(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=zenith_best_emb, view=self)

			@discord.ui.button(label="40L", style=discord.ButtonStyle.success)
			async def l40_btn(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=l40_emb, view=self)

			@discord.ui.button(label="Blitz", style=discord.ButtonStyle.danger)
			async def blitz_btn(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=blitz_emb, view=self)

			async def on_timeout(self):
				for item in self.children:
					if isinstance(item, discord.ui.Button):
						item.disabled = True
				if isinstance(self.message, discord.Message):
					await self.message.edit(view=self)

		view = LeaderBoard()
		view.message = await inter.followup.send(embed=league_emb, view=view)


async def setup(bot:commands.Bot):
	await bot.add_cog(Tetrio(bot))