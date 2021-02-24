#!/usr/bin/env python3
import os
from discord.ext import commands
import discord
import random
import threading

token = os.getenv('DISCORD_TOKEN')
target_guild = 'Bot testing'
target_category = 'Stolovi'
lock = threading.Lock()

TABLES = dict()
CATEGORIES = []

class Table():
	def __init__(self, name, role, channels):
		self.name = name
		self.role = role
		self.channels = channels

	async def clean(self, deep):
		if deep:
			for channel in self.channels:
				await channel.delete()
		if self.role != 'Clean':
			await self.role.delete()

		print(f'Cleaned {self.name}')


intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.command(name='members', help='Prints out the number of server members, prints out all the roles and number of members.')
@commands.has_role('Bot managers')
async def print_memberships(ctx):
	roles = dict()
	for member in ctx.guild.members:
		for r in member.roles:
			if r in roles:
				roles[r] += 1
			else:
				roles[r] = 1
	ret = '\n'.join([str((i,roles[i])) for i in roles])
	await ctx.send(f'{ctx.guild.member_count}')
	role_names = sorted(roles.keys())
	for r in roles:
		await ctx.send(str((r,roles[r])))

@bot.command(name='table', help='!table X @user1 @user2...\nCreates a text & a voice channel named "stol-X" and grants access to selected users.')
@commands.has_role('Bot managers')
async def table(ctx, name:str, *args:discord.Member):
	await create_table_channels(ctx, name, args)
	await ctx.send('Done!')

async def create_table_channels(ctx, name, members, rnd_name=target_category):
	# print(members)
	for m in members:
		print(m)
	c = get_category(ctx, rnd_name)
	role = await ctx.guild.create_role(name=f'role-{name}')
	overwrites = {
		ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
		role: discord.PermissionOverwrite(read_messages=True),
		role: discord.PermissionOverwrite(send_messages=True),
		role: discord.PermissionOverwrite(connect=True),
		role: discord.PermissionOverwrite(speak=True)
	}
	text = await ctx.guild.create_text_channel(name=f'stol-{name}', category=c, overwrites=overwrites)
	voice = await ctx.guild.create_voice_channel(name=f'stol-{name}', category=c, overwrites=overwrites)
	for member in members:
		await member.add_roles(role)
	global TABLES
	print(name)
	TABLES[name] = Table(name, role, [text, voice])

	await text.send(f'{" ".join([m.mention for m in members])}')
	await text.send('''DOBRODOŠLI NA PRVI HRVATSKI ONLINE CATAN TURNIR ! Nemojte zaboraviti postaviti brzinu igre na brzo (fast) jer u suprotnom ćete morati igrati ispočetka ili gubiti poene. 
Uključite postavku private game kako vam netko ne bi ušao u sobu dok čekate da se ostali priključe. Ostala pravila su : 4 Players, 10 Victory Points, Base game, Random Dice, Card discard 7 i hidden bank cards.. Molimo vas da (jedna od četiri osobe) napravite sobu na colonist.io, pošaljete link protivnicima u chat i nazovete ju 1. Hrvatski Online Catan Turnir Stol x. 
U slučaju da nekog nema dulje vrijeme ili vam nešto nije jasno, koristite tag @Pomoć. Kada krene igra napišite u chat stola “krenuli“. NE ZABORAVITE DA POBJEDILI ILI IZGUBILI, KVALIFIKACIJE SE SASTOJE OD TRI IGRE !!! (samo ako odigrate sve tri igre imate šansu osvojiti jednu od nagrada).
KADA STE GOTOVI S IGROM pošaljite screenshoot rezultata u chat stola na kojem ste igrali i u #screenshoot te označite moderatora pomoću oznake @Pomoć''')

def get_category(ctx, rnd_name):
	for c in ctx.guild.categories:
		if c.name.lower() == rnd_name.lower():
			return c
	return None


@bot.command(name='clean', help='!clean [True]\nRemove access to all tables created by this bot instance, with True parameter it also destroys them\nWARNING!!! This action is irreversible')
@commands.has_role('Bot managers')
async def clean(ctx, deep:bool=False):
	global TABLES
	num = len(TABLES)
	for t in TABLES:
		# print(TABLES[t])
		await TABLES[t].clean(deep)
		TABLES[t].role = 'Clean'
	if deep:
		TABLES = dict()
	global CATEGORIES
	for c in CATEGORIES:
		await c.delete()
	await ctx.send(f'Cleaned {num} groups')

@bot.command(name='close', help='!close X [True]\nClose table, remove access, with True in the end it also destroys channels.\nIt allows removal of access and destruction of channels later.')
@commands.has_role('Bot managers')
async def close(ctx, name, deep:bool=False):
	global TABLES
	if name in TABLES:
		await TABLES[name].clean(deep)
		TABLES[name].role = 'Clean'
		if deep:
			del TABLES[name]
		await ctx.send(f'Closed {name}')
	else:
		await ctx.send(f'Unknown name {name}')
		available = []
		for i in TABLES:
			available.append((i, str(TABLES[i].role != 'Clean')))
		s = "\n".join([i[0]+'|'+i[1] for i in available])
		await ctx.send(f'Available channels (name|users still have access):\n{s}')

@bot.command(name='distribute', help='!distribute rundaX @checkinani 4 \nCreates tables & grants access to random players.')
@commands.has_role('Bot managers')
async def distribute(ctx, name, role:discord.Role, num=4):
	if get_category(ctx, name) == None:
		c = await ctx.guild.create_category_channel(name)
		global CATEGORIES
		CATEGORIES.append(c)

	members = []
	for member in ctx.guild.members:
		if role in member.roles:
			members.append(member)
	random.shuffle(members)
	members = [members[i:i+num] for i in range(0, len(members), num)]
	for i, l in enumerate(members):
		await create_table_channels(ctx, f'{name}-{i+1}', l, name)
		await ctx.send(f'{name}-{i+1} {", ".join([m.name for m in l])}')

@bot.command(name='makni_stolove', help='Destroy all channels with a name beggining with "stol".')
@commands.has_role('Bot managers')
async def makni_stolove(ctx):
	for c in ctx.guild.channels:
		if c.name.startswith('stol'):
			# print(c.name)
			await c.delete()

@bot.command(name='swap', help='!swap @user @role - Swap an inactive user with a user from role.')
@commands.has_role('Bot managers')
async def swap(ctx, user:discord.Member, role:discord.Role):
	role_to_set = None
	channel_name = ctx.channel.name
	suffix = '-'.join(channel_name.split('-')[1:])
	r = None
	for i in user.roles:
		if i.name.endswith(suffix):
			r = i
			break
	await user.remove_roles(r)
	with lock:
		new_user = random.choice(role.members)
		await new_user.remove_roles(role)
	await new_user.add_roles(r)
	await ctx.send(f'Swapped {user.mention} with {new_user.mention}')

@bot.command(name='add', help='!add @role - Add a random user from role.')
@commands.has_role('Bot managers')
async def swap(ctx, role:discord.Role):
	role_to_set = None
	channel_name = ctx.channel.name
	suffix = '-'.join(channel_name.split('-')[1:])
	r = None
	for i in ctx.guild.roles:
		if i.name.endswith(suffix):
			r = i
			break
	with lock:
		new_user = random.choice(role.members)
		await new_user.remove_roles(role)
	await new_user.add_roles(r)
	await ctx.send(f'Added {new_user.mention}')

bot.run(token)