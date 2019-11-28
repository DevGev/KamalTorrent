import PyQt5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import Qt
import torrent
import time
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QDialog,
                             QProgressBar, QPushButton)
import os
import pyrateParser
import subprocess
import sys
import libtorrent 
import win32com.shell.shell as shell
import time
import urllib.request
magnets = []
names = []
leechers = []
paused = False
path = ""

def setAssoc():
    ASADMIN = 'asadmin'
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([script] + sys.argv[1:] + [ASADMIN])
    shell.ShellExecuteEx(lpVerb='runas', lpFile=sys.executable, lpParameters=params)
    subprocess.call("REG ADD HKEY_CLASSES_ROOT\\Magnet\\shell\\open\\command /d \""+sys.argv[0]+" %1 /SHELLASSOC\" /f", shell=True)
    time.sleep(1)
    sys.exit()

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

def install():
    try:
        os.mkdir(os.getenv('APPDATA')+"\\kmt\\")
        os.mkdir(os.getenv('APPDATA')+"\\kmt\\images")
        urllib.request.urlretrieve("https://i.postimg.cc/8zNq5ZH7/dirsel.png", os.getenv('APPDATA')+"\\kmt\\images\\dirsel.png")
        urllib.request.urlretrieve("https://i.postimg.cc/gch5HCtw/kmtorrentlogo.png", os.getenv('APPDATA')+"\\kmt\\images\\KmTorrentLogo.png")
        urllib.request.urlretrieve("https://i.postimg.cc/LXGZhwdL/KmIcon.png", os.getenv('APPDATA')+"\\kmt\\images\\icon.png")   
    except:
        pass


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        global path
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(705, 496)
        MainWindow.setStyleSheet("background-color: rgb(85, 87, 83);")

        try:
            with open(os.getenv('APPDATA')+"/kmt/settings/DefaultDir.setting", "r") as F:
                path = F.read()
        except:
            if os.path.isdir(os.path.dirname(os.getenv('APPDATA')+"/kmt/torrents")) == True:
                path = os.path.dirname(os.getenv('APPDATA')+"/kmt/torrents")
            else:
                path = os.path.dirname(".")
        
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        pic = QtWidgets.QLabel(MainWindow)
        pic.setGeometry(12, 25, 477, 65)
        #use full ABSOLUTE path to the image, not relative
        pic.setPixmap(QtGui.QPixmap(os.getenv('APPDATA')+"/kmt/images/KmTorrentLogo.png"))
        
        
        self.TorrentProgress = QtWidgets.QProgressBar(self.centralwidget)
        self.TorrentProgress.setGeometry(QtCore.QRect(2, 424, 480, 27))
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
        self.RemQue.setGeometry(QtCore.QRect(519, 424, 91, 27))
        self.RemQue.setStyleSheet("background-color: rgb(153, 0, 0);")
        self.RemQue.setProperty("value", 0)
        self.RemQue.setObjectName("RemQue")
        
        self.AddQue = QtWidgets.QPushButton(self.centralwidget)
        self.AddQue.setGeometry(QtCore.QRect(610, 424, 91, 27))
        self.AddQue.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.AddQue.setProperty("value", 0)
        self.AddQue.setObjectName("AddQue")
        
        self.SearchRes = QtWidgets.QListWidget(self.centralwidget)
        self.SearchRes.setGeometry(QtCore.QRect(2, 110, 480, 274))
        self.SearchRes.setStyleSheet("background-color: rgb(64, 64, 64);")
        self.SearchRes.setObjectName("SearchRes")
        
        self.StartSearch = QtWidgets.QPushButton(self.centralwidget)
        self.StartSearch.setGeometry(QtCore.QRect(402, 72, 80, 27))
        self.StartSearch.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.StartSearch.setObjectName("StartSearch")
        
        self.StartTorrent = QtWidgets.QPushButton(self.centralwidget)
        self.StartTorrent.setGeometry(QtCore.QRect(520, 72, 181, 27))
        self.StartTorrent.setStyleSheet("background-color: rgb(52, 101, 164);")
        self.StartTorrent.setObjectName("StartTorrent")
        
        self.SetPath = QtWidgets.QPushButton(self.centralwidget)
        self.SetPath.setGeometry(QtCore.QRect(520, 30, 30, 31))
        self.SetPath.setIcon(QtGui.QIcon(os.getenv('APPDATA')+'/kmt/images/dirsel.png'))
        self.SetPath.setObjectName("SetPath")

        self.MagnetInput = QtWidgets.QLineEdit(self.centralwidget)
        self.MagnetInput.setGeometry(QtCore.QRect(550, 30, 151, 31))
        self.MagnetInput.setStyleSheet("background-color: rgb(64, 64, 64);  border: 1px solid grey;")
        self.MagnetInput.setFont(QtGui.QFont("Cursive", 11))
        self.MagnetInput.setPlaceholderText("magnet: ")
        self.MagnetInput.setObjectName("MagnetInput")
        
        self.SearchInput = QtWidgets.QLineEdit(self.centralwidget)
        self.SearchInput.setGeometry(QtCore.QRect(2, 70, 390, 31))
        self.SearchInput.setStyleSheet("background-color: rgb(64, 64, 64);  border: 1px solid grey;")
        self.SearchInput.setFont(QtGui.QFont("Cursive", 11))
        self.SearchInput.setPlaceholderText("search: ")
        self.SearchInput.setObjectName("SearchInput")

        self.label = QtWidgets.QLabel(MainWindow)
        self.label.setGeometry(MainWindow.width()-185, 2, 200, 12)
        self.label.setObjectName("error")
        self.label.setStyleSheet('QLabel {color: red;}')
        self.label.setText("Magnet url is invalid")
        self.label.hide()
		
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
        
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuWeb = QtWidgets.QMenu(self.menubar)
        self.menuWeb.setObjectName("menuWeb")
        
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        self.OpenFolder = QtWidgets.QAction(MainWindow)
        self.OpenFolder.setObjectName("OpenFolder")
        
        self.actionLog = QtWidgets.QAction(MainWindow)
        self.actionLog.setObjectName("actionLog")
        
        self.actionGit = QtWidgets.QAction(MainWindow)
        self.actionGit.setObjectName("actionGit")

        self.actionASSOC = QtWidgets.QAction(MainWindow)
        self.actionASSOC.setObjectName("actionASSOC")

        self.actionDEFAULTDIR = QtWidgets.QAction(MainWindow)
        self.actionDEFAULTDIR.setObjectName("actionDEFAULTDIR")

        self.menuSettings.addAction(self.OpenFolder)
        self.menuSettings.addAction(self.actionLog)
        self.menuSettings.addAction(self.actionASSOC)
        self.menuSettings.addAction(self.actionDEFAULTDIR)
        self.menuWeb.addAction(self.actionGit)
        
        self.menubar.addAction(self.menuMain.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuWeb.menuAction())
		
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.StartTorrent.clicked.connect(lambda: self.start_magnet_onclick(self.MagnetInput.text()))
        self.SetPath.clicked.connect(lambda: self.set_output_path())
        self.StartSearch.clicked.connect(lambda: self.get_results(self.SearchInput.text()))
        self.SearchRes.itemClicked.connect(lambda: self.on_enter())
        self.actionLog.triggered.connect(lambda: self.set_logging())
        self.AddQue.clicked.connect(lambda: self.add_to_que())
        self.RemQue.clicked.connect(lambda: self.rem_que())
        self.OpenFolder.triggered.connect(lambda: self.open_default_folder())
        self.actionGit.triggered.connect(lambda: self.open_github())
        self.actionASSOC.triggered.connect(lambda: setAssoc())
        self.actionDEFAULTDIR.triggered.connect(lambda: self.set_default_folder())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate

        MainWindow.setWindowTitle("KmTorrent");
        self.menuSettings.setTitle(_translate("MainWindow", "Settings"))
        self.menuWeb.setTitle(_translate("MainWindow", "Web"))
        
        self.StartTorrent.setText(_translate("MainWindow", "Download Torrents"))
        self.StartSearch.setText(_translate("MainWindow", "Search"))
        self.actionGit.setText(_translate("MainWindow", "Github"))
        self.actionASSOC.setText(_translate("MainWindow", "Set Magnet Assoc"))
        self.actionDEFAULTDIR.setText(_translate("MainWindow", "Set Default Folder"))

        self.OpenFolder.setText(_translate("MainWindow", "Open Folder"))
        self.actionLog.setText(_translate("MainWindow", "Log"))
        self.AddQue.setText(_translate("MainWindow", "Add"))
        self.RemQue.setText(_translate("MainWindow", "Remove"))

        try:
            if sys.argv[1][:7] != "magnet:":
                return
            self.MagnetInput.setText(sys.argv[1])
        except:
            pass


    def set_default_folder(self):
        global path
        path = str(QtWidgets.QFileDialog.getExistingDirectory())
        try:
            os.mkdir(os.getenv('APPDATA')+"/kmt/settings")
        except:
            pass
        
        with open(os.getenv('APPDATA')+"/kmt/settings/DefaultDir.setting", "w") as F:
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

    def open_default_folder(self):
        print(path)
        _path = os.path.realpath(path)
        os.startfile(_path)

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
        global magnets, seeders, names, leechers
        torrent = self.SearchRes.currentItem().text().replace(" ", "_")
        index = names.index(torrent)
        self.MagnetInput.setText(magnets[index])
        self.TorrentInformation.setText("Seeders: " + seeders[index] + " Leechers: " + leechers[index])
	
    def set_output_path(self):
        global path
        try:
            os.chdir(path)
        except:
            os.chdir(".")
        _path = str(QtWidgets.QFileDialog.getExistingDirectory())
        if _path != "":
            path = _path

    def onSearchRes(self, _names, _magnets, _seeders, _leechers):
        global magnets, seeders, names, leechers
        magnets = _magnets
        seeders = _seeders
        names = _names
        leechers = _leechers
        self.SearchRes.clear()
        
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
        self.parse_query = pyrateParser.Parse(query)
        self.parse_query.listChanged.connect(self.onSearchRes)
        self.parse_query.start()
		
    def start_magnet_onclick(self, magnet):
        global magnets
        if self.ListOfTorrents.count() == 0:
            self.TorrentInformation.setText("Torrent list empty")
            return
        self.TorrentInformation.setText("Retrieving torrent metadata")
        
        try:
            self.torrent_client = torrent.Torrent(path)
        except:
            self.TorrentInformation.setText("Could not open target folder")
            return
        
        self.EndTorrent.show()
        self.PauseTorrent.show()
        self.StartTorrent.hide()
        self.torrent_client.listChanged.connect(self.onListChanged)
        self.torrent_client.countChanged.connect(self.onCountChanged)
        self.torrent_client.statusChanged.connect(self.onStatusChanged)
        self.torrent_client.start()
            
if __name__ == "__main__":
    import sys
    install()
    app = QtWidgets.QApplication(sys.argv)

    app_icon = QtGui.QIcon()
    app_icon.addFile(os.getenv('APPDATA')+"\\kmt\\images\\icon.png", QtCore.QSize(140,100))
    app.setWindowIcon(app_icon)

    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())