import re
import json
import aiohttp
import discord
from bs4 import BeautifulSoup
from torrently.utils.helpers import helpers
from torrently.utils.nyaa import nyaa_utils
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

class nyaa(commands.Cog):
    """
    Search 1337x.
    """

# Settup
    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(nyaa_link=False)
        self.conf.register_guild(nsfw_filter_level=1)
        self.conf.register_guild(bans=[])

# Nyaa Main
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def nyaa(self, ctx, *, query):
        """
        Search Nyaa.si
        Flags:
        - Category: `--manga` and `--anime`
        - Sort: `--seeders`, `--leechers`, `--size`, `--date`
        """
        async with ctx.typing():
            cat, sub, sort = [0, 0, 'seeders']
            if query.__contains__('--'):
                flagged = helpers.parsers.nyaa_flagging(query)
                print(query)
                if flagged['flags']: 
                    query = flagged['line']
                    cat, sub = flagged['flags']['category'].split("_")
                    sort = flagged['flags']['sort']
            allow_nsfw = await helpers.parsers.solve_nfilter(self, ctx)
            bans = await self.conf.guild(ctx.guild).bans()
            results = nyaa_utils.search(query, bans=bans, category=cat, subcategory=sub, sort=sort)
            if not results: return await ctx.send("There was no results")
            embed = await helpers.embed_build.list(results)
            embed = embed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar_url)
        return await ctx.reply(embed=embed)

    @nyaa.command(aliases=['l', 's', 'search'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.guild_only()
    async def lookup(self, ctx, *, query):
        """
        Search Nyaa.si, with maximum data scrape.

        Flags:
        - Category: `--manga` and `--anime`
        - Sort: `--seeders`, `--leechers`, `--size`, `--date`
        """
        async with ctx.typing():
            cat, sub, sort = [0, 0, 'seeders']
            if query.__contains__('--'):
                flagged = helpers.parsers.nyaa_flagging(query)
                print(query)
                if flagged['flags']: 
                    query = flagged['line']
                    cat, sub = flagged['flags']['category'].split("_")
                    sort = flagged['flags']['sort']
            allow_nsfw = await helpers.parsers.solve_nfilter(self, ctx)
            bans = await self.conf.guild(ctx.guild).bans()
            results = nyaa_utils.search(query, bans=bans, category=cat, subcategory=sub, sort=sort)
            if not results: return await ctx.send("There was no results")
            pages = []
            while False in results: results.remove(False)
            for i, torrent_info in enumerate(results): pages.append(await helpers.embed_build.page(nyaa_utils.parse_page(torrent_info['url'], premade=torrent_info), page=(i+1), total_pages=(len(results))))
        return await menu(ctx, pages, DEFAULT_CONTROLS)

# Nyaa Link Detection
    @commands.Cog.listener()
    async def on_message(self, message):
        nyaa_link = await self.conf.channel(message.channel).nyaa_link()
        if not nyaa_link: return
        embed = None

        torrent_link = re.search(r'https?://nyaa.si/view/\S+', message.content)
        if torrent_link:
            torrent_link = torrent_link.group()
            await message.add_reaction("✔")
            torrent_info = nyaa_utils.parse_page(torrent_link)
            embed = await helpers.embed_build.page(torrent_info)

        if torrent_link:
            if not embed: return await message.add_reaction("❌")
            return await message.channel.send(embed=embed)

# Nyaa Settings
    @nyaa.group(aliases=['sets'])
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def settings(self, ctx):
        """Manage 1337x options on your server for further customization.
        
        Bans do not apply to smartlink commands"""

    @settings.command()
    async def banadd(self, ctx, *, target:str):
        """Add a ban"""
        db_bans = await self.conf.guild(ctx.guild).bans()
        if db_bans.count(target.lower()): return await ctx.reply(f"{target} is already on the ban list.")
        db_bans.append(target.lower())
        await self.conf.guild(ctx.guild).bans.set(db_bans)
        if not len(db_bans): return await ctx.reply(f"Added {target} to the ban list.")
        await ctx.reply(f"Added {target} to the ban list.\nCurrent bans: {', '.join(db_bans)}")

    @settings.command(aliases=['bandel', 'bandelete', 'banrem'])
    async def banremove(self, ctx, *, target:str):
        """Remove a ban."""
        db_bans = await self.conf.guild(ctx.guild).bans()
        try:
            db_bans.remove(target.lower())
        except ValueError():
            return await ctx.reply(f"{target} is not on the ban list.")
        await self.conf.guild(ctx.guild).bans.set(db_bans)
        if not len(db_bans): return await ctx.reply(f"Ban list is now empty.")
        await ctx.reply(f"Removed {target} to the ban list.\nCurrent bans: {', '.join(db_bans)}")

    @settings.command()
    async def banlist(self, ctx):
        """List all current bans."""
        db_bans = await self.conf.guild(ctx.guild).bans()
        if not len(db_bans): return await ctx.reply(f"Ban list is empty.")
        await ctx.reply(f"Current bans: {', '.join(db_bans)}")

    @settings.command()
    @commands.guild_only()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx):
        """
        Smartlink for Nyaa makes it so whenever a Nyaa link is sent in an enabled channel. It well fetch data off Nyaa about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """
        current_status = await self.conf.channel(ctx.channel).nyaa_link()
        await self.conf.channel(ctx.channel).nyaa_link.set(not current_status)
        await ctx.reply("The channel **{}** now has Nyaa smartlink as **{}**.".format(ctx.channel.name, not current_status))

    @settings.command(aliases=['nsfwfilter'])
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
        ratings = ["always be shown", "only be shown in nsfw channels.", "never shown."]
        if not nfilter_level in [0, 1, 2]: return await ctx.reply("Invalid choice, the available options are: `0`, `1`, and `2`.")
        rating = ratings[nfilter_level]
        current_status = await self.conf.guild(ctx.guild).nsfw_filter_level()
        if current_status == nfilter_level: return await ctx.reply(f"Nsfw filter was already set to *{rating}*")
        await self.conf.guild(ctx.guild).nsfw_filter_level.set(nfilter_level)
        return await ctx.reply(f"Nsfw content will now *{rating}*")