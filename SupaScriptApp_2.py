#!/opt/local/bin/python

import sys,json,time

from Utils import *
from removePrefs import *
from jenkinsBuild import *


from PySide import QtCore, QtGui

# class CustomButton(QtGui.QPushButton):
# 	def __init__(self, color, name, parent = None):
# 		super(CustomButton, self).__init__(name, parent)
# 		self.color = color
# 		self.setStyleSheet("background-color: red")

# class CustomTab(QtGui.QTabWidget):
# 	def __init__(self, color, name, parent = None):
# 		super(CustomTab, self).__init__(parent)
# 		self.color = color
# 		self.setStyleSheet("QTabWidget::pane {border: 1px solid red;top: -1px;}")

# 		# self.setStyleSheet("QTabBar::tab {color: red;}")


class StableDevTab(QtGui.QWidget):
	def __init__(self,styleData,buildType,guiUtilsObject):
		super(StableDevTab, self).__init__()
		
		self.buildType = buildType
		self.styleData = styleData
		self.buildNumber = ''
		self.guiUtilsObject = guiUtilsObject

		self.stableBtn = QtGui.QPushButton('Get Build', self)
		self.stableBtn.setToolTip('Retrieves the {} build from jenkins and unpacks it'.format(self.buildType))
		self.stableBtn.resize ( 150 , 80)
		self.stableBtn.clicked.connect(self.clickGetBuild)
		self.stableBtn.move(15, 15)

		self.instance = guiUtilsObject

		self.pbar = QtGui.QProgressBar(self)
		self.pbar.setGeometry(110, 220, 200, 25)
		self.pbar.hide()


		self.fileLbl = QtGui.QLabel('Build Folder', self)
		self.fileLbl.move(53, 110)


		self.fileCombo = QtGui.QComboBox(self)
		self.refreshComboBox()
		self.fileCombo.move(15, 125)
		self.fileCombo.resize(150,25)
		self.fileCombo.setMaxCount(40)
		self.fileCombo.activated[str].connect(self.returnSelection)



		self.runBtn = QtGui.QPushButton('Run!', self)
		self.runBtn.setToolTip('Run the selected build')
		self.runBtn.resize ( 200 , 150)
		self.runBtn.clicked.connect(self.runClicked)
		self.runBtn.move(200, 10)


		self.deltePrefsBtn = QtGui.QPushButton('Delete Preferences', self)
		self.deltePrefsBtn.setToolTip('Delete all Joota Preferences')
		self.deltePrefsBtn.clicked.connect(self.deletePrefs)
		self.deltePrefsBtn.resize(280,40) 
		self.deltePrefsBtn.move(70, 170)


		self.messageLbl = QtGui.QLabel('', self)
		self.messageLbl.setStyleSheet("color: #ffa02f;padding: 3px")
		self.messageLbl.move(145, 225)
		self.messageLbl.resize(150,20)


		self.cancelBtn = QtGui.QPushButton('Cancel Download', self)
		self.cancelBtn.setStyleSheet("font-size:12px;background-color:red;border: 2px solid #222222")
		self.cancelBtn.resize(20,20)
		self.cancelBtn.setText('x')
		self.cancelBtn.clicked.connect(self.cancel)
		self.cancelBtn.move(315, 222)
		self.cancelBtn.hide()


	def cancel(self):
		self.workThread.terminate()
		self.workThread2.terminate()
		self.pbar.hide()
		self.messageLbl.setText('Downloading Cancelled')
		self.threadCreated = False
		self.stableBtn.setEnabled(True)
		self.cancelBtn.hide()





	def downloaded(self):
		self.cancelBtn.hide()
		self.stableBtn.setEnabled(True)
		self.messageLbl.resize(150,20)
		self.messageLbl.move(145, 225)
		self.messageLbl.show()



		QtGui.QApplication.processEvents()
		self.refreshComboBox()



	def error(self,text):
		self.cancelBtn.hide()
		self.messageLbl.clear()
		self.eWindow = errorWidow(text)
		self.eWindow.show()
		self.messageLbl.clear()

	def clickGetBuild(self):
		self.cancelBtn.show()
		self.messageLbl.setText('Downloading Build \n      Please Wait')
		self.messageLbl.resize(150,40)
		self.messageLbl.move(145, 210)
		self.messageLbl.show()

		self.workThread = _Download_From_Jenkins_Thread(self.buildType,self.guiUtilsObject,None)
		self.workThread.message.connect(self.finished)
		self.workThread.download_fail.connect( lambda text = "         Download Failed\n    Check Your Connection": self.error(text))




		self.workThread2 = _FileSize_Thread(self.guiUtilsObject,self.buildType)
		self.workThread2.mb.connect(self.progress_bar_update)
		self.workThread2.set_total_size.connect(self.set_progress_bar)


		self.connect(self.workThread, QtCore.SIGNAL('finished()'), self.downloaded)



		self.workThread.start()
		self.workThread2.start()

		self.stableBtn.setEnabled(False)
		QtGui.QApplication.processEvents()


	def refreshComboBox(self):
		self.fileCombo.clear()
		self.returnedList =self.instance.populateList(self.buildType)
		for items in self.returnedList:
			self.fileCombo.addItem(items)
		#Clear the combobox selection to avoid confusion
		self.fileCombo.setCurrentIndex(-1)




		
	def returnSelection(self):
		# self.greenBtn.setStyleSheet("font-size:12px;background-color:#565656;border: 2px solid #222222")
		QtGui.QApplication.processEvents()
		self.messageLbl.clear()
		self.text = str(self.fileCombo.currentText())

	def runClicked(self):
		try:
			self.messageLbl.clear()
			self.instance.runBuild(self.buildType, self.text)
		except:
			self.eWindow = errorWidow("No Build Is Selected Please \nSelect A Build And Try Again")
			self.eWindow.setStyleSheet(self.styleData)
			self.eWindow.show()
		
	def deletePrefs(self):

		self.instance.deletePrefs()
		self.messageLbl.setText('Deleted Preferences')
		self.messageLbl.show()

	def set_progress_bar(self):

		self.total_file_size = self.workThread2.filesize
		print 'total_file_size of %s is %f' %(self.buildType, self.total_file_size)
		self.pbar.setRange(0,self.total_file_size)


	def progress_bar_update(self,text):

		self.pbar.show()
		self.messageLbl.hide()
		text1 = float(text[:-4])
		self.pbar.setValue(text1)
		# print (self.buildType + ' downloaded this much .. ' + str(text1))

		if text1 == self.total_file_size:
			self.pbar.hide()
			self.messageLbl.setText('Processing Build \n    Please Wait')
			self.messageLbl.show()
		else:
			pass


	def finished(self,text):
		self.cancelBtn.hide()
		self.pbar.hide()
		time.sleep(1.3)
		self.messageLbl.setText(text)
		



class _Download_From_Jenkins_Thread(QtCore.QThread):
	message = QtCore.Signal(str)
	download_fail = QtCore.Signal()
	download_cancel = QtCore.Signal()
	def __init__(self,buildType,guiUtilsObject, userDefinedBuildNumber = None ):
		QtCore.QThread.__init__(self)
		self.buildType = buildType
		self.instance = guiUtilsObject
		self.userDefinedBuildNumber = userDefinedBuildNumber


		# if userDefinedBuildNumber != None:
		# 	self.userDefinedBuildNumber = userDefinedBuildNumber
		# else:
		# 	self.userDefinedBuildNumber = None



	def run(self):
		try:
			if self.userDefinedBuildNumber != None:
				buildNumber = self.instance.getSpecific(self.buildType,self.userDefinedBuildNumber)
				self.buildMessage = ('   Build {} ready'.format(buildNumber))
			else:
				buildNumber = self.instance.getBuild(self.buildType)
				self.buildMessage = ('   Build {} ready'.format(buildNumber))

			self.message.emit(self.buildMessage)
		except IOError:
			# print 'nooo'
			self.download_fail.emit()





class _FileSize_Thread(QtCore.QThread):
	set_total_size = QtCore.Signal()
	mb = QtCore.Signal(str)
	fail = QtCore.Signal()

	def __init__(self,guiUtilsObject,buildType,buildNumber = None):
		QtCore.QThread.__init__(self)
		self.buildType = buildType
		self.instance = guiUtilsObject
		self._filesize = 0
		self.buildNumber = buildNumber
		print self.buildType + ' Thread Created'

		if buildType == 'Stable':
			self.archive_file = 'Stable_Archive.tgz'
		if buildType == 'Dev':
			self.archive_file = 'Dev_Archive.tgz'
		# if self.buildNumber != None:
		# 	self.archive_file = 'Specific_Archive.tgz'



	@property
	def filesize(self):
		value = self.sizeof_fmt(self._filesize)
		self.final_value = float(value[:-4])
		return self.final_value


	def run(self):
		try:
			filesize = 0
			time.sleep(1.3)
			if self.buildNumber != None:
				self._filesize = self.instance.get_file_size('Specific',self.buildNumber,self.buildType)
			else:
				self._filesize = self.instance.get_file_size(self.buildType)
				print self.buildType + 'total_file_size is ' + str(self.filesize)
			
			self.set_total_size.emit()
			while filesize != self._filesize:
				filesize = (os.stat(self.archive_file).st_size)
				readableFileSize = self.sizeof_fmt(filesize).strip()
				time.sleep(0.3) # artificial time delay
				self.mb.emit(readableFileSize)
				print (self.buildType + ' downloaded this much .. ' + str(readableFileSize))
			print self.buildType + ' Thread Stopped'

			# for i in range(1, 101):


		except:
			self.fail.emit()



	def sizeof_fmt(self, num, suffix='B'):
	    for unit in ['',' Ki',' Mi',' Gi',' Ti',' Pi',' Ei',' Zi']:
	        if abs(num) < 1024.0:
	            return "%3.1f%s%s" % (num, unit, suffix)
	        num /= 1024.0
	    return "%.1f%s%s" % (num, 'Yi', suffix)







class Integration(QtGui.QWidget):
	def __init__(self,styleData,guiUtilsObject):
		super(Integration, self).__init__()

		self.styleData = styleData
		self.integrationBtn = QtGui.QPushButton('Choose Build', self)
		self.integrationBtn.setToolTip('Enter Details and Unpack Integration build')
		self.integrationBtn.resize ( 150 , 80)
		self.integrationBtn.clicked.connect(self.openNonJenkinsBuildWindow)
		self.integrationBtn.move(15, 15)


		self.instance = guiUtilsObject


		self.fileLbl = QtGui.QLabel('Build Folder', self)
		self.fileLbl.move(53, 110)

		self.fileCombo = QtGui.QComboBox(self)
		self.refreshComboBox()
		self.fileCombo.move(15, 125)
		self.fileCombo.resize(150,25)
		self.fileCombo.setMaxCount(20)

		self.fileCombo.activated[str].connect(self.returnSelection)


		self.runBtn = QtGui.QPushButton('Run!', self)
		self.runBtn.setToolTip('Run the selected build')
		self.runBtn.resize ( 200 , 150)
		self.runBtn.clicked.connect(self.runClicked)
		self.runBtn.move(200, 10)

		self.deltePrefsBtn = QtGui.QPushButton('Delete Preferences', self)
		self.deltePrefsBtn.setToolTip('Delete all Joota Preferences')
		self.deltePrefsBtn.clicked.connect(self.deletePrefs)
		self.deltePrefsBtn.resize(280,40) 
		self.deltePrefsBtn.move(70, 170)

		self.messageLbl = QtGui.QLabel('', self)
		self.messageLbl.setStyleSheet("color: #ffa02f;padding: 3px")
		self.messageLbl.move(145, 225)
		self.messageLbl.resize(150,20)


	def openNonJenkinsBuildWindow(self):
		self.jWindow = nonJenkinsWindow(self.instance,self.styleData)
		self.jWindow.setStyleSheet(self.styleData)
		self.jWindow.show()
		if self.jWindow.exec_():
			pass
		else:
			self.refreshComboBox()
			QtGui.QApplication.processEvents()



	def refreshComboBox(self):
		self.fileCombo.clear()
		self.returnedList =self.instance.populateList('Integration')
		for items in self.returnedList:
			self.fileCombo.addItem(items)
		self.fileCombo.setCurrentIndex(-1)
		
	def returnSelection(self):
		self.text = str(self.fileCombo.currentText())

	def runClicked(self):
		try:
			self.instance.runBuild('Integration', self.text)
		except:
			self.eWindow = errorWidow("      No Build Is Selected\nSelect A Build And Try Again")
			self.eWindow.setStyleSheet(self.styleData)
			self.eWindow.show()

	def deletePrefs(self):

		self.instance.deletePrefs()
		self.messageLbl.setText('Deleted Preferences')
		self.messageLbl.show()







class UtilsTab(QtGui.QWidget):
	def __init__(self,styleData,basePath,globalSettingsPath,guiUtilsObject):
		super(UtilsTab, self).__init__()
		self.globalSettingsPath = globalSettingsPath
		self.basePath = basePath
		self.styleData = styleData
		self.specificBuildBtn = QtGui.QPushButton('Get Specific Build', self)
		self.specificBuildBtn.setToolTip('Download A Specific Build From Jenkins')
		self.specificBuildBtn.clicked.connect(self.openSpecificBuildWindow)
		self.specificBuildBtn.move(10, 40)
		self.specificBuildBtn.resize(200,150)

		self.specificLicenseBtn = QtGui.QPushButton('Generate Specific License', self)
		self.specificLicenseBtn.setToolTip('Generate A Specific License For Any Build')
		self.specificLicenseBtn.clicked.connect(self.generateLicense)
		self.specificLicenseBtn.move(210,40)
		self.specificLicenseBtn.resize(200,150)

		self.guiUtilsObject = guiUtilsObject




	def openSpecificBuildWindow(self):
		self.sWindow = specificBuildWindow(self.styleData,self.basePath,self.globalSettingsPath,self.guiUtilsObject)
		self.sWindow.setStyleSheet(self.styleData)
		self.sWindow.show()


	def generateLicense(self):
		self.gWindow = generateLicenseWindow(self.basePath,self.globalSettingsPath,self.styleData)
		self.gWindow.setStyleSheet(self.styleData)
		self.gWindow.show()




class guiUtils():
	def __init__(self,basePath,globalSettingsPath):
		self.basePath = basePath
		self.globalSettingsPath = globalSettingsPath
		self.product_type = 'Joota'


		self.file_size = 0
		self.utilsObject = Utils(self.basePath)
		#self.removePrefsObject = removePrefs(self.basePath,self.globalSettingsPath)

	def deletePrefs(self):
		removePrefs(self.basePath,self.globalSettingsPath).delete()

	def populateList(self, type):

		folderList = self.utilsObject.getFolderList(type)
		if folderList == None:
			folderList = []
		else:
			pass

		return folderList


	def generateLicense(self,number):
		self.utilsObject.createLicense(number)
		# print 'license generated and in your licenses folder'



	def getBuild(self, buildType):
		self.utilsObject.retrieveFromJenkins(buildType)
		self.jenkinsObject = jenkinsBuild(self.basePath,buildType,self.product_type)
		self.buildNumber = self.jenkinsObject.stableMoveAndExtract()
		return self.buildNumber

	def getIntegration(self,filePath,folderName):
		self.jenkinsObject = jenkinsBuild(self.basePath,'Integration')
		self.newFolderPath = self.jenkinsObject.integrationMoveAndExtract(filePath,folderName)

	def getSpecific(self,buildType,userDefinedBuildNumber):
		self.utilsObject.retrieveFromJenkins('Specific',userDefinedBuildNumber,buildType)
		self.jenkinsObject = jenkinsBuild(self.basePath,buildType,,self.product_type)
		self.newFolderPath = self.jenkinsObject.stableMoveAndExtract()

	def runBuild(self,type,path):
		self.utilsObject.runBuild(type,path)	

	def resetPath(self):
		self.newFolderPath.resetPath()


	def get_file_size(self,buildType,userDefinedBuildNumber =None,version = None):
		if buildType != 'Specific':
			filesize = self.utilsObject.get_file_size(buildType)
		else:
			filesize = self.utilsObject.get_file_size('Specific',userDefinedBuildNumber, version)

		self.file_size = int(filesize[0])
		return self.file_size




class nonJenkinsWindow(QtGui.QDialog):
	def __init__(self,guiUtilsObject,styleData):
		super(nonJenkinsWindow, self).__init__()
		self.styleData = styleData
		self.chosenFile  = ''
		self.folderName = ''
		# Non Jenkins build window
		self.resize(300, 250)
		self.setWindowTitle('Non Jenkins Build')

		self.lbl = QtGui.QLabel('Enter desired folder name', self)
		self.lbl.setStyleSheet("color:#ffa02f;")
		self.lbl.resize(150,20)
		self.lbl.move(75, 10)
		self.instance = guiUtilsObject


		self.line_edit = QtGui.QLineEdit(self)
		self.line_edit.move(100,30)
		self.line_edit.resize(100, 20)
		self.line_edit.textChanged.connect(self.folderNameInputChanged)
		


		self.lbl2 = QtGui.QLabel('Choose Zip file containing build', self)
		self.lbl2.setStyleSheet("color:#ffa02f;")
		self.lbl2.move(60, 60)


		self.fileSelection = QtGui.QPushButton('Choose File', self)
		self.fileSelection.clicked.connect(self.Open)
		self.fileSelection.resize(100, 25)
		self.fileSelection.move(100, 80)

		self.line_edit2 = QtGui.QLineEdit(self)
		self.line_edit2.move(25,110)
		self.line_edit2.resize(250,20)
		self.line_edit2.textChanged.connect(self.fileNameInputChanged)


		self.submit = QtGui.QPushButton('Submit', self)
		self.submit.clicked.connect(self.submitAndExtract)
		self.submit.move(112.5, 135)
		self.submit.resize(75,40)

		self.messageLbl = QtGui.QLabel('', self)
		self.messageLbl.setStyleSheet("color: #ffa02f;padding: 3px")
		self.messageLbl.move(5, 180)
		self.messageLbl.resize(290,60)


	def folderNameInputChanged(self, text):
		self.folderName =  str(text)

	def fileNameInputChanged(self, text):
		self.chosenFile  =  str(text)

	def submitAndExtract(self):
		startCheck = self.folderName[:1] 

		if self.chosenFile == '':
			self.eWindow = errorWidow("      No File Is Selected\nSelect A File And Try Again")
			self.eWindow.setStyleSheet(self.styleData)
			self.messageLbl.clear()
			self.eWindow.show()
		if self.folderName == '':
			self.eWindow = errorWidow("      No Folder Name Is Given\nSpeify A Name And Try Again")
			self.eWindow.setStyleSheet(self.styleData)
			self.messageLbl.clear()
			self.eWindow.show()
		if len(self.folderName) >=254:
			self.eWindow = errorWidow("     File Name Too Long\n          Blame Apple....")
			self.eWindow.setStyleSheet(self.styleData)
			self.messageLbl.clear()
			self.eWindow.show()
		if startCheck == '.':
			self.eWindow = errorWidow(" Sorry You Are Not Allowed\n            To Use The . \nTo Prefix Your Folder Name")
			self.eWindow.setStyleSheet(self.styleData)
			self.messageLbl.clear()
			self.eWindow.show()
		if ':' in self.folderName :
			self.eWindow = errorWidow(" Sorry You Are Not Allowed\n            To Use The : \nWithin Your Folder Name")
			self.eWindow.setStyleSheet(self.styleData)
			self.messageLbl.clear()
			self.eWindow.show()
		else:
			try:
				self.messageLbl.setText('                        Unpacking Build\n                             Please Wait.\n  Window will close when operation is complete')
				self.messageLbl.show()
				QtGui.QApplication.processEvents()
				self.instance.getIntegration(self.chosenFile,self.folderName)
				self.close()
			except AttributeError:
				self.eWindow = errorWidow("    No Folder Name Entered\nSelect A Name And Try Again")
				self.eWindow.setStyleSheet(self.styleData)
				self.messageLbl.clear()
				self.eWindow.show()
			except NameError:
				self.eWindow = errorWidow("      No File Is Selected\nSelect A File And Try Again")
				self.eWindow.setStyleSheet(self.styleData)
				self.messageLbl.clear()
				self.eWindow.show()
			# except OSError:
			# 	self.eWindow = errorWidow("  Folder Name Already Exists")
			# 	self.eWindow.setStyleSheet(self.styleData)
			# 	self.messageLbl.clear()
			# 	self.eWindow.show()
			# except:
			# 	self.eWindow = errorWidow("   Something Went Wrong\n       Please Try Again")
			# 	self.eWindow.setStyleSheet(self.styleData)
			# 	self.messageLbl.clear()
			# 	self.eWindow.show()



	def Open(self):
		fname, _ = QtGui.QFileDialog.getOpenFileName(self, 'Open file')
		self.line_edit2.setText(fname)
		self.chosenFile = str(fname)




class specificBuildWindow(QtGui.QDialog):
	def __init__(self,styleData,basePath,globalSettingsPath,guiUtilsObject):
		super(specificBuildWindow, self).__init__()

		self.option = 'Stable'
		self.styleData = styleData
		self.buildNumber = ''
		# Non Jenkins build window 
		self.resize(300, 340)
		self.setWindowTitle('Specific Build From Jenkins')

		self.lbl1 = QtGui.QLabel('Choose Dev or Stable', self)
		self.lbl1.setStyleSheet("color:#ffa02f;")
		self.lbl1.move(87, 25)

		self.instance = guiUtils(basePath,globalSettingsPath)

		self.pbar = QtGui.QProgressBar(self)
		self.pbar.setGeometry(50, 240, 200, 25)
		self.pbar.hide()

		combo = QtGui.QComboBox(self)
		combo.addItem('Stable')
		combo.addItem('Dev')
		combo.resize(100,25)
		combo.move(100, 45)
		combo.activated[str].connect(self.comboBoxActivation)
		combo.setCurrentIndex(-1)
		


		self.lbl2 = QtGui.QLabel('Enter a build number', self)
		self.lbl2.setStyleSheet("color:#ffa02f;")
		self.lbl2.move(90, 80)

		self.line_edit = QtGui.QLineEdit(self)
		self.line_edit.move(100,100)
		self.line_edit.resize(100,20)
		self.line_edit.textChanged.connect(self.getBuildNumber)

		self.submitBtn = QtGui.QPushButton('Submit', self)

		self.submitBtn.resize(75,40)
		self.submitBtn.clicked.connect(self.submitAndExtract)
		self.submitBtn.move(115, 130)

		self.messageLbl = QtGui.QLabel('', self)
		self.messageLbl.setStyleSheet("color: #ffa02f;padding: 3px")
		self.messageLbl.move(5, 180)
		self.messageLbl.resize(290,60)

		self.threadCreated = False


		self.cancelBtn = QtGui.QPushButton('Cancel Download', self)

		self.cancelBtn.resize(120,40)
		self.cancelBtn.clicked.connect(self.cancel)
		self.cancelBtn.move(95, 275)


	def cancel(self):
		self.workThread.terminate()
		self.workThread2.terminate()
		self.pbar.hide()
		self.messageLbl.setText('                      Downloading Cancelled')
		self.threadCreated = False
		self.submitBtn.setEnabled(True)

	def closeEvent(self, event):

		if self.threadCreated:
			self.workThread.download_cancel.emit()
			event.ignore()
		else:
			pass


	def comboBoxActivation(self,option):
		self.option = option
			

	def getBuildNumber(self, text):
		self.buildNumber = str(text)


	def submitAndExtract(self):
		self.threadCreated = True
		self.workThread = _Download_From_Jenkins_Thread(self.option,self.instance,self.buildNumber)

		self.submitBtn.setEnabled(False)

		self.workThread2 = _FileSize_Thread(self.instance,self.option,self.buildNumber)
		self.workThread2.mb.connect(self.progress_bar_update)

		self.workThread.message.connect(self.finished)

		self.workThread.download_fail.connect( lambda text = "Incorrect Information Entered:\nThis Build Probably Does Not \n                  Exist": self.error(text))
		self.workThread.download_cancel.connect( lambda text = "Please Cancel The Download\n Before Closing This Window": self.error(text))


		self.messageLbl.setText('                        Downloading Build\n                             Please Wait.')
		self.messageLbl.show()
		QtGui.QApplication.processEvents()

		self.pbar.show()

		self.workThread.start()
		self.workThread2.start()
		self.workThread2.set_total_size.connect(self.set_progress_bar)

	def error(self,text):
		self.workThread.terminate()
		self.workThread2.terminate()
		self.pbar.hide()
		self.threadCreated = False
		self.submitBtn.setEnabled(True)
		self.messageLbl.clear()

		self.eWindow = errorWidow(text)
		self.eWindow.show()
		self.messageLbl.clear()



	def progress_bar_update(self,text):

		self.pbar.show()
		text1 = float(text[:-4])
		self.pbar.setValue(text1)

		if text1 == self.total_file_size:
			self.pbar.hide()
			self.messageLbl.setText((' '*25) +'Processing Build' +'\n' + (' '*29) + 'Please Wait')
			self.messageLbl.show()
		else:
			pass


	def finished(self,text):
		self.pbar.hide()
		time.sleep(1.3)
		self.messageLbl.setText('                          Build ' + self.buildNumber + ' Ready')
		self.submitBtn.setEnabled(True)
		time.sleep(1.3)
		self.threadCreated = False


	def set_progress_bar(self):

		self.total_file_size = self.workThread2.filesize
		self.pbar.setRange(0,self.total_file_size)





class generateLicenseWindow(QtGui.QDialog):
	def __init__(self,basePath,globalSettingsPath,styleData):
		super(generateLicenseWindow, self).__init__()

		self.resize(300, 200)
		self.setWindowTitle('Generate License')

		self.styleData = styleData

		self.instance = guiUtils(basePath,globalSettingsPath)
		

		self.lbl2 = QtGui.QLabel('Enter a build number', self)
		self.lbl2.setStyleSheet("color:#ffa02f;")
		self.lbl2.move(92, 40)

		self.line_edit = QtGui.QLineEdit(self)
		self.line_edit.resize(100,20)
		self.line_edit.move(100,60)
		self.line_edit.textChanged.connect(self.setBuildNumber)

		self.submitBtn = QtGui.QPushButton('Submit', self)
		self.submitBtn.resize(70,40)
		self.submitBtn.clicked.connect(self.submitClicked)
		self.submitBtn.move(115, 100)

		self.messageLbl = QtGui.QLabel('', self)
		self.messageLbl.setStyleSheet("color: #ffa02f;padding: 3px")
		self.messageLbl.move(80, 145)
		self.messageLbl.resize(150,40)

	def setBuildNumber(self, text):
		self.buildNumber = str(text)

	def submitClicked(self):
		try:
			self.instance.generateLicense(self.buildNumber)
			self.messageLbl.setText('Generated License for \n          Build {}'.format(self.buildNumber))
		except AttributeError:
			self.messageLbl.clear()
			self.eWindow = errorWidow("Please Select A Build Number")
			self.eWindow.setStyleSheet(self.styleData)
			self.eWindow.show()
			self.messageLbl.clear()

class errorWidow(QtGui.QDialog):
	def __init__(self,text):
		super(errorWidow, self).__init__()
		self.resize(200, 150)
		self.setWindowTitle('ERROR!!')
		self.errorLbl = QtGui.QLabel(text, self)
		self.errorLbl.setStyleSheet("color:#ff0000;")
		self.errorLbl.move(20, 40)

		self.OkBtn = QtGui.QPushButton('OK', self)
		self.OkBtn.clicked.connect(self.submitOkClicked)
		self.OkBtn.resize(40, 40)
		self.OkBtn.move(80, 90)

		styleSheetObject = styleSheet()
		styleData = styleSheetObject.returnSheet()

		self.setStyleSheet(styleData)

	def submitOkClicked(self):
		self.close()




class main():
	def __init__(self):
		self.app = QtGui.QApplication(sys.argv)
		self.app.setStyle("Cleanlooks")


		with open ("SupaScriptPaths.json", "r") as dictionary:
			readIn = json.load(dictionary)
			self.basePath = readIn['SupaScriptPath'] + '/'
			self.globalSettingsPath = readIn['globalSettingsPath'] +'/'
			# print self.basePath
			# print self.globalSettingsPath



		self.guiUtilsObject = guiUtils(self.basePath,self.globalSettingsPath)



		styleSheetObject = styleSheet()
		styleData = styleSheetObject.returnSheet()



		self.tabs = QtGui.QTabWidget()
		self.tab1 = StableDevTab(styleData,'Stable',self.guiUtilsObject)
		self.tab2 = StableDevTab(styleData,'Dev',self.guiUtilsObject) 
		self.tab3 = Integration(styleData,self.guiUtilsObject) 
		self.tab4 = UtilsTab(styleData,self.basePath,self.globalSettingsPath,self.guiUtilsObject) 
		self.tabs.addTab(self.tab1,"Stable")
		self.tabs.addTab(self.tab2,"Dev")
		self.tabs.addTab(self.tab3,"Integration")
		self.tabs.addTab(self.tab4,"Utils")
		self.tabs.setWindowTitle('SupaScript') 

		self.tabs.currentChanged.connect(self.refreshComboBoxFromSpecific)

		self.tabs.setStyleSheet(styleData)



		self.tabs.resize(420,280)
		self.tabs.show()
		sys.exit(self.app.exec_())

	def refreshComboBoxFromSpecific(self,buildType):
		self.tab1.refreshComboBox()
		self.tab2.refreshComboBox()
		self.tab3.refreshComboBox()		

class styleSheet():
	def __init__(self):
		pass
	def returnSheet(self):
		sheet = '''
		QToolTip
		{
		     border: 2px solid black;
		     background-color: #ffa02f;
		     padding: 1px;

		}

		QWidget
		{
		    /*Text*/
		    color: #b1b1b1;
		    /*Change the background colour of the item*/
		    background-color: #323232;
		}

		QWidget:item:hover
		{
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #ca0619);
		    color: #000000;
		}


		QWidget:disabled
		{
		    color: #404040;
		    background-color: #323232;
		}


		QAbstractItemView
		{
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0.1 #646464, stop: 1 #5d5d5d);
		}



		QLineEdit
		{
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #4d4d4d, stop: 0 #646464, stop: 1 #5d5d5d);
		    padding: 1px;
		    border-style: solid;
		    border: 1px solid #1e1e1e;
		    border-radius: 5;
		}

		QPushButton
		{
		    color: #b1b1b1;
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
		    border-width: 2px;
		    border-color: #222222;
		    border-style: solid;
		    border-radius: 6;
		    padding: 3px;
		    font-size: 12px;
		    padding-left: 5px;
		    padding-right: 5px;
		}


		QPushButton:pressed
		{
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
		}

		QComboBox
		{
		    selection-background-color: #262626;
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #565656, stop: 0.1 #525252, stop: 0.5 #4e4e4e, stop: 0.9 #4a4a4a, stop: 1 #464646);
		    border-style: solid;
		    border: 1px solid #1e1e1e;
		    border-radius: 5;
		}

		QComboBox:hover,QPushButton:hover
		{
		    border: 2px solid #ffa02f;
		}


		QComboBox:on
		{
		    padding-top: 3px;
		    padding-left: 4px;
		    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #2d2d2d, stop: 0.1 #2b2b2b, stop: 0.5 #292929, stop: 0.9 #282828, stop: 1 #252525);
		    selection-background-color: #262626;
		}

		QComboBox QAbstractItemView
		{
		    border: 0px solid darkgrey;
		    selection-background-color: #262626;
		    opacity: 60;

		}

		QComboBox::drop-down
		{
		     subcontrol-origin: padding;
		     subcontrol-position: top right;
		     width: 15px;

		     border-left-width: 0px;
		     border-left-color: darkgray;
		     border-left-style: solid; /* just a single line */
		     border-top-right-radius: 3px; /* same radius as the QComboBox */
		     border-bottom-right-radius: 3px;

		 }



		QGroupBox:focus
		{
		border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
		}

		QTextEdit:focus
		{
		    border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
		}



		QDockWidget::title
		{
		    text-align: center;
		    spacing: 3px; /* spacing between items in the tool bar */
		}



		QTabBar::tab {
		    /* The colour of the tab text */
		    color: #b1b1b1;
		    border: 1px solid black;
		    border-bottom-style: none;
		    background-color: #323232;
		    padding-left: 10px;
		    padding-right: 10px;
		    padding-top: 3px;
		    padding-bottom: 2px;
		    margin-right: -1px;
		}

		QTabWidget::pane {
		    /* The colour border */
		    border: 1px solid black;
		    top: -1px;
		}

		QTabBar::tab:last
		{
		    margin-right: 1; /* the last selected tab has nothing to overlap with on the right */
		    border-top-right-radius: 3px;
		}

		QTabBar::tab:first:!selected
		{
		    margin-left: 0px; /* the last selected tab has nothing to overlap with on the right */


		    border-top-left-radius: 3px;
		}

		QTabBar::tab:!selected
		{
		    color: #b1b1b1;
		    background-color: white;
		    border-bottom-style: solid;
		    margin-top: 3px;
		    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #404040, stop:.4 #4d4d4d);
		}

		QTabBar::tab:selected
		{
		    background-color: #262626;
		    border-top-left-radius: 3px;
		    border-top-right-radius: 3px;
		    margin-bottom: 0px;
		}

		QTabBar::tab:!selected:hover
		{
		    /*border-top: 2px solid #ffaa00;
		    padding-bottom: 3px;*/
		    border-top-left-radius: 3px;
		    border-top-right-radius: 3px;
		    background-color: QLinearGradient(x1:0, y1:0, x2:0, y2:1, stop:1 #212121, stop:0.4 #343434, stop:0.2 #343434, stop:0.1 #ffaa00);
		}

		QComboBox::down-arrow
		{
		     image: url(:/down_arrow.png);
		}

		QProgressBar
		{
		    border: 2px solid grey;
		    border-radius: 5px;
		    text-align: center;
		}

		QProgressBar::chunk
		{
		    background-color: #d7801a;
		    width: 2.15px;
		    margin: 0.5px;
		}



		'''
		return sheet







if __name__ == '__main__':
	Run = main()










