import discord
from discord.ext import commands
from discord.ext.commands import EmojiConverter, TextChannelConverter

from utils import simplify, GetLogLink

import io
import re
import copy
import random
import asyncio 
import aiohttp
import datetime as dt


class Embed(commands.Cog):
	def __init__(self, bot):
		self.bot : commands.Bot = bot

	@commands.group(aliases=["e"])
	@commands.max_concurrency(1, commands.BucketType.user)
	@commands.guild_only()
	async def embed(self, ctx:commands.Context):
		if ctx.invoked_subcommand is None:
			await ctx.send("You must select an option (view/help/new)", delete_after=5)

	@embed.command()
	async def view(self, ctx:commands.Context):
		embed = discord.Embed(
			title = "__***Title***__", 
			description = "_Description,_ [link](https://discordapp.com)",
			colour = discord.Colour.random(),
			timestamp=dt.datetime.now()
		)
		embed.url="https://discordapp.com"
		embed.set_author(name="Author", icon_url="https://cdn.discordapp.com/avatars/346945067975704577/a_68711215b0fc9bdbaf4f2701917ef28d.gif?size=1024",url="https://discordapp.com")
		embed.add_field(name="__Field 1__",value="**Value 1**",inline=False)
		embed.add_field(name="~~Field 2~~",value="||Value 2||",inline=True)
		embed.add_field(name="Field 3",value="inline",inline=True)
		embed.add_field(name = "Fiel 4 link",value = "Link [here](https://discordapp.com)",inline=False)
		embed.set_image(url="https://cdn.discordapp.com/attachments/709313685226782751/1073699583697375362/file.gif")
		embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/346945067975704577/a_68711215b0fc9bdbaf4f2701917ef28d.gif?size=1024")
		embed.set_footer(text="Footer",icon_url="https://cdn.discordapp.com/avatars/346945067975704577/a_68711215b0fc9bdbaf4f2701917ef28d.gif?size=1024")
		await ctx.send(embed=embed)
		return

	@embed.command(aliases=["create"])
	async def new(self, ctx:commands.Context):
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
				message = await self.bot.wait_for('message',check=check_embed, timeout=600)
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
						e.timestamp = dt.datetime.now()
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
									url=await GetLogLink(self.bot, url)
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
								e.set_thumbnail(url=await GetLogLink(self.bot, url))

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
								e.set_author(name=e.author.name,url=e.author.url,icon_url=await GetLogLink(self.bot,url))
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
										embed_file_url = await GetLogLink(self.bot, message.attachments[0].url)
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
								emoji = self.bot.get_emoji(id=int(emoji_id.group(1)))
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
								e.set_footer(text=e.footer.text,icon_url=await GetLogLink(self.bot, url))

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
				message = await self.bot.wait_for('message',check=check_send, timeout=300)
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


async def setup(bot:commands.Bot):
	await bot.add_cog(Embed(bot))
