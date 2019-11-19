import urllib.request
from bs4 import BeautifulSoup, SoupStrainer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton)
                             
class Parse(QThread):
	listChanged = pyqtSignal(list, list, list, list)
	
	def  __init__(self, _query):
		QThread.__init__(self)
		self.query = _query
		
	def run(self):
		hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)' }
		req = urllib.request.Request('https://www.thepiratebay.se.net/search/' + self.query + '/0/99/0',  headers=hdr)
		resp = urllib.request.urlopen(req)
		soup = BeautifulSoup(resp, from_encoding=resp.info().get_param('charset'), features="lxml")
		
		self.magnets = []
		self.titles = []
		self.seeders = []
		self.leechers = []
		
		for link in soup.find_all('a', href=True):
			if link['href'][:7] == "magnet:":
				self.magnets.append(link['href'])
			
			if link['href'][:8] == "/torrent":
				parts = link['href'].split("/")
				self.titles.append(parts[3])
		
		mush = str(soup).replace(">", "<")
		all_seed = mush.split("<")
		leech = False
		
		for x in range(0, len(all_seed)):
			if all_seed[x] == "td align=\"right\"":
				if leech == False:
					self.seeders.append(all_seed[x+1])
					leech = True
				else:
					self.leechers.append(all_seed[x+1])
					leech = False
					

		self.listChanged.emit(self.titles, self.magnets, self.seeders, self.leechers)
