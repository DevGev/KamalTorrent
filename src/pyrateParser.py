from decimal import Decimal
import urllib.request
import requests
from bs4 import BeautifulSoup, SoupStrainer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, \
    QPushButton

d = {
        'T': 12,
        'G': 9,
        'M': 6,
        'K': 3
}
def text_to_num(text):
        text = text.replace("B", "")
        if text[-1] in d:
            num, magnitude = text[:-1], text[-1]
            return float(Decimal(num) * 10 ** d[magnitude])
        else:
            return float(Decimal(text))

class Parse(QThread):
    listChanged = pyqtSignal(list, list, list, list, list)

    def __init__(self, _query, _provider, _category, _sizelimit, _seedmin):
        QThread.__init__(self)
        self.query = _query
        self.provider = _provider
        self.category = _category
        self.sizelimit = _sizelimit
        self.seedmin = _seedmin

    def run(self):
        print(self.provider, self.query, self.category, self.sizelimit, self.seedmin)
        urls = [
            'https://thepiratebay0.org',
            'https://pirateproxy.live',
            'https://thehiddenbay.com',
            'https://piratebay.live',
            'https://thepiratebay.zone',
            'https://tpb.party',
            'https://piratebayproxy.live',
            'https://thepiratebay1.com',
            ]

        try:
            url = urls[int(self.query[self.query.find('url[')
                       + len('url['):self.query.rfind(']')])]
            self.query = self.query[6:]
        except:
            url = 'https://thepiratebay0.org'
        self.query = self.query.replace(' ', '%20')
        mid = "/search/"

        
        xcats = {"All":"0/", "Music":"Music/0/", "Movies":"Movies/0/", "TV Shows":"TV/0/", "PC Games":"Games/0/", "UNIX Apps":"Apps/0/", "Windows Apps": "Apps/0/"}

        if self.provider == "1337X":
            url = "https://1337x.to"
            if self.category == "All":
                endurl = "0/"
            else:
                mid = "/category-search/"
                for x in range(0, len(list(xcats.keys()))):
                    if list(xcats.keys())[x] == self.category:
                        endurl = list(xcats.values())[x]

        if self.provider == "skytorrents":
            mid = "/?search="
            url = "https://www.skytorrents.to"
            endurl = ""

        piratebaycats = {"All":"1/99/0", "Music":"1/99/101", "Movies":"1/99/201", "TV Shows":"1/99/205", "PC Games":"1/99/401", "UNIX Apps":"1/99/303", "Windows Apps":"1/99/301"}
        if self.provider == "Pirate Bay":
            for x in range(0, len(list(piratebaycats.keys()))):
                if list(piratebaycats.keys())[x] == self.category:
                    endurl = list(piratebaycats.values())[x]

        if self.provider == "eztv":
            url = "https://eztv.io"
            endurl = ""

        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        resp = requests.get(url + mid + self.query + "/" + endurl,
                            headers=hdr).text
        print(url + mid + self.query + "/" + endurl)
        soup = BeautifulSoup(resp, features='lxml')
        self.magnets = []
        self.titles = []
        self.seeders = []
        self.leechers = []
        self.desc = []
        if self.provider == 'Pirate Bay':
            for link in soup.find_all('a', href=True):
                if (link['href'])[:7] == 'magnet:':
                    self.magnets.append(link['href'])
                if (link['href'])[:8] == '/torrent':
                    parts = link['href'].split('/')
                    self.titles.append(parts[3])
                if link['href'].replace(url, '')[:8] == '/torrent':
                    parts = link['href'].replace(url, '').split('/')
                    self.titles.append(parts[3])

        if self.provider == "eztv":
            sizes =  []
            for link in soup.find_all('a', class_="epinfo"):
                title = link['title'].split("(")[0]
                size = link['title'].split("(")[1].replace(")", "").replace("(","")
                sizes.append(str(size))
                self.titles.append(str(title).replace(" ", "_"))
            for link in soup.find_all('a', class_="magnet"):
                self.magnets.append(str(link['href']))
            i = 0
            update = []
            for upd in soup.find_all('td', {'class':["forum_thread_post"], 'align':["center"]}):
                if len(upd.contents) == 1 and i != 3:
                    i += 1
                    if i == 2:
                        update.append(str(upd.contents[0]))
                else:
                    i = 0
            for seeds in soup.find_all('td', {'class':["forum_thread_post_end"]}):
                if seeds.contents[0] != "-":
                    self.seeders.append(str(seeds.contents[0]).replace(">", "<").split("<")[2])
                else:
                    self.seeders.append("0")
                self.leechers.append("-")
            for x in range(0, len(sizes)):
                self.desc.append("Size: " + sizes[x] + " Uploaded " + update[x] + " ago")
        
        if self.provider == 'skytorrents':
            for name in soup.find_all('tr', class_="result"):
                n = name.find('a', href=True)
                self.titles.append(n.get_text().replace(" ", "_"))
            for link in soup.find_all('a', href=True):
                if link['href'][:7] == "magnet:":
                    self.magnets.append(link['href'])
            for seed in soup.find_all('td', {"style":"text-align: center;color:green;"}):
                self.seeders.append(seed.get_text())
            for leech in soup.find_all('td', {"style":"text-align: center;color:red;"}):
                self.leechers.append(leech.get_text())
            
            i = 0
            sizes, update = [], []
            for info in soup.find_all('td', class_="is-hidden-touch"):
                if i == 3:
                    i = 0
                if i == 0:
                    sizes.append(info.get_text())
                if i == 2:
                    update.append(info.get_text())
                i+=1
            for x in range(0, len(sizes)):
                self.desc.append("Size: " + sizes[x] + " Uploaded: " + update[x])

        if self.provider == '1337X':
            for link in soup.find_all('a', href=True):
                if (link['href'])[:8] == '/torrent':
                    parts = link['href'].split('/')
                    self.titles.append(str(parts[3]).replace("-", "_"))
                    resp2 = requests.get('https://1337x.to'
                            + link['href']).text
                    soup2 = BeautifulSoup(resp2, features='lxml')
                    magnetlinks = soup2.find_all('ul', class_="dropdown-menu")
                    magnetlinks[0] = str(magnetlinks[0])
                    soup3 = BeautifulSoup(magnetlinks[0], features='lxml')
                    m = soup3.find_all('a', href=True)[3]
                    self.magnets.append(m['href'])

            for seed in soup.find_all('td', {'class':["coll-2", "seeds"]}):
                seed = str(seed)
                sdata = seed.replace("</td", 'seeds">').split('seeds">')[1]
                self.seeders.append(str(sdata))
            for leech in soup.find_all('td', {'class':["coll-3", "leeches"]}):
                leech = str(leech)
                ldata = leech.replace("</td", 'leeches">').split('leeches">')[1]
                self.leechers.append(str(ldata))

            users = []
            for user in soup.find_all('td', {'class':['coll-5', 'user']}):
                user = str(user)
                user = user.replace('/">', "</a>").split("</a>")[1]
                users.append(user)
            sizes = []
            for size in soup.find_all('td', {'class':['col-4', 'size']}):
                size = str(size)
                size = size.replace('">', '<span').split('<span')[1]
                sizes.append(size)
            for x in range(0, len(users)):
                self.desc.append("Size: " + sizes[x] + " Uploaded by: " + users[x])
                
        if self.provider == "Pirate Bay":
            mush = str(soup).replace('>', '<')
            all_seed = mush.split('<')
            leech = False

            for x in range(0, len(all_seed)):
                if all_seed[x] == 'td align="right"':
                    if leech == False:
                        self.seeders.append(all_seed[x + 1])
                        leech = True
                    else:
                        self.leechers.append(all_seed[x + 1])
                        leech = False

            for x in soup.find_all('font'):
                x = str(x)
                a = x.replace(', ULed by', '').replace(',', '>'
                    ).replace('Uploaded', '>').replace('<', '>'
                    ).split('>')
                self.desc.append(a[4].replace('Size', 'Size:')
                             + 'Uploaded by: ' + a[6])

        if self.sizelimit != "All" or self.seedmin != "All":
            if self.seedmin == "All":
                self.seedmin = -1
            else:    
                self.seedmin = self.seedmin.replace(">", "").replace("k", "000").replace("Seeders", "")
            
            if self.sizelimit == "All":
                self.sizelimit = "1000TB"
            s, l, m, t, d = [], [], [], [], []
            x = 0
            breakpoint = text_to_num(self.sizelimit.replace(" ", "").replace("<", ""))
            
            while 1:
                if x == len(self.desc):
                    break
                sdata = self.desc[x].split(" ")
                y = sdata.index("Size:")
                size = (sdata[y+1]+sdata[y+2]).replace(" ", "")
                if self.provider == "Pirate Bay":
                    size = sdata[y+1].replace("i", "").replace(" ", "")
                if text_to_num(size) < breakpoint:
                    if int(self.seeders[x]) > int(self.seedmin):
                        s.append(self.seeders[x])
                        l.append(self.leechers[x])
                        m.append(self.magnets[x])
                        t.append(self.titles[x])
                        d.append(self.desc[x])
                x+=1
            self.listChanged.emit(t, m, s, l, d)
            return

        self.listChanged.emit(self.titles, self.magnets, self.seeders,
                              self.leechers, self.desc)
			
