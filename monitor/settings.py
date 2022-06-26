import os
import configparser
import socket

INIFILE = "skmonitor.ini"

def getPasswordFromFile(fn):
	if not os.path.exists(fn):
		print("Unable to determine password - cannot open .password file")
		exit(1)

	with open(fn, "r") as pfp:
		pw = pfp.readline().strip()

	return pw


class Settings:
	def __init__(self):
		# first assign default values
		self.iniipaddr = "shapeoko.local"
		self.port = 9000
		self.user = "jeff"
		self.inipassword = None
		self.localgcdir = os.getcwd()

		self.inifile = os.path.join(os.getcwd(), INIFILE)
		self.section = "skmonitor"

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
			
			self.modified = True
			self.save()

		else:

			self.modified = False	
			if self.cfg.has_section(self.section):
				for opt, value in self.cfg.items(self.section):
					if opt == 'ipaddr':
						self.iniipaddr = value
					elif opt == "port":
						try:
							p = int(value)
						except:
							print("unable to parse %s as port number - using default" % str(value))
							p = self.port		
						self.port = p
					elif opt == 'user':
						self.user = value
					elif opt == "localgcdir":
						self.localgcdir = value
					elif opt == 'password':
						if value == "None":
							self.inipassword == None
						else:
							self.inipassword = value
					else:
						print("Unknown option in ini file: %s - ignoring" % opt)
			else:
				print("Section %s missing from ini file %s - using default values" % (self.section, INIFILE))
				self.modified = True
				self.save()

		if self.inipassword is None:
			self.password = getPasswordFromFile(".password")
		else:
			self.password = self.inipassword

		self.ipaddr = socket.gethostbyname(self.iniipaddr)
	
	def setModified(self):
		self.modified = True
		
	def isModified(self):
		return self.modified

	def saveIfModified(self):
		if self.isModified():
			self.save()
		
	def save(self):
		try:
			self.cfg.add_section(self.section)
		except configparser.DuplicateSectionError:
			pass
		
		self.cfg.set(self.section, "ipaddr", str(self.iniipaddr))
		self.cfg.set(self.section, "port", "%d" % self.port)
		self.cfg.set(self.section, "user", str(self.user))

		if self.inipassword is None:
			pval = "None"
		else:
			pval = self.inipassword
		self.cfg.set(self.section, "password", pval)

		self.cfg.set(self.section, "localgcdir", str(self.localgcdir))

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False
