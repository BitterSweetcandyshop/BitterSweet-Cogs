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
**Games**
    Search for your favourite games.
    - `repack` Search for repacks.
    - `fitgirl` (repacks)
    - `scooter` (repacks)
    - `kaos` (repacks)
    - `vimm` (roms)
**Software**
    - `software` Search for software.
    - `monkrus` (software)
    - `filecr` (software)
**Misc**
    Need help or want to know some stats?
    - `contact` Reach out to BitterSweet#1337.
    - `invite` Invite Bit to your own sevrer. 
    - `set` Other tools for server settings.
    - `info` More information about the bot, credits, and support.
**AniList**
    - `anime` Searches for an anime using Anilist.
    - `character` Searches for an anime character using Anilist.
    - `manga` Searches for a manga using Anilist.
    - `user` Searches for a user on Anilist.
**Notes**
    - Do not use 1337x for software or games.
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
    __Repackers__
        - [Scooter](https://scooter-repacks.site)
        - [FitGirl](https://fitgirl-repacks.site)
        - [KaOsKrew](https://kaoskrew.org)
        - [Darck](https://darckrepacks.com/)
    __Valued Feedback__
        - [DieDoesMC#0945](https://discord.gg/8WCZGZ5Ucr)
        - Bulldög#0533
        - [champagne.sunshine#0968](https://discord.gg/38G68UfhPp)
        - ReX_XeNoME#9250
    __Other__
        - [Vimm's Lair](https://vimm.net)
        - Pfp: ju ju bee#4839

**Outside Commands**
    AniList: [Wyn's Cogs](https://github.com/TheWyn/Wyn-RedV3Cogs)
    Scrub: [CrunchBangDev's cogs](https://gitlab.com/CrunchBangDev/cbd-cogs)

**Donations**
    I don't take donations right now since server costs aren't an issue.
    > Consider donating to the awesome repackers and sites this bot uses!

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
            icon_url="https://cdn.discordapp.com/attachments/932537561166008360/1003456562083414026/clean_rat.jpg"
        )
        await ctx.send(embed=embed)