import select
import queue
from threading import Thread
from socketserver import ThreadingMixIn 
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import os
import json

class Handler(BaseHTTPRequestHandler):
	def do_GET(self):
		app = self.server.getApp()

		parsed_path = urlparse(self.path)
		cmdDict = parse_qs(parsed_path.query)
		cmd = parsed_path.path
		if cmd.startswith('/'):
			cmd = cmd[1:]
			
		cmdDict['__cmd'] = [cmd]
		app.dispatch(cmdDict, self)

	def do_POST(self):
		app = self.server.getApp()

		parsed_path = urlparse(self.path)
		cmdDict = parse_qs(parsed_path.query)
		cmd = parsed_path.path
		if cmd.startswith('/'):
			cmd = cmd[1:]

		cmdDict['__cmd'] = [cmd]
		app.dispatch(cmdDict, self)

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
	def serve_reprap(self):
		self.haltServer = False
		while self.haltServer == False:
			r = select.select([self.socket], [], [], 1)[0]
			if r:
				self.handle_request()

	def setApp(self, app):
		self.app = app

	def getApp(self):
		return self.app

	def shut_down(self):
		self.haltServer = True

class ShapeokoHTTPServer:
	def __init__(self, ip, port, httpcmdq, httprespq):
		print("creating server at (%s) (%d)" % (ip, port))
		self.server = ThreadingHTTPServer((ip, port), Handler)
		self.server.setApp(self)
		self.httpcmdq = httpcmdq
		self.httprespq = httprespq
		self.thread = Thread(target=self.server.serve_reprap)
		self.thread.start()

	def getThread(self):
		return self.thread

	def getServer(self):
		return self.server

	def dispatch(self, cmd, handler):
		cs = cmd['__cmd'][0]
		# handle 'ls', 'sendfile', 'delfile', and 'getfile' commands here since they just
		# deal with the file system
		if cs == 'ls':
			try:
				rv = [f for f in os.listdir(self.directory) \
					if os.path.isfile(os.path.join(self.directory, f)) \
                    and os.path.splitext(f)[1].lower() in [".nc", ".gcode"]]
			except:
				handler.send_response(400)
				handler.send_header("Content-type", "application/octet-stream")
				handler.end_headers()
				handler.wfile.write(b'unable to obtain directory listing')
				return

			body = json.dumps({'files': rv}).encode()
			handler.send_response(200)
			handler.send_header("Content-type", "text/plain")
			handler.end_headers()
			handler.wfile.write(body)

		elif cs == "getfile":
			try:
				fn = os.path.join(self.directory, cmd["name"][0])
			except:
				handler.send_response(400)
				handler.send_header("Content-type", "application/octet-stream")
				handler.end_headers()
				handler.wfile.write(b'missing name of file to retrieve')
				return

			try:
				content = open(fn, 'rb').read()
			except:
				handler.send_response(400)
				handler.send_header("Content-type", "application/octet-stream")
				handler.end_headers()
				handler.wfile.write(b'unable to open requested file')
				return

			handler.send_response(200)
			handler.send_header("Content-type", "application/octet-stream")
			handler.end_headers()
			handler.wfile.write(content)

		elif cs == "delfile":
			try:
				os.remove(self.directory, cmd["name"][0])
			except:
				handler.send_response(400)
				handler.send_header("Content-type", "application/octet-stream")
				handler.end_headers()
				handler.wfile.write(b'unable to delete specified file')
				return

			handler.send_response(200)
			handler.send_header("Content-type", "application/octet-stream")
			handler.end_headers()
			handler.wfile.write(b'file deleted')
			self.httpcmdq.put({'__cmd': ["refresh"]})  # tell main thread to refresh file lists

		elif cs == "sendfile":
			length = int(handler.headers['content-length'])
			filedata = handler.rfile.read(length)
			try:
				fn = cmd["name"][0]			
			except:
				fn = None

			if fn is None:
				body = b'Unable to determine file name'
				handler.send_response(400)
				handler.send_header("Content-type", "text/plain")
				handler.end_headers()
				handler.wfile.write(body)
				return

			try:
				with open(os.path.join(self.directory, fn), "wb") as ofp:
					ofp.write(filedata)
			except:
				handler.send_response(400)
				handler.send_header("Content-type", "application/octet-stream")
				handler.end_headers()
				handler.wfile.write(b'unable to write to specified file')
				return

			body = "POST request File (%s) written %d bytes" % (fn, length)
			handler.send_response(200)
			handler.send_header("Content-type", "text/plain")
			handler.end_headers()
			handler.wfile.write(body.encode())
			self.httpcmdq.put({'__cmd': ["refresh"]})  # tell main thread to refresh file lists

		else:
			self.httpcmdq.put(cmd)
			
			try:
				rc, body = self.httprespq.get(True, 10)
			except queue.Empty:
				handler.send_response(400)
				handler.send_header("Content-type", "text/plain")
				handler.end_headers()
				handler.wfile.write(body)
				return

			return rc, body
			if rc == 200:
				handler.send_response(200)
				handler.send_header("Content-type", "text/plain")
				handler.end_headers()
				handler.wfile.write(body)
			else:
				handler.send_response(400)
				handler.send_header("Content-type", "text/plain")
				handler.end_headers()
				handler.wfile.write(body)

	def close(self):
		self.server.shut_down()


