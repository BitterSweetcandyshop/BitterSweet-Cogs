import rclone
import discord
from redbot.core import commands, Config, checks

async def compile_config(self, ctx):
        remotes = await self.conf.guild(ctx.guild).remotes()
        if len(remotes) == 0:
            return False
        remote_configs = ""
        for remote in remotes:
            remote_configs += remote["config"] + "\n\n"
        return remote_configs

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

# Commands to veiw drive contents
    @rcl.command()
    async def listremotes(self, ctx):
        """List the remotes you have stored."""
        config = await compile_config(self, ctx)
        if not config:
            await ctx.send("No remotes where found.")
            return
        result = rclone.with_config(config).listremotes()
        result = result.get("out")
        result_formmated = "```"
        for res in result.splitlines():
            print(res)
            result_formmated += str(res)[2:-1] + "\n"
        await ctx.send(result_formmated + "\n```")

    @rcl.command()
    async def lsf(self, ctx, *, remote: str):
        """
        From `rclone lsf --help`:

        List the contents of the source path (directories and objects) to
standard output in a form which is easy to parse by scripts.  By
default this will just be the names of the objects and directories,
one per line.  The directories will have a / suffix.
        """
        config = await compile_config(self, ctx)
        if not config:
            await ctx.send("No remotes where found.")
            return
        print(remote)
        result = rclone.with_config(config).run_cmd(command="lsf", extra_args=[remote])
        result = str(result.get("out") or result.get("error") or result.get("code")).replace("\\n", "\n")[2:-1]
        if len(result) > 1990:
            await ctx.send("The message was too large.")
            return
        await ctx.send("```" + result + "```")


    @rcl.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def raw(self, ctx, command: str, *, args: str = "RCL_NONE"):
        """
        Runs any rclone command like the console.
        Using a data transfer commnad can be taxing on the bot's host!
        """
        config = await compile_config(self, ctx)
        if not config:
            await ctx.send("No remotes where found.")
            return
        result = rclone.with_config(config)
        if args == "RCL_NONE":
            result = result.run_cmd(command=command)
        else:
            result = result.run_cmd(command=command, extra_args=args.split(" "))
        
        if len(result) > 1990:
            await ctx.send("The message was too large.")
            return
        await ctx.send("```" + str(result.get("out") or result.get("error")).replace("\\n", "\n")[2:-1] + "```")


# Config commands
    @rcl.group()
    @checks.admin_or_permissions(manage_guild=True)
    async def config(self, ctx):
        """Manage remotes."""
        pass

    @config.command()
    async def add(self, ctx, *, config: str):
        """
        Paste in the remote you want from your rclone config file.
        Careful where you send your remote data, since it can be used to access you account!

        Rember, when you paste it to delete accidental newlines.
        """
        remotes = await self.conf.guild(ctx.guild).remotes()
        remote_name = config.splitlines()[0][1:-1]
        remotes.append({
            "remote_name": remote_name,
            "config": config
        })
        await self.conf.guild(ctx.guild).remotes.set(remotes)
        await ctx.send("Added the remote **{}**.".format(remote_name))

    @config.command()
    async def remove(self, ctx, remote_name: str):
        """
        Removes a specified remote from the system.
        You do not put the `:` at the end.

        There is no confirmation message.
        """
        old_remotes = await self.conf.guild(ctx.guild).remotes()
        new_remotes = []
        for remote in old_remotes:
            if not remote["remote_name"] ==  remote_name:
                new_remotes += remote
        
        await self.conf.guild(ctx.guild).remotes.set(new_remotes)
        await ctx.send("Removed the remote **{}**.".format(remote_name))

    @config.command()
    async def reset(self, ctx):
        """
        Deletes all the saved remotes permently.
        Careful using this, there's no confirmation message!
        """
        await self.conf.guild(ctx.guild).remotes.set([])
        await ctx.send("Reset database.")