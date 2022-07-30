import re
import json
import discord
from redbot.core import commands

exhelp: commands.Command = None
exinfo: commands.Command = None
class Helpless(commands.Cog):
    """Help and Info"""



    def __init__(self, bot):
        self.bot = bot
        global exhelp
        global exinfo
        exhelp = bot.get_command("help")
        exinfo = bot.get_command("info")
        if exhelp:
            bot.remove_command(exhelp.name)
        if exinfo:
            bot.remove_command(exinfo.name)

    def cog_unload(self):
        global exhelp
        global exinfo
        try:
            self.bot.remove_command("help")
            self.bot.remove_command("info")
        except Exception as e:
            print(e)
        if exhelp:
            self.bot.add_command(exhelp)
        if exinfo:
            self.bot.add_command(exinfo)

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def help(self, ctx, **kwargs):
        embed = discord.Embed(
            description="""**Torrenting**
    Search through some popular trackers:
    - `1337x` (good for movies/tv)
    - `nyaa` (good for anime/manga)
    - `rarbg` (good for movies/tv)
**Repacks/Gaming**
    Search for your favourite games.
    - `repack` Search for repacks.
    - `fitgirl` (repacks)
    - `scooter` (repacks)
    - `kaos` (repacks)
    - `vimm` (roms)
**Misc**
    Need help or want to know some stats?
    - `contact` Reach out to BitterSweet#1337.
    - `help` Shows this embed.
    - `invite` Invite Quinque to your own sevrer. 
    - `set` Other tools for server settings.
    - `info` More information about the bot, credits, and support.
**AniList**
    - `anime` Searches for an anime using Anilist.
    - `character` Searches for an anime character using Anilist.
    - `manga` Searches for a manga using Anilist.
    - `user` Searches for a user on Anilist.
**Notes**
    - Do not use 1337x for software.
    - Be careful using 1337x for games.
    - Flags start with `--`.
            """
        )
        embed = embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar_url
        )
        embed = embed.set_image(
            url="https://cdn.discordapp.com/attachments/932537561166008360/991177659948216390/unknown.png"
        )
        embed = embed.set_footer(
            text="Stay crazy, keep seeding.",
            icon_url="https://cdn.discordapp.com/avatars/932434610233684068/5c7750171fc026c9ad151b21add11b6f.png?size=4096"
        )
        await ctx.send(embed=embed)


    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.command(aliases=["i", "about"])
    @commands.bot_has_permissions(embed_links=True)
    async def info(self, ctx, **kwargs):
        embed = discord.Embed(
            description="""Hey! I'm made by BitterSweet!
I made this bot so I can have all those little piracy tools and information I need all \
in one place. More importantly though I'm using this project to learn about parsing and webcraping.

**Backend/Source**
    This bot is actually an instance of [RedBot](https://github.com/Cog-Creators/Red-DiscordBot) So instead of a full source,
    You can settup a redbot instance, and load up [my cogs](https://github.com/bittersweetcandyshop/BitterSweet-Cogs).

**Special Thanks**
    - Pfp: ju ju bee#4839
    Repackers:
        - [Scooter](https://scooter-repacks.site)
        - [FitGirl](https://fitgirl-repacks.site)
        - [KaOsKrew](https://kaoskrew.org)
    Valued Feedback:
        - [DieDoesMC#0945](https://discord.gg/8WCZGZ5Ucr)
        - Bulldög#0533
        - [champagne.sunshine#0968](https://discord.gg/38G68UfhPp)
    Other:
        - [Vimm's Lair](https://vimm.net)

**Outside Commands**
    AniList: [Wyn's Cogs](https://github.com/TheWyn/Wyn-RedV3Cogs)
    Scrub: [CrunchBangDev's cogs](https://gitlab.com/CrunchBangDev/cbd-cogs)

**Contact**
    - Discord: [BitterSweet#1337](https://discord.gg/ChS8MZDPRA)
    - Reddit: [u/BitterSweetcandyshop](https://www.reddit.com/user/BitterSweetcandyshop)
    - Revolt: @BitterSweet
    - Matrix: bittersweetcandyshop
            """
        )
        embed = embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar_url
        )
        embed = embed.set_footer(
            text="Just Keep Laughing, and keep seeding.",
            icon_url="https://cdn.discordapp.com/avatars/932434610233684068/5c7750171fc026c9ad151b21add11b6f.png?size=4096"
        )
        await ctx.send(embed=embed)