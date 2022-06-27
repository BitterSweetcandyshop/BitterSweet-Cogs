import re
import json
import discord
import aiohttp
from bs4 import BeautifulSoup
from redbot.core import commands, Config, checks
from requests_futures.sessions import FuturesSession
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

from nyaa.utils import Utils as uTils


async def shorten(self, magnet: str):
    res = False
    async with aiohttp.ClientSession() as session:
        async with session.get("http://mgnet.me/api/create?&format=json&opt=&m={}".format(magnet)) as response:
            res = await response.read()
    res = json.loads(res)
    return res["shorturl"]

class Nyaa(commands.Cog):
    """Obtain torrents from nyaa."""

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(nyaa_smartlink_enabled=False)

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    def search(self, keyword, **kwargs):
        """
         Return a list of dicts with the results of the query.
        """
        category = kwargs.get('category', 0)
        subcategory = kwargs.get('subcategory', 0)
        filters = kwargs.get('filters', 0)
        page = kwargs.get('page', 0)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        session = FuturesSession()

        if page > 0:
            r = session.get(
                "http://nyaa.si/?f={}&c={}_{}&q={}&p={}&o=desc&s=seeders".format(filters, category, subcategory,
                                                                                 keyword, page), headers=headers)
        else:
            r = session.get(
                "http://nyaa.si/?f={}&c={}_{}&q={}&o=desc&s=seeders".format(filters, category, subcategory,
                                                                            keyword), headers=headers)

        soup = BeautifulSoup(r.result().text, 'html.parser')
        rows = soup.select('table tr')

        results = {}

        if rows:
            results = uTils.parse_nyaa(rows, limit=11)

        return results

    @commands.group()
    @commands.guild_only()
    async def nyaa(self, ctx):
        """Search anime."""


    @nyaa.command(aliases=['search', 's'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def lookup(self, ctx, *, show_name: str):
        """
        Returns torrents from search.
        User arguments - Search query to send for results.

        Example: [p]nyaa lookup tokyo ghoul
        """
        try:
            async with ctx.typing():
                result = self.search(show_name)
                count = len(result)
                pages = []

                #if not result: return await ctx.send(f"There was no results for `{show_name}`")
                for res in result[0:count:]:
                    page = await self.make_embed(res, 1, count)
                    pages.append(page)

                await menu(ctx, pages, DEFAULT_CONTROLS)
        except AttributeError:
            await ctx.send(show_name + " not found.")




    @nyaa.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx):
        """
        Smartlink for Nyaa makes it so whenever a link is sent in an enabled channel.
        It will fetch data off nyaa about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to toggle.
        """

        current_status = await self.conf.channel(ctx.channel).nyaa_smartlink_enabled()
        
        await self.conf.channel(ctx.channel).nyaa_smartlink_enabled.set(not current_status)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @commands.Cog.listener()
    async def on_message(self, message):
        torrent_link = re.search(r'https?:\/\/(?:www\.)?nyaa\.\w{2}\/view\/\S+', message.content)
        if not torrent_link: return
        torrent_link = torrent_link.group()

        smartlink_enabled = await self.conf.channel(message.channel).nyaa_smartlink_enabled()
        if not smartlink_enabled: return

        torrent = self.single_nyaa(torrent_link)
        embed = await self.make_embed(torrent)

        await message.channel.send(content="", embed=embed)


    def single_nyaa(self, link:str):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        session = FuturesSession()

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.result().text, 'html.parser')
        target = soup.select('body div div div [class="row"]')
        header = soup.select('[class="panel-title"]')
        footer = soup.select('[class="panel panel-danger"] [class="panel-footer clearfix"] a')

        return uTils.single_parse(header, target, footer, link)


    async def make_embed(self, res, i:int=0, count:int=1):
        embed = discord.Embed(
            title=res["name"],
            url=res["url"],
            description=f"""
            **Posted on** *{res['date']}*
            **Magnet Link** ||*{await shorten(self, res["magnet"])}*||
            """
        )
        embed.add_field(
            name="Size",
            value=res["size"],
            inline=True
        )
        embed.add_field(
            name="Seeders",
            value=res["seeders"],
            inline=True
        )
        embed.add_field(
            name="Leechers",
            value=res["leechers"],
            inline=True
        )
        embed.set_footer(
            text=f"page: ({str(i+1)}/{str(count)})"
        )
        embed = embed.set_thumbnail(
            url=f"https://nyaa.si/static/img/icons/nyaa/{res['categoryRaw']}.png"
        )

        return embed