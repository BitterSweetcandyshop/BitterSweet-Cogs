# This is actually the first thing I have ever done in python so, yay!
# Let's ignore the large amount of copy-paste, I needed an example
# I typed it all so I can learn as I go through it
import re
import json
import aiohttp
import discord
from py1337x import py1337x
from redbot.core import commands, Config, checks
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

# Based primebot (https://github.com/pryme-svg/PrimeBot/blob/master/primebot/ext/torrent.py#L31)
async def shorten(self, magnet: str):
    res = False
    async with aiohttp.ClientSession() as session:
        async with session.get("http://mgnet.me/api/create?&format=json&opt=&m={}".format(magnet)) as response:
            res = await response.read()
    res = json.loads(res)
    return res["shorturl"]

async def make_embed(self, torrent_link):
    try:
        clientX = py1337x(proxy='1337x.to')
        torrent_info = py1337x().info(torrent_link)
        print(torrent_info['name'])

        short_magnet = await shorten(self, torrent_info["magnetLink"])

        embed = discord.Embed(
            title=torrent_info["shortName"],
            url=torrent_link,
           description=f"*{torrent_info['name']}*\n\n{torrent_info['description']}"
        )
        embed = embed.add_field(
            name="Magnet Link",
            value=f"||{short_magnet}||",
            inline=False
        )
        if not torrent_info["genre"]:
            torrent_info["genre"] = ["Not Found"]
        embed = embed.add_field(
            name="Genres: " + ", ".join(torrent_info["genre"]),
            value=f"**Uploaded by:** {torrent_info['uploader']} *({torrent_info['uploadDate']})*",
            inline=False
        )
        emebed = embed.add_field(
            name=f"**Quality:** {torrent_info['type']}",
            value="__ __",
            inline=False
        )
        emebed = embed.add_field(
            name="Size",
            value=torrent_info["size"],
            inline=True
        )
        emebed = embed.add_field(
            name="Seeders",
            value=torrent_info["seeders"],
            inline=True
        )
        emebed = embed.add_field(
            name="Leechers",
            value=torrent_info["leechers"],
            inline=True
        )

        if torrent_info["thumbnail"]:
            embed = embed.set_thumbnail(
                url=torrent_info["thumbnail"].replace("https://www.1377x.to", "https:")
            )
        return embed
    except AttributeError():
        pass

class ottsx(commands.Cog):
    """
    Search 1337x.
    """

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_channel(smartlink_enabled=False)


    @commands.group()
    @commands.guild_only()
    async def ottsx(self, ctx):
        """Search 1337x.to."""

    @ottsx.command()
    async def lookup(self, ctx, *, query: str):
        """Search all of 1337x."""
        count = "20"
        pages = []
        try:
            async with ctx.typing():
                clientX = py1337x(proxy='1337x.to')
                result = clientX.search(query)['items']
            if len(result) < int(count):
                count = len(result)
                for res in result[0:int(count):]:
                    new_page = await make_embed(self, res["link"])
                    pages.append(new_page)
            else:
                for res in result[0:int(count):]:
                    new_page = await make_embed(self, res["link"])
                    pages.append(new_page)

            if len(pages) == 0:
                await ctx.send(f"Sorry, no results for **{query}**.")
                return

            await menu(ctx, pages, DEFAULT_CONTROLS)

        except AttributeError:
            await ctx.send(f"Sorry, no results for **{query}** or there was an error.")

    @ottsx.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def smartlink(self, ctx, toggle: bool):
        """
        Smartlink for OTTSX makes it so whenever a link is sent in an enabled channel. \
        It well fetch data off 1337x about the torrent
        _ _
        Run the command in the channel you want enabled/disabled to alter.
        """

        current_status = await self.conf.channel(ctx.channel).smartlink_enabled()
        if toggle == current_status:
            await ctx.send("The channel **{}** is already set to **{}** for smartlink.".format(ctx.channel.name, toggle))
            return
        
        await self.conf.channel(ctx.channel).smartlink_enabled.set(toggle)
        await ctx.send("The channel **{}** now has smartlink as **{}**.".format(ctx.channel.name, toggle))

    @commands.Cog.listener()
    async def on_message(self, message):
        print("New message thing")
        torrent_link = re.search("https?:\/\/www\.1337x\.\w{2}\/torrent\/\S+", message.content)
        if not torrent_link:
            return

        torrent_link = torrent_link.group()

        smartlink_enabled = await self.conf.channel(message.channel).smartlink_enabled()
        if not smartlink_enabled:
            return

        embed = await make_embed(self, torrent_link)
        await message.channel.send(embed=embed)