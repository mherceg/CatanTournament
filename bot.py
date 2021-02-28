#!/usr/bin/env python3
import os
from discord.ext import commands
import discord
import threading
import colonist
import random
import time
import asyncio
from calculate import compute

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
		role: discord.PermissionOverwrite(read_messages=True)
	}
	text = await ctx.guild.create_text_channel(name=f'stol-{name}', category=c, overwrites=overwrites)
	voice = await ctx.guild.create_voice_channel(name=f'stol-{name}', category=c, overwrites=overwrites)
	for member in members:
		await member.add_roles(role)
	global TABLES
	print(name)
	TABLES[name] = Table(name, role, [text, voice])

	await text.send(f'{" ".join([m.mention for m in members])}')
	await text.send('''DOBRODOŠLI NA PRVI HRVATSKI ONLINE CATAN TURNIR ! Nemojte zaboraviti postaviti brzinu igre na brzo (fast) jer u suprotnom ćete morati igrati ispočetka ili gubiti poene. Uključite postavku private game kako vam netko ne bi ušao u sobu dok čekate da se ostali priključe. Ostala pravila su : 4 Players, 10 Victory Points, Base game, Random Dice, Card discard 7 i hidden bank cards.. Molimo vas da (jedna od četiri osobe) napravite sobu na colonist.io, pošaljete link protivnicima u chat i nazovete ju 1. Hrvatski Online Catan Turnir Stol x. U slučaju da nekog nema dulje vrijeme ili vam nešto nije jasno, koristite tag `@Pomoć`. Kada krene igra napišite u chat stola “krenuli“. Ukoliko netko izađe tokom igre, dopušteno je trejdanje s botom. NE ZABORAVITE DA POBJEDILI ILI IZGUBILI, KVALIFIKACIJE SE SASTOJE OD TRI IGRE !!! (samo ako odigrate sve tri igre imate šansu osvojiti jednu od nagrada). KADA STE GOTOVI S IGROM pozovite bota s naredbom "!done", ako vam treba pomoć pozovite moderatora sa `@Pomoć`.''')

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

def get_role(ctx, channel_name):
	suffix = '-'.join(channel_name.split('-')[1:])
	for i in ctx.guild.roles:
		if i.name.strip().lower().endswith(suffix.strip().lower()):
			return i

@bot.command(name='swap', help='!swap @user @role - Swap an inactive user with a user from role.')
@commands.has_role('Bot managers')
async def swap(ctx, user:discord.Member, role:discord.Role):
	role_to_set = None
	r = get_role(ctx, ctx.channel.name)
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
	r = get_role(ctx, ctx.channel.name)
	print("Rola", r)
	with lock:
		new_user = random.choice(role.members)
		await new_user.remove_roles(role)
	await new_user.add_roles(r)
	await ctx.send(f'Added {new_user.mention}')

def print_result(result, filt=False):
	r = []
	for i in result:
		if i.finished and not i.quited and i.isHuman or not filt:
			r.append(i)
	return '\n'.join([str(i) for i in r])

@bot.command(name='done', help='!done\nInteractive guide to fetch and store the result')
async def done(ctx):
	username = None
	def check(m):
		return m.channel == ctx.channel and m.author != bot.user
	for i in range(3):
		if username != None:
			break
		await ctx.send('Username jednog od igraca na colonist.io?')
		msg = await bot.wait_for('message', check=check)
		username = msg.content
		if not colonist.check_user(username):
			await ctx.send(f'Nema usera {username} ili ga ne mogu dohvatiti. Probajte opet ili pozovite @Pomoc.')
			username = None
	for i in range(5):
		try:
			results = colonist.get_result(username, i)
		except Exception as e:
			await ctx.send('Nisam pronasao rezultat. Posaljite screenshot rezultata i oznacite @Pomoc.')
			print(e)
			return
		await ctx.send(f'Nasao sam rezultat:``` Rang        Username    Bodovi Ukupno_bodova\n{print_result(results)}\n```')
		msg = await ctx.send(f'Ako je to tocan rezultat klikni :thumbsup:, ako nije klikni :thumbsdown: (potreban je :thumbsup: dva igraca da bi rezultat bio valjan)')
		await msg.add_reaction('👍')
		await msg.add_reaction('👎')
		user1 = None
		def check_reaction(reaction, user):
			if reaction.message != msg:
				return False
			if user == bot.user or (user == user1 and user.id != 694945316625055854):
				return False
			if reaction.emoji == '👍' or reaction.emoji == '👎':
				return True
		reaction, user1 = await bot.wait_for('reaction_add', check=check_reaction)
		if reaction.emoji == '👍':
			reaction, user = await bot.wait_for('reaction_add', check=check_reaction)
			if reaction.emoji == '👍':
				with open(f'results/results-{ctx.channel.name.split("-")[1]}.txt', 'a+') as fout:
					fout.write(print_result(results, True) + '\n')
				await ctx.send('Rezultat zabiljezen, hvala. Ne zaboravite se prijaviti za sljedecu rundu.')
				await ctx.send('Ovaj kanal ce biti zatvoren za dvije minute.')
				await wait_and_close(ctx)
				return	
			elif reaction.emoji == '👎':
				continue
			else:
				return
		elif reaction.emoji == '👎':
			continue
		else:
			return
	await ctx.send('Nisam pronasao rezultat. Posaljite screenshot rezultata i oznacite @Pomoc.')

async def wait_and_close(ctx):
	await asyncio.sleep(120)
	await close(ctx, '-'.join(ctx.channel.name.split('-')[1:]))
	return		

@bot.command(name='results', help='!results')
@commands.has_role('Bot managers')
async def results(ctx):
	output = [' Rang             Ime Broj_pobjeda Zbroj_bodova Udio_bodova Odigranih_rundi']
	for i, x in enumerate(compute()):
		output.append(f'{i+1:>5}{x}')
	with open('results.txt', 'w') as fout:
		fout.write('\n'.join(map(str,output))+'\n')
	with open('results.txt', 'rb') as fin:
		await ctx.send('Rezultati!', file=discord.File(fin))

	

bot.run(token)