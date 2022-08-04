from re import sub
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

def handle_texts(data):
    texts = data.get_text(separator="--&&--").split('--&&--')
    result = []
    for i, text in enumerate(texts):
        if text.__contains__('http'): continue
        result.append({'name': text[:-1], 'link': texts[i+1]})
    return result or [{'name': '', 'link': ''}]

class utilities:

    class darckside:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://darckrepacks.com/search/?&q={query}&type=forums_topic&quick=1&nodes=10&search_and_or=or&search_in=titles&sortby=relevancy",headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('li.ipsStreamItem')

            posts_formatted = []
            for post in posts:
                if len(posts_formatted) == limit: break
                posts_formatted.append({
                    'name': f"{post.select_one('h2.ipsStreamItem_title a').get_text().strip()}",
                    'url': f"{post.select_one('h2.ipsStreamItem_title a').get('href').split('?do=findComment')[0]}"
                })
            return posts_formatted
            
        def parse_page(info_page:str):
            print(info_page)
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(info_page,headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            
            repack = {
                'name': '',
                'repacker': f"{soup.select_one('span.ipsType_normal strong span').get_text().strip()} | Darck Repacks" or "n/a - Darck",
                'repacker_url': soup.select_one('.ipsPhotoPanel > a:nth-child(1)').get('href') or '',
                'repacker_pfp': soup.select_one('.ipsPhotoPanel > a:nth-child(1) > img:nth-child(1)').get('src') or '',
                'date': soup.select_one('span.ipsType_normal time').get_text().strip() or 'n/a',
                'url': info_page,
                'repack_size': '',
                'original_size': '',
                'genre': '',
                'publisher': '',
                'developer': '',
                'thumbnail': soup.select_one('.screenshots').findNextSiblings()[-1].select_one('img').get('src'),
                'platform': '',
                'download': [],
                'nfo': soup.select_one('.repacknfo').findNextSiblings()[-1].select_one('a').get('href')
            }

            main_data = soup.select_one('.ipsPadding_bottom > center:nth-child(1) > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(1) > td:nth-child(2)')
            for line in main_data.get_text().splitlines():
                if not line.strip(): continue
                line = line.lower().strip()
                if not repack['name']:
                    repack['name'] = line.title()
                    continue

                key, value = line.split(':')
                key = key.strip().replace(' ', '_')
                if key.endswith('s'): key = key[:-1]
                if not repack[key]: repack[key] = value.strip()
            
            hidden = soup.select_one('.ipsSpoiler_contents')
            dl_links_raw = hidden.select('a')
            for a in dl_links_raw:
                if not a.get('href'): continue
                repack['download'].append(a.get('href'))

            if not repack['download']: repack['download'].append("Signup required.")

            return repack
                
    class kaoskrew:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://kaoskrew.org/search.php?keywords={query}&terms=any&author=&fid%5B%5D=13&sc=1&sf=all&sr=posts&sk=t&sd=d&st=0&ch=300&t=0&submit=Search",headers=headers)
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
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(info_page,headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('.post')
            
            repack = {
                'repacker': f'{content.select_one("a.username-coloured:nth-child(2)").get_text()} - KaOsKrew',
                'name': content.select_one('.first > a:nth-child(1)').get_text(),
                'url': info_page,
                'date': content.select_one('.author').getText().split('» ')[-1].strip(),
                'nfo': content.select('img.postimage')[-1].get('src'),
                'ddls': []
            }

            for a in content.select('.content a.postlink'):
                if not a.get_text(): continue
                if a.get_text() == 'Here': continue
                if not a.get('href'): continue
                repack['ddls'].append({'name': a.get_text(), 'link': a.get('href')})

            return repack

    class scooter:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://scooter-repacks.site/?s={query}",headers=headers)
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
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(info_page,headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('article')

            repack = {
                'repacker': 'Scooter',
                'name': content.select_one('.title').get_text() or 'Error',
                'date':  soup.select_one('time').get_text() or 'n/a',
                'summary': 'n/a',
                'nfo': content.select('figure img')[-1].get('data-src') or '',
                'size': 'n/a',
                'system': '',
                'url': info_page,
                'ddl': '',
                'torrents': [],
                'thumbnail': content.select('figure img')[0].get('data-src') or ''
            }
            try: repack['size'] = repack['name'].split('|')[-1].strip()
            except: pass

            spoiler = content.select('div.wp-block-inline-spoilers-block > div:nth-child(1) > div:nth-child(2)')
            if spoiler:
                for i, section in enumerate(spoiler):
                    if not section: continue
                    try:
                        if i == 0: repack['system'] = sub(r'<div[^>]*>', '', str(section)).replace('/', '').replace('<br>', '\n').replace('<strong>', '**').replace('\n\n', '\n')[:-5]
                        elif i == 1: repack['summary'] = sub(r'<div[^>]*>', '', str(section)).replace('/', '').replace('<br>', '\n').replace('<strong>', '**').replace('\n\n', '\n')[:-5]
                        elif i == 2: repack['ddl'] = section.select_one('a').get('href') or ''
                        elif i == 3: repack['torrents'] = handle_texts(section)
                        else: break
                    except: pass
            return repack

    class fitgirl:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://fitgirl-repacks.site/?s={query}",headers=headers)
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
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(info_page,headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('.entry-content')

            repack = {
                'repacker': 'FitGirl',
                'mirrors': [],
                'name': soup.select_one('.entry-title').get_text(),
                'date':  soup.select_one('a time').get_text(),
                'summary': 'n/a',
                'genres': 'n/a',
                'company': 'n/a',
                'languages': 'n/a',
                'original_size': 'n/a',
                'repack_size': 'n/a',
                'url': info_page,
                'magnet': 'n/a',
                'torrent': 'n/a',
                'thumbnail': content.select_one('p a img').get('src') or ''
            }

            mirrors_section = content.select('li a')
            for mirror in mirrors_section:
                link = mirror.get('href')
                text = mirror.get_text() or ''
                if (not link) or (not text): continue
                if link.startswith('magnet'):
                    repack['magnet'] = link
                    continue
                if text.startswith('.torrent'):
                    repack['torrent'] = link
                    continue
                repack['mirrors'].append({'name': text, 'link': link})

            try: repack['spoiler'] = content.select_one('.su-spoiler-content').get_text()
            except: pass

            top_info = content.select_one('p').get_text()
            for line in top_info.splitlines():
                #if repack['repack_size']: break
                if line.__contains__('Genres/Tags:'): repack['genres'] = line.split(': ')[-1]
                elif line.__contains__('Company:'): repack['company'] = line.split(': ')[-1]
                elif line.__contains__('Languages:'): repack['languages'] = line.split(': ')[-1]
                elif line.__contains__('Original Size:'): repack['original_size'] = line.split(': ')[-1]
                elif line.__contains__('Repack Size:'): repack['repack_size'] = line.split(': ')[-1]
            return repack


