import re
import json
import discord
import aiohttp
import requests
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
    """Obtain torrents from nyaa.si."""

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(nyaa_smartlink_enabled=False)
        self.conf.register_channel(anilink=False)
        self.conf.register_guild(bans=['yify'])

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def nyaa(self, ctx, *, query:str):
        """Search anime."""
        try:
            async with ctx.typing():
                bans = await self.conf.guild(ctx.guild).bans()
                results = self.search(query, bans=bans)
                count = len(results)
                if not count: return await ctx.send(f"There was no results for `{query}`")
                format=[]
                for i, res in enumerate(results):
                    format.append(f"""
                    **{i+1}. [{res['name']}]({res['url']})**
                    **[Magnet]({await shorten(self, res["magnet"])}) - [Torrent]({res['download_url']})** | Seeders: {res['seeders']} | Size: {res['size']} 
                    """)

                embed = discord.Embed(
                    description="".join(format)
                )
                embed = embed.set_author(
                        name=ctx.author.display_name,
                        icon_url=ctx.author.avatar_url
                )

                await ctx.send(embed=embed)
        except AttributeError:
            await ctx.send(query + " Not found.")


    @nyaa.command(aliases=['search', 's'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def lookup(self, ctx, *, show_name: str):
        """
        Return torrents from search.
        User arguments - Search query to send for results.

        Example: [p]nyaa lookup tokyo ghoul
        """
        try:
            async with ctx.typing():
                bans = await self.conf.guild(ctx.guild).bans()
                result = self.search(show_name, bans=bans, limit=10)
                count = len(result)
                if not count: return await ctx.send(f"There was no results for `{show_name}`")
                pages = []

                #if not result: return await ctx.send(f"There was no results for `{show_name}`")
                for res in result[0:count:]:
                    page = await self.make_embed(res, 1, count)
                    pages.append(page)

                await menu(ctx, pages, DEFAULT_CONTROLS)
        except AttributeError:
            await ctx.send(show_name + " Not found.")




    @nyaa.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx):
        """
        Smartlink for Nyaa makes it so whenever a link is sent in an enabled channel. \
        It will fetch data off nyaa about the torrent.
        _ _
        Run the command in the channel you want enabled/disabled to toggle.
        """

        current_status = await self.conf.channel(ctx.channel).nyaa_smartlink_enabled()
        
        await self.conf.channel(ctx.channel).nyaa_smartlink_enabled.set(not current_status)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @nyaa.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def anilink(self, ctx):
        """
        Anilink for Nyaa makes it so whenever a AniList is sent in an enabled channel. \
        It will fetch the first result from Nyaa about the anime.
        _ _
        Run the command in the channel you want enabled/disabled to toggle.
        """

        current_status = await self.conf.channel(ctx.channel).anilink()
        
        await self.conf.channel(ctx.channel).anilink.set(not current_status)
        await ctx.send("The channel **{}** now has anilink as **{}**.".format(ctx.channel.name, not current_status))

    @commands.Cog.listener()
    async def on_message(self, message):
        # Nyaa
        torrent_link = re.search(r'https?:\/\/(?:www\.)?nyaa\.\w{2}\/view\/\S+', message.content)
        if torrent_link:
            torrent_link = torrent_link.group()

            smartlink_enabled = await self.conf.channel(message.channel).nyaa_smartlink_enabled()
            if not smartlink_enabled: return

            torrent = self.single_nyaa(torrent_link)
            embed = await self.make_embed(torrent)

            return await message.channel.send(embed=embed)

        #Ani List
        anilink = re.search(r'https?:\/\/(?:www\.)?anilist\.co\/anime\/\S+', message.content)
        if anilink:

            anilink_enabled = await self.conf.channel(message.channel).anilink()
            if not anilink_enabled: return

            anilink = anilink.group()
            print(anilink)
            id = anilink.split("anime/")[1].split("/")[0]
            anime = self.get_ani(int(id))
            if anime.get('errors'):
                return await message.add_reaction("❌")
            
            anime = anime['data']['Media']['title']

            nyaa_res = self.search((anime['romaji'] or anime['english']), limit=1)
            if len(nyaa_res) < 1: return await message.add_reaction("❌")
            embed = await self.make_embed(nyaa_res[0])
            
            await message.channel.send(embed=embed)

    def get_ani(self, id:int):
        query = """
query ($id: Int) {
    Media (id: $id, type: ANIME) {
        id
        title {
            romaji
            english
            native
        }
    }
}
"""
        return requests.post('https://graphql.anilist.co', json={'query': query, 'variables': {'id': id}}).json()


    # Ban commands
    @nyaa.group()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def ban(self, ctx):
        """Mange banned phrases. All bans will be checked for in the uploader and torrent name

The ban list ONLY applies to search commands."""

    @ban.command()
    async def add(self, ctx, *, target:str):
        """Add a ban"""
        db_bans = await self.conf.guild(ctx.guild).bans()
        if db_bans.count(target.lower()): return await ctx.send(f"{target} is already on the ban list.")
        db_bans.append(target.lower())
        await self.conf.guild(ctx.guild).bans.set(db_bans)
        if not len(db_bans): return await ctx.send(f"Added {target} to the ban list.")
        await ctx.send(f"Added {target} to the ban list.\nCurrent bans: {', '.join(db_bans)}")

    @ban.command(aliases=['del', 'delete', 'rem'])
    async def remove(self, ctx, *, target:str):
        """Remove a ban"""
        db_bans = await self.conf.guild(ctx.guild).bans()
        try:
            db_bans.remove(target.lower())
        except:
            return await ctx.send(f"{target} is not on the ban list.")
        await self.conf.guild(ctx.guild).bans.set(db_bans)
        if not len(db_bans): return await ctx.send(f"Ban list is now empty")
        await ctx.send(f"Added {target} to the ban list.\nCurrent bans: {', '.join(db_bans)}")

    @ban.command()
    async def list(self, ctx):
        """List all current bans"""
        db_bans = await self.conf.guild(ctx.guild).bans()
        if not len(db_bans): return await ctx.send(f"Ban list is empty")
        await ctx.send(f"Current bans: {', '.join(db_bans)}")



    def single_nyaa(self, link:str):
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        session = FuturesSession()

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.result().text, 'html.parser')
        target = soup.select('body div div div [class="row"]')
        header = soup.select('[class="panel-title"]')
        footer = soup.select('[class="panel panel-danger"] [class="panel-footer clearfix"] a')

        return uTils.single_parse(header, target, footer, link)


    def search(self, keyword, **kwargs):
        """
         Return a list of dicts with the results of the query.
        """
        bans = kwargs.get('bans', [])
        category = kwargs.get('category', 0)
        subcategory = kwargs.get('subcategory', 0)
        filters = kwargs.get('filters', 0)
        page = kwargs.get('page', 0)
        limit = kwargs.get('limit', 11)
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
            results = uTils.parse_nyaa(rows, limit, bans)

        return results


    async def make_embed(self, res, i:int=0, count:int=1):
        author = ""
        if res['uploader']:
            author = f"\n**Uploader**: *[{res['uploader']}]({res['uploaderLink']})*"

        embed = discord.Embed(
            title=res["name"],
            url=res["url"],
            description=f"""
            **Posted on** *{res['date']}*{author}
            **Download** *[Magnet]({await shorten(self, res['magnet'])}) [Torrent]({res['download_url']})*
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