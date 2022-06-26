from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class uTils:
    def search(self, keyword, **kwargs):
        """
        Return a list of dicts with the results of the query.
        """
        category = kwargs.get('category', 0)
        filters = kwargs.get('filters', 0)
        page = kwargs.get('page', 0)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}

        r = FuturesSession().get(
            f"http://1337x.to/search/{keyword}/1/",
            headers=headers)

        soup = BeautifulSoup(r.result().text, 'html.parser')
        rows = soup.select('table tr')

        torrents = []
        for row in rows[:11]:
            block = []

            for td in row.find_all('td'):
                if td.find_all('a'):
                    for link in td.find_all('a'):
                        if link.get('href')[-9:] != '#comments':
                            block.append(link.get('href'))
                            if link.text.rstrip():
                                block.append(link.text)
                else:
                    block.append(td.text)
            
            if not len(block): continue

            try:


                magR = FuturesSession().get(
                    f"https://1337x.to{block[1]}",
                    headers=headers)
                magneticSoup = BeautifulSoup(magR.result().text, 'html.parser')
                search = magneticSoup.select("main div div ul li a")
                for elm in search:
                    link = elm.get('href')
                    if not link: continue
                    if len(link) < 10: continue
                    if elm.get('href')[:6] == "magnet":
                        block.append(elm.get('href'))
                        break


                #print(magnet)

                torrents.append({
                    'quality': block[0],
                    'url': f"https://1337x.to{block[1]}",
                    'name': block[2],
                    'seeders': block[3],
                    'leechers': block[4],
                    'date': block[5],
                    'size': block[6].replace(block[3], ""),
                    'authorLink': f"https://1337x.to{block[7]}",
                    'author': block[8],
                    'magnet': block[9]
                })
            except:
                continue
            
        return torrents
            




    