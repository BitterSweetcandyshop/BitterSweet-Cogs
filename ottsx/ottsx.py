# This is actually the first thing I have ever done in python so, yay!
# Let's ignore the large amount of copy-paste, I needed an example
# I typed it all so I can learn as I go through it
import re
import json
import aiohttp
import discord
from ottsx.utils import uTils
from py1337x import py1337x
from bs4 import BeautifulSoup
from redbot.core import commands, Config, checks
from requests_futures.sessions import FuturesSession
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

# Based primebot (https://github.com/pryme-svg/PrimeBot/blob/master/primebot/ext/torrent.py#L31)
async def shorten(self, magnet: str):
    res = False
    async with aiohttp.ClientSession() as session:
        async with session.get("http://mgnet.me/api/create?&format=json&opt=&m={}".format(magnet)) as response:
            res = await response.read()
    res = json.loads(res)
    return res["shorturl"]

async def make_embed(self, torrent_link, bans:list=[], ignore_bans:bool=False, page:int=1, count:int=1):
    try:
        print(f"Fetching: {torrent_link}")
        torrent_info = uTils().single_parse(torrent_link, bans=bans, ignore_bans=ignore_bans)

        if not torrent_info.get("genres"):
            torrent_info["genres"] = ["Not Found"]
        
        stream = 'N/A'
        if torrent_info['stream']:
            stream = f" - [Stream]({torrent_info['stream']})"

        short_magnet = await shorten(self, torrent_info["magnet"])

        embed = discord.Embed(
            title=torrent_info["shortName"],
            description=f"""*[{torrent_info['name']}]({torrent_link})*

{torrent_info['description']}

**Download:** *[Magnet]({short_magnet}) - [Torrent]({torrent_info['torrent']}){stream}*
**Uploaded by:** [{torrent_info['uploader']}]({torrent_info['uploaderUrl']}) *({torrent_info['date']})*
**Type:** *{torrent_info['language']}, {torrent_info['category']} - {torrent_info['type']}*
**Genres:** {", ".join(torrent_info["genres"])}
"""
        )
        emebed = embed.add_field(
            name="Size",
            value=torrent_info["size"],
            inline=True
        )
        emebed = embed.add_field(
            name="Seeders",
            value=torrent_info["seeders"],
            inline=True
        )
        emebed = embed.add_field(
            name="Leechers",
            value=torrent_info["leechers"],
            inline=True
        )
        embed = embed.set_footer(
            text=f"page: ({str(page)}/{str(count)})"
        )

        if torrent_info.get("thumbnail"):
            embed = embed.set_thumbnail(
                url=torrent_info["thumbnail"]
            )
        return embed
    except AttributeError():
        pass

class ottsx(commands.Cog):
    """
    Search 1337x.
    """

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(smartlink_enabled=False)
        self.conf.register_guild(bans=['yify'])


    @commands.group(aliases=["1337x", "torrent"], invoke_without_command=True)
    @commands.guild_only()
    async def ottsx(self, ctx, *, query:str):
        """Search 1337x.to."""
        try:
            async with ctx.typing():
                bans = await self.conf.guild(ctx.guild).bans()
                results = uTils().search(query, bans, max=9, speed=True)
                format = []
                for i, res in enumerate(results):
                    format.append(f"""
**{i+1}. [{res['name']}]({res['url']})**
**[Magnet]({await shorten(self, res["magnet"])}) - [Torrent]({res["torrent"]})** | Seeders: {res['seeders']} | Size: {res['size']} 
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


    @ottsx.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lookup(self, ctx, *, query: str):
        """Search 1337x and get all information."""
        count = 10
        pages = []
        try:
            async with ctx.typing():
                bans = await self.conf.guild(ctx.guild).bans()
                result = uTils().search(query, bans)
                if len(result) < count:
                    count = len(result)
                for i, res in enumerate(result[0:count:]):
                    new_page = await make_embed(self, res["url"], page=(i+1), count=count)
                    pages.append(new_page)

            if len(pages) == 0:
                await ctx.send(f"Sorry, no results for **{query}**.")
                return

            await menu(ctx, pages, DEFAULT_CONTROLS)

        except AttributeError:
            await ctx.send(f"Sorry, no results for **{query}** or there was an error.")

    #Possibly the dumbest command I hate it
    @ottsx.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def browse(self, ctx, category:str = "movies"):
        """Go through torrents on a main category page."""
        clientX = py1337x(proxy='1337x.to')

        # get about 200 results and put it all into an array 
        item_full_list = []
        page_number = 1
        async with ctx.typing():
            while page_number < 10:
                results = clientX.browse(category, page_number)
                if (len(results["items"])) == 0:
                    return await ctx.send("""That category does not seem to exsist.
Please choose from `games`, `music`,`software`,`tv`,`movies`, and `xxx`
                    """)
                formatted_items = []
                for item in results["items"]:
                    formatted_items.append(f"""[{item["name"]}]({item["link"]})
                    Uploaded by: {item["uploader"]} ({item["time"]})
                    Seeders: {item["seeders"]} | Leachers: {item["leechers"]}
                    """
                    )
                cut_items_int = len(formatted_items)//2
                item_full_list.append(formatted_items[:cut_items_int])
                item_full_list.append(formatted_items[cut_items_int:])
                page_number += 1

            pages = []
            for i, item_list in enumerate(item_full_list):
                embed = discord.Embed(
                    title="Browsing 1337x",
                    description="\n".join(item_list) + f"\npage: {i+1}/{len(item_full_list)}"
                    
                )
                pages.append(embed)

        await menu(ctx, pages, DEFAULT_CONTROLS)


    @ottsx.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx):
        """
        Smartlink for OTTSX makes it so whenever a link is sent in an enabled channel. \
        It well fetch data off 1337x about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """

        current_status = await self.conf.channel(ctx.channel).smartlink_enabled()
        
        await self.conf.channel(ctx.channel).smartlink_enabled.set(not current_status)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @commands.Cog.listener()
    async def on_message(self, message):
        torrent_link = re.search(r'https?:\/\/(?:www\.)?1337x\.\w{2}\/torrent\/\S+', message.content)
        if not torrent_link:
            return

        torrent_link = torrent_link.group()

        smartlink_enabled = await self.conf.channel(message.channel).smartlink_enabled()
        if not smartlink_enabled:
            return

        embed = await make_embed(self, torrent_link, ignore_bans=True)
        await message.channel.send(embed=embed)



    @ottsx.group()
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
        except ValueError():
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
