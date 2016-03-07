import os,shutil
from Utils import *

class jenkinsBuild:
	def __init__(self, jootaLocation, buildType,integrationLocation = None):

		self.jootaLocation = jootaLocation
		self.buildNumber = ''

		if buildType == 'Stable':
			self.archive_file = 'Stable_Archive.tgz'
			self.tmpFolder = self.jootaLocation + 'Joota_Builds/Stable_Builds/tmp'
			self.Type = 'Stable'

		if buildType == 'Dev':
			self.archive_file = 'Dev_Archive.tgz'
			self.tmpFolder = self.jootaLocation + 'Joota_Builds/Dev_Builds/tmp'
			self.Type = 'Dev'

		if buildType == 'Integration':
			self.archive_file = 'Specific_Archive.tgz'
			self.tmpFolder = self.jootaLocation + 'Joota_Builds/Integration_Builds/tmp'
			self.Type = 'Integration'






	def stableMoveAndExtract(self):	
		import tarfile	
		buildPath = self.jootaLocation + 'Joota_Builds/' + self.Type + '_Builds/'

		#Delete Any pre exisitng tmp folders
		if os.path.exists(self.tmpFolder):
			#delete new folder as you already have the build
			shutil.rmtree(self.tmpFolder, ignore_errors=True)
		else:
			pass


		if os.path.exists(self.jootaLocation + self.archive_file):
			#Make Stable folder to put archive in
			os.makedirs( self.tmpFolder);
			#Move the .tgz to the new folder
			shutil.move(self.jootaLocation +  self.archive_file, (self.tmpFolder))
			#Change to the directory
			os.chdir(self.tmpFolder)
			#open the .tgz file
			self.tfile = tarfile.open(self.archive_file)
			#extract all
			self.tfile.extractall()
			#close the operation (i think??)
			self.tfile.close()


			#Get the build number from the plist in the extracted Joota app in order to rename the folder
			self.buildNumber = self.getBuildNumber()


			newFolderPath = buildPath + self.Type +'_' + self.buildNumber

			if self.checkIfExists(newFolderPath):
				pass
			else:
				# #Move back into the folder directory so we can rename it to that of the build number
				os.chdir(self.jootaLocation)
				#Rename the folder from stable to stable_buildName
				os.rename(self.tmpFolder , newFolderPath)

				licenseObject = Utils(self.jootaLocation)
				licenseObject.createLicense(self.buildNumber)

				# print 'Unpacked your build'

		else:
			# #If the file does not exist in your downloads then print out this message on the Gui
			# print("No compressed file with the name \" Archive.tgz \" in your downloads directory...No action taken ")
			pass

		return self.buildNumber

	def integrationMoveAndExtract(self,filePath,folderName):

		compressionType = filePath[-4:]

		buildPath = self.jootaLocation + 'Joota_Builds/Integration_Builds'
		self.fileName = os.path.basename(filePath)
		self.newFolderPath = buildPath + '/' + folderName
		if os.path.exists(self.newFolderPath):
			if len(self.newFolderPath) >0:
				emptyFolder = os.listdir(self.newFolderPath)
				if len(emptyFolder) == 0:
					shutil.rmtree(self.newFolderPath, ignore_errors=True)
				if len(emptyFolder) == 1 and emptyFolder[0] == '.DS_Store':
					shutil.rmtree(self.newFolderPath, ignore_errors=True)
				else: 
					pass
			else:
				pass
		else:
			pass
		#Make Stable folder to put archive in
		os.makedirs( self.newFolderPath );

		shutil.move(filePath, (self.newFolderPath))
		#Change to the directory
		os.chdir(self.newFolderPath )

		if compressionType == '.zip':
			subprocess.call(['unzip', self.fileName])	
		if compressionType == '.tgz':
			import tarfile	
			self.file = tarfile.open(self.fileName)
			#extract all
			self.file.extractall()
			#close the operation (i think??)
			self.file.close()

	def resetPath(self):

		self.fileName = ''
		self.newFolderPath = ''






	def checkIfExists(self,newFolderPath):
		#If the folder already exists (this program has been run on this day) then it will not create a new folder.
		if os.path.exists(newFolderPath):
			#Move the archive out of the location so it doesn't get deleted
			shutil.move((self.tmpFolder + "/" + self.archive_file), self.jootaLocation)	
			#delete new folder as you already have the build
			shutil.rmtree(self.tmpFolder, ignore_errors=True)
			# os.remove(self.tmpFolder)
			# print("You already have this build extracted in the correct place .... make sure that you're using the correct Archive.tgz")

			return True
		else:

			return False

	def getBuildNumber(self):
		import plistlib
		'''
			Reads the PList from the Joota build to determine the build number
		'''
		# Reads the plist build file an stores it in a dict
		self.my_plist = plistlib.readPlist(self.jootaLocation + 'Joota_Builds/'+ self.Type + '_Builds/tmp/joota.app/Contents/info.plist')
		# Searches through the dict for the CFBundleShortVersionString entry
		self.buildString = self.my_plist["CFBundleShortVersionString"]
		# Slices the line to the build number and removes the final character and stores it in the buildNumber variable
		self.buildNumber = self.buildString[4:-1]

		# print ('new folder build name is', self.buildNumber)
		return self.buildNumber









if __name__ == "__main__":
	Stable = jenkinsBuild()
	Stable.retrieveFromJenkins()

