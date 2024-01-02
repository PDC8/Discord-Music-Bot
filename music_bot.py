import discord
from discord import ClientException
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

discord.opus.load_opus(name='/opt/homebrew/lib/libopus.dylib')
TOKEN = 'MTE4OTY2MTc5MzM2NzM3OTk2OA.G1x2FC.lXlpZBTC2-Zmzn19BgBy867ZqzGljg-FI_1f5o'
YDL_OPTS = {'format': 'bestaudio'}
FFMPEG_OPTIONS = {"before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
 "options": "-vn"}

bot = commands.Bot(command_prefix="/", intents=discord.Intents().all())
music_queue = []

# @bot.event
# async def on_ready():
#     await bot.send("Hello!")

#searches songs from youtube
def search_song(input):
    search = VideosSearch(input, limit = 1)
    return {'url': search.result()['result'][0]["link"], 'title': search.result()['result'][0]['title']}

#checks to see that queue is not empty and continues playing the songs
def play_song(voice_channel):
    if len(music_queue) != 0:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(music_queue.pop(0)['url'], download=False)
            url = info['url']
            voice_channel.play(discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS), after= lambda e: play_song(voice_channel))

#searches a song and plays if no songs in queue otherwise places it in queue
@bot.command(name='play', aliases=['p'])
async def play(ctx, *input):
    if len(input) == 0:
        await ctx.send("Enter A Song")
    else:
        query = "".join(input)
        song = search_song(query)
        music_queue.append(song)

    try:
        channel = ctx.author.voice.channel
    except:
        await ctx.send("Connect To Voice Channel First")
    
    _channel = None
    try:
        voice_channel = await channel.connect()
        _channel = voice_channel
    except ClientException:
        _channel = ctx.voice_client

    if not ctx.voice_client.is_playing():
        play_song(_channel)

#pause and resume command
@bot.command(name="pause", aliases=['resume', 'r'])
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
    else:
        ctx.voice_client.resume()

#skips the current song
@bot.command(name='skip', aliases=['s'])
async def skip(ctx):
    ctx.voice_client.stop()
    play_song(ctx.voice_client)
    
#show queued songs
@bot.command(name='queue', aliases=['q'])
async def queue(ctx):
    if len(music_queue) != 0:
        count = 1
        for x in range(0,len(music_queue)):
            await ctx.send(f'{count}. ' + music_queue[x]['title'])
            count +=1
    else:
        await ctx.send('No Songs in Queue')

#clear queue
@bot.command(name='clear', aliases=['c'])
async def clear(ctx):
    ctx.voice_client.stop()
    music_queue.clear()
    await ctx.send("Muisc Queue Cleared")

#remove last song from queue
@bot.command(name= 'remove', aliases=['re'])
async def remove(ctx):
    if len(music_queue) != 0:
        await ctx.send('Removed: ' + music_queue.pop(-1)['title'])
    else:
        await ctx.send('No Songs to Remove')

#disconnects the bot
@bot.command(name='disconnect', aliases=['dc', 'leave'])
async def disconnect(ctx):
    await ctx.voice_client.disconnect()

bot.run(TOKEN)