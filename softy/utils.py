from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class utilities:

    class monkrus:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://w14.monkrus.ws/search?q={query}",headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('div.post-outer', limit=limit)

            posts_formatted = []
            for post in posts:
                date_name = post.select_one('.post-header')
                if not date_name: continue
                posts_formatted.append({
                    'site': 'monkrus',
                    'name': post.select_one('h2.post-title a').get_text(),
                    'url': post.select_one('h2.post-title a').get('href'),
                    'date': date_name.get_text(separator='BOOBS').split('BOOBS')[-1].strip(),
                    'releaser': date_name.select_one('b').get_text().replace('by', '').strip(),
                    'thumbnail': post.select_one('div.post-indent img').get('src')
                })
            return posts_formatted

        def parse_page(software_data):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(software_data['url'],headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')

            software = {
                'site': 'monkrus',
                'name': software_data['name'],
                'url': software_data['url'],
                'date': software_data['date'],
                'releaser': software_data['releaser'],
                'thumbnail': software_data['thumbnail'],
                'downlaod': []
            }

            downloads = soup.select_one('.post-indent > div:nth-child(1)').findNextSiblings()
            for i, sibling in enumerate(downloads):
                sibling_text = sibling.get_text()
                if not sibling_text: continue
                if sibling_text.startswith('http'):
                    software['downlaod'].append({'name': downloads[i-1].get_text().strip().title()[:-1], 'link': sibling_text})

            return software

    class filecr:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://filecr.com/?s={query}",headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            posts = soup.select('div.product-list div.product', limit=limit)

            posts_formatted = []
            for post in posts:
                posts_formatted.append({
                    'site': 'filecr',
                    'name': post.select_one('a.product-title').get_text().strip(),
                    'url': post.select_one('a.product-title').get('href').strip(),
                    'description': post.select_one('p.product-desc').get_text().strip(),
                    'platform': post.select_one('div.category span.text').get_text().strip(),
                    'size': post.select_one('div.product-size').get_text().strip()
                })

            return posts_formatted

        def parse_page(info_page:str):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(info_page,headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            hidden_data = soup.select_one('aside.sidebar [id="post-data"]')

            software = {
                'site': 'filecr',
                'name': hidden_data.get('data-title') or '',
                'url': info_page,
                'description': hidden_data.get('data-description') or '',
                'version': hidden_data.get('data-version') or '',
                'date': hidden_data.get('data-release-date') or '',
                'platform': hidden_data.get('data-primary-category') or '',
                'thumbnail': hidden_data.get('data-icon-url') or '',
                'size': soup.select_one('.download-size').get_text().strip()
            }

            return software