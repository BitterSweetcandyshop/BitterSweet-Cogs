from copy import deepcopy
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class uTils:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}

    torrent = {
        'url': '',
        'name': '',
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
        'nsfw': False,
        'risk': False
    }

    def search(keyword, bans:list=[], **kwargs):
        """
        Return a list of dicts with the results of the query.
        """

        speed = kwargs.get('speed', False)
        ignore_bans = kwargs.get('ignore_bans', False)
        max = kwargs.get('max', 9)
        allow_nsfw = kwargs.get('allow_nsfw', False)
        category = kwargs.get('category', '')
        filter = kwargs.get('filter', '')

        # So by using '' as default value, nothing will be printed, but if there
        #is a value, format it to fit in the search url correctly
        torrents = []
        base = 'search'
        if (category) and (not filter):
            category = f'/{category}'
            base = 'category-search'
        elif category and filter:
            category = f'/{category}'
            filter = f'/{filter}'
            base = 'sort-category-search'
        elif(not category) and (filter):
            filter = f'/{filter}'
            base = 'sort-search'

        r = FuturesSession().get(f"http://1337x.to/{base}/{keyword}{category}{filter}/1/",headers=uTils.headers)

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
                torrent = uTils.speedy_search(f"https://1337x.to{main_link}", bans=bans, ignore_bans=ignore_bans, allow_nsfw=allow_nsfw)
            else:
                torrent = uTils.single_parse(f"https://1337x.to{main_link}", bans=bans, ignore_bans=ignore_bans, allow_nsfw=allow_nsfw)
            if torrent: torrents.append(torrent)

        return torrents
    
    def speedy_search(main_link:str, bans:list=[], ignore_bans:bool=False, allow_nsfw:bool=False):
    #settup
        if ignore_bans: bans=[]
        magR = FuturesSession().get(main_link,headers=uTils.headers)
        pirate_soup = BeautifulSoup(magR.result().text, 'html.parser')

        torrent = deepcopy(uTils.torrent)

    # Name and url
        torrent['name'] = pirate_soup.select_one('div.box-info-heading').get_text().strip()
        if any(ele in torrent['name'].lower() for ele in bans): return False
        torrent['url'] = main_link

    # Center Table scraping (Speed)
        sl_elm = pirate_soup.select("main div div div div div ul.list li")
        for sl in sl_elm:
            if torrent['leechers']: break
            try:
                text_data = sl.get_text().strip()
                if text_data.startswith("uploaded by"):
                    if any(ele in text_data[11:] for ele in bans): return False
                    torrent['uploaded_by'] = text_data
                text_data = text_data.lower()
                if text_data.startswith("seeders"): torrent['seeders'] = text_data.split(" ")[-1]
                elif text_data.startswith("category"):
                    if text_data.__contains__("xxx"): 
                        if not allow_nsfw: return False
                        print("Allowed nsfw")
                        print()
                        torrent['nsfw'] = True
                    torrent['category'] = text_data.title()
                    if text_data.__contains__("games") or text_data.__contains__("software"): torrent['risk'] = True
                elif text_data.startswith("leechers"): torrent['leechers'] = text_data.split(" ")[-1]
                elif text_data.startswith("downloads"): torrent['downloads'] = text_data.split(" ")[-1]
                elif text_data.startswith("total size"): torrent['total_size'] = "".join(text_data.split(" ")[-2:])
            except: continue

        # Buttons
        dl_elms = pirate_soup.select("main div div div div div ul li a")
        for dl_elm in dl_elms:
            if dl_elm:
                link = dl_elm.get('href')
                if link:
                    if link.endswith('.torrent'): torrent['torrent'] = [{'name': link.split('//')[-1].split('/')[0], 'link': link}]
                    elif link.startswith('magnet'): torrent['magnet'] = link

        # Center Table scraping

        return torrent

    def single_parse(main_link:str, bans:list=[], ignore_bans:bool=False, allow_nsfw:bool=False):
        try:
        #settup
            if ignore_bans: bans=[]
            magR = FuturesSession().get(main_link,headers=uTils.headers)
            pirate_soup = BeautifulSoup(magR.result().text, 'html.parser')

            torrent = deepcopy(uTils.torrent)

        # Name and url
            torrent['name'] = pirate_soup.select_one('div.box-info-heading').get_text().strip()
            if any(ele in torrent['name'].lower() for ele in bans): return False
            torrent['url'] = main_link

        # Buttons
            dl_elms = pirate_soup.select("main div div div div div ul li a")
            for dl_elm in dl_elms:
                if dl_elm:
                    link = dl_elm.get('href')
                    if link:
                        if link.endswith('.torrent'): torrent['torrent'] = [{'name': link.split('//')[-1].split('/')[0], 'link': link}]
                        elif link.startswith('magnet'): torrent['magnet'] = link
                        elif link.startswith('https://nova'): torrent['stream'] = link

        # Center Table scraping (Slow)
            sl_elm = pirate_soup.select("main div div div div div ul.list li")
            for sl in sl_elm:
                if torrent['leechers']: break
                try:
                    # These items require a filter to ensure they can be added
                    section = sl.select_one('strong').get_text().strip().lower().replace(" ", "_")
                    section_value = sl.select_one('span').get_text().strip()
                    if section == "uploaded_by":
                        if any(ele in section_value.lower() for ele in bans): return False
                        torrent['uploaded_by'] = section_value
                        torrent['uploaded_by_url'] = sl.select_one('a').get('href')
                        continue
                    elif section == "category":
                        if section_value.lower() == "xxx": 
                            if not allow_nsfw: continue
                            torrent['nsfw'] = True
                        elif section_value.lower() in ['software', 'games']: torrent['risk'] = True
                        continue

                    # These I just automate, idgaf
                    torrent[section] = section_value.lower()
                    
                except: continue

        # The descriptions stuff
            more = pirate_soup.select_one(".content-row")
            if more:
                torrent['short_title'] = more.select_one('h3 a').get_text() or ''
                torrent['short_title_url'] = "https://1337x.to" + more.select_one('h3 a').get('href') or ''
                torrent['description'] = more.select_one('p').get_text() or 'No Description.'
                for genre in more.select('span'):
                    if not genre: continue
                    torrent['genres'].append(genre.get_text())

        # image
            image = pirate_soup.select_one(".torrent-image > img:nth-child(1)")
            if image: torrent['thumbnail'] = "https:" + image.get('src') or ''
        #
            print(torrent)
            return torrent
        except:
            return False