import discord
from discord import ClientException
from discord.ext import commands
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

discord.opus.load_opus(name='/opt/homebrew/lib/libopus.dylib')
TOKEN = 'MTE4OTY2MTc5MzM2NzM3OTk2OA.GTPMqM.NdktxOc-GvgF8ZXry6GZtGnDYQOBe2jBP7_hUA'
YDL_OPTS = {'format': 'bestaudio/best'}

bot = commands.Bot(command_prefix="/", intents=discord.Intents().all())
queue = []
is_paused = False

# @bot.event
# async def on_ready():
#     await bot.send("Hello!")

#searches songs from youtube
def search_song(input):
    search = VideosSearch(input, limit = 1)
    return {'url': search.result()['result'][0]["link"], 'title': search.result()['result'][0]['title']}

#checks to see that queue is not empty and continues playing the songs
async def play_song(voice_channel):
    while len(queue) != 0:
        with YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(queue.pop(0)['url'], download=False)
            url = info['url']
            voice_channel.play(discord.FFmpegPCMAudio(url))

#searches a song plays if no songs in queue otherwise places it in queue
@bot.command(name='play', aliases=['p'])
async def play(ctx, input=None):
    if input == None:
        await ctx.send("Enter A Song")
    else:
        query = "".join(input)
        song = search_song(query)
        queue.insert(0,song)
    try:
        channel = ctx.author.voice.channel
    except:
        await ctx.send("Connect To Voice Channel First")
    try:
        voice_channel = await channel.connect()
        ctx.voice_client.stop()
        play_song(voice_channel)
    except ClientException:
        ctx.voice_client.stop()
        play_song(ctx.voice_client)

#pause and resume command
@bot.command(name="pause", aliases=['resume', 'r'])
async def pause(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.pause()
    else:
        ctx.voice_client.resume()



bot.run(TOKEN)