import nextcord
from nextcord.ext import commands
from nextcord import FFmpegPCMAudio
import youtube_dl

# Set up Discord bot with necessary intents
intents = nextcord.Intents.default()
intents.voice_states = True
intents.message_content = True
intents.members = True
queues = {}

client = commands.Bot(command_prefix='!', intents=intents)

# Read the bot token from the 'token.txt' file
with open('token.txt', 'r') as file:
    token = file.readline()

# Function to check and play the next audio in the queue
async def check_queue(ctx, guild_id):
    if queues[guild_id] and not ctx.voice_client.is_playing():
        source = queues[guild_id].pop(0)

        try:
            player = ctx.voice_client.play(source, after=lambda x=None: check_queue(ctx, guild_id))
            await ctx.send(f"Steve is playing **{source.title}** now.")
        except Exception as e:
            await ctx.send("Uh-oh! Steve encountered an error while playing the audio: {}".format(e))

# Function to find a suitable text channel for join and leave messages
def find_join_channel(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).view_audit_log:
            return channel
    return None

# Event triggered when the bot is ready
@client.event
async def on_ready():
    print(f"Steve is ready! Let the music begin.")
    await client.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.listening, name="a bunch of songs"))

# Event triggered when a new member joins the server
@client.event
async def on_member_join(member):
    join_channel = find_join_channel(member.guild)
    if join_channel:
        await join_channel.send(f"Welcome, {member.mention}! Steve hopes you have a nice stay and good luck.")
    else:
        print("No suitable channel found for join messages.")

# Event triggered when a member leaves the server
@client.event
async def on_member_remove(member):
    join_channel = find_join_channel(member.guild)
    if join_channel:
        await join_channel.send(f"Farewell, {member.mention}. You will not be missed by Steve.")
    else:
        print("No suitable channel found for remove messages.")

# Command to make the bot join a voice channel
@client.command(pass_context=True)
async def join(ctx):
    print("Steve is here now! Ready to join the voice channel.")
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
    else:
        await ctx.send("You need to be in a voice channel for Steve to join!")

# Command to make the bot leave the voice channel
@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect(force=True)
        await ctx.send("Steve left the voice channel.")
    else:
        await ctx.send("Steve is not in a voice channel")

# Command to pause the currently playing audio
@client.command(pass_context=True)
async def pause(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Steve is not playing any audio.")

# Command to resume the paused audio
@client.command(pass_context=True)
async def resume(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Steve did not find any audio currently paused.")

# Command to stop playing the audio
@client.command(pass_context=True)
async def stop(ctx):
    voice = nextcord.utils.get(client.voice_clients, guild= ctx.guild)
    voice.stop()

# Command to play audio from YouTube
@client.command(pass_context=True)
async def play(ctx, *, query):
    ydl_opts = {'format': 'bestaudio/best', 'noplaylist': 'True'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info("ytsearch:{}".format(query), download=False)
            url = info['entries'][0]['url']  # Use the first result
            video_title = info.get('title', 'Unknown Title')

            # Extract audio using youtube-dl
            info = ydl.extract_info(url, download=False)
            source = FFmpegPCMAudio(info['formats'][0]['url']) if 'formats' in info and info['formats'] else None
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

        embed = nextcord.Embed(
            title='Playing 🎵',
            description=f'**Title:** {video_title}'
        )

        try:
            player = voice.play(source, after=lambda x=None: check_queue(ctx, guild_id)) if source else None
            await ctx.send(embed=embed)
        except Exception as e:
            print("An error occurred while playing the audio: {}".format(e))


# Command to add a song to the queue
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
            song_title = info['title']
        except Exception as e:
            print(e)
            return

        queues[guild_id].append(source)
        await ctx.send(f"Added **{song_title}** to the queue. Position in queue: {len(queues[guild_id]) - 1}")

        # If not currently playing, start playing the next in queue
        await check_queue(ctx, guild_id)

client.run(token)