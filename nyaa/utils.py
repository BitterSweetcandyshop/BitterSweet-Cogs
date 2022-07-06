import requests
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

"""
    Module utils
"""

class Utils:


    def search(self, keyword, limit:int=11, bans:list=[], **kwargs):
        """Search nyaa by scraping the restuls
         Return a list of dicts with the results of the query.
        """
        category = kwargs.get('category', 0)
        subcategory = kwargs.get('subcategory', 0)
        filters = kwargs.get('filters', 0)
        page = kwargs.get('page', 0)
        sort = kwargs.get('sort', 'seeders')
        if sort: sort = "&o=desc&s=" + sort
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        session = FuturesSession()



        r = session.get(f"http://nyaa.si/?f={filters}&c={category}_{subcategory}&q={keyword}{sort}", headers=headers)

        soup = BeautifulSoup(r.result().text, 'html.parser')
        rows = soup.select('table tr')
        results = {}
        if rows:
            results = self.parse_nyaa(rows, limit, bans)
            return results
        else: return []

    def single_parse(self, link:str, **kwargs):
        """Get information from a nyaa link"""
        kwargs.get('sort', 'seeders')
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
        session = FuturesSession()

        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.result().text, 'html.parser')
        target = soup.select('body div div div [class="row"]')
        header = soup.select('[class="panel-title"]')
        footer = soup.select('[class="panel panel-danger"] [class="panel-footer clearfix"] a')


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


    def parse_nyaa(self, table_rows, limit:int=11, bans=[]):
        """Parse the search table from nyaa"""
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
            
            if len(block) < 9: continue

            if bans:
                if any(ele in block[2].lower() for ele in bans): continue

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


    def get_ani(self, id:int):
        query = """
query ($id: Int) {
    Media (id: $id, type: ANIME) {
        id
        title {
            romaji
            english
            native
        }
    }
}
"""
        return requests.post('https://graphql.anilist.co', json={'query': query, 'variables': {'id': id}}).json()


    async def get_code(search:str):
        code = ""
        for outer in uTils.categories.keys():
            if not search.lower().__contains__(uTils.categories[outer]['name'].lower()): continue
            for inner in uTils.categories[outer]['subcats'].keys():
                if not search.lower().__contains__(uTils.categories[outer]['subcats'][inner].lower()): continue
                return [outer, inner]

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