import nextcord
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
import os
import youtube_dl

intents = nextcord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True
queues = {}

client = commands.Bot(command_prefix='!', intents=intents)

with open('token.txt', 'r') as file:
    token = file.readline()

async def check_queue(ctx, guild_id):
    if queues[guild_id] and not ctx.voice_client.is_playing():
        source = queues[guild_id].pop(0)

        try:
            player = ctx.voice_client.play(source, after=lambda x=None: check_queue(ctx, guild_id))
            await ctx.send(f"Playing **{source.title}**")
        except Exception as e:
            await ctx.send("An error occurred while playing the audio: {}".format(e))


def find_join_channel(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).view_audit_log:
            return channel
    return None

def is_connected(ctx):
    voice_client = nextcord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

@client.event
async def on_ready():
    print(f"Bot is ready")
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="a bunch of songs"))

@client.command()
async def hello(ctx):
    await ctx.send(os.path.dirname(os.path.abspath(__file__)))

@client.event
async def on_member_join(member):
    join_channel = find_join_channel(member.guild)  # Find channel locally
    if join_channel:
        await join_channel.send(f"Have a nice stay, good luck {member.mention}!")
    else:
        print("No suitable channel found for join messages.")

@client.event
async def on_member_remove(member):
    join_channel = find_join_channel(member.guild)  # Find channel locally
    if join_channel:
        await join_channel.send(f"You will not be missed {member.mention}.")
    else:
        print("No suitable channel found for remove messages.")

@client.command(pass_context=True)
async def join(ctx):
    print("We got here at least")
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()

    else:
        await ctx.send("You are not in a voice channel.")

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect(force=True)
        await ctx.send("Steve left the voice channel.")
    else:
        await ctx.send("Steve is not in a voice channel")

@client.command(pass_context=True)
async def pause(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Steve is not playing any audio.")

@client.command(pass_context=True)
async def resume(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Steve did not find any audio currently paused.")

@client.command(pass_context=True)
async def stop(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild= ctx.guild)
    voice.stop()

@client.command(pass_context=True)
async def play(ctx, *, query):
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': 'True'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info("ytsearch:{}".format(query), download=False)
            url = info['entries'][0]['url']  # Use the first result

            # Extract audio using youtube-dl
            info = ydl.extract_info(url, download=False)
            source = FFmpegPCMAudio(info['url'])
        except Exception as e:
            print(e)
            return

        guild_id = ctx.message.guild.id
        voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)

        if not voice:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
                voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
            else:
                await ctx.send("You are not in a voice channel.")
                return

        try:
            player = voice.play(source, after=lambda x=None: check_queue(ctx, guild_id))
            await ctx.send(f"Playing **{query}**")
        except Exception as e:
            print("An error occurred while playing the audio: {}".format(e))


@client.command(pass_context=True)
async def queue(ctx, *, query):
    guild_id = ctx.message.guild.id

    if guild_id not in queues:
        queues[guild_id] = []

    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': 'True'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info("ytsearch:{}".format(query), download=False)
            url = info['entries'][0]['url']  # Use the first result

            # Extract audio using youtube-dl
            info = ydl.extract_info(url, download=False)
            source = FFmpegPCMAudio(info['url'])
        except Exception as e:
            print(e)
            return

        queues[guild_id].append(source)
        await ctx.send(f"Added **{query}** to the queue. Position in queue: {len(queues[guild_id]) - 1}")

        # If not currently playing, start playing the next in queue
        await check_queue(ctx, guild_id)

@client.command(pass_context=True)
async def skip(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        voice.stop()
        await ctx.send("Skipped the current song. Playing next song in the queue.")
    else:
        await ctx.send("There is no song currently playing.")


client.run(token)