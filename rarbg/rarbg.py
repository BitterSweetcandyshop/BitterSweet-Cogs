import re
import math
import json
import aiohttp
import discord
import requests
from time import sleep
from bs4 import BeautifulSoup
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu


async def shorten(self, magnet: str):
    res = False
    async with aiohttp.ClientSession() as session:
        async with session.get("http://mgnet.me/api/create?&format=json&opt=&m={}".format(magnet)) as response:
            res = await response.read()
    res = json.loads(res)
    return res["shorturl"]

class rarbg(commands.Cog):
    """
    Search Rarbg.
    """

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(rarbg_smartlink_enabled=False)
        self.conf.register_guild(rarbg_token="")

    @commands.group(aliases=["r"])
    @commands.guild_only()
    async def rarbg(self, ctx):
        """Search Rarbg"""

    @rarbg.command(aliases=["quicksearch", "q", "qs", "quicklookup", "ql"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def quick(self, ctx, *, query: str):
        """Quicky search rarbg for torrents"""
        try:
            def format_bytes(size):
                power = 2**10
                n = 0
                power_labels = {0 : '', 1: 'Kb', 2: 'Mb', 3: 'GB', 4: 'Tb'}
                while size > power:
                    size /= power
                    n += 1
                return (str(math.ceil(size)) + " " + power_labels[n])

            async with ctx.typing():
                results = await self.rarbg_search(query, ctx.guild)
                if not len(results): return await ctx.send(f"Sorry, no results for **{query}**")
                format = []
                for i, res in enumerate(results):
                    if i > 9: break
                    format.append(f"""
                    **{i+1}. [{res['title']}]({res['info_page']})**
                    **[Magnet]({await shorten(self, res["download"])})** | Seeders: {res['seeders']} | Size: {format_bytes(res['size'])} 
                    """)

                embed = discord.Embed(
                    description="".join(format)
                )
                embed = embed.set_author(
                        name=ctx.author.display_name,
                        icon_url=ctx.author.avatar_url
                )

                await ctx.send(content="", embed=embed)
            
        except AttributeError:
            await ctx.send(f"Sorry, no results for **{query}** or there was an error.")


    @rarbg.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx):
        """
        Smartlink for Rarbg makes it so whenever a link is sent in an enabled channel.
        It will fetch data off rarbg about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to toggle.
        """

        current_status = await self.conf.channel(ctx.channel).rarbg_smartlink_enabled()
        
        await self.conf.channel(ctx.channel).rarbg_smartlink_enabled.set(not current_status)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @commands.Cog.listener()
    async def on_message(self, message):
        torrent_link = re.search(r'https?:\/\/(?:www\.)?nyaa\.\w{2}\/view\/\S+', message.content)
        if not torrent_link: return
        torrent_link = torrent_link.group()

        smartlink_enabled = await self.conf.channel(message.channel).rarbg_smartlink_enabled()
        if not smartlink_enabled: return

        torrent = self.single_nyaa(torrent_link)
        embed = await self.make_embed(torrent)

        await message.channel.send(content="", embed=embed)

    async def rarbg_search(self, query, guild, **kwargs):
        """
        Return a list of dicts with the results of the query.
        """

        token = kwargs.get("token", False)
        if not token:
            token = await self.conf.guild(guild).rarbg_token()
        r = requests.get(f"https://torrentapi.org/pubapi_v2.php?mode=search&search_string={query}&token={token}&app_id=torrent-api&format=json_extended&sort=seeders").json()
        
        if len(r.keys()) > 1:
            if r['error_code'] == 20: return []

            new_token = requests.get("https://torrentapi.org/pubapi_v2.php?get_token=get_token&app_id=torrent-api").json()['token']
            token = await self.conf.guild(guild).rarbg_token.set(new_token)
            sleep(3)
            return await self.rarbg_search(query, guild, token=token)

        else:
            return r['torrent_results']