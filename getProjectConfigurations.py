import urllib, json



class getProjectConfigurations:
	def __init__(self):	
		self.build_list = []


	def get_builds_for_product(self,product):
		self.build_list = []
		self.product = product 
		self.product_url = 'http://jenkinsii:8080/view/{}/api/json?'.format(self.product)
		response = urllib.urlopen(self.product_url)
		product_list = json.loads(response.read())

		for build in product_list['jobs']:
			self.build_list.append(build['name'])
			# print build['name']
		return self.build_list

	def get_OS_configurations(self,product):
		self.get_builds_for_product(product)
		jsontest = {}
		for build in self.build_list:
			tmp_dict = {}
			url = "http://jenkinsii:8080/view/{}/job/{}/api/json?".format(self.product,build)
			response = urllib.urlopen(url)
			build_info = json.loads(response.read())
			# print build
			active_configurations = build_info['activeConfigurations']
			count = 1 
			for configuration in active_configurations:
				# make key name
				config_type, null = configuration['name'].split(',',1)
				config_type = config_type[14:]
				#assign key to dictionary so it relates it its url
				tmp_dict[config_type]=configuration['name']

			jsontest[build] = tmp_dict
		return jsontest 




	def output(self,product):
		jsontest = self.get_OS_configurations(product)

		print jsontest
		for each in jsontest[product]:
			print each
			# print jsontest[each]
			# for i in jsontest[each]:
			# 	print jsontest[each]
		with open ("jenkins_Builds.json", "w") as outfile:
			json.dump(jsontest, outfile)

	def return_multiple_projects(self,product_list):
		output_dict = {}
		for product in product_list:
			product_details = self.get_OS_configurations(product)
			# print product_details
			output_dict[product]=product_details


		with open ("jenkins_Builds.json", "w") as outfile:
			json.dump(output_dict, outfile)

		print output_dict
		return output_dict




if __name__ == "__main__":
	ins = getProjectConfigurations()
	ins.return_multiple_projects(['Mari','Modo'])


