import discord
from typing import Optional
from redbot.core import commands, checks, Config, bot
from redbot.core.utils.menus import DEFAULT_CONTROLS, menu

class EmbedSpeaker(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # I feel smart: My github username has the numbers 1 and 3 swapped
        #the last three numbers are the index, so this is cog-config 1
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_guild(allowed_channels=[])

        @commands.group()
        @commands.guild_only()
        def embedspeaker(self, ctx):
            """
            Converets sent messages into embeds.

            Specify a channel (by mention), if none is specified it will assume the channel where the command was typed.
            """
            pass

        @embedspeaker.command()
        @checks.admin_or_permissions(manage_guild=True)
        async def add(self, ctx: commands.Context, channel_specified: Optional[discord.TextChannel] = None):

            if not channel_specified:
                channel_specified = ctx.channel
            current_channels = await self.conf.guild(ctx.guild).allowed_channels()
            new_channel = {
                "id": channel_specified.id,
                "name": channel_specified.name
            }

            for saved_channel in current_channels:
                if saved_channel.id == new_channel.id:
                    await ctx.send("Channel is already added")
                    return
            
            current_channels.append(new_channel)
            await self.conf.guild(ctx.guild).allowed_channels.set(current_channels)


        @embedspeaker.command()
        @checks.admin_or_permissions(manage_guild=True)
        async def remove(self, ctx, channel_specified: Optional[discord.TextChannel] = None):

            if not channel_specified:
                channel_specified = ctx.channel
            current_channels = await self.conf.guild(ctx.guild).allowed_channels()
            channel_specified = {
                "id": channel_specified.id,
                "name": channel_specified.name
            }

            specified_removed = False
            for i, saved_channel in enumerate(current_channels):
                if saved_channel.id == channel_specified.id:
                    current_channels.pop(i)
                    specified_removed = True
            
            if specified_removed:
                ctx.send("Removed {} from embedspeaker".format(channel_specified.name))
