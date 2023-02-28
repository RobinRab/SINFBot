import discord
from discord import app_commands
from discord.ext import commands

from utils import is_cutie, get_data, upd_data

class Resp(app_commands.Group):
	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.command(description="Adds a new response to the bot")
	@app_commands.describe(
		key="The key word to trigger the response",
		resp="The response to send",
		time= "The time before the response is deleted (in seconds, max 30)"
	)
	async def add(self, inter:discord.Interaction,*, key:str, resp:str, time:int=None):
		data = get_data()

		if time is not None :
			if time >= 300 :
				time = 300
			elif time < 0 :
				time = None

		data["phrases"].append({"mot":key.strip(),"text":resp,"time":time,"id":data["phrasesID"]})
		data["phrasesID"] += 1

		upd_data(data)

		if time == None :
			await inter.response.send_message(f"Nouvelle réponse ajoutée avec succès :\n**Mot clef : **{key}\n**Réponse : **{resp}\n**Aucune suppression**")
		else :
			await inter.response.send_message(f"Nouvelle réponse ajoutée avec succès :\n**Mot clef : **{key}\n**Réponse : **{resp}\n**Temps avant suppression : ** `{time}` secondes")


	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.command(description="Removes a response from the bot")
	@app_commands.describe(id="The id of the response to remove")
	async def delete(self, inter:discord.Interaction, id:int):
		data = get_data()

		for i, val in enumerate(data['phrases']):
			if val["id"] == id :
				del data['phrases'][i]
				await inter.response.send_message(f"La réponse {id} a bien été supprimée")
				break
		else : 
			await inter.response.send_message("L'id envoyé ne correspond à aucune réponse, veuillez réessayer")
		upd_data(data)


	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.command(description="Lists all the responses of the bot")
	@app_commands.describe(page="The page to display, default is 1")
	async def list(self, inter:discord.Interaction, page:int=None):
		data = get_data()

		pages = int(len(data["phrases"])/25)
		if len(data["phrases"])%25 != 0 :
			pages += 1

		if page is None :
			page = 0
		else :
			page -= 1

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
		await inter.response.send_message(embed=E)


async def setup(bot:commands.Bot):
	bot.tree.add_command(Resp(name="resp",description="automatic responses gestion"))
