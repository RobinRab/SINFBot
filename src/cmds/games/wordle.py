import discord
from discord import app_commands
from discord.ext import commands, tasks

import csv
import random
import asyncio
from typing import Literal, Dict

import time

from settings import DATA_DIR, GUILD_ID
from utils import get_data, upd_data, get_value, get_belgian_time, new_user, GetLogLink, simplify, is_member, get_user_data,UserAccount #, embed_roulette
                                                                                                         #Roulette is comming 👀

#Executes before wordle
async def who(inter: discord.Interaction):
    return inter.user.id == 627431499960156161 or inter.user.id == 411881842439094272

class Wordle(commands.Cog):
    active_games = {}

    def __init__(self, bot):
        self.bot : commands.Bot = bot
    
    async def get_data_wordle(self, inter:discord.Interaction) -> dict:
        # check if account exists
        try :
            user_data : dict = get_data(f"games/users/{inter.user.id}")
            # create wordle if never played
            if "wordle_en" not in user_data:
                user_data["wordle_en"] = {}
                user_data["wordle_fr"] = {}
                user_data["wordle_de"] = {}
                user_data["wordle_sp"] = {}
                upd_data(user_data, f"games/users/{inter.user.id}")
        except :
            user_data = new_user()
            upd_data(user_data, f"games/users/{inter.user.id}")

        return user_data

    @app_commands.command(description="Play today's wordle!")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.guild_only()
    @app_commands.describe(language = "The language you choose")
    async def wordle(self, inter: discord.Interaction, language:Literal["English", "French", "German", "Spanish"]):

        user_data = await self.get_data_wordle(inter)
        user_id = inter.user.id
        
        l_abbr = language[:2].lower()
            
        current_w = f"wordle_{l_abbr}"
        guess_list = get_words()[f"guess_list_{l_abbr}"]
        wordle_word : str = get_data(f"games/todays_word_{l_abbr}")

        E = discord.Embed()
        E.set_author(name=inter.user.name, icon_url = await GetLogLink(self.bot, inter.user.display_avatar.url))

        if user_data["wordle_ban"] > 0:
            await inter.response.send_message(f"You are banned from playing Wordle for {user_data['wordle_ban']} more days.", ephemeral=True)
            return

        #Compute current state of the game
        if user_id in Wordle.active_games and Wordle.active_games[user_id]:
            await inter.response.send_message("You are already playing Wordle.", ephemeral=True)
            return

        try:
            result_displayed : int = user_data[f"wordle_stats_{l_abbr}"]["todays_w_results_shown"]
        except:
            await inter.response.send_message("Connection failure, please try again", ephemeral=True)

        #Check if results shown have to be ephemeral or not
        if result_displayed:
            already_guessed = ""

            for word in user_data[current_w]:
                spaced_word = ""
                for letter in word[1:].upper():
                    spaced_word += f"{letter:^4}"

                already_guessed += "# " + spaced_word + "\n" + space(user_data[current_w][word])+"\n"
            await inter.response.send_message(f"You already played today, but here are your stats for today \nSee you tomorrow!", ephemeral=True)
            return await inter.followup.send(f"{already_guessed}", ephemeral=True)

        try:
            current_number_guess = len(user_data[current_w])
        except:
            await inter.response.send_message("Connection failure, try again", ephemeral=True)
            
        #User got cursed by roulette
        guess_limit = 6
        # if "wordle_guess_reduced" in user_data["effects"]:
        #     guess_limit = 5

        if current_number_guess == 0 and not guess_limit == 5:
            await inter.response.send_message(f'''Welcome to {language} wordle!\nWrite your guess to start playing. 
            \nType 'stop' to *pause* the game, call the function again to *restart*.''')

        elif current_number_guess == 0 and guess_limit == 5:
            #E_roulette = await embed_roulette(self, inter, E)
            #E_roulette.description = f"Welcome to {language} wordle! Something looks strange... You only have 5 guesses today!!"
            #await inter.followup.send(embed = E_roulette, ephemeral=True)
            print("Currently impossible")

        else:
            already_guessed = ""

            for word in user_data[current_w]:
                spaced_word = ""
                for letter in word[1:].upper():
                    spaced_word += f"{letter:^4}"

                already_guessed += "# " + spaced_word + "\n" + space(user_data[current_w][word])+"\n"
            if guess_limit == 6:
                await inter.response.send_message( f"Welcome back to {language} wordle! Here are the words you already guessed : ", ephemeral = True)
            else:
                await inter.response.send_message( f"Welcome back to {language} wordle! Something looks strange... You only have 5 guesses today!!\nHere are the words you already guessed : ", ephemeral = True)
            await inter.followup.send(f"{already_guessed}", ephemeral = True)
            await inter.followup.send("Type 'stop' to pause the game.", ephemeral = True)

        has_won = False
        #The user is now playing, updates the dictionnary to prevent multiple '/wordle'
        Wordle.active_games[user_id] = True

        #The user has 5 or 6 chances (for roulette)
        while current_number_guess<guess_limit:

            def check(message: discord.Message):
                return message.author == inter.user and message.channel == inter.channel
            try:
                #Waiting for the user's response
                message = await self.bot.wait_for("message", timeout = 180, check = check)
            except asyncio.TimeoutError:
                # The user is not playing anymore
                Wordle.active_games[user_id] = False 
                return await inter.followup.send("See you later", ephemeral=True)
            
            guess_word = simplify(message.content.lower())
            several_instances = False
            try:
                await message.delete()
            except:
                #in case two instances of wordle are launched at the same time
                several_instances = True
            if several_instances:
                return await inter.followup.send(f"You launched two instances of wordle at the same time, you are already playing wordle", ephemeral=True)

                       #In case the person wants to stop playing
            if guess_word == "stop":
                # The user is not playing anymore
                Wordle.active_games[user_id] = False
                return await inter.followup.send("See you later", ephemeral=True)
                
            #Word has to be a five letter word
            if len(guess_word) != 5:
                await inter.followup.send("This is not a five letter word", ephemeral=True)
                continue
            
            #Word not int the list
            elif guess_word not in guess_list and guess_word != wordle_word: 
                await inter.followup.send("This word is not in the list", ephemeral=True)
                continue
            #Gets the colors corresponding to the word and print them
            spaced_word = ""
            for letter in guess_word.upper():
                spaced_word += f"{letter:^4}"

            colors = color_function(wordle_word, guess_word)
            already_guessed = "# " + spaced_word + "\n" + space(colors)+"\n"

            await inter.followup.send(f"{already_guessed}", ephemeral=True)
            
            user_data[current_w][f"{current_number_guess}{guess_word}"]=colors

            upd_data(user_data[current_w], f"games/users/{inter.user.id}/{current_w}")
            current_number_guess += 1
            
            #The users wins
            if wordle_word == guess_word:
                has_won = True
                todays_colors = ""
                for color in user_data[current_w].values():
                    todays_colors += color + "\n"
                break

        if has_won:
            #Updates the roses of the user
            user_data = await self.get_data_wordle(inter)
            value = int(get_value(user_data)//2)
            user_data["roses"] += value
            user_data["ideas"] += 1
            both = False
            #Checks if user finished both English and French wordle to give the bonus idea 💡
            if "🟩🟩🟩🟩🟩" in user_data["wordle_en"].values() and "🟩🟩🟩🟩🟩" in user_data["wordle_fr"].values() and (l_abbr == "fr" or l_abbr == "en"):
                both = True
                user_data["ideas"] += 1

            #Checks if user finished both Spanish and German wordle to give the bonus idea 💡
            if "🟩🟩🟩🟩🟩" in user_data["wordle_sp"].values() and "🟩🟩🟩🟩🟩" in user_data["wordle_ge"].values() and (l_abbr == "sp" or l_abbr == "ge"):
                both = True
                user_data["ideas"] += 1

            upd_data(user_data, f"games/users/{inter.user.id}")

            #Sends the has_won message
            current_number_guess = len(user_data[current_w])
            await inter.followup.send("You won!", ephemeral=True)
            E.description = f"{inter.user.mention} solved today's wordle ({language}) in {current_number_guess} guesses ! \n\n||{todays_colors}||"
            E.add_field(name="Reward", value=f"You won {value} 🌹 {'and 2 💡' if both else 'and 1 💡'}!")
            E.color = discord.Color.green()
            await inter.followup.send(embed = E)
        
        if not has_won:
            todays_colors=""
            for color in user_data[current_w].values():
                todays_colors+=color+"\n"
            await inter.followup.send(f"You lost, the word was **{wordle_word}**", ephemeral=True)
            
            E.description = f"{inter.user.mention} lost {language} wordle today. \n\n||{todays_colors}||"
            E.color = discord.Color.red()
            await inter.followup.send(embed = E)

        
        user_data[f"wordle_stats_{l_abbr}"]["todays_w_results_shown"] = 1
        upd_data(user_data[f"wordle_stats_{l_abbr}"], f"games/users/{inter.user.id}/wordle_stats_{l_abbr}")
        # The user is not playing anymore
        del Wordle.active_games[user_id]

    @app_commands.command(description="Ban someone from wordle")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.check(who)
    @app_commands.guild_only()
    @app_commands.describe(user = "The user to ban", days = "Number of days to ban the user")
    async def wordle_ban(self, inter: discord.Interaction, user : discord.Member, days : int) -> None:
        user_id = user.id

        try: 
            user_data: UserAccount = get_data(f"games/users/{user_id}")
        except:
            E.description = f"{user.mention} has never played"
            E.color = discord.Color.red()
            return await inter.followup.send(embed=E)
        
        user_data["wordle_ban"] = days
        upd_data(user_data, f"games/users/{user_id}")
        E = discord.Embed()
        E.set_author(name=inter.user.name, icon_url = await GetLogLink(self.bot, inter.user.display_avatar.url))
        E.description = f"{user.mention} has been banned from playing Wordle for {days} days."
        E.color = discord.Color.red()
        await inter.response.send_message(embed = E)


#Puts spaces between letters of guessed word and colors
def space(content : str):
    spaced_word = ""
    for letter in content:
        spaced_word += f"{letter:^3}"
    return spaced_word

#Function that creates the lists from the csv
#This csv contains 5-letter words with accents removed
def get_words()-> Dict:
    wordle_data = {"guess_list_en": [], "wordle_list_en": [], "guess_list_fr": [], 
                   "wordle_list_fr": [], "guess_list_ge": [], "wordle_list_ge": [],
                   "guess_list_sp": [], "wordle_list_sp": []}
    with open(DATA_DIR/"wordle_words.csv", "r") as f:
        for i in csv.reader(f, delimiter=','):
            #Because it is the longest column, we don't check the length
            wordle_data["guess_list_en"].append(i[0])
            if len(i[1]) == 5:
                wordle_data["guess_list_fr"].append(i[1].strip())
            if len(i[2]) == 5:
                wordle_data["wordle_list_en"].append(i[2].strip())
            if len(i[3]) == 5:
                wordle_data["wordle_list_fr"].append(i[3].strip())
            if len(i[4]) == 5:
                wordle_data["guess_list_sp"].append(i[4].strip())
                wordle_data["wordle_list_sp"].append(i[4].strip())
            if len(i[5]) == 5:
                wordle_data["guess_list_ge"].append(i[5].strip())
                wordle_data["wordle_list_ge"].append(i[5].strip())

    #guess_list are the words you can guess
    #wordle_list are the words that can be the answer
    return wordle_data

def color_function(wordle_word:str, guess_word:str) -> str:
    dico_occurences : dict[str, int] = {}
    #Dictionnary to check repeated letters
    for letter in wordle_word: 
        if letter not in dico_occurences.keys():
            dico_occurences[letter] = 1
        else:
            dico_occurences[letter] += 1
    colors = ""
    colors_list : list[str] = []

    #Iteration in the words to check the green letters
    for letter_guess, letter_wordle_word in zip(guess_word, wordle_word): 
        if letter_guess == letter_wordle_word: 
            colors_list.append("🟩")
            dico_occurences[letter_guess] -= 1
        else:
            colors_list.append("1")

    for letter_guess, letter_wordle_word, color_test in zip(guess_word, wordle_word, colors_list) : 

        #if it is "1" (not green) -> check if it is yellow or grey
        if color_test == "1": 
            index_1 = colors_list.index("1")

            #check the conditions for a letter to be yellow
            #letter in the words && occurence count check -> yellow
            if letter_guess in wordle_word and dico_occurences[letter_guess] != 0: 
                colors_list[index_1]="🟨"
                dico_occurences[letter_guess] -= 1 
            else:
                colors_list[index_1]="🟥"

    for color in colors_list:
        colors += color

    return colors
    
async def setup(bot:commands.Bot):
    await bot.add_cog(Wordle(bot))

