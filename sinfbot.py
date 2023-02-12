
token = "MTA0ODcxNzE1NDkyMjU0MTIxNw.GQncs0.Gr1eDYBCRpa2SxEby78DeHFtSgxaZVAL8DBnVM"

import discord 
from discord import app_commands
intents = discord.Intents.all()
from discord.ext import commands
from discord.ext.commands import MemberConverter, EmojiConverter, TextChannelConverter, Context
client = commands.Bot(command_prefix=["!"],case_insensitive=True,help_command=None,intents=intents,strip_after_prefix=True)
tree = client.tree
tree.synced = False

if 1 : #set everything I need
	import re
	import aiohttp
	import io
	import requests
	import asyncio
	import time
	import calendar
	import random
	import datetime as dt
	import traceback
	import json
	import copy
	from typing import Literal, List
	import threading

	async def GetLogLink(link):
		LogPic = client.get_channel(709313685226782751)
		link = str(link)
		Fim = [".png",".jpg",".jpeg",".webp"]
		Fau = [".mp3",".ogg",".wav",".flac"]
		Fvi = [".mp4",".webm",".mov"]
		LL = [Fim,Fau,Fvi,".gif"]
		for n in LL :
			for i in n :
				if i in link :
					Format = i
					if i in Fim :
						Format = ".png"
					elif i in Fau : 
						Format = ".mp3"
					elif i in Fvi :
						Format = ".mp4"
					else : 
						Format = ".gif"
					try : 
						async with aiohttp.ClientSession() as cs:
							async with cs.get(link) as resp:
								File = discord.File(io.BytesIO(await resp.content.read()),filename=f"file{Format}")
								M = await LogPic.send(file=File)
								return M.attachments[0].url
					except :
						return "https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png"
		return "https://cdn.discordapp.com/attachments/709313685226782751/830935863893950464/discordFail.png"

	def simplify(text):
		import unicodedata
		try:
			text = unicode(text, 'utf-8')
		except NameError:
			pass
		text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
		return str(text)

	def nospecial(text):
		import re
		text = re.sub("[^a-zA-Z0-9_]+", "",simplify(text))
		return text

	async def get_member(ctx, text):
		liste = []
		try : #search by conv
			conv = MemberConverter()
			mem = await conv.convert(ctx, text)
			return [mem]
		except commands.errors.BadArgument : # search by name
			members = [i for i in ctx.guild.members if not i.bot]
			for i in members : 
				if i.name == text :
					liste.append(i)
				elif i.display_name == text :
					liste.append(i)
				else :
					if simplify(text.lower()) in simplify(i.name.lower()):
						liste.append(i)
					elif simplify(text.lower()) in simplify(i.display_name.lower()): 
						liste.append(i)
			return liste

	def get_data(*opts) :
		"""opt is the part of the data you want to access
			if opt is None, return all the data"""

		with open("datasinf.json", 'r') as f:
			data = json.load(f)

		for opt in opts:
			data = data[opt]

		return data

	def upd_data(new_data, *keys):
		"""data is the edited data from get_data()
			opt is the part of the data you edited"""

		with open("datasinf.json", 'r') as f:
			data = json.load(f)

		if not keys:
			data = new_data
		else:
			current_level = data
			for key in keys[:-1]:
				current_level = current_level[key]
			current_level[keys[-1]] = new_data

		with open("datasinf.json", 'w') as f:
			json.dump(data, f, indent=4)

@client.event
async def on_command_error(ctx, error):
	if isinstance(error, commands.CommandNotFound) :
		return
	elif isinstance(error, commands.NoPrivateMessage):
		await ctx.send("Cette commande n'est pas utilisable en messages privés",delete_after=30)
	elif isinstance(error, commands.MaxConcurrencyReached):
		if str(error.per) == "BucketType.guild" : 
			await ctx.send("Cette commande est déjà utilisée sur le serveur",delete_after=30)
		elif str(error.per) == "BucketType.user" : 
			await ctx.send("Vous êtes déjà entrain d'utiliser cette commande",delete_after=30)
		elif str(error.per) == "BucketType.channel" : 
			await ctx.send("Cette commande est déjà en cours d'utilisation dans ce salon",delete_after=30)
		else :
			await ctx.send(error)
	elif isinstance(error, commands.BotMissingPermissions):
			L = error.missing_perms
			if len(L) == 1 : 
				await ctx.send(f"Je ne peux pas executer cette commande, il me faut la permission : **{L[0]} **!",delete_after=30)
			elif len(L) > 1 : 
				await ctx.send(f"Je ne peux pas executer cette commande, j'ai besoin des permissions : **{', '.join(L)}** ! ",delete_after=30)
	elif isinstance(error, commands.CommandOnCooldown):
		await ctx.send(f"Vous ne pouvez pas encore utiliser cette commande, attendez : **{round(error.retry_after,1)}** secondes",delete_after=error.retry_after)
	elif isinstance(error, commands.MissingPermissions):
		L = error.missing_perms
		if len(L) == 1 : 
			await ctx.send(f"Vous ne pouvez pas executer cette commande, vous avez besoin de la permission : **{L[0]} **!",delete_after=30)
		elif len(L) > 1 :
			await ctx.send(f"Vous ne pouvez pas executer cette commande, vous avez besoin des permissions : **{', '.join(L)}** ! ",delete_after=30)
	elif isinstance(error, commands.CheckFailure):
		await ctx.send(f"**{ctx.author},** Vous n'êtes pas autorisé à utiliser la commande **{ctx.command}**",delete_after=30)
	else :
		await ctx.send(error)

		error_chan = await client.fetch_channel(814575840343752714)

		E = discord.Embed(title=str(error),colour=0xFF0000,timestamp=dt.datetime.now())
		E.url = ctx.message.jump_url
		E.description = "\n".join(traceback.format_exception(type(error),error,error.__traceback__))
		await error_chan.send(embed=E)

@client.event
async def on_ready():
	print("\SINF illégal family bot online\n")

@client.command()
@commands.is_owner()
async def sync(ctx):
	# 1032356193731100702
	# Make sure the bot doesn't sync twice
	if tree.synced:
		ctx.send("Bot already synced")
		return
	try : 
		tree.copy_global_to(guild=discord.Object(id=1032356193731100702))
		
		await tree.sync(guild=discord.Object(id=1032356193731100702)) #specify a guild to update tree commands
		tree.synced = True

		await ctx.send("Bot synced")
	except:
		await ctx.send("Sync failed")

@client.event
async def on_message(message : discord.Message):
	if message.author.bot :
		return

	#ctx = await client.get_context(message)

	#resp command
	if 1:
		data = get_data()

		for clef in data["phrases"]:
			if re.search(r'\W',clef["mot"][0]) or re.search(r"\W",clef["mot"][-1]) : #if non-aplhanumeric (start/end) : needs to be handled differently
				pat = r"(\W|^)" + re.escape(str(simplify(clef['mot'].lower()))) + r"(\W|$)"
			else :
				pat = r"\b" + re.escape(str(simplify(clef['mot'].lower()))) + r"\b"

			if re.search(pat,simplify(message.content).lower()) :
				await message.channel.send(clef["text"],delete_after=clef["time"])
				break

	#anon says
	if message.channel.id == 1054385316506652692:
		general = message.guild.get_channel(1032356194255376466)

		Files= []
		try :
			for link in message.attachments:
				link = link.url
				name = link.split("/")[-1].split(".")[0]
				Format = link.split(".")[-1]
				requests.get(link)
				async with aiohttp.ClientSession() as cs:
					async with cs.get(link) as resp:
						Files.append(discord.File(io.BytesIO(await resp.content.read()),filename=f"{name}.{Format}"))

			await general.send(content=message.content, files=Files)
		except:
			await general.send("Désolé, une errueur est survenue")

	await client.process_commands(message)

@client.event
async def on_member_update(before:discord.Member, after:discord.Member):
	#return if removed a role
	if len(before.roles) > len(after.roles):
		return

	# return if not silver
	if before.id != 457594644495073280:
		return

	channel = client.get_channel(1032356194255376466)

	#get the first new role
	for b, a in zip(before.roles, after.roles):
		if b != a :
			role = a
			break

	async for log in before.guild.audit_logs(limit=10):
		if log.action.name == "member_role_update":
			if log.user == before :
				await channel.send(f"Dit {before.mention}, tu peux arrêter de t'auto-role **{role}** stp? <a:Iseeyou:1062129234908291093>")
				return

@client.command()
@commands.cooldown(1, 3, commands.BucketType.user)
async def ping(ctx):
	await ctx.send(f"🏓 **PONG!** je t'ai renvoyé la balle en `{round(client.latency*1000)}`_ms_ !")

########################################### COMMANDS ###########################################

@client.command(aliases=["confess"])
@commands.dm_only()
async def confession(ctx: Context, *, txt=None):
	if txt is None:
		await ctx.channel.send("Je n'ai aucune confession à partager")
		return

	E = discord.Embed(
		title="New confession",
		description=txt, 
		color=discord.Colour.from_rgb(88, 101, 242),
		timestamp=dt.datetime.now()
	)
	E.set_footer(text="Anon",icon_url="https://cdn.discordapp.com/attachments/709313685226782751/1049237441053208676/anon.png")
	chan = await client.fetch_channel(1049238520704806912)

	await chan.send(embed=E)
	await ctx.channel.send(embed=discord.Embed(
		title = "Confession envoyée",
		color=discord.Colour.green()
		)
	)


if 1: #cuties' commands
	def cutie(ctx):
		return ctx.guild.get_role(1032357008634032260) in ctx.author.roles or ctx.author.id == 346945067975704577

	@client.command(aliases=["statut"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.check(cutie)
	async def status(ctx:Context, state:str=None):
		await ctx.message.delete()
		if state in ["online", "idle", "dnd","invisible","offline"]:
			await client.change_presence(status=discord.Status(f'{state}'),activity=ctx.guild.me.activity)
		else : 
			await ctx.send("Ce n'est un statut valable, veuillez choisir entre `online`, `idle`, `dnd`, `invisible`, `offline`")


	@client.command(aliases=["activitée","activitee"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.check(cutie)
	async def activity(ctx:Context, typ:str=None, *, text:str=None):
		await ctx.message.delete()
		if typ == None or text == None :
			await ctx.send("Il me manque une info, veuillez préciser `joue`, `écoute`, `regarde` ou `stop`, suivis de son activité, ex : m!activity jouer un jeu",delete_after=60)
			return
		if typ in ["playing","joue"] :
			await client.change_presence(status=ctx.guild.me.status,activity=discord.Game(name=text))
		elif typ in ["watching","regarde"] : 
			await client.change_presence(status=ctx.guild.me.status,activity=discord.Activity(type=discord.ActivityType.watching, name=text))
		elif typ in ["listening","écoute","ecoute"] : 
			await client.change_presence(status=ctx.guild.me.status,activity=discord.Activity(type=discord.ActivityType.listening, name=text))
		elif typ == "stop" :
			await client.change_presence(status=ctx.guild.me.status,activity=discord.Game(name=""))
		else : 
			await ctx.send("activitée non valable, veuillez choisir entre `playing`, `watching`, `listening` ou `stop`")


	@client.command(aliases=["reponse","réponse"])
	@commands.bot_has_permissions(embed_links=True,mention_everyone=True)
	@commands.cooldown(1, 5, commands.BucketType.user)
	@commands.guild_only()
	@commands.check(cutie)
	async def resp(ctx: Context,way:str=None,*,txt:str=None):
		if way == None : 
			await ctx.send("Veuillez préciser une méthode, pour plus d'aide utilisez `!resp help`")
			return
		data = get_data()

		if way.lower() in ["add","new","create"] :
			if txt != None :
				if len(txt.split(",,")) >= 2 < 4 :
					if len(txt.split(',,')) == 3 :
						if txt.split(',,')[2].replace('s','').strip().isnumeric() :
							key, answer, time = txt.split(',,')
							time = int(time.replace('s','').strip())
							if time >= 30 :
								time = 30
							elif time < 0 :
								time = None
						else :
							await ctx.send("Votre troisième position doit être un nombre")
							return
					else : #time var to None
						key, answer = txt.split(",,")
						time = None

					if key.strip() == '' :
						await ctx.send("Votre mot clef ne peut pas être vide")
						return
					if answer.strip() == '' :
						await ctx.send("Votre réponse ne peut pas être vide")
						return

					data["phrases"].append({"mot":key.strip(),"text":answer,"time":time,"id":data["phrasesID"]})
					data["phrasesID"] += 1
					upd_data(data)
					if time == None :
						await ctx.send(f"Nouvelle réponse ajoutée avec succès :\n**Mot clef : **{key}\n**Réponse : **{answer}\n**Aucune suppression**")
					else :
						await ctx.send(f"Nouvelle réponse ajoutée avec succès :\n**Mot clef : **{key}\n**Réponse : **{answer}\n**Temps avant suppression : ** `{time}` secondes")
				else :
					await ctx.send("Vous devez préciser les mot auquels le bot va réagir, suivis de ',,' puis de sa réponse __(Vous pouvez également préciser la durée avant suppression en ajoutant ',, [durée]' à la fin)__")
			else :
				await ctx.send("Vous devez préciser les mot auquels le bot va réagir, suivis de ',,' puis de sa réponse __(Vous pouvez également préciser la durée avant suppression en ajoutant ',, [durée]' à la fin)__")
		elif way.lower() in ["d","del","delete"] :
			if txt != None :
				if txt.isnumeric() :
					for i, val in enumerate(data['phrases']):
						if val["id"] == int(txt) :
							del data['phrases'][i]
							await ctx.send(f"La réponse {txt} a bien été supprimée")
							break
					else : 
						await ctx.send("L'id envoyé ne correspond à aucune réponse, veuillez réessayer")
					upd_data(data)
				else : 
					await ctx.send("L'id de la réponse doit être un chiffre")
			else :
				await ctx.send("Vous devez préciser l'id de la réponse que vous souhaitez supprimer, vous pouvez trouver l'id des réponses via `m!resp list`")

		# un peu comme del 
		elif way.lower() in ["l","list","liste"] :
			pages = int(len(data["phrases"])/25)
			if len(data["phrases"])%25 != 0 :
				pages += 1
			if txt == None or not txt.isnumeric() :
				page = 0
			else :
				page = int(txt) - 1

			if page+1 > pages : #not above last page
				page = pages -1
			elif page < 0 : #not under 0
				page = 0

			E = discord.Embed(title='Liste des phrases et réponses',colour=discord.Colour.random())
			E.set_footer(text=f"Page {page+1} sur {pages}")

			for i in data["phrases"][page*25:(page*25)+25]:
				if i["time"] == None :
					E.add_field(name=f'**{i["id"]}**',value=f'**Mot : **{i["mot"]}\n**Aucune suppression**\n**texte :** {i["text"]}')
				else :
					E.add_field(name=f'**{i["id"]}**',value=f'**Mot : **{i["mot"]}\n**Supprimé après :** {i["time"]}\n**texte :** {i["text"]}')
			await ctx.send(embed=E)
		else : 
			await ctx.send("Veuillez préciser une fonction existante, pour plus d'aide utilisez `m!resp help`")

	@client.command()
	@commands.check(cutie)
	async def avatar(ctx: Context, avatar=None):
		if avatar is None and len(ctx.message.attachments) == 0:
			await ctx.send("Vous devez envoyer un lien ou une image")
			return

		if len(ctx.message.attachments) > 0:
			link = ctx.message.attachments[0].url
		else:
			link = avatar

		try :
			requests.get(link)
			async with aiohttp.ClientSession() as cs:
				async with cs.get(link) as resp:
					File = await resp.content.read()
					await client.user.edit(avatar=File)
		except requests.exceptions.MissingSchema :
			await ctx.send(f"**{ctx.author},** Le lien envoyé n'est pas un lien",delete_after=5)
		except discord.DiscordException: #pense pas que c'est la bonne exception
			await ctx.send(f"**{ctx.author},** Échec du serveur",delete_after=5)
		except ValueError:
			await ctx.send(f"**{ctx.author},** Le format envoyé n'est pas un lien valide",delete_after=5)
		except :
			await ctx.send(f"**{ctx.author},** Le lien envoyé n'est pas un lien valide",delete_after=5)
		finally:
			await ctx.send("Avatar changé avec succès")

	@client.command(aliases=["e"])
	@commands.bot_has_permissions(manage_messages=True,embed_links=True,attach_files=True,add_reactions=True,external_emojis=True,mention_everyone=True)
	@commands.has_permissions(manage_messages=True,attach_files=True)
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.check(cutie)
	async def embed(ctx:Context, sub=None):
		if sub == None : 
			await ctx.send("vous devez précier une option (view, help, create)")
			return
		elif sub.lower() == "view" : 
			embed = discord.Embed(
				title = "__***title***__", 
				description = "_Description,_ [link](https://discordapp.com)",
				colour = discord.Colour.random(),
				timestamp=dt.datetime.now()
			)
			embed.url="https://discordapp.com"
			embed.set_author(name="author", icon_url="https://cdn.discordapp.com/avatars/346945067975704577/a_68711215b0fc9bdbaf4f2701917ef28d.gif?size=1024",url="https://discordapp.com")
			embed.add_field(name="__Field 1__",value="**Value 1**",inline=False)
			embed.add_field(name="~~Field 2~~",value="||Value 2||",inline=True)
			embed.add_field(name="Field 3",value="inline",inline=True)
			embed.add_field(name = "Fiel 4 link",value = "link [here](https://discordapp.com)",inline=False)
			embed.set_image(url="https://cdn.discordapp.com/attachments/709313685226782751/1073699583697375362/file.gif")
			embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/346945067975704577/a_68711215b0fc9bdbaf4f2701917ef28d.gif?size=1024")
			embed.set_footer(text="footer",icon_url="https://cdn.discordapp.com/avatars/346945067975704577/a_68711215b0fc9bdbaf4f2701917ef28d.gif?size=1024")
			await ctx.send(embed=embed)
			return
		elif sub.lower() in ["create","new"]:
			nb = 0
			embed_text = ""
			embed_file = None
			Reactions = []
			def check_embed(m) :
				return m.channel == ctx.channel and m.author == ctx.author and m.content[0] == "+"
			def check_send(m):
				return m.channel == ctx.channel and m.author == ctx.author
			e = discord.Embed(description="\u200B")
			Lembeds = [e]
			await ctx.send(embed=e)
			while 1 :
				e = copy.deepcopy(e)
				nb += 1
				try :
					question = await ctx.send(f"**{ctx.author},**Continuez à personnaliser votre embed avec `+` suivis des modifications que vous souhaitez lui apporter _(10m)_")
					message = await client.wait_for('message',check=check_embed, timeout=600)
				except asyncio.TimeoutError :
					await ctx.send(f"{ctx.author.mention}, Vos 10 minutes sont écoulées, la construction de l'embed est annulée")
					return
				await question.delete()
				try :
					arg = None
					text = None
					arg = simplify(message.content[1:].strip().split(" ",1)[0]).lower()
					text = message.content[1:].strip().split(" ",1)[1]
				except IndexError:
					if arg in ["done","stop","cancel","image","thumbnail","thumb","author_icon","footer_icon","file","fichier","atta","attachment"] : 
						pass
					else : 
						await ctx.send("Vous devez préciser un changement après le type",delete_after=30)
						continue
				if arg == "done" : 
					break
				elif arg in ["stop","cancel"] :
					await ctx.send("embed annulé")
					return


				if 1 : #tous les paramètres
					if arg in ["title","titre"] :
						if text == "///":
							e.title = discord.Embed.Empty
						elif len(text) < 256 :
							e.title = text
						else : 
							await ctx.send(f"Votre titre est trop long, _({len(text)})_ veuillez le diminuer à 256 caractères maximum",delete_after=30)

					elif arg in ["desc","description"] :
						if text == "///":
							e.description = "\u200B"
						else :  
							e.description = text
				
					elif arg in ["couleur","color","colour"] :
						if text == "///":
							e.colour = discord.Embed.Empty
						elif text == "random" :
							color = "0x"
							for i in range(6) :
								color += str(random.choice(["a","b","c","d","e","f",0,1,2,3,4,5,6,7,8,9]))
							e.colour = eval(color)
						else :
							if "#" in text :
								color = text.replace('#','0x')
							else :
								color = '0x'+text
							try : 
								e.colour = eval(color)
							except : 
								await ctx.send("Ce n'est pas une couleur valable, essayez d'envoyer une couleur hex",delete_after=30)

					elif arg in ["date","time","timestamp"] : 
						if text == "on" : 
							e.timestamp = datetime.datetime.now()
						elif text == "off" : 
							e.timestamp = discord.Embed.Empty
					
					elif arg in ["url"] :
						url = text.split()[0]
						if url == "///":
							e.url = discord.Embed.Empty
						else :
							e.url = url

					elif arg == "image" :
						if text == '///' :
							try :
								del e._image
							except AttributeError:
								pass
						else:
							if len(message.attachments) > 0 :
								url = message.attachments[0].url
							else : 
								url = text.split()[0]
							L = [".gif",".png",".jpeg",".jpg",".webp"]
							if re.match(r"^(http|https)://.*\.(gif|png|jpg|jpeg|webp)",url) :
								for i in L :
									if i in url : 
										url=await GetLogLink(url)
										e.set_image(url=url)
							else :
								await ctx.send("Malheureusement, le lien précisé ne semble pas être valable")

					elif arg in ["thumb","thumbnail"] : 
						if text == '///' :
							try : 
								del e._thumbnail
							except AttributeError:
								pass
						else:
							if len(message.attachments) > 0 :
								url = message.attachments[0].url
							elif text != None :
								url = text.split()[0]
							else :
								await ctx.send("Veuillez préciser l'image que vous souhaitez afficher",delete_after=30)
								continue

							L = [".gif",".png",".jpeg",".jpg",".webp"]
							for i in L : 
								if i in url : 
									e.set_thumbnail(url=await GetLogLink(url))

					elif arg == "author" :
						if text == "///" :
							e.set_author(name="",icon_url=e.author.icon_url,url=e.author.url)
						else :
							if len(text) < 256 : 
								e.set_author(name=text,icon_url=e.author.icon_url,url=e.author.url)
							else :
								await ctx.send(f"Votre nom est trop long, _({len(text)})_ veuillez le diminuer à 256 caractères maximum",delete_after=30)

					elif arg == "author_icon" :
						if text == "///" : 
							e.set_author(name=e.author.name,url=e.author.url,icon_url=discord.Embed.Empty)
						else:
							if len(message.attachments) > 0 :
								url = message.attachments[0].url
							else : 
								url = text.split()[0]
							L = [".gif",".png",".jpeg",".jpg",".webp"]
							for i in L : 
								if i in url : 
									e.set_author(name=e.author.name,url=e.author.url,icon_url=await GetLogLink(url))
									break
							else :
								await ctx.send("Le format envoyé ne correspond pas, les formats acceptés sont : `gif`, `png`, `jpg`, `jpeg`, `webp`",delete_after=30)

					elif arg == "author_url" :
						url = text.split()[0]
						if url == "///":
							e.set_author(name=e.author.name,url=discord.Embed.Empty,icon_url=e.author.icon_url)
						else : 
							e.set_author(name=e.author.name,url=url,icon_url=e.author.icon_url)

					elif arg == "field" : 
						if len(text.split()) > 0 and text.split()[0] in ["del","delete"] : 
							if len(text.split()) > 1 :
								if (V := text.split()[1]).isnumeric() and int(V) <= len(e.fields) :
									e.remove_field(int(V)-1)
								else : 
									await ctx.send(f"Il n'y a pas de field **n°{V}**")
							else :
								await ctx.send("Vous devez préciser un field à supprimer")
						else : 
							n = text.split(',,')[0]
							v = text.split(',,')[1:]
							if len(n) > 256 :
								await ctx.send("Le nom ne peut faire faire plus de 256 caractères",delete_after=30)
							if len(',,'.join(v)) > 1024 :
								await ctx.send("La valeur ne peut pas faire plus de 1024 caractères",delete_after=30)
							if v == [] :
								await ctx.send("Vous devez séparer le nom du field et sa valeur de avec `,,`",delete_after=30)
							else : 
								if len(v) >= 2 :
									if v[-1].strip().lower() in ["line","ligne"] : 
										e.add_field(name=n, value =',,'.join(v[:-1]),inline=True)
									else : 
										e.add_field(name=n, value =',,'.join(v),inline=False)
								else:
									e.add_field(name=n, value =',,'.join(v),inline=False)

					elif arg in ["text","texte"] :
						if text == "///" :
							embed_text = ""
						else :
							embed_text = text

					elif arg in ["file","fichier","atta","attachment"] :
						if text == "///" : 
							embed_file = None
						else :
							if len(message.attachments) > 0 :
								Fim = [".gif",".png",".jpg",".jpeg",".webp"]
								Fau = [".mp3",".ogg",".wav",".flac"]
								Fvi = [".mp4",".webm",".mov"]
								LL = [Fim,Fau,Fvi]
								for n in LL :
									for i in n :
										if i in message.attachments[0].filename[-5:] :
											Format = i
											embed_file_url = await GetLogLink(message.attachments[0].url)
											break
									else : 
										continue
									break
								async with aiohttp.ClientSession() as cs:
									async with cs.get(embed_file_url) as resp:
										embed_file = discord.File(io.BytesIO(await resp.content.read()),filename=f"embed_file{Format}")
							else : 
								await ctx.send("Vous devez attacher un fichier pour utiliser cette option",delete_after=30)

					elif arg in ["emoji","emojis","react","reactions","reaction"] :
						if len(text.split()) > 0 and text.split()[0] in ["del","delete","supprimer"] : 
							if len(text.split()) > 1 :
								if (V := text.split()[1]).isnumeric() and 0 < int(V) <= len(Reactions) :
									del Reactions[int(V)-1]
								elif emoji_id := re.search(r'<a?:.*?(\d*?)>',text.split()[1]):
									emoji = client.get_emoji(id=int(emoji_id.group(1)))
									if emoji == None : 
										await ctx.send("Je n'ai pas trouvé l'émoji à supprimer")
									elif emoji in Reactions : 
										del Reactions[Reactions.index(emoji)]
									else : 
										await ctx.send("Cet émoji ne se trouve pas dans la liste")
								else : 
									await ctx.send(f"Il n'y a pas de réaction **n°{V}**")
							else : 
								await ctx.send("Vous devez préciser un émoji à supprimer")
						else :
							conv = EmojiConverter()
							L = text.split()
							if len(L) > 3 :
								L = L[:3]
							for i in L : 
								try : 
									emoji = await conv.convert(ctx, i)
									if emoji not in Reactions :
										Reactions.append(emoji)
								except commands.BadArgument :
									await ctx.send("Émoji introuvable, veuillez réessayer avec l'émoji, son id ou son nom. Et assurez vous que j'y ai accès",delete_after=30)

					elif arg in ["e","embed"] :
						if text.isnumeric() and int(text) < len(Lembeds) :
							e = Lembeds[int(text)]
						else :
							await ctx.send(f"Il n'existe pas d'embed **{text}**",delete_after=30)

					elif arg == "footer":
						if text == "///" : 
							e.set_footer(text="",icon_url=e.footer.icon_url)
						elif len(text) > 70 : 
							await ctx.send(f"Votre footer est trop long, _({len(text)})_ veuillez le diminuer à 70 caractères maximum",delete_after=30)
						else : 
							e.set_footer(text=text,icon_url=e.footer.icon_url)

					elif arg == "footer_icon" :
						if text == "///" : 
							e.set_footer(text=e.footer.text,icon_url=discord.Embed.Empty)
						else:
							if len(message.attachments) > 0 :
								url = message.attachments[0].url
							else : 
								url = text.split()[0]
							L = [".gif",".png",".jpeg",".jpg",".webp"]
							for i in L : 
								if i in url : 
									e.set_footer(text=e.footer.text,icon_url=await GetLogLink(url))

					elif arg == "ctrl" :
						if text == "z":
							if len(Lembeds) > 1 :
								e = Lembeds[-2]

					else : 
						await ctx.send(f"Il n'existe pas de mode **{arg}**",delete_after=30)


				if 1 : #sending the message
					try :
						if embed_file != None :
							async with aiohttp.ClientSession() as cs:
								async with cs.get(embed_file_url) as resp:
									embed_file = discord.File(io.BytesIO(await resp.content.read()),filename=f"embed_file{Format}")
						# ERRORS : prévoir les erreurs + adpater le code
						em = await ctx.send(f"**({nb}).** Votre Embed ressemble à ça :\n{embed_text}",embed=e,file=embed_file)
						Lembeds.append(e)
					except discord.HTTPException as E: #si l'embed fait plus de 6000 caractères
						e = Lembeds[-1]
						nb -= 1
						if "Not a well formed URL." in E.text : 
							await ctx.send("Le lien envoyé n'est pas un lien valable, il foit commencer par `https://` et contenir au moins deux lettres",delete_after=60)
						elif "Embed size exceeds maximum size of 6000" in E.text : 
							await ctx.send("Votre embed est composé de plus de 6000 caractères, veuillez le réduire pour me permettre de l'envoyer",delete_after=60)
						else :
							await ctx.send(text)
						continue

					if len(Lembeds) > 39 :
						await ctx.send(f"attention, vous avez déjà créer **{len(Lembeds)}** embeds, le maximum est **50**. il ne vous reste plus que **{50-n}** embeds",delete_after=60)
						if len(Lembeds) == 51 :
							await ctx.send("Vous avez utilisé vos 50 embeds, la commande est cloturée")
							return

					for emoji in Reactions :
						try :
							await em.add_reaction(emoji=emoji)
						except discord.Forbidden :
							Reactions = Reactions[:-1]
							continue

			while 1 :
				chan = None
				try :
					question = await ctx.send("Votre embed est donc terminé, dans quel salon souhaitez vous l'envoyer ? _(5m)_")
					message = await client.wait_for('message',check=check_send, timeout=300)
				except asyncio.TimeoutError :
					await ctx.send("Vos 5 minutes sont écoulées, la construction de l'embed est annulée",delete_after=60)
					return
				await question.delete()
				conv = TextChannelConverter()
				if message.content[0] == "+" :
					message.content = message.content[1:]
				if message.content == "stop" :
					await ctx.send("Embed anullé avec succès")
				try :
					chan = await conv.convert(ctx, message.content)
				except commands.BadArgument :
					await ctx.send("Le salon n'a pas été trouvé, veuillez mentionner un salon présent sur le serveur",delete_after=60)
					continue 

				else :
					if embed_file != None :
						async with aiohttp.ClientSession() as cs:
							async with cs.get(embed_file_url) as resp:
								embed_file = discord.File(io.BytesIO(await resp.content.read()),filename=f"embed_file{Format}")
					m = await chan.send(f"{embed_text}",embed=e,file=embed_file)
					for emoji in Reactions :
						try :
							await m.add_reaction(emoji=emoji)
						except discord.Forbidden :
							Reactions = Reactions[:-1]
							continue
					break

			await ctx.send("L'Embed a été envoyé avec succès")
		elif sub.lower() in ["help","aide"] :
			E = discord.Embed(colour=discord.Colour.random())
			E.set_author(name=ctx.author,icon_url=await GetLogLink(ctx.author.avatar))
			E.title = "Page d'aide de la commande `embed`"
			E.description = """Vous trouverez ci-dessous une liste de toutes les options que vous pouvez appliquer à votre embed pour le personnaliser autant que possible en le commancant via `m!embed new`
				Vous aurez **un delay de 10m** à chaque fois avant que l'embed s'anulle.
				Certaines commandes ont également des sous commandes, comme pour field et émoji afin de supprimer ce que vous ne désirez plus, pour les autres, utilisez `///` pour vider le contenu.
				Vous pouvez voir à quoi ressemble un embed entièrement remplis via `m!embed view`"""
			E.description += "\n\n**cooldown** : `60`s\n**alias** : 'e', 'embed'"
			E.add_field(name="**Forme globale**",value="```md\n[titre](texte, url possible)\n[url](url du titre)\n[description](url possible via [nom](url) )\n[image](png, jpg, jpeg, webp, gif)\n[thumbnail](png, jpg, jpeg, webp, gif)\n[color](code couleur en hex/'random')```",inline=False)
			E.add_field(name="**Author**",value="```md\n[author](texte, url possible)\n[author_url](lien de l'author)\n[author_icon](png, jpg, jpeg, webp, gif)```",inline=False)
			E.add_field(name="**Footer**",value="```md\n[footer](texte simple)\n[footer_icon](png, jpg, jpeg, webp, gif)```",inline=False)
			E.add_field(name="**Fields**",value="```md\n[field](texte,,suite)\n[field del](valeur du field à delete)```",inline=False)
			E.add_field(name="**Autres**",value="```md\n[timestamp](on/off)\n[text](ajouter du texte hors embed)\n[file](ajoutr un fichier)\n[émoji](ajoute des émojis à l'embed)\n[émoji del](émoji à supprimer)\n[embed](ID de l'embed pour y retourner)\n[ctrl z](annuler une action)```",inline=False)
			E.add_field(name="**Pour finir**",value="```md\n[done](finir l'embed)\n[stop](anulle l'embed)```")
			await ctx.send(embed=E)
		else : 
			await ctx.send(f"**{sub}** n'est pas une sous commande existante")

if 1: #tetrio stuff
	@tree.command(description="Connect your discord account to your Tetrio profile")
	@discord.app_commands.describe(name="Your Tetrio username")
	async def register(inter : discord.Interaction, name: str):
		data = get_data("tetris")

		if str(inter.user.id) in data.keys():
			await inter.response.send_message(f"Vous avez déjà connecté votre compte", ephemeral=True)
			return


		name = nospecial(name.lower())
		if name in data.values():
			await inter.response.send_message("Ce profil est déjà connecté à un compte discord", ephemeral=True)
			return


		Tdata = requests.get(f"https://ch.tetr.io/api/users/{name}").json()
		if not Tdata['success']:
			await inter.response.send_message(f"L'utilisateur {name.upper()} n'existe pas", ephemeral=True)
			return

		data[str(inter.user.id)] = name

		upd_data(data, "tetris")

		await inter.response.send_message(f"Vous avez bien été connecté au compte {name.upper()}")


	@tree.command(name="profile", description="Shows the Tetrio profile of a user",)
	@discord.app_commands.describe(user="The user's profile you want to see")
	async def profile(inter: discord.Interaction, user:str=None):
		if user is None:
			user = str(inter.user.id)


		for user_id in get_data("tetris").keys():
			if user == user_id:
				break
		else:
			await inter.response.send_message("Vous n'avez pas sélectionné une personne valide", ephemeral=True)
			return

		await inter.response.defer()

		try:
			name = get_data("tetris")[user_id]
		except KeyError:
			await inter.followup.send("Vous n'avez pas encore connecté votre compte", ephemeral=True)
			return
		
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
			await inter.response.send_message("Malheureusement une erreur est survenue sur le serveur, veuillez réessayer plus tard")
			return

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
			E.set_thumbnail(url=await GetLogLink(f"https://tetr.io/user-content/avatars/{data['data']['user']['_id']}.jpg?rv={data['data']['user']['avatar_revision']}"))
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

	@profile.autocomplete("user")
	async def user_autocomplete(inter: discord.Interaction, current:str) -> List[app_commands.Choice[str]]:
		return [app_commands.Choice(name=client.get_user(int(user_id)).name, value=str(user_id)) for user_id in get_data("tetris").keys()]


	@tree.command(description="Shows the rank, 40L and blitz leaderboards")
	async def leaderboard(inter: discord.Interaction):
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
				await inter.response.send_message("Malheureusement une erreur est survenue sur le serveur, veuillez réessayer plus tard")
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


client.run(token)