import requests
import pysftp
import io

class Controller:
	def __init__(self, ipaddr, port, user, pw):
		self.ipaddr = ipaddr
		self.port = port
		self.user = user
		self.pw = pw

	def getJobInfo(self):
		url = "http://%s:%d/getjob" % (self.ipaddr, self.port)
		r = requests.get(url)
		if r.status_code >= 400:
			return r.status_code, None
		else:
			rv = eval(r.text)
			return r.status_code, rv

	def getRemoteFile(self, fn):
		cnopts = pysftp.CnOpts()
		cnopts.hostkeys = None 

		with pysftp.Connection(self.ipaddr, username=self.user, password=self.pw, cnopts=cnopts) as sftp:
			with sftp.cd("shapeokodata"):
				if not sftp.exists(fn):
					return None

				with io.BytesIO() as fl:
					sftp.getfo(fn, fl)
					fl.seek(0)
					gc = [l.decode("utf-8") for l in fl.readlines()]
					return gc
