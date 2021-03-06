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
import imdb
import urllib.parse, urllib.request, re
import random as r
import xlrd
from xlutils.copy import copy
import xlwt





client = commands.Bot(command_prefix = '!')
save_path = 'E:\\'
name = os.path.join(save_path, "token.txt")
with open(name, 'r') as file:
	token = file.readline()
	url = file.readline()
# Logs the status of the bot on the console
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    activity = discord.Activity(name='movies | !helpme', type=discord.ActivityType.watching)
    await client.change_presence(activity=activity)
    '''for channel in client.get_all_channels():
        if channel.name == 'general':
            await channel.send(f'Say hello to my little friend! ')
            with open('sayhellow.gif', 'rb') as read_file:
                await channel.send(file = discord.File(read_file, 'sayhellow.gif'))'''

async def add_cookies(ctx, member, cok):
	loc = 'TFPS_cookiejar.xls'
	flag = False

	workbookr = xlrd.open_workbook(loc, encoding_override="cp1252")
	workbookw = copy(workbookr)
	worksheetw = workbookw.get_sheet(0)
	worksheetr = workbookr.sheet_by_index(0)
	for row in range(worksheetr.nrows):
		if str(worksheetr.cell(row,0).value) == str(member.id):
			cookie = int(worksheetr.cell(row,1).value)
			if cookie <= 0:
				return False
			worksheetw.write(row,1,str(cookie+cok))
			flag = True
			break
	if flag is False:
		if cok>0:
			worksheetw.write(worksheetr.nrows,0,str(member.id))
			worksheetw.write(worksheetr.nrows,1,str(cok))
		else:
			worksheetw.write(worksheetr.nrows,0,str(member.id))
			worksheetw.write(worksheetr.nrows,1,str(0))
			workbookw.save(loc)
			return False


	workbookw.save(loc)
	return True

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
    myembed = discord.Embed(title = f'The following roles are assigned to {member.name}', colour = discord.Colour.green())
    myembed.set_thumbnail(url = url)
    for role in roles:
    	index = int(roles.index(role))+1
    	myembed.add_field(name = f'{index}', value = f'{role}', inline = True)
    await ctx.send(embed = myembed)
   

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
    await ctx.send(f'{ctx.message.author.mention} has created the channel {channel.mention}. You get one TFPS cookie \U0001F36A' )
    await send_channel.send(f'{ctx.message.author.mention} has created the channel {channel.mention}' )
    await add_cookies(ctx, ctx.author, 1)

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
        myembed = discord.Embed(title = f'Channels\' inactive period', colour = discord.Colour.gold())
        myembed.set_thumbnail(url = url)
        testmember = ctx.guild.get_member(737805006820081715)
        for channel in channels:
        	if channel.permissions_for(testmember).read_messages is False:
        		continue
        	async for message in channel.history(limit=1):
        		evolvedtime = datetime.now()-message.created_at # creates a timedelta object
        		secondsEvolved = evolvedtime.total_seconds() #extracts total time in seconds
        		daysEvolved, remainder = divmod(secondsEvolved, 86400) # converts total time in days 
        		if daysEvolved > limit:
		            myembed.add_field(name = f'{channel}', value = f'active {daysEvolved} days ago', inline = False) 
        
        await ctx.send(embed=myembed)

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
            t = '[{strtime}] <{author}> {content} ({embeds}) ({attachments}) \n'
            try:
                if embed != None and attachment != None:
                    file.write(t.format(strtime = strtime, author = author, content = content, embeds = embed.url, attachments = attachment.url))
                elif embed != None:
                    file.write(t.format(strtime = strtime, author = author, content = content, embeds = embed.url, attachments = None))
                elif attachment != None:
                    file.write(t.format(strtime = strtime, author = author, content = content, embeds = None, attachments = attachment.url))
                else:
                    file.write(t.format(strtime = strtime, author = author, content = content, embeds = None, attachments = None))
            except:
                file.write('Archiving Error')

            

    await ctx.send(f'Archiving of {channel.mention} has been complete.', file = discord.File(completeName, channel.name+'.txt'))
    role = get(ctx.guild.roles, id = 734784893107830925)
    print(role.name)
    await channel.set_permissions(role, read_messages = False, send_messages = False, read_message_history = False)
        #await asyncio.sleep(4)
    
@client.command()
async def suggest(ctx, *,moviename = 'qwerty'):
	if moviename == 'qwerty': return
	
	ia = imdb.IMDb()
	movie = ia.search_movie(moviename)
	myembed = discord.Embed(title = 'Suggest a movie', colour = discord.Colour.green(), description = 'Please select which movie you want to suggest by typing the number, press 0 to cancel. (Timeout: 10 sec)')
	myembed.set_thumbnail(url = url)
	for count in range(5):
		if len(movie) == count:
			break
		title = movie[count]['title']
		try: 
			movyear = movie[count]['year']
		except:
			movyear = 'year unknown/under development'

		myembed.add_field(name = f'{count+1}. {title} ({movyear})', value ='\u200b', inline = False)

	botmessage = await ctx.send(embed = myembed)
	
	myembed.clear_fields()
	t = True
	while(t):
		try:
			msg = await client.wait_for('message', check = lambda message: message.author == ctx.author, timeout = 10)
			content = msg.content
			try:
				await msg.delete()
			except:
				pass
		except asyncio.TimeoutError:
			myembed.add_field(name = 'Timeout. Make it snappy next time', value = 'You didn\'t respond for 10 seconds.')
			await botmessage.edit(embed = myembed)
			return
		else:
		#print(msg.content)
			rng = list(range(1,count+1))
			try:
				if int(content) == 0: 
					return
				elif int(content) in rng:
					count = int(content) - 1
					t = False
				else:
					await ctx.send('That is not a valid attempt. Try a number between 1 and 5 or press 0 to cancel.')
			except:
				await ctx.send('Please type a number. Try again.')

	movieid = movie[count].movieID
	title = movie[count]['title']
	try:
		movyear = movie[count]['year']
	except:
		movyear = 'year unknown/under development'

	myembed = discord.Embed(title = f'{title} ({movyear})')
	myembed.set_thumbnail(url = url)
	with open('movie-list-check.txt', 'r') as rfile:
		lines = rfile.readlines()
	for line in lines:
		if movieid+'\n' == line:
			myembed.add_field(name = 'The movie is already in the suggestion list. Thank you.', value = 'You can suggest another movie for TFPS using !suggest.')
			await botmessage.edit(embed = myembed)
			return
	movie = ia.get_movie(movieid, info = ['main'])

	title = movie.get('title')
	movyear = movie.get('year')
	#tag = movie.get('taglines')[0]
	
	movieurl = 'https://www.imdb.com/title/tt' + movieid
	myembed.add_field(name = 'Do you want to say something about the movie?', value = '(Please type it at once in a single message) (Timeout: 120 secs)')
	await botmessage.edit(embed = myembed)
	try:
		msg = await client.wait_for('message',check = lambda message: message.author == ctx.author, timeout = 120)
	except asyncio.TimeoutError:
		content = ''
	else:
		content = msg.content
		content = content.encode('utf-8')
		await msg.delete()
	#imdburl = urllib.request.urlopen('https://www.imdb.com/title/tt' + movieid)
	#await ctx.send(imdburl)
	with open('movie-list-check.txt', 'a') as lfile:
		lfile.write(f'{movieid}\n')
	with open('movie-list.txt', 'a') as file:
		file.write(f'{title} ({movyear})\t{movieurl}\t{content}\n')
	myembed.clear_fields()
	myembed.add_field(name = f'{title} ({movyear})', value = 'The movie has been added to the TFPS suggestions list. Thank you.')
	await botmessage.edit(embed = myembed)
	await botmessage.delete(delay = 5)
	await ctx.send(f'{ctx.author.mention} gets two TFPS cookies \U0001F36A \U0001F36A for their film suggestion.')
	await add_cookies(ctx, ctx.author, 2)


@client.command()
async def helpme(ctx, metho = 'default'):
	myembed = discord.Embed(title = 'Help Commands', colour = discord.Colour.red(), description = 'Command Prefix = !')
	myembed.set_thumbnail(url = url)
	myembed.add_field(name = '!helpme', value = 'Displays the help', inline = False)
	myembed.add_field(name = '!there', value = 'Displays the helpChecks if the bot is online and returns the latency of the bot', inline = False)
	myembed.add_field(name = '!whois <@member-name>', value = 'Get the name from the username', inline = False)
	myembed.add_field(name = '!memlist', value = 'Get the entire member list', inline = False)
	myembed.add_field(name = '!giverole <@member-name>', value = 'Returns the current roles of the tagged member', inline = False)
	myembed.add_field(name = '!!assign <@member-name> <@role-name>', value = 'Assigns the tagged role to the tagged member (MODS only)', inline = False)
	myembed.add_field(name = '!unassign <@member-name> <@role-name>', value = 'Unassigns the tagged role from the tagged member (MODS only)', inline = False)
	myembed.add_field(name = '!ctext <movie-name>', value = 'Creates a channel for movie discussion in the appropriate category', inline = False)
	myembed.add_field(name = '!lsinactive <number of days>', value = 'Lists the channels inactive for more than the number of days entered by user', inline = False)
	myembed.add_field(name = '!archivech <#channel-name>', value = 'Archives the channel and returns a text file (also hides the channel) (MODS only)', inline = False)
	myembed.add_field(name = '!suggest <movie-name>', value = 'Takes a movie to be inserted into the TFPS movie suggestion database', inline = False)
	myembed.add_field(name = '!hangman', value = 'Starts a game of Hangman for movies', inline = False)
	
	myembed.add_field(name = '!recommend', value = 'Recommends three random movies from the coveted TFPS movie suggestion database with the IMDB link', inline = False)

	await ctx.send(embed = myembed)
	

@client.command()
async def whois(ctx, member: discord.Member):
	channel = get(ctx.guild.channels, name = 'welcome')
	messages = await channel.pins()
	for message in messages:
		if message.author == member:
			await ctx.send(f'{member.mention} is {message.content}')
			return
	channel = get(ctx.guild.channels, name = 'welcome2')
	messages = await channel.pins()
	for message in messages:
		if message.author == member:
			await ctx.send(f'{member.mention} is {message.content}')
			return
	await ctx.send(f'{member.mention} is not known. {member.mention} should type their full name in {channel.mention}')

@client.command()
async def memlist(ctx):
	persons = list()
	names = list()
	template = ''
	channel = get(ctx.guild.channels, name = 'welcome')
	messages = await channel.pins()
	for message in messages:
		persons.append(message.author.mention)
		names.append(message.content)
	channel = get(ctx.guild.channels, name = 'welcome2')
	messages = await channel.pins()
	for message in messages:
		persons.append(message.author.mention)
		names.append(message.content)
	
	for count in range(len(persons)):
		persona = persons[count]
		namea = names[count]
		template = template + f'{persona}, {namea}\n'
		if (count+1)%50 == 0 or count == len(persons)-1:
			await ctx.send(f'{template}')
			template = ''
			

@client.command()
async def hangman(ctx, member:discord.Member = None):
	if ctx.guild is None:
		await ctx.send(f'The game experience is better when not played on DMs')
	if member == ctx.author:
		await ctx.send('Get a life. You lose a TFPS cookie.')
		await add_cookies(ctx, ctx.author, -1)
		return
	def process(ctx, moviename, varstr):
		template = ''
		ctemp = ''
		for ch in moviename.lower():
			try:
				varstr.index(ch.lower())
				template = template + ch + ' '
				ctemp = ctemp + ch
			except:
				template = template + '-' + ' '
				ctemp = ctemp + '-'
		return template, ctemp
	ia = imdb.IMDb()
	
	if member is None:
		top250 = ia.get_top250_movies()
		rn = r.randrange(1,250)
		moviename = top250[rn].get('title')
		author = ctx.author
	else:
		await ctx.author.send('Tell me the name of the movie.')
		try:
			mn = await client.wait_for('message', check = lambda message: message.author == ctx.author and message.guild is None, timeout = 60)
		except asyncio.TimeoutError:
			await ctx.author.send('How slow are you? You lose one TFPS cookie')
			await(ctx, ctx.author,-1)
			return
		await ctx.send(f'{member.mention} show us what you got')
		moviename = mn.content
		author = member
		
	varstr = 'aeiou :\',;.0123456789äèéêö'
	template = process(ctx, moviename, varstr)		
	
	myembed = discord.Embed(title = f'Hangman (Movies)', description = 'Type the letter you want to guess, type the entire movie if you can guess. Either type the full movie name or individual letters . (Timeout = 10 seconds)', colour = discord.Colour.dark_orange())
	myembed.add_field(name = f'{template[0]}', value = '\u200b', inline = False)
	botmessage = await ctx.send(embed = myembed)
	count = 1
	wrong = '-'
	while(count <= 7):
		try:
			msg = await client.wait_for('message', check = lambda message: message.author == author, timeout = 10)
		except:
			await ctx.send('You lost on timeout. You lose a TFPS cookie')
			await add_cookies(ctx, author, -1)
			return
		content = msg.content.lower()
		try:
			await msg.delete()
		except:
			pass
		myembed.clear_fields()
		if content == moviename.lower():
			await ctx.send('Congrats babu bhaiya, you win! You get one TFPS cookie \U0001F36A')
			await add_cookies(ctx, author, 1)
			return
		elif len(content) > 1:
			await ctx.send(f'You lose because that is not the right guess. Sir phodd saale ka.\nThe movie is: {moviename}.\nYou lose a TFPS cookie.')
			await add_cookies(ctx, author, -1)
			return
		elif content in moviename.lower() and content not in 'aeiou ':
			for ch in moviename.lower():
				if content == ch:
					varstr = varstr + content
					template = process(ctx, moviename, varstr)
		else:
			completename = str(count-1)+'.png' 
			with open(completename, 'rb' ) as rfile:
				try:
					await botmessagepng.delete()
				except:
					pass
				botmessagepng = await ctx.send(file = discord.File(rfile, completename))
			wrong = wrong +'~~'+content+'~~' + ' '
			count += 1
		myembed.add_field(name = 'Wrong Tries', value = f'{wrong}')
		myembed.add_field(name = f'{template[0]}', value = '\u200b', inline = False)
		await botmessage.edit(embed = myembed)	

		if template[1] == moviename.lower():
			await ctx.send('Halkat! Jeet gaya re! You get one TFPS cookie \U0001F36A')
			await add_cookies(ctx, author, 1)

			return



	await ctx.send(f'*slaps* Ye babu bhai ka shtyle hai re.\nThe movie is: {moviename}.\nYou lose a TFPS cookie.')
	await add_cookies(ctx, author, -1)
	


@client.command()
async def cookiejar(ctx, member: discord.Member = None):
	loc = 'TFPS_cookiejar.xls'
	workbookr = xlrd.open_workbook(loc, encoding_override="cp1252")
	worksheetr = workbookr.sheet_by_index(0)
	if member is None:
		myembed = discord.Embed(title = f'{ctx.guild} Cookie Jar', description = f'Cookiest {ctx.guild} members', colour = discord.Colour.blue())
		myembed.set_thumbnail(url = url)
		
		ckdict = dict()
		for row in range(worksheetr.nrows):
			ckdict[str(worksheetr.cell(row,0).value)] = int(worksheetr.cell(row,1).value)

		sortckdict = sorted(ckdict.items(), key = lambda x: x[1], reverse = True)
		count = 0
		
		for item in sortckdict:
			count = count +1
			member = ctx.guild.get_member(int(item[0]))
			val = item[1]
			if count == 1:
				myembed.add_field(name = f'\U0001F947  {member.name} - {val} cookies', value = '\u200b', inline = False)
			elif count == 2:
				myembed.add_field(name = f'\U0001F948  {member.name} - {val} cookies', value = '\u200b', inline = False)
			elif count == 3:
				myembed.add_field(name = f'\U0001F949  {member.name} - {val} cookies', value = '\u200b', inline = False)
			else:	
				myembed.add_field(name = f'\U0001F396  {member.name} - {val} cookies', value = '\u200b', inline = False)
			if count == 5:
				break

		await ctx.send(embed = myembed)
	else:
		myembed = discord.Embed(title = f'{member.name}\'s Cookie Jar', colour = discord.Colour.blue())
		myembed.set_thumbnail(url = url)
		for row in range(worksheetr.nrows):
			if str(member.id) == str(worksheetr.cell(row,0).value):
				val = int(worksheetr.cell(row,1).value)

		myembed.add_field(name = f'{member.name} - {val} cookies', value = '\u200b', inline = False)
		await ctx.send(embed = myembed)


@client.command()
async def recommend(ctx):
	read1 = list()
	with open('movie-list.txt', 'r') as rfile:
		read1 = rfile.readlines()
	with open('movie-list-check.txt', 'r') as rfile:
		read2 = rfile.readlines()

	
	ia = imdb.IMDb()
	#print(type(read1[3]))			
	rn = r.randrange(1,len(read1))
	
	
	movie = ia.get_movie(read2[rn])
	read = read1[rn].split('\t')
	says = read[2][2:-2]
	
	directors = ''
	try:
		for director in movie['directors']:
			if directors != '':
				directors = directors + ', '
			directors = directors + director['name']
	except:
		directors = 'Visit IMDB to find out'
	genres = ''
	try:
		for genre in movie['genres']:
			if genres != '':
				genres = genres + ', '
			genres = genres + genre 
	except: 
		genres = 'Visit IMDB to find out'
	rating = movie['rating']
	myembed = discord.Embed(title = f'{read[0]}', colour = discord.Colour.teal(), url = f'{read[1]}', description = 'Click on the movie name to visit the IMDB page')
	myembed.set_thumbnail(url = url)
	myembed.add_field(name = f'Directors', value = f'{directors}', inline = True)
	myembed.add_field(name = f'Genres', value = f'{genres}', inline = True)
	myembed.add_field(name = f'IMDB Rating', value = f'{rating}', inline = True)
	myembed.add_field(name = f'A TFPS member says:', value = f'\'{says}\'', inline = False)
	if await add_cookies(ctx,ctx.author, -2):
		await ctx.author.send(embed = myembed)
		await ctx.send(f'{client.user.mention} whispered the recommendation to {ctx.author.mention} costing 2 cookies')
	else: 
		await ctx.send(f'You don\'t have enough cookies')
	#await ctx.send(f'This is said: {read[2][1:]}')
''''@client.command()
@commands.has_role('MODS')
async def givenow(ctx, channel: discord.TextChannel):
    save_path = 'E:\\bots\Archived TFPS'
    completeName = os.path.join(save_path, channel.name+".txt")
    await ctx.send(file = discord.File(completeName, channel.name+'.txt'))'''

@client.command()
@commands.has_role('MODS')
async def loancookies(ctx, member: discord.Member, amount = 2):
	if ctx.author.id != 734071050811474002:
		return
	else:
		await add_cookies(ctx, member, amount)
		await ctx.channel.purge(limit = 1)




client.run(token)

