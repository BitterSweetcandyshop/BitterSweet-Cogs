import re
import json
import aiohttp
import discord
from random import shuffle
from repacky.utils import utilities
from redbot.core import commands, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

# Based primebot (https://github.com/pryme-svg/PrimeBot/blob/master/primebot/ext/torrent.py#L31)
async def shorten(magnet:str):
    res = False
    async with aiohttp.ClientSession() as session:
        async with session.get("http://mgnet.me/api/create?&format=json&opt=&m={}".format(magnet)) as response:
            res = await response.read()
    res = json.loads(res)
    return res["shorturl"]


class repacky(commands.Cog):
    """
    Search your favoutite repackers.
    """

    def __init__(self, bot):
        self.bot = bot
# Main
    @commands.group(aliases=["rep"], invoke_without_command=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.guild_only()
    async def repack(self, ctx, *, query:str):
        """Search for repacks from trusted sources.\nSources: FitGirl, Darck, Scooter, and KaosKrew"""
        async with ctx.typing():
            repacks = []
            try: repacks.extend(utilities.scooter.search(query, limit=5))
            except: pass
            try: repacks.extend(utilities.fitgirl.search(query, limit=5))
            except: pass
            try: repacks.extend(utilities.kaoskrew.search(query, limit=5))
            except: pass
            try: repacks.extend(utilities.darckside.search(query, limit=5))
            except: pass
            results_formatted = []
            shuffle(repacks)
            if not repacks: return await ctx.reply('There was no results')
            for i, res in enumerate(repacks):
                try: results_formatted.append(f"{i+1}. **{res['repacker']}** [{res['name']}]({res['url']})")
                except: pass
            embed = discord.Embed(description="\n".join(results_formatted))
            embed = embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)
    
    @repack.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(ctx, *, query:str):
        """Find repacks with all the important information."""
        async with ctx.typing():
            repacks = []
            try: repacks.extend(utilities.scooter.search(query, limit=3))
            except: pass
            try: repacks.extend(utilities.fitgirl.search(query, limit=3))
            except: pass
            try: repacks.extend(utilities.kaoskrew.search(query, limit=3))
            except: pass
            try: repacks.extend(utilities.darckside.search(query, limit=5))
            except: pass
            repack_embeds = []
            shuffle(repacks)
            if not repacks: return await ctx.reply('There was no results')
            for i, res in enumerate(repacks):
                try:
                    repack_info = None
                    if res['repacker'] == 'Scooter': repack_info = utilities.scooter.parse_page(res['url'])
                    elif res['repacker'] == 'FitGirl':repack_info = utilities.fitgirl.parse_page(res['url'])
                    elif res['repacker'].__contains__('KaOsKrew'): repack_info = utilities.kaoskrew.parse_page(res['url'])
                    elif res['repacker'].__contains__('Darck Repacks'):  repack_info = utilities.darckside.parse_page(res['url'])
                    else: continue
                    if repack_info: repack_embeds.append(await make_page_embed(repack_info, page=(i+1), count=(len(repacks))))
                except: pass
            if not repack_embeds: return await ctx.reply('There was no results')
        await menu(ctx, repack_embeds, DEFAULT_CONTROLS)

# Fitgirl
    @commands.group(aliases=["fg"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def fitgirl(self, ctx, *, query:str):
        """Search FitGirl for repacks."""
        async with ctx.typing():
            results = utilities.fitgirl.search(query, limit=20)
            if not results: return await ctx.reply('There was no results')
            embed = make_embed(results, ctx.author)
        await ctx.reply(embed=embed)

    @fitgirl.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(ctx, *, query:str):
        """Find repacks with all the important information."""
        async with ctx.typing():
            results = utilities.fitgirl.search(query, limit=5)
            if not results: return await ctx.reply('There was no results')
            repacks = []
            for i, res in enumerate(results):
                repack_info = utilities.fitgirl.parse_page(res['url'])
                embed = await make_page_embed(repack_info, page=(i+1), count=(len(results)))
                repacks.append(embed)
        await menu(ctx, repacks, DEFAULT_CONTROLS)

# Scooter
    @commands.group(aliases=["sc"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def scooter(self, ctx, *, query:str):
        """Search Scooter repacks"""
        async with ctx.typing():
            results = utilities.scooter.search(query, limit=20)
            if not results: return await ctx.reply('There was no results')
            embed = make_embed(results, ctx.author)
        await ctx.reply(embed=embed)

    @scooter.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(ctx, *, query:str):
        """Find repacks with all the important information."""
        async with ctx.typing():
            results = utilities.scooter.search(query, limit=5)
            if not results: return await ctx.reply('There was no results')
            repacks = []
            for i, res in enumerate(results):
                repack_info = utilities.scooter.parse_page(res['url'])
                repacks.append(await make_page_embed(repack_info, page=(i+1), count=(len(results))))

        await menu(ctx, repacks, DEFAULT_CONTROLS)

# Darck
    @commands.group(aliases=["darckside", "dar"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def darck(self, ctx, *, query:str):
        """Search Drack's repacks."""
        async with ctx.typing():
            results = utilities.darckside.search(query, limit=20)
            if not results: return await ctx.reply('There was no results')
            embed = make_embed(results, ctx.author)
        await ctx.reply(embed=embed)

    @darck.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(ctx, *, query:str):
        """Find repacks with all the important information."""
        async with ctx.typing():
            results = utilities.darckside.search(query, limit=5)
            if not results: return await ctx.reply('There was no results')
            repacks = []
            for i, res in enumerate(results):
                repack_info = utilities.darckside.parse_page(res['url'])
                repacks.append(await make_page_embed(repack_info, page=(i+1), count=(len(results))))

        await menu(ctx, repacks, DEFAULT_CONTROLS)

#KaOsKrew
    @commands.group(aliases=["kaos", "kk"], invoke_without_command=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def kaoskrew(self, ctx, *, query:str):
        """Search KaOsKrew repacks."""
        async with ctx.typing():
            results = utilities.kaoskrew.search(query, limit=20)
            if not results: return await ctx.reply('There was no results')
            embed = make_embed(results, ctx.author)
        await ctx.reply(embed=embed)

    @kaoskrew.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(self, ctx, *, query:str):
        """Find repacks with all the important information."""
        async with ctx.typing():
            results = utilities.kaoskrew.search(query, limit=5)
            if not results: return await ctx.reply('There was no results')
            repacks = []
            for i, res in enumerate(results):
                repack_info = utilities.kaoskrew.parse_page(res['url'])
                repacks.append(await make_page_embed(repack_info, page=(i+1), count=(len(results))))

        await menu(ctx, repacks, DEFAULT_CONTROLS)


def make_embed(results, author):
    results_formatted = []
    for i, res in enumerate(results): results_formatted.append(f"{i+1}. [{res['name']}]({res['url']})")
    embed = discord.Embed(description="\n".join(results_formatted))
    embed = embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    return embed

async def make_page_embed(repack_info, page:int=1, count:int=1):
    description_main = []
    for key in repack_info.keys():
        if not repack_info[key]: continue
        #Description
        elif key in ['original_size', 'repack_size', 'publisher', 'developer', 'languages', 'genre', 'date', 'system_requirements']: description_main.append(f"**{key.replace('_', ' ').title()}:** {repack_info[key]}")
       # Links
        elif key == 'magnet': repack_info['magnet'] = f"**Magnet:** [Magnet]({await shorten(repack_info['magnet'])})"
        elif key in ['download', 'mirror', 'torrent']:
            links_formatted = []
            if isinstance(repack_info[key][0], str): links_formatted.append(repack_info[key][0])
            else: 
                for option in repack_info[key]: links_formatted.append(f"[{option['name']}]({option['link']})")
            repack_info[key] = f"**{key.title()}:** " + (', '.join(links_formatted)) # Don't question it

    has_altered = False
    for altered_key in ['download', 'magnet', 'torrent', 'mirror']:
        if not repack_info[altered_key]: continue
        if not has_altered:
            has_altered = True
            description_main.append('\n')
        description_main.append(repack_info[altered_key])

    description_main = "\n".join(description_main)
    embed = discord.Embed(
        title = repack_info['name'] or repack_info['name_full'],
        url = repack_info['url'],
        description = f"{description_main}"
    )
    embed = embed.set_author(
        name=repack_info['repacker'],
        url=repack_info['repacker_url'],
        icon_url=repack_info['repacker_pfp']
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    if repack_info["thumbnail"]: embed = embed.set_thumbnail(url=repack_info["thumbnail"])
    if repack_info["nfo"]: embed = embed.set_image(url=repack_info["nfo"])
    return embed