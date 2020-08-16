import libtorrent as lt
import time
import itertools
import magneturi
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog, QProgressBar, \
    QPushButton
import notifier
import datetime
kill = False
started = False
pause = False
notify = False
logpath = ''
que = []
indexing = 1

def set_notification(notify_):
    global notify
    notify = notify_

def torrent_to_magnet(file):
    magnet = magneturi.from_torrent_file(file)
    return magnet

def remove_item_que(index, all_items=False):
    global que
    if all_items == True:
        que = []
        return
    del que[index]

def logging(_path):
    global logpath
    logpath = _path

def torrent_pause():
    global pause
    if pause == True:
        pause = False
    else:
        pause = True

def abort():
    global kill
    kill = True

def set_que(_que):
    global que
    que.append(_que)

class Torrent(QThread):
    countChanged = pyqtSignal(int)
    statusChanged = pyqtSignal(str)
    listChanged = pyqtSignal(int, str)

    def rerun(self, _magnet, path):
        global indexing
        indexing += 1
        self.magnet = _magnet
        self.run()

    def __init__(self, _path):
        QThread.__init__(self)
        global que
        self.magnet = que[0]
        self.path = _path

    def __del__(self):
        self.wait()

    def run(self):
        global started, kill, pause, logpath, que, indexing, notify
        self.starttime = time.time()

        ses = lt.session()
        ses.listen_on(6881, 6891)
        if self.path == '':
            self.statusChanged.emit('Invalid path')
            self.countChanged.emit(0)
            self.countChanged.emit(101)
            return
        params = {'save_path': self.path}

        if self.magnet[:7] != 'magnet:':
            self.statusChanged.emit('Invalid magnet')
            return

        link = self.magnet

        try:
            handle = lt.add_magnet_uri(ses, link, params)
        except:
            self.statusChanged.emit('Invalid magnet')
            return

        ses.start_dht()

        try:
            while not handle.has_metadata():
                time.sleep(1)
        except:
            self.countChanged.emit(0)
            self.statusChanged.emit('Invalid magnet')

        started = True
        torinfo = handle.get_torrent_info()
        self.listChanged.emit(0, torinfo.name())

        while handle.status().state != lt.torrent_status.seeding:
            s = handle.status()
            utime = str(datetime.timedelta(seconds=int(time.time()
                        - self.starttime)))

            state_str = [
                'queued',
                'checking',
                'downloading metadata',
                'downloading',
                'finished',
                'seeding',
                'allocating',
                ]
            print (
                s.progress * 100,
                'complete (down:',
                s.download_rate / 1000,
                'kb/s up:',
                s.upload_rate / 1000,
                'kB/s peers:',
                s.num_peers,
                state_str[s.state] + ' ' + utime,
                )

            try:
                self.countChanged.emit(int(s.progress * 100))
                self.statusChanged.emit('down: ' + str(int(s.download_rate
                        / 1000)) + ' kb/s up: ' + str(int(s.upload_rate
                        / 1000)) + ' kB/s peers: ' + str(s.num_peers)
                        + ' ' + str(state_str[s.state]) + ' Uptime: ' + utime)
            except:
                pass  # Ignore progress bar error it will resume to a working state anyways

            ips = handle.get_peer_info()
            ip_info = []
            for ip in ips:
                _ip = ip.ip
                ip_info.append(_ip)
                print(_ip)

            if logpath != '':
                with open(logpath + '/kml.log', 'a+') as F:
                    F.write('down: ' + str(s.download_rate / 1000)
                            + ' kb/s up: ' + str(s.upload_rate / 1000)
                            + ' kB/s peers: ' + str(s.num_peers) + ' '
                            + str(state_str[s.state]) + ' peer: '
                            + str(ip_info) + '\n')

            if pause == True:
                handle.pause()
                while not handle.status().paused:
                    self.statusChanged.emit('Pausing torrent download')
                    time.sleep(1)

                while 1:
                    if kill == True:
                        self.countChanged.emit(0)
                        self.countChanged.emit(101)
                        self.statusChanged.emit('Status: Idle')
                        return
                    if pause == False:
                        self.statusChanged.emit('Resuming torrent download'
                                )
                        break
                    self.statusChanged.emit('Torrent download paused')
                    handle.pause()
                    time.sleep(1)

            if kill == True:
                self.countChanged.emit(0)
                self.countChanged.emit(101)
                self.listChanged.emit(-1, '')
                remove_item_que(0, True)
                self.statusChanged.emit('Status: Idle')
                kill = False
                return
            time.sleep(0.1)

        self.countChanged.emit(100)
        self.statusChanged.emit('Download complete')
        if notify == True:
            notifier.notify()
        self.listChanged.emit(0, '')
        if que != []:
            time.sleep(3)
            try:
                self.rerun(que[indexing], self.path)
            except:
                self.countChanged.emit(0)
                self.countChanged.emit(101)
                self.statusChanged.emit('Status: Idle')
                que = []
                return



			
