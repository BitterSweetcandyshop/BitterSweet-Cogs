from .ottsx import ottsx


def setup(bot):
    bot.add_cog(ottsx(bot))