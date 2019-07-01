import httplib
import subprocess
from threading import Timer
import time
def internet():
	conn = httplib.HTTPConnection("www.google.com", timeout = 5)
	try:
		conn.request("HEAD", "/")
		conn.close()
		print("ok")
		Timer(20, internet).start()
	except:
		while True:
			try:
				time.sleep(5)
				conn.request("HEAD","/")
				conn.close()
				break
			except:
				print("waiting")
				pass
		BashCommand ="cd /home/pi/Documents/korainside/tunnel/; sh stop_tunnel.sh; sh start_tunnel.sh"
		output = subprocess.run(BashCommand, shell=True, universal_newlines=True, check=True)
		print(output.stdout)
		Timer(20, internet).start()

internet()


