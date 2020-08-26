from playsound import playsound
import platform
if platform.system() == 'Windows':
    from win10toast import ToastNotifier
if platform.system() == 'Linux':
    import notify2

import threading
import os
if platform.system() == 'Windows':
    from PIL import Image
import time


def notification(icon, stime):
    toaster = ToastNotifier()
    toaster.show_toast('KmTorrent', 'Download complete',
                       icon_path=icon, duration=stime)

    while toaster.notification_active():
        time.sleep(0.1)


def linux_notification(icon, stime):
    notify2.init('KmTorrent')
    note = notify2.Notification('Done', message='Download Complete',
                                icon=os.path.abspath(icon))
    note.set_urgency(notify2.URGENCY_NORMAL)
    note.set_timeout(stime)
    note.show()
    time.sleep(stime)


def notify():
    if platform.system() == 'Windows':
        installdir = os.getenv('APPDATA')
    if platform.system() == 'Linux':
        installdir = './.kamaltorrent/'
    playsound(installdir + '/kmt/audio/PersianNotification.wav')
    if platform.system() == 'Window':
        filename = os.getenv('APPDATA') + '\\kmt\\images\\icon.png'
        img = Image.open(filename)
        img.save(os.getenv('APPDATA') + '\\kmt\\images\\icon.ico')
        t1 = threading.Thread(target=notification,
                              args=(os.getenv('APPDATA')
                              + '\\kmt\\images\\icon.ico', 15))
        t1.start()
    if platform.system() == 'Linux':
        t1 = threading.Thread(target=linux_notification,
                              args=('./.kamaltorrent/kmt/images/icon.png'
                              , 15))
        t1.start()
