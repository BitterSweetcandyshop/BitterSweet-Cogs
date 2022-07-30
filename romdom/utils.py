from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession

class utilities:

    class vimm:
        def search(query:str, limit:int=10):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(f"https://vimm.net/vault/?p=list&q={query}",headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            roms_raw = soup.select('div.mainContent tr') # the first result is always empty

            roms = []

            for rom_raw in roms_raw:
                if len(roms) == limit: break
                if rom_raw.select_one('span.redBorder'): continue
                rom = {
                    'name': '',
                    'system': '',
                    'url': '',
                    'regions': [],
                    'flags': [],
                    'version': '',
                    'tags': [],
                    'languages': ''
                }
                for td in rom_raw.select('td'):
                    flags = td.select('img.flag')
                    link = td.select_one('a')
                    if flags:
                        for flag in flags:
                            flag_link = "https://vimm.net" + flag.get('src')
                            if not flag_link: continue
                            rom['flags'].append(flag_link)
                            rom['regions'].append(flag.get('title'))
                        continue
                    if link:
                        rom['name'] = link.get_text()
                        rom['url'] = "https://vimm.net" + link.get('href')
                        continue
                    if not rom['system']: rom['system'] = td.get_text()
                    if not rom['version']: rom['version'] = td.get_text()
                    if not rom['languages']: rom['languages'] = td.get_text()

                if not rom['name']: continue
                roms.append(rom)

            return roms


        def parse_page(info_page:str):
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Arch Linux; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'}
            r = FuturesSession().get(info_page,headers=headers)
            soup = BeautifulSoup(r.result().text, 'html.parser')
            content = soup.select_one('.innerMain > div:nth-child(1)')

            rom = {
                'name': content.select_one('span:nth-child(3)').get_text(),
                'name_full': '',
                'url': info_page,
                'system': content.select_one('span.sectionTitle').get_text(),
                'size': content.select_one('[id="download_size"]').get_text(),
                'flags': [],
                'regions': []
            }

            valid = ['Players', 'Year', 'Serial #', 'Graphics', 'Sound', 'Gameplay', 'Overall', 'CRC', 'MD5', 'SHA1', 'Verified', 'Disc #', 'Version']
            for e in valid: rom[e.lower()] = 'n/a'

            for tr in content.select('tr'):
                try:
                    section = tr.select_one('td').get_text().strip()
                    if not section: continue
                except: continue
                if valid.count(section):
                    try: value = tr.get_text().replace(section, '').replace('⚠More...', '').strip()
                    except: value = ''
                    if rom[section.lower()] == 'n/a': rom[section.lower()] = value
                else:
                    if section == 'Region': 
                        for flag in tr.select('img.flag'):
                            rom['regions'].append(flag.get('title'))
                            rom['flags'].append('https://vimm.net' + flag.get('src'))
                        continue
                    if tr.select_one("[id='data-good-title']"): rom['name_full'] = section
            if rom.get('overall'): rom['overall'] = rom['overall'].replace('\xa0', ' ').replace('Rate it!', '').strip()

            return rom
