import sys
import platform
import discord
from discord.ext import commands

import time
from tinydb import TinyDB, Query, where
from tinydb.operations import delete
import requests

url = 'https://dashleague.games/wp-json/api/v1/stats/data?data=standings'
color = discord.Color.from_rgb(r=245,g=191,b=66).value

bot = commands.Bot(command_prefix='.')
db = TinyDB('db.json')

# disable default help
bot.remove_command('help')

@bot.event
async def on_ready():
	print('Duckie is running down the street.')


@bot.command()
async def ping(ctx):
	await ctx.send('pong')

@bot.command()
async def start(ctx):
	await ctx.channel.purge()

	resp = requests.get(url=url)
	data = resp.json()['data']
	data.sort(key=lambda x: int(x['mmr']), reverse=True)

	fields = []

	for i, d in enumerate(data):
		name = d['name']
		mmr = int(d['mmr'])
		matches = int(d['matches'])
		wins = int(d['wins'])
		losses = matches - wins

		fields.append({
			'inline': True,
			'name': '{: 2d}. {} ({:d})'.format(i+1, name, mmr),
			'value': 'Wins/Losses: {:02d}/{:02d}\nWin ratio: {:.2f}'.format(wins, losses, wins/matches)
		})

	view = {
		'author': {
			'name': 'Duckie',
			'icon_url': 'https://pbs.twimg.com/profile_images/1067242179955896320/mKdx6PgL_400x400.jpg'
		},
		'fields': fields,
		'color': color,
		'type': 'rich',
	}

	embed = discord.Embed.from_dict(view)
	msg = await ctx.send(embed=embed)

	print(msg)


@bot.command()
async def info(ctx):
	await ctx.send('''
	**Duckie info**
	__Platform__: %s
	__Python__: %s
	''' % (platform.platform(), sys.version.replace('\n', '')))

# -------------------------

# read token from token.txt
token = ''
with open('token.txt', 'r') as file:
	token = file.read().replace('\n', '')

bot.run(token)
