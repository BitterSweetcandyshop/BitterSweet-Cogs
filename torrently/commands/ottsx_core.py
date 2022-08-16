import re
import json
import aiohttp
import discord
import requests
from bs4 import BeautifulSoup
from torrently.utils.helpers import helpers
from torrently.utils.ottsx import ottsx_utils
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

class ottsx(commands.Cog):
    """
    Search 1337x.
    """

# Settup
    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(ottsx_link=False)
        self.conf.register_guild(nsfw_filter_level=1)
        self.conf.register_guild(bans=['apunkagames', 'igg games', 'bbrepacks', 'loadgames', 'nosteam', 'nosteam', 'xgirox', 'seyter', 'steamunlocked', 'gog unlocked', 'cracked-games', 'crackingpatching', 'qoob', 'corepack', 'gggames', 'igggames'])

# 1337x Main
    @commands.group(aliases=["1337x"], invoke_without_command=True)
    @commands.guild_only()
    async def ottsx(self, ctx, query):
        """
        Search 1337x.

        Flags:
        - Sort: `--seeders`, `--leechers`, `--size`, `--date`
        """
        async with ctx.typing():
            filter = ''
            if query.__contains__('--'):
                flagged = helpers.parsers.ottsx_flagging(query)
                if flagged['flags']: 
                    query = flagged['line']
                    filter = flagged['flags'][0]
            allow_nsfw = await helpers.parsers.solve_nfilter(self, ctx)
            bans = await self.conf.guild(ctx.guild).bans()
            results = ottsx_utils.search(query, bans=bans, max=10, allow_nsfw=allow_nsfw, filter=filter)
            if not results: return await ctx.reply('There was no results')
            for i, torrent_info in enumerate(results): results[i] = ottsx_utils.parse_page(torrent_info['url'], targets=['magnet', 'torrent'], premade=torrent_info)
            embed = await helpers.embed_build.list(results)
            embed = embed.set_author(name=ctx.author.display_name,icon_url=ctx.author.avatar_url)
        return await ctx.reply(embed=embed)

    @ottsx.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lookup(self, ctx, query):
        """
        Search 1337x, with maximum data scrape.

        Flags:
        - Sort: `--seeders`, `--leechers`, `--size`, `--date`
        """
        async with ctx.typing():
            filter = ''
            if query.__contains__('--'):
                flagged = helpers.parsers.ottsx_flagging(query)
                if flagged['flags']: 
                    query = flagged['line']
                    filter = flagged['flags'][0]
            allow_nsfw = await helpers.parsers.solve_nfilter(self, ctx)
            bans = await self.conf.guild(ctx.guild).bans()
            results = ottsx_utils.search(query, bans=bans, max=5, allow_nsfw=allow_nsfw, filter=filter)
            if not results: return await ctx.reply('There was no results')
            pages = []
            while False in results: results.remove(False)
            for i, torrent_info in enumerate(results): pages.append(await helpers.embed_build.page(ottsx_utils.parse_page(torrent_info['url'], targets=['magnet', 'torrent', 'stream', 'hash', 'thumbnail', 'short_title', 'short_title_url', 'category', 'genres', 'description', 'language', 'type'], premade=torrent_info), page=(i+1), total_pages=(len(results))))
        return await menu(ctx, pages, DEFAULT_CONTROLS)
        
# 1337x Link Detection
    @commands.Cog.listener()
    async def on_message(self, message):
        ottsx_link = await self.conf.channel(message.channel).ottsx_link()
        if not ottsx_link: return
        embed = None

        torrent_link = re.search(r'https?:\/\/(?:www\.)?1337x\.\w{2}\/torrent\/\S+', message.content)
        if torrent_link:
            torrent_link = torrent_link.group()
            await message.add_reaction("✔")
            torrent_info = ottsx_utils.parse_page(torrent_link)
            embed = await helpers.embed_build.page(torrent_info)

        if torrent_link:
            if not embed: return await message.add_reaction("❌")
            return await message.channel.send(embed=embed)

# 1337x Settings
    @commands.group(aliases=['sets'])
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
        Smartlink for 1337x makes it so whenever a 1337x link is sent in an enabled channel. It well fetch data off 1337x about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """
        current_status = await self.conf.channel(ctx.channel).ottsx_link()
        await self.conf.channel(ctx.channel).ottsx_link.set(not current_status)
        await ctx.reply("The channel **{}** now has 1337x smartlink as **{}**.".format(ctx.channel.name, not current_status))

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
