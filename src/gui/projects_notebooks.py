#!/usr/bin/python

import gtk
import gobject
import os
from gui_tools import *

class projects_notebooks:

	onglets = ["Multisession",
			   "Filesystem",
			   "Volume desc",
			   "Reading options",
			   "Writing",
			   "Copy",
			   "Copy options",
			   "CD Text"]

	onglets_num = len(onglets)

	notebook = None
	gui_control = None
	gui_view = None

	iso9660_options = None
	project_id = 0

	multisess_radio_buttons = None
	iso_levels_rb = None
	trackmode_rb = None
	add_file_desc_rb = None
	iso_restrict_rb = None

	check_charset = None
	charsets_combobox = None
	advanced_params_liststore = None
	advanced_params_treeview = None

	volume_desc_entries = {}
	cd_text_entries = {}

	burn_action_rb = None
	copy_method_rb = None
	write_options_rb = None
	speed_combo_box = None

	def __init__(self,gui_control,gui_view,project_id):
		self.gui_control = gui_control
		self.gui_view = gui_view
		self.project_id = project_id

		self.iso9660_options = ((self.gui_control.isofs_tool.allow_untranslated_filenames,"Allow untranslated filenames"),
								(self.gui_control.isofs_tool.relaxed_filenames,"Alow ASCII characters"),
								(self.gui_control.isofs_tool.allow_31_char_fn,"Allow 31 characters Filename"),
								(self.gui_control.isofs_tool.no_iso_translate,"Allow ~ and #"),
								(self.gui_control.isofs_tool.allow_leading_dots,"Allow leading dots"),
								(self.gui_control.isofs_tool.allow_lowercase,"Allow lowercase characters"),
								(self.gui_control.isofs_tool.allow_multidot,"Allow multiple dots"),
								(self.gui_control.isofs_tool.omit_trailing_period,"Omit trailing period"),
								(self.gui_control.isofs_tool.omit_version_number,"Omit version Numbers"),
								(self.gui_control.isofs_tool.max_iso9660_filenames,"Allow max length filenames (37 characters)"),
								(self.gui_control.isofs_tool.gen_transbl,"Create TRANS.TBL files"),
								(self.gui_control.isofs_tool.joliet_long,'Allow 103 characters Joliet filenames'),
								(self.gui_control.isofs_tool.hide_joliet_trans_tbl,"Hide TRANS.TBL in Joliet"))

		self.notebook = gtk.Notebook()
		self.notebook.set_scrollable(True)
		self.notebook.set_tab_pos (gtk.POS_TOP)
		self.notebook.set_size_request (450,-1)


		frame1 = self.multisess_frame ()
		frame1.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[0])
		self.notebook.append_page (frame1,label)

		frame2 = self.file_options_frame()
		frame2.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[1])
		self.notebook.append_page (frame2,label)

		frame3 = self.volume_descriptor_frame()
		frame3.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[2])
		self.notebook.append_page (frame3,label)

		reading_options_frame = self.copy_reading_options_frame()
		reading_options_frame.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[3])
		self.notebook.append_page (reading_options_frame,label)

		copy_options_frame = self.copy_copy_options_frame()
		copy_options_frame.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[6])
		self.notebook.append_page (copy_options_frame,label)

		cd_text_frame = self.cda_options ()
		cd_text_frame.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[7])
		self.notebook.append_page (cd_text_frame,label)

		frame4 = self.create_cd_frame ()
		frame4.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[4])
		self.notebook.append_page (frame4,label)

		make_copy_frame = self.make_copy_frame()
		make_copy_frame.set_shadow_type(gtk.SHADOW_NONE)
		label = gtk.Label (self.onglets[5])
		self.notebook.append_page (make_copy_frame,label)


	def get_notebook(self):
		return self.notebook


	def multisess_frame (self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		radio_labels = ["No multisession Disk",
						"Begin a multisession Disk",
						"Continue a multisession Disk",
						"Finish a multisession Disk"]

		frame_1,self.multisess_radio_buttons = radio_buttons_box ("Multisession",radio_labels,0)
		for label in radio_labels:
			self.multisess_radio_buttons[label].connect ("toggled",self.gui_control.cb_pw_multisess_toggled,self.project_id)
		vbox.pack_start(frame_1,False,False)


		return frame

	def file_options_frame (self):
		frame = gtk.Frame()

		main_vbox = gtk.VBox(False,0)
		vbox_easy = gtk.VBox(False,0)
		vbox_easy.set_border_width (10)
		vbox_advanced = gtk.VBox(False,0)
		vbox_advanced.set_border_width (5)
		frame.add (main_vbox)

		radio_labels = ["Generate Joliet directory records\t(for Win32 Systems)",
						"Generate Rock Ridge directory records\t(for Unix Systems)",
						"UDF Structures"]

		selected = []

		if self.gui_control.isofs_tool.gen_joliet:
			selected.append(0)
		if self.gui_control.isofs_tool.gen_rock_ridge_ext:
			selected.append(1)
		if self.gui_control.isofs_tool.udf:
			selected.append(2)

		frame_3,self.add_file_desc_rb = check_boxes_box  ("Additional File Descrptors",radio_labels,selected)
		self.add_file_desc_rb["Generate Joliet directory records\t(for Win32 Systems)"].connect ("toggled",self.gui_control.cb_pw_add_joliet_toggled,self.project_id)
		self.add_file_desc_rb["Generate Rock Ridge directory records\t(for Unix Systems)"].connect ("toggled",self.gui_control.cb_pw_add_rr_toggled,self.project_id)
		self.add_file_desc_rb["UDF Structures"].connect ("toggled",self.gui_control.cb_pw_add_udf_toggled,self.project_id)

		###############################################################
		# Charsets Parameters Frame
		###############################################################
		hbox_10 = gtk.HBox (True,0)
		hbox_10.set_border_width(2)
		label_hbox = gtk.HBox (False,0)

		charset_label = gtk.Label ("Input Charset:")
		label_hbox.pack_start (charset_label,False,True,4)

		self.charsets_combobox = gtk.combo_box_new_text()
		charsets = ["cp10081",
					"cp10079",
					"cp10029",
					"cp10007",
					"cp10006",
					"cp10000",
					"koi8-u",
					"koi8-r",
					"cp1251",
					"cp1250",
					"cp874",
					"cp869",
					"cp866",
					"cp865",
					"cp864",
					"cp863",
					"cp862",
					"cp861",
					"cp860",
					"cp857",
					"cp855",
					"cp852",
					"cp850",
					"cp775",
					"cp737",
					"cp437",
					"cp857",
					"iso8859-15",
					"iso8859-14",
					"iso8859-9",
					"iso8859-8",
					"iso8859-7",
					"iso8859-6",
					"iso8859-5",
					"iso8859-4",
					"iso8859-3",
					"iso8859-2",
					"iso8859-1"]


		for charset in charsets:
			self.charsets_combobox.append_text(charset)

		self.charsets_combobox.set_active(charsets.index(self.gui_control.isofs_tool.input_charset))
		self.charsets_combobox.connect ("changed",self.gui_control.cb_pw_charset_changed,self.project_id)
		hbox_10.pack_start (label_hbox,False,True,4)
		hbox_10.pack_end (self.charsets_combobox,False,True)

		###############################################################
		# ISO Level Parameters Frame
		###############################################################
		hbox_iso_level = gtk.HBox (True,0)
		label_hbox = gtk.HBox (False,0)
		hbox_iso_level.set_border_width(2)

		iso_level_label = gtk.Label ("ISO Format:")
		label_hbox.pack_start (iso_level_label,False,True,4)

		self.iso_level_combobox = gtk.combo_box_new_text()
		levels = ["ISO Level 1",
					"ISO Level 2",
					"ISO Level 3"]

		for level in levels:
			self.iso_level_combobox.append_text(level)

		self.iso_level_combobox.set_active(levels.index("ISO Level "+str(self.gui_control.isofs_tool.iso_level)))
		self.iso_level_combobox.connect ("changed",self.gui_control.cb_pw_iso_level_changed,self.project_id)
		hbox_iso_level.pack_start (label_hbox,False,True,4)
		hbox_iso_level.pack_end (self.iso_level_combobox,False,True)

		###############################################################
		# Datatrack Format Parameters Frame
		###############################################################
		hbox_data_format = gtk.HBox (True,0)
		hbox_data_format.set_border_width(2)
		label_hbox = gtk.HBox (False,0)
		data_format_label = gtk.Label ("Datatrack Mode:")
		label_hbox.pack_start (data_format_label,False,True,4)

		self.data_format_combobox = gtk.combo_box_new_text()
		formats = ["Auto",
				   "Mode 1",
				   "Mode 2",
				   "xa",
				   "xa1",
				   "xa2",
				   "xamix"]

		for format in formats:
			self.data_format_combobox.append_text(format)

		self.data_format_combobox.set_active(formats.index("Auto"))
		self.data_format_combobox.connect ("changed",self.gui_control.cb_pw_trackmode_changed,self.project_id)
		hbox_data_format.pack_start (label_hbox,False,True,4)
		hbox_data_format.pack_end (self.data_format_combobox,False,True)

		################################################################
		# Advanced Parameters Frame
		################################################################
		frame_label = gtk.Label()
		frame_label.set_markup ('<span weight="bold">ISO 9669 advanced parameters</span>')

		advanced_params_frame = gtk.Frame ()
		advanced_params_frame.set_label_widget(frame_label)
		advanced_params_frame.set_shadow_type(gtk.SHADOW_NONE)
		advanced_params_frame.set_size_request (-1,160)

		sw = gtk.ScrolledWindow()
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

		advanced_params_vbox = gtk.VBox (False,0)
		advanced_params_vbox.pack_start(sw,True,True)
		advanced_params_vbox.set_border_width(10)
		advanced_params_frame.add(advanced_params_vbox)

		self.advanced_params_liststore = gtk.ListStore(
							gobject.TYPE_BOOLEAN,
							gobject.TYPE_STRING
							)

		for option in self.iso9660_options:
			iter = self.advanced_params_liststore.append()
			self.advanced_params_liststore.set(iter,
				0,option[0],
				1,option[1]
				)

		self.advanced_params_treeview = gtk.TreeView(self.advanced_params_liststore)
		self.advanced_params_treeview.set_rules_hint(True)
		self.advanced_params_treeview.set_headers_visible(False)

		self.advanced_params_togglerenderer = gtk.CellRendererToggle()
		advanced_params_tvcolumn1 = gtk.TreeViewColumn ('toggle',self.advanced_params_togglerenderer,active=0)

		self.advanced_params_treeview.append_column(advanced_params_tvcolumn1)


		self.advanced_params_textrenderer = gtk.CellRendererText()
		advanced_params_tvcolumn2 = gtk.TreeViewColumn ("text",self.advanced_params_textrenderer,text=1)
		self.advanced_params_treeview.append_column(advanced_params_tvcolumn2)

		self.advanced_params_togglerenderer.connect(
							'toggled',
							 self.gui_control.cb_pw_isoparam_toggled,
							 self.advanced_params_liststore,
							 self.project_id
							 )

		self.advanced_params_treeview.set_model(self.advanced_params_liststore)
		sw.add (self.advanced_params_treeview)

		# Adding all the boxes
		vbox_easy.pack_start(frame_3,False,True)
		vbox_advanced.pack_start(hbox_iso_level,False,True)
		vbox_advanced.pack_start(hbox_data_format,False,True)
		vbox_advanced.pack_start(hbox_10,False,True)
		vbox_advanced.pack_start(advanced_params_frame,True,True,10)

		advanced_params_expander = gtk.Expander ()
		advanced_params_expander.add(vbox_advanced)
		frame_label = gtk.Label()
		frame_label.set_markup ('<span weight="bold">Advanced File System Params</span>')
		advanced_params_expander.set_label_widget(frame_label)

		main_vbox.pack_start(vbox_easy,False,False)
		main_vbox.pack_start(advanced_params_expander,False,False)

		return frame

	def __cb_change_text (self,column,cell,model,iter):
		cell.set_property('text',model.get_value(iter,1))
		return

	def __cb_change_toggle (self,column,cell,model,iter):
		cell.set_property('activatable',model.get_value(iter,0))
		return

	def volume_descriptor_frame(self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		inside_frame = gtk.Frame()
		frame_label = gtk.Label()
		frame_label.set_markup ('<span weight="bold">Volume Descriptor</span>')
		inside_frame.set_label_widget(frame_label)
		inside_frame.set_shadow_type(gtk.SHADOW_NONE)
		vbox.pack_start(inside_frame,False,False)


		hbox_inside_frame = gtk.HBox(False,5)
		hbox_inside_frame.set_border_width (10)
		inside_frame.add(hbox_inside_frame)

		vbox_inside_left = gtk.VBox(True,0)
		#vbox_inside_left.set_size_request(100,0)
		hbox_inside_frame.pack_start(vbox_inside_left,False,True,20)

		labels = ["Volume name",
				  "System ID",
				  "Volset ID",
				  "Publisher",
				  "Data preparer",
				  "Application",
				  "Copyright file",
				  "Bibliography file"]

		for label in labels:
			temp_hbox = gtk.HBox(False,0)
			gtk_label =  gtk.Label(label)
			temp_hbox.pack_start(gtk_label,False,False)
			vbox_inside_left.pack_start(temp_hbox,False,False,5)

		vbox_inside_right = gtk.VBox(True,0)
		#vbox_inside_right.set_size_request(-1,150)
		hbox_inside_frame.pack_start(vbox_inside_right,True,True)

		for label in labels:
			temp_hbox = gtk.HBox(False,0)
			self.volume_desc_entries[label] = gtk.Entry(32)
			#temp_hbox.pack_start(entry,False,False)
			vbox_inside_right.pack_start(self.volume_desc_entries[label],False,False,5)

		self.volume_desc_entries ["Volume name"].set_text (self.gui_control.isofs_tool.volume_id)
		self.volume_desc_entries ["Volume name"].connect('focus-out-event',self.gui_control.cb_pw_volname_lose_focus,self.project_id)
		self.volume_desc_entries ["System ID"].set_text (self.gui_control.isofs_tool.sysid)
		self.volume_desc_entries ["System ID"].connect('focus-out-event',self.gui_control.cb_pw_sysname_lose_focus,self.project_id)
		self.volume_desc_entries ["Volset ID"].set_text (self.gui_control.isofs_tool.volset)
		self.volume_desc_entries ["Volset ID"].connect('focus-out-event',self.gui_control.cb_pw_volset_lose_focus,self.project_id)
		self.volume_desc_entries ["Publisher"].set_text (self.gui_control.isofs_tool.publisher)
		self.volume_desc_entries ["Publisher"].connect('focus-out-event',self.gui_control.cb_pw_publisher_lose_focus,self.project_id)
		self.volume_desc_entries ["Data preparer"].set_text (self.gui_control.isofs_tool.preparer)
		self.volume_desc_entries ["Data preparer"].connect('focus-out-event',self.gui_control.cb_pw_preparer_lose_focus,self.project_id)
		self.volume_desc_entries ["Application"].set_text (self.gui_control.isofs_tool.application_id)
		self.volume_desc_entries ["Application"].connect('focus-out-event',self.gui_control.cb_pw_application_lose_focus,self.project_id)
		self.volume_desc_entries ["Copyright file"].set_text (self.gui_control.isofs_tool.copyright)
		self.volume_desc_entries ["Copyright file"].connect('focus-out-event',self.gui_control.cb_pw_copyright_lose_focus,self.project_id)
		self.volume_desc_entries ["Bibliography file"].set_text (self.gui_control.isofs_tool.biblio)
		self.volume_desc_entries ["Bibliography file"].connect('focus-out-event',self.gui_control.cb_pw_biblio_lose_focus,self.project_id)

		return frame

	def create_cd_frame (self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		checkbox_labels = ["Simulation",
						   "Burn the Disk",
						   "Finalize Disk"]

		selected = []
		if 	self.gui_control.cdrecord_tool.simulation:
			selected.append(0)
		if 	self.gui_control.cdrecord_tool.write:
			selected.append(1)
		if 	self.gui_control.cdrecord_tool.fixating:
			selected.append(2)

		frame_1,self.burn_action_rb = check_boxes_box ("Action",checkbox_labels,selected)

		self.burn_action_rb["Simulation"].connect("toggled",self.gui_control.cb_pw_simulate_writing,self.project_id)
		self.burn_action_rb["Burn the Disk"].connect("toggled",self.gui_control.cb_pw_writing,self.project_id)
		self.burn_action_rb["Finalize Disk"].connect("toggled",self.gui_control.cb_pw_fixate,self.project_id)

		frame_label = gtk.Label()
		frame_label.set_markup ('<span weight="bold">Writing mode</span>')

		frame_2 = gtk.Frame ()
		frame_2.set_label_widget(frame_label)
		frame_2.set_shadow_type(gtk.SHADOW_NONE)

		writing_mode_vbox = gtk.VBox(False,0)
		###############################################################
		# Write Method Parameters Frame
		###############################################################
		hbox_write_method = gtk.HBox (True,0)
		hbox_write_method.set_border_width(2)
		label_hbox = gtk.HBox (False,0)
		write_method_label = gtk.Label ("Write method:")
		label_hbox.pack_start (write_method_label,False,True,4)

		self.write_method_combobox = gtk.combo_box_new_text()
		methods = ["Disk at once",
				   "Track at once"]

		for method in methods:
			self.write_method_combobox.append_text(method)

		self.write_method_combobox.set_active(methods.index("Disk at once"))
		self.write_method_combobox.connect ("changed",self.gui_control.cb_pw_write_method_changed,self.project_id)
		hbox_write_method.pack_start (label_hbox,False,True,4)
		hbox_write_method.pack_end (self.write_method_combobox,False,True)

		###############################################################
		# Device Speed Parameters Frame
		###############################################################
		hbox_dev_speed = gtk.HBox (True,0)
		hbox_dev_speed.set_border_width(2)
		label_hbox = gtk.HBox (False,0)
		dev_speed_label = gtk.Label ("Writer speed:")
		label_hbox.pack_start (dev_speed_label,False,True,4)

		self.dev_speed_combobox = gtk.combo_box_new_text()
		#print self.gui_control.dev_manager.devices[self.gui_control.dev_manager.used_device].cd_speeds
		dev_manager = self.gui_control.dev_manager

		device = dev_manager.get_drive_features(dev_manager.get_current_writer().get_device())
		speeds = device.cd_speeds

		self.dev_speed_combobox.append_text("Auto")

		for speed in speeds:
			if speed != "Auto":
				self.dev_speed_combobox.append_text(speed+" x")
			else:
				self.dev_speed_combobox.append_text(speed)


		self.dev_speed_combobox.set_active(0)

		self.dev_speed_combobox.connect ("changed",self.gui_control.cb_pw_dev_speed_changed,self.project_id)
		hbox_dev_speed.pack_start (label_hbox,False,True,4)
		hbox_dev_speed.pack_end (self.dev_speed_combobox,False,True)

		writing_mode_vbox.pack_start (hbox_write_method,False,False)
		writing_mode_vbox.pack_start (hbox_dev_speed,False,False)
		frame_2.add (writing_mode_vbox)

		vbox.pack_start(frame_1,False,False)
		vbox.pack_start(frame_2,False,False)

		return frame

	def make_copy_frame (self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		checkbox_labels = ["Simulation",
						   "Close Disk"]

		selected = [1]
		actions_frame,self.burn_action_rb = check_boxes_box ("Action",checkbox_labels,selected)
		self.burn_action_rb["Simulation"].connect("toggled",self.gui_control.cb_pw_simulation,self.project_id)
		self.burn_action_rb["Close Disk"].connect("toggled",self.gui_control.cb_pw_multisess_copy,self.project_id)

		vbox.pack_start(actions_frame,False,False)

		frame_label = gtk.Label()
		frame_label.set_markup ('<span weight="bold">Writing mode</span>')

		frame_2 = gtk.Frame ()
		frame_2.set_label_widget(frame_label)
		frame_2.set_shadow_type(gtk.SHADOW_NONE)

		writing_mode_vbox = gtk.VBox(False,0)

		###############################################################
		# Device Speed Parameters Frame
		###############################################################
		hbox_dev_speed = gtk.HBox (True,0)
		hbox_dev_speed.set_border_width(2)
		label_hbox = gtk.HBox (False,0)
		dev_speed_label = gtk.Label ("Writer speed:")
		label_hbox.pack_start (dev_speed_label,False,True,4)

		self.dev_speed_combobox = gtk.combo_box_new_text()
		#print self.gui_control.dev_manager.devices[self.gui_control.dev_manager.used_device].cd_speeds
		dev_manager = self.gui_control.dev_manager
		device = dev_manager.get_drive_features(dev_manager.get_current_writer().get_device())
		speeds = device.cd_speeds

		self.dev_speed_combobox.append_text("Auto")
		for speed in speeds:
			if speed != "Auto":
				self.dev_speed_combobox.append_text(speed+" x")
			else:
				self.dev_speed_combobox.append_text(speed)

		self.dev_speed_combobox.set_active(0)
		self.dev_speed_combobox.connect ("changed",self.gui_control.cb_pw_copy_speed_changed,self.project_id)
		hbox_dev_speed.pack_start (label_hbox,False,True,4)
		hbox_dev_speed.pack_end (self.dev_speed_combobox,False,True)

		writing_mode_vbox.pack_start (hbox_dev_speed,False,False)
		frame_2.add (writing_mode_vbox)

		checkbox_labels = ["Buffer-under-run-protection",
						   "Write-speed-control"]

		selected = [0,1]
		misc_frame,self.burn_action_rb = check_boxes_box ("Misc",checkbox_labels,selected)
		self.burn_action_rb["Buffer-under-run-protection"].connect("toggled",self.gui_control.cb_pw_buffer_underrun,self.project_id)
		self.burn_action_rb["Write-speed-control"].connect("toggled",self.gui_control.cb_pw_write_speed_control,self.project_id)
		vbox.pack_start(misc_frame,False,False)

		vbox.pack_start(frame_2,False,False)

		return frame

	def copy_copy_options_frame (self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		#===============================================================================
		#		Frame Audio Tracks
		#===============================================================================
		label = "Copy the CD on the fly, meaning no temp image will \nbe created. Please make sure the disk read speed\n at least double the writing speed"

		checkbox_labels = [ label ]

		selected = []
		on_the_fly_frame,self.on_the_fly_option = check_boxes_box ("On the fly",checkbox_labels,selected)

		vbox.pack_start(on_the_fly_frame,False,False)

		#===============================================================================
		#		Frame Temp Image Directory
		#===============================================================================
		tempdir_frame = section_frame ("Image File")
		tempdir_hbox = gtk.HBox (False)
		tempdir_hbox.set_border_width (10)
		tempdir_entry = gtk.Entry ()
		tempdir_entry.set_text (self.gui_control.config_handler.get ("misc/tempdir")+os.sep+"image.iso")
		tempdir_entry.connect('focus-out-event',self.gui_control.cb_pw_image_entry_lose_focus,self.project_id)
		tempdir_button = gtk.Button ("browse",gtk.STOCK_OPEN,True)
		tempdir_button.connect ("pressed",self.gui_control.cb_propw_open_file,tempdir_entry,self.project_id )
		tempdir_hbox.pack_start(tempdir_entry,True,True)
		tempdir_hbox.pack_start(tempdir_button,False,False)
		tempdir_frame.add (tempdir_hbox)

		vbox.pack_start(tempdir_frame,False,False)

		delete_image_option_hbox = gtk.HBox (False)
		self.delete_image_option = gtk.CheckButton("Delete ISO after copy")
		delete_image_option_hbox.pack_start(self.delete_image_option,False,False,10)
		self.delete_image_option.connect("toggled",self.gui_control.cb_pw_del_img_after_copy,self.project_id)

		vbox.pack_start(delete_image_option_hbox,False,False)

		reader_device_frame = section_frame ("Reader Device")
		vbox.pack_start(reader_device_frame,False,False,5)
		reader_hbox = gtk.HBox (False,0)
		reader_hbox.set_border_width (10)
		reader_device_frame.add (reader_hbox)

		device_combo_box = gtk.ComboBox()
		device_combo_box = gtk.combo_box_new_text()
		reader_keys = []
		for dev_key in self.gui_control.dev_manager.devices.keys():
				device_combo_box.append_text(self.gui_control.dev_manager.devices[dev_key].get_display_name())
				reader_keys.append(dev_key)
		device_combo_box.set_active(0)

		speed_combo_box = gtk.combo_box_new_text()
		speed_combo_box.append_text("Auto")

		device_features = self.gui_control.dev_manager.get_drive_features(reader_keys[0])
		for speed in device_features.cd_speeds:
			speed_combo_box.append_text(speed+" x")
		speed_combo_box.set_active(0)

		device_combo_box.connect("changed",self.gui_control.cb_pw_reader_device,reader_keys,self.project_id)
		speed_combo_box.connect("changed",self.gui_control.cb_pw_read_speed_changed,self.project_id)

		reader_hbox.pack_start(device_combo_box,True,True,5)
		reader_hbox.pack_start(speed_combo_box,False,False,5)

		vbox.pack_start(reader_device_frame,False,False)

		self.on_the_fly_option[label].connect("toggled",self.gui_control.cb_pw_on_the_fly_toggled,self.project_id,tempdir_hbox,reader_hbox)

		if len(self.gui_control.dev_manager.devices.values()) <=1:
			on_the_fly_frame.set_sensitive(False)
		return frame

	def copy_reading_options_frame(self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		#disk_type_combobox.connect ("changed",self.gui_control.cb_pw_dev_speed_changed,self.project_id)
#===============================================================================
#		Frame Data Tracks
#===============================================================================
		checkbox_labels = ["Ignore read errors",
						   "Read sectors in raw mode",
						   "Read Media catalog Number and ISRC (slower)"
						  ]
		selected = [0,2]
		data_tracks_options_frame,self.data_tracks_options = check_boxes_box ("General options",checkbox_labels,selected)

		self.data_tracks_options["Ignore read errors"].connect("toggled",self.gui_control.cb_pw_simulate_writing,self.project_id)
		self.data_tracks_options["Read sectors in raw mode"].connect("toggled",self.gui_control.cb_pw_read_sectors_in_raw_mode,self.project_id)
		self.data_tracks_options["Read Media catalog Number and ISRC (slower)"].connect("toggled",self.gui_control.cb_pw_fasttok,self.project_id)

		#checkbox_labels = ["Use CDDB"]
		#selected = [0]
		#music_tracks_options_frame,self.music_tracks_options = check_boxes_box ("Audio CD options",checkbox_labels,selected)
		#self.music_tracks_options["Use CDDB"].connect("toggled",self.gui_control.cb_pw_useCDDB,self.project_id)

		vbox.pack_start(data_tracks_options_frame,False,False)
		#vbox.pack_start(music_tracks_options_frame,False,False)

		return frame

	def cda_options (self):
		frame = gtk.Frame()

		vbox = gtk.VBox(False,10)
		frame.add (vbox)
		vbox.set_border_width (10)

		inside_frame = gtk.Frame()
		frame_label = gtk.Label()
		frame_label.set_markup ('<span weight="bold">CD TEXT Parameters</span>')
		inside_frame.set_label_widget(frame_label)
		inside_frame.set_shadow_type(gtk.SHADOW_NONE)
		vbox.pack_start(inside_frame,False,False)


		hbox_inside_frame = gtk.HBox(False,5)
		hbox_inside_frame.set_border_width (10)
		inside_frame.add(hbox_inside_frame)

		vbox_inside_left = gtk.VBox(True,0)
		hbox_inside_frame.pack_start(vbox_inside_left,False,True,20)

		labels = ["Title",
				  "Performer",
				  "Arranger",
				  "Songwriter",
				  "Composer",
				  "UPC EAN",
				  "Disk ID",
				  "Message"]

		for label in labels:
			temp_hbox = gtk.HBox(False,0)
			gtk_label =  gtk.Label(label)
			temp_hbox.pack_start(gtk_label,False,False)
			vbox_inside_left.pack_start(temp_hbox,False,False,5)

		vbox_inside_right = gtk.VBox(True,0)
		hbox_inside_frame.pack_start(vbox_inside_right,True,True)

		for label in labels:
			temp_hbox = gtk.HBox(False,0)
			self.cd_text_entries[label] = gtk.Entry(32)
			vbox_inside_right.pack_start(self.cd_text_entries[label],False,False,5)

		self.cd_text_entries ["Title"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_title_lose_focus,self.project_id)
		self.cd_text_entries ["Performer"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_performer_lose_focus,self.project_id)
		self.cd_text_entries ["Arranger"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_arranger_lose_focus,self.project_id)
		self.cd_text_entries ["Songwriter"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_songwriter_lose_focus,self.project_id)
		self.cd_text_entries ["Composer"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_composer_lose_focus,self.project_id)
		self.cd_text_entries ["UPC EAN"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_upc_lose_focus,self.project_id)
		self.cd_text_entries ["Disk ID"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_diskid_lose_focus,self.project_id)
		self.cd_text_entries ["Message"].connect('focus-out-event',self.gui_control.cb_pw_cdtext_message_lose_focus,self.project_id)

		return frame
