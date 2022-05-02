import random
import re
import discord
import sys

from datetime import datetime
from functions import db, deck, dice, gcs, quote, remember
from functions.dice import dice_regex
from functions.subfunctions.split_file import split_file

token = sys.argv[1]

prefix = '.'
eight_ball = split_file('eightball')
dice_double_check = r'^(?:(\d+)d(\d+))'

decks = {}
bot = discord.Client()

try:
    conn = db.connect()
except:
    conn = None


@bot.event
async def on_ready():
    print('Logging in...')
    for server in bot.guilds:
        decks[server.name] = deck.NEW_DECK.copy()
        random.shuffle(decks[server.name])
    print("I am ready to serve.")


@bot.event
async def on_member_join(member):
    await member.guild.default_channel.send(
                           "Welcome, " + member.display_name + ", to " + member.guild.name + "!")


@bot.event
async def on_guild_join(server):
    await server.default_channel.send(
                           "Hello, people of " + server.name + "! I am " + bot.user.display_name + "!")


@bot.event
async def on_message(msg):
    if msg.author.bot:
        return
    clean_message = str(msg.clean_content)
    results = re.findall(dice_regex, clean_message)
    doublecheck = re.search(dice_double_check, clean_message)
    if len(results) > 0 and results[0][0] == '' and results[0][3] == '' and results[0][4] == '' and doublecheck is not None:
        try:
            await send_response(msg, dice.parse_dice_request(msg))
        except TypeError:
            return
    elif str(msg.content).startswith(prefix):
        content = parse_command(msg)
        await send_response(msg, content)


def parse_command(msg):
    str_content = str(msg.content[1:])
    command = str_content.split(' ', 1)[0]

    if command == 'echo':
        return 'Echo!'
    elif command == 'repeat':
        return str_content[7:]
    elif command == '8ball' or command == 'eightball':
        return random.choice(eight_ball)
    elif command == 'choose' or command == 'ch':
        result = ""
        if len(str_content[len(command)+1:]) > 0:
            while result == "":
                result = random.choice(str_content[len(command)+1:].split(','))
            return random.choice(str_content[len(command)+1:].split(','))
    elif command == 'deck':
        response = deck.parse_deck_request(msg, decks[msg.guild.name])
        if response[0] is not None:
            decks[msg.guild.name] = response[0]
        return response[1]
    elif command == 'roll':
        return dice.parse_dice_request(msg)
    elif command == 'pfsrd':
        return gcs.pfsrd(msg)
    elif command == 'nethys':
        return gcs.nethys(msg)
    elif command == 'google':
        return gcs.google(msg)
    elif command == 'g':
        return gcs.g(msg)
    elif command == 'youtube':
        return gcs.youtube(msg)
    elif command == 'yt':
        return gcs.yt(msg)
    elif command == 'quote':
        if conn is not None:
            return quote.parse_quote_request(msg, conn)
        else:
            return 'I cannot access the database right now.'
    elif command == 'remember':
        if conn is not None:
            return remember.parse_remember_request(msg, conn)
        else:
            return 'I cannot access the database right now.'


async def send_response(msg, content):
    await msg.channel.send(msg.author.mention + ': ' + content)

start_time = datetime.now()
bot.run(token)
