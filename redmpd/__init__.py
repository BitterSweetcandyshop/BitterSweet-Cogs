from .redmpd import red_mpd

def setup(bot):
    bot.add_cog(red_mpd(bot))