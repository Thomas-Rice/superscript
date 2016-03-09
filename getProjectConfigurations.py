import urllib, json



class getProjectConfigurations:
	def __init__(self,product):	
		self.build_list = []
		self.product = product 
		self.product_url = 'http://jenkinsii:8080/view/{}/api/json?'.format(self.product)

	def get_builds_for_product(self):
		response = urllib.urlopen(self.product_url)
		product_list = json.loads(response.read())

		for build in product_list['jobs']:
			self.build_list.append(build['name'])
			# print build['name']

	def get_OS_configurations(self):
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
				tmp_dict[count]=configuration['name']
				count += 1

			jsontest[build] = tmp_dict
		return jsontest 




	def output(self):
		jsontest = self.get_OS_configurations()

		for each in jsontest:
			for i in range(1,len(jsontest[each])):
				print jsontest[each][i]



if __name__ == "__main__":
	ins = getProjectConfigurations('Nuke')
	ins.get_builds_for_product()
	ins.output()


