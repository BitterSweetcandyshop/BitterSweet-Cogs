from torrently.commands.ottsx_core import ottsx
from torrently.commands.nyaa_core import nyaa

def setup(bot):
    bot.add_cog(ottsx(bot))
    bot.add_cog(nyaa(bot))