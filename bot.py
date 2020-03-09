import discord
import asyncio
from pyosu import OsuApi
import random
import os
import pyosu
from discord.ext import commands

prefix = '!'

get_api = open("apis.txt", "r")
apis = get_api.readlines()
token = apis[1]
api = OsuApi(apis[0][:-1])
bot = commands.Bot(commands.when_mentioned_or(prefix))


def count_notes(player_score): # player score is a list with user_recent
    notes = 0
    notes += player_score.count300
    notes += player_score.count50
    notes += player_score.count100
    notes += player_score.countmiss
    notes += player_score.countkatu
    notes += player_score.countgeki
    
    return notes


def calculate_acc(beatmap, gamemode):
    user_score = 0.0
    unscaled = 1.0

    if gamemode == '0': # std

        '''   full score:  '''
        unscaled = float(beatmap.count300)
        unscaled += float(beatmap.count100)
        unscaled += float(beatmap.count50)
        unscaled += float(beatmap.countmiss)
        unscaled *= 300
        
        ''' user score '''
        
        user_score = float(beatmap.count300) * 300.0
        user_score += float(beatmap.count100) * 100.0
        user_score += float(beatmap.count50) * 50.0
    
    elif gamemode == '1': # don't remember
        '''   full score:  '''
        unscaled = float(beatmap.count300)
        unscaled += float(beatmap.count100)
        unscaled += float(beatmap.countmiss)
        unscaled *= 300
        
        ''' user score '''
        
        user_score = float(beatmap.count300) * 1.0
        user_score += float(beatmap.count100) * 0.5
        user_score *= 300
       
       
       
    elif gamemode == '2': # tezn ie pamietam
        '''   full score:  '''
        unscaled = float(beatmap.count300)
        unscaled += float(beatmap.count100)
        unscaled += float(beatmap.count50)
        unscaled += float(beatmap.countkatu)
        unscaled += float(beatmap.countmiss)
        
        ''' user score '''
        
        user_score = float(beatmap.count300) * 300.0
        user_score += float(beatmap.count100) * 100.0
        user_score += float(beatmap.count50) * 50.5
        
        
    elif gamemode == '3': # mania
        '''    full score:   '''
        unscaled = float(beatmap.count300)
        unscaled += float(beatmap.count100)
        unscaled += float(beatmap.count50)
        unscaled += float(beatmap.countgeki)
        unscaled += float(beatmap.countkatu)
        unscaled += float(beatmap.countmiss)
        unscaled *= 300
        
        '''   user score: '''
        user_score = float(beatmap.count300) * 300.0
        user_score += float(beatmap.count100) * 100.0
        user_score += float(beatmap.count50) * 50.0
        user_score += float(beatmap.countgeki) * 300.0
        user_score += float(beatmap.countkatu) * 200.0

    return round((float(user_score)/float(unscaled)) * 100.0, 2)
    

def calculate_mania_pp(beatmap, player_score):
    p_flag = 0
    mods = get_mods(player_score.enabled_mods)

    multiplier = 0.8
    for mod in mods:
        if mod == "NF":
            multiplier *= 0.9
        if mod == "EZ":
            multiplier *= 0.5
        if mod == "DT":
            multiplier *= 2.3

    score = player_score.score
    od = beatmap.diff_overall
    note_count = count_notes(player_score)
    stars = beatmap.difficultyrating

    for mod in mods:
        if mod == "EZ" or mod == "NF" or mod == "HT":
            score *= 0.5

    hit300_range = float(34 + 3 * (min(10.0, max(0.0, 10-od))))
    
    strain_value = float((5 * max(1.0, stars / 0.2) - 4) ** 2.2 / 135 * (1 + 0.1 * min(1.0, note_count/1500)))
    
    if score <= 500000: # WP
        # strain_value = 0
        p_flag = 1
        acc = calculate_acc(player_score, "3")
        if acc > 99:
            score = 950000
        elif acc > 95:
            score = 850000
        elif acc > 91:
            score = 750000
        else:
            score = 650000
    if score <= 600000:
        strain_value *= ((score - 500000) / 100000 * 0.3)
        
    elif score <= 700000:
        strain_value *= (0.3 + (score - 600000) / 100000 * 0.25)
        
    elif score <= 800000:
        strain_value *= (0.55 + (score - 700000) / 100000 * 0.20)
        
    elif score <= 900000:
        strain_value *= (0.75 + (score - 800000) / 100000 * 0.15)
        
    else:
        strain_value *= (0.75 + (score - 900000) / 100000 * 0.1)
    
    acc_value = float(max(0.0, 0.2 - ((hit300_range - 34) * 0.006667)) * strain_value * (max(0, score - 960000) / 40000)
                      ** 1.1)



    pp_value = ((strain_value ** 1.1) + (acc_value ** 1.1)) ** (1 / 1.1) * multiplier

    if pp_value < 0:
        pp_value = 0
    return round(pp_value, 2)
    
    
def get_username(discord_name):
    islinked = 0
    f = open("Gracze.txt", "r")
    f_line = f.readlines()
    for x in f_line:
        z = x.split('*')
        x = z[1][:-1]
        if str(x) == str(discord_name):
            islinked = 1
            z = z[0]
            break
    if islinked == 1:
        return (z)
    else:
        return ("0")


async def user_stats():
    user_data = await api.get_user('wojciooo')
    print(str(user_data.playcount) + str(user_data.accuracy) + str(user_data.country) + str(user_data.pp_country_rank)
          + str(user_data.pp_rank) + str(user_data.username))


async def user_recent(username, mod):
    recent = await api.get_user_recent(username, mod)
    return recent


async def welcoming_message(user):
    bests = await api.get_user_bests(user, mode=0, type_str='string', limit=1)
    mapname = await api.get_beatmap(beatmap_id=bests[0].beatmap_id)
    return mapname.creator + ' ' + mapname.title + ' ' + str(bests[0].pp) + 'pp'


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.event
async def on_guild_join(guild):
    if guild.system_channel is not None:
        await guild.system_channel.send("Hello dear friends :))))))")
    elif guild.rules_channel is not None:
        await guild.rules_channel.send("Hello dear friends :))))))")
'''
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(f'Hi {member.name}, welcome to my Discord server!')
'''


@bot.command(name='hello', help='no przywita cie przyzwoicie a:)')
async def hello(ctx):
    if ctx.message.author == bot.user:
        return
    else:
        best_play = await welcoming_message(str(ctx.message.author.name))
        if str(ctx.message.author) == 'wojciooo#1522':
            await ctx.message.channel.send(
                'Hello! ' + f'{ctx.message.author.mention} ' + 'your best score is: ' + f'{best_play}, wow that\'s a GREAT job!')
        else:
            await ctx.message.channel.send(
                'Hello! ' + f'{ctx.message.author.mention} ' + 'your best score is: ' + f'{best_play} what a farm :(')


# Link an User command:
@bot.command(name='link',
             help='!link username  :-Powiazuje gracza z nazwa w osu :)')
async def link(ctx, username: str):
    flag = 0
    f = open("Gracze.txt", "r")
    f_line = f.readlines()
    for x in f_line:
        z = x.split('*')
        z = z[1][:-1]
        if str(ctx.message.author) == str(z):
            await ctx.message.channel.send(
                'juz zlinkowales konto uzyj !unlink aby odlinkowac :)')
            flag = 1
            break
    f.close()
    f = open("Gracze.txt", "a+")
    if flag == 0:
        f.write(f'{username}*{ctx.message.author}\n')
        await ctx.message.channel.send(
            'Gratuluje byczku od teraz mozesz nie wpisywac nicknamu przy komendach')
    f.close()


@bot.command(name='unlink', help='!unlink  := usuwa polaczenie nicku z graczem')
async def unlink(ctx):
    flag = 0
    f = open("gracze.txt", "r")
    f_line = f.readlines()
    f = open("gracze.txt", "w")
    for line in f_line:
        splitted = line.split('*')
        if splitted[1][:-1] != str(ctx.message.author):
            f.write(line)
        else:
            flag = 1
    if flag == 1:
        await ctx.message.add_reaction('\U0001F44D')
    if flag == 0:
        await ctx.message.channel.send("You don't have any linked accounts :(")



@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        if str(error.param)[:-5] == "username":
            await ctx.message.channel.send("Wrong syntax, use: !link username")


@bot.command(name='stary_gracz', help='Posluchaj no slow starego dobrego gracza')
async def stary_gracz(ctx):
    f = open("stary.txt", "r+")
    old_player_quotes = f.readlines()
    f.close()
    response = random.choice(old_player_quotes)
    await ctx.message.channel.send(response)


def get_mods(mode):  #taken from pyttanko
    mode = int(mode)
    mods = []
    if mode & 1 << 0:   mods.append('NF')
    if mode & 1 << 1:   mods.append('EZ')
    if mode & 1 << 3:   mods.append('HD')
    if mode & 1 << 4:   mods.append('HR')
    if mode & 1 << 5:   mods.append('SD')
    if mode & 1 << 9:   mods.append('NC')
    elif mode & 1 << 6: mods.append("DT")
    if mode & 1 << 7:   mods.append('RX')
    if mode & 1 << 8:   mods.append('HT')
    if mode & 1 << 10:  mods.append('FL')
    if mode & 1 << 12:  mods.append('SO')
    if mode & 1 << 14:  mods.append('PF')
    if mode & 1 << 15:  mods.append('4 KEY')
    if mode & 1 << 16:  mods.append('5 KEY')
    if mode & 1 << 17:  mods.append('6 KEY')
    if mode & 1 << 18:  mods.append('7 KEY')
    if mode & 1 << 19:  mods.append('8 KEY')
    if mode & 1 << 20:  mods.append('FI')
    if mode & 1 << 24:  mods.append('9 KEY')
    if mode & 1 << 25:  mods.append('10 KEY')
    if mode & 1 << 26:  mods.append('1 KEY')
    if mode & 1 << 27:  mods.append('3 KEY')
    if mode & 1 << 28:  mods.append('2 KEY')
    
    return mods

def determine_mode(mode):
    if mode == "-m":
        mode = "3"
    if mode == "-t":
        mode = "1"
    if mode == "-c":
        mode = "2"
    if mode == "0" or mode == "-s":
        mode = "0"
    return mode


async def find_beatmap(beatmap_id):
    beatmap = await api.get_beatmap(beatmap_id=beatmap_id)
    return beatmap




@bot.command(name='rs', help="!rs (optional: nickname -mode (m = mania, t = taiko, c = ctb, works without "
                             "nickname for linked ppl, default mode is standard")
async def rs(ctx, mode: str = "0", nickname: str = "xd"):
    error_f = 0
    prediction_f = 0
    pp = 0
    if get_username(ctx.message.author) != "0" and nickname == "xd":
        nickname = get_username(ctx.message.author)
        mode = determine_mode(mode)
        x = await user_recent(nickname, mode)
        if x is None:
            error_f = 1
    else:
        mode = determine_mode(mode)
        x = await user_recent(nickname, mode)
        if x is None:
            error_f = 1

    if error_f == 0:

        mods = get_mods(x.enabled_mods)
        if not mods:
            mods = []
            mods.append('NM')
        z = ""
        for mod in mods:
            z += mod + ", "

        mapa = await find_beatmap(x.beatmap_id)

        if mode == "3":
            pp = calculate_mania_pp(mapa, x)
            if x.score <= 500000:
                pp = "Predicted pp: (work in progress)  " + str(pp)


        acc = calculate_acc(x, mode)

        await ctx.message.channel.send(nickname + ": " + str(mapa.artist) + " - " + str(mapa.title) + " [" +
                                   str(mapa.version) + "] +" + str(z)[:-2] + " " + str(acc) + "%  -  " + str(pp) + "pp")
    else:
        await ctx.message.channel.send("Brak ostatnio zagranych map (at least on chosen gamemode) ;(")


bot.run(token)
