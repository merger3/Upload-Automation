import os
import platform

if platform.system() == "Windows":
	xmls = os.getcwd() + '\\xmls'
else:
	xmls = os.getcwd() + '/xmls'
for root, dirs, files in os.walk(xmls):
	for i in files:
		print(os.path.join(root, i))