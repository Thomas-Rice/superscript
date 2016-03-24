import sys
import json
from PySide import QtCore, QtGui
from getProjectConfigurations import *


class AddProductToSetupDialogue(QtGui.QWidget):
	def __init__(self):
		super(AddProductToSetupDialogue, self).__init__()
		pass

	def create_layout(self):
		text, ok = QtGui.QInputDialog.getText(self, 'Add Product To Config', 
			'Type new product name:')
		if ok:
			return str(text)

class RemoveProductToSetupDialogue(QtGui.QWidget):
	def __init__(self,products):
		super(RemoveProductToSetupDialogue, self).__init__()
		pass

	def closeEvent(self):
		reply = QtGui.QMessageBox.question(self, 'Confirm Removal',
			"Are you sure to quit?", QtGui.QMessageBox.Yes | 
			QtGui.QMessageBox.No, QtGui.QMessageBox.No)

		if reply == QtGui.QMessageBox.Yes:
			return True
		else:
			return False

class errorDialog(QtGui.QWidget):
	def __init__(self,message):
		super(errorDialog, self).__init__()
		self.display_message(message)

	def display_message(self,message):
		reply = QtGui.QMessageBox.question(self, 'Error',
			message, QtGui.QMessageBox.Ok, QtGui.QMessageBox.Ok)

class BlockWidget(QtGui.QWidget):
	visibilityToggled = QtCore.Signal()

	def __init__(self, product_name, names = [], parent = None):
		super(BlockWidget, self).__init__(parent)

		self.names = names
		self.checkboxes = {}

		self.product_name = product_name

		self.create_widgets()
		self.create_layout()
		self.create_connections()

	def create_widgets(self):
		self.button = QtGui.QPushButton(self.product_name)
		self.checkBoxContainer = QtGui.QWidget(self)

		checkBoxLayout = QtGui.QVBoxLayout()
		checkBoxLayout.setContentsMargins(0,0,0,0)
		for name in self.names:
			# print name
			checkBox = QtGui.QCheckBox(name)
			self.checkboxes[name] = checkBox
			checkBoxLayout.addWidget(checkBox)

		self.checkBoxContainer.setLayout(checkBoxLayout)

	def create_layout(self):
		main_layout = QtGui.QVBoxLayout()
		main_layout.addWidget(self.button, alignment = QtCore.Qt.AlignTop)
		main_layout.addWidget(self.checkBoxContainer)
		main_layout.setContentsMargins(10,10,10,10)
		self.setLayout(main_layout)

	def create_connections(self):
		self.button.clicked.connect(self.toggleCheckBoxContainer)
		self.visibilityToggled.emit()

	def toggleCheckBoxContainer(self):
		if self.checkBoxContainer.isHidden():
			self.checkBoxContainer.show()
		else:
			self.checkBoxContainer.hide()
		self.visibilityToggled.emit()

	def return_checked(self):
		chosen_config = []
		chosen_products = []
		chosen_products.append(self.product_name)
		for checkbox in self.names:
			if self.checkboxes[checkbox].isChecked():
				chosen_config.append(checkbox)
		# print chosen_config
		list_of_chosen_items = [chosen_products,chosen_config]
		return list_of_chosen_items

class Container(QtGui.QWidget):
	def __init__(self, product_name, config, parent = None):
		super(Container, self).__init__(parent)
		self.resize(400,400)
		self.__config = config
		self.__product_name = product_name


		self.create_widgets()
		self.create_layout()
		self.create_connections()
		self.populate()

	@property
	def config(self):
		return self.__config

	@config.setter
	def config(self, value):
		self.__config = value
		self.populate()

	def create_widgets(self):
		self.table = QtGui.QTableWidget(self)
		self.table.setColumnCount(1)
		#hide the row and colum numbers
		self.table.horizontalHeader().hide()
		self.table.verticalHeader().hide()
		#stretch the row to fill the screen
		self.table.horizontalHeader().setStretchLastSection(True)



	def create_layout(self):
		main_layout = QtGui.QVBoxLayout()
		main_layout.setContentsMargins(0,0,0,0)
		main_layout.addWidget(self.table)
		self.setLayout(main_layout)

	def create_connections(self):
		pass

	def populate(self, config = None):
		if config:
			self.__config = config

		self.table.clear()
		self.rowCount = len(self.__config)+1
		self.table.setRowCount(self.rowCount)

		for index, configurations in enumerate(self.__config):
			block = BlockWidget(self.__product_name[index],configurations)
			block.visibilityToggled.connect(self.resizeRows)
			self.table.setCellWidget(index, 0, block)

		self.table.resizeRowsToContents()

	def resizeRows(self):
		self.table.resizeRowsToContents()

	def return_configs(self):
		config_list = []
		for widget in range(self.rowCount-1):
			returned_list = self.table.cellWidget(widget,0).return_checked()
			if not returned_list[1] == []:
				config_list.append(returned_list)
		# self.make_final_dictionary(config_list)
		return config_list


	def make_final_dictionary(self):
		final_dictionary = self.return_configs()
		config_dictionary = {}
		build_list = []
		with open('jenkins_Builds.json') as data_file:
			original_dict = json.load(data_file)

		#get chosen builds and their configs then make that into a dictionary
		for item in final_dictionary:
			for l in item[1]:
				config_dictionary[l] = original_dict[item[0][0]][l]
				build_list.append(l)
		final_list = [build_list,config_dictionary]
		# print config_dictionary
		return final_list


class main_window(QtGui.QWidget):
	def __init__(self,products,jenkins_object,parent = None):
		super(main_window, self).__init__(parent)
		self.height = 600
		self.resize(400,self.height)

		self.products = products
		self.jenkins_object = jenkins_object
		# add products dialog window
		self.add_dialog = AddProductToSetupDialogue()
		# Remove products dialog window
		self.remove_dialog = RemoveProductToSetupDialogue(self.products)


		self.layout = 'First_Page'
		self.config_window_generated = False
		self.chosen_products = ''

		self.product_form = product_window(self.products)

		self.create_widgets()
		self.create_layout()
		self.create_connections()


	def create_widgets(self):
		self.button = QtGui.QPushButton('Generate Build List')
		self.button2 = QtGui.QPushButton('Generate Config List')
		self.button3 = QtGui.QPushButton('Save and Exit')
		self.button4 = QtGui.QPushButton('Remove Product (Take out later)')
		self.button5 = QtGui.QPushButton('Add Product (Take out later)')
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

		self.splitter.addWidget(self.product_form)
		self.splitter.setSizes([70,230])

	def create_layout(self):
		main_layout = QtGui.QVBoxLayout()
		main_layout.setContentsMargins(0,0,0,0)
		main_layout.addWidget(self.splitter)
		main_layout.addWidget(self.button)
		main_layout.addWidget(self.button2)
		main_layout.addWidget(self.button3)
		main_layout.addWidget(self.button4)
		main_layout.addWidget(self.button5)
		self.setLayout(main_layout)

	def create_connections(self):
		self.button.clicked.connect(self.change_Layout)
		self.button2.clicked.connect(self.generate_config_window)
		self.button3.clicked.connect(self.save_and_exit)
		self.button4.clicked.connect(self.remove_product)
		self.button5.clicked.connect(self.add_product)

	def change_Layout(self):
		try:
			if self.layout == "First_Page":
				chosen_products = self.product_form.return_checked()
				#check if the user has selected a new check box, if so then regenerate the list if not then dont move. 
				if chosen_products != self.chosen_products:
					self.chosen_products = chosen_products
					#get the builds from jenkins for each product
					product_and_config = self.jenkins_object.populate_products_with_builds(self.chosen_products)
					#Populate the checkboxes
					self.checkbox_form = Container(product_and_config[0],product_and_config[1])
					# Add the widget
					self.splitter.addWidget(self.checkbox_form)
					self.layout = 'Second_Page'


			elif self.layout == "Second_Page":
				chosen_products = self.product_form.return_checked()
				#check if the user has selected a new check box, if so then regenerate the list if not then dont move. 
				if chosen_products != self.chosen_products:
					self.chosen_products = chosen_products
					product_and_config = self.jenkins_object.populate_products_with_builds(self.chosen_products)
					#Populate the checkboxes with product names and a dictionary of the builds
					self.checkbox_form = Container(product_and_config[0],product_and_config[1])
					self.hide_widgets()
					# resize back to original 
					self.resize(400,self.height)
					# Insert the new widget
					self.splitter.insertWidget(1,self.checkbox_form)
					self.config_window_generated = False

			else:
				pass
		except IOError:
			window = errorDialog('Cannot Connect to Jenkins, \n Please Check Connection')
		except:
			window = errorDialog('If you have added a new product, \n please check the name is correct (This is case sensitive)')


	def hide_widgets(self):
		count = self.splitter.count()
		# Hide each widget when selecting a new product
		for widget in range(1,count):
			self.splitter.widget(widget).hide()

	def generate_config_window(self):
		if self.config_window_generated == False:
			formatted_config_list = []
			build_list = []
			# Get the configuration dictionary from the checkboxes
			config_dictionary = self.checkbox_form.make_final_dictionary()
			# Format it correctly to pass into to the checkbox widget
			formatted_config_list.append(config_dictionary[1])
			# Check to see if the user has selected anything
			if config_dictionary[0] != []:
				for each in config_dictionary[1]:
					build_list.append(each)
					formatted_config_list.append(config_dictionary[1][each]) 
				#delete the name of the product from the dictionary list as we dont need it and it gets in the way 
				del formatted_config_list[0]
				self.config_checkbox_form = Container(build_list,formatted_config_list)
				# Resize the widget to accomodate the new widget
				self.resize(800,self.height)
				# Insert the widget
				self.splitter.insertWidget(2,self.config_checkbox_form)
				self.config_window_generated = True


	def save_and_exit(self):
		# pass
		output = self.splitter.widget(2).return_configs()
		print output

	def remove_product(self,extra = None):
		#Get the boolean for if the user is sure they want to delete or not
		bool_check = self.remove_dialog.closeEvent()
		# If the user does
		if bool_check == True:
			product_to_be_removed_list = []
			#Get Checked Products to Remove
			product_to_be_removed = self.product_form.return_checked()
			for item in product_to_be_removed:
				product_to_be_removed_list.append(item)
			# Remove products
			updated_product_list = self.jenkins_object.remove_product_from_list(product_to_be_removed_list)
			# Regenerate Product Window
			self.regenerate_widget(updated_product_list)

			self.hide_widgets()
		else:
			pass

	def add_product(self,extra = None):
		# Get the input from the user
		new_product = self.add_dialog.create_layout()
		#add in extra products
		updated_product_list = self.jenkins_object.write_product_list(new_product)
		# # Regenerate Product Window
		self.regenerate_widget(updated_product_list)

	def regenerate_widget(self,product_list):
		self.splitter.widget(0).hide()
		self.product_form = product_window(product_list)
		self.splitter.insertWidget(0,self.product_form)
		self.splitter.setSizes([70,230])
		self.resize(400,self.height)



class product_window(QtGui.QWidget):

	def __init__(self, products = [],parent = None):
		super(product_window, self).__init__(parent)
		self.height = 400
		self.resize(400,self.height)

		self.products = products
		self.checkboxes = {}

		self.create_widgets()
		self.create_layout()
		self.create_connections()
		self.return_checked()

	def create_widgets(self):
		self.checkBoxContainer = QtGui.QWidget(self)

		#Sort the list of names
		tmp_list = []
		for name in self.products:
			tmp_list.append(name)
		tmp_list.sort()

		checkBoxLayout = QtGui.QVBoxLayout()
		checkBoxLayout.setContentsMargins(0,0,0,0)
		for name in tmp_list:
			checkBox = QtGui.QCheckBox(name)
			self.checkboxes[name] = checkBox
			checkBoxLayout.addWidget(checkBox)

		self.checkBoxContainer.setLayout(checkBoxLayout)

	def create_layout(self):
		main_layout = QtGui.QVBoxLayout()
		main_layout.addWidget(self.checkBoxContainer)
		main_layout.setContentsMargins(10,10,10,10)
		self.setLayout(main_layout)

	def create_connections(self):
		pass

	def return_checked(self):
		chosen_products = []
		for checkbox in self.products:
			if self.checkboxes[checkbox].isChecked():
				chosen_products.append(checkbox)
		# print chosen_products
		return chosen_products


class choose_projects():
	def __init__(self):
		pass

	def write_product_list(self, extra = None):
		# Open the currently saved dictionary
		products = self.read_and_write_Json("subScript_General_Settings.json")
		# If the user does not want to add anythin to the list then assign the usual suspects
		if extra == None:
			products['product'] = ['Collectives','Gonzo',"HPC",'Katana','Licensing','Mari','Modo','Nuke','Research']
		else:
			# Get the list from the dictionary
			updated_list = products['product']
			#Add the extra project
			updated_list.append(extra)
			# Put it back in the dictionary
			products['product'] = updated_list
		# Write it out
		self.read_and_write_Json("subScript_General_Settings.json",products,'w')
		return products['product']

	def remove_product_from_list(self,chosen_products):
		products = self.read_and_write_Json("subScript_General_Settings.json")
		product_list = products['product']
		#Remove all the products the user wants to delete
		for product in chosen_products:
			# print product
			product_list.remove(product)

		products['product'] = product_list	
		# Write it out
		self.read_and_write_Json("subScript_General_Settings.json",products,'w')
		return products['product']

	def get_product_list(self):
		products = {}
		# Read in the Json
		products = self.read_and_write_Json("subScript_General_Settings.json")
		return products['product']

	def read_and_write_Json(self,json_to_read, data = None,arg = None):
		if arg == "w":
			with open (json_to_read, "w") as outfile:
				json.dump(data, outfile)
		else:
			with open(json_to_read) as data_file:
				returned_data = json.load(data_file)
			return returned_data


	def populate_products_with_builds(self,product_list):
		self.config = []
		self.products = []
		# Get the builds from selected products and write it to a dictionary
		ins = getProjectConfigurations()
		ins.return_multiple_projects(product_list)
		# Read it from the dictionary
		with open('jenkins_Builds.json') as data_file:
			test1 = json.load(data_file)

		# Format the data so that we get a list that contains the product name and a dictionary for each product
		for each in test1:
			# Products
			self.products.append(each)
			# Dictionary of builds
			self.config.append(test1[each])

		combined_list = [self.products, self.config]
		return combined_list

def main():
	global app
	global wid

	project_choices = choose_projects()
	products = project_choices.get_product_list()
	# project_choices.write_product_list()

	app = QtGui.QApplication(sys.argv)

	wid = main_window(products, project_choices)
	wid.show()

	sys.exit(app.exec_())

if __name__ == '__main__':
   test = main()



