import discord
from discord import app_commands
from discord.ext import commands

import requests
import datetime as dt
from typing import List, Optional

from src.utils import get_data, upd_data, nospecial, GetLogLink

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
		
		r1= requests.get(f"https://ch.tetr.io/api/users/{name}")
		r2 = requests.get(f"https://ch.tetr.io/api/users/{name}/records")

		try :
			data = r1.json()
			datarecords = r2.json()

			if all([data["success"], datarecords["success"]]):
				top = len(requests.get(f"https://ch.tetr.io/api/users/lists/league/all?country={data['data']['user']['country'].upper()}").json()['data']['users'])
			else:
				raise ValueError

		except:
			return await inter.response.send_message("An error occured while fetching data", ephemeral=True)

		#if they have a country
		flag = ""
		if data['data']['user']['country'] is not None:
			flag = f" :flag_{data['data']['user']['country'].lower()}:"

		#get level by xp
		xp = data["data"]["user"]["xp"]
		level = round((xp/500)**0.6 + (xp/(5000+(max(0, xp-4*10^6)/5000))) + 1)

		ranks = {
			"z" : "<:z_:1054519813164245042>",
			"d" : "<:d:1054510687612833912>",
			"d+" : "<:dp:1054510720693321768>",
			"c-" : "<:cm:1054510750921654402>",
			"c" : "<:c:1054510835453665410>",
			"c+" : "<:cp:1054510870723563551>",
			"b-" : "<:bm:1054510901237141594>",
			"b" : "<:b:1054511014386876560>",
			"b+" : "<:bp:1054511043407257690>",
			"a-" : "<:am:1054511090156961912>",
			"a" : "<:a:1054511789959815249>",
			"a+" : "<:ap:1054511812445478923>",
			"s-" : "<:sm:1054511832544587886>",
			"s" : "<:s:1054511852509474927>",
			"s+" : "<:sp:1054511871836835880>",
			"ss" : "<:ss:1054511896088293556>",
			"u" : "<:u:1054511917726699645>",
			"x" : "<:x_:1054511941114150995>"
		}

		#number of players in their country
		top = len(requests.get(f"https://ch.tetr.io/api/users/lists/league/all?country={data['data']['user']['country'].upper()}").json()['data']['users'])

		# gets datetime object from string
		date = f" joined <t:{round(dt.datetime.strptime(data['data']['user']['ts'],'%Y-%m-%dT%H:%M:%S.%fZ').timestamp())}:R>"

		glob = "Unranked"
		local = ""
		if data['data']['user']['league']['standing'] != -1:
			glob = f"\n Global : {data['data']['user']['league']['standing']} top {round(data['data']['user']['league']['percentile']*100,2)}%"
			local = f"\n Local: {data['data']['user']['league']['standing_local']}/{top} top {round((data['data']['user']['league']['standing_local'])/top*100, 2)}%"

		E = discord.Embed(
			title = f"__**{data['data']['user']['username'].upper()}**__" + flag,
			description=f"level {level} \n **{round(data['data']['user']['league']['rating'])}** TR {ranks[data['data']['user']['league']['rank']]} {glob} {local}\n{date}",
			colour = discord.Colour.random(),
			url = f"https://ch.tetr.io/u/{data['data']['user']['username']}"
		)

		if 'avatar_revision' in data['data']['user']:
			E.set_thumbnail(url=await GetLogLink(self.bot, f"https://tetr.io/user-content/avatars/{data['data']['user']['_id']}.jpg?rv={data['data']['user']['avatar_revision']}"))
		else:
			E.set_thumbnail(url="https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png")


		#time format the time they have been playing for
		timeplayed = dt.timedelta(seconds=data['data']['user']['gametime'])
		timeplayed = f"{f'{timeplayed.days}d, ' if timeplayed.days != 0 else ''}{f'{timeplayed.seconds//3600}h' if timeplayed.seconds//3600 != 0 else ''}{f'{(timeplayed.seconds//60)%60}m' if (timeplayed.seconds//60)%60 != 0 else ''}{f'{(timeplayed.seconds//3600)%60}s' if (timeplayed.seconds//3600)%60 != 0 else ''}"

		E.set_footer(text=f"played for : {timeplayed}")

		stats = f"""
				**Wins**  : {data['data']['user']['league']['gameswon']}/{data['data']['user']['league']['gamesplayed']} : {round(data['data']['user']['league']['gameswon']/data['data']['user']['league']['gamesplayed']*100,2)}%
				**APM**   : {data['data']['user']['league']['apm']}
				**PPS**   : {data['data']['user']['league']['pps']}
				**Score** : {data['data']['user']['league']['vs']}
		"""
		E.add_field(name="__**TETRA STATS**__", value=stats)
		E.add_field(name="** **", value="** **")

		id = datarecords["data"]["records"]['40l']['record']["replayid"]
		url = f"https://tetr.io/#r:{id}"
		records = f"**40L**   : [{round(datarecords['data']['records']['40l']['record']['endcontext']['finalTime']/1000, 3)}]({url})s"

		if datarecords['data']['records']['40l']['rank'] is not None:
			records += f"\n**Rank**  : {datarecords['data']['records']['40l']['rank']}"

		id = datarecords["data"]["records"]['blitz']['record']["replayid"]
		url = f"https://tetr.io/#r:{id}"
		records += f"\n**Blitz** : [{datarecords['data']['records']['blitz']['record']['endcontext']['score']:,}]({url})"

		if datarecords['data']['records']['blitz']['rank'] is not None:
			records += f"\n**Rank**  : {datarecords['data']['records']['blitz']['rank']}"

		E.add_field(name="__**RECORDS**__", value=records)

		await inter.followup.send(embed=E)

	@app_commands.command(description="Connect your discord account to your Tetrio profile")
	@app_commands.describe(name="The name of your Tetrio profile")
	@app_commands.guild_only()
	async def register(self, inter : discord.Interaction, name: str):
		data : dict = get_data("tetris")

		if str(inter.user.id) in data.keys():
			await inter.response.send_message(f"You are already connected to an account", ephemeral=True)
			return

		name = nospecial(name.lower())
		if name in data.values():
			await inter.response.send_message("The Tetrio profile is already registered to a discord account", ephemeral=True)
			return


		Tdata = requests.get(f"https://ch.tetr.io/api/users/{name}").json()
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
	async def profile(self, inter: discord.Interaction, user:str=None):
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
		
		datatr = {}
		data40 = {}
		datablitz = {}
		userranks = {}

		ranks = {
			"z" : "<:z_:1054519813164245042>",
			"d" : "<:d:1054510687612833912>",
			"d+" : "<:dp:1054510720693321768>",
			"c-" : "<:cm:1054510750921654402>",
			"c" : "<:c:1054510835453665410>",
			"c+" : "<:cp:1054510870723563551>",
			"b-" : "<:bm:1054510901237141594>",
			"b" : "<:b:1054511014386876560>",
			"b+" : "<:bp:1054511043407257690>",
			"a-" : "<:am:1054511090156961912>",
			"a" : "<:a:1054511789959815249>",
			"a+" : "<:ap:1054511812445478923>",
			"s-" : "<:sm:1054511832544587886>",
			"s" : "<:s:1054511852509474927>",
			"s+" : "<:sp:1054511871836835880>",
			"ss" : "<:ss:1054511896088293556>",
			"u" : "<:u:1054511917726699645>",
			"x" : "<:x_:1054511941114150995>"
		}

		for user in data.values():
			get = requests.get(f"https://ch.tetr.io/api/users/{user}").json()
			getr = requests.get(f"https://ch.tetr.io/api/users/{user}/records").json()

			if not all([get['success'] , getr['success']]) :
				await inter.response.send_message("An error occured while fetching the data")
				return

			datatr[user] = round(get['data']['user']['league']['rating'])

			url = f"https://tetr.io/#r:{getr['data']['records']['40l']['record']['replayid']}"
			data40[user] = (round(getr['data']['records']['40l']['record']['endcontext']['finalTime']/1000, 3), url)

			url = f"https://tetr.io/#r:{getr['data']['records']['blitz']['record']['replayid']}"
			datablitz[user] = (getr['data']['records']['blitz']['record']['endcontext']['score'], url)

			userranks[user] = ranks[get['data']['user']['league']['rank']]

		datatr = dict(sorted(datatr.items(),key=lambda x:x[1],reverse = True))
		data40 = dict(sorted(data40.items(),key=lambda x:x[1][0],reverse = False))
		datablitz = dict(sorted(datablitz.items(),key=lambda x:x[1][0],reverse = True))

		tr_E = discord.Embed(
			title="RANK LEADERBOARD",
			description="",
			color=discord.Colour.blurple()
		)

		l40_E = discord.Embed(
			title="40L LEADERBOARD",
			description="",
			color=discord.Colour.green()
		)

		blitz_E = discord.Embed(
			title="BLITZ LEADERBOARD",
			description="",
			color=discord.Color.red()
		)

		for index, (tr, l40, blitz) in enumerate(zip(datatr, data40, datablitz)):
			

			if index == 0:
				tr_E.description += f"**🥇 {tr.upper()}** : {datatr[tr]:,} TR {userranks[tr]}"
				l40_E.description += f"**🥇 {l40.upper()}** : [{data40[l40][0]}]({data40[l40][1]})s"
				blitz_E.description += f"**🥇 {blitz.upper()}** : [{datablitz[blitz][0]:,}]({datablitz[blitz][1]})"

			elif index == 1:
				tr_E.description += f"\n**🥈 {tr.upper()}** : {datatr[tr]:,} TR {userranks[tr]}"
				l40_E.description += f"\n**🥈 {l40.upper()}** : [{data40[l40][0]}]({data40[l40][1]})s"
				blitz_E.description += f"\n**🥈 {blitz.upper()}** : [{datablitz[blitz][0]:,}]({datablitz[blitz][1]})"

			elif index == 2:
				tr_E.description += f"\n**🥉 {tr.upper()}** : {datatr[tr]:,} TR {userranks[tr]}"
				l40_E.description += f"\n**🥉 {l40.upper()}** : [{data40[l40][0]}]({data40[l40][1]})s"
				blitz_E.description += f"\n**🥉 {blitz.upper()}** : [{datablitz[blitz][0]:,}]({datablitz[blitz][1]})"

			else:
				tr_E.description += f"\n** {index+1}. {tr.upper()}** : {datatr[tr]:,} TR {userranks[tr]}"
				l40_E.description += f"\n** {index+1}. {l40.upper()}**: [{data40[l40][0]}]({data40[l40][1]})s"
				blitz_E.description += f"\n** {index+1}. {blitz.upper()}** : [{datablitz[blitz][0]:,}]({datablitz[blitz][1]})"

		class leader(discord.ui.View):
			def __init__(self, timeout=60):
				super().__init__(timeout=timeout)
				#self.value = None

			@discord.ui.button(label="Rank",style=discord.ButtonStyle.primary)
			async def t1(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=tr_E)

			@discord.ui.button(label="40L",style=discord.ButtonStyle.success)
			async def t3(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=l40_E)

			@discord.ui.button(label="Blitz",style=discord.ButtonStyle.danger)
			async def t4(self, inter: discord.Interaction, button: discord.ui.Button):
				await inter.response.edit_message(embed=blitz_E)

			async def on_timeout(self):
				for item in self.children:
					item.disabled = True

				await self.message.edit(view=self)

		leader.message = await inter.followup.send(embed=tr_E, view=leader())


async def setup(bot:commands.Bot):
	await bot.add_cog(Tetrio(bot))