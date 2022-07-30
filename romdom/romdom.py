import re
import json
import aiohttp
import discord
from random import shuffle
from romdom.utils import utilities
from redbot.core import commands, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

class romdom(commands.Cog):
    """
    Search your favoutite games on safe rom sites.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=["v"], invoke_without_command=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.guild_only()
    async def vimm(self, ctx, *, query:str):
        async with ctx.typing():
            results = utilities.vimm.search(query)
            if not results: return await ctx.reply("There was no results")
            results_formatted = []
            for i, res in enumerate(results):
                results_formatted.append(f"{i+1}. **{res['system']}** [{res['name']}]({res['url']})")

            embed = discord.Embed(
                description="\n".join(results_formatted)
            )
            embed = embed.set_author(
                    name=ctx.author.display_name,
                    icon_url=ctx.author.avatar_url
            )
        await ctx.reply(embed=embed)

    @vimm.command(aliases=["search", "s", "l"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lookup(self, ctx, *, query:str):
        async with ctx.typing():
            results = utilities.vimm.search(query, limit=5)
            roms = []
            for i, res in enumerate(results):
                rom_info = utilities.vimm.parse_page(res['url'])
                if not rom_info: return await ctx.reply("There was no results")
                embed = discord.Embed(
                    title=rom_info['name'],
                    url=rom_info['url'],
                    description=f"*{rom_info['name_full']}*\n\n**General**\n*System:* {rom_info['system']}\n*Size:* {rom_info['size']}\n*Vimm Players:* {rom_info['players']}\n*Verified on:* {rom_info['verified']}\n*Region(s):* {', '.join(rom_info['regions'])}\n\n**Ratings**\n*Overall:* {rom_info['overall']}\n*Graphics:* {rom_info['graphics']}\n*Sound:* {rom_info['sound']}\n*Gameplay* {rom_info['gameplay']}\n\n**Nerd Stuff**\n*crc:* `{rom_info['crc']}`\n*md5:* `{rom_info['md5']}`\n*sha1:* `{rom_info['sha1']}`\n*serial #:* `{rom_info['serial #']}`"
                )
                embed = embed.set_footer(text=f"page: ({str(i+1)}/{str(len(results))})")
                embed = embed.set_author(
                    name='Vimm\'s Lair',
                    url='https://vimm.net',
                    icon_url='https://vimm.net/images/vimmbutton.png'
                )
                roms.append(embed)
        await menu(ctx, roms, DEFAULT_CONTROLS)
