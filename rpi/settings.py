import os
import configparser

INIFILE = "shapeoko.ini"

class Settings:
	def __init__(self):
		# first assign default values
		self.ttyshapeoko = "/dev/ttyACM0"
		self.ttypendant = "/dev/ttyUSB0"
		self.datadir = os.path.join(os.getcwd(), "shapeokodata")
		self.pollinterval = 0.5

		self.ipaddr = "shapeoko.local"
		self.port = 9000

		self.probeheight = 6.35


		self.inifile = os.path.join(os.getcwd(), INIFILE)
		self.section = "shapeoko"

		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			print("Settings file %s does not exist.  Using default values" % INIFILE)
			
			self.modified = True
			return

		self.modified = False	
		if self.cfg.has_section(self.section):
			for opt, value in self.cfg.items(self.section):
				if opt == 'ttyshapeoko':
					self.ttyshapeoko = value
				elif opt == 'ttypendant':
					self.ttypendant = value
				elif opt == 'datadir':
					self.datadir = value
				elif opt == "pollinterval":
					try:
						pi = float(value)
					except:
						pi = self.pollinterval
					self.pollinterval = pi
				elif opt == 'ipaddr':
					self.ipaddr = value
				elif opt == "port":
					try:
						p = int(value)
					except:
						p = self.port
					self.pollinterval = pi
				elif opt == "probeheight":
					try:
						ph = float(value)
					except:
						ph = self.probeheight
					self.probeheight = ph
				else:
					print("Unknown option in ini file: %s - ignoring" % opt)
		else:
			print("Section %s missing from ini file %s - using default values" % (self.section, INIFILE))
			self.modified = True
			return
	
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
		
		self.cfg.set(self.section, "ttyshapeoko", str(self.ttyshapeoko))
		self.cfg.set(self.section, "ttypendant", str(self.ttypendant))
		self.cfg.set(self.section, "datadir", str(self.datadir))
		self.cfg.set(self.section, "pollinterval", "%.3f" % self.pollinterval)
		self.cfg.set(self.section, "ipaddr", str(self.ipaddr))
		self.cfg.set(self.section, "port", "%d" % self.port)
		self.cfg.set(self.section, "probeheight", "%.3f" % self.probeheight)

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False
