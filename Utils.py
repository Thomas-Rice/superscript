import os,shutil,subprocess

class Utils:
	def __init__(self,jootaLocation):	
		self.jootaLocation = jootaLocation



	def createLicense(self, buildNumber):
		'''
			Create a license for the current build
		'''


		# Change directory to the license generation folder
		os.chdir(self.jootaLocation + 'Licensing/licgen/')
		# Creates a variable for running the license tool
		self.fLicrun = self.jootaLocation + 'Licensing/licgen/licgen.sh'
		self.buildNumber = buildNumber
		# Runs the license tool with the build number as a parameter
		subprocess.call([self.fLicrun, self.buildNumber])

		# Moves the license from the project folder to the selected destination
		shutil.move(self.jootaLocation + 'Licensing/licgen/' + 'joota{}.lic'.format(self.buildNumber), self.jootaLocation + 'Licensing/Joota_Licenses' + '/' + 'joota{}.lic'.format(self.buildNumber))

	def retrieveFromJenkins(self,buildType,userDefinedBuildNumber = None,version = None):
		import urllib



		os.chdir(self.jootaLocation)


		if buildType == 'Stable':
			address = 'http://jenkinsii:8080/job/Joota_901stable/lastSuccessfulBuild/FnMachineSpec=meerman,FnOptType=release,FnProductLabel=Joota/artifact/Archive.tgz'
			self.fileName = 'Stable_Archive.tgz'
		if buildType == 'Dev':
			address = 'http://jenkinsii:8080/job/Joota_901dev/lastSuccessfulBuild/FnMachineSpec=meerman,FnOptType=release,FnProductLabel=Joota//artifact/Archive.tgz'
			self.fileName = 'Dev_Archive.tgz'

		if buildType == 'Specific': 
			address = 'http://jenkinsii:8080/job/Joota_901{}/{}/FnMachineSpec=meerman,FnOptType=release,FnProductLabel=Joota/artifact/Archive.tgz'.format(version,userDefinedBuildNumber)
			self.fileName = '{}_Archive.tgz'.format(version)

		else:
			print ' no buildType'

		print 'Archive Files is....' +self.fileName

		#Delete Old Archives in this folder in order to make sure there is only one.
		if os.path.exists(self.jootaLocation + self.fileName):
			os.remove(self.jootaLocation + self.fileName)
			# print 'deleted old archive.tgz'
		else:
			pass

		lastSuccessfulBuild = urllib.URLopener()
		lastSuccessfulBuild.retrieve(address, self.fileName)

	def get_file_size(self,buildType,userDefinedBuildNumber = None,version = None):
		import urllib

		if buildType == 'Stable':
			self.address = 'http://jenkinsii:8080/job/Joota_901stable/lastSuccessfulBuild/FnMachineSpec=meerman,FnOptType=release,FnProductLabel=Joota/artifact/Archive.tgz'

		if buildType == 'Dev':
			self.address = 'http://jenkinsii:8080/job/Joota_901dev/lastSuccessfulBuild/FnMachineSpec=meerman,FnOptType=release,FnProductLabel=Joota//artifact/Archive.tgz'

		if buildType == 'Specific':
			self.address = 'http://jenkinsii:8080/job/Joota_901{}/{}/FnMachineSpec=meerman,FnOptType=release,FnProductLabel=Joota/artifact/Archive.tgz'.format(version,userDefinedBuildNumber)


		site = urllib.urlopen(self.address)
		meta = site.info()
		fileSize =  meta.getheaders("Content-Length") 
		return fileSize




	def getFolderList(self,buildType):

		''' 
			Search through your builds folder and populate a list so that the dropdown box has Content
		'''

		if buildType == 'Stable':
			self.folderPath = self.jootaLocation +'/Joota_Builds/Stable_Builds'
			self.Type = 'Stable'
		if buildType == 'Dev':
			self.folderPath = self.jootaLocation +'/Joota_Builds/Dev_Builds'
			self.Type = 'Dev'
		if buildType == 'Integration':

			self.folderPath = self.jootaLocation +'/Joota_Builds/Integration_Builds'
			self.Type = 'Integration'	


		if not os.path.exists(self.folderPath):
			os.makedirs(self.folderPath)
		else:
			pass

		# Empty the list
		self.buildList = []
		# loop through all the folders within the folder Joota_Downloads and append them to the list self.buildList
		for file in os.listdir(self.folderPath):
			if file == '.DS_Store':
				pass
			else:
				self.buildList.append(file)

		print self.buildList.sort(key = lambda x: os.stat(os.path.join(self.folderPath, x)).st_mtime)

		# for item in self.buildList:
		# 	print item

		return self.buildList

	def runBuild(self,buildType,build):

		if buildType == 'Stable':
			self.JootaCrashReportPath = self.jootaLocation + 'Joota_Builds/Stable_Builds/' + build + '/joota.app/Contents/MacOS/joota'
			# print self.JootaCrashReportPath
		if buildType == 'Dev':
			self.JootaCrashReportPath = self.jootaLocation + 'Joota_Builds/Dev_Builds/'  + build + '/joota.app/Contents/MacOS/joota'
			# print self.JootaCrashReportPath
		if buildType == 'Integration':
			self.JootaCrashReportPath = self.jootaLocation + 'Joota_Builds/Integration_Builds/'  + build + '/joota.app/Contents/MacOS/joota'
			# print self.JootaCrashReportPath
		

		# Create the extension beacuse subprocess says so.... 
		extension = '-dboff:crashreport'
		#Run Joota with crash report 
		subprocess.Popen([self.JootaCrashReportPath, extension])	


