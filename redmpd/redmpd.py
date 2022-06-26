import time
import discord
from mpd import MPDClient
from table2ascii import table2ascii, TableStyle
from redbot.core import commands, Config, checks

# Oh yea this takes in IP addresses, so be responsible and not leak a bunch of IPs
#... dumbass

async def create_client(self, ctx):
    try: 
        client = MPDClient()
        client.connect("localhost", 6600)
        client.timeout = 10 
        client.idleTimeout = None
        client.iterate = True
    except ConnectionError():
        await ctx.send("Failed to connect to host.")
        return

    return client

def return_time(duration):
    return time.strftime("%M:%S", time.gmtime(int(duration)))

def build_table(song_list, amount):
    format = []
    for i, song in enumerate(song_list):
        if i < amount:
            print(song["title"])
            title = song["title"] or "N/A"
            if len(title) > 15:
                title = title[:15] + "..."
            artist = song["artist"] or "N/A"
            if len(artist) > 15:
                artist = artist[:15] + "..."
            album = song["album"] or "N/A"
            if len(album) > 15:
                album = album[:15] + "..."
            
            format.append([title, artist, album])

    if len(format) == 0:
        return "No Results."

    output = table2ascii(
        header=["Title", "Artist", "Album"],
        body=format,
        style= TableStyle.from_string("*-..*||:+-+:+     *''*")
    )

    return output


class red_mpd(commands.Cog):
    """
    Scan links in chat for viruses to ensure saftey powered by you favourite sites.
    """

    def __init__(self, bot):
        self.bot = bot
        self.conf = Config.get_conf(self, identifier="UNIQUE_ID", force_registration=True)
        self.conf.register_member(client=None)

    @commands.group()
    async def mpd(self, ctx):
        "Controliing mpd clients through discord."
        pass

# INFORMATION FETCHING
    @mpd.command()
    async def currentsong(self, ctx):
        "Get information about the currently playing song."
        client = await create_client(self, ctx)
        
        song = client.currentsong()
        print(song)
        song_length = return_time(song['time'])
        position = return_time(song['pos'])


        embed = discord.Embed(
            title=song["title"] + " by " + song["artist"],
            description=f"""*#{song['id']}. [{song['file'].split('/')[-1]}**]*
            
            Playback: {position}/{song_length}
            Released: {song['date']}
            """
        )
        await ctx.send(embed=embed)

        client.disconnect()

    
    @mpd.command()
    async def stats(self, ctx):
        "General information about the music database."
        client = await create_client(self, ctx)

        stats = client.stats()
        await ctx.send(f"Total Artists: {stats['artists']}\nTotal Albums: {stats['albums']}\nTotal Songs: {stats['songs']}")

        client.disconnect()

    @mpd.command()
    async def search(self, ctx, *, query: str):
        "Search the music database for a song by finding query is in the file name"
        client = await create_client(self, ctx)

        results = client.search("filename", query)
        table = build_table(results, 10)
        await ctx.send("```\n" + table + "\n```")

        client.disconnect()

    @mpd.command()
    async def playlist(self, ctx, amount: int = 5):
        "Shows first few songs in the current playlist."
        client = await create_client(self, ctx)

        playlist = client.playlistinfo()
        table = build_table(playlist, amount)
        await ctx.send("```\n" + table + "\nTotal Tracks: "+ str(len(playlist)) + "\n```")

        client.disconnect()

# CONTROLS