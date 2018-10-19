'''
Created on Sep 9, 2018

@author: Jeff
'''
import os
import configparser

INIFILE = "presets.ini"

class Presets:
	def __init__(self, folder):
		self.presetList = {}
		self.inifile = os.path.join(folder, INIFILE)
		
		self.cfg = configparser.ConfigParser()
		self.cfg.optionxform = str
		if not self.cfg.read(self.inifile):
			#print("presets file %s does not exist.  skipping..." % self.inifile)
			return
		
		for sect in self.cfg.sections():
			sectPresets = {}
			for opt, value in self.cfg.items(sect):
				sectPresets[opt] = value
				#print("%s:%s = %s" % (sect, opt, value))
				
			self.presetList[sect] = sectPresets

		
	def getPresetList(self):
		return self.presetList