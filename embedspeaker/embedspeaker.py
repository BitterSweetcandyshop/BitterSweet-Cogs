import discord
from typing import Optional
from redbot.core import commands, checks, Config, bot
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

class EmbedSpeaker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_guild(allowed_channels=[])

    @commands.group()
    @commands.guild_only()
    async def embedspeaker(self, ctx):
        """
        Converets sent messages into embeds.

        Specify a channel (by mention), if none is specified it will assume the channel where the command was typed.
        """
        pass

    @embedspeaker.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def add(self, ctx):
        """Add a channel to embedspeaker."""

        current_channels = await self.conf.guild(ctx.guild).allowed_channels()
        channel_specified = {
            "id": ctx.channel.id,
            "name": ctx.channel.name
        }

        if len(current_channels) > 0:
            for saved_channel in current_channels:
                if saved_channel["id"] == channel_specified["id"]:
                    await ctx.send("Channel **{}** is already a embedspeaker channel.".format(channel_specified["name"]))
                    return
            
        current_channels.append(channel_specified)
        await self.conf.guild(ctx.guild).allowed_channels.set(current_channels)
        await ctx.send("Added **{}** to embedspeaker.".format(channel_specified["name"]))


    @embedspeaker.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def remove(self, ctx):
        """Remove a channel from embedspeaker."""

        current_channels = await self.conf.guild(ctx.guild).allowed_channels()
        channel_specified = {
            "id": ctx.channel.id,
            "name": ctx.channel.name
        }

        if len(current_channels) == 0:
            await ctx.send("You have no channels on embedspeaker.")
            return

        specified_removed = False
        for i, saved_channel in enumerate(current_channels):
            if saved_channel["id"] == channel_specified["id"]:
                current_channels.pop(i)
                await self.conf.guild(ctx.guild).allowed_channels.set(current_channels.pop(i))
                specified_removed = True
            
        if specified_removed:
            await ctx.send("Removed **{}** from embedspeaker.".format(channel_specified["name"]))
        else:
            await ctx.send("Channel **{}** wasn't an embedspeaker channel.".format(channel_specified["name"]))


    @embedspeaker.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def reset(self, ctx):
        await self.conf.guild(ctx.guild).allowed_channels.set([])
        await ctx.send("Removed all channels from embedspeaker.")


    @commands.Cog.listener()
    async def on_message(self, message):
        make_embed = False
        current_channel = message.channel
        stored_channels = await self.conf.guild(message.guild).allowed_channels()
        if len(stored_channels) == 0:
            return
        
        if message.author.bot:
            return

        for stored_channel in stored_channels:
            if stored_channel["id"] == current_channel.id:
                make_embed = True
        
        if make_embed:
            user = await self.bot.fetch_user(message.author.id)
            print(user.avatar_url)
            embed = discord.Embed(
                description=message.content
            )
            embed.set_author(
                name=message.author,
                icon_url=user.avatar_url
            )
            await self.bot.send_filtered(message.channel, embed=embed)
            await message.delete()
            return
