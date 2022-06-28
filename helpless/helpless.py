import re
import json
import discord
from redbot.core import commands


exhelp = None
exfindcog = None
exlicenseinfo = None
exinfo = None
class Helpless(commands.Cog):
    """Obtain torrents from nyaa."""



    def __init__(self, bot):
        self.bot = bot
        global exhelp
        exhelp = bot.get_command("help")
        exfindcog = bot.get_command("findcog")
        exlicenseinfo = bot.get_command("licenseinfo")
        exinfo = bot.get_command("info")
        if exhelp:
            bot.remove_command(exhelp.name)
            bot.remove_command(exfindcog.name)
            bot.remove_command(exlicenseinfo.name)
            bot.remove_command(exinfo.name)

    def cog_unload(self):
        global exhelp
        if exhelp:
            try:
                self.bot.remove_command("help")
                self.bot.exfindcog = bot.remove_command("findcog")
                self.bot.exlicenseinfo = bot.remove_command("licenseinfo")
                self.bot.exinfo = bot.remove_command("info")
            except:
                pass
            self.bot.add_command(exhelp)
            self.bot.exfindcog = bot.remove_command("findcog")
            self.bot.exlicenseinfo = bot.remove_command("licenseinfo")
            self.bot.exinfo = bot.remove_command("info")

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