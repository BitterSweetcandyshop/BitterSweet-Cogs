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
                    if res['repacker'] == 'Scooter':
                        repack_info = utilities.scooter.parse_page(res['url'])
                        repack_embeds.append(scooter_make_embed(repack_info, page=(i+1), count=(len(repacks))))
                    if res['repacker'] == 'FitGirl':
                        repack_info = utilities.fitgirl.parse_page(res['url'])
                        repack_embeds.append(fitgirl_make_embed(repack_info, page=(i+1), count=(len(repacks))))
                    if res['repacker'].__contains__('KaOsKrew'): 
                        repack_info = utilities.kaoskrew.parse_page(res['url'])
                        repack_embeds.append(kaoskrew_make_embed(repack_info, page=(i+1), count=(len(repacks))))
                    if res['repacker'].__contains__('Darck Repacks'): 
                        repack_info = utilities.darckside.parse_page(res['url'])
                        repack_embeds.append(darck_make_embed(repack_info, page=(i+1), count=(len(repacks))))
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
                embed = await fitgirl_make_embed(repack_info, page=(i+1), count=(len(results)))
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
                repacks.append(scooter_make_embed(repack_info, page=(i+1), count=(len(results))))

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
                repacks.append(darck_make_embed(repack_info, page=(i+1), count=(len(results))))

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
                repacks.append(kaoskrew_make_embed(repack_info, page=(i+1), count=(len(results))))

        await menu(ctx, repacks, DEFAULT_CONTROLS)


def make_embed(results, author):
    results_formatted = []
    for i, res in enumerate(results): results_formatted.append(f"{i+1}. [{res['name']}]({res['url']})")
    embed = discord.Embed(description="\n".join(results_formatted))
    embed = embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    return embed

async def fitgirl_make_embed(repack_info, page:int=1, count:int=1):
    mirrors_formatted = []
    for mirror in repack_info['mirrors']: mirrors_formatted.append(f"[{mirror['name']}]({mirror['link']})")
    mirrors_formatted = ", ".join(mirrors_formatted)

    embed = discord.Embed(
        title = repack_info['name'],
        url = repack_info['url'],
        description=f"[Magnet]({await shorten(repack_info['magnet'])}) - [Torrent]({repack_info['torrent']})\n\n**Summary:**\n{repack_info['summary'][:256]}...\n\n**Genres:** {repack_info['genres']}\n**Company:** {repack_info['company']}\n**Languages:** {repack_info['languages']}\n**Original Size:** {repack_info['original_size']}\n**Repack Size:** {repack_info['repack_size']}\n**Posted:** {repack_info['date']}\n\n**Mirrors**\n{mirrors_formatted}"
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    embed = embed.set_thumbnail(url=repack_info["thumbnail"])
    embed = embed.set_author(
        name='FitGirl Repacks',
        url='https://fitgirl-repacks.site',
        icon_url='https://fitgirl-repacks.site/wp-content/uploads/2020/08/icon_fg-1.jpg'
    )
    return embed

def scooter_make_embed(repack_info, page:int=1, count:int=1):
    ddls = []
    torrents = []
    for torrent in repack_info['torrents']: torrents.append(f"[{torrent['name']}]({torrent['link']})")
    torrents = ", ".join(torrents)

    embed = discord.Embed(
        title = repack_info['name'],
        url = repack_info['url'],
        description = f"**Posted on:** {repack_info['date']}\n\n**Summary:**\n{repack_info['summary'][:256]}...\n\n{repack_info['system'].split('**Recommended:')[0]}\n\n**Direct Download:** [offical]({repack_info['ddl']})\n**Torrent:** {torrents}"
    )
    embed = embed.set_author(
        name='Scooter Repacks',
        url='https://scooter-repacks.site',
        icon_url='https://cdn.discordapp.com/icons/815595843205464095/a_8be5d23c5b078d04cb64c59a02ffe430.png'
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    embed = embed.set_thumbnail(url=repack_info["thumbnail"])
    embed = embed.set_image(url=repack_info["nfo"])

    return embed

def darck_make_embed(repack_info, page:int=1, count:int=1):
    if repack_info['download'][0] != "Signup required.":
        links_formatted = []
        for link in repack_info['download']: links_formatted.append(f"[{link.split('//')[1].split('/')[0]}]({link})")
        repack_info['download'] = ", ".join(links_formatted)
    else: repack_info['download'] = 'Signup required.'

    embed = discord.Embed(
        title = repack_info['name'],
        url = repack_info['url'],
        description = f"**Posted on:** {repack_info['date']}\n\n**Original Size:** {repack_info['original_size']}\n**Repack Size:** {repack_info['repack_size']}\n**Genre:** {repack_info['genre']}\n**Developer:** {repack_info['developer']}\n**Publisher:** {repack_info['publisher']}\n**Platform:** {repack_info['platform']}\n\n**Download:** {repack_info['download']}"
    )
    embed = embed.set_author(
        name=repack_info['repacker'],
        url=repack_info['repacker_url'],
        icon_url=repack_info['repacker_pfp']
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    embed = embed.set_thumbnail(url=repack_info["thumbnail"])
    embed = embed.set_image(url=repack_info["nfo"])
    return embed

def kaoskrew_make_embed(repack_info, page:int=1, count:int=1):
    ddls = []
    for ddl in repack_info['ddls']: ddls.append(f"[{ddl['name']}]({ddl['link']})")
    ddls = ", ".join(ddls)

    embed = discord.Embed(
        title = repack_info['name'],
        url = repack_info['url'],
        description = f"**Posted on:** {repack_info['date']}\n**Install:** {ddls}"
    )
    embed = embed.set_author(
        name=repack_info['repacker'],
        url='https://kaoskrew.org',
        icon_url='https://media.discordapp.net/attachments/932537561166008360/1002028187171160167/unknown.png?width=285&height=300'
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    embed = embed.set_image(url=repack_info["nfo"])

    return embed