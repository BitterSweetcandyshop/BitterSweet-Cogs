from re import sub
from copy import deepcopy
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

def handle_texts(data):
    texts = data.get_text(separator="--&&--").split('--&&--')
    result = []
    for i, text in enumerate(texts):
        if text.__contains__('http'): continue
        result.append({'name': text[:-1], 'link': texts[i+1]})
    return result or []

class utilities():
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
    repack_format = {
        #Name title stuff
        'name': '',
        'name_full': '',
        'date': '',
        'url': '',
        #Repacker
        'repacker': '',
        'repacker_url': '',
        'repacker_pfp': '',
        #Details
        'repack_size': '',
        'original_size': '',
        'genre': '',
        'languages': '',
        'publisher': '',
        'developer': '',
        'thumbnail': '',
        'system_requirements': '',
        'nfo': '',
        #Install
        'download': [],
        'mirror': [],
        'magnet': '',
        'torrent': [],
    }

    class darckside:
        def search(query:str, limit:int=10):
            
            r = FuturesSession().get(f"https://darckrepacks.com/search/?&q={query}&type=forums_topic&quick=1&nodes=10&search_and_or=or&search_in=titles&sortby=relevancy",headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('li.ipsStreamItem')

            posts_formatted = []
            for post in posts:
                if len(posts_formatted) == limit: break
                posts_formatted.append({
                    'repacker': 'Darck Repacks',
                    'name': f"{post.select_one('h2.ipsStreamItem_title a').get_text().strip()}",
                    'url': f"{post.select_one('h2.ipsStreamItem_title a').get('href').split('?do=findComment')[0]}"
                })
            return posts_formatted
            
        def parse_page(info_page:str):
            
            r = FuturesSession().get(info_page,headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            
            repack = deepcopy(utilities.repack_format)

            #Url
            repack['url'] = info_page
            #Date
            repack['date'] = soup.select_one('span.ipsType_normal time').get_text().strip()
            # Repacker that posted
            try:
                repack['repacker'] = f"{soup.select_one('span.ipsType_normal strong span').get_text().strip()} | Darck Repacks" or "n/a - Darck"
                repack['repacker_url'] = soup.select_one('span.ipsType_normal strong a').get('href')
                repack['repacker_pfp'] = soup.select_one('a.ipsUserPhoto_mini img').get('src')
            except: pass
            #Thumbnail
            try: repack['thumbnail'] = soup.select_one('img[data-ratio="36.87"]').get('src')
            except: pass
            #NFO 
            try: repack['nfo'] = repack['nfo'] = soup.select_one('.repacknfo').findNextSibling('p').select_one('a').get('href')
            except: pass
            #Data box
            try:
                main_data = soup.select_one('.ipsPadding_bottom > center:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)')
                for line in main_data.get_text().splitlines():
                    if not line.strip(): continue
                    line = line.lower().strip()
                    if not repack['name']:
                        repack['name'] = line.title().replace('\'S', '\'s')
                        continue

                    key, value = line.split(':')
                    key = key.strip().replace(' ', '_')
                    if key.endswith('s'): key = key[:-1]
                    if not repack[key]: repack[key] = value.strip().title()
            except:
                try: repack['name'] = soup.select_one('span.ipsType_break > span:nth-child(1)').get_text().strip()
                except: pass
            #Downloads
            try:
                hidden = soup.select_one('.ipsSpoiler_contents')
                dl_links_raw = hidden.select('a')
                for a in dl_links_raw:
                    link = a.get('href')
                    if not link: continue
                    name = link.split('//')[1].split('/')[0]
                    repack['download'].append({'name': name, 'link': a.get('href')})
            except: pass

            if (not repack['download']) and (not repack['nfo']):  repack['download'].append('This seems to be an older post, please visit the page for information.')
            if not repack['download']: repack['download'].append("Signup required.")

            return repack
                
    class kaoskrew:
        def search(query:str, limit:int=10):
            
            r = FuturesSession().get(f"https://kaoskrew.org/search.php?keywords={query}&terms=any&author=&fid%5B%5D=13&sc=1&sf=all&sr=posts&sk=t&sd=d&st=0&ch=300&t=0&submit=Search",headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('.search.post')

            posts_formatted = []
            for post in posts:
                if len(posts_formatted) == limit: break
                if post.select_one('h3 a').get_text().__contains__('Re: '): continue
                posts_formatted.append({
                    'repacker': f"{post.select_one('.author').get_text().replace('by ', '')} - KaOsKrew",
                    'name': post.select_one('h3 a').get_text(),
                    'url': post.select_one('h3 a').get('href').replace('./', 'https://kaoskrew.org/'),
                    'date': post.select_one('.search-result-date').get_text()
                })
            return posts_formatted

        def parse_page(info_page:str):
            print(info_page)
            repack = deepcopy(utilities.repack_format)
            
            r = FuturesSession().get(info_page,headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('.page-body')
            
            repack['repacker'] = f'{content.select_one("a.username-coloured").get_text()} | KaOsKrew'
            repack['repacker_url'] = 'https://kaoskrew.org/' + content.select_one("a.username-coloured").get('href')[1:]
            repack['repacker_pfp'] = content.select_one('img.avatar').get('src')
            repack['name_full'] = content.select_one('h2.topic-title').get_text()
            repack['url'] = info_page
            repack['date'] = content.select_one('p.author time').getText().split('» ')[-1].strip()
            repack['nfo'] = content.select('img.postimage')[-1].get('src')
            repack['download'] = []
            
            # From respect of gangster who runs KaOsKrew's site, I have removed
            #showing download links in the embed
            #for a in content.select('.content a.postlink'):
            #    try:
            #        if not a.get_text(): continue
            #        if a.get_text() == 'Here': continue
            #        if not a.get('href'): continue
            #        repack['download'].append({'name': a.get_text(), 'link': a.get('href')})
            #    except: pass

            for a in content.select('.content a.postlink'):
                try:
                    if not a.get_text(): continue
                    if a.get_text() == 'Here': continue
                    if not a.get('href'): continue
                    repack['download'].append({'name': a.get_text(), 'link': a.get('href')})
                except: pass

            return repack

    class scooter:
        def search(query:str, limit:int=10):
            
            r = FuturesSession().get(f"https://scooter-repacks.site/?s={query}",headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('article', limit=limit)

            posts_formatted = []
            for post in posts:
                posts_formatted.append({
                    'repacker': 'Scooter',
                    'name': post.select_one('header h1 a').get_text(),
                    'url': post.select_one('header h1 a').get('href'),
                    'size': post.select_one('header h1 a').get_text().split('|')[-1],
                    'date': post.select_one('time').get_text()
                })
            return posts_formatted

        def parse_page(info_page:str):
            repack = deepcopy(utilities.repack_format)
            
            r = FuturesSession().get(info_page,headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('article')

            repack['repacker'] = 'Scooter'
            repack['name_full'] = content.select_one('.title').get_text() or 'Error'
            repack['date'] =  soup.select_one('time').get_text() or 'n/a'
            repack['nfo'] = content.select('figure img')[-1].get('data-src') or ''
            repack['url'] = info_page
            repack['thumbnail'] = content.select('figure img')[0].get('data-src') or ''
            try: repack['repack_size'] = repack['name'].split('|')[-1].strip()
            except: pass

            spoiler = content.select('div.wp-block-inline-spoilers-block div.spoiler-head')
            if spoiler:
                for section in spoiler:
                    # We just don't look at this, all you need to know it works oddly well
                    try:
                        header = section.get_text().lower().strip()
                        keybase = {'torrent': 'torrent', 'system requirements': 'system_requirements', 'about this game': 'summary', 'download links': 'download'}
                        for other_download in ['google drive', 'letsupload', 'megaup', 'pixeldrain']: keybase[other_download] = "download"
                        hidden_sibling = section.findNextSibling('div')
                        if keybase[header] == 'torrent': repack['torrent'] = handle_texts(hidden_sibling)
                        elif keybase[header] == 'download':
                            link = hidden_sibling.select_one('a').get('href')
                            repack['download'].append({'name': link.split('//')[1].split('/')[0], 'link': link})
                        else: repack[keybase[header]] = sub(r'<div[^>]*>', '', str(hidden_sibling)).replace('/', '').replace('<br>', '\n').replace('<strong>', '**').replace('\n\n', '\n')[12:-5].strip()
                    except: pass # fuckit, I don't really need if statments when failure is an option lmao
            return repack

    class fitgirl:
        def search(query:str, limit:int=10):
            
            r = FuturesSession().get(f"https://fitgirl-repacks.site/?s={query}",headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('article', limit=limit)

            posts_formatted = []
            for post in posts:
                posts_formatted.append({
                    'repacker': 'FitGirl',
                    'name': post.select_one('h1 a').get_text(),
                    'url': post.select_one('h1 a').get('href'),
                    'summary':  post.select_one('p').get_text(),
                    'date':  post.select_one('time').get_text()
                })
            return posts_formatted

        def parse_page(info_page:str):
            repack = deepcopy(utilities.repack_format)

            r = FuturesSession().get(info_page,headers=utilities.headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('.entry-content')

            repack['repacker'] = 'FitGirl'
            repack['repacker_url'] = 'https://fitgirl-repacks.site/'
            repack['repacker_pfp'] = "https://fitgirl-repacks.site/wp-content/uploads/2020/08/icon_fg-1.jpg"
            repack['name'] = soup.select_one('.entry-title').get_text().strip()
            repack['date'] =  soup.select_one('a time').get_text().strip()
            repack['url'] = info_page
            #Thumbnail
            try: repack['thumbnail'] = content.select_one('p a img').get('src')
            except: pass
            #Adding links to install
            mirrors_section = content.select('li a')
            for mirror in mirrors_section:
                try:
                    if not mirror: continue
                    link = mirror.get('href')
                    text = mirror.get_text().strip() or ''
                    if (not link) or (not text): continue
                    if link.startswith('magnet') and (not repack['magnet']): repack['magnet'] = link
                    elif text.__contains__('.torrent') and (not repack['torrent']): repack['torrent'].append({'name': 'Torrent', 'link': link})
                    elif text != 'magnet': repack['mirror'].append({'name': text, 'link': link})
                except: pass
            # Faux nfo, just torrent/magnet status, doesn't actually work but nice to include if it ever does
            try:
                torrent_stats = content.select_one('li img').get('src')
                repack["nfo"] = torrent_stats
            except: pass
            #Summary
            try: repack['summary'] = content.select_one('.su-spoiler-content').get_text().strip()
            except: pass
            #Other data
            try:
                top_info = content.select_one('p').get_text()
                for line in top_info.splitlines():
                    try:
                        if line.__contains__('Genres/Tags:'): repack['genres'] = line.split(': ')[-1]
                        elif line.__contains__('Company:') or line.__contains__('Companies:'): repack['company'] = line.split(': ')[-1]
                        elif line.__contains__('Languages:'): repack['languages'] = line.split(': ')[-1]
                        elif line.__contains__('Original Size:'): repack['original_size'] = line.split(': ')[-1]
                        elif line.__contains__('Repack Size:'): repack['repack_size'] = line.split(': ')[-1]
                    except: pass
            except: pass
            return repack


