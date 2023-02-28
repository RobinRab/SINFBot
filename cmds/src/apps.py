import discord
from discord import app_commands
from discord.ext import commands

import datetime as dt
from utils import GetLogLink, log, get_data

#!! all functions added in this class will be added as context menu
#!! all functions added in this class will be added as context menu
class GeneralCM(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		#adds all functions in this class to the context menu
		for attribute_name in GeneralCM.__dict__:
			if not attribute_name.startswith("_"):
				attr = getattr(self, attribute_name)
				if '__call__' in dir(attr):
					name = attribute_name.replace("_", " ").title()
					log("INFO", f"adding {name} to context menu")

					self.bot.tree.add_command(app_commands.ContextMenu( 
						name=name,
						callback=attr
					))

	#@app_commands.context_menu(name="User Info")
	async def user_info(self, inter:discord.Interaction,user:discord.Member):

		E = discord.Embed(title=str(user), colour=user.roles[-1].colour, description=user.mention)#color as user's
		E.set_thumbnail(url=await GetLogLink(self.bot, user.display_avatar)) #avatar
		E.add_field(name="**ID**", value=f"`{user.id}`") #id

		def getEllapsed(date:dt.datetime):
			# to avoid offset aware/naive errors, I'm using the difference in timestamp to convert them into a timedelta
			days = dt.timedelta(seconds=(dt.datetime.now().timestamp() - date.timestamp())).days
			y = int(days/365)
			m = int((days-(y*365))/30)
			d = int(days-(y*365)-(m*30))
			Ellapsed = f"({f'{y}a,' if y != 0 else ''}{f'{m}m,' if m != 0 else ''}{f'{d}j' if d != 0 else ''})"
			if Ellapsed == "()":
				return "Aujourd'hui"
			return Ellapsed

		if user.name != user.display_name : 
			E.add_field(name="**Surnom**",value=f"`{user.display_name}`") #nickname

		#bot aren't allowed to see badges, but maybe in the future
		badges = {
			"active_developer" : 1076560459697750067,
			"bug_hunter" : 822844655317155880,
			"bug_hunter_level_2" : 822844654374355005,
			"discord_certified_moderator" : 886160122617942047,
			"early_supporter" : 822844653811269642,
			"early_verified_bot_developer" : 822844653774569512,
			"hypesquad" : 822991679216418827,
			"hypesquad_bravery" : 822844654252458074,
			"hypesquad_balance" : 822844654000668672,
			"hypesquad_brilliance" : 822844655245852712,
			"partner" : 822844654210777138,
			"staff" : 822844655766863902,
			"verified_bot_developer": 822844653774569512,
		}

		txt = "-"
		premium = ""

		for name, id in badges.items():
			t = f"user.public_flags." + name
			if eval(t):
				txt += f"<:{name}:{id}> "

		#find if nitro + server boosting + banner
		if user.premium_since != None :
			txt += "<:nitro:822844654395064330>"
			#nitro badges
			#        1 month             2 months           3 months           6 months           9 months           12 months          15 months          18 months          24 months
			emotes = [822975889767137332,822975890324979763,822975890048548904,822975890224840724,822975889850892338,822975889947361381,822975890148556800,822975889692033064,822975889054760971]
			L = [1,2,3,6,9,12,15,18,24] #badges months values

			days = (dt.datetime.now()-user.premium_since).days
			m = int(days/30)
			if m != 0 :
				# if m in L I can find the emoji directly 
				if m in L :
					premium = f"Boost depuis : <t:{int(user.premium_since.timestamp())}:F>, <:month:{emotes[L.index(m)]}> `({m} mois)`" #name doesn't really matter
				# if not, I need to do i-1 to get the next closest lower emoji
				else :
					L.append(m)
					L.sort()
					i = L.index(m)
					premium = f"Boost depuis : <t:{int(user.premium_since.timestamp())}:F>, <:month:{emotes[i-1]}> `({m} mois)`" #name doesn't really matter

			if user.banner != None:
				E.image = await GetLogLink(self.bot, user.banner)

		if txt != "-" :
			E.add_field(name="Badges" if len(txt.split())>1 else "Badge",value=txt,inline=False)

		if premium != "" :
			E.add_field(name="Serveur boost",value=premium)

		#get date
		E.add_field(name="Date de création",value=f"<t:{int(user.created_at.timestamp())}:F>, `{getEllapsed(user.created_at)}`",inline=False)
		E.add_field(name="Date d'arrivée",value=f"<t:{int(user.joined_at.timestamp())}:F>, `{getEllapsed(user.joined_at)}`",inline=True)
		#roles
		txt = ""

		for r in user.roles[1:][::-1] : #not @everyone
			txt += f"{r.mention},"

		if txt != "" :
			E.add_field(name=f"Role{'s'if len(txt.split(','))>1 else None} **({len(txt.split(','))-1})**",value=txt[:-1],inline=False) #not last comma

		await inter.response.send_message(embed=E)

	async def avatar(self, inter:discord.Interaction, user:discord.Member):
		P = "**Voici votre avatar :**\n"
		D = ""

		for i in ["png","jpg","jpeg","webp"] :
			#Format = user.display_avatar(format=i)
			Format = str(user.display_avatar.with_format(i))
			D = f"{D}[{i}]({Format}), "

		if inter.user != user :
			P = f"**Voici l'avatar de : {user} **\n"

		if user.display_avatar.is_animated():
			D = "[gif]({})--".format(user.display_avatar.with_format("gif"))

		link = await GetLogLink(self.bot, user.display_avatar)
		embed = discord.Embed(colour=discord.Colour.from_rgb(0,0,0) ,title=P,description=f"**{D[:-2]}**")
		embed.url=link
		embed.set_image(url=link)
		embed.set_footer(text=f"Requête par : {inter.user}")
		
		await inter.response.send_message(embed=embed)

	async def birthday(self, inter:discord.Interaction, user:discord.Member):
		data : dict = get_data("birthday")
		year = dt.datetime.now().year

		if str(user.id) not in data.keys():
			await inter.response.send_message(f"**{user}** n'a pas ajouté son anniversaire")
			return

		date = dt.datetime(year, data[str(user.id)]["month"], data[str(user.id)]["day"])
		if date < dt.datetime.now():
			date = dt.datetime(year+1, data[str(user.id)]["month"], data[str(user.id)]["day"])

		left = date - dt.datetime.now()

		await inter.response.send_message(f"**{user}** a son anniversaire le {date.strftime('%d/%m/%Y')} dans **{left.days+1}j**")


async def setup(bot:commands.Bot):
	await bot.add_cog(GeneralCM(bot))