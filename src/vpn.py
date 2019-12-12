import os
import subprocess
import requests
import winreg

def getpassword():
	response = requests.get('https://twitter.com/vpnbook')
	chunks = response.text.replace("\\", " ").replace("<", " ").split(" ")
	x = chunks.index("Password:")
	return chunks[x+1]

def connect():
	password = getpassword()
	print(password)
	os.system("C:\\WINDOWS\\system32\\WindowsPowerShell\\v1.0\\powershell.exe Add-VpnConnection -Name kamalvpn -ServerAddress DE4.vpnbook.com")
	os.system("rasdial kamalvpn vpnbook " + password)

def disconnect():
	os.system("rasdial /disconnect")