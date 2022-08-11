import requests
import os
import io

TIMEOUT = 0.3

class GFile:
	def __init__(self, printer):
		self.printer = printer
		self.url = "http://%s/api/files" % self.printer.getIpAddr()
		self.header = {"X-Api-Key": self.printer.getApiKey()}
		
	def uploadFile(self, fn, n=None, to=TIMEOUT):
		if n is None:
			bn = os.path.basename(fn)
		else:
			bn = n
			
		location = "/local"

		files = {'file': (bn, open(fn, 'rb'), 'application/octet-stream')}
		r = requests.post(self.url+location, files=files, headers=self.header, timeout=to)
		try:
			rv = r.json()
		except:
			rv = None
		return r.status_code, rv
		
	def uploadString(self, s, n, to=TIMEOUT):
		files = {'file': (n, io.StringIO(s), 'application/octet-stream')}
		location = "/local"
		r = requests.post(self.url+location, files=files, headers=self.header, timeout=to)
		try:
			rv = r.json()
		except:
			rv = None
		return r.status_code, rv
		
	def listFiles(self, local=True, sd=False, recursive=False, to=TIMEOUT):
		location = ""
		if local and not sd:
			location = "/local"
		elif sd and not local:
			location = "/sdcard"
			
		if recursive:
			location += "?recursive=true"
		
		try:	
			req = requests.get(self.url+location, headers=self.header, timeout=to)
		except:
			return None
		
		if req.status_code >= 400:
			return None
		
		finfo = req.json()
		if "files" not in finfo.keys():
			return []
		
		fl = finfo["files"]
		result = []
		for f in fl:
			if "name" in f.keys():
				if "refs" in f.keys() and "download" in f["refs"].keys():
					result.append((f["name"], f["refs"]["download"]))
				else:
					result.append((f["name"], None))
			
		return result
	
	def downloadFile(self, url, to=TIMEOUT):
		req = requests.get(url, headers=self.header, timeout=to)
		try:
			rv = req.text
		except:
			rv = None
			
		return req.status_code, rv
			
