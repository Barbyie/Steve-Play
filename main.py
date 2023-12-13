from discord_components import ComponentsBot
from music_cog import MusicCog

bot = ComponentsBot(command_prefix='!')

bot.add_cog(MusicCog(bot))

with open('token.txt', 'r') as file:
    token = file.readline()

bot.run(token)
