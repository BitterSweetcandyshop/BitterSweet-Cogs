from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class uTils:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}

    def search(self, keyword, bans:list=[], **kwargs):
        """
        Return a list of dicts with the results of the query.
        """

        speed = kwargs.get('speed', False)
        ignore_bans = kwargs.get('ignore_bans', False)
        max = kwargs.get('max', 9)
        allow_nsfw = kwargs.get('allow_nsfw', False)
        category = kwargs.get('category', '')

        torrents = []
        base = 'search'
        if category:
            category = f'/{category}'
            base = 'category-search'

        r = FuturesSession().get(
            f"http://1337x.to/{base}/{keyword}{category}/1/",
            headers=self.headers)

        soup = BeautifulSoup(r.result().text, 'html.parser')
        allas = soup.select('table tr a')

        for i, a in enumerate(allas):
            if len(torrents) > max: break
            main_link = a.get('href')
            if not main_link: continue
            if not main_link.startswith('/torrent/'): continue
            if not ignore_bans:
                if any(main_link.lower().__contains__(ele) for ele in bans): continue
            else: bans = []

            torrent = False
            if speed:
                torrent = self.speedy_search(f"https://1337x.to{main_link}", bans=bans, ignore_bans=ignore_bans, allow_nsfw=allow_nsfw)
            else:
                torrent = self.single_parse(f"https://1337x.to{main_link}", bans=bans, ignore_bans=ignore_bans, allow_nsfw=allow_nsfw)
            if torrent: torrents.append(torrent)

        return torrents
    
    def speedy_search(self, main_link:str, bans:list=[], ignore_bans:bool=False, allow_nsfw:bool=False):
        if ignore_bans: bans=[]
        try:
            magR = FuturesSession().get(
                    main_link,
                    headers=self.headers)
            pirate_soup = BeautifulSoup(magR.result().text, 'html.parser')

            dl_elms = pirate_soup.select("main div div div div div ul li a")
            torrent = ''
            magnet = ''
            for dl_elm in dl_elms:
                if torrent and magnet: break
                if dl_elm:
                    link = dl_elm.get('href')
                    if link:
                        if link.endswith('.torrent'):
                            torrent = link
                        if link.startswith('magnet'):
                            magnet = link
                        

            sl_elm = pirate_soup.select("main div div div div div ul li")
            seeders = ''
            leechers = ''
            size = ''
            for sl in sl_elm:
                if seeders and leechers and size: break
                text_data = sl.get_text()
                if not text_data: continue
                if not text_data.startswith(" "): continue
                if ("xxx" in text_data.lower()) and not allow_nsfw: return False # no nsfw?
                if not (text_data.startswith(" Seeders") or text_data.startswith(" Leechers") or text_data.startswith(" Uploaded By  ") or text_data.startswith(" Total size")): continue
                elif text_data.startswith(" Uploaded By  "):
                    if any(text_data.split(" ")[-2].lower().__contains__(ele) for ele in bans): return False # banned uploader?
                elif text_data.startswith(" Seeders"):
                    seeders = text_data.split(" ")[-2]
                elif text_data.startswith(" Leechers"):
                    leechers = text_data.split(" ")[-2]
                elif text_data.startswith(" Total size"):
                    size = text_data.split(" ")[-3] + " " + text_data.split(" ")[-2]

            torrent = {
                    'magnet': magnet,
                    'torrent': torrent,
                    'url': main_link,
                    'name': main_link[:-1].split("/")[-1],
                    'total_size': size,
                    'seeders': seeders,
                    'leechers': leechers,
            }
            return torrent
        except:
            return False

    def single_parse(self, main_link:str, bans:list=[], ignore_bans:bool=False, allow_nsfw:bool=False):
        try:
            if ignore_bans: bans=[]
            torrent = {
                'url': main_link,
                'name': main_link[:-1].split("/")[-1],
                'genres': [],
                'magnet': '',
                'torrent': '',
                'stream': '',
                'category': '',
                'type': '',
                'language': '',
                'total_size': '',
                'uploaded_by': '',
                'downloads': '',
                'last_checked': '',
                'date_uploaded': '',
                'seeders': '',
                'leechers': '',
                'uploaded_by_url': '',
                'short_title': '',
                'short_title_url': '',
                'description': '',
                'thumbnail': '',
                'nsfw': ''
            }

            magR = FuturesSession().get(main_link, headers=self.headers)
            pirate_soup = BeautifulSoup(magR.result().text, 'html.parser')


            # main data (very fast :3)
            #we do this first since teh category and uploader
            #names are the quickest to look for bans/nsfw
            #to check the uploader name
            sl_elm = pirate_soup.select("main div div div div div ul li")
            for sl in sl_elm:

                if torrent['uploaded_by']:
                    if any(ele in torrent['uploaded_by'].lower() for ele in bans): return False
                
                if torrent['category']:
                    if torrent['category'] == "XXX":
                        if not allow_nsfw: return False
                        torrent['nsfw'] = "nsfw"

                if torrent.get('leechers'): break
                text_data = sl.get_text()
                if not text_data: continue
                if not text_data.startswith(" "): continue
                section = sl.select_one('strong')
                value = sl.select_one('span')
                if (not section) or (not value): continue

                torrent[section.get_text().lower().replace(" ", "_")] = value.get_text()

            if torrent['uploaded_by']: 
                torrent['uploaded_by'] = torrent['uploaded_by'].replace(" ", "")
                torrent['uploaded_by_url'] = f"https://1337x.to/user/{torrent['uploaded_by']}/"
            else: torrent['uploaded_by_url'] = ''

            # The descriptions stuff
            more = pirate_soup.select_one(".content-row")
            if more:
                torrent['short_title'] = more.select_one('h3 a').get_text() or ''
                torrent['short_title_url'] = "https://1337x.to" + more.select_one('h3 a').get('href') or ''
                torrent['description'] = more.select_one('p').get_text() or 'No Description.'
                for genre in more.select('span'):
                    if not genre: continue
                    torrent['genres'].append(genre.get_text())

            # url buttons
            dl_elms = pirate_soup.select("main div div div div div ul li a")
            for dl_elm in dl_elms:
                #once we have everything, gtfo
                if torrent.get('torrent') and torrent.get('magnet') and torrent.get('stream'): break
                if dl_elm:
                    link = dl_elm.get('href')
                    if link:
                        if link.startswith('magnet'):
                            torrent['magnet'] = link
                        if link.endswith('.torrent'):
                            torrent['torrent'] = link
                        if link.startswith('https://novastream'):
                            torrent['stream'] = link

            # image
            image = pirate_soup.select_one(".torrent-image > img:nth-child(1)")
            if image:
                torrent['thumbnail'] = "https:" + image.get('src') or ''

            return torrent
        except:
            return False