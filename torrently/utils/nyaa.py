import re
import requests
from copy import deepcopy
from bs4 import BeautifulSoup

class nyaa_utils:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}

    torrent_format = {
        # Main
        'source': 'Nyaa',
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

    def search(query, limit:int=10, bans:list=[], **kwargs):
        """Search nyaa by scraping the restuls
         Return a list of dicts with the results of the query.
        """

    # Kwargs
        category = kwargs.get('category', 0)
        subcategory = kwargs.get('subcategory', 0)
        filters = kwargs.get('filters', 0)
        page = kwargs.get('page', 0)
        sort = kwargs.get('sort', 'seeders')
        if sort: sort = "&o=desc&s=" + sort
        
    # Settup
        torrents = []
        r = requests.get(f"http://nyaa.si/?f={filters}&c={category}_{subcategory}&q={query}{sort}", headers=nyaa_utils.headers)
        pirate_soup = BeautifulSoup(r.text, 'html.parser')

    # Sort
        for tr in pirate_soup.select('tr'):
            torrent = deepcopy(nyaa_utils.torrent_format)
            try:
                if len(torrents) == limit: break
                tds = tr.select('td')
                for td in tds:
                    for a in td.select('a'):
                        try:
                            try: link = a.get('href')
                            except: continue
                            if link.startswith('/?c'):
                                torrent['category'] = a.get('title')
                                torrent['thumbnail'] = "https://nyaa.si" + a.select_one('img').get('src')
                            elif link.startswith('/view') and (not link.endswith('comments')):
                                torrent['name'] = a.get_text()
                                if torrent['name'].startswith('['): torrent['uploaded_by'] = torrent['name'].split("]")[0][1:]
                                if any(ele in torrent['name'].lower() for ele in bans): continue
                                torrent['url'] = "https://nyaa.si" + link
                            elif link.startswith('/download') and not torrent['torrent']: torrent['torrent'].append({'name': 'Torrent', 'link': "https://nyaa.si" + link})
                            elif link.startswith('magnet'): torrent['magnet'] = link
                            else: continue
                        except: pass
                torrent['downloads'] = tds[-1].get_text().strip()
                torrent['leechers'] = tds[-2].get_text().strip()
                torrent['seeders'] = tds[-3].get_text().strip()
                torrent['date_uploaded'] = tds[-4].get_text().strip()
                torrent['total_size'] = tds[-5].get_text().strip()
                torrents.append(torrent)
            except: pass

    #
        while False in torrents: torrents.remove(False)
        return torrents

    def parse_page(info_page:str, targets:list=torrent_format.keys(), premade:dict=False, bans:list=[], allow_nsfw:bool=False):
        try:
        # Settup
            unify = {
                'submitter': 'uploaded_by',
                'file_size': 'total_size',
                'info_hash': 'hash',
                'date': 'date_uploaded'
            }

            r = requests.get(info_page, headers=nyaa_utils.headers)
            pirate_soup = BeautifulSoup(r.text, 'html.parser')
            torrent = deepcopy(nyaa_utils.torrent_format)
            if premade: torrent = premade
            
            if 'name' in targets: torrent['name'] = pirate_soup.select_one('h3.panel-title').get_text()
            if 'url' in targets: torrent['url'] = info_page

        # Main section
            for row in pirate_soup.select('div.panel-body div.row'):
                for i, child in enumerate(row.select('div.col-md-1')):
                    try:
                        section = child.get_text()[:-1].lower().replace(' ', '_')
                        if unify.get(section): section = unify[section]
                        section_value = row.select('div.col-md-5')[i]
                        if section == 'uploaded_by':
                            if 'uploaded_by' in targets: torrent['uploaded_by'] = section_value.get_text().strip()
                            if any(ele in torrent['uploaded_by'].lower() for ele in bans): return False
                            if 'uploaded_by_url' in targets: torrent['uploaded_by_url'] = "https://nyaa.si" + section_value.select_one('a').get('href')
                            continue
                        elif section == 'category':
                            if 'category' in targets: torrent['category'] = section_value.get_text().strip()
                            if 'thumbnail' in targets: torrent['thumbnail'] = "https://nyaa.si/static/img/icons/nyaa/" + section_value.select('a')[-1].get('href')[4:] + ".png"
                        elif section in targets: torrent[section] = section_value.get_text().strip()
                    except: pass

        # Magnet and Torrent
            if ('torrent' in targets) or ('magnet' in targets):
                for a in pirate_soup.select('div.panel-footer a'):
                    link = a.get('href')
                    if link.startswith('/download') and ('torrent' in targets) and (not torrent['torrent']): torrent['torrent'].append({'name': 'Torrent', 'link': "https://nyaa.si" + link})
                    elif link.startswith('magnet') and ('magnet' in targets): torrent['magnet'] = link
                    
        # Description
            if ('description' in targets) or ('image' in targets) or ('ddl' in targets):
                description = str(pirate_soup.select_one('[id="torrent-description"]')).split('markdown-text="">')[-1][:-6].replace('---', '')
                if 'description' in targets: torrent['description'] = description
                # Images removal
                img_matches = re.search(r'\!\[[^]]+]\([^)]+\)', description, re.MULTILINE | re.IGNORECASE)
                if img_matches:
                    match = img_matches.group(0)
                    if 'image' in targets: torrent['image'] = match.split('](')[-1].split(' ')[0].strip()

                # Mega Matching
                mega_matches = re.finditer(r'https://mega\.nz/(?:(?:folder|file)/(?:\w+)#(?:\w+)|#(?:F?)!(?:[^!]+)!\w+)', description, re.MULTILINE | re.IGNORECASE)
                if (mega_matches):
                    for i, match in enumerate(mega_matches):
                        match = match.group()
                        if 'ddl' in targets: torrent['ddl'].append({'name': f'Mega {i+1}', 'link': match})
                    
                # Cleanup time
                if torrent['description']:
                    torrent['description'] = re.sub(r'\!\[[^]]+]\([^)]+\)', '', torrent['description'])
                    while '\n\n\n' in torrent['description']: torrent['description'] = torrent['description'].replace('\n\n\n', '\n\n').strip()

        #
            return torrent
        except: return False