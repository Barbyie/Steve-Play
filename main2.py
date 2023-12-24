import discord
from discord.ext import commands

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
@client.command()
async def hello(ctx):
    await ctx.send("Testing Steve.")

@client.event
async def on_member_join(member):
    if join_channel:
        await join_channel.send(f"Have a nice stay, good luck {member.mention}!")
    else:
        print("No suitable channel found for join messages.")

client.run(token)




