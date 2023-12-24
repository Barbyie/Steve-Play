import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import os

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix= '!', intents=intents)

with open('token.txt', 'r') as file:
    token = file.readline()

@client.event
async def on_ready():
    global join_channel

    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages and channel.permissions_for(guild.me).view_audit_log:
                try:
                    join_channel = channel
                    break
                except discord.Forbidden:
                    pass
    print("Bot is ready")
@client.command()
async def hello(ctx):
    await ctx.send(os.path.dirname(os.path.abspath(__file__)))
@client.event
async def on_member_join(member):
    if join_channel:
        await join_channel.send(f"Have a nice stay, good luck {member.mention}!")
    else:
        print("No suitable channel found for join messages.")

@client.event
async def on_member_remove(member):
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
    if (ctx.voice_client):
        await ctx.guild.voice_client.disconnect(force=True)
        await ctx.send("Steve left the voice channel.")
    else:
        await ctx.send("Steve is not in a voice channel")

client.run(token)




