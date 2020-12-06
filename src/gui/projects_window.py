import gtk
import gui_tools
from projects_notebooks import *
from constants.config import *

class Projects_window:
	NUM_PROJECTS = 3

	window = None 	# The widow
	mainBox = None	# The main container for gtk components
	icon_boxes = []
	frame_event_box	= None
	dvd_icon_box = None
	frame = None
	icons = {ICONS_DIR+"/gnome-dev-cdrom-audio.png":"Audio CD",
					ICONS_DIR+"/data_disk.png":"Data CD (iso9660)",
					ICONS_DIR+"/cd_copy.png":"Copy CD",
					ICONS_DIR+"/gnome-dev-cdrom-mixte.png":"Mixte CD",
					ICONS_DIR+"/gnome-dev-cdrom-extra.png":"CD Extra"}

	dvd_icons = {ICONS_DIR+"/gnome-dev-dvdrom.png":"Data DVD",
				 ICONS_DIR+"/gnome-dev-dvd-video.png":"DVD Video"}

	icons_indices = {"Copy CD" : 2,
					 "Data CD (iso9660)" : 1,
					 "Audio CD": 0,
					 "CD Extra": 4,
					 "Mixte CD": 3}

	ordered_icons = [
					 ICONS_DIR+"/gnome-dev-cdrom-audio.png",
					 ICONS_DIR+"/data_disk.png",
					 ICONS_DIR+"/cd_copy.png",
					 ICONS_DIR+"/gnome-dev-cdrom-mixte.png",
					 ICONS_DIR+"/gnome-dev-cdrom-extra.png"
					 ]

	ordered_dvd_icons = [
						 ICONS_DIR+"/gnome-dev-dvdrom.png",
						 ICONS_DIR+"/gnome-dev-dvd-video.png"
						 ]

	choices = ["CD","DVD"]

	notebooks_indexes = {}

	notebook = None # The notebook containing the project properties
	buttons_vpane = None # The vertical pan containing the buttons

	current_project_selected = None
	gui_control = None
	gui_view = None
	proj_not = None
	# For Multiprojects Support
	project_id = 0

	def __init__(self,gui_control,gui_view,project_id,project_type="Data CD (iso9660)"):
		self.gui_control = gui_control
		self.gui_view = gui_view
		self.project_id = project_id

		self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
		self.window.set_size_request (732,500)
		self.window.set_title ("Burning Project")
		self.window.connect("delete_event",self.gui_control.cb_pw_hide_window_cancel,self.project_id)

		self.mainBox = gtk.HBox (False,10)
		self.mainBox.set_border_width (15)

		self.left_vbox = gtk.VBox(False,0)
		self.left_vbox_top = gtk.VBox(False,0)
		self.left_vbox_bottom = gtk.VBox(True,0)

		self.icon_box = {}
		self.icon_box["dvd"] = gui_tools.evolution_icon_box(self.dvd_icons,self.ordered_dvd_icons,"Data DVD",self.gui_control.cb_pw_iconbox_clicked)
		self.icon_box["cd"] = gui_tools.evolution_icon_box(self.icons,self.ordered_icons,"Data CD (iso9660)",self.gui_control.cb_pw_iconbox_clicked)
		self.current_project_selected = project_type
		self.left_vbox_bottom.pack_start(self.icon_box["cd"],False,True,1)
		self.left_vbox_bottom.pack_start(self.icon_box["dvd"],False,True,1)

		self.cd_or_dvd_combobox = gtk.combo_box_new_text()
		self.cd_or_dvd_combobox.connect ("changed",self.gui_control.cb_pw_switch_icon_boxes)

		self.left_vbox_top.pack_start(self.cd_or_dvd_combobox,False,True,5)
		#self.left_vbox.pack_start(self.cd_or_dvd_combobox,False,True)
		self.left_vbox.pack_start(self.left_vbox_top,False,True,0)
		self.left_vbox.pack_start(self.left_vbox_bottom,True,True,0)

		for choice in self.choices:
			self.cd_or_dvd_combobox.append_text(choice)
		self.cd_or_dvd_combobox.set_active(0)

		self.hide_icon ("cd",0)

		self.notebook_vbox = gtk.VBox(True,0)
		self.proj_not = projects_notebooks(self.gui_control,self.gui_view,self.project_id)
		self.notebook = self.proj_not.get_notebook()

		self.notebook_vbox.pack_start (self.notebook,True,True)

		self.buttons_vbox = gtk.VBox (False,10)
		self.buttons_vbox.set_size_request (100,-1)
		self.new_button = gtk.Button ("New")
		self.copy_button = gtk.Button ("Copy")
		self.diskinfo_button = gtk.Button ("Disk Informations")
		self.cancel_button = gtk.Button ("Cancel")
		self.create_button = gtk.Button ("Create")
		self.ok_button = gtk.Button ("Ok")
		self.new_button.connect("pressed",self.gui_control.cb_pw_hide_window,self.project_id)
		self.cancel_button.connect("pressed",self.gui_control.cb_pw_hide_window_cancel,self.project_id)
		self.create_button.connect("pressed",self.gui_control.cb_pw_finalize_project,self.project_id)
		self.copy_button.connect("pressed",self.gui_control.cb_pw_hide_window,self.project_id)
		self.ok_button.connect("pressed",self.gui_control.cb_pw_hide_window_ok,self.project_id)

		self.buttons_vbox.pack_start (self.new_button,False,False)
		self.buttons_vbox.pack_start (self.create_button,False,False)
		self.buttons_vbox.pack_start (self.cancel_button,False,False)
		self.buttons_vbox.pack_start (self.ok_button,False,False)
		self.buttons_vbox.pack_start (self.copy_button,False,False)
		self.buttons_vbox.pack_start (self.diskinfo_button,False,False)

		self.mainBox.pack_start (self.left_vbox,False,True)
		self.mainBox.pack_start (self.notebook_vbox,False,False)
		self.mainBox.pack_start (self.buttons_vbox,False,False)

		self.window.add(self.mainBox)

		self.modify_tabs(project_type)
		self.hide_widgets_before_iso_creation()

	def get_window (self):
		return self.window

	def hide_widgets_before_iso_creation(self):
		#self.hide_icon(0)
		self.create_button.hide()
		self.ok_button.hide()

	def hide_widgets_after_iso_creation(self,media_key,icon_project=None):
		if icon_project == None:
			icon_project = self.current_project_selected

		self.switch_icon_boxes(media_key)
		self.cd_or_dvd_combobox.set_sensitive(False)

		for icon in self.icons.values():
			if icon != icon_project:
				self.hide_icon(media_key,self.icons_indices[icon])
			else:
				self.select_icon(media_key, self.icons_indices[icon])

		self.modify_tabs(self.get_current_project_selected())

		self.new_button.hide()
		self.create_button.show()
		self.cancel_button.show()
		self.copy_button.hide()
		self.diskinfo_button.hide()
		self.ok_button.hide()


	def modify_tabs(self,tab_name):
		if tab_name == DATA_CD +" (iso9660)":
			for i in range (8):
				self.notebook.get_nth_page(i).show()

			self.notebook.get_nth_page(4).hide()
			self.notebook.get_nth_page(3).hide()
			self.notebook.get_nth_page(7).hide()
			self.notebook.get_nth_page(5).hide()
			self.notebook.set_current_page(6)
			#self.notebook.set_current_page(0)
			self.copy_button.hide()
			self.diskinfo_button.hide()
			self.new_button.show()
			self.create_button.hide()

		elif tab_name == COPY_CD:
			for i in range (8):
				self.notebook.get_nth_page(i).hide()

			self.notebook.get_nth_page(4).show()
			self.notebook.get_nth_page(7).show()
			self.notebook.get_nth_page(3).show()
			self.notebook.set_current_page(7)

			self.new_button.hide()
			self.copy_button.show()
			self.diskinfo_button.show()

		elif tab_name == AUDIO_CD:
			for i in range (8):
				self.notebook.get_nth_page(i).hide()

			self.notebook.get_nth_page(5).show()
			self.notebook.get_nth_page(6).show()

			self.notebook.set_current_page(6)

			self.copy_button.hide()
			self.diskinfo_button.hide()
			self.create_button.hide()
			self.new_button.show()

		elif tab_name == MIXTE_CD:
			for i in range (8):
				self.notebook.get_nth_page(i).show()

			self.notebook.get_nth_page(7).hide()
			self.notebook.get_nth_page(4).hide()

			self.notebook.set_current_page(6)

			self.copy_button.hide()
			self.diskinfo_button.hide()
			self.create_button.hide()
			self.new_button.show()

		elif tab_name == CD_EXTRA:
			for i in range (8):
				self.notebook.get_nth_page(i).show()

			self.notebook.get_nth_page(7).hide()
			self.notebook.get_nth_page(4).hide()

			self.notebook.set_current_page(6)

			self.copy_button.hide()
			self.diskinfo_button.hide()
			self.create_button.hide()
			self.new_button.show()

	def get_current_project_selected (self):
		return self.current_project_selected

#	def modify_bg (self,widget,event,data=None):
#		for icon_box in self.icon_boxes:
#			icon_box.set_state(gtk.STATE_NORMAL)
#
#		widget.set_state(gtk.STATE_SELECTED)
#		childwidget = widget.get_child().get_children()[1].get_label()
#		self.current_project_selected = childwidget
#		self.modify_tabs(childwidget)

	def hide_icon (self, media_key, index):
		self.icon_box[media_key].get_child().get_child().get_children()[index].hide()

	def select_icon (self,media_key, index):
		self.icon_box[media_key].get_child().get_child().get_children()[index].set_state(gtk.STATE_SELECTED)

	def unhide_icon (self, index):
		self.icon_box[media_key][index].show()

	def switch_icon_boxes(self,media_type):
		if media_type == "cd":
			self.icon_box["dvd"].hide()
			self.icon_box["cd"].show()
	 	else:
	 		self.icon_box["dvd"].show()
			self.icon_box["cd"].hide()
