"""
Created on Oct 6, 2018

@author: Jeff
"""
import os
import json

class Settings:
	def __init__(self, d):
		self.fn = os.path.join(d, 'settings.json')
		try:
			with open(self.fn) as jfp:
				self.settings = json.load(jfp)
		except (FileNotFoundError, PermissionError):
			print("Unable to open settings json file")
			self.settings = {}
			
	def setting(self, key):
		if key in self.settings:
			return self.settings[key]
		
		return None
	
	def setSetting(self, key, val):
		self.settings[key] = val
		self.saveSettings()
		
	def saveSettings(self):
		try:
			with open(self.fn, 'w') as f:
				f.write(json.dumps(self.settings, indent=2))
				print("Settings saved to file '%s'" % self.fn)
				return True

		except IOError:
			print("Cannot write settings file '%s'." % self.fn)
			return False
