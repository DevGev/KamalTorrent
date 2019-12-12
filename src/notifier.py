from win10toast import ToastNotifier
import threading
import os
from PIL import Image

def notification(icon, time):
	toaster = ToastNotifier()
	toaster.show_toast("KmTorrent",
	                   "Download complete",
	                   icon_path=icon,
	                   duration=time)

	while toaster.notification_active(): time.sleep(0.1)

def notify():
	filename = os.getenv('APPDATA')+"\\kmt\\images\\icon.png"
	img = Image.open(filename)
	img.save(os.getenv('APPDATA')+"\\kmt\\images\\icon.ico")
	print("\a")	#Notification sound
	t1 = threading.Thread(target=notification, args=(os.getenv('APPDATA')+"\\kmt\\images\\icon.ico", 15))
	t1.start()