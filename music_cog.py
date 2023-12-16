import discord
from discord_components import Select, SelectOption, Button
from discord.ext import commands
import asyncio
from asyncio import run_coroutine_threadsafe
from urllib import parse, request
import re
import json
import os
from youtube_dl import YoutubeDL

class MusicCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.is_playing = {}
        self.is_paused = {}
        self.musicQueue = {}
        self.queueIndex = {}

        self.vc = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.musicQueue[id] = []
            self.queueIndex[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False
