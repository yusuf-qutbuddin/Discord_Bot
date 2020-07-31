'''
Discord Bot: small_person
Description: A friendly neighbourhood bot for filmmaking/film discussion forums. Helps with moderation and archiving.
Author: Yusuf Qutbuddin

'''


import discord
from discord.ext import commands
from discord.utils import get
from datetime import datetime
import os.path
import asyncio
import sys

client = commands.Bot(command_prefix = '!')

# Logs the status of the bot on the console
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    '''for channel in client.get_all_channels():
        if channel.name == 'general':
            await channel.send(f'Say hello to my little friend! ')
            with open('sayhellow.gif', 'rb') as read_file:
                await channel.send(file = discord.File(read_file, 'sayhellow.gif'))'''


    

# logs the information of a user that joined 
@client.event
async def on_member_join(member):
    print('{0} has joined the server'.format(member))

# logs the information of a user that left 
@client.event
async def on_member_remove(member):
    print('{0} has been removed'.format(member))

# a ping test to know the latency of the bot
@client.command()
async def there(ctx):
    await ctx.send('You talkin\' to me? \n Latency: {0} ms'.format(round(client.latency)*1000))
    with open('talkin.gif', 'rb') as read_file:
                await ctx.send(file = discord.File(read_file, 'talkin.gif'))

# to find the role of a particular member of the server
@client.command()
async def giverole(ctx, member: discord.Member):
    if ctx.message.author == client.user: return
    roles = list()
    roles = member.roles
    roles.pop(0)
    await ctx.send(f'The following roles are assigned to {member.mention}')
    for role in roles: 
        await ctx.send(f'{role}')

# to clear a given amount of messages 
@client.command()
@commands.has_role('MODS')
async def secclear(ctx, amount = 1):
    await ctx.channel.purge(limit = amount+1)

# assign a given role to a particular member
@client.command()
@commands.has_role('MODS')
async def assign(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f'{member.mention} has been assigned the role {role}')

# unassign a given role from a particular member
@client.command()
@commands.has_role('MODS')
async def unassign(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f'{member.mention} has been unassigned the role {role}')

# add a particular channel to the Category of Film/Shows Discussions
@client.command()
async def ctext(ctx, *,channelname = 'qwerty'):
    if channelname == 'qwerty': return
    guild = ctx.guild
    category = get(ctx.guild.categories, name = 'Film/Shows Discussions')
    await guild.create_text_channel(channelname, category = category)
    channelname = channelname.replace(' ','-').lower()
    channel = get(ctx.guild.channels, name = channelname)
    send_channel = get(ctx.guild.channels, name = 'small-person-log')
    await ctx.send(f'{ctx.message.author.mention} has created the channel {channel.mention}' )
    await send_channel.send(f'{ctx.message.author.mention} has created the channel {channel.mention}' )

# testing has_role
'''@client.command()
@commands.has_role('1st Years')
async def test1(ctx):
    await ctx.send('You\'re a first year')'''

# list down inactive channels in the category Film Discussions
@client.command()
async def lsinactive(ctx, limit = 0):
    async def processinactive(ctx, guild, category):
        channels = category.channels
        for channel in channels:
            async for message in channel.history(limit=1): # channel history object is iterable and gives the messages (limit = 1 means it takes only one message )
                evolvedtime = datetime.now()-message.created_at # creates a timedelta object
                secondsEvolved = evolvedtime.total_seconds() #extracts total time in seconds
                daysEvolved, remainder = divmod(secondsEvolved, 86400) # converts total time in days 
                if daysEvolved > limit:
                    await ctx.send(f'{channel.mention} was last active {daysEvolved} days ago') 

    guild = ctx.guild
    category = get(ctx.guild.categories, name = 'Film/Shows Discussions')
    await processinactive(ctx, guild, category)

@client.command()
@commands.has_role('MODS')
async def archivech(ctx, channel: discord.TextChannel):
    save_path = 'E:\\bots\Archived TFPS'
    completeName = os.path.join(save_path, channel.name+".txt")

    with open(completeName, 'a') as file:
        async for message in channel.history(limit = None, oldest_first = True):
            embed = None
            attachment = None
            strtime = message.created_at.strftime('%Y-%m-%d %H:%M')
            author = message.author
            content = message.content
            content = content.encode('utf-8')
            embeds = message.embeds
            attachments = message.attachments
            for attachment in attachments:
                pass
            for embed in embeds:
                pass
            #print(f'{strtime} \t {author} \t {content} \t {embed} \t {attachment}')
            template = '[{strtime}] <{author}> {content} ({embeds}) ({attachments}) \n'
            try:
                if embed != None and attachment != None:
                    file.write(template.format(strtime = strtime, author = author, content = content, embeds = embed.url, attachments = attachment.url))
                elif embed != None:
                    file.write(template.format(strtime = strtime, author = author, content = content, embeds = embed.url, attachments = None))
                elif attachment != None:
                    file.write(template.format(strtime = strtime, author = author, content = content, embeds = None, attachments = attachment.url))
                else:
                    file.write(template.format(strtime = strtime, author = author, content = content, embeds = None, attachments = None))
            except:
                file.write('Archiving Error')

            

    await ctx.send(f'Archiving of {channel.mention} has been complete.', file = discord.File(completeName, channel.name+'.txt'))
    role = get(ctx.guild.roles, id = 734784893107830925)
    print(role.name)
    await channel.set_permissions(role, read_messages = False, send_messages = False, read_message_history = False)
        #await asyncio.sleep(4)
    


''''@client.command()
@commands.has_role('MODS')
async def givenow(ctx, channel: discord.TextChannel):
    save_path = 'E:\\bots\Archived TFPS'
    completeName = os.path.join(save_path, channel.name+".txt")
    await ctx.send(file = discord.File(completeName, channel.name+'.txt'))'''




client.run('xxxx')
