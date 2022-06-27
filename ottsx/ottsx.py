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

async def make_embed(self, torrent_link, page:int=1, count:int=1):
    try:
        clientX = py1337x(proxy='1337x.to')
        torrent_info = py1337x().info(torrent_link)
        print(f"Fetching: {torrent_info['name']}")

        short_magnet = await shorten(self, torrent_info["magnetLink"])

        embed = discord.Embed(
            title=torrent_info["shortName"],
            url=torrent_link,
           description=f"*{torrent_info['name']}*\n\n{torrent_info['description']}"
        )
        embed = embed.add_field(
            name="Magnet Link",
            value=f"||{short_magnet}||",
            inline=False
        )
        if not torrent_info["genre"]:
            torrent_info["genre"] = ["Not Found"]
        embed = embed.add_field(
            name="Genres: " + ", ".join(torrent_info["genre"]),
            value=f"**Uploaded by:** {torrent_info['uploader']} *({torrent_info['uploadDate']})*",
            inline=False
        )
        emebed = embed.add_field(
            name=f"**Quality:** {torrent_info['type']}",
            value="__ __",
            inline=False
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

        if torrent_info["thumbnail"]:
            embed = embed.set_thumbnail(
                url=torrent_info["thumbnail"].replace("https://www.1377x.to", "https:")
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


    @commands.group(aliases=["1337x"])
    @commands.guild_only()
    async def ottsx(self, ctx):
        """Search 1337x.to."""

    @ottsx.command(aliases=["quicksearch", "q", "qs", "quicklookup", "ql"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def quick(self, ctx, *, query: str):
        """Quickly search 1337x"""
        try:
            async with ctx.typing():
                results = uTils().search(query)
                print(results)
                format = []
                for i, res in enumerate(results):
                    format.append(f"""
                    **{i+1}. [{res['name']}]({res['url']})**
                    **[Magnet]({await shorten(self, res["magnet"])})** | Seeders: {res['seeders']} | Size: {res['size']} 
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


    @ottsx.command(aliases=["search", "s"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lookup(self, ctx, *, query: str):
        """Search 1337x and get all information."""
        count = 10
        pages = []
        try:
            async with ctx.typing():
                clientX = py1337x(proxy='1337x.to')
                result = clientX.search(query, sortBy='seeders', page=1)['items']
                print(result)
                if len(result) < count:
                    count = len(result)
                for i, res in enumerate(result[0:count:]):
                    new_page = await make_embed(self, res["link"], (i+1), count)
                    pages.append(new_page)

            if len(pages) == 0:
                await ctx.send(f"Sorry, no results for **{query}**.")
                return

            await menu(ctx, pages, DEFAULT_CONTROLS)

        except AttributeError:
            await ctx.send(f"Sorry, no results for **{query}** or there was an error.")

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
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx, toggle: bool):
        """
        Smartlink for OTTSX makes it so whenever a link is sent in an enabled channel. \
        It well fetch data off 1337x about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """

        current_status = await self.conf.channel(ctx.channel).smartlink_enabled()
        if toggle == current_status:
            await ctx.send("The channel **{}** is already set to **{}** for smartlink.".format(ctx.channel.name, toggle))
            return
        
        await self.conf.channel(ctx.channel).smartlink_enabled.set(toggle)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, toggle))

    @commands.Cog.listener()
    async def on_message(self, message):
        torrent_link = re.search(r'https?:\/\/(?:www\.)?1337x\.\w{2}\/torrent\/\S+', message.content)
        if not torrent_link:
            return

        torrent_link = torrent_link.group()

        smartlink_enabled = await self.conf.channel(message.channel).smartlink_enabled()
        if not smartlink_enabled:
            return

        embed = await make_embed(self, torrent_link)
        await message.channel.send(embed=embed)