import sys
import platform
import discord
from discord.ext import commands

import time
import time
from tinydb import TinyDB, Query, where
from tinydb.operations import delete


skip_roles = ['@EVERYONE', 'DUCKIE', 'ANALYSIS', 'TEST_DUCKIE']

bot = commands.Bot(command_prefix='.')
db = TinyDB('db.json')

# disable default help
bot.remove_command('help')


def get_data(table_name, field=None, field_value=None):
	table = db.table(table_name)
	if field:
		all_results = table.search(Query()[field] == field_value)
	else:
		all_results = table.all()
	return all_results


@bot.command()
async def find(ctx, *args):
	name = ' '.join(args)
	ret = str(db.search(Query().name == name))

	await ctx.send(ret)


@bot.command()
async def schedule(ctx, *args):
	guild = ctx.message.guild

	all_roles = getRoles(guild.roles)

	assigned_role = None
	match_role = args[0].upper()

	if match_role in all_roles:
		assigned_role = list(filter(lambda role: role.name.upper() == match_role, guild.roles))[0]

	if assigned_role == None:
		await ctx.send('The role %s does not exist.' % ' '.join(args[:1]).strip())
		return


@bot.command()
async def store(ctx, *args):
	event_name = ' '.join(args)

	table = db.table(ctx.message.guild.id)

	# Checks if the event has already been created.
	# If it has, don't override the event.
	if db.search(Query().name == event_name):
		await ctx.send('This already exists.')
		return

	# Calculates the date, time, and timezone that the event was created.
	# This helps with logging purposes.
	now_date = time.strftime('%Y-%m-%d')
	now_time = time.strftime('%I:%M%p')
	now_tz = time.tzname[0]
	now_tz_tokens = now_tz.split(' ')
	if len(now_tz_tokens) > 1:
		now_tz = ''.join([token[0] for token in now_tz_tokens])

	# Create the dictionary that represents the record in the event table.
	event_record = {
		'name': event_name, 'date': 'event_date', 'time': 'event_time', 'timezone': 'event_timezone',
		'description': 'event_description', 'author': ctx.author.name, 'created_date': now_date,
		'created_time': now_time, 'created_timezone': now_tz
	}

	try:
		db.insert(event_record)
		await ctx.send('Stored!')
	except:
		await ctx.send('Something broke :(')


@bot.event
async def on_ready():
	print('Duckie is running down the street.')


@bot.command()
async def ping(ctx):
	await ctx.send('pong')


@bot.command()
async def help(ctx):
	view = {
		'author': {
			'name': 'Duckie@Everglades',
			'icon_url': 'https://pbs.twimg.com/profile_images/1067242179955896320/mKdx6PgL_400x400.jpg'
		},
		'fields': [
			{'inline': False, 'name': '__All__',
			 'value': '**nickname** change your own nickname\n**roles** manage your own roles'},
			{'inline': False, 'name': '__Source__',
			 'value': '**info** display information about Duckie\n'}
		],
		'color': 21152,
		'type': 'rich'
	}

	embedVar = discord.Embed.from_dict(view)
	msg = await ctx.send(embed=embedVar, delete_after=30.)


@bot.command()
async def info(ctx):
	await ctx.send('''
	**Duckie info**
	__Platform__: %s
	__Python__: %s
	''' % (platform.platform(), sys.version.replace('\n', '')))


@bot.command()
async def nickname(ctx, *args):
	if len(args) == 0:
		await help.invoke(ctx)
		return

	message = ctx.message
	author = message.author

	command = args[0].upper()

	try:
		if command == 'SET':
			nickname = ' '.join(args[1:]).strip()

			if nickname == '':
				await ctx.send('Invalid nickname.')
				return

			await author.edit(nick=nickname)
			await ctx.send('Updated display name from %s to %s.' % (author.display_name, nickname))
			return
		if command == 'REMOVE':
			await author.edit(nick=None)
			await ctx.send('Updated display name from %s to %s.' % (author.display_name, author.name))
			return
	except:
		await ctx.send('Missing nickname permissions.')
		return


def getRoles(roles):
	return list(filter(lambda role: role not in skip_roles, map(lambda role: str(role).upper(), roles)))


@bot.command()
async def roles(ctx, *args):
	if len(args) == 0:
		await help.invoke(ctx)
		return

	message = ctx.message
	author = message.author
	guild = message.guild

	all_roles = getRoles(guild.roles)
	roles_msg = '```diff\nAvailable roles:'
	roles_msg += '\n+ ' + '\n+ '.join(all_roles)
	roles_msg += '\n```'

	self_roles = getRoles(author.roles)
	user_roles_msg = '```diff\nRoles assigned to %s:' % author.display_name
	if len(self_roles) == 1:
		user_roles_msg += '\n- No roles assigned'
	else:
		user_roles_msg += '\n+ ' + '\n+ '.join(self_roles)
	user_roles_msg += '\n```'

	command = args[0].upper()

	if command == 'LIST':
		if len(args) == 1:
			await ctx.send(roles_msg)
			return

		command = args[1].upper()

		if command == 'ALL':
			await ctx.send(roles_msg)
			return

		if command == 'SELF':
			await ctx.send(user_roles_msg)
			return

	if command == 'ADD':
		if len(args) == 1:
			await help.invoke(ctx)
			return

		assigned_role = None
		match_role = ' '.join(args[1:]).strip().upper()

		if match_role in self_roles:
			await ctx.send('The role %s is already assigned to you.' % ' '.join(args[1:]).strip())
			return

		if match_role in all_roles:
			assigned_role = list(filter(lambda role: role.name.upper() == match_role, guild.roles))[0]

		if assigned_role == None:
			await ctx.send('The role %s does not exist.' % ' '.join(args[:1]).strip())
			return

		await author.add_roles(assigned_role)
		await ctx.send('Added %s to %s!' % (assigned_role.name, author.display_name))
		return

	if command == 'REMOVE':
		if len(args) == 1:
			await help.invoke(ctx)
			return

		assigned_role = None
		match_role = ' '.join(args[1:]).strip().upper()

		if (match_role == 'ALL'):
			user_roles = author.roles

			i = 1
			progress = await ctx.send('Progress: {: <2d}/{: <2d}'.format(i, len(user_roles)-1))

			for role in user_roles:
				if (role.name not in skip_roles):
					await author.remove_roles(role)
					await progress.edit(content='Progress: {: <2d}/{: <2d}'.format(i, len(user_roles)-1))
					i += 1

			await ctx.send('Removed all roles from %s!' % author.display_name)
			return

		if match_role in all_roles:
			assigned_role = list(
				filter(lambda role: role.name.upper() == match_role, guild.roles))[0]

		if assigned_role == None:
			await ctx.send('The role %s does not exist.' % ' '.join(args[:1]).strip())
			return

		await author.remove_roles(assigned_role)
		await ctx.send('Removed %s from %s!' % (assigned_role.name, author.display_name))
		return

# -------------------------

# read token from token.txt
token = ''
with open('token.txt', 'r') as file:
	token = file.read().replace('\n', '')

bot.run(token)
