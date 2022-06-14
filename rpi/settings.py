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
					print("poll interval: %f" % self.pollinterval)
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

		try:		
			cfp = open(self.inifile, 'w')
		except:
			print("Unable to open settings file %s for writing" % self.inifile)
			return
		self.cfg.write(cfp)
		cfp.close()
		
		self.modified = False
