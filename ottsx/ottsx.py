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


class ottsx(commands.Cog):
    """
    Search 1337x.
    """

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(smartlink_enabled=False)
        self.conf.register_channel(imdb_link=False)
        self.conf.register_guild(nsfw_filter_level=1)
        self.conf.register_guild(bans=['yify'])


    @commands.group(aliases=["1337x"], invoke_without_command=True)
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
**[Magnet]({await shorten(self, res["magnet"])}) - [Torrent]({res["torrent"]})** | Seeders: {res['seeders']} | Size: {res['total_size']} 
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
                allow_nsfw = await solve_nfilter(self, ctx)
                print(allow_nsfw)
                result = uTils().search(query, bans, allow_nsfw=allow_nsfw)
                if len(result) < count:
                    count = len(result)
                for i, res in enumerate(result[0:count:]):
                    new_page = await make_embed(self, res, page=(i+1), count=count)
                    pages.append(new_page)

            if len(pages) == 0:
                await ctx.send(f"Sorry, no results for **{query}**.")
                return

            await menu(ctx, pages, DEFAULT_CONTROLS)

        except AttributeError:
           await ctx.send(f"Sorry, no results for **{query}** or there was an error.")


    @commands.Cog.listener()
    async def on_message(self, message):
        smartlink_enabled = await self.conf.channel(message.channel).smartlink_enabled()
        imdb_enabled = await self.conf.channel(message.channel).imdb_link()
        if not smartlink_enabled and not imdb_enabled: return
        embed = None

        torrent_link = re.search(r'https?:\/\/(?:www\.)?1337x\.\w{2}\/torrent\/\S+', message.content)
        if torrent_link:
            torrent_link = torrent_link.group()
            await message.add_reaction("✔")
            embed = await make_embed(self, torrent_link, ignore_bans=True)

        imdb_link = re.search(r'https?:\/\/(?:www\.)?(?:m\.)?imdb\.com\/title\/\S+', message.content)
        if imdb_link:
                imdb_link = imdb_link.group()

                r = FuturesSession().get(imdb_link, headers=uTils().headers)
                soup = BeautifulSoup(r.result().text, 'html.parser')
                title = soup.select_one('[data-testid="hero-title-block__title"]')
                year = soup.select_one('[data-testid="hero-title-block__metadata"] span')
                if (not year)or (not title): return
                await message.add_reaction("✔")
                query = title.get_text() + " " + year.get_text()

                bans = await self.conf.guild(message.guild).bans()
                results = uTils().search(query, bans=bans, ignore_bans=True, max=2, category='Movies')
                if not results: return
                embed = await make_embed(self, results[0], bans)


        if imdb_link or torrent_link:
            if not embed: return await message.add_reaction("❌")
            return await message.channel.send(embed=embed)



    @ottsx.group()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def settings(self, ctx):
        """Manage 1337x options on your server for further customization.
        
        Bans do not apply to smartlink/imdblink commands"""

    @settings.command()
    async def banadd(self, ctx, *, target:str):
        """Add a ban"""
        db_bans = await self.conf.guild(ctx.guild).bans()
        if db_bans.count(target.lower()): return await ctx.send(f"{target} is already on the ban list.")
        db_bans.append(target.lower())
        await self.conf.guild(ctx.guild).bans.set(db_bans)
        if not len(db_bans): return await ctx.send(f"Added {target} to the ban list.")
        await ctx.send(f"Added {target} to the ban list.\nCurrent bans: {', '.join(db_bans)}")

    @settings.command(aliases=['bandel', 'bandelete', 'banrem'])
    async def banremove(self, ctx, *, target:str):
        """Remove a ban."""
        db_bans = await self.conf.guild(ctx.guild).bans()
        try:
            db_bans.remove(target.lower())
        except ValueError():
            return await ctx.send(f"{target} is not on the ban list.")
        await self.conf.guild(ctx.guild).bans.set(db_bans)
        if not len(db_bans): return await ctx.send(f"Ban list is now empty.")
        await ctx.send(f"Added {target} to the ban list.\nCurrent bans: {', '.join(db_bans)}")

    @settings.command()
    async def banlist(self, ctx):
        """List all current bans."""
        db_bans = await self.conf.guild(ctx.guild).bans()
        if not len(db_bans): return await ctx.send(f"Ban list is empty.")
        await ctx.send(f"Current bans: {', '.join(db_bans)}")

    @settings.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def imdblink(self, ctx):
        """
        Makes it so when a IMDB link is sent in chat, it wiwll find a torrent off 1337x.
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """
        current_status = await self.conf.channel(ctx.channel).imdb_link()
        await self.conf.channel(ctx.channel).imdb_link.set(not current_status)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @settings.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx):
        """
        IMDB link for 1337x makes it so whenever a 1337x link is sent in an enabled channel. It well fetch data off 1337x about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """
        current_status = await self.conf.channel(ctx.channel).smartlink_enabled()
        await self.conf.channel(ctx.channel).smartlink_enabled.set(not current_status)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @settings.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def nfilter(self, ctx, nfilter_level:int):
        """
        Set how nsfw should show in the search results. 
        _ _
        0 - No filter, always show nsfw results.
        1 - Only show nsfw results in nsfw channels.
        2 - Never show nsfw.
        """
        ratings = {"always be shown", "only be shown in nsfw channels.", "never shown."}
        if not nfilter_level in [0, 1, 2]: return await ctx.send("Invalid choice, the available options are: `0`, `1`, and `2`.")
        current_status = await self.conf.guild(ctx.guild).nsfw_filter_level()
        if current_status == nfilter_level: return await ctx.send("Nsfw filter was already set to " + ratings[nfilter_level])
        await self.conf.guild(ctx.guild).nfilter_level.set(nfilter_level)
        return await ctx.send("Nsfw content will now " + ratings[nfilter_level])


# Do I show nsfw?
async def solve_nfilter(self, ctx):
    nlevel = await self.conf.guild(ctx.guild).nsfw_filter_level()
    if nlevel == 0: return True
    elif nlevel == 1: return ctx.channel.is_nsfw()
    elif nlevel == 2: return False


#ugly fucking function to make embeds
async def make_embed(self, torrent_info, bans:list=[], ignore_bans:bool=False, page:int=1, count:int=1):
    #try:

        if not torrent_info.get("genres"): torrent_info["genres"] = ["Not Found"]
        
        stream = '- N/A'
        if torrent_info['stream']: stream = f" - [Stream]({torrent_info['stream']})"

        if torrent_info['nsfw']: torrent_info['nsfw'] = "\n**NSFW**"
        if not torrent_info['description']: torrent_info['description'] = "No Description."

        short_magnet = await shorten(self, torrent_info["magnet"])

        embed = discord.Embed(
            title=torrent_info["short_title"],
            url=torrent_info['short_title_url'],
            description=f"""*[{torrent_info['name']}]({torrent_info['url']})*
{torrent_info['nsfw']}
{torrent_info['description']}

**Download:** *[Magnet]({short_magnet}) - [Torrent]({torrent_info['torrent']}){stream}*
**Uploaded by:** [{torrent_info['uploaded_by']}]({torrent_info['uploaded_by_url']}) *({torrent_info['date_uploaded']})*
**Type:** *{torrent_info['language']}, {torrent_info['category']} - {torrent_info['type']}*
**Genres:** {", ".join(torrent_info["genres"])}
""")

        embed = embed.add_field(
            name="Size",
            value=torrent_info["total_size"],
            inline=True
        )
        embed = embed.add_field(
            name="Seeders",
            value=torrent_info["seeders"],
            inline=True
        )
        embed = embed.add_field(
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
    #except AttributeError():
    #    pass