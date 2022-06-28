import re
import json
import discord
from redbot.core import commands

exhelp: commands.Command = None
exinfo: commands.Command = None
class Helpless(commands.Cog):
    """Obtain torrents from nyaa."""



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
            description="""**Torrenting**:
    - `ottsx` 1337x based commands.
    - `nyaa` Nyaa based commands.
    - `rarbg` Rarbg based commands.
**Misc**:
    - `contact` Reach out to BitterSweet#1337.
    - `invite` Invite Quinque to your own sevrer. 
    - `uptime` Total time Quinque has been online.
    - `set` Other tools for server settings.
**AniList**:
    - `anime` Searches for an anime using Anilist.
    - `character` Searches for an anime character using Anilist.
    - `manga` Searches for a manga using Anilist.
    -  `user` Searches for a user on Anilist.
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

**Contact**
    Discord: [BitterSweet#1337](https://discord.gg/nKdNFzHW)
    Reddit: [u/BitterSweetcandyshop](https://www.reddit.com/user/BitterSweetcandyshop)
    Revolt: @BitterSweet
    Matrix: bittersweetcandyshop
            """
        )
        embed = embed.set_author(
            name=ctx.author.display_name,
            icon_url=ctx.author.avatar_url
        )
        embed = embed.set_footer(
            text="Stay crazy, keep seeding.",
            icon_url="https://cdn.discordapp.com/avatars/932434610233684068/5c7750171fc026c9ad151b21add11b6f.png?size=4096"
        )
        await ctx.send(embed=embed)