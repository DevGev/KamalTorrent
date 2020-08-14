#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request
import requests
from bs4 import BeautifulSoup, SoupStrainer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, \
    QPushButton


class Parse(QThread):

    listChanged = pyqtSignal(list, list, list, list, list)

    def __init__(self, _query, _provider):
        QThread.__init__(self)
        self.query = _query
        self.provider = _provider

    def run(self):
        print(self.provider)
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
        endurl = "/1/99/0"
        self.query = self.query.replace(' ', '%20')
        
        if self.provider == "1337X":
            url = "https://1337x.to"
            endurl = "/0/"

        hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
        resp = requests.get(url + '/search/' + self.query + endurl,
                            headers=hdr).text
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

        if self.provider == '1337X':
            for link in soup.find_all('a', href=True):
                if (link['href'])[:8] == '/torrent':
                    parts = link['href'].split('/')
                    self.titles.append(str(parts[3]))
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

        self.listChanged.emit(self.titles, self.magnets, self.seeders,
                              self.leechers, self.desc)



			
