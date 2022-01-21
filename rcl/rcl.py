import rclone
import discord
from redbot.core import commands, Config

class RCL(commands.Cog):
    """
    Use rclone!
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_guild(remotes=[])
    
    @commands.group()
    @commands.guild_only()
    async def rcl(self, ctx):
        """Use rclone"""
        pass

    @rcl.command()
    async def listremotes(self, ctx):
        """They tooking my fookin eyes"""
        # Make the remotes stuff
        #I need to make this thing a util somehow
        remotes = await self.conf.guild(ctx.guild).remotes()
        if len(remotes) == 0:
            await ctx.send("You currently have no remotes.")
            return
        remote_configs = []
        for remote in remotes:
            remote_configs.append(remote["config"])
        remote_configs = "\n\n".join(remote_configs)

        result = rclone.with_config(remote_configs).listremotes()
        result = result.get("out")
        result_formmated = "```"
        for res in result.splitlines():
            print(res)
            result_formmated += str(res)[2:-1]
        await ctx.send(result_formmated + "\n```")

    @rcl.group()
    async def config(self, ctx):
        """Manage remotes"""
        pass

    @config.command()
    async def add(self, ctx, *, config: str):
        """
        Paste in the remote you want from your rclone config file.
        Careful where you send your remote data, since it can be used to access you account!
        """
        print(config)
        remotes = await self.conf.guild(ctx.guild).remotes()
        remote_name = config.splitlines()[0][1:-1]
        remotes.append({
            "remote_name": remote_name,
            "config": config
        })
        print(remotes)
        await self.conf.guild(ctx.guild).remotes.set(remotes)

    @config.command()
    async def reset(self, ctx):
        """
        Deletes all the saved remotes permently.
        Careful using this, there's no confirmation message!
        """
        await self.conf.guild(ctx.guild).remotes.set([])
        await ctx.send("Reset database.")