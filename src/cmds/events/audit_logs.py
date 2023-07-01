import discord
from discord.ext import commands

import datetime as dt

from utils import GetLogLink, UnexpectedValue
from settings import GENERAL_ID

class AuditLog(commands.Cog):
	def __init__(self, bot:commands.Bot):
		self.bot : commands.Bot = bot

	@commands.Cog.listener()
	async def on_audit_log_entry_create(self, entry:discord.AuditLogEntry):
		#!! command disabled for now
		return 
		# check is a role update
		if entry.action.name != "member_role_update":
			return

		# check are the same
		if entry.user != entry.target:
			return

		# find deleted role(s) in list:
		roles = [role for role in entry.before.roles if role not in entry.after.roles]
	
		# no roles were removed
		if len(roles) == 0:
			return

		# timeout and re-add roles:
		until = dt.datetime.now().astimezone() + dt.timedelta(minutes=5)

		if not isinstance(entry.user, discord.Member):
			raise UnexpectedValue("entry.user not a discord.Member")

		try: 
			await entry.user.timeout(until, reason="auto-removed roles")
			await entry.user.add_roles(*roles, reason="Re-added roles after timeout")
		except: 
			return

		# send message
		E = discord.Embed(title="Tentative de retrait de rôle", color=discord.Color.red())
		E.set_author(name=entry.user, icon_url=await GetLogLink(self.bot,str(entry.user.display_avatar)))
		E.description = ', '.join(role.mention for role in roles)

		chan = self.bot.get_channel(GENERAL_ID)
		if not isinstance(chan, discord.TextChannel):
			raise UnexpectedValue("chan not found")

		await chan.send(embed=E)



async def setup(bot:commands.Bot):
	await bot.add_cog(AuditLog(bot))