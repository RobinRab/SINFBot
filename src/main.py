
import discord
from discord.ext import commands
print(discord.__version__)

import settings
from utils import log
from cmds.stuff.birthday import Birthday 

intents = discord.Intents.all()

bot = commands.Bot(
	command_prefix=commands.when_mentioned_or(settings.BOT_PREFIX),
	case_insensitive=True,
	help_command=None,
	intents=intents,
	strip_after_prefix=True
)
bot.description = "" # not synced


@bot.event
async def on_ready():
	log("INFO", f"Logged in as {bot.user}")
	for ext in settings.extensions:
		await bot.load_extension(ext)
		log("INFO", f"{ext} loaded ")

	Bd = Birthday(bot)
	Bd.birthdays_loop.start()

	print("SINF illégal family bot online\n")

# #only allow app_commands in bot channel
# async def interaction_check(inter:discord.Interaction, /) -> bool:
# 	if isinstance(inter.guild, discord.Guild) and isinstance(inter.user, discord.Member):
# 		cutie = inter.guild.get_role(settings.CUTIE_ID)
# 		assert isinstance(inter.channel, discord.TextChannel)
# 		if inter.channel.id != settings.BOT_CHANNEL_ID: 
# 			if not cutie in inter.user.roles and inter.user.id != settings.OWNER_ID:
# 				return False
# 	return True

# bot.tree.interaction_check = interaction_check

#only allow commands in bot channel
@bot.check
def check_commands(ctx:commands.Context) -> bool:
	if isinstance(ctx.guild, discord.Guild) and isinstance(ctx.author, discord.Member):
		cutie = ctx.guild.get_role(settings.CUTIE_ID)
		assert isinstance(ctx.channel, discord.TextChannel)
		if ctx.channel.id != settings.BOT_CHANNEL_ID: 
			if not cutie in ctx.author.roles and ctx.author.id != settings.OWNER_ID:
				return False
	return True


@bot.hybrid_command(name="ping", with_app_command=True, description="Pings the bots!")
async def ping(ctx:commands.Context):
	await ctx.reply(f"🏓 **PONG!** je t'ai renvoyé la balle en `{round(bot.latency*1000)}`_ms_ !")

bot.run(settings.DISCORD_API_TOKEN)