#!/usr/bin/python

import gtk

class CdromIsoProject:
	onglets = ["Multisession",
			   "Opt. du fichier",
			   "Descripteur vol.",
			   "Dates",
			   "CD Audio",
			   "Options CDA"]
	
	notebook = None

	def __init__(self):
	
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos (gtk.POS_TOP)
		
		for onglet in onglets:
			print onglet
			frame = gtk.Frame ()
			label = gtk.Label (onglet)
			notebook.append_page (frame,label)
	
	def get_notebook(self):
		return self.notebook
