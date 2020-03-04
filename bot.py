import discord
import asyncio
from pyosu import OsuApi
import random
import os
import pyosu
from discord.ext import commands

prefix = '$'

api = OsuApi('bc9f34f842a780c634153f5b3fb32b211b3ac8f3')
bot = commands.Bot(command_prefix='!')


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
        return(z)
    else:
        return("0")


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

@bot.command(name='rs', help="!rs (optional: nickname -mode (m = mania, t = taiko, c = ctb, works without "
                             "nickname for linked ppl, default mode is standard")
async def rs(ctx, nickname: str = "xd", mode: str = "0",):
    if get_username(ctx.message.author) != "0":
        nickname = get_username(ctx.message.author)
        mode = determine_mode(mode)
        x = await user_recent(nickname, mode)
    else:
        mode = determine_mode(mode)
        x = await user_recent(nickname, mode)
    mapa = await find_beatmap(x.beatmap_id)

    await ctx.message.channel.send(nickname + " " + str(mapa.title))


bot.run('Njg0MDU3MjM2MjA0ODE0Mzk4.Xl_crg.hq8P-aqHwR0uMaQdtucyL6AGUHs')
