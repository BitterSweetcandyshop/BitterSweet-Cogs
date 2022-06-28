"""
    Module utils
"""

class Utils:

    def nyaa_categories(b):
        category_name = ""
        c = b.replace('/?c=', '')
        cats = c.split('_')

        cat = cats[0]
        subcat = cats[1]

        try:
            category_name = "{} - {}".format(Utils.categories[cat]['name'], Utils.categories[cat]['subcats'][subcat])
        except:
            pass

        return category_name

    def single_parse(header, target, footer, link):
        block = []
        for row in target:
            if row.select('[class="col-md-5"]'):
                for md5 in row.select('[class="col-md-5"]'):
                    block.append(md5.text)
                    if md5.find_all('a'):
                        for a in md5.find_all('a'):
                            if a.get('href'): block.append(a.get('href'))
                    #if (md5.get('herf')): block.append(md5.get('href'))
        
        for a in footer:
           if a.get('href'): block.append(a.get('href'))


        torrent = {}
        try:
            torrent = {
                'category': block[0][1:-1],
                'categoryRaw': block[2].replace('/?c=', ''),
                'url': link,
                'name': header[0].text[4:-4],
                'download_url': f"http://nyaa.si{block[13]}",
                'magnet': block[14],
                'size': block[10],
                'date': block[3],
                'uploader': block[4][1:],
                'uploaderLink': f"http://nyaa.si{block[5]}",
                'seeders': block[6],
                'leechers': block[9],
                'completed_downloads': block[11],
            }
        except IndexError as ie:
            pass
        return torrent


    def parse_nyaa(table_rows, limit):

        torrents = []

        for row in table_rows[:limit]:
            block = []

            for td in row.find_all('td'):
                if td.find_all('a'):
                    for link in td.find_all('a'):
                        if link.get('href')[-9:] != '#comments':
                            block.append(link.get('href'))
                            if link.text.rstrip():
                                block.append(link.text)

                if td.text.rstrip():
                    block.append(td.text.rstrip())
            try:
                torrent = {
                    'category': Utils.nyaa_categories(block[0]),
                    'categoryRaw': block[0].replace('/?c=', ''),
                    'url': "http://nyaa.si{}".format(block[1]),
                    'name': block[2],
                    'download_url': "http://nyaa.si{}".format(block[4]),
                    'magnet': block[5],
                    'size': block[6],
                    'uploader': False,
                    'uploaderLink': False,
                    'date': block[7],
                    'seeders': block[8],
                    'leechers': block[9],
                    'completed_downloads': block[10],
                }

                torrents.append(torrent)
            except IndexError as ie:
                pass

        return torrents

    async def get_code(search:str):
        code = ""
        for outer in uTils.categories.keys():
            if not search.lower().__contains__(uTils.categories[outer]['name'].lower()): continue
            for inner in uTils.categories[outer]['subcats'].keys():
                if not search.lower().__contains__(uTils.categories[outer]['subcats'][inner].lower()): continue
                return [outer, inner]
        

    categories = {
        "1": {
            "name": "Anime",
            "subcats": {
                "1": "Anime Music Video",
                "2": "English-translated",
                "3": "Non-English-translated",
                "4": "Raw"
            }
        },
        "2": {
            "name": "Audio",
            "subcats": {
                "1": "Lossless",
                "2": "Lossy"
            }
        },
        "3": {
            "name": "Literature",
            "subcats": {
                "1": "English-translated",
                "2": "Non-English-translated",
                "3": "Raw"
            }
        },
        "4": {
            "name": "Live Action",
            "subcats": {
                "1": "English-translated",
                "2": "Idol/Promotional Video",
                "3": "Non-English-translated",
                "4": "Raw"
            }
        },
        "5": {
            "name": "Pictures",
            "subcats": {
                "1": "Graphics",
                "2": "Photos"
            }
        },
        "6": {
            "name": "Software",
            "subcats": {
                "1": "Applications",
                "2": "Games"
            }
        }
    }