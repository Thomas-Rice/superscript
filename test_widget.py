import sys
import json
from PySide import QtCore, QtGui
from getProjectConfigurations import *

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

		self.button = QtGui.QPushButton('Save And Exit')


	def create_layout(self):
		main_layout = QtGui.QVBoxLayout()
		main_layout.setContentsMargins(0,0,0,0)
		main_layout.addWidget(self.table)
		self.setLayout(main_layout)

	def create_connections(self):
		self.button.clicked.connect(self.make_final_dictionary)


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

		self.table.setCellWidget(index + 1 , 0, self.button)


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

		self.jenkins_object = jenkins_object
		self.products = products


		self.layout = 'First_Page'


		self.product_form = product_window(self.products)

		self.create_widgets()
		self.create_layout()
		self.create_connections()


	def create_widgets(self):
		self.button = QtGui.QPushButton('Generate Build List')
		self.button2 = QtGui.QPushButton('Generate Config List')
		self.splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)

		self.splitter.addWidget(self.product_form)
		self.splitter.setSizes([70,230])



	def create_layout(self):
		main_layout = QtGui.QVBoxLayout()
		main_layout.setContentsMargins(0,0,0,0)
		main_layout.addWidget(self.splitter)
		main_layout.addWidget(self.button)
		main_layout.addWidget(self.button2)
		self.setLayout(main_layout)

	def create_connections(self):
		self.button.clicked.connect(self.change_Layout)
		self.button2.clicked.connect(self.generate_config_window)

	def change_Layout(self):
		if self.layout == "First_Page":

			#get the builds from jenkins for each product
			product_and_config = self.jenkins_object.populate_products_with_builds(self.products)
			#Populate the checkboxes
			self.checkbox_form = Container(product_and_config[0],product_and_config[1])

			self.splitter.addWidget(self.checkbox_form)
			self.layout = 'Second_Page'

		else:
			product_and_config = self.jenkins_object.populate_products_with_builds(self.products)
			#Populate the checkboxes with product names and a dictionary of the builds
			# print product_and_config[1]
			self.checkbox_form = Container(product_and_config[0],product_and_config[1])

			self.splitter.widget(1).hide()
			self.splitter.insertWidget(1,self.checkbox_form)
			self.layout = 'Second_Page'

	def generate_config_window(self):
		formatted_config_list = []
		build_list = []
		config_dictionary = self.checkbox_form.make_final_dictionary()
		formatted_config_list.append(config_dictionary[1])
		for each in config_dictionary[1]:
			build_list.append(each)
			formatted_config_list.append(config_dictionary[1][each]) 
		del formatted_config_list[0]
		self.config_checbox_form = Container(build_list,formatted_config_list)
		self.resize(800,self.height)
		self.splitter.addWidget(self.config_checbox_form)




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

		checkBoxLayout = QtGui.QVBoxLayout()
		checkBoxLayout.setContentsMargins(0,0,0,0)
		for name in self.products:
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
		self.products = []



	def get_product_list(self):
		# #until i get something working with this it will have to be manual OR I can do a dictionary where the user can add to it

		products = ['Mari','Modo','Nuke']
		#products = ['Collectives','Colourway','Core','Gonzo',"HPC",'Katana','Licensing','Live','MVC','Mari','Mischief','Modo','Nuke','Playground','Research']
		return products

	def populate_products_with_builds(self,product_list):
		self.config = []
		ins = getProjectConfigurations()
		ins.return_multiple_projects(product_list)

		with open('jenkins_Builds.json') as data_file:
			test1 = json.load(data_file)


		for each in test1:
			self.products.append(each)
			self.config.append(test1[each])


		combined_list = [self.products, self.config]
		return combined_list







def main():
	global app
	global wid

	project_choices = choose_projects()
	products = project_choices.get_product_list()


	app = QtGui.QApplication(sys.argv)

	wid = main_window(products, project_choices)
	wid.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
   test = main()



