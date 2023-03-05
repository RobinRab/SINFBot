import discord
from discord import app_commands
from discord.ext import commands

from typing import Optional
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
	async def add(self, inter:discord.Interaction, key:str, resp:str, time:Optional[int]):
		data : dict = get_data()

		if time is not None :
			if time >= 300 :
				time = 300
			elif time < 0 :
				time = None

		data["phrases"].append({"mot":key.strip(),"text":resp,"time":time,"id":data["phrasesID"]})
		data["phrasesID"] += 1

		upd_data(data)

		if time == None :
			await inter.response.send_message(f"New response successfully added :\n**Key : **{key}\n**Resp : **{resp}\n**No Deletion**")
		else :
			await inter.response.send_message(f"New response successfully added :\n**Key : **{key}\n**Resp : **{resp}\n**Deletion after : ** `{time}`s")


	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.command(description="Removes a response from the bot")
	@app_commands.describe(id="The id of the response to remove")
	async def delete(self, inter:discord.Interaction, id:int):
		responses : list = get_data("phrases")

		for i, val in enumerate(responses):
			if val["id"] == id :
				del responses[i]
				await inter.response.send_message(f"The response n°{id} was successfully deleted")
				break
		else : 
			await inter.response.send_message("The specified ID matches no response")
		upd_data(responses)


	@app_commands.guild_only()
	@app_commands.check(is_cutie)
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	@app_commands.command(description="Lists all the responses of the bot")
	@app_commands.describe(page="The page to display, default is 1")
	async def list(self, inter:discord.Interaction, page:int=None):
		responses : list = get_data("phrases")

		pages = int(len(responses)/25)
		if len(responses)%25 != 0 :
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

		for i in responses[page*25:(page*25)+25]:
			if i["time"] == None :
				E.add_field(name=f'**{i["id"]}**',value=f'**Key : **{i["mot"]}\n**No deletion**\n**Response :** {i["text"]}')
			else :
				E.add_field(name=f'**{i["id"]}**',value=f'**Key : **{i["mot"]}\n**Deletion after :** {i["time"]}s\n**Response :** {i["text"]}')
		await inter.response.send_message(embed=E)


async def setup(bot:commands.Bot):
	bot.tree.add_command(Resp(name="resp",description="Automatic responses gestion"))
