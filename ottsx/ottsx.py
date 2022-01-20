# This is actually the first thing I have ever done in python so, yay!
# Let's ignore the large amount of copy-paste, I needed an example
# I typed it all so I can learn as I go through it

from redbot.core import commands
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from py1337x import py1337x

class ottsx(commands.Cog):
    """
    My custom cog
    """

    def __init__(self, bot):
        self.bot = bot


    @commands.group()
    @commands.guild_only()
    async def ottsx(self, ctx):
        """Search 1337x.to."""

    @ottsx.command()
    async def lookup(self, ctx, *, query: str):
        """Search all of 1337x."""
        # credit: https://github.com/TheWyn/Wyn-RedV3Cogs/blob/master/nyaa/nyaa.py
        count = "20"
        pages = []
        try:
            async with ctx.typing():
                clientX = py1337x(proxy='1337x.to', cache='~git/REDBOT_1337X_CACHE', cacheTime=500)
                result = clientX.search(query)['items']
                msg = ""
            if len(result) < int(count):
                count = len(result)
                for res in result[0:int(count):]:
                    msg += "``` Name: " + res['name'] + "\n" + \
                           "Uploader: " + res['uploader'] + "\n" + \
                           "Url: " + res['link'] + "\n" + \
                           "Size: " + res['size'] + " --- " + \
                           "Date: " + res['time'] + " --- " + \
                           "Seeders: " + res['seeders'] + " --- " + \
                           "Leechers: " + res['leechers'] + "\n```"
                    pages.append(msg)
                    msg = ""
            else:
                for res in result[0:int(count):]:
                    msg += "```Name: " + res['name'] + "\n" + \
                           "Uploader: " + res['uploader'] + "\n" + \
                           "Url: " + res['link'] + "\n" + \
                           "Size: " + res['size'] + " --- " + \
                           "Date: " + res['time'] + " --- " + \
                           "Seeders: " + res['seeders'] + " --- " + \
                           "Leechers: " + res['leechers'] + "\n```"
                    pages.append(msg)
                    msg = ""
            await menu(ctx, pages, DEFAULT_CONTROLS)
        except AttributeError:
            await ctx.send(show_name + " not found.")