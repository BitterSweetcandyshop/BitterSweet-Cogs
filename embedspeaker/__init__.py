from .embedspeaker import EmbedSpeaker


def setup(bot):
    bot.add_cog(EmbedSpeaker(bot))