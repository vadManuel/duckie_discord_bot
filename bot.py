import discord
import requests
import asyncio
import platform
import sys
from discord.ext import commands

skip_roles = ['@everyone', 'Duckie', 'Analysis']

bot = commands.Bot(command_prefix='.')

# disable default help
bot.remove_command('help')

@bot.command()
async def info(ctx):
	await ctx.send('''
	**Duckie info**
	__Platform__: %s
	__Python__: %s
	''' % (platform.platform(), sys.version.replace('\n','')))


@bot.command()
async def help(ctx):
	await ctx.send('''
	**Everglades bot help menu**
	__Nickname:__
	**set** Change your own nickname.
	\t.nickname set Boaty McBoatFace
	**remove** Returns to original username.
	\t.nickaname remove
	__Roles:__
	**list** Show all roles.
	\t.roles list [self, all]
	**add** Add a role to yourself.
	\t.roles add Linux
	**remove** Remove a role from yourself.
	\t.roles remove Windows
	\t.roles remove all
	__Info:__
	Displays info about Duckie.
	\t.info
	''')

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
			nickname = ' '.join(args[1:])

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


@bot.command()
async def roles(ctx, *args):
	if len(args) == 0:
		await help.invoke(ctx)
		return

	message = ctx.message
	author = message.author
	guild = message.guild

	roles_msg = '```diff\nAvailable roles:'
	roles_msg += '\n+ ' + '\n+ '.join(list(filter(lambda role: role not in skip_roles, map(lambda role: str(role), guild.roles))))
	roles_msg += '\n```'

	user_roles_msg = '```diff\nRoles assigned to %s:' % author.display_name
	if len(author.roles) == 1:
		user_roles_msg += '\n- No roles assigned'
	else:
		user_roles_msg += '\n+ ' + '\n+ '.join(list(filter(lambda role: role not in skip_roles, map(lambda role: str(role), author.roles))))
	user_roles_msg += '\n```'

	match_roles = list(filter(lambda role: role not in skip_roles, map(lambda role: str(role).upper(), guild.roles)))
	
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
		match_role = args[:1].upper()


		if match_role in match_roles:
			assigned_role = list(filter(lambda role: role.name.upper() == match_role, guild.roles))[0]

		if assigned_role == None:
			await ctx.send('The role %s does not exist.' % args[1])
			return

		await author.add_roles(assigned_role)
		await ctx.send('Added %s to %s!' % (assigned_role.name, author.display_name))
		return
	
	if command == 'REMOVE':
		if len(args) == 1:
			await help.invoke(ctx)
			return
		
		assigned_role = None
		match_role = args[1].upper()

		if (match_role == 'ALL'):
			user_roles = author.roles

			i = 1
			progress = await ctx.send('Progress: {: <2d}/{: <2d}'.format(i, len(user_roles)-1))

			for role in user_roles:
				if (role.name not in skip_roles):
					await author.remove_roles(role)
					await progress.edit(content='Progress: {: <2d}/{: <2d}'.format(i, len(user_roles)-1))
					i+=1

			await ctx.send('Removed all roles from %s!' % author.display_name)
			return

		if match_role in match_roles:
			assigned_role = list(filter(lambda role: role.name.upper() == match_role, guild.roles))[0]

		if assigned_role == None:
			await ctx.send('The role %s does not exist.' % args[1])
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