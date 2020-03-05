import discord
import asyncio
from pyosu import OsuApi
import random
import os
import pyosu
from discord.ext import commands

prefix = '$'

api = OsuApi('')
bot = commands.Bot(command_prefix='!')


def count_notes(beatmap):
    notes = 0
    notes += beatmap.count300
    notes += beatmap.count50
    notes += beatmap.count100
    notes += beatmap.countmiss
    notes += beatmap.countkatu
    notes += beatmap.countgeki
    
    return notes


def calculate_acc(beatmap, gamemode: int):
    if gamemode == 0: # std
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
    
    elif gamemode == 1: # dont remember
        '''   full score:  '''
        unscaled = float(beatmap.count300)
        unscaled += float(beatmap.count100)
        unscaled += float(beatmap.countmiss)
        unscaled *= 300
        
        ''' user score '''
        
        user_score = float(beatmap.count300) * 1.0
        user_score += float(beatmap.count100) * 0.5
        user_score *= 300
       
       
       
    elif gamemode == 2: # tezn ie pamietam
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
        
        
    elif gamemode == 3: # mania
        '''    full score:   '''
        unscaled = float(beatmap.count300)
        unscaled += float(beatmap.count100)
        unsclaed += float(beatmap.count50)
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

    return (float(user_score)/float(unscaled))* 100.0
    

def calculate_mania_pp(beatmap, player_score):

    multiplier = 0.8
    if mods == "NF":
        multiplier *= 0.9
    if mods == "EZ":
        multipler *= 0.5
        
    mods = decode_mods(beatmap.enabled_mods)
    score = player_score.score
    od = beatmap.diff_overall
    note_count = count_notes(beatmap)
    stars = beatmap.difficultyrating
    if mods == "EZ" or mods== "NF" or mods == "HT":
        score *= 0.5
    hit300_range = 34 + 3 * (min(10, max(0, 10-od)))
    
    strain_value = (5 * max(1, stars / 0.2) - 4) ** 2.2 / 135 * (1 + 0.1 *
    min(1, note_count/1500))
    
    if score <= 50000:
        strain_value=0
    
    elif score <= 600000:
        strain_value *= (((score - 500000) / 100000 * 0.3)
        
    elif score <= 700000:
        strain_value *= (0.3 + (score - 600000) / 100000 * 0.25)
        
    elif score <= 800000:
        strain_value *= (0.55 + (score - 700000) / 100000 * 0.20)
        
    elif score <= 900000:
        strain_value *= (0.75 + (score - 800000) / 100000 * 0.15)
        
    else:
        strain_value *= (0.75 + (score - 800000) / 100000 * 0.15)
    
    acc_value *= max(0, 0.2 - ((hit300_range - 34) * 0.006667)) * strain_value *
    (max(0,score - 960000) / 40000) ** 1.1
    
    PP_value = (strain_value ** 1.1 + acc_value ** 1.1) ** (1 / 1.1) * multiplier
    
    return PP_value
    
    
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
    print(mapname.creator + " " + mapname.title)
    return mapname.creator + ' ' + mapname.title + ' ' + str(bests[0].pp) + 'pp'


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


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
async def link(ctx, username: str, ):
    flag = 0
    f = open("Gracze.txt", "r")
    f_line = f.readlines()
    for x in f_line:
        z = x.split('*')
        z = z[1][:-1]
        print(z)
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


@bot.command(name='stary_gracz', help='Posluchaj no slow starego dobrego gracza')
async def stary_gracz(ctx):
    old_player_quotes = [
        'A juz za stary jestem na to',
        'Po 18 roku zycia to juz sie tylko wolniejszy robisz',
        'Pamietam jak sie mnie jescze pytales na jakim tablecie gram',
        'Tęsknie za 2015...',
        'Kiedys to byly na serio fajne mapy a nie to co tera >:(',
        'Hime Hime',
        'Obama? No pewnie ze znam',
        'Nie no ja na myszce bardzo dlugo gralem, wtedy to sie nie wiedzialo co to jest pp',
        ('Jak ja zaczynalem, to nawet nie wiedzialem co to pp'
         'Po prostu gralem.'
         ),
        'Musialem quitnac bo mnie bolal nadgarstek :(',
        'Granie na relaxie nic nie daje'
    ]

    response = random.choice(old_player_quotes)
    await ctx.message.channel.send(response)


def get_mods(mode):  #taken from pyttanko
    number = int(number)
    mods = []
    if number & 1<<0:   mods.append('NF')
    if number & 1<<1:   mods.append('EZ')
    if number & 1<<3:   mods.append('HD')
    if number & 1<<4:   mods.append('HR')
    if number & 1<<5:   mods.append('SD')
    if number & 1<<9:   mods.append('NC')
    elif number & 1<<6: mods.append('DT')
    if number & 1<<7:   mods.append('RX')
    if number & 1<<8:   mods.append('HT')
    if number & 1<<10:  mods.append('FL')
    if number & 1<<12:  mods.append('SO')
    if number & 1<<14:  mods.append('PF')
    if number & 1<<15:  mods.append('4 KEY')
    if number & 1<<16:  mods.append('5 KEY')
    if number & 1<<17:  mods.append('6 KEY')
    if number & 1<<18:  mods.append('7 KEY')
    if number & 1<<19:  mods.append('8 KEY')
    if number & 1<<20:  mods.append('FI')
    if number & 1<<24:  mods.append('9 KEY')
    if number & 1<<25:  mods.append('10 KEY')
    if number & 1<<26:  mods.append('1 KEY')
    if number & 1<<27:  mods.append('3 KEY')
    if number & 1<<28:  mods.append('2 KEY')
    
    return mods

def determine_mode(mode):
    if mode == "-m":
        mode = "3"
    if mode == "-t":
        mode = "1"
    if mode == "-c":
        mode = "2"
    if mode == "0":
        mode = "0"
    return mode


async def find_beatmap(beatmap_id):
    beatmap = await api.get_beatmap(beatmap_id=beatmap_id)
    return beatmap


def decode_mods(mods):
    ans = ""
    if mods == 8:
        ans = "HD"
    if mods == 1:
        ans = "NF"
    if mods == 16:
        ans = "HR"
    if mods == 64:
        ans = "DT"
    if mods == 1024:
        ans = "FL"
    if mods == 512:
        ans = "NC"
    if mods == 256:
        ans = "HT"
    return ans


@bot.command(name='rs', help="!rs (optional: nickname -mode (m = mania, t = taiko, c = ctb, works without "
                             "nickname for linked ppl, default mode is standard")
async def rs(ctx, nickname: str = "xd", mode: str = "0", ):
    pp = 0
    if get_username(ctx.message.author) != "0":
        nickname = get_username(ctx.message.author)
        mode = determine_mode(mode)
        x = await user_recent(nickname, mode)
    else:
        mode = determine_mode(mode)
        x = await user_recent(nickname, mode)
        
    if mode == "3":
        pp = calculate_mania_pp
        
    mapa = await find_beatmap(x.beatmap_id)

    await ctx.message.channel.send(nickname + " - " + str(mapa.artist) + " - " + str(mapa.title) +
                                   " [" + str(mapa.version) + "] +" + str(decode_mods(x.enabled_mods)) +
                                       str(pp))


bot.on_command_error():
    print("XD")


bot.run('')
