import re
import json
import aiohttp
import discord

class helpers:

    async def shorten(magnet: str):
        res = False
        async with aiohttp.ClientSession() as session:
            async with session.get("http://mgnet.me/api/create?&format=json&opt=&m={}".format(magnet)) as response: res = await response.read()
        res = json.loads(res)
        return res["shorturl"]

    # Parsers
    class parsers:
        async def solve_nfilter(self, ctx):
            nlevel = await self.conf.guild(ctx.guild).nsfw_filter_level()
            if nlevel == 0: return True
            elif nlevel == 1: return ctx.channel.is_nsfw()
            elif nlevel == 2: return False

        def ottsx_flagging(line:str):
            ret = {'line': [], 'flags': []}
            if not line.__contains__('--'): return ret
            for word in line.split(" "):
                if not word.startswith('--'):
                    ret['line'].append(word)
                    continue
                word = word[2:]
                if word == '--size': ret['flags'].append('size/desc')
                elif word in ['leechers', 'leech', 'leeches']: ret['flags'].append('leechers/desc')
                elif word == 'date': ret['flags'].append('time/desc')
                elif word in ['seeders', 'seed', 'seeds']: ret['flags'].append('seeders/desc')
                else: ret['line'].append(word)
            return {'line': " ".join(ret['line']), 'flags': ret['flags']}

        def nyaa_flagging(line:str):
            ret = {'line': [], 'flags': {'category':'', 'sort': ''}}
            if not line.__contains__('--'): return ret
            for word in line.split(" "):
                if not word.startswith('--'):
                    ret['line'].append(word)
                    continue
                word = word[2:]
                # Sort
                if word == 'size': ret['flags']['sort'] = 'size'
                elif word in ['leechers', 'leech', 'leeches']: ret['flags']['sort'] = 'leechers'
                elif word in ['seeders', 'seed', 'seeds']: ret['flags']['sort'] = 'seeders'
                elif word == 'date': ret['flags']['sort'] = ret['flags']['sort'] = 'id'
                elif word in ['downloads', 'dl', 'dls']: ret['flags']['sort'] = 'downloads'
                # Category
                elif word in ['manga']: ret['flags']['category'] = '3_1'
                elif word in ['anime']: ret['flags']['category'] = '1_0'
                # Fallback
                else: ret['line'].append(word)
            return {'line': " ".join(ret['line']), 'flags': ret['flags']}

    # Embed Builders
    class embed_build:
        #Build as a list on a single embed
        async def list(torrents:list):
            format = []
            for i, torrent_info in enumerate(torrents):
                torrents_markup = []
                for link in torrent_info['torrent']: torrents_markup.append(f'[{link["name"]}]({link["link"]})')
                torrent_info['torrent'] = " - ".join(torrents_markup)
                format.append(f"\n**{i+1}. [{torrent_info['name'].replace('[...', '...')}]({torrent_info['url']})**\n**[Magnet]({await helpers.shorten(torrent_info['magnet'])}) - {torrent_info['torrent']}** | Seeders: {torrent_info['seeders']} | Size: {torrent_info['total_size']}")
            embed = discord.Embed(description="".join(format))
            return embed

        # Build as pages
        async def page(torrent_info:dict, page:int=1, total_pages:int=1):
            # Make certian sections look good for the embed
            #Download
            download_options = []
            for torrent in torrent_info['torrent']: download_options.append(f'[{torrent["name"]}]({torrent["link"]})')
            for ddl in torrent_info['ddl']: download_options.append(f'[{ddl["name"]}]({ddl["link"]})')
            if torrent_info['stream']: download_options.append(f"[NovaStream]({torrent_info['stream']})")
            if torrent_info['hash']: torrent_info['hash'] = f"`{torrent_info['hash']}`"
            else: torrent_info['hash'] = "No Hash Found"
            if torrent_info['magnet']: download_options.append(f"[Magnet]({await helpers.shorten(torrent_info['magnet'])})")
            download_options = " - ".join(download_options)
            #Uploader
            if torrent_info['uploaded_by'] and torrent_info['uploaded_by_url']:
                torrent_info['uploaded_by'] = f"[{torrent_info['uploaded_by']}]({torrent_info['uploaded_by_url']})"
                torrent_info['uploaded_by_url'] = ''
            if torrent_info['source'] == '1337x': torrent_info['description'] = torrent_info['description'][:250]
            # ... yes I know about multi-line strings, no I do not care.
            description=f"{torrent_info['description']}\n\n{torrent_info['hash']}\n**Download:** {download_options}\n**Uploaded by:** {torrent_info['uploaded_by']} *({torrent_info['date_uploaded']})*"

            if torrent_info['genres']: description += f"\n**Genres:** {', '.join(torrent_info['genres'])}"
            if torrent_info['language'] and torrent_info['tyoe']: description += f"\n**Type:** {torrent_info['language']} - {torrent_info['type']}"
            elif torrent_info['category']: description += f"\n**Type:** {torrent_info['category']}"
            title = torrent_info['short_title']
            url = torrent_info['short_title_url']
            if not title:
                title = torrent_info['name']
                url = torrent_info['url']
                description = f"*[{torrent_info['name']}]({torrent_info['url']})*\n\n" + description

            embed = discord.Embed(
                title=title,
                url=url,
                description=description.strip()
            )
            for stat in ['seeders', 'leechers', 'total_size']:
                if torrent_info[stat]: embed = embed.add_field(inline=True, name=stat.replace("total_", "").title(), value=torrent_info[stat])
            if torrent_info['thumbnail']: embed = embed.set_thumbnail(url=torrent_info['thumbnail'])
            if torrent_info['image']: embed = embed.set_image(url=torrent_info['image'])
            if (total_pages != 1) and total_pages: embed = embed.set_footer(text=f'Page: ({str(page)}/{str(total_pages)})')

            return embed