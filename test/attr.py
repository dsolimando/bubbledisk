#!/usr/bin/python
#
#
import gnome
from gnome.vfs import *

class Maison:
	size = 24
	weigth = 6
	height = 4
	
	def getSize(self):
		return self.size
	
	def getWeigth(self):
		return self.weigth
	
	def getHeight(self):
		return self.height


dirs = open_directory("/home/dsolimando")

for dir in dirs:
#	print dir.__class__.__dict__.items()
	print dir.name
maison = Maison()
print maison.getSize()
print maison.getWeigth()
print maison.getHeight()

maison.size = 30
print maison.getSize()
