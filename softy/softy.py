import re
import json
import discord
import aiohttp
from random import shuffle
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from softy.utils import utilities

class softy(commands.Cog):
    """Obtain information from filecr.com"""

    def __init__(self, bot):
        self.bot = bot

#Main
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def software(self, ctx, *, query:str):
        async with ctx.typing():
            warez = []
            try: warez.extend(utilities.monkrus.search(query, limit=5))
            except: pass
            try: warez.extend(utilities.filecr.search(query, limit=5))
            except: pass
            results_formatted = []
            shuffle(warez)
            if not warez: return await ctx.reply('There was no results')
            for i, res in enumerate(warez):
                try: results_formatted.append(f"{i+1}. **{res['site']}** [{res['name']}]({res['url']})")
                except: pass
            embed = discord.Embed(description="\n".join(results_formatted))
            embed = embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=embed)

    @software.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(ctx, *, query:str):
        async with ctx.typing():
            warez = []
            results_formatted = []
            try: warez.extend(utilities.monkrus.search(query, limit=5))
            except: pass
            try: warez.extend(utilities.filecr.search(query, limit=5))
            except: pass
            shuffle(warez)
            if not warez: return await ctx.reply('There was no results')
            for i, res in enumerate(warez):
                try:
                    if res['site'] == 'filecr':
                        software_data = utilities.filecr.parse_page(res['url'])
                        results_formatted.append(filecr_make_embed(software_data, page=(i+1), count=(len(warez))))
                    if res['site'] == 'monkrus':
                        software_data = utilities.monkrus.parse_page(res)
                        results_formatted.append(monkrus_make_embed(software_data, page=(i+1), count=(len(warez))))
                except: pass
            if not results_formatted: return await ctx.reply("There was no results")
        await menu(ctx, results_formatted, DEFAULT_CONTROLS)

#Monkrus
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def monkrus(self, ctx, *, query:str):
        async with ctx.typing():
            results = utilities.monkrus.search(query)
            if not results: return await ctx.reply('There was no results')
            embed = make_embed(results, ctx.author)
        
        return await ctx.reply(embed=embed)

    @monkrus.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(ctx, *, query:str):
        """Search Monkrus and include download links"""
        async with ctx.typing():
            results = utilities.monkrus.search(query, limit=5)
            if not results: return await ctx.reply('There was no results')
            softwares = []
            for i, res in enumerate(results):
                software_data = utilities.monkrus.parse_page(res)
                embed = monkrus_make_embed(software_data, page=(i+1), count=(len(results)))
                softwares.append(embed)
        await menu(ctx, softwares, DEFAULT_CONTROLS)

# Filecr
    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def filecr(self, ctx, *, query:str):
        async with ctx.typing():
            results = utilities.filecr.search(query)
            if not results: return await ctx.reply('There was no results')
            embed = make_embed(results, ctx.author)
        
        return await ctx.reply(embed=embed)

    @filecr.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(self, ctx, *, query:str):
        """Search Filecr and with more information"""
        async with ctx.typing():
            results = utilities.filecr.search(query, limit=5)
            if not results: return await ctx.reply('There was no results')
            softwares = []
            for i, res in enumerate(results):
                software_data = utilities.filecr.parse_page(res['url'])
                embed = filecr_make_embed(software_data, page=(i+1), count=(len(results)))
                softwares.append(embed)
        await menu(ctx, softwares, DEFAULT_CONTROLS)

def make_embed(results, author):
    results_formatted = []
    for i, res in enumerate(results): results_formatted.append(f"{i+1}. [{res['name']}]({res['url']})")
    embed = discord.Embed(description="\n".join(results_formatted))
    embed = embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    return embed

def filecr_make_embed(software_data, page:int=1, count:int=1):
    embed = discord.Embed(
        title = software_data['name'],
        url = software_data['url'],
        description=f"*{software_data['description']}*\n\n**Platform:** {software_data['platform']}\n**Released:** {software_data['date']}\n**Version:** {software_data['version']}\n**Size:** {software_data['size']}"
    )
    embed = embed.set_author(
        name="Filecr",
        url="https://filecr.com/",
        icon_url="https://cdn.discordapp.com/attachments/932537561166008360/1003520762721865798/unknown.png"
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    embed = embed.set_thumbnail(url=software_data["thumbnail"])
    
    return embed

def monkrus_make_embed(software_data, page:int=1, count:int=1):
    sources = []
    for source in software_data['downlaod']: sources.append(f"[{source['name']}]({source['link']})")
    sources = ", ".join(sources)

    embed = discord.Embed(
        title = software_data['name'],
        url = software_data['url'],
        description = f"**Posted on:** {software_data['date']}\n\n**Install:** {sources}"
    )
    embed = embed.set_author(
        name="Monkrus",
        url="https://w14.monkrus.ws",
    )
    embed = embed.set_footer(text=f"page: ({str(page)}/{str(count)})")
    embed = embed.set_thumbnail(url=software_data["thumbnail"])
    
    return embed