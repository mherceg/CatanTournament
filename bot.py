#!/usr/bin/env python3
import os
from discord.ext import commands
import discord

token = os.getenv('DISCORD_TOKEN')
target_guild = 'Bot testing'
target_category = 'Stolovi'

tables = dict()

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


@bot.command(name='members')
async def print_memberships(ctx):
	
	for member in ctx.guild.members:
		# print()
		roles = ', '.join([role.name for role in member.roles])
		# print(f'{member.name}: {roles}')

	await ctx.send(f'{ctx.guild.member_count}')

@bot.command(name='table', help='!table X @user1 @user2...\nNapravi text i voice kanal sa imenom stol-X i napravi da je vidljiv korisnicima.')
async def table(ctx, name:str, *args:discord.Member):
	await create_table_channels(ctx, name, args)
	await ctx.send('Done!')

async def create_table_channels(ctx, name, members):
	# print(members)
	for m in members:
		print(m)
	c = get_category(ctx)
	role = await ctx.guild.create_role(name=f'role-{name}')
	overwrites = {
		ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
		role: discord.PermissionOverwrite(read_messages=True)
	}
	text = await ctx.guild.create_text_channel(name=f'stol-{name}', category=c, overwrites=overwrites)
	voice = await ctx.guild.create_voice_channel(name=f'stol-{name}', category=c, overwrites=overwrites)
	for member in members:
		await member.add_roles(role)

	tables[name] = Table(name, role, [text, voice])


def get_category(ctx):
	for c in ctx.guild.categories:
		if c.name.lower() == target_category.lower():
			return c
	return None

@bot.command(name='test')
async def test(ctx):
	# print(ctx.guild.categories)
	pass

@bot.command(name='clean', help='!clean [True]\nMakne pristup svim stolovima koje je stvorio, sa True na kraju ih unisti\nPAZI!! Nema povratka kad unisti')
async def clean(ctx, deep:bool=False):
	global tables
	num = len(tables)
	for t in tables:
		# print(tables[t])
		await tables[t].clean(deep)
		tables[t].role = 'Clean'
	if deep:
		tables = []
	await ctx.send(f'Cleaned {num} groups')

@bot.command(name='close', help='!close X [True]\nZatvori stol, makne pristup, sa True na kraju i unisti kanale.\nMoze se prvo samo maknuti pristup i naknadno ukloniti kanale.')
async def close(ctx, name, deep:bool=False):
	if name in tables:
		await tables[name].clean(deep)
		tables[name].role = 'Clean'
		if deep:
			del tables[name]
		await ctx.send(f'Closed {name}')
	else:
		await ctx.send(f'Unknown name {name}')
		available = []
		for i in tables:
			available.append((i, str(tables[i].role != 'Clean')))
		s = "\n".join([i[0]+'|'+i[1] for i in available])
		await ctx.send(f'Available channels (name|users still have access):\n{s}')

@bot.command(name='distribute')
async def distribute(ctx, name, role='Igraju', num=4):
	pass

bot.run(token)