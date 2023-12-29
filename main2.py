import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import os

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
queues = {}

client = commands.Bot(command_prefix='!', intents=intents)

with open('token.txt', 'r') as file:
    token = file.readline()

def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_client
        source = queues[id].pop(0)
        player = voice.play(source)
def find_join_channel(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).view_audit_log:
            return channel
    return None

def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

@client.event
async def on_ready():
    print(f"Bot is ready as {client}")

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
    if (ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        file = os.path.dirname(os.path.abspath(__file__))
        source = FFmpegPCMAudio(f"{file}/lean.mp3")
        player = voice.play(source)
    else:
        await ctx.send("You are not in a voice channel.")

@client.command(pass_context=True)
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Steve left the voice channel.")
    else:
        await ctx.send("Steve is not in a voice channel")

@client.command(pass_context=True)
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("Steve is not playing any audio.")

@client.command(pass_context=True)
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("Steve did not find any audio currently paused.")

@client.command(pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild= ctx.guild)
    voice.stop()

@client.command(pass_context=True)
async def play(ctx, arg):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        print(is_connected(ctx))
        if is_connected(ctx) != True:
            voice = await channel.connect()
        else:
            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    file = os.path.dirname(os.path.abspath(__file__))
    source = FFmpegPCMAudio(f"{file}/{arg}.mp3")
    player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))

@client.command(pass_context=True)
async def queue(ctx, arg):
    voice = ctx.guild.voice_client
    file = os.path.dirname(os.path.abspath(__file__))
    source = FFmpegPCMAudio(f"{file}/{arg}.mp3")
    guild_id = ctx.message.guild.id
    if guild_id in queues:
        queues[guild_id].append(source)

    else:
        queues[guild_id] = [source]

    await ctx.send("Song added to the queue.")

client.run(token)