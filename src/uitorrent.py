import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt
import torrent
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton)
from PyQt5.QtGui import QIcon
import platform
import os
import pyrateParser
import subprocess
import sys
import libtorrent
if platform.system() == "Windows":
    import win32com.shell.shell as shell
import time
import urllib.request
if platform.system() == "Windows":
    import vpn
import threading
import requests
import json
if platform.system() == "Windows":
    import admin
import notifier

magnets = []
names = []
leechers = []
descs = []
paused = False
notify = False
path = ""

DEFAULT_STYLE = """
QProgressBar{
    border: 1px solid grey;
    border-radius: 5px;
    text-align: center
}

QProgressBar::chunk {
    background-color: rgb(52, 101, 164);
    width: 10px;
    margin: 1px;
}
"""

installdir = ""
if platform.system() == "Windows":
    installdir = os.getenv('APPDATA')
if platform.system() == "Linux":
    installdir = "./.kamaltorrent/"
if installdir == "":
    print("System:", platform.system(), "Not supported")

def install():
    if platform.system() == "Windows" and not os.path.exists(installdir):
        os.mkdir(installdir+"\\kmt\\")
        os.mkdir(installdir+"\\kmt\\images")
        urllib.request.urlretrieve("https://i.postimg.cc/8zNq5ZH7/dirsel.png", installdir+"\\kmt\\images\\dirsel.png")
        urllib.request.urlretrieve("https://i.postimg.cc/gch5HCtw/kmtorrentlogo.png", installdir+"\\kmt\\images\\KmTorrentLogo.png")
        urllib.request.urlretrieve("https://i.postimg.cc/LXGZhwdL/KmIcon.png", installdir+"\\kmt\\images\\icon.png")
    if platform.system() == "Linux" and not os.path.exists(installdir):
        original_umask = os.umask(0)
        os.mkdir(installdir)
        os.mkdir(installdir+"/kmt/")
        os.mkdir(installdir+"/kmt/images")
        urllib.request.urlretrieve("https://i.postimg.cc/8zNq5ZH7/dirsel.png", installdir+"/kmt/images/dirsel.png")
        urllib.request.urlretrieve("https://i.postimg.cc/gch5HCtw/kmtorrentlogo.png", installdir+"/kmt/images/KmTorrentLogo.png")
        urllib.request.urlretrieve("https://i.postimg.cc/LXGZhwdL/KmIcon.png", installdir+"/kmt/images/icon.png")

class Ui_MainWindow(object):
    def setAssoc(self):
        if platform.system() == "Linux":
            os.system("xdg-mime default kmtorrent.desktop x-scheme-handler/magnet")
            return

        if not admin.isUserAdmin() and platform.system == "Windows":
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Question)
            msgBox.setText("Set Association")
            msgBox.setInformativeText("This feature requires elevated privilieges\nrun this feature in admin mode?")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msgBox.setDefaultButton(QtWidgets.QMessageBox.No)
            reply = msgBox.exec_()
            if reply == QtWidgets.QMessageBox.Yes:
                admin.runAsAdmin(cmdLine=[sys.argv[0]]+["ADMIN"])

            elif reply == QtWidgets.QMessageBox.No:
                return
        elif platform.system == "Windows":
            change_regedit()

    def setupUi(self, MainWindow):
        global path
        MainWindow.setObjectName("MainWindow")
        MainWindow.setBaseSize(705, 496)
        MainWindow.setStyleSheet("background-color: rgb(85, 87, 83);")

        try:
            with open(installdir+"/kmt/settings/DefaultDir.setting", "r") as F:
                path = F.read()
        except:
            if os.path.isdir(os.path.dirname(installdir+"/kmt/torrents")) == True:
                path = os.path.dirname(installdir+"/kmt/torrents")
            else:
                path = os.path.dirname(".")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        pic = QtWidgets.QLabel(MainWindow)
        pic.setGeometry(12, 25, 477, 65)
        pic.setPixmap(QtGui.QPixmap(installdir+"/kmt/images/KmTorrentLogo.png"))

        self.TorrentProgress = QtWidgets.QProgressBar(self.centralwidget)
        self.TorrentProgress.setGeometry(QtCore.QRect(2, 421, 480, 27))
        self.TorrentProgress.setProperty("value", 0)
        self.TorrentProgress.setStyleSheet(DEFAULT_STYLE)
        self.TorrentProgress.setObjectName("TorrentProgress")

        self.TorrentInformation = QtWidgets.QLabel(self.centralwidget)
        self.TorrentInformation.setGeometry(QtCore.QRect(2, 391, 480, 27))
        self.TorrentInformation.setStyleSheet("background-color: rgb(64, 64, 64);")
        self.TorrentInformation.setObjectName("TorrentInformation")

        self.TorrentInformation.setFont(QtGui.QFont("Mono", 8))
        self.TorrentInformation.setText("Status: Idle")

        self.TorrentInformation.setFrameShape(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Raised)
        self.TorrentInformation.setLineWidth(1)

        self.ListOfTorrents = QtWidgets.QListWidget(self.centralwidget)
        self.ListOfTorrents.setGeometry(QtCore.QRect(520, 110, 181, 307))
        self.ListOfTorrents.setStyleSheet("background-color: rgb(64, 64, 64);")
        self.ListOfTorrents.setObjectName("ListOfTorrents")

        self.RemQue = QtWidgets.QPushButton(self.centralwidget)
        self.RemQue.setGeometry(QtCore.QRect(519, 421, 91, 27))
        self.RemQue.setStyleSheet("background-color: rgb(153, 0, 0);")
        self.RemQue.setProperty("value", 0)
        self.RemQue.setObjectName("RemQue")

        self.AddQue = QtWidgets.QPushButton(self.centralwidget)
        self.AddQue.setGeometry(QtCore.QRect(610, 421, 91, 27))
        self.AddQue.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.AddQue.setProperty("value", 0)
        self.AddQue.setObjectName("AddQue")

        self.SearchRes = QtWidgets.QListWidget(self.centralwidget)
        self.SearchRes.setGeometry(QtCore.QRect(2, 133, 480, 255))
        self.SearchRes.setStyleSheet("background-color: rgb(64, 64, 64);")
        self.SearchRes.setObjectName("SearchRes")

        self.StartSearch = QtWidgets.QPushButton(self.centralwidget)
        self.StartSearch.setGeometry(QtCore.QRect(402, 95, 80, 27))
        self.StartSearch.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.StartSearch.setObjectName("StartSearch")

        self.StartTorrent = QtWidgets.QPushButton(self.centralwidget)
        self.StartTorrent.setGeometry(QtCore.QRect(520, 72, 181, 27))
        self.StartTorrent.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.StartTorrent.setObjectName("StartTorrent")

        self.SetPath = QtWidgets.QPushButton(self.centralwidget)
        self.SetPath.setGeometry(QtCore.QRect(520, 30, 30, 31))
        self.SetPath.setIcon(QtGui.QIcon(installdir+'/kmt/images/dirsel.png'))
        self.SetPath.setObjectName("SetPath")

        self.MagnetInput = QtWidgets.QLineEdit(self.centralwidget)
        self.MagnetInput.setGeometry(QtCore.QRect(550, 30, 151, 31))
        self.MagnetInput.setStyleSheet("background-color: rgb(64, 64, 64);  border: 1px solid grey;")
        self.MagnetInput.setFont(QtGui.QFont("Cantarell", 11))
        self.MagnetInput.setPlaceholderText("magnet: ")
        self.MagnetInput.setObjectName("MagnetInput")

        self.SearchInput = QtWidgets.QLineEdit(self.centralwidget)
        self.SearchInput.setGeometry(QtCore.QRect(2, 93, 390, 31))
        self.SearchInput.setStyleSheet("background-color: rgb(64, 64, 64);  border: 1px solid grey;")

        self.SearchInput.setFont(QtGui.QFont("Cantarell", 11))
        self.SearchInput.setPlaceholderText("search: ")
        self.SearchInput.setObjectName("SearchInput")

        self.SetSearchProvider = QtWidgets.QComboBox(self.centralwidget)
        self.SetSearchProvider.setGeometry(QtCore.QRect(302, 72, 90, 20))
        self.SetSearchProvider.setFont(QtGui.QFont("Mono", 6))
        self.SetSearchProvider.addItem("Pirate Bay")
        self.SetSearchProvider.addItem("1337X")
        self.SetSearchProvider.addItem("eztv")
        
        self.SetSearchCat = QtWidgets.QComboBox(self.centralwidget)
        self.SetSearchCat.setGeometry(QtCore.QRect(2, 72, 100, 20))
        self.SetSearchCat.setFont(QtGui.QFont("Mono", 6))
        self.SetSearchCat.addItem("All")
        self.SetSearchCat.addItem("Music")
        self.SetSearchCat.addItem("Movies")
        self.SetSearchCat.addItem("TV Shows")
        self.SetSearchCat.addItem("PC Games")
        self.SetSearchCat.addItem("UNIX Apps")
        self.SetSearchCat.addItem("Windows Apps")

        self.SetSearchSizeFilter = QtWidgets.QComboBox(self.centralwidget)
        self.SetSearchSizeFilter.setGeometry(QtCore.QRect(102, 72, 100, 20))
        self.SetSearchSizeFilter.setFont(QtGui.QFont("Mono", 6))
        self.SetSearchSizeFilter.addItem("All")
        self.SetSearchSizeFilter.addItem("< 10 MB")
        self.SetSearchSizeFilter.addItem("< 100 MB")
        self.SetSearchSizeFilter.addItem("< 1 GB")
        self.SetSearchSizeFilter.addItem("< 10 GB")
        
        self.SetSearchSeedFilter = QtWidgets.QComboBox(self.centralwidget)
        self.SetSearchSeedFilter.setGeometry(QtCore.QRect(202, 72, 100, 20))
        self.SetSearchSeedFilter.setFont(QtGui.QFont("Mono", 6))
        self.SetSearchSeedFilter.addItem("All")
        self.SetSearchSeedFilter.addItem("> 10 Seeders")
        self.SetSearchSeedFilter.addItem("> 50 Seeders")
        self.SetSearchSeedFilter.addItem("> 90 Seeders")
        self.SetSearchSeedFilter.addItem("> 1k Seeders")
        
        self.EndTorrent = QtWidgets.QPushButton(self.centralwidget)
        self.EndTorrent.setGeometry(QtCore.QRect(520, 71, 90, 27))
        self.EndTorrent.setStyleSheet("background-color: rgb(153, 0, 0);")
        self.EndTorrent.setObjectName("EndTorrent")
        self.EndTorrent.setText("Abort")
        self.EndTorrent.hide()
        self.EndTorrent.clicked.connect(lambda: torrent.abort())

        self.PauseTorrent = QtWidgets.QPushButton(self.centralwidget)
        self.PauseTorrent.setGeometry(QtCore.QRect(610, 71, 91, 27))
        self.PauseTorrent.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.PauseTorrent.setObjectName("PauseTorrent")
        self.PauseTorrent.setText("Pause")
        self.PauseTorrent.hide()
        self.PauseTorrent.clicked.connect(lambda: self.pause())

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setStyleSheet("background-color: rgb(64, 64, 64);")

        self.menubar.setGeometry(QtCore.QRect(0, 0, 705, 24))
        self.menubar.setObjectName("menubar")
        self.menuMain = QtWidgets.QMenu(self.menubar)

        self.menuTorrent = QtWidgets.QMenu(self.menubar)
        self.menuTorrent.setObjectName("menuTorrent")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuWeb = QtWidgets.QMenu(self.menubar)
        self.menuWeb.setObjectName("menuWeb")
        self.menuVPN = QtWidgets.QMenu(self.menubar)
        self.menuVPN.setObjectName("menuVPN")

        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.OpenFolder = QtWidgets.QAction(MainWindow)
        self.OpenFolder.setObjectName("OpenFolder")

        self.actionLog = QtWidgets.QAction(MainWindow)
        self.actionLog.setObjectName("actionLog")

        self.actionDownload = QtWidgets.QAction(MainWindow)
        self.actionDownload.setObjectName("actionDownload")

        self.actionDownloadUrl = QtWidgets.QAction(MainWindow)
        self.actionDownloadUrl.setObjectName("actionDownloadUrl")

        self.actionGit = QtWidgets.QAction(MainWindow)
        self.actionGit.setObjectName("actionGit")

        self.actionASSOC = QtWidgets.QAction(MainWindow)
        self.actionASSOC.setObjectName("actionASSOC")

        self.actionNotification = QtWidgets.QAction(MainWindow, checkable=True)
        self.actionNotification.setObjectName("actionNotification")

        self.actionDEFAULTDIR = QtWidgets.QAction(MainWindow)
        self.actionDEFAULTDIR.setObjectName("actionDEFAULTDIR")

        self.actionVPN = QtWidgets.QAction(MainWindow)
        self.actionVPN.setObjectName("actionVPN")

        self.menuWeb.addAction(self.actionGit)
        self.menuSettings.addAction(self.OpenFolder)
        self.menuSettings.addAction(self.actionLog)
        self.menuSettings.addAction(self.actionASSOC)
        self.menuSettings.addAction(self.actionDEFAULTDIR)
        self.menuSettings.addAction(self.actionNotification)
        self.menuTorrent.addAction(self.actionDownload)
        self.menuTorrent.addAction(self.actionDownloadUrl)
        self.menuVPN.addAction(self.actionVPN)

        self.menubar.addAction(self.menuTorrent.menuAction())
        #self.menubar.addAction(self.menuMain.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuWeb.menuAction())
        if platform.system() == "Windows":
            self.menubar.addAction(self.menuVPN.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.StartTorrent.clicked.connect(lambda: self.start_magnet_onclick(self.MagnetInput.text()))
        self.SetPath.clicked.connect(lambda: self.set_output_path())
        self.StartSearch.clicked.connect(lambda: self.get_results(self.SearchInput.text()))
        self.SearchRes.itemClicked.connect(lambda: self.on_enter())
        self.actionLog.triggered.connect(lambda: self.set_logging())

        self.SetSearchProvider.currentIndexChanged.connect(lambda: self.check_provider())
        self.AddQue.clicked.connect(lambda: self.add_to_que())
        self.RemQue.clicked.connect(lambda: self.rem_que())

        self.OpenFolder.triggered.connect(lambda: self.open_default_folder())
        self.actionGit.triggered.connect(lambda: self.open_github())

        self.actionDownload.triggered.connect(lambda: self.open_torrent_file())
        self.actionDownloadUrl.triggered.connect(lambda: self.open_torrent_url())

        self.actionASSOC.triggered.connect(lambda: self.setAssoc())
        self.actionDEFAULTDIR.triggered.connect(lambda: self.set_default_folder())
        self.actionVPN.triggered.connect(lambda: self.set_vpn())
        self.actionNotification.triggered.connect(lambda: self.notifier_set())

        MainWindow.setFixedSize(705, 496)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle("KmTorrent");
        self.menuTorrent.setTitle(_translate("MainWindow", "Torrent"))
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuWeb.setTitle(_translate("MainWindow", "Web"))
        self.menuVPN.setTitle(_translate("MainWindow", "Vpn"))

        self.StartTorrent.setText(_translate("MainWindow", "Download Torrents"))
        self.StartSearch.setText(_translate("MainWindow", "Search"))
        self.actionGit.setText(_translate("MainWindow", "Github"))
        self.actionDownload.setText(_translate("MainWindow", "Download .torrent"))
        self.actionDownloadUrl.setText(_translate("MainWindow", "Download .torrent from URL"))

        self.actionASSOC.setText(_translate("MainWindow", "Set Associations"))
        self.actionNotification.setText(_translate("MainWindow", "Notification"))
        self.actionDEFAULTDIR.setText(_translate("MainWindow", "Set Default Folder"))
        self.actionVPN.setText(_translate("MainWindow", "Connect"))

        self.OpenFolder.setText(_translate("MainWindow", "Open Folder"))
        self.actionLog.setText(_translate("MainWindow", "Log"))
        self.AddQue.setText(_translate("MainWindow", "Add"))
        self.RemQue.setText(_translate("MainWindow", "Remove"))

        try:
            if sys.argv[1][:7] == "magnet:":
                self.MagnetInput.setText(sys.argv[1])

            if sys.argv[1][-8:] == ".torrent":
                try:
                    self.MagnetInput.setText(torrent.torrent_to_magnet(sys.argv[1]))
                except:
                    self.TorrentInformation.setText("Invalid .torrent file")
        except:
            pass

    def check_provider(self):
        if self.SetSearchProvider.currentText() == "eztv":
            self.SetSearchCat.setCurrentIndex(0)
            self.SetSearchCat.setEnabled(False)
        else:
            self.SetSearchCat.setEnabled(True)

    def notifier_set(self):
        global notify
        if notify == True:
            notify = False
            return
        if notify == False:
            notify = True
            return

    def open_torrent_url(self):
        msgBox = QtWidgets.QInputDialog()
        url, ok = msgBox.getText(MainWindow, "Direct torrent download", "Enter torrent url")

        url = str(url)
        if not ok:
            return
        try:
            urllib.request.urlretrieve(url, "temp.torrent")
        except:
            self.TorrentInformation.setText("Invalid url")
        try:
            self.MagnetInput.setText(torrent.torrent_to_magnet("temp.torrent"))
            os.remove("temp.torrent")
        except:
            self.TorrentInformation.setText("Invalid .torrent file")

    def open_torrent_file(self):
        fileName = str(QtWidgets.QFileDialog.getOpenFileName(filter="*.torrent")[0])
        print(fileName)
        if fileName == "":
            return
        try:
            self.MagnetInput.setText(torrent.torrent_to_magnet(fileName))
        except:
            self.TorrentInformation.setText("Invalid .torrent file")

    def set_vpn(self):
        os.system('rasdial > out')
        with open("out") as F:
            result = F.read().encode()

        if self.actionVPN.text() == "Connect":
            if result == b'No connections\nCommand completed successfully.\n':
                t1 = threading.Thread(target=vpn.connect)
                t1.start()
                self.actionVPN.setText("Disconnect from VPN")
                self.TorrentInformation.setText("Connecteded to vpn")
            else:
                self.TorrentInformation.setText("Already connected to vpn")
            self.actionVPN.setText("Disconnect")
        else:
            if result == b'Connected to\nkamalvpn\nCommand completed successfully.\n':
                t1 = threading.Thread(target=vpn.disconnect)
                t1.start()
                self.actionVPN.setText("Connect to VPN")
                self.TorrentInformation.setText("Disconnected from vpn")
            else:
                self.TorrentInformation.setText("Already disconnected from vpn")
            self.actionVPN.setText("Connect")
        os.remove("out")

    def set_default_folder(self):
        global path
        path = str(QtWidgets.QFileDialog.getExistingDirectory())
        try:
            os.mkdir(installdir+"/kmt/settings")
        except:
            pass

        with open(installdir+"/kmt/settings/DefaultDir.setting", "w") as F:
            F.write(path)

    def open_github(self):
        if sys.platform == 'darwin':
             subprocess.check_call(['open', '--', 'https://github.com/KamalDevelopers/KamalTorrent'])
        elif sys.platform == 'linux2':
            subprocess.check_call(['xdg-open', '--', 'https://github.com/KamalDevelopers/KamalTorrent'])
        elif sys.platform == 'linux':
            subprocess.check_call(['xdg-open', 'https://github.com/KamalDevelopers/KamalTorrent'])
        elif sys.platform == 'win32':
            os.system('start https://github.com/KamalDevelopers/KamalTorrent')

    def getip(self):
        ip = requests.get('http://ip.42.pl/raw').text

        data = requests.get('http://ip-api.com/json/' + ip).text
        j = json.loads(data)["country"]

        self.TorrentInformation.setText(ip + "  --  " + j)

    def open_default_folder(self):
        print(path)
        _path = os.path.realpath(path)
        if platform.system() == "Windows":
            os.startfile(_path)
        elif platform.system() == "Linux":
            os.system("xdg-open " + str(_path))

    def set_logging(self):
        self.path_log = str(QtWidgets.QFileDialog.getExistingDirectory())
        torrent.logging(self.path_log)

    def rem_que(self):
        global magnets
        try:
            index = [x.row() for x in self.ListOfTorrents.selectedIndexes()][0]
            self.ListOfTorrents.takeItem(index)
            torrent.remove_item_que(index)
        except:
            self.TorrentInformation.setText("Could not remove item from queue")

    def add_to_que(self):
        global magnets, names
        if self.MagnetInput.text() == "":
            return
        try:
            index = magnets.index(self.MagnetInput.text())

            torrent.set_que(self.MagnetInput.text())
            self.ListOfTorrents.addItem(names[index].replace("_", " "))
        except:
            torrent.set_que(self.MagnetInput.text())
            self.ListOfTorrents.addItem(self.MagnetInput.text())
        self.MagnetInput.setText("")

    def pause(self):
        global paused

        if paused == False:
            self.PauseTorrent.setText("Unpause")
            paused = True
        else:
            self.PauseTorrent.setText("Pause")
            paused = False
        torrent.torrent_pause()

    def on_enter(self):
        global magnets, seeders, names, leechers, descs
        torrent = self.SearchRes.currentItem().text().replace(" ", "_")
        index = names.index(torrent)
        self.MagnetInput.setText(magnets[index])
        self.TorrentInformation.setText("Seeders: " + seeders[index] + "  Leechers: " + leechers[index] + " " + descs[index])

    def set_output_path(self):
        global path
        try:
            os.chdir(path)
        except:
            os.chdir(".")
        _path = str(QtWidgets.QFileDialog.getExistingDirectory())
        if _path != "":
            path = _path

    def onSearchRes(self, _names, _magnets, _seeders, _leechers, _descs):
        global magnets, seeders, names, leechers, descs
        magnets = _magnets
        seeders = _seeders
        names = _names
        leechers = _leechers
        descs = _descs
        self.SearchRes.clear()

        if len(seeders) == 0:
            self.TorrentInformation.setText("No search results found")
        elif self.TorrentInformation.text() == "No search results found" and len(seeders) != 0:
            self.TorrentInformation.setText("")

        for x in range(0, len(seeders)):
            self.SearchRes.addItem(_names[x].replace("_", " "))

    def onListChanged(self, index, name=""):
        if name != "":
            self.ListOfTorrents.takeItem(index)
            self.ListOfTorrents.insertItem(index, name)
            return

        if index == -1:
            self.ListOfTorrents.clear()
            return
        self.ListOfTorrents.takeItem(index)

        #print(self.ListOfTorrents.findItems(value, QtCore.Qt.MatchExactly))
        #if self.ListOfTorrents.findItems(value, QtCore.Qt.MatchExactly) == []:
        #    self.ListOfTorrents.addItem(value)

    def onCountChanged(self, value):
        if value == 101:
            self.EndTorrent.hide()
            self.PauseTorrent.hide()
            self.StartTorrent.show()
            return
        self.TorrentProgress.setValue(value)

    def onStatusChanged(self, value):
        self.TorrentInformation.setText(value)

    def get_results(self, query):
        if query == "ip[]":
            self.getip()
            return
        self.parse_query = pyrateParser.Parse(query, self.SetSearchProvider.currentText(), self.SetSearchCat.currentText(), self.SetSearchSizeFilter.currentText(), self.SetSearchSeedFilter.currentText())
        self.parse_query.listChanged.connect(self.onSearchRes)
        self.parse_query.start()

    def start_magnet_onclick(self, magnet):
        global magnets, notify
        if self.ListOfTorrents.count() == 0:
            self.TorrentInformation.setText("Torrent list empty")
            return
        self.TorrentInformation.setText("Retrieving torrent metadata")

        try:
            self.torrent_client = torrent.Torrent(path)
        except:
            self.TorrentInformation.setText("Could not open target folder")
            return

        torrent.set_notification(notify)
        self.EndTorrent.show()
        self.PauseTorrent.show()
        self.StartTorrent.hide()
        self.torrent_client.listChanged.connect(self.onListChanged)
        self.torrent_client.countChanged.connect(self.onCountChanged)
        self.torrent_client.statusChanged.connect(self.onStatusChanged)
        self.torrent_client.start()

def change_regedit():
    os.system("REG ADD HKEY_CLASSES_ROOT\\Magnet /d \"Magnet URI\" /f")
    os.system("REG ADD HKEY_CLASSES_ROOT\\Magnet /v \"Content Type\" /d \"application/x-magnet\" /f")
    os.system("REG ADD HKEY_CLASSES_ROOT\\Magnet /v \"URL Protocol\" /d \"\" /f")
    os.system("REG ADD HKEY_CLASSES_ROOT\\Magnet\\shell\\open\\command /d \"\""+sys.argv[0]+"\" \"%1\" /SHELLASSOC\" /f")
    os.system("REG ADD HKEY_CLASSES_ROOT\\Magnet\\shell\\open\\command /d \""+sys.argv[0]+" %1 /SHELLASSOC\" /f")
    os.system("REG ADD HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.torrent\\OpenWithList /v MRUList /d ba /f")
    os.system("REG ADD HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.torrent\\OpenWithList /v a /d {1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\OpenWith.exe /f")
    os.system("REG ADD HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\FileExts\\.torrent\\OpenWithList /v b /d uitorrent.exe /f")

def SetExeLinux():
    apath = os.path.abspath("./.kamaltorrent")
    desktopdata = """[Desktop Entry]\nEncoding=UTF-8\nVersion=1.3\nType=Application\nTerminal=false\nExec="""+os.path.abspath(sys.argv[0])+"""\nName=KmTorrent\nIcon="""+apath+"/kmt/images/icon.png"+"""\nCategories=Network;"""
    os.system("touch /usr/share/applications/kmtorrent.desktop")
    with open("/usr/share/applications/kmtorrent.desktop", "w") as F:
        F.write(desktopdata)
    os.system("xdg-mime default kmtorrent.desktop x-scheme-handler/magnet")

if __name__ == "__main__":
    import sys

    kill = False
    install()
    if ".py" not in sys.argv[0] and platform.system() == "Linux" and not os.path.isfile("/usr/share/applications/kmtorrent.desktop"):
        SetExeLinux()

    app = QtWidgets.QApplication(sys.argv)
    app_icon = QtGui.QIcon()
    app_icon.addFile(installdir+"/kmt/images/icon.png", QtCore.QSize(140,100))
    app.setWindowIcon(app_icon)

    try:
        if sys.argv[1] == "ADMIN":
            change_regedit()
            kill = True
    except:
        pass

    if kill == True:
        sys.exit(0)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
