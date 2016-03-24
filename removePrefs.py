import os, platform, sys, shutil


class removePrefs:
	def __init__(self, jootaLocation,footwearPath):
		self.prefs = ''
		self.prefsPath = ''
		self.jootaDir = ''
		self.dirPath = ''
		self.footwearPath = ''
		self.settingsPath = ''
		self.prefsList = []
		self.user = os.path.expanduser("~")
		self.localOS = platform.system()
		self.jootaLocation = jootaLocation
		self.footwearPath = footwearPath
		self.jootaDir = 'Joota'


	def delete(self):
		#Windows 
		if self.localOS == 'Windows':
			self.prefs = 'JOOTA901.CFG'
			self.prefsPath = '{}\AppData\Roaming\Luxology\{}'.format(self.user, self.prefs)
			self.prefsList.append(self.prefsPath)

			if self.footwearPath != '':
				self.settingsPath = '{}\Settings\Modo\mAdiGlobalSettings.py'.format(self.footwearPath)
				self.prefsList.append(self.settingsPath)

			self.dirPath = '{}\AppData\Roaming\Luxology\{}'.format(self.user, self.jootaDir)
		#Mac
		elif self.localOS == 'Darwin' or self.localOS == 'MacOS':
			self.prefs = ['com.luxology.joota.plist', 'com.luxology.joota901','com.luxology.joota_cl904','com.luxology.joota904',
							'com.luxology.modo901','com.luxology.modo902','com.luxology.modo903','com.luxology.modo904','com.luxology.modo.plist']

			# append filepath strings to a list for deletion
			for pref in self.prefs:
				self.prefsPath = '{}/Library/Preferences/{}'.format(self.user, pref)
				self.prefsList.append(self.prefsPath)

			if self.footwearPath != '':
				self.settingsPath = '{}/mAdiGlobalSettings.py'.format(self.footwearPath)
				self.prefsList.append(self.settingsPath)

			self.dirPath = '{}/Library/Preferences/{}'.format(self.user, self.jootaDir)


		#Delete Prefs stored in the list
		for eachPref in self.prefsList:
			if os.path.exists(eachPref):
				os.remove(eachPref)
				
		if os.path.exists(self.dirPath):
			shutil.rmtree(self.dirPath)

		# print ('Deleted Preferences') 

if __name__ == "__main__":
    removePrefs = removePrefs()
    removePrefs.delete()