import discord 
from discord import app_commands, ui
from discord.ext import commands, tasks

import random
import datetime as dt
from typing import Literal
import asyncio

from settings import BOT_CHANNEL_ID
from utils import get_data, upd_data, GetLogLink, random_avatar, get_belgian_time, embed_roulette
from cmds.games.games import traveler
from cmds.games.gambling import GamblingHelper

class Roulette:
    def __init__(self, bot:commands.Bot):
        self.bot : commands.Bot = bot
        self.GH = GamblingHelper(bot)
    
    async def roulette(self, inter:discord.Interaction, other_user:discord.Member):
        assert inter.guild
        await inter.response.defer()
        
        has_been_answered = False

        E, user_data = await self.GH.check(inter)

        #Free spin used for first use and sunday roll
        class FreeSpin(ui.View):
            def __init__(self):
                super().__init__(timeout=60)
                self.clicked = asyncio.Future()

            @discord.ui.button(label="🎰 Free spin!", style=discord.ButtonStyle.green)
            async def free_spin(self, inter: discord.Interaction, button: ui.Button):
                if not self.clicked.done():
                    self.clicked.set_result(inter)

                button.disabled = True
                await inter.response.edit_message(view=self)
            async def on_timeout(self):
                await self.close()
                
            async def close(self):
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                self.stop()

        #Not enough candies and no free spin
        if user_data["candies"]<1 and user_data["free_sunday_roll"] == 0 and "effects" in user_data:
            E.description = f"{inter.user.mention}, You don't have enough 🍬"
            E.color = discord.Color.red()
            return await inter.followup.send(embed=E)

        try :
            other_user_data : dict = get_data(f"games/users/{other_user.id}")
        except :
            return await inter.followup.send("This user doesn't have an account", ephemeral=True)
        
        if other_user_data==user_data:
            return await inter.followup.send("You can't choose yourself", ephemeral=True)

        #Are those three lines needed ? Url avatar is done previously with 
        #inter.user.display_avatar.url in self.check definition
        url = random_avatar()
        if inter.user.avatar:
            url = inter.user.avatar.url
        E = await embed_roulette(self.bot, inter, E)
        
        E.set_author(name=inter.user.display_name, url = await GetLogLink(self.bot, url))


        #First time using the roulette => free spin
        if "never_played" in user_data["effects"]:
            #never_played removed from json (so the user can't /roulette more than once)
            user_data["effects"].remove("never_played")
            upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")

            E.colour = discord.Colour.gold()
            E.description = f"Welcome to the Roulette, {inter.user.mention}!\n As it's your first time, you get a *free spin*! \n\nYou can use the `help` command to know more about this feature."

            view = FreeSpin()
            msg = await inter.followup.send(embed=E, view=view)
            
            #if wait > 60s, close the view and return
            try:
                await asyncio.wait_for(view.clicked, timeout=60)
            except asyncio.TimeoutError:
                await inter.followup.send(
                    "Are you still here? You can try again later",
                    ephemeral=True
                )
                await view.close()
                await msg.edit(view=view)
                
                #add never_played to json so the user can have a free spin next time
                user_data["effects"].append("never_played")
                upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")
                return

        #The user won a free roulette from another player
        elif "free_roulette" in user_data["effects"]:
            E.description = f"{inter.user.mention} used the roulette! Free roll!"
            await inter.followup.send(embed = E)
            user_data["effects"].remove("free_roulette")
            upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")

        #free sunday roll
        elif user_data["free_sunday_roll"] == 0:
            E.description = f"{inter.user.mention} used the roulette! It costs only one 🍬."
            await inter.followup.send(embed = E)
            upd_data(user_data["candies"]-1, f"games/users/{inter.user.id}/candies")

        else:
            E.colour = discord.Colour.gold()
            E.description = f"{inter.user.mention} used the roulette! Free sunday roll!"
            #free sunday roll to 0 (so the user can't /roulette more than once)
            upd_data(0, f"games/users/{inter.user.id}/free_sunday_roll")

            view = FreeSpin()
            msg = await inter.followup.send(embed=E, view=view)
            try:
                await asyncio.wait_for(view.clicked, timeout=60)
            except asyncio.TimeoutError:
                await inter.followup.send(
                    "Are you still here? You can try again later",
                    ephemeral=True
                )
                #free sunday roll to 1 so the user can have a free spin next time
                upd_data(1, f"games/users/{inter.user.id}/free_sunday_roll")
                await view.close()
                await msg.edit(view=view)
                return


        #consequences + weight (try to keep the total to 100)
        consequences = {
            #positive consequences (user)
            "level_up": 2.5,    
            "tech_up": 4.0,  
            "bank_double": 2.5, 
            "next_gain_x3": 5.0,       
            "next_gain_x10": 2.5, 
            "next_collect_x3": 6.0, 
            "free_flip_when_collect": 6.0,
            "chances_next_bet_x2": 5.0,

            #negative consequences (user)
            "level_down": 2.5,   
            "tech_down": 4.0,          
            "bank_robbery": 3.5,
            "next_gain_/3": 4.5,
            "next_gain_/10": 2.0,
            "fail_next_traveler": 4.0,
            "chances_next_bet_/2": 5.0,

            #other user consequences
            "choose_name_level_up": 3.0,
            "choose_name_level_down": 2.5,
            "tech_up_other_user": 5.0, 
            "tech_down_other_user": 4.0, 
            "next_bet_someone_else": 4.0,
            "free_roulette": 6.0,   

            #other consequences
            "traveler_spawn": 6.5,  
            "change_bet_method": 6.0,
            "next_bet_all": 4.0
        }

        cons = random.choices(list(consequences.keys()), list(consequences.values()))[0]
        has_been_answered = False
        url = random_avatar()

        if cons == "level_up":
            has_been_answered = True
            user_data["level"]+=1
            upd_data(user_data["level"], f"games/users/{inter.user.id}/level")
            E.colour = discord.Colour.green()
            E.description = f"Congratulations you leveled-up to level **{user_data['level']}**!"
            await inter.followup.send(embed=E)
            
        elif cons=="level_down":
            has_been_answered = True
            if user_data["level"]>0:
                user_data["level"]-=1
                upd_data(user_data["level"], f"games/users/{inter.user.id}/level")
                E.colour = discord.Colour.red()
                E.description = f"Haha noob you leveled-down to level **{user_data['level']}**"
                await inter.followup.send(embed=E)
            else:
                # If the user is at level 0 they're not leveled down
                E.colour = discord.Colour.red()
                E.description = f"You didn't level down because you're already level 0..."
                await inter.followup.send(embed=E)

        elif cons=="tech_up":
            has_been_answered = True
            user_data["tech"]+=1
            upd_data(user_data["tech"], f"games/users/{inter.user.id}/tech")
            E.colour = discord.Colour.green()
            E.description = f"Congratulations you upgraded your tech to level **{user_data['tech']}**:gear:!"
            await inter.followup.send(embed=E)

        elif cons=="tech_down":
            has_been_answered = True
            if user_data["tech"]>0:
                user_data["tech"]-=1
                upd_data(user_data["tech"], f"games/users/{inter.user.id}/tech")
                E.colour = discord.Colour.red()
                E.description = f"Haha noob you downgraded your tech to level **{user_data['tech']}**:gear:!"
                await inter.followup.send(embed=E)
            else:
                # If the user is at level 0 they're not teched down
                E.colour = discord.Colour.purple()
                E.description = f"You didn't tech down because you're already level 0..."
                await inter.followup.send(embed=E)

        elif cons=="tech_up_other_user":
            has_been_answered = True
            other_user_data["tech"]+=1
            upd_data(other_user_data["tech"], f"games/users/{other_user.id}/tech")
            E.colour = discord.Colour.green()
            E.description = f"Congratulations you leveled-up {other_user.mention} to level  **{other_user_data['tech']}**:gear:!"
            await inter.followup.send(embed=E)

        elif cons=="tech_down_other_user":
            has_been_answered = True
            if other_user_data["tech"]>0:
                other_user_data["tech"]-=1
                upd_data(other_user_data["tech"], f"games/users/{other_user.id}/tech")
                E.colour = discord.Colour.red()
                E.description = f"Haha, you leveled-down {other_user.mention} to level **{other_user_data['tech']}**:gear:!"
                await inter.followup.send(embed=E)
            else:
                # If the user is at level 0 they're not teched down
                E.colour = discord.Colour.purple()
                E.description = f"{other_user.mention} didn't tech down because they're already level 0..."
                await inter.followup.send(embed=E)

        elif cons == "traveler_spawn":
            has_been_answered = True
            E.colour = discord.Colour.purple()
            E.description = f"Look, there, a traveler!" 
            await inter.followup.send(embed=E)
            bot_channel = await self.bot.fetch_channel(BOT_CHANNEL_ID)
            asyncio.create_task(traveler(bot_channel=bot_channel))
            return 

        # The robber steals the roses in the user's bank and puts it in robber_total
        elif cons == "bank_robbery":
            has_been_answered = True
            value : int = get_data(f"games/users/{inter.user.id}/bank/roses")
            if value<=0:
                E.description = f"{inter.user.mention}, your bank is empty so the robber didn't take you anything"
                E.colour = discord.Colour.purple()
                await inter.followup.send(embed=E)
                return
            robber_money : int = value + get_data(f"games/robber_total")
            upd_data(0, f"games/users/{inter.user.id}/bank/roses")
            upd_data(robber_money, "games/robber_total")
            E.colour = discord.Colour.purple()
            E.description = f"{inter.user.mention} your bank got robbed.\n\nThe Robber got all the money you put in there."
            await inter.followup.send(embed=E)

        elif cons == "bank_double":
            has_been_answered = True
            double_money : int = get_data(f"games/users/{inter.user.id}/bank/roses")
            if double_money<=0:
                E.description = f"{inter.user.mention}, your bank is empty so the roulette couldn't double it :("
                E.colour = discord.Colour.purple()
                await inter.followup.send(embed=E)
                return
            double_money+=double_money
            upd_data(double_money, f"games/users/{inter.user.id}/bank/roses")
            E.colour = discord.Colour.purple()
            E.description = f"{inter.user.mention} your roses in bank got multiplied by two!"
            await inter.followup.send(embed=E)

        elif cons=="choose_name_level_up":
            has_been_answered = True
            other_user_data["level"]+=1
            upd_data(other_user_data["level"], f"games/users/{other_user.id}/level")
            E.colour = discord.Colour.purple()
            E.description = f"Congratulations you leveled-up {other_user.mention} to level **{other_user_data['level']}**!"
            await inter.followup.send(embed=E)

        elif cons=="choose_name_level_down":
            has_been_answered = True
            if other_user_data["level"]>0:
                other_user_data["level"]-=1
                upd_data(other_user_data["level"], f"games/users/{other_user.id}/level")
                E.colour = discord.Colour.purple()
                E.description = f"Haha, you leveled-down {other_user.mention} to level **{other_user_data['level']}**!"
                await inter.followup.send(embed=E)
            else:
                # If the user is at level 0 they're not leveled down
                E.colour = discord.Colour.red()
                E.description = f"{other_user.mention} didn't level down because they're already level 0..."
                await inter.followup.send(embed=E)
        
        #future effects : puts them in the effects list in the json

        elif cons=="next_bet_all":
            user_data["effects"].append("next_bet_all")

        elif cons == "next_gain_x3":
            user_data["effects"].append("next_gain_x3")
            user_data["effects"].append("next_gain")

        elif cons == "next_gain_/3":
            user_data["effects"].append("next_gain_/3")
            user_data["effects"].append("next_gain")

        elif cons == "next_gain_x10":
            user_data["effects"].append("next_gain_x10")
            user_data["effects"].append("next_gain")

        elif cons == "next_gain_/10":
            user_data["effects"].append("next_gain_/10")
            user_data["effects"].append("next_gain")

        elif cons == "next_bet_someone_else":
            other_user_data["effects"].append("next_bet_all")
            upd_data(other_user_data["effects"], f"games/users/{other_user.id}/effects")

        elif cons == "chances_next_bet_x2":
            user_data["effects"].append("chances_next_bet_x2")

        elif cons == "chances_next_bet_/2":
            user_data["effects"].append("chances_next_bet_/2")

        elif cons == "fail_next_traveler":
            user_data["effects"].append("fail_next_traveler")

        elif cons == "change_bet_method":
            user_data["effects"].append("change_bet_method")

        elif cons == "free_flip_when_collect":
            user_data["effects"].append("free_flip_when_collect")

        elif cons == "next_collect_x3":
            user_data["effects"].append("next_collect_x3")

        elif cons == "free_roulette":
            has_been_answered = True
            other_user_data["effects"].append("free_roulette")
            upd_data(other_user_data["effects"], f"games/users/{other_user.id}/effects")
            E.colour = discord.Colour.purple()
            E.description = f"You won a free roulette spin for {other_user.mention}!"
            await inter.followup.send(embed=E)

        if not has_been_answered:
            await inter.followup.send("A random effect has been applied to one of you, wait and see", ephemeral=True)

        upd_data(user_data["effects"], f"games/users/{inter.user.id}/effects")


class Roulette_bis(commands.Cog):
    def __init__(self, bot):
        self.bot : commands.Bot = bot
        self.R = Roulette(bot)

    @app_commands.command(description="Spins the wheel")
    @app_commands.checks.cooldown(1, 1, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    async def roulette(self, inter:discord.Interaction, other_user:discord.Member):
        await self.R.roulette(inter, other_user)

async def setup(bot:commands.Bot):
    await bot.add_cog(Roulette_bis(bot))