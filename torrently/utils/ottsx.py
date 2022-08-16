import requests
from copy import deepcopy
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class ottsx_utils:
    """TOllkit for scraping 1337x"""
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    torrent_format = {
        # Main
        'source': '1337x',
        'url': '',
        'name': '',
        # Intall/Play
        'magnet': '',
        'torrent': [],
        'ddl': [],
        'hash': '',
        'stream': '',
        'imdb': '',
        # Uploader
        'uploaded_by': '',
        'uploaded_by_url': '',
        'category': '',
        'type': '',
        'language': '',
        'total_size': '',
        'genres': [],
        # Dates
        'last_checked': '',
        'date_uploaded': '',
        # Install stats
        'seeders': '',
        'leechers': '',
        'downloads': '',
        # Lower Desc
        'short_title': '',
        'short_title_url': '',
        'description': '',
        'thumbnail': '',
        'image': '',
        # Extras
        'nsfw': False,
        'risk': False
    }

    # Unlike in the repack commands we have a flag control weather to do a full parse or partial parse
    #repackers post the important information on the search results page, unlike 1337x
    def search(query, bans:list=[], max:int=10, allow_nsfw:bool=False, category:str='', filter:str='', page:int=1):
        """
        Search function for 1337x, returns wanted data
        - filter:str => "size", "time", "seeders", or "leechers" to sort by (descending)
        - category:str => Category name to search in
        - max:int => Max results
        - bans:list => An array of strings to filter out results; checked against uploader and title
        - allow_nsfw:bool => Weather or not nsfw resuls should be allowed
        """
    # Create the url
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

    # Keep looping until max is met, increasing the page count after parsing each search page
        while len(torrents) < max:
        # Fetch the html wanted
            if page == 5: break
            if not len(torrents) and (page != 1): break
            r = requests.get(f"http://1337x.to/{base}/{query}{category}{filter}/{str(page)}/",headers=ottsx_utils.headers)
            soup = BeautifulSoup(r.text, 'html.parser')
            trs = soup.select('.table-list > tbody tr')
            page+=1

        # Parse
            for i, tr in enumerate(trs):
                if len(torrents) == max: break
                skip = False
                torrent = deepcopy(ottsx_utils.torrent_format)
                for a in tr.select('a'):
                    href = "https://1337x.to" + a.get('href')
                    if href.startswith('https://1337x.to/sub/48') and (not allow_nsfw): skip = True
                    elif href.startswith('https://1337x.to/torrent'):
                        torrent['name'] = a.get_text()
                        if any(ele in torrent['name'].lower() for ele in bans): skip = True
                        torrent['url'] = href
                    elif href.startswith('https://1337x.to/user'):
                        torrent['uploaded_by'] = a.get_text()
                        if any(ele in torrent['uploaded_by'].lower() for ele in bans): skip = True
                        torrent['uploaded_by_url'] = href
                if skip: continue
                torrent['seeders'] = tr.select_one('.seeds').get_text()
                torrent['leechers'] = tr.select_one('.seeds').get_text()
                torrent['total_size'] = tr.select_one('.size').get_text().replace(torrent['seeders'], '')
                torrent['date_uploaded'] = tr.select_one('.coll-date').get_text()

                torrents.append(torrent)
            
    # Return
        while False in torrents: torrents.remove(False)
        return torrents

    def parse_page(info_page:str, targets:list=['name', 'url', 'seeders', 'magnet', 'torrent', 'total_size'], premade:dict=False, bans:list=[], allow_nsfw:bool=False):
        """
        Parse a 1337x page.
        - info_page:str => A 1337x page url
        - targets:list => A list of keys that will be returned int he result
        - premade:dict => A torrent arguement to add new data to
        - bans:list => An array of strings to filter out results; checked against uploader and title
        - allow_nsfw:bool => Weather or not nsfw resuls should be allowed

        On failure, will return False
        """
        try:
        #settup
            try:
                magR = requests.get(info_page,headers=ottsx_utils.headers)
                pirate_soup = BeautifulSoup(magR.text, 'html.parser')
            except: return False

            torrent = deepcopy(ottsx_utils.torrent_format)
            if premade: torrent = deepcopy(premade)

        # Name and url
            try:
                if 'name' in targets: torrent['name'] = pirate_soup.select_one('div.box-info-heading').get_text().strip()
                if any(ele in torrent['name'].lower() for ele in bans): return False
                if 'url' in targets: torrent['url'] = info_page
            except: return False

        # Buttons
            dl_elms = pirate_soup.select("main div div div div div ul li a")
            for dl_elm in dl_elms:
                try:
                    if dl_elm:
                        link = dl_elm.get('href')
                        if link:
                            if ('torrent' in targets) and link.endswith('.torrent'): torrent['torrent'] = [{'name': link.split('//')[-1].split('/')[0], 'link': link}]
                            elif ('magnet' in targets) and link.startswith('magnet'): torrent['magnet'] = link
                            elif ('stream' in targets) and link.startswith('https://nova'): torrent['stream'] = link
                except: pass

        # Center Table scraping (Slow)
            sl_elm = pirate_soup.select("main div div div div div ul.list li")
            for sl in sl_elm:
                if not sl: continue
                try:
                    # These items require a filter to ensure they can be added
                    section = sl.select_one('strong').get_text().strip().lower().replace(" ", "_")
                    section_value = sl.select_one('span').get_text().strip()
                    if (not section) or (not section_value): continue
                    if section == "uploaded_by":
                        if any(ele in section_value.lower() for ele in bans): return False
                        if 'uploaded_by' in targets: torrent['uploaded_by'] = section_value
                        if 'uploaded_by_url' in targets: torrent['uploaded_by_url'] = sl.select_one('a').get('href')
                        continue
                    elif section == "category":
                        if "xxx" in section_value.lower():
                            if not allow_nsfw: return False
                            if 'nsfw' in targets: torrent['nsfw'] = True
                        elif ('risk' in targets) and section_value.lower() in ['software', 'games']: torrent['risk'] = True
                        continue

                    # These I just automate, idgaf
                    if section in targets: torrent[section] = section_value.lower()
                except: continue

        # The descriptions stuff
            try:
                more = pirate_soup.select_one(".content-row")
                if more:
                    if 'short_title' in targets: torrent['short_title'] = more.select_one('h3 a').get_text() or ''
                    if 'short_title_url' in targets: torrent['short_title_url'] = "https://1337x.to" + more.select_one('h3 a').get('href') or ''
                    if 'description' in targets: torrent['description'] = more.select_one('p').get_text() or 'No Description.'
                    if 'genres' in targets:
                        for genre in more.select('span'):
                            if not genre: continue
                            torrent['genres'].append(genre.get_text())
                    if 'hash' in targets: torrent['hash'] = pirate_soup.select_one('.infohash-box span').get_text()
            except: pass

        # image
            try:
                if 'thumbnail' in targets:
                    image = pirate_soup.select_one(".torrent-image > img:nth-child(1)")
                    if image: torrent['thumbnail'] = "https:" + image.get('src') or ''
            except: pass
        
        #
            return torrent
        except: return False