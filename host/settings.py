import os
import configparser

INIFILE = "shapeoko.ini"

def getPasswordFromFile(fn):
	if not os.path.exists(fn):
		print("Unable to determine password")
		exit(1)

	with open(fn, "r") as pfp:
		pw = pfp.readline().strip()
		print("(%s)" % pw)

	return pw


class Settings:
	def __init__(self):
		# first assign default values
		self.ipaddr = "shapeoko.local"
		self.user = "jeff"
		self.password = None

		self.inifile = os.path.join(os.getcwd(), INIFILE)
		print(self.inifile)
		self.section = "shapeoko"

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
						self.ipaddr = value
					elif opt == 'user':
						self.user = value
					elif opt == 'password':
						if value == "None":
							self.password == None
						else:
							self.password = value
					else:
						print("Unknown option in ini file: %s - ignoring" % opt)
			else:
				print("Section %s missing from ini file %s - using default values" % (self.section, INIFILE))
				self.modified = True
				self.save()

		if self.password is None:
			self.derivedPassword = getPasswordFromFile(".password")
		else:
			self.derivedPassword = self.password

	
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
		
		self.cfg.set(self.section, "ipaddr", str(self.ipaddr))
		self.cfg.set(self.section, "user", str(self.user))

		if self.password is None:
			pval = "None"
		else:
			pval = self.password
		self.cfg.set(self.section, "password", pval)

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False
