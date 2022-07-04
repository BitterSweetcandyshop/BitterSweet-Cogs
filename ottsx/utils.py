from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class uTils:
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}

    def search(self, keyword, bans:list=[], ignore_bans:bool=False, **kwargs):
        """
        Return a list of dicts with the results of the query.
        """

        speed = kwargs.get('speed', False)
        max = kwargs.get('max', 9)

        r = FuturesSession().get(
            f"http://1337x.to/search/{keyword}/1/",
            headers=self.headers)

        soup = BeautifulSoup(r.result().text, 'html.parser')
        allas = soup.select('table tr a')

        torrents = []
        for i, a in enumerate(allas):
            if len(torrents) > max: break
            #print(a)
            main_link = a.get('href')
            if not main_link: continue
            if not main_link.startswith('/torrent/'): continue
            if not ignore_bans:
                if any(ele in main_link.lower() for ele in bans): continue
                bans=[]

            torrent = False
            if speed:
                torrent = self.speedy_search(f"https://1337x.to{main_link}", bans=bans, ignore_bans=ignore_bans)
            else:
                torrent = self.single_parse(f"https://1337x.to{main_link}", bans=bans, ignore_bans=ignore_bans)
            if not torrent: continue
            torrents.append(torrent)
            
        return torrents
    
    def speedy_search(self, main_link:str, bans:list=[], ignore_bans:bool=False):
        if ignore_bans: bans=[]
        try:
            magR = FuturesSession().get(
                    main_link,
                    headers=self.headers)
            pirate_soup = BeautifulSoup(magR.result().text, 'html.parser')

            dl_elms = pirate_soup.select("main div div div div div ul li a")
            magnet = ''
            torrent = ''
            for dl_elm in dl_elms:
                if torrent and magnet: break
                if dl_elm:
                    link = dl_elm.get('href')
                    if link:
                        if link.startswith('magnet'):
                            magnet = link
                        if link.endswith('.torrent'):
                            torrent = link

            sl_elm = pirate_soup.select("main div div div div div ul li")
            seeders = ''
            leechers = ''
            size = ''
            uploader = ''
            for sl in sl_elm:
                if seeders and leechers and size: break
                parsed_sl = sl.get_text()
                if not parsed_sl: continue
                if not (parsed_sl.startswith(" Seeders") or parsed_sl.startswith(" Leechers") or parsed_sl.startswith(" Uploaded By  ") or parsed_sl.startswith(" Total size")): continue
                if parsed_sl.startswith(" Seeders"):
                    seeders = parsed_sl.split(" ")[-2]
                elif parsed_sl.startswith(" Leechers"):
                    leechers = parsed_sl.split(" ")[-2]
                elif parsed_sl.startswith(" Total size"):
                    size = parsed_sl.split(" ")[-3] + " " + parsed_sl.split(" ")[-2]
                elif parsed_sl.startswith(" Uploaded By  "):
                    parsed_sl.split(" ")[-2]

            if any(ele in uploader.lower() for ele in bans): return False

            torrent = {
                    'magnet': magnet,
                    'torrent': torrent,
                    'url': main_link,
                    'name': main_link[:-1].split("/")[-1],
                    'size': size,
                    'seeders': seeders,
                    'leechers': leechers,
                    'uploader': uploader
            }
            print(torrent)
            return torrent
        except:
            return False

    def single_parse(self, main_link:str, bans:list=[], ignore_bans:bool=False):
        if ignore_bans: bans=[]
        try:
            block = []
            stream = ''
            magR = FuturesSession().get(
                main_link,
                headers=self.headers)
            magnet_soup = BeautifulSoup(magR.result().text, 'html.parser')

            # Main details
            data_page = magnet_soup.select('main div div div div div ul')
            for i, ul in enumerate(data_page):
                if i == 0:
                    links = ul.find_all('a')
                    for link in links:
                        href = link.get('href')
                        if not href: continue
                        if href.startswith("https://novastream"):
                            stream = href
                            continue
                        block.append(href)
                else:
                    spans = ul.find_all('span')
                    for span in spans:
                        if not span.text: continue
                        block.append(span.text)

            if any(ele in block[11].lower() for ele in bans):
                return False

            # Image
            img = magnet_soup.select("main div div div div div div div img")
            image = ""
            for im in img:
                img_link = im.get('src')
                if not img_link: continue
                if not img_link.startswith("//lx1.dyncdn.cc/cdn"): continue
                image = "https:" + img_link

            # Other
            extras = magnet_soup.select('main div div div div div div div')
            extra_block = {
                'name': '',
                'more': '',
                'desc': 'No Description.',
                'genres': []
            }
            title = magnet_soup.select_one('main div div div div div div div h3 a')
            if title:
                if title.text:
                    extra_block['name'] = title.text
                    if title.get("href"):
                        extra_block['more'] = title.get("href")

            desc = magnet_soup.select_one('main div div div div div div div p')
            if desc:
                if desc.text:
                    if len(desc.text) < 2000:
                        extra_block['desc'] = desc.text

            genres = magnet_soup.select('main div div div div div div div div span')
            for genre in genres:
                if genre.text:
                    if len(genre.text):
                        extra_block['genres'].append(genre.text)

            print(extra_block)
            print("\n\n")

            if not len(block): return False
            torrent = {
                'magnet': block[0] or '',
                'torrent': block[2] or '',
                'torrage': block[3] or '',
                'btcache': block[4] or '',
                'stream': stream,
                'url': main_link,
                'name': main_link[:-1].split("/")[-1],
                'category': block[7]  or '',
                'type': block[8]  or '',
                'language': block[9]  or '',
                'thumbnail': image,
                'size': block[10]  or '',
                'uploader': block[11]  or '',
                'uploaderUrl': f"https://1337x.to/user/{block[11].replace(' ', '')}"  or '',
                'downloads': block[12]  or '',
                'lastCheck': block[13]  or '',
                'date': block[14]  or '',
                'seeders': block[15]  or '',
                'leechers': block[16]  or '',
                'description': extra_block['desc'].replace("â", "'").replace("â¦", " &").replace("â", '"').replace("â", '"'),
                'more': f"https://1337x.to{extra_block['more']}",
                'shortName': extra_block['name'],
                'genres': extra_block['genres']
            }
            return torrent
        except:
            return False